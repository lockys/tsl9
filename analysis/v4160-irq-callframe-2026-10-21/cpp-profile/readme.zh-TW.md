# 單一 C++ 組態移除額外 unwind 配置

在凍結的 C++17 原生組態上，**只加入 `-fno-exceptions`**，實際 object 與連結 ELF 的 `.eh_frame` 都已消失。沒有加入 RTTI flag、改變最佳化／暫存器配置或修改來源；其餘仍為 -Oz、停用 machine outliner、僅配置 A0/A1/A4/A5，SP 與其他整數暫存器皆保留。

| 實測結果 | 舊封存 C++ | 新 C++ 組態 |
|---|---:|---:|
| 五函式 bytes | 300 | **完全相同的 300 bytes** |
| 各 helper | 30 bytes／12 條 | 完全相同 |
| 初始化函式 | 180 bytes／65 條 | 完全相同 |
| Object `.eh_frame` | 120 bytes | 不存在 |
| 連結後 `.eh_frame` | 124 bytes、VA0 | 不存在 |
| Object 總配置 | 420 bytes | 300 bytes |
| 連結後總配置 | 424 bytes | 300 bytes |
| 所有配置均屬五函式 | false | **true** |
| 初始化可放入原 144 bytes | false | **false** |

本輪使用的是凍結的 `experiments/tsl9-v4160-irq-native` **leaf 初始化函式**，並非另一個獨立開發中的 callframe 實作。四個 helper 保持原位 0x19124／0x19142／0x19160／0x1917E，合計仍與原映像 120 bytes 完全相同。初始化函式仍位於診斷 VA0x30000，超過原區段 36 bytes。可用儲存空間、完整映像整合、完整原 ABI 與 OTA readiness 仍未證明／保持 false；解決 C++ metadata 不等於解決配置問題。

可攜 runner 在匯入前會核對舊封存、checker／parser／基準 receipt 的精確 hash，直接以舊 receipt 的 raw rows 比對實際五函式 bytes，不依賴舊 ignored build。五函式完全相同，machine／正常輸出／LLVM IR 證明結果也相同：完整 bytes 與編碼目的暫存器、無 SP/T0/A2/A3／隱藏呼叫／可寫資料／未解析符號、helper A1 零寫入、初始化精確 20 效應、七次有序提交與最終正常輸出。另重做三十個文字控制。本輪沒有新增來源 mutant 編譯或測試其他組態。

跨平台命令見 [English](readme.en.md)。Runner 接受 `--project-root`、`--tool-dir`，也支援 `--clang`／`--linker`／`--objdump`／`--firmware` 本機覆寫。依賴的舊 runner 提供相同工作區／發布版離線韌體定位與精確 hash 檢查。Fresh build 只需凍結的 native/public 來源、明確釘選的舊 checker／parser／receipt／seal、本輪 runner、離線原映像及本機 LLVM，不需舊編譯產物。直接 Python CLI 已在 Windows 實測；POSIX launcher 僅交付來源，未透過 WSL／Git Bash 執行。

`results.json` 選定一份逐 byte 相同的 receipt 副本。唯讀 checker 核對 metadata、目前來源及依賴；本機歷史輸出存在時會重做實際 artifact 檢查，加 `--require-local-builds` 可要求輸出必須存在。只核對 metadata 不等於 fresh compile。ELF／IR／log 僅留本機，沒有韌體 BIN、目標執行、ISA 模擬、網路或裝置操作，也未修改舊模型／P／D／封存檔案。
