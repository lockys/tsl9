# 0x18ec4 host-only C harness

`harness.c` 直接包含相鄰的 candidate，使用手寫靜態事件腳本檢查 callback 順序、類型、地址、讀取回傳值、寫入值、事件耗盡及對齊返回值。案例涵蓋 busy 重讀、不同 control 讀值及零值；意外 callback 或不符時立即失敗；但若錯誤程式不再呼叫 callback 而掛起，仍需要外部逾時。

這些 fixtures 是人手指定的腳本，不是硬體行為或地址 alias 的證明，也不證明 candidate 與原始程式等價。C harness **尚未編譯或執行**，不能宣稱 C 測試通過；本次沒有執行 target、模擬、網路或硬體設定。

`test_pins.py` 僅以 SHA-256 檢查 candidate 與 harness 的檔案位元組，並測試記憶體內變異及不存在路徑的負例；這不是 C 語意驗證。從 repository 根目錄可執行：

```text
python experiments/v4160-18ec4-c-harness/test_pins.py
python -O experiments/v4160-18ec4-c-harness/test_pins.py
```

以上路徑以 repository 根目錄為基準；pin 更新應經人工檢視，而不是自動接受變更。
