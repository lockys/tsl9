# Callback 鏈表寫入：借用物件、兩階段移除與 latch

接續 [callback查找與record清理](v4160-typeb0-record-static.zh-TW.md)，本次完整核對callback鏈表的append、remove、第二條鏈表detach及固定參數wrapper。兩份參考候選合計 **688 bytes／278條指令**，全部由原始sparse HEX覆蓋，且與候選bytes一致。這是條件性靜態合約，沒有提高既有C重建覆蓋率；實際installed provider、所有writers及完整物件保存期仍未閉合。

| 完整範圍（右端不含） | V1.31 | V1.40 | 每版 |
| --- | --- | --- | --- |
| append | `4CF22..4CF96` | `4CFBA..4D02E` | 116B／49i |
| callback-list remove | `4B830..4B88C` | `4B8C8..4B924` | 92B／38i |
| paired-list detach | `4B7D8..4B830` | `4B870..4B8C8` | 88B／35i |
| wrapper | `4CF96..4CFC6` | `4D02E..4D05E` | 48B／17i |

前三者各有一條構成cycle的搜尋edge；wrapper為DAG，呼叫append使用無新link尾移交。原始operands、每個call target、完整CFG與hash固定於[checker](check_v4160_callback_list_writers_static.py)及[ledger](v4160-callback-list-writers-static.json)。搜尋仍須有效、有限鏈表等前提，沒有把靜態CFG當作已執行或終止的證明。

## Append保存的是原A3物件pointer

append建立32-byte frame。原A0是config pointer；若為0，直接回覆2。非空時保存config，並把原A3物件pointer保存到S2，準備自己的descriptor：

| local offset | 本機寫入 |
| --- | --- |
| halfword SP+8 | low16(入口A1) |
| byte SP+10 | low8(入口A2) |
| byte SP+11 | 此處沒有直接寫入 |
| word SP+12 | 原config pointer |

以A0=`&SP8`呼叫 `4CE22 / 4CEBA`。這個validator／setup callee的完整效果尚未展開，其他argument registers仍是ambient值，不能假定它看不到原A3。傳入pointer也沒有證明它只讀指定範圍或不保留stack address。

callee非零回覆被完整傳回；零時才檢查原A3是否空。**A3為空會返回0，但沒有本機node配置或發布。** 因此前段setup的0、callback節點已存在、實際功能已綁定是不同結論。

A3非空時，fresh讀取 `U16[config+10]`，為0回2；非零則呼叫 `20000040(12,0x4705)`。配置回覆空時回19。這個key不是SP+10的descriptor byte，兩者不可混淆。

配置結果N非空後，本體直接寫入：

```text
U32[N+0] = 0
U32[N+8] = 原A3物件pointer
U16[N+4] = fresh U16[config+10]    // allocator返回後重新讀取
```

bytes6..7沒有本機直接初始化。config key在allocator之前、之後是兩次fresh read；後一次沒有再次做非零檢查，不能無條件把它等同於較早通過guard的值。

## 節點初始化後才發布，沒有物件深拷貝

callback head為 `20002F94 / 20002FE4`。empty head時直接存入N；非空則沿next word尋找第一個null，再把N寫到尾端next。三個node欄位stores都在這個本機pointer發布之前。沒有duplicate key檢查、count上限或cycle detection。

普通返回且saved status保持時，配置成功的append回0；但未知allocator、validator或其他writer可能有自己的效果，不能由0推導實際callback已可用。

node+8保存原A3的pointer值，**沒有在這個本體中複製A3所指物件內容**。接回前輪getter後，來源關係是：

```text
node+8 -> 原A3物件pointer V
wrapper再讀 U32[V+8] -> callback word
```

因此物件V與其+8欄位需要活到後續查找／呼叫時。12-byte節點本身的配置，不證明V的配置身分、保存期、embedded function ABI或有效性。

## Remove：先改主鏈表，再嘗試移除另一條鏈表

callback remove從自己的head搜尋第一個 `U16[node+4] == 完整入口A0`。key不截成U16；沒有相符項目就返回1，且尚未建立match分支的32-byte frame。

找到node後，先取其next，更新head或predecessor next；再以**該node地址原值**呼叫private release `20000110`。這裡沒有直接釋放node+8所指callback物件。

然後以 `(原key,&parent_SP8)`呼叫paired detach `4B7D8 / 4B870`。它的回覆被傳回上層：

- paired detach失敗1：主callback節點已先被摘除，且已嘗試private release；沒有本機rollback。
- paired detach成功0且原A1非空：把 `U32[parent_SP12]`寫到原A1所指output。
- paired detach成功0但原A1空：不寫output，仍回0。

所以返回1既可表示主鏈表未命中，也可表示主鏈表已改動後，第二階段未命中。不能只依回覆碼推導兩條鏈表都保持原狀，或兩個移除動作是原子操作。

## Paired detach：key來自node+8所指物件的+10

第二條鏈表的head為 `20002F88 / 20002FD8`，和callback head不同。它不是直接比較node+10，而是：

```text
V2  = U32[secondary_node+8]
key = U16[V2+10]
```

這個V2讀取沒有本機null guard，須另證有效物件與extent。搜尋以完整入口A0比較key，第一個命中項目同樣先更新head或predecessor next。

若caller A1非空，準備copy service `20000332(A1,secondary_node+4,8)`；之後private release該secondary node地址，忽略provider回覆並固定回0。未找到返回1。

由callback remove呼叫時，A1是其32-byte frame內的SP+8。若copy採用預期byte語義，secondary node+8的word會落到parent SP+12，成為remove可能寫給外部caller的output。**這個output來源是第二條鏈表的node+8，不是較早已摘除的callback node+8。**

即使兩邊以相同key搜尋，仍未證明唯一性或兩條鏈表的物件身分相同。此處也沒有直接釋放secondary node+8所指物件。copy與private release都是呼叫嘗試，不是實際釋放完成或safe ownership transfer的證明。

## 固定wrapper：先設latch，再看bit0

wrapper使用以下固定地址；兩版不能套用同一個RAM偏移量：

| 用途 | V131 | V140 | 差值 |
| --- | --- | --- | --- |
| latch byte | `20002F7C` | `20002FCC` | `0x50` |
| config | `20002E7C` | `20002EC8` | `0x4C` |
| callback object | `20002EBC` | `20002F08` | `0x4C` |

若fresh latch非零，直接回0。若為0，**先寫latch=1，再測入口A0的bit0**：bit0為0回0，bit0為1則無新link尾移交：

```text
append(config,4,16,callback_object)
```

本體沒有在selector為even、append回2／19或未知validator回覆後，把latch清回0的路徑。這只是本機順序與在無其他writer前提下的保存條件，不能解讀為thread-safe once、同步鎖或實際重試政策已證明。

wrapper普通返回0也可能只是因latch早已非零或bit0為0，沒有新增節點。

## 接回ID11 defaults仍有來源缺口

重用 [ID11 defaults](v4160-id11-outer-tail-static.zh-TW.md)，它會初始化兩個head為0、latch為0，並對上述callback object直接寫word+0=0、word+8=0；word+4是另一個欄位。已知reader讀取的是object+8，不能把word+4的既有函式pointer當成同一個欄位。

這接上了固定wrapper的物件來源，卻未證明較晚哪個writer把object+8設定成有效callback、validator如何調整config+10、wrapper實際何時被呼叫，或defaults之後各欄位是否保持。初始化、加入鏈表與真正可呼叫的綁定，仍需逐段證明。

本次halfword-aligned靜態掃描找到直接head讀取、地址形成、append/remove及defaults清零的候選位置；掃描只協助定位，沒有證明所有computed、別名或其他映射下的writers都已找齊。

## Frame與離線重播

append frame為32B，validator descriptor在SP+8..15，保存槽在SP+16..31；paired detach的8-byte snapshot目的地在remove frame的SP+8..15，避開remove的SP+20..31保存槽。detach另有16B child frame。這些位移證據不是callee實際extent或no-escape合約。

```powershell
python -B analysis/check_v4160_callback_list_writers_static.py
python -O -B analysis/check_v4160_callback_list_writers_static.py
```

檢查涵蓋完整operands／hash、每條CFG edge的terminal見證、空／一筆／兩筆append、主鏈表已改動後的第二階段失敗、snapshot投影、65536組latch/selector純量，以及278條指令與6個typed-load變異。所有普通call-return、list有限性、valid node/config/object/output、saved-frame保存及無adverse alias／IRQ／DMA／重入等仍是前提。

全程只讀本機bytes、原始HEX、不可變CFG與host純量；沒有執行或模擬目標ISA、callback、provider、RAM／heap／list、MMIO或硬體。GitHub僅新增本階段三份分析與驗證檔案。下一段繼續展開validator、第二條鏈表的建立端、object+8 writers與wrapper實際caller。
