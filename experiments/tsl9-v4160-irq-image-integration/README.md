# IRQ 來源整合映像輸入

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

`source-manifest.json` 固定原始載體的 691 筆配置中繼資料與符號角色、34 個載體編譯單元、
73 個原始程式及標頭的雜湊、53 個區段相對標籤，以及已覆核的 8270 筆區段外重定位摘要。
`original-image-layout.ld` 是歷史完整 691 區段配置的逐位元組相同副本，SHA-256 為
`651a8f14d09e373cb5523ec12f97d1fcce3ff26a51b3d835ae55d0239945507b`。

`prepare_manifest.py` 記錄一次性的歷史證據抽取，需要原始封存檔，並非重新建置入口。
全新建置只需已發布的清單與配置、固定的 startup 程式、可讀 callframe 程式與證據、原始離線
參考映像及本機 LLVM。新流程不連結歷史物件，也不以舊位元組補救編譯失敗的區段。

請使用 IRQ 映像案例內另有說明的 `integration/verify_image.py`。
`build/` 保留本機物件、依賴檔、日誌、收據、ELF 位址見證及新匯出的映像，不隨文件發布。
五個型別化函式共 264 bytes；其餘內容仍為擷取的原始載體，不代表完整還原應用程式原始碼。
尚未證明可燒錄、實體相容、非同步等價或 OTA。
