# CH32V208GBU6 候選硬體

[English](readme.en.md)

使用者提供的原廠 TSL9 板正面近照中，主晶片印字可辨為 **CH32V208** 與 **GBU6**；這是該照片所示板子的型號標記證據。後續以 **WCH CH32V208GBU6（QFN28）** 為離線分析依據；照片無法驗證晶片內部、其他批次、PCB 接線、ROM 或韌體相容性。

使用者先前提供的影片截圖標示「CH32V208GBU6 開發板」，並稱作品為「手搓 TSL9 代模塊」。原廠板新近照則提供了獨立的晶片印字證據；影片中的 CAN、SPI 及 MCP2515 接線表仍僅描述自製方案，不能直接套用原廠硬體。

[WCH 官方型號表](https://www.wch.cn/products/productsCenter/mcuInterface?categoryId=74)列有 CH32V208GBU6／QFN28。既有[原 APP 分析](../tsl9-original-APP-library-binding/README.md)發現程式比較 `CH32V20x_BLE_LIB_V1.3` 前綴，與此候選一致，但未證明實機 ROM 身分或完整 ABI。

既有 [CH32V208／D8W 實驗候選](../tsl9-ch32v208-candidate/README.md)仍是早期 V4.1.00 逐 byte 重建，不包含目前全部來源的整合成果。此次僅記錄候選，沒有修改程式、接腳設定或 BIN；六個未解析來源、原機 ROM／啟動／記憶體／IRQ 與 OTA 相容性仍待驗證。

## 記憶體配置的靜態比對

[WCH 評估板文件](https://www.wch.cn/uploads/file/20220627/1656323204206699.pdf)中的 CH32V208x 例子列出 Flash/RAM 128/64、144/48、160/32 KiB 三種配置，範例基址為 Flash `0x00000000` 與 RAM `0x20000000`。以該文件的連續映射及原 APP 位址不重映射為條件，已有[reset 查核](../tsl9-reset-state-bootstrap-contract/README.md)記錄的清零範圍 `[0x20004080,0x2000C958)` 超過 48 KiB RAM 頂端 2,392 bytes；已核對的[clock frame](../tsl9-clock-reset-noninterference/README.md)亦使用 `[0x2000FFF0,0x20010000)`。因此這兩項靜態存取均只落在三個例子的 64 KiB RAM 範圍內。這不代表已讀到實機選項或排除其他記憶體映射。

原 APP 假設的 `[0x8000,0x1AC00)`、76,800 bytes 在三個例子的 Flash 數值範圍內；這不證明該位置可寫、BOOT／ROM 佔用情況、OTA 支援或執行成功。官方不同版本資料對總 Flash 與零等待區的表述有差異，不將簡單位址相加視為已確認的實際配置。

## CAN 腳位的條件式對照

原始 ID2966 V4.1.60 的 `0x12DC0..0x12DE2` 34 bytes 與目前 C 重建診斷 ELF 的同位址 bytes 一致；原始 BIN 整檔 SHA-256 為 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。在 `0x12DCC` 與 `0x12DDE` 的呼叫分別傳入 `(0x40010800, 0x1000, 0x18)` 與 `(0x40010800, 0x0800, 0x48)`。依 [WCH 周邊定義](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/inc/ch32v20x.h)及 [GPIO 模式定義](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/inc/ch32v20x_gpio.h)，這些數值對應 GPIOA、pin 12／複用推挽，及 pin 11／上拉輸入。此解讀仍以 helper `0x9A24` 實際採用對應參數契約為條件。

[WCH CH32V208 資料手冊](https://atta.szlcsc.com/upload/public/pdf/source/20240411/5E05523CBB231C22A5C78C078317BD2C.pdf)的 QFN28 腳位表將 PA12／19 列為 CAN1_TX、PA11／18 列為 CAN1_RX，與使用者提供的自製方案截圖一致。這是晶片定義、呼叫參數與自製接線表的相符性，不證明原廠板上實際接線、重映射狀態、收發器或 CAN 訊框行為；不可據此單獨燒錄。

### GPIO helper 的指令證據

進一步比對原始 V4.1.60 與目前 C 診斷 ELF：`0x9A24..0x9A42` 的 30 bytes 和 `0x18F88..0x1904A` 的 194 bytes 均逐 byte 相同。`0x9A24` 將 a1 低 16 位存為 pin mask、將數值 3 存於設定結構的 speed 欄位位置，並將 a2 存為 mode 後呼叫 `0x18F88`。後者取 mode 的低四位，對輸出模式合併 speed，並依 mask 對 GPIO 設定欄位進行 read-modify-write；mode `0x48` 的高腳位路徑另寫入 `base+0x10` 以設定該位元。上述資料流與 WCH GPIO 結構及模式定義吻合，縮小上一節的 helper 契約不確定性。

這是原始指令與候選 SDK 的靜態對照，並以有效 stack、正常呼叫及候選記憶體映射為條件；沒有讀取實機暫存器、驗證電路或測試車輛功能。

### 控制器初始化與診斷候選

原始 V4.1.60 的 `0x18AB0..0x18BA2`（242 bytes）及呼叫後的 `0x12E2A..0x12E4C`（34 bytes）均與目前 C 診斷 ELF 的同址 bytes 一致。`0x12E34` 以 `0x40006400` 為第一參數呼叫初始化函式；此位址符合 WCH 的 CAN1 基址。該函式清除控制位 1、設定控制位 0，輪詢狀態位 0，並傳回狀態；其結構與 [WCH CAN 初始化](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/src/ch32v20x_can.c)中的進入／退出初始化及狀態確認相符。這是候選介面對照，並非宣稱兩份函式完全等價。

呼叫返回後，`0x12E38..0x12E4C` 在沒有檢查 a0 返回值的情況下，對 `0x40006414` 進行讀取、OR 2 與寫回，再返回。可考慮日後新增唯讀診斷以呈現初始化返回狀態，但尚未實作；靜態指令不證明初始化失敗、實際暫存器內容或可安全讀寫實機。

## 原廠板照片與 SPI 協定對照

使用者提供的原廠板照片顯示 `TSL9`、三組 CAN H/L 標示，至少一顆晶片可讀為 `MCP2515`；另一顆相似但照片不足以確認完整料號。較新的主控近照可讀為 `CH32V208`、`GBU6`。照片沒有納入公開儲存庫；上述為目視觀察，未量測電路連線。

V4.1.60 `[0x16896,0x16994)` 的 254 bytes 與目前 C 診斷 ELF 對應位址逐 byte 一致。既有 [SPI 重建分析](../tsl9-spi-write-providers/README.md)記錄 `0x168DE` 呼叫底層傳輸時先送 `0x02` 與地址，`0x1693E` 先送 `0x05`，再依序送地址、mask、value。這與 [Microchip MCP2515 手冊](https://ww1.microchip.com/downloads/en/DeviceDoc/MCP2515-Stand-Alone-CAN-Controller-with-SPI-20001801J.pdf)的 WRITE／BIT MODIFY 指令格式一致，支持照片中的元件與分析路徑可能相關；通用協定相符不證明訊號實際到達該晶片或成功傳輸。

已觀察路徑的 selector bits 會分別對 `0x40010814` 寫入 `0x10`／`0x01`；若採 WCH GPIOA 映射，數值對應 PA4／PA0，與自製方案的兩個 CS 候選一致。原廠 PCB 的實際網路、兩顆晶片料號及接腳對應仍需進一步確認；不應以此推定可刷入。

原始 `0x1706C/0x170B8` 將 `s0` 構成 `0x40010800`，之後 `0x17132..0x17168` 以此 base 呼叫 `0x9A24` 五次。依既有 helper 契約與 [WCH GPIO 模式定義](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/inc/ch32v20x_gpio.h)，在 register／stack 保存、記憶體映射與初始化正常完成等條件下，這些參數分別請求：

| GPIOA pin | 模式參數 | 候選 WCH 解讀 |
| --- | --- | --- |
| PA4、PA0 | `0x10` | 一般推挽輸出 |
| PA5、PA7 | `0x18` | 複用推挽輸出 |
| PA6 | `0x48` | 上拉輸入 |

接著同一路徑在 `0x1718C..0x171A0` 初始化並啟用數值 base `0x40013000` 的 SPI 候選。PA5／PA6／PA7 的方向與候選 SPI1 SCK／MISO／MOSI 分配一致，PA0／PA4 也與前述 selector 寫入相容；這是條件式配置相符性，不證明複用重映射設定、PCB 走線或兩顆 MCP2515 實際連接。未讀取或改寫實體暫存器。

`0x168DE` 的 SPI WRITE 路徑把輸入 `a0` 當位元遮罩：bit 0 非零時向 `0x40010814` 寫入 `0x10`，bit 1 非零時寫入 `0x01`；之後傳送 `0x02`、地址與資料，正常結束時向 `0x40010810` 寫入 `0x11`。若這兩個 GPIOA 位址分別符合 WCH 的 bit-clear／bit-set 定義，且線路為低有效 CS，這對應選擇 PA4／PA0 並在結束時釋放兩線。

函式只檢查低兩位，沒有在本體拒絕 0 或 3：0 不執行上述兩次選擇寫入但仍繼續傳送，3 則要求兩次選擇寫入；其他高位在這兩處判斷中被忽略。這是原始指令與 GPIO 候選介面的條件式解讀，不能推定呼叫者會傳入這些值、兩條線實際接了哪些元件、電氣有效電平或硬體安全。未執行函式或操作硬體。

已辨識呼叫者 `0x16CC4` 在入口先以 `((a0-1)&255)<=1` 檢查；通過代表輸入的**低 byte**為 1 或 2，並不要求整個 32-bit 值恰為 1／2。程式將原 `a0` 存入 `s0`，在後續 `0x16D70..0x16D7E` 把 `s0` 傳給 `0x168DE`。若途中兩個 indirect slot 與其餘 callee 正常返回且遵守 `s0` 保存契約，則這個呼叫點的低兩位分別只能是 `01` 或 `10`：候選 GPIO 解讀下每次選擇一線，而非上述理論上的 0／3。這只涵蓋此呼叫路徑，不證明其他 caller 的範圍、迴圈次數、實際晶片或成功傳送。

另一條 record 路徑 `0x16B7C` 對 record offset 11 的 byte 執行相同的 1／2 guard；通過後還會檢查其他設定與 record 長度。到 `0x16C18` 時，程式**重新讀取** offset 11，並在 `0x16C2C` 將其傳給 `0x168DE`。因此只有在 record pointer／內容未被中間呼叫、alias 或非同步路徑改寫且呼叫正常完成時，才能將入口的 1／2 限制延伸到這個 SPI WRITE 呼叫；原始程式沒有在該 fresh read 旁再次執行同一 guard。此結果不證明 record 的實際來源、CS 電路或傳送成功。

第三個 wrapper `0x16B50` 依輸入 `a1` 從 stack 的 `0x2420` halfword 所在位置取 byte 作 SPI 地址，再把原 `a0` 傳給 `0x168DE`。已辨識的 `0x16E88` 路徑在 `0x16ED0／0x16ED8` 分別提供 `a1=0／1`，因此在 little-endian 且 stack／callee 契約成立時，地址分別為 `0x20／0x24`；這個局部界線不等於 wrapper 本體有任意索引的上限檢查。

該兩次呼叫的 `a0` 沿用 `0x16E88` 的原始輸入，受 `0x16E0C` 返回 0 與中間控制流程約束，但已核對的 `0x16E88／0x16E0C` 本體沒有像上述兩條路徑一樣直接將輸入限制為 1／2。若中途保存與記憶體契約成立，片選低兩位會延續該輸入；尚不能據此證明 0 或 3 在實際 caller 可達，也不能假定全域只有單片選。沒有執行目標或硬體。

進一步核對已辨識的四個直接呼叫點：`0x16F38`、`0x16F86` 以 `a0=1` 呼叫 `0x16E88`；`0x16F6C`、`0x16F8E` 以 `a0=2` 呼叫。這些呼叫各受 `0x16F00` 的事件遮罩、計數或先前返回值分支控制。若 `0x16E0C` 返回 0，且中間所有呼叫正常返回、保留 `s0` 並維持有效 stack，則到達前述兩次 `0x16B50` 時 selector 仍分別為 1 或 2。此結果收斂這四個已辨識直接呼叫點，不能排除其他未辨識入口、間接 caller 或實體線路差異。

在這些呼叫進入設定前，`0x16E0C` 依 selector 位元做 GPIO 候選選擇，經 `0x16896` 傳送 `0xC0`，再要求釋放兩條候選線。之後它反覆以地址 `0x0E` 呼叫 `0x16994`，只有讀回值 `(value&0xE0)==0x80` 時回傳 0；若 `0x81B0` 的無號時間差大於 2，則回傳 1。`0x16E88` 只有在收到 0 時才進行後續設定，包括上述 `0x20／0x24` 寫入。

這與先前 MCP2515 候選協定的 reset／狀態檢查脈絡相符；`0xC0`、`0x0E` 與遮罩是原始運算元，沒有單憑它們證明實機晶片、時鐘單位、有效的片選或初始化成功。超時出口依時鐘結果變化與正常呼叫等條件；沒有執行硬體測試。
