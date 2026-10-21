# Flash 元件獨立審查

[English](readme.en.md)

本審查以原始 ID2966 V4.1.60 的來源證據，獨立核對六個可讀 C/C++ Flash 函式，實際編譯元件物件檔與 ELF，並執行合成主機測試。沒有執行韌體、連接硬體或原廠服務，也沒有產生新的韌體 BIN；目前不能視為可 OTA 燒錄成果。

## 跨版本證據與可重用部分

`compare-versions.py` 實際產生的 `cross-version.json` 綁定本次映像、舊 V4.1.00 Runtime 與舊 BOOT 的雜湊。原始 Runtime 五個 helper（18E90、18E98、18EB6、18EC4、18EF2）與舊版 18BE4、18BEC、18C0A、18C18、18C46 合計 198 位元組完全相同。64 位元組包裝函式由 9B6C 移到 9C0A；十個差異位元組全部落在五個直接 JAL 的運算元內。小型靜態解碼器核對跳轉目標，不執行指令。包裝函式與 helper 的位址差不同，因此不能推廣成整個映像的固定搬移規則。

舊 `experiments/tsl9-contract-model/src/flash_page.c` 可提供控制器位址、解鎖鍵、遮罩、即時來源字組讀取、輪詢與操作順序的獨立參考，不能直接證明新函式的堆疊或暫存器 ABI。舊模型的 `FP_RETURNED` 是主機流程狀態，並非原生 Flash 成功碼；測試輪詢額度也不是硬體逾時。另一個 V4.1.60 `flash_contract.c` 對應 197BE，而非本次 9C0A，不能沿用其回傳零的慣例。`reuse-contract.json` 明確記錄這些界線。

## 已實際完成的驗證

`receipts/` 收錄實際新跑結果的原樣 JSON，不是事後重製摘要。C11、C++17 各自通過正式主機測試 5 組、481 案例、247191 項檢查，以及六個實際編譯的行為突變控制。獨立編寫的預期效果測試，各通過 12 情境、8964 項斷言，並拒絕另外十二個實際編譯的突變版本；核對操作位置、順序、寬度、值、已知位元遮罩、重新讀取控制器值、SP+12 來源替換及正常返回的輸出欄位。

每個語言的原生編譯，靜態核對六函式共 256 位元組、98 指令，大小依序為 64/8/30/14/46/94。兩種語言的元件 ELF SHA-256 相同：`1097156d90ee982a6c03c903785b563acae0357d1bbc7b7c2e29315adbf5d613`。各結果綁定 41 個產物及六條編譯器依賴規則，涵蓋三個專案原生輸入檔；此依賴清單不含編譯器系統／資源標頭。檢查包含正常 ABI 模式、全部輸出指令、CFG、ELF、ISA 與 IR 限制。兩語言合計拒絕 30 個機器碼位元組控制及六個 IR 文字控制；IR 控制修改保留的文字，沒有重新編譯，與合計 36 個主機實際編譯控制的證據層級不同。原始來源檢查另核對 262 位元組、99 指令及 20 個原始位元組控制。

審查曾發現三處不足，已在上述最終新跑前修正：先建立正常效果的順序／值斷言再比較流程前綴；主機檢查改為精確涵蓋量並核對執行前後 runner/helper 雜湊；原生審查改收真正的模型來源目錄。`review.json` 綁定精確輸入、結果與未解限制。

## 仍未證實的部分

新原生 program 函式在初始輪詢後才對齊 A0，原始 18EFA 較早對齊。包裝函式保有原始 32 位元組堆疊框架與重新讀取 SP+12 來源，但前言儲存順序不同。因此未返回／錯誤時的實體暫存器前綴，以及逐點／非同步等價性都未成立。主機流程前綴只涵蓋 provider 效果；正常返回的暫存器欄位不是硬體擷取結果。A0 回傳對齊目的位址，不代表控制器成功狀態。CSR 0x800 先清除後設定遮罩 136，不是恢復先前值；原始輪詢沒有逾時或錯誤清理。

program 由原始 100 位元組變為 94，剩餘六位元組尚未證明可用、分配或整合。本次沒有完成全部入口／內部／計算參照的所有權核對、整個映像整合、已安裝 BOOT 身分確認、Flash 持久化、時序／故障、ROM 約束、實體相容性或 OTA 接受驗證，也沒有實作新的產品功能。

## 重現方式

於專案根目錄使用 Python 3，輸出目錄必須全新：

```sh
python experiments/tsl9-v4160-flash-native/verify.py --project-root . --language both --build-root apk-analysis/tsl9-v4160-flash-native-2026-10-22/review/build/host-new
python apk-analysis/tsl9-v4160-flash-native-2026-10-22/implementation/verify_native.py --project-root . --tool-dir /absolute/llvm/bin --language both --build-root apk-analysis/tsl9-v4160-flash-native-2026-10-22/review/build/native-new
python apk-analysis/tsl9-v4160-flash-native-2026-10-22/review/check-review.py --project-root .
```

主機編譯器需受 `scripts/portable_verify.py` 支援；原生工具使用 Clang、LLD、llvm-objdump，runner 也接受明確的編譯器、連結器、objdump 與韌體路徑。這些命令只編譯及靜態檢查原生產物，不執行 RV32 程式。

在 `check-review.py` 加上 `--firmware /absolute/ID-2966-V4.1.60-decoded.bin` 可核對原始來源。重新跨版本比較時，另需同時提供 `--old-runtime`、`--boot`、`--old-evidence`。歷史證據檔是 `apk-analysis/tsl9-function-hardware/fifteenth-round/flash-review/native-evidence.json`，發布目錄不保證具備，請明確提供合法持有的本機檔案；缺檔是未滿足輸入條件，不能當成通過。沒有為補連結而複製舊 APK／來源封存。

若仍保留本機編譯封存，可加 `--archive-root /absolute/review/build` 重驗四份正式主機／原生結果。保留結果內的絕對路徑及工具指紋代表實際 Windows 執行環境；封存重驗需要相符產物、工具及目錄，與新跑支援明確路徑的可攜性不同。編譯封存、執行檔與突變副本不在本審查封存範圍。`seal.json` 綁定發布的審查檔案，不能代替完整重驗所需產物。
