# v4.1.60：四個別名同時改為直接引用

延續[四種重定位的單項對照](v4160-direct-alias-relocation-types.zh-TW.md)。在同一次全圖診斷連結中，將 `tsl9_boot_main_9008`、`tsl9_callback_external_12b24`、`tsl9_record_consumer_provider_c6a8`、`tsl9_vector_entry_12c24` 改為直接引用各自的具名定義，並一併移除四個 linker 別名。這一批涉及四個不同的 ET_REL 輸入，各一筆重定位；未測同一物件內多次替換。

只刪四個別名而保留原引用，嚴格連結報出四個預期新增的未定義符號。替換後，全部 6,364 個配置區段的內容及位址與未修改對照一致，覆蓋的 76,800 bytes 等於原 BIN；72 個別名降至 68 個。一般 Python 及 `-O` 各重跑 C / C++ 基準與 split/leaf 候選四路，共八路批次對照通過。

原 BIN 與正式來源未改。這是使用暫存物件的診斷連結，仍有 resident 數值見證，非實機或可刷寫驗證。本提交只發布報告。下一步選一個有多筆引用的別名，檢查每個引用都已替換，並測試刻意漏掉一個引用時是否能偵測。重跑入口為 `experiments/v4160-aggregate-no-ident-next/verify.py --full`，沿用先前的 baseline 及 llvm-objcopy 參數。
