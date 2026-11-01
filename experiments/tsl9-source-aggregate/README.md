# 來源物件局部合併

[English](readme.en.md)

執行 `python scripts/verify-source-aggregate.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>`。工具在 C 與 C++ 模式各自重編譯 125 個既有程式單元、13 個既有資料單元及 13-byte 資料窗口，檢查包含檔來源，並局部連結各 139 個物件。獨立 TX 候選套件未納入此合併。

加上 `--tx-candidate <CANDIDATE_BIN>` 後，工具重新編譯候選 TX，驗證 280-byte 窗口，將舊傳輸單元換成三段連續的 TX 物件；已檢查其他物件的 8 筆可見引用都指向舊入口，再將該入口的候選別名連到新入口。這是未配置的局部物件合併，並未證明間接中途入口或執行時 ABI。此模式額外保留 TX 的 RAM 匯入，共 8 個未解析名稱。

ADC 與 resident 單元各自提供三個同名 I/O 輔助函式。工具先檢查所有輸入均無這些名稱的外部引用或重定位，再各自將它們設為 local，避免重複符號衝突。它保留輸入物件且不修改原始碼。

未配置版面的合併物件原有 79 個未解析名稱。工具以固定雜湊的歷史來源物件查找原位址，以位址後綴與編譯前 bytes 配對 71 個 CODE 候選；另以 128-byte 內容配對初始化資料，條件性建立共 72 個別名，剩 7 個未解析名稱。這些別名均指向實際編譯區段，不是數值位址佔位；但尚未證實所有重定位語意、原位址版面、重疊所有權或執行時契約。保留的 resident／堆疊等單元也不表示已證明硬體 ROM 或 RAM。

輸出是 `NOT-FLASHABLE-*.o`，不是 BIN。此檢查依賴歷史物件作證據比較，不讀韌體、不執行目標、不證明可燒錄或功能正常。

## 原位址診斷連結

`python scripts/verify-source-layout.py --tool-dir <LLVM_BIN> --candidate <CANDIDATE_BIN> --out <NEW_OUTPUT_DIR>` 重新建立 TX 來源合併物件及比較版面，依歷史來源物件的符號與編譯前 bytes 為來源區段配置原位址。C／C++ 各有 6,235 個區段、73,551 bytes 經重定位後與既有候選診斷版面一致；無重疊且跳過既定排除區。

嚴格連結必須報出 7 個未解析符號：原有 6 個 APP 依賴與 TX RAM 依賴。僅為核對已選區段，診斷連結以數值見證填入這 7 個名稱；它們不是程式或資料的實際 provider。結果為零 `PT_LOAD` 的不可燒錄 ELF，不包含全部 76,800 bytes，不證明缺失資料、啟動、ROM／RAM 或硬體功能。此流程仍依賴歷史來源物件及 TX postpass，不是純 `src/` 獨立建置。

## 精簡版面模式

`python scripts/build-compact-source-layout.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>` 使用固定的 [compact-layout.json](compact-layout.json) 重編來源、配置區段並檢查重定位後摘要，建置過程不開啟歷史建置物件或候選 BIN。C／C++ 產生的診斷 ELF 與前述歷史物件比對流程的對應產物各自完整相同；此模式以既有摘要核對，不是當次重新讀取候選檔。

這份資料是由前述歷史比對結果整理的 9 筆區段例外、22 個排除項目、72 個候選別名與已選區段摘要；它不是獨立取得的新硬體證據。此模式仍需要 LLVM、來源追溯檔與 TX postpass，仍有 7 項數值見證與不可燒錄限制。可選擇加上 `--candidate <CANDIDATE_BIN>`，額外逐 byte 比對候選檔的 280-byte TX 窗口；不讀取排除區。
