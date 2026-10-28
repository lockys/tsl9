# 計數器資料與候選 ROM 清零路徑

[English](readme.en.md) · [專案](../../README.md) · [C/C++ DATA](counter_data.v1.c)

已核對三個完整 APP 函式 **592B／201 指令**，以及候選 ROM 的完整 RAM 清零函式 **46B／14 指令**。新增8-byte唯讀 C/C++ DATA，與官方 BIN 對照相同，並已做真實部分連結；尚未納入正式 `src/` 或原位址配置。

|位置|已確認行為|
|---|---|
|`0xA0FA`、`0xA344`|直接寫入 `GP+176`，兩者都先執行 `(old_byte+1)&3`|
|`0xA158`|以 `0x1AB48+2*counter` 讀取一個16-bit值|
|`0xA37C..0xA38E`|透過表格 `0x40048` tail，送出 `A0=GP+172,A1=0,A2=5`；呼叫端本身沒有實作清零|
|候選 `0x2000039C..0x200003CA`|候選表格的實際目標；先保存／清零 `0x4002420C`、執行 `fence.i`，做 byte fill 後恢復該 MMIO word|

在 installed slot確實等於此候選、目的 RAM 非零／有效／不溢位且不與 MMIO 控制word重疊、MMIO可正常存取且無錯誤或干擾寫入等條件下，長度5的 fill 會涵蓋 `GP+[172,177)`，包括計數器 byte `GP+176`，並將它清為0。這是候選程式的靜態結果，沒有實機 ROM 身分或 MMIO 實體效果證明。

目前已選的69,412B／23,602指令中，找到兩個上述直接寫入、三個直接讀取，以及196個 GP ADDI取址。這份清單**不涵蓋所有動態 alias、SDK／中斷／DMA或排除的 CODE**，因此不能宣稱全域計數器永遠是0～3。

完整 CFG 中，`0xA0FA` 不支配 `0xA158`：存在繞過該 store 的 CFG 路徑，尚未證明其實際可達性。只根據 byte 寬度，讀取包絡為 `0x1AB48..0x1AD48` 共512B，其中328B超出提供的 APP；這是保守包絡，不是原表格大小、實際非法存取或缺陷證明。

只有在已知 masked store或候選清零完成、counter至讀取時仍在0～3、正常入口／穩定GP／有效且不重疊的記憶體等條件下，才需要 `0x1AB48..0x1AB50` 的8B。這次只重建該窗口，未建立 `tsl9_input_state_decoders_static_data_1ab48` provider alias，也未補齊其他504B或判定其實體功能／封包語義。

[`verification-v2.json`](verification-v2.json) 保留完整 CFG／stack、reaching definitions、實際 SDK 原生 byte／typed branch 對照與獨立 ELF reader 證據。新 DATA物件只有1個8-byte readonly OBJECT；C11／C++17結果相同。部分元件含69,412B CODE＋4,018B DATA，保留所有輸入 allocated byte、global symbol、typed relocation與6個 UND。

正式來源仍為160份、**73,422／76,800B（95.60%）**。沒有新 BIN、原硬體／ROM／RAM／IRQ／Flash／OTA完成證明或 target／HOST／ISA／硬體執行。

具備既有本機產物與既定 LLVM 時可重播（不編譯／執行 target）：

```sh
python3 experiments/tsl9-input-counter-data/verify-v2.py --tool-dir "$LLVM_BIN"
```

[新增功能候選](feature-candidates.json)：離線分別顯示計數器來源、CFG繞路與 ROM 候選副作用；尚未實作。
