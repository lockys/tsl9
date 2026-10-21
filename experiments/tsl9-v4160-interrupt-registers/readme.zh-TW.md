# 保留正常暫存器契約的中斷初始化

本 C/C++ 元件重建 ID2966 V4.1.60 的 `0x9A42..0x9AD2`，以及 `0x19124`、`0x19142`、`0x19160`、`0x1917E` 四個各 30-byte 的 RCC helper。原始初始化本體是 144 bytes，五個函式合計 264 bytes／94 條指令。先前的 118-byte 初始化與 22-byte helper 能保留記憶體效果，但會改寫原始程式保留的 A2／A3，因此不能把縮小的差額當成原址可用空間。

每個 helper 重新讀取 32-bit MMIO，A0 回傳更新後的 word。A1 保留傳入 enabled 的完整 bits，包含非標準的非零值。啟用時 A4=`0x40021000`、A5=當次讀值；停用時兩者交換。初始化保留原本 20 個有序 MMIO／CSR 效果，正常邊界 A1=0、A4=128、A5=`0xE000E000`、A0=第六次 RCC 讀值清除 `0x101D`。原生一般配置只允許 A0／A4／A5，A1 只供明確的邊界承諾使用；A2／A3 保留仍須另外核對實際機器碼目的暫存器。

主機 adapter 在記憶體／CSR 事件外記錄 helper 與初始化的邊界輸出，不模擬處理器，也不能證明實體暫存器保留。C11／C++17 每語言檢查四組／9,184 案例／246,384 項，涵蓋高 bit 的 enabled、全部 bit-pair 基底、同址重新讀取及初始化的六個不同讀值。

```sh
sh experiments/tsl9-v4160-interrupt-registers/verify.sh --language both
```

需要 Python 3.10 以上及 C11／C++17 編譯器。`CC`／`CXX` 指定單一編譯器，`PYTHON` 指定 shell 入口使用的 Python；也支援直接執行 Python。完整模式核對未修改的 94 指令封存來源證據，`--tests-only` 明確省略該證據。編譯產物放在新的忽略目錄。Windows 結果不代表 Linux／macOS 或 POSIX shell 啟動已通過。

原生 LLVM 編譯及實際 object／反組譯證據分開保存於 `analysis/v4160-placement-2026-10-21/compiler-review/`。邊界保留不代表中斷途中狀態、原始堆疊／呼叫 PC、原機 ROM、板子、Flash 或 BLE 相容。未替換原始映像、未執行或模擬 RV32，也未產生韌體 BIN；歷史行為模型與封存證據保留原始 bytes。
