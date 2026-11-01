# 有限窗口的 BOOT 與映像形狀核對

[English](readme.en.md)

[檢查器](check.py)重新核對保存的 ID2580 候選 BOOT 的 14 個指令錨點，以及原廠 ID2966 與 TX 候選的 APP 檔案大小。兩個 APP 均為 76,800 bytes；按既有 BOOT 分析的 1,024-byte 頁與 0–95 數值頁面限制，75 頁的索引 0–74 均落在限制內。每頁加兩個索引 bytes 為 1,026 bytes。

兩份 APP 的第 0 頁 `[0x8000,0x8400)` 與 reset 窗口 `[0x186AA,0x18734)` 分別逐 byte 相同，雜湊依序為 `90f03cc6687486011333937ddecd72767f464560f8039d66114ecf9e30250fe0` 和 `9507502c874a03e2c64a28b186a1f56aba9e85c9989dbf0cc053dabc4045bb4d`。以 APP 名目基址 `0x8000` 解碼，入口 `JAL x0` 指向 `0x186AA`，reset 尾部 `JAL x0` 指向 resident `0x40000`。兩個視窗的一致性不證明 reset 被執行或 resident 在實機存在且相容。

這是**對照已分析候選 BOOT 的形狀條件**，不是實機安裝 BOOT 的辨識、完整檔案相等、簽章／完整性、可正常燒錄或重啟成功的證據。原始指令與頁面上限的語義依據為[既有 BOOT 審查](../../analysis/v4160-tx-image-integration-2026-10-22/image-plan/README.md)，本檢查器固定錨點但沒有重新反組譯。沒有讀取其他 APP byte 或排除範圍、沒有執行目標或連接硬體。

執行：`python -B experiments/tsl9-bounded-boot-shape/check.py`。
