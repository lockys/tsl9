# Task transition、parser 與訊息傳遞鏈

[English](readme.en.md) · [前輪 initializer](../tsl9-resident-init-final/README.md) · [原 task callbacks](../tsl9-resident-callback-registration/README.md)

[C/C++](resident_task_transition.c) 新增 **6 個完整本體／1,378 CODE bytes／479 指令**。實際 C11／C++17 物件相同，83 個正尺寸 FUNC、69 relocations（55 direct controls＋7組 HI／LO）。原始位址正規化後每個 byte 相同，17 個 Xwchc ports 經原始 encoding definitions／52 個官方正例核對；不是恢復出的原廠 C 原始碼。

| 完整範圍（半開） | Bytes／指令 | 自身 frame | 本輪作用 |
| --- | --- | --- | --- |
| `0x5F0D2..0x5F234` | 354／121 | 80 | 原 task 的狀態轉換、輪詢與後續設定 |
| `0x5EE98..0x5F0D2` | 570／191 | 48 | 依原始 buffer／record 條件解析、分支及訊息請求 |
| `0x6A79E..0x6A7BC` | 30／9 | 0 | stack／A6／A7 寬度正規化後，無 link 尾跳 builder |
| `0x52906..0x52A02` | 252／98 | 80 | 配置、填入欄位、複製後，釋放 frame 並尾跳 send |
| `0x43208..0x4329A` | 146／50 | 16 | 原候選 `tmos_msg_send`：檢查、排入佇列、事件請求 |
| `0x2000021C..0x20000236` | 26／10 | 0 | 依 metadata next pointer 接到 linked queue 尾端 |

每個 CFG 的所有指令均可到達，自身 frame 在正常出口平衡。沒有把 RET 後仍可到達的分支切掉；相鄰函式未選入。原 register／call／return ports 保留，不是 hosted C 函式庫。

## 實際 caller 與原始效果

原 task `0x60516` 在 `0x606B4`／`0x60708` 呼叫 `0x5F0D2`，相關 state byte comparison 為165（record+10）。task root 重新讀取 record pointer `0x20003438`，從 `0x2000353C` 取得 base，於 `0x5F112/0x5F114` 反覆讀 base+100，直到該 word 為0。保留所有輪詢、寫入寬度、mask 與順序；**不推定實機暫存器意義或輪詢必定結束**。

`0x5F11C` 寫入 original word AND `0xFFFFDFFF`；之後 base pointer 會重新讀取，`0x5F138` 把先前讀得的 original word 寫入新 base+12。不假設兩次 base 相同，也不把這段當作已證明的原子操作。RET `0x5F226` 後的 `0x5F228..0x5F234` 重試分支完整保留。

## Wrapper、stack arguments 與訊息配置

`0x6A79E` 對 incoming SP+0／+4／+12 分別以 unsigned halfword／byte／byte 讀取，再以 word 寫回；A6／A7 取低8位，接著無 link 跳 `0x52906`。builder 配置80-byte自身 frame 後，讀 SP+80／84／88／92／96，對應 caller SP+0／4／8／12／16，不是自身 frame 內的新欄位。

builder 的配置長度為 **36＋unsigned8 length（最多291）**；實際配置成功、可用 heap／buffer／callback 契約仍未證明。配置返回 null 時走原 restore／RET，不呼叫 send；非 null arm 保留三次 copy requests：

| 配置結果相對 offset | 長度 |
| --- | --- |
| +10 | 6 |
| +25 | 6 |
| +36 | length |

prefix 的其他原 stores、+31 length 與 +32 pointer 完整保留。逐一解碼所有 stores／copy extents 後，**prefix byte21 沒有在 builder 中被明確寫入**；未觀測其值，也未證明 allocator 或 callee 是否初始化它，不宣稱洩漏或錯誤。成功路徑在 `0x529DE` 釋放80-byte frame，`0x529E0` 尾跳 send。

## Send、queue 與事件請求

官方候選 header 的 `tmos_msg_send` 為 jump-table slot12；實際候選 `0x40064` 的函式指標 word 為 `0x43208`，不是跳躍指令，兩者均核對。編碼返回路徑為 null pointer→5、task rejection→3、metadata rejection→5、enqueue／event request 路徑→0；這是指令結果，不是實機傳送完成證明。

send 保存 `0x4002420C` word，寫0、FENCE.I，並保留各結果路徑的原 restore requests。成功路徑寫 message−2 的 task metadata、使用 queue root `0x20003198`，然後請求 event bits `0x8000`。**硬體鎖定／原子性、callee effects、事件實際交付均未證明。**

RAM enqueue 將 incoming message−8 next word 設為0；空 queue 寫 root，非空 queue 逐個讀 next 到末端。沒有新增遍歷上限或修正原邏輯；cycle／alias／無效指標下是否終止、安全仍未知。其完整 source `[0x4048C,0x404A6)` 對應 RAM `[0x2000021C,0x20000236)`，落在前輪 loader 的完整 first-copy 區間；不是安裝 ROM 的身分證明。

## 驗證與使用

[task_abi.c](task_abi.c) 只編譯驗證 RV32 widths、36-byte prefix、291-byte數值上限與 stack offsets；C／C++ 物件相同、allocated bytes=0，沒有 runtime provider。

實際非載入 ET_REL 組合為 **22,786 CODE＋256 DATA／7,810 指令**，1,460 正尺寸 FUNC、1,109 relocations。所有 input bytes／symbols／relocations 保留、原始 CODE 位址不重複，兩個獨立 ELF readers 一致。補上一個原 task 缺口，具名依賴 **9→8**；本輪7個 imports 均有前輪真實 providers，沒有新具名依賴、stub 或 opaque call。間接／transitive memory effects 並未因此封閉。

[證據](evidence-v1.json) · [完整驗證](audit-result-v1.json) · [摘要](summary.json)

```sh
python experiments/tsl9-resident-task-transition/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

需要固定本機 APP／SDK、前輪 native artifacts 與 Windows NDK LLVM；無下載，其他平台未驗證。APP保持159 C/H、95.54%位元組覆蓋率，**不是功能完成率**。4-byte啟動來源缺口、實體 ROM／RAM／ISA／IRQ／Flash／OTA 相容性及 binding 前無 dispatch 仍開放。

未連入 APP、未產生 BIN，沒有 target／HOST model／ISA／硬體執行；**尚未成功重建可用替代韌體**。唯讀離線 queue-path／rejection 診斷是後續功能候選，尚未實作，不新增 RF、車輛控制或 live queue 寫入。
