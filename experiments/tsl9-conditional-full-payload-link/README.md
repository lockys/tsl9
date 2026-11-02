# 來源原始區段與條件式資料連結

[English](readme.en.md)

執行 `python scripts/verify-conditional-full-payload-link.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>`。
測試將原有來源載體的 `0x14056..0x14C8A` 程式 bytes 與 `0x1A69C..0x1A6A0` 資料編譯為有實際 section 的物件，配合三個條件式資料別名和 TX RAM 模型連結。嚴格連結剩下 `tsl9_boot_resident_40000`；提供數值位址作診斷見證後，每種語言的完整映像均為 76,800 bytes，且 SHA-256 符合既有候選。

這只證明所選條件下的連結與位元組布局。其中入口與結尾共 70 bytes 已由來源架構指令編譯，其餘 3,058 bytes 仍使用原始載體；三個資料別名的全域索引不變條件、RAM 所有權與原機 ROM／ABI 未證。診斷 ELF 沒有 PT_LOAD，輸出的 BIN 尚未驗證可安全燒錄；不執行韌體或硬體。可能涉及驗證的資料不在本文件披露。
