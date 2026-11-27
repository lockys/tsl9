# v4.1.60 setup callback：槽位消費、實參與返回後清零

接續[setup 下游服務](v4160-b1-setup-services-static.zh-TW.md)。本輪把 setup 登記的 literal callback，接到完整 event dispatcher 的同槽位讀取／呼叫／清除原指令，並核對 callback 與 common body 的可能重新登記路徑。兩版仍為 **resident 參考候選**；這是條件性靜態串接，沒有宣稱實際啟動順序、installed provider 或實機功能。

主要結論：**消費端先捕獲槽值，非零才呼叫；清零發生在 callback 正常返回之後，沒有比較槽位當前值。** Callback 內存在通往 common body 的語法路徑，後者可再登記同一 literal。因此不能將這些指令解讀為「恰好一次」或「重新登記必定留到下一次」的合約。

## 完整原指令與來源

| 重用本體 | V131 | V140 | bytes／instructions |
|---|---|---|---|
| event dispatcher | RAM `0x200007d0`，FLASH `0x40a40` | 同 RAM PC，FLASH `0x40a80` | 各 438／150 |
| callback | `0x55480` | `0x5555e` | 1064／356；1154／387 |
| callback switch table | `0x6e50c` | `0x6e6fc` | 各 52 bytes／13 words |
| common body | `0x54c08` | `0x54cd2` | 各 1220／443 |

本輪重新核對 **5534 code bytes／1929 instructions，加 104 table bytes／26 words**。它們全部已有完整原指令檢查，本輪新增的是跨函式 def-use 與控制流證書；**新增原始 byte 覆蓋為 0，APP C 重建覆蓋率不變**。

重用[完整 event dispatcher](check_v4160_event_dispatch_static.py)、[callback／函式表](check_v4160_callback_dispatch_static.py)與[common body](check_v4160_list_common_body_static.py)的 guard。每個範圍都與保留的 sparse HEX 逐 byte 對照；event 的 first-copy source／destination／末址也再次核對，缺口不以零補齊。本輪另以 radare2 對照兩版 FLASH 的槽位讀取、null 分支、JALR、清零與 cursor／count 比較指令。

## Producer 與 consumer 是同一個槽位

令 event metadata `M=0x2000319c／0x200031ec`，`G=0x20003000`。Setup 的 registrar 呼叫傳入 `(literal callback, index=0)`，條件性 store 與 event 的 hook slot 恰好一致：

| 版本 | M+44 hook slot | setup 發布的 literal |
|---|---|---|
| V131 | `0x200031c8` | `0x55480` |
| V140 | `0x20003218` | `0x5555e` |

這證明的是固定地址與 literal 相符。仍須另外證明實際執行了登記、讀取時該 word 仍是此 literal、對應 code／startup mapping 適用，以及沒有其他 writer 或非同步干擾。

## 消費端捕獲一次，正常返回後直接清除

以下偏移以十進位表示，相對 event RAM 入口 `0x200007d0`，兩版相同：

```text
+358  A5 = fresh U32[M+44]
+362  若 A5==0，跳至 +370
+364  透過捕獲的 A5 間接呼叫，link=+366
+366  U32[M+44] = 0
+370  A4 = fresh U8[M]
+374  A5 = separately fresh U8[M+1]
+378  使用這兩個 byte 做 unsigned bounds 比較
```

對應呼叫 PC 是 `0x2000093c`，清零 PC 是 `0x2000093e`。JALR 使用 `+358` 捕獲的值；null gate 與呼叫之間沒有重新載入槽位。槽值為零時跳過呼叫與清零。

非零路徑只在 callback 正常返回、S2 仍保存 G、frame 與存取有效等前提下接到清零。`+366` 沒有讀取舊槽值、比較當前槽值或檢查 callback 回覆。它不是 compare-and-swap，也不是呼叫前將槽位取走。若 callback 沒有返回，這筆後置清零不會沿此 local return edge 發生；沒有建立取消、互斥或排除重入的證據。

## Hook 的 A0 是完整合併值，並非物件指標合約

Event dispatcher 先於 `+314` 呼叫 task handler。其 A0 回覆經過 fresh U16 return-mask 與另一個 fresh pending-halfword 的運算，再傳給 hook：

```text
hook_A0 = full32((opaque task-handler A0 & ~fresh U16[M+64])
                 | separately fresh U16[pending location])
```

`+344` 將結果寫入 pending **halfword**，不會把 A0 register 截成 16 位。Hook `+364` 前的最近 A0 定義是 `+342` 的 OR；高 16 位仍可能保留 handler 回覆的內容。不能把它預設為 task ID、payload pointer 或只含 U16 的值。

Hook 前也沒有重新組裝 A1／A2；它們來自 task handler 返回後的 caller-saved registers，不能直接沿用呼叫該 handler 之前的實參。

Hook 回覆不控制緊接的清零或 `+378` 分支；該分支使用重新讀取的 cursor／count。但 A0 並未立刻被丟棄：非零路徑仍保留 callback 回覆，null 路徑保留 earlier 合併值，後續路徑可能將其帶到下一個 call 或 RET。因此不宣稱「callback 回覆完全無影響」。

## Callback 的物件 N 另有來源

匹配的 callback 在入口獨立讀取：

```text
B = 0x200033b8 / 0x20003408
N = fresh U32[B+100]
```

N 取自 `0x2000341c／0x2000346c`，而非把 hook 入口 A0 當成 N。Callback 捕獲 N 後，以 fresh U8[N+11] 決定 switch／redispatch；N 指標沒有每輪重新讀取，也沒有在第一次解參考前的 null guard。`N+20` 也由這個捕獲指標派生。

**尚未證明 N 與 setup 入口 P 為同一個物件。** 槽位 literal 串接不會自動補足 B+100 的 producer、有效 extent、配置來源、release 後狀態或 ownership。

完整 callback 有 48-byte frame，保存／恢復 RA 與 S0～S6，唯一普通 RET 在 `+0xd0`。本輪再次核對這些配對、兩版完整函式與 13-entry switch tables。這些是 encoded frame／CFG 證據，仍依賴 nested callees、frame 存取與別名／非同步保存條件；callback 的迴圈、等待與子呼叫沒有因此取得必定終止保證。

## 可能的重新登記，不能假設新值存活

Callback 的 `+0x26c／+0x26e` 會以捕獲 N 呼叫 matching common body。完整 common body 在 `+0x498..+0x4a2` 形成同一 callback literal、A1=0，再呼叫同一 registrar，因此存在語法上的同槽位重新發布路徑：

```text
event hook call
  -> callback
     -> matching common body
        -> registrar(callback literal, 0)
        -> common frame 恢復後 tail，若正常返回則回到 callback
  -> callback 若正常返回
  -> event 直接清零 M+44
```

Ledger 保留 callback 入口至 common call、common 入口至 registrar、registrar link 至 tail，以及 callback link 至 RET 的有限 CFG walk。它們只證明原指令／edge 的語法連接，**沒有證明跨函式分支資料可達或實際發布順序**。

因此可以確定後置清零沒有保留新值的比較機制；若同槽位重新發布確實發生在該清零之前，它也可能被覆蓋。反之，null 分支略過清零；若有 writer 在 null 取樣之後發布，該次指令路徑沒有額外清除。這些是順序與缺少比較的界線分析，沒有建立可變 target memory、callback 或 IRQ 模型，也沒有實際觸發重入／競態。

## 驗證與剩餘缺口

[檢查器](check_v4160_b1_setup_event_static.py)與[固定 ledger](v4160-b1-setup-event-static.json)逐 byte 核對原始輸入、strict sparse HEX 與完整本體，記錄 producer／consumer 固定槽位、callsite reaching definitions、null／非零路徑、frame 與重新發布 walk。Ledger 保留本體雜湊、指令數、CFG 及既有完整 guard 名稱；指令清單沿用已發布的原檢查器，避免重複收錄。拒絕 **1929 個逐指令突變、214 個 load 型別突變、26 個 table-word 突變**。另核對 524288 個 host 整數組合，確認完整 hook A0 與截斷 halfword store 的區別，沒有推定真實 handler 回覆域。

```powershell
python analysis/check_v4160_b1_setup_event_static.py
python -O analysis/check_v4160_b1_setup_event_static.py
```

全程離線，沒有執行或模擬目標韌體、硬體存取、封包重放或 target network。尚需追查實際啟動／JT0／provider 綁定、callback 呼叫當下的槽值與登記順序、B+100 的來源與保存期、其他 writer／IRQ／重入順序，以及完整 buffer 消費釋放與 notification 指標保存合約。
