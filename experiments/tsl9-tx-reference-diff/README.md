# 原廠與來源候選 TX 指令差異

[English](readme.en.md)

`python scripts/compare-tx-reference.py --tool-dir <LLVM_BIN> --reference <REFERENCE_BIN> --out <NEW_OUTPUT_DIR>` 只讀取參考檔的 TX `[0x8A56,0x8B6E)` 280 bytes，重新編譯來源候選並以明示 RISC-V 特徵解碼；不讀取既定排除區或執行目標。

對 `legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，原廠與 C／C++ 候選各有 96 條解碼指令，280 bytes 中有 93 bytes 不同；共有 83 個相同指令起點，其中 20 處的標準化指令文字不同。這不是 20 個功能差異：長度、暫存器配置及指令順序也會改變比較結果。

在 `0x8B10`，原廠為 `bltu a0,s0,0x8B52`，候選為 `bgeu a0,s0,0x8B2E`；相同輸入下條件互補，迴圈回跳分別位於 `0x8B6A` 與 `0x8B2C`。在 `0x8A7E`，分支使用的暫存器也不同；是否具有相同實際值取決於前置資料流。這些局部事實不證明整個迴圈、外部呼叫、非同步事件或 TX 功能等價。

輸出的 280-byte 片段與 ELF 都不是完整韌體，**不可燒錄**。七項預設嚴格連結依賴、排除的 3,128 bytes 及實機相容性仍未解決。
