# OTA 頁面回覆：獨立 ABI 靜態審查

[English](readme.en.md) · [简体中文](readme.zh-CN.md)

本範圍審查 ID2966 V4.1.60 的 `0x9B8E..0x9C0A`（124 bytes、50 條指令），以及實際由 C/C++ 編譯產生的對應物件。原始證據來自已封存的 `../source-review/`。最終實際產物為 `experiments/tsl9-v4160-ota-page-reply/build/formal-native-final/{c,cpp}`；兩種語言的排程後連結內容均與原始 124 bytes 完全相同。完整映像整合尚未執行。

編譯器產生的 124 bytes 保留所有呼叫、分支與尾端跳轉的位置；標頭寫入、完整 32 位元索引算式及 TX 參數配置都符合原始指令。只有 `[+0x02,+0x16)` 的儲存／ROM 指標讀取順序，以及 `[+0x58,+0x60)` 的成功路徑還原順序不同，共 28 bytes。這兩個區間各自包含相同的指令字；編譯器本身尚未產生完整原始順序。

`native.py` 分別檢查實際 C/C++ ELF、完整 50 條原始指令欄位與 LLVM IR。每種語言另有 7 個實際機器碼變異及 4 個 IR 變異，全部必須拒絕。若提供明確排程後的物件，還會要求排程只改動上述兩個區間，其他 ELF bytes、區段、符號與重定位完全相同，且最終指令順序與原始證據相符。TX 的 4-byte JAL 仍由其唯一重定位處理。

```sh
python -B native.py --project-root ROOT --folder ACTUAL_COMPONENT_FOLDER --report NEW_REPORT.json
python -B native.py --project-root ROOT --folder ACTUAL_COMPONENT_FOLDER --scheduled SCHEDULED_OBJECT --report NEW_REPORT.json
```

這是明確指定實際產物的靜態檢查，並不編譯或執行目標韌體。報告路徑必須尚未存在。

完整的實際產物檢查與唯讀重播使用以下介面（亦可透過 `review.sh`）。它還會核對排程收據、C11／C++17 配方、固定 `0x9B8E` 的連結函式及實際 TX 的 `0x8A56` 目標／`0x9BE4` RA，並拒絕 3 個實際 ELF bytes 變異。駐留 TX 實作沒有連入；ABS 數值符號僅供位址見證。

```sh
python -B review.py --project-root ROOT --folder ACTUAL_COMPONENT_FOLDER --receipt NEW_REPORT.json
python -B review.py --project-root ROOT --replay NEW_REPORT.json
python -B verify.py
```

最後一個指令及 `verify.sh` 預設只驗證封存的來源與中繼資料，不重播未發佈的建置產物。封存排除 `.o`、`.elf` 與 `build/`。`metadata/` 保存最終獨立 C/C++ 結果及原型排程的每種語言 18 個實際 ELF、5 個路徑、3 個收據變異結果；原型與最終原始編譯物件的 SHA 相同。`order_audit.py` 可針對明確提供的實際資料夾及新的 `--work` 路徑重做這 26 項排程檢查。

配置器與複製函式透過即時 S2 的新鮮指標呼叫；成功路徑在還原 S0 前選取 A0，再透過新鮮 T1 指標尾端跳轉。這次跳轉不建立新 RA。空配置結果使用獨立還原路徑返回，A1..A7 留下配置器決定的值。IR 的三參數 `musttail` 介面只是暫存器轉接：A1/A2 必須轉送 TX 回傳後的值；它不能證明駐留釋放函式的實際 C 簽名。

未知駐留函式的 SP／callee-saved 暫存器行為、未記錄的計算式入口、實體 ROM 身分與硬體／OTA 相容性都未驗證。調換堆疊儲存與 ROM 讀取會改變錯誤或中斷前綴，因此排程層必須明確標示為來源 ABI 順序還原；不能聲稱任意輸入下編譯前後均可交換。此範圍未執行 CPU、模擬器、網路或硬體操作。
