# Flash 原生 C/C++ 實作與驗證

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

本輪實際建置六個 V4.1.60 函式，合計 256 bytes／98 指令；原始為 262 bytes／99 指令。
程式位於 `experiments/tsl9-v4160-flash-native/`，C11／C++17 的六函式 ELF 相同，
SHA-256 `1097156d90ee982a6c03c903785b563acae0357d1bbc7b7c2e29315adbf5d613`。
不執行 RV32、模擬器或硬體，也不輸出 BIN。

三個可直接使用的入口：

```sh
python3 -B experiments/tsl9-v4160-flash-native/verify.py --project-root . --language both
python3 -B analysis/v4160-flash-native-2026-10-22/implementation/verify_native.py --project-root . --tool-dir /path/to/llvm/bin --language both
python3 -B analysis/v4160-flash-native-2026-10-22/implementation/verify_native.py --project-root . --replay /path/to/native/c/verification.json
```

工作目錄將 `analysis/v4160-` 換為 `apk-analysis/tsl9-v4160-`。兩種 CLI 均接受全新
`--build-root`，有相同參數的 shell 啟動器；主機 CLI 也接受 `--replay`。
原生工具可用 `--clang`／`--linker`／`--objdump` 分別指定，原始參考檔可用 `--firmware` 指定。
Python 與本機 LLVM／MSVC 流程已在 Windows 實際執行；POSIX shell 原始碼提供跨平台入口，
未宣稱已在 WSL／Git Bash 或其他 OS 執行。

主機每種語言驗證 5 組、481 案例、247191 檢查，以及 6 個確實編譯並執行失敗的語意負例。
包含完整預期 key／status／CTRL／data／CSR 次序、每個 HALT／TRANSFER 外部效果前綴、
live source 改動、正向重疊、位址 wrap、未知位元與 fresh frame 觀察。獨立覆核另有不同 oracle。
合成 provider 並非控制器模擬器，也不證明實際 Flash 完成或有效的實體位址。
每個正／負主機程式在啟動前檢查格式、機器與寬度，啟動後確認位元組未變；
架構只由目前 Python 自身標頭及執行期指標寬度決定，replay 也重讀七個程式。
實際 RV32 component 及九個格式／機器負例在零次 subprocess 呼叫下被拒絕。
四個 Linux／macOS 標頭 fixture 只驗證解析，未在其他 OS 執行。
macOS 目前要求 thin Mach-O Python；universal／fat interpreter 會被拒絕。

原生驗證使用各函式原始 GPR 寫入及參數集合推導的保留暫存器參數，實際編譯所有六個物件及 IR，
嚴格連結而無 UND；檢查完整 raw disassembly 覆蓋、CFG、RV32IMAC_Zicsr／ILP32、無額外配置／
helper stack／隱藏函式，以及原始正常返回的暫存器與記憶體模式。獨立檢查器的 15 個機器碼負例、
3 個 IR 負例及工具／parser／韌體 context 負例另行保留。6 份 `-MMD` 檔只涵蓋專案非系統標頭；
系統 resource 標頭不在該清單，實際工具執行檔及輸出位元組另行固定。

`status/unlock/lock/erase/program/quarter` 的實際大小為 8/30/14/46/94/64。
wrapper 保留 32-byte frame、SP+12 重讀、五個原始 JAL 位置／目標及 fresh RA／S0／S1 restores。
保存次序由 S0/S1/RA 改為 RA/S0/S1，故逐步／非同步等價為 false。
program 的 A0 對齊移至初始輪詢之後，非返回 GPR 前綴也不等價。
所有正常返回結果皆有條件：每次存取完成、輪詢最終清除，且沒有未建模的非同步干擾。

原始證據重用已封存的 262B／99 指令 source proof；發布後的 fresh 建置不冒稱重新執行歷史
691 區段 owner 稽核。`probe_native.py` 是早期 Windows 診斷及固定參數來源，仍由正式原生
CLI 匯入參數；它不是跨平台主入口，也不能從發布檔案漏掉。

program 短 6 bytes，原始區段尾端尚未取得儲存／入口所有權；本輪沒有填補、改寫舊映像或建立
完整來源映像。後續整合必須另證明六個原始別名／區段、所有 caller／RELA、內部入口與尾端所有權。
六個高位址 caller 不能當作實體 Flash 容量證據。ROM／晶片／板子、時序、電源失敗、開機、
實體相容及 OTA 仍未證明。`check.py` 只重驗封存與可用的本機產物；未發布的 build 不會假裝已重驗。
