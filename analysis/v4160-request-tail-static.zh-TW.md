# Request 尾跳：欄位修改、stack 正規化與雙byte通知

接續 [request 消費端](v4160-request-consumers-static.zh-TW.md)，本次展開prepare、wrapper、adapter、通知stub及通知body。仍是resident參考候選的離線靜態合約，沒有執行或模擬目標。

| Body | V131範圍（右端不含） | V140範圍（右端不含） | 每版bytes／指令 |
|---|---|---|---|
| prepare | `45612..45650` | `456aa..456e8` | 62／24 |
| wrapper | `533ce..53414` | `5347c..534c2` | 70／25 |
| adapter | `679ce..67a2e` | `67b0c..67b6c` | 96／33 |
| notify stub | `6a70c..6a710` | `6a8f0..6a8f4` | 4／1 |
| notify body | `52f96..52ff8` | `5303e..530a0` | 98／39 |

合計660原始bytes、244條指令；全部operands、SHA256、閉合本機CFG與22條選定路徑見 [JSON](v4160-request-tail-static.json)，由[檢查器](check_v4160_request_tail_static.py)精確重播。兩版各callee的地址差並不一致，所有串接均從原始jump／call operands計算，沒有沿用單一位移。

## Prepare 只改高兩位，不補齊來源

prepare無frame、無call，入口是完整mode A0與pointer A1。pointer為null或mode恰為0時返回0，不解參考pointer。其餘路徑返回1，但只有mode恰為1、2、3時讀寫 `pointer+5`：

| 完整mode | 單byte寫入 |
|---|---|
| 1 | `old OR c0` |
| 2 | `old AND 3f` |
| 3 | `(old AND 3f) OR 40` |
| 其他非零值 | 不讀寫，仍返回1 |

所以返回1不能解讀為「欄位已被修改」或「mode有效」。這裡沒有先截mode為byte；上游caller才以 `U8[P0+3]` 提供mode。

上游pointer是P0+4，因此此helper修改P0+9。全部模式均保存原byte的低六位；它不會把先前七個來源bytes的缺口補成已知值。尤其tag=3來源路徑中，P0+9的低六位仍依賴先前copy及source內容，mode本身也來自該來源範圍。這些物件關係仍需有效配置、copy輸出及非別名保存前提。

## Wrapper 會改寫 caller 的九個 stack words

wrapper以16-byte frame暫存S0／S1，讀取原callerSP+0、+4、…、+32各word的低byte，再以32-bit word寫回同樣九個位置：

- callerSP+4使用signed LB，將低byte符號擴展。
- 其餘八個位置使用LBU，將低byte零擴展。
- 所有九次byte讀取在這九次輸出word寫入之前完成。

寫入的wrapper offsets為SP+16..48，等於**原caller的參數區**，不全在新16-byte frame內。A0–A7及RA沒有被改寫；S0／S1和SP恢復後，以 `JAL rd0` 尾跳adapter，沿用原fallback call的返回位址。

上游fallback本來就提供同樣的signed／unsigned值，所以在有效且未被改寫的caller frame前提下，這次正規化對其值是冪等的。不能將這個性質擴大成所有caller或所有任意32-bit stack值都不變。

A7仍是先前借用的P2+4。wrapper本身不解參考或顯式保存A7，但後續core是否保留該pointer仍未知。

## Adapter 多傳一個輸出pointer

adapter建立80-byte frame，保存RA。它從incoming stack讀九個參數，將相同的signed／unsigned byte擴展結果寫到outgoing SP+0..32；另將 `&SP+61` 寫到SP+36。進入 `68bb4/68cf2` 之前，A0–A7保持原值。

因此core呼叫位置共有8個register與10個stack參數位置，最後一個stack word是借用輸出pointer。這是原指令的位置合約，尚未宣告完整C prototype，也尚未驗證core的輸出大小或保存期。

incoming stack在adapterSP+80..112；outgoing參數在SP+0..39、通知資料在SP+60..61、保存RA在SP+76..79。在普通不溢位且有效的stack配置下，這些區間不重疊。

## 回覆先截低byte，再通知，最後 fresh 讀回

core返回後，adapter依序：

1. 以SB將core A0低byte寫入SP+60。
2. 呼叫通知stub，參數為code=`2036`（hex）、length=2、source=SP+60。
3. 通知返回後重新以LBU讀SP+60，恢復frame並返回這個0..255值。

它不保留完整core回覆，也不以通知函式的A0作返回。若要認定最後結果等於原core回覆低byte，仍需通知及其callees保存SP+60、RA／SP／frame與非別名等條件。

SP+61在adapter內沒有預先初始化，只在core呼叫前作為輸出pointer傳出。因此「兩個通知bytes都已知」尚未成立：第一個由core返回低byte提供；第二個是否寫入、寫入extent與有效值仍需展開core。本次未構造或執行這條通知路徑。

## 通知 body 要求配置14 bytes，再 copy2

stub本身只以rd0尾跳notify body。一般notify入口為code A0、完整32-bit length A1、借用source A2；建立32-byte frame並保存RA／S0／S1／S2。

它以 `length+12` 的32-bit加法結果作A0呼叫RAM `20000236`。本次adapter給length=2，因此要求14 bytes。配置返回null時直接恢復frame，以A0=0返回；非null N時本機寫入：

| 位置 | 寫入 |
|---|---|
| N+0，SH | `0e91`（hex） |
| N+2，SB | length低byte，本次為2 |
| N+4，SH | code低16位，本次為`2036` |
| N+8，SW | payload pointer N+12 |

N+3、N+6、N+7沒有本機寫入，不能視為零值。隨後以 `(N+12,原source,完整length)` 呼叫RAM `20000332`，本次即要求將SP+60..61複製到N+12..13。

所需copy返回後，以fresh task byte `200033ac/200033fc`及原N作A0／A1，恢復SP與保存register，再尾跳 `43208/43294`。實際allocation extent、copy同步完成／保存指標、delivery成功與物件所有權仍需provider合約；本機沒有證明N實際釋放或永久保存。

這段只把通知的資料來源、要求長度及header欄位接通。不能由copy名稱推定借用stack pointer不會被保存，也不能由delivery尾跳推定實際已傳送。

## 重播與剩餘工作

```text
python analysis/check_v4160_request_tail_static.py
python -O analysis/check_v4160_request_tail_static.py
```

兩種模式要求244次逐指令operand變異拒絕、22條選定CFG路徑、65536組mode／old-byte組合、256個signed／unsigned正規化案例，並精確重播ledger。APP、candidate、SDK與上游來源身分亦核對。

仍需展開core `68bb4/68cf2`，證明SP+61的輸出與A7／stack保存合約；另需釐清實際allocation／copy／delivery provider、來源writers、callback枚舉與缺失ROM pattern。本次沒有執行或模擬目標ISA、provider、callback、RF、NV、MMIO、CSR或trap；既有約88.09%的C重建基準不變。
