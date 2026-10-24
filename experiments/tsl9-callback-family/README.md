# 回呼表原生重建

[English](readme.en.md)

範圍為原廠 V4.1.60 的 `901A–9124`，266B／102 條指令、20 個架構基本區塊。C11／C++17 均核對完整原位址編碼；244 個非控制 bytes 與 8 個具型別分支保留。`9070` 是共用迴圈，建立 frame 的入口為 `901A`、`907A`、`90B0`。

保留四個間接呼叫、一個 `t1` 間接尾跳、原始 16B frame 與共用出口。這些 C 函式是架構區塊，依原順序相鄰，並非可獨立呼叫的一般 C API。AUIPC 須依原始 PC 解讀；ET_REL VMA0 不是最終配置或可燒錄 BIN。

```sh
python3 experiments/tsl9-callback-family/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-callback-family/build/trial-v1
```

LLVM_BIN 由使用者指定現有 LLVM 工具目錄。只讀取既有物件與收據；不執行 RV32、HOST model、硬體或網路操作。裝置 ROM、完整 ABI／啟動／中斷及 BLE OTA 相容性仍未證明。
