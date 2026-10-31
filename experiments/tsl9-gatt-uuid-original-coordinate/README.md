# GATT UUID 原位址診斷試驗

[English](readme.en.md)

本試驗使用既有 `write_UUID.c`，以 C11／C++17 分別編譯 `FFF1` 的兩-byte 候選資料，並接到既有 APP 可重定位元件與原位址診斷配置。它核對原有 73,538 bytes、全部 owner／relocation 及六個真實未解析 provider；新增資料僅位於 `0x1AB44..0x1AB46`，診斷配置合計 73,540 bytes。這不是正式 `src/` manifest 整合或完整 GATT 表。

```sh
python experiments/tsl9-gatt-uuid-original-coordinate/verify.py --tool-dir /path/to/llvm/bin --output-dir /existing/parent/new-trial
```

輸出目錄必須不存在，依賴既有本機凍結物件及原始 BIN；程式只讀原 BIN 中允許的兩-byte UUID，不讀排除區。C／C++ 診斷 ELF 必須一致，entry 為 0 且無 `PT_LOAD`。以真正未解析輸入執行嚴格連結必須因同六個 provider 失敗；不產生 BIN、不執行 target，數值參考不是 ROM provider 或硬體相容證明。
