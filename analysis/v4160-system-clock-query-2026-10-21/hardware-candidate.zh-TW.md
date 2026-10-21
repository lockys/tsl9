# WCH CH32V20x候選

記錄日期2026-10-21。使用者提供「TSL6使用WCH CH32V20x RISC-V」線索，要求納入TSL9參考。[TSL6參考專案](https://github.com/jfryton/TSL6-Firmware)也如此描述TSL6；這支持系列假說，尚未辨識TSL9板子或確切料號。

| 證據 | 觀察與限制 |
| --- | --- |
| 原始ID2966 V4.1.60，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667` | `18838`讀取`40021004`；`1889E`讀取`40023800`。這是靜態數值觀察。 |
| [WCH官方CH32V20x標頭](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/inc/ch32v20x.h) | RCC／CFGR0與EXTEN位址符合上述觀察；共用暫存器配置不能唯一辨識晶片。 |
| [官方CH32V208資料](https://www.wch-ic.com/products/CH32V208.html) | 無線功能及64KB SRAM選項，使其成為值得比對的子系列；封裝及組態仍未知。 |
| 目前reset／entry資料流 | GP數值`20004000`與SP數值`20010000`符合64KB SRAM假說，但未量測實體RAM。 |

後續持續將啟動、時脈、中斷與resident介面對照確切來源，保留變體差異。此參考不補完resident UND，也不證明接腳、原機ROM ABI或BLE OTA相容性。目前無法讀取晶片印字，繼續離線工作不需要重複索取或存取硬體。
