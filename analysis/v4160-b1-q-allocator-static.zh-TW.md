# v4.1.60：RF config 的直接 allocator 與 Q 保存分支

接續 [RF 返回與 caller 邊界](v4160-b1-q-return-static.zh-TW.md)。本輪接通 RF config 的 **直接 core 呼叫**，並將 APP `flag1` 的配置發布路徑分成可驗證的 fit／失敗條件。這不是 fresh heap、實機配置成功或完整指標保存期的證明。

在 fresh F+29=251 的條件下，config 傳入 `request=253, tag=73`，core 對齊得 R=256 並選 large list。這個呼叫入口是 `0x20000040`，不是 message marker wrapper；不能在 tag 上自行加上 `0x8000`。

配置回覆原樣存入 C+4，之後 config 將自己的 A0 設為零。**Core 回覆零也會被發布，config 的零回覆不能證明配置成功。**

## 原指令與實參

| 接點 | V1.31 | V1.40 |
|---|---|---|
| 完整 RF config | `0x64bae`，318 bytes | `0x64c98`，318 bytes |
| Core 原始來源 | `0x402b0`，208 bytes | `0x402f0`，208 bytes |
| Core 名義 runtime 入口 | `0x20000040` | `0x20000040` |
| Large-head pointer 槽 | `0x20003190` | `0x200031e0` |
| Fallback pointer 槽 | `0x20003220` | `0x20003270` |
| Accounting 半字 | `0x200031a2` | `0x200031f2` |

檢查器核對兩版完整 core 的 72 條原指令／CFG、strict HEX 與 first-copy 來源對應，以及 config 的 +0xba fresh U8 read、+0xbc tag73、+0xc0 加2、+0xc6 direct call、+0xca C+4 store、+0xce forced-zero reply。這仍是候選 code／mapping 身分的條件式連接。

全部 256 種 fresh F+29 值 b 都有 `request=b+2`，範圍 2..257，對齊 R=4..260，沒有這個實參域內的 U16 回繞：

- b=0..50：R≤52，選 small list。
- b=51..255：R>52，選 large list。
- 本輪 APP 特化採 **fresh b=251**，因此 request253、R256。

較早 default store 提供 251 的來源，不能代替呼叫當下的 fresh sample；若有其他 writer／重入或別名干擾，必須重新證明該值保存。

## Fit 的寫入與回覆

令 H 為實際選中的 current header，B 為本次讀得的 `U16[H+4]`。接受 fit 還要求 fresh `U16[H+6]==0`。R 與 tag 在通往 tag store 的有限 fit prefix 中保持；search SCC 沒有編碼 store 或 nested call，但串列／有效存取與遍歷終止仍未證明。

| B 的範圍 | 分支 | Heap header 寫入 | Accounting 效果 | 回覆 |
|---|---|---|---|---|
| 0..255 | 太小，繼續搜尋 | 無此 fit 寫入 | 無此 fit 扣帳 | 不在此返回 |
| 256..264 | 不分割 | `U16[H+6]=73` | 扣256，mod 2^16 | `(H+8) mod 2^32` |
| 265..65535 | 分割 | 新 N 的八 bytes；H 的八 bytes | 扣8再扣256，mod 2^16 | `(H+8) mod 2^32` |

其中 N=`(H+264) mod 2^32`。新 header 的 stores 是 N+4 半字、N+0 word、N+6 半字，合計恰好八 bytes；舊 header 的 stores 是 H+0 word、H+4 半字、H+6 半字，也恰好八 bytes。未分割時不改 H 的原 size，扣帳仍用 R=256，不能換成原 B。

Core 沒有 payload fill／copy 呼叫。對有效、不回繞且與固定 globals／frame／control 無不良別名的配置區塊，這些 header stores 位於所交出 R-byte payload 之外；這不是一般任意 H 的所有存取別名排除，也沒有證明 payload 的內容、所有權或可讀容量。

## 未分割時的有限值保存引理

前輪 selected RF 路徑提供的是有前提的 Q=`0x40025000`。若這個值保持至 core，並與 fresh tag-zero read 使用同一個一致的普通 little-endian byte 映像，Q 的四個 bytes 為：

```text
Q+0  Q+1  Q+2  Q+3
 00   50   02   40
```

未分割分支唯一的 heap store 是在 A=H+6 寫入 `0x0049`。一個兩 byte store 若碰到 Q，A 只可能位於 Q−1..Q+3：

| A | 與 fresh tag=0 是否相容 | 對 Q 的結論 |
|---|---|---|
| Q−1 | 可能；相交的 Q+0 原本是零 | 相交的 store 高 byte 也是零，Q 值不變 |
| Q..Q+3 | 不相容；tag read 會包含至少一個 Q 的非零 byte | 不能同時滿足這個一致影像與 tag-zero 前提 |

因此，**這個特定未分割／tag73 情形可在正常存取完成後保存 Q 值，即使不先假設 tag store 的數值區間與 Q 完全分離。** 這是 byte-lane 等式與讀值一致性的結論，不是未對齊存取必定成功的證明；其他 accounting／control／frame 寫入仍需分別排除 Q 別名與副作用。

引理不適用於任意 tag 或任意 Q。例如 tag=`0x8049` 的高 byte 不為零，便沒有上述同值寫回性質；這只是封閉 scalar 反例，不表示本呼叫使用該 tag。

## 分割與 sentinel 的額外條件

分割會寫兩個八 byte header，不能套用未分割引理。可使用以下任一有前提的區間證書：H／N 的八 byte 寫入範圍各自有效、不回繞且與 Q 分離；或由有效 owned block `[H,H+B+8)` 包含兩個 header，且整塊不回繞、與 Q 無別名。

後者的包含關係來自 B≥265 與 N=H+264，故 N+8≤H+B+8。既有名義 heap `[0x200043ac,0x2000b184)` 位於兩版 Q 之後，可在真正維持該 ownership／區間條件時支持排除；**名義圖本身不證明 fresh head、所選 H 或目前 heap 仍符合它。**

若遍歷抵達 sentinel：

- Fresh fallback 槽為零：core 返回零；本地路徑沒有 header／accounting store。仍有 frame 與 control 寫入，需其正常存取與別名排除前提。
- Fresh fallback 槽非零：以 `A0=1, A1=0x01000049` 呼叫該 target，A2 仍是 core 入口的未限定值。正常返回後，core 丟棄 callback 的 A0，不重試串列，最後返回零。

**丟棄 callback 回覆不代表 callback 沒有副作用。** 非零 fallback 的 Q 保存仍未封閉，不能從最後的零回覆推定它安全、成功或完全沒做事。

## 接回 config 的範圍

在 matching code／helpers、普通有效來源、必要 context／frame／S／SP／RA 保存、正常有限遍歷與存取、無不良物理別名／IRQ／DMA／重入／其他 writer 等條件下，若：

1. Fresh 舊 C+4 為零，因而跳過較早 private release；
2. APP 特化所需 fresh F+29=251 與入口 Q 值成立；
3. Core 落在已證的未分割、具 header 排除條件的分割，或 fresh fallback 為零的 sentinel 情形；

則可將 Q 保存接過 **包含 allocator 的 config 發布路徑**。C+4 收到 P 或零，後續沒有以回傳指標作為 base 的本地解參考或 null／status 分支，config 自己均返回零。

若舊 C+4 非零，較早 release 的保存仍需單獨處理。本輪也未封閉 role 到較晚 config 的所有中間呼叫，不能把這個局部條件式證書當成完整 APP boot 或跨事件時序的證明。

## 驗證

[檢查器](check_v4160_b1_q_allocator_static.py)與[固定 ledger](v4160-b1-q-allocator-static.json)重新驗證完整來源、原指令與 strict HEX，核對全部 256 個 fresh-byte request、65,536 個 U16 block size、131,072 個 accounting 等式、Q／tag 的五個相交 byte-lane 情形，以及 48 個 rounding／list／fallback／header／account／return 原指令位置突變。

```powershell
python analysis/check_v4160_b1_q_allocator_static.py
python -O analysis/check_v4160_b1_q_allocator_static.py
```

新增原始 byte 覆蓋為 **0**，APP C 重建覆蓋率不變。仍需確認實際 provider／fresh heap／fallback、private release 與其他中間 callees、有效 traversal 與 IRQ／poll 進展，以及完整指標保留／消費／釋放／通知保存期。

全程離線，只有原 bytes／CFG 與封閉數值關係；沒有執行或模擬目標、建立 mutable target model、硬體存取、封包重放或 target network。
