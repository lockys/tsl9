# 13-byte 條件性讀取窗口

[English](readme.en.md)

此來源提供名目位址 `[0x1AB37,0x1AB44)` 的 13 bytes。既有[讀取範圍分析](../../analysis/v4160-data-addresses-2026-10-21/retained-read-domains/README.md)將它列入 `0x1A078 + 16*mode + column` 的局部讀取集合；這不證明實機會到達該範圍，也不證明原始資料物件型別或全域索引界限。

執行 `python scripts/verify-window-1ab37.py --tool-dir <LLVM_BIN> --candidate <CANDIDATE_BIN> --out <NEW_OUTPUT_DIR>`，編譯 C／C++ 來源，僅讀取此允許窗口與基礎診斷版面允許的區段，建立不可燒錄的原位址診斷 ELF。41 個區段合計 73,551 bytes 與候選檔一致，包含原有 73,538 bytes 及本窗口 13 bytes。結果保留 6 個數值地址見證、零 `PT_LOAD`；不建立完整 provider、完整 BIN 或硬體相容性。
