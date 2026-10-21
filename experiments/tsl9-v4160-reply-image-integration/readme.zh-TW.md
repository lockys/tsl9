# OTA 回覆加入完整離線映像

[English](readme.en.md)

本管線從來源重新產生 V4.1.60 ID2966 的 76,800-byte 映像。12 個可讀 C/C++ 函式共650 bytes，包含既有 IRQ、Flash 與本輪的 `9B8E..9C0A` OTA 頁面回覆；其餘679個區段仍是保留原始內容的來源載體。這是部分可讀重建，並非完整還原原始專案。

實際 C11 與 C++17 都重新編譯34個原始載體與9個型別化來源單元。回覆函式先經獨立 ABI 排序，再與其他輸出合併並執行既有 IRQ／Flash 框架排序。兩個步驟只重排本次編譯出的指令，保留編譯前後物件及收據；沒有從舊物件、舊 BIN、指令模板或填補位元組產生新程式碼。

兩份實際輸出的 `NOT-FLASH-VALIDATED-reply-integrated.bin` 都與原版完全一致：

```text
bytes: 76800
SHA256: 0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667
differences from original / previous eleven-function image: 0 / 0
```

## 重新產生與唯讀檢查

在專案根目錄執行，`LLVM` 指向本機 LLVM NDK 工具目錄：

```sh
sh experiments/tsl9-v4160-reply-image-integration/verify.sh --tool-dir "$LLVM" --language both
```

或直接使用 Python：

```sh
python -B experiments/tsl9-v4160-reply-image-integration/verify.py --project-root . --tool-dir "$LLVM" --language both
python -B experiments/tsl9-v4160-reply-image-integration/verify.py --project-root . --replay RECEIPT
```

支援 `--firmware`、`--clang`、`--linker`、`--objcopy`、`--language c|cpp|both` 與尚不存在的專案內 `--build-root`。重讀時不允許編譯工具或輸出目錄覆寫；指定語言必須符合收據。`.sh` 使用 `PYTHON` 環境變數，否則選 `python3`／`python`。目前實測環境為 Windows NDK 27.1.12297006，其他主機平台尚未實測。

發布後的唯讀中繼資料檢查：

```sh
python -B analysis/v4160-reply-image-integration-2026-10-22/implementation/check_image.py --project-root .
```

工作區使用 `apk-analysis/tsl9-v4160-reply-image-integration-2026-10-22/`。預設只驗證封存來源與選定中繼資料，不自動重讀本機產物。`--require-local-builds` 才要求兩份選定實際封存；`--receipt FRESH_RECEIPT` 可重讀新根目錄內產生的收據。建置輸出和日誌保留於忽略的 `build/`；發布收據不表示發布了這些封存。

## 本輪證據

- 61個按順序核對的真實命令：59個LLVM編譯／查詢／連結／匯出命令與2個明確Python ABI步驟。沒有執行目標RV32。
- 43份`-MD`相依檔，實際觀察74個專案來源／標頭、14個產生的過濾來源／介面及1個Clang資源標頭。14個來源單元實際使用該資源標頭，並非宣稱所有來源都包含它。
- 保留全部691個原始配置與679個原始載體雜湊；8269筆RELA分為8257筆完整保留角色及12筆型別化JAL。53個正規相對綁定、21個外部入口及11個原始私有分支均核對。
- 原本的回覆公開符號仍為NOTYPE、大小0，原本區域入口仍為相對偏移0；新C函式是另立的FUNC124。`9DF4`實際是2-byte C.JAL，回返連結為`9DF6`。
- 15個LOAD的位元組、記憶體範圍與權限逐一核對。全部輸出位元組由實際區段及LOAD供應，沒有洞、隱藏補位、RAM或ROM位元組匯出。
- `.llvm_addrsig`被明確核對為原56-byte排除型中繼資料加上新原生函式的1-byte符號索引；最終ELF不保留它。沒有把額外非配置中繼資料一概忽略。
- 每種語言41個實際檔案／收據反例：30個ELF／RELA／映像、4個相依檔、6個排序收據與1個命令順序。另有5個唯讀CLI案例。

缺少駐留ROM提供者的嚴格連結必須失敗。成功ELF僅把該入口設為數值`0x40000`，沒有提供ROM內容。此輪完整映像包含原始保留的TX函式，不使用前輪獨立元件的數值TX替身。

原始映像一致性不證明未知駐留ABI、任意callee破壞SP／暫存器、非同步或fault行為、計算出的內部入口、實體板子、BLE／Flash／OTA相容性。全程沒有RV32執行、ISA模擬、網路、封包或裝置操作。
