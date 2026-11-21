# v4.1.60：完整位址範圍的 TX 直接綁定診斷

延續 [雙物件對照](v4160-tx-direct-binding.zh-TW.md)。本次以現有診斷建置取得 C/C++ baseline/candidate 四路的實際連結輸入，僅在暫存副本將 dispatcher 的 `tsl9_dispatch23_filter_8a56` 引用改為 TX 定義的 `tsl9_filter_external_8a56`，並移除原本以 linker script 依區段地址合成的 TX 入口別名。保留 `--no-undefined`、`--no-relax` 和原有比較。每路測試三種配置：

| 配置 | 四路結果 |
|---|---|
| 直接引用且保留 TX 定義 | 連結成功；6,352 個放置區段、76,800 bytes 與原診斷圖一致；覆核 `0x14738` 的 JAL、TX 符號的區段歸屬與舊別名不存在 |
| 保留 `.text.tx`，但將入口符號改為 local | 連結失敗；唯一未定義符號為 `tsl9_filter_external_8a56`，診斷也指向改名後的 dispatcher 物件 |
| 由 linker script 丟棄 `.text.tx` | 連結失敗且診斷涉及 `tsl9_filter_external_8a56`；這不是只改單一符號的控制 |

一般與 Python `-O` 各完成四路，共 24 個診斷重連結。正向輸出沒有 PT_LOAD，主驗收仍拒絕六項 aggregate 比較。這是暫存診斷，不是正式原始碼變更，也不是從零重建：保留 BIN 衍生資料、其他數值見證及既有片段，沒有執行韌體或連接設備。下一步是將這條直接引用納入可重跑的診斷建置流程，並獨立處理主驗收的符號表與 addrsig 差異。本次只發佈驗證報告。
