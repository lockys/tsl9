# Flash quarter 的其他數值目的地

[English](readme.en.md)

固定 ID2966／V4.1.60 原始 BIN（SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`）有六個其他直接呼叫 `0x9C0A` 的片段。每段包含 LUI、C.MV、ADDI、JAL，共 14 bytes；六段合計 84 bytes／24 條指令。

| JAL 原始 PC | A0 數值目的地 |
| --- | --- |
| `0x12E7A` | `0x08077900` |
| `0x12F0C` | `0x08077800` |
| `0x12F6E` | `0x08077700` |
| `0x13078` | `0x08077600` |
| `0x130FC` | `0x08077500` |
| `0x1315E` | `0x08077A00` |

各片段在 JAL 前將當時 SP 放入 A1，將常數算入 A0，並把 RA 設為呼叫 PC+4。這是條件式靜態資料流；不證明正常執行一定到達、實體 SP 值、來源緩衝內容、設定功能或 Flash 寫入成功。

**通用 quarter helper 不能新增 OTA 接收器的位址限制。** 這些目的地在兩個已封存的接收器數值範圍之外：BOOT 接收 Runtime 的 `0x08008000..0x08020000`，以及 Runtime 接收 BOOT 的 `0x08001000..0x08008000`。範圍來自原始分支條件；它們不是晶片實體 Flash 容量或映射的量測。這些高位址也不能反過來確認晶片、板子或安全可寫空間。

`report.json` 的 60 個實際 raw 變異先通過語意拒絕測試，再檢查原始全檔案雜湊。`compiled-crosscheck.json` 另保存已觀察到的完整來源映像 ELF 核對：六段及其整個 owner 都與原始 bytes 相同，並從真實 section-backed FUNC entry 逐步核對 16／32-bit 指令邊界。這是寬度與資料核對，不是 ISA 模擬或動態可達性證明；不能假裝未被 assembler 保留的局部標籤仍存在。

使用 `python callers/inspect_callers.py --project-root <project> --check` 重查原始來源及封存證據；加 `--elf <actual-linked-ELF>` 才額外核對該實際編譯產物。省略 ELF 時不宣稱已重播封存 ELF。沒有網路、真裝置識別資料、原程式執行、模擬器、硬體或新 BIN 操作。
