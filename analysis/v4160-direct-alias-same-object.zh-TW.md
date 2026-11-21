# v4.1.60：同一輸入物件內的多筆別名引用

延續[跨物件多引用對照](v4160-direct-alias-multi-reference.zh-TW.md)。本輪選 `tsl9_callback_provider_external_128fe`，兩筆引用同屬一個 ET_REL。只在診斷用暫存副本中將兩筆引用都改為直接引用具名定義，再移除此別名。6,364 個配置區段的內容與位址等同基準，涵蓋 76,800 bytes，與原 BIN 一致。

負對照在暫存副本重新加入原別名的未定義符號，僅將 `.text.tsl9_callback_provider_block_12b58+0xe` 的一筆重定位改回。檢查重定位清單確實只變更這筆的符號引用，且配置區段不變。其餘引用仍指向具名定義，resident 數值見證也保留；嚴格連結的唯一未定義符號是 `tsl9_callback_provider_external_128fe`。

一般 Python 與 `-O` 各執行 C / C++ 基準及 split/leaf 候選四路，共八路得到相同結果。本輪仍是單一別名對照，不是與前幾批合併移除。未修改原 BIN 或正式來源，未接設備；僅發布報告。重跑入口：`experiments/v4160-aggregate-no-ident-next/verify.py --full`，沿用 baseline 與 llvm-objcopy 參數。下一步把已驗證的六個別名合併，檢查共同輸入物件及連結輸出。
