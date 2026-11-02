# 序列狀態的相鄰位址指令掃描

以 GP=`0x20004000` 為數值條件，四個序列狀態 byte 為 `[0x2000414C,0x20004150)`。在固定 layout 的 69,412-byte 程式區及 `[0x14056,0x14C8A)` 3,124-byte 線性解碼窗口中，檢查相鄰的標準 `LUI`／`AUIPC` 與以相同目的暫存器為 base 的標準 load、store、`ADDI`，或壓縮 `C.LW`／`C.SW`：1,417 組符合編碼，其中 137 組為壓縮形式，其中沒有數值範圍與四個 state bytes 重疊。

此掃描不檢查非相鄰指令、後續位址運算、其他壓縮記憶體指令、指標、其他程式區、resident 或非同步行為；它不能證明沒有其他 state 寫入，也不建立全域 0／1 值域。線性解碼不證明命中指令可達。

`python experiments/tsl9-sequence-address-pairs/verify.py --firmware <CANDIDATE_BIN> --layout <ORIGINAL_LAYOUT_ELF> --reader <ELF_READER>` 使用固定雜湊輸入與八個合成解碼控制；不執行目標或操作硬體。
