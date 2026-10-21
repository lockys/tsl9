# 已驗證里程碑

## 原始尺寸的 Flash program 與入口事件順序

新版 C11／C++17 program 函式自然產生 100 bytes／38 指令。補回兩次 fresh 基底暫存器載入，並明確約束 A0／A5 primitive 後，整個區段由新來源持有，沒有 NOP、padding 或借用原始 bytes。六個 Flash 函式合計 262 bytes／99 指令，兩種語言產生相同元件 ELF。入口控制讀取位於 +4，接著在 +6 對齊 A0、+14 首次寫入控制暫存器；五個 program 迴圈目標仍位於原址，最後六個 bytes 是實際清理及返回指令。

主機每語言通過 481 案例／247,191 斷言，並拒絕六個實際編譯變異；新的獨立 expected-effect 測試每語言通過 12 情境／8,964 斷言及十二個編譯變異拒絕，所有主機執行檔均在啟動前後核對架構。獨立靜態審查另外核對實際元件 bytes、IR 及已知分支角色。另以不同韌體參考路徑實際編譯及重播，並確認錯誤參考 context 會被拒絕。

這補上前輪六個 bytes 的來源缺口，但並未保留所有指令邊界：原始 program 的 +8 位於新版四-byte 對齊指令內。scratch 暫存器、fault／非返回 prefix、非同步、ROM、板子及 OTA 相容性仍未證明。此元件里程碑沒有產生完整新映像或 BIN。已封存的下一階段整合規劃涵蓋 691 個配置、十一個可讀函式、680 段保留儲存、8,259 筆範圍外 RELA 及二十筆外部入口引用；預計的 42 個編譯單元尚非完整映像建置成果。詳見 [繁體中文說明](../analysis/v4160-flash-entry-order-2026-10-22/README.md)。主機入口為 `python experiments/tsl9-v4160-flash-entry-order/verify.py --language both`，原生靜態檢查入口為 `python analysis/v4160-flash-entry-order-2026-10-22/implementation/verify_native.py --project-root . --tool-dir <LLVM-bin> --language both`。Windows 證據不代表 shell、Linux、macOS 或 CI 已執行。

## 六個可讀 V4.1.60 Flash 函式

共用 C11／C++17 來源重建 quarter wrapper、status、unlock、lock、erase 與 64-word program。原始證據為 262 bytes／99 指令；六個原址原生元件分別為 64／8／30／14／46／94 bytes，status 與 lock 共 22 bytes 完全一致。正常返回契約保留 32-byte frame、fresh `SP+12` source reload、五個有序呼叫、CSR mask 136 與暫存器殘值。program 剩下的六個 bytes 尚無新的儲存來源；此輪沒有產生完整新映像或 BIN。

主機每語言通過 481 案例／247,191 斷言，並拒絕六個實際編譯變異；獨立 expected-effect 測試每語言另有 12 情境／8,964 斷言與 12 個已編譯變異拒絕。原生靜態檢查讀取實際機器碼及 IR，每語言另拒絕 15 個機器碼與三個 IR 反例。原始六函式、六個高位址 caller slice 與整個物件的已記錄重定位 frontier 分開保存證據。

frontier 在前輪物件的 8,276 筆 RELA 中找出 12 筆外部入口及 11 筆 owned 呼叫／分支，後續整合仍須保留其餘 8,265 筆完整角色。已記錄 RELA 沒有外部 interior target，不等於 ROM、間接數值引用或未知執行期沒有其他入口。frame 保存順序、fault／非返回 GPR prefix、逐指令／非同步狀態、板子／ROM／Flash 與 BLE OTA 仍未證明。詳見 [繁體中文說明](../analysis/v4160-flash-native-2026-10-22/README.md)。預設主機入口為 `python experiments/tsl9-v4160-flash-native/verify.py --language both`；原生入口為 `python analysis/v4160-flash-native-2026-10-22/implementation/verify_native.py --project-root . --tool-dir <LLVM-bin> --language both`。Windows 證據不代表 POSIX／Linux／macOS／CI 已執行成功。

## IRQ 可讀來源的完整離線映像

已實際重新編譯 34 個原始指令／資料載體與兩個可讀單元，並在 C11／C++17 分別連結、匯出相同的 76,800-byte 映像。新映像 SHA-256 為 `47f200dce24be25ac89d57922689da536259935e8615ba8195b10ca192895e1c`，只在 `0x9A44..0x9A4B` 有八個明確 byte 差異，對應四個 prologue 保存指令的順序。原始 APK、廠商 BIN 與先前來源一致映像未替換。

核對 691 個原始配置、686 段保留儲存、53 個真實區段內符號綁定及八筆外部進入呼叫；8,270 筆範圍外 RELA 保持完整角色與次數。新總數為 8,276，其中六筆為新核心 JAL，四筆原 helper 分支 RELA 由一致 bytes 明確解除。所有匯出 bytes 均由實際區段及 LOAD 支持；無補洞、原始 BIN 回填、RAM NOBITS 或 ROM bytes 匯出。

每語言有 36 個實際編譯單元的依賴閉包、44 個受檢指令及 15 個實際 ELF／重定位／映像負例。完整嚴格連結明確拒絕唯一缺失的 ROM provider；成功產物僅使用 `0x40000` 的數字位址見證。可讀 C/C++ 只取代五個 IRQ／RCC 函式，其餘仍是原始指令／資料載體，不能宣稱完整來源重建。

映像位於 [NOT-FLASH-VALIDATED-irq-callframe.bin](../artifacts/offline-images/ID2966-V4.1.60-readable-IRQ-integration/NOT-FLASH-VALIDATED-irq-callframe.bin)，入口與分開的獨立審查見 [繁體中文說明](../analysis/v4160-irq-image-integration-2026-10-21/readme.zh-TW.md)。原機 ROM、非同步中斷狀態、硬體、實體 Flash 與 BLE OTA 仍未通過；此 BIN **尚未驗證可刷寫**。Windows Python／LLVM 建置不代表 shell、Linux／macOS 或 CI 結果。

## 144-byte IRQ 呼叫框架與 C++ 配置

新版可讀 C/C++ main 改用六個四-byte JAL 呼叫既有 RCC helper，由編譯器建立 16-byte frame。C11／C++17 的實際 main 均為 144 bytes，四個 helper 各 30 bytes，264 bytes／94 指令全部位於原始區段，且無額外配置。C++ 的 `-fno-exceptions` 移除先前 unwind metadata；獨立 predecessor 實驗也確認此單一 flag 不改動其五個函式 bytes。

main 的第一條 SP 調整與 offset 10 以後的 134 bytes 原樣一致，四個 helper 的 120 bytes 完全一致。差異是四個兩-byte prologue store 的排列；frame slot 集合、六個 JAL 的 PC／目標／RA、所有指令邊界及還原載入分別核對。**逐指令 stack 狀態與非同步 IRQ 等價仍未通過。**

主機每語言通過 9184 案例／246384 斷言；獨立測試每語言 3820 案例／138312 斷言，共拒絕 60 個實際編譯變異。原生每語言拒絕六個已編譯／連結反例與 30 個覆蓋反例。完整 source-carrier 的下一階段整合規劃已找出 34 個 C TU、691 個配置、53 個 section-relative alias；四個 helper 的原始 branch RELA 由 byte 一致性解除，不能虛稱新物件仍有 8280 筆 RELA。

此輪尚未整合或生成新 BIN，原 76,800-byte 離線映像與 gate 保持不變；ROM、板子、硬體中斷及 OTA 相容性仍未證明。來源入口為 `sh experiments/tsl9-v4160-irq-callframe/verify.sh --language both`；原生入口為同目錄 `verify-native.sh --tool-dir <LLVM-bin> --language both`。Windows Python／MSVC／LLVM 證據不代表 Linux／macOS 或 shell 已執行成功，既有 CI 帳戶限制未重試或調整。

## 分支式 IRQ 核心與 RCC 原址 bytes

新版 C/C++ 核心讓兩條 RMW 分支各自保留讀取、運算、寫入與返回值，使用逐次基底／立即數與明確的 A0 返回橋接，並停用 machine outliner。四個 RCC helper 各 30 bytes，在原址 0x19124／0x19142／0x19160／0x1917E 連結後與原 BIN 的 120 bytes 完全一致；完整機器碼核對確認只寫 A0/A4/A5，A1 精確保留。IRQ 本體只寫 A0/A1/A4/A5，正常返回輸出符合原始契約；20 個有序效果及六次 fresh RCC 讀取分別由機器碼與 LLVM IR 檢查。

主機 C11／C++17 每語言通過 4 組／9184 案例／246384 斷言，沿用完整 264 bytes／94 指令來源證據。獨立主機測試每語言 3820 案例／138312 斷言，合計拒絕 44 個實際編譯變異。原生每語言另拒絕五個實際編譯變異與 30 個反組譯覆蓋反例。

本體 180 bytes 超過原始 144 bytes，尚未接受任何新位置。C++ 額外配置 `.eh_frame`：object 120 bytes、linked 124 bytes；已配置區段完全由函式持有的 gate 明確為 false，不能以「唯讀」免除整合義務。函式正常返回證據不等於中途狀態／非同步 IRQ 等價。完整映像、ROM、硬體與 OTA 相容性仍未通過，未執行 RV32、未改原始映像、未產生新 BIN。

入口為 `sh experiments/tsl9-v4160-irq-native/verify.sh --language both`，原生入口為同目錄的 `verify-native.sh --tool-dir <LLVM-bin> --language both`。新文件在 `analysis/v4160-irq-native-2026-10-21/`。Windows Python／MSVC／LLVM 證據與未驗證的 POSIX shell、Linux／macOS／CI 結果分開報告。

## 原址審查與中斷暫存器模型

確切配置池為八個分開的原始範圍，共 540 bytes：reset 記憶體 62、時脈查詢 174、衍生欄位 40、IRQ 初始化 **144**，四個 RCC helper **各 30**。綁定 bytes 的審查核對完整固定 linker layout 的 691 個 section 配置與 8,280 筆 RELA。helper 均有其他呼叫端；已納入的程式碼未見外部直接跳進內部，但 939 條間接指令使計算式目標仍未排除，總和算術不能證明可安全連續配置。

實際舊版原生 IRQ 本體否定了看似可用的空間：118-byte 初始化與 22-byte helper 都會寫入原始程式保留的 A2／A3，A1／A4／A5 返回值也不同。既有呼叫鏈上的 A3 會傳到未知 callback，這些舊本體尚不能依原始契約提供替換空間。

新的 `interrupt-registers` C/C++ 模型保留 20 個 MMIO／CSR 效果、helper 完整 A1 bits、分支特定 A4／A5，以及初始化最終 A1=0／A4=128／A5=`0xE000E000`。含完整來源證據的主機測試每語言通過四組／9,184 案例／246,384 項，屬主機正常邊界結果。預定原生配置目前五個函式均出現 `Stack pointer required, but has been reserved.`，未產生 object／ELF，**尚無通過的原生暫存器或原址證據**；三個有限診斷組合也失敗。IR 檢查與預期失敗重現，分開記錄，不當成成功編譯；分支內值生命週期的重整仍待實作。

另有確定的原生大小進展：未改動的 reset C/C++ 改用 `-Oz`，leaf／fragment 從 78／80 降為 66／68 bytes，原始為 62；實體 GP operand 從四處降為三處。時脈查詢／衍生欄位仍為 196／38。合成跳轉證據核對同 section 兩-byte C.J 與外部四-byte JAL x0 的幾何，沒有提供原始入口 adapter 或配置空間。未修改原始映像，也未產生 BIN。

使用 `sh experiments/tsl9-v4160-interrupt-registers/verify.sh --language both`。來源、ABI 反證、獨立測試、成功的有限探針與失敗的新原生配置均位於 `analysis/v4160-placement-2026-10-21/`，英文／繁中指南分開。目的地／checkout 驗證產生新的本機結果，不交付歷史編譯封存。Linux／macOS、原始中斷途中狀態、ROM、板子、Flash 與重建映像 OTA 仍未驗證。

## 啟動記憶體初始化

`0x186BA..0x186F8` 現在有可讀的 C/C++ 實作：分開觀察 GP、交錯向前 word 複製、無號邊界、BSS word 清零，以及正常邊界的 A0／A1／A2。確切 ID2966 來源證據涵蓋 62 bytes／17 條指令，拒絕 17 個 raw 突變；128-byte 初始化資料只當資料讀取。主機測試每語言通過五組／338 案例／133,601 項；獨立審查每語言另通過五組／538 案例／193,964 項，合計拒絕 22 個實際編譯反例。

原始區段直接接到 CSR 設定，沒有函式返回。正常 A0／A1 經原始時脈初始化後仍傳到未知 ROM 入口，不能任由一般 C helper 捨棄。另有 372 bytes／130 條指令的 reset／clock 呼叫端證據記錄此邊界；原機 ROM 身分與中斷相容性仍未證明。

原生 leaf 編譯為 78 bytes／24 條指令，超過原始 62-byte 區段，且新增了 C 編譯器產生的返回。可選的延續 fragment 為 80 bytes；來源雖寫 `c.j`，實際組譯成四 byte JAL，兩者均放不進原始範圍。在不重疊的診斷位址綁定數值延續，只能證明 relocation，並未提供原始入口 adapter。完整指令 bytes、暫存器、記憶體寬度與迴圈 CFG 檢查，也不等於原生全路徑或非同步狀態等價。未替換原始映像，也未產生 BIN。

使用 `sh experiments/tsl9-v4160-reset-memory/verify.sh --language both`。來源、呼叫端、獨立 C/C++ 及編譯器審查位於 `analysis/v4160-reset-memory-2026-10-21/`。交付選定的審查程式、文字與收據 metadata；歷史編譯封存留在工作區，目的地驗證會建立新的本機產物。Windows 結果不代表 Linux／macOS 或 POSIX shell 啟動已通過。

## 時脈正常返回暫存器契約

使用者於 2026-10-21 回報 `tsl9-morphe` 可選取官方 BIN 並成功更新韌體。這是使用者提供的官方映像 OTA 基準，確切 APK／BIN 身分與版本尚未指定；與下述重建映像的啟動、接受與恢復要求分開記錄。

時脈重建新增原始分支特定的 A3、條件式 A2 寫入、查詢 A4／A5 及衍生欄位完整 A5 乘積。新增呼叫端證據覆蓋 298 bytes／98 條指令，另檢視 130 條傳遞指令，顯示 A3 經 fresh `0x4004C` 指標傳入 `0x131E0` 的未知 callback。`1973C` 後的確切呼叫是 `9F4C`，再到 `131C2`。尚不能證明 callback 使用 A3，但也不能任意捨棄。

新 C11／C++17 主機測試每語言通過六組／293,845 項；獨立測試每語言通過四組／5,345 案例／250,316 項，合計拒絕十六個實際編譯的返回值／A2 反例。沿用未修改的 214 bytes／69 條指令及五十個 raw 負例，並另核對原始整數目的暫存器欄位。

原生編譯採用暫存器保留旗標及明確的實體暫存器限制。查詢只寫 A2–A5，A2 不供一般配置使用；本體為 196 bytes，原始為 174 bytes，仍有 22-byte 配置缺口。衍生欄位為 38 bytes，原始為 40 bytes；完整十指令模式確認 unsigned 除法、byte／halfword 寫入及正常返回 A4=1000／A5=完整乘積。這些元件證據不代表非同步中途狀態、中斷、完整映像、ROM 或實體硬體相容。未替換原始本體，也未產生 BIN。

主機驗證使用 `sh experiments/tsl9-v4160-clock-registers/verify.sh --language both`，原生 CLI 與限制記錄於 `analysis/v4160-clock-abi-2026-10-21/compiler-review/`。在先前觀察到的 CI 帳戶限制解除前，Linux／macOS 及 POSIX shell 執行仍未驗證。新文件維持分語言。

## 可讀的原生時脈與衍生欄位

兩個時脈函式新增獨立的可讀 C/C++ 實作，直接使用 volatile MMIO／RAM 與當下 GP，不依賴舊暫存器直譯模型。沿用未修改的 214 bytes／69 條指令及 50 個 raw 負例來源證據。主機測試每語言通過六組／269,618 項；獨立測試每語言通過四組／5,345 案例／214,811 項，合計拒絕十個實際編譯反例。

Freestanding C11／C++17 RV32 編譯結果各為 170-byte 查詢與 44-byte 衍生欄位函式。後者超過原始 40-byte 範圍，不能直接替換原址。獨立連結元件沒有未定義符號、執行期 helper 或可寫資料。完整核對 ELF bytes 的反組譯覆蓋範圍，檢查四／三處 GP 讀取、記憶體寬度與直接分支邊界；LLVM IR 另核對動態 GP 位移與 unsigned 運算。兩語言合計拒絕十個實際編譯的原生突變及 24 個反組譯文字反例。這是結構證據，未證明原生所有路徑語意或原始暫存器／堆疊／中斷 ABI。

來源／主機驗證使用 `sh experiments/tsl9-v4160-native-clock/verify.sh --language both`。獨立 LLVM CLI 記錄於 `analysis/v4160-native-clock-2026-10-21/native-review/readme.zh-TW.md`。未執行或模擬 RV32、未修改原始映像，也未產生新 BIN。新增指南與審查文件分英文與繁中，每個 `README.md` 只連結語言版本。

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
