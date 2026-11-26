# 第三個外層 ID8 初始化：low2 資源、callback 發布與 ID9 邊界

接續[ID7 完整初始化](v4160-id7-initialization-static.zh-TW.md)，本次完整展開 `4a7d6`／`4a86e`、clear leaf、尾跳資源函式與兩個 pointer setter，並接上既有 selector／callback 登記合約。兩版 resident bytes 仍屬參考候選，實際 RAM provider 綁定與執行狀態未由此確定。

| Body | V131 範圍（右端不含） | V140 範圍（右端不含） | 每版 bytes／指令 |
|---|---|---|---|
| initializer | `4a7d6..4a808` | `4a86e..4a8a0` | 50／16 |
| clear leaf | `445d4..445e6` | `44668..4467a` | 18／5 |
| resource tail | `4d068..4d172` | `4d100..4d20a` | 266／89 |
| pointer setter A | `4a1f6..4a200` | `4a28e..4a298` | 10／3 |
| pointer setter B | `44694..4469e` | `44728..44732` | 10／3 |
| next outer window | `6dd4e..6dd5e` | `6df3e..6df4e` | 16／4 |

新範圍合計740個 bytes、240條指令，逐一固定 operands、CFG、呼叫目標與完整 SHA256。證據見 [JSON](v4160-id8-initialization-static.json)；[檢查器](check_v4160_id8_initialization_static.py) 另重播既有44-byte selector與42-byte callback 登記 leaf。

## ID8 保存、record0 更新與 frame 交接

沿用前階段條件性入口 `(A0,A1,A2)=(8,5,9)`，initializer 建立32-byte frame，保存 RA@SP+28及入口A0@SP+12。clear leaf 只將 `20002f04`、`20002f00` 兩個 word 清零；V140 對應地址均加 `50` hex。

返回後 initializer 重讀 saved ID8，清 word `20002f6c`／`20002f70`，將 byte8存至 `200033ad`。它設定 A1=4，呼叫既有 selector：更新 record0 halfword `20003320=4`、byte `20003322=8`。V140 分別為 `20003370`、`20003372`。因此先前48-byte記錄區會被明確修改。

selector 返回後，initializer 取回 caller RA、釋放 frame，再以不設 link 的跳躍進入 resource tail。後者重新建立自己的32-byte frame，保存 RA、S0–S3；這是已釋放 frame 的重用，不能把原 saved-ID slot 視為仍然存活的物件。

## 資源來源是 D+9，不是相鄰的 q

resource tail 的三次窄 LBU 都讀取 D+9：`200033b5`／`20003405`。原指令 `8834`／`9034`／`9834` 的 offset 是9，不能採用一般浮點解碼所呈現的位移。

第一個 ID6 resource callee 曾將 `b & 3` 寫入此 byte，b 來自 config F+21。相鄰 D+8保存的才是 q=`(b&3)+(b>>2)`。本次逐指令接上原寫入與三次讀取地址，並核對前階段 ID7 的固定寫入避開 D+9。

- 不假設欄位保存時，每次 fresh unsigned byte 仍為0..255。
- 若初始 low2 值持續保存至各次讀取，數量 N 限於0..3。
- APP source byte14 的條件性來源案例給 low2=2；若來源 copy／validation、欄位、provider及其他 writer 等保存條件成立，request=394 bytes、下述 layout使用386 bytes。這不是已證明的當前裝置設定。

## 零數量與非零數量分開

tail 先清除三個 pointer words：V131 `20002f8c`／`20002f90`／`20002f80`，V140各加 `50` hex。

若入口 fresh count=0，CFG直接跳過 allocator、fill與所有 payload迴圈，進入兩個 setter 與一次 callback 登記呼叫。這條路徑只有已展開的 RAM leaf操作；有效 code／frame／table、實體非alias與無干涉等前提成立時，可接到普通RET。

若入口 fresh count=N1≠0，本次第一個未閉合 provider 邊界是 RAM `20000040` 的請求：

```text
allocation bytes = (194*N1 + 6) & 65535
allocation tag   = 4701
```

對 unsigned byte N1，最大49476，不會被low16截斷；非零路徑最小200 bytes。沒有 allocator 返回值的本機 null guard。接著 fill 使用另一次 fresh N2，長度 `194*N2+6`，範圍6..49476；迴圈又 fresh 讀取 N3。N1、N2、N3不能自動視為相等，仍需有效非零 allocation、足夠 extent、provider返回與 frame／count／相關狀態保存等條件。

## 兩區 layout 的條件性界線

原指令的本機形狀為：

- 第一區有 N3 筆184-byte記錄：每筆 halfword+0=`ffff`；內圈恰15次，依序寫 halfword `record+4+12*j=0`、word `record+12+12*j=0`，j=0..14。
- 第二區有 N3+1 筆6-byte記錄：halfword+0=`ffff`、byte+3/+2=`ff`、byte+4=0；第一筆 halfword 再改為 `fffe`。
- 中段 pointer 為 P+184*N3，尾端 pointer 為 P+190*N3+6，分別存至上述第二、第三個 pointer words。

N3讀入暫存器後，本機外圈最多255次，內圈每筆15次，第二區最多256次；仍要求有效存取與所需 GPR／地址關係保持。

僅當 N1=N2=N3=N、payload與算術／存取條件成立時，才能用以下整數式連接 request與layout：

```text
used = 184*N + 6*(N+1) = 190*N+6
requested - used = 4*N >= 0
```

檢查器涵蓋全部256個 byte數量及每筆內圈15個存取區間。這是條件性區間證據；沒有執行或模擬目標迴圈，也沒有把未知 allocator 的結果當成已知有效物件。

## 兩筆 callback 指標寫入、一次登記嘗試與返回

不論零數量路徑或成功完成非零處理的路徑，都到達：

| 動作 | V131 | V140 |
|---|---|---|
| setter A：word←pointer | `20002f70←4b944` | `20002fc0←4b9dc` |
| setter B：word←pointer | `20002f04←4bafa` | `20002f54←4bb92` |
| 送往12槽 callback 登記 leaf | `4b8a6` | `4b93e` |

前兩個 setter 各只有 LUI、SW、RET，會重新寫入稍早被清零的欄位。第三個只嘗試保存指標到既有 callback table；這三個動作都不執行那些 callbacks。

callback 登記 leaf 成功插入時返回A1=0；全12次讀取非零時，A1為第12槽當次觀察值。tail沒有檢查其A0=0或19，最後明確設定A0=0、恢復frame後RET；正常返回時A2=12。本機固定寫入與各callback槽位均核對避開 task metadata、T及相關來源欄位；動態payload／未知provider的保存效果仍需另外證明。

## 下一筆 task 登記與 ID9 邊界

若 tail普通RET與所需保存條件成立，控制回到 `6dd4e`／`6df3e`。outer直接形成 handler `502b4`／`5034e`，沒有檢查先前返回值。

若這次 fresh count仍9、capacity仍≥14、table pointer仍T=`200047f4`，且有效extent／非alias／保存前提成立，下一筆登記會寫entry9=`20004818`，回覆A0=9、A2=10，count變10；A1保留callback登記的結果。

本次停在 `6dd5a`／`6df4a` 對第四個 initializer `50412`／`504ac` 的呼叫前。尚需追查這個 initializer、三個新發布指標的消費者，以及 allocator／fill的實際綁定與物件保存期。

## 離線重播

```text
python analysis/check_v4160_id8_initialization_static.py
python -O analysis/check_v4160_id8_initialization_static.py
```

兩種模式均要求精確JSON重播、240次逐指令operand變異拒絕、全部256個count域、low2來源地址與零路徑provider排除檢查。原APP／candidate／SDK及上游靜態證據身分一併重播。未執行或模擬目標ISA、allocator、fill、callback、MMIO、CSR或trap；本次不增加既有約88.09%的C重建基準。
