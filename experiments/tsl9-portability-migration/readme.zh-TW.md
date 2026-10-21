# 已發布腳本的可攜性盤點

本獨立工作以提交 `99de4f9d4da22f0cd28e039e0197defebf48fb72` 的發布目錄為準。沒有修改發布檔案、目的專案、既有封存證據或原生驗證器；**不宣稱 116 份 PowerShell 全已移植**。

| 靜態分類 | PS1 數量 |
| --- | ---: |
| C/C++ 主機測試 | 54 |
| RISC-V／ELF 原生驗證 | 50 |
| 主機測試加 RV32 編譯 | 2 |
| 調度或證據腳本 | 9 |
| 下載器 | 1 |
| 合計 | 116 |

`inventory.json` 記錄全部 116 份腳本的路徑、SHA-256、參數、編譯旗標文字、來源／測試檔案、執行引數與證據檢查標記，另含 33 份已發布 Python 及 28 份 BIN。`suite-map.json` 對應原根入口全部 93 個 `-Suite` 選項，各入口均存在。這是靜態文字盤點，不是 PowerShell AST，也不等於每個入口都已可攜；動態組合路徑仍須人工核對。位於 `tests/` 且明示以上層為根的腳本已按該規則解析。

## 移植時必須保留的條件

- 明確障礙包括 MSVC `DevShell.dll`／`Enter-VsDevShell`、Windows NDK 路徑、可執行檔副檔名，以及硬編碼的使用者 Python 路徑。僅以 shell 呼叫 PowerShell 不算移除依賴。
- 主機編譯／測試、原始來源證據、RV32 ELF 驗證是不同關卡。既有 clock 與 memcmp 入口同時執行主機測試及 freestanding 目標編譯；若只移植前者，後者必須明列尚待完成。
- 必須保留 C11／C++17、警告視為錯誤、原始來源／夾具雜湊、範圍檢查、測試引數、封存與建置後輸入未變檢查。ELF 驗證另須保留實際儲存／符號角色、完整 relocation 多重集、own-HI／LOW 配對與負例。
- 舊主機程式的引數並不一致：有些接專案根、有些接 Runtime 與 BOOT、有些不接參數。`host_runtime_argument_lines` 保存原始對應行；啟用通用 runner 前仍須核對來源檔與推導檔名。
- 所需原 BIN 已發布。ID2966 V4.1.60 為 76,800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。舊 Runtime ID2581 同為 76,800 bytes，但雜湊是 `32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc`。所選 BOOT ID2580 為 12,288 bytes，雜湊 `650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb`。不能因大小相同就混用 Runtime。
- 已以明確可攜參數重播五份發布中的來源檢查器：BOOT command、BOOT UID、resident-copy reference、resident-entry reference、V4.1.60 runtime-loop。它們支援 `--check`、`--firmware` 或 `--carrier` 以及 `--source-root`。另一份 `tx-source/check-source.py` 雖有 `--check`，卻沒有這些根路徑參數，不能算已參數化。
- 其他 Python 只列為可重用候選。沒有偵測到 Windows 路徑文字，不代表整份驗證器已可攜或不依賴歷史證據。

## 一個有限的輔助工具

`download_firmware.py` 以 Python 標準函式庫重建既有下載器的目錄、回應與第一階段解碼契約，**僅提供 dry-run 與合成資料的 loopback 模式**。`download-firmware.sh` 直接呼叫 Python，沒有包裝 PowerShell。本工具刻意沒有正式廠商模式，也不接受真實 UID，不能取代原本需合法授權的實際下載流程。

| 舊參數 | 新參數 |
| --- | --- |
| `-FirmwareId` | `--firmware-id` |
| `-OptionsReceipt` | `--options-receipt` |
| `-OutputRoot` | `--output-root` |
| `-MockUri` | `--mock-uri`，只准 HTTP literal loopback |
| 無 | `--dry-run`，不送請求、不產生輸出檔 |

解碼器要求單一結尾標記、CRLF 分行、每頁 2,048 個十六進位字元、1..96 頁、回應上限 262,144 bytes，再逐 byte XOR `0xB7`。只有通過檢查的內容才寫入唯一且不覆寫的目錄，並核對寫後雜湊。錯誤不輸出任意回應或請求身分。只嘗試一次、不跟 redirect、不用代理、不重試。解碼資料仍屬第一階段候選；硬體適用性、執行與 OTA 就緒均未證明。

```sh
python3 -B download_firmware.py --firmware-id 2966 \
  --options-receipt tests/synthetic-catalog.json --dry-run
sh download-firmware.sh --firmware-id 2966 \
  --options-receipt tests/synthetic-catalog.json --dry-run
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
```

本 Windows 主機上的 Python 測試為 5 組、23 個行為案例，全部通過。Dry-run 實際啟動子行程 CLI；回應測試使用真正解碼／寫檔程式與離線 HTTP 邊界替身。最初 stub 確實因缺少 dry-run 行為失敗；port 0 的回歸案例也先觀察到失敗後才修正。

本機 socket loopback 曾實際嘗試，但被執行沙箱以 `PermissionError`、errno 13、WinError 10013 拒絕。Git for Windows `sh` 雖存在，卻在進入 wrapper 前因 `NtCreateDirectoryObject`、`0xC0000022` 失敗。沒有規避這些限制。**Socket 整合、shell wrapper 的實際執行，以及 Linux／macOS 執行均尚未驗證。** `verification.json` 已明列；離線替身通過不等於網路或跨平台實際執行通過。

## 重播與範圍

盤點使用固定提交的檔案清單，並核對發布目錄的實際 bytes。後續提交即使新增腳本，也不會悄悄改變這份 116 檔基線。

```sh
python3 -B inventory.py --published /absolute/published-checkout --check
python3 -B verify_migration.py --published /absolute/published-checkout --check
```

第二個命令完全唯讀，只重核盤點與封存成員。要產生新的測試收據，須在未封存副本使用 `verify_migration.py --run`；若提供 `--shell /path/to/sh`，必須真正執行 wrapper 成功才會通過。本盤點沒有安裝或呼叫編譯器，沒有執行原始／重建韌體、ISA、BLE 或硬體。父代理負責的可攜主機 runner 是另一項工作。
