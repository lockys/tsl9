# v4.1.60：分開的 context 入口與候選 callback 的 frame+0 來源

承接 [IRQ setup 與舊 stackword 候選](v4160-irq-setup-stack-sources-static.zh-TW.md)，本階段確認 `0x8448` 與 `0x8498` 是兩個獨立本體；後者自己不填 frame+0，但透過 GP+384 呼叫的 resident **候選**有一條路徑會把當時的 CSR `0x341` 存入該 word。這關閉了一個條件性的 frame-word 來源，沒有證明實際 provider、硬體 trap 路由或與 `0x12c24` 的共同 frame。

只解析原 bytes、核對 operands／局部 CFG／映射／欄位算術，未執行或模擬 ISA、CSR、MRET／ECALL、frame／RAM／copy、resident、callback 或裝置。[檢查器](check_v4160_context_callback_frame_static.py) 與 [完整 ledger](v4160-context-callback-frame-static.json)。既有 C 重建 bytes／覆蓋率不增加。

## 範圍與固定身分

| 類別 | 原始半開區間 | bytes／指令／stores |
|---|---|---:|
| 完整 APP restore | `0x8448..0x8496` | 78／35／0 |
| 完整 APP save/call/reload | `0x8498..0x851e` | 134／64／29 |
| APP publication prefix | `0x199e2..0x199f0` | 14／5／2 |
| APP setup prefix | `0x8e88..0x8eac` | 36／13／3 |
| V1.31 候選 callback | FLASH `0x430a4..0x430dc` → RAM `0x20002e34..0x20002e6c` | 56／16／3 |
| V1.31 候選 gateway | FLASH `0x43098..0x430a0` → RAM `0x20002e28..0x20002e30` | 8／2／0 |
| V1.40 候選 callback | FLASH `0x43130..0x43168` → RAM `0x20002e80..0x20002eb8` | 56／16／3 |
| V1.40 候選 gateway | FLASH `0x43124..0x4312c` → RAM `0x20002e74..0x20002e7c` | 8／2／0 |

APP 完整兩個本體合計 **212 bytes／99 指令**，另外兩個明示 prefix 合計 **50 bytes／18 指令**。兩版 reference 的完整四個本體合計 **128 bytes／36 指令**。不把 prefixes 視為完整初始化；離開 prefix 的接續點仍列於 ledger。

每個本體／prefix 逐條核對 operands 與完整 bytes SHA-256。候選 callback／gateway 同時在 FLASH 及條件性 RAM 座標解碼，分別核對 PC-relative targets，沒有只把 FLASH target 原封不動當成 RAM target。

APP 為 76,800 bytes、base `0x8000`，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`；既有 SDK、兩份 carrier 身分、sparse 覆蓋與前階段來源鏈亦重算。first-copy 中這些 bytes 的覆蓋不等於完整 boot 已證，既有 second-copy 四個缺 bytes 的界線保留。

## 兩個 APP 入口：相同 GPR 欄位，不同返回流程

令 F 為當時 frame base。以下 29 個 registers 依序佔 F+4、+8、…、+116：

```text
RA, TP, T0,T1,T2, S0,S1, A0,A1,A2,A3,A4,A5,A6,A7,
S2,S3,S4,S5,S6,S7,S8,S9,S10,S11, T3,T4,T5,T6
```

不包括 GP；SP 用明示加減 128 處理，不能因此推論硬體或未知 callee 保存 GP／SP。

`0x8448` 不配置 frame，先以 A1=`0x20` 對 CSR `0x804` 執行 CSRRS，再讀 U32[F+0] 寫入 CSR `0x341`（MEPC operand），然後從上述 29 個欄位載回 GPR、SP+=128，於 `0x8492` MRET。沒有子呼叫，也沒有建立這份 frame 或驗證其內容有效的指令。

`0x8498` 則先 SP−=128，以新 F 保存上述 29 個 GPR，隨後：

```text
A1=then-live GP+384
A0=fresh U32[A1]
84da JALR A0      （有效 target=raw A0 &~1，link=84de）
```

沒有 local null guard。只有 callback 普通返回、必要 SP／frame 保存時，才繼續 `0x84de` 的 29 個 reload、SP+=128、MRET。保存的 A0 會覆蓋 callback scalar 回覆，沒有用該回覆判斷成功。

APP save 本體只寫 F+4..119，**未填 F+0..3、F+120..127**，也沒有明示讀寫 MEPC。因此不能把它自己當成 `0x8448` 所需完整 frame 的建立者；兩個 MRET 本體也不是因相鄰就會自動接續。

## GP+384 callback 的 APP publication 來源

已固定的初始化序列以 `0x9268 → 0x8e88` 進入所選 setup prefix。它提出 fresh fill 請求 `(0x2000b18c,0,2124)`；在正常返回及所需 context 保存前提下，於 `0x8ea8` 呼叫 `0x199e2`。

後者首 14 bytes 依序：LUI A5=`0x20000000`、LW A5,+8、配置 96-byte frame、保存 S0、SW A5 至 GP+384。其間沒有 call 或其他 A5 重定義，所以可固定「讀取 RAM JT[2] word，再將同一 pointer word 寫入 GP+384」的本機關係。名義 GP=`0x20004000` 時，slot 地址是 `0x20004180`。

這不證明整個初始化完成、GP 一直維持名義值、slot 沒有被其他 writer 改動或 callback 真正被呼叫。SDK header 的 `LLE_IRQLibHandler` alias 使用 `BLE_LIB_RAM_JT(2)`；名稱只是固定來源對照，不提供實際 installed 身分或呼叫成功證據。

## 候選 JT[2]、第一段 copy 與 flag 初值界線

兩個候選 initializer 的完整原指令仍被核對；各自向 `[0x20000008]` 寫入上述 RAM callback 地址。

| 候選 | first-copy source → destination | end-exclusive | JT2 runtime | flag 地址 |
|---|---|---|---|---|
| V1.31 | `0x402b0 → 0x20000040` | `0x20002e74` | `0x20002e34` | `0x20002efc` |
| V1.40 | `0x402f0 → 0x20000040` | `0x20002ec0` | `0x20002e80` | `0x20002f4c` |

兩版 callback 及其前 12-byte 位置上的 8-byte gateway 全在 first-copy 要求範圍內。initializer 的 pointer publication 仍先於 code copy，不能把寫入 pointer 當成程式碼當時已就緒。

flag 位於 first-copy end 之外，不能從 callback code 映射推出初值。既有 startup zero request 分別為 `[0x20002ef8,0x20003618)`、`[0x20002f48,0x20003668)`，確實包含各自 flag；只有零化完成、來源匹配且後續保存等前提成立時，才可連到初始零值。未宣稱 full boot、flag 的真實狀態或所有寫入者已閉合。

## callback 的兩條完整本機路徑

callback 不配置自己的 frame。它 fresh signed LB flag，接著先 SB0 清同址，再依讀值是否為零分支；256 個 byte 的 signed／unsigned 零判定相同，但不因此加入原子性或 IRQ 同步保證。

**讀到零：** 保存 callback caller 的 RA 至 F+120，呼叫直接 resident callee，再讀回該 RA、普通 RET。若實際 callback 來自 `0x8498`，且需要的 SP／frame／saved word 保持，則返回 `0x84de`，使用 APP 的 inline reload 序列。此路徑不寫 F+0，也不需要用它返回。

**讀到非零：** 先讀 CSR `0x341` 到 A1，再 SW 至 F+0；形成 runtime gateway 地址，寫到 CSR `0x341`；呼叫另一個直接 callee，然後 MRET。這條路沒有普通 RET 邊，不能視為一定回到 `0x84de`。

| 候選 | 非零路徑直接 callee | 零路徑直接 callee | gateway |
|---|---|---|---|
| V1.31 | `0x20002b4c` | `0x2000298e` | `0x20002e28` |
| V1.40 | `0x20002b98` | `0x200029da` | `0x20002e74` |

如果實際綁定確實符合候選、初始化／copy／pointer 保存成立，而且 callback 的 SP／frame 有效，則非零路徑能在 APP save 預留的 F+0 寫入當時 MEPC operand。原有 29 組 GPR fields 加上這個 word，涵蓋 `0x8448` 的全部明示 frame reads；這是欄位契約的條件性相容，沒有建立實際控制轉移。

上述 resident callees 本批仍是未知邊界；它們可能影響 SP、GP、frame、CSR 或其他資料。因此 callback 寫入 gateway MEPC operand，不等於 MRET 時該值必定保持。

## gateway 的 ECALL 與三個不同向量入口

兩版 gateway 都是直接呼叫 runtime `0x200007a0`，正常返回後 ECALL。本階段不執行 service 或 ECALL，也沒有用一般平台慣例自行推斷其 trap 會到哪裡。

| target word | APP raw word 位置 | 相對名義 base `0x8038` 的 word index |
|---|---|---|
| `0x8448` | `0x804c`、`0x8058` | 5、8 |
| `0x8498` | `0x8138` | 64 |
| `0x12c24` | `0x80c8` | 36 |

全 APP 逐 byte 搜尋上述絕對 little-endian words，位置如表；逐半字搜尋 JAL／C.J／C.JAL 原始編碼候選，沒有直達這三個入口的命中。這個語法域不涵蓋所有 indirect edges、任意常數／pointer 流、resident 或其他映像，也不把原始候選當成已證可達指令。

因此目前仍沒有證據把 `0x12c24` 轉交給這兩個 context 本體，也不能把 gateway ECALL 與 `0x8448`、或名義索引 36 與 64 自動連成實際 IRQ frame。

## 重播與後續

```text
python analysis/check_v4160_context_callback_frame_static.py
python -O analysis/check_v4160_context_callback_frame_static.py
```

一般／`-O` 皆需精確重播 ledger，核對 29 組 GPR 欄位、frame+0／尾部缺口、256 個 signed-byte 零判定，以及 20 個指定原指令 mutation。FLASH／RAM PC-relative targets、完整 initializer publication、來源身分與既有 sparse 界線同步重算。

下一步可展開 `0x200007a0`、callback 兩條直接 callee 與 flag writers；實際 ECALL／IRQ 路由、frame 保存、JT2／GP+384 最後 writer、兩個尚未展開的 driver 與整體物件保存期仍待釐清。
