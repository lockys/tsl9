# 五個實際 C/C++ 原生元件

凍結的分支獨立 C 實作，已使用本機 Clang 18.0.2，以 RV32IMAC_Zicsr／ILP32、**-Oz**、`-mllvm -enable-machine-outliner=never` 成功編譯連結。只允許配置 A0/A1/A4/A5，其餘包含 SP/T0/A2/A3 都保留。Verifier 另外檢查實際 bytes 與編碼目的暫存器，不只相信 flags。

| 結果 | C11 | C++17 |
|---|---:|---:|
| 四個 RCC helper，各自 | 30 bytes／12 條 | 30 bytes／12 條 |
| 初始化函式 | 180 bytes／65 條 | 180 bytes／65 條 |
| 可執行配置歸屬 | 300 bytes，通過 | 300 bytes，通過 |
| 額外唯讀配置 | 0 | `.eh_frame`：object 120 bytes，連結後 124 bytes |
| 所有 allocated bytes 都屬於五函式 | true | **false** |
| 初始化函式可放入原 144 bytes | **false** | **false** |

四個 helper 共 **120 bytes**，已在 **0x19124／0x19142／0x19160／0x1917E** 原位連結，與釘選的 ID2966 原映像逐 byte 相同。初始化函式只放在診斷用 **0x30000** 虛擬位址，尚未證明那是可用 Flash，也未安裝原入口 thunk。它仍比原區段 `[0x9A42,0x9AD2)` 多 36 bytes。

本組態保留 C++ `.eh_frame`，沒有丟棄 metadata 或另加 exception flags。連結後該 metadata orphan 位於 VA0，含四 bytes 結束標記，尚無可用儲存／整合證據。可執行 bytes 歸屬與全部配置歸屬是分開的 gate；辨識出 metadata 不會使後者變成 true。完整映像整合與 OTA readiness 均為 false。

原生檢查確認五個實際函式、沒有未解析符號／別名／隱藏實作、沒有可寫資料、沒有 SP/T0/A2/A3 存取或寫入；各 standalone helper 的 **A1 編碼寫入數為零**。反組譯完整逐 byte 綁定 ELF，包括 helper 第一個 RET 後的另一分支。Raw destination 欄位與顯示指令獨立比對，也核對壓縮 branch 的編碼目標、兩條 helper 返回路徑、無外逃／無環 CFG。所有可執行配置都屬於這五個函式；C++ 的非執行配置另行記錄。

初始化函式的有限直線靜態 def-use 證明確認 **20 項有序 CSR/MMIO 效應**、六次各自新讀取的 RCC 值、精確讀改寫遮罩、PFIC 寬度／值，以及正常返回 **A0=最後新讀改寫值、A1=0、A4=128、A5=0xE000E000**。LLVM IR checker 逐項處理初始化指令、檢查透明固定暫存器 primitive 及 **七次有順序的 returning commitment**。Helper 另有分支獨立的 IR 結構檢查，其最強原生身分證據是原位 bytes 完全相同。沒有建立 guest RAM／CSR state／PC stepping、沒有執行或模擬 ISA。尚未證明中斷／逐點語意及完整原 ABI；Main 中途會以 A1 暫存 PFIC 位址，最後輸出另有檢查。

C/C++ 各五個**實際編譯且連結**的負向控制：寫 A2、寫 SP、錯誤最終 A1、錯誤 PFIC 寬度、錯誤 helper register offset，全數拒絕。每個語言另有三十個文字控制，涵蓋五函式的缺列、改 raw byte、截斷及無法解析的列。所有產物與控制均未執行。

跨平台命令請見 [English](readme.en.md)。`verify_native.py` 接受 `--project-root`、`--tool-dir`、`--language both`，也可分別用 `--clang`／`--linker`／`--objdump` 指定本機工具。`.sh` launcher 依 PYTHON、python3、python 選擇執行器。唯讀 `check_native.py` 可加 `--require-local-builds` 要求歷史輸出存在。

原映像依序選擇明確 `--firmware`、工作區 `exports/.../ID-2966-V4.1.60-decoded.bin`、發布用 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，全部仍要求精確 76800 bytes 與 SHA-256。`path-resolution.json` 確認 W/P/D 現存檔案能唯讀定位且 hash 相同，不代表已在三者執行 native build。本輪已在 Windows 實測直接 Python CLI；POSIX launcher 僅交付原始碼，沒有透過 WSL／Git Bash 執行。

Fresh build 只需三個釘選 native/public 原始檔、本 verifier/parser、離線原映像及本機 LLVM，不依賴舊 build、完整原映像 gate、網路或硬體。輸出只有 component ELF／IR／log，沒有韌體 BIN。`results.json` 選定兩份逐 byte 相同的結果副本；編譯產物與負向來源只保留本機 `build/`。Receipt 保留原 compile-run script hash，以及完成 C++ IR attribute／預設檔案定位後的最終靜態 replay。靜態證明通過不能當作原配置適用或韌體 ready。

唯讀 checker 核對封存來源與 metadata；若本機選定歷史檔案存在，會重做 ELF／IR／原生／控制檢查，缺檔會明確列出。只核對 metadata 不等於重新編譯。本 review 沒有修改原映像、模型、舊封存資料或交付／發布 checkout。
