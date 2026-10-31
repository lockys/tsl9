# 六個未解析依賴：靜態用途與邊界

[English](readme.en.md)

此表整理目前原位址 C/C++、既有原始 BIN 指令對照與條件式分析；位址是 V4.1.60 的分析座標。用途屬靜態觀察或有明示前提的推論，並非實機執行結果。六個 symbol 仍未解析；本紀錄不新增 alias、函式、資料或 BIN。

| 依賴 | 已觀察的使用 | 尚未證實 |
| --- | --- | --- |
| `0x40000` | reset 的 `0x18730` 以不寫入返回位址的跳轉交出控制。候選 SDK 啟動鏈可進行 RAM 初始化與 `MRET`。 | 原機該位址是否與候選 SDK 相同、ABI 及實際啟動完成。見 [slot2 啟動](../tsl9-resident-slot2-startup/README.md)。 |
| `0x14056` | `0x8A48` 以連結呼叫；`a0=s3`、`a1=uint8(GP+0xA4)`、`a2=0x2000B9D8`、`a3=uint16(GP+0x8E)`。接收狀態機在 `0x8A1C` 將內容寫到同一 buffer；正常長度解析路徑允許 0–1040。見下節。 | 入口本體位於既定排除區；語義模型稱之 router，但實際分派、各參數的完整 ABI、返回值與副作用尚未確認。 |
| `0x1AB48` | `0xA158` 按 `base+2*counter` 讀 halfword；兩個直接寫入使用 `(old+1)&3`。 | 讀取前全域 counter 一定為 0–3 尚未證明；若成立，現有 8B 窗口覆蓋該次讀取。見 [counter 分析](../tsl9-input-counter-data/README.md)。 |
| `0x1A078` | `0xCF5A` 按 `base+16*mode+column` 讀取，column 經 `&15`；模式 0–5 的條件資料列已納入來源。 | setter 可接收任意低 byte，局部 0–5 不等於全域值域；完整 provider 尚未建立。見 [mode 整合](../tsl9-record-mode-row-integration/README.md)。 |
| `0x1A638` | `0x12046..0x1205E` 按 `base+6*(2*channel+state)` 準備 6-byte 比對，迴圈 channel 為 0–3。 | state 每次讀取均為 0 或 1、實際 ROM slot 為候選比較函式及實體功能，均未證明；條件成立時現有 48B 窗口涵蓋比對。見 [sequence 分析](../tsl9-sequence-pattern-data/README.md)。 |
| `0x1A69C` | `0x131AA` 把此位址放入 `a1`、長度 4 放入 `a2`，並以 `a0=*(GP+0x54)+12` 呼叫由 `0x4004C` 取出的間接目標。候選槽具有逐 byte 複製本體；條件見下節。 | 四 bytes 內容屬既定排除範圍；未讀取或輸出。原機槽身分與記憶體有效性仍未證明。 |

上述 register、位址公式與條件範圍不等於可達性或完整原始 C 宣告。不同版本的地址不能直接互換；目前沒有實機 ROM、RAM、IRQ 或 OTA 相容證據。

## `0x1A078` 的 selector 週期條件

原 `0xCEDC..0xCF96` 在 enable byte 非零且 selector `s` 非 `255` 時，先儲存 `(s+1)%3`；若舊 `s` 非零，這次查表的 effective mode 強制為 0，若舊 `s` 為零，則改讀 mode byte。若舊 `s=255`，走直接讀 mode 的分支，不執行此 selector 更新。這與[完整查表合約](../tsl9-third-provider-lookup-contract/README.md)一致，不是對全域 mode 的限制。

在每次呼叫都從 `0xCEDC` 正常進入、enable 一直非零、儲存後的 selector 沒有被 callee／IRQ／DMA／alias 改寫且查表及尾呼叫均正常完成的條件下，從 `s=0` 開始連續三次呼叫的舊 selector 依序循環為 `0→1→2→0`；相應 effective mode 為「當次 mode byte、0、0」。初始 `s=1..254` 的一次更新會使下一 selector 進入 `0..2`，但 `s=255` 是例外。此結論不保證上述條件、三次呼叫可達、mode 穩定或表內容有效；倒數到零可清除 enable，使後續呼叫直接返回，因此不能把三次模式循環宣稱為實機頻率。

### 三個具體 setter 分支的單次查表

依[既有 setter 控制流程](../tsl9-mode-state-writer-contract/README.md)，到達 `0xD0C8` 的三條分支會把 `[enable, mode, selector, countdown]` 寫成 `[1, M, 0, 1]`，其中 `M` 分別為 2、4、5。若該寫入後狀態沒有被其他路徑改寫、下一次從 `0xCEDC` 正常進入且指標有效，則 selector 先由 0 更新為 1，countdown 由 1 減為 0，`0xCF8E` 清除 enable；但本次仍繼續以 `M` 和 `0..15` 的欄位查表，然後尾跳 `0x12A08`。若之後 enable 沒有重新設置，下一次進入 `0xCEDC` 即返回，不會自然完成上述三次週期。

因此，這三條特定 setter 路徑的這次讀取分別落在既有 mode 2／4／5 的 16-byte 窗口；條件式覆蓋不代表完整 `0x1A078` provider 已閉合，亦不證明寫入、查表或傳送在實機曾發生。其他 setter 可以設定不同 countdown、selector 與任意低 byte mode，不能將此一次性結論套用到全部入口。

### 一般 setter 的已見常數參數

`0xD05C` 把 `(a0,a1,a2)` 轉成 `[enable,mode,selector,countdown]=[1,low8(a0),low8(-a2),low8(a1)]`。在已識別的直接呼叫／尾跳中，原指令提供以下常數；各呼叫本身仍受前置 guard 控制，不能推論一定執行。

| 呼叫位置 | `(mode, countdown, selector)` |
| --- | --- |
| `0xA224`、`0xE6E8` | `(3, 1, 0)` |
| `0xAC6C` | `(1, 1, 0)`、`(3, 1, 0)` 或 `(3, 2, 0)` |
| `0xD528` | `(5, 10, 255)` |
| `0xE1EA` | `(3, 15, 255)` |

特別是 `a2=1` 在 setter 經 `low8(-a2)` 變為 selector 255。若後續沒有任何狀態覆寫、每次均正常進入且完成查表，這兩條 selector 255 路徑分別可完成 10／15 次使用 mode 5／3 的查表，最後一次將 enable 清零；第 11／16 次不重新啟用則直接返回。這是有條件的控制流程推論，不是實測呼叫次數、頻率、傳送或功能；不涵蓋間接呼叫及其他 setter。

### 兩個多次查表呼叫點的條件

`0xD50A..0xD528` 先由 `0xD052` 讀取 byte `0x2000BF44`；只有該值為 1 且 `GP+354` 的 byte 為 0，才尾跳至 setter 並設定 `(5,10,255)`。其他條件走不同路徑，不能由狀態數值猜測車輛功能。

`0xE1A6..0xE1EA` 首先要求 `GP+357` byte 為 1–4、`0x2000BF44` 為 4、`0x8202` 返回非零。之後 `0x81B0` 從槽 `0x4007C` 讀取並呼叫間接目標，將返回值 `x` 以 RV32 算術計算 `((x*10)&0xFFFFFFFF)>>4`；只有此結果減去 `*(GP+272)` 的 32-bit 無號差值大於 1999，才呼叫 setter 設定 `(3,15,255)`。同一路徑隨後會將這次 `0x81B0` 結果寫回 `GP+272`；原始指令沒有在差值比較前補上 rollover 修正。

固定版本 [WCH V1.30 標頭](https://github.com/openwch/ch32v20x/blob/ec059e0b18046b111ee850e44f105fcd095e775c/EVT/EXAM/BLE/LIB/wchble_rom.h) 將 slot 18（`0x4007C`）定義為 `TMOS_GetSystemClock`，單位 0.625 ms。若實機槽相容且乘法沒有發生 32-bit 截斷，`0x81B0` 結果可解作向下取整的毫秒值；乘法會在右移前截斷，因此不能無條件把差值解作實際毫秒或聲稱定時精度。時鐘 ABI、slot、狀態與實際時間均未量測，未證明具體產品觸發事件。

## 追查 `0x14056` 的接收參數

V4.1.60 原始指令 `0x8A3A` 的 `AUIPC a2,0x20003` 加上 `0x8A3E` 的 `ADDI a2,a2,-98`，得到 `0x2000B9D8`。在 `0x8A12..0x8A1C`，另一組 PC-relative 計算得到同一 base，將接收 byte 寫入 base 加計數器。這支持 `a2` 是接收 buffer 的推論，並非實機 RAM 快照。

`0x89C2` 與 `0x89D6` 組成 GP+142 的 16-bit 長度；`0x89E0..0x89E4` 的正常解析路徑對大於 1040 的非零值轉入清除狀態，零長度另行處理。`0x8A2A..0x8A32` 的狀態及 checksum 比較通過後，`0x8A36` 才重新讀取該欄位傳入 `a3`。因此 0–1040 是正常長度解析路徑的條件範圍，**不是已證明所有入口、別名寫入、中斷或跨回呼後都成立的全域不變條件**。`a1` 是 GP+164 的 byte，不能僅依此斷言具體命令語義。

這些結果與既有 [GATT 接收模型](../tsl9-v4160-gatt-ingress-model/README.md)一致；該模型採合成 provider，不能證明 `0x14056` 內部或硬體行為。本輪未讀取排除的函式本體。

## `0x1A69C` 與設定預設值

原 `0x131A6..0x131B4` 每次從 `0x4004C` 載入間接目標，傳入目的 `*(GP+0x54)+12`、來源 `0x1A69C` 與長度 4。既有 [SDK 複製函式核對](../tsl9-resident-copy-arch/README.md)指出候選槽值為 `0x20000332`，其 58-byte 本體以來源／目的／長度執行順向 byte 複製，並先存取 `0x4002420C` 與執行 `FENCE.I`。

依[設定初始化分析](../tsl9-original-prebinding-settings/README.md)，若 reset 所設 GP 與初始 pointer 未被改寫，目的為 `0x2000C2A8..0x2000C2AC`；其初始化路徑會檢查四個 byte 是否為 ASCII 32–126，遇到不符合條件者可進入預設值流程。**若**原機槽確為該候選、來源／目的有效且呼叫正常返回，則四個來源 bytes 會被複製到此目的範圍。這不證明預設內容、實際設定語義、每次開機都執行該路徑，或實機 ROM／Flash 寫入結果；排除資料內容未讀取。

## `0x1AB48` 查表結果的局部用途

在 `0xA146..0xA158`，程式以 `uint8(GP+176)` 作索引，讀取 `0x1AB48+2*index` 的無號 16-bit 值 `x`。該路徑的 `0xA15C..0xA166` 計算 `y=(x+0x802)&0xFFFF`；`0xA16C` 將 `y` 的低 8 bits 寫到 `SP+10`，而 `0xA168..0xA18E` 將 bits 8–11 寫到 `SP+9` 的低 nibble，保留其高 nibble。因此兩欄合起來是 `(x+0x802)&0xFFF`，若以稍後 `a0=SP+4` 為緩衝區起點，它們分別是 offset 6 與 offset 5 的低 nibble。

`0xA1A8` 再以 `a0=SP+4`、`a1=7` 呼叫 `0xED00`。該完整函式讀取 buffer 前兩個 bytes 相加作初始值，依 offset 2 的 byte 長度逐一加上 offset 3 起的資料，略過索引 7，運算保留低 8 bits；`0xA1AC` 將返回 byte 寫到 `SP+14`，即 buffer offset 10／資料索引 7，接著 `0xA1B2` 呼叫 `0x12A08`。在有效 buffer、無干擾且該路徑正常完成時，這支持把 `0xED00` 的結果視為加總檢查碼；不能由此確定協定、單位、實際傳送結果或產品功能。參見[既有 checksum 對照](../tsl9-feature-callback/README.md)。

上述是經此查表路徑的靜態資料流；指標有效、stack 未被 alias／非同步覆寫、callee 正常執行仍是條件。查表索引與後續欄位只分別具 byte、12-bit 的保守範圍，不能由此證明索引全域為 0–3 或宣稱四筆資料即完整表格。

## 檢查碼後的條件式分派

`0xA1B2` 將上述 buffer 交給 `0x12A08`。依[原始 dispatcher](../tsl9-record-dispatch/README.md)，此函式先呼叫 `0x81AA`，若返回 0 且輸入首 halfword 不為 1 則返回；否則以 0 呼叫 `0x821E`，返回 0 亦直接返回。之後輸入 offset 11 非零轉到 `0x16B7C`；為零則組合 stack record，使用 `0x4004C` 間接槽、來源 input+3 與 input offset 2 的 byte 長度，再以 `a0=0x40006400`、`a1=SP+12` 呼叫 `0x18CA4`。

數值 `0x40006400` 對應 WCH 的 CAN1 基址；`0x18CA4` 的 mailbox 選擇與欄位操作和 [WCH CAN_Transmit](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/src/ch32v20x_can.c)相符。這支持在**通過上述 guard、offset 11 為零、複製與呼叫契約成立**時，把該分支理解為向內建 CAN1 提交訊息的推論；沒有證明實際硬體、線路、資料長度合法、mailbox 可用、訊框送達或另一分支的用途。caller 沒有檢查 `0x12A08` 的返回值。間接槽、callee 副作用與執行期間可能改寫仍屬限制。

## 資料長度與 stack 邊界

`0xA0D4..0xA0E0` 將來源 `s3`、目的 `SP+4`、長度 12 傳給 `0x4004C` 間接槽；在槽為候選 copy 且呼叫正常返回等條件下，後續處理的最初 12-byte record 來自該輸入。`0x12A32` 重新讀取 record offset 2 作為 byte 長度，`0x12A46..0x12A4E` 將 `record+3`、該長度與 dispatcher 自身 `SP+23` 傳給另一個 fresh `0x4004C` 間接呼叫。本分支中沒有在這兩處之間看到本地長度上限檢查。

WCH 的 [CanTxMsg](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/inc/ch32v20x_can.h) 定義 8-byte Data；`0x18CA4` 在選中 mailbox 的路徑固定讀取該欄位的 8 bytes。若兩次 indirect call 均為候選順向 copy、讀寫有效且沒有其他寫入：長度小於 8 時，dispatcher 複製不到 8 個資料 bytes；大於 8 時會超過該資料欄位。其 48-byte frame 的 saved S0 與 RA 分別在 `SP+40`、`SP+44`，從 `SP+23` 起算，長度至少 18／22 才分別觸及這些位置。這是**條件式位址分析**，不是實際越界、未初始化內容、可達輸入或安全漏洞的證明；原機槽身分、前置驗證、alias 與非同步行為仍未封閉，也不能藉此改寫或刷入韌體。

### 呼叫前的 checksum 檢查不能單獨限制長度

`0xA062` 呼叫 `0x1069E`；此函式在 `0x106A8` 以排除索引 7 呼叫 `0xED00`，然後僅比較回傳值與輸入 offset 10，結果相等才返回 1。`0xA066` 在返回 0 時離開。這個函式本體沒有長度比較；`0xED00` 將 offset 2 當作 0–255 的迴圈長度，並不把長度 byte 自身加入加總。

對每個 byte 長度 0–255，在**足夠長且可讀的合成 buffer**中，令 offset 2 為該長度、其餘 bytes 全為零，則加總與 offset 10 均為零，數學上可滿足此 checksum 條件。這否定「checksum 相等本身可證明長度不超過 8」，但不是在原程式中執行測試、也不證明這些記錄可通過其他 guard 或可到達後續 copy；兩次呼叫之間記憶體一致性仍未知。

### 上游 record 的一條分派入口

已納入範圍的 dispatcher 從 record `s0+0` 讀取 halfword；在對應分派樹中，`0x14F18..0x14F1C` 比較此值與 **880／`0x370`**，相等時跳至 `0x152D0`，該區塊把 `s0` 放入 `a0`、還原自身 frame 後，於 `0x152D8` 尾跳 `0xA054`。因此 `0x370` 是**這條路徑**所比較的 record 值，不是已證明的全部入口或資料來源。分派樹還受先前 `0x829E` 返回值與其他分支控制；此處沒有發現可直接推定 offset 2 長度的比較。

結合下一階段與 WCH CAN1 介面的對照，`0x370` 可作為待驗證的訊息識別值線索；目前沒有實際 CAN 擷取、完整原機入口或產品功能證據，不能宣稱這是已確認的 CAN ID、裝置行為或長度保障。參見 [feature dispatcher](../tsl9-feature-dispatch/README.md)。

### Queue 的長度 4 檢查屬另一分支

原 queue 消費函式 `0x12C86..0x12CA4` 依 12-byte stride 取 record，並請求經 `0x4004C` 間接槽複製 12 bytes 到自身 `SP+8`。接著 `0x12CB0` 呼叫 `0x82D2`，僅在結果為 0 時繼續；`0x12CB6..0x12CBA` 新讀 stack record 首 halfword，與 `s4` 比較。`s4` 在 queue 入口被設為 1；**若呼叫後仍保留該值**，首值不為 1 時就跳到 `0x12D78`，繞過 `0x12CBE..0x12CC4` 的 offset 2 等於 4 檢查。該分支另經設定 bit 與 `0x81AA` guard，於 `0x12D8C` 把 `SP+8` 傳給 `0x14D2E`。

因此，若上游 record 首值在相關讀取時保持 `0x370`，它會走非 1 分支，而不能以另一分支的「長度等於 4」來界定此 record。這是**條件式分支分析**：間接 copy、`0x82D2`、`s4`／stack 與記憶體在呼叫間是否保持、record 的實際 producer 與其他驗證均未封閉；沒有證明特定長度可達或存在漏洞。見[queue 來源](../../src/native/receive/queue_consumer.c)與[功能分派器](../tsl9-feature-dispatch/README.md)。

### 兩條已識別 queue 寫入路徑

`0x12BC8` 選取最多 32 個、每個 12-byte 的 slot，先把 `a0` 低 halfword 寫至 offset 0、`a2` 低 byte 寫至 offset 2，再透過 `0x4004C` 以完整 `a2` 請求複製到 offset 3；本體沒有長度上限檢查。[原位重建](../tsl9-ring-insert/README.md)和 queue consumer 的 PC-relative 運算都指向相同基址 `0x2000C038`。共享數值位址並不單獨證明實機記憶體所有權或呼叫間內容不變。

| 已見來源 | 呼叫 `0x12BC8` 前的原始長度處理 | 靜態界線 |
| --- | --- | --- |
| SPI 接收 `0x16ACC..0x16AFA` | 對 `SP+20` byte 取低四位，再以 `(length-1)&255 <= 7` 為接受條件；符合後原樣傳入 `a2`。 | 此呼叫點的 `a2` 為 **1–8**，以前述路徑正常執行、暫存器／stack 未受干擾為條件。 |
| CAN1 候選 IRQ `0x12C24..0x12C4A` | `0x18D9C..0x18DA2` 將來源 word 低四位存至輸出結構 offset 10；IRQ 由自身 `SP+22` 讀該 byte 作為 `a2`。 | 若 provider 正常完成且 stack／暫存器未被改寫，值為 **0–15**；不能僅憑指令斷定硬體實際會給出哪些 DLC。 |

這兩條是已辨識呼叫點，並非所有可能 producer 的完整清單；也不證明 `0x370` 特定 record 一定由其中某一路徑產生。候選 copy、後續 slot／consumer、IRQ 與記憶體一致性仍需成立，才能把來源界線延伸至後續使用。沒有執行韌體或硬體測試。

### CAN1 候選接收結構與 WCH 的對照

原 `0x18D78` 接收函式將識別型態、ID、RTR、低四位長度、八個資料 bytes 與 FIFO metadata 寫入呼叫者提供的結構；寫入位置及 FIFO release 的控制流程與 [WCH CAN_Receive](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/src/ch32v20x_can.c) 和 [CanRxMsg 定義](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/inc/ch32v20x_can.h)相符，支持將其視為 CAN 接收 helper 的推論，並非逐字證明兩者完全等價。

IRQ `0x12C32` 在 32-byte frame 中以 `SP+12` 作結構起點，故 DLC 位於 `SP+22`、八個 Data bytes 位於 `SP+23..SP+30`、FMI 位於 `SP+31`。`0x12C3C..0x12C4A` 傳入 ring 的來源為 `SP+23`，長度為 DLC byte；ring slot 的 8-byte 資料窗口為 offset 3–10，offset 11 在 copy 後寫入 tag 0。

**若** DLC 為 9、兩個 helper 正常完成、`0x4004C` 為候選順向 copy 且記憶體／暫存器無干擾，則來源複製會讀入 `SP+31` 的 FMI，寫到 slot offset 11，之後被 tag 0 覆寫；若 DLC 至少為 10，數值上會讀到 IRQ frame 之外並寫超過該 slot。這是來源與目的範圍的條件推算，不能證明 DLC 9–15 真實可由此硬體產生、該路徑可達、實際越界或漏洞；更不能推論車輛功能或刷寫安全。未接觸硬體。

## `0x1A638` 序列狀態的局部正規化

`0x12046` 先讀取目前 channel 狀態，使用 `0x1A638+6*(2*channel+state)` 準備比對。間接比對返回後，相等分支在 `0x12066` **重新讀取**狀態 byte `v`，算出 `t=(v+1)&255` 並於 `0x12072` 寫入；若 `t<=1`，即保留 `t` 並離開。若 `t>1`，走 `0x1207A..0x12090` 後將該狀態清為 0。不相等分支在 `0x1209C` 直接清為 0，再考慮下一 channel。

對 `v=0..255` 完整枚舉，上述相等分支正常完成後的值只有 0 或 1：`v=0` 得 1、`v=255` 因 byte 回繞得 0，其餘值經第二次寫入變成 0。不相等分支寫 0。這是**一次完整局部轉換**的性質，條件包括記憶體有效、`s5`／`s6`／channel 關聯正常、間接呼叫與各路徑正常完成、無 alias／IRQ／DMA／重入覆寫。`t>1` 時，在 `0x12072` 與 `0x12090` 之間會暫時存在該值；而第一次查表發生在正規化之前，兩次狀態讀取也可能不同。因此不能以此證明每次查表索引必為 0／1、沒有中間狀態或全域狀態範圍。見[既有序列分析](../tsl9-sequence-pattern-data/README.md)。

### 完成後的標記資料流

匹配路徑中，當 `0x12076` 的新狀態大於 1，`0x1207A..0x1209A` 從 `s2+0..2` 各讀取一個 byte，並與 `0x80+channel` 合成 32-bit `word=(byte0<<24)|(byte1<<16)|(byte2<<8)|(0x80+channel)`；正常迴圈的 channel 為 0–3，低 byte 因而是 `0x80..0x83`。此處已將對應狀態清零，再跳到 `0x11C64`。

在 `0x2000BFD3` byte 為 0 的分支，`0x11C7A..0x11C96` 寫入 1 到該 byte、將 word 寫入 `0x2000BFCC`、清除 `0x2000BFD0..0x2000BFD2`，接著分別從 `0x40058` 新讀間接目標並呼叫，兩次的 `a1/a2` 分別為 `1/480` 與 `2/640`；`a0` 每次取 `0x2000BFC8` byte。這是**條件式靜態資料流**：指標、stack、記憶體及間接函式的保存／回傳契約必須成立，不能從數值 480／640 推定時間單位或已成功排程。狀態 byte 非 0 時會走另一條分支；這些觀察不識別硬體按鍵或產品功能，也不證明實機曾匹配。

### WCH V1.30 函式表候選對照

本機保存、來源為 [WCH 固定版本 V1.30 標頭](https://github.com/openwch/ch32v20x/blob/ec059e0b18046b111ee850e44f105fcd095e775c/EVT/EXAM/BLE/LIB/wchble_rom.h)的預設表格基址為 `0x40034`，`BLE_LIB_JT(n)` 讀取 `base+4*n`；其 `tmos_start_task(taskID,event,time)` 使用 slot 9，因此該候選的表項位址為 `0x40058`。同一標頭將事件定時單位標示為 625 微秒。標頭 SHA-256 為 `647a185941fedeb6ba16d544d9bca91a6f53219bb649a5513b59abeb21a9a94c`。

**如果**原機該槽確實與此 V1.30 介面及定時單位相容、任務 ID／事件值有效且呼叫正常成功，則前述兩次呼叫可解讀為事件 `1`／`2` 的 480／640 ticks，名義上為 **300／400 毫秒**。這是對照公開候選介面的條件式推算，沒有量測實際時間、證明槽內容或函式 ABI、驗證執行成功，也不能識別按鍵或產品功能；V1.30 標頭不能證明原機 resident 版本。

在 `0x2000BFD3` 非 0 的另一分支，`0x12186..0x12194` 將 `0x2000BFCC` 的舊 word 與新 word 比較，再檢查 `0x2000BFD2` 是否為 0。若兩者條件成立，程式將該旗標設為 1，呼叫 `0x11356(0)`，再從 `0x4005C` fresh 讀取間接目標，以 `a0=uint8(0x2000BFC8)`、`a1=1` 呼叫，最後回到 `0x11CB0` 的 `0x40058`／`a1=2`／`a2=640` 呼叫。若 word 不同或該旗標非零，則直接走後者。

同一 WCH V1.30 標頭把 `tmos_stop_task(taskID,event)` 定義在 slot 10，即 `0x4005C`。**若**兩個原機槽均符合此候選介面，則相等且旗標為零的路徑可推論為先請求停止事件 1，再請求以 640 ticks 啟動事件 2；這不是已確認的操作結果或時間量測，且依有效記憶體、`0x11356` 與間接函式正常返回、保存暫存器及無非同步覆寫等條件。程式未藉此證明實際按鍵用途。

### 候選任務 ID 與事件回呼的連接

`0x1250A` 令 `s0=0x40000`；在中途呼叫遵守保存暫存器契約且控制流程到達該處的條件下，`0x1262E..0x1263C` 從 `0x40080` 載入間接目標，傳入 `0x11442`，並把回傳值低 8 位寫到 `0x2000BFC8`。同一 byte 被上述兩個計時呼叫讀取。候選 WCH V1.30 標頭定義 slot 19（`0x40080`）為 `TMOS_ProcessEventRegister`，接收事件回呼並回傳 task ID；其文件將 `0xFF` 列為錯誤。這支持兩者連接的**條件式推論**，不能證明實際 resident 版本、註冊成功、回傳值有效或後來沒有覆寫該 byte。

原始 `0x11442` 的 `a1` 遮罩分支優先檢查 bit 2，再檢查 bit 1：bit 2 呼叫 `0x11356(1)`、清零 `0x2000BFD3` 並回傳原遮罩 XOR 2；若 bit 2 未設而 bit 1 有設，則呼叫 `0x11356(0)` 並回傳原遮罩 XOR 1。前述候選事件 1／2 因此與此回呼的兩條分支相符；這仍依賴實機函式表、排程器與回呼 ABI 相容，而且只能說明控制流程，不證明特定車輛功能或事件曾實際執行。

### 事件分支對應的記錄選擇

`0x11356` 先讀 `0x2000BFCC`，若為零即返回；非零且 `0x2000BFC9` 為零時，才以 `*(GP+88)` 為來源、每筆 6 bytes 掃描最多 42 筆。每次重新讀取指標與 `0x2000BFCC`，把記錄 offset 2 的 halfword 作低 16 位、offset 4 的 halfword 作高 16 位比較。這個 word 與前述完成路徑儲存的組合值使用同一數值位址，並不保證兩次讀取之間未改變。

每次相符時，若 `0x11356` 的輸入為 1，則以 `255` 呼叫 `0x155D0`；輸入為 0 時，依 `0x2000BFD2` 是否為零選擇該記錄 offset 0 或 1 的 unsigned byte 傳入 `0x155D0`，隨後以 `a1=16`、`a2=160` 呼叫 `0x40058` 間接槽。多筆相符均可能處理。上述只描述掃描分支：`0x2000BFC9` 非零另有不同路徑；指標有效、讀取對齊、call 正常返回與保存暫存器、記憶體未受干擾均是條件。它不證明記錄實際內容、動作值的產品意義、事件成功或硬體效果。

### 與 APP reset 及 RAM 配置的交叉對照

既有 [APP reset 分析](../tsl9-reset-state-bootstrap-contract/README.md)核對 `0x186EE` 的 word 清零範圍為 `[0x20004080,0x2000C958)`；`0x2000BFC8`（任務 ID byte）、`0x2000BFC9`、`0x2000BFCC..0x2000BFD0`（word）、`0x2000BFD2` 與 `0x2000BFD3` 均落在其中。因此，在原始進入暫存器、有效記憶體、清零迴圈正常完成且無干擾的條件下，這些位置在 `0x186F8` 為零。這是該時刻的局部結果；不能推論後來第一次比較、註冊或回呼時仍為零。

既有 [clock 存取核對](../tsl9-clock-reset-noninterference/README.md)列出的明確 CPU store 及 [候選 bootstrap 寫入範圍](../tsl9-reset-state-bootstrap-contract/README.md)均避開上述位置。在非 alias、無 IRQ／DMA／重入或間接副作用、所有呼叫正常返回且實機 resident 相符等前提下，這收窄了 reset 後至候選 MRET 的已知直接覆寫來源；不證明啟動成功、後續 APP 初始化沒有改寫、註冊成功或首次使用的狀態。

這些數值位址均高於 RAM base 32 KiB 的 `0x20008000`，低於 48 KiB 的 `0x2000C000`；以 [CH32V208 候選記憶體配置](../tsl9-ch32v208gbu6-evidence-20261029/README.md)的連續映射且無重映射為條件，它們位於該文件所列 48 KiB 與 64 KiB 範例而不在 32 KiB 範例內。這些欄位本身不能區分 48 與 64 KiB，也不是實機選項位元、RAM ownership 或容量的讀取結果。

### 42 筆記錄的初始指標

原始 BIN 在 `0x1ABB8` 的 little-endian word 是 `0x2000C30C`。`0x186BA..0x186DA` 將 `[0x1AB60,0x1ABE0)` 複製到 GP 所指的 128-byte 區；若 GP 為 reset 所設 `0x20004000`、複製正常且沒有覆寫，則 `*(GP+88)` 初始為 `0x2000C30C`。以 42 筆、每筆 6 bytes 計算，記錄範圍為 `[0x2000C30C,0x2000C408)`，整段落在 reset 清零範圍 `[0x20004080,0x2000C958)` 內。

因此在這些條件成立且清零完成後，各記錄的兩個比對 halfword 均為零；要由此初始狀態走到掃描分支的非零 key 相符，至少需有後續寫入改變記錄或指標。候選 bootstrap 與已核對 clock 的明確寫入避開指標及此記錄區，但這不排除 APP、IRQ、DMA、alias 或其他間接作用後續改寫；不能把初值當成第一次掃描時的實測值，也未確認記錄的產品語義。

此初始指標及記錄區高於 `0x2000C000` 而低於 `0x20010000`；僅在前述 WCH 連續映射與無重映射條件下，該記錄區符合 64 KiB 範例而超出 48 KiB 範例。實機 RAM 選項、實際指標內容及有效性仍未量測。

### 同一記錄區的載入與 fallback

原 APP 初始化在 `0x13238..0x13252` 從 `0x4004C` 載入間接目標，以來源 `0x08077800`、目的 `0x2000C30C`、長度 256 呼叫。若該槽是候選 copy、來源與目的有效且呼叫正常完成，則整個 42×6-byte 掃描區是此次載入的前 252 bytes。後續 `0x13254..0x13264` 檢查目的 offset 255（`0x2000C40B`）是否為 `0x5A`，不符時呼叫 `0x12F18`。此 marker 不涵蓋完整性檢查，也不能單憑它證明前 252 bytes 有效或已知產品功能。

fallback `0x12F18..0x12F44` 以目的 `0x2000C30C`、值 0、長度 256 呼叫 `0x40048` 槽，接著將 `0x5A` 寫至 offset 255，再尾跳 `0x12EE6`。該 writer 透過 `0x4004C` 請求複製 256 bytes 至 stack，以 `0x08077800` 和 stack 指標呼叫 `0x9C0A`。若相關槽分別符合候選 fill／copy、記憶體有效且無干擾，fallback 會清零掃描區；實機來源內容、marker 是否相符、實體 Flash 位址映射及寫入成功均未確認。見[既有 NVM 區域分析](../tsl9-NVM-record-layout/README.md)。

### 動作值 255 的分派限制

事件遮罩 `0x2` 的候選回呼在掃描分支每筆相符時，以 `255` 呼叫 `0x155D0`。該函式先檢查 `*(GP+84)` 所指記錄 offset 4 的 `0x08` bit；若為 1，因 `(255+6)&255=5 > 2`，直接到 `0x1578C` 還原返回，不走後續 pending 或跳轉表。若此 bit 為 0，則讀 `GP+358` byte：非零時清除此 byte，尾跳 `0x18110`，後者以 `a0=0`、`a1=3`、`a2=1` 尾跳 `0x1802E`。

若 bit 與 pending byte 均為 0，則 `(255-1)&255=254`，大於跳轉表的最大索引 252，因而同樣從 `0x1578C` 返回；它不走 1–8 的前置排程，也不進入 253 項相對跳轉表。這些是原始控制流程與 byte 運算，不表示 `255` 永遠無作用；間接資料有效、無非同步覆寫和正常執行仍是條件，`0x1802E` 的產品語義及實際效果未由此確定。參見[既有動作分派器證據](../../analysis/action-dispatch-2026-10-24/README.md)。

在前述 bit 為零、pending byte 非零且控制流正常到達的情況，`0x18110` 尾跳至 `0x1802E` 時的參數為 `(0,3,1)`。`0x1802E..0x18056` 將 `3` 寫入 byte `0x2000C928`、將 `0` 寫入 byte `0x2000C927`，由於第三參數非零而跳過與舊 word 的 OR，將 `0` 寫入 word `0x2000C92C`，再以 `a0=0` 尾跳 `0x17F80`。這提供該特殊分支的具體 RAM 寫入證據，但不證明實機發生、最終狀態持續、下游動作成功或這些欄位的產品意義。

## `0x1A078` 查表輸出與分派

在到達 `0xCF36` 的路徑上，程式寫入 record offset 4，於 `0xCF3A` 重新讀取該 byte `b`；接著把低 nibble 設為 `(b+1)&15`，保留高 nibble，並以這個新低 nibble 作為 column。`0xCF5A` 從 `0x1A078+16*effective_mode+column` 讀取一個 byte，`0xCF5E` 寫至 record offset 3，再於 `0xCF62` 不寫入返回位址地尾跳 `0x12A08`。因此 column 必為 0–15，但讀出的 byte 仍為 0–255；尚未確認其產品語義或其值是否可代表特定命令。

這段 `0xCF36..0xCF62` 沒有呼叫 `0xED00` 檢查碼函式；這不是全程未重新計算檢查碼的證明，因為上游及尾跳後的呼叫可能改寫或處理 record。若 record 記憶體有效、讀寫之間無 alias／非同步覆寫且原控制流正常執行，則上述資料流成立。`effective_mode` 未被 `&7` 限制，既有 [mode 寫入來源分析](../tsl9-mode-state-writer-contract/README.md)中的局部 1–5 值也不是全域界限。

### Enable、selector 與倒數的局部分支

原 `0xCEDC..0xCEF6` 先讀 enable，為 0 時直接返回，不執行本次查表。enable 非 0 時讀 selector：值為 `0xFF` 時走 `0xCEFA` 讀 mode 與倒數；值為 0 時，先依 `0xCF66..0xCF78` 更新 selector，再走相同 mode／倒數路徑；值為 1–254 時更新 selector，並強制本次 effective mode 為 0，不走該次倒數遞減。

在 mode／倒數路徑，`0xCF0E..0xCF18` 以 byte 算術計算並寫回 `(old_count-1)&255`。若結果為 0，`0xCF8A` 清除 enable，然後仍跳回 `0xCF1E` 完成本次查表與尾跳；所以 old_count=1 會停用**後續**呼叫但不取消目前這次，old_count=0 則回繞為 255，不觸發該次清除。上述是以有效記憶體、非同步狀態不被改寫、正常控制流為條件的局部結論；不是產品上倒數的單位、排程頻率、全域狀態值域或可達性的證明。

### Selector 週期的條件式推算

在 enable 持續非零、每次呼叫正常完成且沒有其他寫入的條件下，selector 初值 `0..254` 每次依 `(old+1)%3` 更新；第一次更新後即為 0、1 或 2，後續循環 `0→1→2→0`。在穩定循環中，舊值為 0 的呼叫讀取 stored mode 並遞減 countdown；舊值為 1 或 2 的呼叫使用 effective mode 0、不遞減 countdown。因此每三次**實際進入且完成的呼叫**中有一次遞減，前提是 enable 在此期間沒有被清除。

`0xFF` 是獨立路徑：此函式不更新 selector，每次進入均走 stored mode／倒數路徑。不能因此推算真實時間、事件頻率或全域 selector 域；任何其他 writer、重入、錯誤或倒數歸零後停用都會破壞上述持續週期假設。
