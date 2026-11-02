# 設定指標儲存位置的直接 GP 掃描

依固定 layout 的 69,412 bytes 已選程式（23,602 條指令），加上 `[0x14056,0x14C8A)` 的 3,124 bytes 線性解碼窗口（1,008 條），掃描標準 RISC-V 直接以 GP 作 base 的 byte／halfword／word store，沒有找到與 `GP+[84,88)` 重疊的寫入。掃描也辨識 74 次將 `GP+81..87` 直接算入暫存器的 ADDI；其中 71 次下一條是由該暫存器零位移讀取 word；其中 57 次以讀取結果覆蓋該位址暫存器，14 次則仍保留該位址，需進一步追蹤。其餘位於 `0x12C82`、`0x133C0`、`0x18240`，需後續資料流追查。

檢查器包含覆蓋邊界的合成正反例，並固定 candidate BIN、layout 與 ELF reader 的 SHA-256。它只處理上述指令編碼與所選範圍，不證明指標不變：reset 是透過其他 base 寫入、間接指標、不同編碼、未選程式、resident、IRQ／DMA 與執行階段記憶體均未封閉。

以本機固定資料執行：`python experiments/tsl9-settings-pointer-gp-scan/verify.py --firmware <CANDIDATE_BIN> --layout <ORIGINAL_LAYOUT_ELF> --reader <ELF_READER>`。檢查不執行目標；沒有證明實機或 OTA 相容。
