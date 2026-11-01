# 有限窗口的 BOOT 與映像形狀核對

[English](readme.en.md)

[檢查器](check.py)重新核對保存的 ID2580 候選 BOOT 的 14 個指令錨點；只讀取原廠 ID2966 與 TX 候選的 APP 首 byte 和檔案大小。兩個 APP 均為 76,800 bytes、首 byte `0x6F`；按既有 BOOT 分析的 1,024-byte 頁與 0–95 數值頁面限制，75 頁的索引 0–74 均落在限制內。每頁加兩個索引 bytes 為 1,026 bytes。

這是**對照已分析候選 BOOT 的形狀條件**，不是實機安裝 BOOT 的辨識、完整檔案相等、簽章／完整性、可正常燒錄或重啟成功的證據。原始指令與頁面上限的語義依據為[既有 BOOT 審查](../../analysis/v4160-tx-image-integration-2026-10-22/image-plan/README.md)，本檢查器固定錨點但沒有重新反組譯。沒有讀取其他 APP byte 或排除範圍、沒有執行目標或連接硬體。

執行：`python -B experiments/tsl9-bounded-boot-shape/check.py`。
