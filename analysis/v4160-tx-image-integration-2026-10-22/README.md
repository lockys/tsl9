# TX 可讀來源納入完整實驗映像

[English](readme.en.md)

本輪將已審查的 TX 入口、C/C++ 主體與返回葉函式納入完整 ID2966 V4.1.60 版面。正式 C11 與 C++17 分別重新編譯後，產出相同的 76,800-byte 實驗 BIN；SHA-256 為 `28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89`。相較官方原檔，93 個 byte 不同，全部位於 `0x8A56..0x8B6E`；其餘 byte 完全相同。**這個新檔尚未驗證可刷寫，不應當作官方韌體。**

## 來源與靜態證據

- 現有十三個原始函式範圍共 930 bytes，由十五個真實配置的 FUNC 角色承接。TX 保留真實的 8-byte 公開入口、270-byte 區域主體及 2-byte 返回葉，沒有偽造單一 FUNC280 或數值位址供應者。
- 每種語言重新編譯 46 個單元：34 個原始承載、11 個可讀 C/C++ 單元及一個直接組譯入口。45 個 C/C++ 編譯單元使用完整 `-MD`；組語入口直接釘選且不經預處理。67 個內部步驟含 64 個 LLVM 操作及三個明示排序步驟；外層資源查詢與來源產生另行記錄。
- 全部 691 個配置、678 個保留原始承載、8,261 筆重定位及十五個 LOAD 的範圍／權限都經核對。8,258 筆非 TX 重定位只容許九個目標 FUNC 大小由 280 改成真實的 8；原有其他來源、位元組與角色保持一致。
- 記錄的三十個邊界參照包含二十九個位於選定區域外的來向，以及一個既有頁面回覆呼叫。它們不是整個映像全部呼叫的枚舉。TX 的九個直接來向包含 `0x13EAC` 的無連結跳躍；未知計算式或內部入口仍未排除。

實際編譯命令、依賴、IR、物件、ELF 與 BIN 的完整產物集合由 [implementation](implementation/README.md) 與[獨立來源審查](source-review/README.md)核對；[獨立 ABI 審查](ABI-review/README.md)另讀實際物件、呼叫、重定位、三個排序階段及完整映像。預設 metadata 檢查不等於重讀真實編譯產物，需明確傳入新 build 的收據。

## 離線版面及後續限制

[版面檢查](image-plan/README.md)重讀候選 BOOT ID2580 與新映像，核對 75 頁、每頁 1024 bytes、頁碼 0..74、十四個 BOOT byte 錨點及五個實際 byte／長度反例。它不產生完整 OTA 封包，不使用裝置身分，也不證明實機的 BOOT 身分、Flash 別名或 CRC／簽章規則。

這仍是部分來源重建，其餘 678 個區段保留原始承載；不是完整原始碼還原。ROM 位址仍只是數值見證。完整原始 ABI、非同步行為、code-as-data、實體晶片、安裝的 ROM／BOOT、BLE OTA 與復原流程均待證。沒有執行或模擬 RV32、連接硬體或呼叫廠商 API。既有主機行為測試未因文件或整合而重跑。

新功能方面，離線版面檢查已成為研究工具；完整封包預檢、更新等待原因顯示仍是[提案](../v4160-ota-tx-2026-10-22/continuation-plan/README.md)，尚非硬體功能。下一步應沿實際呼叫與資料邊界重建剩餘更新流程，同時收斂 ROM／BOOT 與硬體適用性證據。

## 重跑

```sh
python3 -B experiments/tsl9-v4160-tx-image-integration/verify.py --project-root /absolute/re-tsl9 --tool-dir /absolute/llvm/bin --language both
python3 -B analysis/v4160-tx-image-integration-2026-10-22/source-review/check-review.py --project-root /absolute/re-tsl9 --firmware /absolute/ID-2966-V4.1.60-decoded.bin --receipt /absolute/new-build/c/verification.json
```

目前實際編譯證據來自 Windows NDK LLVM；可攜 Python／shell 入口本身不構成 Linux、macOS 或 CI 已執行的證明。
