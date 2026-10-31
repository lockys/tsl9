# CH32V208 時鐘啟動：原始指令對照

[English](readme.en.md)

以原 ID2966 V4.1.60 的 `0x1874A..0x18834` 為對象。既有[完整 clock 核對](../tsl9-clock-reset-noninterference/README.md)記錄這 234 bytes 與原位址 C11／C++17 診斷 ELF 相同；本頁依 [WCH 官方標頭](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/inc/ch32v20x.h)辨識位元，不讀取實機暫存器。

| 原始位置 | 指令觀察與官方定義的對照 |
| --- | --- |
| `0x1874A..0x1875A` | 對 `0x40021000` bit 0 設 1；依 WCH 定義對應 `RCC_CTLR.HSION`。 |
| `0x18794..0x187B4` | 對同位址設 `0x10000`，再輪詢 `0x20000`；分別對應 `HSEON` 與 `HSERDY`。計數器從 0 起至 `0x1000` 可停止輪詢，之後仍重讀狀態。 |
| `0x187BC..0x187CE` | 重新檢查 ready bit；若未設，經 `0x18830` 返回路徑，不執行下述 PLL 設定。 |
| `0x187FC..0x1880C` | 設 `0x01000000`，再輪詢 `0x02000000`；對應 `PLLON`／`PLLRDY`。該迴圈沒有觀察到本地 timeout。 |
| `0x18810..0x18828` | 將 `0x40021004` 低兩位設定為 2，然後等 `(值 & 0x0C)==8`；對應選擇 PLL 與等待 `SWS_PLL`。該迴圈沒有觀察到本地 timeout。 |

正常 HSE ready 路徑會進入 PLL 設定與等待；首次等待結束後重新讀取 ready，所以不能把「計數器到上限」簡化為必然失敗。PLL ready／切換狀態輪詢可能持續，能否正常退出取決於實際硬體；靜態指令不證明啟動成功、實際時鐘頻率、GPIO 接線或 IRQ 行為。官方 D8W 預設 HSE 常數為 32 MHz，但這是 SDK 設定，不是實測頻率。

照片中的晶片印字支持 CH32V208GBU6；記憶體映射、選項位元、ROM、時鐘與實際電路仍須另行驗證。沒有執行目標或連接硬體。
