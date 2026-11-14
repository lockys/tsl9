# 原始 BIN epilogue 局部比對

`verify.py` 使用既有的 RV32IMAC 片段編譯器，將 `src/native/receive/ota_epilogue_14098.inc` 以 C 與 C++ 編譯，直接與 SHA-256 固定之原始 BIN 的 `[0x14098, 0x140a6)` 比較。編譯器助手亦檢查 section、符號與零 relocation；測試逐一拒絕 14 個單 byte 變造及四個錯誤範圍邊界。

```text
python -I -B experiments/v4160-epilogue-original-proof/verify.py --tool-dir <Android-NDK-LLVM-bin>
```

`python -B experiments/v4160-epilogue-original-proof/semantics.py` 額外以有限 RV32C 解碼器執行原始 bytes，在 10,000 組合成暫存器與成功的對齊記憶體讀取下檢查還原 `ra/s0–s3` 的順序、其餘暫存器、`sp + 192`（含 RV32 環繞）與返回目標，並測試四種指令變造。解碼器與預期結果皆為自製，不涵蓋 trap、中斷或硬體。

同一驗證也將既有入口片段 `[0x14056, 0x14098)` 分別以 C/C++ 編譯並在暫存 ELF 中連結，檢查 object relocation 配置和固定目標後，將 66 bytes 直接比對原始 BIN；逐一拒絕 66 個單 byte 變造及四個錯誤範圍。入口與 epilogue 連續但分開比對；此暫存 ELF 並非完整韌體或可刷寫映像。

另以相同方式比對三段既有暫存連結結果：`[0x140a6,0x140dc)`（54 bytes）、`[0x140dc,0x14122)`（70 bytes）、`[0x1417a,0x141ac)`（50 bytes）。這些片段各自包含需由輔助程式檢查並解析的 relocation；每段的單 byte 變造及邊界均遭拒絕。區間之間仍有未在本測試比對的缺口，不可合計成連續覆蓋。

這些片段原本即存在，並非新還原的 C。它是依賴周邊 192-byte stack frame 的內嵌組語函式尾段，不可視為獨立可呼叫函式。這是局部 object 與原始 BIN 的直接比對，不變更正式 original-coordinate 覆蓋率政策，也不證明連結影像、路徑可達、ABI、功能或實機安全。
