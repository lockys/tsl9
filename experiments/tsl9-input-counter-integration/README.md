# 計數資料正式來源與原位址整合

[English](readme.en.md) · [專案](../../README.md) · [C/C++ 來源](../../src/native/receive/input_counter_data.c)

已將 `0x1AB48..0x1AB50` 的8-byte唯讀資料納入正式 `src/`、manifest及原位址診斷連結。C/C++診斷ELF一致，**73,430／76,800 bytes（95.61%）** 與官方BIN逐byte相符：69,412B CODE＋4,018B DATA。這是位元組覆蓋率，不是功能完成率或可刷入比例。

|項目|證據|
|---|---|
|來源|161份C/H；125個CODE、10個DATA單位|
|來源證據|270組／540物件：保留父536物件的組合證據，追加4個origin／curated C11／C++17 DATA物件|
|保留範圍|160份舊來源與2,125個父證據輸入；僅manifest精確追加一份來源、一個DATA單位|
|原位址|6,182個CODE owner、60個DATA OBJECT、43個相鄰區段；5,270筆重定位角色保留|
|依賴|原有6個compiler UND與6個DATA label保留，沒有新增provider alias|

新窗口是4個halfword讀取單元。只有在已知masked store或候選清零完成、`GP+176`計數器至讀取時仍為0～3，且正常入口、穩定GP、有效且不與caller buffer／MMIO控制word重疊的RAM等前提成立時，`0xA158`對 `0x1AB48+2*counter` 的讀取才只需要這8B。

原始完整CFG存在繞過 `0xA0FA` 的路徑，兩處直接寫入以外還有alias／SDK／IRQ／DMA缺口。byte寬度的保守讀取包絡仍是512B，包含328B超出提供的APP；這不是實際非法讀取或原表格宣告大小的證明。新增8B不等於證明全域計數器界限，因此不建立原始opaque symbol `tsl9_input_state_decoders_static_data_1ab48` 的完整provider alias。

候選表格 `0x40048` 的目標 `0x2000039C..0x200003CA` 除了byte fill，也保存／清零／恢復 `0x4002420C` 並執行 `fence.i`。其清除 `GP+[172,177)` 的結果仍取決於installed slot確實相同、RAM/MMIO有效且不重疊、無fault或干擾等條件；實體ROM身分與MMIO效果未證。詳見[封存v2分析](../tsl9-input-counter-data/verification-v2.json)。

所有既有CODE／DATA owner的byte與座標均保留。新增窗口align4，相鄰既有DATA為align1，因此分成43個真實區段，未改變任一來源對齊或補入padding。程式區與continuation觀察不變；保留原有 `0x8034→0x8038` 啟動／向量資料邊界觀察，不宣稱啟動流程完成。

[`audit-result-v1.json`](audit-result-v1.json) 與 [`summary.json`](summary.json) 記錄實際原生及獨立ELF reader核對。剩餘3,370B包括刻意排除的3,128B與其他未選242B，沒有用填零或複製原BIN補足。

診斷ELF為ET_EXEC／entry0／零PT_LOAD，**不是韌體BIN**。原機晶片、ROM／RAM／IRQ／Flash／OTA與完整執行仍未證；本輪不執行target、HOST model、ISA模擬或硬體。

具備既有本機物件與既定LLVM時，可唯讀重播：

```sh
python3 experiments/tsl9-input-counter-integration/audit-v1.py --tool-dir "$LLVM_BIN"
```

本次文字提交不含編譯產物；缺少父物件時，須先依凍結配方重建。組合證據保留原532物件證明與後續DATA投影，不宣稱本輪重新解析或編譯全部540個物件。

[新增功能候選](../tsl9-input-counter-data/feature-candidates.json)：離線計數器來源、CFG繞路與ROM副作用診斷；尚未實作。
