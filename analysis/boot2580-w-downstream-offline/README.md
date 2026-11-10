# ID2580 W wrapper 下游：事件槽候選與尚未閉合的 buffer 路徑

## 可確定的邊界

只針對保存的 ID2580 BOOT，12288 bytes，SHA-256 `650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb`，base `0x1000` 是分析座標。[既有 wrapper 核對](../boot2580-w-wrapper-offline/README.md)的前置條件包含 `READ32(0x4013c)` 呼叫返回**恰好 1**。在記憶體正常、無並行改寫且 W 零資料路徑成立時，wrapper 構造 `55 7f 57 00 00 57` 於 `0x200090aa`，總長 6 存於 `0x200090a6`，offset 0 存於 `0x200090a8`。

| PC / raw | 行為 |
|---|---|
| `18a4 a305f700` | checksum byte 寫入計算出的 buffer 結尾 |
| `18c6 03a30705` | 從 `0x40050` 讀 32-bit 間接目標至 t1 |
| `18ca 03c5c107` | `lbu a0,124(gp)` |
| `18ce 8545` | `a1=1` |
| `18d2 0283` | 恢復 frame 後 `jr t1`，不建立新的 return address |

因此這個尾呼叫**沒有明確把 buffer 指標或長度當作 a0/a1 傳入**；不可將它直接說成 buffer send。被呼叫者仍可能存取其他暫存器或共用 RAM，本分析不假設其副作用。整段 `[0x1848,0x192c)` 228-byte SHA-256 `e9e1e949d9ddde3636ccb3cbf144c7dfdff67c243aa7754fc24a59d4c832d5dd`，指令語意沿用既有保存反組譯，並非獨立 ISA 執行。

## 獨立公開 resident 候選

[公開 SDK 版本比較](../../experiments/tsl9-wch-official-v140/README.md)及 V1.31 保存標頭將 `0x40034 + 7*4 = 0x40050` 宣告為 `tmos_set_event(taskID, event)`。稀疏 HEX 實際 slot 分別為：

| 參考 | HEX SHA-256 | `READ32(0x40050)` | 入口首 32 bytes |
|---|---|---|---|
| V1.31 | `11d849ac3333535b31dae1941afd8d59fa99ad7760de5c1e64bdfcc8c0024bb5` | `0x4354a` | `b747024083a6c72023a607200f100000373700200347d7196370e50237360020` |
| V1.40 | `5a4331c80f71dda3fc28e13481e185bda6877d8be7977cbfa0238c2f0baadf23` | `0x435d6` | `b747024083a6c72023a607200f100000373700200347d71e6370e50237360020` |

這是條件式跨映像對照：若 slot、ABI 和 resident 實作均相符，尾呼叫的兩參數對應 task ID 與事件 mask 1，**是排程請求而非直接 buffer 傳遞**。候選 scheduler 對已註冊 callback 的事件分派可參考 [V1.31 靜態研究](../../experiments/tsl9-resident-scheduler/README.md)，但尚未在 ID2580 閉合 task 註冊、event handler、讀取 buffer 的指令及其後的 provider。因此不能確認哪些後續函式送出該 buffer，也不能假定候選 slot 或 scheduler 安裝於實機。下一不可見邊界是 BOOT 所讀 `[0x40050]` 的實際內容；即使假設 SDK 候選成立，回到 BOOT callback 取用 buffer 的路徑在此仍未證明。

## 可重播核對與限制

```sh
python -B analysis/boot2580-w-downstream-offline/check.py
```

檢查完整 BOOT／兩份 HEX hash、HEX record checksum 與 sparse mapping、完整 wrapper hash、兩個 slot 值和兩個候選入口的 32 bytes。13 個 BOOT 和每候選 10 個單 byte 記憶體突變繞過整檔 hash，分別由 wrapper 或候選 raw gate 拒絕；只測固定來源的完整性，不執行或證明突變指令語意。未追完 BOOT 消費路徑，不能稱本任務已完整閉合。沒有連接設備、刷寫、執行目標 ISA 或觀察 BLE；不推斷實際傳輸、資料送達、ACK 或 Flash 持久化。
