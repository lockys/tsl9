# RAM-JT0 主排程候選 C/C++

[English](readme.en.md) · [註冊函式](../tsl9-resident-task-registration/README.md) · [佇列／事件](../tsl9-resident-message-queue/README.md)

公開 SDK V1.31 的 `TMOS_SystemProcess` 經 RAM 表第0項呼叫。實際初始化指令把 **`0x200007D0`** 寫入 `0x20000000`；先前的 `0x200004FA` 是本體呼叫的另一個函式，並非此表的主入口。**這仍是公開候選，裝置 ROM 尚未確認。**

[C/C++ 來源](resident_scheduler.c)重建 `0x200007D0..0x20000986` 的完整 **438 bytes／150條指令**，39個正尺寸 FUNC、30筆重定位。C11／C++17 物件完全相同，還原原始位址編碼後全部 bytes 吻合；14條條件式 Xwchc 指令依官方定義與28個向量核對。來源需要原始暫存器與私有執行環境。

## 表格與程式碼來源

- 官方 header 定義 `RAM_BASE_ADDRESSS=0x20000000`；`TMOS_SystemProcess`／BB IRQ／LLE IRQ 分別使用 RAM 表第0／1／2項。
- V1.31 初始化的 `0x6DE1C`／`0x6DE26`／`0x6DE3C` 分別寫入 `0x200007D0`／`0x2000251C`／`0x20002E34`。表格是明確的指令寫入，不能把程式碼 copy 的位移公式套到 RAM0。
- 在 seed 與第一段 word copy 正常完成的前提下，排程來源為 Flash `0x40A40..0x40BF6`，位於已捕獲的完整第一段 copy 範圍內。後面的第二段 copy 與清零範圍在數值上不覆蓋本體或三個表項。
- 既有 V1.31 稀疏來源契約仍記錄第二段 copy 的 `0x6EB2C..0x6EB30` 缺4 bytes。後續清零不能證明該讀取完成；**沒有補零或宣稱完整啟動成功**。另核對234 bytes 的啟動／seed 片段，本輪未把它們編成新的 BOOT。

## 事件派送

- 主排程以 `0x2000319C` 的 task index 與 `0x2000319D` 的註冊數尋找事件。取出 event halfword 後先清零該 slot，再把 task index／event 放入 A0／A1，從 handler-array 呼叫函式指標；這裡沒有 null 檢查。
- 呼叫前把 `0x200031DC` 的清除遮罩清零。handler 返回後，**重新讀取目前 task index**，將 `(returned_A0 & ~live_clear_mask) | live_pending_event` 的低16位寫回重新選取的 slot。不能假定 callback 重入或並行修改時仍是呼叫前的 slot。
- `tmos_stop_task` 操作的共享 halfword 與這個 clear-mask 相吻合。四處不透明 callback 的生命週期與副作用未閉合。
- 完整局部 CFG 中每次正常進入最多到達一次 registered-handler 呼叫點；這不包含 callback 再次呼叫排程的重入。自身32-byte frame 在正常返回與外部 tail 均平衡，**不是 callee／全程 IRQ stack 預算**。

## 部分連結與限制

加入既有2312-byte 候選後，C／C++ 非載入式 ET_REL 均為 **2750 bytes／971條指令**、247個正尺寸 FUNC、181筆重定位，每個輸入 byte、符號與重定位皆保留。

四個真實具名相依仍未提供：RAM `0x200004FA`／`0x2000061A`／`0x20002610` 與 Flash `0x63DD0`。未建立 stub，未連入 APP，沒有新增 BIN。RAM／callback 所有權、完整啟動、原子性、IRQ／stack、實機 ROM／ISA／Flash／OTA 仍未確認；APP byte 覆蓋維持 **95.54%**。

證據：[audit-result-v1.json](audit-result-v1.json)、[summary.json](summary.json)、[原始指令與啟動片段](evidence-v1.json)。事件合併／callback 重入診斷值得考慮，目前尚未實作。

## 重跑

需先具備 [spec-v1.json](spec-v1.json)／[evidence-v1.json](evidence-v1.json)與 audit 所列原始 APP、SDK／標頭／指令參考及前述候選的既有產物。SDK 原始輸入與 native 產物未隨此次提交提供，不會自動下載。使用固定雜湊的 Windows NDK LLVM，從專案根目錄執行：

```sh
python experiments/tsl9-resident-scheduler/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-scheduler/audit-v1.py --tool-dir "$LLVM_BIN" --link-trial composition-v1
```

trial 必須尚不存在；已有產物時，第一個改用 `--replay experiments/tsl9-resident-scheduler/build/native-v1`，第二個省略 `--link-trial`。沒有執行目標／HOST 模型／ISA 模擬、存取硬體或廠商 API。
