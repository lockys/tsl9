# ID2580 BOOT event 回溯：有限 raw store 掃描（未閉合）

後續 [event continuation](../boot2580-w-event-continuation/README.md) 已定位 alias store 與候選 handler，亦更正下文當時工具不可用的描述；以下保留原有限掃描與其負結果，不代表目前進度。

原始檔 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2580-V1.0.00-decoded.bin`；長度 12288、SHA-256 `650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb`，以 base `0x1000` 做分析座標。沿用 [既有尾呼叫](../boot2580-w-downstream-offline/README.md)：`18c6 03a30705` 載入 `[0x40050]`，`18ca 03c5c107` 為 `lbu a0,124(gp)`，`18ce 8545` 設 a1=1，`18d2 0283` 跳轉。是否為 task ID/event 僅在該槽與 SDK 候選 ABI 一致的條件下成立。

新增 `check.py` 對整個原始檔每個 2-byte 對齊位置掃描 **32-bit RV32 S-type `sb`/`sh`/`sw`、rs1=gp**，檢查所寫 byte 範圍是否包含 gp+124；結果 **零筆**。掃描不區分指令或資料，也不要求指令邊界；這是編碼模式的有限負結果，不是沒有 writer 的證明。尤其不排除 alias 基址、不同 gp 值、間接存取、compressed 指令、其他執行映像或 provider 寫入；尚未確定 GP 對應 RAM 的初始化與生命週期。不能由零筆推定未註冊或 task byte 不會變動。

`python -B analysis/boot2580-w-event-scan-offline/check.py` 通過兩項測試：固定影像 hash 與尾部 raw bytes，並對 byte/halfword/word 覆蓋的合成正例及不重疊、其他 base、load、保留 funct3 的反例測試掃描器；另測試突變 hash 不符。這些是靜態模式測試，非 ISA 執行、分派或硬體測試。

**尚未完成：** task registration、event handler、buffer 讀取及其下一 provider 尚未定位，無法閉合題目要求；實際 `[0x40050]` 內容亦不可見。現有環境未提供 REA MCP、`rea` CLI 或 RISC-V 反組譯工具；未下載或連線。後續需離線取得可用反組譯工具或完整原始 BOOT 指令記錄，追蹤 gp 初始化、註冊槽與 indirect callbacks，再以原始影像固定各指令及正負測試。未接設備、刷寫、執行目標或觀察回覆；不假定 SDK resident、傳輸、ACK 或持久化。
