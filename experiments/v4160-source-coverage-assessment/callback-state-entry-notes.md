# v4.1.60 狀態轉移入口：局部呼叫邊界

此記錄針對原始 decoded APP SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667` 的靜態投影，不是新增正式原址覆蓋、完整函式反編譯或實機驗證。

- `callback-state-entry-1074c.py` 固定 `0x1074c..0x10766`；在先前呼叫均返回且相關狀態保持的前提下，依序呼叫 `0xd272`、`0xb0fc`、`0x820c(0)`、`0x10032`。前兩個 callee 的全部副作用沒有由此腳本執行。`0x820c(0)` 的 byte store 為 `[gp+193]=0`，假設寫入成功。
- `callback-provider-d272-decoder.py` 對 `0xd272..0xd288` 做有限解碼：從 `[0x40048]` 讀取間接目標，以 `(0x2000bf48, 0, 19)` 為引數尾跳，保留呼叫者的 `ra`，目標 bit 0 清除。
- `callback-provider-10032-decoder.py` 對 `0x10032..0x10044` 做有限解碼：讀同一 slot，以 `((gp+300) mod 2^32, 0, 3)` 尾跳，保留 `ra`。間接呼叫使用的 slot 數值、`gp` 等仍取決於執行時狀態。
- `callback-reference-fill-composition.py` 在兩版公開參考 carrier 的檔案與 bytes 均通過固定驗證時，**假設**上述兩次間接呼叫使用參考 fill、參數未被中途變更、操作均成功，分別組合每版 12,544 個合成位置／初值案例。重設 `gp=0x20004000` 時兩段數值位址分離；人工構造其他 `gp` 可重疊，不代表真實可達。此腳本的 byte 填值是手寫投影，不執行參考 provider，也不模擬其 MMIO、副作用或中間呼叫。
- `test-callback-reference-fill.py` 檢查 APP wrapper 的逐 byte 變造、參考 slot／函式 byte 變造後重算檔案雜湊、填值的順序與環繞，以及 wrapper 對間接目標與 `ra` 的處理。若沒有任何參考 carrier，測試失敗而不是成功略過。

在專案根目錄執行（參考 carrier 是選用本機輸入，並非已安裝到實際裝置的證據）：

```powershell
$env:TSL9_ROOT=(Get-Location).Path
python -I -B experiments/v4160-source-coverage-assessment/test-callback-reference-fill.py
python -I -OB experiments/v4160-source-coverage-assessment/test-callback-reference-fill.py
python -I -B experiments/v4160-source-coverage-assessment/callback-reference-fill-composition.py
Remove-Item Env:TSL9_ROOT
```

以上均不證明真實 resident、載入完成、呼叫可達、其他 callee 對記憶體／暫存器的副作用、異常或硬體行為。
