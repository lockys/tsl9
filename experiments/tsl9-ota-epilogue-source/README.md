# 0x14098 結尾的來源整合

[English](readme.en.md)

`src/native/receive/ota_epilogue_14098.inc` 以 C/C++ naked 函式與明確 RISC-V 指令描述原始區段 `0x14098..0x140A6`：恢復 RA／S0–S3、回復 192-byte stack frame，然後返回。這段依賴由既有函式建立的 frame，**不可獨立呼叫**。

完整候選建置與條件式連結會分別用 C、C++ 編譯這 14 bytes，核對實際 ELF section、符號大小及與原始載體逐 byte 相同，然後以編譯結果放入映像。原始 JSON 中的對照 bytes 仍保留；其餘區段的最新進度見下方入口來源整合。完整 BIN 雜湊與先前候選相同，不等於實機啟動或相容性已驗證。

另可執行 `python scripts/verify-full-source-isolation.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>`，在只含 193 個來源及建置檔案的副本中重建兩種 BIN；該副本沒有既有候選 BIN，但包含上述原始資料載體。後續[入口來源整合](../tsl9-ota-entry-source/README.md)另以來源產生 66 bytes。
