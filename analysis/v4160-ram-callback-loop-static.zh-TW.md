# v4.1.60：callback 更新迴圈、回繞算術與四個後續出口

接續 [service pointer 的條件性來源](v4160-service-provider-link-static.zh-TW.md)，本輪把 callback prefix 留下的三個 cuts 接上更新段。新增驗證兩份 resident **候選**共 404 bytes／132 指令；結合先前 prefix 共 676 bytes／220 指令。這些仍是有界片段，不是完整 callback。

主要結果：合併的 conditional-normal-return CFG，每份有一個精確的 **41-node strongly connected component**，其中包含更新欄位、direct／indirect calls、fresh reads 與 signed-negative 回跳。這證明原編碼存在局部循環路徑，不代表已觀察實際執行、能到達該路徑或可證明終止。

全程只讀原 bytes、核對 operands／hash／CFG／SCC，並做主機端有限位寬算術。沒有執行或模擬目標 ISA、RAM、frame、copy、callback、resident、MMIO 或裝置。既有 C 重建 bytes 未增加。

## 新增片段與座標

| 片段 | V1.31 FLASH，end-exclusive | V1.40 FLASH，end-exclusive | 每份 bytes／指令 |
|---|---|---|---:|
| completion | `0x4102c..0x41048` | `0x4106c..0x41088` | 28／9 |
| 第二個 threshold | `0x41064..0x4108a` | `0x410a4..0x410ca` | 38／11 |
| iteration header | `0x4108a..0x410ac` | `0x410ca..0x410ec` | 34／11 |
| update | `0x410ac..0x410fc` | `0x410ec..0x4113c` | 80／25 |
| field136 的 wrap 修正 | `0x410fc..0x41104` | `0x4113c..0x41144` | 8／4 |
| 兩個 update fixups | `0x41138..0x41146` | `0x41178..0x41186` | 14／6 |

每份新增 202 bytes／66 指令，合計十二個片段。檢查器釘住每條 operands 與每片 SHA-256，並在原 FLASH 與 first-copy RAM 座標分別核對 PC-relative targets。兩份 callback entry 均為 `0x20000d50`。

APP 仍是 76,800 bytes、base `0x8000`、SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。既有 APP／候選／SDK／sparse／指令格式來源合約遞迴重驗；先前的 service publication 仍保留 copy 與實際綁定前提。

## 第二個 threshold 也有回繞，但溢位不一定得到零

進入第二個 threshold 前，若第二次 reply 小於當次 field136，原指令先讀 fresh `[then-live S1+4]`，將 `reply+(wrap-field136)` 以 U32 算術形成 A0；另一支已做 `reply-field136`。這不是跨呼叫不變的 snapshot。

threshold 使用原 QK.C.LHU encodings `0x3c7e` 與 `0x249a`：

```text
a = fresh U16[then-live S0+62]
b = fresh U16[then-live S1+8]
N = (8*a*b + 400) modulo 2^32
Q = N unsigned_div 800
if unsigned Q < A0: leave to cut
```

`a<<3` 自身可放入 U32；乘法與後續加法必須保留回繞。只有 `a*b <= 536870861` 時，才可使用不回繞的 `(a*b+50)//100`。在整個 U16 domain，Q 的上界為 `5368709`。

| a | b | 回繞後 N | 原算術 Q | 不回繞 quotient |
|---:|---:|---:|---:|---:|
| 16384 | 32768 | 400 | 0 | 5368709 |
| 65535 | 65535 | 4293919128 | 5367398 | 42948362 |

這些是主機端算術反例，不證明實際 object 欄位可達該值。它們也顯示第二個 threshold 的溢位不能一律簡化成零。

## iteration 的 fresh reads 與 call boundaries

threshold 沒有選擇離開時，原指令先形成 S6=`999999`、S5=`1000000`，再進 iteration header：

1. fresh U16 `[then-live S0+64]` 加 1，以 SH 寫回，`65535→0`。
2. fresh byte `[then-live S0+320]` 決定是否以 A0=S0 呼叫 mapped local target `0x200014c6`。
3. 再設 A0=then-live S0，呼叫另一個 AUIPC／JALR target；V1.31 為 `0x56972`，V1.40 為 `0x56ab2`。這些是 mapped PC 計算結果，並不推定函式語意。
4. 若該 call 正常返回非零，走外部 cut；若返回零，進入 update。

兩個 callees 的副作用與正常返回均未知。S0／S1／S2／S4／S5／S6、保存 frame 與相關值是否仍符合原假設，必須另列條件，不能以 ABI 名稱自動視為成立。

## word144 的更新只做一次條件減法

update 重新載入 A=`U32[then-live S0+144]`、B=`U32[then-live S0+140]`、W=`U32[then-live S1+4]`，然後：

```text
C = (A+B) modulo 2^32
if unsigned C < A or unsigned C >= W:
    T = (C-W) modulo 2^32
else:
    T = C
```

接著 fresh 讀 byte31 與 halfword134，將 T 寫回 word144，再把 byte31 加 1、以 QK.C.SB 寫回，`255→0`；factor halfword `[then-live S1+8]` 也是重新讀取。

沒有輸入界線就不能把 T 改寫成一般 `(A+B)%W`。例如 A=B=100、W=7，原條件減法得到 193，數學 modulo 得 4；A=`0xfffffff0`、B=`0x30`、W=256，原回繞後修正得到 `0xffffff20`，數學 modulo 得 32。W=0 也沒有 local reject。

## 後半算術與真實編碼回跳

更新後，指令以 fresh halfword134 與 fresh factor 相乘，加 **then-live S6**、除以 **then-live S5**。將它們解讀成 `+999999`、`/1000000`，需要前述 constants 跨未知 callees 保留；若未保留，不能套用該常數公式或 quotient 界線。

原條件修正接著使用 fresh service pointer call。即使 nominal word 與之前相同，每次 target load、wrap read、object read 都是分開的存取，不能認成同一份保存值。返回後有另一個條件性 fresh wrap-word 修正，再做 U32 subtraction；結果 A0 以 signed 比較：

- signed A0<0：`0x410f6→0x4108a`，V1.40 是 `0x41136→0x410ca`，回到 iteration header。
- 否則：`0x410fa→0x4102c`，V1.40 對應 +`0x40`，進 completion。

completion 另做 halfword64 增加、清 byte31，再依 fresh byte320 選擇 local call 或其他 continuation。它不在該 41-node SCC 內。

SCC 精確包含 V1.31 `0x4108a..0x410fa` 內的所有 instruction starts，加上 `0x41138..0x41146` 的 fixups；範圍均 end-exclusive，**不包含 `0x410fa` 本身**。V1.40 對應 +`0x40`。未知 call targets 與 omitted continuations 不納入這個 local SCC 結論。

## 四個 cuts、重播與剩餘工作

| RAM cut | V1.31 FLASH | V1.40 FLASH |
|---|---|---|
| `0x20000e94` | `0x41104` | `0x41144` |
| `0x20000ed6` | `0x41146` | `0x41186` |
| `0x20000eda` | `0x4114a` | `0x4118a` |
| `0x20001092` | `0x41302` | `0x41342` |

[檢查器](check_v4160_ram_callback_loop_static.py) 與 [完整 ledger](v4160-ram-callback-loop-static.json)：

```text
python analysis/check_v4160_ram_callback_loop_static.py
python -O analysis/check_v4160_ram_callback_loop_static.py
```

一般及 `-O` 模式逐 byte 重現 ledger，核對原 operands／hash、雙座標 targets、prefix joins、每份精確 41-node SCC 與四個 cuts、關鍵 QK encodings，以及 56 個指定 operand mutation。主機算術另檢查全部 65,536 個 halfword increment 值與 max-factor threshold row、256 個 byte increment 值及上述反例；沒有執行 target loop，也沒有宣稱窮舉所有輸入組合。

接續仍需展開四個 cuts、被呼叫的本機函式與 epilogue，完成整個 callback；完整 config gates、copy 合約、實際 fields／writers／登錄順序、frame 保存期與 installed provider 綁定也尚未解除。counter 增加與 local CFG 存在循環，都不能證明實際迴圈終止或裝置行為。
