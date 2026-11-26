# v4.1.60：返回後發布、下一筆ID6與clock來源鏈

接續 [範圍與重試驗證](v4160-range-retry-static.zh-TW.md)，本輪把零gate分支的**條件式普通返回**接回gate／primary，核對七個pointer words發布及下一筆registration。同時建立APP設定欄位36到word-source primary callback的具體候選鏈；實際fresh／installed binding仍需另證。

程式：[check_v4160_gate_return_publication_static.py](check_v4160_gate_return_publication_static.py)。證據：[v4160-gate-return-publication-static.json](v4160-gate-return-publication-static.json)。只驗原bytes、operands／CFG、frame links及來源／區間等式；未執行或模擬ISA、clock、callback、copy、registration或裝置。C重建覆蓋率不變。

## 新核對視窗

| 項目 | V131起點 | V140起點 | bytes／指令 |
|---|---|---|---:|
| clock wrapper完整本體 | `43520` | `435ac` | 42／17 |
| gate共同suffix | `55bfc` | `55d3c` | 54／17 |
| primary共同suffix | `61b24` | `61c0e` | 54／15 |
| outer第一組handler／兩個call | `6dd1e` | `6df0e` | 16／4 |
| APP pointer來源 | `19a74` | 同一APP | 30／10 |

每版前四項166 bytes／53指令，加一份APP視窗，全部逐指令guard。另重播既有完整caller、config、registration、clock callback與arithmetic原bytes合約。outer視窗包含下一initializer call operand，語意截止在該call之前。

## APP欄位36：primary callback的候選來源

APP `19a74` fresh讀取`U32[S0+124]`；在S0保持`40000`時，這就是槽`4007c`。`19a90`將同一A5寫到SP+52，兩者之間沒有call或其他A5定義。builder的C=SP+16，因此這是 **C+36**。

SDK header將槽`40034+18*4=4007c`命名為`TMOS_GetSystemClock`；兩份候選該word分別指向`43520／435ac`。原resident config的matching64-byte copy會將C+36帶到F+36：

| 版本 | F | word-source primary slot | 候選pointer |
|---|---|---|---|
| V131 | `200031ec` | `20003210` | `43520` |
| V140 | `2000323c` | `20003260` | `435ac` |

既有defaults的直接stores不碰field36。startup zero request包含此word，ordinal為198（從0開始）；config的fill64也會先請求清零該位置，但後面的copy64可以覆寫。這些是來源見證，不能推成目前fresh值仍為零或必為上述pointer。

整條連接需要APP的S0／SP與來源frame、C+36在validation／copy之前的保存、matching code與copy完成，以及之後calls／其他writers不改F+36。候選槽及copy幾何都不能代替實際安裝與執行順序證據。

## clock wrapper與巢狀保存條件

wrapper fresh讀F+68，即`20003230／20003280`。這是clock callback槽，與word-source fallback `200031e0／20003230`不同；不同候選的同一數字也不能混作同版欄位。

wrapper使用16-byte frame保存S0／RA，將S0設為ctx。pointer非零時，呼叫該fresh目標，再把callback回覆與post-callback fresh `U32[ctx+20]`相加mod32，存回ctx+20。pointer為零則跳過。兩條路徑最後都以fresh ctx+20返回A0：

| 版本 | accumulator ctx+20 | clock callback的prior-result ctx+24 |
|---|---|---|
| V131 | `200031b0` | `200031b4` |
| V140 | `20003200` | `20003204` |

這兩個words相鄰但分離。wrapper本機只定義RA／SP／S0／A0／A5；未知callback仍須保存wrapper／word-source的live S registers、SP、frame、所需GP及物件／global內容。

若fresh clock pointer符合先前候選`43d62／43dee`，且其fresh copied-reader pointer仍為APP `191c6`，可重用130-byte clock callback、914-byte arithmetic及90-byte reader的保存證據：callback自己的非frame store在ctx+24；wrapper則寫ctx+20；兩者都不碰本輪所需的count／gate／table／source槽。arithmetic沒有stores、calls或RA／SP／GP／S定義。

這個matching case的數值回覆維持opaque，不需要先證明quotient或隨機性。reader的配對halfword retries仍須正常完成，並保留code／data／frame、非alias與無不利MMIO／非同步干擾等前提。

## 普通返回後，沒有A0成功／失敗測試

前輪重試函式若完成，其RET沿用initializer尾交的RA，返回gate共同suffix。gate再從自己的frame載回primary link；primary同樣載回outer link。

以401a0入口SP=S表示：outer／primary／gate的RA保存位置分別是S−4／S−20／S−36。initializer早先的16-byte frame已釋放；後來retry的32-byte frame會重用S−52作RA位置，不是兩個同時active的frame。

retry RET後SP=S−48；gate與primary依序還原後SP=S−16，outer仍active。這段suffix沒有callee、條件分支或A0／A1／A2定義。因而**前輪合法返回A0=0，也照常進入發布**，不應加上原code不存在的Boolean gate。

## 七個pointer words

B為`200033b8／20003408`，發布順序及資料如下：

| field | V131地址 ← value | V140地址 ← value |
|---|---|---|
| B+104 | `20003420 ← 5397c` | `20003470 ← 53a2a` |
| B+108 | `20003424 ← 55120` | `20003474 ← 551ea` |
| B+112 | `20003428 ← 558a8` | `20003478 ← 559e0` |
| B+116 | `2000342c ← 550cc` | `2000347c ← 55196` |
| B+184 | `20003470 ← 6089a` | `200034c0 ← 60984` |
| B+188 | `20003474 ← 609de` | `200034c4 ← 60ac8` |
| B+324 | `200034fc ← 61234` | `2000354c ← 6131e` |

前六個word在B296之內，B+324則是範圍外的固定global publication，單獨核對。七個stores都與count、capacity、gate、table、node、task及source pointer槽分離。它們安裝的是pointer資料，並不呼叫所指函式。

## 零gate路徑的下一筆registration

這裡沿用先前零gate分支留下的count6／gate5，以及fresh capacity≥14、table T=`200047f4`仍相同且有效等保存前提。ordinary return後，outer直接把A0重新形成handler `4dbf2／4dc8a`，呼叫matching registration leaf。

該leaf不呼叫handler；它將handler SW到 **entry6=`T+24=2000480c`**，count增為7，返回A0=6，A2=7。這與先前「一開始gate非零、跳過內層registration」的分支不同，不能把兩種路徑的ID混用。

最後一次unsigned-range wrapper在本輪呼叫域載回upper=`ffffffff`、減lower0；其後candidate RET、兩個publisher及registration都不改A1。因此新截止點的實參可條件式固定為：

| 版本 | 下一call PC | 目標 | A0／A1／A2 |
|---|---|---|---|
| V131 | `6dd2a` | `4da70` | `6／ffffffff／7` |
| V140 | `6df1a` | `4db08` | 同上 |

截止在call前，尚未展開該initializer。後面的registration IDs、outer tail及實際任務進度都不能由這一筆固定。

## 可重現檢查與後續

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_gate_return_publication_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_gate_return_publication_static.py
```

一般與`-O`要求ledger逐bytes一致，116個逐指令operand mutations均被拒絕；另核對SDK槽、APP source資料流、defaults排除、frame／RA幾何、無A0-test suffix、七筆store範圍與entry6界線。

下一步展開`4da70／4db08`，接續後面initializers；實際callback綁定、各等待／重試的完成、setter順序及物件保存期仍待釐清。
