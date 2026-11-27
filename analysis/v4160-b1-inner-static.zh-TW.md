# v4.1.60：內層 word 介面、命令 13 與輸出來源

本階段完整核對 RAM provider 兩份 **360 bytes／158 instructions**，合計 **720 bytes／316 instructions**，接通[worker 與 core 外層](v4160-b1-worker-static.zh-TW.md)的明確呼叫與輸出切片。原始 sparse HEX 與候選 BIN 全部一致。

| 候選 | linked RAM entry | FLASH source，結尾不含 | SHA-256 |
| --- | --- | --- | --- |
| V131 | `200022be` | `4252e..42696` | `0c64a96bcd53534dfb7d1727d8995ccef3add0a2095304f67329aa6480281f3a` |
| V140 | `2000230a` | `425ba..42722` | `3e705fa75087c6efb627aad518e863c3f9917bad0936d65a3e503643f435886b` |

[檢查器](check_v4160_b1_inner_static.py)與[帳本](v4160-b1-inner-static.json)保存完整 operands、CFG、58 loads／29 stores、Xwchc 編碼、所有局部 edges 的語法見證及等待路徑。另重用先前完整 RF／reset／pointer-publication 共 892 bytes，沒有重計為本階段 provider bytes，也沒有提高 C 重建覆蓋率。

只讀原指令與資料做離線驗證；沒有執行或模擬目標、硬體、provider、callback、RAM service 或任何加密演算法，也沒有可變的目標寄存器／記憶體模型。

## 兩組 16-byte 輸入的傳送格式

令 slot=`20003504 / 20003554`，入口三參數為 `(A,B,O)`。Provider 先捕獲 P=U32[slot]，向 P+0 寫 `0x100`，再寫零；沒有 P／輸入／輸出的 null guard 或長度參數檢查。

接著先讀 A 的 16 bytes，再讀 B 的 16 bytes。每四個 bytes 的 fresh 讀取順序是 **1、2、0、3**，分別放入 bits8..15、16..23、0..7、24..31。Scalar 算式為：

```text
word = b0 + (b1<<8) + (b2<<16) + (b3<<24)
```

| 入口來源 | 四個 word 的相對 P 位移 |
| --- | --- |
| A[0..15] | 40、44、48、52 |
| B[0..15] | 24、28、32、36 |

這是位元組拼裝與直接 store 的證據，不是輸入 snapshot、介面演算法或物理計算結果的證據。輸入可能在各次 fresh read 之間改變；實際存取、alias 與 word 介面語意另有前提。

## 三次獨立 RMW 與沒有有限上限的等待

輸入 word stores 之後，仍以最初捕獲的 P 依序執行：

1. fresh 讀 P+4，AND `~2`，寫回 P+4。
2. 再 fresh 讀 P+4，OR 1，寫回 P+4。
3. fresh 讀 P+0，OR 1，寫回 P+0。

不能把三次讀取合併成同一個控制字快照，也不能從寫入值推得硬體已接受或完成。

等待迴圈每次都**重新讀 U32[slot]**，再讀該 pointer+4 的 word。bit0 非零走 `+164` 保留編碼與 `+166` backward jump，回到 `+ee` 重新取 pointer；bit0 為零才開始 output。

完整 body 包含 RET 後仍可由分支到達的這兩條指令。`+164` 原始 bytes=`0100`，依既有 decoder 記錄為 nop 並固定原編碼；本分析沒有賦予其硬體等待／進展效果。沒有 timeout、counter、visited-set 或可證明的有限次數上限；slot 也沒有在迴圈中固定為第一次捕獲的 P。

## 16 個輸出 bytes 來自 16 次 word 觀察

退出等待後，A0 在第一個 output store 前設零，之後不再定義；只有完成全部 16 個 ascending byte stores 才走正常 RET。各 byte 的來源如下：

| O 相對 byte | word 位移 | pointer 來源 | extraction shifts |
| --- | --- | --- | --- |
| 0 | +24 | 成功退出的最後一次 poll pointer | 0 |
| 1 | +24 | 新取 U32[slot] | 8 |
| 2 | +24 | 又一次新取 U32[slot] | 16 |
| 3 | +24 | 又一次新取 U32[slot] | 24 |
| 4..7 | +28 | byte4 前重新取 pointer，之後保存在 A5 | 0、8、16、24 |
| 8..11 | +32 | 同一個 byte4 pointer | 0、8、16、24 |
| 12..15 | +36 | 同一個 byte4 pointer | 0、8、16、24 |

**每個 output byte 都各自重新讀一次 word。**即使後十二個 bytes 共用 pointer，也不是從三個保存的 word 擷取；不同 byte 可觀察到不同 word 值。前四個 bytes 的 pointer 甚至可能彼此不同。因此不能把結果寫成四個一致 word snapshot。

在 core 傳入 `(W,W+16,W+32)` 的範圍、ABI、非別名與資料保存前提下，這些 stores 作用於 W+32..47。Worker 最後倒序複製 W+45..47，所以 caller 的 SP+12／13／14 分別接收 provider 的 **output15／14／13**。它們依序取自同一個最後 pointer+36 的三次獨立 word read，分別擷取 bits24..31／16..23／8..15。這釐清資料來源，仍不證明其值有效、穩定或來自某個已驗證演算法。

## 命令 13：不沿用初始化時的 state=1

重用[完整 RF／reset 原指令合約](v4160-rf-tail-return-static.zh-TW.md)，但本輪的 core caller 只確定 A0=13，沒有證據沿用先前 initializer 的 state=1。

RF `63eda / 63fc4` 先保存 word `4002420c`、寫零並經 FENCE.I。由 `2000353c / 2000358c` 取得 pointer，再讀其 word0 的低兩位：

| 取樣條件 | 命令 13 的局部路徑 |
| --- | --- |
| low2=0 | 直接進 epilogue，encoded store 寫回自己的 control snapshot；不查 state、callback 或 reset |
| low2 非零，第一次 fresh state+7=3 | 從 `20003550 / 200035a0` 取 callback，明確傳 `(17,0,0)`，沒有 null guard |
| low2 非零，第一次 state+7 非3 | 略過該 callback |

命令保存在 S1；在 nested callee 保存 S1／frame 的前提下，13 排除專用的 command6 與 command7 arms。之後另外三次 fresh state+7 依序與 6、7、8 比較，遇到第一個符合才檢查 fresh state+9：

- state+9 非零：略過 local latch stores。
- state+9 為零：**再讀一次** state+7，寫至 state+8，然後 state+9=1。最後保存的 byte 不必等於先前匹配的 6／7／8。
- 三次皆不符合：略過 latch stores。

這些 selected low2 非零路徑都會清 flag `20002efc / 20002f4c`、呼叫 reset，正常返回後才寫回 RF 捕獲的 control snapshot。Callback reply 可影響 RF 的 scalar return；reset 的原指令不定義 A0，而外層 core 最後仍忽略這個 scalar、固定返回零。Control store-source 配對不是物理狀態已還原的證據。

Reset 的 bit3 read 只選擇略過或經過四個 NOP，沒有等待迴圈；descriptor slot 為非零時，還有兩組 descriptor-derived pointer OR stores，不能概括為只寫固定外設。四個 bit3／descriptor 語法組合均核對，但不代表已觀察到實際輸入可達。

## 找到 pointer 發布來源，尚未證明 B1 時點仍保持

重用完整 parent `64298 / 64382` body 的原始 HEX 與 operands，核對兩個明確發布：

| slot | encoded source |
| --- | --- |
| `20003504 / 20003554` | `40024000 + 768 = 40024300` |
| `2000353c / 2000358c` | `40024000 + 512 = 40024200` |

這提供了 provider 與 RF context 的靜態來源。在各次 fresh load 仍保持該發布的前提下，前述相對 word 操作才可換算成對應固定地址。尚未證明沒有其他 writers、B1 的實際初始化順序、callback slot 身分、實際 installed RAM copy、硬體進展或 borrowed pointer 完整保存期。

本輪不直接將此介面命名為某種 cipher，也不把 bit0 清除、provider 的正常零返回或 core 的固定零返回當成正確硬體輸出。下一步仍需追查 pointer／callback writers 與呼叫順序、可達資料及保存合約。

## 重播

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_b1_inner_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_b1_inner_static.py
```

檢查拒絕 316 個逐指令 mutations 與 34 個 typed-load mutations；驗證 65,536 組 byte-lane 加法、1,024 個 lane 值、poll bit 代數、全部明列的 command13／reset 路徑與 output index 串接。所有證書都是 host scalar／interval 或不可變 CFG 見證；一般與 `-O` 均逐 byte 重播同一份 JSON，沒有目標 ISA、provider 或硬體執行。
