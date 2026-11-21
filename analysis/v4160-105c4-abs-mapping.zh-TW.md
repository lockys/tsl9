# v4.1.60：隔離 0x105c4 剩餘的 ABS mapping symbol

延續 [`-fno-ident` 聚合對照](v4160-105c4-aggregate-no-ident.zh-TW.md)。C 與 C++ 各重建 140 輸入基準及 141 輸入 split/leaf 候選，包含套用 72 個別名之前和之後。對候選 leaf 的 `.riscv.attributes` 唯一 local `$d` 做兩種暫存對照，未變更正式來源或驗收。

| 對照（均有 `-fno-ident`） | 聚合符號投影相對基準 | 輸入 leaf 的 `.llvm_addrsig` |
|---|---|---|
| 不碰 attributes mapping | 多一筆 ABS `$d` | 符號表連結有效 |
| `llvm-objcopy --strip-symbol` 移除該 local mapping | 無差異 | `sh_link=0`，失去身分連結 |
| 只將該符號的 `st_name` 清零，保留符號表項目及索引 | 多一筆未命名 ABS 項目 | 仍有效，原單一身分不變 |

兩種操作都保留 leaf 的 RISC-V attributes bytes；聚合後 attributes、目標 12 bytes、其餘配置區段投影、重定位和重定位區段標頭投影均與基準一致。普通與 Python `-O` 各完成 16 組比較。聚合 addrsig 則一律 `sh_link=0`，原始資料長度仍為基準 10,595、候選 10,594 bytes；符號投影相等不等於 addrsig 等價。

結論：此 local mapping 確實可在保留 attributes 的情況下移除；但所測 objcopy 路徑會破壞 leaf 有效的 addrsig 連結，因此不採為正式修正。下一個驗證點是用剝除前的有效身分對照剝除後的符號表，確認是否需要重新編碼，而不是直接補 `sh_link` 或沿用舊 ordinal。這仍不能自行修好聚合端的無效連結。僅發佈報告；本機重跑：`experiments/v4160-aggregate-no-ident-next/verify.py --baseline <saved baseline> --objcopy <llvm-objcopy.exe>`。此為離線 ET_REL 診斷，未執行韌體、未連設備。
