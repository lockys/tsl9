# APP 寫入回呼、UUID 與候選 CCC 通知設定鏈

[English](readme.en.md) · [專案](../../README.md) · [C/C++ CCC 本體](resident_gatt_CCC_write.c) · [兩-byte APP UUID](write_UUID.c)

新增6個完整SDK候選本體：**274 CODE bytes／115指令**；另選取APP實際讀取的 **2-byte UUID `0x1AB44..0x1AB46`（FFF1）**。C11／C++17與原始指令、資料及22筆控制重定位均相符；未新增普通外部CODE依賴。

|位置|已核對行為|
|---|---|
|APP table `0x19DFC`|原始readonly內容為 `[NULL,0x888C,NULL]`；沒有APP read／authorize callback。8614不是此表的read callback|
|APP `0x888C..0x8A56`|完整458B／153指令、64-byte frame與pre-frame退路；候選permission bit32回8，type／UUID／handle不匹配可直接回0|
|APP `0x88CE..0x88D0`|`GP+36`取UUID指標，再LHU讀2B；若原初始化指標仍有效，來源就是1AB44，沒有推定整段表格大小|
|APP `0x88C8`|CCC type2902路徑保留A0..A4、設定validCfg=1，無新frame／RA寫入地尾呼叫slot40144→候選4B4A4|
|SDK `0x4B2E4..0x4B308`、`0x4B33C..0x4B35A`|依容量byte查找4-byte記錄／清除所有handle為FFFF、value為0；不清padding byte3|
|SDK `0x4B456..0x4B500`|讀設定、更新或找空記錄、處理兩-byte CCC請求；保留逐次fresh lookup及frame釋放後tail|
|SDK `0x4CFD0..0x4CFF6`|FFFF要求尾跳全部清除；其他connection只清除對應記錄|

候選CCC在非零offset回11、長度不等於2回13、設定含不允許bit回128。APP給的mask=1，因此在正常ABI下接受的request value為0／1；這是通知設定路徑，**不證明實際已訂閱或已送出通知**。既有設定相同時直接回0，找不到connection的read回0，沒有空記錄的write回17；不能把各種0都解讀成發生了寫入。

記錄為handle halfword offset0、value byte offset2、stride4，官方候選結構已通過零runtime-byte編譯期斷言。APP `0x8FB6`傳FFFF及GP+128給候選初始化API，但表格容量來自 `0x200033B5` 的live byte。**尚未證明此時的值、賦值順序或RAM範圍**；容量0時不會讀／清任何記錄。每次容量取樣都要求有效且不wrap的4×capacity記憶體，不能先假定只有兩筆。

部分連結後，C/C++各自一致：SDK為 **41,684 CODE＋412 DATA bytes／14,394指令**、2,917正大小FUNC、2,317重定位、0具名UND；APP實驗元件為 **69,412 CODE＋4,068 DATA bytes**，原有6個UND與5,270筆重定位保留。所有父allocated byte、global與typed role均保留。

兩-byte UUID尚未正式整理到 `src/` 或原位址最終配置；APP正式來源仍162份、**73,478／76,800B（95.67%）**。沒有新增完整provider alias、替換命令router或選取被排除的payload／個別雜湊；原有4-byte SDK啟動來源缺口保持。這些候選status不構成過去OTA字母E的原因診斷。

[`verification-v2.json`](verification-v2.json) 與 [`summary.json`](summary.json) 記錄完整原CFG、唯一reaching definitions、原生／獨立ELF讀取與輸入保留證據。仍缺installed ROM／Xwchc／ABI、global pointer／容量／callback生命週期與實體RAM／IRQ／Flash／OTA證據；**沒有新BIN或已驗證可用的替代韌體**。本輪不執行target／HOST model／ISA或硬體。

具備既有本機輸入與固定LLVM時，可唯讀重播：

```sh
python3 experiments/tsl9-resident-gatt-CCC-write/verify-v2.py --tool-dir "$LLVM_BIN"
```

只提交文字來源與證據，native產物留本機。[新增功能候選](feature-candidates.json)：離線通知訂閱與CCC容量／狀態解讀，尚未實作。
