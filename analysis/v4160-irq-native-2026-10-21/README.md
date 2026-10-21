# IRQ 原生重建證據

[English](readme.en.md)

本輪修正的是編譯器配置問題與可讀 C/C++ 核心，完整目標仍為原機相容 BIN。新核心位於 `experiments/tsl9-v4160-irq-native/`，舊模型與歷史失敗證據不覆寫。

| 問題 | 本輪證據 | 尚未證明 |
| --- | --- | --- |
| 舊核心為何要求 SP | compiler-diagnosis 的實際 spill／outliner 診斷 | allocator 全部內部決策 |
| 新核心是否保留主機行為 | canonical 與 source-review 的 C11／C++17 實際測試及已編譯變異 | 主機測試不證明 native bridge |
| 原生 helper 能否保留原區段 | compiler-review：四個原址各 30 bytes 與原 BIN 完全一致 | 完整映像整合 |
| 正常返回暫存器與效果 | abi-review 獨立 bytes 審查、compiler-review 全覆蓋／20 效果／LLVM IR | 中途狀態及非同步 IRQ 等價 |
| IRQ 本體是否可放回 | 180 bytes，大於原始 144 bytes，明確拒絕 | 新配置與其所有參照 |
| C++ 額外配置 | object `.eh_frame` 120 bytes、linked 124 bytes，all-allocated ownership 為 false | metadata 儲存位置／整合 |

`source-design`、`compiler-diagnosis`、`source-review`、`abi-review` 與 `compiler-review` 各自封存。交付只保留來源、檢查器與選定收據 metadata；舊 build 封存不搬移。`abi-review` 早期獨立審查的重播需要當時工作站的 candidate build；發佈副本透過新編譯的逐函式 bytes 與封存結果對照，不能把缺少的 build 當作已在發佈處重新執行舊審查。

```sh
sh experiments/tsl9-v4160-irq-native/verify.sh --language both
sh experiments/tsl9-v4160-irq-native/verify-native.sh --tool-dir /path/to/llvm/bin --language both
```

Python 可直接啟動兩個對應檢查器；native CLI 支援明確 `--project-root`、`--tool-dir`、`--firmware`。來源綁定 V4.1.60 ID2966 SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。只讀原始 bytes；不執行或模擬 RV32，不存取廠商、BLE、UART、CAN 或實體 Flash，不產生新 BIN。
