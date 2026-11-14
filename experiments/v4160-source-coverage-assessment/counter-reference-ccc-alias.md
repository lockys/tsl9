# 條件式參考 CCC 初始化與 counter 重疊

`counter-reference-ccc-alias.py` 固定原 APP、WCH V1.31 **參考候選** carrier 的雜湊及局部原始編碼；`0x8fb6` 前 APP 設定 `a0=0xffff`、`a1=gp+128`，而參考候選 `0x40138` 指向 `0x4cfd0`，其全表分支進入 `0x4b33c`。根據既有 `experiments/tsl9-resident-gatt-CCC-write/` 的條件 Xwchc 解讀，每筆 4-byte record 依序寫入 `ff ff 00`，不寫 padding。程式的記憶體投影窮舉 256 個合成容量，每個核對 255 筆 record。

若 GP 仍為 `0x20004000`，表起點就是 `0x20004080`，counter `0x200040b0` 正好是第 12 筆（零起算）的第一個 byte。因此在所有下列條件同時成立時，容量至少 13 會將初始值 1 改為 `0xff`，得到局部 `0..3` 不變量的**條件性反例**：實際 slot 和語意與該候選相同、Xwchc 解讀正確、呼叫可達、有效容量足夠、存取成功且無競態。容量小於 13 則此次合成清除不碰 counter。

這不是裝置實際 ROM、容量或路徑的證明，也不是 CPU 執行或新 byte 覆蓋。候選 carrier 缺失時程式明確回傳非零 SKIP，不將缺失當作通過。
