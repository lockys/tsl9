# 離線 resident 完整性稽核（獨立於 strict link）

```
python -B scripts/audit_sparse_resident_integrity.py --elf <診斷ELF> --reference-dir analysis/wch-resident-candidate-2026-10-21/carrier-dec2023
python -B -m unittest discover -s tests -p 'test_sparse_resident*.py' -v
```

工具固定 APP 候選雜湊，驗證固定 V1.31 HEX、固定 map 與全部 17 個分段的逐位址來源，再比對 ELF 的 resident 配置 bytes。因間接引用無法由連結器符號完整列舉，保守地要求 **全部已記錄 resident bytes**，並額外要求 seed `[0x40280,0x402b0)`、第一 copy `[0x402b0,0x430e4)`、第二 copy `[0x6eaa4,0x6eb30)` 的每一 byte。禁止重疊、越界 section，對缺來源、缺 ELF、不同 bytes、無來源的 ELF bytes 分別輸出半開區間；返回碼 0 僅代表此固定離線資料範圍通過，1 代表失敗。輸出包含 ELF、HEX 與各分段雜湊和路徑。

固定 HEX 缺 `[0x6eb2c,0x6eb30)`；即便 ELF 包含全部 17 段，此稽核仍必然失敗，不能用其他版本或填值補足。合成正例只測試比較邏輯，不改變正式來源固定值；入口四 bytes、缺末字、偽造來源及污染測試均須失敗。既有證據測試也檢查重算雜湊的污染與偽造 map。

範圍僅限該 APP／V1.31 參考模型；這不是通用控制流或動態 callback 完整性證明，也不證明原機安裝的 ROM、ABI、RAM ownership、可執行或可刷寫。未接觸硬體，不修改或放寬原產品 strict gate。參考 copy 路徑和其條件見 `analysis/v131-startup-source/README.md` 與 `analysis/resident-entry-reference-2026-10-21/source/inspect-source.py`。
