# 傳送入口的編譯器診斷

[English](readme.en.md)

這裡的 C/C++ 是合成的編譯器診斷，不是 TSL9 功能實作。目的在於用實際機器碼排除錯誤的修正方向，再回到傳送函式的相容性工作。所有 RV32 產物只作靜態資料讀取，不執行或模擬。

## 已確認的結果

- `minimal_guard.c` 含有記憶體 clobber 與僅暫存器 clobber 兩種長度檢查。C11、C++17 各新編譯一次，兩種函式都是 22 bytes：無號檢查位於 +4，堆疊配置位於 +8，超長輸入直接到 +20 的 RET。這證明記憶體 clobber 本身不足以解釋完整 TX 函式的提前 prologue，也沒有證明任意普通 C 拓撲都能發出同樣順序。
- `global_owned_s0.c` 的全域 register 宣告確實被編譯器接受，但 C/C++ 都產生 16-byte 函式，包含 SP−16、S0 儲存及返回前的 S0 還原。宣告一個固定暫存器不等於取得呼叫框架所有權。
- 新診斷的四個實際分支位元反例均被拒絕；每個編譯單元以 `-MD` 核對其來源及實際 Clang `stdint.h`。編譯器、反組譯器、舊 profile、ELF parser 與原始欄位 decoder 均核對雜湊。

舊的原始 TX decoder 不接受診斷額外產生的 C.SW。新 runner 僅在自身增加 C.SW 的指令欄位解碼，保留舊 decoder 不變；沒有實作 CPU 狀態、指令執行或模擬器。

## 重新驗證

在專案根目錄使用已核對的 LLVM 工具目錄：

```sh
python3 -B analysis/v4160-tx-register-abi-2026-10-22/entry-plan/verify-diagnostics.py --project-root . --tool-dir /absolute/llvm/bin
```

本研究工作區的路徑為 `apk-analysis/tsl9-v4160-tx-register-abi-2026-10-22/entry-plan/`。亦可從這裡執行 `sh ./verify.sh --project-root /absolute/project --tool-dir /absolute/llvm/bin`；`PYTHON` 可選擇 Python 執行檔。每次使用新的輸出目錄，拒絕覆寫已有的 build。

`results.json` 記錄本機 Windows LLVM 的既有實測；它不是 Linux/macOS 實測、原機 ROM 契約或硬體證據。重新執行 runner 才會重新編譯並產生新的 `verification.json`。本診斷不連線、不取得新套件，不產出可刷寫 BIN。
