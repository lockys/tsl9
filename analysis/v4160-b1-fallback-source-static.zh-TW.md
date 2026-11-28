# v4.1.60：Fallback 零來源、局部保存與 fresh load

接續 [private release](v4160-b1-q-release-static.zh-TW.md) 與 [Q 初始化來源](v4160-b1-q-source-static.zh-TW.md)。本輪將 fallback 的 APP 設定來源接到 initializer 的 getter 返回，並建立選定 RF 路徑與 allocator fresh load 的局部保存證書。

結論分成兩個尚未完全接合的區段：

1. 匹配 APP 清零、validation、64-byte copy 與 getter closure 等前提下，fallback 的零值可保存到 **initializer +0xce 的 post-config 呼叫前**。
2. 若零值已存在於選定 RF 路徑／allocator 的相應入口，並滿足 frame、動態寫入與物理副作用的排除條件，該次 core 的 fresh fallback load 會讀零並略過失敗 callback。

**兩者之間的 post-config／wrapper／param774 等中間呼叫仍有缺口。** 本輪未證明實際 boot 順序、整段槽位不變值、配置成功或完整保存期。

## 槽位與 APP 來源

| 項目 | V1.31 | V1.40 |
|---|---|---|
| Copied config D | `0x200031ec` | `0x2000323c` |
| Fallback 槽 D+52 | `0x20003220` | `0x20003270` |
| Initializer | `0x43c7e` | `0x43d0a` |
| 本輪零值來源證書終點 | `0x43d4c` 呼叫前 | `0x43dd8` 呼叫前 |

APP `0x199e2` 的完整 308-byte builder 在 `0x19a38` 要求清零 `[SP+16,SP+80)`，並在 `0x19aec` 將 SP+16 交給 initializer。設定資料 +52..55 對應 **SP+68..71**，與相鄰 +48 hook 的 SP+64..67 不同；也不能與 SP+52 混同。

清零後的直接 stack stores 不碰 SP+68..71。直到 initializer 呼叫前，唯一中間 call 是 `0x19ab4` 的六 byte UID leaf，其輸出 SP+8..13 與隨後六 byte loop 的目的 SP+40..45 都分離於該 word。這仍要求普通有效 frame、匹配的 clear helper、必要 context 保存與無外部干擾。

既有 startup zero helper 也有條件地包含這個槽；但後續 64-byte config copy 會重寫它，不能只用較早 zero range 代替較晚的來源／保存證據。

## Validation、copy 與初始 getter

Initializer 的 validation call 匹配 `0x200004bc`：完整 62-byte／19 指令 helper 只有三個控制字 store，沒有 nested call。控制字的名義地址均為 `0x4002420c`。在實體副作用不破壞來源／frame 的前提下，它不另寫設定來源 word。

Fill 與 copy 的名義 runtime 入口為 `0x2000039c`／`0x20000332`，重用完整 46／58-byte 原指令證書及 strict HEX／first-copy 來源對應。正常完成有效、穩定且無不利重疊的 64-byte copy 後，來源 +52 的四個零 bytes 被帶到 D+52。這是完成後的值證書，不是四 byte 原子發布或並行消費順序的證明。

Initializer 的八筆 defaults、getter 回覆的固定半字 store 與稍後固定 byte store 都不碰 D+52。它在 +0xba 呼叫的是 **D+44**，不是 fallback 的 +52。Matching APP 來源提供 getter `0x197f0`；getter 會在進入自己的軟體 closure 時把 inherited A0 換成私有 scratch pointer。

本輪重用並重新核對 getter 的完整 **14 個軟體本體、1072 bytes、390 指令、79 個 store sites**。其 RAM 寫入投影為 callback 的 128-byte frame、frame 內 32-byte scratch，以及 reset wrapper 的額外 spill；最大 144-byte 深度以 **getter 入口 SP** 為基準，不是整條 APP call chain 的總深度。

若這些 frames／scratch 不別名到 D+52，且匹配的 nominal MMIO／FENCE 效應、IRQ／DMA／重入與其他 writer 不破壞受保護 RAM，getter 可保存該零 word。必要存取與 poll 仍須正常完成。接上其後兩筆固定 stores 後，證書停在 initializer +0xce 的 post-config 呼叫前；該呼叫與後續 wrapper／事件順序不能直接當作已保存。

## 選定 RF 路徑的保存區間

在先前四槽來源／Q 返回證書的相同選定分支、memory-base 投影、有效 code／context／frames、正常 calls／polls 與無不利物理別名等前提下，本輪另核對 fallback 槽：

- 前輪取樣前 96 筆分類區間；
- RF 返回段 131 筆分類區間；
- Parent 在四槽建立前的六筆固定 writes。

每版合計 **233 筆路徑分類的寫入區間**均與 fallback 四 bytes 數值分離。這包含不同分支及重複位置，並非一次執行的 store 次數。Frame writes 仍需另外排除該槽別名；數值分離不自行證明實體映射分離。

Role／config 的 12 筆固定 stores 及三個 bulk 目的範圍也不碰 fallback。可是保護 Q 的條件不能自動用來保護這個不同地址：

| 邊界 | 仍需的條件 |
|---|---|
| Role registration | 固定 count byte 分離；接受時的動態 `T+4*n` word 必須另排除 fallback／frame／code 別名 |
| Private release | 固定 stores 分離；實際 written H／J headers 也需排除 fallback，owned arena 可作有條件的充分前提 |
| Allocator fit | 若要在 fit 返回後仍保存槽位，需實際 H／N header 的寫入排除條件 |

若另有 fresh `T=0x200047f4` 的名義 table 前提，全部可接受 U8 索引的 word envelope `[0x200047f4,0x20004bf0)` 與 fallback 分離。但實際 T／table extent 仍未證明。未限定對齊時，對至少一個 n=0..254 而言可能碰到 fallback 的 T 值聯集是 `[slot−1019,slot+3]`；這只是地址等式，不是實際 table 值或可達性證據。

前輪對 Q=`0x40025000` 的特殊 tag73 值保存引理也不能照搬到原本為零的 fallback：零 word 與 fresh zero-tag read 可以相容，但 tag73 的低 byte 不為零，重疊寫入仍可能改值。本輪採用額外的區間／ordinary-memory 保存條件。

## Allocator 的 fresh load 證書

Core 入口 `0x20000040` 的 +0x54 對上述 fallback 槽重新讀取完整 word。沿入口至該 load 的 CFG ancestor set，編碼 store **只有**：

| Core offset | 寫入 |
|---|---|
| +0x02 | SP+8 saved word |
| +0x08 | SP+12 saved RA |
| +0x0e | 名義控制字 `0x4002420c` |

在這個 ancestor set 沒有 header／accounting store 或 indirect call。Fit 的 metadata writes 不會在同一次呼叫中回頭走到此 load。

因此，若 **core 入口 fallback=0**，且這兩筆 frame store、控制字與外部／物理副作用不改槽，抵達 +0x54 時便讀零。+0x58 的零分支跳至 +0x1a，略過 +0x60 的失敗 callback，恢復控制與 frame 並返回零。

這項「該次 core 不呼叫失敗 callback」的局部結論，**不需要猜測遍歷過的 header 地址**，但仍不證明遍歷終止或存取有效。Fit 路徑仍可能返回 pointer；若其 header writes 未另排除槽位，不能從入口為零推定 fit 返回後也保持零。其他 getter／hook／事件 callback 不在這個失敗 callback 排除結論內。

## 有界 writer 普查與驗證

另外重用逐半字標準 LUI 起點、最多 32 解碼指令的局部定義搜尋，分別檢查 APP、兩版 BIN 與完整 strict sparse HEX 對 fallback 四 bytes 的寫入。此次沒有命中 literal-base store 或目標地址建構。

這不是 all-writers 證明。搜尋不跨 calls／branches／unknown／缺口／上限，也不封閉 load-derived pointers、動態 headers、copy／fill 的跨函式效果、實體別名或外部 writer。已知的 64-byte config copy 本身就是一個不能用這種零命中結果排除的 writer。

[檢查器](check_v4160_b1_fallback_source_static.py)與[固定 ledger](v4160-b1-fallback-source-static.json)保留 APP word 來源、initializer／helper／getter closure 接點、233 筆區間的固定摘要、caller 足跡、writer 搜尋界線與 fresh-load CFG 證書。37 個 APP 來源／initializer 發布／getter／load／branch／call 原指令位置突變必須被拒絕。

```powershell
python analysis/check_v4160_b1_fallback_source_static.py
python -O analysis/check_v4160_b1_fallback_source_static.py
```

新增原始 byte 覆蓋為 **0**，APP C 重建覆蓋率不變。仍需串接 post-config／wrapper／param774 等發布到 RF 的中間邊界，確認 actual provider／mapping／fresh snapshots 與 headers 所有權，並完成跨事件與保留／消費／釋放／通知保存期。

全程離線，僅核對原 bytes／CFG／定義與封閉數值區間；沒有目標執行、模擬、mutable target model、硬體存取、封包重放或 target network。
