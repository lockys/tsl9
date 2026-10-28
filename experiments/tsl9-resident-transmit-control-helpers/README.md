# 控制資料準備 helper 與 copy 來源

[English](readme.en.md) · [專案](../../README.md) · [C/C++ 本體](resident_transmit_control_helpers.c)

新增 **10個完整原始函式，890 CODE bytes／321指令**。C11／C++17與原指令、21筆直接控制與4組遠呼叫（合計29重定位）相符。10個父普通UND由真實本體解析，**30降至20**；唯一新單元匯入由既有copy本體20000332解析。沒有新DATA、間接呼叫、stub或alias；歷史`unprovided`符號現在具有實際定義。

|完整入口|靜態確認|
|---|---|
|5A120..5A1DC|長度12、數值opcode0；序列化record+86／88／90／92／94，保留條件式counter94更新及三組halfword比較後的bool98|
|5A568、5A588、5A614、5A686、5A6E0|準備opcode29／30／35／36／40；保留global byte讀取、RV32變動shift的低5位規則、有號byte讀取及條件式旗標。這五個本體沒有本地null-buffer guard|
|5A70C..5A768|copy record+296的5B至frame+3；保留counter302更新與兩個byte封裝|
|5A7BA..5A804|opcode8，copy record+248的8B至frame+3，更新flags42與state16；長度先於null guard寫入|
|5A804..5A84E|opcode9，copy相同範圍，但先做null guard才寫長度；成功路徑清record+43、OR flags160的32並設state16=1|
|5A898..5A928|opcode15，保留手動欄位封裝與record+104的12B copy至frame+14|

四處copy呼叫 **5A742／5A7E0／5A828／5A904 → 20000332**，完整CFG確認每個null guard都支配copy，並核對A0／A1／A2的唯一原始定義。沒有讀取live record或global內容。實際buffer範圍、重疊／生命週期與協定opcode名稱仍未證明；不可把opcode8與9合併成同一條錯誤處理，也不可將return0解讀為送達或ACK。

相同的C/C++部分連結為 **50,292 CODE＋412 DATA bytes／17,461指令**，3,706正大小FUNC、2,971重定位、20普通UND，無重複原始CODE。父bytes、globals與重定位角色保留。尚未納入正式src、連入APP或做最終原位址配置。

APP仍 **162份來源、73,478／76,800B（95.67%靜態byte覆蓋）**，不是功能完成率。**沒有新BIN；原硬體ROM／RAM／IRQ／Flash／OTA相容性尚未證明**，4B啟動來源與既有間接／RAM缺口保留。未執行target、HOST model、ISA或硬體，未存取廠商API。

[`verification-v1.json`](verification-v1.json) · [`summary.json`](summary.json) · [尚未實作的診斷候選](feature-candidates.json)

固定本機輸入與LLVM齊備時，唯讀重播：

```sh
python3 experiments/tsl9-resident-transmit-control-helpers/verify-v1.py --tool-dir "$LLVM_BIN"
```
