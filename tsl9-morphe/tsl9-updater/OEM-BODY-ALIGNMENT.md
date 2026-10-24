# 0.7.2：原廠解鎖／燈光流程對照

使用者實車回報：座椅可用，解鎖與燈光無效。本版修正已重現的燈光設定條件差異，保留已確認相同的解鎖封包並增加診斷。尚未取得新版實車結果，不宣稱解鎖問題已修復。

## 原廠來源與對照方法

來源為先前提供的原廠 1.2.7 APK 內解包小程式；`app-service.js` SHA-256 為 `c5eb7ae87e5edf310379f19743d720114c9717c3484b8abd30ad8b158affc017`。以下位移為該解包檔的 UTF-8 byte offset。

| 功能 | 原廠證據 | Companion 行為 |
|---|---|---|
| 解鎖 | `pages/index/index.js.controlBtn`，`0x3dfd2`；`chunk_2.webview.js` 的解鎖常數區 `0x512f`，按鈕碼23 | `MainActivity.sendCar → VehicleControls.perform → BleClient.sendGuarded → Protocol.encode`；完整 frame `55 7F A7 00 01 17 BF`。與原廠相同，沒有改碼或自動重送。 |
| 鎖定 | 同原廠入口，常數區緊鄰解鎖，按鈕碼22 | 保留 A7/22。 |
| 座椅 | `SideControl`，`app-service.js 0x3df61`；按住送方向碼，結束送16 | 原有主副駕方向碼、1秒期限、放開／取消／離頁停止與佇列取消條件不變。 |
| 燈光設定入口 | `pages/set/set.js.save` 普通 `blinkHighBeam` 設定事件呼叫 `tx(163)`；沒有讀取 B0、檔位或速度的分支 | 移除 Companion 額外加入的 B0/P檔/零車速條件。沒有把未知檔位改判成P。 |
| 燈光資料 | `tx`，`app-service.js 0x4ab28`；`blinkHighBeam` 寫入位置 `0x4b422`，A3完整設定 byte30 bit6；原廠接收設定時將 bytes18..23 清零 | 保留76-byte完整快照、只改目標bit、依原廠清零狀態區，其餘設定保留。A0讀回後才確認設定相符。 |
| 支援範圍 | 原廠設定頁對 hw7 只顯示標為 `tsl7` 的項目；`blinkHighBeam` 沒有此旗標 | 不將 hw7 當成此快捷設定的相容類型。已知設定 layout 3/5/6/8/19 經離線比較；raw0 的既有手動確認相容流程保留，但不將其當成自動辨識型號。 |

`tests/oem-body-reference.cjs` 在無網路／無BLE的 Node VM 中載入固定雜湊的原廠模組，實際呼叫 `controlBtn`、`SideControl`、設定 `rx/save/tx` 與原廠 BLE frame serializer。全部輸入為合成資料，不載入使用者UID或密碼。

14組對照包含鎖定、解鎖、主駕開始／停止，以及 hw3/5/6/8/19 的燈光開／關。合成設定先經原廠 roundtrip 建立有效 enum 預設，避免把原廠不接受的全零時間／延遲值當成正常設定。`OemBodyCompatibilityTests` 比較 command、完整 payload 與 frame，共74項；這不是所有可能設定或實車動作的相容性保證。

回歸測試先在原 Companion 重現 `OEM setting must remain available without B0` 失敗，修正後通過。完整設定長度、模組身分、硬體layout、10秒快照新鮮度、模組密碼驗證、前景及作業互斥條件保留。

## 解鎖診斷與功能意義

「解鎖車輛」與「開車門」在原廠為不同項目。A7/23 解鎖不保證車門自動彈開，也不能在已解鎖時期待再看到動作。本版顯示此差別，並增加：

- `CAR DIRECT ... action=UNLOCK code=23`：開始原廠解鎖請求。
- `CAR DIRECT frame_drained ... vehicleExecution=unconfirmed`：本機傳輸 callback 已完成，仍不是車輛執行證據。
- `CAR OEM A7 reply ... interpretation=raw-only`：若模組有回覆，只記錄長度與最多兩個原始bytes；不猜測成解鎖成功，也不觸發重送。

若同一模組在原廠 App 能解鎖，而本版無效，需要新版一次點擊前後的 debug log，確認傳送是否完成及是否收到模組回覆。仍未發現有證據支持依「2021 年底 Model 3」改成另一組解鎖碼；本版不猜測或輪流試碼。

## 燈光測試方式

連線並完成模組驗證後，讀取模組資訊，再展開「原廠燈光快捷設定」。此區現在顯示停用原因：完整設定尚未收到、缺模組身分、layout不符、快照過期、等待藍牙請求或尚未確認原廠有此項。檔位未回報本身不再阻擋此設定。

這是「遠光閃三次」快捷功能的開關，不會在按下設定開關時立即閃燈。A0讀回只證明模組設定符合，實際燈光觸發與車型支援仍需在車上確認。

## 重跑

```powershell
pwsh -File ./test.ps1 -OriginalJs './inputs/app-service.js'
pwsh -File ./test.ps1 -SkipOemReference
```

第一項需要另外準備相同雜湊的原廠解包資料；第二項明確跳過原廠對照，只執行本機合成模型測試。原廠 APK／解包內容不納入Git或APK，App仍無INTERNET權限。
