# OTA 真實 C 接線實驗 BIN — 尚未驗證可刷寫

[English](readme.en.md)

`NOT-FLASH-VALIDATED-ota-source-wired.bin` 是離線編譯／連結產物，**不是已驗證可由原 BLE OTA 刷寫的韌體**。已確認 C11／C++17 產出相同 bytes。

| 欄位 | 值 |
|---|---|
| 檔案長度 | 77,824 bytes／76個1,024-byte頁 |
| SHA-256 | `3be918942c03de99c8a5f3fb7d6eba40ab9af63930020efb7f4cac07cc9a10ee` |
| 繼承的 TX 整合映像 | 76,800 bytes，SHA-256 `28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89` |
| 原 caller | `0x14094` 的 JAL 到真實 C `0x1AC00`，RA `0x14098` |
| 繼承範圍差異 | 僅 caller 指令中的3 bytes |
| 尾端新增 | 可執行 C568、明示非執行 FF456頁尾 |

原 handler530 bytes保留，其他大量程式仍是原始 carrier；此 BIN 不是完整重寫的原始碼成果。部分連結保持真 ROM UND；完整 ELF 的 `0x40000` 為原指令已指向的數值地址見證，不提供 ROM 實作。

Flash／NV 所有權、實體 ROM／BOOT／RAM、中斷／callee／堆疊 ABI、更新器接受與失敗恢復仍未證實。測試沒有執行 RV32 或接觸 BLE／UART／CAN／Flash。這份檔案不應被當成刷寫相容性證明。

[程式與靜態證據](../../../analysis/v4160-ota-source-wiring-2026-10-22/README.md) | [可讀模型](../../../experiments/tsl9-v4160-ota-source-wiring/README.md)
