# TX composed RAM 候選：Windows host C 執行紀錄

在使用者同意核對既有工具、更新索引與執行 host 測試後，以本機 Microsoft Visual C 編譯 `experiments/v4160-tx-composed-c-harness/harness.c`；該檔直接 include `experiments/v4160-tx-composed-ram-c/candidate.c`。本次僅執行新建的 **host 測試程式**，沒有執行、模擬或燒錄目標韌體，也沒有安裝軟體。

- `cl.exe` file version `19.44.35228.0`，SHA-256 `88c8344236a27a6e727e0a8edc49aaa2690bdc7a9464b9d18cc7abe70a9f1c0d`；`link.exe` file version `14.44.35228.0`，SHA-256 `ca11e6c45debd34bf652dfe984c5360a531a005ed78bf72852330c9c2590cf0d`。本機 Authenticode 檢查兩者均顯示 Valid、簽署者為 Microsoft Corporation；這不是對所有編譯依賴或供應鏈的驗證。
- 使用 Visual Studio 2022 Build Tools MSVC `14.44.35207` 的標頭及 x64 lib，以及 Windows SDK `10.0.26100.0` 的 UCRT 標頭／lib 和 x64 UM lib；環境變數僅在該 PowerShell 程序設定。這些標頭及 library 未逐一固定 hash。
- 從新建的系統暫存目錄編譯，參數為 `/std:c11 /W4 /WX /DNDEBUG`，object 與 executable 輸出均位於該目錄。編譯及連結退出碼 `0`。隨後用 Python subprocess 以 15 秒外部 timeout 啟動該 host executable，退出碼 `0`，stdout 為 `all concrete host cases passed`。
- 執行後 `harness.c` SHA-256 `0709699f7c790aa049e783363403078c082e86fe5ec8c1a5cf0de2f39fd09fe1`、`candidate.c` SHA-256 `de88c0b5677d5d036443e022c6ac71b41e7b7de347c184908cc9fc1039d957cf`；對應 Git blob 分別為 `a2d5ed563d609e8613e34beb33927384b288b967`、`ef926ac09f49f0d4c2fbbb93004bdce60622fdae`。此為執行後身分核對，不排除編譯期間檔案被暫時改動。執行檔 SHA-256 `b5732c1f6e5ee02b72901bad269347e1b799b10f1e79e8ca2b98cf04a9d50b6f`；產物未加入 Git。

六個具體案例包含兩 bank 零長、header 來源別名、前向重疊傳播、非重疊 checksum 與長度 65535 的 sentinel 案例；每例比較整個 host RAM 陣列及回傳欄位。此結果是一次 host C 語義測試，**不是**所有輸入的證明，也不證明 RISC-V codegen、private ABI、原始半字 store 的 bus 寬度／原子性、韌體原址 bytes 或完整 BIN 一致。未測異步干擾、硬體、負例突變或其他 compiler。

另以本機 Android NDK `27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin/clang.exe`（Clang 18.0.2，SHA-256 `047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6`；此處省略本機 SDK 根目錄）、明確的 MSVC/UCRT include 路徑執行同一 harness 的 `-std=c11 -Wall -Wextra -Wpedantic -DNDEBUG -fsyntax-only`，退出碼 `0`；此步只檢查語法與型別，未用 Clang 產生或執行程式。
