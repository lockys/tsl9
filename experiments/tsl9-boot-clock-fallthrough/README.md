# Clock fall-through 元件

[English](readme.en.md)

可讀 C 核心保留 85 行計算 IR 與 216 bytes 計算指令；架構入口直接落入相鄰的 C body，末端以 SP+16／RET 返回。C11／C++17 實編譯均為 **232 bytes、93 指令**，比上一版 240 bytes 縮短 8 bytes。

- 實際名目配置：entry `0x1874A`、body `0x18756`、end `0x18832`；不再覆蓋下一函式 `0x18834`。
- 只有兩個真實 FUNC，無 alias／UND／ABS／relocation；沒有額外 frame、spill 或 RA 改寫。
- 每語言 18 項負例、完整 ELF／IR／工具／標頭／命令／MD／來源與產物閉包檢查通過。這些是離線靜態證據。
- 原 `0x18832..0x18834` 仍是 cold jump，不能當空白；檔內直接跳轉掃描不涵蓋 indirect／resident／BOOT／IRQ。
- reset caller 整合仍待驗證；`src/native/clock/clock_init.c` 目前保留上一個已整合的版本。本實驗沒有產生 BIN，`--require-firmware-ready` 會拒絕。

在專案根目錄設定 `TSL9_LLVM_BIN` 為已核對的工具目錄，再使用新 build 目錄：

```sh
python -B experiments/tsl9-boot-clock-fallthrough/verify.py --project-root . --tool-dir "$TSL9_LLVM_BIN" --build-root experiments/tsl9-boot-clock-fallthrough/build/local-v1
python -B experiments/tsl9-boot-clock-fallthrough/verify.py --project-root . --tool-dir "$TSL9_LLVM_BIN" --replay experiments/tsl9-boot-clock-fallthrough/build/local-v1/c/verification.json
```

目前工具／標頭雜湊固定為已驗證的 Windows LLVM；其他編譯器或平台需要另外核對。公開收據不包含本機 build 產物；重播需要保留對應產物，新 checkout 請先編譯。

[來源與驗證摘要](../../analysis/clock-fallthrough-2026-10-23/summary.json) · [C 收據](../../analysis/clock-fallthrough-2026-10-23/receipts/c.json) · [C++ 收據](../../analysis/clock-fallthrough-2026-10-23/receipts/cpp.json) · [OTA 紀錄功能缺口](../../analysis/clock-fallthrough-2026-10-23/ota-evidence-opportunity.zh-TW.md)
