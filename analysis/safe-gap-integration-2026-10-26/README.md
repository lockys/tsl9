# 剩餘 CODE 的正式來源整合

[English](readme.en.md)

十個候選本體已加入 [`src/native/runtime/safe_gap_functions.c`](../../src/native/runtime/safe_gap_functions.c)，新增 **764B／288 條指令**。原有 158 個 C/H 檔、248 項 CODE 結果及 1,489 筆產物紀錄均未變更。

| 驗證範圍 | 實際結果 |
|---|---|
| 完整來源 | 159 個 C/H 檔；125 CODE＋8 DATA 單元；266 組比較／532 個物件 |
| 原始位址 | 69,412B CODE＋3,962B DATA＝73,374／76,800B，**95.54% 位元組覆蓋率** |
| 實際提供者 | 6,182 個正長度 FUNC、56 個 DATA OBJECT、71 個 CODE alias、6 個 DATA label |
| 參考與流程 | 5,270 個 relocation 角色；23,602 條指令、4,619 個直接轉移、1,432 個正常回傳位置；13 個有守衛的分派表 |
| 原生物件／ELF | C11 與 C++17 結果一致；獨立 ELF 解析器核對通過；無 ABS FUNC、entry=0、無 PT_LOAD |

數值與來源雜湊見 [摘要](summary.json)、[證據](evidence.json)。本輪新增 17 個編譯相依全數綁定至既有正長度函式；六個原有 UND 仍明示，另有不在 UND 數量內的未定界靜態資料依賴。

新本體內含三個 ROM 間接呼叫、四個間接尾呼叫；完整流程紀錄的 922 個間接轉移**包含 RET**，不能當作全部都未知的呼叫。一般順序與回傳位置沒有缺口，不代表完整執行期 CFG 或可達性已證明。新候選的實機呼叫來源仍未證。

**這是位元組重建證據，不是功能完成率或可刷入比例。** 原硬體、ROM／RAM／IRQ、啟動、OTA 與重啟後功能仍未驗證。本輪沒有產生 BIN、執行目標／模擬器、連接硬體或呼叫供應商服務。剩餘條件見 [相依契約](provider-contracts.json)；兩個值得嘗試的離線工具構想見 [功能候選](feature-candidates.json)，尚未實作。

## 本機唯讀重播

需要已固定雜湊的本機 LLVM 工具與前置原生輸出；`LLVM_BIN` 設為工具目錄。本收據使用 Windows／Android NDK 27.1／LLVM 18，其他作業系統未驗證。以下不產生韌體：

```sh
python3 scripts/verify-curated-source.py --replay build/curated-source/safe-gap-20261026-v1/verification.json
python3 experiments/tsl9-safe-gap-functions/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-safe-gap-functions/build/component-v1
python3 experiments/tsl9-original-layout/build-v65.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-layout/build/safe-gap-v2
python3 experiments/tsl9-original-layout/verify-flow-v65.py --replay experiments/tsl9-original-layout/build/safe-gap-flow-v1
```

Windows 可用 `py -3` 取代 `python3`。原生輸出與完整本機收據不隨本輪文字提交上傳；沒有前置輸出的新 clone 不能直接重播。
