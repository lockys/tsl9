# 傳送分片準備與 pool 初始化順序

[English](readme.en.md) · [專案](../../README.md) · [C/C++ 本體](resident_transmit_fragment_prepare.c)

新增一個完整候選本體：RAM **`0x20000AC6..0x20000BC0`，250 CODE bytes／94 指令**，條件式Flash來源為40D36..40E30。C11／C++17與原指令、13筆控制重定位相符；唯一普通匯入由既有copy helper解析，沒有新DATA或fake provider。

|原始行為|已核對的結果|
|---|---|
|queue head+280為NULL|加frame前回1；非空正常路徑回0|
|remaining halfword大於record+78的byte limit|準備split；首片清marker的0x80、先將node buffer加2，再複製limit bytes；續片保留對應分支|
|首個完整片段|設定prepared state1，清node marker；此分支沒有copy helper呼叫，也沒有明確推進node buffer／remaining，不能改寫成一律複製|
|完整續片|copy後依fresh head／length讀取更新buffer與remaining，prepared state3；split狀態為2|
|frame與flags|copy目的地為record+272指標再加2；保留record+12低位旗標、bit0x10及config TxNumEvent offset18的比較|
|記錄生命週期|沒有明確更新queue head/tail或回收descriptor；prepared不等於無線送出或ack完成|

新本體與先前enqueue可對上同一個head+280、node buffer+4／remaining+12／marker+9。首片split的buffer+2也保留了enqueue先存incoming−2的原始關係。來源、目的地與每次fresh讀取都須有效；**尚未證明此RAM入口的呼叫／pointer綁定、limit的live值或其與buffer大小的界線**。

另對既有 **1,414B／454指令**完整native參考核對初始化與guard：59E70→57962，第一個controller list為空時在579DC呼叫578A4建立pool。controller record的head/tail先發布，**pool配置失敗會跳過pool pointer寫入，但建構器不檢查此回值，仍可能在正常返回後讀出record ID**。這是原CFG與資料流分析，沒有執行負面案例、HOST model或硬體；外部同步、配置成功及初始化順序仍是條件。

RAM `0x20001122..0x2000138E`只是以queue非空作排程guard，不是此分片準備器。原APP config另核對308B；名義BufMaxLen251對應既有建構器的256B frame buffer配置，但尚未證明record+78的limit受其約束。

C/C++部分連結一致：**45,144 CODE＋412 DATA bytes／15,710指令**，3,223正大小FUNC、2,566重定位、0具名普通UND。父bytes、globals與symbolic relocation roles保留；零UND仍不代表完整callback／啟動／無線執行環境。

APP正式來源仍 **162份、73,478／76,800B（95.67% 靜態byte覆蓋）**，不等於功能完成。SDK未連入APP或做最終原位址配置；既有4B啟動來源缺口保留。**沒有新BIN，實體ROM／RAM／IRQ／Flash／OTA相容性仍未證明**。未執行target、HOST model、ISA或硬體，未呼叫廠商API。

[`verification-v1.json`](verification-v1.json) · [`summary.json`](summary.json) · [尚未實作的分片進度診斷候選](feature-candidates.json)

已有固定本機輸入與LLVM時，可唯讀重播：

```sh
python3 experiments/tsl9-resident-transmit-fragment-prepare/verify-v1.py --tool-dir "$LLVM_BIN"
```
