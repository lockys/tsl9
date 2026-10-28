# 四組成對樣式與候選 Boolean 比較函式

[English](readme.en.md) · [專案](../../README.md) · [C/C++ DATA](sequence_data.v1.c)

後續進度：48B已納入[正式SRC／原位址整合](../tsl9-sequence-pattern-integration/README.md)，靜態覆蓋率95.67%。以下保留未整合時的封存證據；凍結驗證器可能拒絕新版manifest，請使用最新整合入口。

已核對完整 APP callback **2,878B／912指令** 與候選 ROM 比較函式 **72B／23指令**。新增的48-byte唯讀資料通過 C11／C++17編譯、原始資料比對及真實部分連結；尚未納入正式 `src/` 或原位址配置。

|位置|已確認的靜態行為|
|---|---|
|`0x12032`、`0x120A0..0x120A4`|組別從0開始，逐組增加，在4退出；比對時組別為0～3|
|`0x12046..0x1205E`|由 `GP+332+channel` 讀取state，傳入 `0x1A638+6*(2*channel+state)`，長度6|
|候選slot `0x4003C`|實際候選目標 `0x20000442..0x2000048A`；有效非空輸入全相等回傳1，有byte不同回傳0|
|`0x12072..0x12090`|匹配後增加state；第一段使0→1並離開，第二段使1→2，再清0並交出組別＋`0x80`標記|
|`0x1209C`|不匹配則清除目前組別state，繼續下一組|

「四組二段樣式識別」是上述條件下的程式語義推論。`0x80+channel`是交給共同處理路徑的低byte標記；尚未識別實體按鍵或車輛動作。若較早組別匹配，較後組別不會在這次迴圈被檢查，不能把不匹配簡化為全組重置。

候選 API **不是標準 C `memcmp` 的回傳慣例**；它在null pointer或長度0也回傳1。因此「相等」結論需有效非空六-byte緩衝區。函式還會保存／清零／恢復 `0x4002420C` 並執行 `fence.i`，含一個參考Xwchc `qk.c.lbu`。其原生byte、typed branch、完整CFG與52個主來源編碼範例均已核對；installed ROM身分、實體Xwchc支援與MMIO效果仍未證明。

在state每次讀取時為0／1、GP／saved register合約成立、緩衝區有效且不與MMIO控制word重疊、無alias／IRQ／DMA／巢狀callback干擾等前提下，才只需要 **8組×6B＝48B，`0x1A638..0x1A668`**。實際八組資料可分四對，每對僅第一個byte不同；這不等於已證明全域狀態界限或原始完整宣告大小。

若state只限於byte寬度0～255，保守包絡為 `0x1A638..0x1AC5C` 共1,572B，其中92B超出提供的APP，並涵蓋刻意排除的4-byte預設資料。**本輪只選取條件式48B，沒有讀出／輸出該排除內容或其個別雜湊**，也不將保守包絡當成實際越界缺陷證明。

[`verification-v1.json`](verification-v1.json) 保留完整48-byte frame／CFG、reaching definitions、候選比較函式與獨立ELF reader證據。新增DATA物件只有1個48-byte readonly OBJECT，無CODE／重定位／UND／ABS provider；C/C++一致。部分元件為69,412B CODE＋4,066B DATA，所有輸入allocated byte、global symbol、typed relocation與原有6個UND保留。

正式來源仍為161份、**73,430／76,800B（95.61%）**。未建立 `tsl9_registered_callbacks_static_data_1a638` 完整provider alias，未產生新BIN或證明原硬體／ROM／RAM／IRQ／Flash／OTA相容；不執行target、HOST model、ISA模擬或硬體。

具備既有本機物件與既定LLVM時，可唯讀重播：

```sh
python3 experiments/tsl9-sequence-pattern-data/verify-v1.py --tool-dir "$LLVM_BIN"
```

[新增功能候選](feature-candidates.json)：離線顯示四組待匹配階段、不匹配重置與標記來源；尚未實作，不推定實體功能。
