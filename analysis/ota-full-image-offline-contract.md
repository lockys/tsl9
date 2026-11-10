# ID2966 全影像離線契約與缺口

本次唯讀比較本機標示的 ID2966 V4.1.60 解碼 BIN 與 TX integrated 候選；不認證原廠來源，不使用設備、不執行 APK、BOOT 或 MCU。候選以 `artifacts/offline-images/ID2966-V4.1.60-tx-integrated/NOT-FLASH-VALIDATED-tx-integrated.bin` 明確限定，並非其他候選或新鮮重建輸出。兩者 SHA-256 分別為 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`、`28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89`。

| 範圍 | 固定 bytes／離線結果 | 未證明的部分 |
|---|---|---|
| 首 byte／長度 | 均為 `6f`、76,800 bytes。保存的 ID2580 BOOT 一般 startup 有首 byte guard；另有不同 selector 路徑。 | 首 byte 不是全影像驗收；實機 BOOT 身分、跳轉後執行未知。 |
| 全影像 | 全部 76,800 bytes 逐 byte 對照，共 93 bytes 不同，全在映像位址 `0x8a7f..0x8a80`、`0x8ad3..0x8ad4`、`0x8b11`、`0x8b13..0x8b5b`、`0x8b5d..0x8b6b`；其餘包括先前排除的 OTA 載體範圍均相同。基址 `0x8000`。 | 位元組差異集中不等於執行等價；不證明 ROM、RAM、IRQ、ABI、裝置相容。 |
| 合成分頁 | 將各映像切成 75 頁，各加 BE16 頁號為 1,026 bytes；總計 76,950 bytes。兩影像僅第 2 頁不同。頁資料含索引加總 mod 65536 分別為 31872、32058。 | 這是由本機 BIN 合成，非截取的伺服器回覆；原 APK 不硬編碼此頁大小。實際伺服器 PageCount、BytesCount、CheckCode 和頁面未認證。 |
| 合成 W envelope | 按 APK 靜態證據合成 `55 7f 57 04 02 | page | sum8`，共 1,032 bytes；逐頁 round-trip。 | 不是擷取的 BLE 流量或 APK 執行；fragmentation、重試和設備接受未驗證。 |
| 更新完成 | 保存的 BOOT 路徑及 APK 回覆檢查已在下列既有分析界定。 | APK 的 R 可接受非空相符前綴；E 回覆並非完整影像完整性證明。實機 BOOT、完整讀回、重新啟動和復原未知。 |

執行 `python -B -m unittest discover -s tests -p test_ota_full_image_contract.py -v`。測試固定兩個本機檔案完整 SHA、核對全部差異、重組頁、頁 index/長度/數量/加總與 envelope；負例涵蓋截斷、增頁、換序、單 byte、首 byte、wire header/checksum。合成的相反兩 byte 修改仍通過加總，顯示加總不能取代 digest。固定 digest 是本地回歸基準而不是簽章。測試需要本機提供上述原始參考檔，缺檔會失敗而非跳過。

上述 APK 和 BOOT 敘述是先前靜態分析的限定結論，並非本測試的執行結果。此契約測試本身不重新建置；新鮮替代建置及其隔離驗證見 [原廠 TX 替代候選](original-tx-alternative-NOT-FLASH-VALIDATED.md)。**不得將本結果表述為可安全刷寫或 OTA 驗證。**
