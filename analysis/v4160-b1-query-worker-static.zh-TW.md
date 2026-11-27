# B1 query worker與record reschedule：返回域、部分更新及節點保存界線

接續[完整RAM query](v4160-b1-ram-query-static.zh-TW.md)，完整展開其直接worker與record callback的reschedule服務，新增 **1,920 bytes／628條指令**。worker正常返回僅為0／1／2／40，query會將非零回覆全部轉成`ffffffff`；reschedule查找未命中仍可返回0，不能把零直接當成節點已改寫。

[Python checker](check_v4160_b1_query_worker_static.py)與[固定JSON ledger](v4160-b1-query-worker-static.json)保存原始hashes、完整operands、CFG、全部stores、邊證書及所有正常出口的最後A0定義。只做離線strict HEX／不可變圖／封閉host整數檢查，沒有目標執行／模擬、可變物件／list／clock／event模型、packet replay、硬體或目標網路分析。既有C重建覆蓋率不變。

## 完整範圍與驗證量

| 函式 | V131 FLASH | V140 FLASH | 每版bytes／指令 | stores／calls |
|---|---|---|---|---|
| worker | `[0x56972,0x56cb2)` | `[0x56ab2,0x56df2)` | 832／266 | 44／7 |
| reschedule | `[0x436a8,0x43728)` | `[0x43734,0x437b4)` | 128／48 | 9／2 |

完整範圍包含首次RET之後的可達分支。兩本體local CFG均無環；未知callees、timer lookup遍歷及整個query仍沒有有限返回保證。

checker把子呼叫也視為opaque A0定義，從所有RET向前追查最後定義，確認只有明示status constants可到達出口。另以不可變DAG遞迴計數涵蓋每版本worker的78,534條、reschedule的4條**語法路徑**；沒有列舉物件狀態，也不將語法路徑數當成可行路徑數、機率或執行量。

## Worker四種正常回覆及前置副作用

令P為入口A0；它沒有本機null guard。

| 條件／出口 | 正常回覆 |
|---|---:|
| fresh U8[P+10]=0 | 1，無frame／callee |
| P+10非零，P+15 bit1清除，fresh U16[P+64]≤5 | 0 |
| 同上但P+64>5，請求threshold(P,62)，回覆低8位寫P+43 | 2 |
| 後段某個schedule比較走過期分支，請求threshold(P,40)，回覆低8位寫P+43 | 40 |
| 其餘正常本機出口 | 0 |

P+10非零後建立16-byte frame，保存RA／S0／S1，**先將U16[P+128]加1取低16位，再清P+24 byte**，之後才決定其他分支。因此非零回覆不代表沒有寫入；較晚的40出口之前可能已完成多組更新，沒有本機整體rollback。

query在worker返回後只檢查零／非零：worker 1／2／40都進query強制`ffffffff`出口，worker 0才繼續query的P+144／P+31及Out更新。這是正常call／frame／register保存前提下的返回串接，不是整條流程成功證明。

## Flags、欄位更新與算術界線

完整store清單在ledger中。以下是按原分支條件的來源關係，不能合併為單一原子snapshot：

- P+15 bit1設置後，bit5可觸發清自身bit5、P+43=0、P+160 word OR4。此分支且P+11=1時，以U16[P+58]×1250做DIVU除以U32[P+148]，加fresh global byte及80，再取low16寫P+132；其兩倍加1250×fresh P+55的low16寫P+130。分母沒有零值guard。
- P+17 bit0、bit1、bit4、bit5在各自路徑都重新讀取，不能當成一份保存的flags。bit0／1／4的scheduled U16比較會把difference的低16位當signed值；這不是未回繞的物理時間先後判斷。
- bit0且fresh P+94==P+64時，將P+60／92／85／86／90分別寫P+96／62／55／56／60，呼叫`0x435ce／0x4365a`，明示參數是P+40 byte及`16*captured P92−2`。其後清P+128，依P+11分支更新P+144／P+58；fresh P+29非零時另請求`0x5627a／0x563ba(P)`。
- 後續U16來源乘積的unsigned `/800`寫P+140，REMU800結果乘1250後用**signed DIV**除以fresh U16 factor，低16位寫P+32；factor=0時RV32 DIV回覆−1，halfword為`ffff`。這不是fault或飽和處理證明。
- P+398 bit3路徑另以P+400、P+64、P+58及fresh P+88形成signed low32乘積／DIV，結果加counter後寫P+400。這組分母同樣沒有零值guard；low32乘積可能超過signed範圍，不能改寫為無回繞的正整數比例。

worker最大明示P存取是P+400 halfword，需402-byte有效範圍。另有外部global pointer、child index×88與child+28的來源存取，並無完整pointer／extent guards；402不是所有來源或未知callee的範圍證明。

## Mask與兩個conditional bytes

P+17 bit1的schedule相等路徑先清P+312與P+316兩個word，再請求`copy(P+312,P+296,5)`，隨後呼叫`0x57ad8／0x57c18(P+312)`，將回覆低8位寫P+301，並獨立重讀／清P+17 bit1。

在matching forward copy、有效範圍、正常完成、所需nonalias及保存條件下，這組請求覆寫P+312..316，先清零區間的P+317..319可保留零。`0x57ad8`的回覆意義仍待展開，不把P+301直接當成已證明bit count或有效除數。

P+17 bit4的schedule相等路徑清bit4，P+330／P+331各自控制P+326／P+327：輸入byte為零時**略過該store**；非零時，bit1設置寫1，否則bit2設置寫2，再否則寫0。兩個byte更新各自獨立，沒有整體初始化保證。

之後請求`0x55f94／0x560d4(P)`，可依fresh P+124把P+160 OR256，再獨立把P+160 OR512並清P+43。其他tail gates可清P+17 bit5；若P+42 bit6與P+70==P+64條件成立，P+16舊值74時改為1，並把P+164 OR1024。未知callees、writers及alias仍可影響這些欄位。

## 重用完整RAM selector，沒有新增重算覆蓋

重新核對[既有完整166-byte selector及44-byte shift](v4160-local-selector-static.zh-TW.md)的原始bytes、strict HEX與first-copy映射。query的P+320 gate為零時呼叫RAM`0x200014c6(P)`，**下一條明示將A0重設為P**再呼叫worker，所以沒有採用selector的scalar回覆作為成功gate。

selector只明示寫P+311／P+310。其初始candidate為兩個byte相加取low8，>36才減37一次，因此數值可到218；不能無條件假定0..36。fallback最多掃描37個位置的條件性bound已在既有checker保存。返回A0是最後probe的bit，不是selected index或成功旗標；counts≥64的shift也不是一般64-bit right shift。

query覆寫A0不代表selector的記憶體副作用或其他live registers消失，也不證明後續worker／callees會保存P+310／311。

## Reschedule：先控制word動作，再驗證index與occupant

reschedule入口是完整U32 index I、scalar V=A1。建立32-byte frame保存RA／S0..S3，先捕獲U32[`0x4002420c`]，寫零並FENCE.I，之後才做guards：

1. 完整unsigned I>15：恢復原控制word，返回2，尚未讀arena。
2. I≤15：讀arena base `U32[0x2000322c／0x2000327c]`，再讀U32[base+12×I]；該occupant word為零亦恢復並返回2。

base自身沒有null guard。這次guard只檢查callback occupant word，未使用它作timer pointer。最大明示arena讀取到base+183，並不是實際arena allocation證明。

I∈0..15時，mask=low16(1<<I)恆為單一非零bit。接著請求完整30-byte RAM timer lookup `0x20000314(0,mask)`：它依node的task byte與event halfword查找，沿node+12的next遍歷，未證明list無環／有限。

## Lookup未命中也返回零；命中才在clear後寫L+8

lookup回覆L被保存在S3，原V保存在S1：

- L=0：略過event-clear及L+8 store，恢復控制word，仍返回0。
- L非零：請求既有完整68-byte event-clear `0x4358a／0x43616(0,mask)`；忽略其回覆，正常返回後才寫U32[**保存的L+8**]=原V，再恢復控制word並返回0。

clear可能返回拒絕，這個helper仍不依其status分流。它沒有重新讀取／驗證L，也沒有把V寫回arena row。保存pointer數值不證明clear之後L仍有效、未被釋放或未被alias破壞。控制word恢復只限正常本機出口，不是實體狀態／異常恢復、重入或原子性的保證。

因此reschedule的0只表示相應guards與普通call流程走到本機出口，**不能證明lookup命中或L+8確實改寫**。這正是record callback其他R分支的下游：fresh U8[P+41]作I，調整後的SP+12 word作V；正常helper回覆0／2由callback傳回，而上層handler不採用該scalar來決定record清理。

## 重播與剩餘工作

```powershell
python analysis/check_v4160_b1_query_worker_static.py
python -O analysis/check_v4160_b1_query_worker_static.py
```

兩模式保留完整祖先證據、strict HEX與固定ledger。每版worker299條CFG邊、reschedule50條邊均有語法路徑證書；DAG最後A0定義／計數涵蓋全部本機正常出口。628個逐指令變異與78個typed-load變異必須拒絕。封閉整數檢查明列U16 counter／signed16、byte除零、取樣H×全部K16及全部byte pairs等範圍，沒有執行目標callee或可變list／clock。

後續仍需展開`0x435ce`、`0x5627a`、`0x55f94`、`0x57ad8`等巢狀服務；確認clear後L保存期、實際arena／timer／query／record同一性，以及`0x5d006／0x5d14e`、clock／hook綁定、其他writers與完整消費釋放順序。
