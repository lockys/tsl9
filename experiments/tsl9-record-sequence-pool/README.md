# 唯讀資料池與內部標籤

[English](readme.en.md) · [證據與限制](../../analysis/record-sequence-pool-2026-10-25/README.md)

`src/record_sequence_pool.v1.c` 是89個uint16_t的唯讀C/C++資料池。三個零配置量的OBJECT標籤位於相同資料section的0／36／72偏移，與全域ABS假位址不同。

編譯使用既有鎖定雜湊的Windows LLVM工具，沒有下載或安裝。設定 `LLVM_BIN` 為工具目錄，在專案根目錄選擇新的輸出名稱：

```sh
python3 experiments/tsl9-record-sequence-pool/build-v1.py --tool-dir "$LLVM_BIN" --trial my-pool
python3 experiments/tsl9-record-sequence-pool/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-sequence-pool/build/my-pool
```

Windows可用 `py -3` 取代 `python3`，PowerShell使用 `$env:LLVM_BIN`。`--trial` 只建立新資料夾；`--replay` 只重新讀取與驗證。需要既有量測父元件與本機來源證據。C/C++物件與實驗連結不會被執行，也不會建立BIN或接觸硬體／網路。其他平台工具鏈尚未驗證。

本頁v1實驗本身未更動正式來源清單；後續已完成[來源與原位址整合](../../analysis/record-sequence-integration-2026-10-25/README.md)。原始宣告範圍、全域指標／上限界限與ROM／IRQ／OTA相容性仍未證明。
