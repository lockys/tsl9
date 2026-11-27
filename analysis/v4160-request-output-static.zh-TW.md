# Request 輸出：整數分段合成與鏈表 lookup

接續 [request core](v4160-request-core-static.zh-TW.md)，本次完整展開物件lookup與兩個輸出helper。所有證據來自resident參考候選，沒有執行或模擬目標ISA、鏈表、provider或硬體。

| Body | V131範圍（右端不含） | V140範圍（右端不含） | 每版bytes／指令 |
|---|---|---|---|
| lookup | `55108..55120` | `551d2..551ea` | 24／9 |
| signed map Q | `639ca..63a2c` | `63ab4..63b16` | 98／36 |
| unsigned map R | `63966..639ca` | `63a50..63ab4` | 100／37 |

合計444原始bytes、164條指令。完整operands、SHA256、CFG、48個完整32-bit區間憑證、六條lookup選定路徑及1022個core合成案例見 [JSON](v4160-request-output-static.json)，由[檢查器](check_v4160_request_output_static.py)精確重播。

## Lookup 沿鏈表找 byte key，沒有長度上限

lookup無frame、無call、無store。先讀head word `20003414/20003464`（前階段context B+92，與B+88 busy object不同），之後：

```text
node非零：
  U8[node+8] == 完整入口A0 → 返回node
  否則 node = U32[node+0]，再次檢查
node為零 → 返回0
```

head只在入口讀一次，next則在每次未命中後fresh讀取。byte key與**完整32-bit A0**比較；大於255的raw入口值無法命中byte key，但不代表函式會有限時間返回。沒有local counter、長度限制或cycle檢查；需要有效node／next、鏈表進展、無環或其他終止來源才能證明搜尋結束。

已驗證head null、首節點命中、跳過一個節點後遇null三種結構路徑；沒有執行實際鏈表或宣稱它只有這些情況。每個被讀node至少需要+0..8可讀extent；返回node並不證明core後續所需的108-byte物件有效性、唯一所有權或保存期。

上游完整caller鏈在參數保存前提下提供key=1。鏈表初始化、head／next／key writers與實際節點內容仍待追查。

## Q：完整 signed32 分段

Q與R都無frame、無load、無store、無call；只改寫A0／A4／A5，沿RA返回，因此其本機body保存SP、RA及S0–S11。沒有將任何物理單位、RF設定或裝置行為套入這兩個整數map。

Q使用完整**signed32** A0：

| 輸入x | Q(x) |
|---|---|
| `−2^31..−18` | 1 |
| `−17..−10` | 3 |
| `−9..−5` | 5 |
| `−4..−3` | 7 |
| `−2..0` | 9 |
| 1／2／3／4／5／6 | 11／13／17／21／27／37 |
| `7..2^31−1` | 63 |

例如−17屬第二格；原始BLT是嚴格小於−17，不能錯移到第一格。Q本身沒有先截成byte；只有core之前的LB提供了signed byte輸入域。

## R：完整 unsigned32 分段

R使用完整**unsigned32** A0，以下負數結果是logical signed literal，實際RV32回覆為對應的two's-complement bits：

| 輸入u | R(u) |
|---|---|
| 0..2 | −18 |
| 3..4 | −10 |
| 5..6 | −5 |
| 7..8 | −3 |
| 9..10 | 0 |
| 11..12 | 1 |
| 13..16 | 2 |
| 17..20 | 3 |
| 21..26 | 4 |
| 27..36 | 5 |
| 37..62 | 6 |
| `63..2^32−1` | 7 |

例如raw `ffffffff`走最後一格，不能將R的比較改成signed。Q的回覆都為正整數，因此接到R時不需要假設未知callee的輸出域。

檢查器由原指令literal建立每個區間，確認每個branch在整個區間上的真假一致、最後A5定義及返回值，並核對相鄰區間無缺口或重疊，分別覆蓋全部signed／unsigned 32-bit域。這是靜態整數區間證明，沒有執行目標或建立register／RAM模擬器。

## 串回 core：輸出值已可由代數縮小

前階段core以signed LB物件byte+21作Q的A0；將Q回覆低byte寫入物件+104，接著未重新設定A0就呼叫R。中間的SB不改寫A0，而Q／R本機都不修改RAM，因此可在有效target、物件、非別名、frame及輸出pointer保存等前提下，接成 `T(x)=R(Q(x))`：

| signed x | T(x) |
|---|---|
| `−2^31..−18` | −18 |
| `−17..−10` | −10 |
| `−9..−5` | −5 |
| `−4..−3` | −3 |
| `−2..0` | 0 |
| 1..6 | 原值 |
| `7..2^31−1` | 7 |

這個合成並非對所有輸入還原原值，負數區間尤其不能簡化成恆等函式。

**非sentinel query25**：令s為其signed byte，s≠127。core先將 `min(s,6)` 寫入物件+21，因此最後logical結果只可能為：

```text
−18、−10、−5、−3、0、1、2、3、4、5、6
```

core將R回覆以SB寫入物件+21及fresh輸出pointer（所需保存前提下對應adapterSP+61）；實際輸出bytes為238、246、251、253及0..6。raw query25 bytes 7..126都先限制到6；128..255按signed負數處理。檢查器核對全部255個非sentinel byte案例。

**sentinel 127**：core先把global `20003200/20003250` byte寫到輸出，但沒有先以127覆寫物件+21。Q接到的是物件原有byte+21的signed值，所以最終結果另可能包含7。檢查器核對全部256個舊物件byte案例。

若輸出pointer／storage按前提保存，後續R的byte寫入會取代sentinel初次global寫入。若動態pointer別名到物件+21或incoming pointer slot，先前store則可能改變後續來源；不能省略非別名與frame保存條件。

上述資料byte與core status `0／7／12／17／18／69`分開。較早core返回仍未經過輸出store，這次純算術helper驗證沒有補足那些路徑的SP+61初始化缺口。

## 重播與剩餘工作

```text
python analysis/check_v4160_request_output_static.py
python -O analysis/check_v4160_request_output_static.py
```

兩種模式要求164次逐指令operand變異拒絕、48個完整32-bit區間憑證、六條lookup路徑與兩版合計1022個core合成案例，並精確重播ledger。APP、candidate、SDK及上游來源亦核對身分。

仍需追查鏈表head／next／key writers、配置callback來源、實際六byte服務與copy／通知provider、指標保存期、callback枚舉與缺失ROM pattern。本次沒有執行或模擬目標ISA、provider、callback、RF、NV、MMIO、CSR或trap；既有約88.09%的C重建基準不變。
