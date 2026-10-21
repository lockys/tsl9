# V4.1.60 Runtime初始化與派送

C/C++模型涵蓋原始ID2966的main9008、initializer9250、永久loop8180及dispatcher901A，共220 bytes／80指令。可攜來源證據拒絕45個原始運算元突變；C11／C++17各執行6組／1,431項。

```sh
sh ./verify.sh --language both
```

此入口使用專案的Python／原生編譯器後端，不需要PowerShell。初始化保留14個深層呼叫及尾端提供者，每個callee均須明示返回路徑。迴圈重讀當下槽位，主機次數用盡不會變成main返回。派送先讀mode再讀argument，單次欄位在callback前清除，結果使用當下S0／S1，再從當下堆疊還原。未知分支及相容但不完整的返回路徑停止。

resident橋接必須是指定候選明示的MRET且目標完整已知9008；嚴格擷取資料更早停止。這是來源／host效果，不是原機ROM或實體ABI證據；不執行原始指令、不模擬ISA、不存取硬體，也未驗證OTA。[歷史封存說明](README.md)保留原始bytes以符合舊收據身分。
