# V4.1.60時脈查詢與衍生欄位

本固定C11／C++17資料流模型重建原始ID2966 V4.1.60的`18834..188E2`（174 bytes／58指令）與`1973C..19764`（40 bytes／11指令）；終點不含在範圍內。已封存的raw來源證據涵蓋214 bytes／69指令，拒絕50個原始運算元突變。原Runtime的SHA-256為`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。

`sf_query_18834`從分開的即時讀取選擇來源與PLL計算，保留倍率17改18的規則，先將基礎結果寫入GP+108。之後重新讀prescaler，透過GP+64+index讀取當下byte，再重讀GP+108，以shift低五位執行無號右移，最後寫回。RAM表不換成常數表；其reset條件對映另有來源證據。

`sf_derive_1973c`重讀GP+108，無號除以8,000,000、遮罩至255，向GP+382寫byte，再將遮罩後的值乘1000，向GP+380寫halfword。原碼沒有本地堆疊框架、巢狀callee或A0回傳值賦值；這兩個衍生欄位的意義及物理單位尚未確認。

提供者接收每次效果前的數值位址及狀態快照；load回應後才更新目的暫存器，後續位址使用當下狀態。提供者可明示合成的暫存器／環境改動，但須保留engine控制及次數限制，不能當作實體中斷證據。部分已知算術保留保守位元集合；模糊分支停止，未知位元不自動補零。HALT、TRANSFER及次數限制均保留原碼順序、寬度及已完成前綴。

`sf_ml_init_call`只橋接指定來源profile的ML9254→18834、ML925C→1973C，並要求明示continuation。它與實際runtime-loop模型共用所有已表示的暫存器及記憶體。中間9A42仍是opaque提供者，可更動GP或clock word，因此後續callee必須重讀；SF與ML次數限制分開。

在此目錄執行：

```sh
sh ./verify.sh --language both
```

`tests/run-tests.sh --language c`只執行有標記的host-only測試。完整驗證另核對確切韌體、封存來源成員及已宣告依賴。需要Python3.10以上及可用的原生C/C++編譯器，不需要PowerShell。目前Windows來源測試每語言通過7組／1,414項；跨平台結果另有收據。

WCH CH32V20x只是硬體候選，尚非確認的實體profile。模型不執行原始RISC-V指令、不模擬ISA、不提供原機ROM、不產生native BIN、不存取實體硬體，也未證明BLE OTA相容性。
