# 新 TX 完整映像的布局與 BOOT 形狀核對

[English](readme.en.md)

這項檢查讀取原始 ID2966、重建候選 BIN 與保存的候選 BOOT ID2580，確認本次替換的範圍及既有軟體條件。它不產生韌體、不傳送封包，也不連接硬體。真正的 C/C++ 來源、完整 ELF、呼叫與重定位證據由本輪 implementation、source-review 及 ABI-review 分別提供。

## 明確的檢查範圍

- 原始 ID2966 為 76,800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。
- 候選必須同樣完整；只有 VA `0x8A56..0x8B6E`、檔案 offset `0xA56..0xB6E` 的 280 bytes 可以不同，其餘每個 byte 都必須相同，包括入口及尾端資料。它不以補零補齊不完整映像。
- 保存的 ID2580 BOOT SHA-256 為 `650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb`。新檢查重讀 14 個來源指令 byte 錨點，包含 1026-byte W 長度條件、無號頁面界線及 APP 首 byte `0x6F` 的弱條件。
- 已有 BOOT 的來源契約只證明頁資料 1024 bytes、BE16 頁碼及數值頁範圍 0..95。本次候選可拆成 75 頁、頁碼 0..74，不需要尾頁補齊。軟體位址公式為 `0x08008000 + index*1024`；這不是實體 Flash 別名的證明。
- 輸出每頁 SHA-256 及「兩個頁碼 byte 加上頁資料」的 sum16，供離線交叉核對。它不生成完整 OTA frame、UID 或身分命令；也不把這些計算當成 Flash 讀回。

五個實際 byte／長度反例必須被拒絕：入口外側變動、尾端變動、短一個 byte、多補一個 byte，以及 BOOT 首 byte 比較立即數的變動。單獨通過此檢查不證明被允許的 TX 區域就是合法程式碼，仍需真正來源及 ABI 檢查。

## 可重跑指令

在交付或發布目錄中：

```sh
python3 -B analysis/v4160-tx-image-integration-2026-10-22/image-plan/verify-layout.py --original /absolute/ID-2966-V4.1.60-decoded.bin --candidate /absolute/NOT-FLASH-VALIDATED-tx-integrated.bin --boot /absolute/ID-2580-V1.0.00-decoded.bin --receipt /absolute/new-layout-receipt.json
```

研究工作區的入口位於 `apk-analysis/tsl9-v4160-tx-image-integration-2026-10-22/image-plan/`。收據使用 create-only 寫入；三個輸入檔案不被修改。

## 仍然不能證明的部分

候選 BOOT 的來源事實繼承自 `v4160-ota-handoff-2026-10-21/boot-acceptance`，其 facts 與 source-map 雜湊記錄在新收據。這裡重讀保存的 BOOT 與指定原碼錨點，沒有重做完整 BOOT 語意，也沒有證明它是原機目前安裝的版本。

完整映像的 CRC／簽章政策、ROM、硬體 SKU、真實 Flash／RAM、BLE 時序、14-byte 身分資料、更新後重啟與復原仍須另外證明。入口首 byte 正確、頁面數正確及所有本機檢查通過，都不等於 OTA 可用。沒有執行或模擬 RV32，也沒有廠商 API 請求。
