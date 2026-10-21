# IRQ 與 Flash 全映像：獨立 ABI／連結審查

實際 C11 與 C++17 全映像均通過本審查的靜態檢查；每種語言另有 **20 個實際產物位元組反例**，全部被拒絕。完整映像為 76,800 位元組，SHA-256 為 `de159bb345b27250a683e197dd84b04e51a7a7ed89315347395baaea53f68be1`。這證明本文件限定的儲存、角色與正常返回邊界；硬體、ROM、OTA、非返回與非同步等價仍未證實。[English](readme.en.md)

## 審查結果

- 691 個配置區段保留原位址、大小、種類、旗標及對齊；其中 680 個非替換區段的實際合併與連結內容完全一致。
- 11 個可讀 C 函式共 526 位元組：IRQ 主函式 144、四個 RCC 輔助函式各 30；Flash 六函式為 64／8／30／14／46／100。實際連結內容逐位元組等於先前封存且通過正常暫存器合約的元件。
- 原有 8,259 個外部 RELA 的完整語義摘要不變；新物件共 8,270 個 RELA，其中 11 個為明確 JAL。其目的函式、`rd=1` 與 RA 返回邊界均由實際機器碼核對。
- 保留 53 個區段相對綁定，以及所有原有 global／weak／非中繼資料 local／SECTION 角色。Flash 六個私有迴圈標籤僅在原物件各有一個同區段分支引用，改由實際連結分支核對後消除；沒有建立僅數值相同的假別名。
- 20 個已知外部進入點的實際呼叫寬度、目的與 RA 合約不變。`9D00`、`9E7A` 是 2 位元組 C.JAL；`18906` 是 `JAL x0` 尾跳，不能視為產生新 RA 的一般呼叫。
- 中繼資料例外嚴格限定：六個 `$d`→`$x`，各新增六個未引用 comment／ABS attributes／FILE 記錄，最終連結移除 42 個未引用 comment 映射。沒有放寬非中繼資料角色。
- 690 個有檔案內容的配置完整覆蓋 76,800 位元組，無洞、重疊、補洞或額外配置。新映像與原版差 70 個位元組，與先前 IRQ 映像差 62 個，全部位於 11 個已選取函式內。
- 15 個實際 LOAD segment 完整且各一次涵蓋 691 個配置；記憶體長度、檔案長度、實體／虛擬位址與權限分別核對，並拒絕未擁有的記憶體尾端或可寫程式碼。

`receipts/c.json`、`receipts/cpp.json` 綁定正式 `formal-final` 產物與生產端回條；`report.json` 彙整選定雜湊。生產端的來源、42 個編譯單元、相依檔及工具命令追溯，另由生產端與來源審查證據負責；本審查不將讀取回條等同重新編譯。

## 可攜重驗

在專案根目錄執行，下列指令只讀取產物、解析 ELF 與解碼指令，不執行目標程式：

```sh
python3 -B apk-analysis/tsl9-v4160-flash-image-integration-2026-10-22/ABI-review/check_seal.py --project-root .
```

審查同一來源新建的 C 或 C++ 產物目錄：

```sh
python3 -B apk-analysis/tsl9-v4160-flash-image-integration-2026-10-22/ABI-review/review.py --project-root . --folder PATH_TO_MODE_DIR --receipt review-result.json
python3 -B apk-analysis/tsl9-v4160-flash-image-integration-2026-10-22/ABI-review/review.py --project-root . --replay review-result.json
```

目錄須含 `source-integrated.o`、`ADDRESS-WITNESS-ONLY.elf`、`NOT-FLASH-VALIDATED-irq-and-flash.bin`；若有 `verification.json`，會另外綁定其雜湊與語言模式。也可透過 `sh .../review.sh` 使用相同參數；Windows 可用 `python -X utf8 -B`。Shell 包裝器只有靜態檢查，未在本輪執行 Linux／WSL／Git Bash。

`source-baseline.json` 是由實際舊物件、原始配置清單與已封存元件推導的事實摘要；檢查器固定其雜湊。它保存配置／角色摘要、20 個原呼叫、11 個元件與先前 IRQ 的八位元組差異，**不需要 W 路徑的舊物件或 ELF**。重驗仍需要原始韌體及專案內固定雜湊的來源證據／解碼器。`--firmware`、`--parser` 可明確指定同雜湊的替代路徑。一般可攜重驗不重新產生舊來源基線；回條將此項標為 `archived_source_replay=false`。

## 合約的限制

正常返回證據沿用逐指令元件合約，要求存取完成、輪詢終止、有效堆疊與未建模非同步干擾不存在。IRQ 與 Flash 的暫存器殘值、動態 frame reload、32 位元組 Flash wrapper／`SP+12` source slot、64 個 word transfer 與 CSR 邊界皆受元件機器碼身分約束。

Flash program 的原始 `+8` 指令邊界仍未保留，新版新增 `+10`；五個已知迴圈角色相同不代表所有內部進入點等價。早期 CTLR scratch 原用 A5、新版用 A2；wrapper／IRQ 的保存順序亦有差異。因此本審查不宣稱完整 GPR 故障／非返回前綴、逐點中斷或非同步行為等價，亦未排除未知計算式間接進入點。`__tsl9v4160_rom_entry=0x40000` 僅為數值連結見證，沒有 ROM 實作證明。

本輪沒有目標 ISA 執行／模擬、裝置操作、網路請求或燒錄。檔名 `NOT-FLASH-VALIDATED` 的限制仍然適用；這不是硬體成功、復原能力、晶片型號、Flash 容量或 OTA 相容性證明。
