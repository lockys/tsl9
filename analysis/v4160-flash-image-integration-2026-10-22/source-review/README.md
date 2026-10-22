# IRQ 與 Flash 整體映像的獨立靜態審查

[English](readme.en.md)

本輪實際讀取最終 C11、C++17 的 `.o`、ELF、BIN 與編譯紀錄，確認 11 個可讀 C 函式共 526 bytes 已整合到原有映像配置。其餘 680 個配置仍保留原始資料或指令載體。這是部分原始碼重建的混合映像，尚未證明能在硬體啟動或透過 OTA 更新。

兩種語言的實際 76,800-byte BIN 都是 `de159bb345b27250a683e197dd84b04e51a7a7ed89315347395baaea53f68be1`，與原始 ID2966 有 70 bytes 不同，與前一個僅整合 IRQ 的映像有 62 bytes 不同。審查沒有執行原始或重建的 RISC-V 指令、模擬器、硬體或網路操作。

## 證據與通過範圍

`source-constraints.json` 由本機實際原始 8280-RELA 載體、前輪 8276-RELA 載體，以及已封存的 IRQ／Flash 原生元件獨立推導；其 SHA-256 是 `d29445adccff76de983d85bf0384c3fd5d9f5af5805387bebaf200dc495cd180`。這份小型基準保留角色與雜湊，供發佈目錄沒有舊建置物件時驗證新成品。可攜模式不會宣稱重新讀過那些舊建置檔。

| 實際檢查 | 結果與限制 |
| --- | --- |
| 配置 | 全部 691 個原配置的名稱、大小、型態、旗標、對齊及最終位址一致；680 個保留配置的部分連結原始內容逐一核對雜湊。 |
| 原始碼替換 | 獨立以引號組語區段範圍過濾四個 TU，只移除指定 11 個函式；實際 34 個原始載體物件均未留下這 11 個 raw fallback。 |
| 來源與依賴 | 實際 42 個 TU、56 個編譯／IR／連結／匯出命令、42 個 `.d` 規則、72 個既有專案檔與 12 個產生檔。每條規則核對自己的目標物件、主來源與注入 adapter。`-MMD` 不包含編譯器系統標頭。 |
| 重定位 | 8259 筆外部範圍角色、位移、型態、有號 addend 與重複次數完整保留；新函式實際只有 11 筆 JAL，總數 8270。 |
| 呼叫與符號 | 20 筆外部參照仍指向函式入口；53 個原有相對區段綁定保留；原入口別名及新 C 名稱皆為真實區段所屬 FUNC，沒有用 ABS 假入口代替。 |
| 最終載入 | 691 個已連結配置與 15 個實際 PT_LOAD 的資料、記憶體範圍及每 byte 權限相符；其中 RAM 為 `0x20004000`、35160 bytes、NOBITS。ELF 配置資料、LOAD 資料、BIN 與獨立元件覆蓋推導結果完全一致。 |
| 編譯證據 | 兩種語言各實際讀回 194 個編譯成品／紀錄／依賴檔，並額外重播製作者的 23 個 ELF／RELA／映像負向控制及 3 個依賴控制。這些均為靜態檔案驗證。 |

原始 8280 筆重定位中的 21 筆屬於被替換函式：6 IRQ JAL、4 IRQ 分支、5 Flash JAL、6 Flash 分支。前輪 IRQ 載體已將 4 個 IRQ 分支化為元件內部控制流，因此是 8276 筆，所屬舊紀錄剩 17 筆。本輪實際新載體是 `8259 + 11 = 8270`。這三個基準不能混用。六個 Flash 私有分支名稱僅依確切角色解除；沒有用名稱萬用規則把未知內部參照當成可刪除資料。

部分連結 `.o` 的重定位資料尚未套用，不能直接要求所有 raw bytes 等於最後 BIN。審查分別核對保留區段的部分連結雜湊、已連結的原生函式 bytes，以及實際 ELF／LOAD／BIN。完整命名符號角色也與獨立推導的基準一致。

## 獨立負向控制

`independent-controls.json` 記錄 15 個實際 ELF／RELA／BIN 檔案變更及 2 個實際 `.d` 文字變更，全部被獨立檢查器拒絕。案例包括漏掉配置、以原始程式碼取代新 C 函式、外部 RELA addend 改變、筆數相同的重複重定位、ABS／NOTYPE 假入口、入口參照移入函式內部、相對綁定位移、100-byte 區段縮成 94 bytes、LOAD 實體位址／記憶體大小／權限錯誤，以及 BIN 外部 byte 改變與截斷。它們不是目標韌體執行測試。

原始控制檔只保留於本機 `build/independent-controls`，不隨這個小型審查封存發佈。封存的控制結果是歷史執行紀錄；預設檢查不會把它說成重新執行。`control-artifacts.py` 可在新的目錄重建及重驗這一組有界控制。

## 使用方式

預設只驗證封存成員、當前專案來源及獨立基準，不需要舊建置封存：

```sh
python3 -B source-review/check-review.py --project-root /path/to/project --firmware /path/to/ID-2966-V4.1.60-decoded.bin
```

對新建置的實際成品進行獨立 ELF／LOAD／BIN 檢查及編譯來源讀回：

```sh
python3 -B source-review/check-review.py --project-root /path/to/project --firmware /path/to/original.bin --receipt /path/to/new-build/c/verification.json
```

若只有三個成品，可改用 `--new-object source-integrated.o --new-elf ADDRESS-WITNESS-ONLY.elf --new-bin NOT-FLASH-VALIDATED-irq-and-flash.bin`；此模式不聲稱有編譯命令與依賴紀錄。只有完整實際建置封存及當時工具均在本機時，才加上 `--producer-replay` 重播製作者的額外靜態控制。`check-review.sh` 使用 `PYTHON` 或 `python3`，Windows 可直接使用 Python。

`inspect-image.py` 是可選的原始封存重讀入口，另需 `--original-object`、`--prior-object`、`--IRQ-elf`、`--Flash-elf`。這項較完整的舊封存讀回已在工作目錄做過；可攜檢查仍明確輸出 `original_baseline_archives_replayed: false`。

## 尚未證明

嚴格連結確實因缺少 `__tsl9v4160_rom_entry` 而失敗；數值見證腳本只把它指向 `0x40000`，沒有提供 ROM 內容或實作。現有測試不證明 ROM 合約、完整韌體功能、非返回時的實體暫存器前綴、逐指令／非同步等價、已安裝 BOOT 身分、硬體相容性或 OTA 接受條件。這些欄位維持 false／unknown，沒有新增功能已實作的宣稱。

`review.json` 與兩個 `selected-*-verification.json` 綁定本輪最終來源與實際收據；`final-C-review.json`、`final-CPP-review.json` 是獨立讀回結果。收據保留原工作目錄的歷史路徑，移到其他電腦不代表原建置封存也已存在；應以新建置的實際 `--receipt` 或三個新成品驗證。
