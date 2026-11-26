# v4.1.60 provider 槽位、候選啟動映射與證據界線

2026-11-26。本批把前幾批條件性TX／callback驗證所依賴的服務槽位，與本地兩份SDK reference carrier做靜態對照。**未取得installed resident身分，也沒有把候選當成原機provider。** 所有分析離線；只做host端讀bytes、解操作數及產生清單，不執行APP／候選ISA、provider或設備操作。

固定APP為76800 bytes，base=8000，end=1ac00，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。本批13個400xx槽位都在該檔案範圍之外，因此這份APP本身不含它們的實際word內容。

產物：[可重跑腳本](check_v4160_provider_binding_ledger.py)、[完整JSON ledger](v4160-provider-binding-ledger.json)。本批未修改原BIN、舊seal、C或既有驗證器，不提高C覆蓋百分比。

## 固定的本地reference輸入

只讀主連續segment，不補稀疏HEX洞位或讀取缺失尾端。兩份原始來源provenance及既有提取說明見 [candidate README](wch-resident-candidate-2026-10-21/README.md)、[resident-entry](wch-resident-candidate-2026-10-21/resident-entry/README.md)。本輪沒有下載資料。

| 嵌入版本 | 主segment bytes | SHA-256 |
|---|---:|---|
| V1.31／carrier-dec2023 | 191078 | `133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22` |
| V1.40／carrier | 191574 | `b02cf8ec6829425a558887bd6bc10d28ae1f0e2e9e1850333f0bab6088e9e941` |

候選標籤、API header名稱與table數值不是installed證據；即使某段code相同，也不能推論整體ABI、RAM狀態或副作用相同。

## 先解各自startup，再換算RAM target的load image

腳本從40000的原JAL解entry，對startup前40 bytes做有界常數傳播，固定其20-byte seed-copy迴圈與MRET bytes，再解原initializer呼叫。initializer只分析第一個helper呼叫之前的直線操作數；不執行stores、copy或callee。

seed helper的18 bytes固定為inclusive比較／word複製形狀。由原A0/A1/A2及helper內容換算第一段copy的load-image範圍：

| 候選 | entry／initializer | seed source | 第一段source | RAM目的範圍（右界不含） |
|---|---|---|---|---|
| V1.31 | 6de7e／6de0c | 40280 | 402b0 | 20000040..20002e74 |
| V1.40 | 6e06e／6dffc | 402c0 | 402f0 | 20000040..20002ec0 |

A2為最後word的**inclusive**位址，故end-exclusive=A2+4。所有要求的第一段來源bytes都位於各自主連續segment內。這是候選初始化操作數建立的條件性load-image映射，不是觀測到啟動完成或RAM code保持未改。

## 同一RAM數值不代表同一flash座標

下表數字均為十六進位；版本槽40034為資料指標，其餘為候選table值。ledger另保存JALR最低bit正規化target、映射後source及16-byte prefix hash。

| slot | V1.31 word | V1.40 word |
|---|---|---|
| 40034 | 6e6a0 | 6e890 |
| 40038 | 433a8 | 43434 |
| 4003c | 20000442 | 20000442 |
| 40048 | 2000039c | 2000039c |
| 4004c | 20000332 | 20000332 |
| 40050 | 4354a | 435d6 |
| 40058 | 43728 | 437b4 |
| 40060 | 43a8c | 43b18 |
| 40068 | 431ba | 43246 |
| 4007c | 43520 | 435ac |
| 40080 | 43c4e | 43cda |
| 4013c | 4b456 | 4b4ee |
| 4022c | 43932 | 439be |

三個RAM targets分別換算為：

| target | V1.31 source | V1.40 source |
|---|---|---|
| 20000442 | 406b2 | 406f2 |
| 2000039c | 4060c | 4064c |
| 20000332 | 405a2 | 405e2 |

不能直接以RAM位址減40000取檔案bytes，也不能把所有版本差異套用同一flash偏移。其他function的prefix16 hash僅固定有界來源，不宣稱完整函式相同、可達或ABI已證。4004C完整58-byte copy body沿用既有候選hash；本批另固定40048的完整46-byte body。

## 新補的40048候選fill body guard

兩份候選經各自映射後，46 bytes完全相同，SHA-256：

```text
d67147a681aca68d4d082eebf74ab6214f61f43253be91e932eebd5c3e3d05a3
```

固定原bytes的靜態解讀：先讀控制word4002420c、寫0、FENCE.I，再檢查目的指標及count；因此null目的或count=0也先經控制word序列。非空時逐byte寫low8(A1)、遞增A0，正常完成前回到saved控制word的store與RET。

本體只寫A0/A4/A5，沒有frame或其他call；非空且正常完成時A0為32-bit end pointer，**不是標準memset的原始dst返回值**。尚未證明控制word／FENCE.I的物理意義、存取成功、正常返回或實際保存合約。

這提供先前 [TX fill假設](v4160-tx13346-prefix-cpu.zh-TW.md) 的一個具體reference對應；不把它升格成installed實作。本輪只固定及解讀bytes，未執行該body，沒有接觸真實或合成MMIO裝置。

## APP相鄰編碼清單不等於完整writer／callsite清單

延伸既有4004C checker的模式：遍歷APP每個halfword對齊位置，只接受 `LUI reg,40000` **緊接**匹配base的LW/SW或C.LW/C.SW，彙整13個slot的語法候選。JSON保存每一對原位址。

| slot | load／store候選 |
|---|---|
| 40034 | 0／0 |
| 40038 | 3／0 |
| 4003c | 5／0 |
| 40048 | 47／0 |
| 4004c | 41／0 |
| 40050 | 4／0 |
| 40058 | 21／0 |
| 40060 | 1／0 |
| 40068 | 8／0 |
| 4007c | 1／0 |
| 40080 | 1／0 |
| 4013c | 2／0 |
| 4022c | 0／0 |

全部store數為0，只代表**此相鄰模式**沒找到store候選；不排除間接stores、隔多條指令的地址計算、其他寫入途徑，也沒有排除資料誤解碼或證明CFG可達。尤其4022C明明在原9124尾段被讀取，卻因LUI與LW間隔多條指令而不在本模式內，不能把0當作不存在。

## 版本前綴與身分界線

重新讀取既有version contract所定位的APP比較operand：1ab1c起21 bytes為 `CH32V20x_BLE_LIB_V1.3`。本批重讀literal及候選version指標內容，沒有執行memcmp或原機版本gate。

V1.31候選的前21 bytes相符，但完整字串為 `...V1.31`，與APP完整literal不同；V1.40前綴亦不符。因此ledger只記錄「prefix21 match」及「full-string mismatch」，所有 `installed_binding_proved` 保持false。不能用前綴相符補足installed身分、startup成功或provider保存合約。

## 驗證與重跑

ledger已存在時，預設只讀重算、逐byte比對，無寫入：

重跑需要上表兩個完整carrier置於腳本指定的本地路徑。本輪已核對GitHub主線APP與本地blob一致；主線目前沒有這兩份candidate carrier，因此只clone倉庫尚不足以重跑candidate檢查。JSON ledger可直接審閱，完整來源檔的hash與本地正常／-O結果均已記錄。

```text
python analysis/check_v4160_provider_binding_ledger.py
python -O analysis/check_v4160_provider_binding_ledger.py
```

`--write`只用於初次建立新ledger，使用exclusive-create並拒絕覆寫。一般與-O皆使用check，不靠assert：

```text
PASS: 28 synthetic access encodings; 9 specified raw mutations rejected; odd-pointer distinction
PASS: 13 slot words/profile; two independently decoded startup mappings; full copy58/fill46 byte guards
PASS: ledger exact replay; V1.31 prefix21 matches but full string does not; installed provider identity NOT proved
```

28個合成encoding測試涵蓋每slot的32-bit load/store及兩個compressed範例。9組負測直接進入不含整檔hash前置門檻的derive，分別改APP operand、inclusive helper、首copy來源、RAM target、fill body、截短version來源、首copy目的、seed-loop及MRET，均由指定guard拒絕。

另有odd-pointer正測：raw slot word改成奇數時，JALR正規化target與prefix可保持相同，但原始table word已不同；不能把「同一entry」當作「同一原始綁定證據」。完整baseline仍先核對APP及兩candidate的完整hash。

後續尚需釐清installed provider來源、RAM code是否未改、真實資料與保存／副作用合約，以及其餘APP呼叫。本批僅新增靜態ledger、guard與說明，沒有安裝、下載、修補、執行provider或操作硬體。
