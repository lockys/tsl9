# 已驗證里程碑

## 可讀的原生中斷初始化

新增元件以可讀 C/C++ 重建 `0x9A42` 及四個 RCC 輔助函式；原生版本直接使用 volatile MMIO 與 CSR 指令。原始五個函式共 264 bytes／94 條指令，來源核對拒絕 94 個原始指令突變。主機測試每語言通過 4 組／6,680 項；獨立測試每語言通過 4 組／34,267 項，六個實際編譯反例均遭拒絕。

C11 與 C++17 也能編譯及連結成獨立 RV32 元件：四個 helper 各 22 bytes，初始化本體 118 bytes。LLVM IR 與實際機器碼檢查均核對 20 個有序效果，包含六次重新讀取 RCC、確切 word／byte 寬度、CSR 清除／設定遮罩及最後的 RMW 回傳值。八個實際編譯的原生突變均遭拒絕。這些是獨立元件檢查，尚未替換完整韌體，也未證明原始堆疊／暫存器 ABI；沒有 RV32 執行或實體 I/O。既有 691-section／8,280-relocation 映像及唯一缺少實作的 resident 入口保持不變。

本元件來源／主機檢查使用 `sh experiments/tsl9-v4160-interrupt-init/verify.sh --language both`。原生檢查需要 LLVM，明確 CLI 記錄於 `analysis/v4160-interrupt-init-2026-10-21/native-plan/`。上一輪跨平台 CI 因 GitHub 帳戶付款／支出限制，在任何步驟前就停止；沒有重跑，也沒有變更付費設定。

## 跨平台入口與時脈計算

新的 Python 驗證入口涵蓋 runtime-loop、system-clock-query、resident-entry 與 resident-copy 四個模型。每項先核對封存來源證據，再編譯及執行自行重建的 C11／C++17 主機測試。Windows 原生編譯器測試已通過；Linux、macOS 及 shell 啟動須另以 CI 證據確認。此入口不依賴 PowerShell 或 CMake。

新增時脈模型涵蓋 ID2966 V4.1.60 的 `0x18834..0x188E2` 與 `0x1973C..0x19764`，共 214 bytes／69 條指令，來源核對拒絕 50 個 raw operand 突變。每語言通過 7 組／1,414 項。保留分開讀取 RCC、當下暫存器與位址、即時 prescaler 表、無號運算及依寬度寫入。初始化整合只綁定兩個已有證據的呼叫點，中間呼叫仍為未知實作。

## 先前重建模型

| 模型 | 來源證據 | 每語言主機測試 |
| --- | --- | --- |
| Runtime 主程式、初始化、迴圈與派送 | 220 bytes／80 指令；拒絕 45 個 raw 突變 | 6 組／1,431 項 |
| resident 候選入口、初始化與 RAM seed | 230 bytes／66 指令及 4-byte header；拒絕 35 個 raw 突變 | 5 組／121,496 項 |
| 候選 byte-copy | 58 bytes／18 指令；拒絕 23 個 raw 突變 | 5 組／772 項 |

以上是選定範圍的來源與合成主機行為證據。原始韌體只作資料讀取，不執行或模擬。resident 候選在 `0x6EB2C` 缺少原始 bytes，合成延續無法證明缺少的實作。

## 移植進度與證據限制

移植盤點記錄 116 支歷史 PowerShell 腳本與 93 個根目錄 suite。四個跨平台模型不能取代原本 RV32／ELF、整合或下載檢查。新下載器原型僅支援 dry-run 與離線 HTTP 邊界替身；23 個案例不代表已從廠商下載成功。

來源證據位於 `analysis/*/source/`。完整本機獨立審查與整合收據可能綁定未發佈的主機執行檔及日誌。`publication-manifest.json` 核對實際發佈的檔案。歷史封存文件保留原始 bytes；新的使用說明分為英文與繁體中文文件。

WCH CH32V20x 目前是硬體假說，並未確認為 TSL9 料號。原機 ROM、板子、啟動／中斷 ABI、實體 Flash 與 BLE OTA 接受性仍未證實。原有 76,800-byte 來源一致離線映像維持 **NOT-FLASH-VALIDATED**。
