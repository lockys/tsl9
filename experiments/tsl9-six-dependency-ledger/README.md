# 六個未解析依賴：靜態用途與邊界

[English](readme.en.md)

此表整理目前原位址 C/C++、既有原始 BIN 指令對照與條件式分析；位址是 V4.1.60 的分析座標。用途屬靜態觀察或有明示前提的推論，並非實機執行結果。六個 symbol 仍未解析；本紀錄不新增 alias、函式、資料或 BIN。

| 依賴 | 已觀察的使用 | 尚未證實 |
| --- | --- | --- |
| `0x40000` | reset 的 `0x18730` 以不寫入返回位址的跳轉交出控制。候選 SDK 啟動鏈可進行 RAM 初始化與 `MRET`。 | 原機該位址是否與候選 SDK 相同、ABI 及實際啟動完成。見 [slot2 啟動](../tsl9-resident-slot2-startup/README.md)。 |
| `0x14056` | `0x8A48` 以連結呼叫此入口；呼叫前 `a0=s3`，`a1=uint8(GP+0xA4)`，`a3=uint16(GP+0x8E)`，`a2` 由 PC-relative 指令計算。見 [incoming_protocol.c](../../src/native/receive/incoming_protocol.c)。 | 入口本體位於既定排除區；參數語義、`a2` 指向物件、返回值及副作用均未確認。 |
| `0x1AB48` | `0xA158` 按 `base+2*counter` 讀 halfword；兩個直接寫入使用 `(old+1)&3`。 | 讀取前全域 counter 一定為 0–3 尚未證明；若成立，現有 8B 窗口覆蓋該次讀取。見 [counter 分析](../tsl9-input-counter-data/README.md)。 |
| `0x1A078` | `0xCF5A` 按 `base+16*mode+column` 讀取，column 經 `&15`；模式 0–5 的條件資料列已納入來源。 | setter 可接收任意低 byte，局部 0–5 不等於全域值域；完整 provider 尚未建立。見 [mode 整合](../tsl9-record-mode-row-integration/README.md)。 |
| `0x1A638` | `0x12046..0x1205E` 按 `base+6*(2*channel+state)` 準備 6-byte 比對，迴圈 channel 為 0–3。 | state 每次讀取均為 0 或 1、實際 ROM slot 為候選比較函式及實體功能，均未證明；條件成立時現有 48B 窗口涵蓋比對。見 [sequence 分析](../tsl9-sequence-pattern-data/README.md)。 |
| `0x1A69C` | `0x131AA` 把此位址放入 `a1`、長度 4 放入 `a2`，並以 `a0=*(GP+0x54)+12` 呼叫由 `0x4004C` 取出的間接目標。見 [settings_defaults.c](../../src/native/startup/settings_defaults.c)。 | 四 bytes 內容屬既定排除範圍；未讀取或輸出。間接目標身分、記憶體有效性及其是否複製資料仍須證明。 |

上述 register、位址公式與條件範圍不等於可達性或完整原始 C 宣告。不同版本的地址不能直接互換；目前沒有實機 ROM、RAM、IRQ 或 OTA 相容證據。
