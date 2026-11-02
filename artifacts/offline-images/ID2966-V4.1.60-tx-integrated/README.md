# TX 整合實驗 BIN：尚未驗證可刷寫

[English](readme.en.md)

`NOT-FLASH-VALIDATED-tx-integrated.bin` 是本專案由 C11 與 C++17 各自重新編譯而得、逐 byte 相同的完整實驗映像。2026-10-22 已有使用者回報以 tsl9-morphe APK 更新此檔，最後顯示與原廠對照相同的「E 回覆已收到、所有頁讀回相符；版本重啟尚未驗證」。這是本候選的實機 OTA 會話／讀回回報，完整原機相容與重新啟動後的程式執行仍未確認。

## 使用者實機回報

[field-observations.json](field-observations.json) 區分本機檔案比對、原廠截圖與使用者候選回報。提供的截圖實際選取原廠 `ID-2966-V4.1.60-decoded.bin`；使用者隨後明確指出本候選也得到相同的最後訊息。尚無候選那次的選檔 SHA／原始傳輸紀錄，因此不將原廠截圖當成本候選的逐 byte 傳輸證明。

原廠更新後仍顯示 V4.1.00、但座椅功能確有變動，是使用者另外提供的觀察，未歸因於本候選。版本顯示不能單獨識別實際映像；E 也屬於更新結束回覆，不能單憑它判斷新 runtime 已啟動。[協定與版本證據](../../../docs/ota-e-response.zh-TW.md)另行記錄。

檔名與原始 `provenance.json` 保留生成當時的未完成驗證狀態；新觀察附在本文件及 field-observations，不改寫舊 producer 證據。

## 檔案與靜態證據

- 長度：76,800 bytes。
- SHA-256：`28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89`。
- 官方參考：ID2966 V4.1.60，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。
- 與官方檔案的 93 個差異全部位於 TX `0x8A56..0x8B6E`；其餘 byte 相同。
- 十三個原始函式範圍共 930 bytes／十五個配置 FUNC 角色；678 個其餘區段仍使用原始承載。這是部分來源重建。

檔案由本輪正式 producer 的 C／C++ 一致產物複製，不覆寫官方 22 份 BIN。[完整來源與獨立審查](../../../analysis/v4160-tx-image-integration-2026-10-22/README.md)說明來源、配置、重定位、呼叫及頁面形狀證據。ROM／BOOT 身分、實體 Flash 別名、完整 ABI、CRC／簽章規則、完整 OTA 相容性與失敗復原仍待證；使用者會話與頁面讀回回報如上。此檔尚不具一般可刷寫或完整相容結論。
