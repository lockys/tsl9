# 原始IRQ初始化與RCC helpers已接入

[English](readme.en.md)

[目前 C/C++ 原始碼](../../src/native/irq/irq_initializer.c)完整重建 `9A42–9AD2` 初始化 **144B／46指令**，並接上四個各30B的RCC helper（`19124／19142／19160／1917E`）。合計 **264B／94指令、19個私有區塊、10筆控制relocation**，C11／C++17原址編碼全部吻合，沒有外部依賴。主元件UND **92 → 91**。

保留原16B frame，依原順序保存S2／RA／S0／S1，執行CSR `0x800` 的mask `0x88` clear／set、六次真實helper呼叫、六筆byte／word MMIO寫入，再按原順序還原暫存器與SP。這是原指令順序；沒有宣稱CSR的實體用途、先前狀態還原或非同步IRQ等價。

| 目前主元件 | 結果 |
| --- | --- |
| Code／data | 14,524B／674B；1,246個具大小code區塊、71個保留alias |
| 原生部分連結 | 961 relocation／91真實UND；沒有ABS函式提供者或stub |
| 原始位址 | 全部 **15,198B** 經實際連結器配置後逐byte與官方BIN相同 |
| 控制位置 | 5,049指令／836直接轉移；4,645一般後續位置、292個可能呼叫返回位置均有指令 |
| 尚未證明 | 226個暫存器間接轉移、10個MRET、8034 EBREAK恢復行為 |
| 來源整理 | 101 C/H、74 code units＋1 data unit；合計150組比對／300物件 |

原廠reset的 `18710–18720` 指令以基址 `0x8038` 組出 `0x803B` 並寫入MTVEC。該資料表slot45／36／39的原始指標分別是 `979E／12C24／16FB6`，最新診斷ELF的三筆typed vector reference也指向真實已重建code。初始化的priority-style位移45／36／39與單bit位置13／4／7具有數值對應；實體控制器的bank／index定義與周邊身分仍未確認。

舊 `interrupt_registers.c` 的180B初始化候選保持不變，沒有接入目前主元件。新原址產物仍是**入口0、PT_NULL only、沒有PT_LOAD的診斷ET_EXEC**，不是OTA BIN。91個hidden／local／NOTYPE ABS常數只保留未知提供者參照位址，沒有函式本體。

[摘要與完整操作順序](summary.json) · [靜態原碼證據](evidence.json) · [來源證明](../../experiments/tsl9-irq-initializer/build/source-proof-v1.json) · [主元件收據](../../experiments/tsl9-irq-initializer/build/component-v1/measurement.json) · [原址收據](../../experiments/tsl9-original-layout/build/irq-initializer-v1/measurement.json) · [仍缺91個提供者](next-providers.json)

在專案根目錄，用已安裝且符合pin的LLVM重查：

```sh
python3 experiments/tsl9-irq-initializer/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-irq-initializer/build/component-v1
python3 experiments/tsl9-original-layout/build-v7.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-layout/build/irq-initializer-v1
python3 experiments/tsl9-original-layout/verify-flow-v6.py --replay experiments/tsl9-original-layout/build/irq-initializer-flow-v1
```

下一步追查共用 `181C4` 及其實際依賴。新增的離線IRQ設定對照已保存CSR／呼叫／寫入與向量資料；唯讀實機中斷診斷仍是候選，沒有加入新裝置功能。

完整76,800B映像、實體MCU／控制器、resident、RAM／私有ABI、非同步IRQ及OTA仍未證明。本輪未執行目標／HOST模型／ISA模擬，未接觸硬體／網路、未產生BIN、未commit／push。歷史個資問題尚未清除；舊階段收據維持原樣。
