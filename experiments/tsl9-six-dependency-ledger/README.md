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
