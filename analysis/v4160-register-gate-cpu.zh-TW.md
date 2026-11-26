# v4.1.60 `0x9fc8` gate 與 `0x9124` callback 表更新

2026-11-26。原 APP 為 76800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。本批在有限CPU中離線執行原 `0x9fc8`、`0x8202`、`0x9124..0x9250` 及B6F4原呼叫邊；所有資料均為合成fixture，不操作設備。

## 先清欄位，再決定是否進入服務

`0x9fc8` **先store `U8[GP+172]=0`**，才讀 `[GP+84]` 指標及config+8；任何早返路徑都已發生清除。fixture GP=`0x20004000`。

| 條件 | 行為 |
|---|---|
| config+8 bit4清除 | 不建立frame，返回入口A0 |
| bit4設定 | 建16-byte frame、只保存RA，執行原 `0x8202` |
| getter返回0 | 恢復frame返回0，不讀GP+354 |
| getter非零、GP+354非零 | 恢復frame，返回getter byte |
| getter非零、GP+354=0 | 恢復frame，tail `0x9124` |

`0x8202` 只讀 `U8[0x2000bee1]` 至A0，其他暫存器保持，沒有stores。成功到達tail的參數固定為 **A0=`0x9f7a`、A1=0、A2=10000、A3=0**，RA／SP保持caller狀態。本批將`0x9f7a`作為表key，不執行該callback函式體。

## `0x9124` 的三種表搜尋

表位址 `0x2000be08`，15行、stride12；key為row+4、payload為row+8，flag只寫row+0的一個byte，高三bytes保持。輸入為 `(key,flag,duration,payload)=(A0,A1,A2,A3)`。

入口frame=32 bytes，保存順序為S2／RA／S0／S1／S3／S4，地址依次caller_SP−16／−4／−8／−12／−20／−24。

**duration=0的快路徑**先找第一個key=0，不先找相同key：找到就依序寫入key、flag byte=0、payload，恢復frame，讀槽 `[0x40050]` 及 `U8[GP+166]`，tail該target。A0=GP+166 byte、A1=`(1<<index)&0xffff`、A2仍為0。

快路徑不讀舊payload，也不free；即使已有同key，仍可能在空行新增重複項。若15行全滿，**不立即失敗**，而是落入下面的一般搜尋，既有key仍可能更新。

**一般路徑**（duration非零或上述全滿落入）先搜尋第一個相同key，即使前方有空行，也優先更新後面的既有key：

- 匹配後讀舊payload。非零則讀 `[0x40068]`，在target入口停止：A0=舊payload、RA=`0x91b6`、SP=`caller_SP-32`；S0=完整flag、S1=index、S2=table、S3=duration、S4=新payload。此時尚未改表。
- 舊payload=0：先讀GP+166，再store flag byte、新payload；不重寫既有key。
- 無匹配才第二次掃描第一個key=0，插入順序為key、flag byte、新payload，再讀GP+166。不讀該空行的舊payload，可能覆寫其stale word而不進free邊界。
- 無匹配且無空行：恢復frame，返回A0=1，不寫table、不呼叫provider。duration=0的全滿情形最多可讀三輪15行key。

key=0同樣參與匹配／空行判定，沒有另一個occupied檢查。測試覆蓋零key、重複key、前方空行但後方已有key，以及stale payload，不推定這些fixture在原機上的所有權或可達性。

## 縮放與完整flag判斷

一般路徑在改表後計算：

`scaled = ((duration * 1000) & 0xffffffff) // 625`

這裡duration是完整32-bit輸入，不能套用上一批nibble有界流程的 `8*duration//5` 簡化。4294967／4294968及MASK等案例覆蓋乘法回繞；非零duration即使scaled=0，也不會改走zero-duration快路徑。

| 完整flag | 目標與邊界 |
|---|---|
| 0 | call `[0x40058]`，RA=`0x9230`、frame仍在 |
| 非零 | 恢復frame，tail `[0x4022c]` |

兩者A0=GP+166 byte、A1=單bit mask、A2=scaled。判斷看完整flag，故 `flag=0x100` 雖store byte0，仍走非零tail。槽位是 **`0x4022c`**（`0x40000+0x22c`）。新插入走40058時S1仍為15；既有更新則S1=index。

free與兩個tail target均不執行。40058可停在入口，或使用明示正常返回：保存SP／GP、table、saved frame及未列入clobber的其他暫存器；刻意改寫caller-saved及S0–S4，A0給指定reply。原碼只對reply做SEQZ，隨後從frame恢復S0–S4，故返回 **1 iff reply=0，否則0**。不代表provider可以任意破壞所有S暫存器或stack。

table在呼叫provider前已修改；即使reply非零，原後段也不回滾。本批只證明數值控制流與明示返回合約，不把0／1命名為實體服務成功或失敗。

## 原gate與B6F4串接

128組沿 `0x9fc8` 的真實tail接入 `0x9124`：112組gate早返，4組停free，8組到40058，4組滿表自然返回。`0x9fc8`固定duration10000、flag0、payload0，因此此上游路徑A2縮放為16000，不到40050／4022c；其他路徑由獨立fixture覆蓋。

另外30組執行原 `0xb6f4`→`0x171de` 早返→後續分支：6／7進`0x9fc8`，高位別名跳過它。滿表自然返回或指定40058正常返回後，繼續原SB至 `0x2000bf0c`，核對完整caller frame、A0及S0–S4恢復。未指定40058返回的兩組仍停在入口，不列入30組完成返回。

## 重現與結果

```powershell
python analysis/test_v4160_register_gate_cpu.py
python -O analysis/test_v4160_register_gate_cpu.py
python analysis/test_v4160_zero_id_queue_cpu.py
```

只需標準庫、原APP與既有有限CPU／schedule模組，不需SDK carrier。

```text
PASS: 196608 gate byte cases; 1536 K probes; 256 unconditional clears; 19440 table cases {'immediate': 1440, 'full': 0, 'free': 6120, 'call': 2970, 'repeat': 8910}; 23040 task/flag cases; 324 full tables; 1260 priority/duplicate cases; 90 declared normal returns; 4 mutations
PASS: 128 original 9fc8-to-9124 chains {'return': 112, 'free': 4, 'call': 8, 'full': 4}; 30 b6f4 full returns; free/tail providers NOT executed; 40058 return premise explicit
```

196608組為config8×getter全部byte×K=0／1／255；1536組另覆蓋K全部byte；256組變動GP172舊值。19440組table矩陣含全部行、既有／新行、九種duration、四種完整flag、三種task byte、三種key及兩種舊payload。其內都有可用行／匹配，因此full=0；滿表無匹配另由324組核對。

另外23040組遍歷task byte、flag與行；1260組覆蓋搜尋優先／重複key；90組明示正常返回取0／1／MASK。逐例比較精確reads／stores、整張表及flag相鄰canary、provider參數、live／restored frame。四個記憶體複本變異改GP172清除位置、搜尋上限、倍率1000及SEQZ門檻，均須由指定存取／endpoint／參數／返回斷言抓出，不以解碼失敗充當通過。

原APP未改。共用CPU只新增標準C.SW解碼，仍對未知指令、未映射存取及界外執行失敗即停；queue回歸通過。

既有`output_dependencies.c`、`state_leaf_reads.c`、`scheduler.c`已重建這些C區域。本批增加原指令與呼叫合約證據，沒有新增重建bytes或重算覆蓋率。仍需追查非零payload的free保存合約、各槽位provider綁定，以及`0x9f7a` callback後續。
