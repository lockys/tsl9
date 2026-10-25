# 紀錄處理輔助函式與回呼

[English](readme.en.md)

新增 12 個完整入口：1,564B／539 指令、163 個私有程式區塊、129 個直接轉移與九組型別化位址參照。包含分開保留的 `0xCD4E`／`0xCD58` 與 `0xF414`／`0xF468`。

- C11／C++17 均通過原始編碼比對。147 個 C/H 檔、242 組來源比較／484 個物件；保留前 238 組結果與 1,429 筆產物紀錄。
- 接上 10 個舊相依，新增兩個未提供資料位址，剩 58 個真實未解析符號。保留全部 16 個既有唯讀區段。
- 主元件 58,522B code＋2,647B data／4,233 重定位。原位址 61,169／76,800B＝79.65% 位元組吻合，合併成 63 個僅相鄰範圍；診斷 ELF 沒有 PT_LOAD 或可執行入口。
- `0xCD58` 寫入狀態偏移 7／8；欄位的實體用途仍未知。`0xF468` 是實際回呼函式；參照它的排程路徑含原始數值 5000，時間單位尚未證實。
- `0x12AD0` 保留 128B 堆疊框架及 94／106 的長度參數。兩個靜態來源與被呼叫函式的完整語意仍需確認，未新增其資料內容。

覆蓋率不是功能完成率。原機 ROM、私有 ABI、晶片／RAM／IRQ、OTA 與實車行為均未通過完整驗證。本輪沒有目標／HOST／ISA 執行、硬體操作、後端連線或新 BIN。

[來源](../../src/native/receive/record_field_helpers.c) · [原始指令](evidence.json) · [契約與限制](provider-contracts.json) · [驗證摘要](summary.json) · [下一步](next-providers.json) · [功能提案](feature-candidates.json)

需既定 LLVM 工具與本機測量收據；`LLVM_BIN` 指向工具目錄：

```sh
python3 experiments/tsl9-record-field-helpers/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-field-helpers/build/native-v1
python3 experiments/tsl9-original-layout/build-v53.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-layout/build/record-field-helpers-v1
python3 experiments/tsl9-original-layout/verify-flow-v53.py --replay experiments/tsl9-original-layout/build/record-field-helpers-flow-v1
```
