# callback 0x901a 原址連結實驗

執行 `python experiments/callback-901a-original-link/check.py`；預設使用 Android NDK 27.1.12297006 Windows LLVM，可用 `--ndk-bin PATH` 指定工具目錄。只在暫存目錄產生物件和 ELF，不修改正式來源。

從 `src/native/receive/callback_table.c` 擷取完整的 `[0x901a,0x907a)`，按十個基本區塊以 function-sections 連結在原 VA；檢查 ELF 各 symbol 的位置、大小及整段 96 bytes，與 SHA-256 固定的 V4.1.60 decoded APP（base 0x8000）逐 byte 比較。區塊間 fallthrough 與 branch relocation 都必須按此順序解析；單個 C 區塊並不是一般獨立可呼叫函式。AUIPC 的立即數是來源中固定編碼，這次只在指定原址驗證結果，並非可重定位資料依賴證明。

來源依賴：實驗直接編譯上述來源的前綴（含巨集，截於下一入口標記），不是從參考映像轉寫 `.byte`；檢查同時禁止常見的原始位元組／指令資料 directives。這是混合 C 與 inline assembly 的重建，而非全 C 或純語意模型。連結腳本只排序編譯物件的 executable function sections，未嵌入參考 bytes。離線參考映像只用於雜湊及最終比較。這個檢查並非所有可能編碼方式的通用防偽審計。

額外的人工 caller stub 是獨立組譯的可執行 code object，不是原廠 caller 的證據：其 `call` object relocation 必須指向 `tsl9_callback_table_entry_901a`；連結後解碼 AUIPC/JALR 並確認目的地是該 symbol 的 0x901a。逐一核對 callback object 五筆 executable-section relocation 的 offset、種類、目標 symbol 和 addend，並核對十個 linked symbol 位址及大小。0x9058 的 `c.jalr a3` 是間接呼叫，目標取決於記憶體，並未由這個直接 caller stub 或 linker 證明。

C 和 C++ 各重編三個來源負例：迴圈上限 15 改 14（0x9024 不符）；0x902c 分支目標由 0x9070 改 0x9066（object relocation 審計及 linked bytes 均拒絕）；同一分支由 `c.beqz` 改 `c.bnez`（0x902d 不符）。突變只修改暫存來源，不修改輸出 ELF；各測試仍跑完整連結和相同 byte gate。

這只是離線 linker/bytes 證據；沒有執行目標、模擬或硬體測試，不證明註冊可達、RAM、ABI、整體映像或實機功能。
