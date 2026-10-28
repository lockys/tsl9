# 連線事件 callback 與待處理記錄清理

[English](readme.en.md) · [專案](../../README.md) · [C/C++ 本體](resident_link_event_callback.c)

新增 **14 個完整 SDK 候選本體：1,068 CODE bytes／428 指令**。C11／C++17 的原生物件與原指令、82筆重定位相符；保留原寄存器繫結、volatile 存取及必要 inline assembly，仍需原布局與 ABI。

|位置|已確認的靜態行為|
|---|---|
|`0x4D916..0x4D952`|先忽略 loopback handle FFFE；event1 直接以 reason0 尾呼叫清理，event2 查 connected bit1，結果為false才清理；其他event返回|
|`0x4F072..0x4F0A4`|loopback直接回true；沒有connection record回false，否則檢查record+4的state flag並回傳boolean|
|RAM `0x20000A94..0x20000AC6`|候選Flash來源 `0x40D04..0x40D36`；只取樣一次total byte，依60B stride與handle+2找第一筆，找不到回NULL|
|`0x4D83A..0x4D916`|依live數量掃16B待處理記錄；reason0另走第二組清理並處理resource indices4..7；保留逐次fresh讀取與匹配條件|
|`0x4D66E..0x4D6BA`|nested pointer非NULL時，依序有條件free其+12／+20子指標，再free nested owner；清16B記錄後把slot9設FF|
|`0x4D820..0x4D83A`|把slot9傳給既有候選記錄移除helper43A14，然後將slot9設FF；不推定實體計時器狀態|
|`0x4E2EE..0x4E362`|配置32B訊息；NULL則不送出。body+8的24B依來源copy或填0；釋放48B frame後尾跳既有message send|
|`0x4EBC2..0x4EBDA`|24B／12指令序列化callback，重讀兩個halfword，依小端順序寫4B並回4；不合併原始fresh讀取|

上一輪只保留數值 `0x4D916` 的 callback 現在有完整候選本體。另找到 wrapper 傳入 `0x4EBC2` 的literal並重建其本體；兩者仍需原位址綁定，**不是新增typed relocation或已證明實體呼叫**。

6 個普通匯入由既有free／fill／copy／message及記錄helper解析；**`0x4EB12` 保留為唯一具名UND**，沒有補入推測本體。因此callback清理路徑尚未閉合，也尚未證明會清除CCC或能修復OTA。wrapper的stack payload完整初始化仍未證明，未自行把未證明的bytes改成0。

C/C++ 部分連結物件一致：**43,350 CODE＋412 DATA bytes／15,020 指令**、3,048正大小FUNC、2,435重定位、1具名UND。父輸入bytes、globals、typed roles全部保留。加入真實序列化callback後以 `native-v2` 保存完整證據；13-body舊試驗 `native-v1` 留本機。

APP正式來源仍 **162 份、73,478／76,800B（95.67% 靜態byte覆蓋）**，不等於功能完成度。SDK未連入APP或做最終原位址配置；既有4B啟動來源缺口保留。**沒有新BIN，實體ROM／RAM／IRQ／Flash／OTA相容性仍未證明**。未執行target、HOST model、ISA或硬體，未呼叫廠商API。

[`verification-v1.json`](verification-v1.json) · [`summary.json`](summary.json) · [尚未實作的離線診斷候選](feature-candidates.json)

已有固定本機輸入與LLVM時，可唯讀重播：

```sh
python3 experiments/tsl9-resident-link-event-callback/verify-v1.py --tool-dir "$LLVM_BIN"
```
