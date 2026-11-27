# v4.1.60 B1 setup：完整本體、長度調整、組裝及正常返回

本次接續[可選欄位與 helper](v4160-b1-setup-options-static.zh-TW.md)，核對兩個 resident **參考候選**的完整 setup 原指令，接通先前的 `+0x188／+0x396` 出口、資料組裝、四個 payload copy callsites、等待迴圈和唯一正常返回。這是候選原指令的靜態合約；沒有證明 v4.1.60 APP 實際 installed provider、可用韌體或實機功能。

| 候選 | 完整範圍（末址不含） | 原指令 |
|---|---|---|
| V131 | `0x5d006..0x5d5c4` | 1470 bytes／467 instructions |
| V140 | `0x5d14e..0x5d70c` | 1470 bytes／467 instructions |

合計完整核對 **2940 bytes／934 instructions**。其中先前的 prefix 已覆蓋 784 bytes／260 instructions；本次新增凍結的後段為 **2156 bytes／674 instructions**，沒有將重複 prefix 算成新增，也沒有增加 APP C 重建覆蓋率。APP 仍為 76800 bytes、SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。

## 勘誤：初始 count 是 1

前一份 options 文件的條件表把初始 `Q+2` 寫成 2，對應的 host scalar family 也以 2 為假設。完整原指令確認兩版都是 `+0xd6 LI A4,1`、`+0xd8 SB zero,3(S5)`、`+0xdc SB A4,2(S5)`，即 **Q+2=1、Q+3=0**。因此，在物件同一性、欄位穩定、無別名／外部改寫且 callee 正常返回等條件下，該表應更正為：

| bit9 分支 | bit10 分支 | 條件性 Q+2 | 條件性 Q+3 |
|---|---|---|---|
| 不取 | 不取 | 1 | 0 |
| 取 | 不取 | 2 | 4 |
| 不取 | 取 | 3 | 8 |
| 取 | 取 | 4 | 12 |

本檢查器明確核對初始化指令，並用初始 1 的條件族重新核對全部 U16 length；取代先前初始 2 的推導。原先已凍結的指令、fresh loads、分支目標及 `253-c` signed 比較公式沒有因此改變。歷史 checkpoint 保留，勘誤以本文件與新 ledger 為準。

## 記號與前提

下文偏移均相對各版 setup 入口。`P` 是 `+0x38` 捕獲的入口 A0（S8）；`Q` 是 `+0xc4` 載入的 P+76（S5）；第二輪的 `Q′` 是 `+0x432` 重新載入的 P+76（S9）。`G=0x20003000`；`T` 等全域指標每次按原指令重新讀取。Q 與 Q′ 不預設相同，後續 `fresh P+76` 也不與它們自動等同。

`fresh U8/U16/PTR` 表示當次原指令的獨立載入，不把不同取樣合成同一份資料。U8、U16 分別為零擴充的 byte／halfword。所有公式描述編碼的寫入或呼叫請求；容量、有效指標、外部 writer／IRQ 時序和 callee 保存條件仍須另外證明。

## 長度 gate 與 mode 組裝

第一個 gate 在 `+0x184` 做 **signed BGE**：`253-fresh U8[Q+2] >= fresh U16[P+132]`。成立時跳到 `+0x396`，清除重新讀取的 B+124 bit4，再回到 `+0x20c`；這個出口不是函式返回。不成立才進入 mode 組裝。第二輪 `+0x496` 改用 `254-fresh U8[Q′+2] >= fresh U16[P+114]`，成立則跳過第二輪 mode 組裝。

| 當次 P+128 mode | base | `(base+439) signed DIV 30` | 寫入 T+96 的 `60*q` |
|---|---|---|---|
| 1 | 1064 | 50 | 3000 |
| 2 | 17040 | 582 | 34920 |
| 其他 byte | 2120 | 85 | 5100 |

mode 2 的離線尾段 `+0x38e` 會回到共用除法；沒有繞過組裝。組裝會設置 fresh B+124 bit4、寫 T+8=4096、T+96=60*q，並設置持有的 Q 或 Q′ 的 byte3 bit4。三個 byte 的位置分別使用先前 count、另一個 fresh count、再另一個 fresh count，base 也分開載入 P+76：

```text
byte[first fresh P76 + inherited count + 3] = fresh U8[P+126]
byte[second fresh P76 + fresh count + 4] = low8(q)
byte[third fresh P76 + another fresh count + 5] = low8((q >> 8) | (fresh U8[P+128] << 5))
held Q/Q′ byte2 = low8(another fresh count + 3)
```

最後 mode byte 是重新載入，不能直接用選取 q 的那次 mode 代替。第二輪使用相同常數／公式；S5 此時已改作 17040，S11=2120，不能繼續視為第一輪 Q。

## 第一輪的其他組裝

P+96 bit6 可再把 fresh P+21 byte 寫入 `fresh P76+fresh Q2+3`，設 Q3 bit6，並將另一個 fresh Q2 加 1。這些寫入位於 payload copy 之前，前面的 length gate 不是它們的容量保證。

`+0x23c..0x248` 的 low8(P124−16) 比較，僅 byte 16／17 進入固定區塊。捕獲 `Z=fresh P76+fresh Q2+3`，先寫 Z[0]=8、Z[1]=40，再請求 `copy(Z+2,G+1214/1294,5)`。

copy 返回後**重新讀取 P124**：若等於 16，將 `low16(fresh U16[P136]+8)` 寫入 P130，並寫 P124=17；否則比較 `fresh U16[P130]−fresh U16[P136]`，差值不大於 2 才寫 P124=18。之後 Z[7] 取 fresh U8[P130]，Z[8] 取另一個 fresh U16[P130] 的高 byte；不能宣稱兩次讀取構成同一個穩定 U16 快照。最後 fresh Q2 加 9。

## Payload copy、欄位更新與 header

| 階段 | 捕獲 length | 來源 | 目的請求 | bit4 設置時的 N | bit4 清除時 |
|---|---|---|---|---|---|
| 第一輪 | U16[P132] | fresh PTR[P168] | fresh P76+fresh Q2+3 | low8(254−c) | 請求捕獲的 U16 length；返回後 N 另讀 U8[P132] |
| 第二輪 | U16[P114] | fresh PTR[P120] | fresh P76+fresh Q′2+3 | low8(254−c) | 請求捕獲的 U16 length；返回後 N 另讀 U8[P114]，再 SH 0 到 P114 |

捕獲 length=0 時跳過該 payload copy，N=0。是否分段由當次 Q3／Q′3 bit4 決定，與全域 B124 的重讀分開；沒有把兩者的穩定性當成事實。分段 copy 返回後，第一輪使用 **fresh P168+持有 N →P120**、`low16(fresh U16[P132]−N) →P114`；第二輪則 **fresh P120+N →P120**、`low16(fresh U16[P114]−N) →P114`。第二輪將 N 暫存於 SP+12 跨過 copy，再重新載入。來源指標與剩餘值均是返回後重讀，不能自動認為等於呼叫前快照。

header 由 `low8(N+1+(fresh count & 63))` 算出，寫入 P17 與 fresh P76 的 byte1；重新取樣的 count 也寫回持有 Q／Q′ byte2。之後 dispatch 的 A2 又重新讀取 P17。四個 payload copy 的 scalar A0 回覆都在被讀取或傳給下一個 call 之前遭新 A0 定義覆蓋；**N 不是 copy 回覆，也不是已證實複製成功的 byte 數**。第一輪整段 copy 後沒有清除 P132 或 P114；第二輪整段路徑明確清除 P114。

copy 請求的 `low8(254-c)` 在 c=254 時為 0、c=255 時為 255，不是飽和減法。U16 剩餘量按 low16 儲存；不能僅憑這些指令排除下溢或建立有效容量上限。

## 發布、等待與唯一正常返回

第一輪先把 **fresh P76 發布至 fresh T+112**；發布的是組裝 buffer 指標，沒有證明 ownership transfer。接著呼叫 `0x43b28/0x43bb4`、RAM `0x200026ba/0x20002706`，以及 `0x63e58/0x63f42`。RAM 呼叫的實參是 `(A0=0,A1=fresh U8[P128],A2=fresh U8[P17])`。第二輪也使用同一 RAM 服務與重讀實參，並清 H+3。這三組 callees 的完整副作用／指標保存還未在本輪閉合，不能把呼叫完成稱為實際 TX 成功。

`+0x368` 重讀 B124 bit4：清除才進共用 epilogue；設置則跳到 `+0x3c6` 的 bit5 等待。bit5 清除時重讀迴圈本身，沒有 encoded timeout。bit5 設置後會再次讀 B124 並清 bits4/5、重新設定 R/T/U 欄位、取得 Q′，重新建立 byte0=7、byte3=0、byte2=1；第二輪只保留 bit10 的兩 byte 可選組裝，沒有重走 bit9 helper。第二輪 dispatch 後 `+0x5aa` 回到 `+0x368`，可能再循環。

完整 CFG 每版 467 nodes／485 edges；所有節點可由正常入口**語法上**到達，且每條 edge 都有入口至唯一 RET 的有限 walk 證書。另有一個 160-node cyclic SCC，範圍最小 `+0x368`、最大 `+0x5bc`。有限 walk 與 SCC 分析沒有證明分支資料可達、IRQ 會推進、polling 必定終止或整體 loop 有上限。

唯一正常 RET 在 `+0x38c`。`+0x370..+0x388` 恢復 RA 與 12 個 S registers，`+0x38a` 釋放 80-byte frame；全部 epilogue 指令在正常 CFG 上支配 RET。除入口 SP−80 與返回 SP+80 外沒有其他 SP 定義。結論依賴 callee 維持 ABI、frame 未被別名覆寫等前提；不涵蓋 trap／異常返回。

RET 的 A0 最後來源是 `+0x360` 的 `0x63e58/0x63f42` 回覆，或最後一輪 `+0x5a6` 的 RAM dispatch 回覆，**沒有固定 success=0 合約**。持有的入口 P、Q、Q′ register 定義與四條 payload copy 的 A0 kill 均有 CFG def-use 證書；這不是 heap 物件保存期證明。

## 重用的參考 copy 與驗證範圍

將 RAM `0x20000332` 連回 first-copy 的候選來源 `0x405a2/0x405e2`，strict HEX 對照全部 58 bytes／18 instructions，重用[完整 APP NV callbacks 檢查器](check_v4160_app_nv_callbacks_static.py)的 copy body。原指令無 local frame／nested call，只定義 A3/A4/A5/A6，正常 A0 保留入口 destination。null src、null dst 或 zero length 都會略過 forward-byte loop；caller 後續欄位更新不構成確實複製成功的證據。沒有證明 memmove、非別名、有效 extent、控制 word／FENCE.I 實體語意、actual installed binding 或非同步保存合約。

檢查器針對兩版完整本體凍結 boundaries、operands、targets、hashes、98 stores／版、113 typed loads／版與 13 個 QingKe byte-store forms／版；拒絕 934 個逐指令突變及 226 個 typed-load 突變。Host scalar 核對包含 65536 個 mode／fresh-mode 配對、262144 個更正 count／U16 gate 組合、458752 個 U16 subtraction 邊界族及全部 byte count／16、17 predicate。沒有建立 target buffer、packet 或 IRQ 模型，也沒有執行／模擬目標韌體或連線裝置。

```powershell
python analysis/check_v4160_b1_setup_full_static.py
python -O analysis/check_v4160_b1_setup_full_static.py
```

[檢查器](check_v4160_b1_setup_full_static.py)與[固定 ledger](v4160-b1-setup-full-static.json)保留原始輸入身份、strict sparse HEX 與既有驗證鏈。下一步是展開上述 opaque callees，確認其 ABI／欄位副作用、實際 buffer 分配與 provider 綁定，再串接消費釋放與完整保存期；本輪未證明完整可用韌體。
