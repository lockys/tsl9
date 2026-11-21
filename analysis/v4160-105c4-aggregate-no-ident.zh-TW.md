# v4.1.60：以單一編譯旗標隔離 0x105c4 符號表差異

接續 [TX 診斷重跑](v4160-tx-direct-diagnostic-replay.zh-TW.md)，這輪不改 TX 或正式韌體來源。先將既有 140 輸入基準依原順序重連結，並重播 72 個別名；C/C++ 兩路的基準和別名輸出均逐檔與保存的基準相同。再以 split + leaf 的 141 輸入重連結，只對 leaf `0x105c4` 比較有無 `-fno-ident`，所有新建物件均在暫存目錄。

| C/C++，別名前與別名後 | 預設 leaf | leaf 加 `-fno-ident` |
|---|---:|---:|
| 候選多出的符號投影 | `.comment` `$d` + ABS `$d` | 僅 ABS `$d` |
| 目標 12 bytes、其他配置區段投影、relocation 及 relocation header 投影 | 與基準相同 | 與基準相同 |
| 聚合 `.llvm_addrsig` 長度，基準／候選 | 10,595／10,594 | 10,595／10,594 |
| 聚合 `.llvm_addrsig` `sh_link` | 0，身分未解析 | 0，身分未解析 |

普通與 Python `-O` 各完成八個對照輸出。候選旗標前後的聚合 raw stream 只有 offset 5,456 的 byte 從 `05` 變 `04`；leaf 輸入的有效符號表所解出的單一身分一致。這不表示聚合輸出中的 ordinal 可用，也沒有讓基準和候選 raw stream 相等。

本機重跑腳本：`experiments/v4160-aggregate-no-ident-next/verify.py --baseline <saved baseline>`。本次只發布報告，未改正式比較規則。下一步獨立核對仍殘留的 ABS `$d`，確認能否去除而不改 RISC-V attributes、配置區段或重定位；addrsig 身分問題另處理。這是離線 ET_REL 診斷，不是完整韌體、ABI 或可刷映像驗證。
