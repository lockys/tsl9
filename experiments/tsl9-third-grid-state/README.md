# 第三張表索引的唯讀離線稽核

[English](readme.en.md) · [分析結果](../../analysis/third-grid-state-2026-10-25/README.md)

核對原廠指令、目前元件與五個直接設定呼叫者，區分已知初始化常數與尚未證明的全域界限。沒有提供資料、改動來源清單或產生 BIN。

```sh
python3 experiments/tsl9-third-grid-state/audit-v1.py
python3 experiments/tsl9-third-grid-state/audit-v1.py --full
```

需要既有的本機原位址 ELF 與已封存證據；不重新編譯、不執行目標、不呼叫網路。Windows 可用 `py -3` 取代 `python3`。
