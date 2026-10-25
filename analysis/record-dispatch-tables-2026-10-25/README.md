# 有界跳轉表與欄位查找資料

[English](readme.en.md)

新增五個真正的唯讀資料物件，合計 264B，未新增可執行程式。四個相對跳轉表含 64 個項目，指向 49 個不同的既有指令入口；八項查找表的索引為 unsigned byte >> 5，範圍 0–7。

- 原始／整理後版本的 C11／C++17 四個編譯物件均通過；128 個 ADD32/SUB32 關係及所有 DATA bytes 在原位址編碼後與官方一致。
- 149 個 C/H 檔；121 個程式單元保持不變，獨立資料單元增至兩個。共 246 組來源比較／492 個物件，保留前 242 組程式比較及 1,453 筆產物紀錄。
- 接上五個舊相依、沒有新相依，剩 29 個未解析符號。程式 64,544B 完全保留；資料增至 2,911B，重定位 4,861 個。
- 原位址 67,455／76,800B＝87.83% 吻合。靜態控制流驗證涵蓋 11 組有界表格；這四組新增 64 個表格項目及其實際目的。這些不是 64 項實體功能。

新增唯讀離線檢視器，可列出索引界限與編譯後分支目的。使用 Python 標準函式庫，本輪在 Windows 驗證；需要本機已產生的測量 ELF／收據，不執行韌體或連線硬體：

```sh
python3 experiments/tsl9-record-dispatch-tables/inspect-dispatch-tables.py --json --full
```

位元組覆蓋率不是功能完成率。原始宣告的物件長度、執行時索引、非同步 ABI、原機 ROM／RAM／IRQ／OTA 與實車行為仍未完全證明；診斷 ELF 沒有 PT_LOAD 或可執行入口。本輪沒有目標／HOST／ISA 執行、後端連線或新 BIN。

[來源](../../src/native/receive/record_dispatch_tables.c) · [原始資料與界限](evidence.json) · [契約](provider-contracts.json) · [摘要](summary.json) · [下一步](next-providers.json) · [已實作檢視功能](feature-candidates.json)

重播需既定 LLVM 與本機測量收據，`LLVM_BIN` 指向工具目錄：

```sh
python3 experiments/tsl9-record-dispatch-tables/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-dispatch-tables/build/data-v1
python3 experiments/tsl9-original-layout/build-v55.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-layout/build/record-dispatch-tables-v1
python3 experiments/tsl9-original-layout/verify-flow-v55.py --replay experiments/tsl9-original-layout/build/record-dispatch-tables-flow-v1
```
