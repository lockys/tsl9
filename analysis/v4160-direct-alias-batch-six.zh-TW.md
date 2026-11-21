# v4.1.60：六個具名別名同時改為直接引用

將[四別名批次](v4160-direct-alias-batch-four.zh-TW.md)、[跨物件多引用](v4160-direct-alias-multi-reference.zh-TW.md)和[同物件多引用](v4160-direct-alias-same-object.zh-TW.md)合併為一次全圖診斷連結。六個別名為 `tsl9_boot_main_9008`、`tsl9_callback_external_12b24`、`tsl9_callback_provider_external_128fe`、`tsl9_main_provider_90b0`、`tsl9_record_consumer_provider_c6a8`、`tsl9_vector_entry_12c24`；共八筆重定位、七個暫存 ET_REL 物件。

六個改為直接引用且不再定義原別名後，剩餘 66 個別名逐一驗證與其具名定義的區段、值一致。6,364 個配置區段的內容及位址等於未修改對照，覆蓋的 76,800 bytes 等於原 BIN。只刪除六個別名而不重寫輸入，嚴格連結的未定義符號集合恰為這六個加上尚未提供的 resident。一般 Python 與 `-O` 分別測 C、C++ 的基準及 split/leaf 候選，合計八路通過。

未修改原 BIN 或正式來源，未連設備。仍依賴 resident 數值見證與原 BIN 取樣，不是獨立建置或可刷寫證據。本提交只發布報告；本機重跑 `experiments/v4160-aggregate-no-ident-next/verify.py --full` 並沿用先前 baseline 與 llvm-objcopy 參數。下一步先對剩餘別名按物件盤點符號碰撞、重複定義與保留區段，再分批驗證可直接替換者。
