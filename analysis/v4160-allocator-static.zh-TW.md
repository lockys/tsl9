# v4.1.60：候選 allocator 私有 release helper 完整靜態合約

日期：2026-11-26。承接 [cancel-provider](v4160-cancel-provider-static.zh-TW.md) 與 [timer helpers](v4160-timer-helpers-static.zh-TW.md)，展開 RAM target `0x20000110` 的兩份完整參考本體。這是候選程式的條件性合約；實際 installed 綁定、實體 ISA profile、最終 RAM bytes 均未證明。本輪未增加 C 還原覆蓋率。

## 輸入與範圍

[檢查器](check_v4160_allocator_static.py) 與 [JSON ledger](v4160-allocator-static.json) 固定下列完整本體，並逐指令檢查 operands、封閉 CFG、SCC、dominators 與 GPR 寫入集合。原始輸入全檔身分沿用既有 APP、header、carrier SHA-256，第一段 startup copy 的完整來源／目的範圍也會檢查；不執行 loader。

| 參考候選 | flash source（終點不含） | RAM target（終點不含） | bytes／instructions | SHA-256 |
| --- | --- | --- | --- | --- |
| V1.31 | `0x40380..0x40454` | `0x20000110..0x200001e4` | 212／73 | `a510cc84e9173549d7f5b68da894f5b5ba9109bcd0c2601653bbdf0f5c964c50` |
| V1.40 | `0x403c0..0x40494` | `0x20000110..0x200001e4` | 212／73 | `2f3352fb93e881b9bcd6164c8d7b02def9073df23ccb1e51d4d0fc89607ef703` |

解碼使用明示的 `conditional-LLVM-Xwchc-RVInst16CL-GPRC` profile，沿用前輪已保存的四份 LLVM 欄位來源、digest 與 28 筆 encoding vectors。新解碼器補入本體所需 RV32 integer forms；通用 r2 顯示為 FLD／FSD 的位置仍須依此條件性 Xwchc 解讀，不視為實體 profile 證明。

既有 `experiments/v4160-105c4-closure-next/heap_release_*` 是 V1.31 的分段 synthetic models。本輪新增兩個版本的完整靜態閉合證據，沒有執行那些 models，也沒有模擬任何目標指令、linked list、provider 或 MMIO。

## 控制字、暫存器與返回

入口先讀／保存 `U32[0x4002420c]` 至 A6、寫零、`FENCE.I`，之後才檢查 input A0 是否為零。即使 A0=0，也經過控制字存取。

唯一 RET 位於 `0x20000126`；`0x20000122` 的控制字恢復 store 支配所有抵達這個 RET 的 CFG 路徑。A6 唯一寫入為入口讀取；恢復時 A5 的控制字 base 來自入口或共用尾段。這只證明編碼中的正常返回路徑；不涵蓋例外、無限搜尋、硬體 read／write 效果或外部干擾。

完整 GPR 寫入集合為 `x6, x10..x17, x28`，即 T1、A0..A7、T3；無 nested call、stack 操作，未直接寫 S0..S11、GP、SP 或 RA。

**未直接寫暫存器不等於完整 caller-frame 保存。** 未知 heap／global pointers 可能與外層保存的 S registers、RA 或程式碼重疊；若 store 改寫 outer stack 或 code，不能沿用完整外層 ABI／此靜態 CFG 的執行推論。ledger 明列 `outer_stack_nonalias_proved: false`、`code_immutability_proved: false`。條件性組合還需要有效存取、程式碼穩定、保存區不受寫入影響及沒有外部暫存器變動。

## 搜尋判定：區間而非精確 payload 起點

| 候選 | head pointer slot | limit pointer slot | boundary pointer slot |
| --- | --- | --- | --- |
| V1.31 | `0x20003194` | `0x2000318c` | `0x20003190` |
| V1.40 | `0x200031e4` | `0x200031dc` | `0x200031e0` |

非零輸入讀 head 至 cur、limit 至 T1、prev=0，進入 `0x2000013c`：

1. unsigned cur ≥ limit，跳尾段恢復控制字。
2. 讀 `next=U32[cur]`；input < cur 或 next < input 時，prev=cur、cur=next，繼續搜尋。
3. 區間命中後，若 input < `(cur+8) & 0xffffffff`，跳尾段；否則進入欄位更新。

因此此處條件是 `cur <= input <= next`，再加上 wrapped `cur+8` 下界；沒有 `input == cur+8` 判定，也未正規化 pointer bit 0。host 區間例證 cur=`0x1000`、next=`0x1020` 時，`0x1008..0x1020` 全部通過這些比較；它不是任何實際記憶體呼叫的測試。

沒有證明 head 非零、節點地址／欄位可讀、對齊、範圍、鏈結有序或無循環。七節點循環 SCC 是 `0x2000013c, 0x20000140, 0x20000144, 0x20000148, 0x200001de, 0x200001e0, 0x200001e2`，沒有 iteration bound；未命中的穩定可讀循環可能不返回。未知節點地址也可能指向 MMIO。

## 欄位更新與合併順序

此處只依讀寫寬度及 offset 命名；未宣稱 SDK 型別、heap ownership 或實際 payload 來源已證。

| 候選 | U8 counter | accounting base |
| --- | --- | --- |
| V1.31 | `0x20002fa4` | `0x2000319c` |
| V1.40 | `0x20002ff4` | `0x200031ec` |

- 讀 `U16[cur+6]`，**只有等於 `0x8001`** 時，counter 作 U8 加一（255 繞回 0）。這不是拒絕其他 flag 的 guard。
- `0x20000174` 讀原命中節點的 `U16[cur+4]`；讀 `U16[account_base+6]`，先清零 `U16[cur+6]`，再寫回兩讀值之和的 low16。
- cur=head、cur=boundary pointer 或 `U16[prev+6] != 0` 時略過 previous merge。否則依序將 next 寫入 prev+0、更新 prev+4 為原兩個 payload sizes 加 8 的 low16、accounting 加 8，最後改 cur=prev。
- 重新讀 next；next=limit、next=boundary pointer 或 `U16[next+6] != 0` 時略過 next merge。否則將 cur+4 更新為兩個 payload sizes 加 8 的 low16，再將 next 的 successor 寫至 cur+0，最後重讀 accounting 並加 8。

若相關 reads 穩定且互不 alias，accounting 可摘要為：

```text
(old_U16 + original_matched_payload_U16_at_0x20000174
 + 8*previous_merge + 8*next_merge) & 0xffff
```

其中 payload size 指 previous merge 改 cur 之前的原命中節點讀值。任意 alias、外部寫入或 fault 下，必須保留 ledger 中逐項讀寫順序，不能把這個初始快照公式當成普遍記憶體合約。本輪沒有從 flags／size／links 推論安全配置器或真實物件保存期。

## 與外層 deallocate 的條件性組合

helper 的 A0／A1 沒有一般性的 status 或保存保證。外層在 helper 正常返回後自行設定 A0=0，因此這個 0 不能單獨證明找到區塊、執行欄位更新或完成釋放；helper 的範圍退出也可正常返回。外層原有 null／marker 路徑仍依前輪 5／4／0 分類。

兩個完整 helper 的 register non-write set 縮小了私有 ABI 的未知範圍，但 installed 身分、執行時 code／資料、caller saved frame 的不重疊條件仍然未知。

## 實際驗證結果

重跑需要本機 `analysis/wch-resident-candidate-2026-10-21/` 內 digest 相符的兩份 carrier、SDK header、四份 LLVM 來源，以及三個既有 Python dependency 模組。這些候選輸入未隨本次提交發布；僅 clone repo 不足以重現。檢查器不下載輸入、不啟動服務，預設只讀重播 JSON；`--write` 使用 exclusive-create。

```text
python analysis/check_v4160_allocator_static.py
python -O analysis/check_v4160_allocator_static.py
```

一般與 `-O` 模式均實際輸出：

```text
PASS: 65536 flag values; 256 byte wraps; 196608 U16 merge-credit cases; interval witness; 8 specified raw mutations
PASS: 2 complete bodies, 424 bytes; all operands/CFG; restore dominance; S/GP/SP/RA not written
PASS: ledger exact replay; installed/physical profile/outer stack nonalias UNPROVED; NO ISA/provider/MMIO execution
```

65,536 flag values 檢查精確 `0x8001` 關係；256 cases 檢查 byte 繞回；196,608 cases 僅是 U16 值 × 0／1／2 次八 byte merge-credit 的模數代數，沒有窮舉整個 accounting 公式或任意記憶體狀態。

八個 raw mutations 改動 loop bound branch、inclusive next branch、flag load offset、flag clear offset、prev link store offset、尾段 accounting store offset、prev-register write 及 saved-control restore source。變異直接進入推導，必須命中特定 instruction operand guard；未用全檔 hash 不符或任意 parser exception 充作通過。BLTU 在 CFG adapter 中僅以另一個雙 successor branch 標記共用拓撲演算法，原始 operands／方向仍獨立檢查。

後續重點：真實 payload／marker／node 寫入來源與保存期、實際 installed provider 綁定，以及 caller frame／資料不重疊條件。沒有因候選 helper 靜態閉合而解除這些未知。
