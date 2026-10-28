# 條件 mode 1／3 查表資料

[English](readme.en.md) · [正式 src 與原位址整合](../tsl9-record-mode-row-integration/README.md)

從原廠 APP 的 `[0x1A088,0x1A098)`、`[0x1A0A8,0x1A0B8)` 各取 16 bytes，建立兩個 C 常數陣列。C11／C++17 實際物件相同，無 CODE、import、重定位或完整 provider alias；每一資料 byte 均與原廠區段相同。

本目錄保存正式來源擴充前的固定實驗快照：當時父來源為 162 檔，native partial component 為 69,412B CODE＋4,098B DATA。後續已納入正式 `src/`；目前重播入口請用上方整合文件。舊實驗 verifier 固定舊 manifest，不能將更新後的 manifest 漂移當成歷史證據已重跑。

使用條件及未知項見 [寫入來源](../tsl9-mode-state-writer-contract/README.md)。局部 mode 1～5 不等於全域值域，兩列 backing 不等於完整查表 provider，也未證明實體 RAM／ROM／IRQ／OTA 相容性。未讀取整個保守 DATA 包絡或排除 payload，未產生可刷寫 BIN。

[C/C++ 原始定義](mode_rows.v1.c) · [固定輸入](inputs-v1.json) · [原生實驗收據](verification-v1.json)
