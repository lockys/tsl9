# 七筆事件 word 資料正式整合

[English](readme.en.md) · [專案](../../README.md) · [C/C++ 來源](../../src/native/receive/event_word_table_data.c)

`0x1AAE8..0x1AB04` 的 **28 bytes** 已納入 `src/`、manifest 與原位址診斷連結。C11／C++17 診斷 ELF 完全一致，**73,538／76,800 bytes（95.75%）** 與原廠 APP 原位址逐 byte 相同：69,412B CODE＋4,126B DATA。這是靜態位元組覆蓋率，不是功能完成率或刷寫成功率。

| 項目 | 實際證據 |
| --- | --- |
| 來源 | 164 個 C/H；125 個 CODE、13 個 DATA 單元 |
| 編譯證據 | 保留父 548 物件與 2,240 個父輸入；新增 origin／src C11／C++17 四物件；合計 276 組比較／552 物件，未宣稱重編全部 |
| 原位址 | 6,182 個 CODE owner、64 個 DATA OBJECT、40 個相鄰區段；5,270 個重定位角色完整保留 |
| 仍缺 | 3,262B：刻意排除 3,128B＋其他未選 134B；六個 APP source provider 未解析 |

## 使用條件與語義

[完整 consumer 合約](../tsl9-event-word-table-data/README.md)核對 `0x176F8..0x1787C` 的 388B／135 指令、48-byte frame。讀取 `0x17844` 使用 `0x1AAE8 + 4*uint8(GP+370)`；只有索引在讀取時為 0～6，這七筆 DATA 才涵蓋該次讀取。

`(舊索引+1)%7` 的寫回發生在讀取後，不能證明第一次讀取的值域。196 個 GP 地址取得，以及 alias、間接寫入、排除 CODE、IRQ／DMA、初始化與一致性仍未封閉。沒有加入 clamp，也沒有把七筆條件 backing 宣告成已證明的完整表格大小。

表格低三個 bytes 寫入記錄 offsets 2／3／4。原始完整 `LW(SP+12)` 保留；其 factor 選取 SP+14 bits 2～6 後加一，值為 1～32，原始 A2 參數為 `800*factor`。時間單位、實體槽 `0x40058` 的身分及效果未證。七筆低24-bit值像配色序列，這是推論，**未確認 RGB 通道、燈光硬體或產品功能**。

所有既有 CODE／DATA owner 的內容與座標、六個 import、六個 DATA label 及 CODE continuation 觀察均保留，包括 `0x8034→0x8038` 啟動邊界。沒有補零、padding、stub 或完整 provider alias。只選取 28B，未讀保守 1,024B 包絡或排除 payload。

## 重播與 readiness

具備凍結的本機父產物及 LLVM 時，在 repo 根目錄執行：

```sh
python3 experiments/tsl9-event-word-table-integration/audit-v1.py --tool-dir "$LLVM_BIN"
python3 experiments/tsl9-event-word-table-integration/check-readiness-v1.py --tool-dir "$LLVM_BIN"
```

第二項目前回傳 **exit 2**：證據核對成功，但八項門檻只有來源／原生證據成立。exit 1 代表證據漂移或檢查失敗。APP 完整性、provider、可載入產物、原機 ROM／ABI、啟動／IRQ、RAM、Flash／OTA 與重建後功能仍未就緒或未證。

診斷 ELF 為 entry 0、PT_LOAD 0，**不是可刷寫 BIN**。這輪沒有 target、HOST model、ISA、硬體或第三方 API 執行。來源擴充前重播了父來源與實驗證據；擴充後保留其固定輸入與精確重建的歷史 manifest，沒有宣稱重跑不相容的舊快照。

[摘要](summary.json) · [完整收據](audit-result-v1.json) · [readiness 收據](readiness-v1.json) · [來源擴充](source-extension-v1.json) · [離線功能構想](feature-candidates.json)
