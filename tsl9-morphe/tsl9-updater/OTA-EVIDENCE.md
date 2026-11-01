# OTA 更新證據

[English](OTA-EVIDENCE.en.md)

開始更新時，App 以獨立本機檔案保留檔案與傳輸 payload 的 SHA-256、檔案格式、頁數、指令與頁碼、重試、讀回策略、最終 E 回覆及讀回結果。每筆帶有手機時間；之後的 A0 版本 byte 也可能記入，但不會自動確認回覆裝置身分或它是在重啟前還是後。

在更新結束或中斷後，按原有「匯出 debug log」；`LATEST OTA EVIDENCE` 區段不受一般 debug log 捲動截斷。此區段只接收明確欄位，不包含 UID、VIN、MAC、密碼或韌體 payload。整份 debug log 仍請檢查敏感資料後再分享。新更新開始時取代上一份 OTA 紀錄，請先匯出需要保留的紀錄。獨立紀錄上限 512 KiB；儲存失敗時同一 App 工作階段的匯出會標記可能不完整。

`readbackVerified=true` 表示本機逐頁比較成功；`eReplyReceived=true` 表示收到 E 回覆；`restartVerified=false` 表示尚未驗證裝置重啟後執行該檔。不要為了產生日誌而重新燒錄。此版本是 debug 測試 APK，尚未於實機驗證。
