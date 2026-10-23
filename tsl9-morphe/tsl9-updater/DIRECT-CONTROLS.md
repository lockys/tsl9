# 0.6.1：門鎖／座椅直接傳送

依使用者新要求，門鎖與座椅不再要求車型checkbox、P檔、零車速或有效／最新B0。未知檔位仍顯示未知，沒有改判為P。車型checkbox從畫面移除；門鎖／解鎖改為按下立即發送，不再出現確認對話框。

## 生效條件與路徑

原廠A7指令不使用UID，因此門鎖／座椅也不再要求非零UID。仍需GATT連線就緒、正常運行模式的有效A0、完成模組要求的密碼驗證、App在前景，以及沒有OTA或硬體記錄進行中。BLE寫入仍經同一序列化佇列；可排在先前唯讀查詢之後，不因短暫查詢忙碌閃爍停用。

`MainActivity`門鎖按鈕→`sendCar`→`VehicleControls.perform`→`BleClient.sendGuarded(0xA7,[22/23])`。座椅沿用原廠方向碼，按下→`beginSeat`→`sendGuarded`，放開／移出／取消→`stopSeat`→`send(A7,[16])`。原始碼與圖示證據見 `VEHICLE-CONTROLS.md`；本文件的新操作政策優先於舊版P檔／checkbox條件。

移動／門鎖指令排隊時綁定動作序號、可用條件與期限。`BleClient.writeNext`在進入GATT與第一個chunk前再次檢查；取消、身份變化、模式改變、離開前景或過期後，尚未開始的動作直接丟棄。停止指令不套用此guard，保留在佇列中。已開始傳輸的frame不在中途截斷；軟體取消無法撤回已送達的動作。

門鎖／座椅的檔位和車速現在僅供監看，不會因B0缺失、未知或過期而擋住。操作前由使用者自行確認已停妥及操作空間。App送出不代表車輛已執行，實際動作需現場核對。

## 保留的停止與其他功能

座椅於1秒後要求停止，放開或離開前景也要求停止；1秒是App計時而非硬體停止保證。停止frame完成本機write callback前仍保留連線，重複停止不重送。模組身份變化、無效A0或模式變更會要求停止；斷線清除作業，不重播動作、不自動重試。

OTA與記錄互斥、模組密碼驗證、BOOT模式限制保留。燈光快捷A3是完整設定寫入，保留原本的燈光layout確認、最新P／零車速、完整76bytes、有效UID及A0讀回核對；這些不影響門鎖與座椅的直接A7操作。即時車況與CAN分頁不變。

## 驗證

`DirectControlTests`先在舊程式失敗：無checkbox／UID／B0時`canOperate`為false；修改後通過。涵蓋直接鎖／解鎖、未知／非P／過期B0、座椅計時停止、放開停止、不可用與BOOT仍阻擋。

Android `VehicleUiChecks`以合成連線能力與記錄器取代BLE傳輸：檢查checkbox不存在、實際門鎖／解鎖Button立即產生22／23，實際座椅DOWN／UP產生26／16，沒有確認對話框；另保留取消、短A0、身份變化、A3不能假確認、停止完成後才斷線等檢查。測試不連接車輛，不代表實車動作已成功。

`PendingControlTests`涵蓋取消、身份變化、BOOT、期限與新舊動作順序。Android `BleQueueChecks`另直接使用正式`BleClient`的Write／佇列／writeNext，在未開啟GATT的狀態驗證失效動作移除，而停止與唯讀查詢保留。這是實際佇列邏輯測試，沒有實體BLE寫入。
