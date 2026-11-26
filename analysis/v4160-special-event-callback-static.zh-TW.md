# Special handler 與 record callback：事件優先序、借用 buffer 及枚舉界線

接續[ID11與outer尾段](v4160-id11-outer-tail-static.zh-TW.md)，本次展開可選task的handler及最後發布的record callback。原bytes仍是resident參考候選；handler／callback是否實際被排程、provider綁定及物件有效性尚未由此確定。

| Body | V131範圍（右端不含） | V140範圍（右端不含） | 每版bytes／指令 |
|---|---|---|---|
| special handler | `6d26c..6d4a4` | `6d458..6d690` | 568／188 |
| message helper | `6d214..6d26c` | `6d400..6d458` | 88／29 |
| record callback | `4cff6..4d068` | `4d08e..4d100` | 114／45 |
| invalidate helper | `4cfd0..4cff6` | `4d068..4d08e` | 38／15 |

合計1616個原始bytes、554條指令。完整operands、SHA256、CFG及30條選定路徑見 [JSON](v4160-special-event-callback-static.json)，由[靜態檢查器](check_v4160_special_event_callback_static.py)精確重播。handler在`6d4a4/6d690`終止，後面的函式沒有被算入同一body。

## 事件選擇與返回mask

handler建立32-byte frame，保存RA、S0、S1；S1保留完整32-bit入口A1。它一次只處理以下優先序中的首個命中位元：

```text
bit15 (8000) > bit14 (4000) > bit0 (1) > bit1 (2) > bit2 (4)
```

bit15與bit14以shift／signed比較檢查，但所需callee返回後的結果是**完整入口mask XOR所選bit**，不截成16位。若五個bit都沒有命中，則返回0。檢查器涵蓋全部65536個low16及四組upper16，確認選擇域與高16位保存的整數關係。

因此不能假設所有未處理bit都原樣返回，也不能把結果簡化為單一boolean。handler的本機CFG無迴圈；跨callee的返回、S1／SP／frame／RA等保存仍需另外成立。

## bit15 message 路徑的呼叫界線

以fresh task byte `200035f5/20003645`作A0呼叫RAM `2000028c`。null返回直接走mask XOR8000；非null返回保存在S0，當作message pointer。

後續fresh flag與message byte欄位決定呼叫哪些路徑：

- fresh flag `200035ab/200035fb`為0時，先呼叫message helper，再以原S0呼叫 `431ba/43246`。
- type208依byte+2、byte+12或byte+7進一步分類；部分路徑另呼叫RAM `20000a94`，要求有效返回物件或null分支。
- type145檢查byte+1=14及LHU+4=`1405`，再讀取word+8所指資料的byte+1/+2組成索引，進入相同lookup邊界。
- 部分路徑呼叫 `43208/43294`，參數為fresh byte `20003612/20003662`及原message S0，然後返回mask XOR8000。

這些呼叫分屬不同路徑。不能同時宣稱message已釋放、已轉移所有權、callee不保存指標，或所有payload讀取都在有效extent內。free／delivery命名僅用於識別既有候選服務，實際消費、保存與副作用仍待證明。

## Message helper 的signed byte與間接尾跳

message helper沒有frame或本機store：

- type208尾跳 `6cf34/6d120`，本次未展開該callee。
- type145必須通過byte+1=14、LHU+4=`1405`；令payload=`U32[message+8]`。它沒有先檢查payload為null，需保留有效可讀物件前提。
- 使用**signed LB**讀payload byte+3至A1；值等於127時不走callback，其餘可能包含−128..−1。
- 對hook object及其word+4函式指標都有null guard。通過後A0=`U8[payload+1] | (U8[payload+2]<<8)`，以A1=signed byte尾跳該函式。

這裡是保留RA的間接尾跳，不是新建link的普通call；不匹配路徑也沒有強制統一的返回status。payload、hook及callee ABI／保存期未由本機guard自動成立。

## bit14與低事件的狀態更新

bit14呼叫 `4435c/443f0`及 `44310/443a4`，所需返回後給出入口mask XOR4000。

低事件的成功服務路徑修改word `200035cc/2000361c`：

| 選中的event | 本機更新 |
|---|---|
| bit0 | `(freshword & fffffff0) | 6` |
| bit1 | `freshword & ffffff0f` |
| bit2 | `freshword & fffff0ff` |

每類都有可選的間接callback：fresh讀hook word `20002ff0/20003040`，再讀object word+0；兩層pointer皆非零才以A0=更新後的word、A1=0呼叫。它們需保存後續返回計算使用的S1及frame等；實際hook內容、callback副作用與保存合約未知。服務未滿足其分支條件時，仍可直接返回對應mask XOR bit。

## SP+4 request 並非所有分支都完整初始化

bit0分支會將A1=SP+4、A0=fresh task byte傳給 `482f4/4838c`：

- 一條路徑寫SP+4、SP+5，並要求copy6 bytes至SP+6..11。
- 另一條路徑只將SP+4寫為3。
- 兩者共同寫SP+12、SP+13。

因此第二條路徑的SP+5..11沒有被本機初始化。caller也沒有在共同call處明確給出整個10-byte區間的長度，不能在未展開callee前宣稱它會／不會讀那些bytes，或把它們直接視為已知零值。較完整路徑同樣需要copy provider的輸出與保存合約。

buffer在32-byte frame內，但實際讀取extent、同步消費與是否保存SP指標仍未知；本次沒有構造輸入或執行此路徑。

## Record callback：三類入口與未知長度的枚舉

record callback使用32-byte frame，保存RA及S0–S2，S2保存完整入口selector：

1. A1=1：呼叫 `4b61e/4b6b6`；其返回非零時另呼叫 `4b5d2/4b66a`，然後進入枚舉。
2. A1=2：先以入口A0、A1=1呼叫 `4f072/4f10a`；返回0才接到第一類的檢查，非零則RET。
3. 其他A1：不呼叫這些helpers，直接恢復frame返回。

初次枚舉call `4bf06/4bf9e`收到：

```text
A0=1, A1=ffff, A2=6ea70/6ec60, A3=2, A4=SP+14
```

這個ROM pointer與前階段保存的外部ROM pointer相符，位於各自候選檔右端之外，其pattern內容未知。SP+14/+15亦沒有本機預先初始化，必須由實際callee的輸出合約提供。

node非零時，callback反覆：

- 以入口selector與fresh `U32[node+12]`呼叫invalidate helper。
- 讀取fresh LHU[SP+14]為A2。
- 以 `(node,ffff,LHUSP14,0)`呼叫 `4c35e/4c3f6`取得下一node。

`ffff`在迴圈中沒有遞減，不能拿來推定最多65535次。沒有local iteration bound，也未證明next-node必然進展、無環或最後返回null。node/payload extent、callee對S0–S2／SP／frame的保存，以及借用SP+14的初始化、消費與保存期仍需展開。

實際bytes `3087`已按快取且雜湊固定的LLVM Xwchc來源確認為 **LHU A2,14(SP)**；不是A4或浮點load。檢查器重播6個官方LHUSP向量及128個register／even-offset欄位組合。

## Invalidate helper 的兩種路徑

selector恰等於完整`ffff`時，helper以入口A1作pointer尾跳上一階段的pool-margin clear，沿用其count／有效保留空間前提。

其他selector則呼叫 `4b2e4/4b37c`。若返回R非零，本機寫SH `ffff`至R+0、SB0至R+2，再返回該lookup結果；null則跳過寫入。這裡沒有allocation／extent／physical-alias保證，也沒有固定boolean返回值。

## 重播與剩餘工作

```text
python analysis/check_v4160_special_event_callback_static.py
python -O analysis/check_v4160_special_event_callback_static.py
```

兩種模式要求554次逐指令operand變異拒絕、30條選定CFG路徑、65536個事件優先序案例、6個LHUSP官方向量及128個欄位案例，並精確重播JSON。APP／candidate／SDK及上游靜態來源身分一併核對。

仍需展開message/provider與type208 tail、request對SP+4的實際讀取範圍、枚舉helper與缺失ROM pattern、間接callee ABI及各種物件保存期。本次沒有執行或模擬目標ISA、provider、NV、callback、MMIO、CSR或trap；不增加既有約88.09%的C重建基準。
