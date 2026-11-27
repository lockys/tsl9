# B1 retry 計數、callback 發布與 RAM 派送的靜態合約

接續 [fallback 與 shared-tail 驗證](v4160-b1-fallback-tail-static.zh-TW.md)，本輪完整核對兩版候選 resident 的 retry、發布服務與 RAM dispatcher，共 **240 bytes、76 條原指令**。三者都沒有本機 linked call 或 frame；dispatcher 的成功出口是 `JR T1` 尾跳，不能把它視為已完成 callback。

[Python checker](check_v4160_b1_retry_services_static.py) 與 [固定 JSON ledger](v4160-b1-retry-services-static.json) 保存完整指令、operands、hashes、CFG、每條 edge 的出口見證及條件性串接。所有分析僅讀取原始 bytes／strict sparse HEX，使用不可變 CFG、暫存器 def-use 與封閉整數恆等式；沒有執行／模擬目標、建立可變目標狀態、重播封包或存取硬體。

| 完整本體 | V131 | V140 | 每版 bytes／指令 |
|---|---|---|---|
| retry | `[0x56146,0x56184)` | `[0x56286,0x562c4)` | 62／19 |
| callback 發布 | `[0x43ed2,0x43edc)` | `[0x43f5e,0x43f68)` | 10／3 |
| RAM 派送 | `[0x200009ba,0x200009ea)` | 同左 | 48／16 |
| 派送本體的 FLASH 來源 | `[0x40c2a,0x40c5a)` | `[0x40c6a,0x40c9a)` | 上列 RAM 本體的來源，未重複計數 |

RAM 指令以執行位址解碼，並核對 first-copy 的完整來源範圍與 affine 映射。兩版候選仍是參考映像，尚未證明是 APP 實際 installed provider。

## Retry：carry 與 reset 使用不同的高字取樣

入口 `A0=P`。本機順序為：

```text
L = low32(fresh U32[P+236] + 1)
U32[P+236] = L
若 held L == 0：
    U32[P+240] = low32(fresh U32[P+240] + 1)
重新讀取 H = fresh U32[P+240]
若 H & 128：依序寫 U32[P+236]=1、U32[P+240]=0
F = fresh U8[P+42]
若 F & 64：寫 byte[P+42] = F | 32
RET；A0 仍是入口 P
```

只有 A4/A5 被定義；直接 P prefix 至少需要 244 bytes。這裡沒有配置、釋放或完整指標發布。P+42 bit6 未設時沒有 byte store，並非清除 bit5。

在欄位穩定、途中無其他寫入者的假設下，reset 之前的 low/high 更新等價於 unsigned 64-bit 加一。reset 檢查的是高字 **bit7，也就是串接值的 bit39**，不是 bit63，也不是任意輸入都成立的 modulo `2^39` 正規化。

若進入時已滿足 `0 <= V < 2^39`，同樣在穩定取樣假設下，`V=2^39-1` 會重設為 1，其餘加一；0 也前進至 1。若高字是 256，bit7 仍未設，更新後更高位可以保留，不能反推全域一直遵守 39-bit 範圍。carry 的高字取樣、其後 reset 的高字取樣、flag 的 byte RMW 都非原子操作。

已重用完整 prior shared-tail 及 18-byte parent retry 閘門，確認呼叫目標與 `A0=P`。parent 仍有其他迴圈與呼叫；這只補上本機 retry 合約，未證明重試進展、終止或實際可達的初始計數。

## 發布服務：寫入 D+16，原樣回傳傳入 word

令 `G=0x20003000`，`D=0x20003234／0x20003284`。發布服務完整三條指令為：

```text
LUI A5,G
SW A0,580／660(A5)       # U32[D+16] = 入口 A0
RET                     # A0 未改變
```

它沒有讀取、null guard、callback call、獨立清零路徑或釋放，也沒有判斷傳入值是否為有效函式指標。無條件寫入代表傳入 0 時也會清零 D+16，並原樣回傳 0。故舊 shared-tail 的 `+0xbe` fresh pending-word load、`+0xc2` 呼叫與 `+0xde` 正常 RET 可再縮小為：**傳入的那個 held word 同時寫到 D+16，並原樣回到 caller A0**。其他 earlier callbacks 的副作用仍依既有證據界線保留。

pending word 是 `G+1260／1340`，即 `0x200034ec／0x2000353c`，與 D+16 是不同 cell。它也不同於 registered-hook slot、delay-callback slot；跨版本恰巧相同的數字位址不能當成同版物件同一性的證據。

## 消費端：依序檢查兩個 byte 與 callback word

RAM `0x200009ba` 的完整順序為：

| fresh 取樣與分支 | 本機結果 |
|---|---|
| U8[G+415／495] 為 0 | A0=1，RET |
| 第一項非零、U8[D+12] 為 0 | A0=2，RET |
| 前兩項非零、U32[D+16] 為 0 | A0=255，RET |
| 三項均非零 | `JR T1`，跳向剛讀取的 callback word |

成功尾跳之前沒有 A0/A1/RA/SP 定義，所以交給 callback 的是 **dispatcher caller 當時傳入的 A0/A1**。這不是把發布服務收到的函式位址再當成 callback 的資料參數。此 dispatcher 沒有 store、slot clear 或 free，也不保證 callback 返回、一次性消費或 callback 執行後的標量結果。

## 條件性來源、selector 輸出與清零界線

重用 [key-source tail](v4160-b1-key-source-tail-static.zh-TW.md) 的完整 168-byte 本體與 [RAM selector](v4160-b1-ram-record-callback-static.zh-TW.md) 的完整 222-byte 本體：

- key tail 的 D+12 非零分支，在捕捉的 pending word 為零時，把 fresh D+4 寫入 B+176，再於 `+0x30` 把固定 literal `0x200013e8` 寫入 pending cell。
- `+0x34` 重新讀 pending 作為 A0，`+0x3c` 呼叫發布服務；fresh reload 不保證仍等於先前 literal。pending 原已非零也會跳過 literal store。D+12 為零的另一分支在 `+0x5e` 清 pending。
- 若 D+16 在派送時仍等於 `0x200013e8`，且實際 RAM code 與候選相符，尾跳才會接入該 selector。selector 的入口 A0 是 caller 的借用 Out，需要至少 4 bytes 可寫空間；沒有本機 Out null guard。
- selector 會遍歷 registry、呼叫 query，並可能交出 SP+12。其本機沒有先初始化 SP+12，故 query 輸出初始化、是否保存該指標、鏈表終止與物件存活仍須追查。B+176 儲存的是 scalar，不能把它誤認成 Out 指標。

另重用 [完整 config gates](v4160-config-gates-static.zh-TW.md) 的兩版 220／228-byte 函式：V140 在入口 `+0x0c`，於 optional hook 與參數驗證前，直接清零 **D+16**；V131 該本體沒有對應的前置 clear。這是永久綁定尚未成立的具體界線。

config 的 16-byte copy 範圍只覆蓋 D+0..15，數值上排除 D+16；不能因此排除未知 copy／optional hook 或其他 callee 的額外副作用，也不能保證槽位在兩次呼叫之間保持不變。指標發布／清零不等於 free、排空 in-flight callbacks 或 ownership transfer。

## 驗證與後續缺口

```powershell
python analysis/check_v4160_b1_retry_services_static.py
python -O analysis/check_v4160_b1_retry_services_static.py
```

新三個本體每版的 CFG edge 數為 21／2／15，DAG 語法路徑數為 8／1／4；每條 edge 皆有有限出口見證，並非目標執行軌跡。負向核對涵蓋 **76 個逐指令變異與 14 個 typed-load funct3 變異**。封閉整數核對包含 262144 組 high/low 邊界族、另 65536 個 canonical low16 值，以及全部 256 個 flag byte；這些樣本不代表所有 U32 pair 或實際可達輸入。

checker 重跑既有驗證鏈、APP／SDK／兩版候選身份、strict sparse HEX 及固定 ledger。接續仍需定位 dispatcher 的實際 callers、其他 pending／D+16／gate writers、呼叫順序、provider 綁定、別名與完整消費釋放及指標保存期。

本輪增加候選 resident 的靜態合約，**沒有增加 APP 的 C 重建覆蓋**；既有約 95.75% 靜態重建快照不代表完整可用韌體或實機功能已驗證。
