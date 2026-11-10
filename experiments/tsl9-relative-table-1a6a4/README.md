# 0x1A6A4 相對跳轉表：獨立原位連結實驗

`table.c` 以五組 RISC-V ADD32/SUB32 relocation 表示各目標符號減表基址；不是複製表格 bytes。測試 linker script 將五個外部目標符號綁定既有定位地址，並將表置於 `0x1A6A4`。這些絕對符號是實驗用位置替身，不是對目標函式實作或可達性的證明。只建立 20-byte section，不讀取或假設 `0x1A6A0..0x1A6A3` 的內容或歸屬。

執行：

```
python experiments/tsl9-relative-table-1a6a4/verify.py --tool-dir <LLVM_BIN>
```

本機使用 Android NDK 27.1.12297006 的 clang 18.0.2 / LLD 18.0.2：C11 和 C++17 均成功編譯及原位連結，20 bytes 與 SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667` 固定 decoded 原廠 APP 的對應範圍相同；逐項解碼為 `1452e, 1453e, 1454a, 1473e, 14748`。每種語言各重連五次，每次單獨將一個目標偏移兩 bytes，確認只有該項改變且驗證拒絕。輸出只在臨時目錄中，不修改既有候選。

此結果僅是指定座標下的資料表靜態重建；不證明 target 內容、執行路徑、整體韌體、實機行為或刷機安全。未執行韌體或刷機。
