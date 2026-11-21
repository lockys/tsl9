# 斷線後何時釋出連線列？

原 APP 的 `0x1a548` 相對跳表項 6 指到 `0x11948`。RV32 編譯參考 SDK 標頭確認：`GAP_LINK_TERMINATED_EVENT == 6`，`gapTerminateLinkEvent_t.connectionHandle` 是偏移 +4 的兩位元組欄位。這與建立事件從 +10 讀 handle 不同。

從事件取 handle 後，依序跟 `R+2` 的半字比對（`R = 0x2000bfec + 12*i`，i 為 0、1、2）。第一個相等即選該列；三個都不等時 `0x11974` 跳到 `0x117f6`，不執行本段重設。比對沒有另外排除特殊 handle。

| 順序 | APP PC | 成功執行時的效果 |
|---|---|---|
| 1 | 0x1198e | 在 R 寫一個 word `0xfffe0080`。小端序為 `80 00 fe ff`，因此同一條指令已把 R+2 的 handle 設回 `0xfffe`。 |
| 2 | 0x11990 | 將 R+10 的單一 byte 設為零。 |
| 3 | 0x1199e | 呼叫 `[0x40048](R+4, 0, 6)`，要求將六個位址 bytes 填零。 |

與建立事件對讀：`0x10d9a` 以 handle `0xfffe` 識別空列，不以六個位址 bytes 是否全零判斷。因此 APP 寫回空列標記在先，並非等填零服務返回才釋出；兩者不是一次原子更新。本段沒有直接寫 R+11，也不能由呼叫參數推定實機服務成功或有其他工作在兩步間讀列。

離線驗證：原 BIN SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`；從跳表、三對 PC-relative 載入及 LUI/ADDI 立即數獨立重算分支入口、三個 handle 位址與 reset word。RISC-V 反組譯核對比較順序及三個更新步驟，未連裝置。
