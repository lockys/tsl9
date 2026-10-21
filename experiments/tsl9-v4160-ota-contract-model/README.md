# ID2966／V4.1.60 OTA 命令契約

這是原 `9C4A` 命令本體與 `9B8E` 回讀回覆流程的可讀 C11 / C++17 語義模型。三段 source-map 範圍共 718 bytes，固定原 ID2966 韌體 SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。同一版的原始執行指令另外保存在 native integration；本工程沒有實作原機 resident、硬體驅動、傳送器或可刷映像。

## 與舊版不同的原始行為

- W：active、n=1026、BE16 page、`08001000 + page*1024`，接受 page 0..27。來源未對齊時，以原 nominal ROM copy 操作搬至較低的對齊地址；不猜重疊 copy 的原機語義。依序呼叫四次 `9C0A` 256-byte primitive，再逐 word 先讀 Flash、後讀 live source。讀回不符回一 byte `255`；相符會配置 1026-byte buffer，寫 BE16 page、從 Flash 複製 1024 bytes，再要求 W 回覆。配置失敗不送這份回覆。
- E：active 後必須 strict n=15、mode=0，再以 `92F2(payload+1,14)` 的 raw zero-result 通過，才清 active、要求兩個延遲 callback 與 empty E 回覆。不能套用舊模型 active-only 的 E。
- S：先保存 mode 作回覆 byte0、設定 byte1=1，驗證後重新讀取 live mode。成功置 active1，失敗清 active 並回 `[FF,1]`。回覆不是整份 start payload。
- U：先清 active，再驗 `(n-1)&255`／payload+1；通過後 mode1 才要求 BOOT-transition callbacks，但 mode 非1仍可走一 byte1 回覆。
- R：active、strict n=16、`92F2(payload+2,14)` 通過後才讀 BE16 page，走同一 1026-byte echo。原本體沒有 W 的 page0..27 guard，模型不替它增設這項條件。

`92F2` 的 raw zero-result 才走通過分支，不能套用另一 SDK BOOL 比較 API 的相反慣例。回讀 helper 在要求 TX 後仍 tail-delegate 給 `40068`；此時 HALT/TRANSFER 不會撤銷先前已發生的合成效果。沒有把普通 return 當成真實傳送或寫入成功。

## 執行與證據限制

```powershell
.\verify.ps1
.\verify.ps1 -Cpp
```

預設查找專案內原始 ID2966 BIN，也可用 `-Firmware <絕對路徑>`。先核原始檔與三段 bytes，再以 `/W4 /WX` 編譯並執行 host tests；每次輸出獨立 build 收據與 source/executable/compiler SHA256。

所有記憶體與 callee 效果都經明確的合成 provider。原數值地址不轉成 host 指標。小型回覆的 inline bytes 是本模型的資料 view，不宣稱原 SP 或 C ABI。原 `9C0A` quarter primitive 包含 CSR 0x800／mask136、status49 與 Flash helpers，這裡保留為未知 provider；不可用另一個 `197BE` BLE storage hook 取代它。配置、copy、排程、傳送與釋放的普通返回都不保證實體成功。

測試涵蓋 W echo 與 FF、嚴格 E/R guards、R 與 W 不同範圍、live source/mode 變化、未知值、配置失敗、alignment-copy 邊界及五條正常路徑每一步的 HALT/TRANSFER 前綴。只使用合成記憶體與識別比對結果，沒有產生真 UID 的封包、執行韌體、模擬 MCU 或操作 BLE/CAN/UART/Flash。

這只是 Runtime 自身更新 BOOT 區域的本體契約。寫入 Runtime 映像要由相應 BOOT receiver 接收；已保存 BOOT 的版本/回覆相容性必須另核，不能由本模型或頁面數值合格就宣稱可 OTA。硬體、resident、stack/IRQ 與完整更新/復原仍未證明，`OTA_ready=false`。

