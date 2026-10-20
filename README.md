# TSL9 離線韌體分析與 C/C++ 重建

保存原始 APK、22 份官方更新服務已回傳的解碼 BIN，以及目前的 C/C++ 重建程式與本機驗證工具。版本標籤來自伺服器，不能單靠標籤判斷硬體適用性。

**目前沒有已驗證可由藍牙燒錄的重建 BIN。** 實際 MCU／PCB、ROM ABI、記憶體／中斷契約與 OTA 相容性仍未確認。請勿將本專案的候選配置或 `ADDRESS-WITNESS-ONLY.elf` 當作可執行、可刷寫韌體。

## 檔案位置

| 內容 | 位置 |
|---|---|
| 原始 Android APK 1.2.7 | [artifacts/apk/安卓-TSL电子模块-1.2.7-1.apk](artifacts/apk/安卓-TSL电子模块-1.2.7-1.apk) |
| 22 份不同 SHA-256 的官方回傳 BIN | [firmware-downloads/legacy-options-2026-10-20/BINs/](firmware-downloads/legacy-options-2026-10-20/BINs/) |
| V4.1.60／ID2966 啟動、IRQ、初始化與回呼重建 | [experiments/tsl9-v4160-startup/](experiments/tsl9-v4160-startup/) |
| V4.1.00／ID2581 主體與功能模型 | [experiments/tsl9-contract-model/src/](experiments/tsl9-contract-model/src/) |
| V4.1.00／R81 資料與回呼閉包實驗 | [experiments/tsl9-lookup-domain-closure/](experiments/tsl9-lookup-domain-closure/) |
| 多版本比較程式 | [experiments/tsl9-multiversion/](experiments/tsl9-multiversion/) |
| POST 下載腳本及 localhost Mock 測試 | [scripts/README-download-firmware.md](scripts/README-download-firmware.md) |
| 交付來源檔案的大小與 SHA-256 | [publication-manifest.json](publication-manifest.json) |

`apk-analysis/tsl9-server-current/` 的兩份 BIN 是 ID2580／ID2581 的相同內容別名，保留給舊驗證程式使用；不是另外兩份不同韌體。APK 的下載原名為 `安卓-TSL电子模块-1.2.7.apk`，此處依上傳要求使用 `-1.apk` 檔名，內容未修改：48,067,278 bytes，SHA-256 `10d7d92f16d7806d841fcfd152b318601f6c234a2445e99e0729709aacc9c3ee`。

## 重建範圍與證據

本專案包含高階 C 功能模型，以及用 C11／C++17 加 RV32 inline assembly 保留原始指令、暫存器行為和語意重定位的元件。它不是完整恢復的原始 C/C++ 原始碼；Python／PowerShell 用於離線分析、編譯與 ELF 核對。

最新 V4.1.60 已交付階段見 [MATERIALIZED.md](experiments/tsl9-v4160-startup/MATERIALIZED.md)：捕獲 6306B code、459B RO、554 筆重定位。嚴格最終連結仍因 84 個真實未解析符號而失敗，另有 79 個間接呼叫位置的目標／ABI 尚未完整解析。以上數字只適用於此有限捕獲範圍，不表示整份韌體只剩這些缺口。

V4.1.00 與 V4.1.60 分開處理；不混用版本的程式或尾段資料。[FEATURE-COVERAGE.md](FEATURE-COVERAGE.md) 與各實驗內文件含歷史階段說明，不能當作原硬體功能驗證。此儲存庫保存目前有效的原始碼與實驗輸入，未上傳數百 MB 的歷史分析快照、私人 API 請求／回應、日誌或暫存編譯產物；部分歷史報告連結與原機絕對路徑因此只供來源追溯。

## 本機靜態核對

原工具環境為 Windows、PowerShell 7、Python 3，以及 Android NDK `27.1.12297006` 的 Clang／LLD。既有驗證器有固定的原工具路徑；在其他環境重做前需自行配置等效工具。僅執行主機端驗證器，不執行、模擬或刷寫 RV32 目標。

```powershell
python scripts/verify-publication.py
python experiments/tsl9-v4160-startup/verify-extension.py --spec experiments/tsl9-v4160-startup/evidence/materialized-integration.json
pwsh -NoProfile -File experiments/tsl9-lookup-domain-closure/verify-native.ps1
```

最後一項可加 `-Cpp` 檢查 C++17。驗證成功表示相應的主機端靜態條件成立，不代表原機啟動、藍牙 OTA 或車輛功能通過。

原始 APK／BIN 仍屬各自權利人；此儲存庫未賦予第三方元件額外授權。
