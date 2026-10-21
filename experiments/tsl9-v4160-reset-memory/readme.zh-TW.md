# 可讀的 reset 記憶體初始化

此 C11／C++17 元件重建 ID2966 V4.1.60 的 `[0x186BA,0x186F8)`，
原始共 62 bytes／17 條指令。複製目的地、複製上限與清零起點分別讀取當下 GP。
逐一讀取並立即寫入 32-bit word，再清零到 `0x2000C958`，保留 unsigned
比較與位址回捲運算。原始固定 GP=`0x20004000` 時，從 `0x1AB60` 複製
32 個 word，並清零 8,758 個 word。

正常輸出為 A0=清零後游標、A1=`0x2000C958`、A2=第二次 GP+128。
原始 A0／A1 會通過時脈函式，一直保留到未知 ROM 交接，不能依一般 C 呼叫慣例捨棄。
複製最後一個 word 留在 T0 的值，在 `0x186F8` 立即被覆寫；本 helper
不宣稱保留這個截點狀態。來源的正常 SP 位址為 `0x20010000`，但此 helper
不設定 SP，也不證明實體 RAM。

## 離線主機驗證

```sh
sh experiments/tsl9-v4160-reset-memory/verify.sh --language both
```

也可直接執行 `python3 -B experiments/tsl9-v4160-reset-memory/verify.py
--language both`。需要 Python 3.10+ 與 C11／C++17 編譯器；`CC`／`CXX`
可指定單一編譯器執行檔，shell 入口用 `PYTHON` 指定 Python。
驗證器不下載資料，會核對原始映像及封存來源，也核對周圍 138-byte reset
與實際 128-byte initializer。Initializer 只當資料複製到新的忽略編譯目錄，
主機測試只收到該資料檔的本機 ASCII 檔名。

每語言有五組／338 案例／133,601 項檢查，包含原始資料、獨立改變的 GP、
0–32 個 word 複製、少量及正常清零範圍、unsigned 略過／回捲、重疊區域的
即時向前複製，以及最終游標值。不對齊的數值位址只在合成 callback 中測試，
不代表已驗證實體對齊或 trap。測試輸入刻意限制為有限、可終止的案例；
原始程式在某些改變 GP 的範圍不會終止，重建 C 不加任意 timeout 或固定 32 次捷徑。
`--tests-only` 略過 raw 證據，但仍需要已辨識的原始 initializer 資料。

## 原生介面與限制

原生版本使用三次編譯器專用的即時 GP primitive，明確保留 A0／A1／A2。
一般配置只允許 T0 與 A0–A2；仍須由實際 ELF 檢查確定沒有額外暫存器、
堆疊存取或隱藏的 `memcpy`／`memset` helper。原生審查位於
`analysis/v4160-reset-memory-2026-10-21/compiler-review/`。

預設 leaf 使用新的 RET 介面；原始片段則直接落入 `0x186F8` 的 CSR 設定。
可選的原生 fragment 用真正的壓縮跳轉前往 `__tsl9_reset_resume_186f8`，
該延續符號仍是明確待提供的義務。數值位址 witness 不供應實作。
兩者均未證明原始入口 adapter、CSR／clock／ROM 整合、非同步狀態、硬體或 OTA
相容性。未替換原始映像、未執行或模擬 RV32，也未製作 BIN。
