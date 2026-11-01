# 條件性 TX RAM 模型

[English](readme.en.md)

[來源](../../src/native/tx_candidate/conditional_storage.c)宣告 2,124-byte 未初始化物件，診斷版面將其放在名目 `[0x2000B18C,0x2000B9D8)`。依據是[既有主流程分析](../../analysis/main-runtime-family-2026-10-24/README.md)中傳入 ROM 的起點與長度，以及 TX 兩個 1,062-byte 槽位；ROM 行為與實際 RAM 所有權尚未證明。

`python scripts/verify-conditional-tx-storage.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>` 以 C／C++ 分別編譯實際 `NOBITS` 物件並做條件性診斷連結。TX RAM 符號由物件定義後，嚴格連結仍有 6 個 APP 依賴；以數值見證進行比較時，73,551 bytes 的既有 Flash 區段均不變。ELF 為零 `PT_LOAD`，不是 BIN。

**此配置只是假設性連結模型**：尚未確認硬體 RAM 容量、啟動清零、stack、IRQ、DMA、其他全域資料、ROM 使用及其不重疊。不得據此燒錄或宣稱 RAM 問題已在實機解決；預設建置仍保留原本未解析的 RAM 參照。
