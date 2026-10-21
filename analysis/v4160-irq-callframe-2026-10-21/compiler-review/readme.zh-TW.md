# 實際符合原 144 bytes 的 C/C++ callframe main

Fresh C11 與 C++17 均產生初始化函式 **144 bytes／46 條指令**，以及四個各 **30 bytes／12 條** helper，合計 **264 allocated bytes／94 條**。全部連結在原位：main 0x9A42，helpers 0x19124／0x19142／0x19160／0x1917E。沒有額外配置 metadata、可寫狀態、隱藏函式、別名或最終未解析符號。C++ 使用已驗證的 `-fno-exceptions`，沒有額外搜尋最佳化／組態。

第一個 SP 調整與 **main offset 10 起的所有 bytes** 都在原位與原映像相同，保留全部原指令邊界；helper 共 **120 bytes** 也完全相同。唯一差異為開頭四個兩 bytes 的 stack save 順序：

| 順序 | 原版 | 編譯後 C/C++ |
|---:|---|---|
| 1 | S2 → SP+0 | RA → SP+12 |
| 2 | RA → SP+12 | S0 → SP+8 |
| 3 | S0 → SP+8 | S1 → SP+4 |
| 4 | S1 → SP+4 | S2 → SP+0 |

Save multiset 與 16 bytes frame 位置相同，但在 0x9A44／0x9A46／0x9A48／0x9A4A 的寫入順序不同。**Main 完整 byte 身分、原逐點等價及非同步／中斷等價仍為 false／未證明。** 差異發生於 CSR clear 前，是可觀察的 stack 寫入順序差異。函式大小／原位配置這個局部 gate 已通過，仍不能當成安全替換、完整原 ABI、完整映像整合或硬體／OTA 相容證明。

Checker 先核對原 264 bytes／94 指令 seal 與 callframe source-plan seal，再以釘選 raw operand decoder 獨立核對 objdump。每列 bytes 都綁定實際 ELF 與完整函式範圍，包含 helper 第一個 RET 後的另一分支；只允許原 main/helper 目的暫存器集合。Standalone helper 沒有 A1/SP/T0/A2/A3 寫入。

六次呼叫都是原 PC／target 上的**四 bytes JAL、RD=RA**，RA=PC+4 對應原續接指令邊界。Main object 恰有六筆相應 offset 的 `R_RISCV_JAL`，以及四個明確 helper 未解析義務；最終 ELF 全部解析，沒有虛構 ABS provider 或 stub。Body 比對也確認原 CSR source、live mask add、PFIC 指令、最終 RET 與平衡 SP 調整。

尾端保留原本由 live SP+12／+8／+4／+0 **重新讀取 frame** 至 RA/S0/S1/S2 的指令，沒有改成回填輸入 snapshot。只有 saved words 未變時，才等於輸入暫存器；SP 恢復也依賴 live frame base。正常輸出契約保留這些條件。靜態證據沒有執行呼叫、讀取目標 RAM、模擬 CSR 或宣稱中斷等價。IR 另外檢查六個有序 call primitive 的 A0/A1/RA/A4/A5/memory constraints、兩個 live S2 CSR 邊界及六項 PFIC store 寬度；這是 IR 結構檢查，並未宣稱完整 IR 語意執行。

C/C++ 各有**六個實際編譯且連結**的來源控制並全數拒絕：移除 RA clobber、錯誤 JAL link register、錯誤第一個 target、錯誤最後 flag、錯誤 PFIC 寬度、錯誤 helper offset。每語言另有三十個文字控制，拒絕五函式的缺列、修改 raw byte、截斷與無法解析的列。所有元件與控制均未執行。

跨平台命令見 [English](readme.en.md)。發布／交付版使用 `analysis/v4160-irq-callframe-2026-10-21`；原分析工作區使用 `apk-analysis/tsl9-v4160-irq-callframe-2026-10-21`，依賴定位同時支援兩者並檢查精確 hash。工具支援 `--project-root`、`--tool-dir`、`--language both`，以及獨立 `--clang`／`--linker`／`--objdump`／`--firmware` 覆寫。離線原映像可由明確輸入、工作區 exports 或發布版 firmware-downloads 定位，仍要求精確原 hash。不需舊 build，只需五個凍結來源／header、釘選舊工具／parser／原 source／plan 證據、原映像與本機 LLVM。直接 Python CLI 已在 Windows 驗證；POSIX launcher 僅交付來源，未透過 WSL／Git Bash 執行。

`results.json` 選定兩份逐 byte 相同的 metadata 副本。唯讀 checker 檢查封存與目前來源，若本機歷史輸出存在，會重做 artifact 驗證；加 `--require-local-builds` 可要求指定歷史檔案存在。只核對 metadata 不等於 fresh compile。ELF／IR／log／控制來源均僅留本機，沒有韌體 BIN、完整映像 patch、目標執行、ISA 模擬、網路或裝置操作；沒有修改原映像、模型、舊封存檔或 P/D checkout。
