# 事件記錄的七筆 word 資料

[English](readme.en.md) · [C/C++ 定義](event_words.v1.c) · [目前正式整合](../tsl9-record-mode-row-integration/README.md)

本輪重建 `0x1AAE8..0x1AB04` 的 **28-byte 條件讀取視窗**。C11／C++17 的 DATA 物件及 partial component 完全一致，每個新資料 byte 都與原廠 APP 相同。這仍是實驗來源，未納入正式 `src/` 與新原位址連結；正式覆蓋率維持 **95.72%／163 個 C/H**。

## 已確認的程式行為

- 完整 consumer `0x176F8..0x1787C` 為 388B／135 指令、48-byte frame；CFG 所有指令可達且正常出口還原 SP，並與現有 C/C++ 原位址 ELF 逐 byte 相符。
- `0x17844` 讀取 `0x1AAE8 + 4*uint8(GP+370)` 的完整 word。只有讀取時索引為 0～6，這 28B 才涵蓋該次讀取。
- `0x17868` 在讀取之後，將 `(舊索引+1)%7` 的低 byte 寫回。u8 輸入加一落在 1～256，原始 signed REM 的結果為 0～6；這不能證明第一次讀取的索引，也沒有在讀取前加入 clamp。
- 已選 69,412B CODE 的直接 GP 存取只有上述讀／寫兩處；另有 196 個 GP ADDI 地址取得。alias、間接寫入、排除 CODE、IRQ／DMA 未完全涵蓋，不能宣稱全域不變量。
- 表格 word 的 bits 0～23 依序寫到記錄 offsets 2、3、4，保留原 frame 的其他記錄 bytes。word 最高 byte 未用於這三個寫入。
- 保留 `LW(SP+12)` 的完整四-byte fresh 讀取，沒有因先前參數長度 7 就縮窄它。`((word>>18)&31)+1` 選的是 SP+14 的 bits 2～6，並非剛寫入 SP+12 的表格 byte；其值為 1～32，乘 800 得原始 A2 參數 800～25,600。
- `0x1782E` 經槽 `0x40058` 間接轉移，A1 為 2。實體 callee、時間單位及效果未證，不能直接稱為毫秒或燈光定時器。

## 推論與限制

七筆值互不相同、最高 byte 為零，低三個 byte 的非零位置依序為 `1,3,3,2,6,4,5`（位元遮罩）。其型態像三通道配色序列，**這是資料型態推論，尚未確認 RGB 接線、硬體燈光或產品功能**。可進一步做離線記錄欄位／配色候選檢視器，見 [待實作功能構想](feature-candidates.json)。

索引僅按 byte 寬度估計的保守範圍為 1,024B，其中 744B 超出提供的 APP；這不是完整表格大小或實際越界證明。本輪只選七筆／28B，不讀該保守包絡或排除 payload，不建立完整 provider alias。

實驗 partial component 為 69,412B CODE＋4,126B DATA；保留父物件每個已配置 byte、global symbol 與 5,270 個重定位角色，六個 APP source provider 仍未解析。VMA 0 的 ET_REL 物件不是可刷寫 BIN，原機 ROM／RAM／IRQ／Flash／OTA 相容性與全域初始索引仍未證。

## 重播

有凍結的本機父產物與 LLVM 時，在 repo 根目錄執行：

```sh
python3 experiments/tsl9-event-word-table-data/verify-v1.py --tool-dir "$LLVM_BIN"
```

此實驗固定當前 163-source manifest，後續正式擴充時須保留其歷史證據。所有核對均離線；未執行 target、HOST model、ISA、硬體或第三方 API。

[輸入](inputs-v1.json) · [完整 consumer 合約](contract-v1.py) · [原生收據](verification-v1.json)
