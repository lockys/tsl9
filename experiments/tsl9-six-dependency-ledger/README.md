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

### Mode 查表的數值位址範圍

對 `0xCF5A` 的公式 `0x1A078+16*effective_mode+column`，若只使用 byte 寬度 `effective_mode=0..255` 與 `column=0..15`，共有 4,096 個數值組合。以現有 APP 映像半開區間 `[0x8000,0x1AC00)` 計算：mode **98** 的 column **4–7** 指向既定排除區 `[0x1A69C,0x1A6A0)`；mode **184** 的 column **8–15** 與 mode **185–255** 的全部 columns 超過 APP 結尾，共 1,144 個組合。

這是位址公式的保守分類，不代表這些 mode／column 可達、實際記憶體不可讀、發生越界，或完整 provider 有 256 列。已納入來源的 mode 0–5 共 96 bytes，也不能據此推出其他列。只有 setter、selector、記憶體及執行條件經進一步證明，才能縮小實際讀取域。[檢查器](check-mode-address-domains.py)固定允許的指令窗口、查詢 APP 檔案大小並做區間算術；不讀取排除資料或執行目標。

### 三個具體 setter 分支的單次查表

依[既有 setter 控制流程](../tsl9-mode-state-writer-contract/README.md)，到達 `0xD0C8` 的三條分支會把 `[enable, mode, selector, countdown]` 寫成 `[1, M, 0, 1]`，其中 `M` 分別為 2、4、5。若該寫入後狀態沒有被其他路徑改寫、下一次從 `0xCEDC` 正常進入且指標有效，則 selector 先由 0 更新為 1，countdown 由 1 減為 0，`0xCF8E` 清除 enable；但本次仍繼續以 `M` 和 `0..15` 的欄位查表，然後尾跳 `0x12A08`。若之後 enable 沒有重新設置，下一次進入 `0xCEDC` 即返回，不會自然完成上述三次週期。

因此，這三條特定 setter 路徑的這次讀取分別落在既有 mode 2／4／5 的 16-byte 窗口；條件式覆蓋不代表完整 `0x1A078` provider 已閉合，亦不證明寫入、查表或傳送在實機曾發生。其他 setter 可以設定不同 countdown、selector 與任意低 byte mode，不能將此一次性結論套用到全部入口。

#### 三條分支的輸入與守衛

進一步核對 `0xD07C..0xD0EC`：入口先比較 32-bit `a0` 與 byte `0x2000BF44`；相等便返回。否則呼叫 `0x10402`，後者讀取 `uint16(GP+80)`；若返回值大於 8，則不走這次四-byte 寫入。若該值不大於 8，還要 `GP+354` 的 byte 為 0，才依保存在 `s0` 的原始輸入選擇：

| 原始 32-bit 輸入 | 寫入 mode | 四個 bytes `[enable,mode,selector,countdown]` |
| --- | --- | --- |
| 1 | 5 | `[1,5,0,1]` |
| 2 | 2 | `[1,2,0,1]` |
| 4 | 4 | `[1,4,0,1]` |

在這條 `GP+354=0` 路徑，其他完整 32-bit 輸入不執行該四-byte store；若 `GP+354` 非零則尾跳 `0x10022`，其局部用途如下。這些是局部控制流程，條件包括有效 GP／stack、記憶體與 `s0` 保存；未證明呼叫實際發生、其他 writer 不存在或 mode 的全域範圍。[檢查器](check-mode-setter-guards.py)核對原始指令窗口與三個 little-endian 常數，沒有執行目標或讀取排除區。

#### `GP+354` 非零時的替代 record 路徑

`0xD0DE..0xD0E8` 傳入原始輸入及 `a1=0`，尾跳完整函式 `0x10022..0x10032`。該函式將輸入低 byte 寫入 `GP+300`，將 `1` 寫入 `GP+301`；它的明確 store 沒有寫入 mode 的四-byte 狀態。若兩個狀態區位址正常且互不 alias，這條函式本身不變更 `0x2000BF38..0x2000BF3C`。

後續 `0xFFA4` 只有在 `GP+301` 與 `GP+354` 均非零時才繼續處理 record：先將 record offset 4 的低 nibble 算成 `(old+1)&15`，然後依 `GP+300` 的 byte，對結果 OR 上下表旗標；其他值不額外 OR 旗標。它將結果寫回 offset 4，以 record 和 `a1=0` 呼叫 `0xED00`，把返回 byte 寫入 offset 3；再將重新讀取的 `GP+301` 減 1 並尾跳 `0x12A08`。

| `GP+300` | 額外 OR 旗標 |
| --- | --- |
| 1 | `0x10` |
| 2 | `0x20` |
| 3 | `0x80` |
| 4 | `0x40` |

若前述設定後沒有其他改寫、`0xFFA4` 正常到達且 callee 正常返回，這次會使用輸入低 byte，並將一次計數從 1 減為 0；這不保證下一個 record 一定到達、傳送成功，或可把旗標解釋成特定車輛功能。`0x10022` 的其他 caller 可傳入非零 `a1` 而設定 10，不能將本分支的 1 套用到所有呼叫。

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

#### 乘法截斷的數學反例

令 `f(x)=((x*10)&0xFFFFFFFF)>>4`。`f(429496729)=268435455`，但下一個 tick 的 `f(429496730)=0`。若前一次儲存值恰為前者、這次 slot 回傳後者，原 32-bit 無號減法得到 `4026531841`，大於 1999；即使候選時鐘只增加一個 0.625 ms tick，該比較仍會通過。此轉折是乘法先截斷的結果，不等同 32-bit 時鐘本身已回繞。

若原機確實採用候選時鐘、上述兩個輸入值連續可達、其他 guard 均通過且保存狀態沒有干擾，該例支持可能出現不同於直覺時間間隔的觸發。這只是依指令做的算術見證：沒有量測時間、證明該狀態可達或發生過，也沒有判定實機缺陷。

#### 時鐘換算的重複與九個截斷邊界

同一 `f` 對任意 32-bit `x` 滿足 `f((x+2^31) mod 2^32)=f(x)`，因為乘以 10 後的差是 `5×2^32`，低 32 位完全相同。因此兩次原始計數相差 `2^31` 時，單看換算值與無號減法會得到差值 0；這不是一般的完整經過時間。若候選 WCH slot 和 0.625 ms tick 均適用，`2^31` ticks 相當於約 15.53 天；這是條件式換算，非實測週期。

在原始計數不回繞的 `0..2^32-1` 範圍，乘積的九個邊界是 `ceil(k×2^32/10)`，`k=1..9`；每個邊界前後換算值都由 `268435455` 降至 `0`。在前次保存值恰為前者、下次取得後者且其他 guard 均成立時，無號差均為 `4026531841`，超過 1999。這些是算術與靜態指令的結果；實機 slot 身分、實際取樣、保存值、可達性與觸發均未確認，也不能把它當成實機缺陷。可用 [`check-clock-arithmetic.py`](check-clock-arithmetic.py) 重播九個邊界和固定指令片段；不讀取排除區，也不執行目標。

### 已重建 mode 0–5 的資料關係

對照原始 BIN 的六個已重建 16-byte 窗口 `0x1A078..0x1A0D8`，對每一欄 `c=0..15`，六列均滿足 `row[m][c] = row[0][c] XOR k[m]`；`k[0..5]` 分別為 `00、E0、EF、0F、F1、E9`。每列內的 16 個 byte 互不相同，因此在 mode 已知且這六列之一確實被讀取時，該列輸出值可唯一反推欄位。

跨六列的 96 個位置只有 74 個不同 byte 值；20 個值出現多次，其中最高出現三次。因此若 mode 不明，不能單憑輸出值唯一決定 mode 與欄位。這只是一份原始資料窗口的可重現關係，不證明產品語義、實際可達性、其他 mode 的 XOR 參數或原始完整表長；不可用它生成未知列或代替 `0x1A078` provider。

### 可識別的 record 分派入口

在 `0x14D2E` 的一條分派樹路徑中，`0x14D5E` 將 record offset 0 作無號 halfword 讀取；若該值為 553／`0x229`，`0x14DD2` 轉至 `0x150BE`。後者先以 record 呼叫 `0xCEC0`，再把相同 pointer 傳給 `0xCEDC`；由 `0xCEC0` 正常返回、saved register／記憶體不被改寫且 enable 非零等條件成立時，才可能讀取 `0x1A078` 並修改 record offset 3／4。

這條 handler 還受 `0x829E` 的選擇結果與上游 queue 的 guard 限制；相同數值位址的 ring 已識別 SPI 與候選 CAN1 輸入，但尚未證明 `0x229` record 的特定來源或實際訊框。此處的 `0x229` 是原分派比較值，不足以單獨確定實體 CAN ID、車輛功能或傳送成功。尾跳 `0x12A08` 的候選 CAN1 路徑及其守衛見本文件的「檢查碼後的條件式分派」。

#### 前置 record 欄位與相鄰狀態機

`0xCEC0..0xCEDC` 讀 record offset 4 的 byte `b`，傳給 `0xEBAC` 的三個參數是 `57+((b>>4)&7)`、`57` 與 `0x2000BF3C`。因此前者只取原 byte 的 bits 4–6，參數值是 57–64；bit 7 不參與此計算。這個指標緊接 mode 狀態 `[0x2000BF38,0x2000BF3C)` 之後，不是 mode selector 本身。

在 reset 清零正常完成、`0x2000BF3C..0x2000BF3E` 仍為零且記憶體與呼叫沒有干擾的條件下，若 bits 4–6 為 0，`0xEBAC` 由 `0xEC22` 返回；若為 1–7，則先將 `0x2000BF3C..0x2000BF3F` 寫成 `[1,1,57+bits]`，再以 `(57+bits,1,0)` 呼叫 `0xE220`。其 type 0 表項指向 `0xE246`；在前置呼叫及 guard 允許進入第二張表時，對應 58–64 的七個表項都指向 `0xE288`。這些是上游狀態和分派的局部限制：`0xE220` 後續仍可能有副作用，不能推定 mode 不變、某個 record 實際可達或這些值代表特定功能。[檢查器](check-mode-upstream-state.py)固定允許的原始指令及表項，沒有執行目標或讀取排除區。

#### 上游代碼 64 的具體分支

延續上述條件，若 bits 4–6 為 7，`0xE220` 的保存值為 64；若前置呼叫正常、記憶體及保存暫存器穩定，則會到達 `0xE288`。該處 `0xB6A8` 只在 `(byte[0x2000C234]&0x30)==0x20` 時返回 1。若這個條件成立，後續分支到 `0xE642`：將 1 寫到 `GP+263`，再以 1 呼叫 `0xBD00`；後者直接將此 byte 寫到 `0x2000BEFD`。若 GP 為 reset 的 `0x20004000`，前者是 `0x20004107`。接著以 1 呼叫 `0xDA36`：若 `*(GP+84)` 所指設定 offset 6 的 bit 7 為 1，則尾跳 `0xFE1C`；bit 7 為 0 時直接返回。

這證明在列明條件下前置函式並非單純讀取，但尚未封閉 `0xFE1C`、其他 callee 或非同步副作用，不能據此判斷後續 mode 值、實際發生的事件或產品功能。`0xB6A8` 不相符的其他分支未包含在此結論。[檢查器](check-mode-code64-branch.py)固定允許的指令窗口及位元運算，沒有執行目標或讀取排除區。

#### `0xFE1C` 的條件式回呼請求

若上述路徑以 `a0=1` 進入 `0xFE1C`，它先將 1 寫入 `GP+291`，以 `0xFB5E` 呼叫 `0x90B0`，再以 `(callback=0xFB1E, argument=0, delay=500, a3=0)` 尾跳 `0x9124`。在前置呼叫正常返回、排程器找到項目且乘法不溢位等條件下，既有排程器換算為 800 ticks；若 installed slot 符合候選 WCH 625 微秒 tick，名義延遲為 500 ms。這是排程**請求**，不是成功、準時或已執行的證據。

若該回呼之後實際執行，`0xFB1E` 讀取 `0x2000BEDC`：值為 1 或 7 時，以 `0xFB5E` 尾跳 `0x90B0`；其他值則將 1 寫入 `GP+288`，並以自身為 callback、argument 0、delay 1500 再尾跳 `0x9124`。同樣的候選換算為 2400 ticks／名義 1.5 秒。這條後續路徑依實際狀態、呼叫、排程容量與 slot 契約成立；不證明回呼發生、永遠週期重複、mode 值或車輛功能。[檢查器](check-code64-callback-path.py)只核對原指令窗口與整數換算，不執行目標或讀取排除區。

`0x90B0..0x9124` 從數值位址 `0x2000BE08` 起，掃描最多 15 項、每項 12 bytes，以 offset 4 的 word 比較傳入的 callback；找不到時返回 1。找到第一項時，如 offset 8 非零會先透過 `0x40068` 呼叫，再將該項 offset 4／8 清零，並以 task byte 和 `1<<index` 尾呼叫 `0x4005C`。候選 WCH 標頭將兩槽分別定義為 `tmos_msg_deallocate` 與 `tmos_stop_task`；原機槽身分、釋放或停止是否成功仍未確認。

因此 `0xFE1C` 及 `0xFB1E` 傳給 `0x90B0` 的 `0xFB5E`，與之後送至 `0x9124` 的 `0xFB1E` 是不同 callback。這次按位址搜尋的直接目標是 `0xFB5E`，不能描述成直接搜尋 `0xFB1E`；也不能排除間接呼叫、別名或非同步作用。表項是否存在、內容有效、slot 是否相容及停止結果均未知，不能宣稱取消或排程成功。既有檢查器已加入此完整指令窗口。

`0xFB5E..0xFBA2` 同樣透過 `0xA9DE` 讀取 `0x2000BEDC`。若讀得 7，它寫入 `GP+288=2`、`GP+291=0`，並以自身為 callback、argument 0、delay 1500 尾跳 `0x9124`；若讀得其他值，則寫入 `GP+288=0`，以 `0xFB1E` 尾跳 `0x90B0`。這與 `0xFB1E` 會搜尋 `0xFB5E` 的路徑形成條件式的相互回呼搜尋；只有比較值 7 在兩邊的條件都出現，`0xFB1E` 額外包含值 1。

這些是各自被呼叫時的指令結果，依記憶體有效、slot 契約、沒有非同步覆寫且呼叫正常返回等條件；不代表兩者必然交替、排程或停止成功，也不證明兩個 GP byte 會改變 `0x1A078` 的 mode。檢查器已固定 `0xFB5E` 完整窗口。

#### 狀態值 2／3 的 record 消費路徑

原 `0xFBA2` 可讀取 `GP+288`。若先前 `0xFB5E` 寫入的值 2 保留至 `0xFC1E`，且 record、設定指標及之前分支均有效、無干擾，則 `0xFC90` 把 record offset 3 的 bits 2–3 設為二進位 `01`，將 `GP+288` 改為 3，並以 `(callback=0xFD3E, argument=0, delay=20, a3=0)` 呼叫 `0x9124`。依候選時鐘與既有換算，若排程成立為 32 ticks／名義 20 ms。

若 `0xFD3E` 日後實際執行，它先透過 `0x82A8` 取得一份 stack record；僅在該 record offset 2 非零時呼叫 `0xFBA2`。若進入 `0xFC1E` 時 `GP+288` 仍為 3，則 `0xFCB8` 清零該狀態及 record offset 3 的 bits 2–3，並令 offset 9 的高 nibble 加 1、以 byte 寬度回繞。後次 record 是否與先前 record 相同、複製及排程是否成功、是否送出，以及這些欄位的產品意義均未知；不能視為實機功能已重建，也不直接限制 `0x1A078` mode。[檢查器](check-record-consumer-state.py)固定允許的指令窗口及欄位運算，不執行目標或讀取排除區。

`0xFD3E` 傳入 `0x82A8` 的 index 是 13，後者要求槽 `0x4004C` 從數值 RAM `[0x2000C254,0x2000C260)` 複製 12 bytes 到 stack record。若此槽符合候選 copy 且兩端有效、無覆寫，這是當時該 RAM 區的快照；不能單憑同一來源地址認定它與前次 record 內容相同。

一個已辨識的寫入入口是 selector 1 的 record 分派樹：`0x14D5E` 讀 record offset 0 的 halfword，數值為 `1001 / 0x3E9` 時，經 `0x14ED8 → 0x14FA0 → 0x1522E`。後者以 `(a0=0,index=13,a2=record)` 呼叫 `0x82A8`，要求把 record 的 12 bytes 複製到同一 RAM 區；`0xFD3E` 的 `a0=1` 則要求反方向複製。這兩個方向與候選槽的對照依指標有效、正常呼叫、copy 契約及無非同步干擾成立；不證明 record 實際到達、兩次內容一致、該值是實體 CAN ID，或此為唯一 writer。

該寫入 helper 和 `0x1522E` 這段本身沒有檢查 record offset 2 的長度。後次讀取前若 source 沒有改變，offset 2 的數值才會延續原輸入；上游可能另有限制，不能據此聲稱所有 byte 值可達。數值上，檢查碼寫入 offset `length+2` 僅在 length **0–9** 時落在這 12-byte record 內；`0xFD3E` 的非零 guard 進一步只留 **1–9**。length 10–255 將指向該 record 之後，但沒有證明這些值可達、實際發生越界或缺陷。檢查器已納入寫入指令窗口及這項範圍運算。

將這條來源與下方已核對的固定 CAN 候選濾波表交叉比較：`0x3E9` 出現在 48 個 halfword 中的 **index 16**，左移五位為 `0x7D20`；按四項一組對應第 5 組的第一項。若固定表複製、候選 resident 槽、濾波器配置及 WCH 標準資料訊框解讀均成立，這支持 CAN1 是該 record 的一個可能來源，而非實際接收或唯一來源的證明。

依下方既有接收與 queue 證據，此候選 CAN1 路徑傳入的長度僅取低四位，條件式範圍為 **0–15**；若長度 byte 在所有複製與後續 RAM 讀取中保持不變，`0xFD3E` 的非零 guard 後為 1–15，其中 1–9 的檢查碼目的位於 12-byte record 內、10–15 位於其後。這仍不證明後六種值可由硬體產生或實際到達該分支，也不排除其他來源或 writer。[固定表檢查器](check-counter-can1-fixed-filters.py)已核對該表項及編碼。

#### Queue 前置檢查與長度的關係

queue 在 `0x12CB0` 呼叫 `0x82D2`，只有返回 0 才可能繼續進 dispatcher。`0x82D2` 依序檢查以 `0x2000C794+4*i`（`i=0,1`）為基址的兩項：該基址 offset 2 halfword 不等於 `0xFFFE`、offset 5 byte 等於 2、offset 4 byte 非零時，此項符合條件。若兩次讀取穩定、相關呼叫正常返回且保存暫存器未受干擾，只要任一項符合，返回值即為非零；即使 record 長度大於 8，`0x832C` 在長度分支前已保存非零值。因此此 queue 路徑要繼續至 `0x3E9` dispatcher，**兩項都須不符合上述條件**。

這是上述普通入口的條件式必要條件，不能排除其他 dispatcher 入口或設定被覆寫；也不能以「長度大於 8」單獨推出 record 一定被拒絕：兩項皆不符合時仍可返回 0。實際設定、record 與可達性未知。[檢查器](check-record-queue-gate.py)固定兩段允許的指令窗口，不執行目標或讀取排除區。

#### 與 `0x1A638` 前置檢查共用的狀態

下方六-byte 比對路徑呼叫的 `0x838E`，與 queue 的 `0x82D2` 皆檢查同一數值基址 `0x2000C794`、同一個 4-byte stride 的兩個索引，使用相同的 halfword sentinel、type 與非零 byte 條件。若兩次呼叫所見設定相同、讀取有效、所有相關呼叫正常返回且暫存器未受干擾，兩條路徑只有在**兩項均不符合**時才會分別從這兩個前置函式獲得 0；因此這組狀態是兩條已辨識路徑通往後續 `0x1A078`／`0x1A638` 處理的共同條件，而不是單靠任一表格可解決的依賴。

這些被讀取的數值位址位於 reset 清零範圍 `[0x20004080,0x2000C958)`。若 reset 清零完成、記憶體映射有效，且之後至兩次讀取前完全沒有其他寫入，兩項的 type／flag 都為 0，不符合啟用條件，兩個前置函式可返回 0。這不證明實機 reset、初始化後仍為 0、兩次呼叫或後續查表必然發生；兩次也可能看到不同狀態。[交叉檢查器](check-shared-precheck.py)固定兩個允許的指令窗口及地址算術，不執行目標或讀取排除區。

原 `0x13BA6..0x13BD2` 是一個已辨識的 type 寫入入口：它以完整 32-bit `a0` 依序與 `0x2000C796`、`0x2000C79A` 的 unsigned halfword 比較，選中第一筆相符項後，將 `a1` 的低 byte 寫到該項 type（分別為 `0x2000C799`、`0x2000C79D`）；若都不相等則不寫。兩個 halfword 都相等時只寫第一項。這些局部比較可相等的 `a0` 數值必為 0–65535，但沒有證明呼叫入口、全域值域或這是唯一 setter。

此函式自身沒有直接寫入兩項的 flag bytes `0x2000C798`／`0x2000C79C`；因此單次把 type 寫為 2 不足以證明該項符合全部條件。若設定確實仍是 reset 的全零狀態，輸入 `a0=0` 會命中第一項，但兩個 flag 仍為零；其他 writer、alias、重入及呼叫副作用依然未知。交叉檢查器已固定此函式的完整指令窗口。

另一個已辨識入口 `0x13E0E..0x13E98` 使用相同的兩個 halfword／flag／type 數值位置。當完整 `a1=1` 且完整 `a0` 符合其中一個 unsigned halfword，它選擇第一個相符項，將該 flag 寫為 1、type 寫為 0。接著若以相同 `a0`、`a1=2` 呼叫前述 `0x13BA6`，且該 halfword 不是 sentinel `0xFFFE`、兩次間狀態不變及呼叫正常完成，該項便同時滿足兩個前置函式的三項啟用條件。順序重要：反向執行會由 `0x13E0E` 將 type 再清為 0。

此入口在 `a1=2` 時會選第一個 sentinel 空項，寫入 `a0` 低 halfword，並清除該項 flag／type；其他 `a1` 路徑可對匹配項寫入 sentinel 並清除 flag／type。這些局部靜態寫入不能證明呼叫順序或實機設定。[交叉檢查器](check-shared-precheck.py)固定了指令窗口。

**初始化線索：** main 在 `0x9278` 呼叫 `0x14C8A`。此函式向尚未確認契約的 `0x40048` 槽請求以零填寫 `0x2000C794` 起 10 bytes；間接呼叫正常返回且 `s0` 保持不變時，後續明確把 `0x2000C796`、`0x2000C79A` 寫成 `0xFFFE`，把 `0x2000C798`／`0x2000C799` 和 `0x2000C79C`／`0x2000C79D` 清零。這支持兩個共用前置設定的條件式初始化，但不證明實機曾執行或之後狀態不被改寫；間接槽內容仍未知。交叉檢查器固定 `0x14C8A..0x14CC8`，未讀取排除區。

**候選 fill 與另一個閘門：** 兩份 WCH 候選映像的 `0x40048` 均指向 `0x2000039C`，且對應的 46-byte 指令本體逐 byte 相同。其完整路徑先保存並清除數值位址 `0x4002420C` 的 word，執行 byte fill 迴圈後恢復該 word；若實機槽與候選一致、目的和控制位址有效、正常返回且無干擾，這次呼叫會把 `[0x2000C794,0x2000C79E)` 填零，包括前述直接 stores 未涵蓋的 `0x2000C794`／`0x2000C795`。該控制位址的硬體意義與副作用未確認。

另一入口 `0x13BD2` 先讀 `0x2000C794`，非零立即返回；為零時才逐項檢查 halfword 非 `0xFFFE`、type 為 **4** 且 flag 非零，符合者以該 halfword、`0xD1`、輸入指標加 3 和長度 8 呼叫 `0x8A56`。在上述初始化完整結束、狀態未被改寫等條件下，閘門雖為零，兩項仍因 sentinel 而不會進入這個呼叫。這是靜態條件式結論，不代表裝置實際狀態、此分派的產品功能或其唯一呼叫入口。交叉檢查器固定了閘門函式與候選 fill 全部指令證據。

`0x8A56` 的已辨識路徑進一步限制此 type-4 請求：長度必須不大於 `0x40F`（此處固定為 8），輸入 halfword 必須符合 `GP+150` 或 `GP+154` 的非 sentinel 項，且由 `0x4013C` 呼叫所返回的完整值必須**恰為 1**；第一槽不符合時可再檢查第二槽。WCH V1.30 標頭將該槽對應為 `GATTServApp_ReadCharCfg(handle, table)`，將 1 定義為 notify、2 定義為 indicate。因此若實際 slot／ABI 與該候選一致，這是依候選通知設定篩選，但回傳 3 即使包含 notify bit 也不符合此處的等值比較。打包後程式向 `0x40050` 槽提出 `(選定槽的 task byte, 1)`；WCH 將它對應 `tmos_set_event`，仍不證明事件實際排程、封包傳送或硬體行為。[檢查器](check-type4-notify-candidate.py)固定 APP 窗口與本機官方標頭，不讀排除區。

一個已辨識的清除呼叫來自 `0x8B90`：入口 `a0` 為 2／3 時，要求輸入 offset 2 為 6，並將 offset 4 halfword 與 `GP+150`、`GP+154` 依序比對。匹配時先將對應 GP halfword 設為 `0xFFFE`，再呼叫 `0x8B6E(1)`；正常返回後，`0x8C70` **重新讀取**輸入 offset 4，以該值和 `a1=0` 呼叫 `0x13E0E`。若 fresh 值仍與上述共用設定的某個 halfword 相符，後者會將第一個相符項設成 sentinel 並清除 flag／type。

這串連了特定輸入事件與兩項共用前置設定的條件式清除，但中間呼叫可能改寫記憶體，兩次讀值不保證相同；輸入格式、slot 契約、實機事件及全域初始化仍未證明。不要因此認定該事件已經發生，或它是唯一清除入口。交叉檢查器已固定入口與呼叫指令。

#### 與 WCH GAP 連線終止事件的候選對照

原 `0x19DE0` 三個 word 為 `[0x8B90,0,0x85C8]`；`0x8872..0x8884` 從 `0x401A4` 取目標，將該表當作第三參數、第二參數設 0 後呼叫。固定版 WCH V1.30 標頭將此槽定義為 `GAPRole_PeripheralStartDevice`，第三參數是 `gapRolesCBs_t`；其第一欄是接收 `(newState,eventPointer)` 的 state-change callback。這與表的第一個 word 和 `0x8B90` 的兩個輸入形狀相符，但仍須實機槽、ABI、註冊及生命週期相容。

同一標頭將 `0x06` 定義為 `GAP_LINK_TERMINATED_EVENT`，其事件結構含兩-byte header、opcode，再接 16-bit connection handle。若採候選結構及 RV32 對齊，opcode 位於 offset 2、handle 位於 offset 4；這與 `0x8C3E`／`0x8C48` 讀取相符。入口狀態 2／3 在該標頭分別名為 advertising／waiting。因此這條清除路徑可**條件式推論**為連線終止後清除對應項目，而非已觀察的斷線事件；兩次 handle 讀取間可能被改寫的限制仍成立。[檢查器](check-gap-disconnect-candidate.py)固定允許的 APP 窗口與本機 WCH 標頭，不執行目標或讀取排除區。

同一候選對照也解釋了相鄰操作：`0x8B6E(1)` 透過 `0x40174` 傳入 `(0x305,1,&byte_1)`；WCH 將該槽定義為 `GAPRole_SetParameter`、`0x305` 定義為廣播 enable。若 slot 與介面相容，這是**要求啟用廣播**；原 caller 沒有依其返回碼決定是否繼續清除項目，不能證明廣播實際啟用。

另一分支要求入口 state 為 4、事件 offset 2 為 5，從 offset 10 讀 halfword，寫入第一個可用的 `GP+150/154` 項目；隨後以該值和 stack 中的 `247` halfword 呼叫 `0x400D8`。WCH 將 state 4／opcode 5 分別列為 connected／link established，並將該槽定義為 `GATT_ExchangeMTU`；按候選結構及 RV32 對齊，offset 10 是 connection handle。這支持「連線建立後提出 MTU 247 交換請求」的條件式解讀，不證明 slot、連線、請求成功或協商結果。沒有讀取裝置資料或執行藍牙操作；既有檢查器已納入相關窗口及標頭宣告。

#### 候選連線槽的 APP 初始化

原 reset 的清零範圍包含 `GP+150`、`GP+154`（以 GP=`0x20004000` 計）；這只給出清零完成時的條件式值。之後正常主初始化在 `0x9268` 呼叫 `0x8E88`；其 `0x8F7A` 設 `s1=-2`，`0x8F90` 和 `0x8FA6` 分別將 `s1` 低 halfword 存到這兩個位置。若所經間接呼叫均正常返回並保存 `s1`／GP、沒有中斷或 alias 改寫，兩槽在第二次 store 後為 `0xFFFE`，與連線建立分支選空槽的 sentinel 相符。

這補上 reset 零值到候選空槽標記的靜態銜接，不能證明初始化已完成、兩次註冊成功或 callback 不會在兩次寫入之間觸發；另一組共用前置設定的初始化證據須看上方 `0x14C8A` 路徑。既有檢查器已固定主初始化和兩次 store 指令。

進一步追蹤 `0xFCB8` 之後的控制流：前段高 nibble 加 1 後，`0xFCE6` 還會再加 1；若接著讀得 `GP+289=2`，則 `0xFD1A` 在 `0xFCE6` 前再加一次。因此在 record 穩定且正常到達檢查碼呼叫前，offset 9 高 nibble 共增加 **2 次**，或在該特殊分支增加 **3 次**，各以四位元回繞；上段所述一次僅為 `0xFCB8` 的局部效果。

`0xED00` 正常返回後，程式將結果寫到 record offset `length+2`，其中 length 是呼叫前記住的 offset 2 byte。若 length 為 7，此寫入會覆蓋 offset 9，故不能把上述增加值直接當作最後內容。這些是有界指令與位址運算；長度實際值、buffer 效果、呼叫返回和傳送均未實測。檢查器已加入相關窗口。

進一步核對普通入口：`0x829E` 直接讀取 byte `0x2000BFB5`；`0x14D3C` 對大於 6 的值走另一出口，否則以此值索引 `0x1A6B8` 起的七項 32-bit 相對跳轉表。原始表在索引 1 指向 `0x14D5E`，其餘六項指向其他入口。因此，若從 `0x14D2E` 正常進入、該 byte 與表資料穩定且間接跳轉按原始規則執行，前述 `0x229` 分派樹需要選擇 byte 為 **1**。這不是全域唯一入口或實際狀態的證明；沒有讀取排除的 `0x1A69C..0x1A6A0` 資料。

直接寫入點 `0x1074C` 將 incoming `a0` 保存在 `s0`，經四個原始呼叫後，在 `0x10766..0x10776` 將 `s0&255` 寫入 `0x2000BFB5`；該寫入點沒有 0–6 範圍檢查。它需要前置 callees 正常返回並遵守 `s0` 保存契約；`0x1077A` 以後還有其他呼叫及條件分支，不能假設整個 setter 的副作用只有這一筆。

`0x2000BFB5` 亦在 reset 清零區 `[0x20004080,0x2000C958)` 內，因此清零正常完成且無干擾時在 `0x186F8` 為 0；要由此狀態走到上述 selector 1 分支，之後須有寫入或別名作用使該 byte 變成 1。這些局部事實不能證明 `0x1074C` 是唯一寫入者、其輸入實際值域或某次實機 record 一定走何分支。

對正常 dispatcher 入口的具體限制：若 `0x829E` 讀得的 selector 大於 6，`0x14D3C` 轉至 `0x1549A`；後者還原 dispatcher frame，設 `a0=0` 並尾跳 `0x1074C`。若這些指令與 setter 的前置呼叫正常完成、`s0` 保存且沒有干擾，該路徑會把 selector 寫成 0；但同時也會執行 setter 的其他呼叫，不能簡化為純粹的 byte clamp。這是讀到超範圍值**之後**的一條修正路徑，不能證明所有讀取前 selector 均為 0–6、全部錯誤入口都會執行該路徑，或實機真的發生過修正。

## 追查 `0x14056` 的接收參數

V4.1.60 原始指令 `0x8A3A` 的 `AUIPC a2,0x20003` 加上 `0x8A3E` 的 `ADDI a2,a2,-98`，得到 `0x2000B9D8`。在 `0x8A12..0x8A1C`，另一組 PC-relative 計算得到同一 base，將接收 byte 寫入 base 加計數器。這支持 `a2` 是接收 buffer 的推論，並非實機 RAM 快照。

`0x89C2` 與 `0x89D6` 組成 GP+142 的 16-bit 長度；`0x89E0..0x89E4` 的正常解析路徑對大於 1040 的非零值轉入清除狀態，零長度另行處理。`0x8A2A..0x8A32` 的狀態及 checksum 比較通過後，`0x8A36` 才重新讀取該欄位傳入 `a3`。因此 0–1040 是正常長度解析路徑的條件範圍，**不是已證明所有入口、別名寫入、中斷或跨回呼後都成立的全域不變條件**。`a1` 是 GP+164 的 byte，不能僅依此斷言具體命令語義。

這些結果與既有 [GATT 接收模型](../tsl9-v4160-gatt-ingress-model/README.md)一致；該模型採合成 provider，不能證明 `0x14056` 內部或硬體行為。本輪未讀取排除的函式本體。

### 到達呼叫點的框架結構

依 `0x8962..0x8A48` 的正常狀態機，框架起始依序檢查 `0x55`、`0x7F`，接著讀取一個 command byte、兩個以高 byte 在前組成的長度 bytes、指定數量的 payload bytes，最後將收到的 checksum byte 與累加值比較；兩個前導 bytes 不納入累加。從讀取 command 開始，原程式對 command、兩個長度 bytes 及 payload 做低 8-bit 加總。若長度為 0，直接等待 checksum；長度 1–1040 走 payload 路徑，大於 1040 的正常解析長度會清除解析狀態。

只有狀態及 checksum 比較通過，`0x8A36..0x8A48` 才在此路徑將當時 context、command、固定 buffer 和重新讀取的長度交給 `0x14056`。在 GP／buffer 有效且沒有 alias、回呼間覆寫或其他非同步干擾等條件下，這支持「命令＋長度＋payload 的 byte-sum 封包」解讀；它不是加密完整性、完整指令表、已授權 API 或真實 BLE 執行證據，也不能推定排除本體的分派與副作用。

#### 零長度框架與 buffer

若正常解析的兩個長度 bytes 都為零，`0x89DA..0x89DE` 直接進入 checksum 狀態，沒有經過 `0x8A12..0x8A1C` 的 payload 寫入。此前加總在第二個前導 byte 後歸零，故在沒有干擾的條件下，零長度框架的正確 checksum 等於 command byte。驗證通過時，呼叫點仍傳入固定 buffer `0x2000B9D8` 和重新讀取的長度 0；這條零長度流程本身不清空 payload buffer，也不證明它的舊內容。

`0x14056` 正常返回後，呼叫端 `0x8A4C` 才將 parser state 清為 0。前述結論依賴呼叫期間 state／長度／buffer 未被 alias、其他回呼、IRQ 或 DMA 改寫，亦不證明空框架一定可達、函式會讀取 buffer、返回成功或任何命令的實際語義；排除本體仍未讀取。

#### 分段解析的時鐘邊界

解析器在每次普通資料呼叫開始時由 `0x81B0` 取得值 `now`，比較 `(now - *(GP+160)) mod 2^32`；若大於 299，`0x891A` 清除 parser state，然後才保存 `now` 並開始處理該次片段。若間隔檢查及其他記憶體條件允許，跨呼叫維持的 parser state 可接續；`0x8900` 將這次入口的 `a0` 存於 `s3`，因此 checksum 完成時送到 `0x14056` 的 `a0` 是**完成該框架的那次呼叫之 context**，不必然是開始框架的 context。

`0x81B0` 使用 `f(x)=((x*10)&0xFFFFFFFF)>>4`，與下文既有時鐘截斷證據相同。若上一次保存值恰由 `x=429496729` 形成，且下一次 slot 回傳 `429496730`，兩次 `f` 分別是 `268435455` 與 `0`，原無號差是 `4026531841 > 299`，故該次會清除原有 parser state。若實機槽確與候選 WCH 0.625 ms tick 相容，這個例子只跨一 tick；仍不能因此聲稱實機曾出現錯誤或特定框架一定失敗，因 slot 身分、連續取樣、前次保存值、可達性及無干擾均未確認。若 state 已為 0，這次清除也沒有額外狀態差異。

[檢查器](check-ingress-clock-boundary.py)只讀取允許的指令窗口、直接解碼 `0x8916` 分支並檢查九個算術邊界；不執行目標或讀取被排除的 `0x14056` 本體。

#### 候選 WCH 寫入 callback 的長度上界

原始 `0x19DFC` 的三個 little-endian word 是 `[0, 0x888C, 0]`。本機保存的 [WCH V1.30 標頭](https://github.com/openwch/ch32v20x/blob/ec059e0b18046b111ee850e44f105fcd095e775c/EVT/EXAM/BLE/LIB/wchble_rom.h)將 `gattServiceCBs_t` 的第二個欄位定義為寫入 callback，並將它的 `len` 宣告為 `uint16_t`。若該表確實按此結構註冊、實機使用相容的 callback 介面及 RV32 參數擴展慣例，則 `0x888C` 的 `a3` 長度為 **0–65535**，`a0` connection handle 也為 0–65535。

`0x8904` 把完整 `a3` 保存到 `s2`；`0x8938..0x893E` 每次以 index 的低 16 bits 與完整 `s2` 比較。在上述候選 ABI、迴圈暫存器保存正常且每次處理都能返回的條件下，單次 callback 至多處理 65535 bytes，不會因 index 的低 16-bit 回繞而使這個迴圈持續。這不證明實際 BLE 資料可達此長度、輸入 buffer 有效、callee 一定返回或 `0x14056` 的 payload 長度界限；後者仍受前述正常框架的 1040-byte 檢查及 fresh read 條件約束。若實機 ABI 不同或存在其他入口，不能套用此上界。

[檢查器](check-gatt-callback-bound.py)讀取指定的本機 V1.30 標頭與兩個允許的 BIN 窗口，核對 callback 型別、指標表及迴圈分支；不下載、執行目標或讀取排除區。

#### 原 APP 將 callback 表交給候選服務註冊槽

[既有完整註冊分析](../tsl9-resident-gatt-registration/README.md)將上述表追到原 APP 的 `0x8FB8..0x8FCC`：在進入函式時 `s0=0x40000`、其後所有呼叫均正確保存 `s0` 的條件下，程式從 `0x40130` 讀取間接目標，傳入 `a0=GP`、`a1=4`、`a2=16`，並以 `0x8FBC` 的 PC-relative 運算形成 `a3=0x19DFC`，於 `0x8FCC` 呼叫。這是原始指令的資料流；它強化了該三-word 表用作 callback 表的候選解讀。

WCH V1.30 標頭將 slot 63（`0x40034+4*63=0x40130`）定義為 `GATTServApp_RegisterService(pAttrs,numAttrs,encKeySize,pServiceCBs)`；候選原機執行層的該槽另指向 `0x4CF22`。若 installed slot、介面與記憶體均相容，這次呼叫可解讀為以四筆 attribute、key-size 參數 16 和該表請求註冊。`0x8FCC` 返回後 `0x8FCE` 直接繼續下一項工作，沒有在此處依返回碼分支；不能把發出呼叫視為註冊成功，也不能由 key-size 數值證明實際連線已加密。候選 wrapper 在部分狀態下還可能先完成核心註冊，再因 callback 節點配置失敗而返回錯誤；詳見既有分析。

只有註冊成功、指標生命週期有效且 installed ABI 相符時，上節 `uint16_t` callback 上界才可套到該候選路徑。未讀取排除區、連線裝置或測試實機服務；[獨立覆核器](check-key-control-flow.py)核對原始槽讀取、PC-relative 指令及呼叫。

#### 兩份候選 resident 映像的槽位差異

本機保存的兩份官方候選 Intel HEX 經記錄 checksum 核對後，`0x40034` 所指的版本字串分別為 `CH32V20x_BLE_LIB_V1.31` 與 `CH32V20x_BLE_LIB_V1.40`；兩者 `0x40130` 槽分別包含 **`0x4CF22`** 與 **`0x4CFBA`**。前述 V1.30 是參考 **標頭**版本；其所搭配保存的 2023 年候選 HEX 版本字串是 V1.31。槽位地址相同而目標不同，不能把 `0x4CF22` 硬編碼成跨版本或原機的實際入口。

這是兩個保存檔的內容比較，不證明任一映像已安裝在裝置，也不證明新舊兩個目標內部行為或 ABI 完全相同。[檢查器](check-gatt-resident-versions.py)接受兩個本機 HEX 路徑，固定檔案雜湊、驗證 Intel HEX 記錄 checksum，並只保留選定的版本、槽位、loader 與本體 bytes；不連線、不產生韌體。

#### 與六項依賴相關的候選槽與 RAM 本體

相同兩份候選 HEX 中，WCH 標頭對應的 `tmos_memcmp`／`tmos_memset`／`tmos_memcpy` 槽 `0x4003C`／`0x40048`／`0x4004C` 在兩版分別都存放 RAM 目標 `0x20000442`／`0x2000039C`／`0x20000332`。依各版 loader 的來源與目的運算，V1.31 的第一段 copy 從 `0x402B0` 複製至 `0x20000040`，V1.40 則從 `0x402F0` 複製至相同 RAM 位置；因此這三段 RAM 本體在兩版 HEX 的來源地址相差 `0x40`。對應的 72-byte 比較、46-byte fill、58-byte copy 三段，分別在兩個保存檔之間逐 byte 相同。

相對地，計時／註冊的三個槽在候選 V1.31 → V1.40 的目標分別為：`0x40058`：`0x43728 → 0x437B4`、`0x4007C`：`0x43520 → 0x435AC`、`0x40080`：`0x43C4E → 0x43CDA`。這支持依槽位與已確認版本分析，而非把 flash 實作地址當全域常數。

[同一檢查器](check-gatt-resident-versions.py)核對兩版 loader 窗口、來源立即數、七個槽及三對本體雜湊；它不執行 loader。三段來源位元組一致不證明實機 RAM 已被複製、實際 slot 值或 ABI 相同，也不涵蓋其他 resident 版本和周邊副作用。

#### 兩版啟動第二次 copy 的來源缺口

依兩版 loader 指令與既有 inclusive-word copy helper 契約，V1.31 第二次 copy 要求來源 `[0x6EAA4,0x6EB30)` 共 140 bytes，但保存的 HEX 缺少最後 `[0x6EB2C,0x6EB30)`；V1.40 要求來源 `[0x6EC94,0x6ED24)` 共 144 bytes，其保存 HEX 也缺少最後 `[0x6ED20,0x6ED24)`。其餘各自請求的 136／140 bytes 在各自 HEX 中有記錄。這裡比較的是**檔案記錄覆蓋**，沒有填入缺口或讀取其不存在的值。

兩個版本隨後的 zero 都覆蓋該次 copy 的最後一個目的 word：V1.31 為 `[0x20002EF8,0x20002EFC)`，V1.40 為 `[0x20002F48,0x20002F4C)`。然而 copy 在 zero 之前仍需嘗試讀取來源；最終目的會被覆寫，不能證明先前讀取有效或啟動必定成功。[檢查器](check-gatt-resident-versions.py)逐筆驗證 HEX checksum，檢查兩個來源範圍的記錄覆蓋與缺口；實機 Flash 是否包含這些 bytes、記憶體映射與 loader 能否完成仍未知。

#### APP 的 resident 版本前綴守衛

原 APP 初始化 `0x199F4..0x19A08` 從 `0x4003C` 取得比較目標、從 `0x40034` 取得候選版本字串指標，以 `0x1AB1C` 的 **21 bytes** 為比較值後呼叫；原始 bytes 為 `CH32V20x_BLE_LIB_V1.3`，不含後續 NUL。比較返回非零時跳到 `0x19A0A`，返回零則進入 `0x19A08` 自我迴圈。

前述 V1.31 候選字串的前 21 bytes 與 APP 前綴相同；V1.40 在第 21 個 byte 不同。若各候選 loader 已正確載入相同的比較本體、slot／指標有效、以既有候選 BOOL 相等慣例執行且無干擾，兩者將分別取得非零／零結果，因而走不同分支。這是條件式靜態比對，不證明實機安裝版本、比較呼叫曾執行或實機一定卡住；中斷、重置及其他外部效果亦未排除。兩份 HEX 的版本字串、APP 前綴及比較本體可由[版本檢查器](check-gatt-resident-versions.py)核對；[獨立指令覆核](check-key-control-flow.py)檢查原始比較與分支。

原 APP 的 `0x8E88` 在 `0x8EA8` 呼叫上述版本守衛 `0x199E2`，正常返回後才繼續 `0x8EAC` 等初始化步驟；前述 GATT 註冊呼叫位於同一函式稍後的 `0x8FCC`。因此若比較返回零，控制留在 `0x19A08` 自我迴圈且沒有中斷／重置等外部控制流改變，這條正在執行的初始化路徑無法走到 `0x8FCC`，也就不能藉該次呼叫註冊 `0x888C` callback。V1.31 的前綴相符只容許繼續，不證明其後各步成功；也未排除其他註冊入口、IRQ 或實機版本差異。

#### Payload 寫入範圍與 reset／RAM 的交叉檢查

每次走到 payload 分支時，`0x89FA` 以 unsigned halfword 讀取 counter；`0x89FE..0x8A02` 對 counter 大於 1039 的情況轉至清除 state 的路徑，不執行這次 payload store。通過後，`0x8A12..0x8A1C` 使用同一暫存器中的舊 counter，向 `0x2000B9D8+counter` 寫入一個 byte。因此在正常指令流程、暫存器未受干擾的條件下，這一個 store 的位置必落在 `[0x2000B9D8,0x2000BDE8)`；這個局部界限獨立於重新讀取並傳給 `0x14056` 的長度值，不保證被呼叫函式本身的讀寫範圍。

此 1,040-byte 窗口完整位於 APP reset 的清零範圍 `[0x20004080,0x2000C958)` 內；parser counter、length、state 及 checksum 的 GP-relative 欄位也位於該清零範圍。若 reset 清零正常完成且沒有干擾，這些欄位和窗口在 `0x186F8` 時為零；後續接收與其他路徑仍可改寫，不能推論某次呼叫時 buffer 為零。依既有 WCH 三種候選連續 RAM 配置，此窗口落在 48／64 KiB 數值範圍內，不在 32 KiB 範圍；但完整 reset 清零本身超過 48 KiB，因此不能單憑此窗口選定整體 RAM 配置。實際 RAM 映射、正常開機與呼叫仍未證明。[靜態檢查器](check-ingress-buffer-bound.py)核對相關原始指令與範圍，不執行目標或讀取排除區。

進一步與既有完整 clock CPU-store 收據及候選 bootstrap 寫入範圍交叉檢查：那些**已辨識的明確寫入位址**均不與上述窗口或四個 parser 欄位重疊。若記憶體映射與候選 resident 內容相符、兩份既有分析的指令及 helper 契約成立、clock 正常返回且所有載入有效，並且沒有 MMIO 引起的間接寫入、IRQ／DMA／alias／重入等干擾，則 reset 的零值可條件式延續至已分析 bootstrap 的 MRET。候選第二次 copy 仍缺來源四 bytes，不能因目的範圍不重疊就假定讀取成功；此結果也不涵蓋 MRET 之後的 APP 執行或第一次接收時的狀態。檢查器固定兩份既有收據雜湊，只核對明確寫入範圍，沒有重跑目標。

## `0x1A69C` 與設定預設值

原 `0x131A6..0x131B4` 每次從 `0x4004C` 載入間接目標，傳入目的 `*(GP+0x54)+12`、來源 `0x1A69C` 與長度 4。既有 [SDK 複製函式核對](../tsl9-resident-copy-arch/README.md)指出候選槽值為 `0x20000332`，其 58-byte 本體以來源／目的／長度執行順向 byte 複製，並先存取 `0x4002420C` 與執行 `FENCE.I`。

依[設定初始化分析](../tsl9-original-prebinding-settings/README.md)，若 reset 所設 GP 與初始 pointer 未被改寫，目的為 `0x2000C2A8..0x2000C2AC`；其初始化路徑會檢查四個 byte 是否為 ASCII 32–126，遇到不符合條件者可進入預設值流程。**若**原機槽確為該候選、來源／目的有效且呼叫正常返回，則四個來源 bytes 會被複製到此目的範圍。這不證明預設內容、實際設定語義、每次開機都執行該路徑，或實機 ROM／Flash 寫入結果；排除資料內容未讀取。

### 預設資料目的指標的局部限制

`0x131A0..0x131B4` 直接從 `GP+84` 載入 word `p`，以 RV32 加法傳入目的 `(p+12) mod 2^32`；此片段沒有先檢查 `p` 是否為 0。候選 copy 在處理參數之前仍先存取 `0x4002420C` 並執行 `FENCE.I`，之後才判斷**加法後的目的**是否為 0。

因此，若 `p=0`，傳入的目的數值為 `0x0000000C`，不會被候選 copy 的零目的檢查擋下；若 `p=0xFFFFFFF4`，加法回繞後目的才是 0，候選 copy 會跳過資料複製。前者只有在候選 slot、來源與 MMIO 等條件相符且控制流程繼續時才會嘗試存取該數值目的；不能據此宣稱實際 RAM／Flash 映射、故障或此指標值可達。重建不得把「原始 pointer 為 0」等同於此候選 helper 的 null guard。這些邊界不揭露或推導排除的四 bytes；[檢查器](check-default-copy-pointer-guard.py)只核對原始呼叫與候選 copy 的有限指令窗口。

`0x1ABB4` 的初始 word 為 `0x2000C29C`；在 reset 以 GP=`0x20004000` 正常複製初始資料且 pointer 未被覆寫時，`*(GP+84)+12` 即 `0x2000C2A8`。當任一受檢 byte 不在 32–126 時，`0x13204` 呼叫 fallback `0x1316A`：先以槽 `0x40048` 要求清零 `0x2000C29C` 起 112 bytes，寫入若干固定欄位，再透過 `0x4004C` 要求從 `0x1A69C` 複製 4 bytes；最後尾跳 `0x13138`，要求把設定區 112 bytes 複製至 stack，並呼叫 `0x9C0A`，數值目的為 `0x08077A00`。

這條 fallback 在四-byte copy 後沒有重新執行 ASCII guard；在不知道來源 bytes 時，不能證明 fallback 結果符合 32–126。其寫入器之後的候選 program leaf 會讀取 256-byte stack 來源，而此 writer 僅明確複製 112 bytes；其餘 144 bytes 的初始化來源仍未知，詳見 [NVM 區域分析](../tsl9-NVM-record-layout/README.md)。槽身分、記憶體有效性與實際持久化成功皆未確認；沒有讀取或輸出排除資料。

#### 下次載入的條件式取值限制

假設候選 copy 槽確實逐 byte 複製、此次設定的四個預設 byte 成功且原樣持久化，下一次載入也原樣複製到相同位置，且指標、記憶體與控制流程均正常並無干擾，則四個來源 byte **全部在 32–126** 是下一次通過這項 ASCII guard 的必要且充分條件。只要任一 byte 不在該範圍，該次 guard 便走 fallback；這不證明來源確實有不合規值、實際會再次開機或發生重複寫入。

單一 byte 有 95 個可通過值；四 byte 組合為 `95^4 = 81,450,625` 種，僅是 guard 接受集合的大小，不是已知預設值或產品語義。真實來源仍是未解析且受排除的四 bytes，不能由此選出值或建立 provider。[檢查器](check-default-persistence-guard.py)固定允許的指令窗口並枚舉全部 byte 值，不讀取排除區或執行目標。

同一套本機保存的 WCH 公開候選 `wchble_rom.hex`（SHA-256 `11d849ac3333535b31dae1941afd8d59fa99ad7760de5c1e64bdfcc8c0024bb5`）經 Intel HEX 記錄 checksum 檢查後，其資料記錄最小位址為 `0x40000`，最大半開端點為 `0x6EB2C`；數值區間 `[0x77500,0x77B00)` 沒有資料記錄。六個設定頁使用的高位數值 `[0x08077500,0x08077B00)` 若減去 `0x08000000` 恰得到該區間，但**這個算術不證明硬體 alias**。

此交叉檢查只描述該參考 HEX 的記錄覆蓋，不表示實機該區空白、已擦除、保留或可寫，也不補足候選啟動所缺的資料或證明 installed ROM／Flash 配置。實機映射與容量仍待獨立證據；沒有讀取裝置 Flash。

#### 與兩版 resident 參考資料的數值關係

V1.30 標頭註解列出 CODE `0x00040000..0x0006FFFF`，但預設巨集另定義 `LIB_FLASH_BASE_ADDRESSS=0x40000`、`LIB_FLASH_MAX_SIZE=0x40000`；若僅作半開區間算術，後兩個值形成 `[0x40000,0x80000)`。只有再假設 APP 的高位 `0x08000000` 為對應 alias 時，六個設定頁 `[0x08077500,0x08077B00)` 才會數值對應 `[0x77500,0x77B00)`：它在前述巨集最大範圍內，卻位於標頭註解 CODE 範圍之後。這兩種標示的意義不能由算術自行統一，也不能因此判定該頁已保留、可寫或不與其他用途重疊。

對兩份已保存的 V1.31／V1.40 候選 Intel HEX 逐筆核對後，上述低位設定頁範圍均沒有資料記錄；兩份檔案資料記錄的最大半開端點分別是 `0x6EB2C`／`0x6ED20`。這只說明**兩份檔案**的覆蓋，不代表原機 Flash 該處空白或頁面安全；宏可被建置設定覆寫，實體容量與 alias 仍未知。[檢查器](check-nvm-candidate-map.py)固定 V1.30 標頭與兩份 HEX，檢查巨集、記錄 checksum 及地址覆蓋，不讀取裝置或排除的 APP 預設資料。

## `0x1AB48` 查表結果的局部用途

在 `0xA146..0xA158`，程式以 `uint8(GP+176)` 作索引，讀取 `0x1AB48+2*index` 的無號 16-bit 值 `x`。該路徑的 `0xA15C..0xA166` 計算 `y=(x+0x802)&0xFFFF`；`0xA16C` 將 `y` 的低 8 bits 寫到 `SP+10`，而 `0xA168..0xA18E` 將 bits 8–11 寫到 `SP+9` 的低 nibble，保留其高 nibble。因此兩欄合起來是 `(x+0x802)&0xFFF`，若以稍後 `a0=SP+4` 為緩衝區起點，它們分別是 offset 6 與 offset 5 的低 nibble。

`0xA1A8` 再以 `a0=SP+4`、`a1=7` 呼叫 `0xED00`。該完整函式讀取 buffer 前兩個 bytes 相加作初始值，依 offset 2 的 byte 長度逐一加上 offset 3 起的資料，略過索引 7，運算保留低 8 bits；`0xA1AC` 將返回 byte 寫到 `SP+14`，即 buffer offset 10／資料索引 7，接著 `0xA1B2` 呼叫 `0x12A08`。在有效 buffer、無干擾且該路徑正常完成時，這支持把 `0xED00` 的結果視為加總檢查碼；不能由此確定協定、單位、實際傳送結果或產品功能。參見[既有 checksum 對照](../tsl9-feature-callback/README.md)。

上述是經此查表路徑的靜態資料流；指標有效、stack 未被 alias／非同步覆寫、callee 正常執行仍是條件。查表索引與後續欄位只分別具 byte、12-bit 的保守範圍，不能由此證明索引全域為 0–3 或宣稱四筆資料即完整表格。

### 觸發 counter 更新的來源 byte

`0x81F8` 以 PC-relative 位址讀取 unsigned byte `0x2000BEEA`。在 `0xA0E2..0xA0FA`，若它與 `GP+170` 保存的 byte 不同，程式先把新值存入 `GP+170`，再將 `GP+176` 更新為 `(old+1)&3`；相同時跳到另一分支，不執行這次更新。這個來源只有 byte 寬度的保守範圍，尚不能依其位址或數值判斷產品意義，也不能排除其他 writer。

`0x2000BEEA`、`GP+170` 與 `GP+176` 均在已核對的 reset 清零範圍內。若 reset 完成、GP 為 `0x20004000`，保存值與 counter 在此比較前均未被其他路徑改寫，且比較期間沒有干擾，則兩者起始為 0：來源 byte 可在 reset 後變化，觀察值為 0 時不執行本次遞增；觀察值為非零時本次會將 counter 設為 1。這只約束該次局部更新，不證明其後續查表一定發生、後續 counter 沒被改寫或全域索引恆為 0–3。[檢查器](check-counter-source-byte.py)核對原始指令窗口與位址算術，沒有執行目標或讀取排除區。

#### 已識別的兩個來源寫入點

到達 `0xAF4C` 時，原程式讀取輸入 record offset 8 的 byte `b`，計算 `n=(b>>2)&15`。原始測試 `((n+13)&15)<=4` 恰等價於 `n` 為 3、4、5、6 或 7。測試通過時，經兩個呼叫後 fresh 讀取 `0x2000BEEA`；若值為 0，`0xAF76` 將它設為 1，非零則不在此處覆寫。測試不通過時，`0xB016` fresh 讀同一 byte，若非零則 `0xB026` 將它清為 0；已為 0 則不寫。

若進入該分支時來源值為 0／1、輸入與記憶體有效、兩個呼叫正常返回且中間沒有其他寫入，這兩條路徑完成上述局部處理後分別產生 1／0。測試通過但原值為 2–255 時，此處會保留原非零值，不能把這個片段本身當作任意 byte 的 Boolean 正規化器。兩處寫入為狹義直接位址搜尋的結果，不代表已排除間接 pointer、其他編碼或非同步 writer；尚不能確認該四位元欄位的產品意義或全域索引範圍。檢查器固定兩處指令並枚舉 256 個輸入 byte 的算術條件，沒有執行目標。

#### 兩條已識別 record 分派入口

對 `0x14D2E` 的一般入口，若 selector byte 為 1，原始相對跳轉表會到 `0x14D5E`，以 record offset 0 讀取 unsigned 16-bit 值。經該分派樹，值 `0x0399`（921）導向 `0x152DC → 0xB036`，值 `0x039B`（923）導向 `0x152E8 → 0xB05C`。兩個 wrapper 均先呼叫 `0x1069E`：它以 record 和索引 7 呼叫 `0xED00`，並比較結果與 record offset 10 的 byte；相等返回非零，wrapper 才繼續並尾跳 `0xAE0E`。

`0xAE0E` 保留該 record pointer。對 `0x039B`，它在 `0xAE54` 走往 `0xAF4C` 的分支；對 `0x0399`，若 record offset 11 不等於 1，同樣走往 `0xAF4C`，等於 1 則先走另一段處理，不能直接假定最終會更新來源 byte。上述需 selector、record／動態長度及 stack 有效、checksum helper 與中間呼叫正常返回、保存暫存器與記憶體未被改寫等條件。兩個數值是**record 內的比較值**，不單憑此宣稱它們是真實 CAN ID、來源介面或特定車輛功能；也不排除其他入口。[檢查器](check-counter-record-entry.py)核對有限原始指令及允許的表項，沒有執行目標。

#### 與候選 CAN1 接收的條件式連接

原 `0x12C24..0x12C4A` 以數值 base `0x40006400` 呼叫接收 helper `0x18D78`，再將接收結構 offset 0 的低 halfword、長度及資料傳給 ring 插入函式。按 [WCH CAN 定義](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/inc/ch32v20x_can.h)與已核對的 helper，當接收識別型態 bit 2 為 0 時，offset 0 由接收暫存器右移 21 位形成標準識別欄位；`0x399` 和 `0x39B` 均落在其 11-bit 數值範圍。這支持它們**可能**經 CAN1 標準格式路徑進入前述 record 分派，不證明實機有此訊框或其產品語義。

對一個長度恰為 8 的此類候選接收資料，若 mailbox 各次讀取一致、ring 有空槽且候選 copy 正常、consumer 及其他守衛放行並保持 record 不變，則 record offset 8 對應資料 byte 5，offset 10 對應資料 byte 7，offset 11 的 tag 為 0。此時 checksum gate 的條件是 `data[7] == (ID低byte + ID高byte + data[0] + … + data[6]) & 255`；`0x399` 的 tag 0 也使它避開前述 tag 1 特殊分支。這是完整列明前提的資料流推論，不是觀測到的封包，也不證明 queue 一定成功、實體接線或車輛動作。

擴充識別型態的分支將數值寫入接收結構 offset 4；已核對的 helper 在該分支沒有寫 offset 0，而 IRQ 隨後仍讀 offset 0。因此不能把擴充格式也直接套入上述標準 ID 結論，或假定該欄位已初始化。[檢查器](check-counter-can1-source.py)固定允許的原始指令窗口，不執行目標或讀取排除區。

### 兩條不讀取 counter 表的分支

`0xA132` 呼叫的 `0x81EE` 直接讀 byte `0x2000BED5`。在 `0xA136..0xA158`，若返回值為 1，程式以固定值 `1960`（`0x7A8`）進入共同封包欄位處理；若為 2，則於 `0xA1FC` 設固定值 `2140`（`0x85C`）後進入共同處理。只有其餘 byte 值才在此入口讀 `GP+176` 並查 `0x1AB48`，所以這兩條分支不依賴該表值或 counter 值。

在記憶體有效、函式正常返回、無中途干擾且後續欄位處理完成的條件下，兩個固定值的低 12 bits 分別為 `0x7A8` 與 `0x85C`。這不證明狀態 1／2 實際可達、它們的產品意義、所有可能入口都避開查表或其他下游依賴已解決；不能因此刪除完整 provider。

### 已重建四筆 counter 資料的結果

原始 BIN 在 `0x1AB48..0x1AB50` 的四個 little-endian halfword 與[正式資料來源](../../src/native/receive/input_counter_data.c)相符。當本次 counter 在讀取時確實為 0–3，且呼叫及記憶體條件成立時，`0xA158..0xA18E` 的合併欄位 `(x+0x802)&0xFFF` 為：

| counter | 原 halfword `x` | 12-bit 欄位 |
| --- | --- | --- |
| 0 | `0x0096` | `0x898` |
| 1 | `0x00B4` | `0x8B6` |
| 2 | `0xFF6A` | `0x76C` |
| 3 | `0xFF4C` | `0x74E` |

最後兩筆以無號 halfword 載入；表格只列原始位元與實際低 12-bit 算術，不將其宣稱為有號實體量、單位或車輛功能。四筆條件窗口無法證明其他索引不可達，也沒有消除未解析 provider。

### 查表前的 12-bit 輸入守衛

原 `0xA114..0xA12E` 從當前 stack record 組出 12-bit 值 `v`：`((SP+9 的低 nibble)<<8) | *(SP+10)`。它計算 `(v-1961)&0xFFFF`，若無號結果大於 178，便轉至 `0xA1E8`，不走這次 `0xA132` 的狀態選擇或 `0x1AB48` 查表。因 `v` 本身只有 12 bits，通過該守衛的確切數值是 **1961–2139（含端點）**；此外仍有其他上游條件，不能說這個範圍內的 record 都會到達查表。

上表四個條件輸出分別為 2200、2230、1900、1870；前述兩條不查表的固定輸出為 1960、2140，這六個值都在該輸入守衛之外。若某個後續輸入 record 恰以相同兩個欄位再次進入此守衛，且中途沒有改寫，它會避開這次查表路徑；這只是條件式欄位關係，不證明 record 會回送、實機有回授迴路或可據此識別產品功能。相關指令、四筆允許資料與全部 4,096 個可能輸入的算術界線可由[檢查器](check-counter-input-guard.py)離線核對，沒有執行目標或讀取排除區。

這些數值有可重現的對稱關係：以 `0x802`（2050）為中心，通過的輸入是 `2050±89`；兩個固定輸出是 `2050±90`；四筆條件查表輸出是 `2050±150` 與 `2050±180`。這只是 12-bit 欄位的算術關係，不代表已確認中立位置、物理單位或特定控制功能。檢查器直接從允許的八個原始資料 bytes 解碼四個 halfword，再核對這些關係。

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

四個 state 的數值位置是 `GP+332..335`；GP 為 `0x20004000` 時，這四 bytes 位於原 reset 清零區。若 reset 清零成功，且之後直到各次讀取期間，**只有已辨識序列路徑**可修改它們、該路徑每次完整返回並無重入／IRQ／DMA／alias 干擾，則可由全零初態及上述局部轉換歸納：每次讀表前四個值均在 0／1，因而此路徑的讀取落於既有 48-byte 窗口。這是明確依賴寫入封閉性與無重入的條件式不變量，不證明這些前提在實機成立，也不解除 provider。

[有界檢查](check-sequence-state-gp.py)掃描既有 layout 指定的 69,412 bytes 原始 APP 程式區（不含排除區）：未見直接以 GP 為 base、立即數位移即涵蓋 `GP+332..335` 的標準 RISC-V byte／halfword／word store；它也辨識到 196 個 GP-relative ADDI 位址產生，其中精確 `GP+332` 的是 `0x1202E`。這**不排除**其他偏移再加索引、pointer、callee、壓縮或其他指令編碼、未納入區段及非同步寫入，因此不能把這項掃描當成所有 writer 的完整清單。

進一步區分標記分支：在比較結果走相等分支且此後流程正常時，第二次讀得的 `v=1..254` 都會使 `t>1`，進入 `0x1207A` 的標記路徑；其中只有 `v=1` 是已知兩階段序列的正常第二階段。若 `v=0`，則保留 state 1；若 `v=255`，byte 加法回繞成 0，均不進入該標記路徑。這是對第二次讀值的條件式控制流，不能證明 `2..254` 可達、第一次查表的索引相同、比較真的相等或發生產品動作；也不可把非預期值當成實機缺陷。既有[序列檢查器](check-sequence-interleave.py)已加入 256 個值的分支算術核對。

### `0x1A638` 索引的精確數值邊界

以既有解析座標、原始 APP 半開區間 `[0x8000,0x1AC00)`、正常 channel 0–3、state 的 byte 寬度 0–255 為條件，令 `k=2*channel+state`，比較請求的六-byte 半開窗口是 `[0x1A638+6*k, 0x1A638+6*k+6)`。純位址算術給出下列界限：

| channel | 窗口與既定排除區 `[0x1A69C,0x1A6A0)` 重疊的 state | 窗口部分或全部超過 APP 結尾的 state |
| --- | --- | --- |
| 0 | 16、17 | 246–255 |
| 1 | 14、15 | 244–255 |
| 2 | 12、13 | 242–255 |
| 3 | 10、11 | 240–255 |

因此 1,024 組數值組合中有 8 組的請求窗口碰到排除區、52 組超過 APP 結尾；這些只是可能參數的位址分類，**不是已證明 state 可達、比較函式確實讀取全部六 bytes 或實際越界**。有效來源、候選比較槽的空指標處理及所有權均尚待確認；禁止以這個分類推測或讀取排除內容。[檢查器](check-sequence-window-domains.py)只固定相關原始指令、查詢檔案大小並計算區間，沒有讀取排除區或執行目標。

### 四組樣式的區分性

原始 `0x1A638..0x1A668` 的 48 bytes 與[已重建資料](../../src/native/receive/sequence_pattern_data.c)相符。每個 channel 的 state 0／1 六-byte 樣式依序為 `02 00`／`03 00` 加上同一組後四 bytes；四個 channel 的後四 bytes 互不相同。因此在 state 只為 0／1、候選 `0x4003C` 的六-byte 等值比較契約成立且輸入穩定的條件下，這八個樣式兩兩不同，不會由同一個六-byte 輸入同時命中兩組。

更具體地說，若四個 state 初始均為 0，連續兩次符合讀得的長度 byte 為 6／資料第二 byte 為 0 的輸入，分別完全匹配同一 channel 的 state 0 與 state 1 樣式，且比較／記憶體在呼叫間沒有干擾，則第一次使該 channel 變成 1；第二次使其回到 0 並進入 `0x1207A` 的標記路徑。這不是對任意交錯輸入或未知初始 state 的結論，也不證明裝置實際收到這些值、標記字其他 bytes 的意義或對應按鍵功能。

#### 兩組交錯輸入的順序差異

在上述八個樣式互不相同、四個 state 起始均為 0、比較槽符合候選契約、三次輸入均進入此迴圈且沒有干擾的條件下，令 `A0`／`A1` 分別為 channel A 的 state 0／1 樣式，`B0` 為另一 channel B 的 state 0 樣式。輸入 `A0 → B0 → A1` 的結果取決於迴圈先後：

| A、B 的順序 | `B0` 時對 A 的影響 | `A1` 時的條件式結果 |
| --- | --- | --- |
| `B < A` | B 先匹配並離開，A 尚未被檢查，保留 state 1 | B 先不匹配而清零，A 匹配並進入標記路徑 |
| `A < B` | A 先不匹配而清零，再由 B 匹配 | A 的 state 0 樣式與 `A1` 不同，八種樣式互異使本次不產生匹配標記 |

這是原迴圈「不匹配清目前 state、首次匹配立即離開」與既有資料的條件式推論；不是已觀察的 BLE 訊息或車輛行為，也不能假設未知 state 或其他輸入符合此例。[檢查器](check-sequence-interleave.py)只固定原始指令和已允許的 48-byte 資料窗口，未執行目標、HOST model 或 ISA。

### 六-byte 比對輸入的上游

原回呼 `0x119C8` 在輸入 `a1` 的低 16 bits 最高位為 1 的分支，從 `0x4006C` 載入並呼叫間接目標；若返回指標非零且其 offset 0 為 `0xB0`，才繼續特定訊息處理。依固定版本 [WCH V1.30 標頭](https://github.com/openwch/ch32v20x/blob/ec059e0b18046b111ee850e44f105fcd095e775c/EVT/EXAM/BLE/LIB/wchble_rom.h)，此槽為 slot 14 的候選 `tmos_msg_receive(taskID)`；這支持佇列訊息來源的推論，但不證明實機槽、訊息來源或完整 ABI。

原始路徑先以訊息 offset 2 的 halfword 比較三個候選值，並在訊息 offset 4 為 27 或 29 的分支，以 `*(GP+92)+43*i+3` 與選中狀態區的六 bytes 經 `0x4003C` 比較，最多檢查三筆。經匹配及其他 guard 後，`0x12392` 將訊息 offset 12 的 word 載入 `s3` 作資料指標，`0x12396` 將 offset 10 的 byte 載入 `s4` 作長度；以該指標與長度呼叫 `0x838E` 且結果為零後，仍需通過多個間接比較及分支，才可能進入 `0x12020` 的長度 6 與資料第二 byte 為 0 檢查。

此鏈是條件式靜態結構，依賴指標有效、原機間接函式契約、暫存器保持與無非同步覆寫；尚未確認這是實機 BLE 訊息、資料生命週期、訊息數值的產品語義或全部可達路徑。沒有讀取使用者裝置資料或執行回呼。

### 與 WCH GATT 事件的候選結構對照

同一固定版本 WCH 標頭將 `0xB0` 定義為 `GATT_MSG_EVENT`，將 27／`0x1B` 定義為 `ATT_HANDLE_VALUE_NOTI`、29／`0x1D` 定義為 `ATT_HANDLE_VALUE_IND`；其 `gattMsgEvent_t` 包含事件 header、`connHandle`、`method` 和訊息 union。候選 notification／indication 結構含 `uint16_t handle`、`uint16_t len` 與 `uint8_t *pValue`。

若原機使用該標頭所述結構、RV32 little-endian 與一般 4-byte 指標／union 對齊，則 header、連線 handle、method、訊息 union 分別位於 offset 0、2、4、8；在 notification／indication 的 union 成員中，handle、16-bit length、pointer 會位於訊息 offset 8、10、12。這與原程式的數值讀取及方法分支一致，支持輸入為 GATT notification／indication 資料的**條件式推論**，並非 ABI 或真實 BLE 封包的實測證明。

尤其 `0x12396` 是 `LBU`，只讀 offset 10 的低 byte；即使候選結構有 16-bit `len`，原始長度高 byte 也未在這個讀取點檢查。因此 `s4==6` 只證明所讀 byte 為 6，不能單靠此 guard 宣稱完整 16-bit 長度為 6；實際緩衝區可讀範圍、前置檢查和 installed ABI 仍需證據。

`0x123A4` 先以該指標與讀得的長度 byte 呼叫 `0x838E`；此函式並非純粹 predicate。它依 4-byte 步進檢查 `0x2000C794` 起兩個位置：對應 halfword 非 `0xFFFE`、類型 byte 等於 2、另一 byte 非零時，將此次傳入長度限制為最多 30，經 `0x4004C` 槽要求複製至 stack+2，並以含 2-byte 前綴的資料呼叫 `0x8A56`。上述欄位地址有重疊的數值視圖，不能直接當成已證實的 C 結構或所有權。

`0x123A8` 僅在 `0x838E` 返回 0 時繼續後面的樣式比對流程；匹配項的非零 byte 會成為該函式的返回值之一。這提供「先依設定條件處理，返回零才繼續」的靜態控制流證據，不證明 `0x8A56` 的傳送成功、實機記錄內容、空值／長度安全或候選槽的真實身分。複製與後續效果仍依有效 buffer、callee 正常返回及無干擾等條件。見 [既有函式證據](../../analysis/callback-completion-2026-10-25/README.md)。

### 回呼註冊與訊息生命週期

初始化路徑 `0x1253C..0x12550` 從 `0x40080` 載入間接目標，傳入 `0x119C8`，將回傳值低 byte 存到 `0x2000BFD4`。若 installed slot 符合相同標頭的 `TMOS_ProcessEventRegister`，這可解讀為註冊前述回呼並保存 task ID；`0xFF` 是候選介面的失敗值，原指令在此處沒有檢查結果。實機是否註冊成功、後續有無覆寫與 scheduler 是否採用此 ABI 仍未知。

`0xB0` 訊息到共同清理處 `0x1240C` 時，程式將 `message+8` 與 `message[4]` 傳給槽 `0x4012C`，再從 `0x1241E` 把 message 傳給 `0x40068`；非 `0xB0` 的非空訊息直接走後者，空指標則跳過這兩處。候選 WCH 標頭分別把 slot 62 和 slot 13 定義為 `GATT_bm_free(gattMsg_t*,opcode)` 與 `tmos_msg_deallocate(msg_ptr)`，且其 `gattMsg_t` 候選 union 與 method offset 符合上述參數。

若 installed slots 與候選介面相符、兩次呼叫均正常且記憶體有效，這支持先處理 GATT 內部 buffer 再釋放外層訊息的推論；`message+12` 所指資料不能未經其他 ownership 證據假定在此清理之後仍有效。未證明實機 slot、釋放成功、其他所有出口或指標別名；沒有執行裝置程式。

### 三個六-byte 候選比對來源

reset 的初始資料在原 BIN `0x1ABBC` 包含 word `0x2000C40C`；在 GP=`0x20004000`、初始複製完成且無覆寫時，`*(GP+92)` 因而指向此位址。上述 `0x11A58..0x11A76` 使用 offsets 0、43、86，各從指標加 offset 再加 3 處比較六 bytes；這三個半開窗口分別是 `[0x2000C40F,0x2000C415)`、`[0x2000C43A,0x2000C440)`、`[0x2000C465,0x2000C46B)`。

`0x132C8..0x132F8` 經 `0x4004C` 槽要求從數值來源 `0x08077500` 載入 133 bytes 至 `0x2000C40C`，並檢查 offset 132 的 `0x5A` 標記；三個窗口均在載入區內。若槽確實為候選 copy、指標與記憶體有效且未改寫，這將上游比較連到同一個候選設定區；標記不是完整性校驗，來源實際內容、身分資料含義及實體 Flash 映射均未知。

標記不符時，`0x13108` 要求由 `0x40048` 將此區 133 bytes 填 0，寫入 offset 132 的 `0x5A`，再尾跳 writer `0x130D6`。在 fill 契約等條件成立時，三個比較窗口均被清零；是否真的匹配、後續是否重新設定及寫入是否成功都未證實。此處沒有讀取或輸出裝置連線識別資料；數值來源與 133-byte writer 的界限另見 [NVM 區域分析](../tsl9-NVM-record-layout/README.md)。

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

#### 清零記錄與序列完成標記的關係

若上述 fallback 的候選 fill 正常將 256 bytes 清零，後續只有 offset 255 被寫為 `0x5A`，則 42 筆記錄使用的前 252 bytes 仍全為零，每筆用於比較的 offset 2／4 halfword 合成值均為零。反之，`0x1207A..0x1209A` 的正常四組序列完成標記低 byte 為 `0x80..0x83`，因此其 32-bit 值不為零。

在記錄指標仍指向該區、完成標記保留在 `0x2000BFCC`、`0x2000BFC9=0`、所有讀寫／呼叫正常且沒有其他覆寫或非同步干擾的條件下，`0x11356` 的這次 42 筆掃描不會匹配，因此不會從相符分支呼叫 `0x155D0`。這不排除其他呼叫 `0x155D0` 的路徑，也不證明 fallback、序列完成、計時事件或實機動作曾發生；真實設定頁可能包含非零記錄。[檢查器](check-sequence-cleared-records.py)固定三段原始指令窗口，不讀取任何裝置資料或執行目標。

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

### 固定 CAN 濾波表對接收來源的限制

`0x12B82` 呼叫 `0x1299E`，後者將 `0x19CA8` 的 96 bytes 複製並交給 `0x128FE`。原始表包含 48 個 little-endian 16-bit 值，均不大於 `0x7FF`，其中沒有 `0x399` 或 `0x39B`。[檢查器](check-counter-can1-fixed-filters.py)固定原始指令及資料窗口，並檢查這兩個值的左移五位編碼；不執行目標。

`0x128FE` 呼叫兩個尚未確認契約的 resident 槽後，將資料分為 14 組、每組四個 halfword，左移五位並呼叫 `0x18BA2`。若 resident 槽分別正確清零 112 bytes 與複製 96 bytes，剩餘八個值為零；依已保存的 WCH CAN 定義，這條設定路徑對應 14 組啟用的 16-bit ID list、FIFO0。若設定均成功、硬體採用相符的標準資料訊框比對語義且之後沒有改寫，該固定表不接受 ID `0x399`／`0x39B`。這限制先前的 CAN1 來源推論，但不證明實機使用此設定，也不排除其他設定路徑、外部控制器或其他來源。resident 實際行為、濾波生效及實機資料均未驗證。

固定表的**第一段**複製可進一步由 APP 指令收窄：`0x1299E` 以來源 `0x19CA8`、長度 96、目的當時 `SP` 呼叫完整本地函式 `0x19BF0..0x19CA6`，再把相同 `SP` 及長度 96 傳給 `0x128FE`。來源地址四-byte 對齊；若目的也四-byte 對齊、兩區有效且不重疊、地址不溢位且無干擾，原始 `0x19C3C..0x19C9C` 先複製兩組各 36 bytes，再以六個 word 複製剩餘 24 bytes，恰為 96 bytes。目的未對齊而來源對齊時，會走逐 byte 複製路徑，同樣以目的加 96 為終點。

因此在上述記憶體與控制流條件下，傳入 `0x128FE` 的來源內容確實是這 96-byte 固定表；這不消除 **第二段**的 `0x40048`／`0x4004C` resident 契約，也不證明實際濾波器設定成功或維持不變。[分支覆核器](check-key-control-flow.py)核對兩次呼叫與本地複製的關鍵分支及步進；其算術不是硬體或目標執行。

#### 同一分支的兩個候選 SPI 通道

同一 `0x12B82` 分支在固定表設定返回後，依序以通道 `1`、`2` 呼叫 `0x16DD4`。該函式先清兩個 stack word：通道 1 再寫入 `0x01450399`，通道 2 寫入 `0x039B0370`，各以長度 8、參數 `a3=1` 呼叫 `0x16CC4`。依 little-endian halfword 分組，前四項分別為 `[0x399, 0x145, 0, 0]`、`[0x370, 0x39B, 0, 0]`。

若兩個 resident 槽確實完成 12-byte 清零及 8-byte 複製、呼叫保留必要暫存器且六輪均完成，`0x16CC4` 將以上四項及後補兩個零值作為 11-bit 候選濾波值，交給 SPI 寫入路徑。`0x16A7C..0x16AFA` 的候選接收路徑將解析出的 ID 及原通道值分別傳給 ring 作 record ID 和 tag；在 13 次 SPI 讀取、資料格式、記憶體與 ring 皆符合條件時，通道 1 的 `0x399` 可形成 tag 1，通道 2 的 `0x39B` 可形成 tag 2。前者會遇到上述 `0x399` 的 tag 1 特殊分支，不能套用 CAN1 tag 0 的結論。

這是初始化設定與接收資料流的靜態連接，不證明實際控制器識別、mask／濾波生效、接收到封包、checksum 通過或觸發後續狀態。呼叫值只是通道標籤，不等同已確認的實體接線。[檢查器](check-counter-spi-filter-path.py)核對原始指令窗口與常數編碼，不執行目標。

#### 候選 EXTI、SPI 選擇與 record tag

既有[向量表對照](../tsl9-qingke-v4-vectors/README.md)將 slot 39 對應至 `0x16FB6`；若採用 WCH CH32V208 候選定義，它是 EXTI9_5。該函式分別讀 `0x40010414` 的 bit 6／7，對相同位址寫 `0x40`／`0x80`，並分別把 `GP+360` 的 bit 0／1 設為 1。本機保存的 [WCH 標頭](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/inc/ch32v20x.h)將該位址對應 EXTI interrupt-pending register、這兩個 bits 對應 line 6／7；實機映射及清除效果仍須確認。

若後續進入 `0x17002`、旗標保持有效且中途呼叫保留必要暫存器，bit 0 路徑呼叫 `0x16B0A(1)`，bit 1 路徑呼叫 `0x16B0A(2)`；後者重新讀旗標，因此不能假設兩次觀察同時成立。`0x16B0A` 先讀候選 SPI 裝置 register `0x2C`，依讀回的 bit 0／1 分別以地址 `0x61`／`0x71` 呼叫 `0x16A7C`。接收函式對 channel 1 向 `0x40010814` 寫 `0x10`，對 channel 2 寫 `0x01`；若採 WCH GPIOA 定義及低有效線路，分別是 PA4／PA0 的候選片選。它在滿足 header／長度守衛後把原 channel 傳給 `0x12BC8`；在 ring 空槽、copy 及保存暫存器條件成立時，對應 record tag 1／2。

這條連接提供 `0x399`／`0x39B` 來源的具體候選，但只在相應初始化、IRQ 交付、SPI 裝置與資料格式均相容時成立；它不證明實際 PCB 走線、裝置收到特定 ID 或 counter 已改變。詳見[獨立指令覆核器](check-key-control-flow.py)；沒有接觸硬體或執行韌體。

#### EXTI line 6／7 的初始化指令

`0x170A2..0x170F4` 分別以 `(0x40011000,0x40,0x48)` 與 `(0x40011000,0x80,0x48)` 呼叫既有 GPIO helper `0x9A24`；依已核對的 WCH 定義及 helper 契約，這請求將 **PC6／PC7 設為上拉輸入**。接著 `0x17104`、`0x17112` 對本地 helper `0x1904A` 分別傳入 `(2,6)`、`(2,7)`。該 helper 對 `0x4001000C` 做四-bit 欄位的 read-modify-write；在 WCH AFIO 映射與傳入值不變時，兩個欄位分別被設為 2，對應 EXTI 6／7 的 GPIOC 來源。

同一初始化在 stack 準備 `[line=0xC0, mode=0, trigger=12, enable=1]` 並呼叫 `0x18E1C`。依完整 helper 的讀寫，可見它清除 `0x40010408` 中 `0xC0` 位、在 `0x4001040C` 中設定這些位，並在 `0x40010400` 設定這些位；在 WCH EXTI 定義下，這對應 line 6／7 的上升緣停用、下降緣與中斷啟用。前述步驟與候選 EXTI handler 的 bit 6／7 及兩個 SPI 通道形成靜態對應。

上述結論依有效 stack、正常呼叫、暫存器保存、無重映射／非同步覆寫及候選 WCH 寄存器定義成立；不等於量測到實際 pin 電平、確認 PCB 與控制器的導通，或證明 IRQ 曾發生。這也不排除之後的重新設定。[獨立覆核器](check-key-control-flow.py)固定初始化與兩個 helper 的指令窗口。

#### 啟動時序與旗標清除的條件式交互

原 APP main `0x9258` 先呼叫 IRQ 初始化 `0x9A42`；該函式在 `0x9ABE` 向候選 PFIC enable 位址寫入對應 EXTI9_5 的 mask，`0x9AC2` 設定全域中斷相關 CSR mask。main 經其他初始化呼叫後，才於 `0x9280` 呼叫上述 PC6／PC7 初始化 `0x17040`。該函式進入時，`0x17048..0x17058` 請求由 `0x40048` 槽以值 0 填寫 `GP+360..362` 三個 bytes；之後才進行前述 GPIO 與 EXTI 設定。

若該槽符合候選 fill 契約、記憶體有效，且在早期 enable 請求之後、這次 fill 完成之前，候選 EXTI handler 因既有 pending／enable 等條件而執行並把 `GP+360` 的 bit 0 或 1 設為 1，那次 fill 可將該已設旗標清掉。這是具體的**可能時序**，不是實測競態：沒有確認早期 peripheral enable／pending、IRQ 是否真的送達、實機槽內容或被清除的事件是否可觀測；其他初始化也可能影響狀態。`0x14C8A` 等中間呼叫是否正常返回亦是條件，未讀取既定排除區。

#### 接收旗標與 queue 的主迴圈順序

`0x900C` 呼叫上述初始化 `0x9250`，正常返回後在 `0x900E` 呼叫 `0x8180`。後者的循環依序從數值地址 `0x20000000` 載入間接目標並呼叫、於 `0x819E` 呼叫旗標消費函式 `0x17002`、於 `0x81A2` 呼叫 queue 消費函式 `0x12C58`，之後在 `0x81A8` 跳回循環。候選 WCH bootstrap 將 `0x200007D0` 寫到 `0x20000000`，但原機 slot 與 ABI 未確認。

因此，若初始化及間接呼叫正常返回、旗標消費時對應 bit 已設、接收成功放入 queue，且呼叫及記憶體狀態保持有效，**同一次正常迴圈**接著會進入 `0x12C58` 掃描 queue；是否找到剛插入的 slot、通過守衛或進入 `0x14D2E` 仍由後續條件決定。這連接了先前的候選 EXTI／SPI 接收與 counter record 分派，但不是實際封包、主迴圈執行、時間或功能的證明。

#### `0x399`、tag 1 特殊分支的匯合

在 checksum 等上游守衛通過並到達 `0xAE62` 的條件下，此分支要求 `0x4004C` 槽將原始 12-byte record 複製到 `SP+4`。因此，若槽確為順向 copy 且來源與目的有效，`SP+12` 最初對應原 record offset 8。此分支可能修改的是 **stack 副本**的 `SP+12`，也可能重算副本 checksum 並呼叫 `0x12A08`；它不因此證明傳送成功。

追蹤 `0xAE70..0xAF4C` 的所有靜態分支：`0xAF48` 的 `s2=0` 直接落入 `0xAF4C`；`s2≠0` 則先到 `0xAEE0` 處理副本，經 checksum 與 `0x12A08` 返回後由 `0xAF08` 跳到同一位置。其他分支也匯合到這兩條路徑。**若**所有經過的間接與直接呼叫均正常返回、保存的 `s0` 與 stack 有效且無 alias／非同步干擾，tag 1 特殊分支仍可到達 `0xAF4C`；該處從 `s0+8` 重新讀取的是原 record，而非 stack 副本。因此其 counter 來源條件仍由原始 byte 的 `(b>>2)&15` 是否為 3–7 決定，不能以副本修改後的 byte 取代。

這只證明條件式控制流與資料來源，不證明封包、初始 checksum、callee 副作用、記憶體穩定或 counter 更新實際發生。[檢查器](check-counter-tag1-convergence.py)固定相關原始指令窗口，不執行目標或讀取排除區。

### 第二個 counter 寫入點的守衛

在 `0xA2EE..0xA37C`，`0xA344` 的 `(old+1)&3` 寫入只出現在一條受限路徑。首先 `0x829E` 回傳的 byte 必須為 1；否則該函式尾跳 `0x10816`，不經此寫入。其後 `0x81DE` 讀 `*(GP+84)` 指向區域的 offset 5，回傳 `(byte&3)+1`。若這個返回值的 bit 0 為 1，程式先呼叫 `0xA204`；接著只有返回值的 bit 1 為 1 才繼續。依 0–3 完整四種低位組合，後者恰要求原 byte 的低兩 bits 為 **1 或 2**。

要到達 `0xA344`，還須 `0x821E(2)` 返回非零、入口保存的完整 `a0` 非零，以及再次讀得的設定 offset 3 低 nibble **不等於 `0xF`**：`0xA32E` 是 `beq a5,a4,0xA372`，相等會離開。此處更正先前將分支方向反讀的結論。在有效指標／記憶體、各呼叫正常返回、保存暫存器不變且無非同步或 alias 干擾下，程式才遞增該 counter、把 `GP+175` 設為 1，並以 `0x9F74` 為回呼、`a2=(入口 a0 × 1000) mod 2^32` 尾跳 `0x9124`。`0x9F74` 本體清除 `GP+175`；`0xA1E2` 在此 byte 非零時可分支至 `0xA114` 的欄位守衛。這不證明回呼已註冊／執行或後續查表可達。

`0x81DE` 的 bit 0 為 1 時還有 `0xA204` 副作用；這個分支不會直接讀作「原 low bits 為 1 或 2 就足夠」。以上是必要局部條件而非全域 state 界限，且不排除其他 counter writer。[檢查器](check-counter-second-writer.py)固定相關原始指令窗口及四種低位組合，不執行目標。

#### 已辨識呼叫點的輸入與排程換算

在已辨識的直接呼叫點 `0x172FC`，上游 `0x172CA` 從設定 offset 8 取低四 bits，範圍 0–15；只有當時 offset 3 低 nibble 為 `0xF` 且 `0x829E` 返回 1 才將它限制為最多 3。若設定在兩次檢查間保持一致，會走到 `0xA344` 的情況必須是 offset 3 低 nibble 不等於 `0xF`，因此**不會走這個上限 3 的分支**。在保存暫存器正常且實際到達寫入的條件下，輸入非零且範圍為 **1–15**。先前聲稱只能為 1–3 是錯誤的。其他間接呼叫及記憶體變化仍需獨立分析。

在上述條件下，令輸入為 `n=1..15`，`0xA360` 傳入 `0x9124` 的 `a2=1000*n`、`a1=0`。若 scheduler 找到既有相符項或空項，且所經呼叫與保存暫存器均正常，`0x91D0..0x91E8` 再乘 1000、除以 625，得到 **1600*n**；此範圍沒有乘法溢位。`0x922C` 從 `0x40058` 讀取間接目標；若該槽符合上文 WCH V1.30 `tmos_start_task` 介面及 625 微秒 tick，名義延遲為 **1–15 秒**。

沒有證明當時有可用排程項、slot 身分、呼叫成功、計時精度或回呼實際執行；其他入口不能套用 1–15 的結論。[檢查器](check-counter-caller-delay.py)除固定指令窗口外，也直接解碼兩條分支的指令、運算元與目標，並核對 1–15 的算術；不執行目標。

#### 排程表容量與回呼執行的區別

APP 的 `0x9124` 對非零延遲先掃描 15 筆、每筆 12-byte 的工作表，依 offset 4 的 callback word 找相同回呼；找不到才掃描空項。若 15 筆 callback 均非零且沒有 `0x9F74`，在無非同步改寫且控制流程正常的條件下，兩輪掃描結束後經 `0x924C` 返回 1，沒有進入本次 `0x40058` 的計時呼叫。由於呼叫前 `0xA344` 已更新 counter 並將 `GP+175` 設為 1，該排程失敗路徑本身不回復這兩次寫入；若沒有其他 writer 或非同步干擾，旗標會維持 1，不能把 counter 更新當作計時器已成功建立。

相反地，原 `0x907A..0x90AC` 先要求清零 180-byte 工作表，再經 `0x40080` 傳入 `0x901A` 並將返回低 byte 存入 `GP+166`。`0x901A..0x907A` 依事件 bit 選擇對應槽位；槽位的 byte flag 為 0 時，先清 callback 和 argument word，再以 argument 呼叫保存的 callback。若此初始化、先前的一次性排程、候選 WCH 事件介面與事件交付全部成立，且槽內容未被改寫，保存的 `0x9F74` 可清除 `GP+175`。這不證明 slot 真的被註冊、計時器啟動、事件到達或旗標永遠維持任何值。[檢查器](check-counter-scheduler-capacity.py)固定相關原始指令窗口，不執行目標。

## 近期分支的獨立覆核

針對先前 `0xA32E` 分支方向誤判，新增 [靜態覆核器](check-key-control-flow.py)：從原 BIN **只讀二十四個明確窗口**，核對窗口雜湊後，將窗口放入 radare2 的暫時記憶體反組譯，並比對 95 個指定指令。覆蓋 counter、selector、序列狀態、GATT 註冊、resident 版本守衛、固定濾波表複製及候選 EXTI／SPI 接收、主迴圈與初始化路徑。檢查器對記憶體中的一個分支位元做負例；不修改原 BIN。

執行 `python experiments/tsl9-six-dependency-ledger/check-key-control-flow.py --r2 /path/to/r2`。Windows 也可傳入本機 `r2.exe` 的路徑；需自行提供支援 RV32C 的 radare2，不會下載工具。此覆核確認所列指令及目的地，**不證明**其餘指令語意、動態可達性、callee 契約或硬體效果；也未讀取排除區、執行目標或執行模擬器。
