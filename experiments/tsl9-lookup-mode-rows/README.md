# 查表模式與三列資料重建

[English](readme.en.md) · [根目錄](../../README.md)

後續進度：48B已完成[正式 SRC／原位址整合](../tsl9-lookup-mode-integration/README.md)，目前覆蓋率95.60%。以下保留本輪未整合時的封存證據。

原始 `0xD07C..0xD0EE` setter 的 `0xD0C8` 是32位元 store；到達此處時，其三個來源值將狀態寫成 `[1,5,0,1]`、`[1,4,0,1]` 或 `[1,2,0,1]`。模式在 `0x2000BF39`；`rem 3` 更新的是另一個 phase byte `0x2000BF3A`。

在已知 setter 先完成、模式未被其他路徑覆寫、呼叫記憶體有效且 record buffer 不與狀態重疊的條件下，`0xCEDC..0xCF96` consumer 在 `0xCF5A` 讀取 `0x1A078 +16*mode+nibble`，模式可限為 `{0,2,4,5}`，nibble 為 `0..15`。這是條件式範圍，尚未證明全程式只有這些模式。

| 模式 | 原始讀取列（不含尾端） | 本次處理 |
|---|---|---|
|0|`0x1A078..0x1A088`|既有432-byte唯讀 owner 的最後16 bytes|
|2|`0x1A098..0x1A0A8`|新增獨立16-byte C/C++ DATA|
|4|`0x1A0B8..0x1A0C8`|新增獨立16-byte C/C++ DATA|
|5|`0x1A0C8..0x1A0D8`|新增獨立16-byte C/C++ DATA|

[`lookup_mode_rows.v1.c`](lookup_mode_rows.v1.c) 只重建三列共48 bytes；沒有補模式1／3、宣稱完整表格大小或建立 `1A078` provider alias。每列與既有模式0列呈固定 XOR 差值；這只是資料形狀，不是演算法或用途的完整證明。

[`verification-v1.json`](verification-v1.json) 保留完整兩個函式的300 bytes、原生位元組對照、CFG／stack檢查、store reaching definitions，以及 C11／C++17 實際編譯與獨立 ELF reader 比對。新物件只有48-byte唯讀 DATA、3個 OBJECT，沒有 CODE、重定位、未定義或絕對位址 provider。不執行 target、HOST model 或模擬器。

[`composition-v1.json`](composition-v1.json) 進一步核對與既有 APP 物件的實際部分連結：保留69,412-byte CODE、既有3,962-byte DATA，再加48-byte DATA，共73,422 bytes。所有輸入 allocated section 位元組、global symbol 與 typed relocation 保留；C/C++ 結果相同，6個 compiler UND 未消除。這是 ET_REL 物件，尚未完成原位址連結。

[新增功能候選](feature-candidates.json)：離線診斷分開顯示查表模式、phase 與來源條件，避免將 `rem 3` 當成模式界限；目前尚未實作。

本輪封存實驗當時尚未納入正式 `src/` manifest 或 APP 原位址整合；當時正式覆蓋率為 **95.54%（73,374／76,800 bytes）**，6個 compiler UND 保留。未證明 ROM／RAM／IRQ／Flash／OTA 或全域 writer／alias；沒有新 BIN，仍不可宣稱可刷入或功能完成。

以既有 LLVM 工具鏈重新核對（只編譯／讀取物件）：

```sh
python3 experiments/tsl9-lookup-mode-rows/verify-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-lookup-mode-rows/build/native-v1
```

若本機尚無保留物件，使用 `--trial native-v1` 進行首次編譯；輸出目錄採建立一次模式，既有收據必須完全相符，不覆寫。
