# 原生元件證明：第二版

第二版保留已封存的第一版檔案作為歷史證據，並加強機器碼涵蓋範圍檢查。重新編譯請使用 `verify_native_v2.py`；唯讀重播本機封存產物請使用 `check_native_v2.py`。第一版指南中的元件說明、來源效果、ABI／佈局限制及工具鏈資訊仍適用；新建置請改用下方第二版指令。

C11 與 C++17 仍產生相同的 118 位元組、43 條指令初始化函式，以及四個各 22 位元組的輔助函式。兩種模式都通過 20 項 IR 效果及 20 項機器碼效果證明，沒有未定義符號或可寫資料。第二版進一步將每筆反組譯直接綁定實際連結 ELF 符號：入口位址正確、指令位址連續、原始指令位元組一致、指令邊界完整，且涵蓋全部 118 位元組。無法解析的內部／尾端指令行與內部標籤均會拒絕，解析器不能默默略過任何指令或位元組。

每種新建置都會將第一版的四個錯誤來源版本實際編譯並拒絕。此外，每種模式另有六項反組譯文字控制，拒絕遺失首筆指令、遺失中間指令、截斷最後一筆、竄改指令位元組、無法解析的內部行及尾端行。這六項測試驗證靜態證據解析器，不代表執行目標程式。

在發布的專案目錄執行：

```sh
python3 analysis/v4160-interrupt-init-2026-10-21/native-plan/verify_native_v2.py \
  --project-root . \
  --clang /path/to/clang \
  --linker /path/to/ld.lld \
  --objdump /path/to/llvm-objdump \
  --language both
```

也可用 `--tool-dir /path/to/llvm/bin` 取代三個工具執行檔參數。分析工作區的前綴為 `apk-analysis/tsl9-v4160-interrupt-init-2026-10-21/`，發布版本前綴為 `analysis/v4160-interrupt-init-2026-10-21/`。只需要 Python 3.10 以上、新模型的 C／標頭、已發布的 Python 驗證檔，以及本機 LLVM 工具；不需要舊有被忽略的 691 區段建置封存。每次執行都建立新的本機 `build/native-.../` 目錄與真實收據。本次已驗證工具仍為 Android NDK 27.1.12297006 的 Clang 18.0.2。

重播原驗證封存產物：

```sh
python3 analysis/v4160-interrupt-init-2026-10-21/native-plan/check_native_v2.py \
  --project-root . --require-local-builds
```

省略 `--require-local-builds` 時，唯讀檢查器會檢查封存中繼資料與目前 C／標頭內容，並明確列出缺少的本機建置收據。這類中繼資料檢查不代表重新編譯。產生的 ELF、物件、IR 及日誌只保留本機，不隨來源碼發布。

這是獨立原生元件。118 與 144 位元組的比較僅是大小證據；尚未替換至原始 `0x9A42`。原堆疊／呼叫邊界及 caller-saved 暫存器殘值不同。原始 C／IRQ ABI、已安裝 ROM、真實周邊行為、完整映像整合及藍牙 OTA 仍未證明。舊有 691 區段／8,280 RELA 檢查保持不可變，仍存在真正未提供的駐留入口。沒有產生韌體 BIN、沒有執行或模擬原始／重建 RV32 程式，也沒有硬體 I/O。
