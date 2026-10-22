# OTA dispatcher 獨立 HOST／原生審查

[English](readme.en.md)

本套件審查新版共享可讀 C/C++，對照官方候選 ID2966 V4.1.60 的 `0x9C4A..0x9E5C`。原始範圍為 530 bytes／169 條指令／48-byte frame；新元件尚未整合至完整映像。原 BIN 只作唯讀來源驗證，不參與產生程式。

## 已實際完成

- 獨立 HOST fixture 的 C11／C++17 各通過 16 個敘事案例、18 次 dispatcher 呼叫、898 項行為 assertions；容量防護與測試初始化不計入此數字。每語言另有四個成功編譯、隨後被獨立斷言拒絕的語意反例。
- 案例涵蓋 full32 command、W 門檻順序／四次 quarter 與返回值不作成功判斷、先 Flash 後 live RAM 的逐 word 讀取、alignment copy UNKNOWN、第二 quarter TRANSFER，以及 postcallee live S0／limit／page／context。S 測試含 saved mode、fresh mode、live S1／GP／payload／SP；U／E／R 保留各自長度與 mode 門檻，不替 R 增加 W 頁碼上限。另驗 UID UNKNOWN、active 清除先於 UID／排程、HALT／TRANSFER 保留已發生效果。
- 四個反例為 command 截成 byte、UID 後沿用舊 payload、S active 強制寫 1，以及 RAM 先於 Flash 讀取。沒有重跑舊的大型逐效果 cut 矩陣。
- 最新正式 C／C++ 原生物件各為真實單一 FUNC **776 bytes／285 條指令／112-byte frame**，比原範圍大 **246 bytes**。先前 752-byte 草稿不是本套件選定的正式產物。
- 全部原生位元組逐指令欄位與 LLVM 文字反組譯一致；每語言四個實際編譯／IR／resource／反組譯命令、三個專案 MD 輸入及實際 `stdint.h`、來源／工具／收據雜湊均讀回。三個原生運算元反例拒絕錯誤 SP 加法、移除 JAL link、把 GP read 改成 GP write。

每份正式原生物件保留九個真 UND：六個直接 callee 身分，以及三個 callback 位址身分。23 項 RELA 包含十五個 JAL 呼叫及四組 callback HI20／LO12_I；另有一個經 fresh 32-bit slot4C 讀取的間接 copy 呼叫。此十五是編譯後呼叫指令數，不能與原十三個呼叫站點依排序強配。沒有呼叫／資料 stub、數值 ABS provider、連結見證 ELF 或新 BIN。唯一 ABS 符號是精確的 `STT_FILE ota_handler.c` 中繼資料。

## 證據界線

HOST provider 使用合成數值記憶體。只有命名的 CALL 邊界能修改 named state／參數；READ／WRITE 不得暗改 frame。未知 UID 結果不當作零；中止／轉移後不撤銷先前效果。這驗證的是明示的 HOST 契約，不是 MCU 執行或暫存器直譯器。HOST fresh SP/frame 案例亦不能證明原生 C 的實體 SP 與 alias 相同。

原生版本仍以一般 C callee-preservation 為條件；參數 mask 只聲稱明示子集，沒有完整 raw A0..A7／S／GP／SP 前綴等價。W 回覆的已知 A3／A4／A5 來源投影已保留，但不能延伸成所有呼叫的完整 ABI。原 51 項 owner RELA、23 個 owner symbols 與一筆 `14094→9C4A` 的來源角色另由固定證據保留；它們尚未全部轉換成新元件的整合綁定。原函式位置、112-byte frame 的實體安全、ROM／IRQ／BOOT／Flash／OTA 與失敗復原均未證明。

`selected.json` 保存已完成量測及來源／產物 pins；seal 僅收來源與中繼資料，沒有 `.o`、可執行檔、IR 或 build archives。預設 metadata 通過不代表已讀回那些產物。

## 執行

以下路徑以本案目錄為起點。`ROOT` 必須是實際 project 根目錄；支援原 `apk-analysis/tsl9-...` 與交付後 `analysis/...` 證據版面。

```sh
python3 -B ABI-review/check.py --project-root ROOT
python3 -B ABI-review/run-host.py --project-root ROOT --language both
python3 -B ABI-review/run-host.py --project-root ROOT --replay HOST_RECEIPT.json
python3 -B ABI-review/review.py --project-root ROOT --folder NATIVE_MODE --receipt NEW_REVIEW.json --firmware OFFICIAL.bin
python3 -B ABI-review/review.py --project-root ROOT --replay NEW_REVIEW.json --firmware OFFICIAL.bin
```

`run-host.py` 的新 build 必須在本 scope `build/` 內且尚不存在；HOST 執行前後皆以封存 machine guard 檢查本機 executable，拒絕 RISC-V。`--draft` 只做未凍結來源的 positive 診斷，不執行四反例，亦非正式選定結果。唯讀 HOST replay 不重編譯或重啟 executable。

原生 review 只讀 `NATIVE_MODE` 的正式 `verification.json`／object／IR／MD／反組譯，產生的 `NEW_REVIEW.json` 必須在該既有資料夾之外且不可覆寫。省略 `--firmware` 則不讀官方 BIN，重播須保持相同模式。Python API 為 `native.py: inspect(root, folder)`；包裝 API 為 `review.py: inspect(root, folder, firmware=None)`。shell 入口接受相同參數，可用 `PYTHON` 指定 Python。

metadata stdout 的 `actual_host_artifacts_replayed`／`actual_native_artifacts_read` 為 false；實際 HOST replay／原生 review 各自明示 true。所有 full ABI／placement／hardware OTA 准入旗標維持 false。
