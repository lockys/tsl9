# v4.1.60 本機清零、TX header 與 RX ID 投影

2026-11-26。原廠 APP `ID-2966-V4.1.60-decoded.bin`：76800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。全程本機離線，未執行韌體或操作設備。

## 結論

原指令 `0x16bd2..0x16bf8` 將 row 的首 halfword ID 編成：

```text
frame[0] = (ID >> 3) & 255
frame[1] = (ID << 5) & 255
frame[4] = length
```

把這個 frame 在合成記憶體中交給[原 RX guard](v4160-ingress-queue-chain.zh-TW.md) 重讀，得到 `ID & 0x7ff`。枚舉所有 65536 個 halfword ID 後，每個 11-bit ID 恰有 32 個原值投影至它。既有 RX 的 0–2047 ID 域可保留；超出該域的高五位不在這個 header 中。這是數值投影驗證，沒有執行傳送、外設或線路上的往返。

TX 的前置靜態 guard 只拒絕長度大於 8，故與 RX 僅接受 1–8 不同。長度 0 可到 TX 的 copy 呼叫點，但本次 RX frame 重讀會拒絕零長度；不能把 TX 走到該呼叫點等同 RX 接受或已傳送成功。

## caller 與本機 fill 的界線

radare2 RV32 離線解碼 `0x16b7c..0x16bf8` 顯示：

| 區段 | 已觀察的作用 |
|---|---|
| `0x16b7c..0x16b88` | row `+11` byte 要是 1 或 2，否則早退 |
| `0x16b8c..0x16b9a` | `[gp+84]` 所指結構的 `+4` byte，bit 3 設定時早退 |
| `0x16ba8..0x16bae` | row `+2` byte 載至 S1；大於 8 則拒絕，0–8 繼續 |
| `0x16bbe..0x16bce` | 直接呼叫 APP `0x8520(sp+18,0,11)` |
| `0x16bd2..0x16be6` | 寫上述三個 header bytes |
| `0x16bea..0x16bf8` | 當次讀取 `[0x4004c]`；A0=`sp+21`、A1=`row+3`、A2=S1，間接呼叫 |

前置 `0x8520` **是 APP 內的本機 fill 函式**，不是未知 resident clear。既有 C 位於 [fill_provider.c](../src/native/receive/fill_provider.c)。本次依 `(sp+18,0,11)` 執行其原指令：`0x8524` 走短長度路徑；`0x854a..0x8556` 計算並跳至 `0x856a`，按 offsets 10..0 反向寫零，清掉 `sp+18..28`，返回 `0x16bd2`。SP、S0/S1 不變。沒有以主機 memset 取代此流程。

未知 provider 仍是後續 `[0x4004c]`；在它執行前，payload 區域只有本機 fill 的零值，不能假裝已經從 row 複製 payload。

## 測試與前提

```powershell
python analysis/test_v4160_tx_header_roundtrip.py
python -O analysis/test_v4160_tx_header_roundtrip.py
```

依賴標準庫、原 BIN、同目錄已發布的 queue CPU 與 RX guard。一般與 `-O` 均通過：

```text
PASS: 65536 local-fill/TX/RX ID cases (2048 IDs x 32); 45 ID/length boundaries; zero length rejected on replay; 2 instruction mutations and default-scope guard detected
```

每例從合成的 fill 呼叫邊界開始，SP／S0／S1 分別指定有效的合成 stack、row 與 0–8 長度；不是從 TX 入口完整執行所有 guard。表格前三項 guard 的結論來自靜態解碼，沒有用這些切片測試宣稱已驗證完整 TX 函式。

測試先毒化整個 stack region，執行 fill 短路徑，驗證 11 次 store 的地址、值與順序，再執行 header 寫入直至未知 provider 入口。比較全部 stack bytes、三個 header stores、provider 完整 A0/A1/A2 與 link；不執行該 provider。隨後在相同 frame 以獨立合成 RX tag 重讀原 guard，檢查接受／拒絕及 ID 投影；沒有模擬資料真的穿過硬體。額外的 45 個邊界為 5 個 ID × 長度 0–8。

為重用既有 CPU，只增加 SUB、RV32 JALR、無號條件分支的解碼，以及可由子類明列的有限 PC 範圍。預設 queue 範圍保持原值，測試確認它仍拒絕 TX 位址。新子類只允許 fill 的短路徑與 header 區段，沒有聲稱可解譯 fill 的完整長度／對齊路徑。

兩個記憶體複本負向對照分別改錯 ID 右移量與 fill 的第一個 byte-store offset，必須被 header／fill footprint 檢查抓出。原 BIN 未改。既有 queue、call-contract、ingress、capture、transfer-chain、NV caller 測試也重新通過。

本批補強既有 C 重建的原指令證據，沒有增加重建 bytes 或重算覆蓋率。完整 TX 後續序列、實際 provider 身分及硬體傳輸仍未證；可接續查證 guard 到 fill 的資料流，或 provider 返回後的動作。
