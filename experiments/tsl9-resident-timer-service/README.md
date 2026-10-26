# Timer 串列服務候選 C/C++

[English](readme.en.md) · [真正的主排程](../tsl9-resident-scheduler/README.md) · [佇列／事件](../tsl9-resident-message-queue/README.md)

主排程的 `0x20000872` 呼叫 `0x200004FA`。本輪重建 `0x200004FA..0x2000061A` 的完整 **288 bytes／103條指令**；後面的 `0x2000061A` 是另一個真實入口，未混入。**這是公開 SDK V1.31 候選，實機 ROM 尚未確認。**

[C/C++ 來源](resident_timer_service.c)含32個正尺寸 FUNC、24筆重定位。C11／C++17 物件完全相同，還原原始位址編碼後全部 bytes 吻合；3條條件式 Xwchc byte／halfword 指令依官方定義與28個向量核對。保留原匯入符號 `tsl9_candidate_external_ram_200004fa`，由真實本體解析它，沒有 alias 或 stub。

## 已確認的流程

| timer 節點欄位 | 觀察到的 offset |
| --- | ---: |
| task byte／event halfword | 0／2 |
| interval／deadline／next word | 4／8／12 |

- 從 `0x200031E8` 走訪串列。event=0 的節點被移出並交給真實 heap-free；這補上先前 `tmos_stop_task` 清零 event 後的延後回收路徑。只有服務實際執行時才回收，沒有保證回收時機或串列終止。
- 非零 event 路徑呼叫 `0x200031E0` 的 clock callback，函式內沒有 null 檢查；已確認的主排程呼叫路徑有先檢查，但仍需指標保持穩定。clock 單位、回傳範圍及副作用尚未確認。
- 以 runtime word `M=*(0x20003238)` 算 unsigned elapsed：`now>=deadline ? now-deadline : M-deadline+now`。elapsed≤29999999時走到期路徑，呼叫真實事件設定函式；**其回傳值未使用，不能推定事件已成功排入**。
- interval=0 的到期節點會移除並釋放；否則只做一次 unsigned deadline+interval，發生32-bit wrap 或 sum≥M時只減一次M。**不把它改寫成一般 `%M` 或多週期補發。** 這些數字尚未換算為秒或毫秒。
- 未到期時，僅在 idleCB 非空的分支更新 `0x200031AC` 的較小 future-delay。非空串列走訪結束後做 `cache<=1 ?0:cache-1`；入口串列已空時直接返回，不做這個 post-pass。

自身48-byte frame 在共同返回點平衡。已選取的主排程與 timer 自身 frame 合計80 bytes，**不含 clock／其他 callee、重入或 IRQ stack 預算**。節點至少16 bytes 有效、穩定無循環串列、所有權與正常 callee 返回仍是前提。

## 實際部分連結

加入既有2750-byte 候選後，C／C++ 非載入式 ET_REL 均為 **3038 bytes／1074條指令**、279個正尺寸 FUNC、205筆重定位。scheduler 的 timer 匯入及本輪的 heap-free／event-set 匯入均由真實本體解析；每個輸入 byte、符號與重定位皆保留。

仍未提供 RAM `0x2000061A`／`0x20002610` 與 Flash `0x63DD0`，clock callback 亦未閉合。保留先前4-byte 啟動來源缺口，未連入 APP，沒有新增 BIN。實機 RAM／ROM／ISA／IRQ／stack／Flash／OTA 仍待確認；APP byte 覆蓋維持 **95.54%**。

證據：[audit-result-v1.json](audit-result-v1.json)、[summary.json](summary.json)、[原始指令](evidence-v1.json)。Timer 延遲、clock 範圍及延後取消診斷值得考慮，目前尚未實作。

## 重跑

需先具備 [spec-v1.json](spec-v1.json)／[evidence-v1.json](evidence-v1.json)與 audit 所列原始 APP、SDK／標頭／指令參考及既有產物。SDK 原始輸入與 native 產物未隨此次提交提供，不會自動下載。使用固定雜湊的 Windows NDK LLVM，從專案根目錄執行：

```sh
python experiments/tsl9-resident-timer-service/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-timer-service/audit-v1.py --tool-dir "$LLVM_BIN" --link-trial composition-v1
```

trial 必須尚不存在；已有產物時，第一個改用 `--replay experiments/tsl9-resident-timer-service/build/native-v1`，第二個省略 `--link-trial`。來源需要原始暫存器／私有執行環境；沒有執行目標／HOST 模型／ISA 模擬、存取硬體或廠商 API。
