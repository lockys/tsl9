# `GP+167` 狀態 byte 的直接寫入

掃描已選 69,412-byte 程式區與 `[0x14056,0x14C8A)` 的 3,124-byte 線性解碼窗口，共 24,610 條指令；在標準 RISC-V、直接以 GP 為 base 的 byte／halfword／word store 中，唯一與 `GP+167` 重疊的寫入是 `0x93A2` 的 `sb a0,167(gp)`。緊接此前 `0x939E` 是 `seqz a0,a0`，因此此單次明確寫入值為 0 或 1，與此前值無關。

如果 reset 確實將該 byte 清為 0，其後所有寫入只來自這條指令，且 GP、記憶體、控制流與非同步行為均符合假設，則讀取時狀態為 0 或 1。這是條件式歸納：reset 以其他 base 寫入，間接指標、其他編碼、未選區、resident、IRQ／DMA 與異常均未封閉；不證明產品語義、指令實際執行或全域值域。

`python experiments/tsl9-state167-writers/verify.py --firmware <CANDIDATE_BIN> --layout <ORIGINAL_LAYOUT_ELF> --reader <ELF_READER> --r2 <R2_EXECUTABLE>` 固定輸入雜湊、核對掃描結果與寫入前指令，並檢查四個合成邊界；不執行目標。
