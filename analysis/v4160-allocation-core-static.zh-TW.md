# v4.1.60：完整 allocation core 與 opaque fallback 的條件性靜態合約

日期：2026-11-26。承接 [message marker 串接](v4160-message-marker-static.zh-TW.md)，將先前只審查 110-byte prefix 的私有 core 擴至完整 208 bytes／版本。檢查原始 bytes、operands、條件性 CFG／SCC、編碼中的寫入集合與主機代數；沒有執行或模擬目標 ISA、heap、linked list、provider、loader 或 MMIO。C 還原覆蓋率沒有增加。

## 完整本體與證據範圍

| 參考候選 | flash source（終點不含） | 條件性 RAM target（終點不含） | SHA-256 |
| --- | --- | --- | --- |
| V1.31 | `0x402b0..0x40380` | `0x20000040..0x20000110` | `e74bee633acbf171c951df2720f2aeb66758fc597a8aa8efc0271bc686d2c42b` |
| V1.40 | `0x402f0..0x403c0` | 同上 | `d386953a4afde83699523eed2fd8fcb8c4c1ffb405641600c77dffcbe13a0163` |

每份 208 bytes／72 instructions。[檢查器](check_v4160_allocation_core_static.py) 固定兩個完整 hash、全部 72 個指令的 opcode／operands／targets，以及 message-wrapper-to-core 和第一段 copy 的完整來源／目的範圍；[JSON ledger](v4160-allocation-core-static.json) 保存推導結果。template 只正規化五個已各自檢查的版本專屬 RAM operand，並未將版本身分視為相同。

解碼明示為 `conditional-LLVM-Xwchc-RVInst16CL-GPRC`，沿用已保存 LLVM 欄位來源、四份 SHA-256／Git blob pins 及 28 筆 encoding vectors。r2 在 compressed halfword 位置顯示的浮點名稱不作語義依據。實體 ISA、installed resident、最終 RAM bytes 仍未知。

## 前置控制字與 rounding

core 建立自己的 16-byte frame，保存 S0／RA，讀 `U32[0x4002420c]` 至 S0、寫零、`FENCE.I`，才檢查輸入。完整 A0=0 或完整 A1=0，經控制字恢復路徑返回 0；不是無裝置存取的純配置器。

非零輸入的 rounded request：

```text
R = ((full_input_A0 + 3) & 0xffff) & 0xfffc
```

R≤52 選 small head，R>52 選 large head；兩者使用同一 sentinel word。U16 input 的非零域中，55 個 input 走 small 分類、65,480 個走 large，另 input=0 先被拒絕。input=`65533..65535` 雖非零，R 仍會回繞成 0，沒有第二個 R=0 拒絕條件。

| 候選 | small head slot | large head slot | sentinel slot | fallback slot | accounting base |
| --- | --- | --- | --- | --- | --- |
| V1.31 | `0x20003194` | `0x20003190` | `0x2000318c` | `0x20003220` | `0x2000319c` |
| V1.40 | `0x200031e4` | `0x200031e0` | `0x200031dc` | `0x20003270` | `0x200031ec` |

這些名稱僅表達該本體的比較與讀取角色；不證明實際資料、heap ownership 或記憶體有效性。

## fallback 回覆被丟棄；A2 仍可被觀察

搜尋的 current pointer 與 sentinel 相等時，fresh LW 讀 fallback slot 至 A4。值為零直接走失敗路徑；非零則在 `0x200000a0` 以 JALR A4 呼叫，link=`0x200000a2`，target 依 JALR 清除 bit0：

```text
A0 = 1
A1 = full_input_A1 | (R << 16)
A2 = ambient caller value，編碼中的 prefix 沒有讀寫它
```

**正常返回後不重試 list，也不把 fallback A0 當作配置結果。** `0x200000a2` 無條件跳往共用控制字恢復路徑，之後明確 LI A0=0。這個返回結論仍要求 fallback 正常返回至 link，且所需 live context、saved frame、code 與後續存取有效；不能排除 callback 改記憶體、改控制流、不返回或造成後續 fault。

整個 core 不能再說 A2 未改：第一次直接定義 A2 是 fit path 的 `0x200000bc`，作 `block_size - R`，後面用於新 header 地址。在這條路徑之後沒有本體內的邊返回 fallback call；但 fallback 發生在該定義之前，因此仍可看到原 caller A2，其他 ambient registers／記憶體也未受已證合約限制。此結果沒有證明 pointer nonescape，也沒有解析 fallback 的實際提供者。

## 搜尋、分割與 accounting

current≠sentinel 時，先讀 `U16[cur+6]`；非零跳 next。否則讀 B=`U16[cur+4]`，B<R 也跳 next。next=`U32[cur]`，沒有 pointer bit 正規化、null guard、iteration bound 或 cycle detection。

fit 條件是 flag=0 且 B≥R；**只有 B−R>8 才分割**。分割路徑依序讀舊 next、讀 accounting，然後：

1. 新 header N=`(cur+R+8)&0xffffffff`；寫 U16[N+4]=B−R−8。
2. 寫 U32[N+0]=舊 next，U16[N+6]=0。
3. 寫 U32[cur+0]=N，U16[cur+4]=R。
4. accounting 的 U16 值先扣 8。

不分割時，`U16[cur+4]` 保持 B，沒有改成 R。兩條路的共用成功後段都寫 `low16(input_A1)` 至 U16[cur+6]，fresh 讀 accounting、扣 **R**、寫 low16，返回 `(cur+8)&0xffffffff`，並恢復控制字。

在讀取穩定、相關 header／accounting／frame 不 alias 的前提下：

```text
account_final = (account_initial - R - (8 if split else 0)) & 0xffff
```

例如 R=20、B=24 不分割，stored size 仍為 24，但 accounting 扣 20。不能改寫成扣 stored size，也不能僅由此推論 accounting 的全域意義或 allocator 正確性。前輪 release helper 讀取的 size／flag 與這些 stores 之間仍需要實際資料及保存條件。

完整 input_A1 非零不代表 low16 flag 非零，例如 `0x10000` 會寫入 flag 0。成功後段的返回指標也可能 RV32 回繞為零。沒有獨立 counter increment 出現在本體中；這些欄位算術不構成安全配置、合法指標或物件所有權證明。

## 接回 APP 的 12-byte 描述項請求

承接前輪已固定的三個 APP 建立函式與 message wrapper：APP request12 → core A0=20、A1=`0xf00c`，本 core R=20、選 small head。若正常選中 free block 並完成後段，在同一組穩定／不重疊／context 前提下：

| 關係 | 模 2³² 的地址／條件 |
| --- | --- |
| core 返回 P | `cur+8` |
| message wrapper 返回描述項 D | `cur+16` |
| message marker `D-2` | `cur+14`，由 wrapper 寫 255 |
| APP 通知 marker `D+2` | `cur+18`，APP 寫 AB／BA／B9 |
| 分割條件 | B>28，accounting 扣 28 |
| 不分割條件（fit 域） | B=20..28，stored size 保持 B，accounting 扣 20 |

這補上描述項的兩層 header 位移與 core 分支關係；不證明當次 slot target 相符、取得有效區塊、callback 必定執行、實際 D 未變或只交回一次。

## CFG、保存與限制

一個七節點搜尋 SCC：`0x2000008c, 0x200000ae, 0x200000b0, 0x200000b2, 0x200000b4, 0x2000010c, 0x2000010e`。未命中的穩定可讀循環可不返回；任意未知 node pointer 也可能落在 MMIO 或無效區域。

唯一 encoded RET 在 `0x2000010a`。移除兩個控制字恢復 store（`0x2000005e`／`0x20000100`）後，靜態圖不再有入口至 RET 路徑；RA／S0 的 epilogue reload 也支配 RET。這只證明編碼中的恢復路徑，不保證保存字內容或硬體效果。

CFG 把 fallback call 到其 link 記作**明示假設的正常返回邊**；BLTU 只為共用拓撲計算轉成另一個雙 successor branch 標記，原 operands／方向另由獨立規格檢查。不代表分析了未知 callee 的全部 successors、effects 或終止性。

encoded GPR write set 為 RA、SP、S0、A0..A7；S1..S11、GP、T registers 沒有直接被本體寫入。opaque fallback 可以有不同效果，heap stores 也可能改寫 stack、saved registers、accounting 或 code；不能把直接 non-write set 當作完整 ABI／保存合約。正常分支推論需要 code 不變、有效存取、必要 live S／GP／SP／frame 保持，以及對公式所需的穩定與不重疊條件。

## 實際驗證

需要固定原 APP、五個既有 Python dependency 模組，以及本機 `analysis/wch-resident-candidate-2026-10-21/` 中兩份 carrier、SDK header 與四份 LLVM 來源／測試參考。候選輸入目錄未隨本次發布；只 clone repo 不足以重跑。程式不下載、安裝或啟動服務，預設精確重播 JSON；`--write` 僅可建立不存在的 ledger。

```text
python analysis/check_v4160_allocation_core_static.py
python -O analysis/check_v4160_allocation_core_static.py
```

兩種模式均實際輸出：

```text
PASS: 65536 rounding cases (55 small/65480 large/1 zero input); 65536 split gaps; 786432 U16 accounting cases; 10 specified raw mutations
PASS: 2 complete cores, 416 bytes/144 instructions; conditional CFG/SCC; fallback-zero return; encoded restore cut set
PASS: ledger exact replay; installed/fallback/context integrity UNPROVED; NO ISA/provider/heap/MMIO execution
```

rounding 窮舉 U16 input 的算式與分類，不是所有完整 32-bit 入參；split gaps 窮舉 U16 gap 的比較；accounting cases 為全部 U16 初值 × 六個 R × 是否扣八的模數代數，部分組合不一定能由合法 U16 block 執行到。它們不是 CPU／記憶體模型，也不宣稱任意 heap 狀態覆蓋。

十個 raw mutations 分別改 rounding mask、fallback A0 入參、JALR target GPR、失敗 A0=0、flag load offset、split threshold、remainder size store offset、remainder link store offset、tag store offset、accounting subtraction source。變異直接進入推導，必須由指定 operand guard 拒絕，不以全檔 hash 不符或任意 decoder exception 充作通過。

下一步仍需追查兩個 fallback slot 的寫入／初始化來源、其實際 provider 與保存合約，並持續保留 installed 身分及真實 payload lifetime 未知。
