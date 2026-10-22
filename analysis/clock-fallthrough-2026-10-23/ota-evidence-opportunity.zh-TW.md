# OTA 證據紀錄：來源核對與功能提案

[English](ota-evidence-opportunity.en.md) · [檔案雜湊與證據類型](ota-evidence-opportunity.json)

本輪只讀取現存 Android 來源，沒有執行 App、儲存耐久測試、藍牙或硬體操作。

- `MainActivity.onCreate / flushLog`（51–54、331–347 行）設計上會寫入、重載與匯出文字日誌；已記錄原檔／預計傳送 SHA。日誌會截尾且忽略寫入錯誤，完整與 crash durability 未證。
- `FirmwareImage`（13–15 行）的 transfer SHA 是預計送出的 payload 摘要，不能當成硬體接收或啟動證據。
- `OtaSession.onPacket`（60–75 行）已有依策略逐頁讀回比較；E 只使 END 狀態完成，其 payload 語意與重啟後行為未證。現有繁中 UI 已區分讀回成功／略過／未提供，且標示重啟版本未驗證。
- `MainActivity` 每次建立新的 OTA 物件（43–55 行），重開只恢復文字日誌；`DeviceInfoSnapshot`（3–12 行）仍將完整 revision 標為未知。獨立 hardware capture 與 OTA 操作互斥，不能當成既有 OTA 完整收據。

值得新增的缺口：本機、按 session 區分的 append／atomic 證據收據，串起 image／transfer SHA、讀回策略與實際結果、E 事件，以及之後另外取得的 runtime／功能觀察。重開可看歷史，不自動續傳；預設不存 UID／VIN／MAC 或未檢視 payload。

此功能尚未實作。來源以 `MORPHE_JAVA_ROOT`／`MORPHE_MAIN_ROOT` 代稱，完整檔案摘要見 JSON；本輪沒有遷移或解鎖 Morphe 目錄。
