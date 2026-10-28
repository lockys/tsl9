# 查表資料正式來源與原位址整合

[English](readme.en.md) · [專案](../../README.md) · [C/C++ 來源](../../src/native/receive/lookup_mode_rows.c)

三列共48-byte DATA 已納入 `src/`、正式 manifest 與原位址診斷連結。C/C++ 產物相同，**73,422／76,800 bytes（95.60%）** 與官方 BIN 逐 byte 相符：69,412B CODE＋4,010B DATA。這是位元組覆蓋率，不是功能完成率或可刷入比例。

|項目|證據|
|---|---|
|來源|160份 C/H；125個 CODE、9個 DATA 單位|
|來源比較|268組／536物件：先完整核對既有532物件，再追加並核對4個 origin／curated C11／C++17 DATA物件|
|保留證據|既有159份來源與完整父證據的2,086個輸入不變；只有 manifest 精確追加一份來源、一個 DATA單位|
|原位址|6,182個 CODE owner、59個 DATA OBJECT、42個相鄰區段；5,270筆重定位角色保留|
|未解依賴|6個 compiler UND、6個既有 DATA label 保留；沒有新增 provider alias|

`0xD0C8` 的 packed state store 將模式 byte `0x2000BF39` 設為2／4／5；phase byte `0x2000BF3A` 接受另一個 `rem 3` 更新。只有在該 store 先完成、模式未被其他路徑覆寫、正常入口及有效記憶體／register，且 record buffer 不與固定狀態重疊時，`0xCF5A` 的 `0x1A078 +16*mode+nibble` 才限於模式 `{0,2,4,5}`、nibble `0..15`。

|模式|原始讀取範圍（不含尾端）|實際 DATA owner|
|---|---|---|
|0|`0x1A078..0x1A088`|既有432-byte資料池的最後16B|
|2|`0x1A098..0x1A0A8`|新增16B列|
|4|`0x1A0B8..0x1A0C8`|新增16B列|
|5|`0x1A0C8..0x1A0D8`|新增16B列|

四列共64B現在都有真實原位址 DATA。沒有補模式1／3或其他未選區段，也未宣稱完整表格範圍或全域模式界限；`1A078`完整 provider 仍未解。剩餘3,378B包括刻意排除的3,128B與其他未選250B，不以填零或複製原 BIN 補齊。

程式區、owner座標及 continuation觀察與前版完全相同。保守的末指令掃描仍保留 `0x8034→0x8038` 啟動／向量資料邊界觀察；本輪沒有宣稱已證明該入口的實機流程。

[`audit-result-v1.json`](audit-result-v1.json) 與 [`summary.json`](summary.json) 提供原生、來源與獨立 ELF reader 證據。`NONLOADABLE-ORIGINAL-LAYOUT.elf` 是 ET_EXEC／entry0／零 PT_LOAD 的診斷物件，**不是韌體 BIN**。原機晶片、installed ROM、RAM／IRQ／Flash／OTA、完整執行仍未證明；不執行 target、HOST model、ISA模擬或硬體。

已有本機編譯產物與既定 LLVM 工具鏈時，可唯讀重播：

```sh
python3 experiments/tsl9-lookup-mode-integration/audit-v1.py --tool-dir "$LLVM_BIN"
```

建置產物不包含在這份文字證據提交；缺少既有本機父物件時需先依各凍結配方重建。工具鏈與其他作業系統的等價性仍需另外驗證。

[新增功能候選](../tsl9-lookup-mode-rows/feature-candidates.json)：離線診斷分別顯示模式、phase與來源條件；尚未實作。
