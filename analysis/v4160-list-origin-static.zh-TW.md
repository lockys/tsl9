# 鏈表來源：callback 設定、192-byte 配置與發布順序

接續 [request 輸出與lookup](v4160-request-output-static.zh-TW.md)，本次定位並完整驗證一條callback寫入來源，以及它指向的物件建立函式。

| Body | V131範圍（右端不含） | V140範圍（右端不含） | 每版bytes／指令 |
|---|---|---|---|
| callback installer | `55bde..55c32` | `55d1e..55d72` | 84／26 |
| node creator | `5397c..53a3e` | `53a2a..53aec` | 194／69 |

合計556原始bytes、190條指令。全部operands、SHA256、閉合CFG、16條選定路徑、capacity域與default R案例見 [JSON](v4160-list-origin-static.json)，由[檢查器](check_v4160_list_origin_static.py)精確重播。

兩個body皆無本機迴圈。這些是resident參考候選中的已驗證寫入路徑，尚未證明其實際入口執行、所有writers或runtime綁定；本次沒有執行或模擬目標。

## 一條具體的配置 callback 寫入來源

令B=`200033b8/20003408`。installer建立16-byte frame保存RA，先讀fresh byte `2000319f/200031ef`：

- 非零：略過兩個setup calls。
- 零：以A0=`5352c/535da`呼叫 `43c4e/43cda`，再呼叫 `5362e/536dc`。第二個call的A0沿用第一個回覆，沒有本機重設成0。

所需calls返回後，兩條路徑共同依序寫入：

| 槽位 | V131值 | V140值 |
|---|---|---|
| B+104 | `5397c` | `53a2a` |
| B+108 | `55120` | `551ea` |
| B+112 | `558a8` | `559e0` |
| B+116 | `550cc` | `55196` |

B+104恰是前階段core無local null guard的配置callback槽位，值恰好指向本次完整展開的creator。其餘三個callback body本次未展開；它們的版本地址差也不同，不能套用單一delta。

四個store後沒有其他call；在installer實際執行、正常返回、有效slot／frame及無中途改寫等前提下，這提供了一個具體綁定來源。它仍不是「這個callback在實機已安裝」或「只有此處寫入」的證明。

installer不強制返回固定成功status：非零flag路徑本機保留原A0；零flag路徑保留第二個setup回覆。它也沒有本機初始化head、count或capacity，這些來源仍需展開setup與其他writers。

## Creator 要求配置192 bytes，不等同已證明有效extent

creator建立16-byte frame，保存RA／S0／S1／S2。先讀 `U8[B+62]` 作count、`U8[B+63]` 作capacity，只有unsigned `count < capacity`才繼續；否則返回0，不呼叫allocator。

通過後保存完整入口A0，呼叫RAM `20000040`，實參 `(192,241hex)`。null回覆返回0；非null N保存於S0，接著呼叫RAM `2000039c`，實參 `(N,0,192)`。

這兩處證明的是配置與fill的**呼叫要求**。192 bytes足以涵蓋creator直到+180的本機欄位與core所需的至少108-byte範圍，但仍需allocator真的提供有效、保留且不與其他物件別名的extent，以及fill／ABI／保存合約。不能由尺寸實參直接宣稱實際配置大小或memset成功。

fill回覆沒有用作返回物件；後續仍使用所需保存的原N。creator成功路徑返回原allocator N；沒有本機free、失敗回滾或完整生命週期證明。

## Key=1 並不是 creator 寫入

fill返回後，只有完整入口A0恰為0時，creator顯式將N byte+8寫為`f0`。其他入口值略過此store，byte+8是否為0取決於實際fill輸出合約。

core的配置callback呼叫提供A0=1，因此略過`f0`寫入。creator先發布node並完成defaults，返回core且非null後，**core才把原core入口A0的低byte寫到N+8**；已發布的上游鏈在參數保存前提下提供1。

這串接了lookup的byte+8 key來源，但也表明發布鏈表節點發生在後續key寫入之前。沒有據此推論實際併發行為、原子發布或可達runtime問題。

## Head null：同時寫入三個 context 槽位

fresh head=`U32[B+92]` 為null時，順序是：

```text
B+88 = N
B+92 = N       // lookup head
B+96 = N       // tail
U32[N+0] = 0   // next
U8[B+62] = 1   // count
```

B+88是先前core的busy/current物件槽位，與head B+92分開；這條路徑恰好同時設定它們。此body沒有核對舊B+88、B+96、count是否與null head一致，count會直接寫1。

這些pointer發布先於下面的defaults。若要證明其他消費者只看見完整初始化物件，還需執行順序與保存／同步來源，不能只靠這些本機store。

## Head nonnull：使用未作null guard的舊tail

head非零時：

```text
oldtail = U32[B+96]    // 沒有local null guard
U32[oldtail+0] = N
B+96 = N
U32[N+0] = 0
freshcount = U8[B+62]
U8[B+62] = low8(freshcount+1)
```

append路徑不寫head與B+88。非零head不能自動證明tail有效、tail確為最後節點、N與既有鏈表分離、無環，或count等於鏈表長度。

檢查器核對全部65,536組count／capacity bytes：32,640組通過、32,896組拒絕；capacity=0全部拒絕。若同一count值保存到增量時，通過條件可推出 `count+1 <= capacity <= 255`，不會byte溢位。

但append在allocator與fill後**重新讀count**；若沒有保存與全域不變量前提，freshcount=255加1仍會截成0。這只是區分兩種整數前提，沒有聲稱該值實際可達或構造目標輸入。

## 發布之後才寫 defaults

首次建立與append都接到同一組defaults：

| 位置 | 本機來源 |
|---|---|
| N+9 | 1 |
| N+11 | `90`（hex） |
| word N+76／N+80 | fresh words `20003534/20003538`；V140為`20003584/20003588` |
| N+22／N+125 | `ff` |
| N+180 | fresh byte B+74 |
| N+104 | fresh byte `20003200/20003250` |
| N+21 | 對同一fresh source byte呼叫既有R helper，再取回覆低byte |

R=`63966/63a50`已在上一階段證明為無記憶體存取的unsigned整數map，因此這個default運算不再需要未知輸出helper假設。兩版各核對256個source byte案例；logical R值可為−18、−10、−5、−3及0..7，N+21實際保存其低byte。仍沒有賦予物理單位。

這些新物件若確實來自此creator，可在allocator／fill／caller保存等前提下，連回lookup與core物件。既有鏈表節點可能有其他來源，不能將192-byte要求擴大成所有lookup回覆的extent保證。

## 重播與剩餘工作

```text
python analysis/check_v4160_list_origin_static.py
python -O analysis/check_v4160_list_origin_static.py
```

兩種模式核對190次逐指令operand變異拒絕、16條選定CFG路徑、callback／head／key串接、發布先於defaults的順序、65,536組capacity與512個R案例，並精確重播ledger。APP／candidate／SDK及上游來源亦核對身分。

仍需追查installer的實際callers與setup callees、初始head／count／capacity與其他writers／移除流程、allocator／fill實際綁定與保存期，以及其他callbacks、枚舉與缺失ROM pattern。本次沒有執行或模擬目標ISA、provider、callback、RF、NV、MMIO、CSR或trap；既有約88.09%的C重建基準不變。
