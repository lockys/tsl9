# 0x140DC 命令處理來源整合

[English](readme.en.md)

`src/native/receive/ota_ae_140dc.inc` 以 C/C++ 架構指令描述 `0x140DC..0x14122` 的 70 bytes，保留原始分支、參數處理與呼叫順序。它依賴原本的 stack frame、暫存器和原位址，不可獨立呼叫。

C/C++ 物件各有 11 個重定位，包括六個外部 JAL。片段連結使用原位址見證；完整條件式連結另核對六個呼叫目標均由可執行 section 支撐。建置器逐 byte 比對後使用編譯結果；原始 JSON 保留作對照。目前該區段與[另一命令路徑](../tsl9-ota-ad-source/README.md)合計有 488 bytes 由來源編譯，2,640 bytes 仍由原始載體提供。

`python scripts/verify-full-source-isolation.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>` 可在沒有既有 BIN 的 198 檔來源副本重建候選。此結果不證明完整功能、實機 ROM／ABI 或燒錄安全性。
