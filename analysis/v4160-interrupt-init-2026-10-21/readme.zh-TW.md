# 中斷初始化來源證據

[可讀 C/C++ 元件](../../experiments/tsl9-v4160-interrupt-init/readme.zh-TW.md) 重建原 `0x9A42` 及四個 helper 在一般呼叫下的 MMIO／CSR 效果。`source/` 保存來源證據；`abi-review/` 整理原始暫存器與堆疊限制；`code-review/` 是獨立 C 測試；`native-plan/` 是原生編譯器與 ELF 檢查。

目前原生入口是 `native-plan/verify_native_v2.py --project-root <專案> --language both`，LLVM 執行檔可在 PATH，或用 `--tool-dir`、`--clang`、`--linker`、`--objdump` 指定。V2 將每個反組譯 byte 與完整 ELF 函式核對，缺少、變更或無法解析的指令列都會拒絕。V1 原樣保留作為歷史證據。完整本機 build 收據與執行檔不放入發佈快照，請使用全新驗證指令重建元件檢查。

這些證據分別回答不同問題。一般 C 回傳值及沒有未定義符號的獨立原生元件，不能證明原始暫存器殘值、固定位址、完整啟動、原機 ROM、中斷派送或 BLE OTA 相容。原始韌體只作資料讀取；不執行或模擬 RV32 程式，不進行實體 I/O。
