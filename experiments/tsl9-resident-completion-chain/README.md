# 完成尾端、controller transition 與既有診斷 callback

[English](readme.en.md) · [專案](../../README.md) · [C/C++ 候選本體](resident_completion_chain.c)

新增 **3個完整原始本體，3,204 CODE bytes／1,011指令**。C11／C++17的原指令、195筆直接控制與5組遠呼叫（205重定位）相符，完整CFG/frame檢查通過。這是原指令的候選重建；許多數值state分支的產品語意仍待分析。

|完整範圍（尾端不含）|確認的原始行為|
|---|---|
|567BE..568D4，278B／92指令／frame32|保留兩個間接callback、record14=176、兩條尾端路徑；一條寫入數值位址E000E204，另一條恢復frame後tail至4354A，event mask保留RV32 shift與uint16截位|
|56D0E..5774E，2,624B／818指令／frame48|保留整個多旗標transition本體、post-return分支及7個間接呼叫；包含條件式code9–12狀態回報|
|58F14..59042，302B／101指令／frame32|保留record310索引的bitmap測試、clear-bit首遇設定後直接返回、兩個flag guard，以及5B copy到record296與後續word164旗標更新|

既有完成處理器的 **59BC0／59C3C→56D0E、59BFA→58F14、59C14 tail→567BE**，均核對原record引數來源；tail前恢復原frame。部分連結確認原call角色與新的正大小原始CODE provider相符，未把座標或stub算作實作。

官方header定義 `staCB` 為`void(uint8_t code,uint32_t status)`，config offset52。原56D0E從global20003220讀取它，在record64非0且模100為0、config bit及初次callback非空條件下送出：

|code|原始數值引數|
|---|---|
|9|global200033B8的halfword16作高16位、halfword18作低16位|
|10|同global的halfword14|
|11|record50的有號halfword延伸值|
|12|record52的有號byte延伸值|

**只有初次pointer有null guard，後續各次重新讀取callback**，不得假設前一次回呼後指標仍有效。原cache清零在dispatch或config／pointer不符合的對應路徑保留。這些數值的實體意義、callback是否在硬體啟用及模100所對應的時間皆未證明。此既有介面值得作唯讀診斷候選，尚未實作。

本輪解析3個舊普通UND，新增單元另有23個匯入：13個由真實父provider解析、**10個新缺失保留**。因此整體普通UND由15變**22**，另有**9處新間接呼叫未閉合**。沒有新DATA、stub或alias。相同C/C++部分連結為 **53,742 CODE＋412 DATA bytes／18,558指令**、3,997正大小FUNC、3,185重定位，無重複原始CODE，父bytes／globals／重定位角色保留。

**沒有新BIN；尚未納入正式src、連入APP或最終原位址配置。** APP仍162份來源、73,478／76,800B（95.67%靜態byte覆蓋，非功能完成率）。原硬體ROM／RAM／IRQ／Flash／OTA與4B啟動來源仍未證明；數值MMIO寫入不證明中斷控制器身分。未執行target、HOST model、ISA或硬體，未存取廠商API。

[`verification-v1.json`](verification-v1.json) · [`summary.json`](summary.json) · [尚未實作的診斷候選](feature-candidates.json)

固定本機輸入與LLVM齊備時，唯讀重播：

```sh
python3 experiments/tsl9-resident-completion-chain/verify-v1.py --tool-dir "$LLVM_BIN"
```
