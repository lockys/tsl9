# V4.1.60 0x103ca bit1 compare/store event candidate

離線基準：main 的 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，76800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，Git blob `e6cd0db8bd7d460a16967a5df9eadb42b04fa00d`；位址基底 0x8000。參照 commit `d6e2391030eee86cc73426c206c47c7750e00c57` 的 `src/native/receive/record_field_transitions.c`，Git blob `2e974f2e4fd6ad6c7c60aee940a92828dc1d7fa3`；驗證器不讀取工作樹的該來源檔或 Git，因此不會核實該歷史來源。這是靜態來源線索，不是生成或編譯證明。

## 視窗與事件

固定半開區間 `[0x103ca, 0x103ea)` 的 bytes。0x103ca `lbu a5,7(s1)`；0x103ce `lbu a4,82(gp)`；右移並遮罩取得 bit1；0x103d6 相等跳到 0x103f8，不等落入 0x103da，恢復暫存器後於 0x103e0 `sb a5,82(gp)`，0x103e6 尾跳 0x13c4e。此處 `p7` 是 **0x103ca 的再次讀取**，不假定等於前次 input[7] 的讀取，期間記憶體可能改變；`old` 是 GP+82 讀出的完整 unsigned byte，不能預先遮罩為 bit。

`candidate.c` 接受兩個已觀察的 byte，回傳 value 與 store 事件：value = (p7 >> 1) & 1；old 等於 value 則 store=0，否則 store=1，若 store=1 寫入值為 value。這不是直接對 GP 寫入，也不聲稱對早前讀取值的關係、進入路徑可達性、記憶體有效性或並發提供保證。等值分支 0x103f8 及不等值路徑的尾跳 0x13c4e **目的地效應與所有後續行為均不在模型內**；不建模堆疊和暫存器恢復。

## 驗證

```
python -I -S -B experiments/v4160-103ca-bit-candidate/verify.py
python -I -S -B -O experiments/v4160-103ca-bit-candidate/verify.py
```

Python 標準庫驗證整體 firmware 長度、SHA-256、Git blob，以及候選 C 的精確 Git blob；對候選 C 的 bit 遮罩、移位與比較子做記憶體負例。C 的 blob pin 只固定受審閱原文，不是 C 語義測試。另固定指令視窗並測試每個 bit 翻轉、截斷和窗外變動；窮舉第二次讀取 p7 與完整 old 的 65536 組。`unittest` 在 `-O` 下仍生效。Python 抽象模型只與算術規格比對；沒有編譯或執行 C，也不是 ISA 模擬、target differential 或硬體驗證。
