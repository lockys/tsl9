# 記憶體／ROM 需求編譯檢查

[English](readme.en.md)

[`requirements-v1.h`](requirements-v1.h) 保存 **ID2966 V4.1.60** 原廠啟動程式的數值需求；[`layout-contract-v1.c`](layout-contract-v1.c) 以 C11／C++17 靜態斷言檢查地址、範圍及指標寬度。這不是可執行韌體，也不代表已辨識實體晶片。

`verify-v1.py` 先核對兩份原廠 BIN、啟動 source map、SDK header、ELF reader 及編譯器雜湊，再從原始指令解出版本差異，編譯兩個沒有已配置程式碼／資料的 RV32 ET_REL 物件。只做正常輸入的編譯檢查，不連接硬體或執行產物。

在專案根目錄，使用已保存的 SDK header 與已固定雜湊的 Windows LLVM 18 工具鏈：

```sh
python3 experiments/tsl9-memory-rom-contract/verify-v1.py \
  --sdk-header "$TSL9_SDK_HEADER" \
  --llvm-bin "$LLVM_BIN" \
  --output "$TSL9_AUDIT_OUTPUT"
```

變數分別指向本機 `wchble_rom.h`、LLVM `bin` 及尚不存在的輸出目錄；Windows 可用 `py -3`，並依 Shell 調整換行。腳本不下載依賴；其他工具鏈須另建具來源記錄的驗證設定，不能略過固定雜湊檢查。C/C++ 靜態斷言本身沒有 Windows API 依賴。

[分析與限制](../../analysis/memory-rom-requirements-2026-10-25/README.md)。SDK 預設 ROM 指標表相符，不能證明原機已安裝的函式內容或 ABI；數值上的 64 KiB RAM 容納關係不能證明 RAM 所有權、可用堆疊或硬體相容性。
