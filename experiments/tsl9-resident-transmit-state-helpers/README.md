# 狀態 helper 與分片長度來源

[English](readme.en.md) · [專案](../../README.md) · [C/C++ 本體](resident_transmit_state_helpers.c)

新增 **12個完整原始 helper，682 CODE bytes／257指令**。C11／C++17與原指令、29筆控制重定位及完整CFG相符。12個父普通UND由這些真實本體解析，**42降至30**；沒有新普通匯入、間接呼叫或DATA。符號保留先前的`unprovided`名稱以對應既有參照，但現在具有實際本體，沒有加stub或alias。

|完整入口|靜態證據|
|---|---|
|5A1DC、5A222、5A23E、5A25E、5A286、5A306、5A326、5A348、5A370|先更新record+21長度，再測試frame buffer+272；空指標回7或1，已有長度副作用；正常路徑準備數值opcode2／6／7／10／11／13／17／18／19|
|5A2A2..5A306|準備opcode12，從global base200033B8的20／22／24／25 offset讀資料；保留record+46、+43、+160的條件式旗標更新。未讀取live global內容|
|5A386..5A406|準備opcode22，根據record+324旗標、+486與+328 halfword計算候選值，與+484 halfword取unsigned min，將低byte寫入+78|
|5A48E..5A52A|準備opcode24；保留`uint16(counter64+8)`至record+332與可選header counter，再以相應旗標計算並寫入record+78|

最後三個本體**沒有本地null-buffer guard**；有效record與frame buffer為前提。兩個長度計算保留signed DIV、算術右移、uint16截位、unsigned比較與最後byte截位，不能改成一般無號除法或額外clamp。這補上先前分片準備器讀取record+78的兩個來源，但**仍未證明live輸入範圍與實際frame配置上限**，也未確認數值opcode的協定名稱。

相同的C/C++部分連結為 **49,402 CODE＋412 DATA bytes／17,140指令**，3,657正大小FUNC、2,942重定位、30普通UND，沒有重複原始CODE。父bytes、globals與重定位角色保留。這是SDK候選部分物件，尚未納入正式src、連入APP或最終原位址配置。

APP仍 **162份來源、73,478／76,800B（95.67%靜態byte覆蓋）**，不代表功能完成率。**沒有新BIN；原硬體ROM／RAM／IRQ／Flash／OTA相容性尚未證明**，4B啟動來源與其他間接／RAM依賴仍保留。未執行target、HOST model、ISA或硬體，未存取廠商API。

[`verification-v1.json`](verification-v1.json) · [`summary.json`](summary.json) · [尚未實作的診斷候選](feature-candidates.json)

固定本機輸入與LLVM齊備時，唯讀重播：

```sh
python3 experiments/tsl9-resident-transmit-state-helpers/verify-v1.py --tool-dir "$LLVM_BIN"
```
