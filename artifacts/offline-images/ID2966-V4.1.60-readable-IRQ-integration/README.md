# 尚未驗證可刷寫的 IRQ 整合映像

[English](readme.en.md)

`NOT-FLASH-VALIDATED-irq-callframe.bin` 是離線來源重建產物，**尚未驗證可由原藍牙 OTA 刷入硬體，請勿以此當作可刷寫版本**。

- 大小：76,800 bytes。
- SHA-256：`47f200dce24be25ac89d57922689da536259935e8615ba8195b10ca192895e1c`。
- 原始比對：ID2966 V4.1.60，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。
- 僅 IRQ 初始化及四個 RCC helper 由可讀 C/C++ 取代；其他內容保留原始指令／資料載體，並非完整反編譯來源。
- 與原始相差八個 bytes：`0x9A44..0x9A4B`，為四個暫存器保存指令的順序。逐時點與非同步中斷等價仍未知。
- resident ROM 只指定 `0x40000` 的數字位址，未供應 ROM 實作。硬體、執行期、啟動、更新器接受性與實體燒錄仍未完整證明。

[來源、重建入口與分開的獨立審查](../../../analysis/v4160-irq-image-integration-2026-10-21/readme.zh-TW.md)。原始 APK、22 份廠商 BIN 與先前來源一致映像均保留原樣。
