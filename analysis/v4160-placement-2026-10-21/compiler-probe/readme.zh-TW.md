# 有限的大小與跳躍寬度檢查

凍結的 reset-memory C/header 改用 **-Oz** 後，C11 與 C++17 都產生 **66 bytes 的 leaf**、**68 bytes 的 fragment**，各 **20 條指令**；原 -Os 為 78/80 bytes、24 條。配置仍限定 T0/A0/A1/A2。三個原始碼 GP 觀察點，現在對應三次機器指令 GP 讀取，仍有兩個迴圈 SCC。兩者依然超過原本 62 bytes。Fragment 雖寫 `c.j`，實際仍是四 bytes JAL x0，續接 relocation 位於 offset 64；缺少提供者的嚴格連結確實失敗。數值位址見證只提供位址，沒有提供續接程式。

同樣只將凍結的 clock register 模型改為 -Oz，C/C++ 都得到 **query 196 bytes／64 條**、**fields 38 bytes／10 條**，與 -Os 相同。Query 配置 A3/A4/A5，只有明確的外部遮罩 primitive 可寫 A2；fields 只配置 A4/A5。原本的 fields 正常輸出指令樣式與原始目的暫存器檢查均通過；這些結構檢查沒有證明 query 的所有分支語意。

每個 reset 組態通過釘選的 ELF、LLVM IR、完整原始指令 bytes、編碼目的暫存器及雙迴圈 CFG 檢查，另有三個實際編譯負向控制、六個反組譯文字控制。每個 clock 組態通過既有 ELF／完整 bytes／RD／無環 CFG，另有三個實際編譯控制、十四個文字控制。沒有執行目標程式。Reset 正常輸出有結構限制，共用 C 行為另有 hosted 測試；仍未證明完整原生迴圈、變動 GP／中斷情境及原始 fallthrough ABI。

合成組語實測 C.J 在 +2046 與 -2048 位移皆是兩 bytes，編碼範圍為 [-2048,2046] 且需兩 bytes 對齊。但同一工具鏈在 `--no-relax` 下，對僅相距 +378 的外部符號仍產生四 bytes JAL x0，不能只看 `c.j` 拼法宣稱已壓縮。JAL x0 的兩 bytes 對齊位移範圍為 [-1048576,1048574]，已核對實際連結符號與 raw immediate 欄位。這僅證明幾何條件，報告中的候選位址尚未證明為可用空間。Reset/query/fields 的原入口第一條均是四 bytes，單寫兩 bytes 會切開原指令；IRQ 開頭為兩條各兩 bytes 指令。沒有安裝原入口 thunk、修改原映像或產生韌體 BIN。

`results.json` 選定七份逐 byte 相同的結果副本。歷史 object／ELF／IR／log 保留在本機 `build/`，重新編譯不依賴舊 build。Checkout 需包含凍結的模型原始碼及明確釘選的既有 verifier/parser 原始碼依賴。跨平台命令請見 [English](readme.en.md) 的 code block。

`probe_thunks.py` 額外唯讀存取釘選的原映像以確認入口指令邊界。`check_probes.py --project-root .` 檢查封存資料及目前原始碼；若本機歷史輸出仍在，會重做靜態檢查；加 `--require-local-builds` 可要求歷史檔案必須存在。只核對 metadata 不代表重新編譯。所有工具由本機提供，沒有下載、網路、裝置 I/O、RV32 執行或模擬。

最初一次合成 `.S` 前處理因 sandbox 暫存檔 rename 權限失敗；成功的純 `.s` 不需前處理。失敗輸出保留在本機，但未列為成功證據。
