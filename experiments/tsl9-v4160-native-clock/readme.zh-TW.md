# 可讀的原生時脈重建

此元件將 V4.1.60 的 `0x18834`（174 bytes）與 `0x1973c`（40 bytes）
重建成一般 C 函式，也可用 C++17 編譯。沿用既有 214 bytes／69 條指令、
50 個原始位元組負例的來源證據，未修改封存內容，也未執行原始指令。

`src/native_clock.c` 重建直接時脈與 PLL 選擇，每次分開讀取 RCC，
在查詢函式的四處重新讀取當下的 GP，讀取實際記憶體中的位移表 byte，
再重新載入時脈 word，套用 `shift & 31`。衍生欄位函式有三處 GP 讀取，
以 unsigned 除以 8,000,000，先截成八位元，再寫入 byte 與 halfword。
實作沒有以固定 GP、複製的表格或快取的時脈值取代這些讀取。

## 離線驗證

需要 Python 3.10+ 與本機 C11／C++17 編譯器（MSVC、GCC 或 Clang）。
完整驗證另需 checkout 中的原始映像與先前封存的來源證據；驗證程式不下載資料。
在專案根目錄執行：

```sh
sh experiments/tsl9-v4160-native-clock/verify.sh --language both
```

也可直接執行 `python3 -B experiments/tsl9-v4160-native-clock/verify.py
--language both`。Shell 入口以 `PYTHON` 選擇 Python，`CC`／`CXX` 可指定
單一編譯器執行檔。`--tests-only` 會明確跳過原始來源檢查，並在紀錄中標示。
本機測試每種語言有六組、269,618 個檢查，涵蓋 16 個 prescaler 索引 ×
256 個位移 byte、五種 PLL 來源 × 16 個倍頻欄位、unsigned 商數邊界、
GP 即時改變，以及 volatile 存取之間改變的全域值。

產生的驗證紀錄保留輸入、編譯器與本機測試執行檔的雜湊。
只執行自行重建的合成記憶體測試；RV32 編譯與結構檢查使用獨立的
`native-review` 驗證器，不執行產生的 RV32 程式。

## 限制

這是新的一般 C 介面。`void` 不保證維持原始 A0／A1 或其他 caller-saved
暫存器。暫存器、中斷、堆疊與呼叫端 ABI 尚未證明相容。原生分支結構檢查
也不代表所有路徑的機器碼等價證明。沒有原始入口別名、原址配置、啟動整合、
完整韌體映像或 BIN。晶片身分、ROM 相依、OTA 接受條件與實機行為仍未驗證。
沒有操作 BLE、UART、CAN 或 Flash。
