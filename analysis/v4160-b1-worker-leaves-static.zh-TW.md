# B1 worker 下游：37-bit 計數、設定限制、分組計時與候選掃描

接續[完整 query worker 與 reschedule](v4160-b1-query-worker-static.zh-TW.md)，這次展開四個直接下游函式的兩份 resident 候選原指令，共 **1,340 bytes、458 條指令**。已確認五位元組輸入的計數結果為 **0～37**、兩組設定限制的常數是 **2704／2120**，以及分組計時會跨三個呼叫保留同一個節點指標值，最後寫入 `L+8`。這仍未證明節點在寫入時有效。

[Python checker](check_v4160_b1_worker_leaves_static.py) 與[固定 JSON ledger](v4160-b1-worker-leaves-static.json) 保存完整 operands、hashes、CFG、全部 stores、呼叫串接及驗證憑證。分析只讀取本機原始 bytes／strict sparse HEX，並核對不可變 CFG 和封閉的 host 整數恆等式；沒有執行或模擬目標韌體，沒有建立可變物件、鏈表、clock、timer 或 provider 模型，也沒有封包重播、硬體存取或目標網路分析。

## 完整函式範圍

| 用途 | V131 FLASH | V140 FLASH | 每份 bytes／指令 | stores／calls |
|---|---|---|---|---|
| 五位元組計數 | `[0x57ad8,0x57b28)` | `[0x57c18,0x57c68)` | 80／33 | 0／0 |
| 兩組設定限制 | `[0x55f94,0x5605c)` | `[0x560d4,0x5619c)` | 200／65 | 5／1 |
| 分組計時更新 | `[0x435ce,0x436a8)` | `[0x4365a,0x43734)` | 218／75 | 10／4 |
| 候選碰撞掃描 | `[0x5627a,0x56326)` | `[0x563ba,0x56466)` | 172／56 | 4／1 |

stores 包含保存暫存器的 frame stores。每個範圍都涵蓋普通 RET 之後、仍由分支到達的指令。兩份候選不代表實際 installed provider 已辨識；串接結論均以相符原指令、正常返回及所需 register／frame／pointer 保存條件為前提。

## 計數只納入低 37 bits，結果不保證非零

計數 leaf 依序讀取輸入 offsets **1、2、4、0、3**。offsets 0～3 的四個 byte 組成 held little-endian word，offset 4 的 byte 先 AND 31；再分別走 32 次與 8 次位元計數。第二段最多只有五個非零 bit，因此普通返回值精確等於這些已讀值的低 37-bit popcount，範圍 **0～37**。沒有 frame、store、child call 或本機 null guard。

這是不同時點讀取的五個 byte，未證明它們構成同一個原子快照。第五個 byte 的高三位不影響此計數，也未因此證明來源的高三位為零。

- worker 在五位元組 copy 後呼叫此 leaf，接著以 byte 寫入 `P+301`。
- [B+120 目標](v4160-b1-b120-target-static.zh-TW.md) 對 `N+160` 呼叫同一 leaf，接著以 byte 寫入 `N+129`。

在相符呼叫與保存條件下，這兩處 writer 寫入 **0～37**，byte 截斷不會損失計數。這不是所有 writers 的欄位不變式，也不能推出兩欄位相等、count 為正，或初始 selector 探測只會落在 0～36。原 selector 的 wrapped 高索引探測與這個 popcount 是不同合約，仍保留[既有 selector 邊界](v4160-local-selector-static.zh-TW.md)。

## 設定的兩條 lane 各自取樣

以下 `U16[P+n]` 指該指令當下讀取的無號 halfword，不能合併成整個物件的共同 snapshot。

| 來源最小值 | mode byte | 輸出 halfword |
|---|---:|---:|
| `min(U16[P+470], U16[P+474])` | `P+326` | `P+486` |
| `min(U16[P+466], U16[P+478])` | `P+327` | `P+482` |

每條 lane 獨立套用：mode **恰為 2** 時下限為 **2704**；其他 mode 若值大於 **2120**，才讀取 fresh `U32[P+256]`，且只有 bit 11 清除時才限制為 2120。mode 2 沒有這個 2120 上限，其他 mode 沒有 2704 下限。兩條 lane 可能分別讀到不同的 P+256。

只有計算值與當下輸出欄位不同時才寫入 halfword，並寫 `P+124=1`；兩條 lane 都不會因「沒有改變」而本機清除 P+124。之後呼叫 `0x55dea／0x55f2a(P)`，忽略它的 scalar 回覆，再強制返回 0。這個 child 尚未在本階段展開，因此不能將前述本機寫入公式當成函式返回後的欄位不變式，也未排除 child 保存 P。

此函式直接存取最高為 P+486 的 halfword，需要至少 **488-byte 可讀寫範圍**；這是本機存取需求，不是配置大小或有效期的證明。

## 分組計時：低 byte gate 與完整索引不能混用

入口為完整 U32 索引 I 與 scalar V。先保存並清零控制 word `0x4002420c`、執行 FENCE.I，再檢查 **`low8(I−16) <= 31`**。這只限制 I 的低 byte 為 16～47，沒有將完整 I 限制為 47 以下。通過後以完整 I 計算 `low32(12*I)` 的 arena offset，僅檢查 row 的 occupant word 非零；arena base 本身沒有本機 null guard。任一 gate 失敗，恢復控制 word 並返回 2。

本次串接的 worker 實參另有較強限制：I 來自 **U8[P+40]**，因此該 caller 通過的 I 才是 16～47，對應 task 1 或 2。V 是 **`low32((U16[P+92]<<4)−2)`**，沒有額外截成 halfword；P+92 為 0 時 V 為 `0xfffffffe`。這不能反向套成 generic helper 的入口限制。

通過 gate 後的呼叫與寫入順序為：

1. 以完整 `I>>4` 作 task、`low16(1<<(I&15))` 作 mask，呼叫既有 RAM lookup `0x20000314(task,mask)`，將回傳 L 的**指標值**保存在 S4。
2. L 為零時略過其餘 calls 與 L+8 store，仍恢復控制 word 並返回 **0**。
3. L 非零時呼叫 `0x4358a／0x43616(task,mask)` 清除服務，忽略 status；接著呼叫 fresh clock slot，沒有本機 null guard，實參為當時 ambient registers。
4. 保留 clock scalar，讀取 fresh `U16[Q+8]` 為 K，向算術 helper `0x6df1a／0x6e10a` 傳遞完整 pair **K*V+800** 與 divisor pair **0:1600**。MULHU 與進位保留高 word，沒有先截斷成 32-bit 乘積。
5. 將 opaque A0 回覆加上 held clock。若進位或和大於等於 fresh `U32[Q+4]`，只減一次該 period；最後寫入**原先保留的 L+8**，恢復控制 word，返回 0。

V131 的 arena／clock slot／Q 分別為 `0x2000322c`／`0x200031e0`／`0x20003234`；V140 為 `0x2000327c`／`0x20003230`／`0x20003284`。完整 lookup、clear、first-copy 映射與算術 helper 原 bytes 亦沿用並再次核對。

本階段沒有對新增算術實參域證明完整商值，因此不將 helper 的 A0 回覆直接命名為數學商；單次減 period 也不是一般 modulo 正規化證明。L 在 clear、clock 與算術呼叫之後沒有重新取得或驗證，保留指標值不能證明節點仍存活。正常返回 0 不保證 lookup 命中、清除成功、timer 改寫成功或實體計時進展。

## 候選掃描：返回值不是選中的候選編號

B 為 `0x200033b8／0x20003408`。若 fresh `U16[B+180]<=1`，直接走普通 epilogue，A0 仍為入口 P，沒有存取 P 的物件欄位。

否則計算 `U16[P+482]+U16[P+486]+625`，範圍 625～131695；與 fresh 無號 halfword K 相乘，以完整高低 pair 與 divisor pair **0:1000000** 呼叫同一算術 helper。這裡 MULHSU 的第一操作數為非負，因此乘積高 word 與無號乘法一致。helper 回覆 D 留在 A0，之後本機路徑都不再定義 A0，普通返回值為 **D**，不是 candidate 或成功 status。

呼叫後才讀取 byte `P+85` 與 captured head `U32[B+156]`。候選 i 從 1 開始，條件為無號 **`i < U32(P+85−1)`**：

- P+85 為 1 或 2 時不掃描。
- P+85 為 3～255 時，名義上最多 P+85−2 個候選。
- P+85 為 **0** 時 bound 為 `0xffffffff`，若每次內層都能完成，i 可到 `0xfffffffe`；不能當成「沒有候選」或短迴圈。

每個候選先讀 fresh P+144，得到 `C=low32(P+144+40*i)`，再從同一 captured head 開始走鏈表。對自物件的分支使用 fresh P+0；鏈表後繼也是 fresh node+0，沒有有限性或無環證明。

比較值在**每個候選起點**設為 `0xffffffff`，不是每個節點都重設。node+140 與 fresh P+140 相等時，才改為 node+144 與 C 的 unsigned 絕對差；不相等時沿用先前比較值。沿用值必然已通過先前的 `metric >= D`，因此不會因這個不匹配節點而拒絕候選。僅當比較值嚴格小於 D 才遞增 i、重啟下一候選。

走到 null 後以 halfword 寫 `P+86=low16(i)`，這是唯一的非 frame 直接 store。count gate、初始 bound 不成立或候選全部被拒絕的返回路徑都不會本機寫 P+86；未知 callee／alias 仍可能改變欄位，不能聲稱整段呼叫保持 P+86 不變。此函式直接 P extent 同為 488 bytes，foreign node 的直接讀取至少需要 148 bytes，但都未證明實際配置與有效期。

## 驗證與剩餘工作

```powershell
python analysis/check_v4160_b1_worker_leaves_static.py
python -O analysis/check_v4160_b1_worker_leaves_static.py
```

checker 重跑祖先驗證、原始 APP／SDK／兩份候選身份、strict sparse HEX 全範圍比對與固定 ledger。每份 CFG 的 edge 數依序為 **36／76／79／63**，每條 edge 都有語法上的 entry→edge→RET walk；這不是條件可滿足性、可執行測資或真實執行頻率的證明。計數 leaf 有兩個各七指令的循環 SCC，候選掃描有一個 22 指令 SCC；其餘兩個函式的本機 CFG 無環，callee 是否正常返回另論。

負向檢查逐一修改 **458 個指令位置**，另外修改 **46 個 typed-load funct3**，均須被拒絕。封閉純整數檢查包括 262,144 組重複 halfword word 家族與第五 byte 取樣、全部 256 個第五 byte、524,288 組 clamp 代表條件、256 個 caller byte indices 及候選 bound。這些不是 37-bit 輸入的窮舉，也不是目標執行或可變記憶體模擬。

仍需展開 `0x55dea／0x55f2a`、`0x5d006／0x5d14e` 等巢狀服務，查明來源欄位 writers、實際 clock／arena／record provider 綁定、clear 後節點有效期，以及完整消費與釋放順序。此階段新增的是條件性的原指令合約驗證，**沒有增加既有 C 重建分子或更新 95.75% 的靜態重建快照**，也未產生經實機驗證的完整可用韌體。
