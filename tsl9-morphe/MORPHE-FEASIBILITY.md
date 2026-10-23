# TSL 1.2.7：Morphe patch 可行性

這是實作前的靜態評估；後續最小 patch 的實際建置與啟動結果見 [SMOKE-RESULT.md](SMOKE-RESULT.md)。

檢查日期：2026-10-18。結論：**有條件可行，適合製作專用 Morphe patch；尚未證明修改後可以正常執行。**

## 已確認的 APK 結構

| 項目 | 本機靜態結果 |
| --- | --- |
| 輸入 | `C:/Users/locky/Downloads/安卓-TSL电子模块-1.2.7.apk` |
| 大小 | 48,067,278 bytes |
| SHA-256 | `10d7d92f16d7806d841fcfd152b318601f6c234a2445e99e0729709aacc9c3ee` |
| Package / 版本 | `com.tencent.weauth` / `1.2.7`，versionCode `127` |
| SDK | minSdk 21、targetSdk 29 |
| DEX | `classes.dex`、`classes2.dex`、`classes3.dex` |
| 解析到的類別 | 9,474 |
| Application | `com.tencent.weauth.DemoApplication` |
| 啟動 Activity | `com.tencent.weauth.ui.MainActivity` |
| 核心結構 | Android 外殼＋騰訊 SaaA / Luggage 小程式執行環境＋內嵌 `.wxapkg` |
| 原生程式庫 | 包含 arm64-v8a 的小程式與 V8 等執行環境依賴；未深入分析各 `.so` |

`MainActivity.onCreate()` 可反編譯成 Java，能看見啟動畫面與選單分支。其 `BKmli()` 方法透過 `SaaAApi.Factory.INSTANCE.getApi().launchAppModule(...)` 啟動小程式。這提供外殼層 patch 的實際定位點，但不是完整功能都位於 DEX 的證據。

## TSL 功能實際在哪裡

APK 內含 `assets/SaaA_embed/` 下的 `.wxapkg`，大小 946,284 bytes。本機可直接解析其索引，共 76 個項目，包括：

- `/app-service.js`、`/appservice.app.js`：可讀的 JavaScript。
- `/chunk_2.appservice.js`：包含 `createBLEConnection`。
- `/appservice.app.js`：包含 `writeBLECharacteristicValue`、`onBLECharacteristicValueChange`、`openBluetoothAdapter`。
- `/pages/ble/`、`/pages/bleHost/`、`/pages/set/`、`/pages/gauge/`、`/pages/batteryInfo/`、`/pages/debug/` 等頁面。
- webview JS、頁面 HTML、圖片與設定檔。

因此，修改 TSL 畫面、文案或部分 BLE 行為時，應先定位小程式 JS／頁面資源。單靠修改 Android Activity，未必會影響這些功能。上述 API 字串與檔案位置已確認；尚未逐一追蹤完整呼叫鏈或裝置通訊協定。

索引中存在重疊的資料區段，例如 `/app-service.js` 涵蓋多個 appservice 片段。正式重打包時，必須一致處理所有相關項目、offset 與長度，不能只替換其中一個檔名對應的內容便假定全部生效。

## Morphe 的適用方式

Morphe 官方提供 `BytecodePatch`、`ResourcePatch`、`RawResourcePatch`，分別修改 DEX、解碼後資源與任意 APK 檔案。以 raw resource patch 讀取並重建 `.wxapkg`，在框架能力上有依據；wxapkg 解析與重新封裝仍需自行實作。[官方說明](https://github.com/MorpheApp/morphe-patcher/blob/main/docs/2_patches_intro.md)

| 想改的內容 | 建議途徑 | 目前判斷 |
| --- | --- | --- |
| App 名稱、圖示、Android 啟動畫面 | Resource / Bytecode patch | 可定位，適合作為小型驗證目標 |
| TSL 頁面文案、顏色、顯示格式 | Raw resource patch → wxapkg 資源 | 有明確實作路徑；需確認實際載入的版本 |
| BLE 重連、逾時、顯示與解析修正 | Raw resource patch → 指定 JS 邏輯 | 已找到相關 API；需依具體需求追蹤程式 |
| Android 權限或小程式容器行為 | Manifest / DEX patch | 需定位到對應執行路徑 |
| 電子模組韌體、硬體能力 | 不屬於 APK patch 本身 | App 改動不能直接證明或改變硬體能力 |

可以從 [Morphe 官方 template](https://github.com/MorpheApp/morphe-patches-template) 建立獨立 TSL patch bundle，不必修改既有 LINE / Facebook patch。

本機既有 Andrew's Patches 的 `patches-list.json`，目前只列出 `jp.naver.line.android` 與 `com.facebook.katana`，沒有 `com.tencent.weauth`。**不能直接套用該 bundle 的現成 patch。**此結論僅涵蓋已讀取的本機 metadata，不代表已查遍所有社群 patch。

## 尚未驗證的關鍵限制

1. **重簽名與小程式驗證**：修改 APK 後需要重新簽名；是否影響此 App 的 SDK 初始化、小程式授權、內嵌套件校驗，尚未驗證。
2. **載入來源與快取**：外殼確認會啟動小程式，但執行時是否優先使用內嵌包、已下載版本或快取，仍需執行證據。
3. **BLE 與硬體行為**：目前只有靜態字串與程式位置證據，沒有真機、電子模組或實際封包驗證。
4. **Morphe 工具鏈**：本次未編譯 `.mpp`、未執行 Morphe patch、未產生重簽 APK、未安裝或啟動。可行性判斷不等於已完成端到端驗證。

## 建議下一步

先指定一個修改目標，例如「某段文案改成繁體」、「調整某個畫面的顯示」或「修正特定 BLE 連線問題」。先以固定 package、版本與 SHA-256 限定輸入，建立檔案與原始內容檢查；遇到不匹配立即停止 patch。以單一可觀察的畫面變更驗證小程式重新封裝與載入後，再處理行為變更。

這次只做本機靜態分析並查閱公開 Morphe 文件；未執行 APK、未修改原始 APK、未呼叫 APK 中的後端服務，也未上傳 APK 或其程式內容。

## 靜態證據索引

- package / manifest：`ev_a337761656b84e8e6bb4f96c8b0a3cc20faddd32ebfae9c0f839fa9ad2a1ee24`
- App class inventory：`ev_672fe844160d753d1f464bbe5d66f80eaf8a745bed544495ea4713a285045cee`
- `MainActivity` metadata：`ev_8361d1c8491db8fc31292cfdeb8800d485594a36a7f112423f5eb2b9e402db0b`
- `onCreate`：`ev_5ef35952983725fbae2410dd3031a44d1f0b9186da734c87b0bb70a1a5770338`
- `BKmli`：`ev_855fa3e35050d30a4403b0f042c1f324e3f2aa09f27e68febd29c27b8d9a9e53`
- ZIP entry 與 wxapkg 索引／API 搜尋：直接對上述輸入檔本機讀取，未執行其中程式。JADX Java 表示仍受反編譯推論限制。
