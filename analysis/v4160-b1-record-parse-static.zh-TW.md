# B1 私有 record parser：檢查、查找與物件寫入

接續[通知與 selector](v4160-b1-notify-selection-static.zh-TW.md)，本階段完整展開私有 `0x5c830／0x5c978`，共 **776 bytes／276 條指令**。它會檢查 packet、查找既有鏈表物件並條件性更新欄位。**查找未命中仍可能返回零，零不是配置、提交或傳輸成功證明。**

[Python checker](check_v4160_b1_record_parse_static.py) 與[固定 JSON ledger](v4160-b1-record-parse-static.json) 保存 operands、原始 hashes、完整 CFG、所有 stores、11 條選定狀態語法路徑／版本及每條 CFG 邊的證書。全程只讀原始 APP／carrier／嚴格 sparse HEX，檢查不可變圖與 host 封閉整數關係；沒有目標執行、模擬、packet replay、硬體連線或目標網路分析。既有 C 重建覆蓋率不變。

## 完整函式與入口服務

| 參考 carrier | 完整 FLASH 範圍 | bytes／指令 | stores／linked calls |
|---|---|---|---|
| V131 | `[0x5c830,0x5c9b4)` | 388／138 | 22／9 |
| V140 | `[0x5c978,0x5cafc)` | 388／138 | 22／9 |

兩版本 local CFG 無環，所有 138 條指令從入口在語法圖可達；唯一 RET 位於 +0x62，後面的多個分支塊仍屬完整本體。32-byte frame 保存 RA、S0..S3。局部無環不保證 callees、鏈表遍歷或整條鏈有限返回。

令入口物件為 N。首個請求是 **RAM `0x2000263a／0x20002686(U32[N+80],0,0,0)`**。它不是 copy helper。重用[完整 128-byte service](v4160-large-consumer-service-static.zh-TW.md)後，這組零參數會略過 packet 解參考與兩個 optional output stores；在 matching implementation、有效服務物件等前提下，本機返回 0／1。非零則 parser 返回 1；零才繼續重新讀 N+80。

service 的控制／狀態讀寫、alias、正常存取與實際綁定仍需前提。不能把這次入口服務當作已經驗證了 packet bytes 或 length。

## 先寫欄位，再依序檢查

令重新讀出的 `U32[N+80]` 為 P；它不必等於首個服務的入口 pointer。parser 先寫：

```text
N+19 = U8[P+0] & 15
N+18 = U8[P+1]
```

之後依序通過以下 gates，否則走共同 status 出口：

| 條件 | 失敗 status |
|---|---:|
| 初次 service 完整回覆為零 | 1 |
| P+0 的低四 bits 等於 8 | 7 |
| 擷取的 byte P+2 小於 64 | 5 |
| 擷取的 byte P+1 等於擷取的 P+2 加 1 | 25 |
| fresh byte P+3 等於 3 | 17 |
| comparator(`fresh U32[N+176]+4`,P+4,6) 非零 | 17 |
| comparator(N+54,P+10,6) 非零 | 18 |
| 先前擷取的 P+2 等於 13 | 24 |

通過這些 scalar gates 必要的擷取 byte pair 為 **P+1=14、P+2=13**；不是實際 buffer 長度或所有來源已初始化的證明。兩次比較會明示涉及 P+4..9、P+10..15，在非零且有效的 comparison 路徑下至少需要 16-byte P 範圍，不能只用 header 宣告長度取代可讀 extent。

兩次呼叫都是 RAM `0x20000442`，重用[完整 72-byte comparator](v4160-comparator-tail-static.zh-TW.md)。它返回 0／1，但任一 pointer 為零時會返回 1。因此非零回覆只有在有效、non-null、非 wrapping 及觀察／alias 前提下才能解讀為六對 fresh bytes 相同；不代表原子快照。它還有固定控制 word 的保存、清零、FENCE.I 與恢復，並非無副作用比較。

N+18／N+19 已在 type gate 前發布，後續拒絕沒有本機 rollback。所有 parser status 都在共同出口由 S2 移至 A0，再恢復原 frame；callee 保存 S2 等仍是跨呼叫條件。

## 查找鍵來自另一服務，不是配置請求

通過 gates 後，呼叫 `0x59e64／0x59fac`。A0 當時是第二個 comparator 的完整回覆，其他參數是 then-live registers；本階段不替這個未知服務指定更窄的 ABI 或副作用。

該服務返回後，沒有先改寫 A0，就呼叫 `0x5784a／0x5798a`。重用[完整 24-byte lookup](v4160-constructor-consumer-tail-static.zh-TW.md)：它由固定全域 word 取得 head，沿 node+0 的 next word 遍歷，以 fresh U16[node+8] 比較**完整入口 key**，命中返回 node，耗盡返回零。這個函式沒有配置指令，也沒有將 key 截為低 16 bits。

全域鏈表有限性、node 有效、key producer、lookup 回覆的 ownership 與存活期仍未證明。key 的 high16 非零時不可能匹配 U16，卻仍不能因此保證遍歷會結束。

lookup 回覆保存為 W。W=0 時跳過全部 W stores、copy、提交與 event-builder 呼叫，仍與非零路徑會合，重新讀 N+172，向該 child+11 寫 3，然後返回 **0**。這清楚限制了「零就是物件建立成功」的解讀。

## W 非零時的明示來源與寫入範圍

令 Q 為這時 fresh 讀取的 U32[N+176]，T 為 fresh U32[N+76]。這些 pointer 與早先比較中的 observations 不自動相同。

| W 目的位置 | 本機來源／請求 |
|---|---|
| +136 word | fresh U32[N+36] |
| +152 word | U32[Q+24] |
| +156 word | U32[Q+20] |
| +53 byte | fresh U8[Q+28] |
| +55 byte | fresh U8[T+21] |
| +56..63 | 四組 LE16：T+22/23、24/25、26/27、28/29 |
| +312、+316 words | 先各寫零 |
| +312..316 | copy(W+312,固定 global source,5) |
| +320 byte | 1 |
| +326、+327 bytes | 同一次擷取的 fresh U8[N+128] |

第一至第三組 LE16 的讀取順序是高 byte 再低 byte；第四組是低 byte 再高 byte。沒有把來源觀察當成一份原子 snapshot。

固定五-byte copy source 是 V131 `0x200034be`、V140 `0x2000350e`。重用完整 58-byte RAM copy `0x20000332`，並重驗 first-copy 的完整來源／目的涵蓋。若 matching forward copy、正常存取、來源有效、所需非重疊／alias 與保存條件成立，先清零的 W+312..319 中，前五 bytes 被 copy 覆寫，W+317..319 保留零。這不是整個 W 初始化完成，也沒有證明 global source 的真實內容或初始化時序。

本機固定存取範圍至少要求 N 180 bytes、Q 29 bytes、T 30 bytes、W 328 bytes，以及 child 12 bytes。這些是需求界線，沒有證明實際配置大小、來源長度、權限或保存期。W+8 的 U16 也沒有在本函式初始化，不能由這份 store 清單推得後續 ID 一定有效。

## 提交、兩個獨立 flag 與 caller 的處理

W 欄位寫入後呼叫 `0x59d3e／0x59e86(W)`，其回覆沒有作為成功 gate。這個服務是否保存 W、是否改變欄位／生命期或具有其他副作用，仍需展開。

之後依兩次獨立 global word observations 選擇 event-builder：

- fresh B+224 的 bit9 設置：builder(fresh U16[W+8],128,41)。
- fresh B+216 的 bit14 設置：builder(另一個 fresh U16[W+8],128,20)。

B 為 `0x200033b8／0x20003408`。第二個 gate 的原指令是 SLLI17 後 signed branch，因此測的是 bit14；它不取決於第一個 gate 是否成立。兩個 call sites 都可能出現，不能把它們當成互斥選擇，也不能假定兩次 W+8 相同或提交後仍有效。

重用[完整 102-byte message builder](v4160-threshold-message-static.zh-TW.md)後，在 matching 配置／存取／送出合約下，對應四個可見 bytes 為 `80 29 IDlo IDhi` 或 `80 14 IDlo IDhi`（均為 hex；41／20 是原始十進位參數）。builder／sender 的失敗、marker、task、鏈表與事件條件仍保留；parser 沒有依 builder 回覆分流，無實際入佇列、消費、delivery 或 release 證明。

[完整上層 record callback](v4160-b1-record-callback-static.zh-TW.md) 在 +0x338 傳 N、+0x33a 呼叫 parser。正常返回後的 +0x33e..+0x350 沒有讀 A0，而是把保存 table 的 byte+9 加一再取低 8 bits，並與另一個 fresh count 比較。因此上層沒有以這個 parser status 阻止這段 cursor 前進；不能由 caller 繼續就推論驗證／提交成功。

## 重播與剩餘界線

```powershell
python analysis/check_v4160_b1_record_parse_static.py
python -O analysis/check_v4160_b1_record_parse_static.py
```

兩模式均核對完整祖先證據與固定帳本。276 個逐指令變異、14 個 typed-load 變異必須拒絕；每版本 148 條 CFG 邊與 11 條狀態語法路徑證書，另有 65,536 組 length byte pairs、65,536 組 LE16 byte pairs、256 個 byte gate 與 32 個 flag basis 的封閉整數檢查。這些不執行目標 parser、比較、copy、lookup 或 provider。

尚需展開 key producer `0x59e64／0x59fac`、提交服務 `0x59d3e／0x59e86` 與後續 `0x5d006／0x5d14e`；實際 provider 綁定、來源 writers／長度、lookup ownership、callback 順序、訊息消費／釋放及完整指標保存期仍未封閉。
