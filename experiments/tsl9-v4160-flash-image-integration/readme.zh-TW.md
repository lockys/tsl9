# 十一個可讀函式的完整離線映像整合

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

已由來源實際重編譯 34 個 raw carrier TU、2 個 IRQ C TU 與6個 Flash C TU，
合計42個 object TU。C11／C++17 產出相同的76,800-byte檔案：
`NOT-FLASH-VALIDATED-irq-and-flash.bin`，
SHA-256 `de159bb345b27250a683e197dd84b04e51a7a7ed89315347395baaea53f68be1`。

這是部分可讀重建加上其餘 raw carriers 的來源映像，不是完整還原原始碼，
也不是已驗證可燒錄的韌體。本輪不執行 RV32／模擬器，不操作 BLE、UART、CAN、Flash 或硬體。

```sh
python3 -B experiments/tsl9-v4160-flash-image-integration/verify.py --project-root . --tool-dir /path/to/llvm/bin --language both
python3 -B analysis/v4160-flash-image-integration-2026-10-22/implementation/verify_image.py --project-root . --replay /absolute/path/to/c/verification.json
python3 -B analysis/v4160-flash-image-integration-2026-10-22/implementation/check_image.py --project-root . --require-local-builds
```

原始分析 checkout 將 `analysis/v4160-` 換成 `apk-analysis/tsl9-v4160-`。
Python 3.9+ 與已安裝的相容 LLVM 工具是必要條件；本輪實際使用本機 NDK27.1.12297006
Clang18.0.2／ld.lld／llvm-objcopy。Python／shell 入口接受相同參數；Windows流程已實際執行，
未宣稱 POSIX shell、Linux 或 macOS 已執行。可指定 `--clang`、`--linker`、`--objcopy`；
`--build-root` 必須是專案內不存在的新目錄。`--language` 選 fresh 建置語言，replay 使用收據語言。
`--firmware` 同時轉送至建置與 replay 的原始資料檢查，仍強制相同固定 ID2966 SHA。

| 檢查項目 | 實際結果 |
|---|---|
| 可讀函式 | 11個／526 bytes：IRQ 264＋Flash 262 |
| 原始配置區段 | 691個，名稱／型別／flags／大小／alignment／entry-size／VMA保持 |
| 保留 raw 儲存 | 680個區段，逐一比對原始 partial ledger SHA |
| 原始來源過濾 | 僅4個 TU 的11段精確引號組語區塊 |
| 來源相依 | 42份 .d；72個固定原始檔＋12個生成來源／adapter |
| 編譯／IR／連結／輸出 | 每種語言56個實際 LLVM 指令；每份 .d 綁定自己的 MT／主來源／adapter |
| relocation | 實測8270＝8259個完整保留外部角色＋11個 typed JAL |
| canonical labels | 53個真實 section-relative binding，無新增數值 ABS provider |
| 外部入口參考 | 保留20筆，含2-byte C.JAL與不寫RA的tail JAL |
| 原始 private branches | 相對原始8280筆來源，精確解除4個IRQ＋6個Flash角色；不是假數值別名 |
| LOAD與BIN | 15個 LOAD；每個輸出位元組同時有 section 與 LOAD來源；RAM35160 bytes只保留記憶體配置 |
| 實際反例 | 每種語言23個 ELF／RELA／LOAD／BIN反例＋3個 .d 關聯反例均拒絕 |

保留區段的 partial bytes 與最終 BIN 必須分開：原始有20個配置會因 relocation 而與最終
BIN不同。680個 raw hash 是與原始 partial ledger 比，不冒稱直接等同最終BIN；
最終 ELF 的所有 section／LOAD file payload 則另與輸出及原始 BIN逐位元組比對。

與原始 ID2966 BIN 比有70 bytes不同，其中8 bytes來自前輪 IRQ prologue、
62 bytes是本輪 Flash函式。與前輪僅8-byte差異的IRQ映像相比，本輪新增62個差異位元組。
完整位址與新舊值保留在 `source-manifest.json` 和實際收據的 `checks.image`；
十一個函式的物件／連結後位元組另與已封存 native component固定，
不是從舊 BIN或舊 .o補入。其餘配置／外部 RELA／非metadata符號保持，
FILE／SECTION／mapping metadata 的實際變化單獨列帳；
8個新 typed TU 的 attributes marker僅形成不被引用的本機ABS metadata。

嚴格連結確實因唯一缺少的 `__tsl9v4160_rom_entry` 失敗，且沒有輸出。
後續 ELF僅用 `0x40000` 數值 witness完成靜態位址解析，提供0 bytes ROM程式；
不得把它當成ROM provider、韌體可執行或硬體相容證據。輸出完全由fresh物件／區段產生，
沒有舊物件連結、舊BIN fallback、padding、NOP補尾或NOBITS匯出。

program已自然佔滿100 bytes，已知poll/copy內部角色保持，但原始偏移8的指令邊界改變；
初始scratch使用A2而非A5，wrapper保存次序仍有差異。
正常返回契約依據已封存的機器碼／IR模式且有存取完成、輪詢最終清除等條件；
完整GPR前綴、逐指令、非同步／中斷等價仍為false。
已記錄的直接／relocation參考不排除未知computed或ROM參考。

晶片、板子、ROM、時序、電源失敗、開機、復原、實體相容及OTA均未證明，`flashable=false`。
本輪只有離線分析映像。新資料報告用UTF-8 LF；layout檔保留歷史封存來源的原始CRLF位元組。
`prepare_manifest.py` 是一次性的歷史證據摘取器；fresh建置只需要發布的來源／ledger／proof，
不需要它讀取過的歷史物件。build／log／反例二進位留本機，不隨來源封存發布。
唯讀檢查會明示缺少的本機archives，不能把閱讀選定metadata冒充實際產物重驗。
