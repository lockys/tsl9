# v4.1.60：較大 consumer、有限 table helper 與 RAM service

本階段完成 B+152 consumer 的完整本體、caller、counter、threshold helper，以及 callback 使用的另一個 RAM service。新增 **2,980 bytes**：996 條指令，另含兩份各 24-byte 的 threshold table；既有 constructor、callback、startup 與 C 重建覆蓋率不重複計入。

| 完整本體 | V1.31 entry | V1.40 entry | 每版 bytes／指令數 |
|---|---|---|---|
| B+152 consumer | `69a22` | `69b3a` | 1214／400 |
| 直接 caller | `678cc` | `67a0a` | 46／20 |
| counter | `56184` | `562c4` | 24／10 |
| threshold helper | `534f6` | `535a4` | 54／18 |
| 映射 RAM service | `2000263a` | `20002686` | 128／50 |

完整範圍、SHA-256、兩版 literal operands、calls／stores、CFG、路徑與整數證據見 [機器可讀證據](v4160-large-consumer-service-static.json)。以下 `+offset` 為各本體入口相對十六進位位置。

全程是離線讀檔、解碼、圖與整數檢查，沒有執行或模擬目標 ISA、copy、allocator、provider、polling、MMIO、CSR 或裝置。resident 候選、load-image 映射與本機請求合約，不等同已安裝或實際呼叫。

## Consumer 的驗證順序與副作用界線

B=`200033b8/20003408`，F=`200031ec/2000323c`。frame80 保存 RA 及全部 12 個 S registers。entry A5／A6／A7 與五個 incoming stack words 都會作為選定路徑的 halfword-array pointers；只看入口 prefix 的前兩個 stack words 不足以涵蓋完整本體。

第一個請求是 **`20000332(SP+10,entry A3,6)`**，發生在所有 flags／tag rejection 之前。因此拒絕輸入不代表沒有 provider 呼叫或來源存取；source、frame、nonalias 與保存期仍是前提。

原指令接著依序執行：

1. fresh B+128 若非零，讀其 word+28；bit14 設置就返回 12。
2. 初次 fresh B+152 為零就返回 12；否則呼叫 counter。
3. counter 回覆**恰等於**另一個 fresh `U8[F+21] >> 2` 才返回 12。不是上限比較；大於該值不會被這個 equality gate 拒絕。
4. entry A4 高於低三位的 bits 非零就返回 17；低三位只有 0 或 2 時返回 18。接受的完整 flags 恰為 **`{1,3,4,5,6,7}`**。
5. 再次 fresh 讀 B+128；該物件 word+28 bit14 設置或 byte+11 非零就返回 12。不能合併前後兩個 snapshots。
6. fresh B+148 非零時取既有 N，N+7=1 就返回 12；為零則 fresh 重讀 B+152，**沒有再次 function null guard** 就呼叫 constructor。此路徑本機 A0=17；constructor 回覆為零就返回 12。
7. 之後才檢查 unsigned entry A1 tag 是否大於 3，大於就返回 18。這個 tag rejection 發生在**可能配置與發布物件之後**。

沿用 [constructor 證據](v4160-list-outer-objects-static.zh-TW.md)，匹配且保存的 B+152 literal 才對應 `57cbe/57dfe`。初次 nonzero guard 不保證後來 fresh function read 有效，也沒有證明配置 ownership 或保存期。

## 六個 bytes 的測試與 copy

通過後寫入 N+13=entry A0 低8位、N+101=已檢查 tag，再請求 `200004bc(entry A3,0,6)`。

- 回覆非零：N+108=0，跳過第二次 copy。
- 回覆為零：N+108=1、N+109=entry A2 低8位，再請求 `20000332(N+110,entry A3,6)`。

這個零回覆不能當作 source 非 null 或完整六個 bytes 可讀的證明。參考 predicate 的只讀定位顯示 null／早期 mismatch 也可回覆零；其完整 source／installed binding／控制副作用尚未納入本次新 proof。後面的 copy 需要自己的 extent／同步完成／不保存借用指標前提。

## 三組數值欄位與 signed DIV

flags bits0／1／2 選擇三個本機數值區段；輸入 pointers 使用依先前已選 bits 累積的 dense index，而非固定 bit 編號。原指令在這些條件下形成的 byte offsets 是 0、2、4；flags7 的每個實際使用 halfword array，六個有效 bytes 可涵蓋其選定 accesses，但實際來源大小、alignment 與保存期沒有因此成立。

三個 threshold-helper callsites 可更新 N+80／82／84。其後重新讀取 halfword，先 clamp 到 6..3200，再 zero-extend 到 A0，作為三個 signed DIV（`+214/+2fa/+434`）的分母。checker 用 dominance 與 encoded definition sites 核對 clamp／A0 definitions 在相應 DIV 前，而且其間沒有其他 A0 定義或 call。

在普通指令語義與有效存取／必要 callee 保存前提下，這三個本機 DIV 的分母為 6..3200、分子為 40..12800，局部可排除除以零；不能把這個結論擴大成整條呼叫鏈完成或實際輸入已知。

signed quotient 範圍是 0..2133，減一後再與 K（0..499）做 signed min，結果可以是 **-1**，halfword store 會成為 `ffff`。正分母不代表最後欄位必為非負或 unsigned<=499。

純整數 witness：D=3200、K=81，前面的 `floor((K+1)*D/4)=65600` 先截 low16 成 64，再 clamp；`256/3200` 的 quotient=0，減一得 -1。這只展示原式的代數可能性，沒有證明實際 ingress 能提供這組資料或指標。

其餘 clamps、means、signed comparisons、fresh halfword reads 與缺少 flags 時的 copybacks 均保留原指令；沒有為數值指定物理時間單位，也沒有假定未更新欄位在每組 flags 下都完成初始化。

## Threshold table：本機可證明的有限掃描

兩版 table 位於 `6e4f4/6e6e4`，各 24 bytes，內容相同：

```text
07 0b 0d 11 13 17 1d 1f 25 29 2b 2f 35 3b 3d 43
47 49 4f 53 59 61 ff 00
```

helper 從 index0 開始，每輪讀 threshold byte。threshold>A0 或 threshold=`ff` 就返回；否則 fresh 讀 `U16[A1]`，threshold>=該 word 時 SH threshold 並返回，否則 index 加一再 mask255。

固定 table 的第一個 `ff` 在 index22；到這裡以前 index 不會 wrap，因此在 bytes 保持、存取有效與普通 index 語義下，最多 **23 次 threshold reads、22 次 input-word reads、1 次 SH**。末尾 index23 的 `00` 不會被這條掃描讀到。

這個 leaf 沒有 frame／calls，也不改 A0 或 S registers。它的有限本機掃描與另一個 counter 的鏈表遍歷不同，不能拿 23-read bound 保證整個 consumer 返回。

## Counter、最終 callback 與 caller

counter 由 B+156 取 head，沿 node+0 的 next word 遍歷；fresh node+11 byte 為零時，fullword count 加一。沒有 store、frame 或 call，本機保存 S／SP／RA，但鏈表無環、節點至少 12-byte 有效範圍、count 不 wrap 與最終遇到 null 都未證明。

consumer 最後 fresh 讀 B+224，OR512 後寫回，再從 **fresh `U32[N+136]`** 呼叫 function pointer，沒有 null guard，也沒有把 A0 重新設成 N。回覆隨後直接進 frame restoration／RET，consumer 成功路徑的 A0 是該 callback 回覆，沒有固定 success0。

matching 新 constructor 的 N+136 literal 為 `57b7c/57cbc`；既有物件、後續 writers、callback 身分及物件保存期仍需追查。固定 N accesses 最少需要 140 bytes、B 最少需要 228 bytes。

直接 caller 使用 frame48，轉送 A0～A7 與五個 incoming stack words，呼叫完整 consumer。接著以 A0=consumer 回覆、A1=`2043` 請求 `6a710/6a8f4`；此服務的兩版差 484，不能沿用 consumer 的位址差。只有第二服務正常返回後，caller 才明確設 A0=0；這不是 consumer 成功、callback completion 或 async 工作完成的證據。

## 映射 RAM service：signed LH 與當前 callback 路徑

沿用 startup operands／copy-helper 證據，本階段將 RAM `2000263a/20002686` 的完整 128 bytes 分別映射到 FLASH **`428aa..4292a`／`42936..429b6`**，並在 RAM PC 解碼。它正好結束於先前 250-byte RAM tail 的入口，沒有重算後者。

此 leaf 無 frame、call 或 loop，只改 GPR A0、A3～A6，本機不寫 S registers、SP、RA、A1、A2；資料存取／alias 與實際 provider identity 仍需前提。

generic 本體依序為：

1. capture R0 pointer，讀 R0+56 bit5；設置就返回 1，尚未做任何 data store。
2. A2 非 null 時，把 `U32[R0+48]` 的 bits15..22 存成 byte[A2]。
3. A3 非 null 時，fresh 讀另一個 R1／word48，取 signed10 bits5..14；再以 **SIGNED LH** 讀 old[A3]。old=0 時存該 signed10 值，否則 signed DIV(value+old,2) 向零截斷後 SH。不能用 unsigned LHU 或 Python 的負數 floor division 代替。
4. A1 非零時才把 entry A0 當 packet P：k=`U8[P+1]`，k 非零才讀 `U8[P+k+9]`。byte 01／11 通過、81／91 返回 14，其餘 252 個 byte 返回 6。
5. 通過或跳過 packet check 時 fresh 讀 R2／word56，將 bits27..28 存到 C+11，返回 0。

R0／R1／R2 及各 word snapshots 不預設相同。狀態 6／14 可能在 A2／A3 已寫入後返回，因此不是 transactional no-write error。

沿用 [callback 參數證據](v4160-callback-dispatch-static.zh-TW.md)，三處實際請求都給 A1=0、A3=0、A2=N+20 指標。這組參數跳過 signed-LH 與 packet 解參考路徑；entry A0 雖載入 N+80 的 word，這條路不把它當 packet pointer 使用。在有效 N／R／C、matching leaf 與正常存取前提下，本機回覆為 0 或 1：initial bit5 清除時寫 N+20，再寫 C+11；bit5 設置時不做 data stores。

這次需 R object 至少 60 bytes、C 至少 **12 bytes**，比先前 callback 自身的 C>=11 多一個 byte；optional A2 需可寫1 byte、optional A3 需可讀寫2 bytes。generic packet 的 raw k 最大可要求 265-byte contiguous extent，沒有推定真實 k 或 buffer 大小。物理 MMIO、pointer retention、global alias 與其他 callers 的參數仍未封閉。

## 重播與後續邊界

[靜態 checker](check_v4160_large_consumer_service_static.py) 驗證 996 次 instruction mutations、48 次 tablebyte mutations、2 次 LH→LHU signedness mutations、58 條選定 CFG walks、1102 條 edge witnesses，以及 flags、DIV、signed arithmetic、packet byte domains、helper bound 與 exact ledger。RAM 當前 callback 路徑另有明列的兩條 conditional walks。

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_large_consumer_service_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_large_consumer_service_static.py
```

consumer／caller／RAM service 的局部 CFG 無環；counter 的鏈表循環及其他 callees 的完成仍未知。後續需驗證 N+136 callback、`200004bc` predicate 的完整 source／binding、node／callback writers，以及實際副作用、保存期與 async completion。C 重建覆蓋率沒有改變。
