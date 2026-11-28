# v4.1.60：Parent pool／record 前段至首次 getter 的保存驗證

接續 [outer 資源前段](v4160-b1-fallback-outer-static.zh-TW.md)，本輪接過 parent 的第一個 fill48，核對所選 `0x4c04／0x4c05` 配置與 16-byte records，止於首次 getter 呼叫前。

檢查器：[check_v4160_b1_fallback_parent_static.py](check_v4160_b1_fallback_parent_static.py)；證據：[JSON ledger](v4160-b1-fallback-parent-static.json)。本輪使用原始 bytes／CFG、封閉配置幾何與 record 區間證書，沒有執行韌體、建立可變 target heap／RAM 模型、操作硬體、重播或連線 target。沒有增加 C 重建 bytes 或提高覆蓋百分比。

## Fill48 不會設定後面的 count

前階段截止於 parent `+0x7e`，請求清除 `[G+800+δ,G+848+δ)` 的 48 bytes。匹配 fill 正常完成後，parent 於 `+0x86` 另讀 fresh `U8[G+848+δ]`；這個 byte 不在剛清除的範圍內。其後的 tag byte `G+849+δ` 也是獨立 fresh 來源。

| 項目 | V1.31 | V1.40 |
|---|---|---|
| Parent 入口 | `0x4da70` | `0x4db08` |
| Fresh first count | `0x20003350` | `0x200033a0` |
| Fresh tag byte | `0x20003351` | `0x200033a1` |
| First pool pointer | `0x20003310` | `0x20003360` |
| Combined-count byte | `0x20002fa0` | `0x20002ff0` |
| Second pool pointer | `0x20002f98` | `0x20002fe8` |

First count 為零只略過第一筆 `0x4c04` 配置，不略過第二筆。第二筆會計算 `m=(fresh resource_q + fresh local_byte) & 255`，再呼叫 core `(16*m,0x4c05)`。

本證書只關閉以下明列條件的路徑，不宣稱已證明各種 fresh 值在真實 boot 中可達。

## 路徑 A：First count 為零

要求 first count=`0`、所需 local byte=`0`。第一筆配置與其 pointer store 都跳過，因此不宣稱舊 first pool pointer 已清零。

- 若 resource q=`0`，第二筆仍呼叫 core，但 request=`0`。Core 走 request-zero 早退並返回 `0`；這不是 sentinel／fallback 失敗路徑，也不是有效配置。Parent 發布零回覆並清兩個本機 bytes，不寫 records。
- 若 resource q=1..66，第二筆 request=`16*q`、tag=`0x4c05`。此情況要求前階段有效 resource pool 幾何、實際成功回覆與必要 header／count／pointer 保存。

對 q=1..3，request 為 16／32／48，選 small list。本證書另要求 fresh timer header A=`0x200043ac` 仍已配置 16 bytes、tag=`0xff03`、next=S=`A+24`；S 為 size480、tag0、next=B 的有效 free block。Core 略過 A，再分割 S。

對 q=4..66，request 為 64..1056，選 large list。Core 必須先略過已配置的 table block B 及前階段 resource header，再命中 resource 配置之後保存完好的 free remainder。不能沿用「large head 就是 free remainder」的假設。

全部 66 組幾何都檢查舊／新 headers、payload 與 accounting 的更新，並確認不改先前 resource owner 或完整 first-table payload。Small case 的 fresh A／S 條件沒有套用到前階段 small-head-sentinel 的替代情況。

成功後，parent 再次載入長度做 fill，之後又重讀 pool pointer／count 寫 records。因此仍要求這些 fresh count 與實際配置長度相容，且 pointer 仍是原本有效 P。在本輪選定的相等條件下，fill 長度為 `16*q`，每筆 stride=`16`，只寫 `P+16*j+9` 的 byte 為 `0xff`。全部寫入均在 owned payload 中。

## 路徑 B：First small 配置成功，second request 為零

另選 first count n=1..3，core 請求 `(16*n,0x4c04)`。使用上述獨立 fresh A／free S small 幾何，配置成功後 fill `16*n` bytes；後續重讀的 count 仍須與 n／有效 payload 相符。

此路另外要求 resource q=0..66，fresh tag byte 為 `(-q)&255`。Parent 把該值保存至 local byte，使第二筆 `m=(q+local_byte)&255=0`。第二筆 core 因 request zero 早退返回 `0`，不配置、不寫 records，parent 清本機 bytes。**第一筆 small pool 仍已配置**，沒有因第二筆零回覆被釋放。

三個 first-small 幾何與 66 個 second-pool 幾何是不同的分支證書，沒有把它們當成共用同一個已分割後 header 的連續配置。

## 截止點與 record CFG

| 項目 | V1.31 | V1.40 |
|---|---|---|
| 本輪截止 call，parent `+0x114` | `0x4db84` | `0x4dc1c` |
| 尚未執行的 getter | `0x4efd8` | `0x4f070` |

成功 record 路徑以固定的 `+1` byte-counter／AND255／stride16 原指令與全部 q=1..66 的有限 CFG 重複路徑核對。這是圖與整數 ranking 證書，不是 target 指令執行。此範圍不會把 66 次內的 counter 增量回繞成零。

第二筆零回覆路徑走兩個 byte-clear 後接到同一個 getter call。截止時 fallback=`0`、gate=`5`、task count=`7`、保存的 ID byte=`6`；parent 的 48-byte frame 仍活躍。Getter 尚未執行，後面的 `0x4c06` 配置、第二次 getter／fill 與尾跳也未納入。

## 保存範圍與限制

每版的八個固定範圍包絡涵蓋 parent fill48、控制 word、accounting、兩個 pool pointers、first count／local tag／combined count。另逐組核對所選配置 header／payload／record 區間。

它們在數值上避開 fallback、F96、role object、task count／capacity／gate／table pointer、既有 entry0..6、timer head／node／header、已配置的 large table header、兩個 APP task bytes、保存的 ID6、resource counts／pool pointer／callback table。Dynamic second-pool 寫入另排除先前 resource header／payload 與完整 first-table payload。

正 request 的 null 回覆、任意第一 count／tag 組合及其他 fresh heap headers 不在已關閉範圍。零請求早退與 null 配置失敗並不相同；先前 header snapshot、nonnull owned payload、重讀長度／pointer、SGPR／SP／RA 保存都仍是明列條件。

所選 parent48＋core16 的 frame 深度為 64 bytes。三個 resident strict sparse HEX 來源（完整 parent／core／fill）、500 筆原指令變異、69 組配置幾何、zero-request CFG 與 exact-byte ledger 均須通過：

```powershell
python analysis/check_v4160_b1_fallback_parent_static.py
python -O analysis/check_v4160_b1_fallback_parent_static.py
```

所有前階段 source／retry／resource／metadata 條件仍保留，並要求匹配 core／fill／ISA／first-copy、正常返回／存取、有效且不回繞／不別名的 owned frames／heap／globals／table、保存字，以及無不利 MMIO／FENCE／IRQ／DMA／reentry／外部 writer。數值分離不證明物理副作用分離。實際 fresh 設定／headers、其他配置路徑、第三 pool 與完整消費保留釋放期仍待分析。
