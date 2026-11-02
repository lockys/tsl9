# 指標位址暫存器的局部前綴

對 [GP 掃描](../tsl9-settings-pointer-gp-scan/README.md)中 14 處立即讀取後仍保留 `GP+84` 位址的指令，從讀取後線性往後檢查，遇到該暫存器首次使用、控制流程改變或 24 條指令上限即停止：七處在首個分支／呼叫之前被覆蓋；七處先遇到控制流程邊界。這個局部前綴沒有找到位址暫存器的 store、複製或傳遞，但沒有追過分支、例外、呼叫或記憶體別名，也不排除位址早已存在其他暫存器。

後七處為 `0xAC7C`、`0xBDC6`、`0xDF26`、`0xFE6A`、`0x155D4`、`0x171EC`、`0x142FC`；例如 `0xFE6A` 在 `0xFE76` 分支，因此其後位址複製不屬這次前綴結論。其餘三處原本就非立即讀取，見[延後讀取](../tsl9-settings-pointer-delayed-reads/README.md)。

`python experiments/tsl9-settings-pointer-live-prefix/verify.py --firmware <CANDIDATE_BIN> --layout <ORIGINAL_LAYOUT_ELF> --reader <ELF_READER> --r2 <R2_EXECUTABLE>` 使用固定雜湊輸入、radare2 解碼及四個合成分類控制，不執行韌體。這不是完整 CFG、全域指標不變性、ROM／硬體或燒錄證明。
