# 十二函式完整映像：獨立 ABI 審查

[English](readme.en.md) · [简体中文](readme.zh-CN.md)

此審查將新 OTA 頁面回覆函式納入既有十一函式的整合驗證。十二個可讀 C/C++ 函式共650 bytes；其餘區段仍保留原始位元組載體，沒有宣稱完整還原所有程式碼。最終實際 C/C++ 結果及選定產物雜湊見 `summary.json`、`receipts/`。

`baseline.json` 是從已封存的前一版實際物件與連結檔獨立整理的**驗證資料**。它固定691個配置區段、679個保留區段的內容雜湊、8257筆外部重定位角色、全域／區域／SECTION符號角色、53個相對區段綁定及21個實體入口。新的實際檢查不依賴舊 Windows 建置物件仍然存在。

檢查要求十二個連結函式的650 bytes與原始韌體相同，12個 JAL 的實際寬度、目的暫存器、目標及 RA 正確，11個已消除私人標籤的分支仍保有原始指令與目標。新增 TX 呼叫位於9BE0，目標是保留區段中的8A56，RA為9BE4。入口9DF4的`693b`是 C.JAL，寫入RA9DF6；它不是無連結跳轉。原始公開NOTYPE/size0及local entry0保留，新編譯函式的FUNC124為另一個符號。

兩個排程階段分別核對：獨立回覆物件的28 bytes順序還原，以及合併後IRQ／Flash quarter的14 bytes保存順序還原。每一步都使用實際編譯字，核對收據、原始／產物雜湊及其他符號、重定位與位元組不變。這是「C/C++編譯＋明確ABI排程」流程，不能稱作編譯器單獨輸出最終保存順序。

新物件讓排除型`.llvm_addrsig`從56增為57 bytes。檢查要求舊56 bytes雜湊不變，僅追加實際回覆物件的一個符號索引；該索引在原生物件的實際符號表指向新的FUNC124。合併後的排除型區段link=0，不能把其串接索引當成全域符號索引。最終ELF必須不含此區段。

完整映像檢查包含所有LOAD的記憶體範圍、權限及檔案／NOBITS區別，並要求690個檔案區段無重疊、無缺口地覆蓋76800 bytes。實際BIN必須同時等於ELF散佈內容與SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667` 的原始韌體。6個獨立控制修改實際ELF／BIN bytes，測試錯誤入口連結、TX RA、原始NOTYPE角色、LOAD權限、addrsig追加內容及輸出位元組都會被拒絕。

```sh
python -B check.py --project-root ROOT
python -B review.py --project-root ROOT --firmware ORIGINAL_FW --folder ACTUAL_MODE_FOLDER --receipt NEW_REPORT.json
python -B review.py --project-root ROOT --firmware ORIGINAL_FW --replay NEW_REPORT.json
```

`check.py`及`check.sh`預設只核對封存來源／中繼資料，**不重播建置產物或讀取韌體**。後兩個指令及`review.sh`是明確的實際產物模式；新報告路徑必須尚未存在。發布封存不含`.o`、`.elf`、BIN或`build/`；README與完整繁中版本相同，其他語言分檔。

數值ROM位址見證並不包含駐留ROM實作。未知計算式入口、實際晶片／板型、ROM、硬體、中斷時序與藍芽燒錄安全性仍未驗證。此審查沒有執行或模擬目標CPU、連網、操作硬體或另行產生韌體BIN。
