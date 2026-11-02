# 0x140A6 分派延續區段

[English](readme.en.md)

`src/native/receive/ota_more_140a6.inc` 以 C/C++ 架構指令重建 `0x140A6..0x140DC` 的 54 bytes，保留命令比較、狀態讀取與原始分支。它依賴既有 stack frame、暫存器與原位址，不可獨立呼叫。

C/C++ 物件各含五個標準 branch 與一個壓縮 jump relocation。建置器核對其位置與目標，在 `0x140A6` 連結並逐 byte 比對原始資料後，將編譯結果放入候選映像。入口、結尾、此區段與[後續命令路徑](../tsl9-ota-ae-source/README.md)與[另一命令路徑](../tsl9-ota-ad-source/README.md)共 254 bytes 由來源編譯，另 2,874 bytes 仍由原始載體提供；原始 JSON 保留作對照。

執行 `python scripts/verify-full-source-isolation.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>` 檢查獨立來源重建。`scripts/verify-payload-active-gates.py` 可重驗條件式連結和既有路徑。這不證明完整功能、原機 ABI 或燒錄安全性。
