# TX 完整映像的獨立 ABI 與產物審查

[English](readme.en.md) · [简体中文](readme.zh-CN.md)

本審查驗證真實新產物的靜態整合契約。TX 使用窄組語入口 8B、可讀 C/C++ 主體 270B、真正 C 返回葉節點 2B；原有公開入口如實改為 FUNC8，沒有虛構 FUNC280 或 ABS 程式提供者。這不等於原硬體 ABI、ROM 行為、非同步行為或藍牙燒錄已獲證實。

`baseline.json` 是前一版實際完整 12 功能映像的驗證用角色、配置與雜湊資料。`prepare-baseline.py` 僅供重新稽核歷史來源；一般檢查不需要歷史 `.o` 或 ELF。原 BIN 只供驗證，不輸入程式產生流程。

本次獨立檢查包含：

- 691 個配置區域與全部 LOAD 的實際位址、檔案／記憶體長度、權限、完整 76,800B 匯出覆蓋。
- TX 外 690 個區域的 partial／linked 位元組與角色保留，TX 外 76,520B 仍與原映像相同。新 TX 的 93 個差異位元組全部位於其 280B 區間；不要求整張 BIN 的原雜湊。
- 三個實際新提供者串接、原獨立元件已審查之機器碼、真正配置的 RAM PCREL 提供者與 HI／LO 錨點；不從舊元件複製產生任何位元組。
- 8,258 筆非 TX 重定位完整比對，僅對九個原有 TX 入口參照明示 FUNC280→FUNC8 的大小角色變更。總重定位 8,261＝選定 13 區域外 8,246＋其內 15。
- 30 個已記錄邊界參照的實際指令寬度、目標、rd、連結與返回位址：29 個來自選定區域外，另 1 個是已重建 page-reply 的 9BE0 呼叫。這不是全映像所有呼叫的列舉；其他選定區域內呼叫由完整非 TX 重定位及位元組保留覆蓋。13EAC 的 JAL x0 必須維持不寫 RA。
- 原有 IRQ／quarter、page-reply 排序，以及新 TX 排序的實際編譯前後產物、原有指令字、元資料與收據關聯。三層排序分別改變 14／28／50 個檔案位元組，明示不是編譯器單獨產生最終順序。
- 九個直接破壞實際 ELF／BIN 的反例，涵蓋虛構 FUNC280、ABS 替身、PCREL 錨點與目標、address-significance 資料、呼叫連結、TX 指令、LOAD 與匯出位元組。

`selected-c.json`、`selected-cpp.json` 是封存的實際審查紀錄；`summary.json` 綁定所選產物與工具版本。本套件不附編譯產物。

## 指令與證據層級

預設只查封存來源與中繼資料；不讀原 BIN，也不重播任何實際建置：

```sh
python -B ABI-review/check.py --project-root ROOT
```

實際審查必須提供新建置目錄、原韌體與新收據位置。`MODE` 應含 producer 完整產物，包括三個新 TX `.o`、各層排序前後 `.o`／JSON、完整 ELF 與匯出 BIN：

```sh
python -B ABI-review/review.py --project-root ROOT --firmware FW --folder MODE --receipt NEW.json
python -B ABI-review/review.py --project-root ROOT --firmware FW --replay NEW.json
```

第二行唯讀重新執行實際檢查並要求紀錄完全一致。`review.sh` 無參數走中繼資料檢查，其餘參數傳給實際檢查器；可用 `PYTHON` 指定直譯器。

實際模式回傳 `actual_build_artifact_replay=true` 與 `static_full_image_contract_passed=true`。預設模式明示兩者沒有在本次執行，避免把中繼資料通過當成完整建置重播。編譯來源、46 TU／45 MD／67 recipes 的完整鏈由相鄰獨立 source-review 另外審查。

## 保留的限制

所檢查之迴圈 CFG、入口、frame 邊界與已記錄角色具備靜態證據；其前提包含對應的活躍 GPR／記憶體回覆、來源指令角色、沒有任意 code-as-data 依賴。未證實未知 ROM 的實作與任意 clobber、未知計算跳入、所有故障／中斷／非同步前綴、實體晶片相容性、BOOT 接受條件、完整 OTA 封裝或實機功能。所有 `original_full_ABI_admitted` 與 `hardware_OTA_proved` 仍為 false。
