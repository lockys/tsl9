# TSL9 硬體工具 0.7.0-test

本機測試用 Android APK：手動連線 TSL9、擷取硬體 BLE／CAN 記錄、選擇原廠或自行修改的 APP bin，依原廠 U/S/W/R/E 協定寫入運行韌體。選檔與匯出均透過 Android 系統選檔器，沒有 INTERNET 權限，不打包韌體。

APK：[`TSL9-Updater-0.7.0-test.apk`](../artifacts/tsl9-updater/TSL9-Updater-0.7.0-test.apk)。獨立套件 `com.lockys.tsl9updater.test`；debug 簽章供本機測試。原始 APK 分析見 [REA 報告](../artifacts/firmware-trace/REPORT.zh-TW.md)。0.3 的原廠流程對照與保留差異見 [OEM-ALIGNMENT.md](OEM-ALIGNMENT.md)。

0.7依確認的 mockup 改為原生淺底深綠介面與浮動膠囊導覽。三頁共享語言／連線標示；座椅改為主／副駕切換與方向按鍵，切換時要求停止。即時資料使用實際回覆的指標區塊，無效回覆或身份重置立即清空顯示。進階設定與長文收納為可展開區域，三種韌體格式、模組驗證、診斷／匯出與既有作業條件保留。詳見 [UI-REDESIGN.md](UI-REDESIGN.md) 與 [DESIGN.md](DESIGN.md)。

0.7驗證：163項本機模型、1090項三語資源、472項Android介面／生命週期檢查通過；系統選檔／匯出另通過123項Android及4項匯出內容檢查（基礎斷言重疊）。[精確收據](verification/ui-0.7.0.json)／[汽車頁截圖](verification/screens/car-portrait.png)／[藍牙更新頁](verification/screens/tools-portrait.png)／[即時資料頁](verification/screens/live-portrait.png)。截圖來自API36模擬器，無實車連線；橫向與200%字型檢查圖亦在同資料夾。需原廠素材的差異／韌體fixture測試及API23–32實機未重跑。

0.6.1依使用者要求移除門鎖／座椅的車型checkbox、檔位／車速限制與門鎖確認對話框。連線、正常A0、模組驗證及作業互斥仍需成立；未知檔位仍顯示未知，按門鎖直接送原廠A7，座椅放開／取消／1秒後要求停止。排隊動作在取消、身份改變或過期後不再開始。燈光A3完整設定維持原有獨立條件。詳見 [DIRECT-CONTROLS.md](DIRECT-CONTROLS.md)。下方0.5／0.6的舊門鎖／座椅操作條件屬歷史記錄。

0.6.1驗證：266項JVM、1014項資源、380項Android介面檢查；系統選檔／匯出另通過101項Android及4項匯出內容檢查（基礎斷言重疊）。使用本機API36模擬器與合成資料，未測實車動作。[驗證收據](../artifacts/tsl9-updater/verification-0.6.1.json)。經使用者明確確認後已上傳[私人Drive APK](https://drive.google.com/file/d/1YxLJ7vcsn125DomYKZoUsVLaJ-AGXtSt/view?usp=drivesdk)，核對檔名與208686bytes，維持owner-only；未取得遠端checksum。

0.6新增第三分頁「即時資料」：B0車況、原始檔位代碼、里程／百分比／行李廂與選用溫度／電壓欄位，另有C0 CAN ID、DLC、次數、平均Hz與資料年齡。欄位意義可在App內查看；未知CAN ID不猜測解碼，原始bytes預設遮蔽。參見 [LIVE-CAN.md](LIVE-CAN.md)。

0.6驗證：266項本機核心、1014項三語資源、344項Android檢查通過；真實系統選檔／匯出另通過92項Android與4項文件檢查（共用基礎斷言）。3797筆接收metadata離線回放彙整148個ID，沒有發送到硬體。[精確驗證收據](../artifacts/tsl9-updater/verification-0.6.0.json)／[私人Drive APK](https://drive.google.com/file/d/1KdUOCThINzzD029tmNnNjzyB1TVcKJbB/view?usp=drivesdk)。使用者目前實車P檔而模組回覆未知的問題尚未確認原因，需這次debug log及原廠App儀表對照。

0.5.1修正車況解析：檔位／速度只需B0的完整4-byte前綴，舊版誤要求16bytes；保留P檔／零車速／新鮮度限制。新增「讀取車輛狀態」、具體停用原因及遮蔽後的狀態解析log。此問題已有本機重現與回歸測試，但使用者目前提供的CAN記錄沒有B0，實機故障原因仍待新版回覆確認。詳見 [VEHICLE-STATUS-FIX.md](VEHICLE-STATUS-FIX.md)。

## 0.5 新增汽車控制分頁與版本

新增 Model 3（2021 年底）門鎖／解鎖、主副駕座椅原廠箭頭操作，以及原廠「遠光閃三次」快捷設定開關。先連線，再到汽車分頁確認車型；只有最新 P 檔／速度0資料才開放。座椅放開、移出、取消或切換分頁即要求停止，App於1秒後也要求停止，實際送達時間受GATT與硬體影響。燈光是快捷設定開關，不是立即閃燈；需另外確認原廠有此設定，並以A0讀回確認，A3回音不能作為成功。

「讀取韌體版本」查詢 A0，顯示運行／藍牙韌體版本前段。原始回覆沒有修訂號，不能僅憑0x41補出完整V4.1.60。車控與OTA／記錄互斥、更換模組／短A0會撤銷確認。完整封包、原廠方法與byte offset見 [VEHICLE-CONTROLS.md](VEHICLE-CONTROLS.md)。

## 連線與第一次測試

1. 安裝 APK，授予「附近裝置」權限。Android 6–11 需位置權限與系統位置功能。
2. 保持 TSL9 供電，關閉其他連線此模組的 App。按「掃描 TSL9」，在 10 秒掃描結果選擇自己的模組。
3. 等待 FFF0／FFF1 探索、通知訂閱及 A0 模組資訊。若要求密碼，輸入自己的 4 字元藍芽密碼；App 不猜測、不自動重試、不保存密碼。
4. 先用「BLE 回覆」記錄模式確認收到實際 A0，再停止並匯出硬體 log。零筆會顯示尚未收到資料，不代表硬體功能已正常。
5. 首次 OTA 請選自己確認相容的原廠 APP bin；測試自訂 bin 前保留可恢復的韌體與硬體方式。保持供電穩定，App 在前景，測試時不操作車輛。

## 擷取硬體 log

硬體記錄和手機端 debug log 分開儲存、匯出。

| 模式 | 來源與行為 |
|---|---|
| BLE 回覆 | 解析 FFF1 的原廠 frame，記錄指令／長度；A0 只保留版本、模式，不保存 UID／原始 payload。開始時請求一次 A0。 |
| CAN 接收 | 使用原廠 debug 頁的 `C0 01` 接收全部，或 `C0 FF FF ...` 篩選 ID。可輸入 `123,456`；不提供任意 CAN 傳送。停止送 `C0 00`。 |
| 自訂文字 | 被動接收 FFF1 notify 的 UTF-8 換行文字，支援跨通知分段。需要自訂韌體把 printf／UART 轉送至此 characteristic；App 本身不會啟用 MCU UART。 |

CAN data bytes 預設遮蔽，可明確勾選存入本機；標準診斷 ID `7DF`／`7E0–7EF` 仍遮蔽。文字遇到已知密碼、UID、Token 等標籤時遮蔽整行，但無法辨識所有自訂敏感資訊，韌體不要輸出秘密。

每次最多 5 分鐘、10000 筆或約 512K 字元；單行文字最多 4096 bytes。開始新記錄會取代上一份。最新記錄以 AtomicFile 寫入 App 私有 `files/latest-hardware.jsonl`；按「停止硬體記錄」後可「匯出硬體 log」為 JSONL。

記錄與 OTA 互斥。離開前景會停止記錄並斷線；CAN 停止指令先等待 GATT write 完成，再斷線。Activity 銷毀有 8 秒斷線上限。GATT write 完成不等於周邊確認已停止，斷電／連線錯誤時也無法保證送達。

原始協定證據與自訂文字模式的邊界見 [HARDWARE-LOG-PROTOCOL.md](HARDWARE-LOG-PROTOCOL.md)。

## 選擇原廠或修改的 bin

| 格式 | 輸入與處理 |
|---|---|
| OTA 分頁（1026B／頁） | 每頁 `[index_hi,index_lo,1024 bytes]`，從 0 依序遞增；保留原內容，頁序錯誤拒絕。 |
| RAW 映像（1024B／頁） | 大小必須為 1024 倍數；只加 2-byte 頁序。 |
| 自訂 RAW（尾頁以 FF 補齊） | 明確選擇後，僅將最後不足的頁補 `FF`；不搬移 Flash 起點、不修改原有資料。 |

畫面及 debug log 顯示原檔 SHA-256、實際傳輸 payload SHA-256、補齊 bytes、頁數。傳輸雜湊不含每頁兩個 index bytes。沒有原廠檔案雜湊白名單，可選自行修改的映像；格式與雜湊不證明硬體相容性或原廠簽章。

軟體輸入上限 256 頁，並非硬體容量承諾。只支援 APP／運行韌體 `is_app=1`，不提供 BOOT 更新；不要選其他機型或錯誤 Flash 起點的映像。

停止硬體記錄後選檔，確認相容性勾選，再按「開始 APP 更新」確認檔案雜湊。流程為 U → 必要時等待同 UID bootloader → S → 逐頁 W → 裝置支援時逐頁 R → E。模組重啟最多重連同一裝置 3 次，總等待 30 秒。

收到 E 僅顯示「模組 E 回覆已收到」。一般依 S 回覆決定讀回；若已確認原廠 `hw_ver=20`，可勾選對應的原廠略過讀回策略，不能把上方 raw hw byte 當作此型號。讀回最後一頁後，會依原廠再送 R(index=pageCount)，收到回覆才發 E。E 不代表已驗證重啟後版本。

依原廠在等待 ACK 1200ms 後重送當前 S／W／E，最多 9 次傳送；讀回間隔 1000ms，最多 5 次。GATT frame 尚未送完時不疊加，錯誤或中斷不自動續傳。單 byte W ACK 沒有頁序，無法由它區分延遲重複 ACK；這個原協定限制仍需讀回與實機驗證。

重試用盡、GATT 逾時、模式／UID 不符、停止、斷線或離開前景會停止傳送，不能回復已寫入部分。OTA 失敗時只在失敗轉換關閉連線，保留手動重新連線機會；重新連線須重新確認相容性。

## 手機端 debug log

底部「匯出 debug log」匯出手機 GATT status、MTU、指令、chunk offset、頁碼、逾時與狀態；不含密碼、UID 或 bin 內容。最新檔在私有 `files/latest-debug.log`，有長度限制。沒有自動上傳，也不呼叫原廠授權或更新統計 API；模組本身拒絕驗證時保留錯誤。

電腦查看已遮蔽的手機 debug log：

```powershell
adb logcat -s Tsl9Updater:D '*:S'
```

## 語言
App 內可選跟隨系統、简体中文、繁體中文、English。Android 13 以上同步系統 App 語言；Android 6–12 使用本機偏好。連線、連線中、掃描、記錄與更新期間禁用語言選擇。從系統設定改語言時保留當前作業，待完全斷線與停止後才重建畫面。旋轉螢幕不觸發語言重建。

使用標準 Android 字串資源，預設英文，另含 zh-Hans 與 zh-Hant。UI、確認、驗證錯誤、BLE 狀態及 OTA 進度翻譯；硬體原文與技術 debug log 保留原文。細節見 [I18N.md](I18N.md)。

## 建置與驗證

原生 Java、minSdk 23／targetSdk 36；無第三方 App runtime、JNI 或 native library。`Protocol`、`FirmwareImage`、`OtaSession`、`HardwareCapture` 可獨立 JVM 測試，`BleClient` 序列化主執行緒 GATT 操作，`MainActivity` 處理 UI 與私有檔案。

```powershell
pwsh -File ./test.ps1
pwsh -File ./test.ps1 -FactoryPaged 'C:/path/to/fw-app.bin' -FactoryRaw 'C:/path/to/fw-app-stripped.bin'
pwsh -File ./build.ps1 -GradlePath 'C:/path/to/gradle-8.13/bin/gradle.bat'
pwsh -File ./test-documents.ps1 -Serial emulator-5562
```

離線 build 需既有 AGP 8.13.0 cache、JDK、SDK 36，`local.properties` 指向 SDK。建置包含 debug APK、instrumentation APK、lint。測試包含合成 OTA／記錄資料、原廠兩種格式 75 頁比較、Android UI／通知橋接／私有日誌／停止斷線順序回歸。

`test-documents.ps1` 僅接受模擬器，需 Android 29+、英文系統文件選擇器；本次環境為 API 37。它透過真正 DocumentsUI 選入明確標記為合成資料的 1031-byte bin，再匯出兩種 log，主機 ADB 取回實際文件檢查內容與遮蔽。180 秒逾時會停止此測試 App；不掃描、不連線、不發送 BLE。合成輸入在測試結束刪除，匯出結果與執行證據依版本保留，例如 `../artifacts/tsl9-updater/documents-smoke-0.4.0/`。

0.4.0 的確切 APK、簽章與測試證據見 [verification-0.4.0.json](../artifacts/tsl9-updater/verification-0.4.0.json)。194 項 JVM、650 項三語資源、184 項三語／切換 Android 檢查通過；系統選檔與兩種 log 匯出另通過 52 項 Android 及 4 項實際文件內容檢查（部分基礎斷言重複）。三語驗證執行 `node tests/i18n-resources.cjs` 與 `pwsh -File ./test-i18n.ps1 -Serial emulator-5564`。最終 API36 模擬器通過，API37 早期啟動失敗與逾時紀錄保留，皆為本機／合成證據。[私人 Drive APK](https://drive.google.com/file/d/1JwIX6WszT6Cj1lyC336Aq3BBQ6O4QtAb/view?usp=drivesdk)。

0.5 核心與原廠檔案對照共236項、三語資源818項／194keys，三語與系統切換Android共284項通過；系統選bin／兩種log匯出另通過77項Android與4項實際文件檢查（含重複基礎斷言）。簽章與其餘驗證見 [verification-0.5.0.json](../artifacts/tsl9-updater/verification-0.5.0.json)。所有模擬器資料為合成，沒有實車動作測試。[私人 Drive 0.5 APK](https://drive.google.com/file/d/16R6gj8gRkFiaULmx1fCkZXWOMCVg96lp/view?usp=drivesdk)。

使用者後續提供的實機log已證明BLE重連、6209筆CAN接收，以及另一份75頁bin的W／R與E流程；詳見 [硬體日誌查核](../artifacts/vehicle-controls/USER-HARDWARE-EVIDENCE.md)。仍缺重啟後完整版本、車控動作、自訂文字韌體及Android6–12語言路徑的實機證據。
