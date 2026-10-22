# 旗標到接收流程：離線靜態分析

[English](readme.en.md) · [來源片段與雜湊](source-spans.json) · [C/C++ 驗證](../../experiments/tsl9-irq-flag-consumer/README.md)

**已確認於這些原始碼範圍：** `17002` 清除旗標後以 channel 1／2 呼叫 `16B0A`；後者讀取 register `0x2C`，以同一 status 快照的 bit0／bit1 決定讀 `0x61`／`0x71`，最後寫 `0x2C=0`。channel 與接收 buffer 選擇是不同層級。

`16994`／`16A30` 分別以 `03`／`02` 加位址進行讀寫；下游 `16896` 對 `0x40013008`／`0x4001300C` 做 16-bit MMIO。兩段輪詢各最多 255 次，timeout 回傳 0；這不代表成功讀到值 0。

`16A7C` 接收 13 bytes，經格式檢查後呼叫 `12BC8`。後者使用 `0x2000C038` 起的 32×12-byte slots，並從 `0x4004C` 取得間接 provider；尚未確認 installed provider，不能直接以一般 `memcpy` 取代。

**重建限制：** 旗標消費候選的非呼叫 54 bytes 相同，兩個 JAL 尚未解析。SPI 候選編譯為 74B／26 指令，原始是 72B／25 指令，未通過全文相等檢查，未納入 `src/`。未證明完整接收鏈、實體晶片型號、IRQ／ROM ABI 或可燒錄性。

`source-spans.json` 固定七段共 586 bytes／210 指令寬度列，保留原始 bytes 與檔案 offset；此範圍分析不構成完整函式邊界或所有間接入口的證明。沒有執行 RV32、MMIO 或操作硬體。
