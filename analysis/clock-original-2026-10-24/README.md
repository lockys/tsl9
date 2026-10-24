# 完整時鐘查詢與欄位更新已重建

[English](readme.en.md)

[目前 C/C++ 原始碼](../../src/native/clock/clock_original.c)重建原始 `18834–188E2` 查詢 **174B／58 指令**與 `1973C–19764` 欄位更新 **40B／11 指令**。16 個私有區塊、11 筆內部控制 relocation 在 C11／C++17 全部核對通過，沒有外部呼叫。兩個真實入口已接入主元件，UND **94 → 92**，沒有新增依賴。

查詢保留每次原始周邊讀取、GP+64 的 byte 查表、GP+108 的 word 寫入與讀回，以及第一個 return 後的分支。A2 只在原外部來源路徑的 `188B6` 寫為 `0x00C00000`，沒有入口快照／還原。欄位更新保留 unsigned DIVU：GP+108 的 word 除以8,000,000後取低8 bits，寫 byte到GP+382，再乘1000並以 halfword寫入GP+380。這些是靜態指令事實，不是實際頻率量測。

| 目前證據 | 結果 |
| --- | --- |
| 新增原碼 | 214B／69指令；10個static load、4個static store；沒有新增 frame 或外部呼叫 |
| 主元件 | 14,260B code＋674B data；1,227個具大小code區塊、71個保留alias |
| 原生部分連結 | 951 relocation／92真實UND；沒有ABS函式提供者或stub |
| 原始位址 | 全部 **14,934B** 經實際連結器配置後逐byte與官方BIN相同 |
| 控制位置 | 4,955指令／826直接轉移；4,560一般後續位置、286個可能呼叫返回位置均有指令 |
| 仍未知 | 217個暫存器間接轉移、10個MRET，以及8034 EBREAK的處理與恢復位置 |
| 來源整理 | 100 C/H、73 code units＋1 data unit；合計148組比對／296物件 |

舊 `clock_query.c` 的196B候選與 `clock_fields.c` 的38B候選保持不變，沒有接入目前主元件；原始範圍分別為174B與40B。新原址產物仍是**入口0、PT_NULL only、沒有PT_LOAD的診斷ET_EXEC**，不是OTA BIN。92個hidden／local／NOTYPE ABS常數只保留未知提供者的參照位址，不代表函式本體。

[摘要](summary.json) · [原始靜態證據](evidence.json) · [來源證明](../../experiments/tsl9-clock-original/build/source-proof-v1.json) · [主元件收據](../../experiments/tsl9-clock-original/build/component-v1/measurement.json) · [原址收據](../../experiments/tsl9-original-layout/build/clock-original-v1/measurement.json) · [仍缺92個提供者](next-providers.json)

在專案根目錄，用已安裝且符合pin的LLVM重查：

```sh
python3 experiments/tsl9-clock-original/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-clock-original/build/component-v1
python3 experiments/tsl9-original-layout/build-v6.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-layout/build/clock-original-v1
python3 experiments/tsl9-original-layout/verify-flow-v5.py --replay experiments/tsl9-original-layout/build/clock-original-flow-v1
```

下一步為完整 `9A42` IRQ初始化；180B舊候選仍未綁定。可擴充方向是唯讀時鐘設定／計算值診斷，尚未實作裝置功能或加入傳輸介面。

完整76,800B映像、實體MCU／周邊、GP／table／RAM所有權、resident、私有ABI、IRQ與OTA相容性仍未證明。本輪未執行目標／HOST模型／ISA模擬，未接觸硬體／網路、未產生BIN、未commit／push。歷史個資問題仍未清除；舊階段收據及計數保持歷史原樣。
