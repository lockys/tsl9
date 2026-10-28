# 第三 DATA provider：查表使用原始 mode

[English](readme.en.md) · [APP／BIN門檻](../tsl9-app-bin-readiness-audit/README.md) · [檢查器](check-v1.py) · [完整合約](verification-v1.json)

已核對完整 **CEDC..CF96，186B／56指令／frame0**，包括原函式CFG、register reaching definitions與實際C11／C++17原位址ELF逐指令byte比對。正式C/C++來源已含此本體；本輪新增其資料使用合約，沒有增加重建byte。

|位置|確認行為|
|---|---|
|CF7C..CF86|`mode&7`寫到A3，再合併至record4旗標；沒有把A4的查表mode改成低3位|
|CF3E..CF5A|地址為`1A078 + 16*effective_mode + ((fresh_record4+1)&15)`|
|CF66..CF7A|以舊selector決定分支；舊值1..254會讓本次effective mode為0，即使已將下一selector寫成mod3結果|
|CF8A..CF92|countdown減至0時清enable，再繼續本次查表；不能改成當次立刻返回|

四個logical RAM byte為2000BF38／39／3A／3B；本文依行為稱enable／mode／selector／countdown，是分析標籤，尚非已確認的產品設定名稱。實體RAM映射、alias與IRQ／DMA／重入一致性仍未證。

只根據byte寬度，A4在shift前可由未遮罩的mode讀取或forced0到達，column確定為0..15。保守包絡為 **1A078..1B078，共4,096B**，其中 **1,144B超出提供的APP**，並涵蓋目前排除的default DATA。因此不能讀出整個包絡來補表，亦不能只因record flag使用`&7`就宣稱表有八列。

這是靜態保守包絡，**不是原始宣告大小、實際可達值或越界缺陷證明**。原mode0與條件式mode5的兩個16B窗口已有positive DATA backing；不新增資料、不把backing當完整provider alias。要閉合1A078 provider，仍需mode每次讀取的實際值域／使用合約或獨立合法需求，不能假設global invariant。

本輪未讀取查表包絡DATA、未輸出其payload或個別雜湊；未讀取／輸出排除的default內容。正式src與native產物保持不變：**162份來源、95.67%靜態byte覆蓋、6個APP source UND**。BIN readiness仍未就緒，沒有新BIN或硬體相容性證明。

唯讀重播（從專案根目錄）：

```sh
python3 experiments/tsl9-third-provider-lookup-contract/check-v1.py
```

exit0僅表示這份靜態合約與固定實際證據一致。可刷入狀態仍以[readiness checker](../tsl9-app-bin-readiness-audit/README.md)區分；本輪不執行target、HOST model、ISA或硬體，不呼叫廠商API。[唯讀診斷候選](feature-candidates.json)尚未實作。
