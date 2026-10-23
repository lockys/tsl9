# Resident copy：SDK 候選的精確架構重建

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

新增 [copy.v1.c](src/copy.v1.c)，同份來源分別以 C11／C++17 編譯。六個 private regions 在條件式 RAM 位址 `0x20000332` 連結後，完整 **58 bytes／18 指令**與公開 WCH V1.31 SDK 候選的 `[0x405A2,0x405DC)` 相同。這不是已量測的 TSL9 resident，也未注入原 Runtime 或產生可燒錄 BIN。

- 只寫 A3／A4／A5／A6；保留 A0–A2、T0、A7、SP、GP、RA。舊 52B normal-I/O 投影仍保留，此版本消除額外 T0／A7 寫入。
- 即使指標／長度為零，也先讀取並暫存 `0x4002420C`，寫零，再執行 `FENCE.I`；不將它猜作特定周邊或關中斷。
- 順向即時讀一 byte，再計算目的位址、遞增索引、寫入目的。保留重疊、uint32 回繞及故障前綴的指令順序；故障不保證恢復暫存值。
- 正常出口 A4＝初次讀值、A5＝`0x40024000`；跳過複製時保留 A3／A6，實際複製後為最後目的位址／讀值。RET 目標為 `RA & ~1`。
- 物件有五筆真實 relocation；連結後無 UND／RELA／全域 ABS。ELF 的 RX LOAD 為 58B，另有 180B 唯讀 ELF headers；不是完整韌體。

以 `probe-v2.py` 建立全新輸出，再用 `verify-v3.py --folder <輸出目錄> --write` 產生 create-only 收據；省略 `--write` 為唯讀重播。工具鏈由使用者環境或 `--llvm-bin` 指定，不下載工具、不執行產物。v3 使用同一份 v2 編譯產物；v1／v2 checker 與收據原封保留。

正式檢查涵蓋原候選雜湊、所有位元組／LLVM 位址、六個強定義、五筆邊、C 的 SSA／volatile／實體暫存器 ports、完整輸入／產物／MD include closure、逐命令 argv／消耗位元組／日誌、ELF entry／LOAD／權限／對齊。每種語言 50 項有限負向控制通過；獨立檢查另拒絕 38／38 項來源與 PHDR 變異。這些是靜態檢查，沒有 HOST 行為模型、ISA 模擬、MMIO 或硬體操作。

[完整分析與公開證據](../../analysis/resident-copy-arch-2026-10-23/README.md)。仍缺裝置實際 `[0x4004C]`、resident 身分、完整 startup／IRQ／物理 ISA／MMIO 及 OTA 相容性證據。原傳送鏈 740B 的局部證明未因此成為完整閉合韌體。
