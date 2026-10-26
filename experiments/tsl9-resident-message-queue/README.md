# 訊息佇列與事件候選 C/C++

[English](readme.en.md) · [前一輪 task 回呼](../tsl9-resident-task-callbacks/README.md)

重建公開 WCH SDK V1.31 的訊息接收與其完整具名相依。**實機 ROM／RAM／ISA 相容性尚未確認，沒有新增可刷 BIN。**

| 本體 | 候選範圍 | bytes |
| --- | --- | ---: |
| 訊息接收 | 條件式 RAM `0x2000028C..0x20000314` | 136 |
| 移出節點 | Flash `0x4319C..0x431BA` | 30 |
| 設定事件 | Flash `0x4354A..0x4358A` | 64 |
| 清除事件 | Flash `0x4358A..0x435CE` | 68 |
| `tmos_stop_task` | Flash `0x439A8..0x43A14` | 108 |
| timer lookup | 條件式 RAM `0x20000314..0x20000332` | 30 |

[C/C++ 來源](resident_message_queue.c)共 **436 bytes／151 條指令**、40個正尺寸 FUNC、29筆重定位。C11／C++17 物件完全相同，還原原始位址編碼後每個 byte 均吻合；6條條件式 Xwchc 指令依官方定義及28個向量核對。來源需要原始暫存器與私有執行環境，不是一般可直接呼叫的 C API。

## 指令證據

- 接收函式沿 `0x20003198` 的鏈結串列尋找 task tag 相符的第一筆訊息，並繼續判斷是否存在下一筆相符訊息。存在時設定官方 `SYS_EVENT_MSG=0x8000`，不存在時呼叫真正的 `tmos_stop_task`； helper 的回傳值未使用。
- 移出函式更新 head 或 predecessor 的 next，清零所選節點的 `payload[-8]` word，將 `payload[-2]` byte 設為 `0xFF`。它不配置或釋放記憶體；該標記符合既有訊息釋放函式的 tag 檢查，但仍需有效所有權與沒有介入修改。
- 設定／清除事件先檢查 task-count byte `0x2000319D`，再透過 `0x200031E4` 的 halfword-array pointer 存取 `2×taskID`。設定做 OR，清除做 AND NOT；有效 task 返回0，超出範圍返回3。
- `tmos_stop_task` 查找 `0x200031E8` 串列中的 task／event，找到時清零節點 event halfword，之後仍呼叫清除事件。它忽略清除事件回傳值，依 lookup 是否找到節點返回0或6；不能把它改寫成單純的事件清除函式。
- 原始 MMIO `0x4002420C` 的保存／清零／還原與 `FENCE.I` 均保留；其實體語意、原子性與 IRQ 效果尚未確認。串列終止也未證明，需要有效且穩定的無循環串列。

## 部分連結與限制

與既有1828-byte 候選做實際非載入式 ET_REL 部分連結後，C／C++ 均為 **2264 bytes／805 條指令**、204個正尺寸 FUNC、149筆重定位。前一輪的訊息接收匯入由本輪真實函式解析；每個輸入 byte、符號與重定位皆保留。

**具名 UND 為0，不代表執行層閉合。** 原始 RAM／heap／callback 所有權、實機 ROM／ISA／IRQ／stack／Flash／OTA 仍未確認，尚未連入 APP。正式 APP byte 覆蓋維持 **95.54%**，不是功能完成度。前一輪固定256-byte Flash CPU 搬移的條件式證據保持不變。

證據：[audit-result-v1.json](audit-result-v1.json)、[summary.json](summary.json)、[原始 SDK 指令與向量](evidence-v1.json)。可考慮新增每個 task 的訊息積壓及 queue／event 一致性診斷，目前尚未實作。

## 重跑

需先具備 [spec-v1.json](spec-v1.json)／[evidence-v1.json](evidence-v1.json)與 audit 所列的原始 APP、SDK carrier、標頭／指令參考及前述候選的既有建置產物。SDK 原始輸入與 native 產物未隨此次提交提供，不會自動下載。使用固定雜湊的 Windows NDK LLVM，從專案根目錄執行：

```sh
python experiments/tsl9-resident-message-queue/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-message-queue/audit-v1.py --tool-dir "$LLVM_BIN" --link-trial composition-v1
```

trial 必須尚不存在；已有產物時，第一個改用 `--replay experiments/tsl9-resident-message-queue/build/native-v1`，第二個省略 `--link-trial`。未執行目標／HOST 模型／ISA 模擬，未連接硬體或廠商 API。
