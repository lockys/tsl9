# IRQ 與 Flash 可讀來源的離線候選 BIN

[English](readme.en.md)

`NOT-FLASH-VALIDATED-irq-and-flash.bin` 為 76,800 bytes，SHA-256 是 `de159bb345b27250a683e197dd84b04e51a7a7ed89315347395baaea53f68be1`。這是 C11／C++17 實際重新編譯十一個可讀函式及其餘原始載體後的完整映像，並非完整原始碼還原；相較官方映像共有 70 個 byte 不同。

**目前尚未驗證可刷寫，請勿把離線建置成功當成原硬體或 BLE OTA 相容性證明。** 成功連結僅使用數字 ROM 位址見證，嚴格 ROM provider gate 仍失敗；原機 BOOT、晶片／板子、非同步 IRQ 與完整 fault prefix 尚未證明。沒有進行任何韌體執行、ISA 模擬或實體操作。

完整來源、重定位、區段／LOAD、獨立審查與限制見 [繁體中文分析說明](../../../analysis/v4160-flash-image-integration-2026-10-22/README.md)。原始官方檔、前輪候選與已封存證據均保留。
