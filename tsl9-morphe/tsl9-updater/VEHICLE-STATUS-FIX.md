# 0.5.1：車控已連線卻停用的查核

使用者截圖顯示運行模式、車型確認及燈光設定確認都已勾選，但「尚未讀到有效的檔位／車速」。這排除了單純未勾選的解釋，尚未證明 B0 回覆缺失或長度不相容。

再次提供的 `tsl9-hardware-20261021-192750.jsonl` SHA-256 為 `4aac352cee929f4f8590db68d0e0c7aa60d6fd8b54e55122e5f1cc55c0c4bf5e`，和先前檔案相同。3797筆都是 C0 CAN 接收，沒有 B0 車況回覆，不能將這份舊CAN記錄當作目前車控故障的直接封包證據。

## 可重現的程式問題

原廠 `app-service.js pages/gauge/gauge.js.rx`，UTF-8 byte offset 213590（`0x34256`），從 `a[0..3]` 讀取 LE32，再取 speed bits0..8／gear bits9..11。只解析這兩個欄位所需的最小完整資料為4bytes。0.5 的 `VehicleControls.onTelemetry` 卻要求至少16bytes，會丟棄具有完整檔位／車速的4、8或12-byte前綴。

新增測試先在舊程式失敗：`four-byte B0 prefix provides complete gear/speed fields and permits parked control`，改為檢查4bytes後通過。仍拒絕0..3bytes，保留最新2.5秒、P檔、零車速、明確車型確認、正常模式／模組資訊、密碼驗證和操作互斥條件。解析來源仍是通過原有frame驗證的B0回覆，沒有從CAN資料猜測狀態。

這確認一個會導致同樣症狀的程式問題，**尚未證明使用者的模組實際回覆短格式B0**。需要安裝新版後的狀態與debug log確認。

## 讓實機問題可定位

- 新增「讀取車輛狀態」按鈕：沿用原廠 `B0[1]`，不傳送任何車控動作。
- 分別顯示未勾選、未收到B0、短回覆（實際bytes）、狀態過期、非P檔、非零車速、記錄未停止、OTA進行中、密碼要求或通訊忙碌。
- `CAR STATUS B0 len=... fieldsValid=... gear=... speed=...` 記錄解析邊界；`CAR GATE ...` 只在原因變化時記錄，不包含UID、密碼、原始payload。
- 三語涵蓋新增診斷文字。門鎖、座椅和燈光的傳送指令及OTA狀態機均未改動。

本輪沒有實體手機或TSL9可供ADB測試；回歸驗證為本機核心與Android模擬器合成資料。實車是否恢復由使用者測試回覆決定，不會以合成資料宣稱實車修復。
