# 第四個外層 ID9 初始化、vector 啟用與間接派送邊界

接續[ID8 資源與返回鏈](v4160-id8-initialization-static.zh-TW.md)，本次完整展開 `50412`／`504ac`，以及它建立的兩組 vectors、兩個 activation selector、登記的 callback及讀取 active-vector 的 consumer。這些仍是 resident 參考候選，不等於實際安裝或已執行的 provider。

| Body | V131 範圍（右端不含） | V140 範圍（右端不含） | 每版 bytes／指令 |
|---|---|---|---|
| initializer | `50412..5043c` | `504ac..504d6` | 42／14 |
| vector setup | `50368..503d2` | `50402..5046c` | 106／29 |
| bit8 activation | `503d2..503f2` | `5046c..5048c` | 32／10 |
| bit4 activation | `503f2..50412` | `5048c..504ac` | 32／10 |
| registered callback | `4f516..4f54c` | `4f5ae..4f5e4` | 54／22 |
| active-vector consumer | `4f54c..4f5a4` | `4f5e4..4f63c` | 88／36 |
| next outer window | `6dd5e..6dd6e` | `6df4e..6df5e` | 16／4 |

合計740個原始 bytes、250條指令。完整 operands、SHA256、CFG、44張有限路徑憑證與256個旗標案例見 [JSON](v4160-id9-vector-dispatch-static.json)，由[靜態檢查器](check_v4160_id9_vector_dispatch_static.py)精確重播。呼叫邊的 fallthrough 都要求 callee正常返回與所需保存前提。

## ID9 與 record2 的發布

沿用前階段條件性入口A0=9、A2=10，initializer使用32-byte frame，保存RA@SP+28及入口A0@SP+12。唯一新callee是完全直線的vector setup；它沒有load、call或frame，只定義A4/A5。

返回後 initializer重讀saved ID9，將byte9存至 `200033af`／`200033ff`，再以A1=6呼叫既有selector。這會更新record2：halfword `20003338`／`20003388`=6，byte `2000333a`／`2000338a`=9。它與前階段更新的record0/1分離，但仍明確改變原48-byte記錄區。

initializer隨後取回RA、釋放frame，以A0=`4f516`／`4f5ae`尾跳既有12槽callback登記leaf。成功插入返回0；滿表不寫入，返回19。正常返回不要求登記成功，也不會在初始化流程中執行這個callback。

## 建立 vectors 與啟用 vectors 是不同步驟

vector setup先清除三個words，包括兩個active pointer，然後保存六個函式指標：

| 欄位 | V131 | V140 |
|---|---|---|
| A active word，初始清零 | `2000338c` | `200033dc` |
| A vector base | `200033a0` | `200033f0` |
| A 的三個 pointers | `5091a,50668,4f39e` | `509ba,50708,4f436` |
| B active word，初始清零 | `20003388` | `200033d8` |
| B vector base | `20003390` | `200033e0` |
| B 的三個 pointers | `517a0,5134e,515ee` | `51840,513ee,5168e` |
| 另一個清零word | `2000339c` | `200033ec` |

code pointers的兩版增量並不統一；檢查器分別固定每個LUI/ADDI及最終值。RAM位移為80 decimal，但部分code位移是152、154或160 decimal，不能混用。

這九個word stores位於先前callback table右端之後。最後一筆word右端恰好止於ID7 byte之前，避開task metadata、T、相關config/source/hook、pool pointers及low2/count欄位。這些固定地址區間關係不證明外部writers、實體alias或物件保存期。

兩個獨立activation leaf各fresh讀取 `U8[200033b0/20003400]`：

- bit8為1時，將A vector base寫入A active word；為0時寫零。
- bit4為1時，將B vector base寫入B active word；為0時寫零。

它們各返回A0=0，沒有frame或call。256個byte案例中，各bit有128個啟用值，兩者同時啟用有64個。兩次呼叫是分別fresh讀取，不能視為一致旗標快照。本initializer沒有呼叫這兩個activation leaf；旗標來源、其他writers及後續啟用順序仍待追查。

## 新登記callback的 provider 邊界

`4f516`／`4f5ae`建立32-byte frame，保存S0、RA、入口A1；S0保存完整32-bit入口A0。它直接呼叫RAM `20000a94`，本次停在這個provider合約邊界。

若provider返回C，接著立即讀取word `[C+52]`；**沒有先檢查C是否為零**，因此必須有可讀的context與有效存取前提。令讀出的record pointer為R：

1. R=0：恢復frame後普通RET。
2. R非零，但fresh `U16[R]`不等於保存的完整入口A0：普通RET。
3. 上述相等，但保存的入口A1不等於1：普通RET。
4. 三個條件皆通過：恢復frame後尾跳 `4f43c`／`4f4d4`，帶A0=C、A1=1；A0不是record pointer。

比較沒有先將入口A0截成16位。provider仍須保存live S0、SP、frame中的saved A1/RA與所需code/object；其實際綁定、副作用及尾跳目標尚未展開。這四條完整本機路徑並不代表callback已被觸發。

## Active-vector consumer 的資料流

`4f54c`／`4f5e4`是讀取上述active words的另一個完整consumer。它呼叫 `4f2ae`／`4f346`取得C；這個lookup本體尚未展開。其後對C與word `[C+52]`得到的R均有null guard。

R有效後，fresh record byte+2非零時選A active word，為零時選B active word。這個record byte與activation leaf讀取的global flags byte是不同欄位。若選到的fresh active pointer V及fresh `U32[V+4]`都非零，才以A0=R間接呼叫該函式。

若activation與vector內容保留為本次來源，對應候選目標為A的 `50668`／`50708`，或B的 `5134e`／`513ee`。這是資料來源的條件性連接，未證明實際綁定、呼叫可達或callee保存合約。

**即使active pointer或函式指標為零而跳過呼叫，仍會檢查fresh record byte+3。**若其等於47，取fresh `U16[C+2]`至A0、設A1=0，恢復frame後尾跳 `4f4b8`／`4f550`；否則普通RET。若實際發生間接呼叫，返回後需保存S0=R、S1=C、SP/frame/RA等前提。lookup、indirect target與post-tail均留作後續邊界。

consumer的14條本機路徑涵蓋兩個早退、A/B選擇、vector-null／function-null／呼叫三種情況，以及共同post-check的兩種出口。本次沒有建立新登記callback到此consumer的呼叫鏈；兩者各自的完整body與共用資料來源分開驗證。

## 下一筆task登記與ID10邊界

initializer的callback登記leaf正常返回至 `6dd5e`／`6df4e`後，outer不測試0/19，直接形成下一個handler `6cc4c`／`6ce38`。

若fresh count仍10、capacity仍≥14、table pointer仍T=`200047f4`，且有效extent／frame／非alias／無干涉等前提成立，下一筆登記寫entry10=`2000481c`，回覆A0=10、A2=11，count變11。A1保留callback登記結果：插入時為0，滿表時為第12槽當次觀察的非零word。

新邊界停在 `6dd6a`／`6df5a`對第五個initializer `6c300`／`6c4ec`的呼叫前。

## 離線重播

```text
python analysis/check_v4160_id9_vector_dispatch_static.py
python -O analysis/check_v4160_id9_vector_dispatch_static.py
```

兩種模式均要求250次逐指令operand變異拒絕、44張CFG路徑憑證、256個flags案例與精確JSON重播；原APP／candidate／SDK及上游身分證據一併核對。未執行或模擬目標ISA、provider、callback、MMIO、CSR或trap。新增靜態證據不增加既有約88.09%的C重建基準。
