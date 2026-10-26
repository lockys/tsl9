# Task 註冊候選 C/C++

[English](readme.en.md) · [SDK 佇列／事件](../tsl9-resident-message-queue/README.md) · [條件式 RAM 配置](../tsl9-resident-task-layout-contract/README.md)

官方 slot19 的 `TMOS_ProcessEventRegister` 指向 `0x43C4E`，相鄰 slot28 的 `BLE_LibInit` 從 `0x43C7E` 開始。本輪重建中間完整的 **48 bytes／16條指令**，沒有選入相鄰函式。**實機相容性未確認，沒有新增可刷 BIN。**

[C/C++ 來源](resident_task_registration.c)含4個正尺寸 FUNC、2筆重定位。C11／C++17 物件完全相同，還原原始位址編碼後全部 bytes 吻合；3條條件式 Xwchc byte 指令依官方定義與28個向量核對。來源需要原始暫存器與私有執行環境。

## 行為與條件

- 讀取 `0x2000319D` 的 count byte 與 `0x2000319E` 的 capacity byte。若 count≥capacity，返回255且不寫入；否則把 count+1 寫回，將入口 A0 word 存到 handler-array+4×舊count，返回舊count。
- handler-array pointer 來自 `0x200031C4`。在穩定、有效的4×capacity-byte 陣列及沒有並行修改的前提下，成功路徑滿足 count+1≤capacity，也不會發生 byte wrap。若初始 count≤capacity，順序執行可保留此不變量；初始狀態已超界時，函式不會修復它。
- **函式未檢查回呼是否為 null 或可呼叫。** 指令順序為 `0x43C6A` 先寫 count，再由 `0x43C72` 寫 handler word；沒有編碼出的 gate 保存／還原或 FENCE 序列。成功回傳不能證明 callback 有效或註冊具有原子性。
- 若前一輪的容量29與三個內建註冊條件成立，則還有26次成功註冊的數值空間。這個例子仍要求 SNV 途徑後 count／指標未被修改；實際 IRQ 狀態與觀察順序未驗證。

## 實際部分連結

加入既有2264-byte 候選後，C／C++ 非載入式 ET_REL 均為 **2312 bytes／821條指令**、208個正尺寸 FUNC、151筆重定位。每個輸入 byte、符號與重定位皆保留；slot19 現有真實本體，但具名 UND 為0仍不代表執行層閉合。

未連入 APP；RAM／callback 所有權、原子性、完整 IRQ／stack、實機 ROM／ISA／Flash／OTA 仍待確認。APP 正式 byte 覆蓋維持 **95.54%**，不是功能完成度。可考慮新增序列化註冊與可呼叫 handler 診斷，目前尚未實作。

證據：[audit-result-v1.json](audit-result-v1.json)、[summary.json](summary.json)、[原始指令與官方綁定](evidence-v1.json)。

## 重跑

需先具備 [spec-v1.json](spec-v1.json)／[evidence-v1.json](evidence-v1.json)與 audit 所列的原始 APP、SDK／標頭／指令參考及先前建置產物。SDK 原始輸入與 native 產物未隨此次提交提供，不會自動下載。使用固定雜湊的 Windows NDK LLVM，從專案根目錄執行：

```sh
python experiments/tsl9-resident-task-registration/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-task-registration/audit-v1.py --tool-dir "$LLVM_BIN" --link-trial composition-v1
```

trial 必須尚不存在；已有產物時，第一個改用 `--replay experiments/tsl9-resident-task-registration/build/native-v1`，第二個省略 `--link-trial`。沒有執行目標／HOST 模型／ISA 模擬、存取硬體或廠商 API。
