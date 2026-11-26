# v4.1.60：完整 config+44 callback、硬體值保存與 low16 返回鏈

日期：2026-11-26。承接 [設定長度與 buffer 來源](v4160-config-buffer-source-static.zh-TW.md)，展開 APP 提供的 C+44 callback `197f0`，以及它直接呼叫的 poll／result 小函式。[檢查器](check_v4160_app44_callback_static.py)／[ledger](v4160-app44-callback-static.json) 保存全部指令規格、CFG、store census、16 組保存／恢復配對及 resident 回覆寫入位置。

**原指令呈現保存、設定、輪詢、讀值、恢復的流程。正常回覆來自先前讀值函式的保存字，並非最後一次 callee 的 A0。** 在所需 context 與保存字完整的條件下，回覆為硬體 U32 讀值的 low16。其他 11 個呼叫位置尚未展開，故仍不能證明 config 長度／count／cache 在整段流程不變。

僅離線讀檔、反組譯、解碼與主機代數檢查，未執行或模擬 target ISA、callback、buffer、MMIO 或 polling。C 重建覆蓋率不變。

## 三個完整本體

| 本體 | range（終點不含） | bytes／instructions | SHA-256 |
| --- | --- | --- | --- |
| C+44 callback | `197f0..1995c` | 364／130 | `ee7d9a35ebc31a363cc5f6efca0ce21d341099694f34aa90185be94995d826a4` |
| result leaf | `18a66..18a6e` | 8／4 | `3742627de5a8d8a288a2a2a446c3a88b6056a8892352d99777783ea3467b5504` |
| poll leaf | `18a8e..18a98` | 10／4 | `54df366a01082d8608026cdcc1facff8db6e5c1447bb3b66237bd2ad55888349` |

合計 **382 bytes／138 instructions／42 個靜態 store 位置**。所有 138 條指令均有獨立 opcode／operand／target 規格，另核對完整 bytes hashes。新增標準 RV32 SLTU 解碼，其他形式沿用既有 checker；固定原 APP、兩份 carrier、SDK header、LLVM 欄位來源／Git blob hashes 與 28 vectors 仍再檢查。實體 ISA profile 與 installed provider 未證。

APP builder 的 `19a92/19a96` PC-relative 值為 `197f0`，`19a9e` 存至當時 SP+60；在 C=SP+16 的關係下即 C+44。這是來源賦值證據，仍需後續 copy、保存與實際綁定才能套用至執行中的 callback。

## 128-byte frame 與本機寫入範圍

入口 SP-=128，保存 RA 至 SP+124、S0 至 SP+120、S1 至 SP+116，依序到 S11 至 SP+76；尾聲成對讀回並 SP+=128、RET。各區段終點含最後一 byte：

| 區段 | 當時 SP-relative bytes | 用途 |
| --- | --- | --- |
| 六個 snapshot words | 4..27 | 暫存六個硬體 word |
| result word | 28..31 | 保存 result leaf 回覆 |
| 本機 config request | 32..63 | 先提出 32-byte 清零請求，再設定欄位 |
| 保存 GPR words | 76..127 | RA、S0..S11 |

這四段互不重疊。入口 `19814→8520` 參數為 A0=live SP+32、A1=0、A2=32；該 callee 仍 opaque，不由正常返回直接推定清零完成。其後六個明示 config stores 為 U32[SP+32/36/40/48]=0、U32[SP+44]=`000e0000`、U8[SP+52]=1。

callback 本體有 26 個 SP-based store 與 16 個硬體恢復 store。直接 stack store offsets 都在這個 128-byte frame 內，但 live SP 與 frame 有效性仍需保存前提。encoded GPR writes 涵蓋 RA／SP／S0..S11／A0..A5；GP、T registers、A6／A7 沒有被本體明確寫入。這不是 nested callees 的 ABI 或保存合約。

## 十六組硬體 word 配對

以下地址是以所需 live bases 保持為前提的數值投影。前段 S1=`40012400`、S0=`40012000`；兩個 `400210xx` accesses 另在相應位置重新建立 A5 base。

| 投影地址 | 讀取位置與暫存 | 寫回位置 |
| --- | --- | --- |
| `40021018` | `1981c` → S11 | `198ee` |
| `40021004` | `19820` → S10 | `198f2` |
| `40012404` | `1982c` → S9 | `198f6` |
| `40012408` | `19830` → S8 | `198fa` |
| `4001242c` | `19834` → S7 | `198fe` |
| `40012430` | `19838` → S6 | `19902` |
| `40012434` | `1983c` → S5 | `19906` |
| `4001240c` | `19840` → S4 | `1990a` |
| `40012410` | `19844` → S3 | `19910` |
| `40012414` | `19848` → S2 | `19914` |
| `40012418` | `1984c` → SP+4 | `19918` |
| `4001241c` | `19856` → SP+8 | `19922` |
| `40012420` | `1985e` → SP+12 | `1992c` |
| `40012424` | `19862` → SP+16 | `19936` |
| `40012428` | `19866` → SP+20 | `19940` |
| `40012438` | `1986a` → SP+24 | `1994a` |

這些是不同時間的 fresh U32 loads，並非 atomic snapshot。十個值跨多次 callee 保存在 S registers，六個值經 stack 重新載入；各自都需要寄存器／保存字／code 完整。多數寫回使用 then-live S0 加偏移，不是完全獨立的絕對地址。

即使寫回相同 bit pattern，也不能由指令配對宣稱硬體狀態確實恢復：MMIO 的讀寫副作用、外部更新與實體映射均未證。

## 呼叫順序與輪詢

完整本體有 13 個 direct-call sites；參數只列相鄰原指令明確建立的部分，未列者仍可能是 ambient 值。

| call | target | 明示參數 |
| --- | --- | --- |
| `19814` | `8520` | SP+32、0、32 |
| `1986e` | `19124` | A0=512、A1=1 |
| `19874` | `1908c` | A0=`c000` |
| `1987a` | `188e2` | A0=live S1 |
| `19896` | `1892e` | A0=live S1、A1=SP+32 |
| `1989e` | `18986` | A0=live S1、A1=1 |
| `198a6` | `18a98` | A0=live S1、A1=1 |
| `198ac` | `18a6e` | A0=1 |
| `198b8` | `189ae` | A0=live S1、A1=16、A2=1、A3=7 |
| `198c0` | `18996` | A0=live S1、A1=1 |
| `198ca` | `18a8e` | A0=當時 A5、A1=2 |
| `198dc` | `18a66` | A0=live S0+1024 |
| `198e6` | `188e2` | A0=live S0+1024 |

本輪只展開 `18a8e`／`18a66`。其餘 **11 個呼叫位置、10 個不同 target** 的 effects 仍未知，所有 call fallthrough 皆是假設正常返回。

poll leaf 執行：

```text
word = fresh U32[entry A0]
A0 = unsigned(0 < (word & entry A1))   # SLTU，結果完整0或1
RET
```

caller 的 mask=2，回覆零則重試；沒有 timeout。首次 A5 取自 live S1，之後在每次 branch 前明示重建 A5=`40012400`。因此不能不加保存前提就把首次位址也寫成該常數。

callback 本機 CFG 只有一個六節點 cyclic SCC：`198c6,198c8,198ca,198ce,198d2,198d6`。這張圖不包含其他 opaque callee 內部的等待；即使此 poll 退出，也不代表已證硬體操作成功。

## low16 回覆的保存與 resident 寫入

result leaf 是 **LW 32-bit，然後截 low16**，不是 LHU：

```text
A0 = U32[entry A0+76]
A0 = ((A0 << 16) & 0xffffffff) >> 16
RET
```

若 live S0 保持 `40012000`，caller 傳 `40012400`，故投影讀取地址是 `4001244c`。真實 word 未知。兩個小 leaf 都只明確寫 A0，無 stores、nested calls 或本機 loops。

回覆路徑按原指令順序：

1. `198dc` 呼叫 result leaf。
2. `198e0` 將回覆存到 then-live SP+28。
3. `198e6` 呼叫另一個 `188e2`；它可以改 A0，其 scalar reply 並非最後返回來源。
4. `1991e` 從 then-live SP+28 fresh 讀 word 至 A4。
5. `19948` A0=A4，後續無 A0 定義，再恢復 frame 並 RET。

本體在 result store 之後沒有別的 SP-relative store 覆蓋該 word；reload 與 final move 之間也無其他 A4 定義。**只有保存字、SP、code/context 與必要 accesses 完整，最後回覆才可等同早先 low16 讀值，範圍為 0..65535。** 未知 callee、alias 或外部 writer 破壞保存字時，這個範圍也不是無條件結論。

串回兩份參考 resident 的 config+44 caller：

| 候選 | callback call | 接回覆的 SH | 投影目的地址 |
| --- | --- | --- | --- |
| V1.31 | `43d38` | `43d3e` | `200031a4` |
| V1.40 | `43dc4` | `43dca` | `200031f4` |

caller fresh 讀 C+44，非零才呼叫，返回後 SH A0。這兩個地址是 metadata 的半字欄位，**不是 config 的 C+12 長度或 C+14 count**。callback 本機可見 stores 在所需 bases 保持時投影到自身 stack 或上述 MMIO，沒有辨識出直接 RAM config store；但另外 11 個 call sites、動態 alias／外部 writer 仍未排除，不能據此宣稱長度／count 必然保存。

## 實際重播與反例

```text
python analysis/check_v4160_app44_callback_static.py
python -O analysis/check_v4160_app44_callback_static.py
```

兩模式均實際輸出：

```text
PASS: 196608 word extraction cases; 65536 poll-bit cases; 4 disjoint stack regions; 12 specified raw mutations
PASS: 3 complete APP bodies, 382 bytes/138 instructions; 42 store sites; 16 projected snapshot/restore pairs
PASS: exact ledger replay; low16 reply conditional on saved-word/context integrity; 11 opaque call sites; NO target execution
```

word extraction cases 為全部 65536 個低半字乘三個高半字模式，不是窮舉所有 U32。poll-bit 與 stack-region checks 也是主機代數，沒有建立硬體回覆或記憶體模型。十二個 raw mutations 改 frame size、snapshot/config offset、poll mask／branch、result save／reload、MMIO restore offset、final reply register、SLTU operand、result load offset／shift；每個都需命中特定 semantic guard，不能以全檔 hash 不符或任意 exception 代替。

預設只讀重算並精確比對 JSON；`--write` 只建立不存在的 ledger。重播需要十一個既有 Python dependency 模組，以及本機固定 APP、兩份 carrier、SDK header 與 LLVM sources／vectors。candidate 輸入未隨本次發布，僅 clone repo 不足以重跑。

後續仍需展開 `8520` 與 peripheral helpers 的完整 effects，串接整個 closure 的 config/cache/frame 保存條件，並保留實際 provider、硬體語義、終止性及初始 NV contents 未知。
