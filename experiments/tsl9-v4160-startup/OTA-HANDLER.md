# ID2966 的 OTA 命令執行片段

本輪增加原始 900 bytes code、6 個實際片段、70 項 RELA、7 個 private NOTYPE0／size0 標籤。來源為 `9C4A` 的 U/S/W/R/E 命令 CFG，以及 UID、頁面回覆與延遲 callback 的必要相依。未增加 RO、RAM views 或資料載體；原有 31 個 UND 全保留。

完整 C11/C++17 整合通過：63,222 code bytes、3,676 RO bytes、620 個非空配置、7,308 項 RELA、665 個 module providers、3 個 code views、1 個 data anchor。原 614 個配置與所有 7,238 項 RELA／符號 metadata 均保留；新增 36 個實際負例均拒絕。`native-v2` 修正 code-view 必填欄位的描述，C/H 原指令與 v1 完全相同，未改 frozen engine。

新增 `13B4C` code view 沿用原 `.text.tsl9v4160.conditional_runtime_13b4c` 的 90-byte storage，offset0；以舊 `conditional-runtime` 中 root13E98 的原指令 `7971` 作為入口邊界證據。它不是新增 storage 或 FUNC／C ABI 宣告，沒有重出原 bytes 或用另一個跨 section symbol 假冒入口。

原檔靜態可追到 record19DFC+4 的 pointer888C，候選 GATT 註冊後的接收／frame parser 路徑為 `888C → 8A48 → 14056 → 14094 → 9C4A`。本輪新增 native storage 只涵蓋命令本體與必要相依，不宣稱上述整條鏈都已納入此 partial，也不因 SDK 名稱而假定 resident 確實使用該 callback ABI。原 19DFC canonical 及 ROM contract 繼續未知。

W 的四次 256-byte program 使用既有真實 `9C0A` 64-byte body，含 CSR0x800/mask136、status49 與 Flash primitives。這與 `197BE` 的配對資料 storage hook 不同。新 W 成功回覆為 BE16 page + 1024-byte Flash copy；mismatch 回一 byte255。E 重新檢查 strict15/mode0/UID14，R 另有 strict16/UID14 且沒有 W 的 page<=27 guard。可讀語義另見 `../tsl9-v4160-ota-contract-model/`。

```powershell
python -X utf8 -B verify-data-anchor-extension.py --spec evidence/ota-handler-integration.json
```

`re-tsl9` 預設使用其內部原 ID2966 BIN；分析工作區需加 `--firmware <原始BIN絕對路徑>`。ROOT 完整收據為 `build/data-anchor-extension-674b00a38c9f45b1a783ca47e4a38b4a/verification.json`，目的地重新編譯另有交付收據。

這些 C/C++ translation units 承載保留的 RV32 指令，不是完整高階原始碼恢復。`ADDRESS-WITNESS-ONLY.elf` 只證原數值位置，不是 OTA BIN。硬體、原 ROM／IRQ、memory/stack、BOOT 適用性、真實傳送與更新復原尚未證明；未執行或模擬韌體、未操作硬體、沒有可燒錄宣稱。
