# 參考 carrier 的 `[0x40068]`

`reference_free_slot.py` 固定兩份本機參考 carrier 的完整 SHA-256、slot 指標、78-byte 函式本體，並解碼 AUIPC/JALR 目標：

| 參考版本 | slot 指標 | 呼叫位址 | helper 目標 |
|---|---:|---:|---:|
| V1.31 | `0x431ba` | `0x431f8` | `0x20000110` |
| V1.40 | `0x43246` | `0x43284` | `0x20000110` |

兩者各針對 slot 與本體共 82 個 byte 變造；這些變造**由完整 carrier 雜湊擋下**，不是獨立語意測試。缺少 carrier 時輸出 SKIP 並以非零狀態結束，不視為通過。普通與最佳化 Python 均通過。

先前靜態審查指出兩候選本體在巢狀 helper 呼叫前不直接使用或覆寫 a1，但本驗證只是固定 bytes 與解碼目標；**未執行或驗證 helper**。參考 carrier 並非 TSL9 已安裝 ROM 的實測資料，不能以此推論裝置實際 provider 及其完整行為。

執行 `python -I -B experiments/v4160-b0b0-pure-c-candidate/reference_free_slot.py`；在隔離來源快照可用 `--root` 指向包含 carrier 的工作目錄。
