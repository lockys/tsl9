# 0x1417A 命令處理來源整合

[English](readme.en.md)

`src/native/receive/ota_ad_1417a.inc` 以 C/C++ 架構指令描述 `0x1417A..0x141AC` 的 50 bytes，保留原始參數處理、呼叫與分支。它依賴原本 stack frame、暫存器及原位址，不可獨立呼叫。

C/C++ 物件各有八個重定位，其中五個是外部 JAL。片段連結使用原位址見證；完整條件式連結核對這些呼叫目標均有可執行 section。建置器逐 byte 比對原始資料後使用編譯結果，中間尚未還原的區段仍保留原始載體。整個區段目前有 254 bytes 由來源編譯、2,874 bytes 仍為載體。

`python scripts/verify-full-source-isolation.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>` 可在不含既有 BIN 的 195 檔來源副本重建候選。這不證明完整功能、原機 ROM／ABI 或燒錄安全性。
