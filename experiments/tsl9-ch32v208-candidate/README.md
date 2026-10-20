# TSL9 CH32V208／D8W 候選 Runtime BIN

這是依目前最強硬體候選產出的離線實驗映像，**尚未證明可燒入原機或由原藍牙 OTA 接受**。沒有執行目標、模擬器或硬體通訊；沒有網路/API 操作。原始重建目標仍未完成。

## 產物與驗證範圍

交付 BIN 為 76,800 bytes，對應模型 Flash `[0x8000,0x1AC00)`；入口 `0x8000` 跳至 reset `0x183FE`。僅 Runtime，不含 BOOT、ROOT 或 resident ROM。不是完整 MCU Flash dump，也不是帶 OTA 封裝／簽章的新升級包。

SHA256：`32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc`。

C 與 C++ 路徑分別使用已封存且本輪逐檔核對來源／工具／收據雜湊的 R81 compiled core，重新編譯 carrier、嚴格 final-link、objcopy。未重編未變動的舊 core。ELF、map、實際命令、原生工具 exit code、輸入／輸出 hash、audit 均保留在 `experiments/tsl9-ch32v208-candidate/build/{c,cpp}/<build-id>/`。交付 manifest 指向實際兩份建置收據。

實際 linked Flash 每個 section、每個原始位址，以及最終 BIN 都與留存 Runtime 完全相同。這是**原指令忠實重建**：C/C++ 原始檔仍大量使用內嵌組語；不表示高層語意已完整恢復，也未新增功能。不是把下載檔改名：BIN 由真實 ELF 經 objcopy 產生，鏈中記錄編譯輸入與重定位結果。

| 來源 | 區段 | Bytes | 說明 |
|---|---:|---:|---|
| 已有 C/C++ core 的 code | 638 | 71762 | 仍含內嵌組語，不等同高層 C/C++ 恢復率 |
| 已有 C/C++ core 的 RO | 29 | 4685 | 含既有 136B 初始化資料，配置一次 |
| 原始載體 carrier | 25 | 353 | 逐範圍來源、offset、hash；語意未重建，不統稱 padding |
| RAM NOBITS／NOLOAD | 1 | 35152 | `[0x20004000,0x2000C950)`，不進 BIN |

ELF 為 RV32 RISC-V ET_EXEC，零剩餘 UND、零未套用 REL/RELA，只有 Flash／RAM 兩個 LOAD；另有不載入 Runtime 的標準 RISC-V ABI attributes 中繼資料。位址與大小逐區段固定，無隱式補零／FF，無來源外的 bytes。

## 明示候選假設與缺口

- `__tsl9_rom_entry=0x40000`、`__tsl9_opaque_address_19d10=0x19D10`：只在此新 profile 綁定為 ABS／NOTYPE／size0 地址，沒有新增函式、假 ROM 或表格內容。舊 R81 嚴格 two-UND 失敗與所有封存保持原樣。
- `0x19D10` 的完整 raw-U8 lookup domain 尚缺 272 bytes 來源；沒有補造 `[0x1AC00,0x1AD10)`，也未證明所有實際輸入不會讀到缺失範圍。
- CH32V208／D8W 僅為候選；實機 MCU、PCB、晶振、ROM 版本與 ABI、回呼／低 RAM、IRQ／stack 所有權、BOOT／ROOT 配合及 OTA 接受條件均未完成實證。
- 留存 Runtime 的來源版本關聯為 V4.1.00；不是截圖中的 V4.1.60 原機 dump，不能宣稱是最新版韌體。
- `target_ready=false`、`ota_verified=false`、`goal_complete=false`。目前不要將此檔作為已驗證的原機升級包。

## 在此機重新建置

在 PowerShell 7 執行下列指令，`RuntimePath` 必須指向同 SHA256 的原始 Runtime。腳本依收據使用本機固定的 LLVM／Python，不下載依賴；每次輸出全新 GUID 目錄，不覆蓋舊建置。

```powershell
pwsh -NoProfile -File C:/Users/locky/Documents/projects/re-tsl9/experiments/tsl9-ch32v208-candidate/build.ps1 -Mode cpp -RuntimePath C:/Users/locky/Documents/Codex/2026-10-13/rea-https-github-com-morluto-rea/apk-analysis/tsl9-server-current/TSL9-runtime-api-payload.bin
# C 路徑：將 -Mode cpp 改為 -Mode c
```

此建置入口刻意沒有連接／掃描／燒錄選項。產物通過的是靜態來源、連結與 byte identity 驗證，並非執行行為或硬體相容性驗證。
