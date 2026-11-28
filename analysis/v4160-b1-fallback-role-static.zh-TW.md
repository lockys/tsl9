# v4.1.60：Role gate 兩分支的 fallback 保存邊界

接續 [timer 與第二個 task](v4160-b1-fallback-timer-static.zh-TW.md)。本輪把 `0x8eb6` 呼叫前的條件式 fallback=`0`、實參 `(4,0,5)`，接到匹配的 `0x401a0` 候選服務；分別核對 gate 為零及非零時的寫入與截止點。

檢查器：[check_v4160_b1_fallback_role_static.py](check_v4160_b1_fallback_role_static.py)；證據：[JSON ledger](v4160-b1-fallback-role-static.json)。全程使用原始 bytes、CFG／stores 分類、固定區間與封閉欄位運算；沒有執行韌體、建立可變 target 狀態模型、操作硬體、重播或連線 target。沒有增加 C 重建 bytes 或提高覆蓋百分比。

## 共用入口與登記條件

| 項目 | V1.31 | V1.40 |
|---|---|---|
| 候選 `0x401a0` 入口 | `0x6dd16` | `0x6df06` |
| Primary | `0x61b1c` | `0x61c06` |
| Gate 函式 | `0x55bde` | `0x55d1e` |
| Fresh gate byte | `0x2000319f` | `0x200031ef` |
| 物件 B | `0x200033b8` | `0x20003408` |
| Fallback | `0x20003220` | `0x20003270` |

Gate byte 是 `ctx+3`，與 count `ctx+1`、capacity `ctx+2` 不同。前階段 context clear 只是來源證據，沒有據此判定實際走哪條分支。新證書涵蓋全部 256 個 gate byte 的條件式分類，並不宣稱兩條路徑均已證明可從真實 boot 到達。

兩條路徑都要求 fresh count=`5`、capacity=N0、table=`0x200047f4` 保持至所選登記。全部 67 個 N0（14..212、間隔 3）均接受 index 5，將 count 改為 `6`，在 `T+20=0x20004808` 寫入該路徑自己的 callback，並返回舊 index `5`。入口 A0=`4` 不等於這次登記的 ID。

## Gate 為零：初始化至第一個 RF call 前

內層登記保存 callback `0x5352c`／`0x535da`。Initializer 以返回的 ID `5` 為輸入，建立 16-byte frame，將 ID 保存至 S0，請求 fill 清除 `[B,B+296)`，另用一筆直接 word store 及兩個無 frame leaf setters 清除 `[B+296,B+308)`，再把 byte `5` 寫回 `ctx+3`。

完整 initializer 為 426 bytes／138 指令。第一個 late call 前的 41 筆直接 stores 全部分類：4 筆自身 frame、物件外緊鄰 word／gate 各一筆，以及 35 筆物件欄位 stores。Suffix 的 35 筆均在 `[B,B+296)`；期間只有一個已核對、無 stores／frame／巢狀呼叫的 selector leaf。

物件 `B+3` 是 selector 結果 byte，與 `ctx+3` 的 ID byte 分離。若 fresh copied clock halfword 仍為 `1000`，selector 結果即為 `0`；原指令對所有大於 250 的 halfword 都回傳 0。這不會把 gate 的 `5` 改成 `0`。

第一個 RF call 的參數使用另一個來源：

```text
k = min(fresh U16[config64+16], 251)
A0 = 27
A1 = 328
A2 = 8*(k+14)，範圍 112..2120
A3 = 8*(k+138)，範圍 1104..3112
```

新證書以三個 size 區間核對所選 CFG（0..26、27..251、252..65535），並對全部 U16 值檢查欄位界線。Selector 的 halfword 與此 size halfword 是不同來源，沒有將兩次 fresh loads 當成同一個值。

| 截止點 | V1.31 | V1.40 |
|---|---|---|
| Initializer | `0x5362e` | `0x536dc` |
| 第一個 late call 指令 | `0x537b2` | `0x53860` |
| 尚未執行的 RF callee | `0x64298` | `0x64382` |

在此截止點，initializer／gate／primary／outer frames 仍活躍。Gate 與 primary 後面的 callback pointer stores 尚未執行；沒有證明 initializer 已返回，也沒有把這些 stores 提前算進零分支的行為。

## Gate 非零：發布後至第一個 outer initializer 前

Fresh gate 為 1..255 時，gate 跳過內層登記及 initializer，只發布四個固定 callback words；primary 再發布三個固定 words。這些是指標資料寫入，不能據此說 callback 已被呼叫。

之後 outer 的第一個登記保存自己的 handler `0x4dbf2`／`0x4dc8a` 到同一個 entry5，返回 ID `5`、count=`6`。這與零分支的 handler 是不同路徑，不能合併為同一次登記。

| 截止點 | V1.31 | V1.40 |
|---|---|---|
| 尚未執行的 outer initializer | `0x4da70` | `0x4db08` |
| 呼叫前實參 | `(5,0,6)` | `(5,0,6)` |

在此條件下 gate byte 保持原非零值，outer frame 仍活躍。後續 initializer、副作用、登記 indices 及 outer tail 都不在本證書內。

## 保存證據與限制

每版零分支的六個範圍包絡為 fill control word、count byte、entry5 word、296-byte 物件、12-byte 緊鄰欄位、gate byte。非零分支的九個包絡為 count、entry5 及七個 callback words。

這些區間均在數值上避開 fallback、兩個 APP task bytes、timer head／名義 timer node、small／remainder／large headers、capacity、table pointer 及既有 entry0..4。對前階段沒有建立 node 的替代路徑，node 區間只是額外保守的排除範圍，沒有宣稱該節點存在。

相對 role 入口 SP=S，saved RA 位於 outer 的 S−4、primary 的 S−20、gate 的 S−36；initializer SP 為 S−64，其 S2／S1／S0／RA 保存在 S−64／−60／−56／−52。這是原指令保存位置與相對深度證據，仍要求有效且不回繞／不別名的 owned frames，以及保存字不受干擾。

兩版各核對十個 resident strict sparse HEX 區間，包含完整入口／primary／gate／initializer／selector／setters／登記／fill 與 `0x401a0` word；缺失 bytes 沒有補零。520 筆原指令變異檢查、全部 256 gate byte／65,536 size 值及 exact-byte ledger 比對都必須通過：

```powershell
python analysis/check_v4160_b1_fallback_role_static.py
python -O analysis/check_v4160_b1_fallback_role_static.py
```

所有前階段 source／timer／保存條件仍保留。實際 installed provider、fresh gate／source fields、head／header 的先前保存、frame／heap ownership、正常存取與呼叫完成、實體 MMIO／FENCE／IRQ／DMA／reentry／外部 writer 影響均未無條件證明。零分支的 RF 與後續 late callees／tail、非零分支的 outer initializer、完整事件消費與保存釋放期仍待釐清。
