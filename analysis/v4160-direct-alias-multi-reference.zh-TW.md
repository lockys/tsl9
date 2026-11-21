# v4.1.60：驗證跨兩個物件的別名替換

延續[四別名批次對照](v4160-direct-alias-batch-four.zh-TW.md)。本次選 `tsl9_main_provider_90b0`：連結輸入中有兩筆引用，分屬不同的 ET_REL。只在暫存物件副本將兩者改為直接引用同一具名定義，確認重定位的位置、類型、addend 與輸入配置區段不變。移除該別名後，全部 6,364 個配置區段內容及位址等同未修改對照，覆蓋的 76,800 bytes 與原 BIN 一致。

負對照將恰好一個只含一筆該別名引用的物件換回原版，保留另一個已替換的物件、其餘別名與 resident 見證。嚴格連結失敗，唯一未定義符號是 `tsl9_main_provider_90b0`。C / C++ 基準與 split/leaf 候選在一般 Python 與 `-O` 共八路均得相同結果。

這是独立於四別名批次的對照，不表示已同時移除五個別名。原 BIN 與正式來源未改，仍非實機、獨立建置或可刷驗證。本提交只發布報告。下一步驗證同一輸入物件內的多筆引用，再評估批次整合。重跑使用 `experiments/v4160-aggregate-no-ident-next/verify.py --full`，沿用 baseline 與 llvm-objcopy 參數。
