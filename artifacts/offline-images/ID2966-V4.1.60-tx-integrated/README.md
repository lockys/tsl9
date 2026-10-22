# TX 整合實驗 BIN：尚未驗證可刷寫

[English](readme.en.md)

`NOT-FLASH-VALIDATED-tx-integrated.bin` 是本專案由 C11 與 C++17 各自重新編譯而得、逐 byte 相同的完整實驗映像；不是官方下載檔，也尚未經實體硬體或 BLE OTA 驗證。

- 長度：76,800 bytes。
- SHA-256：`28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89`。
- 官方參考：ID2966 V4.1.60，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。
- 與官方檔案的 93 個差異全部位於 TX `0x8A56..0x8B6E`；其餘 byte 相同。
- 十三個原始函式範圍共 930 bytes／十五個配置 FUNC 角色；678 個其餘區段仍使用原始承載。這是部分來源重建。

檔案由本輪正式 producer 的 C／C++ 一致產物複製，不覆寫官方 22 份 BIN。[完整來源與獨立審查](../../../analysis/v4160-tx-image-integration-2026-10-22/README.md)說明來源、配置、重定位、呼叫及頁面形狀證據。ROM／BOOT 身分、實體 Flash 別名、完整 ABI、CRC／簽章規則、OTA 與失敗復原仍待證。此檔供離線研究，尚不具可刷寫結論。
