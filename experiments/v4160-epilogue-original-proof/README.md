# 原始 BIN epilogue 局部比對

`verify.py` 使用既有的 RV32IMAC 片段編譯器，將 `src/native/receive/ota_epilogue_14098.inc` 以 C 與 C++ 編譯，直接與 SHA-256 固定之原始 BIN 的 `[0x14098, 0x140a6)` 比較。編譯器助手亦檢查 section、符號與零 relocation；測試逐一拒絕 14 個單 byte 變造及四個錯誤範圍邊界。

```text
python -I -B experiments/v4160-epilogue-original-proof/verify.py --tool-dir <Android-NDK-LLVM-bin>
```

此片段原本即存在，並非新還原的 C。它是依賴周邊 192-byte stack frame 的內嵌組語函式尾段，不可視為獨立可呼叫函式。這是局部 object 與原始 BIN 的直接比對，不變更正式 original-coordinate 覆蓋率政策，也不證明連結影像、路徑可達、ABI、功能或實機安全。
