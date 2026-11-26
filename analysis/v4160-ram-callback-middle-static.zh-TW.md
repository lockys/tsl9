# v4.1.60：callback 中段、fresh-target 等待循環與尾段接點

承接 [callback 出口與獨立尾段](v4160-ram-callback-exits-static.zh-TW.md)，本輪展開 entry graph 留下的 `0x20000ee8` cut。新增兩份 resident **候選**共 436 bytes／136 指令，將先前獨立的 final tail 接入同一個 conditional-normal-return CFG。

每份選定 graph 現有 242 個 instruction nodes，均可由原 entry 做局部圖走訪；共有精確的 41-node 更新 SCC 與 3-node 等待 SCC，只剩 `0x20000fb2` 一個 fallthrough cut。這是編碼與條件控制流的接點，不證明實際值可達、callback 曾執行、callee 正常返回或迴圈終止。

只讀原 bytes、核對 operands／hash／CFG／SCC，另做主機端有限位寬算術；未執行或模擬目標 ISA、RAM／frame、callback、resident、MMIO、copy 或裝置。既有 C 重建 bytes 未增加。

## 新增八個有界片段

| 片段 | V1.31 FLASH，end-exclusive | V1.40 FLASH，end-exclusive | 每份 bytes／指令 |
|---|---|---|---:|
| 中段算術與 optional helper | `0x41158..0x411fa` | `0x41198..0x4123a` | 162／50 |
| field136 差值修正 | `0x41316..0x41320` | `0x41356..0x41360` | 10／3 |
| 取樣與等待 | `0x411fa..0x41222` | `0x4123a..0x41262` | 40／12 |
| 等待後差值修正 | `0x41320..0x41326` | `0x41360..0x41366` | 6／3 |

本輪每份新增 218 bytes／68 指令；連同先前共選定 1452 bytes／484 指令，仍不是完整 callback。全部原 operands 與片段 SHA-256 均核對，PC-relative targets 在 FLASH／first-copy RAM 兩種座標分別驗證。

APP 仍為 76,800 bytes、base `0x8000`、SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。既有候選／SDK／sparse／指令格式來源合約也遞迴重驗。

## field136 與 word144：重新取樣及一次修正

中段起點重新讀 b=`U16[then-live S1+8]`、a=`U16[then-live S0+134]`，並形成：

```text
Q = ((a*b+999999) modulo 2^32) unsigned_div 1000000
V = fresh U32[then-live S0+144]
SB0 [then-live S0+54]
W = fresh U32[then-live S1+4]
field136 = (V-Q) modulo 2^32        if unsigned V>=Q
           (V+W-Q) modulo 2^32      otherwise
```

這裡的 Q 與先前 prefix 的乘加形式相同，仍需保留回繞，不能直接換成一般 ceiling。修正分支 `0x41316→0x41188` 在原比較之後匯流，不自行構成迴圈。

之後 fresh 讀 B=`U32[S0+140]`，與**先前已載入的 V** 相加，做一次條件減法：C=low32(B+V)，若 C<B 或 C>=W 則 T=low32(C-W)，否則 T=C。S2=T、S6=0。

接著 fresh 讀 halfword `[S0+32]`，才把 T 寫回 word144。這個 halfword 為零便跳過 optional helper block。以上 store／load 依原順序描述，沒有排除物件與 globals 的 alias，也不把一次 W 修正當成任意輸入的 modulo。

## halfword32／34／36 與 helper 實參

halfword32 非零時，原 QK encodings 對應：

| raw halfword | 原存取 |
|---|---|
| `0x301e` | unsigned load `[S0+32]` |
| `0x305a` | unsigned load `[S0+36]` |
| `0x303a` | unsigned load `[S0+34]` |
| `0xb056` | halfword store 至 `[S0+36]` |
| `0xb03e` | halfword store 至 `[S0+34]` |

令 R 為已讀 halfword32、c=`U16[S0+64]`、oldc=`U16[S0+36]`、oldp=`U16[S0+34]`：

```text
SH c,[S0+36]                      // 先寫入新 counter
D = (c-oldc) modulo 2^32          // register subtraction 仍是 RV32
p = (R*D+oldp) modulo 65536
A0 = p*b                         // 兩者均 U16，乘積可放 U32
SH p,[S0+34]
A1 = 0
A2 = 1000000
A3 = 0
```

linked helper 的 mapped target 為 V1.31 `0x6df1a`／V1.40 `0x6e10a`。這組 word-pair 形狀的實參不能單獨證明 64-bit division、返回 ABI 或 copy／ownership 語意。

## helper 返回後只用 A0 作 zero guard

原指令只測返回 A0 是否為零，並沒有把 A1 納入這個判定。譬如返回 `(A0,A1)=(0,1)`，仍會跳過後續加法與 word144 store。

若 A0 非零，且未知 helper 保留所需 S0／S2／S5／S6 等狀態，後續 operand pattern 為：

```text
lo = (returnA0 + then-live S2) modulo 2^32
carry = unsigned(lo < oldS2)
hi = (returnA1 + carry) modulo 2^32
result = (lo-then-live S5) modulo 2^32
         if hi != then-live S6 or unsigned lo >= then-live S5
         else lo
SW result,[then-live S0+144]
```

S6 在 helper 前設為零，但跨 call 的保存仍是前提。這是 carry-like 指令樣式，不是已證明的任意 64-bit modulo。以保留 S2=0、S5=7、S6=0，返回 pair=(1,1) 為例，原修正值是 `0xfffffffa`，而數學 `(2^32+1)%7` 是 5。

## 三個節點的等待 SCC

接下來先 fresh load service target、call，將 seed reply 放入 S2。等待 SCC **不包含 seed call 或 seed 保存指令**，精確只有：

```text
V1.31 0x41202: fresh LW A5,[then-live S4+480]
      0x41206: linked call A5
      0x41208: BEQ returned A0,then-live S2,0x41202
```

V1.40 對應 +`0x40`，service delta 為 560。若 S4 保留原基址，nominal service words 仍為 `0x200031e0`／`0x20003230`，但每次都 fresh reload target；不能假定 target 相同、reply 單調或會改變。

相等便重複；不同才離開。這個比較需要 S2 seed 跨 call 保留，並沒有 timeout 或 retry bound。先前條件性的 service publication／reader 分析，仍不足以把這些 premises 認定為實際 installed 行為。

## 等待結束後的 snapshot，與 final-tail 接點

離開等待 SCC 後，原指令再次 fresh load target，並在**下一處 call 前**讀 field136 到 S2。它是片段中的第三個靜態 call site；等待內的 call 可重複，動態呼叫次數並非固定三次。這與早期 prefix 的 call 後 field136 load 不同；這份 snapshot 也需要 callee 保存 S2。

若 unsigned S2<返回 A0，另一個 fixup fresh load `[then-live S1+4]`，加到 S2，跳到原比較之後。它不重試該 BLTU，也不是一般 modulo。

匯流後做 A0=low32(S2-returnA0)：

- A0=0：原 BEQ 從 `0x4121e`／`0x4125e` 接到先前 final tail `0x41342`／`0x41382`，mapped RAM `0x200010d2`。
- A0≠0：落到唯一仍未展開的 cut `0x41222`／`0x41262`，mapped RAM `0x20000fb2`。

因此先前獨立 root 的 28 個 tail nodes，現在已在 conditional-normal-return entry graph 中接通。這仍不證明寄存器值實際滿足分支或未知 callees 正常返回。

## 重播與下一個邊界

[檢查器](check_v4160_ram_callback_middle_static.py) 與 [完整 ledger](v4160-ram-callback-middle-static.json)：

```text
python analysis/check_v4160_ram_callback_middle_static.py
python -O analysis/check_v4160_ram_callback_middle_static.py
```

一般與 `-O` 模式逐 byte 重現 ledger，核對全部 operands／hash、雙座標 targets、entry 到 final tail 的接點、精確 3／41-node SCCs 及唯一 cut，並拒絕 48 個指定 operand mutations。主機算術另用 65,536 個 current counter 與三個 old-counter 邊界值，共 196,608 cases，核對低 16-bit 代數與乘積界線；沒有宣稱窮舉全部 field 組合，也沒有執行 helper／wait loop。

接續仍需展開 `0x41222`／`0x41262` 與其後尚未驗證的 MULHU、中段分支及完整 callback closure；所有 callees、config gates／copy 合約、登錄順序、實際 provider 與物件／frame 保存期也仍待釐清。
