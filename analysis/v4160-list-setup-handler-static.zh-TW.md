# 鏈表 setup 與已登記事件 handler 的串接

接續 [callback／鏈表來源](v4160-list-origin-static.zh-TW.md)，本次重用既有完整setup與caller證據，新增完整事件handler的原指令驗證。

| 新增 body | V131範圍（右端不含） | V140範圍（右端不含） | 每版bytes／指令 |
|---|---|---|---|
| registered handler | `5352c..5362e` | `535da..536dc` | 258／90 |

新增516原始bytes、180條指令；[JSON](v4160-list-setup-handler-static.json)包含完整operands、SHA256、閉合CFG、34條選定路徑、事件域及來源串接，由[檢查器](check_v4160_list_setup_handler_static.py)精確重播。

已存在的426-byte setup不重算為新增範圍。其原指令、selector及欄位合約重用[initializer fields](v4160-role-initializer-fields-static.zh-TW.md)；caller鏈重用[first role gate](v4160-first-role-gate-static.zh-TW.md)，登記函式重用[task registration](v4160-task-registration-static.zh-TW.md)。本次逐一核對原bytes與既有檢查器，補上它們與鏈表及handler的關係。

## 靜態 caller 鏈已定位，實際執行仍需來源前提

候選檔word `401a0` 指向 `6dd16/6df06`，其首call為 `61b1c/61c06`，後者首call為已驗證installer `55bde/55d1e`。

installer的零flag路徑以handler地址 `5352c/535da`作A0呼叫 `43c4e/43cda`，其回覆接到setup `5362e/536dc`。所以本次handler不是任意挑出的函式，而是登記呼叫實際形成的literal地址。

這證明候選靜態call／data鏈，仍不證明實機使用這份表、installer已被呼叫、登記成功或scheduler實際派送事件。

## 登記回覆會寫入 gate，包含0與255

完整登記leaf使用fresh count／capacity bytes。count小於capacity時，將handler寫到table[count]、增加count並返回原index；否則返回255且略過兩個store。

setup先保存完整入口A0，後來以SB將其低byte寫入 `2000319f/200031ef`。installer沒有在進setup前拒絕255，因此：

- 成功index=0時，setup前段寫入的gate仍為0，不能把gate=0直接視為從未初始化。
- 登記被拒絕而回覆255時，若setup正常到達該store，gate前段值為255；這不表示handler已進入登記table。
- 其他成功情況使用實際index，不能跨所有入口固定成task ID 5。

全部65,536組登記count／capacity byte關係都有整數核對；以上仍需有效table、非別名與所需保存等前提，沒有構造或執行目標輸入。

## Setup 的局部鏈表狀態切點

令B=`200033b8/20003408`。setup要求RAM `2000039c` 對 `(B,0,296)` 作fill。既有reference fill body已逐指令驗證；在實際匹配該實作、有效非別名資料／frame、正常返回且無其他改寫等前提下，其正常輸出涵蓋B+0..295。

本次將這個範圍對應到：

| 欄位 | 296-byte fill 涵蓋範圍 |
|---|---|
| count | B+62 |
| busy/current、head、tail | words B+88、+92、+96 |
| 四個callback槽位 | words B+104..+116 |
| nested outer pointers | words B+128、+148 |
| handler末段讀取bytes | B+4..+7 |

setup本機後續store不與上述欄位重疊；另外，setup+222有明確SB1至capacity B+63。setup+62之後、第一個late call之前，唯一call為已驗證的pure selector，沒有store／frame／nested call。

因此在**setup+388之前的局部切點**，所需前提成立時，可給出count=0、head／tail／busy及上述pointer words／bytes為0、capacity=1的條件性狀態。這不是完整setup返回後的狀態保證：後面三個calls與尾跳仍可能修改欄位。installer也只有在整段setup／tail正常返回後，才寫入四個callback地址。

此外，B+300的顯式清零發生在fill之前；B+296與B+304由兩個既有leaf setters在fill之後清零。這三個trailing words在296-byte範圍之外，不能合併成同一個fill呼叫。

reference fill的MMIO／FENCE.I指令僅作來源核對，本次沒有執行或模擬它們，也沒有把CPU store還原推論成硬體狀態已恢復。

## Handler 一次只消費優先序中的首個 bit

handler建立16-byte frame，保存RA／S0／S1，S0保存完整32-bit入口event mask A1。優先序為：

```text
8000 > 0001 > 0002 > 0008 > 0004 > 0020 > 0010 > 2000  （hex）
```

亦即bit15、bit0、bit1、bit3、bit2、bit5、bit4、bit13。最後SLLI18測的是bit13，不能誤標bit14。

在所需calls正常返回並保存S0／frame等前提下，有命中的返回為「原完整mask XOR所選bit」，不截成16位；沒有這八個bit時返回0。未知bit及高16位只在已選中某個已知bit時由XOR保留。

檢查器涵蓋全部65,536個low16 mask及四組upper16向量。優先序各選擇域的組數為32768、16384、8192、4096、2048、1024、512、256，無命中256。

## Message bit15 與直接 callbacks

bit15以**原入口A0 task值**呼叫RAM `2000028c`，沒有改讀固定global task ID。null回覆不解參考message、不呼叫release；非null M保存於S1：

- `U8[M+0] XOR 128 <= 1` 恰好選中type128／129，才呼叫 `5e230/5e378`。
- 所有非null types隨後都以原M呼叫 `431ba/43246`，再返回原mask XOR `8000`。

parser、release的實際消費／保存、message有效extent及所有權尚未由這些呼叫成立。

bit0與bit1分別讀取fresh函式pointer B+112與B+116；為null時略過call，否則間接呼叫。若前階段installer值保存到此處，它們分別是：

| Event | 槽位 | 條件性target V131／V140 |
|---|---|---|
| bit0 | B+112 | `558a8/559e0` |
| bit1 | B+116 | `550cc/55196` |

它們不是配置用的B+104，也不是B+108。call之前A0仍是原入口task、A1仍是完整mask；沒有重新設定其他實參。callee回覆不參與本機mask計算，但仍需S0／frame等保存合約。這兩個callback body仍待展開。

## Nested callbacks 只 guard 函式pointer

| Event | 先讀outer pointer槽位 | 再讀函式word |
|---|---|---|
| bit3 | B+128 | outer+112 |
| bit2 | B+128 | outer+108 |
| bit5 | B+148 | outer+144 |
| bit4 | B+148 | outer+140 |

程式先對outer解參考，才檢查讀出的函式pointer是否為null。**outer本身沒有local null guard**，所以「null就略過callback」只適用於函式word，仍需有效outer物件及至少116／148-byte可讀extent。

setup局部切點的outer words為0，並不能提供這些物件。仍需追查其他writers與事件可達條件；本次沒有宣稱實際fault、runtime事件或物件來源。

## Bit13 服務使用四個byte

bit13路徑依序fresh讀B+7、+6、+5、+4至A3、A2、A1、A0，再呼叫 `67c0e/67d4c`；這些都是LBU，**不是 timing halfwords**。服務回覆不作本機返回值，而是返回原mask XOR `2000`。

handler本機只有三個frame stores，沒有直接修改鏈表或持久global；這不代表各callee沒有副作用。四個byte的實際來源、服務內容及保存期仍待閉合。

## 重播與剩餘工作

```text
python analysis/check_v4160_list_setup_handler_static.py
python -O analysis/check_v4160_list_setup_handler_static.py
```

兩種模式核對180次新指令operand變異拒絕、34條選定CFG路徑、event／registration完整byte域、256個message type案例，以及重用setup、selector、fill、登記和caller原指令身分，並精確重播ledger。

仍需展開直接callbacks、nested outer物件writers、message parser／release與bit13服務；完整setup返回後的欄位保存、實際provider與scheduler綁定、其他鏈表writers／移除及缺失ROM來源也尚未證明。既有約88.09%的C重建基準不變。
