# v4.1.60：APP config callbacks、四 byte readback 與固定 256-byte 寫入

日期：2026-11-26。承接 [config-I/O 合約](v4160-config-io-static.zh-TW.md)，核對 APP 提供的 C+56／C+60 callbacks 及其完整本機 callees，並把 read callback 串接到兩版本候選 copy。[檢查器](check_v4160_app_nv_callbacks_static.py)／[ledger](v4160-app-nv-callbacks-static.json) 保存完整指令、operands、CFG、store census 與條件。

本輪最重要的區別：**read callback 用 num×4 作 copy bytes；write callback 不使用入口 num，完整正常路徑固定取 256 bytes。兩者正常返回均強制 A0=0，不能據此認定硬體操作成功。** 所有分析只讀本機檔案與主機整數代數，沒有執行或模擬 target ISA、provider、buffer、MMIO 或 polling。既有 C 重建覆蓋率未增加。

## 完整本體與 APP 欄位證據

| 本體 | range（終點不含） | bytes／instructions |
| --- | --- | --- |
| read wrapper | `1979a..197b8` | 30／13 |
| write wrapper | `197be..197f0` | 50／20 |
| unlock-like leaf | `18e98..18eb6` | 30／10 |
| lock-like leaf | `18eb6..18ec4` | 14／6 |
| erase-like leaf | `18ec4..18ef2` | 46／19 |
| program-like leaf | `18ef2..18f56` | 100／38 |
| timer-like leaf | `19764..1979a` | 54／22 |
| V1.31 reference copy | RAM `20000332..2000036c`，flash `405a2..405dc` | 58／18 |
| V1.40 reference copy | RAM `20000332..2000036c`，flash `405e2..4061c` | 58／18 |

七個 APP 本體合計 324 bytes／128 instructions，兩份候選 copy 合計 116／36；總計 **440／164**、29 個靜態 store 指令位置。另核對三個各 10-byte／3-instruction 的 APP 欄位賦值窗口，不計入完整本體總數：

| window | 寫入位置 | 解算值 | 若 C=當時 SP+16，對應欄位 |
| --- | --- | --- | --- |
| `19a4a..19a54` | SP+24 | `08077c00` | C+8 |
| `19a76..19a80` | SP+72 | `1979a` | C+56 |
| `19a80..19a8a` | SP+76 | `197be` | C+60 |

這些是指令賦值證據；後續 config copy、欄位未被改寫與實際 installed 綁定仍有條件。`197b8..197be` 的獨立六 byte tail 不屬於 read wrapper。所有完整本體 SHA-256、每條 operand 與 source mapping 均在 ledger 精確保存；沒有用下一個 symbol 名稱猜測邊界。

沿用固定 APP、兩份 carrier、SDK header identity 及已保存的 LLVM Xwchc 規則／28 vectors。新增標準 RV32 ADD、ORI、SB 解碼，其他 forms 沿用既有 checker。每條完整指令的欄位、所有 store 與 GPR writes 皆有明確期望值；完整 body hash 另作獨立 guard。radare2 的只讀 program leaf 反組譯也確認 word loop 與四個輪詢區段。

## read callback：初始 num=1 的條件性四 byte 輸出

入口參數記為 `(source, num, destination)`。`1979a` fresh 讀取 slot `4004c`，建立 16-byte frame，保存 RA，接著形成：

```text
copy_A0 = entry destination
copy_A1 = entry source
copy_A2 = (entry num << 2) & 0xffffffff
call fresh slot target
恢復 RA、SP
A0 = 0（忽略 copy 的 scalar reply）
RET
```

這段 wrapper 本身不填 output。slot target 的具體行為取決於當時 installed provider，不能直接套用參考候選。

兩個參考 carrier 的 slot word 均為 `20000332`。各自的 first-copy mapping 把完整 58-byte copy 映到該 RAM 地址，兩份 body SHA-256 相同：

```text
558a82658cb54901945d4c2884f2e87e763f64d57c0cafa831307beb44ae0c36
```

在此條件性 copy 解讀下：先保存 `U32[4002420c]`、寫零並作 FENCE.I；destination 或 source 為零、或 count 為零時跳過資料 loop。其餘路徑由 index=0 開始，fresh LBU[source+index]，SB 到 destination+index，再依 count 結束；正常返回前恢復先前保存的控制 word。這是前向逐 byte 傳遞，沒有來源快照或 memmove 保證，位址按 RV32 寬度處理。

前輪 config-I/O 初次傳入 num=1、destination=caller SP+12。因此在**slot、欄位與 code/context 符合此候選、來源與目的位址非零且有效、copy 完成並無破壞所需狀態**的條件下，四次 byte store 可供 resident 讀回 `[caller SP+12,caller SP+16)`。APP 的初始 source `08077c00` 所指內容不在這份 APP 檔案內，故仍不能決定實際 word 或 resident 的 equality branch。

以同一個有效且不回繞的 caller SP 為基準，wrapper 的 RA spill 位於 `[SP-4,SP)`；resident output 是 `[SP+12,SP+16)`；resident 保存的 S2 是 `[SP+16,SP+20)`。三者不重疊。這只是相對區間與編碼證據，不能取代 SP 保存、copy destination 有效性、source extent 或實際 slot 綁定證明。

## write callback：入口 count 被忽略

`197be` 建立 32-byte frame，保存 RA、S0 及入口 A2（source pointer）。入口 A0（destination address）放在 S0，依序呼叫：

1. `197c8 → 18e98`：unlock-like。
2. `197ce → 18ec4`：A0=live S0，erase-like。
3. `197d8 → 18ef2`：A0=live S0、A1=fresh U32[當時 SP+12]，program-like。
4. `197dc → 18eb6`：lock-like。
5. `197e2 → 19764`：A0=1，timer-like。

**入口 A1 不被 wrapper 讀取；在覆寫它之前的兩個 leaf 也不讀 A1。** program 的來源使用重讀的 saved A2，並非入口 num；wrapper 最後恢復 S0／RA／SP，強制 A0=0。沒有檢查任何 callee 的 scalar reply。

### program leaf 的 64 個 word

erase 與 program 都以 `A0 &= 0xffffff00` 抹掉目的位址最低八 bits。program 先處理控制欄位並等待 bit0、bit1 清零。第二個 poll 執行 `A5 &= 2`，只有 A5=0 才退出，因此**退出結果本身提供 transfer index=0**，並非另有 LI zero。

然後 A2=256，對 offsets `0,4,...,252`：

```text
fresh word = U32[source_A1 + offset]
U32[aligned_A0 + offset] = word
等待 status bit1 清零
offset += 4
offset != 256 時重複
```

若所有 poll 完成、code／暫存器 context／accesses 有效，這是 64 次 U32 load/store，即固定 256 bytes。每輪 fresh load 使來源與目的重疊時可能有次序效應，不能當作預先複製的 buffer。靜態 CFG 有四個 cyclic SCC：首 poll 三節點、次 poll 三節點、word loop 與其內 poll 合併九節點、尾 poll 三節點。所有 poll 均沒有本機 timeout。

### 其他 leaf 的可見存取

| leaf | 可見編碼行為 | 靜態 store 位置數 |
| --- | --- | ---: |
| unlock | 常數 `45670123`、`cdef89ab` 依序寫至 `40022004`，再寫至 `40022024` | 4 |
| erase | control OR `20000`、aligned address 至 `40022014`、control OR `40`；等 status bit0 清零後 fresh control AND `fffdffff` | 4 |
| program | control OR `10000`；word loop；control OR `200000`；尾 poll 後 fresh control AND `fffeffff` | 4 |
| lock | fresh `U32[40022010] OR 8000` 寫回 | 1 |
| timer | fresh U8[GP+382]×A0 modulo 32-bit；六個 `e000f000` family stores，等 status bit0 設定 | 6 |

表中只是地址與 bit 操作的編碼解讀，沒有嘗試硬體讀寫。program 的四個位置之一在完成的 word loop 中會執行 64 次。timer 的 A0 由 wrapper 設為 1；實際計時單位／時長與 bit 的物理語義未證，零計數也沒有單獨繞過 poll 的分支。

## 保存條件與 config-I/O 串接界線

read wrapper 的 own GPR writes 是 RA／SP／A0／A1／A2／A4／A5；候選 copy 只明確寫 A3／A4／A5／A6。write closure 的明確 GPR writes 不包含 GP／S1／S2；唯一使用 S0 的 wrapper 有成對保存與恢復，五個 leaf 均不建立 frame 或再呼叫函式。

這補足「沒有哪條明確指令寫入哪些保存暫存器」的證據；**不代表無條件保存**。動態 source／destination、MMIO／外部干擾或 alias 仍可能破壞 frame、code、config 或所需資料。write wrapper 的 SP+12／24／28 重讀需要 then-live SP 與保存字仍有效；兩個 callback 的正常 RET 也要求返回控制完整。

接回前輪 resident，每輪 callback 的入口 count 為 `Li >> 2`，但此 APP write callback 不使用它；不能把 callback 的 256-byte source extent 推定為 `4*(Li>>2)`。allocation L0、fill L1 與每輪 Li 是不同 fresh reads，Pcurrent 也由 cache 重新取得。要證明此路徑的來源範圍與保存期，仍需另外證明足夠的有效 extent 與各值／指標之間的關係。本輪只記錄這個固定長度差異，沒有建立故障觸發資料或執行硬體操作。

強制 A0=0 仍不證明 erased／programmed／locked 成功，也不證明等待會結束。resident 不檢查 callback scalar reply 的前輪結論不變。

## 重播與驗證

```text
python analysis/check_v4160_app_nv_callbacks_static.py
python -O analysis/check_v4160_app_nv_callbacks_static.py
```

兩模式均實際輸出：

```text
PASS: 65536 U16 counts; 6 U32 wrap cases; 1024 alignment cases; 256 poll-bit cases; fixed 64-word algebra; 13 specified raw mutations
PASS: 9 complete bodies, 440 bytes/164 instructions/29 store sites; 30 binding bytes/9 instructions
PASS: exact ledger replay; fixed 256-byte write versus scaled read; NO target ISA/provider/MMIO execution
```

十三個 raw mutations 分別改動 read shift／source、saved source reload、program alignment／poll mask／bound／load offset／store offset／stride、timer poll 方向、copy load width／store offset、APP callback address；每個都必須命中特定 semantic guard，不能以全檔 hash 不符或任意 exception 代替。

65536 counts、wrap／alignment／poll-bit cases 與固定 word offsets 皆為主機整數關係，沒有 target 暫存器、memory 或 callback 執行模型。預設只讀重算並逐 byte 比對 JSON，`--write` 僅建立不存在的 ledger。重播需要九個既有 Python dependency 模組，以及本機固定 APP、兩份 carrier、SDK header 和 LLVM 來源；candidate 輸入未隨本次發布，僅 clone repo 不足以重現。

後續仍需釐清實際 installed provider、初始 NV 資料、L0／L1／Li 與 256-byte source extent 的來源關係，以及其他 writer／中斷下的保存條件。前輪 sparse 初始化最後缺失的 source word 也仍未補齊。
