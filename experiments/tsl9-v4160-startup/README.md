# 最新整合：條件回呼與新版 Runtime reset

執行 `python verify-gatt-ingress-extension.py --spec evidence/residual-callbacks-integration.json`，詳見 [RESIDUAL-CALLBACKS.md](RESIDUAL-CALLBACKS.md)。新增85C8／8B90原始318B／2配置／24 RELA，規格要求整合70764B code、3708B RO、640配置、8107 RELA；原31真UND、539 symbolic relative32、7個原VA固定表項保留。可讀C/C++ reset模型在 `../tsl9-v4160-reset-contract/`。兩個回呼入口由原記錄條件接納，resident ABI與實體執行仍未知；沒有可燒錄重建BIN。以下保留先前記錄。

---

# 前一階段：GATT 接收與完整原路由片段

執行 `python verify-gatt-ingress-extension.py --spec evidence/gatt-ingress-integration.json`，詳見 [GATT-INGRESS.md](GATT-INGRESS.md)。新增原7224B code＋32B RO／18配置／775RELA；整合70446B code、3708B RO、638配置、8083RELA。31個真UND保留。新增5項正式relative32，另7項沿用舊資料的原VA固定表，不宣稱任意重定位。新驗證入口保留原gate並精確分區新增記錄；原frozen CLI的實際失敗亦保留。可讀C/C++接收模型在 `../tsl9-v4160-gatt-ingress-model/`。原resident ABI、硬體、IRQ與OTA接受尚未證明，沒有可燒錄重建BIN。以下保留先前記錄。

---

# 最新整合：OTA 命令本體與必要相依

執行 `python verify-data-anchor-extension.py --spec evidence/ota-handler-integration.json`，詳見 [OTA-HANDLER.md](OTA-HANDLER.md)。新增原始 900B code／6 片段／70 RELA／7 個 private NOTYPE0，另以有原指令邊界證據的 code view 沿用 13B4C 舊 storage。整合 63,222B code、3,676B RO、620 個配置、7,308 RELA；原 31 UND 保留。新版 W 全頁回覆與 strict E/R guards 已納入研究，可讀 C/C++ 契約另在 `../tsl9-v4160-ota-contract-model/`。硬體、ROM 與 OTA 接受仍未證明，沒有可燒錄重建 BIN。以下保留先前記錄。

---

# 最新整合：條件式執行層與 Flash 鏈

執行 `python verify-data-anchor-extension.py --spec evidence/conditional-runtime-integration.json`，詳見 [CONDITIONAL-RUNTIME.md](CONDITIONAL-RUNTIME.md)。本輪新增原始 6,318B／14 片段，C/C++ 承載原 RV32 指令；31 個新標籤全為 NOTYPE0，不猜原 C 函式 ABI。整合 62,322B code、3,676B RO、614 個配置、7,238 RELA；原 23 UND 全保留，另有 8 個未知資料地址義務，strict 仍拒絕 31 UND。Flash 的 256-byte 複製鏈已有靜態證據，實際 OTA 路徑與硬體相容性未證明，沒有可燒錄重建 BIN。以下保留先前各階段記錄。

---

# 最新整合：保留opaque canonical的條件式分派器

執行 `python verify-data-anchor-extension.py --spec evidence/conditional-dispatcher-integration.json`，詳見 [CONDITIONAL-DISPATCHER.md](CONDITIONAL-DISPATCHER.md)。新增901A..907A原始96B／38指令及7項RELA，保存已知35個callback的registry-consumer片段；唯一新label是獨立NOTYPE0 byte-storage identity，不提供C函式signature。原901A canonical及全部23個UND保留，不因同VA已有指令就假閉ROMentry／ABI。整合56004B code、3676B RO、600個非空配置、6679RELA；C11／C++17一致，原engine/specs／程式／資料保留，仍沒有可燒錄重建BIN。

---

## 前一階段：兩處首次讀取域與432B唯讀聯集

執行 `python verify-data-anchor-extension.py --spec evidence/data-contracts-integration.json`，詳見 [DATA-CONTRACTS.md](DATA-CONTRACTS.md)。新增原始432B RO，19ED8／1A018保留NOTYPE0並共用真carrier，後者offset320；1A078雖有前16B被捕獲，完整讀域仍缺1144B，繼續UND。整合55908B code、3676B RO、599個非空配置、6672RELA；C11／C++17一致，strict仍拒絕23個真UND。既有程式、資料、2codeviews及1data-anchor保留；原機resident／硬體／IRQ／OTA尚未證明，沒有可燒錄重建BIN。

---

## 前一階段：35個條件回呼與必要本體

執行 `python verify-data-anchor-extension.py --spec evidence/materialized-callbacks-integration.json`，詳見 [MATERIALIZED-CALLBACKS.md](MATERIALIZED-CALLBACKS.md)。新增35個有消費證據的條件callable及8個必要直接入口，共2658B code／44片段；另依首次未遮罩u8讀域新增229B RO、沿用舊45B組成274B聯集。原NOTYPE0身份、既有程式與資料保留。整合55908B code、3244B RO、598個非空配置、6672RELA；C11／C++17一致，strict仍拒絕25個真UND。舊入口未改，新增入邊／讀域由本輪獨立合併audit補證；硬體／ROM／IRQ／OTA尚未證明，沒有可燒錄重建BIN。

---

## 前一階段：已觀察讀域與獨立資料錨點

執行 `python verify-data-anchor-extension.py --spec evidence/data-anchor-integration.json`，詳見 [DATA-ANCHOR.md](DATA-ANCHOR.md)。本輪只增加1AB59的7B RO；原1AB58以真舊RO carrier末端的GLOBAL NOTYPE0／size0錨點解析，模型沒有替byte0配置section。整合53250B code、3015B RO、550個非空配置、6302RELA；C11／C++17一致，strict仍拒絕60個真UND。新入口完整fresh重播前階段，舊generic／spec保留；bounded讀域不證原C物件或任意動態路徑，硬體與OTA尚未證明，沒有可燒錄重建BIN。

---

## 前一階段：兩個有條件回呼的真實本體

執行 `python verify-table-extension.py --spec evidence/callback-bodies-integration.json`，詳見[CALLBACK-BODIES.md](CALLBACK-BODIES.md)。新增F4D0／F578共352B，原地址保持NOTYPE0、body helpers分名；整合53250B code、3008B RO、549個非空配置、6302RELA。C11／C++17一致，strict仍拒絕61個真UND＝ROM1 direct＋60materialized-only。四條已知路徑的條件回呼不代表所有動態輸入／ABI已閉合；硬體與OTA尚未證明，沒有可燒錄重建BIN。新spec須明示，generic與舊spec保留原階段。

---

## 前一階段：剩餘兩個直接入口的真實本體

執行 `python verify-table-extension.py --spec evidence/residual-code-integration.json`，詳見[RESIDUAL-CODE.md](RESIDUAL-CODE.md)。新增9AE4／F666共24B、兩個真FUNC及兩筆RAM own-HI／LOW_S引用；整合52898B code、3008B RO、547個非空配置、6258RELA。C11／C++17一致；目前captured code的具名直接UND只剩ROM入口，另有62個materialized-only UND與未知runtime／IRQ／資料契約，strict仍拒絕，沒有可燒錄重建BIN。新spec須明示，generic與舊spec保留原階段。

---

## 前一階段：84個直接入口、必要尾段與六項有限分派

執行 `python verify-table-extension.py --spec evidence/direct-frontier-integration.json`，詳見[DIRECT-FRONTIER.md](DIRECT-FRONTIER.md)。新增3312B code、320B RO，保留原13D48的140B／17RELA；整合52874B code、3008B RO、545個非空配置、6256RELA。C11／C++17產物一致，strict仍拒絕65個真UND（兩個非ROM直接入口、62個取址用途及ROM1）。來源讀取範圍的條件證明不等於實體RAM／ABI驗收；硬體與OTA尚未證明，沒有可燒錄重建BIN。新spec須明示，generic預設與舊spec各保留原階段。

---

## 前一階段：後續直接入口、253項有限分派與原地址身份

執行 `python verify-table-extension.py --spec evidence/direct-followup-integration.json`，詳見[DIRECT-FOLLOWUP.md](DIRECT-FOLLOWUP.md)。本輪新增7212B code、1068B RO，沿用原AD48的112B及26筆RELA；共49562B code、2688B RO、453個非空配置、5765筆semantic RELA。C11／C++17產物一致；strict仍拒絕145個真UND，硬體／ROM／IRQ／OTA尚未證明，沒有可燒錄重建BIN。新spec須明示；generic預設及舊spec保留各原階段。

---

## 前一階段：66個直接入口、必要分派與有限常數讀取

執行 `python verify-table-extension.py --spec evidence/direct-successors-integration.json`，詳見[DIRECT-SUCCESSORS.md](DIRECT-SUCCESSORS.md)。本輪新增8204B code、817B RO，含66個captured entry helpers、五表189項及四literal讀取視窗；共42350B code、1620B RO與4636筆semantic relocations。C11／C++17實際產物一致，strict仍拒絕116個UND（含兩個mixed用途），原機／ROM／IRQ及OTA尚未閉合，沒有可燒錄重建BIN。新spec須明示，verifier預設與舊spec保留各原階段。

---

## 前一階段：後續直接入口與四張有限分派表

執行 `python verify-table-extension.py --spec evidence/post-table-code-integration.json`，詳見[POST-TABLE-CODE.md](POST-TABLE-CODE.md)。本輪新增13446B code及256B有限讀取視窗，含70個captured entry helpers、四張表的64項與978B必要case；共34146B code、803B RO、3174筆semantic relocations。C11／C++17實際產物一致，strict仍拒絕116個真UND；原機／ROM／IRQ及OTA尚未閉合，沒有可燒錄重建BIN。新spec須明示，verifier預設及舊spec各保留原階段。

---

## 前一階段：三張相對表與可達分支

執行 `python verify-table-extension.py --spec evidence/table-cases-integration.json`，詳見[TABLE-CASES.md](TABLE-CASES.md)。本輪新增1968B code及88B已證讀取視窗，22個表項用同址ADD32／SUB32表示；共20700B code、547B RO及1559筆semantic relocations。分支揭露69個新code義務，strict仍拒絕92UND；原機／ROM／IRQ與OTA尚未閉合，沒有可燒錄BIN。原generic及舊spec維持各階段入口。

---

## 前一階段：剩餘直接入口與191C6本體

執行 `python verify-extension.py --spec evidence/direct-closure-integration.json`，詳見[DIRECT-CLOSURE.md](DIRECT-CLOSURE.md)。本輪新增37個本體／2360B，保留原address191c6為NOTYPE0 view；整合18732B code、459B RO及1293筆semantic relocations。24個真UND中只有ROM尚有直接控制引用，其餘23個目前只有取址用途；間接目標、資料與原機／OTA契約仍未閉合，尚無可燒錄BIN。

---

## 前一階段：47個直接用途入口與原地址身份

執行 `python verify-extension.py --spec evidence/code-continuation-integration.json`，詳見[CODE-CONTINUATION.md](CODE-CONTINUATION.md)。本輪新增4372B／47個物理片段、47個FUNC及3個保留原型別的NOTYPE view；整合16372B code、459B RO與1191筆semantic relocations。61個真實UND、未知間接目標及硬體／ROM／OTA條件仍未閉合，尚無可燒錄BIN。1AAE8 index已有正常reset清零與已知writer寫0..6證據，但全生命週期不變量仍未證明。

---

## 前一階段：71個直接入口與可達片段

執行 `python verify-extension.py --spec evidence/direct-expansion-integration.json`，詳見[DIRECT-EXPANSION.md](DIRECT-EXPANSION.md)。本輪新增4932B／73個物理片段，涵蓋前一階段71個直接入口；8520的62B另有有限計算分派證明，另外兩個hole仍不配置。整合12000B code、459B RO及898筆semantic relocations；69個真實UND與其他未閉合的硬體／ROM／OTA條件仍阻止產生可燒錄BIN。

---

## 前一階段：十個直接呼叫本體

執行 `python verify-extension.py --spec evidence/frontier-integration.json`，詳見[FRONTIER.md](FRONTIER.md)。本輪新增十個本體／762B，保留先前materialized配置；整合7068B code、459B RO與587筆semantic relocations。83個真實UND、83個間接callsite與1個間接tail仍未完全閉合，沒有可燒錄成品。

---

## 前一階段：取址引用與回呼本體

執行 `python verify-extension.py --spec evidence/materialized-integration.json`，詳見[MATERIALIZED.md](MATERIALIZED.md)。本輪新增七個本地程式capture（1812B）及3B已證local-read範圍；整合6306B code、459B RO、554筆semantic relocations。五個原opaque程式名稱保留NOTYPE0 view，不宣稱原C型別／ABI；84個UND與79處間接callsite仍未閉合，沒有可燒錄成品。

---

## 前一階段：初始化第一層與持續執行流程

該階段執行 `python verify-extension.py`，詳見[CORE-FLOW.md](CORE-FLOW.md)。它加入19個本地本體／2788B，含初始化呼叫鏈、全部第一層callee及主迴圈；整合4494B code、456B RO、437筆重定位。該scope嚴格link仍拒絕79個不同角色的UND，另有48個間接callsite的target／ABI待確認；沒有可燒錄BIN。

---

## 前一階段：main 與七個直接呼叫入口

該階段入口是 `python verify-dependencies.py`，詳見[DEPENDENCIES.md](DEPENDENCIES.md)。它加入18B main及366B真實callee bodies，合計1706B code、456B RO、223筆relocation；該scope三個明示UND為8180、9250及ROM40000，動態回呼與硬體／OTA契約另保持未知。下方原有vector／clock／reset說明各自屬先前獨立驗證階段。

---

## 先前階段：vector／IRQ／clock

此階段入口為 `python verify-vector-platform.py`：reset、真clock、有限vector capture與IRQ本體，共1322B code／456B RO／211重定位；該階段九個真實callee依賴仍使嚴格link失敗。C11與C++17靜態核對通過，**尚無可燒錄BIN**。[該階段範圍與三個驗證入口](PLATFORM.md)。

---

以下保留初始reset-only階段的範圍說明；其`verify.py`仍只驗證該元件，四UND不當作最新整合結果。`verify-platform.py`則是clock-only三UND階段。

## 初始reset-only C/C++ 元件

從固定來源 SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667` 的真實 BIN，重建138B reset入口、128B初始化資料與35160B NOBITS RAM carrier。程式為 C11／C++17 加 RV32 inline assembly；Python只負責離線取證與ELF核對。這是新版獨立元件，不替換原R81／V4.1.00工程，不是可燒錄韌體。完整產品選項文字未保留，ID2966對使用者這顆硬體的適用性仍未證實，不能只憑V4.1.60標籤認定。

## 已從原始指令確認的地址模型

| 項目 | ID2966／V4.1.60 | 舊ID2581／V4.1.00 |
|---|---|---|
| reset 模型位址 | 0x186AA | 0x183FE |
| GP地址 | 0x20004000 | 0x20004000 |
| 初始化來源／長度 | 0x1AB60／128B | 136B |
| data／BSS分界 | 0x20004080 | 0x20004088 |
| BSS清零終點 | 0x2000C958 | 0x2000C950 |
| 數值RAM carrier範圍長度 | 35160B | 35152B |
| BSS清零長度 | 35032B | 35016B |
| 初始SP地址期望 | 0x20010000 | 0x20010000 |

`evidence/startup-evidence.json`記錄22份映像的來源hash與獨立地址運算。基址由offset0x40的vector值減去已核mret stub的file offset導出，再與offset0x38核對；沒有以r2的-m選項證明載入位址。以上不是實體RAM容量、stack有效性或MCU型號證明，也不能從共用GP/SP推論兩版可混用。

## 原生表示與驗證

`src/startup.c`保留原138B指令ABI，加入14筆語意重定位（6組own-anchor PC-relative pair及2筆JAL）。128B初始化來源只配置一次；RAM是一個NOBITS物件。SP是size0的ABS位址常數，沒有配置stack。初始化資料目前保留原始bytes，其中raw指標的型別、被指物件與後續使用尚未全部整理，不能以此宣稱完整依賴閉合或可任意重定位。

執行 `python verify.py`；預設使用`../../firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，也可給`--firmware <絕對路徑>`。使用本機已存在的Windows Python及Android NDK27.1.12297006 clang／lld，沒有安裝或網路操作。

驗證C11、C++17的RV32物件逐byte相同，核對138B原指令／128B原資料、NOBITS extent、size0 SP與14筆重定位。嚴格最終link必須失敗，且不留下ELF。輸出的唯一正常native產物是relocatable object；沒有BIN。

另有明標`ADDRESS-WITNESS-ONLY.elf`的**數值位址驗證夾具**：`layout/address-witness.ld`只把四個已解出的數字填入linker symbol，讓靜態工具比較原指令重定位後是否逐byte相同。四個數字沒有對應實作，未供應向量表／clock／main／ROM程式，也不代表實體位置可呼叫。此ELF只供byte核對，不能當候選韌體、不可執行或燒錄。

## 尚缺條件

reset的四個明示外部依賴保持UND：vector_base（0x8038）、clock_init（0x1874A）、main（0x9008）、ROM入口（0x40000）。這是此元件的外部引用清單，不是完整韌體缺口總數。還需整理initializer中的指標物件、其他函式、ISR、BOOT/root、ROM版本／ABI、實體晶片／PCB／RAM／stack、最終配置及OTA相容性。沒有執行／模擬任何原始或重建RV32程式，也沒有操作硬體。

