# 原始暫存器／保存順序一致的完整離線映像

[English](readme.en.md) | [繁體中文](readme.zh-TW.md)

`NOT-FLASH-VALIDATED-register-scheduled.bin` 為 76,800 bytes，SHA-256：

```text
0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667
```

它與封存的官方 ID2966 V4.1.60 逐 byte 相同。兩條生成鏈分別以 C11／C++17 新編譯 42 個單元，再經明確的 ABI 保存順序處理、連結與匯出。11 個可讀函式共 526 bytes，其餘內容仍為原始承載資料；這不是完整來源重建。編譯器單獨輸出與最後排程後物件均保留，不能將兩者混稱。

生成沒有以原始 BIN 回填、補洞、貼回函式或供應 ROM。原始 BIN 只作核對參考；既有承載資料則是有來源身分的 C 檔與重定位宣告。完整流程與限制見[整合說明](../../../analysis/v4160-register-image-integration-2026-10-22/README.md)，保存順序規則見[獨立工具](../../../experiments/tsl9-v4160-frame-schedule/README.md)。

**尚未驗證可刷寫。** 原機 ROM、已安裝 BOOT、確切晶片／板子、實體中斷與 Flash 行為、BLE 更新接受性與失敗復原均未確認。此檔不構成刷寫建議；沒有執行或模擬 RV32，也沒有接觸實體裝置。
