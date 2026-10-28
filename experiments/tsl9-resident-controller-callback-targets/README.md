# Callback 目標本體與條件式註冊／dispatch 鏈

[English](readme.en.md) · [專案](../../README.md) · [C/C++ 候選本體](resident_controller_callback_targets.c)

新增 **3個完整原始本體，258 CODE bytes／86指令**。C11／C++17、15筆控制重定位與完整CFG/frame相符。補齊普通callee561B8，整體UND由19降至 **18**；另兩個新增本體就是先前的數值callback目標，不能將它們算成兩個普通UND解析。

|完整範圍（尾端不含）|靜態確認|
|---|---|
|55C32..55C48，22B／7指令／frame0|record為NULL直接返回；否則word160 OR0x80，slot38寫255|
|56CB2..56CDC，42B／16指令／frame16|NULL在frame前返回；568F6接受原record與數值34，回值低byte存43，再清byte16、slot39寫255|
|561B8..5627A，194B／63指令／frame16|保留43E6A(0,4)初值至halfword86，以及原list／高位乘法／REMU／截位和候選步長2；產品語意與live domain未確認|

另核對 **1,014B／372指令**既有完整參考，**不算新增CODE**：兩個slot wrapper、43874註冊本體、兩個dispatch與561B8 caller。

43874掃描slots16..47，使用global2000322C所指table的12B entry；43728回非0後才在word0存callback、word4存record，A3非NULL時寫slot ID。原回值為成功0／callback空2／無slot8。兩個dispatch以`12*((task<<4)+event_bit_index)`定位entry，將word4載入A0，再間接呼叫word0。因此，**註冊成功、對應event到達且table／record保持有效時**，可連起先前55C32／56CB2數值引數與新本體。43390的呼叫沒有本地pointer-null guard，不自行補上或宣稱安全。

**本輪只證明原始CODE本體身分與條件式引數來源。** 先前LUI／ADDI數值指標仍沒有新增native relocation；最終原位址配置、live table身分／不可變性、callback生命週期及實體事件均未證明，不能宣稱runtime binding已完成。

相同C/C++部分連結為 **54,780 CODE＋412 DATA bytes／18,917指令**、4,091正大小FUNC、3,253重定位、18普通UND，無重複原始CODE。3個新單元匯入均由真實父provider解析；沒有新DATA、stub、alias或本地間接呼叫，既有動態callback缺口保留。

**沒有新BIN、正式src納入、APP整合或最終原位址配置。** APP仍162份來源、73,478／76,800B（95.67%靜態byte覆蓋，非功能完成率）。原硬體ROM／RAM／IRQ／Flash／OTA與4B啟動來源仍未證明。未執行target、HOST model、ISA或硬體，未存取廠商API。

[`verification-v1.json`](verification-v1.json) · [`summary.json`](summary.json) · [尚未實作的註冊／callback診斷候選](feature-candidates.json)

固定本機輸入與LLVM齊備時，唯讀重播：

```sh
python3 experiments/tsl9-resident-controller-callback-targets/verify-v1.py --tool-dir "$LLVM_BIN"
```
