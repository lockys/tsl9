# v4.1.60：名義mismatch暫存區配置、record callbacks與free合併

本輪從 [首次table配置](v4160-initial-table-extent-static.zh-TW.md) 的共同prefix重新分支，處理config-I/O readback **不相等**的名義路徑；不沿用前一輪相等shortcut的前提。在固定length256／record count3與matching callback等條件下，第二個配置區塊位於原table payload之後，最後free只與後方remainder合併，不碰仍allocated的原table區塊。

這條件式合約可接回IO cleanup、三筆builtin stores與post-config返回。它不是實際NV內容、erase/program成功、poll終止或installed provider的證明。

全程只有原bytes／operands與封閉尺寸、link、區間等式。未建立mutable heap／list／NV或target register模型，未執行或模擬韌體、flash operation、callback、MMIO或裝置。重用完整原本體，C重建覆蓋率未增加。

## 證據與本輪前提

程式：[check_v4160_mismatch_temp_release_static.py](check_v4160_mismatch_temp_release_static.py)。證據：[v4160-mismatch-temp-release-static.json](v4160-mismatch-temp-release-static.json)。private free完整原本體沿用 [既有allocator-release驗證](v4160-allocator-static.zh-TW.md)，兩版均為212 bytes／73條指令、無nested call／frame；其來源分別40380、403c0，runtime target均為20000110。

除前輪fresh名義heap H/L、首次P1配置及有效非別名frame／header／global等條件外，本輪要求在config-I/O入口及後續所需讀取時：

- NV base=`08077c00`、U16 length=256、U8 record count=3。
- read callback匹配1979a、write callback匹配197be、copy匹配20000332，code及slots保存。
- 完成的初始4-byte讀取所組LE結果不同於fresh config+8，因此走mismatch分支。
- 所有必要存取與poll正常完成；NV／MMIO實際副作用、physical alias、DMA／interrupt／reentry與外部writers不破壞所需資料／context。

以上是條件，沒有讀取裝置NV或假造其實際內容。APP來源／defaults只提供這些值的候選來源，不能單憑早期stores當成fresh runtime snapshot。

## 第二個256-byte配置

用P1表示原table allocation，R1是其rounded payload size：

```text
P1 = 200045b4
R1 = roundup4(576+6*N0)，N0 ∈ {14,17,…,212}
B1 = 200045ac，tag=1
B2 = P1+R1，free size S1=27600−R1−8
```

第二次allocator request是256、tag78。large head仍是B1；其tag1使core前進至B2。B2 free且S1至少25744，必可fit並再次split：

```text
P2 = B2+8                         # 第二配置的payload
B3 = P2+256                       # 後方free header
新free size = S1−256−8
```

| 項目 | 全67種capacity的名義範圍 |
|---|---|
| B2 | `20004848..20004cec` |
| P2 | `20004850..20004cf4` |
| B3 | `20004950..20004df4` |
| S1 | 25744..26932 |
| 第二split後free size | 25480..26668 |

原table與其payload在B2之前，P2位於B2之後。因此fill(P2,ff,256)、IO每輪的word store及後續source讀取都可限制在第二payload內，不直接寫原table、context或headers。

## 三次write callback的直接範圍

固定length/count且S2／欄位保存時，迴圈indices恰為0、1、2。每輪先把record destination寫到U32[P2]，再傳：

```text
A0 = 08077c00 + 256*i
A1 = 256>>2 = 64
A2 = P2
```

APP write wrapper忽略入口A1的num64，保存A2再重載作program source。program固定讀64個word、offsets0..252，共256 bytes；本次P2 payload正好足夠。三次source都需是同一個保留的P2，不能僅憑首次allocator reply推定後續cache未變。

完整read／write及unlock／erase／program／lock／timer原本體均重新核對。write wrapper保存S0／RA並使用自己的32-byte frame；五個helpers無nested call／frame，均不定義S1／S2／GP。其直接CPU writes可分類為：

| 類別 | 範圍或encoded地址 |
|---|---|
| wrapper stack | 保存source、S0與RA的child frame words |
| unlock | word `40022004`、`40022024` |
| erase／program／lock控制 | word `40022010`、`40022014` |
| program data SW | 每個aligned destination的64個word，offsets0..252 |
| timer | word `e000f000`、`e000f004`、`e000f010`、`e000f014` |

三個program data區間（右端不含）為`08077c00..08077d00`、`08077d00..08077e00`、`08077e00..08077f00`。這只界定CPU data SW，**不界定控制操作造成的實際erase／program physical範圍或效果**。

在matching code、有效且分離的frames／heap／globals／NV資料區與MMIO effects、正常poll返回及無外部干擾前提下，這些local writes不改cache word、config length/count/callback fields或temp headers，因而可將Pcurrent=P2及S2保存帶到cleanup。callback scalar reply不決定IO重試或成功；APP wrapper回0也不是NV成功收據。

## private free如何避開原table

free使用最後重讀的cache pointer。此名義保存case中它是精確owned payload P2，而不是任意interior pointer。原free的一般range predicate較寬，本輪沒有把它升級成通用ownership檢查。

固定link／tag事實給出：

1. 搜尋由small header A前進到B1，再到B2；前兩者的next均小於P2。
2. P2=B2+8且P2<B3，通過matched block與payload下界guards。
3. tag78不等於32769，不走special byte-counter更新。
4. B2先清tag並將account加256。B2既非small head也非large head；prev=B1的tag1使backward merge被跳過。
5. next=B3既非sentinel也非large head，且tag0，所以只作forward merge。

最後：

```text
B2.size = 256+8+(S1−264) = S1
B2.next = E
account再加8
```

若首次配置後account為A1，第二次split使其成為A1−264；free的+256及forward-merge +8恰好回到A1。所有67個case的此段account都在U16範圍內，不靠wrap抵銷。

free的直接heap stores只落在B2 header、accounting欄位及encoded控制word，沒有寫B1 header或P1 payload／table。它沒有SP／RA／S／GP定義，所以正常返回下所需caller registers可保存；frame、code與physical effects仍受前提限制。

## 合併恢復的範圍與post返回

恢復的是free remainder的linked-header layout與accounting。B3的舊header bytes及已填寫的temp payload bytes仍可能留在現在的free payload，不能稱為整個heap byte image還原或wipe。

IO忽略free的A0，明設A0=0，清cache ctx+32及neighbor ctx+36，恢復frame後RET。這些metadata slots不與table pointer ctx+40或count ctx+1重疊。原context fill40給出的count0，在本輪條件下仍可帶到post suffix。

接回post-config，三筆builtin word stores仍為T、T+4、T+8，count變3；capacity至少14，全部在原P1 payload內。suffix未再定義A0，因此本輪mismatch case的post返回0。這與前輪shortcut返回1是不同分支結果，沒有同時假設相等與不相等。

## 重播與後續

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_mismatch_temp_release_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_mismatch_temp_release_static.py
```

檢查包含67個first-capacity幾何、第二配置／merge／accounting等式、64-word source extent、IO／完整APP callback family／core／free接點，以及90個core／free operand變異拒絕；JSON須逐bytes重播一致。

後續仍需串接outer initializer與APP continuation至registration／optional hook，確認實際fresh欄位／callback slots及provider身分，並追查其他length/count輸入域、fault／clobber情況、poll進度與一般ownership／payload生命週期。
