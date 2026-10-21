# TSL9離線C/C++重建

[English](readme.en.md) | [简体中文](readme.zh-CN.md)

本專案保存原始APK、22份不同的更新器BIN、可讀C/C++行為模型及靜態來源證據。完整目標仍是產出與原硬體及BLE更新器相容的重建BIN，並在逆向過程中評估值得新增的功能，將提案與已實作功能分開列出。**目前尚無經驗證可刷寫的重建BIN。**

## 跨平台驗證

需要Python 3.10以上、C11／C++17編譯器及POSIX shell。Linux可用GCC或Clang；macOS可用Clang；Windows可用Git Bash加Visual Studio C++ Build Tools。新的跨平台入口不需要PowerShell或CMake。

```sh
sh ./verify.sh --list
sh ./verify.sh --model runtime-loop --language both
sh ./verify.sh --model system-clock-query --language both
```

`sh ./verify.sh`執行目前全部已登錄的跨平台模型；也可直接執行`python scripts/portable_verify.py`。`CC`／`CXX`可指定單一編譯器執行檔；shell入口可用`PYTHON`指定Python執行檔。路徑以專案位置解析，不依賴呼叫者的工作目錄；產物寫入新的忽略目錄。

第一批跨平台項目為runtime-loop、system-clock-query、resident-entry及resident-copy。每項核對確切原始檔案、封存的raw來源證據、程式依賴與C/C++主機行為；收據記錄實際編譯器及執行檔雜湊。原始韌體只當資料讀取，不執行或模擬。

儲存庫另有116支歷史PowerShell腳本；其中RV32、ELF、整合與下載檢查須逐項移植，主機測試通過不能取代這些檢查。歷史封存檔案保留原bytes，移植清單會標示精確範圍。跨平台CI、本機測試與實體硬體證據分開報告。

## 內容

| 內容 | 位置 |
| --- | --- |
| 原始APK 1.2.7 | [APK](artifacts/apk/安卓-TSL电子模块-1.2.7-1.apk) |
| 22份原始解碼BIN | [韌體封存](firmware-downloads/legacy-options-2026-10-20/BINs/) |
| 新時脈計算模型 | [繁體中文說明](experiments/tsl9-v4160-system-clock-query/readme.zh-TW.md) |
| 可讀的原生中斷初始化 | [繁體中文說明](experiments/tsl9-v4160-interrupt-init/readme.zh-TW.md) |
| 可讀的原生時脈與衍生欄位 | [繁體中文說明](experiments/tsl9-v4160-native-clock/readme.zh-TW.md) |
| 時脈正常返回暫存器契約 | [繁體中文說明](experiments/tsl9-v4160-clock-registers/readme.zh-TW.md) |
| 啟動資料複製、BSS 清零與輸出暫存器 | [繁體中文說明](experiments/tsl9-v4160-reset-memory/readme.zh-TW.md) |
| 中斷初始化正常暫存器契約 | [繁體中文說明](experiments/tsl9-v4160-interrupt-registers/readme.zh-TW.md) |
| 原址機器碼一致的 RCC helper 與新版 IRQ 核心 | [繁體中文說明](experiments/tsl9-v4160-irq-native/readme.zh-TW.md) |
| 可放回原區段的 144-byte IRQ 呼叫框架 | [繁體中文說明](experiments/tsl9-v4160-irq-callframe/readme.zh-TW.md) |
| IRQ 可讀來源與完整原始布局整合 | [繁體中文說明](analysis/v4160-irq-image-integration-2026-10-21/readme.zh-TW.md) |
| 六個可讀 Flash 函式與原址元件 | [繁體中文說明](analysis/v4160-flash-native-2026-10-22/README.md) |
| 自然產生 100-byte program 與原始進入順序 | [繁體中文說明](analysis/v4160-flash-entry-order-2026-10-22/README.md) |
| 新功能候選與既有功能證據 | [繁體中文提案](analysis/v4160-irq-callframe-2026-10-21/feature-candidates/readme.zh-TW.md) |
| Runtime主程式／初始化／迴圈／派送 | [說明](experiments/tsl9-v4160-runtime-loop/readme.zh-TW.md) |
| resident候選入口與byte-copy | [入口](experiments/tsl9-resident-entry-reference/readme.zh-TW.md)／[copy](experiments/tsl9-resident-copy-reference/readme.zh-TW.md) |
| 發佈檔案身分 | [Manifest](publication-manifest.json) |

WCH CH32V20x已列入硬體假說，CH32V208是其中值得比對的子系列。暫存器配置與程式相似仍不能辨識TSL9確切料號、板子、原機ROM、接腳或中斷ABI。resident候選擷取資料仍有缺漏；合成條件的延續不補原始缺洞。

原有76,800-byte來源一致離線映像仍為**NOT-FLASH-VALIDATED**。測試不存取BLE、UART、CAN或實體Flash。每個完成驗證的里程碑commit／push。`README.md`預設顯示繁體中文；英文與簡體中文分別放在`readme.en.md`與`readme.zh-CN.md`，`readme.zh-TW.md`保留獨立的繁體中文版本。各語言分開維護，歷史封存文件保留原始內容。發佈排除真實裝置識別資料、憑證、私有請求／回覆日誌及暫存編譯產物。
