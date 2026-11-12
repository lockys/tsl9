# V4.1.60 `0x131c2` 六筆讀取：非正式語義候選

本目錄僅為離線、非正式候選；不整合至產品。固定檔案 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，長度 76,800，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。位址減 `0x8000` 為檔案 offset；`verify.py` 固定完整半開窗口 `[0x131c2,0x1330a)` 的 328 bytes，及 `candidate.c` 原始檔 SHA-256 `b89d8552a4270c5ea2a6672ce7f2c88867f878d9c98c60a6f5d09c061a85b38f`。固定 bytes 不等於對指令語義的自動證明；參照既有 [六筆記錄分析](../tsl9-NVM-record-layout/README.md) 與 [table 證據](../v4160-131c2-table-init-provenance/README.md)。

| 順序 | source 數值 | destination 數值 | 長度 | guard | default target |
|---|---|---|---:|---|---|
| 0 | `08077a00` | `2000c29c` | 112 | +12..+15 每 byte 在 32..126 | `1316a` |
| 1 | `08077900` | `2000c494` | 256 | +255 等於 `5a` | `12e86` |
| 2 | `08077800` | `2000c30c` | 256 | +255 等於 `5a` | `12f18` |
| 3 | `08077700` | `2000c594` | 256 | +255 等於 `5a` | `12f7a` |
| 4 | `08077600` | `2000c694` | 256 | +255 等於 `5a` | `13084` |
| 5 | `08077500` | `2000c40c` | 133 | +132 等於 `5a` | `13108`（tail transfer） |

每筆先獨立載入數值 slot `0x4004c`，`load_slot` 返回未修改的 32-bit raw word；JALR 清除最低位，故 `external_call` 收到的 effective target 是 `raw & ~1`，之後才讀 guard。偶數不變、奇數減一（例如 `0x12345679` → `0x12345678`）；零和一都得到零，模型不對 target 有效性作額外判斷；不假定 target 是 ROM copy、不假定外部呼叫成功複製任何內容。第一筆依序逐 byte 讀取，首次不符即 default，後續 bytes 不讀；不能事先快取四個 bytes。其餘不符各自呼叫 default，然後繼續；最後一筆不符為 tail transfer，hook 的 tail 標記表示該控制流，不聲稱 C 編譯器產生 tail call。

C 與 Python 都以 hooks 抽象 slot 載入、外部呼叫、每次 byte 讀、default；hook 可改動任意其他模型記憶體及未來 slot 值。假設 hooks 可用、存取有效，外部呼叫與前五個 default 正常返回；最後 tail hook 若返回，模型隨即結束。無法推論不返回、異常、並行、中斷、實際位址映射、函式回傳值或記憶體所有權。hooks 未傳遞或保存未指定的暫存器、隱含參數及跨呼叫暫存器狀態；因此不能表達依賴這些狀態的任意 callee 行為，並非完整機器 ABI 模型。default 的內部行為與 ROM 均不建模，marker 成功不是完整資料有效性證明。

## 自測

在 repo 根目錄：

```sh
python -I -S -B experiments/v4160-131c2-six-record-candidate/verify.py
python -O -I -S -B experiments/v4160-131c2-six-record-candidate/verify.py
```

測試記錄每次載入的 raw word 和 external call 的 effective target，以精確事件序列檢查 `0`、`1`、`0x12345678`、`0x12345679`、`0xfffffffe`、`0xffffffff`，涵蓋 odd/even 與邊界值及每次重新載入。另測試四個位置及五個 marker 各自 256 值、失敗短路、所有 default、最後 tail、事件順序與跨呼叫／讀取造成的副作用；驗證 image hash、窗口、C blob hash 和記憶體內變異負例。測試是有限案例，不涵蓋所有副作用組合。Python **沒有執行 C**，不能證明 C 行為或與機器碼等價；C **未編譯**。未執行或模擬韌體，未調整工具或 settings。
