# 條件性資料參照連結

[English](readme.en.md)

在[條件性 TX RAM 模型](../tsl9-conditional-tx-storage/README.md)之上，將三個資料參照連到已編譯的實際來源區段：

| 名目位址 | 實際區段與已核對範圍 |
| --- | --- |
| `0x1AB48` | 8-byte 計數器資料，涵蓋 index 0–3 的 16-bit 讀取 |
| `0x1A638` | 48-byte 序列資料，涵蓋 channel 0–3、state 0–1 的六 byte 窗口 |
| `0x1A078` | 432-byte grid 物件內部；另核對 mode 0–5 各 16-byte 列均有唯一來源區段 |

執行 `python scripts/verify-conditional-data-providers.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>`。C／C++ 的候選別名均指向實際 section，而非絕對位址佔位；在這些條件與 RAM 模型下，嚴格連結剩 3 個外部名稱：`0x40000` resident、`0x14056` 程式入口與 `0x1A69C` 預設資料。為比較而對這三項使用數值見證時，73,551 bytes 已選 Flash 區段不變。

**這不是完整 provider 的證明。** 全域 index／mode／state 界限、RAM 所有權及實機行為均未確認；超出上述窗口可能讀到其他資料或越界。輸出為零 `PT_LOAD` 的診斷 ELF，不是 BIN，不可燒錄；預設建置不套用這些條件性別名。
