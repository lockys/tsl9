# ID2580 BOOT W：數值範圍離線核對

## 證據與條件

`check.py` 重讀 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2580-V1.0.00-decoded.bin`：12,288 bytes，SHA-256 `650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb`。分析座標 base `0x1000` 是檔案／既有分析座標，**不是實測載入位置**。固定四段原始 bytes 的 SHA-256，涵蓋 W、wrapper、erase、program；具體指令與呼叫圖另見 [`../boot2580-command-adapter-2026-10-21/source/README.md`](../boot2580-command-adapter-2026-10-21/source/README.md)，以及既有 [`../../experiments/tsl9-contract-model/src/flash_page.c`](../../experiments/tsl9-contract-model/src/flash_page.c) 的條件式 Flash 模型。此檢查本身是從固定指令解讀導出的算術模型，不是解碼器或指令執行器；窗口 hash 證明輸入未改，不獨立證明其語意。先前的 BOOT acceptance 報告及其歷史重播依賴不包含在此 checkpoint；其跨版本、APK 和相容性結論不能由本檢查重播或獨立證實。

以下以 W active 非零、長度恰為 1026、記憶體讀取有效、所有必要的呼叫正常返回為前提；這些前提不是實機觀察。`0x2210` 先讀 payload+1 的低 byte，`0x2214` 再讀 payload 的高 byte，指令重排後 page = `(high << 8) | low`。同一次取樣的兩個 byte 可組成 `0..65535`，不假設 payload 不會被其他執行者改寫。

## 算術及 API 邊界

* `0x222a..0x2240` 算 `D = ((0x20020 + page) << 10) mod 2^32`，並以 unsigned 比較 `(D + 0xf7ff8000) mod 2^32 <= 0x17f00`。對完整 u16 域窮舉，恰好 page `0..95` 通過；96、256、65535 不通過。最大 u16 時 D 為 `0x0c007c00`，因此此域目的位址計算本身沒有 32-bit 溢位；不能將此結論推廣到非 byte 組成的任意 page。
* 通過時 D 為 `0x08008000..0x0801fc00`，每頁四次呼叫 `0x20e6`，`a0=D+{0,0x100,0x200,0x300}`，`a1=aligned_source+相同 offset`（32-bit 算術）。所有通過頁的數值程式寫入 word store 涵蓋聯集 `[0x08008000,0x08020000)`，最後一 byte 是 `0x0801ffff`。例如 page 74 涵蓋 `[0x0801a800,0x0801ac00)`；page 95 涵蓋 `[0x0801fc00,0x08020000)`。
* wrapper 將相同 a0 傳至 `0x3016` erase 和 `0x3044` program。既有靜態鏈顯示 erase 將 a0 下對齊 256，寫數值 address register `0x40022014`；program 同樣以 256 對齊目的，對 offset `0..252` 作 64 個 4-byte store。在 W 路徑四個 a0 本來就 256 對齊。這些是**寄存器請求與 store 位址**，不是實際擦除範圍：控制器擦除粒度、別名及完成狀態仍未知。呼叫可能等待、失敗或不返回；四次皆到達亦為條件。
* source 為 `(payload+2) mod 2^32`，再向下對齊 4。未對齊時先透過 `READ32(0x4004c)` 載入的指標請求複製 1024 bytes；重疊及 provider 的真實效果未知。source 加法、四個 a1 與後續 word 位址均可能在 32-bit 回繞；例如 payload `0xfffffffd` 的 source 是 `0xffffffff`，aligned 為 `0xfffffffc`，下一個 a1 回繞為 `0xfc`。這只描述數值，並不宣稱該地址可讀、複製成功或真實 caller 能傳入。
* readback 逐 word 先讀目的再讀 live source，不相等即靜默返回。數值回讀／回覆條件不證 Flash 持久化、整個映像完整或原機可啟動。

## 重播與界限

```sh
python -B analysis/boot2580-w-range-2026-11-01/check.py
```

測試包含固定全檔與四視窗、每視窗各一 byte 突變負例（獨立於全檔 hash gate）、65536 個 page、四次參數、首末 byte、active／長度／頁碼反例，以及 source 對齊和 `2^32` 回繞。測試不執行原始 ISA、不模擬 Flash 控制器，且只在上述正常返回假設下驗證算術；也不證實安裝版本、實體 MCU、Flash 容量／別名／擦除幾何、匯流排行為、IRQ、電源中斷或實際寫入。未連接設備、未刷寫、未產生封包。
