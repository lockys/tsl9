# 剩餘紀錄分派與輔助入口

[English](readme.en.md)

新增 38 個完整入口區間：6,022B／1,926 指令、568 個私有程式區塊、462 個直接轉移與十九組位址參照。補上 B730／BD88 等大型分派及其回呼／輔助鏈。

- C11／C++17 原始編碼比對通過；148 個 C/H 檔、244 組來源比較／488 個物件。保留前 240 組結果與 1,441 筆產物紀錄。
- 兩個獨立解析器對實際 1,043 個 ELF 區段、1,214 個符號及 500 個重定位逐欄一致。舊解析器保留，新版只提高區段上限及修改說明。
- 首輪發現兩個 RAM 位址 ADDI 被壓縮；保留原 32-bit 寬度後的 native-v2 通過。失敗 native-v1 保留，不覆寫。
- 接上 29 個舊相依，展開五個資料位址，剩 34 個未解析符號：32 個資料位址，以及排除的 0x14056／0x40000 入口。未知間接 ROM 實作不包含在這個符號數內。
- 整合元件 64,544B code＋2,647B data／4,733 重定位。原位址 67,191／76,800B＝87.49% 吻合，40 個僅相鄰範圍；ELF 沒有 PT_LOAD 或可執行入口。

0x19BF0..0x19CA6 是先前已重建的軟體記憶體複製函式；第一個 12B 區塊不是完整函式，也不是 ROM 跳板。資料來源界限與實際硬體記憶體仍需逐項確認。

這是位元組覆蓋率，並非功能完成率。私有 ABI、原機晶片／ROM／RAM／IRQ／OTA 與實車行為尚未通過完整驗證。本輪沒有目標／HOST／ISA 執行、硬體操作、後端連線或新 BIN。

[來源](../../src/native/receive/remaining_record_dispatch.c) · [原始指令](evidence.json) · [契約與限制](provider-contracts.json) · [驗證摘要](summary.json) · [下一步](next-providers.json) · [功能提案](feature-candidates.json)

需既定 LLVM 工具及本機測量收據；`LLVM_BIN` 指向工具目錄：

```sh
python3 experiments/tsl9-remaining-record-dispatch/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-remaining-record-dispatch/build/native-v2
python3 experiments/tsl9-original-layout/build-v54.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-layout/build/remaining-record-dispatch-v1
python3 experiments/tsl9-original-layout/verify-flow-v54.py --replay experiments/tsl9-original-layout/build/remaining-record-dispatch-flow-v1
```
