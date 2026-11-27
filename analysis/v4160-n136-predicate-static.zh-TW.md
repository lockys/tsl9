# v4.1.60：N+136 callback、lookup 與 predicate 呼叫合約

本階段封閉兩版完整 callback 與它直接呼叫的 RAM lookup，共新增 **796 bytes** 原始指令證據。另重播兩份已分析的 62-byte predicate，新增的是與目前 consumer 的參數串接，不重複計算這 124 bytes，也不增加既有 C 重建覆蓋率。

| 本體 | V1.31 entry／FLASH source | V1.40 entry／FLASH source | 每版 bytes／指令 |
|---|---|---|---|
| N+136 callback | `57b7c` | `57cbc` | 322／111 |
| RAM lookup | `2000202c`／`4229c` | `20002084`／`42334` | 76／31 |
| 既有 predicate | `200004bc`／`4072c` | `200004bc`／`4076c` | 62／19 |

[完整 ledger](v4160-n136-predicate-static.json) 保留所有 literal operands、原 bytes SHA-256、完整 CFG、calls、stores、路徑與來源映射。RAM bodies 在 RAM PC 解碼；來源映射重用 startup 的 first-copy operands，不能據此宣稱實際已安裝、已啟動或後來仍保持相同內容。

全程離線讀檔與主機圖／整數檢查，沒有執行或模擬目標 ISA、callback、copy、lookup、predicate、MMIO、FENCE、裝置或 mutable register／RAM machine。

## Callback 重新取得物件，沒有依賴入口 A0=N

沿用 [較大 consumer 證據](v4160-large-consumer-service-static.zh-TW.md)，最後一次間接呼叫取自該 consumer 的 N+136，沒有把 A0 重新設為 N。現在確認 matching callback **忽略入口 A0**，自行把 fresh `U32[B+148]` 載入 S0，作為後續物件 N′。

B=`200033b8/20003408`。N′ 不一定等於 caller 先前保存的 N；全域槽位、物件及 callback 在呼叫前後保持的條件仍需證明。入口沒有 N′ null guard，先讀 N′+101，再清 N′+100。frame16 保存 RA、S0、S1、S2；其餘 callees 的保存條件仍是必要前提。

callback 本體的局部 CFG **無環**。先前觀察到的反向跳轉只是分支共用程式碼，不能僅依位址向後跳就判定有迴圈。這也不保證它呼叫的 lookup、其他服務或整條鏈必然返回。

## Tag、來源選擇與 N′+132 指標保存

第一次 tag 為 fresh `U8[N′+101]`，N′+100 在所有正常返回路徑之前都先被清為 0。

- tag=0：N′+100=1，請求 copy6 到 N′+102，來源 G0=`200034a0/200034f0`。
- tag=1：fresh `U8[B+2]` 為零就返回 18；非零則 N′+100=1，以 G1=`200034a6/200034f6` 作 copy6 來源。
- 其餘 tag：先讀 fresh `U32[N′+132]` 指標 Q。Q 非零且 Q+10 byte 非零，則 N′+100=2，以 Q+12 作 copy6 來源。
- Q 為零且 N′+108 byte 非零：以 **A0=N′+108 指標** 呼叫 RAM lookup；完整回覆立即存入 N′+132，之後才檢查回覆是否為零及 Q+10 byte。這是實際的 pointer save，不是只保存 boolean。

找不到可用 Q 時，或 Q-copy 後 fresh N′+100 不等於 2，會進 fallback：**重新讀取** N′+101，等於 2 則選 G0；其餘值再 fresh 讀 B+2，為零返回 18，非零選 G1。前後 tag、Q 與 B+2 不能合併成同一 snapshot。

兩個 copy callsites 都明確請求 `20000332(destination,source,6)`。這沒有證明真實 copy provider、同步完成或借用來源的保存期。返回 18 可能發生於 N′+100 清零、lookup 請求或 N′+132 寫入之後，不能當作沒有副作用的拒絕。

callback 固定 N′ accesses 需要至少 136 bytes，B 的固定欄位至少 152 bytes；若把兩個來源也視為同一個連續 B block，則需要至少 244 bytes。Q 的 byte+10 讀取需要 11 bytes，Q+12 的 copy6 請求需要至少 18-byte 範圍。實際 extent、alignment、nonalias、生命週期及 child effects 未因這些地址界線而成立。

## Lookup：查詢描述符是借用指標，鏈表遍歷尚無界限

完整 RAM lookup 為 76 bytes／31 instructions，frame32 保存 RA、S0～S3。query 保存於 S1，query+2 保存於 S2；head 來自 fresh `U32[B+204]`。

每個 node 比較 fresh `U8[node+3]` 與另一個 fresh `U8[query+1]&1`。相等才請求 `20000442(query+2,node+4,6)`；**回覆恰等於 1** 時返回當前 node pointer。其餘情況沿 fresh `U32[node+60]` 繼續。head 或後續 next 為零時返回 0。

空鏈表不解參考 query；非空時沒有 query null guard。選定 compare 請求需要 query 至少 8 bytes，next 讀取需要 node 至少 64 bytes。callback 傳入的 query=N′+108，包含 flag byte、下一個 byte 與六個來源 bytes；lookup 本機沒有把 query address 寫入非 frame memory，但會借用給未知 comparator。

lookup **確實有鏈表迴圈**。目前沒有證明 node next 無環、比較 provider 的完整行為、指標保存期、遍歷完成或返回 node 在存入 N′+132 後仍有效。本體只做 frame stores；不能由此推論 nested comparator 沒有寫入或保存參數。

## 成功尾段的實際返回與事件參數

所有來源選擇成功路徑共用以下尾段：

1. `43eb2/43f3e(0,00ffffff)`，完整 A0 回覆存入 N′+92；上界是 `00ffffff`，不是 `ffffffff`。
2. 呼叫 `640d8/641c2`，完整回覆存入 N′+88；此處沒有替它臆定 seed、時間或完成語義。
3. `43e6a/43ef6(5,16)`，回覆低 8 bits 存入 N′+12；另寫 N′+7=1、N′+4=3。
4. fresh N′+56=3 時 A2=`U16[N′+52]+U16[N′+70]`；=2 時只用後者；其餘用前者。加法結果最大 131070，呼叫前沒有截為 halfword。
5. `43932/439be(fresh U8[C+3],16,A2)`，之後 `4354a/435d6(另一個 fresh U8[C+3],16)`，C=`2000319c/200031ec`。兩次 task byte 不能合併 snapshot。
6. 清 B+0，明確設 A0=0，恢復 frame 並返回。

這裡的 16 是十進位。局部正常返回值為 0 或 18；尾段服務回覆並不直接作為 callback 的最終 status，也沒有證明排程事件已送達或 async 工作完成。不同 callee 的兩版位址差不同，checker 逐一核對；lookup 位址差為 88，callback entry 差為 320。

## Predicate：零回覆不能作 copy 的完整來源驗證

完整 predicate 已有 `analysis/v4160-resident-memory-2026-10-22/precopy-review/check.py` 的 sealed proof；兩版 62-byte 原始 bytes 相同，SHA-256 為 `39eff00fe85a0bdea780df359a1f1d1356681a168097a60b7b805faac6303581`。本次以現有 strict decoder 重播原指令，串接 consumer 的 `(entry A3,0,6)` 請求。

predicate 的順序是：**讀取並保存 `U32[4002420c]`、寫零、FENCE.I，然後才檢查 source 是否 null／length 是否為零**。正常退出前在兩個 restore sites 寫回先前保存的 word。即使 null 或 length0 也有這些控制欄位操作；沒有執行它們，也未證明板端意義、原子性、外部干擾或異常時恢復。

非 null／length 非零時，逐 byte 讀取並與完整 A1 比較，不將 A1 截為 byte。任一 mismatch 返回 0；全部 length 次比較通過返回 1。A1>255 不可能匹配 LBU，首 byte 即返回 0。

在普通 uint32 地址／指令語義及每次存取有效完成前提下，pointer 每次加一，固定 end=(P+n)mod2³²；n>0 時，最多 n 次成功比較就到 end，mismatch 可更早返回。這是 index 算術，不是目標迴圈執行或有效記憶體證明。每次 byte 仍是 fresh observation，不假定整段來源為原子 snapshot。

對目前 `(source,0,6)`：null 返回 0；非 null 遇到非零 byte 就返回 0；六次讀取都為零才返回 1。consumer 恰在 **零回覆** 時設 N+108=1 並請求後續 copy6，因此零回覆不保證 source 非 null，也不保證完整六個 bytes 可讀。控制欄位若與 source alias，讀到的內容還可能受到前面的 clear 影響。

predicate 只改 A0、A3～A5，無 frame／calls，沒有 payload writes 或直接保存輸入 pointer 的 store；這不等同整條呼叫鏈沒有保存指標或物件內容保持不變。

## 可重播檢查與剩餘範圍

[Checker](check_v4160_n136_predicate_static.py) 核對 322 次原指令變異、44 條選定 CFG walks、354 條 edge witnesses、constructor／consumer／startup joins，以及控制操作必經路徑、完整 A1 比較、有限 pointer-step 與數值範圍。這些是靜態圖與整數證據，不宣稱選定路徑實際可達或 callees 都返回。

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_n136_predicate_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_n136_predicate_static.py
```

仍需展開 `20000442` comparator 與尾段 callees，追查 B+148、N′+132、鏈表／來源 writers，以及真實 installed provider、nonalias、物件與借用 pointer 保存期。
