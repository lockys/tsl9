# v4.1.60：索引回呼在兩版候選 resident 中只登記，不直接呼叫

接續[初始化順序](v4160-app-event-selector-init-order.zh-TW.md)。原 APP `0x17c1e..0x17c30` 從 `s0+128` 取目標（`s0=0x40000` 時為 `[0x40080]`），把 `0x176f8` 傳給該目標，返回後把低 byte 存到 `gp+379`。

| 候選 | `[0x40080]` | 48-byte 函式內的 callback store |
| --- | --- | --- |
| WCH V1.30 | `0x43afe` | `0x43b22` |
| WCH V1.31 | `0x43c4e` | `0x43c72` |

兩個函式各 16 條指令，只有偏移 `+7`、`+23` 的 bytes 不同，分別是狀態基址及表指標載入的立即數。承接 [V1.31 Xwchc 解碼](callback-901a-sdk-registration-static.zh-TW.md)，在同樣的指令解釋和正常記憶體存取下，舊 count 小於 capacity 時更新 count、把輸入 `a0` 存到 handler table 並回傳舊 count；否則跳到回傳 `255` 的分支。兩個函式都沒有直接或間接呼叫該 handler。通用反組譯器會把部分 WCH 壓縮資料指令顯示成浮點存取，不能以該輸出推定暫存器與記憶體語意。

因此，若 APP 的 slot 實際指向其中一個候選，這一步**只登記，不同步執行 `0x176f8`**；這不排除其他上下文在登記後、直接寫零前派發事件，也未證明實際 ROM 身分或登記成功。下一步對照候選 scheduler 與 APP 啟動路徑，確認第一次可辨識的派發入口相對於直接寫零的位置。

Python `-O` 通過 APP 與兩候選 SHA-256、兩個 slot word、兩段函式的容量分支、返回及呼叫指令檢查。候選 SHA-256：V1.30 `8fd279d4bc08bea74625e0ef3b8ca873746a84bf430c46a7565482effd96a04c`；V1.31 `133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22`。未連設備，未修改原 BIN 或正式來源。
