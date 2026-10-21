# IRQ 可讀來源完整映像整合

[English](readme.en.md)

這個里程碑將已驗證的 IRQ 初始化與四個 RCC helper 放回完整原始布局。**產物仍為 NOT-FLASH-VALIDATED，不能視為可刷寫韌體。**可讀 C/C++ 只取代五個函式；其餘程式與資料仍由保留的原始指令／資料來源載入，沒有宣稱完整還原原始碼。

## 如何重建

需要 Python 3.10 以上及可編譯 RV32 的本機 LLVM 工具。由專案根目錄執行：

```sh
sh experiments/tsl9-v4160-irq-image-integration/verify.sh --tool-dir /path/to/llvm/bin --language both
```

也可用 Python 直接執行同一入口；Windows 已驗證的 Python／LLVM 結果不代表 POSIX shell、Linux、macOS 或 CI 已通過。所有結果寫入新的 build 目錄；不執行或模擬 RV32，不操作 BLE、UART、CAN 或實體 Flash。

## 驗證範圍

- 由固定的 34 個原始來源單元與兩個可讀 C/C++ 單元重新編譯。僅移除五個被取代的原始指令區段，保留其他來源。
- 保留 691 個配置範圍、其餘 686 段儲存內容、53 個區段內符號綁定及 8 個外部進入呼叫。核對符號角色，避免用絕對位址假造函式。
- 保留 8,270 筆範圍外 RELA；新核心有六筆 JAL，四筆已由相同 helper bytes 證明不再需要的內部分支 RELA 被明確解除。新總數應為 8,276。
- 完整嚴格連結必須回報缺少唯一的 resident ROM provider。另一個獨立檢查只指定原始 ROM 位址 `0x40000`；沒有供應 ROM bytes 或證明它存在。
- 匯出映像必須恰為 76,800 bytes，全部來自實際區段與 ELF LOAD；無補洞、原始 BIN 回填或 RAM NOBITS 匯出。只允許 `0x9A44..0x9A4B` 八個明確值差異。
- C/C++ 分開編譯並比較產物；透過實際 ELF、重定位與映像負例檢查拒絕錯誤配置。收據綁定來源、工具、指令日誌與實際產物。

實際結果與雜湊請讀 [整合紀錄](integration/)；獨立核對位於 [契約審查](contract-review/) 與 [來源審查](source-review/)。這些證據不能互相替代。

## 尚未通過的目標

四個暫存器保存指令的順序與原始不同，最終 frame 相同不等於任意中斷時點等價。原機 ROM、完整板子／晶片辨識、所有執行期資料與回呼、啟動與中斷相容性、更新器接受性、實體 Flash 與 BLE OTA 均尚未完整證明。原始 APK 與 22 份廠商 BIN 保持原樣。

[功能候選](../v4160-irq-callframe-2026-10-21/feature-candidates/readme.zh-TW.md) 仍為提案，沒有隨這份映像新增免打擾說明、狀態面板、快照、檢查器或診斷匯出功能。

