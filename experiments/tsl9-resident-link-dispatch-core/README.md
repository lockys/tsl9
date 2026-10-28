# 狀態 callback 分派、連線移除與請求核心

[English](readme.en.md) · [專案](../../README.md) · [C/C++ 本體](resident_link_dispatch_core.c)

新增 **14 個完整 SDK 候選本體，1,260 CODE bytes／495 指令**。C11／C++17 與原指令及100筆重定位相符。原寄存器繫結、volatile 存取、條件式Xwchc與必要inline assembly保留，仍需原布局／ABI。

|證據位置|已確認的靜態行為|
|---|---|
|`0x4ED98..0x4EDD2`|真正的12-slot狀態callback分派器；逐次讀取 `0x20003358..0x20003388`，跳過NULL後繼續，保留原handle／changeType給非NULL callback|
|`0x4F00C..0x4F058`|找不到連線回2；找到後先分派event1，再有條件free record+44、清60B、設handle=FFFF／state=0，回0|
|`0x4F0CC..0x4F128`|另一個per-link走訪API；NULL callback在加frame前返回，逐次重讀total與record pointer，傳入60B record指標。它不是狀態分派器，完整入口是4F0CC|
|`0x4EB12..0x4EBC2`|176B請求核心；selector6找既有記錄，其他路徑配置。保留交易byte遞增／跳過0、失敗清理及回0後傳入delay30的排程|
|`0x4D4BC..0x4D5A0`|無out pointer回1、未連線回20、無slot或heap配置失敗回21；保留32B nested配置及原本兩次移位，不改成推測索引公式|
|`0x4D806..0x4D820`、`0x4D6E0..0x4D70A`|數值delay乘1600、以literal4D6E0排程；非零key callback走status23及釋放frame後清理。實體時間單位未證明|
|`0x4EA8C..0x4EB12`|保存serializer指標後間接呼叫；寫selector、transaction及長度欄位，數值channel5。來源、長度與callback有效性仍須成立|
|RAM `0x200001E4..0x2000021C`|原Flash來源40454..4048C；依heap鏈範圍條件調整buffer指標，fallback保留原指標；未證明live heap鏈有效／終止|
|`0x534A6..0x534AA`|只有一條4B尾跳至6A626，沒有把相鄰函式算進來|

**條件式呼叫鏈：**若非零total初始化完成48B清0，且到註冊／分派前無改寫，first-empty註冊會把literal4D916放在首slot。相同表格的穩定分派iteration便會以原handle／changeType呼叫它；連線移除路徑再接到先前重建的reason0記錄清理。這是原候選CFG與資料流證據，**尚非實體呼叫或全域生命週期證明**。

`0x4EB12` 保留舊匯入符號名稱，但現在由實際176B原始本體解析，沒有建立空alias。10個新匯入由既有真實provider解析；**目前唯一具名UND為 `0x6A626`**。另有三個間接呼叫點的所有可能目標尚未閉合，literal callback仍需原位址綁定，不能用UND數量代表完整環境。

selector6路徑會在讀nested halfword前使用record+12指標，未新增NULL guard；對應有效性是條件。也未把數值status、channel5或delay乘數擴張成完整協定／實體時間／OTA診斷。

C/C++ 部分連結結果一致：**44,610 CODE＋412 DATA bytes／15,515 指令**，3,175正大小FUNC、2,535重定位、1具名UND。父allocated bytes、globals與symbolic relocation roles保留，原UND參照解析至真實CODE。

APP正式來源仍 **162 份、73,478／76,800B（95.67% 靜態byte覆蓋）**，不等於功能完成。SDK未連入APP或做最終原位址配置；既有4B啟動來源缺口保留。**沒有新BIN，實體ROM／RAM／IRQ／Flash／OTA相容性仍未證明**。未執行target、HOST model、ISA或硬體，未呼叫廠商API。

[`verification-v1.json`](verification-v1.json) · [`summary.json`](summary.json) · [未實作的離線診斷候選](feature-candidates.json)

已有固定本機輸入與LLVM時，可唯讀重播：

```sh
python3 experiments/tsl9-resident-link-dispatch-core/verify-v1.py --tool-dir "$LLVM_BIN"
```
