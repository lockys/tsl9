# v4.1.60：lookup 的 SP30 輸出與 callback 後續訊息

本輪完整核對兩版本 lookup 與 post-helper，共 **356 bytes／134 instructions**；另重用既有 message allocator／sender 共 464 bytes，不增加既有 C 重建覆蓋率。

| 本體 | V131 | V140 | 每版 bytes／instructions |
| --- | --- | --- | --- |
| lookup，linked RAM entry | `20000a48` | `20000a48` | 76／27 |
| lookup，FLASH source | `40cb8` | `40cf8` | 同上，不重複計數 |
| post-helper | `4b534..4b59a` | `4b5cc..4b632` | 102／40 |

[檢查器](check_v4160_callback_lookup_post_static.py) 與 [固定帳本](v4160-callback-lookup-post-static.json) 保存完整 operands、SHA-256、CFG、不可變路徑憑證及原始 sparse HEX backing。lookup 在 linked RAM PC 解碼，來源與候選 startup first-copy operands 對應；不是已觀察到的 RAM 或實際 installed provider。全程沒有目標執行／模擬、mutable target state、callback、allocator、copy、MMIO 或硬體操作。

## Lookup 搜尋第二條鏈表，返回實際命中的記錄

入口 H=A0 為完整 word，A1 是可選的 halfword output pointer。從 `20002f88 / 20002fd8` 取 head；每個 node 依序：

1. 讀 C=U32[node+8]，捕捉 F=U16[C+10]，即首筆 config 的 handle。
2. 若**無號** H<F，略過此 node，尚不讀 count。
3. 否則捕捉 N=U16[node+4]，計算 F+N；若**有號** signed32(H)>=F+N，略過此 node。
4. 進入後以 i=0..N−1、步長 16 掃描 config records，fresh 讀 U16[record+10]，與完整 H 比較。

第一個命中返回該 record 的地址 C+16*i。未命中就沿 fresh U32[node+0] 繼續，head 最後為 0 才返回 0。外層沒有 count／cycle guard，仍須有效有限鏈表；內層 count 為 U16，最多 N 筆，達到 count 前不會先發生 index wrap。pointer extent、地址無 wrap 與實際 count／配置大小仍是前提。

F、N 都是 U16，總和不超過 131070。只有在 H 屬於 U16 域時，兩個 range guards 才可直接寫為 `F<=H<F+N`；一般完整 word H 不可把有號上界換成無號。即使 H>65535 因 range guards 而進入掃描，也不可能等於 fresh、零擴展的 U16 record handle。

第一次捕捉 F 與 i=0 的 candidate handle 是兩次讀取；後續不得無條件當成同一個值，也沒有直接以 H−F 計算 record index。

## SP30 保存的是服務首筆 handle，不是本次 H

命中後，若 A1 非 null，唯一的 payload store 是：

```text
U16[A1] = captured F
return matched_record_pointer
```

因此查詢 H=7 命中某個 F=5、N=3 的服務時，output 是 5。這只是區分兩個值的純量例子，沒有執行目標查詢。

接回 [完整 +4 消費端](v4160-callback-fields-static.zh-TW.md)：它以 `(original A1,&SP30)` 呼叫 lookup，再 fresh LHU[SP30] 傳給 callback-list getter。matching lookup、有效非 null frame output、正常返回且 output 沒有被改寫時，SP30 確實已由 lookup 寫入 F；前輪尚未展開的局部輸出缺口在這些條件下已閉合。

lookup 沒有 frame／child call，只寫 output halfword，不保存輸入 pointers。callback getter 是否仍以相同首筆 handle 找到對應 callback 表，另須 config+10、node key、鏈表及跨呼叫保存條件；不能把 lookup 命中當作完整註冊或生命週期證明。

## Post-helper 的第一個 gate 是全域 task byte

post-helper 建立 32-byte frame，讀取 `U8[20002ee0 / 20002f30]` 為 T0。此讀取覆蓋 A4，**不是檢查入口 A4**；前輪 caller 帶來的 A4=`0x2902` 不決定這個 gate。

- T0=255：不呼叫 allocator，還原 frame 後返回原入口 A0。
- T0!=255：保存原 A0／A1／A2，請求 `0x20000236(10)`。
- allocator 返回 null：本函式返回 0，沒有訊息 stores 或 sender tail。

此處的 `0x20000236(10)` 僅表示 A0 的長度；post-helper 在呼叫前沒有清零或重設 A1／A2。它們的實際用途仍須以 matching allocator 的完整合約為準。

所以 post-helper 返回 0 既可能是配置失敗，也可能來自後續 sender；上層消費端本來就保存 callback 返回的 0，並忽略 post-helper 最後的正常回覆。

## 10-byte 可見訊息：0x00B1 與三個 low16 值

配置返回非 null M 時，原指令依下列順序寫入：

| 次序 | offset／寬度 | 值 |
| --- | --- | --- |
| 1 | M+0／U16 | `177`，即 `0x00b1` |
| 2 | M+4／byte | 0 |
| 3 | M+2／U16 | low16(原 A0) |
| 4 | M+6／U16 | low16(原 A1) |
| 5 | M+8／U16 | low16(原 A2) |

**M+5 沒有本機初始化。** 不能把訊息視為完整清零的 10-byte 結構。這裡只保存三個低 16-bit 值，沒有深拷貝來源 buffer；外部 allocator／callback 的保存或副作用仍未知。

在前輪 caller 的 post 路徑中，原 A2 指向的兩個 source bytes 已先組成整數，該整數才傳入本 helper 的 A2。訊息 M+8 保存的是該值，不是 caller 原 source pointer 的完整副本。

接著重新讀取同一個 task cell 為 T1，設定 `(A0=T1,A1=M)`，還原 frame 後以 JAL x0 尾移交 `0x43208 / 0x43294`。**沒有再測 T1 是否為 255**；T0、T1 分開保存，配置及其他 writers 可能使它們不同。

## 重用 allocator／sender 的入佇列條件

沿用 [訊息建立與 sender 合約](v4160-threshold-message-static.zh-TW.md)，本輪重算其 bytes、operands／hash、映射與原始 HEX，不執行任何服務：

- matching message allocator 將可見長度 10 轉成 core 請求 18、tag `0xf00a`。隱藏 header 的 next=0、length=10、owner=255；header 的另一個 byte 及可見 payload 不由該 wrapper 全面清零。
- matching sender 要求非 null M、完整 task>2 且 task<fresh task-count、header next=0／owner=255。符合才寫 owner、發布至全域佇列、通知 event `0x8000` 並返回 0。
- 無效 task 會嘗試 cleanup 後返回 3；header 不合會嘗試 cleanup 後返回 5。cleanup 嘗試不等於已完成釋放，更不證明與原 allocator 存在完整 ownership 逆關係。

T0 非 255、allocator 非 null 或 post-helper 曾建立訊息，都不能單獨保證入佇列。此處沒有證明實際 task、sender 綁定、event 送達、B1 消費或完整釋放流程。

## 重播與下一段

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_callback_lookup_post_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_callback_lookup_post_static.py
```

檢查器拒絕 134 個 instruction mutations 與 8 個 typed-load mutations，核對 U16 range 邊界、完整 count 域、first-handle 輸出與訊息 byte 區間，以及帳本精確重播。所有正常 call-return、S／SP／RA／saved-frame 保存、有效 extents、外層有限鏈表及無不利 alias／wrap／IRQ／DMA／重入仍是條件，沒有以 syntactic CFG 見證替代實際可達性。

後續需追查 task byte writers、B1 下游消費與釋放，以及 node／config／count／handle 的來源與跨呼叫保存。實際 provider、startup completion、物理副作用、物件保存期及可用韌體仍未完成驗證。
