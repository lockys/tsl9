# 完成路徑的位元 gate 與計數更新

[English](readme.en.md) · [專案](../../README.md) · [C/C++ 本體](resident_completion_status_gates.c)

新增 **5個完整原始函式，246 CODE bytes／86指令**。C11／C++17與所有原指令、9筆控制重定位及完整CFG相符；沒有新普通匯入、間接呼叫或DATA。真實本體解析5個父普通UND，**20降至15**。歷史`unprovided`符號現在有實際定義，沒有stub或alias。

|完整範圍（尾端不含）|靜態確認|
|---|---|
|56086..560AA|從record+276指標讀header；低2位存+13；類型3才讀byte2至+23，其餘存255；另將raw bit0x10存+18、byte1存+22|
|560B2..560D4|input header0 bit2與record flags12 bit3不同：翻轉record bit3、回0；相同：回1且不翻轉|
|560D4..560F6|input header0 bit3與record flags12 bit2相同：翻轉record bit2、回0；不同：回1且不翻轉|
|560F6..56146|更新word228／232；低word加1變0才進位。高word bit7設定時重設為low1／high0；依record42 bit6條件更新halfword70並清word164 bit10|
|56146..56184|對word236／240保留相應進位與重設；依record42 bit6條件設定其bit5|

既有完整完成路徑在 **59800呼叫560B2**，回0只是5983C更新queue head之前的其中一個必要條件，其他status／head／prepared／marker與release gate仍保留。部分連結確認原call角色不變，現在真正擁有560B2的完整正大小CODE本體。該角色在舊報告中即被正規化為CODE座標，**不能把舊座標標籤誤當作先前已有實作**。

以上只證明位元、分支及原始讀寫。**未證明實體ACK／CRC、live counter語意或原子性**。header decoder的兩次header0讀取保持分開；不合併snapshot，也不新增null guard。有效record／input buffer、IRQ／DMA與生命週期仍是前提。

相同的C/C++部分連結為 **50,538 CODE＋412 DATA bytes／17,547指令**，3,729正大小FUNC、2,980重定位、15普通UND，無重複原始CODE；父bytes、globals與重定位角色保留。尚未納入正式src、連入APP或做最終原位址配置。

APP仍 **162份來源、73,478／76,800B（95.67%靜態byte覆蓋）**，不是功能完成率。**沒有新BIN；原硬體ROM／RAM／IRQ／Flash／OTA相容性尚未證明**，4B啟動來源與既有間接／RAM缺口保留。未執行target、HOST model、ISA或硬體，未存取廠商API。

[`verification-v1.json`](verification-v1.json) · [`summary.json`](summary.json) · [尚未實作的診斷候選](feature-candidates.json)

固定本機輸入與LLVM齊備時，唯讀重播：

```sh
python3 experiments/tsl9-resident-completion-status-gates/verify-v1.py --tool-dir "$LLVM_BIN"
```
