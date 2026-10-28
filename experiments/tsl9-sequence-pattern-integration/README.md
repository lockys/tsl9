# 序列比對資料正式來源與原位址整合

[English](readme.en.md) · [專案](../../README.md) · [C/C++ 來源](../../src/native/receive/sequence_pattern_data.c)

`0x1A638..0x1A668` 的48-byte唯讀資料已納入正式 `src/`、manifest及原位址診斷連結。C11／C++17診斷ELF一致，**73,478／76,800 bytes（95.67%）** 與官方BIN逐byte相符：69,412B CODE＋4,066B DATA。這是靜態位元組覆蓋率，不是功能完成率或可刷入比例。

|項目|已核對證據|
|---|---|
|來源|162份C/H；125個CODE、11個DATA單位；272組比較／544物件的組合證據|
|保留範圍|161份舊來源、父540物件證據與2,164個父輸入；追加4個origin／curated C11／C++17 DATA物件|
|原位址|6,182個CODE owner、61個DATA OBJECT、43個相鄰區段；原有5,270筆重定位角色保留|
|依賴|6個compiler UND與6個既有DATA label保留；沒有新增完整provider alias|

在[完整callback／候選比較函式分析](../tsl9-sequence-pattern-data/README.md)的前提下，`0x12046..0x1205E` 使用 `0x1A638+6*(2*channel+state)` 讀六個byte。channel為0～3；只有state每次讀取為0／1、有效非空緩衝區、穩定GP／saved register、無alias／IRQ／DMA／巢狀干擾，以及候選slot／Xwchc／MMIO條件成立時，這48B才足以支援該條件式讀取。

候選比較函式在有效非空輸入相等時回傳1、不同時0；null或長度0也回傳1，不能改成標準 `memcmp` 回傳慣例。第一段匹配使state0→1，第二段使1→2後清0，交出低byte標記 `0x80+channel`；這是條件式程式語義推論，尚未識別實體按鍵或車輛動作。

全域state界限與installed ROM身分未證；不建立 `tsl9_registered_callbacks_static_data_1a638` 完整provider。byte-state保守包絡仍為1,572B，其中92B超出APP；它不證明實際越界或完整宣告大小。本輪只選48B，未輸出刻意排除區域的payload或個別雜湊。

所有既有CODE／DATA owner的內容及座標、CODE continuation觀察均保留，包括 `0x8034→0x8038` 啟動／向量資料邊界觀察。剩餘3,322B含刻意排除3,128B與其他未選194B，沒有以填零、padding或直接複製原BIN補足。

[`audit-result-v1.json`](audit-result-v1.json) 與 [`summary.json`](summary.json) 保留實際原生及獨立ELF reader證據。產物為ET_EXEC／entry0／零PT_LOAD診斷ELF，**不是韌體BIN**；原機ROM／RAM／IRQ／Flash／OTA、完整執行與可刷入性未證。本輪不執行target、HOST model、ISA模擬或硬體。

具備凍結的本機父物件與LLVM時，可唯讀重播：

```sh
python3 experiments/tsl9-sequence-pattern-integration/audit-v1.py --tool-dir "$LLVM_BIN"
```

本次提交只含文字來源及證據；不宣稱本輪重新解析或編譯全部544物件。[新增功能候選](../tsl9-sequence-pattern-data/feature-candidates.json)是離線序列狀態與樣式辨識診斷，尚未實作。
