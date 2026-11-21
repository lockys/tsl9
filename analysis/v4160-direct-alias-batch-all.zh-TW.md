# v4.1.60：全圖診斷連結不再需要 72 個具名別名

接續[18 個別名的批次驗證](v4160-direct-alias-batch-eighteen.zh-TW.md)，在 16 個暫存 ET_REL 副本改寫 83 筆重定位的符號引用，讓它們直接指向各自的具名定義。這次全圖連結不提供原有的 72 個具名別名；最終符號表也檢查沒有任何已移除的別名定義。全部 6,364 個配置區段的內容與位址等同基準，覆蓋的 76,800 bytes 逐位元組等於原 BIN。C／C++ 基準與 split/leaf 候選在一般 Python 及 `-O` 下共八路通過。

兩個負對照：只刪別名不改引用時，未定義符號集合為 72 個別名加 resident；改為直接引用但不提供 resident 數值見證時，唯一未定義符號是 `tsl9_boot_resident_40000`。成功的診斷連結仍將它標為 `SHN_ABS`、值 `0x40000`，不是輸入物件中的 resident 實作。GP 設定與四個取自 BIN 的資料位元組亦保留。

原 BIN 與正式來源未改。本提交僅發布報告；本機驗證入口為 `experiments/v4160-aggregate-no-ident-next/verify.py --full`，沿用 baseline 與 llvm-objcopy 參數。這不是獨立建置、來源整合、可刷寫或設備證據。下一步將 `0x18730` 的 resident 呼叫與可能的來源分開稽核，不把參考 ROM 當作設備上的實際版本。
