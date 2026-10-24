# 原始19BF0搬移函式已重建並接入

[English](readme.en.md)

[目前 C/C++ 原始碼](../../src/native/receive/memory_transfer.c)已重建官方 `0x19BF0–0x19CA6` 的完整 **182B／54 指令**，包含第一個 return 後的所有路徑。15 個私有區塊、10 筆內部控制 relocation 在 C11／C++17 全部核對通過，沒有外部呼叫。主元件已用真實函式綁定原 `tsl9_callback_flow_external_19bf0`，UND **95 → 94**，沒有新增依賴。

已確認的指令行為：依對齊條件向前逐 byte／word 搬移，並有每輪 36B 的批次路徑。批次先載入八個 word、寫出第一個 word，再載入第九個 word並完成其餘寫入；保留原始指標更新順序、A0 不變與 scratch 暫存器。共 12 個 static load／12 個 static store 位置，沒有新增 stack frame。這些是原始指令與編譯物件證據，不是實際執行記錄，也不宣稱一般 `memcpy` ABI、重疊或 buffer 邊界安全。

原呼叫端 `0x129B0` 將 `0x19CA8` 的 96B 常數搬到 SP，之後在 `0x129BA` 呼叫 `0x128FE`；設定欄位及面向使用者的功能仍未確認。[原呼叫證據](../callback-flow-2026-10-24/evidence.json)

| 目前主元件 | 結果 |
| --- | --- |
| Code／data | 14,046B／674B；1,211 個具大小 code 區塊、71 個保留 alias |
| 原生部分連結 | 940 筆 relocation、94 個真實 UND；沒有 ABS 函式提供者或 stub |
| 原址配置 | 全部 **14,720B** 經原生連結器配置後逐 byte 與官方 BIN 相同 |
| 逐指令控制位置 | 4,886 指令／815 直接轉移；4,497 一般後續位置與286個可能的呼叫返回位置均有指令 |
| 仍未知 | 215 個暫存器間接轉移、10 個 MRET、`0x8034` EBREAK 的處理與恢復位置 |
| 來源整理 | 99 C/H、72 code units＋1 data unit；合計146組比對／292物件 |

原址產物仍是**入口 0、PT_NULL only、沒有 PT_LOAD 的診斷 ET_EXEC**，不是 OTA BIN。94 個 hidden／local／NOTYPE ABS 常數只記錄未知提供者的原始參照位址，不代表函式實作。完整76,800B映像、實體 MCU、resident、ABI、啟動／RAM／IRQ 與 OTA 尚未證明。

[摘要](summary.json) · [靜態證據](evidence.json) · [來源證明](../../experiments/tsl9-memory-transfer/build/source-proof-v1.json) · [主元件收據](../../experiments/tsl9-memory-transfer/build/component-v1/measurement.json) · [原址收據](../../experiments/tsl9-original-layout/build/memory-transfer-v2/measurement.json) · [尚缺94個提供者](next-providers.json)

在專案根目錄，用已安裝且符合 pin 的 LLVM 重查：

```sh
python3 experiments/tsl9-memory-transfer/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-memory-transfer/build/component-v1
python3 experiments/tsl9-original-layout/build-v5.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-layout/build/memory-transfer-v2
python3 experiments/tsl9-original-layout/verify-flow-v4.py --replay experiments/tsl9-original-layout/build/memory-transfer-flow-v2
```

下一步為完整 clock `18834`、fields `1973C` 與 IRQ `9A42` 的精確重建，既有不精確候選仍未綁定。可擴充方向是離線96B事件模板差異檢視與唯讀延後事件診斷；兩者仍是候選，沒有加入新的車輛控制功能。

本輪只有離線編譯與靜態核對；未執行目標／HOST模型／ISA模擬、未接觸硬體／網路、未產生 BIN，也未 commit／push。歷史個資問題仍未清除。舊階段的文件、原址診斷與來源收據保持原樣；其當時的95 UND計數屬歷史快照。
