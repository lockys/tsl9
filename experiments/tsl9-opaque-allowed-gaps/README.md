# 允許範圍內的未知位元組

[English](readme.en.md)

[來源](../../src/native/receive/opaque_allowed_gaps.c)以 31 個唯讀資料區段保留候選映像中先前未選取、且位於允許讀取範圍內的 121 bytes。這些是原始位元組，不是功能、原始型別、可達性或可執行性的重建；不能因為部分值相同就推論其用途。

`python scripts/verify-allowed-source-layout.py --tool-dir <LLVM_BIN> --candidate <CANDIDATE_BIN> --out <NEW_OUTPUT_DIR>` 逐區段重編並比較 C／C++ 的 73,672 bytes。每筆讀取前先檢查半開區間，不讀 `[0x14056,0x14C8A)` 與 `[0x1A69C,0x1A6A0)`；兩者共 3,128 bytes，仍未包含在建置中。

選定區段與候選檔相同不代表還原了原始碼或完整韌體。嚴格連結、ROM／RAM、啟動與實機功能仍未解決；輸出是零 `PT_LOAD` 診斷 ELF，不是可燒錄 BIN。
