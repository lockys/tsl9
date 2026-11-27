# Request core：輸出寫入時機、返回值與三次 bit 檢查

接續 [request 尾跳](v4160-request-tail-static.zh-TW.md)，本次完整展開兩版core：V131 `68bb4..68ee4`、V140 `68cf2..69022`（右端不含），每版816 bytes、271條指令。兩版完整operands與CFG、SHA256、26條選定路徑及靜態定義分析見 [JSON](v4160-request-core-static.json)，以[檢查器](check_v4160_request_core_static.py)精確重播。

原始資料仍是resident參考候選。完整本機body不代表實際installed provider、所有caller可達性或硬體執行已證明；本次沒有執行或模擬目標。

## SP+116 是輸出pointer，不是輸出byte

core建立80-byte frame，保存RA及S0–S11。上游adapter將 `&adapterSP+61` 放在第十個stack word：

```text
coreSP = adapterSP − 80
U32[coreSP+116] = U32[adapterSP+36] = adapterSP+61
```

此等式需要caller frame及pointer參數保存。core在兩個寫入位置各自fresh讀取word `[coreSP+116]`，再透過該pointer作SB，沒有local null guard。不能把它誤解成對coreSP+116的直接byte寫入，也不能假設兩次fresh pointer必然相同。

incoming stack其他讀取：+80為argument0 byte、+84為signed query25、+88為query26、+92為query28、+96為query27、+100為query29、+104為query30、+108為query64、+112為query65；除query25外均以LBU取得byte。

## 返回值與輸出初始化分開判斷

檢查器以編譯器式reaching-definitions分析T1，並將每個call保守視為可任意改寫T1。共用epilogue返回A0=T1，其所有到達定義仍都是literal status：

```text
0、7、12、17、18、69
```

另以CFG移除測試確認：第二個輸出store支配成功status0的定義。因此在所需call返回、有效物件／輸出extent與frame保存等前提下，本機成功0路徑會先經過第二個輸出store。

| 選定路徑類別 | 返回 | 本機輸出store |
|---|---|---|
| 初始busy、早期capability gate | 12 | 未經過 |
| flags／tag／role早期gate | 18 | 未經過 |
| lookup及callback皆返回null | 7 | 未經過 |
| 物件既有halfword限制失敗 | 69 | 未經過 |
| interval限制失敗 | 17 | 未經過，但可已有物件寫入 |
| query64／query65後段capability gate | 12 | 已經過 |
| 後段query27限制失敗 | 18 | 已經過 |
| 本機成功尾段 | 0 | 已經過，並接續狀態寫入 |

這26條是選定的條件性CFG憑證，不是所有實際執行軌跡；callee返回、有效資料及可達實參仍是前提。表中的「未經過」只指core本機store，沒有替未知callee的外部副作用下結論。

上游adapter在任何正常core返回後，都接著要求兩byte通知：status低byte與SP+61。因此core的較早返回仍未提供SP+61的本機初始化保證；較晚錯誤則可能已寫入它。不能用「非零status」統一判斷輸出，也沒有據此宣稱實際runtime讀取或可利用性。

## Context、gate 與取得物件

令B=`200033b8/20003408`。初始讀取 `[B+88]`；非null時讀其word+84，以SLLI5後signed比較檢查原word的**bit26**，命中返回12。後面成功尾段OR的是**bit27**，兩者不同。

入口A5使用完整unsigned比較，超過3返回18；前階段caller的0..3組合值只在上游ABI前提下縮小此域。入口tag A1：

- bit4設置時，query26 byte必須為1，否則18。
- bit4未設置時，拒絕low2=3及bit3設置；query26／query27與fresh `[B+60]` capability bits決定後續是否返回12。

取得物件先呼叫 `55108/551d2`。若返回null，再讀 `[B+104]` 作函式pointer，以A0=1間接呼叫；這個callback pointer沒有local null guard。其返回亦為null時返回7；非null時僅這條分支將原入口A0低byte寫入新物件+8。

後續S4物件包含直到+107的本機欄位存取，至少需要108-byte有效extent及其他callee所需空間。**這個物件不是已證明等同於前階段12-byte request配置**；後者只是借用A7來源的P2。不能拿12-byte配置呼叫當作S4物件有效性的證明。

## 輸出之前已有物件變更

core可先寫tag低byte至物件+96、模式欄位+14及其他欄位，再檢查interval並返回17。interval要求完整unsigned query3／query4符合：

```text
32 <= query3 <= query4 <= 16384
```

typed lowtag5寫byte+14=`81`（hex），並將合法區間的整數中點SH至+32；lowtag13寫byte+14=1、halfword+32=2；lowtag2／0／其他分別使用6／2／0。untyped路徑另寫+94／+95等欄位。完整分支與當時live operands保留於JSON，沒有將暫存register一律當作原入口值。

query4恰為32時還有既有物件halfword限制：query27=3要求+28／+30不超過249，query27=1使用749，其他query27值略過這兩類限制；失敗返回69。

本機沒有rollback、free或恢復舊欄位的流程，不能把非零返回當作「物件未變」。

## 唯一迴圈固定三次，零 bitmap 另作處理

入口A4寫入物件byte+15。A4為零時，物件byte+24直接寫1；非零時先寫0，再以counter 0、1、2測試三個低bit，逐次增加物件byte+24。

迴圈中無call，counter只有初始化0及每次加1，bound register固定3。移除唯一backedge（core+770→+750）後，其餘本機CFG無環。於有效code／物件／非別名保存前提下，此迴圈固定三次。

對上游byte域，結果為：

```text
bitmap=0：結果1
bitmap!=0：popcount(bitmap & 7)
```

例如128是非零bitmap但結果0。256個bitmap中，結果0／1／2／3的組數分別為31／97／96／32；不能將零bitmap混同一般popcount，也不能計入高五位。

## 借用 A7 的六byte服務界線

入口A7保存於S6，通常來自前階段P2+4。core以 `(A7,0,6)` 呼叫RAM `200004bc`：

- 回覆非零：寫物件byte+60=0，略過copy。
- 回覆零：寫byte+60=1、byte+61=原入口A6低byte，再以 `(物件+62,A7,6)` 呼叫RAM `20000332`。

這裡第二個實參0只是確定的實參值，尚未證明服務意義，不能逕自命名為比較null或推定對零地址解參考。實際讀取、寫入、重疊、同步完成及保存期仍未知。

原S6在frame中先保存，之後才令S6=入口A7；沒有對borrowed A7的顯式nonframe pointer store。但兩個provider收到它，不能據此證明不保存pointer。

## 兩個輸出store及最後值

第一個輸出store在core+482，只走signed query25恰為127的sentinel分支，寫入fresh byte `20003200/20003250`。

非sentinel時，先將signed query25限制為 `min(value,6)` 寫入物件byte+21。負值保持負值，沒有向0下限裁切。其後所有繼續路徑接到：

1. signed LB讀物件byte+21，呼叫 `639ca/63ab4`，SB回覆低byte至物件+104。
2. 不重新設定A0，呼叫 `63966/63a50`，其A0沿用前一call完整回覆；其他live arguments及callee合約仍需展開。
3. SB第二個回覆低byte至物件+21，重新讀輸出pointer，於core+508作第二個輸出SB。

若pointer與相關storage按前提保存，第二次寫入會覆蓋sentinel的第一次寫入，所以最終輸出不能直接當作global `20003200/20003250`。輸出byte與core返回status也不是同一來源。

後續query64／query65的capability檢查可返回12，fresh物件+96 bit4未設置時的query27域檢查可返回18；兩者都可發生在第二次輸出之後。成功尾段寫入+97／+103等欄位，word+84 OR `08000000`，再以T1=0返回。

## 重播與剩餘工作

```text
python analysis/check_v4160_request_core_static.py
python -O analysis/check_v4160_request_core_static.py
```

兩種模式核對542次逐指令operand變異拒絕、26條選定CFG路徑及status／輸出階段、完整返回定義域、成功輸出支配關係、三次迴圈及256個signed／bitmap案例，並精確重播ledger。APP／candidate／SDK及上游來源亦核對身分。

仍需展開取得物件的callee／callback、六byte provider、兩個輸出helper、實際綁定與物件保存期，以及context來源writers、callback枚舉和缺失ROM pattern。本次沒有執行或模擬目標ISA、provider、callback、RF、NV、MMIO、CSR或trap；既有約88.09%的C重建基準不變。
