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

## 條件式頻率對照

`0x187EE` 以 `0xFFC0FFFF` 遮罩 `CFGR0`，`0x187F4..0x187FA` OR `0x00290000`；該數值由官方定義的 HSE 作為 PLL 來源 `0x00010000` 與 PLLMULL12 `0x00280000` 組成。此前 `0x18786` 的 `0xFF80FFFF` 遮罩會清除此組 PLL 欄位，兩次操作之間若無其他改寫，設定值與 [WCH 96 MHz 範例](https://github.com/openwch/ch32v20x/blob/main/C%2B%2B/Use%20MRS%20Create%20C%2B%2B%20project-example/CH32V203C8T6%2B%2B/User/system_ch32v20x.c)一致。

官方範例對 D8W／CH32V208 描述 `32 MHz / 4 × 12 = 96 MHz`。同一原始路徑先清除低 16 位設定，再於 `0x187E6` 設 `PPRE1_DIV2`；如果中間沒有其他寫入、HSE 確為 32 MHz 且 PLL ready 與系統時鐘切換成功，則按該官方範例推算 SYSCLK／HCLK 為 96 MHz、PCLK1 為 48 MHz、PCLK2 為 96 MHz。此為**條件式配置推論**，不是實測頻率，且不證明振盪器實際頻率、設定未被改寫或路徑完成。

## SPI1 初始化的條件式比對

原始 `0x1716C..0x1719A` 組合 stack 資料，以 `0x40013000` 與該資料呼叫 `0x196C4`；後者將前八個 halfword OR 入控制暫存器，再將第九個寫至 offset 16。以 [WCH SPI 結構與常數](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/inc/ch32v20x_spi.h)解讀，該組值對應 master、雙線全雙工、8-bit、CPOL 低、第一邊緣、軟體 NSS、MSB 優先及 **除以 8**；`0x1719A..0x171A0` 隨後請求設定 enable。這是指令與標頭的靜態對照，依初始化路徑、暫存器映射與內容不被改寫等條件成立。

若上一節 96 MHz PCLK2 條件也成立且 SPI1 實際使用此 APB2 時鐘，除以 8 對應 **12 MHz SCK**。實板有可讀為 MCP2515 的晶片；[Microchip 資料表](https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ProductDocuments/DataSheets/MCP2515-Family-Data-Sheet-DS20001801K.pdf)在其表列條件下規定 SPI 時鐘上限 10 MHz。這提示一項需釐清的條件式差異，不代表已量到 12 MHz、已確認 PCB 連接或實際違規／故障；時鐘路徑、後續重新設定及板上訊號均未驗證。不要以此單獨修改韌體或刷寫。

`0x171A0` 呼叫的 `0x1971E..0x1973C` 在非零參數路徑將控制暫存器 bit 6 設為 1，保留其餘 bits，包括分頻欄位。已比對的 `0x16896..0x168DE` 傳輸 helper 則只對 SPI 狀態／資料 offsets 8／12 執行輪詢及資料讀寫，沒有在這個函式本體中修改控制暫存器；兩個等待各以 255 起始的計數器界限退出，但此數字不能換算成已知時間。兩處 timeout 與正常收到 `0x00` 均回傳數值 0。這只縮小這兩個局部函式內的可能性，不能排除其他程式、間接呼叫或非同步路徑重新設定時鐘或 SPI。
