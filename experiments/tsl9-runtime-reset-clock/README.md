# Runtime reset／時鐘交接：離線診斷元件

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

現行程式位於 [src/native/startup](../../src/native/startup/) 與 [clock_init.c](../../src/native/clock/clock_init.c)。以可讀C迴圈和最小架構port重建ID2966啟動流程，**尚非完整、可刷寫韌體**。

- reset138B／38指令：20B入口＋118B記憶體／CSR交接；GP／SP前16B與原檔相同。
- 保留三次獨立GP取樣、unsigned guard、forward word copy、零寫入，以及copy跳過時的incoming T0。無C frame、spill或額外helper。
- 真實連結保留 `18720→1874A` 的時鐘JAL與RA=`18724`，MEPC=`9008`，最後 `18730→40000` 不新增link。
- 初始化128B與原檔完全相同；RAM35160B及stack16B是明確NOBITS配置。C11／C++17機器碼相同，IR分別固定hash（C++ GP port帶noundef）。

## 驗證

需要既有LLVM18工具鏈；[工具路徑由環境變數設定](../../docs/local-paths.zh-TW.md)。在專案根目錄執行，輸出目錄必須全新：

```sh
python3 experiments/tsl9-runtime-reset-clock/verify.py --project-root . --tool-dir "$TSL9_LLVM_BIN" --build-root "$PWD/experiments/tsl9-runtime-reset-clock/build/new-run"
python3 experiments/tsl9-runtime-reset-clock/verify.py --project-root . --replay "$PWD/experiments/tsl9-runtime-reset-clock/build/new-run/c/verification.json"
```

Windows可用python／py -3，並以PowerShell的 `$env:TSL9_LLVM_BIN` 指定工具。實測NDK27.1.12297006／LLVM18；其他平台未實測。每語言12項raw operand負例＋4項IR負例；不執行target／HOST模型／ISA或硬體。current本機收據為build/component-v12。

## 尚未閉合

clock240B比原234B多6B，占用原 `[18834,1883A)` 下一段程式；禁止直接嵌入原APP。`--require-firmware-ready` 會拒絕此結果，工具沒有BIN輸出功能。

ELF無UND不代表所有執行相依已實作：vector8038、main9008、resident40000仍未提供。前兩次GP取樣的PC／A0形成順序、AUIPC中間值、時序及完整IRQ／fault效果仍有差異或未證；RAM／ROM／硬體身分與整份APP配置亦未證。正常暫存器交接只適用於GP穩定、原資料讀寫成功、沒有非同步干擾且clock正常返回的條件。
