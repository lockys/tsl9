# TSL9離線C/C++重建

[English](readme.en.md) | [简体中文](readme.zh-CN.md)

本專案保存原始APK、22份不同的更新器BIN、可讀C/C++行為模型及靜態來源證據。完整目標仍是產出與原硬體及BLE更新器相容的重建BIN，並在逆向過程中評估值得新增的功能，將提案與已實作功能分開列出。**目前尚無經驗證可刷寫的重建BIN。**

## 完整暫存器保留配方仍未符合原始 ABI

以每個原始 leaf 的可寫暫存器與三個輸入推導唯一完整 mask，C11／C++17 六份實際物件都能編譯。選定 compare60／fill68／copy64 bytes（23／24／22指令），但全部新增16-byte frame與RA／SP寫入，fill另暫時寫A2；因此此配方不能直接替換原機leaf。完整物件各保留十一個真實global FUNC，為454／492／418B，UND／RELA皆零。**沒有新BIN，舊元件及實驗映像保持不變。**

另完成原始0x188E2與唯一相依0x19160共106B／37列：對callback傳入的0x40012400，遮罩0x200先OR、再fresh read並AND ~mask；不能宣稱整字恢復原值。此有界鏈在明示前提下保存SP／RA／S／GP／TP，仍未證明整個callback或config52生命期。下一來源缺口為0x19896→0x1892E。[C/C++、獨立ABI與來源證據](analysis/v4160-register-contract-2026-10-22/README.md)

## 原生記憶體 IO 入口已移除 context 與 frame

沿用封存的共享 C 演算法，新增真實 volatile byte／word IO 與 FENCE.I。兩個實測 profile 後，C11／C++17 三參數、單值回傳入口為 compare52／fill48／copy52 bytes，合計152B／52指令；三入口無 context／sret、call 或 SP／RA／S／A1／A2 明示寫入。整個物件仍包含八個未使用的真實 global functions230B，總382B／138指令，0UND／0RELA。**額外暫存器、scratch與fault時序仍不同，fill也超過原範圍2B；完整ABI與placement未通過，沒有新BIN。**

原App field44的197F0入口已界定364B／130指令，並核對第一段aligned填零路徑與兩個小RCC leaf；13個呼叫點及無明示timeout的輪詢仍有未解依賴，不能宣稱callback後staCB保持零值。 [原生C/C++、實物與限制](analysis/v4160-resident-native-2026-10-22/README.md)

## 三個候選記憶體 leaf 已重建為 C/C++

新增比較固定 byte、填值與向前複製的 C11／C++17 元件，保留參數判斷前的 MMIO guard、FENCE.I 與正常退出恢復。比較採完整32-bit期望值；fill回傳前移位址，copy回傳原目的位址並保留重疊時的向前回饋。以合成 IO 測試及原生物件檢查驗證，**尚非原機 ROM provider，沒有新 BIN**。

兩候選完整初始化228B／92指令已讀取；在明示映射、有效記憶體、無不利 alias／非同步修改及正常返回條件下，staCB零值推導可延伸至設定copy與第一個後續callback入口。該callback的原App數值來源為197F0；tsCB／temperature名稱仍屬header推論，其效果與後續初始化待證。 [C/C++、證據與限制](analysis/v4160-resident-memory-2026-10-22/README.md)

## 550-byte C/C++ 已取得原回覆位置的獨立物件

新 C11／C++17 元件為 **550 bytes／186 指令／48-byte frame**；真實4-byte物件位於SP+12..15，只寫前兩bytes，不與最低SP+16的保存槽重疊。在相同入口SP前提下，回覆指標均為原來的SP−36；S回覆長度2與E空回覆0/0也已獨立核對。**只閉合這個位置／物件投影，額外S6保存、完整callee／IRQ ABI、placement及OTA仍待證；現有568元件與BIN不變。**

另完成50-byte MAC helper與兩候選46-byte fill leaf的局部範圍核對。原App在指定有效stack、正常存取、無alias／非同步變更等條件下，可推導BLE初始化入口的staCB為零，不能延伸到callee內部或後續callback生命週期。 [程式、實檔證據與條件](analysis/v4160-config-lifetime-2026-10-22/README.md)

## 配置 callback 欄位來源與 556-byte C/C++ 實驗

兩份候選 BLE 初始化的實際64-byte copy，已追到配置 callback word 來自設定結構 `staCB`（+52）；兩份 header 以真實 RV32 C 編譯核對欄位，原 App 的 SNV 設定數值為 `0x08077C00`，並不代表其餘 Flash 可用。另以兩個有依據的 C 生命週期調整，將 OTA 元件縮為 **556 bytes／188 指令／48-byte frame**，移除一對 S8 保存；回覆物件為獨立 SP+10/11，仍比原 SP+12/13 低2 bytes，**指標 ABI 尚未通過，不替換現有568元件或完整 BIN**。 [程式、實檔證據與限制](analysis/v4160-allocator-callback-2026-10-22/README.md)

## OTA 原 caller 已接上真實 C/C++，新增完整實驗映像

新的 C11／C++17 同 TU 強別名接上原 caller；實際 `0x14094` 的 JAL 已指向 `0x1AC00`，返回地址仍為 `0x14098`。兩語言產出相同 **77,824-byte** 實驗 BIN；繼承的 76,800 bytes 中只有該指令的三個 bytes 改變，原 530-byte handler 保留，尾端新增 568-byte C 與 456-byte 非執行 FF 頁尾資料。SHA-256：`3be918942c03de99c8a5f3fb7d6eba40ab9af63930020efb7f4cac07cc9a10ee`。

**這不是已驗證可刷寫的 BIN。** 部分連結仍保留真實 ROM UND；完整 ELF 只沿用原始 `0x18730` 指令已指向的 `0x40000` 數值見證，不提供 ROM 實作或實機身分證明。新增區域的 Flash／NV 所有權、callee／堆疊 ABI、實體 BOOT 與 OTA 接受／恢復仍待證。兩份候選配置路徑會把 ambient A2 傳到另一個未知 callback，不能宣稱回覆地址不被觀察。 [程式與證據](analysis/v4160-ota-source-wiring-2026-10-22/README.md) | [實驗映像](artifacts/offline-images/ID2966-V4.1.60-ota-source-wired/README.md)

以下各里程碑的「未整合／沒有新 BIN」敘述只適用於該歷史範圍。

## OTA 的九個 provider 已完成真實部分連結

既有 568-byte C／C++ 元件已用真實 provider 物件完成 `ld.lld -r`：九個外參照均解析至配置區段，只剩原有 ROM 入口未解析。**原 caller 尚未改向新 C，沒有 final ELF 或新 BIN。** 同時確認回覆指標會逃逸到配置 slot 的 A2；候選 BOOT 的 Runtime 頁上限為95，其後數值餘量不代表 free Flash。 [連結工具、原碼證據與配置限制](./analysis/v4160-ota-handler-layout-2026-10-22/README.md)

## OTA 原生元件縮減至 568 bytes

以回覆陣列的生命週期分離及三個共用 C 回覆出口，將元件由 776 bytes／285 指令／112-byte frame 縮至 **568 bytes／193 指令／48-byte frame**；八個暫存器呼叫橋接與各命令效果保留。仍超出原 530-byte 範圍 38 bytes，**未連結、未新增 BIN；完整 TX 映像不變**。前輪分析 README 的「四個展開 quarter callsite」已另附更正，真實物件是一個迴圈呼叫點。 [程式、獨立核對與限制](./analysis/v4160-ota-handler-compact-2026-10-22/README.md)

## OTA 命令已重建為共享 C/C++

新增 U／S／W／R／E 命令的可讀 C11／C++17，保留 UID、長度、頁碼、即時模式、四次 quarter 寫入與逐 word 讀回的先後順序。兩語言各通過本組及獨立 HOST 測試；實際原生物件均為 **776 bytes／285 指令／112-byte frame**，相較原 530-byte 範圍多 246 bytes，九個外部參照仍為真 UND。**尚未連結或納入 BIN；原有完整 TX 映像維持不變。** W 寫入 BOOT 別名，不代表已證明 Runtime 自更新。 [程式、證據與缺口](./analysis/v4160-ota-handler-2026-10-22/README.md)

## callback 原生元件縮減至 624 bytes

新的 C11／C++17 元件均為 624 bytes／223 條指令：明確保留 S10／S11，將六個 GP 使用位置改為讀取當下實體 GP，並以明示步驟交換兩個既有保存指令。48-byte frame、十一組保存／還原、十五個間接呼叫已由獨立審查核對；本輪未重跑 HOST。原始剩餘 8 bytes 含有可執行指令，完整 prefix、呼叫返回 ABI、尾區所有權及原位配置尚未證實。**元件尚未整合，沒有新增 BIN；原有完整 TX 映像維持不變。** [證據與限制](./analysis/v4160-callback-registers-2026-10-22/README.md)

呼叫邊界的後續靜態核對確認：GP+42 的半字在新舊呼叫前均已覆寫，沒有這裡的 A4 漏傳；兩份官方 ROM 候選的 `+0x13C` 小函式對只按一般方式保存／返回 RA，不觀察 caller S4／S7。這縮小了部分限制，但不證明實機 ROM 身分或其餘 callee。候選 slot 對應 CCC 設定讀取與通知送出；讀取可回傳 0..255，仍須區分原始 `==1` 與 `&1` gate。 [呼叫邊界與候選條件](./analysis/v4160-callback-call-frontiers-2026-10-22/README.md)

## 先前事件 callback 的可讀重建與原生差距

`0x8614..0x888C` 的 632-byte callback 已重建為可讀 C/C++，涵蓋事件優先序、兩組 context／connection、分段長度、重試與後續事件。原生明確內聯診斷由 1,034 bytes 降到單函式 658 bytes，取得 48-byte frame／十五個間接呼叫；仍超出 26 bytes，且額外 S10 保存、儲存順序、返回地址及未知 ROM 契約未閉合。**此 callback 尚未納入完整 BIN，沒有新增可刷寫映像。** [分析與限制](analysis/v4160-event-callback-2026-10-22/README.md)

## TX 已納入完整實驗 BIN

正式 C11／C++17 各新編譯 46 個單元，產出相同的 76,800-byte 實驗 BIN；十三個原始函式範圍共 930 bytes，由十五個真實 FUNC 角色承接，678 個其餘區段仍使用原始承載。與官方 ID2966 的 93 個差異全部位於 TX，其餘 byte 相同。SHA-256：`28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89`。**新 BIN 尚未驗證可刷寫。** [完整整合](analysis/v4160-tx-image-integration-2026-10-22/README.md) | [實驗映像](artifacts/offline-images/ID2966-V4.1.60-tx-integrated/README.md)

## 跨平台驗證

OTA 傳送入口 `0x8A56` 已取得實際 280-byte 原生元件：8-byte 窄組語入口、270-byte 可讀 C/C++ 主體及 2-byte 返回函式。超長輸入可直接返回、不碰堆疊，兩次 ROM 呼叫的返回位址吻合。暫存器儲存／還原時序以新的獨立排序步驟核對；**此元件已納入上述新版映像，仍未經原硬體或 BLE OTA 驗證**。詳見[入口與呼叫框架分析](analysis/v4160-tx-register-abi-2026-10-22/README.md)、[原始傳送契約](analysis/v4160-ota-tx-2026-10-22/README.md)及[新功能提案](analysis/v4160-ota-tx-2026-10-22/continuation-plan/README.md)。

先前完整映像已納入 OTA 頁面回覆：12 個可讀 IRQ／Flash／OTA 函式共 650 bytes，完整 76,800-byte BIN 與官方 ID2966 V4.1.60 相同。C、C++ 各新編譯 43 個單元，61 個命令含兩次明確 ABI 排序；全部單元記錄完整標頭依賴。其餘 679 個區段仍使用原始承載，這是部分來源重建，**不是原硬體或 BLE OTA 驗證**。詳見[新版整合](analysis/v4160-reply-image-integration-2026-10-22/README.md)與[離線映像](artifacts/offline-images/ID2966-V4.1.60-reply-integrated/README.md)。

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
| 十一個 IRQ／Flash 函式整合的完整離線映像（尚未驗證可刷寫） | [繁體中文說明](analysis/v4160-flash-image-integration-2026-10-22/README.md) |
| 五個 Flash 葉函式的暫存器與指令前綴一致 | [繁體中文說明](experiments/tsl9-v4160-flash-register-prefix/README.md) |
| 明確的 ABI 堆疊保存順序處理與唯讀重驗 | [繁體中文說明](experiments/tsl9-v4160-frame-schedule/README.md) |
| 十一個可讀函式與官方 bytes 相同的完整離線映像 | [繁體中文說明](analysis/v4160-register-image-integration-2026-10-22/README.md) |
| 新功能候選與既有功能證據 | [繁體中文提案](analysis/v4160-irq-callframe-2026-10-21/feature-candidates/readme.zh-TW.md) |
| Runtime主程式／初始化／迴圈／派送 | [說明](experiments/tsl9-v4160-runtime-loop/readme.zh-TW.md) |
| resident候選入口與byte-copy | [入口](experiments/tsl9-resident-entry-reference/readme.zh-TW.md)／[copy](experiments/tsl9-resident-copy-reference/readme.zh-TW.md) |
| 發佈檔案身分 | [Manifest](publication-manifest.json) |

WCH CH32V20x已列入硬體假說，CH32V208是其中值得比對的子系列。暫存器配置與程式相似仍不能辨識TSL9確切料號、板子、原機ROM、接腳或中斷ABI。resident候選擷取資料仍有缺漏；合成條件的延續不補原始缺洞。

原有76,800-byte來源一致離線映像仍為**NOT-FLASH-VALIDATED**。測試不存取BLE、UART、CAN或實體Flash。每個完成驗證的里程碑commit／push。`README.md`預設顯示繁體中文；英文與簡體中文分別放在`readme.en.md`與`readme.zh-CN.md`，`readme.zh-TW.md`保留獨立的繁體中文版本。各語言分開維護，歷史封存文件保留原始內容。發佈排除真實裝置識別資料、憑證、私有請求／回覆日誌及暫存編譯產物。
