# OTA 離線 preflight 調查：尚無可安全強制的相容政策

**結論：目前不能界定不誤拒合法映像、又能阻止未驗證 candidate 的燒錄政策。** 本次不修改送出邏輯，也沒有建立可授權燒錄的 preflight；現有 App 仍可能傳送未驗證檔案，請勿使用它燒錄 candidate。格式通過、使用者勾選、雜湊或離線模擬通過均不代表映像可燒錄。這是風險報告，不是防護已實施的聲明。

## 實際範圍與證據

* `../app/src/main/java/dev/tsl9/morphe/FirmwareImage.java` 只檢非空、選定格式的長度、PAGED 連續頁序和最多 256 頁。RAW 以 1024 bytes 加頁號，PAGED 是 1026 bytes（大端頁號加 1024 bytes），RAW_FF_PAD 明確補 FF。計算原檔及不含頁號的傳輸 SHA-256；兩者都不是信任判斷。任何整頁內容，包括截斷、延長和合成內容，皆可通過。
* `MainActivity.java` 的 `canFlash()` 要求 BLE ready、A0、非零 UID、手動相容勾選、認證和操作互斥；確認視窗再次檢查映像物件、UID、hw20。這不驗證型號、韌體來源或映像完整性。`OtaSession.start()` 自身也不驗證相容性，先送 U，後續 S/W/R/E；只支援 APP 模式。`S` 回覆及使用者選擇的 hw20 可導致沒有讀回；即使讀回也不證明啟動，E 回覆不是重啟驗證。
* App 是通用 TSL9 APP updater，而不是有已驗證型號清單的 updater：README 描述原廠和修改映像，A0 raw byte 及標準 Device Information 均未建立可靠 SKU／版本對應。使用者提供的另一份 75 頁檔案曾有 W/R/E 硬體日誌（`../../artifacts/vehicle-controls/USER-HARDWARE-EVIDENCE.md`），不足以推廣到所有設備或候選檔。
* `../../../firmware-downloads/legacy-options-2026-10-20/catalog.json` 記錄 22 個解碼下載，11 個伺服器版本標籤，均明列硬體適用性未證實。4 個 V1.0.00 檔 12288 bytes；16 個其他檔 76800 bytes，ID2873、2914 各 77824 bytes。這是下載存檔，不是可刷白名單；單一 75 頁限制會錯誤排除 76 頁存檔，且頁數也不能判定 APP／BOOT 或正確型號。
* ID2966 V4.1.60 原檔 76800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`；現有離線測試觀察 74、75、96、97 頁均能進入 W。見 [OTA-PAGE-RANGE.zh-TW.md](OTA-PAGE-RANGE.zh-TW.md)。其他版本與用途不能由此推論。
* ID2580 BOOT 的靜態條件算術得到 W 頁 0–95，並不證明它配對 ID2966、設備安裝此 BOOT 或 Flash 實際幾何；不得據此套用 updater 全域上限。見 `../../../analysis/boot2580-w-range-2026-11-01/README.md`。

## 可驗證的後續條件與測試（先離線，仍不能作為燒錄批准）

1. 收集每個支援 profile 的可信來源證據：裝置型號／硬體修訂、實際 BOOT 與 APP 身分、Flash 佈局、伺服器映像用途和精確完整 bytes；從獨立來源交叉確認。不能把 UID、版本 byte、檔名或使用者勾選當作型號證明，也不能推定 ID2580 的配對。
2. 分離「格式檢查」與「已驗證相容性」狀態，設計預設拒絕的授權機制：以可信 profile 綁定設備證據、精確傳輸 bytes 和經驗證的來源／版本；未識別、資訊缺失、疑似 BOOT、未知 candidate 一律不得授權。若未能取得可信 profile，就不聲稱可安全放行；自訂 candidate 的驗證標準和可信批准來源須先確立，而不是靠可自行填寫的 hash 或勾選。
3. 在純 JVM／假 listener 測試所有格式相同傳輸內容的雜湊、明確 padding、索引錯誤、空檔、最大值；對每個已證實 profile 測完整正例及少／多整頁、單 byte 變動、跨型號、錯誤 BOOT、不同填充和 unknown candidate 負例。包含 75、76 頁，以避免將特例硬編碼為通用政策。存檔標籤不是正例授權證據。
4. 授權必須在 `OtaSession.start` 等所有入口、任何 U/S/W 之前強制，綁定不可變映像 bytes 與裝置身份；測試更換檔案、格式、設備、重連 UID、勾選、非同步競態及直接呼叫 session 都不能繞過。偽 listener 斷言拒絕時 **零封包**。對未知身份也應拒絕，而不是降級為警告。
5. 即使通過上述離線條件，仍需獨立確認實際設備恢復方式、擦除幾何、斷電復原與啟動結果；這些不在本次範圍。未驗證 candidate 保持禁止，不將 host 測試、R 或 E 視作刷寫證明。

## 本次驗證

依 [OTA-PAGE-RANGE.zh-TW.md](OTA-PAGE-RANGE.zh-TW.md) 的 Python/JDK 命令執行實際 `FirmwareImage`、`OtaSession`、`Protocol` 加假 listener：PASS，覆蓋 ID2966 原檔、74/75/96/97 頁、長度、重試與尾端 R。僅在記憶體模擬，未連接設備、未呼叫 BLE、未修改 updater 或其他既有改動。
