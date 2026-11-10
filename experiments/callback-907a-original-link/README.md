# callback registration/cancel 原址連結實驗

執行 `python experiments/callback-907a-original-link/check.py`；預設 Android NDK 27.1.12297006 Windows LLVM，可用 `--ndk-bin PATH` 指定。需要同目錄樹的 `experiments/callback-901a-original-link/check.py`（共用工具設定及 object relocation parser），不可使用 Python `-O`。只在暫存目錄編譯、連結；不修改 candidate、不執行目標或操作硬體。

從 `src/native/receive/callback_table.c` 取巨集與 `[0x907a,0x9124)` 完整來源，NDK 以 C11、C++17 各自編譯為 source object，function sections 按十個區塊依序原址 link，不注入 reference bytes。核對每個 symbol 及大小，區段恰好 170 bytes，無 undefined symbols，並與 SHA-256 固定的 V4.1.60 decoded APP（base 0x8000，完整映像 SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`）逐 byte 比對；該範圍 SHA-256 為 `cd049b87b5048a5467868d04b256066222b8db194a0c4eb60d5d2d77cce05a17`。逐項核對三筆 branch object relocation 的位置、種類、目標、addend；連結器禁止 undefined symbols。

邊界：0x907a registration entry；0x9096 以固定 AUIPC/addi 計算 0x901a 並透過 slot 間接註冊，0x90a4 結束；0x90b0 cancel entry，0x90c6–0x9118 為其循環、清除、間接呼叫／tail transfer 與返回區塊；0x9124 不屬此範圍。各區塊依賴順序 fallthrough，不是各自普通 C 函式。固定 PC-relative immediate 及間接 slot 目標並非 linker symbol 綁定證明；本實驗未納入 0x901a 內容或 0x9124 之後。

每種語言均在暫存來源測試：180 改 179（0x9088 不符）、0x90c8 bne 改 beq（0x90c9 不符）、0x90d6 分支目標改 0x9118（relocation 與 bytes 不符）；缺失 branch 目標另驗證 linker 明確報 undefined 並失敗。正常版本均完整吻合。這是 C 與 inline assembly 混合的離線 bytes 證據，非純 C 重建、可重定位性、實際呼叫可達性、RAM、ABI 或實機功能證明。
