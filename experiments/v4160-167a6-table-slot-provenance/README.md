# V4.1.60 `0x167a6` 表格指標槽：離線來源證據

本實驗只讀原始 ID2966 映像，不產生或修改韌體。檔案 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin` 固定長度 76,800、SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。本文位址是分析位址，檔案 offset = 位址 − `0x8000`，所有區間為半開。

## 來源與獨立審核

`verify.py` 直接從映像擷取後固定精確 bytes：reset `[0x186aa,0x186de)`、初始化三個 word `[0x1abc0,0x1abcc)`、使用者迴圈 `[0x167a6,0x16846)`；不是以來源碼或反組譯結果重建 bytes。額外以 radare2 6.2.4 對原始映像、分析 base `0x8000` 獨立逐指令審核，並對照既有 [reset 路徑紀錄](../../analysis/resident-startup-continuation-static.md)。反組譯不屬於執行 verifier 的依賴；verifier 比對 bytes 而不自動證明指令語意。

審核重點：`0x186aa/ae` 形成 GP=`0x20004000`，`0x186ba/be` 形成來源 `0x1ab60`，`0x186c2/c6` 設目的 GP 與結束 GP+128，`0x186ca..da` 逐 word 複製。若該路徑與記憶體操作正常完成，來源 `0x1abc0` 的三個小端 word 即分別複製至 GP+`0x60/64/68`：

| 槽 | 初始值 |
|---|---|
| `0x20004060` | `0x2000c494` |
| `0x20004064` | `0x2000c594` |
| `0x20004068` | `0x2000c694` |

`0x167ba..da` 的第一迴圈使用第一槽，offset 為 0,2,…,252；每次讀取 offset，只有比較符合才讀 offset+1，因此條件最大為 **+253**。`0x167de..16842` 使用另兩槽，各以 offset 7,14,…,245 讀取兩個 byte，最大 **+246**。以上只描述此函式內的直接讀取；到達最後一次、初始指標仍保持、記憶體有效、被呼叫者及非同步事件不破壞相關狀態等均為條件，並不證明 buffer 實際大小、內容、存取成功或 runtime 狀態。

## 全映像 raw 掃描與邊界

對完整映像每個 2-byte 對齊位置（含資料及可能位於其他指令中間的 bit pattern），若有完整 4 bytes，辨認標準 RISC-V opcode `0x23`、rs1=`gp`、funct3=SB/SH/SW，將 S-immediate 符號延伸並以寬度 1/2/4 計算位元組覆蓋。覆蓋任一 GP offset `[0x60,0x6c)` 的結果為空。這是保守 raw pattern 篩選，不判斷可執行性或實際 GP 值；不涵蓋其他 base、計算後別名、compressed/custom 指令、外部程式、DMA、resident、硬體或記憶體初始條件，**不能推論全域 writer 完整性或槽永不改變**。

## 重現

在 repo 根目錄以 Python 3 執行：

```sh
python -I -S experiments/v4160-167a6-table-slot-provenance/verify.py
python -O -I -S experiments/v4160-167a6-table-slot-provenance/verify.py
```

上述相對路徑命令需在 repo 根目錄執行；亦可提供腳本絕對路徑。自測涵蓋所有 4096 個有號 immediate、三種寬度、兩個半字對齊位置、錯誤 base、截斷和奇數對齊；每個固定視窗每一 byte 都做獨立變異負例，另測映像 hash 變異。檢查不使用 `assert`，最佳化模式仍有效。無編譯器、target、模擬器、硬體、網路或環境設定需求；此結果不是執行或刷寫驗證。
