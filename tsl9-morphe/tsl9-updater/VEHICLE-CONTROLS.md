# 汽車分頁與版本查詢：0.5.0-test

目前0.6.1門鎖／座椅已依使用者要求改為直接A7操作，移除車型checkbox、P／零車速與門鎖確認對話框，並增加排隊指令取消檢查。下方保留0.5原始協定證據與當時操作政策；現行路徑為`MainActivity.sendCar → VehicleControls.perform → BleClient.sendGuarded`，政策以 [DIRECT-CONTROLS.md](DIRECT-CONTROLS.md) 為準。燈光設定維持獨立確認與P／零車速條件。

目標為使用者的 2021 年底 Model 3／TSL9。新增原生 `MainActivity.buildVehicleUi()` 分頁，沿用同一個 BLE 連線；沒有原廠登入、後端請求、任意 CAN 傳送或新增 JNI。實車控制尚未驗證，模組仍可能拒絕指令。

## 原廠靜態證據與實作對照

位移為解包檔 UTF-8 **byte offset**，不是 Java 行號或 MCU Flash address。APK 與原始 JS 雜湊見既有 [REA 報告](../artifacts/firmware-trace/REPORT.zh-TW.md)。

| 原廠功能 | 檔案／方法／位移 | 新 App 路徑與封包 |
|---|---|---|
| 車控入口 | `app-service.js`，`pages/index/index.js.controlBtn`，`0x3dfd2`，`tx(167,[dataset.btn])` | `MainActivity.confirmCar → VehicleControls.perform → BleClient.send → FFF1`；A7，門鎖 22／解鎖 23 |
| 主駕座椅方向 | `chunk_2.webview.js` 常數池 `gz$gwx_XC_7_3`，左 `0xbd86`／右 `0xbe10`／上 `0xbe9a`／下 `0xbf24` | `seatRow → beginSeat`；A7 payload 26／27／28／29 |
| 副駕座椅方向 | 同檔左 `0xc582`／右 `0xc60c`／上 `0xc696`／下 `0xc720` | A7 payload 12／13／14／15 |
| 放開停止 | 原廠 `SideControl` touchstart/touchend；結束傳 16 | `ACTION_UP/CANCEL`、移出、多指、離開分頁／前景與失去控制條件時 `stopSeat → A7[16]` |
| 座椅箭頭證據 | `page-frame.html` 內嵌字型，實際渲染 e612／e66d／e611／e66e 為左／右／上／下 | 圖見 `artifacts/vehicle-controls/oem-seat-icons.png`；新 App 使用原生箭頭，不打包原廠字型 |
| 燈光快捷「遠光閃三次」設定 | `app-service.js pages/set/set.js.tx 0x4ab28`；寫入 `0x4b41d`、讀取 `0x4c073` | `confirmLight → setBlinkHighBeam → A3[完整76bytes]`；僅修改 byte30 bit6，依原廠將 bytes18..23 清零，其餘保留 |
| 設定確認 | 原廠 A0／A3 cache；`setCheckData 0x28f34`／`getCheckData 0x28f92` 為比對狀態，非 payload checksum | 新 App A3 只送一次，之後另查 A0；只有 A0 內容符合原快照與修改才顯示已讀回，A3 echo 不能確認 |
| 韌體版本欄位 | `app-service.js getinfo 0x1a04c`：`bt_ver=s[1]<<8`、`fw_ver=s[2]<<8`；`pages/my/my.js.getver 0x3852a` 格式化完整16bit | `requestInfo → A0 → packet → DeviceInfoSnapshot.parse → displayVersions`；byte1 藍牙、byte2 運行韌體前段，**不是 BOOT 版本** |

以上位移對應 `app-service.js` SHA-256 `c5eb7ae87e5edf310379f19743d720114c9717c3484b8abd30ad8b158affc017`。完整分頁版本鏈包含原始小程式 JS 與 Java BLE bridge，見 REA 主報告；新 App 的控制核心是 Java，沒有 `.so`／RegisterNatives 邊界。

## 使用方式與限制

先在「硬體工具」連線並完成使用者自己的模組密碼驗證，再進入「汽車控制」。勾選確認車型，等待車輛資料顯示 P 檔、車速 0。門鎖／解鎖另有確認視窗。座椅方向按住傳一次開始、放開要求停止；App 於 1 秒後要求停止，GATT 延遲、斷線或模組不支援時不能保證實際停止時間。需要時使用車上實體控制。

燈光功能是開啟／關閉原廠快捷設定，**不是立即開關大燈或直接閃燈**。使用者需再確認原廠設定頁有此項；僅支援完整 76-byte 快照和對照過的標準 Tesla layout（raw hw byte 0／3／5／6／7／8／19），快照需在 10 秒內。未知或其他長度拒絕寫入。raw hw byte0 仍是未知型號，不當作自動相容性證明。

控制需要 2.5 秒內的 B0 資料（原廠 `B0[1]`）；速度取 word bits0..8、檔位 bits9..11，P=1。只有開啟汽車分頁時才輪詢，A0 每5秒、B0 約每秒。資料失效、短 A0、UID／硬體／版本變化會撤銷確認或要求停止。斷線不重播動作；車控不自動重試。

OTA、硬體記錄及汽車動作互斥。座椅停止仍排隊時保留連線，完成本機 GATT write callback 後才處理使用者要求的斷線；這個 callback 不是硬體動作完成回覆。所有狀態與確認有簡體／繁體／英文。

A0 只給版本高 byte。例如 0x41 顯示 V4.1；完整 V4.1.60 的尾段無法由此回覆得知，畫面明確標示未提供修訂號。沒有呼叫原廠後端補全，沒有把 bin 檔名當作目前版本。

## 最終效果與證據層級

控制的預期終點是 FFF1 藍牙封包與模組／車輛動作；手機只儲存已遮蔽的 debug log，不寫資料庫，不呼叫網路。門鎖／座椅本機送出只顯示「未確認」，不能據此宣稱實車動作成功。燈光 A0 讀回確認僅證明設定快照相符。

`VehicleControlsTests` 驗證 wire bytes、P/速度/新鮮度、停止與 A3 bit-mask；`VehicleUiChecks` 在 Android 模擬器測實際 Activity packet 分派、短 A0／UID 撤銷、A3 echo 不能確認、touch CANCEL 與停止完成後才斷線。這些是合成測試，沒有實體車輛控制證據。實機 OTA／CAN 的使用者日誌證據另外列在 [硬體日誌查核](../artifacts/vehicle-controls/USER-HARDWARE-EVIDENCE.md)。
