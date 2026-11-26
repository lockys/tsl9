# v4.1.60：候選 timer lookup／clear-event 的條件性靜態合約

日期：2026-11-26。承接 [cancel-provider 靜態合約](v4160-cancel-provider-static.zh-TW.md)，展開參考 V1.31／V1.40 的兩個完整 leaf，合計 196 bytes。本輪沒有新增 C 還原覆蓋率，也未證明實機 installed resident 或實體 ISA profile。

## 證據與重播條件

- [檢查器](check_v4160_timer_helpers_static.py) 逐 byte 固定四個本體、解碼 operands、建立封閉 CFG／SCC、列出 GPR 寫入集合，並精確重播 [JSON ledger](v4160-timer-helpers-static.json)。預設不寫檔；`--write` 僅可建立不存在的 ledger。
- APP 固定為 76,800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。候選 carrier、SDK header 身分檢查沿用前一檢查器；lookup 的完整 30-byte 範圍另受第一段 startup copy 的來源與目的範圍檢查約束。這只建立條件性 load-image 映射，不代表 loader 或最終 RAM 已被執行、觀察。
- 四份已保存 LLVM 原始碼／測試檔均檢查 SHA-256 與 Git blob SHA-1；名稱與 digest 在檢查器 `PINS` 及 ledger `sources`。它們是各自固定內容的參考檔，沒有證明屬於同一 compiler build／revision。
- 解碼 profile 明示為 `conditional-LLVM-Xwchc-RVInst16CL-GPRC`。LLVM 的欄位宣告與 28 筆已保存 encoding vectors 支持此 profile 下的解讀，不能單獨證明目標晶片採用它。未呼叫 assembler、下載工具或執行任何目標指令。
- 所需候選 carrier、SDK header、LLVM 參考檔位於本機 `analysis/wch-resident-candidate-2026-10-21/`；此目錄未隨本次提交發布。僅 clone GitHub repo 不足以重跑，仍需具備這些 digest 相符的本機輸入，以及前一檢查器與其 binding ledger 模組。

## 完整本體與來源

下列區間終點均不含。

| 候選 | lookup flash source → RAM | lookup SHA-256 | clear-event flash | clear-event SHA-256 |
| --- | --- | --- | --- | --- |
| V1.31 | `0x40584..0x405a2` → `0x20000314..0x20000332` | `3dbc188eb9ab2d30be1a30431a4e29a19fa7bbc0b21326dc7accd6d73913e1e8` | `0x4358a..0x435ce` | `1dc75e6d3f02458afbbaebd2a0fe3656a24b3c82b9c17066f210fe3f9940c38e` |
| V1.40 | `0x405c4..0x405e2` → `0x20000314..0x20000332` | `fd479d64abd9a70599e2a32ecc5b0f66fda66c4345890568f90959997842c6b6` | `0x43616..0x4365a` | `18228e82f425e14ada63b8de3a47adf76c428db874429a6a087e37584cb54066` |

lookup 每份 30 bytes／11 instructions；clear-event 每份 68 bytes／21 instructions。只有明確檢查的 relocation／RAM operand 欄位可在 template 比對時正規化，並另比對完整本體 hash。

## Xwchc 欄位解讀

所選 profile 將四個關鍵 word 解作：

| word | 解讀 |
| --- | --- |
| `0x23ba` | `qk.c.lhu a4, 2(a5)` |
| `0x2398` | `qk.c.lbu a4, 0(a5)` |
| `0x211a` | `qk.c.lhu a4, 0(a0)` |
| `0xa10e` | `qk.c.sh a1, 0(a0)` |

這些位置與通用解碼器的 FLD／FSD 顯示衝突，不能直接採信通用助記符。檢查器依 LLVM 的 GPRC（x8..x15）、opcode quadrant 與立即數 bit 配置解碼；profile 不符或輸入不是真正 uint16 時拒絕。

## lookup：第一筆 task／event 完全相等的節點

head pointer slot：V1.31 `0x200031e8`；V1.40 `0x20003238`。讀出 U32 head，零指標返回零；非零時先讀 `U16[node+2]` 與完整 A1 比對，只有相等才讀 `U8[node+0]` 與完整 A0 比對。第一筆兩欄皆相等者返回 node；未命中則以 `U32[node+12]` 前進，沒有清除 pointer bit 0，也沒有 event mask 交集判定。

讀取的欄位僅能支持 offset 0／2／12 與寬度，不能據此確定整個 node 大小、所有權或實際資料來源。未知指標可落在何種記憶體仍未證明。

CFG 有一個七節點循環 SCC：`0x2000031c, 0x20000322, 0x20000324, 0x20000328, 0x2000032a, 0x2000032e, 0x20000330`。沒有 iteration bound 或 cycle detection；若可讀且穩定的鏈結在未命中節點形成循環，不能保證返回。本輪沒有建立或遍歷任何 runtime linked list。

完整 GPR 寫入集合為 A0、A4、A5；無 store、nested call 或 stack 操作。沒有固定 MMIO operand，但未知 node pointer 的讀取地址仍可能指向 MMIO，不能宣稱所有可能讀取均無裝置副作用。

## clear-event：先控制字，再 unsigned task bound

兩個本體皆先讀取並保存 `U32[0x4002420c]`、寫零、`FENCE.I`，之後才讀 task count byte。無效 task 也經過這個控制字前置路徑。

| 候選 | task count byte | event table pointer slot |
| --- | --- | --- |
| V1.31 | `0x2000319d` | `0x200031e4` |
| V1.40 | `0x200031ed` | `0x20003234` |

- 完整 unsigned A0 ≥ U8 count：不讀 table pointer／entry，恢復控制字後 A0=3 返回。count=0 拒絕所有 task；count=255 時 task=255 仍無效。
- A0 < count：讀 table pointer，entry address 為 `(U32[table_slot] + 2*A0) & 0xffffffff`。讀 entry U16，寫回 `old_U16 & (~input_A1 & 0xffff)`，恢復控制字後 A0=0 返回。

以上恢復與返回均以正常指令語義、有效存取及沒有外部干擾為前提；不證明 pointer 非零、對齊、可存取範圍、加法不繞回，也不證明 MMIO read／write 的硬體效果或例外後恢復。

完整 GPR 寫入集合為 A0..A5；CFG 無循環、無 nested call／stack 操作。兩個 leaf 在所選 profile 的正常返回下都未寫 S0..S11、GP、SP、RA 或 T registers，因而可支持外層 stop-task 的 live S0..S3 保存條件。這不延伸至尚未展開的 deallocate private helper `0x20000110`。

外層 stop-task 的 0／6 返回與「lookup 未命中仍呼叫 clear-event」沿用前一合約；clear-event 的 0／3 返回在該外層未被用作最終狀態。不能把這兩層 status 混為一談。

## 本輪離線驗證

從 repo 根目錄，以具備上述本機輸入的 Python 環境執行：

```text
python analysis/check_v4160_timer_helpers_static.py
python -O analysis/check_v4160_timer_helpers_static.py
```

兩種模式均實際輸出：

```text
PASS: 28 saved LLVM vectors; 8192 operand roundtrips; 64 bit mutations (12 invalid/52 different); profile/type guards
PASS: 65536 byte task/count pairs; 1024 high-word rejects; 983040 U16/mask algebra cases; 7 specified raw mutations
PASS: four complete leaf bodies, 196 bytes; lookup cycle and clear-event bounds; selected-profile GPR preservation
PASS: ledger exact replay; installed/physical-profile identity UNPROVED; NO ISA/provider/MMIO execution
```

8192 組 round-trip 涵蓋四種 encoding 的 GPRC／合法立即數組合；另對四個關鍵 word 作 64 次逐 bit 改動。U16 algebra 僅窮舉 65,536 個 old value × APP 的 15 個單 bit masks，並非所有任意 input A1。另有 65,536 組 byte task/count 與 1024 組帶高位 task 的 unsigned 關係檢查，均屬 host algebra，不是目標 ISA 執行。

七種指定原始碼變異直接進入合約推導，分別改動 lookup event/task/next 欄位、event branch、count 讀取寬度、table stride、entry store offset；必須由各自指定的 operand guard 拒絕，未以完整檔案 hash 不符或任意 parser exception 充作通過。

仍待追查：allocator 私有 callee `0x20000110`、真實 payload／node 寫入來源與保存期，以及實際 installed 綁定。這些候選靜態結果不會解除其不確定性。
