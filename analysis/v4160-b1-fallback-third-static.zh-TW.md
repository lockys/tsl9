# v4.1.60：第三個 pool、getter 保存與 parent 返回

本輪接續 [parent 配置與 record 前段](v4160-b1-fallback-parent-static.zh-TW.md)，將先前選定的路徑接過兩次 getter、`0x4c06` 配置、parent 尾跳，以及下一次 task 登記。條件成立時，終點為 ID7／count8，停在第二個 outer initializer 呼叫前。

檢查器：[check_v4160_b1_fallback_third_static.py](check_v4160_b1_fallback_third_static.py)；證據：[JSON ledger](v4160-b1-fallback-third-static.json)。使用原始 bytes、不可變 CFG 與區間／整數證明；沒有執行或模擬目標程式，也沒有建立可變 target RAM、heap、provider、MMIO 或 IRQ 模型。本輪沒有增加 C 重建 bytes，不能據此宣稱可用韌體或實機完成度提高。

## 兩次 getter 的來源與界線

| 項目 | V1.31 候選 | V1.40 候選 |
|---|---|---|
| Parent | `0x4da70` | `0x4db08` |
| Getter | `0x4efd8` | `0x4f070` |
| Getter 的 unsigned byte 來源 | `0x200033b4` | `0x20003404` |
| 第三個 pool pointer | `0x20003318` | `0x20003368` |
| Callback 登記 leaf | `0x4efe2` | `0x4f07a` |
| Callback table 起點 | `0x20003358` | `0x200033a8` |

Getter 是完整 10-byte／3-instruction 函式，只讀一個 U8，寫 A0、A5，沒有 store、frame 或巢狀呼叫。Parent 先以 `12*g1`、tag `0x4c06` 呼叫配置核心，保存回覆；回覆非零時才再次讀 getter，以 `12*g2` 清零 payload。U8 的最大乘積為 3060，指令的 low16 截取在此域內不改變值。

兩次讀取彼此獨立，程式沒有比較 g1、g2。本證明沿用已限定的 q=0..66 資源來源，逐一排除配置 header、accounting、control、pool pointer 與 payload 寫入對 count／相鄰 lowbits 欄位的覆蓋。在匹配的實際 core／fill、有效且不別名的配置與 frame、沒有不利的外部寫入等前提下，才能接成 g1=g2=q。這不是原指令提供的原子快照保證。

## 264 組第三池成功配置

承接兩組先前路徑：first count=0、second pool 配置 `16*q` 的 66 組；以及 first small pool 配置 `16*n`（n=1..3）、second request=0 的 198 組。兩者各取 q=1..66，第三池 request=`12*q`、tag=`0x4c06`。實際 fresh free header、size、next、arena head 與前置 allocated headers 必須符合 ledger。

| 承接路徑／q | 第三池使用的 free block | 跳過 allocated headers |
|---|---|---|
| Second 成功，q=1..3 | Second small pool 後的 remainder | 2 |
| Second 成功，q=4 | 尚未使用的 small S=`A+24`，size480 | 1 |
| Second 成功，q=5..66 | Second large pool 後的 remainder | 3 |
| First small 成功、second zero，q=1..4 | First small pool 後的 remainder | 2 |
| First small 成功、second zero，q=5..66 | Resource large pool 後的 remainder | 2 |

q=4 是額外界線：second request64 使用 large list，third request48 改用 small list。因此該列另需 fresh small head A 已配置16、tag=`0xff03`、next=S，以及 S free480／tag0／next=B；不能從 second large 成功推得 small header 狀態。

每列以不可變公式驗證 payload P=H+8、新 free header N=P+12*q、新 free size=`old_size-12*q-8`，所有列均有正 remainder，split 精確接回 arena 終點。Account 減少 `12*q+8`，按原指令截成16 bits。所有 header、payload／fill 區間都排除先前 resource／first 或 second pool owners、完整第一張 table payload，以及沿用的 fallback、F96、role object、task metadata、callback table、timer、ID6 與 count 來源。

另保留四組 q=0 路徑：first count 為0、1、2、3，第三池仍呼叫 request-zero 核心並保存回覆0，跳過第二次 getter 與 fill。此路徑沒有 header 配置或 fallback callback；first small 已配置的三列也不會因此被釋放。正長度配置失敗、其他 first-count／tag／heap 組合不在已證明域內。

## Parent 尾跳與下一次 task 登記

Parent 還原 S0、RA 與其他 saved registers，釋放48-byte frame，把 callback pointer `0x4d916／0x4d9ae` 送入完整42-byte／17-instruction leaf，使用不更新 RA 的尾跳。Leaf 普通 RET 因此返回 outer entry+24。所選配置階段的 parent48＋core16 最高為64 bytes；尾跳時 parent frame 已釋放，outer16-byte frame 仍存活。有效的 frame 所有權與實體不別名仍是前提。

Leaf 最多逐次讀12個 callback slots，找到第一個觀察到的零值便寫入 pointer、回覆 `(A0,A1,A2)=(0,0,12)`；若12次皆非零，沒有 store，回覆 `(19,最後讀到的非零word,12)`。它不檢查 null／重複 pointer，也不呼叫所登記的 callback。

- q>0：先前 resource 路徑清零的48-byte callback table，在所有選定的 parent／pool 寫入後仍被排除覆蓋；清零結果保留至 fresh read 時，leaf 選 slot0。
- q=0：resource 路徑沒有清零此 table，所以保留 slot0..11 插入或全滿的13種 fresh-read CFG 結果，沒有假定 table 為空或一致快照。

Outer 不測試 leaf 的回覆0／19，而是重新載入 task handler `0x465b4／0x4664c` 並呼叫既有 registrar。在 fresh count7、capacity至少14、table pointer仍為 T=`0x200047f4`、metadata／frame 保留等條件下，entry7=`0x20004810` 發布 handler，count 更新8，回覆 A0=7、A2=8。Registrar 保留 A1，故插入路徑的 A1=0；q=0 table 全滿路徑則沿用最後觀察到的非零 word。

終點為 V1.31 `0x6dd3a → 0x46570`／V1.40 `0x6df2a → 0x46608`，fallback0、gate5、saved ID6、task count8。第二個 initializer 尚未納入本輪串接。

## 驗證與未完成項目

檢查器重核先前條件性證據、兩個候選的9個 strict sparse HEX 範圍／profile、完整 getter／leaf／outer-return window、264組幾何、26條 callback CFG 路徑，以及548組原指令／core 變異拒絕。`check` 是明確例外檢查，正常與 `-O` 模式都必須重算並逐 byte 比對 ledger：

```powershell
python analysis/check_v4160_b1_fallback_third_static.py
python -O analysis/check_v4160_b1_fallback_third_static.py
```

實際 installed provider、fresh header／count 寫入者、非所選配置與失敗路徑、IRQ／DMA／重入等順序與物理副作用、callback 消費端及完整跨事件保存／釋放合約仍未完成驗證。上述結果是條件性靜態串接，不表示啟動時必然可達、輪詢必然進展或 pointer 生命週期已閉合。
