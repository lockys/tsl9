# 回呼路徑唯讀 C/C++ 資料實驗

[English](readme.en.md) · [分析證據](../../analysis/callback-prefix-data-2026-10-26/README.md)

14 個固定長度資料提供者／109 bytes。實驗性連結有 8 個編譯器未解參照；正式元件仍為 22。四個新辨識的間接 CODE 缺口另列於證據，未被此計數涵蓋。沒有可燒錄 BIN。

`LLVM_BIN` 指向既定 LLVM 工具目錄：

```sh
python3 experiments/tsl9-callback-prefix-data/audit-v1.py
python3 experiments/tsl9-callback-prefix-data/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python3 experiments/tsl9-callback-prefix-data/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-callback-prefix-data/build/native-v1
```

`--trial` 僅建立新目錄；已有產物時使用 `--replay`。重播不重新編譯或執行目標。原機 ROM 契約仍未證明。
