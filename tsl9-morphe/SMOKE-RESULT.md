# 最小 Morphe patch 驗證結果

日期：2026-10-18。**patch、wxapkg 重打包、簽名與安裝已通過；進入 TSL 主畫面及顯示修改文字仍未驗證。**

## 交付

- [Morphe Desktop patch bundle](artifacts/tsl-text-smoke.mpp)
- [已簽名測試 APK](artifacts/tsl-text-smoke.apk)
- [Kotlin patch 原始碼](patches/src/main/kotlin/tsl/TextSmokePatch.kt)
- [建置與驗證方法](README.md)

這是本機測試用途的 JVM bundle，已由 Morphe Desktop 1.18.1 載入並執行。沒有加入 Android DEX 的 patch bundle，也尚未驗證 Morphe Manager 載入；測試 APK 使用本機測試簽名。

唯一產品改動是底部分頁標籤「状态」→「狀態·M」。修改目標為內嵌小程式的 `/app-config.json`，沒有變更 BLE 控制或硬體參數。

## 檢查結果

| 項目 | 結果與證據範圍 |
| --- | --- |
| Kotlin 編譯 | Kotlin 2.4.21、JDK 21，成功 |
| Morphe 載入 | 正確列出 `TSL wxapkg text smoke test` |
| Morphe 套用與重建 | `artifacts/morphe-result.json` 的 PATCHING、REBUILDING 均為 success；failedPatches 為空 |
| APK payload 差異 | 只變更 `assets/SaaA_embed/` 內的一個 wxapkg |
| wxapkg 差異 | 76 個索引項目均通過範圍與內容檢查；僅 `/app-config.json` 變更 |
| 真正位移更新 | UTF-8 內容增加 3 bytes；header body length、目標 size、後續 offset 均正確 |
| 其他內容 | JSON 其他欄位相同；其他小程式檔案、DEX、Manifest、原生程式庫均保持原有 bytes |
| 簽名與 ZIP 對齊 | apksigner 驗證 v1/v2/v3 成功；zipalign 檢查成功 |
| 重複套用保護 | 對修改版再次執行，Morphe 因原始 wxapkg SHA-256 不符而停止，exit code 1，未產生輸出 APK |
| 原版 APK | 原始檔未修改；SHA-256 固定檢查通過 |

簽名檢查有 94 筆原有 META-INF 資料未受 v1 entry 簽章保護的警告；v2、v3 完整 APK 簽章仍驗證成功。未宣稱 SourceStamp 或正式發行簽名。

## 實際啟動對照

1. API 37 / 16 KB / ARM64 轉譯模擬器：**原版就會崩潰**。linker 明確指出 `libmmkv.so` 的 program alignment 為 4096，小於系統 page size 16384，隨後發生 MMKV `UnsatisfiedLinkError`。此環境不能判斷 wxapkg patch 的成敗，未修改 native library 去處理它。
2. 本機 `medium_phone` 的唯讀實例 `emulator-5570`：API 36 / 4 KB，支援 ARM64 轉譯。兩版安裝前均為乾淨測試安裝，原版與修改版離線啟動都回報 `Status: ok`，並進入 `com.tencent.luggage.wxa.SaaA.app.SaaANetworkErrorActivity`；啟動後可觀察到 App 進程。畫面均為「当前网络连接不可用，请确保手机正常联网后重试」。
3. 因為停在容器的網路錯誤頁，**這不證明內嵌 wxapkg 已被載入，也沒有看到「狀態·M」文字**。目前只能確認修改版能安裝並啟動到相同的容器錯誤階段。

| 原版離線 | 修改版離線 |
| --- | --- |
| ![原版](artifacts/original-offline.png) | ![修改版](artifacts/patched-offline.png) |

## 聯網驗證阻礙

使用者已明確允許原版與修改版各一次正常聯網啟動。準備原版後，實際啟動指令遭自動安全審核拒絕，理由是第三方目的地與可能傳送的資料尚未具體授權，無法核准敏感外連。因此兩次聯網啟動都未執行，沒有改用其他工具或間接方式執行被拒絕的動作。

已停止測試 App、關閉其測試模擬器網路並結束該唯讀模擬器。原先的 `emulator-5562` 已移除這次安裝的原版，並還原原有飛航、Wi-Fi 與行動資料設定。

使用者後續又回覆「都允許」。已記錄這項授權，但補做的本機靜態檢查仍不足以確認完整啟動目的地與傳送資料，因此沒有重試被拒絕的聯網動作。

補查 DEX 只確認存在下列騰訊相關 URL host 字串（不是啟動呼叫清單，也不是完整網路白名單）：`debugxweb.qq.com`、`developers.weixin.qq.com`、`dldir1.qq.com`、`dldir1v6.qq.com`、`lhp.map.qq.com`、`long.open.weixin.qq.com`、`maplbs-40171.sh.gfp.tencent-cloud.com`、`mp.weixin.qq.com`、`mp.weixinbridge.com`、`open.weixin.qq.com`、`p6ngateway.weixin.qq.com`、`tdid.m.qq.com`、`weapp.tencent.com`、`weixin.qq.com`。SDK 同時存在小程式登入與 TDI CGI 包裝類別；本次未取得完整正常啟動呼叫鏈、動態目的地及 payload 證據，沒有對這些 host 發送請求。

若要繼續，需要先釐清可明確授權的服務目的地、啟動用途與允許傳送資料，或提供可授權的測試環境；不能將本次離線結果當作正常聯網啟動成功。

## 產物 SHA-256

```text
原始 APK
10d7d92f16d7806d841fcfd152b318601f6c234a2445e99e0729709aacc9c3ee

tsl-text-smoke.mpp
6c83ebc0cbc7c9b324c98aa8b7cd8f52cf6d0c928b08a2a81233a992a21384e9

tsl-text-smoke.apk
da760775cc35a644a351bf1d58607773001becd97f43018f68e96446f9ed0ad0
```

未 commit、push 或上傳 APK／程式內容。測試工具僅從 Morphe 與 JetBrains 的官方公開發行來源下載。
