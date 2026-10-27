# Task 0 時鐘／狀態回呼條件

[English](readme.en.md)

核對 **3 個完整既有 SDK 函式／1,816 bytes／592 條指令**，將剩餘 12 個間接轉移與原 APP 設定串接。本輪沒有新增目標 C/C++、編譯或 BIN。

| 類型 | 點數 | 條件式結論 |
|---|---:|---|
| Raw clock | 10 | 原非空 16-byte 時鐘設定已接受並複製、槽值穩定時，`200031E0 → 191C6` |
| Status | 2 | 已知 BLE 設定清零／複製後，`20003220` 維持零時，由原 guard 略過 `20000EC6`／`2000137A` |

`200031E0` 是這些呼叫直接讀取的 **raw-clock 槽**，不能改當成另一層 clock provider。原 APP `191C6` 的完整 90-byte 本體及設定／native 證據重新核對通過；MMIO 的實體意義、取樣一致性與頻率仍未證明。先前 heap 呼叫的狀態槽值、全程初始化順序及其他覆寫者仍未封閉。

重要執行前提：`20000F8E` 先讀時鐘，`20000F90` 保存結果；`20000F92` 重新載入指標，`20000F96` 再呼叫，`20000F98` 在值相等時跳回。**原碼沒有明示 retry 上限或 timeout；需要觀察到不同的時鐘值才能離開此迴圈。** 指標正確、零具名 UND 或本機比對通過，均不能證明迴圈會終止，也不能用固定回傳值的 stub 代替實際時鐘。

逐 byte 原位址重編碼、完整 CFG、自身 frame、有限 may-reaching-definitions 與原 APP 設定契約均通過。十個 raw-clock 指標與兩個狀態 guard 的全部來源保留在 [逐點清單](ledger-v1.json)。

**僅目前這份部分 SDK 物件的 63 個 register-transfer sites，各已有至少一種條件情境**（51 個目標／集合、12 個略過／呼叫者條件）。這不是所有 live 綁定、整份 APP、未選入程式碼或功能完成率的證明。

候選組合仍為 **40,874 CODE＋392 DATA bytes**；原 APP 靜態覆蓋率維持 **95.54%**。啟動來源 4 bytes、實機晶片／ROM／RAM／IRQ／Flash／OTA、時鐘活性與完整功能相容性仍未確認。未執行目標、模型、模擬器或硬體，**尚不可宣稱可燒錄**。

功能候選：更新前的唯讀時鐘活性與初始化診斷；目前僅提案，沒有執行硬體測試。

[檢查器](verify-v1.py) · [原始證據索引](evidence-v1.json) · [收據](verification-v1.json) · [摘要](summary.json)

以保留的參考檔、原物件及已核對 LLVM，在專案根目錄唯讀重驗：

```sh
python3 experiments/tsl9-resident-task0-clock-status-binding/verify-v1.py --tool-dir "$LLVM_BIN"
```

Windows 可使用 `py -3`；公開文字收據不能替代原參考檔或建置產物。
