# v4.1.60：以缺少提供者的對照驗證 dispatcher → TX

接續 [TX 候選重跑](v4160-tx-reconstruction-replay.zh-TW.md)。本次新建雙物件連結測試：使用既有 dispatcher `0x1471a` 片段與既有 TX 候選，分別真編 RV32 C11 與 C++17，以 LLD `--no-relax --no-undefined` 放回原位。只在暫存來源替換一個符號名稱，未改正式來源或建置檢查。對照的 decoded v4.1.60 BIN SHA-256 是 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。

| 試驗 | 兩種語言的結果 |
|---|---|
| 原 dispatcher + TX 物件，不給 TX 入口別名 | 拒絕；唯一未定義符號為 `tsl9_dispatch23_filter_8a56` |
| 原 dispatcher，不給 TX 物件，只給同名數值 `0x8a56` | 連結成功；dispatcher 36 bytes 與原 BIN 相同，卻沒有 TX 區段 |
| 暫存 dispatcher 直接引用 `tsl9_filter_external_8a56`，附 TX 物件，無 TX 入口別名 | 連結成功；dispatcher 36 bytes 與 TX 280 bytes 均與原 BIN 相同 |
| 同上改用直接名稱，但移除 TX 物件 | 拒絕；唯一未定義符號為 `tsl9_filter_external_8a56` |

一般與 Python `-O` 的 8 項結果一致。可重跑的本機試驗路徑為 `experiments/v4160-tx-direct-binding-next/verify.py --tool-dir <NDK LLVM bin>`；此提交只發佈報告。附 TX 物件的路徑仍以 `0x2000b18c` 作為 RAM 數值假設，不是完整無外援連結。

結論：只檢查 dispatcher 位元組，會漏掉數值別名掩蓋真實 TX 提供者缺失的情況；在這個雙物件測試中，改用實際定義的名稱並要求移除提供者時失敗，可以區分兩者。不代表較大圖已整合這項改動，也不證明 ABI、實機行為或可刷寫性。下一步將同一項缺提供者測試移到較大的診斷圖，並保留現有正式檢查。
