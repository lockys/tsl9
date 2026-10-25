# 複製來源 C/C++ 資料實驗

[English](readme.en.md) · [分析證據](../../analysis/record-copy-windows-2026-10-25/README.md)

`src/record_copy_windows.v1.c` 重建原始兩個複製來源的 94＋106 bytes。只有唯讀 DATA，沒有可執行韌體或硬體功能名稱。

在專案根目錄執行唯讀靜態檢查（Python 3.10+；Windows 已測試）：

```sh
python3 experiments/tsl9-record-copy-windows/verify-v1.py --static-only
```

Windows 可用 `py -3` 取代 `python3`。編譯量測使用既有鎖定雜湊的 Windows LLVM 工具；將 `LLVM_BIN` 設成該工具目錄，再用新的輸出名稱：

```sh
python3 experiments/tsl9-record-copy-windows/verify-v1.py --tool-dir "$LLVM_BIN" --trial my-copy-data
python3 experiments/tsl9-record-copy-windows/verify-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-copy-windows/build/my-copy-data
```

PowerShell 的變數寫法為 `$env:LLVM_BIN`。`--trial` 只建立新資料夾；`--replay` 不重編譯。沒有下載、硬體操作或韌體／模型執行。其他主機的工具鏈尚未驗證。

後續已納入來源清單與診斷元件，見[整合證據](../../analysis/record-copy-integration-2026-10-25/README.md)。本頁的v1編譯紀錄保留獨立實驗範圍；仍未證明可刷入原硬體。
