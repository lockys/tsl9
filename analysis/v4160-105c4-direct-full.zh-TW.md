# v4.1.60：不經聚合的全 BIN 診斷連結

延續 [6,278 區段的直接連結](v4160-105c4-direct-selected.zh-TW.md)，在同一次最終 LLD 連結加入重新編譯的 85 個 dispatcher 物件（3,124 bytes），以及以原 BIN 取樣生成的 4-byte 資料物件。原有輸入仍逐件交給最終連結器，不以 `ld -r` 聚合物件為輸入。內部位置以區段與偏移表示；這類按地址建立的別名不等於證實來源符號直接綁定。

一般 Python 與 `-O` 各四路（C／C++ 基準及 split/leaf 候選）均通過：每路 6,364 區段、76,800 bytes，地址連續無重疊或空洞，逐段與原 BIN 一致，同語言的基準和候選輸出投影相同。以數值設定 GP 後，仍有 73 個未定義符號；提供 72 個既有別名後，嚴格連結只剩 `tsl9_boot_resident_40000`。提供該數值見證後才完成。輸出零 PT_LOAD。

這是依賴既有來源與不透明內容的位元組重現，不是獨立重建：4-byte 資料直接取自參考 BIN，resident 未提供，也未證實裝置上的 BOOT／ROM、ABI 或可刷性。聚合 `.llvm_addrsig` 未修正。下一步應盤點 resident 引用與 72 個別名的提供者，區分可用真實定義連結者與仍需外部環境者。原 BIN、正式來源未改；本次僅發布報告。

本機重跑：`experiments/v4160-aggregate-no-ident-next/verify.py --baseline <saved baseline> --objcopy <llvm-objcopy.exe> --full`。
