# OTA 收到 E：協定分類紀錄

[English](ota-e-response.en.md)

使用者回報以重建 BIN 嘗試更新時，硬體回覆 `E`；原廠 BIN 最後也回覆 `E`。使用的 App 是 tsl9-morphe APK，更新後仍可重新連線並讀取韌體版本。這些是使用者實機回報，本次未由 agent 操作硬體。

使用者已明確指定 [TX 整合候選](../artifacts/offline-images/ID2966-V4.1.60-tx-integrated/README.md)，並確認它最後也顯示與截圖相同的訊息。該候選本機 SHA256 為 `28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89`。截圖實際選取原廠 SHA `0ee64183...fb667`；候選結果以使用者文字回報為證，未將原廠截圖套用成候選的原始傳輸紀錄。

這個對照與 END 回覆一致，E 本身不是已確認的失敗症狀。本候選已有「使用者回報 OTA 會話完成、所有頁讀回相符」的實機證據；重新啟動後的候選程式執行與完整原機相容性仍未完成驗證。另見[分層觀察記錄](../artifacts/offline-images/ID2966-V4.1.60-tx-integrated/field-observations.json)。

## 已確認的離線證據

1. 既存 APK 解包的 `app-service.js`：`UpgradeEnd()` 執行 `TxSend(69, ...)`，RX 的 `case 69` 呼叫 `UpdateVerNumber0x45()`。69 十進位等於 0x45，即 ASCII E。這是原始 App 的更新結束流程，不是單憑字母命名的通用 error 判定。腳本 SHA256：`c5eb7ae87e5edf310379f19743d720114c9717c3484b8abd30ad8b158affc017`。本次未呼叫腳本中的網路功能。
2. 目前 Morphe updater 的 `OtaSession.java`：`end()` 送 command 0x45；`onPacket()` 先要求 command 等於目前 expected，在 END 分支將狀態設為 DONE。註解明示 E payload 語意未有文件。這只是這份 updater 的會話結果，不驗證新 runtime 已成功執行。來源 SHA256：`da7a612e0314cab3ef46a3c5c2650f8a342e94b5d59607174bbc194dd393e7f0`。
3. 官方 ID2966 V4.1.60 Runtime，SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，確有刻意回覆空 E 的分支：

| 原始 VA | 實際作用 |
| --- | --- |
| 0x9C6A／0x9C6E | 比較 command=0x45，分支到0x9DF8 |
| 0x9DF8..0x9E18 | 要求 active非零、完整長度15、payload mode=0，並要求0x92F2回傳零 |
| 0x9E2C | 清除 active |
| 0x9E30／0x9E44 | 對0x8E18／0x99E8要求排程，參數分別200／400；不在此宣稱已經過對應時間 |
| 0x9E48..0x9E50 | A3=A2=0、A1=0x45，跳到共用回覆路徑 |
| 0x9DB4 → 0x13E98 → 0x8A56 | 對空 payload 要求 TX queue handoff；並非已送達證明 |

此 Runtime 分支沒有確認整份映像 CRC、callback 執行完成或新韌體啟動成功。它接受 mode0；目前 APP-only updater 送 mode1。因此不能將本次 E 直接歸因於這個 Runtime 分支，回覆也可能來自更新器／BOOT。

## 為何 V4.1.00 不能識別目前映像

使用者進一步提供同一台裝置的功能對照：刷官方 V4.1.00 後座椅功能無法運作，透過我們的 tsl9-morphe APK 更新官方 V4.1.60 後恢復正常。這是使用者回報的實機功能證據，支持 APK 能完成官方映像更新，且更新後裝置執行行為確實改變；證據強於單獨的 E 或頁讀回。它沒有驗證所有硬體／映像組合，也不能延伸為重建 TX 候選已正常執行的證明。

使用者回報非凡官方更新後一律顯示 V4.1.00，但座椅功能有變動。這與下列實際程式路徑不矛盾，不能單憑畫面版本認定仍是舊映像：

1. 原 APK 的 `getinfo(s)` 先以 `fw_ver=s[2]<<8` 建立前綴。只有伺服器回覆正值 `e.fw_ver` 才覆蓋它；程式也可恢復快取的 deviceinfo。可讀解包檔 `7FE9D4A3BD32C12F198FBCA429EFC052.js` 的第27、29、37行對應這些步驟；原始 `app-service.js` 第3019行有相同內容。
2. 原 `getver()`（app-service.js 第4012行）使用十六進位 nibble 與最後兩位格式化。因此 `0x41 << 8` 就會顯示 `V4.1.00`。這是條件性推導，不判定此次伺服器／快取為何選用該值。
3. 本機獨立 updater 的 `DeviceInfoSnapshot.java` 也只將 A0 `data[2]` 解讀成兩個 nibble 的前綴，`revisionKnown()` 固定為 false。
4. ID2966 原 BIN 的 `0x9E84..0x9EA6` 經 fresh `0x4004C` provider，要求將數值來源 `0x08077B00` 的8 bytes複製到目前 SP，再回傳兩個 word。A0 producer `0x13346..0x133A2` 將 metadata byte1 放入最終 payload index2；`0x1359A..0x135AC` 以 command160、長度76呼叫回覆入口。三段共144 bytes／51指令，均已逐列對照實際官方 BIN。

上述 firmware 資料鏈要求 provider 正常 copy、有效 SP／GP、沒有不利 alias／IRQ／外部改寫且後續 helpers 不改 header；它不是實測裝置的 `0x08077B00` 內容，也不能用數值來源識別實體晶片。原始證據為 `experiments/tsl9-v4160-startup/evidence/direct-expansion-cfg.json` 的0x9E84，以及 `code-continuation-cfg.json` 的0x13346／0x1359A。

## 目前證據界線

只有解碼後的 command0x45 才套用 END 語意；payload內的0x45、0x0E錯誤碼及任意 App 文字不同。此次已有 App 畫面與使用者原廠／候選對照，不再將 E 當作失敗線索。

候選那次的選檔 SHA 截圖、原始訊框與確切 App build 尚未提供；既有觀察已分開保留，不要求重刷。版本文字不能單獨作為映像 fingerprint，ACK／App DONE／讀回結果也各有不同的驗證範圍。本次未因此修改韌體、操作硬體或呼叫網路服務。
