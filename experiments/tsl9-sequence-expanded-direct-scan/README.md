# 擴充序列狀態直接寫入掃描

既有序列分析曾在 69,412-byte 已選程式範圍內，掃描直接以 GP 為基底且覆蓋 `GP+[332,336)` 的標準 byte／halfword／word store。此次納入原先未納入的 `[0x14056,0x14C8A)` 3,124-byte 線性解碼窗口；兩者合計 24,610 條指令，仍沒有這類直接 store。

實際序列程式會經其他暫存器與索引更新 state，因此這不是「沒有寫入」的證明，也不能排除 indirect pointer、其他編碼、未選程式、resident、IRQ／DMA 或重入。全域 0／1 不變量仍取決於那些條件。

重播使用 `experiments/tsl9-state167-writers/verify.py` 與固定雜湊的 candidate BIN、layout、ELF reader 及 radare2；檢查器包含八個合成 store 邊界案例。未執行目標或操作硬體。
