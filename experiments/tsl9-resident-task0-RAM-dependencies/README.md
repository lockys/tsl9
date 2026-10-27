# Task 0 RAM 回呼的實際依賴

[English](readme.en.md)

以保留原暫存器情境與明示指令 port 的 C/C++，補齊前輪三個缺失 callee，另加入其共用 helper。**四個完整本體／1,892 bytes／626 條指令**；實機 ROM／RAM mapping 仍未確認。

| 候選原位址範圍 | Bytes | 自身 frame |
|---|---:|---:|
| `436A8..43728` | 128 | 32 |
| `20000D50..20001122` | 978 | 32 |
| `20001122..2000138E` | 620 | 32 |
| `200014C6..2000156C` | 166 | 48 |

RAM 本體依既有啟動 copy mapping 對照實際 SDK Flash bytes。完整 CFG 保留第一個 `ret` 後仍可達的分支、兩條釋放自身 frame 的尾跳，以及 26 個條件式 Xwchc 操作；不是一般 HOST 可呼叫 API。

`436A8` 僅接受 ID 0..15 且對應 callback word 非零的記錄。它以 task 0、`low16(1 << ID)` 查找計時記錄；找到時清除 event，將入口 A1 寫至計時記錄 `+8`。**查找返回 null 時也回覆 0，沒有更新該欄位**；ID 不合或空 callback 回覆 2。返回 0 不代表計時器確實更新或實體操作成功，時間單位仍未證明。

C11／C++17 物件相同，逐 byte 原位址重編碼、完整 CFG／frame、獨立 ELF readers 與非載入式合併通過。累計 **38,744 CODE＋392 DATA bytes／13,347 條指令**。前輪三個 UND 均由真實本體提供，仍有兩個更深層具名缺口：**`56972`、`2000156C`**；未用 stub 補齊。

新本體帶入 **11 個尚未串接的間接轉移**，所以目前部分 SDK 物件的範圍擴為 **62 處，其中 51 處有至少一種條件情境**。分母增加反映新增程式碼；不是功能完成率、缺失函式數，亦不涵蓋整份 APP 或未提供 callee 內的呼叫。

原 APP 靜態覆蓋率仍 **95.54%**。4-byte 啟動來源、實機晶片／ROM／RAM／IRQ／Flash／OTA 與完整功能相容性仍未證明。未執行目標、模型、模擬器或硬體，**未產生 BIN，尚不可宣稱可燒錄**。

功能候選：離線計時診斷同時呈現「查找是否命中、是否實際寫欄位、返回狀態」，避免只以 0 判定更新成功；目前僅提案。

[C/C++](resident_task0_RAM_dependencies.c) · [原始指令](evidence-v1.json) · [檢查器](audit-v1.py) · [收據](audit-result-v1.json) · [摘要](summary.json)

以保留的參考檔、物件與已核對 LLVM，在專案根目錄唯讀重驗：

```sh
python3 experiments/tsl9-resident-task0-RAM-dependencies/audit-v1.py --tool-dir "$LLVM_BIN"
```

Windows 可使用 `py -3`；公開文字收據不能替代原參考檔與建置產物。
