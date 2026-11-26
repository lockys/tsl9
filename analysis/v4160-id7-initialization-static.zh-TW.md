# 第二個外層 ID7 初始化：四個 callee、記錄發布與 ID8 邊界

接續[ID6 leaf 返回鏈](v4160-id6-leaf-return-static.zh-TW.md)，本次完整展開 `46570`／`46608`、四個直接 callee、selector 尾跳，以及返回後的下一筆 task-registration。resident 映像仍是參考候選；實際 RAM provider 綁定尚未由來源表證明。

| Body | V131 範圍（右端不含） | V140 範圍（右端不含） | Bytes／指令 |
|---|---|---|---|
| initializer | `46570..465b4` | `46608..4664c` | 各68／22 |
| defaults | `45220..45380` | `452b4..45418` | 352／102；356／103 |
| vectors A | `48c56..48ce6` | `48cee..48d7e` | 各144／40 |
| vectors B | `47eac..47f2a` | `47f44..47fc2` | 各126／35 |
| final state | `6d682..6d700` | `6d86e..6d8ec` | 各126／36 |
| selector tail | `4d9ec..4da18` | `4da84..4dab0` | 各44／16 |
| next outer window | `6dd3e..6dd4e` | `6df2e..6df3e` | 各16／4 |

合計1756個原始 bytes、511條指令；所有 operands、分支／呼叫目標與各 body SHA256 均固定於[靜態檢查器](check_v4160_id7_initialization_static.py)，完整證據見 [JSON](v4160-id7-initialization-static.json)。有 call 的 CFG fallthrough 是正常返回的前提，並非已實際執行。

## ID7 的保存與四個 callee

沿用前階段條件性入口，A0=7、A2=8；A1可能是0或 callback table 的最後觀察值。initializer 建立32-byte frame，將 RA存入SP+28、完整入口A0存入SP+12；以入口SP計算，分別為−4、−20。

它依序呼叫 defaults、vectors A、vectors B、final state。前三個都是無 load、無 call、無 frame 的直線函式，只將固定值或 code pointer 寫入固定 RAM 地址。它們不定義 RA、SP、GP、TP、S registers，但 defaults 會令 A0=2000，因此 caller 後續重新載入 saved ID 是必要步驟。vectors 的指標寫入不會呼叫那些 callbacks。

final state 也只有固定寫入，最後不設 link 地尾跳 RAM `2000039c`，要求 fill `(200035b0/20003600, 0, 6)`。這是本次唯一仍需 provider 返回／保存合約的呼叫邊界。若它正常沿 carried RA 返回，便接回 initializer+22；仍需有效 code／RAM／stack、SP／frame／所需狀態保存、實體非alias與無外部干涉等條件。這些條件沒有透過執行 provider 或硬體來驗證。

## 兩版 defaults 有實質差異

defaults object 分別位於 `20003268`／`200032b8`：

| 尾端欄位 | V131 | V140 |
|---|---:|---:|
| field132 半字 | `ffff` | `ff81` |
| field134 半字 | 本函式無此 store | `ffff` |

V140 還調整了部分 store 順序與暫存器配置，完整 body 比 V131 多4 bytes、1條指令、1個 store。檢查器分別固定兩版模板，沒有把這個差異當成單純 relocation。

## 返回前的固定發布

四個 callee 返回且保存條件成立後，initializer 執行以下本機寫入：

| 寫入 | V131 | V140 |
|---|---|---|
| halfword=`ff00` | `2000324a` | `2000329a` |
| byte=0 | `2000324c` | `2000329c` |
| byte=`ff` | `200033ae` | `200033fe` |
| byte=saved ID7 | `200033ac` | `200033fc` |

其中窄指令 `baa3` 是 halfword offset+2，`34a3` 是 byte offset+2；沒有採用一般 RISC-V disassembler 將它們顯示為浮點 store 的結果。

initializer 接著取回 saved RA、釋放32-byte frame，設定 A1=5，帶 saved A0=7 尾跳 selector。它自己沒有 ordinary RET。

## Selector=5 寫入第1筆記錄

selector leaf 先計算：

```text
t = (A1 - 4) mod 2^32
accept iff (t & 65535) <= 3
record = (base + 12*t) mod 2^32
```

接受路徑依序 SB入口A0至record+2、SH入口A1至record+0，返回 A0=0；拒絕路徑沒有 store，返回 A0=2。兩條路徑都保留 A1，不呼叫其他函式，也不改寫 SP／RA／GP／S。

本 caller 明確設定 A1=5，因此 t=1，record 是 `2000332c`／`2000337c`：先寫 byte+2=7，再寫 halfword+0=5。這三個 bytes **確實修改了先前第一 initializer 的48-byte記錄區**，不能把整個記錄區視為保持原值。它與 callback table `20003358..20003388`／`200033a8..200033d8` 是不同區間。

檢查器涵蓋全部65536個 U16 selector：接受值為4..7，其餘65532個拒絕。但一般32-bit A1的 guard只檢查低16位，地址乘法仍使用完整t；因此 guard本身不能證明任意32-bit caller 的寫入都落在48-byte表內。本次 caller=5 的區間證據不依賴這種泛化。

## 固定寫入的保存界線

檢查器為所有非frame store建立固定地址區間：V131118筆、V140119筆，另列6-byte fill的目的區間。這些區間逐一避開 task count/capacity/gate/table-pointer、T 的 task entries、F+21／F+36／F+48 optional hook／F+68，以及先前的 pool pointers、resource count bytes 和48-byte callback table。

這證明已列本機固定 store 的直接寫入界線；frame與實體alias、未知 fill provider、其他 writers／非同步寫入仍保留前提。對來源 slots 的保存也不等於已證明其當前內容、指標身分或 callback 物件保存期。

## 返回 outer 後，條件性進入 ID8

selector 的普通 RET 在有效 frame／table／code 等前提下返回 `6dd3e`／`6df2e`，A0=0、A1=5。此處未固定 A2，因為它可能被 fill provider 改寫。

outer 不測試返回值，直接將 A0改為下一個 handler `4a808`／`4a8a0`，再呼叫既有 task-registration。若這次 fresh count仍8、capacity仍≥14、table pointer仍T=`200047f4`，且 extent／非alias／保存前提成立，會寫入entry8=`20004814`，回覆A0=8、A2=9，count變為9。該 registration 不定義A1，因此此時 A1仍為5。

新的邊界停在 `6dd4a`／`6df3a` 對第三個 initializer `4a7d6`／`4a86e` 的呼叫前，參數為 `(A0,A1,A2)=(8,5,9)`。這是條件性串接，未宣稱實際裝置已執行到這裡。

## 離線重播

```text
python analysis/check_v4160_id7_initialization_static.py
python -O analysis/check_v4160_id7_initialization_static.py
```

兩種模式均要求精確 JSON 重播、511次逐指令 operand 變異拒絕、65536個 selector 算術域、所有固定寫入區間與返回連結檢查。既有 APP／candidate／SDK／來源身分及上游靜態證據一併重播。未執行或模擬目標 ISA、fill、callback、MMIO、CSR 或 trap；新增靜態合約不增加既有約88.09%的 C 重建基準。
