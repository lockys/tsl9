# 查找表視窗 C/C++ 實驗

[English](readme.en.md) · [證據](../../analysis/grid-read-windows-2026-10-25/README.md)

432-byte 唯讀資料池／兩個真實 DATA 標籤；僅實驗性連結，未更新正式來源或覆蓋率，沒有可燒錄 BIN。第三張表仍未解。

`LLVM_BIN` 指向既定 LLVM 工具目錄：

```sh
python3 experiments/tsl9-grid-read-windows/audit-v1.py
python3 experiments/tsl9-grid-read-windows/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python3 experiments/tsl9-grid-read-windows/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-grid-read-windows/build/native-v1
```

`--trial` 僅建立新目錄；若已存在，使用 `--replay` 驗證既有產物。重播不重新執行編譯或目標程式。
