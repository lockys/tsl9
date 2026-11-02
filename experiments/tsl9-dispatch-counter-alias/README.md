# 命令路徑的 counter 指標別名條件

`0x142FC` 把 `GP+84` 的位址保存至 `s1`。若保存暫存器有效且前置呼叫正常返回，`0x14332..0x1433E` 讀取 `0x4004C` 槽及 `p=*(GP+84)`，並請求以 `(p, s0+24, 16)` 呼叫該槽。`0x14340..0x14350` 重新讀取 `p` 和槽，再請求 `(p+96, s0+59, 16)`。在槽符合候選 byte-copy、記憶體有效且不受干擾時，若第一個 p 恰為 `GP+172`，counter `GP+176` 會由來源的第 4 byte 覆寫；若第二個 p 恰為 `GP+80`，第二次複製會覆寫 counter。兩次 p 是分別讀取，不能假設值必然相同。

reset 的 `0x186BA..0x186DA` 將 128 bytes 從 `0x1AB60` 複製至 GP；初始 word `0x1ABB4` 為 `0x2000C29C`，對應 `GP+84`。若 GP 為 `0x20004000`、複製完成且兩次讀取都保持此值，目的區間分別是 `[0x2000C29C,0x2000C2AC)` 與 `[0x2000C2FC,0x2000C30C)`，均避開 counter、四個 sequence state 及指標儲存位置。這只排除該初始指標條件下的重疊，無法排除其他 writer 或指標後續變動。

這是具體的**條件式別名風險**，沒有證明 p 實際取上述值、命令路徑可達，或實機槽符合候選 copy。`0x1441C..0x14430` 另對 `p+4` 在條件下清除 bit 3；即使它與 counter 重疊，對原已介於 0–3 的值此操作不會使之超界。這不排除其他 writer。

`python experiments/tsl9-dispatch-counter-alias/verify.py --firmware <CANDIDATE_BIN> --r2 <R2_EXECUTABLE>` 核對固定映像雜湊、31 條指定指令及算術，包含變動指令的負例；不執行目標。原機 ROM、p 的有效範圍與全域 counter 上界仍待驗證。
