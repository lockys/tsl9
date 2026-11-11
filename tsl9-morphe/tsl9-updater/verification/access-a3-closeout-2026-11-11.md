# 便利進出 A3 結案紀錄（2026-11-11）

**真車尚未驗證。** 本次沒有連線 TSL9、沒有掃描藍牙、沒有送出任何車控或開蓋／開門指令。模擬器與本機測試不能證明車輛會執行這些設定。

## 範圍

只交付三個原廠 A3 設定欄位，不包含立即開蓋或開門：

| 設定 | 快照位置 | 選項 |
|---|---|---|
| 副駕便利進出 | byte 25 bit 3–4 | 0–2 |
| 門把手開關前備箱 | byte 29 bit 2–4 | 0–7 |
| 門把手開關充電口 | byte 29 bit 5–7 | 0–7 |

寫入沿用燈光閘門：完整 76-byte 快照、bytes 18–23 清零、其餘位元保留、獨立 layout 確認、新鮮 P 檔與零車速、A0 讀回。A3 回音不能當成功。硬體 byte 7 只顯示前備箱計時；其他 Tesla layout（raw byte 0／3／5／6／8／19）還要 byte 28 bit 3 為 0。這是 A0 raw byte，不是伺服器 `hw_ver`。

## 驗證

- 本機模型：`VehicleControlsTests` 43 項通過。沒有車控動作。
- 三語資源：1170 項、282 個鍵通過。
- Android：只在 `emulator-5554` 安裝並執行 `SmokeInstrumentation`，其中包含 `VehicleUiChecks`。結果 `PASS 133 Android UI/lifecycle assertions; no physical BLE tested`。硬體 byte 7 隱藏、模組總開關可見性，以及 A3 回音不能確認讀回，都在這次儀器測試內。
- 獨立審查：規格軸沒有缺項或超範圍。標準軸沒有硬性違規；三個判斷問題（讀回命名、選項數量、layout 判斷）已在送測前改入來源。

## 產物

- 套件：`dev.tsl9.morphe.test`
- 版本：`0.7.2-test`，versionCode 11
- 檔案：`TSL9-Updater-0.7.2-test.apk`
- 大小：1,412,161 bytes
- SHA-256：`fae7c9414069f216c4dfaec28c56e0b83df38a180c1eac53283d7853cdca9443`
- 簽章：debug，僅供測試

這不是 GitHub 上 `tsl9-updater-0.7.10-test`（versionCode 19）的後續版。不要用這份 0.7.2-test 覆蓋或取代 0.7.10-test。
