# 紀錄欄位更新與通知路徑

[English](readme.en.md)

重建 19 個原始入口：3,682B／1,149 指令，另提供四段合計 51B 的有界資料視窗。C11 與 C++17 的原位址編碼均與原廠相同。入口包含兩個不同的短回呼；兩者仍跳到尚未重建的 `0xA476`。

- 完整來源證明：146 個 C/H 檔、240 組比較／480 個物件；保留前 236 組結果及 1,417 筆產物紀錄。
- 整合元件：56,958B code＋2,647B data、4,086 個重定位；提供 17 個舊相依，展開 12 個新相依，剩 66 個未解析符號。
- 原位址連結：59,605／76,800B＝77.61%，73 個僅合併相鄰範圍。沒有 PT_LOAD、沒有可執行入口、沒有 ABS FUNC。
- `0xD14A` 比較 record 的偏移 3／5／7／9；有差異才寫入 GP 偏移 232..235 並尾呼叫 `0x13C4E`。實體欄位與通知用途尚未證明。
- `0xC97E` 與 `0xCC20` 的 AND 15 限定三段 16B 的查找視窗。`0xD2CC` 的三位元組來源及 ROM 槽位呼叫仍需原機實作證明。三張較大表未確認索引範圍，因此保留為相依，未擅自補資料。

這是靜態位元組覆蓋率，不是功能完成率。ROM、私有 ABI、實際晶片／RAM／IRQ、藍牙 OTA 與實車行為仍未通過完整驗證；本輪未執行目標／HOST 模型／ISA、未連線硬體或後端、未產生 BIN。

[來源](../../src/native/receive/record_field_transitions.c) · [原始指令](evidence.json) · [欄位與範圍證據](provider-contracts.json) · [驗證摘要](summary.json) · [下一步](next-providers.json) · [新功能提案](feature-candidates.json)

重播方式（需既定 LLVM 與本機測量收據，`LLVM_BIN` 指向工具目錄）：

```sh
python3 experiments/tsl9-record-field-transitions/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-field-transitions/build/native-v1
python3 experiments/tsl9-original-layout/build-v52.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-layout/build/record-field-transitions-v1
python3 experiments/tsl9-original-layout/verify-flow-v52.py --replay experiments/tsl9-original-layout/build/record-field-transitions-flow-v1
```
