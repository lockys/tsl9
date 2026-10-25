# 離線索引來源檢查

[English](readme.en.md) · [分析證據](../../analysis/lookup-index-2026-10-25/README.md)

從專案根目錄執行（Python3.10+，只用標準函式庫；Windows已測試）：

```sh
python3 experiments/tsl9-lookup-index/audit-v1.py
python3 experiments/tsl9-lookup-index/audit-v1.py --full
```

Windows可用 `py -3` 取代 `python3`。工具需要 `spec-v1.json`／證據所引用的既有本機量測元件、診斷ELF與來源規格；不會下載或建立它們。重建流程與範圍見[上一輪整合](../../analysis/record-copy-integration-2026-10-25/README.md)。

預設回報摘要；`--full` 另列出GP位址、局部寫入者、未閉合外逸與序列來源。它只讀檔案，不寫入證據、不執行韌體或模型，也不接觸硬體或網路。不宣稱全域索引界限或OTA相容性已證明。
