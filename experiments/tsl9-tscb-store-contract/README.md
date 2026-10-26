# tsCB 的 CPU 寫入合約

[English](readme.en.md) · [BLE 啟動 C/C++](../tsl9-resident-ble-initialization/README.md)

本輪核對既有 C/C++ callback `0x197F0..0x1995C` 與其相依函式的**編碼 CPU 寫入**。沒有新增或重編譯 target code，也沒有執行韌體、HOST 模型或 ISA 模擬。

14 個完整函式共 1072 bytes／390 條指令。原 BIN bytes、既有四組 C/C++ 來源／八個實際物件及兩個獨立 ELF reader 已核對。[驗證收據](verification-v1.json)逐項記錄 79 處 store；[檢查器](verify-v1.py)只做定義鏈、常數位址與堆疊位移分析，不模擬記憶體或硬體。

| store 類型 | 指令位置數 | 已確認範圍／條件 |
| --- | ---: | --- |
| 區域堆疊 | 27 | 各函式配置的 frame 內 |
| 數值 MMIO | 33 | 17 個明列周邊 word 位址；物理映射未確認 |
| 清零 word | 4 | 此呼叫長度32、值0、有效且16-byte對齊的堆疊；兩輪各16 bytes |
| byte-tail | 15 | 在上述特化條件下不會到達；不是一般 fill 函式的完整語意證明 |

callback 自身 frame 為128 bytes，加上最深直接 callee 的配置後，**局部配置深度為144 bytes**。這是針對完整選定呼叫鏈、正常返回與明列記憶體條件的靜態界限；不是整機 stack budget、IRQ 巢狀上限，也不是實體 RAM 容量證明。

## 證明的界線

此證據把 CPU store 目的限縮到區域堆疊／清零區與17個數值 MMIO word 位址。若要排除對 SDK 設定或 APP heap 的影響，仍必須證明入站堆疊位置、有效且不回繞的記憶體、區間不重疊，以及硬體沒有相關 alias。

**仍未證明 `staCB` 在 heap 呼叫時為零。** IRQ、DMA、周邊非同步效果、暫存器讀寫副作用、輪詢終止、實機 ROM／ISA 與 OTA 都不由這份 CPU store 合約保證。數值 MMIO 位址符合候選程式，不代表已辨識實體晶片。

[既有 C/C++ callback](../../src/native/startup/resident_startup.c) · [周邊 helper](../../src/native/startup/peripheral_primitives.c) · [RCC helper](../../src/native/irq/irq_initializer.c) · [fill](../../src/native/receive/fill_provider.c) · [摘要](summary.json)

## 重跑

需先備妥 [spec-v1.json](spec-v1.json)列出的原 BIN、來源與既有 curation 物件／收據；不會自動下載或重編譯。從專案根目錄執行：

```sh
python experiments/tsl9-tscb-store-contract/verify-v1.py
```

APP 正式 byte 覆蓋仍為 **95.54%**，本輪新增重建 bytes 為0。候選新功能是 callback 階段與等待狀態診斷；尚未實作，需先確認安全讀取語意及 IRQ／堆疊預算。沒有新增 BIN 或實機操作。
