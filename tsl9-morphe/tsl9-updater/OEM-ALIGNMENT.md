# 0.3 原廠 APP OTA 流程對齊

目標：依使用者要求，將既有自選 bin APK 的 APP 更新握手、分頁、回覆、重試及讀回順序對齊原廠。保留既有 BLE 密碼驗證、自選 RAW／OTA 檔、硬體記錄與 debug log。

原始證據為指定 APK SHA-256 `10d7d92f16d7806d841fcfd152b318601f6c234a2445e99e0729709aacc9c3ee` 內的 `app-service.js`，SHA-256 `c5eb7ae87e5edf310379f19743d720114c9717c3484b8abd30ad8b158affc017`。OTA module 在 UTF-8 byte offset `0x181e8..0x19b20`。完整入口／Java／JNI 證據見 [REA 報告](../artifacts/firmware-trace/REPORT.zh-TW.md)。

| 階段 | 原廠方法／JS byte offset | 0.3 行為 |
|---|---|---|
| 準備 | `prepare` `0x18c05` | U=`55`，payload `[1]+14-byte UID`；U 第一 byte 為 0 時進 S，非 0 時等同一 UID 的 bootloader A0。 |
| 開始 | `start` `0x18bb4` / `Write` `0x191d9` | S=`53`，payload `[1]+UID`；回覆第一 byte 必須為 1。只有恰好兩 bytes 且第二 byte 為 1 才表示可讀回。 |
| 寫頁 | `Write` `0x191d9` / `rxCallback` `0x18c97` | W=`57`，payload `[index_hi,index_lo,1024 bytes]`；單 byte `00` 或完整頁面回顯才進下一頁。不符時重送當頁。 |
| 寫入重試 | `Write` | ACK 等待 1200ms；原廠 `++retryCount >= 10` 在傳送前停止，實際最多 9 次傳送。每個有效頁 ACK 重設計數。S 與無讀回的 E 同樣使用這個預算。 |
| 讀回 | `Read` `0x18f64` / `SendRead` `0x196a1` | R=`52`，payload `[index_hi,index_lo]+UID`，逐 byte 比對；錯誤重讀同頁，最多 5 次，間隔 1000ms。 |
| 讀回結尾 | `Read` | 驗完最後一頁後，仍送一次 R(index=pageCount)，收到該 R 回覆才進 E。這一筆不是額外的韌體寫入。 |
| 完成 | `UpgradeEnd` `0x1971d` / `UpdateVerNumber0x45` `0x19869` | E=`45`，payload `[1]+UID`；收到 E 才顯示模組完成回覆，仍不宣稱重啟版本已驗證。 |

## 硬體型號與讀回

原廠 `S` 分支在 `hw_ver==20` 或原廠管理員模式關閉讀回。原廠 `deviceinfo.hw_ver=Number(response.hw_ver)` 來自 `getinfo` 伺服器回覆，不能把 A0 的第一個 raw byte 當成它。

0.3 預設依 S 回覆判斷。若使用者已在原廠裝置資訊確認 `hw_ver=20`，可明確勾選對應選項；確認寫入視窗會列出這個策略。沒有新增管理員身份或存取能力。連線改變會清除手動確認，更新期間不能改策略。

## 保留的邊界與有界差異

- 韌體來源是使用者本機檔案；原廠下載階段的 `hexbuf` 由本機格式檢查與 RAW 分頁準備。沒有伺服器 CheckCode 清單可驗證原廠真偽；SHA-256 只識別輸入與傳輸內容。
- 原廠更新／統計 HTTP 不是本機 BLE 更新所需的資料來源。本 APK 保持無 INTERNET 權限，不使用 APK 內的服務憑證，也不呼叫原廠 `getinfo/update/updateok`。
- GATT frame 尚未送完時不疊加重試；ACK 計時從整個 frame 的 write callback 完成後開始。GATT 失敗直接停止，保留「實際寫入狀態未知」，不自動重連續傳 W。
- 若已收到會重啟的非零 U／完成 E，但 Android 最後 write callback 尚未到達就斷線，保留這個周邊回覆證據：U 進入有同 UID 限制的 30 秒 boot 等待；E 保留模組完成回覆。沒有 E 的斷線仍為未完成，W／R／S 中途斷線仍停止。
- S 模式拒絕、空 U、重新連線 UID 不符時保留停止判定，避免原廠錯誤提示後殘留的 timer 繼續寫入。
- 原廠 U／重啟等待及沒有任何 R 回覆時可能無界等待；本機分別保留 10 秒、30 秒及 5 次 R 的上限。
- 原廠讀回完成後等待 E 時仍保留 R 輪詢計時器。本機在已收到結尾 R 之後，以 1200ms／最多 9 次重送 E，避免原廠這條路徑的無界 R 輪詢。正常成功路徑的封包順序相同；這個遺失回覆情境未宣稱完全相同。
- 單 byte W ACK 沒有頁序欄位，無法證明延遲重複 ACK 屬於哪一頁。這是原協定限制；讀回與實機驗證仍然必要。
- 僅 APP `is_app=1`；BOOT 更新沒有加入。停止、離開前景、錯誤或換裝置會停止傳送，不回復已寫入的 Flash。

## 對照測試

`tests/oem-reference.cjs` 先檢查原始 JS 雜湊，再執行該 APK 的真實 OTA module；以明確離線的 getApp／BLE／wx／timer stub 餵合成頁面。沒有對原廠後端或硬體送出任何請求。Java 測試逐個比較 command、payload 長度、完整 payload SHA-256 與終止狀態。

涵蓋一般更新、讀回、切 bootloader、非零 U 回覆、額外 S bytes、錯誤 W ACK、S/W/E 逾時、讀回不符、hw_ver=20。另測有界靜默 R、GATT 未送完不重送、完整 ACK 間隔、取消後回呼。可用 `test.ps1 -UserRaw <path>` 再比對使用者 RAW bin 的完整 75 頁傳輸。

這些是原始 APK 程式的離線執行對照，不是執行原廠 Android APK，也不是實體硬體測試。

Windows PowerShell 的 UTF-8 BOM 產生方式與 PowerShell 7 不同，oracle 檔案已改成明確 UTF-8 無 BOM。專案原有 `pwsh` 流程已執行；另行嘗試 Windows PowerShell 驗證被本機 AuthorizationManager 政策拒絕，保留此限制，未加 Bypass 或修改政策，因此沒有宣稱 Windows PowerShell 的執行驗證通過。
