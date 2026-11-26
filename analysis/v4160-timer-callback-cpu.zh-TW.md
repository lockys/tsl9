# v4.1.60 計時縮放、callback 表移除與返回後流程

2026-11-26。原 APP 為 76800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。本批離線執行原 `0x81b0`、`0x90b0` 及 `0xfe6a` 的返回後指令，不操作設備。

## 計時 wrapper 的明示來源假設

`0x81b0` 先讀槽 `[0x4007c]`，建立 16-byte frame，保存 caller RA 至 caller_SP−4。target 入口 RA=`0x81bc`、SP=`caller_SP-16`，A0／A1 等輸入未由 wrapper 改寫。

本批唯一的合成 callee 返回是此 raw target：假設它正常返回一個 32-bit raw，保存 SP／S／GP 及全部記憶體；刻意改寫 caller-saved 暫存器，包含 RA。target 函式體不執行、不證明身分或時間單位。

正常返回後執行原 MUL／shift／epilogue，結果為：

`T = ((raw * 10) & 0xffffffff) >> 4`

乘積先截為 RV32，再右移，不能代替成未截斷的乘除。例如 raw=`0x19999999` 得 T=`0x0fffffff`，下一個 raw=`0x1999999a` 得 T=0；raw=`0xffffffff` 得 T=`0x0fffffff`，raw=`0x80000000` 得 T=0。

## `0x90b0` 搜尋並移除第一個匹配項

它讀取原表 `0x2000be08`，15 行、stride 12，只比對每行 `U32[row+4]` 與入口 A0；row+0 不讀寫。這段不是建立新 callback 表項。

- 沒有匹配：恢復 RA→S0→S1／SP，返回 A0=1；不讀 GP+166、不寫表、不呼叫 provider。
- 匹配且 `U32[row+8]` 非零：讀槽 `[0x40068]`，在 target 前停止。A0=payload、RA=`0x90e0`、SP=`caller_SP-16`、S0=行索引、S1=table base。此時 key／payload 尚未清除；未假設釋放服務返回。
- 匹配且 payload=0：原碼恢復 caller S0、RA，再讀 `U8[GP+166]`；依序清 row+4、row+8，讀槽 `[0x4005c]`，恢復 S1／SP，尾跳該 target。本批停在 target 入口，A0=GP+166 byte、A1=`(1<<index)&0xffff`、RA=原 caller link。

`free／event` 只是槽位角色的描述性名稱，target 身分與實際副作用未證明；兩者均不執行，也不供給合成返回。所有行的 row+0、其他行及 canary 都核對保持。

搜尋沒有 occupied guard。key=0 也可匹配第一個零 key，若 payload 非零仍走 free 邊界。重複非零 key 只清第一行，下一次才移到下一行；key=0 清除後仍是零，重複呼叫會再次匹配同一行。不能把「清除」概括成下一次一定跳過它。

## `0xfe6a` 計時返回後

沿用上一批原 getter 與入口 gate，不重做服務結果的假設。

activation 的 `0xfea8` 後段依序：

1. store `U32[GP+296]=T`。
2. 讀 GP+291 byte。非零時 flag=1；零時重新讀 `[GP+84]` pointer cell、config+9，flag=`(byte>>2)&3`。
3. 指定 key=`0xfb1e`，store GP+292=flag，呼叫原 `0x90b0`，RA=`0xfece`。
4. 隨後以 key=`0xfb5e` 再呼叫，RA=`0xfeda`；兩次間不按 A0 返回值分支。
5. 兩次返回後 store GP+288=2、GP+291=0，再按 RA→S0→S1 恢復 frame。

本批以表內不存在兩個 key 的 fixture 執行：兩次服務均自然返回 1，不需 free／event 返回假設，原 caller 最終也返回 A0=1。找不到 key 並不阻止上述狀態更新，不能把此值直接解釋為已移除實際 callback。

deactivation（I=0、GP+292=2）先後用同樣兩個 key，continuation=`0xff2e`／`0xff3a`。兩次未匹配自然返回後，依序 store GP+288=1、GP+292=0，恢復 caller，A0=1；不要求 raw timer 返回。

若任一次 key 匹配，就在 free／event target 前停止，只核對此前的 table 與 state 效果，**不宣稱其後 activation／deactivation 完成**。

## 無號差值與門檻

`0xff00` 後段讀 `old=U32[GP+296]`，原指令計算 `D=(T-old)&0xffffffff`：D≤1499 保持 GP+292；D>1499 先清 GP+292，再恢復 caller。A0 保留完整 D，不轉成 boolean。

這是 32-bit 差值，不是 28-bit 環形差值。另實跑原碼的具體反例：raw=`0x1999999a`、old=`0x0fffffff` 得 D=`0xf0000001` 並清 GP+292，並非 D=1。在 analysis 目錄中可用既有 helper 重現：

```python
from test_v4160_timer_callback_cpu import *
c = Services(IMAGE.read_bytes())
initialize(c)
setup(c, 1, kind=0, active=1, stage=0, event=0)
c.mem(GP+296, 4, scale(0x19999999))
table(c)
check(continuation(c, 0x1999999a) == ('elapsed', 0), 'counterexample route')
check(c.reg[10] == 0xf0000001 and c.mem(GP+292, 1) == 0, 'counterexample state')
```

此例及所有時間敘述只證明數值控制流程，不推定 provider 的物理時間、IRQ 或時鐘規格。

## 重現與驗證

```powershell
python analysis/test_v4160_timer_callback_cpu.py
python -O analysis/test_v4160_timer_callback_cpu.py
python analysis/test_v4160_zero_id_queue_cpu.py
```

僅需標準庫、原 APP 及既有有限 CPU／downstream 測試模組，不需 SDK carrier。一般與 `-O` 的完整輸出：

```text
PASS: 65536 timer inputs + 36 wrap/basis probes; 11520 callback removals; 135 pre-free stops; 768 misses; 315 duplicate/repeated pairs; 3 mutations; free/event NOT executed
PASS: 16384 full activations; 16396 unsigned elapsed checks; 1024 deactivations; 24 pending free/event boundaries; actual callback scans; explicit raw-timer return only
```

矩陣包括 raw 低16位全值與36組高位／溢位探測；15行×全部GP+166 byte×三種key的11520組無payload移除；135組非零payload入口、768組無匹配、315組重複key的連續兩次搜尋。

16384組activation變動 config、GP+291全值、raw代表值、type及I=1／`0xffffffff`；16396組elapsed涵蓋D=0–2047（含1499／1500）、減法回繞與大型無號差值；1024組deactivation使用兩個缺席key；24組matching key分別停在第一／第二次移除的free／event target。

逐段核對精確資料reads／stores、table完整內容、GP state canary、各層wrapper／caller的frame、A0與provider入口參數；兩次callback之間無stores、結束時GP stores與epilogue順序也直接比對。三項記憶體複本變異把倍率10改9、掃描15行改14行、mask基值1改2，必須被指定數值／endpoint／參數檢查抓出。

原 APP 未改。共用 CPU 僅新增標準 RV32 SLL 與 C.SUB，均經 `put` 截為32-bit；未知指令、未映射區域及界外執行繼續失敗即停。既有queue回歸通過。

既有 native C 已包含這些區域；本批增加條件性原指令與返回後流程證據，沒有新增重建bytes或重算覆蓋率。仍需追查raw timer／free／event的實際provider綁定、非零payload後續保存合約，以及 `0x171de` 等其餘callee。
