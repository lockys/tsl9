# F030 純 C 狀態介面實驗（離線）

這兩個純 C 檔案只是可讀的有限假設，不是正式 owner 的替代品。`leaf.c` 只表達一次 byte store；`candidate.c` 接受標準 C 參數、寫入後呼叫 BD46 provider。標準 C 參數與 F030 進入時的私有暫存器狀態並非已證相同。

以假設 BIN base `0x8000` 讀參考映像 F030 視窗，原始 8 bytes 為 `23059400efc03fd1`：`sb s1,10(s0)` 後 `jal ra,0xbd46`。局部對照中，完整正式 `record_continuations.c` 的 BD46 在原址為 `170500201305b51c8280`。其 owner 仍含 inline assembly，選區連結及 provider 不代表整個映像已是純 C。

先前本機離線實驗以 manifest 的 `queue-consumer-a0-a5` C11／C++17 profile 編譯這兩個候選，並使用真實 BD46 owner 的選定 section：

- store-only leaf 沒有指向 BD46 的 call relocation，選區連結的 GC 因此丟棄 provider；它不涵蓋原始呼叫。
- state adapter 的 F030 選區為 12 bytes `2305b50017d3ffff670023d1`，不同於原始 8 bytes；物件的 +4 為 `R_RISCV_CALL_PLT`，最終 JALR 的 destination register 是 x0，並非原始 JAL 寫入 ra。此結果也超出原始 F030 範圍。
- 測試的非正式移除 fixed registers 方案沒有達成原始 bytes；禁用 sibling-call 且保留 fixed x1／x2 時，Clang 報告所需的 return-address 和 stack-pointer registers 已保留；移除 fixed x1／x2 的非正式非尾呼叫產出也不同。

這些是**有限候選和工具旗標的負向結果**，不是所有純 C 方案不可能的證明。讀／寫有效性、`s0`／`s1` 真實入口、`ra`、堆疊、呼叫者／被呼叫者 ABI、其他區段和完整 BIN 均未閉合；不可據此修改正式來源或放寬正式 guard。原始映像 SHA-256 為 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。

本文件及兩個候選不含完整重播鏈；本機 verifier 與其依賴尚未發布。本機測試數不是遠端乾淨樹驗收，請勿據此宣稱 CI、正式整合或完整映像通過。
