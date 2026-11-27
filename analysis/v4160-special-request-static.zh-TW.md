# Special request：10-byte copy、tag 分類及返回合約

接續 [special handler／callback](v4160-special-event-callback-static.zh-TW.md)，本次展開 handler bit0 呼叫的 request callee。兩版都是 resident **參考候選**，尚未證明已安裝於實機，亦沒有執行或模擬目標。

| 候選 | 完整範圍（右端不含） | bytes／指令 |
|---|---|---|
| V131 | `482f4..4845c` | 360／132 |
| V140 | `4838c..484f4` | 360／132 |

合計720原始bytes、264條指令。逐指令operands、SHA256、完整本機CFG、40條選定路徑及整數域見 [JSON](v4160-special-request-static.json)，以[檢查器](check_v4160_special_request_static.py)精確重播。雖有向低地址跳轉，完整本機CFG仍無迴圈；跨callee是否返回另列前提。

## 三個前置返回

令 `g=20003000/20003050`。callee建立48-byte frame，保存RA及S0–S5。

1. fresh word `[g−236]` 非零：返回17。
2. fresh byte `[g+944] & 5` 為零：返回18。256個byte中有192個通過此flag條件，不能簡化為某一單獨bit。
3. 通過以上條件後，先將入口task低byte寫入 `[g−195]`，再呼叫RAM `20000040`，參數 `(12,4717)`。將實際返回值（包含null）寫到 `[g−236]`，null返回19。

前兩個gate在source pointer保存與task byte寫入之前；配置失敗則已經有task byte／slot寫入。實際配置大小、有效extent及allocator身分仍需provider合約。

## Caller SP+4 的實際 copy 呼叫範圍

入口A1保存於S4；非null配置P依序寫 `P[0]=task低byte`、`P[1]=0`，呼叫RAM `20000332`：

```text
A0 = P+2
A1 = 原入口A1（S4）
A2 = 10
```

上游handler提供A1=`callerSP+4`，所以**呼叫要求涵蓋 callerSP+4..13，目的為P+2..11**。這是確定的實參範圍；真正逐byte讀寫、同步完成、重疊處理與保存期仍取決於copy provider，不能把它直接當成已驗證memcpy。

上游tag=3路徑僅寫callerSP+4、+12、+13：

| Caller來源 | 目的位置 | tag=3路徑本機來源 |
|---|---|---|
| SP+4 | P+2 | 已寫3 |
| SP+5..11 | P+3..9 | 七個bytes未由該caller路徑初始化 |
| SP+12..13 | P+10..11 | 已寫fresh設定bytes |

另一條來源路徑另有copy6的輸出前提。本次只縮小來源證明缺口，沒有構造輸入，也沒有宣稱實際未初始化讀取或可利用性。

request本體沒有直接以S4為base讀來源，也沒有將S4顯式寫入global／heap；它把S4傳給copy provider。這**不等於provider不保存指標**。持久slot保存的是配置返回值；配置物件與借用來源是不同的保存問題。

## Tag 分類在配置與 copy 之後

copy返回後重新讀取 `[g−236]`，再讀fresh物件byte+2；沒有新的null guard。若要把tag視為剛才來源byte，還需slot不被改成其他物件、有效非別名extent及copy輸出等條件。

| fresh tag | 本機對byte+2的映射（穩定有效storage前提） | 後續 |
|---|---|---|
| 0／1／2／3／4 | `13／1d／12／10／15`（hex） | 共用查詢 |
| 5／6／7／8／9／10 | `5／2／0／1／6／4`（decimal） | 先查詢25，再共用查詢 |
| 11..255 | 不作上述映射 | 返回1 |

tag0..4先寫映射值，再fresh讀同一byte、OR `10`（hex）後寫回。tag9寫的是先前比較tag6時載入且仍保留於A3的**6**，不是更早的5；檢查器另核對該路徑中間沒有改寫A3。

tag5..10以A0=25呼叫 `45f9c/46034`。只有**完整返回register恰為127**才略過OR `40`；其餘回覆重新載入slot，對fresh byte+2作OR `40`。不能截成低byte比較。

未知tag返回1時，配置、slot發布及copy呼叫都已發生。本函式沒有local free或slot清零，不能據此宣稱實際洩漏、永久保存或合法所有權。

## 借用輸出與兩種返回流程

有效tag的共用路徑呼叫 `6bc2e/6be12`，參數 `(1055,requestSP+7)`。SP+7沒有本機預先初始化。原bytes `9c83` 是 **QK LBUSP A5,7(SP)**；依固定雜湊的LLVM快取確認，並重播6個官方向量及128種register／offset欄位案例。

- SP+7讀值非零，或fresh byte `[g+586] != 3`：呼叫 `48070/48108`，S0保存實際完整回覆；非零時另呼叫 `47fc8/48060`，最終仍返回所需保存的S0。
- SP+7為零且role byte=3：依序呼叫 `456ea/45782`、`4fd72/4fe0a`（A1=SP+8、A0沿用前call回覆）、`45d3a/45dd2`（A0=SP+8）、`45f9c/46034`（A0=17），再令S0=0。
- 最後查詢17的回覆非零時，另呼叫 `43728/437b4`，參數為fresh byte `[g+940]`、4、`low32(reply*1600)`；所需call返回並保存S0／frame後，這條路返回0。

requestSP+7與SP+8都是新48-byte frame中的借用輸出位置，和上游callerSP+4來源不同。沒有local初始化不代表callee未寫入；輸出extent、有效性、同步消費、指標保存及跨call欄位穩定性仍待展開。timer乘法只證明低32位算術，不證明時間單位、回覆域或實際排程。

## 重播與範圍

```text
python analysis/check_v4160_special_request_static.py
python -O analysis/check_v4160_special_request_static.py
```

兩種模式核對264次逐指令operand變異拒絕、40條選定CFG路徑、完整tag／flag byte域、LBUSP來源向量與精確ledger。APP、兩份candidate、SDK與上游靜態來源亦核對身分。

仍需展開query1055、fallback與role3 callees、實際copy／allocator綁定、配置slot的下游消費與保存期，以及callback枚舉與缺失ROM pattern。本次沒有執行或模擬目標ISA、provider、NV、callback、MMIO、CSR或trap；既有約88.09%的C重建基準不變。
