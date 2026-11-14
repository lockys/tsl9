# `0xf7` 零物件至參考 allocator 的分段組合

`case_f7_reference_alloc_composition.py` 條件性串接已固定的 APP 前置、零物件尾跳和兩份參考 carrier 的 allocator 入口。固定 `[gp+358]=0`、物件 word=0、slot=`0x20000236`，對每份 carrier 測 256 個狀態 byte 與五個 a1；狀態 bit 3 為零的 640 組在模型中到達 helper 邊界 `(20, 0xf00c)`，其餘 640 組在 APP 前段返回。兩種 Python 模式皆通過。

這些段落均為獨立手寫投影，不是連續 CPU 執行；假設候選資料已正確複製進 RAM、狀態穩定、讀寫成功且無干擾性別名或中斷。沒有證明 APP 上游可達、實際 resident 身分、helper 副作用或完整功能等價。缺少任一參考 carrier 為 SKIP 並以非零狀態結束。
