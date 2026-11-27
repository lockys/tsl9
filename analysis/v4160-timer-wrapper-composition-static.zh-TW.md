# v4.1.60：timer、lookup、wrapper 與除數1600的條件性合約

本階段重用兩版既有完整函式，新增的是 **50-node 選定商值路徑及跨函式保存合約**。沒有新計入的原指令 bytes，也不增加既有 C 重建覆蓋率。

| 重用本體 | V1.31／V1.40 entry | 每版 bytes |
|---|---|---:|
| timer service | `43728/437b4` | 332 |
| RAM timer lookup | `20000314`，來源 `40584/405c4` | 30 |
| event wrapper | `43932/439be` | 118 |
| 完整算術 helper | `6df1a/6e10a` | 914 |
| 算術 table prefix | helper entry+`a42` | 16 |

[完整 ledger](v4160-timer-wrapper-composition-static.json) 保存重用函式身分、selected operands／CFG、16條 service walks、數值公式、指標保存及來源前提。全程離線讀檔、圖與 Euclidean scalar arithmetic，沒有執行或模擬 target ISA、timer、lookup、算術 helper、callback、MMIO、裝置或 mutable register／RAM machine。

## 除數1600：從未釐清的回覆收斂為選定域的商值

沿用 [尾段 wrapper 證據](v4160-comparator-tail-static.zh-TW.md)，目前 callback 提供 K=`U16[N′+52]`、`U16[N′+70]` 或兩者的完整 word 加總，因此 K∈0..131070。算術請求的 numerator 是 MUL／MULHU／add800／carry 形成的完整64位 N=H×K+800，H 為 fresh U16；denominator pair 為 A3:A2=`0:1600`。

```text
800 <= N <= 8,589,673,250 < 2^33
entry A1 = N highword ∈ {0,1} < 1600
```

matching helper／table、普通 RV32 DIVU／REMU／shift／乘法語義、有效 table access 及無 code／GPR 干擾前提下，選定路徑恰為50條指令，封閉且無環，唯一退出為 entry+`ba`。其中沒有 stores、calls 或 frame，也不改 RA、SP、S registers。

分支依次由以下事實決定：高 denominator=0；numerator highword<1600；1600<65536；255<1600；normalization shift 非零；兩個 quotient-correction products 為零。

1600=`640`，table index=`1600>>8`=6，原 byte=3，故 normalization shift=32-(8+3)=21。normalized denominator=`c8000000`，其16位 digits 是 **51200、0**；兩個低 digit 乘積因此為零，不進 correction blocks。

純 Euclidean 分解如下，沒有執行目標函式：

```text
U = N >> 11
L = (N mod 2048) << 21
q1 = U div 51200
r1 = U mod 51200
m = (r1 << 16) OR (L >> 16)
  = 32 × (N mod 104857600)
q0 = m div 51200
Q = (q1 << 16) OR q0 = N div 1600
```

q1<=81、q0<=65535，m<51200×65536<2³²，這些合併沒有 word overflow；OR 的兩部分不重疊。最後明確 `LI A1,0`。

因此這個選定域的實際返回為 **A0=floor((H×K+800)/1600)，範圍0..5,368,545；A1=0**。A1 不是 remainder；A6 恰為 `(N mod1600)<<21` 的 normalized residue，也不推論為一般 remainder ABI。

這沒有證明任意 U32 K、其他 denominator、其他 numerator highword 或所有 correction branches 的通用除法合約。完整914-byte結構證據及其他既有 denominator=1,000,000 的49-node證據不能直接代換這個50-node路徑。

## 三個 H 為同址的不同 fresh observations

timer 的兩次算術請求與外層 wrapper 的一次請求，都使用 `2000323c/2000328c` 的 U16，但分別位於：

1. timer admission calculation 前的 H0。
2. clock callback 返回後重新讀取的 H1。
3. wrapper 第二次 lookup 返回後重新讀取的 H2。

三個值不能合併 snapshot，也不推定固定比例、物理時間單位或一致設定。以上 domain／preservation 前提保持時，各自有 Qi=floor((Hi×K+800)/1600)。

timer 首先檢查完整 unsigned task<fresh U8[C+1]，以及 fresh clock-service pointer 非零；之後比較 Q0 是否<=`(先前捕捉的 W0-30000000)mod2³²`，才會呼叫 clock。clock 的實際回覆 R 與 Q1 相加後，只在 carry 或 sum>=另一個 fresh W1 時減 W1 一次；這不是任意範圍的 modulo 或一般時間校正證明。

clock、failure hook、allocator fallback 的實際綁定、副作用、是否保存指標及是否返回仍未封閉。算術 leaf 的局部 no-S／SP／RA-write 性質可縮小保存義務，但不能替未知 callbacks 保證整條鏈完成。

## Timer 回覆不是 node pointer，wrapper 回覆也不是建立成功證明

完整 timer 的所有局部正常返回，在最後 A0 definitions 恰為 `LI0` 或 `LI1`；不存在把新 node pointer 作為最終回覆的路徑。

- task／service／threshold 拒絕、allocation failure 路徑返回0。allocation failure 可先呼叫 fresh failure hook，再返回0。
- 更新既有 node，或配置並完成初始化新 node 的路徑返回1。查找／append／nested callees 仍可能不返回。

wrapper 不檢查第一次 timer 回覆，恢復原 task、event 後，再呼叫 RAM `20000314`。

matching lookup 沿 fresh head／node+12 遍歷，以完整 task 比較 node+0 byte、完整 event 比較 node+2 halfword；不讀 A2，也不寫 S／SP／RA，沒有 frame、store 或 call。因而第二次呼叫 then-live A2 沒有重新設定，在 matching lookup 下不影響 key；未知 installed provider 仍可能觀察它。

第二次 lookup 為 null 時，wrapper 返回8；非 null 時，wrapper 把第三次算術回覆寫入 Rnode+4，之後返回0。這與第一次 service 的0／1、算術商值或事件送達是不同資訊。

形式上的相反案例包括：第一次 timer 因 gate 返回0，第二次 lookup 卻找到既有匹配 node，wrapper 仍返回0。這不是實機可達性或已觀察到的執行紀錄。

## Event width：建立時截為16位，查詢時比較完整值

被 admission 接受的 task 至多254，可無損存入 byte；但建立 node 時 event 存為 low16，lookup 卻比較完整 incoming event，沒有先截斷。

一般參數例子 event=65536：在其餘成功／原先空且保持的鏈表前提下，timer 可以建立 event欄位0的新 node並返回1；wrapper以完整65536查詢，就不會匹配該 node，可返回8。這是 API 寬度的形式案例，沒有推定它能從目前入口到達。

目前 N+136 callback 的 event 明確為十進位16，沒有這個截斷損失；仍需保留 task／event、head、next、node生命週期及實際綁定前提。

## 同一個 node+4：先清零，再寫入第三次商值

新 node 的 allocator 請求為16 bytes，tag=`ff00|tasklow8`。初始化欄位為：task+0、flag1+1、eventlow16+2、word4=0、deadline+8、next0+12。

原指令先將 pointer 寫入 head 或尾端 node+12，**之後才初始化新 node 的欄位**。本機控制欄位操作並不能證明物理原子性或杜絕外部讀取部分初始化物件。

在 matching providers、有限有效鏈表、原 miss 事實仍保持、fresh nonalias 16-byte node、keys／head／next／生命週期保持及 event=16 前提下，wrapper 的第二次 lookup 才可確定找到這個 P。於是其局部效果可串為：

```text
timer:   P+4 = 0
wrapper: P+4 = floor((H2×K+800)/1600)
```

結果仍可能是0，不保證正值。wrapper 自己的這個 word store 不覆寫 P+0／1／2／8／12；nested callees、控制地址 alias 或其他 writers 的效果仍需另外限制。

既有匹配 node 的情況則是 timer 更新 P+8，wrapper 後續更新 P+4；若 key／links 被改、node 被釋放重用或出現新的較早匹配 node，不能宣稱兩次 lookup 指向同一物件。

外層及 timer 內層各自 capture／clear／FENCE.I／restore 自己的控制 word snapshot。不能從本機寫零推導內層必讀零、IRQ 關閉、coherence 或 atomic restore，也不能由 wrapper0 推論後續 poster／async 工作完成。

## 重播

[Checker](check_v4160_timer_wrapper_composition_static.py) 驗證100次 selected-instruction、32次 table-byte、40次串接 operands 變異；另檢查327,680組 H/K、7,651組 quotient/remainder boundaries、65,536組 task/count 及16條 service walks。純 scalar samples 支持邊界；完整商值結論來自上述 Euclidean identities，沒有宣稱窮舉所有 H/K 組合或執行 ISA。

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_timer_wrapper_composition_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_timer_wrapper_composition_static.py
```

一般與 `-O` 都必須精確重播 ledger。後續仍需釐清 clock／failure hook／allocator fallback 的實際綁定與副作用，以及 global／list／key／生命週期保存、硬體控制與事件效果。
