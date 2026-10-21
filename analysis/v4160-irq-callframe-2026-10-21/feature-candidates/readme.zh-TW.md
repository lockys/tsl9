# 五項可安全新增的功能候選

本研究只查看既有本機 APK 衍生原始碼、C/C++ 重建程式及靜態報告，新增的只有提案。沒有執行測試、編譯、下載、裝置操作、原始／重建目標程式或 ISA 模擬。[candidates.json](candidates.json) 逐項列出精確檔案、函式、行號、版本界限與仍需證明的條件；`seal.json` 保存完整來源檔案指紋，不複製 payload 或憑證。

以下「原有」只指已有證據的基礎能力，並非宣稱整個原產品沒有候選的新畫面。readable JS 為有來源對應的閱讀投影，證據 E13 保存其屬性。V4.1.00 的舊模型地址不能直接當成 V4.1.60 完整行為；跨版本只匹配一個 predicate，不能擴大為整個免打擾功能等價。

| 優先／候選 | 已有基礎 | 新增價值與必要證明 |
|---|---|---|
| 1. 免打擾說明與本機間隔預覽 | APK `show/update` 已提及免打擾；舊靜態契約有17048啟用、16F4A間隔、170E2事件及843A狀態讀取，`da_run_pair` 保留 value/known 界限。E1–E5。 | 提供使用者狀態頁，分辨已知、過期與無資料，並用明確輸入預覽相對間隔。先證明版本對應欄位及資料新鮮度，才能顯示實機狀態。尚無每日排程或硬體時序證明；不新增切換或計時命令。 |
| 2. 連線與更新階段面板 | BLE `init/txCallback/connIsOK`、`at_success/at_failure`，以及 OTA `rxCallback/Write/Read/Verify`。E1,E6–E9。 | 分開呈現已連線、通知就緒、SDK 寫入回呼、韌體回覆及比對結果。仍需處理舊回呼與共用佇列替換的歸屬。寫入回呼不是 Flash 成功證明；不新增重試、自動重連或續傳。 |
| 3. 本機設定快照與差異檢視 | `app.js/getFunListJs/storage` 和原 App 快取清除提供擴充位置；舊 loader12FDC..13124 有設定運算元，但 ROM／Flash 契約仍未確認。E1,E10,E11。 | 只保存已確認無敏感性的顯示偏好，提供帶版本的本機差異預覽。逐欄審查前白名單為空；不能把原始 `set/btn` 快取當安全格式。不匯出全部 storage、不還原任何模組設定，排除識別資料、憑證與管理／服務／控制狀態。 |
| 4. 離線韌體資訊檢查畫面 | 已有頁序／長度／加總檢查、精確來源表及映像保真報告。E5,E8,E9,E12。 | 對使用者選取的本機檔案顯示雜湊、大小、已記錄的角色／版本／來源，分開列完整性、相容性及可開機性。仍須證明解析限制與來源。雜湊或 checksum 不代表驗章、硬體適配；不加入下載或燒錄操作。 |
| 5. 去識別診斷封存 | 原 App 顯示版本與連線狀態，傳輸／OTA 有明確效果界限。E1,E6–E8,E12。 | 本機輸出有限大小的結構化 JSON，僅含不識別個人的版本、公開韌體雜湊、階段計數與無法確認的原因，提供預覽。需白名單與隱私測試；不擷取任意日誌、封包、記憶體、UID／VIN／MAC、金鑰或車輛資料。不自動上傳，不新增裝置診斷命令。 |

前兩項直接服務 App 使用者，不需要在韌體新增控制功能。第三項先限快照與差異，不能因有設定 loader 就宣稱能安全備份／還原實體 Flash。免打擾的相對間隔算式也不等於時鐘排程、手機通知抑制或已驗證的原機行為。

主要證據入口：

- [APK「我的」頁](../../miniapp/chunk_14.appservice.js) 第97行的 `show`、`connCallback`、`update`、`btn(clear)`，E1。該來源另含敏感／管理邏輯，只引用函式位置，不轉載相關內容或整頁匯出。
- [免打擾靜態契約](../../tsl9-function-hardware/twenty-third-round/dnd-contract-review/review.md) 的原 V4.1.00 範圍；[既有模型快照](../../tsl9-function-hardware/forty-eighth-round/model-root/experiments/tsl9-contract-model/src/dnd_actions.c) 的 `gate_channel/interval/da_run_pair`，E2,E3。
- [純 predicate](../../../experiments/tsl9-multiversion/src/observed_predicate.c) 與 [來源表](../../../experiments/tsl9-multiversion/src/observed_profiles.c) 的 ID2966／offset542，E4,E5；單一函式匹配不能推導整個功能。
- [BLE 投影](../../readable/BDB12361BD32C12FDBD74B66CADFC052.js) 與 [傳輸契約](../../../experiments/tsl9-apk-tx-contract/src/apk_tx.h)，E6,E7；[OTA 投影](../../readable/7686EA01BD32C12F10E0820688FFC052.js) 與 [接收／接受條件契約](../../../experiments/tsl9-apk-ota-contract/src/apk_ota.h)，E8,E9。
- [快取位置](../../readable/app.js) 第126–146行、[設定 loader 界限](../../tsl9-function-hardware/forty-eighth-round/independent-settings-loader/README.md)、[映像保真界限](../../tsl9-v4160-image-fidelity-2026-10-21/image-review/README.md)，E10–E12。

候選全部排除 ADAS 解鎖、安全繞過、CAN／車輛致動器修改、授權繞過、自動 OTA 與 raw Flash 還原。此里程碑已凍結的 source-review 沒有更動。上述功能都仍是提案，沒有宣稱實作、實機驗證或可燒錄。
