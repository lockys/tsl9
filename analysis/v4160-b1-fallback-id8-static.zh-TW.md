# v4.1.60：ID8 的相關計數、資源配置與 ID9 返回

接續 [ID7 至 ID8 返回](v4160-b1-fallback-id7-static.zh-TW.md)，本輪串接第三個 initializer 的 selector4／record0、資源配置、record／queue 組裝、三個發布呼叫與下一次 task 登記。所選條件成立時，終點為 ID9／count10，停在第四個 outer initializer 呼叫前。

檢查器：[check_v4160_b1_fallback_id8_static.py](check_v4160_b1_fallback_id8_static.py)；證據：[JSON ledger](v4160-b1-fallback-id8-static.json)。所有結果來自原始 bytes、不可變 CFG、區間與閉合整數／frame 證明；沒有執行或模擬目標，也沒有建立可變 target RAM／heap／provider／MMIO／IRQ 模型。原始 bin 未修改，本輪新增 C 重建 bytes 為0。

## q 與低兩位必須共同推導

原始 resource source byte 為 b，先前寫入相鄰兩個 byte：`r=b&3`、`q=(b>>2)+r`。ID8 使用的是 r，不能把它和先前 q 當成獨立參數。對固定 r，q 只能是 r..r+63；q=0 只可能來自 b=0。

檢查器承接四組 first-count 家族：first count0（q>0 時 second pool 成功，q=0 時 second request 為零、未配置），以及 first small count1..3／second request0。每組枚舉同一個 b=0..255，合計1024組條件性來源組合，其中768組 r>0、256組 r=0。First count／tag／fresh header 等先前條件仍須成立，這不是實際 boot 可達性的宣告。

| r | 原請求 `194*r+6` | 配置對齊大小 | Record／queue 使用量 `190*r+6` |
|---|---:|---:|---:|
| 0 | 配置呼叫被略過 | 無新增配置 | 無 payload 迴圈 |
| 1 | 200 | 200 | 196 |
| 2 | 394 | 396 | 386 |
| 3 | 588 | 588 | 576 |

三次低兩位讀取分別發生在配置前、配置後的 fill 長度、fill 後的迴圈計數。原指令沒有比較這三次值；只有在 matching core／fill、合法 owned payload／frame、來源欄位不被所列寫入覆蓋，且沒有不利外部寫入等保存前提下，才可接成 N1=N2=N3=r。

## 大型 free list 的768組配置

| 承接路徑／q | ID8 使用的 free header | 跳過 allocated headers |
|---|---|---:|
| Second 成功，q=1..3 | Resource remainder | 2 |
| Second 成功，q=4 | Second remainder | 3 |
| Second 成功，q=5..66 | Third remainder | 4 |
| First small 成功／second zero，q=1..4 | Resource remainder | 2 |
| First small 成功／second zero，q=5..66 | Third remainder | 3 |

每列仍受 b／q／r 相關限制，不是表中所有 q 與 r 都可任意配對。Tag=`0x4701`，三種非零請求都選 large list；匹配的 fresh head、前置 allocated headers、free header／size／next 是額外前提。每列均滿足 split gap>8，payload P=H+8、新 free header N=P+rounded，remainder 精確接回 sentinel，account 減少 `rounded+8` 後按16 bits 截取。

本輪會刻意把所選 free header 改成新的 allocated header，因此沒有宣稱所有舊 free headers 都保持原值。已配置的 resource／first 或 second／third pool headers 與 payload、未選中的 third remainder header、完整第一張 table payload，均逐列排除覆蓋。新配置與 fill 也排除 fallback、既有 pool pointers、CB48、來源 q／r、task metadata、timer 與已發布的 ID／record1。

JSON 以 `allocation_case_columns` 說明768列緊湊陣列的欄位，包含 first count、b、q、r、free header／size、request／rounded、P、N、remainder、skip 數、account 差額與 layout 使用量；另列256組零分支。它們是不可變幾何資料，不是 heap 或記憶體重播。

## Record／queue 與局部寫入

資源函式在 r>0 時保存新 pool pointer，按 `194*r+6` 清零，再從保留的 r 組裝 r 個 stride184 records。每筆 header 半字設為 `0xffff`；內層15次在 `record+4+12*j` 寫零半字、`record+12+12*j` 寫零 word，j=0..14。所有 stores 都在該184-byte record 內。

Queue 從 P+184*r 開始，有 r+1筆 stride6 records；每筆寫半字 `ffff`、byte+3=`ff`、byte+2=`ff`、byte+4=`00`，第一筆半字再覆寫 `fffe`。Middle pointer=P+184*r，end pointer=P+190*r+6。使用量不超過原請求；對齊 padding 不當作額外 fill 長度。有限 CFG 證書核對 r=1..3、每筆15次內層、r+1次 queue 的邊與 counter 關係，沒有執行目標指令。

r=0 路徑沒有 allocator、fill 或 payload 迴圈，但仍清零三個資源 pointer words，並執行後續發布呼叫。正請求沒有 null guard；本輪只證明列出的正常非零 fit／split 路徑，不涵蓋任意 allocator 失敗或 fallback。

| 局部發布位置 | V1.31 | V1.40 |
|---|---|---|
| New pool pointer | `0x20002f8c` | `0x20002fdc` |
| Middle pointer | `0x20002f90` | `0x20002fe0` |
| End pointer | `0x20002f80` | `0x20002fd0` |
| Hook A word | `0x20002f70` | `0x20002fc0` |
| Hook B word | `0x20002f04` | `0x20002f54` |
| Local ID8 byte | `0x200033ad` | `0x200033fd` |

Initializer 另外把 selector4／ID8 寫到舊48-byte 區塊的 record0，保留 record1 的 selector5／ID7。前輪 F+94 的 `ff00` 半字、F+96 的零 byte、本輪未選中的 pool owners 與 local ID7 也在明確保護範圍內；不能把整段 record block 當作不變。

## 再次登記 callback

兩個 setter 分別發布 `0x4b944／0x4b9dc` 與 `0x4bafa／0x4bb92` 到 Hook A／B word，沒有呼叫那些指標。第三次呼叫把 `0x4b8a6／0x4b93e` 送入先前的12-slot callback-register leaf；其 store 是 CB48 中的預期更新。

- q>0：先前 resource 清零 CB48、第一次登記占用 slot0 的非零 pointer，而其餘零值保留。所有選定的配置／組裝／固定寫入都排除 CB48，故本次登記在這些保存前提下選 slot1。這也涵蓋 q>0、r=0 的零配置路徑。
- q=0：單次 leaf 仍有原始13條 CFG 路徑。若進一步沿用前次每個非零觀察值、成功寫入的非零 pointer，且中間沒有寫入，下一次第一個零 slot 必須晚於前次插入位置，或全滿；前次全滿則下一次仍全滿。檢查器列79組純索引關係，index12代表全滿。這是額外保存前提下的關係，不是原子 table 快照。

Leaf 插入時 A1=0；全滿時 A1 為最後觀察到的非零 slot11 word。資源函式忽略登記回覆，最後固定回傳 A0=0，保留 A1 與 A2=12；不能把 A0=0 解讀成 callback 登記成功。

## Frame、返回與 ID9／count10 終點

ID8 initializer 保存 ID8／RA 於32-byte frame，重載入口 ID8 後呼叫 selector4。其 frame 釋放後，尾跳資源函式；資源函式使用自己的32-byte frame，實際重用已釋放的範圍，而非覆蓋仍存活的 saved ID。正常 allocator／fill 與所有 required S／GP／SP／RA 保存仍是前提。所選階段最高同時存活 outer16＋resource32＋core16=64 bytes。

資源函式普通 RET 回 outer entry+56。Fresh count9、capacity至少14、table pointer仍為 T=`0x200047f4` 時，registrar 把 handler `0x502b4／0x5034e` 發布到 entry9=`0x20004818`，count 更新10，回覆 A0=9、A2=10，A1 保留 callback-register 結果。Entry9 是第一張 table payload 內的預期更新，不覆蓋既有 entry0..8 或配置 owners。

終點為 V1.31 `0x6dd5a → 0x50412`／V1.40 `0x6df4a → 0x504ac`，fallback0、gate5、saved ID6、local ID7／ID8、task count10。第四個 initializer 尚未串接。

## 驗證範圍

檢查器重核先前證據、每個候選13個 strict sparse HEX 範圍、740 bytes／240個本輪原指令護欄、合計1299組變異拒絕、1024組相關來源幾何，以及 callback 與有限 resource CFG 證書。正常與 `-O` 模式均須重算並逐 byte 比對 ledger：

```powershell
python analysis/check_v4160_b1_fallback_id8_static.py
python -O analysis/check_v4160_b1_fallback_id8_static.py
```

實際 installed provider、fresh source／header writers、其他 allocator 失敗與分支、第四個 initializer 與新發布 callbacks 的消費、IRQ／DMA／重入與物理副作用、完整跨事件保存／釋放期仍未完成驗證。所有正常返回與不別名關係都是明列條件，並非實機啟動或輪詢進展保證。
