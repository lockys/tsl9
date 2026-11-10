# V4.1.60 mode setter 直接轉移候選

重播：`python experiments/tsl9-six-dependency-ledger/check-mode-direct-callers.py`；mutation tests：`python experiments/tsl9-six-dependency-ledger/test-mode-direct-callers.py`。使用 ID-2966 V4.1.60 decoded APP，基址 `0x8000`、長度 `0x12c00`；只讀半開區間 `[0x8000,0x14056)`、`[0x14c8a,0x1a69c)`、`[0x1a6a0,0x1ac00)`。對每個偶數位址解碼 JAL、C.J、C.JAL，目的固定 `0xD05C`，固定五個候選及 setter、各候選的參數窗口原始 bytes。這是編碼掃描，並非指令邊界或全部呼叫證明；不含 JALR、AUIPC+JALR、排除區及其他 image。掃描不執行 target。

| 候選 | 固定窗口（半開） | 窗口連續執行時的 setter 輸入 `(a0,a1,a2)` |
|---|---|---|
| `0xA224` | `[0xA21C,0xA228)` | `(3,1,0)` |
| `0xAC6C` | `[0xAC60,0xAC70)` | `a5` bit 8 非零的落入路徑 `(3,2,0)`；其他路徑不適用 |
| `0xD528` | `[0xD51C,0xD52C)` | `(5,10,1)` |
| `0xE1EA` | `[0xE1DE,0xE1EE)` | `(3,15,1)` |
| `0xE6E8` | `[0xE6DC,0xE6EC)` | `(3,1,0)` |

`[0xD05C,0xD07C)` 的 setter 指令將 `a0` 低 byte 寫入 mode，沒有 182–184 值域檢查。上述五個固定窗口的正常連續執行路徑均將 `a0` 指定為 3 或 5，因而不能由這些窗口支持 caller 輸入 182–184；這是固定常數，不是對所有 caller 的 range check 證明。若其他入口能傳入這三個值，setter 本身不會阻擋；是否存在這樣的入口、值是否由外部可控、寫入後是否被覆寫及查表是否使用它，均未證明。尤其間接轉移及其他 writer 未封閉，不能宣稱全域可達或不可達。

測試對每個固定窗口逐一變更 byte，並變更呼叫編碼、模擬短讀，預期均被拒絕；並非所有可能 mutation 的完備證明。更多 setter 與讀取之間的狀態和查表算術見同目錄 `README.md` 的 mode 各節。
