# v4.1.60：最後初始化、pool reserve 與 outer 的所選返回

接續 [ID66 setter 至 ID11](v4160-b1-fallback-writer-static.zh-TW.md)，本輪把第六個 initializer 的 factory／defaults、pool 保留區、第四次 callback 登記、outer frame 釋放與 final gate 接起來。兩條 early-return 回覆24；admitted 分支在額外登記與所選 NV 快速錯誤路徑後回覆0。這是所選條件下的 outer 初始化返回證明，不是整份韌體或所有 APP 路徑完成。

檢查器：[check_v4160_b1_fallback_id11_static.py](check_v4160_b1_fallback_id11_static.py)；證據：[JSON ledger](v4160-b1-fallback-id11-static.json)。只使用原始 bytes、不可變 CFG、閉合索引／區間／frame 關係；沒有執行或模擬 target、NV、provider、MMIO 或硬體，也沒有建立可變 RAM／heap 模型。新增 C 重建 bytes 為0，原始 bin 不變。

## 原函式與預期更新

| 項目 | V1.31 候選 | V1.40 候選 |
|---|---|---|
| 最後 initializer | `0x4d172` | `0x4d20a` |
| Factory | `0x493f2` | `0x4948a` |
| Defaults | `0x4b35e` | `0x4b3f6` |
| Pool leaf | `0x4b33c` | `0x4b3d4` |
| Outer epilogue | `0x6dd7e` | `0x6df6e` |
| Final gate | `0x6d572` | `0x6d75e` |

令 G=`0x20003000`。大部分 scalar fields 的 profile 位移是80，但三個 RAM objects 的位移是76，所發布的 ROM pointers 位移則是496，不能全部套同一個 relocation。

Factory 刻意把前輪 ID66 byte `0x20002edc／0x20002f2c` 從10改成2。Defaults 先把 `G−289+δ`、`G−274+δ` 設 `ff`，initializer 再用保存於 S0 的入口 ID11，分別覆寫為11。Matching fill 必須保留 factory 的 S0=2、caller 的 ID11 及 frame／RA；defaults／pool 沒有局部 S0 定義。

另一筆重要更新是 factory `+228` 的 pointer store：

| 項目 | V1.31 | V1.40 |
|---|---|---|
| 寫入位置 | `0x20002e70` | `0x20002ebc` |
| 寫入 bytes | 4 | 4 |
| Pointer 值 | `0x49156` | `0x491ee` |

這恰好覆蓋 first-copy 目標範圍末四 bytes，故本輪**不宣稱整段 copied region 保持不變**。檢查器另行排除本階段實際使用的 fill、copy 等 helper code 範圍；不能由此推論其他複製區內容或之後 callback 的綁定。

Defaults 也會把 ID8 的 end pointer 發布到其物件 `+60` 欄位，並寫入五個超出已提供候選 bytes 的 ROM 位址。它們在這條路徑只被存為 pointer，沒有解參考；缺失 ROM 的消費合約仍未完成。

## Pool 的 `4*r` 保留區

Pool leaf fresh 讀取先前的 `r=b&3`。它的 pointer 來自 ID8 end-pointer word，而該值在所選非零配置下是 `P+190*r+6`。同一筆 ID8 原請求結束於 `P+194*r+6`，因此剩下 `4*r` bytes。

每筆 stride4 record 只寫 `SH ffff` 於 +0、`SB 0` 於 +2；byte+3 本次不寫。檢查器逐列核對 r=0..3 的有限 CFG 與範圍，最後正好接到原請求終點。r=0 時不解參考入口 pointer，因此該 pointer 為0仍可普通 RET。

Pool stores 是 ID8 payload 內的預期更新，不能把整個 payload 當作不變。其他 allocated owners、headers、新 NV pool、完整第一張 task table 與 protected metadata 都分別排除覆蓋。Pool 的 r、gate fresh 讀取 F+21 的低兩位及原始 b，只有在來源與欄位保留條件下才能接成相同值。

## 第四次 callback 登記與 outer frame

Initializer 以16-byte frame 保存 caller RA／S0，factory 另用16 bytes；連同仍存活的 outer16，本階段最高48 bytes。完成兩個 ID11 stores 與 pool 後，initializer 還原並釋放 frame，尾跳 callback-register leaf，輸入 `0x4cff6／0x4d08e`，沒有呼叫 callback 本體。

- q>0：前三個非零 pointer 與其餘清零值保留時，第四次插入 slot3。
- q=0：在前次非零觀察／成功寫入與無介入 writer 的額外保存條件下，四次掃描有794組索引序列，依四、三、二、一、零次插入分成495／220／66／12／1；index12代表全滿。單次 leaf 的13條原始 CFG 路徑仍分開保留，沒有原子快照宣告。

Leaf RET 到 outer epilogue。Outer 不測試插入回覆0／19，而是還原其 caller RA、釋放16-byte frame，再尾跳 final gate。Gate 的16-byte frame 若有建立，使用的是已釋放的 outer 範圍；其 caller RA 仍必須正確保存與還原。

## Final gate 的三種所選結果

| 條件 | Task count | 最終 A0 | 額外動作 |
|---|---:|---:|---|
| Fresh low2=0 | 12 | 24 | 不建立 gate frame |
| Low2 非零、fresh cached ID 非 `ff` | 12 | 24 | 還原 gate16 後返回 |
| Low2 非零、cached ID=`ff`，且 fresh count12／capacity>=14／table=T | 13 | 0 | 發布 ID12，並走下述服務路徑 |

前兩條 early-return 的 A2 都保留 leaf 的12；A1 在 low2=0／q=0 table 全滿時可能是最後觀察到的非零 slot11 word，其他所選插入情形為0。Cached ID 位於 `G+1525+δ`，其 fresh 值並非由 pool count 推導。

Admitted 分支把 handler `0x6d26c／0x6d458` 發布到 entry12=`0x20004824`，count 更新13；將 cached ID byte 設12，並以 special-ID leaf 把 `G+942+δ` 從先前的 `ff` 改為12。Fresh count／capacity／table 與 matching registrar 正常返回仍是前提。

## Admitted 分支的 NV 快速錯誤與零值傳遞

Admitted 分支額外選定同一組被保留的 read-wrapper 條件：configured missing callback（F+8 非零、F+56 為零），或 RAM null（F+8 為零、C+32 為零）。三次原始 read wrapper 都回覆10，沒有子呼叫或輸出寫入，gate 不檢查這些回覆。

兩段 fill16 先清零 `G+1492+δ`、`G+1508+δ`。Read `(2,16,第一段)`、`(3,16,第二段)` 不寫輸出；matching copy 再把兩段各複製16 bytes 到 `G+1528+δ`、`G+1464+δ`。最後 read 是 `(4,4,G−12+δ)`，該輸出 word 已先清零，因此所選錯誤路徑下仍為零。

Copy 是完整58-byte／18指令 leaf，只有 A3–A6 局部定義，沒有 frame 或子呼叫。16-byte 零值傳遞依賴來源保存、有效不別名存取，以及 control clear／`FENCE.I`／captured-value restore 沒有不利副作用；這些指令沒有被執行。

Gate 最後強制 A0=0，再還原 RA／S0–S2、釋放 frame 並 RET 回原 caller。此0不是 NV 成功狀態。兩條 read-wrapper 路徑還能分別核對最終 registers：

| 所選 read-wrapper 分支 | 最終 A1 | 最終 A2 |
|---|---:|---|
| Configured missing callback | 4 | `G−12+δ` |
| RAM null | 0 | `G−12+δ` |

Gate16＋read-wrapper32 的峰值也是48 bytes；所有本階段 frames 都在最後 RET 前釋放。實際 caller、source／frame 所有權與 normal-return ABI 仍是明列條件，不是完整 APP 可達性或輪詢進展保證。

## 保存檢查、驗證與未完成範圍

固定 factory／defaults／gate envelopes、兩個 bulk fills、兩個 copy outputs、callback store、control word 與 pool margin，逐一對1024組舊來源及4096組 NV count 家族檢查。ID66 byte、first-copy tail、pool reserve、special-ID byte、`G−12+δ` 等預期更新明列，沒有宣稱所有舊 RAM 都保持原值。Callback 與 task entry12 發布分開檢查。

每個候選有12個 strict sparse HEX 範圍核對。原函式合計1764 bytes／528個本輪操作數護欄，另核對18指令 copy，累計3497組指令／typed-load 變異拒絕。正常與 `-O` 模式均須重算並逐 byte 比對 ledger：

```powershell
python analysis/check_v4160_b1_fallback_id11_static.py
python -O analysis/check_v4160_b1_fallback_id11_static.py
```

已閉合的是上述所選 outer 初始化返回鏈。實際 installed 綁定、其他 allocation／NV／flag／cache 分支、特殊 handler 與 callbacks／ROM objects 的消費、APP 上層返回與可達性、硬體副作用及完整跨事件保存／釋放期仍未完成驗證；沒有宣稱整份可用韌體已重建。
