# Reset 與 232-byte clock：離線整合

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

這個實驗使用目前 `src/native/startup/` 與 `src/native/clock/clock_init.c`，實際編譯 C11／C++17 並連結為診斷 ELF，不執行目標或產生韌體 BIN。

- reset 138B／38 指令；clock 232B／93 指令，合計 370B／131 指令。原 `0x18720 → 0x1874A` 呼叫保留 RA=`0x18724`。
- clock 真正的 12B 入口緊鄰 220B C 主體；沒有新增跳躍、別名、ABS provider 或未解析 relocation。固定 linker 配置與檢查器是必要契約，不能單獨以普通 C ABI 呼叫主體。
- 每種語言檢查 6 個實際 ELF、完整 IR／來源與工具雜湊／MD include 閉包，以及 16 項 reset、18 項 clock 負例。
- initializer 128B；RAM 35160B、stack 16B 是真 NOBITS。這些配置不證明實體硬體 ownership。

## 使用

從專案根目錄設定 `PROJECT_ROOT` 為該目錄、`LLVM_BIN` 為既有工具目錄，再執行：

```sh
python3 experiments/tsl9-runtime-reset-clock-fit/verify.py --project-root "$PROJECT_ROOT" --tool-dir "$LLVM_BIN" --build-root experiments/tsl9-runtime-reset-clock-fit/build/my-run
python3 experiments/tsl9-runtime-reset-clock-fit/verify.py --project-root "$PROJECT_ROOT" --tool-dir "$LLVM_BIN" --replay experiments/tsl9-runtime-reset-clock-fit/build/my-run/c/verification.json
```

Windows 可使用 `py -3`，並以 PowerShell 的 `$env:PROJECT_ROOT`／`$env:LLVM_BIN` 傳入變數。工具只接受已記錄雜湊的本機 NDK LLVM，不下載依賴；新 build 目錄必須不存在。`--clock-source origin` 可明確選用實驗來源，預設使用整理後來源並強制逐 byte 相同。

本輪實際收據位於本機 `build/curated-v1/{c,cpp}/verification.json`。新收據的來源欄位使用相對路徑；既有本機原始收據不改寫。公開版本及整理後來源驗證摘要見 [分析目錄](../../analysis/runtime-reset-clock-fit-2026-10-23/summary.json)。舊 runtime-reset-clock 檢查器與歷史收據維持凍結；其舊 clock pin 不適用目前 checkout。

## 未證明

新 RET 位於 `0x18830`，取代原始 cold SW；原 `0x18832..0x18834` cold J 仍不能當作空間。沒有覆蓋下一函式，不代表已排除間接／BOOT／resident／IRQ 入口。vector `0x8038`、main `0x9008`、resident `0x40000`、完整 APP、非同步／fault 語意及實體晶片／ROM／OTA 相容性尚未閉合。

`firmware_ready=false`；以 `--require-firmware-ready` 重播必須拒絕。未產生可刷寫 BIN，沒有執行或模擬 RV32／MMIO，也沒有硬體或網路操作。
