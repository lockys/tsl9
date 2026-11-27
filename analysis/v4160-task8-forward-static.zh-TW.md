# typeA0 下游：B0 訊息轉送與指標選取

接續 [other callback 與函式表](v4160-task8-callback-static.zh-TW.md)，本次完整核對 callback 的兩個下游 helper，並接回既有 sender 與 message allocator 的靜態合約。兩份參考候選合計 **520 bytes／192 條指令**，全部由原始 sparse HEX 覆蓋，且與候選 bytes 一致。沒有更新既有 C 重建覆蓋率，也沒有證明實際 installed provider、硬體功能或完整 payload 保存期。

| 完整範圍（右端不含） | V1.31 | V1.40 | 每版 |
| --- | --- | --- | --- |
| B0 forward helper | `0x49E4A..0x49ED0` | `0x49EE2..0x49F68` | 134B／51i |
| pointer-selection leaf | `0x49DCC..0x49E4A` | `0x49E64..0x49EE2` | 126B／45i |

兩個函式內 CFG 均為 DAG。leaf 的兩版原始 bytes 完全相同；forward helper 的呼叫位址隨候選版本不同。call fallthrough 仍以未知 callee 普通返回及所需保存條件為前提。

## forward helper 的兩種錯誤與固定返回0

入口以**完整 A0** 與255比較，恰好相等便在建立 frame 前返回2。它沒有在這裡截成 byte，也不是一般 task 範圍檢查；例如 A0=256 不會被這個特定條件拒絕。

其餘入口先保存原 task、ID、flag、opcode、source pointer，再明確設定 A0=32，呼叫 mapped message allocator `0x20000236`。配置結果 M 為空時返回19，沒有本機 release 呼叫。

M 非空時，依次直接寫入：

| visible M offset | 寫入來源 |
| --- | --- |
| byte0 | `0xB0` |
| byte1 | low8(原 A2) |
| halfword2 | low16(原 A1) |
| byte4 | low8(原 A3) |

此函式沒有存取 bytes5..7。不能由此判定它們為零，或推定全域初始化狀態。

接著令目的地為 M+8、長度24：原 A4 非空時呼叫 copy service `0x20000332(M+8,原A4,24)`；空時改呼叫 fill service `0x2000039C(M+8,0,24)`。這些是原指令實參，實際 provider 語義、source extent、初始化與保存行為仍需分別證明。

最後呼叫 sender `0x43208`／`0x43294`，明確實參為 `(原完整 task,M)`。**sender 普通返回後，helper 無條件把 A0 改成0。** copy、fill、sender 的 scalar 回覆都沒有從這個 helper 傳回上層。

所以完整本機返回規則是：

```text
full task == 255          -> 2
otherwise allocator null -> 19
otherwise                -> sender call, then 0
```

這個0表示走完相應本機返回路徑，不能單獨代表訊息已入佇列或事件已送達。

## 對照既有 sender：拒絕結果會被遮住

本次重用 [sender／queue 合約](v4160-threshold-message-static.zh-TW.md)，重新核對完整146B sender 與86B mapped allocator 的既有雜湊及對應入口；不把這些 bytes 重複算成本次新增函式覆蓋。

sender 對非空 M 另要求：完整 task>2 且小於 fresh U8 task count、`U32[M-8]==0`、`U8[M-2]==255`。在普通返回及其他前提成立時：

- 無效 task：嘗試 deallocate M，再返回3。
- 無效 header：嘗試 deallocate M，再返回5。
- 接受：更新 marker、發布訊息至既有鏈表、嘗試 event，固定返回0；event 回覆仍沒有被採用。

forward helper 會把這三種 sender 回覆全部遮成0。特別是 task0..2，雖不等於255而會嘗試配置，但若 M非空且執行到 sender，仍會被它拒絕；較早的 callback task gate 不等於後續 fresh task／count 的保存證明。

既有 public deallocator 把 M 原值交給 private release，沒有減8；不能直接套用只針對 core payload M-8 的釋放逆運算證明。因此這裡的 deallocate 也只是呼叫嘗試，不代表已確認原配置成功釋放。

本階段沒有執行 sender、allocator、控制欄位、FENCE.I 或 queue，也沒有把這些原指令當成已驗證的實體 critical section。

## pointer leaf 的完整 U32 映射

leaf 沒有 call、store 或 SP 改動，encoded definitions 只有 A0、A5。它對完整 unsigned A1 進行比較，沒有截成 byte，也沒有先驗證 A0 非空或來源 extent。返回值是選定的 U32 word 原值，或固定0：

| opcode | 讀取 `U32[原A0+offset]` |
| --- | --- |
| 14 | offset0 |
| 5、7、9、11、13、15、17、18、27、29、82、210 | offset4 |
| 22、23 | offset8 |
| 6 | offset12 |
| 其餘全部 U32 值 | 不讀來源，返回0 |

共有16個 opcode 會讀取一個 word，其餘 `2^32-16` 個值返回0。offset0 的分支不是直接的 equality14：它結合前面的比較，留下13<opcode<15，才唯一確定14。

checker 對完整 DAG 的每條路徑提取 literal equality／unsigned comparison 條件，用 host 純整數區間求交，驗證所有非空區間互不重疊且覆蓋整個 U32 域，再核對上述映射。這是不可變 CFG 的條件證書，沒有逐步執行目標指令、更新目標 registers 或讀取模擬記憶體。

## callback 串接：只有四個初始 opcode 可能選到 word

在 tuple opcode 跨未知 row decoder、handler、helper 與 fresh reads 都保持不變的額外前提下，前一階段的11個表內 opcode 中，opcode4會先直接返回，opcode30根本另走分支。leaf 的來源域為：

```text
2,6,8,10,12,14,16,18,22,24
```

其中只有 `6→offset12`、`14→offset0`、`18→offset4`、`22→offset8` 會選取 word。其他六個返回0。這個縮小的集合不是對執行時 opcode 永不變動的證明；callee aliases、IRQ、DMA、重入或其他 writer 都需另行排除。

正常 row handler 成功路徑呼叫 forward helper 時，準備的是：

```text
(fresh task byte, 原ID, 0, fresh opcode, &callback_local_SP24)
```

helper 返回2或19時，callback 直接傳回該值，繞過 release flag 直接清零。helper 返回0才呼叫 pointer leaf；leaf 選出的 word 非零時，callback 才執行 `U8[原release_flag_pointer]=0`。

**因為 helper 也會把 sender 的拒絕3／5遮成0，這條 flag clear 不代表 sender 接受或投遞成功。** 而被選中的非零 word，也沒有在這裡被驗證等於原 payload、body pointer 或某個仍有效的配置。

opcode30的另一條呼叫準備 source=0、A2=0；只有確實進入 helper、未因 task255返回且配置成功後，才會呼叫24-byte fill。callback 最終仍忽略 helper 回覆並返回0。因此 opcode30路徑中的配置失敗19不會直接變成 callback19。

## 32-byte 訊息與保存期界線

在實際 allocator/copy 合約、有效 extent 與不相互別名等前提下，helper 的直接訊息寫入覆蓋 `[0,5)`，copy/fill 的實參範圍為 `[8,32)`，兩者在32-byte request內，中間留下 `[5,8)`。來源24 bytes與 leaf 的四種4-byte讀取位移也能作條件性區間連接。

但24-byte固定長度不證明來源已完整初始化、所有 row decoder 都產生24 bytes、內部 pointer 已深拷貝，或訊息內含的 pointer 能活到消費完成。正常 caller 的來源是 callback frame SP+24；frame 後續返回時的安全性取決於真正 copy、embedded pointers 與消費端行為。

另外，最初 allocator 呼叫只明確準備 A0=32，**A4仍帶著原 source pointer**，並且保存在 S2 直到還原。不能在未知 allocator ABI 下宣稱 source 到 copy 時才首次可能被下游看見。sender 呼叫只明確重設 A0/A1，其餘 argument registers 是 provider 之後的 then-live 值，也不能假定全為零。

callback 明確傳給這個 helper 的 A2為0，沒有直接把 release flag pointer 當成此 helper 的 A2；但 [callback 初次 lookup 的 ambient A2](v4160-task8-callback-static.zh-TW.md) 仍是另一個未閉合的保存邊界。

## 返回19之後與下一段

在初始 flag1未被其他寫入者改變、original M+8非空及所需普通返回／保存條件下，row-success forward helper 配置失敗19可傳成 callback19，然後父 handler 仍先嘗試 private payload release，再因保存的 R=19略過 public message cleanup及event XOR。不能由此宣稱 retained message 安全重用、原 payload已保留或已完成釋放。

下一段應追查 typeB0訊息消費與內部 pointer 的釋放、各 row decoder／handler、其他 callback來源、實際 copy/fill／allocator/provider 綁定及所有 writers。完整生命周期尚未閉合。

## 離線重播

[checker](check_v4160_task8_forward_static.py) 與 [精確 ledger](v4160-task8-forward-static.json)：

```powershell
python -B analysis/check_v4160_task8_forward_static.py
python -O -B analysis/check_v4160_task8_forward_static.py
```

檢查涵蓋完整 operands／雜湊、每條函式內 CFG edge 的返回見證、四條 forward path、整個 U32 leaf 區間分割、192條指令變異、10個 unsigned→signed branch變異、65,536組 task/count、訊息區間與 callback/sender/allocator 串接。

全程只讀本機 bytes、原始 HEX、不可變 CFG 與 host 純量區間；沒有執行或模擬目標 ISA、callback、provider、RAM／heap／queue、MMIO 或硬體。GitHub 僅新增本階段三份分析與驗證檔案。
