# B1 fallback 輸出、共用尾段與清零／保存期界線

接續[gate 派送及來源槽位](v4160-b1-gate-source-static.zh-TW.md)，本輪完整展開 **32-byte fallback** 及兩個 parent 共用的 **278-byte 尾段**，兩份候選合計 **620 bytes／210 條指令**。另對先前已普查的 parent 補上 **168 bytes／74 條指令**的回覆處理與 epilogue 合約，未將其當成完整 parent 行為重建。

[Python checker](check_v4160_b1_fallback_tail_static.py) 與[固定 JSON ledger](v4160-b1-fallback-tail-static.json) 保存完整 operands、hashes、CFG、stores、全部出口及串接憑證。全程只讀本機原始 bytes／strict sparse HEX，檢查不可變圖、暫存器 def-use 與封閉整數關係；沒有目標執行或模擬、可變物件／provider 模型、封包重播、硬體存取或目標網路分析。

## 完整函式及選定 parent 視窗

| 完整函式 | V131 | V140 | 每份 bytes／指令 |
|---|---|---|---|
| fallback | `[0x5a23e,0x5a25e)` | `[0x5a386,0x5a3a6)` | 32／13 |
| shared tail | `[0x567be,0x568d4)` | `[0x568fe,0x56a14)` | 278／92 |

兩個本體都包含普通 RET 之後仍可由分支進入的指令。shared tail 的另一個出口是恢復 frame 後的 `JAL x0`，不是本機 RET。兩個本機 CFG 都無環，callee 是否正常返回另論。

| 補核對的 parent 視窗 | V131 | V140 | 每份 bytes／指令 |
|---|---|---|---|
| fallback 返回後重讀 P+22 | `[0x617ee,0x617f4)` | `[0x618d8,0x618de)` | 6／3 |
| P+76 bit0 gate／retry call | `[0x6179c,0x617ae)` | `[0x61886,0x61898)` | 18／6 |
| parent A epilogue | `[0x59bfe,0x59c18)` | `[0x59d46,0x59d60)` | 26／12 |
| parent B epilogue | `[0x61992,0x619b4)` | `[0x61a7c,0x61a9e)` | 34／16 |

這些 parent 視窗已有完整來源 identity／CFG 普查，本輪只補選定 operands 與資料流意義；未增加既有 C 重建分子，也未把所有 parent branches／等待／副作用視為已封閉。

## Fallback：兩次讀取 P+272，只有第一次經過非零檢查

入口 A0=P，原始順序為：

```text
P+21 byte = 2
X0 = fresh U32[P+272]
若 X0 == 0：返回 1
寫 byte[X0+2] = 7
X1 = fresh U32[P+272]
v = fresh U8[P+45]
寫 byte[X1+3] = v
返回 0
```

因此回覆 1 不代表「未寫入任何欄位」：**P+21=2 在兩條路徑都發生**。回覆 0 只是在後續讀寫正常完成後的返回常數，沒有指標有效性／傳輸成功意義。

第一次 X0 非零不會保證第二次重新讀出的 X1 非零、相同或仍有效。即使沒有非同步 writer，第一個間接 store 若與 P+272／P+45 有別名，也可能改變後續 fresh 讀取；兩次 pointer snapshots 不能直接合併。

本體只定義 A0／A4／A5，沒有 SP、RA、S 暫存器定義、frame、child call、配置、釋放或完整指標 publication。直接 P 存取需至少 276-byte prefix；X0 需能寫到 +2，X1 需能寫到 +3。若另證明兩者是同一個有效配置且保持不變，4-byte 可寫前綴便容得下兩次 store；這不是實際配置或保存期的證明。

既有 key 將另一塊 allocator 回覆存到 W+272，要求大小為 64～260；只有同一 W=P、匹配 allocator、有效 extent／ownership、未覆寫且無干擾 alias 等條件都成立，才能把容量串接到這裡。這與接收來源 **W+276** 是不同欄位，不能互換。

## 外層重新決策，不使用 fallback 的舊 A0 回覆

parent B 的原 call `0x617da／0x618c4` 正是上述 fallback，返回後直接跳到 `0x617ee／0x618d8`：重新讀 P+22，非零則到 retry 視窗，零則到 `0x61690／0x6177a`。

retry 視窗再讀 fresh P+76 bit0；清除時直接跳到同一 join，設定時以 A0=P 呼叫 **`0x56146／0x56286`**，再跳到 join。該 retry callee 尚未在本輪展開，不能由其名稱或回覆推定副作用。

checker 另外對完整 parent B 的 immutable CFG 做 A0 liveness 核對：從 fallback 返回後，保守地把任一 A0 來源使用或 opaque call 都當成可能讀取；所有本機路徑都會先在 parent+`0x49e` 或 `0x572` 重新定義 A0。這證明舊 fallback 回覆沒有被後續本機流程觀察到，並不是目標重播或迴圈進展的證明。

parent 中間仍有其他 branches、calls 與 waits，**不代表 fallback 返回後一定立即進入 shared tail**。若控制真的到達兩個 epilogues，原指令會先 `A0=S0` 保留物件數值，再恢復 RA／S 暫存器與外層 **48／80-byte frame**，最後不新增 link 地跳入 shared tail。尾段另建自己的 32-byte frame；parent 的 frame 不會因此繼續疊留。

## Shared tail 的可選 clock／delay callback 前段

以下 G=`0x20003000`，D=`0x20003234／0x20003284`。入口先捕捉 delay-callback 槽位 `G+1256／1336` 的 H0；H0=0，或之後 fresh U16[`G+1132／1212`] 不恰為 1，都直接跳到共同的 P+14 store。

通過兩個 gate 時，讀取 K=U16[D+8]、h=U16[P+134]、base=U32[P+144]，計算：

```text
q = floor(low32(h*K + 999999) / 1000000)
若 unsigned base < q：baseAdjusted = low32(base + fresh U32[D+4])
否則：baseAdjusted = base
C = low32(baseAdjusted - q)
```

h*K 本身不超過 U32，但加 999999 可能回繞，所以這不是完整 64-bit 乘積的數學 ceil。q 的上界是 4294。checker 保留 h=K=65535 的封閉算術例子：回繞 numerator=868928，q=0；沒有宣稱存在對應的實際可達物件或封包。

接著從 `G+480／560` fresh load clock pointer，沒有本機 null guard；當時傳入 A0 的值為 **baseAdjusted**，不是 C 或強制零。clock 回覆 T 在本階段保持 opaque。之後的 residual R 分支為：

- 若 unsigned C>=T：`R=C−T`。
- 若 C<T 且 signed `low32(T−C)` 非負：R=0。
- 否則：C 加另一個 fresh D+4 **一次**，再取 `R=low32(C−T)`。

這包含對 wrapped 差值的 signed 判斷，不能簡化成一般無號 clamp，也沒有重複 modulo 正規化、共用 period snapshot、實體時間或單調進展證明。

之後取 M=`fresh U8[G+515／595] >> 1`，範圍 0～127；再把原 delay-callback 槽位**重新讀取**成 H1，沒有第二次 null check。H1 不必等於最初的 H0。

- R<=M：以 A0=0 呼叫 H1，其餘參數保持 then-live。
- R>M：以完整高低 pair `(R−M)*1000000`、除數 pair `(fresh U16[D+8],0)` 請求 `0x6df1a／0x6e10a`；再將 opaque A0 回覆交給 H1，其餘參數仍未全部重設。

高位 MULHU 被保留，不是只取 low32 的乘積；新實參域的完整商值與除零語意未在本輪證明，fresh divisor 也沒有非零 guard。H1 回覆不作後續成功 gate。未知 clock、H1 與算術 callee 的實際綁定／副作用仍需條件。

## 共同 store 後分兩路：只有一路本機清 B+164

所有正常本機出口前，先寫 **P+14=176**（SB −80 的低 byte），再 fresh 讀 **D+12 byte**，不是 D+9。

| fresh D+12 | 後續原指令順序 |
|---|---|
| 非零 | `RAM 0x2000078a(0)` → `B+164=0` → 讀 fresh `G+1260／1340` 作 A0 → 呼叫 `0x43ed2／0x43f5e` → 固定位址 store → 恢復 frame／RET |
| 零 | 讀 fresh U8[P+41] → 恢復 frame → 以 `(0,mask)` 尾跳 `0x4354a／0x435d6` |

B=`0x200033b8／0x20003408`，B+164 正是前階段 query publication／parent capture 的 current-object cell。**D+12=0 的本機路徑沒有這個 clear**。

非零路徑的固定位址原指令為 U32[`0xe000e204`]=`0x02000000`；此處只核對 operands，不推定實體控制器事件已發生。普通 RET 前最後一個 A0 定義是 `0x43ed2／0x43f5e` 的 call，故回覆維持 opaque，沒有強制 0／1。

### 匹配 setter 清的是另一個 callback 槽位

重用完整 first-copy setter（22 bytes），確認 `RAM 0x2000078a(0)` 會直接清除 registered-hook slot **`0x20002ef8／0x20002f48`**，並略過相鄰 flag 的本機寫入。

這與 delay callback 槽位 **`0x200034e8／0x20003538`**，以及 B+164 current-object slot，都是不同 cell。不能把三者當成同一 callback pointer，也不能把 pointer 清零視為排空既有 callback、停止非同步活動或釋放物件。隨後的 `0x43ed2／0x43f5e` 副作用仍未在此封閉。

### 零分支的 mask 與 event helper

j=fresh U8[P+41]，原指令先用 RV32 的低五位 shift count，再取 low16：

```text
mask = low16(1 << (j & 31))
A0 = 0
A1 = mask
恢復 32-byte frame，再以 JAL x0 進入 event helper
```

`j&31` 為 0～15 時 mask 為單一 bit；16～31 時 mask 為 **零**。不能用原始 byte 的大小當成沒有 wrap 的 shift count。

重用完整 64-byte event helper，確認它先保存／清零控制 word `0x4002420c` 並 FENCE.I，再檢查 task0 是否小於 fresh task count。count 非零時，讀取 event table pointer，將 mask OR 入 halfword 並返回 0；count=0 時略過 event-table 存取，返回 3；兩條正常路徑都恢復控制 word。mask=0 並不跳過 count 通過後的 pointer 存取／store，也沒有 pointer null guard。

這個匹配 event leaf 沒有 APP callback 或釋放 call，但不能因此排除較早 opaque callees、其他 writers 或整體生命週期問題。

## 清除 publication，不是 free／ownership 證明

fallback、shared tail 的明示 callsites，以及匹配的 setter／event leaf，都沒有向已知 allocator private-free entry 傳入 P 或 X 的直接釋放請求。這只是所列本機及已核對 leaf 的呼叫界線，不能排除未知 callee 的 transitive free、保存指標或其他副作用。

尤其 shared tail 的可選 clock／delay callback 發生在後續 P+14 store 之前；保存 S2 的 P 數值不能證明當時 pointee 仍有效。另一條路徑清 callback slot／B+164，也沒有建立 P+272 配置的 ownership、釋放時點、來源物件同一性或 in-flight callback 的保存期。

## 驗證與後續缺口

```powershell
python analysis/check_v4160_b1_fallback_tail_static.py
python -O analysis/check_v4160_b1_fallback_tail_static.py
```

checker 重跑祖先證據鏈、APP／SDK／兩份 candidate 身份、strict sparse HEX 與固定 ledger。兩個完整本體的 CFG edges 分別為 **12／97**，DAG 語法路徑數為 **2／28**；shared tail 有 14 條到 RET、14 條到外部 tail。每條 edge 有語法 exit walk；這些不是可執行測資、路徑機率或 target traces。

返回與 frame 憑證核對 fallback 的強制 0／1、shared tail 的 opaque RET／事件尾跳參數、配置支配 SP-relative 存取、兩個出口各自恢復 32-byte frame，以及 P+14 store／B+164 clear 的支配與分支界線。

負向檢查含 **284 個指令位置、26 個 typed-load funct3**，必須全部拒絕。q 的純整數檢查為四個 K 樣本各遍歷全部 65536 個 h，共 **262144 組**，不是 U16×U16 的完全窮舉；另核對 256 個 byte masks、threshold、full numerator 上界及 signed 差值邊界。未建立目標 ISA、clock、frame、buffer、heap 或 provider 的可變模型。

仍需展開 retry `0x56146／0x56286`、service `0x43ed2／0x43f5e` 及其他 parent 路徑，確認 P+272 第二次 reload 的物件同一性、有效配置／別名、clock／callback 實際綁定、in-flight callbacks、完整消費／釋放與 ownership。此次未增加既有 C 重建分子或更新 **95.75%** 靜態重建快照，也未宣稱完整可用韌體已驗證。
