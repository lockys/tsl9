# v4.1.60：B1 目的 task 寫入與候選消費端

本輪完整核對兩版本的 task setter、兩個來源 wrapper 及 registered handler，新增 **1,104 bytes／382 instructions** 靜態證據。所有 bytes 對回原始 sparse HEX；既有 C 重建覆蓋率不變。重用的 registration／initializer／receive／release 不再計為新覆蓋。

| 完整本體（右端不含） | V131 | V140 | 每版 bytes／instructions |
| --- | --- | --- | --- |
| task setter | `4cfc6..4cfd0` | `4d05e..4d068` | 10／3 |
| wrapper A | `6c0c6..6c0f0` | `6c2aa..6c2d4` | 42／15 |
| wrapper B | `6c0f0..6c11a` | `6c2d4..6c2fe` | 42／15 |
| handler | `6cc4c..6ce16` | `6ce38..6d002` | 458／158 |

[檢查器](check_v4160_b1_task_route_static.py) 與 [固定帳本](v4160-b1-task-route-static.json) 固定所有 operands、SHA-256、完整 CFG、17 個 handler calls、stores、Xwchc 解碼與選定不可變路徑。各本機 CFG 都無環；callee 返回與實際可達性仍是條件。沒有執行或模擬目標 ISA、callback、provider、RAM／heap／queue、MMIO 或裝置。

## Task setter 的兩個直接來源

setter 只有一個 byte store：將 low8(入口 A0) 寫至 `20002ee0 / 20002f30`，然後 RET；A0 本身不被截斷或重設。這正是 [B1 producer](v4160-callback-lookup-post-static.zh-TW.md) 在配置前、配置後分別讀取的 task cell。

兩個 wrapper 的共同流程是：

1. 讀取 role task byte `20002fc2 / 20003012`，捕捉為 R0，放到 A1。
2. 將原入口 A0 的完整 word 存到另一個全域欄位：wrapper A 為 `20002fe4 / 20003034`，wrapper B 為 `20002fe0 / 20003030`。此處不解參照該值。
3. 設 A0=24，呼叫 `46506 / 4659e`。其餘參數不是全數重新初始化；這裡保留 callee 副作用及保存前提。
4. 返回後**重新讀取** role task byte 為 R1，放到 A0；還原 16-byte frame，以無新 link 的尾跳移交 setter。

故 producer task cell 保存的是第二次 R1 的 low8，不是早先傳給索引 24 callee 的 R0，也不是 wrapper 的入口指標值。R0、R1 不能自動視為相等；這些 wrappers 沒有自行檢查 255 或登記成功。

兩個直接尾移交的原指令已固定，但沒有宣稱這是全部 computed／aliased writers，也未證明原 APP 實際走入這些 wrappers。

## Role task byte 與候選 handler 的同一次登記來源

重用 [ID9 到下一筆登記](v4160-id9-vector-dispatch-static.zh-TW.md) 及 [ID10 initializer](v4160-id10-nv-initialization-static.zh-TW.md)：

- outer `6dd5e / 6df4e` 形成 handler `6cc4c / 6ce38`，呼叫既有 registration leaf，接著直接呼叫 initializer `6c300 / 6c4ec`，中間沒有覆寫 A0 的指令。
- initializer 把入口 A0 保存到 SP+12，跨越 setup call 後重新載入，再將 low8 寫到 `20002fc2 / 20003012`。來源不是 setup 的返回 A0。
- 在既有 count=10、capacity／table／context 與 callee 保存等條件下，registration 寫入 table row10=handler、回覆 10，因而 role byte 可接成 10。setup 中途曾把同一 byte 設為 FF；初始化、NV tail 正常返回及稍後資料保持仍須另證。

這把「table 登記的 handler」與「wrapper／consumer 使用的 role byte」接到同一條條件性來源。它不是已觀察到的 scheduler 登記、實際 task10、startup completion 或全域不可變證明。

## Handler 的 bit15 路徑與 B1 選取

handler 保留完整入口 event word E；以 signed16(E)<0 選 bit15 路徑。該路徑不拿入口 A0 當 receive task，而是 fresh 讀 role task byte，再呼叫 linked RAM `2000028c`。

receive 返回 0 時，略過 release，正常返回完整 **E XOR `0x8000`**。非零 M 則保存到 S1，讀 U8[M+0]：

- byte 等於 `0xb1` 才進 B1 分支。producer 雖以 SH 寫 `0x00b1`，consumer **只測低 byte**；沒有要求 M+1=0。
- fresh U8[M+4] 非零時，不讀後續三個 U16，直接進共用 cleanup。
- M+4=0 時，依原指令順序讀 U16[M+8]→A2、U16[M+6]→A1、U16[M+2]→A0。

selected B1 路徑的訊息 reads 僅涵蓋 M0、M4、M8..9、M6..7、M2..3，**沒有讀 M1 或 M5**。因此前輪 producer 未本機初始化的 M5，不是這條 B1 路徑的讀取依賴；這不保證其他消費端或較晚 callee 不會存取它。

三個 U16 對應 producer 保存的 low16 原始值；不能還原成原本完整 word，也不能把 M+8 當成 source buffer pointer 的完整副本。

## 清 flag、處理、條件通知，再 cleanup

B1 的三個欄位載入後，handler 建立 flag pointer `20002fd4 / 20003024`：

1. 先將 flag byte 清為 0。
2. 呼叫 `6c042 / 6c226`，參數為 `(U16[M+2], U16[M+6], U16[M+8])`。它的返回值未被當成 handler status。
3. fresh 重讀 flag。為 0 直接 cleanup；非零則 fresh 讀**另一個** task byte `20002ef0 / 20002f40`，再次清 flag，呼叫 `44310 / 443a4` 後 cleanup。

這個通知 task 與 role task、B1 producer task 是三個不同的 cell，不可合併。flag 被清零後的實際變化，以及兩個 callees 的完整副作用，仍待展開。

兩個 flag 結果及 M+4 非零的 B1 路徑，均將 **原捕捉的 M** 交給 public release `431ba / 43246`；不是釋放較晚 callee 的回覆指標。清理正常返回後，handler 回傳完整 E XOR `0x8000`，保留 upper16，也不因 release 回覆而改變。

全函式其他訊息及 event 路徑也已固定 bytes／CFG，但本輪沒有補齊所有 callee 語意。尤其 D0 分支可依 child 返回 0 略過共用 cleanup，**不能把 B1 的清理合約推廣為所有訊息都釋放**。

## Receive／release 的保存界線

重用 [receive 與內部指標釋放合約](v4160-message-receive-static.zh-TW.md)：matching receive 選取／摘除訊息後，把 owner marker 還原為 FF，再返回 M；public release 在通過相關 guard 的路徑上，將 M 原值轉交 private release `20000110`。

已有的 interior-pointer 證明只在有效 heap／header／extent、配置身分、鏈表及保存前提下成立，不能只因呼叫了 release 就宣稱原區塊實際已釋放。也沒有證明 `6c042`、通知服務或其他 provider 不保留訊息衍生資料。

整條來源保留分開的 snapshots：registration 回覆、initializer saved byte、wrapper R0／R1、producer T0／T1、consumer fresh role byte。若要把 B1 的 sender task 與此 handler 的 receive task 視為相同，需要各段資料保持與實際綁定；本輪沒有以多次相同地址的讀取替代這些證明。

## 重播與下一段

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_b1_task_route_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_b1_task_route_static.py
```

檢查涵蓋 382 個 instruction mutations、24 個 typed-load mutations、65,536 個 event low16 與 setter low16 純量案例、B1 欄位與清理路徑、原始 HEX，以及帳本精確重播。圖見證只表示本機控制流，仍須正常 callee／S／SP／RA／saved-frame 保存、有效記憶體、有限 queue 及無不利 alias／wrap／IRQ／DMA／重入等前提。

下一段可展開 `6c042 / 6c226`、`44310 / 443a4` 及 flag writers，並繼續追查 wrapper 實際 caller、task 保存與完整訊息生命週期。實機功能、installed provider 及可用韌體仍未驗證。
