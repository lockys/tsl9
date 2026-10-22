# 通往原機 BIN 的目前範圍與缺口

[English](status.en.md)

此盤點的完整映像基線為 GitHub `fd48bf5` 保留的 TX 實驗映像，SHA-256 `28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89`。本輪另外新增的 OTA handler 以本目錄報告為準，不能把獨立物件的 bytes 加進尚未整合的完整 BIN。

## 真正的來源覆蓋

完整檔案為 76,800 bytes：十三個原始函式範圍共 930 bytes 由可讀 C/C++ 與明示 ABI 層提供，其中 8 bytes 是標準組語入口，其餘 922 bytes 來自包含小型原語與明示排序的 C/C++ 單元。其餘 75,870 bytes 仍是原始承載，包括 71,526 bytes executable storage 與 4,344 bytes 非 executable storage。另有 35,160-byte NOBITS RAM，不在 BIN 中。

以上是 byte／儲存體來源統計，**不是功能完成率**。把原指令寫進 C 編譯單元，不會使它變成可讀 C 重建。624-byte callback 尚未整合，也不能計入這 930 bytes。

實讀 `source-integrated.o` 有 691 個非空配置與一個真 UND：`__tsl9v4160_rom_entry`。歷史「31 個未解析符號」不是目前的 ELF 狀態；後續實際 storage 與相對標籤已解析位置義務，但沒有因此證明 resident、callback、資料生命週期或實機 ABI。

來源依據為 [完整 TX 整合](../v4160-tx-image-integration-2026-10-22/README.md)及其本機 `build/formal-v1/c/verification.json`（SHA-256 `9b76a657fae241ab83a598ced274bbd819ffd45dc1c5133d33281f00311bb2e7`）。本輪再次讀取的 `source-integrated.o` SHA-256 為 `85c674487c0bf2b0bbcbc3f0f5607d82dd07014acaf0634cfd45525ccdcdf456`。

## 完成目標仍需要的證據

| 項目 | 已有範圍 | 尚缺的必要條件 |
| --- | --- | --- |
| App 程式 | 部分可讀 C/C++、大量原始承載、可重跑的合成 HOST 與原生編譯證據 | 重要控制與更新路徑需進一步 typed native 化、處理真實 provider 與完整映像版面。 |
| MCU／ISA／板子 | WCH CH32V208／D8W 候選、原碼的外設數值與官方 SDK 關聯 | 實體 MCU／指令 profile、板上元件與連線的獨立確認。 |
| ROM | 兩份官方候選與部分閉合小函式；原 App 對版本前綴的檢查 | 已安裝 resident 的身分與必要介面／呼叫契約。韌體可依賴板上 ROM，不必只為消除 UND 而重建整個 ROM。 |
| RAM／啟動／IRQ | 原始 startup、GP／SP／RAM 與 IRQ 指令及部分 C 實作 | 實際記憶體可用性、別名、初始化／可見性、IRQ 進出及非同步觀察契約。 |
| BOOT／Flash | 數份候選 BOOT、數值寫入位置、頁面形狀及 byte 錨點 | 已安裝 BOOT 身分、實際 Flash 規則與 BOOT／Runtime 切換。檔案大小與錨點不足以證明硬體相容。 |
| BLE OTA／復原 | APK／BIN 格式、回覆及重試的靜態鏈；使用者回報官方 BIN 可由 App 更新 | 本次重建 BIN 的實際接受、CRC／簽章規則、失敗與復原證據。官方檔成功不等於重建檔成功。 |

## 不將保守條件誤作唯一實作

530／632 bytes 是原本的儲存體範圍，不是所有正確 C 實作必須恰好輸出的大小。必要條件是原語義與存活來向／continuation、可觀察 ABI 及完整版面來源均得到證明。較短不代表能把剩餘可執行 bytes 當 padding；較長也不能強行覆蓋相鄰區域或借用原 bytes 補缺。

RA 必須能正確返回，並保留實際會被觀察的語意，不是所有數值一律需要相同。候選 ROM `+0x13C` 的閉合證據只可條件縮小那個 slot 的義務，不能替代其他 callee 或已安裝 ROM 的證明。逐 byte／逐 RA 相等可以是保守的充分證據，不應取代真正的介面與行為分析；目前亦不足以自行放寬既有准入。

本輪的方向是增加真正的 App C/C++：`0x9C4A..0x9E5C` 的 U/S/W/R/E body 連接四次 Flash primitive、讀回、排程與回覆。其 W 寫 BOOT 區，不能單靠此函式就宣稱新 Runtime 可以刷入。完整目標持續開放；離線封包預檢與等待原因顯示仍是提案，沒有冒充成已驗證的硬體功能。
