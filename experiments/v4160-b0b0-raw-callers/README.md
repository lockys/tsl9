# V4.1.60 `0xb0b0` 原始跳轉位元樣式盤點

此處只做離線、唯讀位元樣式搜尋，不執行韌體。輸入固定為 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`：76,800 bytes、offset 0 映射 `0x8000`、範圍 `[0x8000,0x1ac00)`，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。額外固定精確窗口 `[0xb0b0,0xb0ba)` = `97 17 00 20 a3 8d a7 e2 82 80`；兩項檢查均不依賴 Python assert。

`scan` 要求 base 為偶數，否則在迭代時以 `ValueError` 拒絕（包括空輸入）。每個 2-byte 對齊位置都獨立檢查，不依指令長度跳過位置：完整 4 bytes 的標準 JAL（記錄所有 rd），及 2 bytes 的 RVC C.J、C.JAL 原始 subtype。立即數依各自排列重組並作有號延伸，目標為 PC 加位移，僅列出恰好等於 `0xb0b0` 者。C.JAL 是 raw subtype 名稱，其實際 ISA 適用性取決於架構；此處不作認定。

此固定映像的結果（bytes 為檔案順序）：

| PC | bytes | 原始類型 | 位移 |
|---|---|---|---:|
| `0x102e6` | `ef a0 bf dc` | JAL rd=x1 | -21046 |
| `0x16272` | `6f 40 ff e3` | JAL rd=x0 | -45506 |
| `0x16282` | `6f 40 ff e2` | JAL rd=x0 | -45522 |
| `0x16292` | `6f 40 ff e1` | JAL rd=x0 | -45538 |

**這些只是候選位元樣式，不是可達性或實際呼叫證明**：資料、其他指令內部或重疊位置都可能匹配。此搜尋不涵蓋間接跳轉、跳至窗口內部其他地址、條件分支、跳表，或此映像以外的模組；也不對 ABI、參數、返回值或執行行為作任何主張。

從 repository 根目錄執行（僅 Python 標準函式庫）：

```text
python -B experiments/v4160-b0b0-raw-callers/survey.py
python -B experiments/v4160-b0b0-raw-callers/test_survey.py
python -B -O experiments/v4160-b0b0-raw-callers/test_survey.py
```

測試以先前 r2 確認的四條精確 bytes、rd、位移及目標作固定解碼例證，並驗證映像內 bytes 及完整 raw scan 四筆結果。另遍歷所有可編碼 JAL 與 C.J/C.JAL 有號偶數位移（含邊界）、全部 JAL rd，檢查各指令位元突變、重疊位置、截斷和映像突變；這些合成編碼不代表真實程式碼，也不是獨立的 C.J/C.JAL 解碼證據。
