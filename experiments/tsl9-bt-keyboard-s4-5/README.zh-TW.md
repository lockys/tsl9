# V4.1.60：BT KeyBoard 的 0x11dce／s4=5 分支

## 範圍與先前報告

這是**靜態推導**，不執行韌體、不模擬裝置、不接觸硬體。搜尋 `analysis/` 與 `experiments/` 的 Markdown 中 `11dce`、`11dd0`、`11e14`：`experiments/tsl9-bt-keyboard-local/README.md` 明確說 5、2 分支不在其切片內；其測試只核對 0x11dce 起始六 bytes。`analysis/v4160-conditional-runtime-2026-10-21/` 的機械式反組譯、CFG 與重建碼包含這些位址，但不因此等同此分支的語意解說。這是有限文字搜尋，不保證其他命名或未搜尋格式沒有相關解釋。

原始來源是 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，76,800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。以 APP 映射基址 0x8000 換算檔案 offset；此本地 decoded 檔的 hash 證明身分，不證明供應鏈。解讀可對照既存 `analysis/registered-callbacks-2026-10-24/evidence.json` 的逐指令記錄；測試獨立從原映像比對 bytes 和解碼直接分支。

## 前提和完整切片

依既有 `experiments/tsl9-bt-keyboard-local/README.md`，上游 0x1238a 從 `[s0+12]` 取 s3 指標、從 `[s0+10]` 取 s4 byte；s2 由更早表格路徑形成。0x11cc8 間接呼叫以 `BT KeyBoard`、s5、11 為參數，正常返回非零後，s4 不等於 8 才到 0x11dce。呼叫目標可變，其語意、副作用、是否返回，以及跨呼叫 ABI 是否遵守均是前提而非實測事實，不能無條件認定名稱確實匹配。

以下令 `p` 為 s3 所指 bytes，`q` 為 s2 所指 bytes，假定讀取皆有效：

1. 0x11dce 設 a5=5；0x11dd0 若 s4≠5 跳 **0x11e16**，此為其他分支，不在本次 s4=5 路徑。
2. 0x11dd4 讀 p[0] 至 a3；0x11dd8 若為零跳 **0x1240c**。接著依序在 0x11ddc/0x11de4/0x11dec/0x11df4 讀 p[1..4]，各自非零於 0x11de0/0x11de8/0x11df0/0x11df8 跳 **0x1240c**。短路意味後續 bytes 未必被讀取；此出口是既有局部切片的共同出口，不在此聲稱其全域語意。
3. 通過才讀 q[2]、q[1]、q[0]，依序位移並加上保留的 p[0]，得到 `a5 = (q[0]<<24) | (q[1]<<16) | (q[2]<<8) | p[0]`（RV32、項目位元不重疊）。0x11e14 直接跳 **0x11c64**，而非 0x11c56 或其 0x11c60 零值檢查；由 p[0] 非零可知此值亦非零。
4. **0x11c64 是已知匯合點**：既有 s4=8 切片也在其非零檢查通過後到此。既有報告記錄該處讀取靜態位址 byte，非零走 0x12186，零走 0x11c78；這兩條後續不在本分支切片。不能把 s4=5 的輸入約束套用到所有匯合點來路。

本切片內除暫存器變更與上述讀取外，沒有 store 或呼叫；因此切片本身不寫記憶體，但上游間接呼叫及匯合後的副作用未由此證明。p/q 記憶體有效性、資料生命週期及並行變更、真實鍵盤協定語意、共同出口和後續外部行為仍未知。

## 獨立離線核對

`test_branch.py` 鎖定完整映像 hash 和 0x11dce..0x11e16 原始 bytes；以獨立 B-immediate 解碼驗證六個條件跳躍的目標、條件及運算元，並解碼 0x11e14 壓縮跳躍。突變多個指令 bytes、截斷映像均拒絕。純 Python 模型測試 s4≠5、p[0]=0、p[1..4] 各自非零、有效組合與短輸入；這些是規格模型測試，不是韌體執行或完整指令解碼。模型和靜態閱讀同源，不能當作獨立實測；原始 bytes 核對也不能證明所有資料流解讀正確。

執行 `py -B -m unittest discover -s experiments/tsl9-bt-keyboard-s4-5 -v`：3 tests 通過。無 REA MCP 工具，結果不是 REA Evidence；沒有執行目標或硬體驗證。
