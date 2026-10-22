# TX 原始來源證據：JSON 結構修正

[English](readme.en.md)

本份僅取代旁邊已封存 `source-review` 的公開 checker 入口。舊 seal 為 `46da5762a0bc46c15a04ad6b2bf0f890a001de66b8ac006d0c507529505d76e2`；其中11個檔案、raw decoder、280 bytes／96條指令、40個操作數控制、契約及保留證據均維持原樣。舊 checker 將新算出的 Python tuple 邊界與 JSON 讀回的 list 邊界直接比較，因而失敗。這是 checker 的序列化比較錯誤，沒有新增指令或契約變更。

新 checker 先驗證每個舊封存檔案，再呼叫原始 proof，將新結果經 JSON 正規化後逐值嚴格比較。5個結構控制確認：tuple／list 的端點改值、顛倒或缺少區間、錯誤欄位數都會被拒絕。正規化只容許等值結構轉換，不接受數值改變；亦特別重現原先直接比較失敗的原因。沒有執行重建 C/C++ 或目標指令。

```sh
python3 -B apk-analysis/tsl9-v4160-ota-tx-2026-10-22/source-review-v2/check-review.py --project-root . --firmware exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin
```

`.sh` 包裝接受相同參數及 `PYTHON` 覆寫。可重複指定 `--object 實際carrier.o`，才會額外重新讀取該實體 object 的符號、重定位及 raw body。預設明確回報實際 carrier 重查數為0；歷史 carrier metadata 不會冒充本次重播。選定封存前檢查實際讀回原始 carrier 與目前十二函式 carrier。來源證據仍無法證明不存在計算式參照、不透明 ROM 行為、硬體運作或 OTA 可用性。新的 C/C++ HOST 審查另有獨立範圍。
