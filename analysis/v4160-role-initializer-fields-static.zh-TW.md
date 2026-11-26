# v4.1.60：完整角色 initializer、selector 與欄位尺寸

接續 [gate 寫回前綴](v4160-first-role-gate-static.zh-TW.md)，本輪驗證 initializer 的完整426-byte本體及70-byte selector，將條件式欄位證據推到第一個尚未封閉的後續 callee 之前。先前的 `ctx+3=5` 保存登記 ID；本輪的 `B+3` 則存 selector 回覆，是不同地址。若前輪 copied config halfword+10仍為1000，selector回0，因此兩個 byte 可分別為5及0。

程式：[check_v4160_role_initializer_fields_static.py](check_v4160_role_initializer_fields_static.py)。證據：[v4160-role-initializer-fields-static.json](v4160-role-initializer-fields-static.json)。只驗原bytes、operands、CFG及封閉欄位／區間等式，沒有執行或模擬 initializer、selector、target ISA、RAM、MMIO或裝置。C重建覆蓋率不變。

## 完整本體與截止點

| 項目 | V131 | V140 | bytes／指令 |
|---|---|---|---:|
| initializer | `5362e..537d8` | `536dc..53886` | 426／138 |
| selector | `43e24..43e6a` | `43eb0..43ef6` | 70／22 |
| 欄位基址B | `200033b8` | `20003408` | 296-byte object |
| 外層設定基址F | `200031ec` | `2000323c` | fresh欄位來源 |
| 本輪語意截止 | `537b2` 呼叫前 | `53860` 呼叫前 | initializer+388 |

範圍右端不含。完整initializer共41 stores、11 loads、七個linked calls，local CFG無環。沒有普通RET：還原S0／RA／S1／S2／SP後尾跳 `5e758／5e842`。尾跳之後的兩段本機code仍分別由前面分支可達，因此一併納入完整範圍。

前綴既有fill與兩個setter已封閉；本輪另封閉selector。其後的三個callees與tail仍未封閉，不能由完整本機CFG推定整個initializer已返回gate或setup。

## selector 的完整分段函數

selector fresh讀 `U16[2000323e／2000328e]`，即前輪 copied config+10；沒有frame、store或nested call，只定義A0／A4／A5。

| unsigned halfword h | A0 |
|---|---:|
| 0..20 | 7 |
| 21..30 | 6 |
| 31..50 | 5 |
| 51..75 | 4 |
| 76..100 | 3 |
| 101..150 | 2 |
| 151..250 | 1 |
| 251..65535 | 0 |

最後一段由SLTIU `<251` 形成。全部65,536個輸入以門檻數目等式與分段式交叉檢查，沒有跑目標指令。若前輪16-byte copy及其後保存條件成立，h=1000，回覆0寫入B+3；這不覆寫位於 `2000319f／200031ef` 的ctx gate5。

## 固定值與fresh取樣

`53670／5371e` 才將S0從保存的登記ID改為B；S1原先為 `20003000`，稍後也改為B。S2形成F。所有直接stores均分類為自己的frame、既有ctx gate／trailing words，或B內欄位；每個operand及有效區間另核對。

| B相對欄位 | 寬度 | 寫入值 |
|---|---|---|
| +20 | word | `07d7000d` |
| +24 | word | V131 `0d0db131`；V140 `0d0db140` |
| +28 | word | V131 `07d7b131`；V140 `07d7b140` |
| +32 | halfword | V131 `b131`；V140 `b140` |
| +224／+228 | words | 31／0 |
| +262／+264 | halfwords | `dfff` |
| +266 | byte | 31 |
| +58／+60 | halfwords | `0f0f` |
| +57／+63 | bytes | 0／1 |
| +126／+64 | halfwords | 460 |
| +66 | halfword | 3 |
| +68／+72 | words | 0／`06071440` |
| +52 | word | `0015f900`，即1440000 |

以上僅位元值，不指定硬體／時間單位。

在前輪296-byte清零與後續無干擾條件下，最初B+208／B+212是0。原指令分別將它們OR `072d79ff`／`00001b9e`，結果各寫兩處：B+208／B+216與B+212／B+220。不是對各目的word分別取樣的RMW。

另fresh讀一次 `U8[F+14]`，將同一byte寫入B+193／B+201。`U16[F+4]>>10`寫入B+137，完整halfword域的結果範圍是0..63；本輪不把這個fresh來源無條件固定成早期APP值。

## 尺寸分支與自寫入flags

令 `k=min(fresh U16[F+16],251)`。後段會讀B+60、B+61各自的mask4。前面已SH `0f0f`到B+60，selector又沒有stores，因此在所需非alias／無干擾條件下，兩個byte的bit2都為1，選擇 `(k+138)*8`，不走另一個 `(k+14)*8` 分支。

| B相對halfword | 條件式結果 | 範圍 |
|---|---|---|
| +42／+46 | k | 0..251 |
| +44／+48 | `8*(k+138)` | 1104..3112 |
| +34 | `max(k,27)` | 27..251 |
| +36／+40 | `8*(k+138)` | 1104..3112 |
| +38 | `8*(k+14)` | 112..2120 |

原code還有對328的下限選擇；此處1104..3112都大於328，因此該修正分支可排除。所有結果都能放入halfword，沒有截斷損失；兩個乘8尺寸的差固定為992。

第一個後續call前的實參可收斂為：A0=27、A1=328、A2=`8*(k+14)`、A3=`8*(k+138)`。這只描述呼叫點資料流，尚未賦予callee的ABI或用途。

## 保存與尚未封閉的呼叫

從前輪prefix截止點到initializer+388之間，唯一callee是已完整驗證的selector。其保存集合、所有41個direct store分類及固定object範圍，可在既有mapping、有效非回繞／非別名frame與globals、無不利MMIO／FENCE.I／IRQ／DMA／重入／外部writers等前提下，將ctx gate5、count6、既有table與名義timer node保存到本輪截止點。

| 順序 | V131目標 | V140目標 |
|---|---|---|
| 第一個未封閉linked call | `64298` | `64382` |
| 第二個 | `57ac4` | `57c04` |
| 第三個 | `63704` | `637ee` |
| 還原frame後tail | `5e758` | `5e842` |

這些呼叫及tail都未在本輪執行，也未假設它們保存所有B欄位、metadata或frames。後面的gate／primary callback words發布及外層六次registration的實際ID，仍不能由此直接固定。

## 驗證與後續

一般與Python `-O` 均要求ledger逐bytes一致。檢查涵蓋完整來源身分、兩版full bodies／CFG／全部operands／stores、unsigned來源load與Xwchc窄存取、320個逐指令operand mutations拒絕、65,536個threshold／size案例、selector精確輸出分布、halfword界線與選定分支。

下一步是 `64298／64382` 及後續callees，補上它們的副作用與返回合約；實際fresh來源、provider綁定、物理效果與後續保存期仍待釐清。
