# v4.1.60：完整 local selector 與純暫存器 shift leaf

接續 [完整 callback 原指令閉合](v4160-ram-callback-closure-static.zh-TW.md)，本輪展開其中 mapped target `0x200014c6`，並把它的兩個靜態 probe call sites 接到完整 leaf。兩份 resident 仍為**候選**，未認定實際 installed provider。

在明列的指令／存取／保存前提下，selector 的 fallback 掃描最多 37 輪，加上初次 probe 最多 38 次。這個有限步數結論來自已核對的 leaf clobbers 與 counter ranking，不涵蓋上層 callback 的更新／等待循環。

只讀原 bytes、核對 operands／hash／CFG，另做主機端整數與 shift 代數；未執行或模擬目標 ISA、callback、RAM／frame、resident、MMIO 或裝置。既有 C 重建 bytes 未增加。

## 四個完整本體

| 候選／本體 | FLASH，end-exclusive | bytes／指令 | SHA-256 |
|---|---|---:|---|
| V1.31 selector | `0x41736..0x417dc` | 166／61 | `e20608a420fad0d2bcadc9188c56c5f655764288c31e5322ba361faa14c885ed` |
| V1.40 selector | `0x41776..0x4181c` | 166／61 | `4f6f58637e6f16ca3efa2844d7e3840b7eac68ccc04c58352bf6beca5ee1978e` |
| V1.31 leaf | `0x6dec2..0x6deee` | 44／15 | `1eb4d7b36ea3c0fd97d6c5e13c51cd41901375aea68054d52fa1f0572a047a92` |
| V1.40 leaf | `0x6e0b2..0x6e0de` | 44／15 | 同上 |

合計 420 bytes／152 指令；兩份 leaf bytes 相同。selector 經 first-copy 都映射至 `0x200014c6..0x2000156c`，leaf 保留其 FLASH 呼叫座標。

先前 callback 的兩個 direct call sites 均精確指向此 selector，且 call 前明確以 MV 設 A0=then-live S0。兩份 selector 的兩處 AUIPC／JALR 又分別指向表中的 leaf。所有原 operands、邊界、無 unresolved local cuts、entry 圖走訪與 hash 均核對。

APP 仍為 76,800 bytes、base `0x8000`、SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。既有 APP／候選／SDK／sparse／指令格式來源合約也遞迴重驗。

## byte 相加後只條件減一次 37

selector 配置 48-byte frame，保存 RA／S0..S7 九個 fields，然後：

```text
c = (fresh U8[object+311] + fresh U8[object+53]) & 255
if unsigned c>36: c=(c-37)&255
S4 = fresh U32[object+312]
S5 = fresh U32[object+316]
SB c,[object+311]
probe(A0=S4,A1=S5,A2=c)
test returned A0 & 1
```

一減之後的 c 仍可達 218。只有 wrapped sum≤73，才能把此操作解作 modulo37；例如 wrapped sum74 得到37，而74%37為0。若已另證兩個原 byte 都在0..36，則其和≤72，會落在正確 normalization 的範圍；目前未建立該資料界線。

words312／316 在初次 probe 前各取樣一次，掃描時使用保存在 S4／S5 的同一份值。這與 callback 的每輪 fresh service-target load 不同，也不是來源物件在整段期間不變的證明。

## 完整 leaf：domain 以外不能當作任意 64-bit shift

leaf 沒有 load／store、call 或 frame allocation，所有 register definitions 精確只有 A0、A1、A2、A5。它不改 S registers、SP 或 RA，local CFG 無循環，經普通 RET 返回。

對呼叫者可能傳入的 byte count domain，令原 A0=lo、A1=hi、A2=n：

| n | 返回的 pair 行為 |
|---|---|
| 0 | 原 pair 不變 |
| 1..31 | unsigned `(hi:lo)` 邏輯右移 n |
| 32..255 | A1=0，A0=`hi >> ((n-32)&31)` |

所以在0..63可對應一般 unsigned 64-bit right shift；n≥64時 register shift count 會按 RV32 低5bits處理，並不是任意大小的數學64-bit shift。例如 n=64、hi=1，返回 A0=1；數學 `(1<<32)>>64` 是0。

selector 的初次 c 可能超過63，因此不能把初次 probe 一律解讀為讀取 64-bit bitmap 的第 c 位。不過 fallback 掃描只傳0..36，其 probe lowbit 在該 domain 可對應 captured pair 的 bit index。

## fallback 的 remainder、ordinal 與有限掃描

初次 probe lowbit=1便直接採 c。否則 fresh 讀 d=`U8[object+301]`，依 RV32M REMU：d≠0時 targetOrdinal=c%d；d=0時 remainder 為 dividend c。原本體沒有 local d-zero guard。

然後令 index=0、ordinal=0、limit=37。每輪 probe 使用 captured S4／S5 與當輪 index，返回後 AND1：

- lowbit=0：不增加 ordinal，進 index++。
- lowbit=1 且 ordinal=targetOrdinal：把 index 的 low8 放入候選，完成選擇。
- lowbit=1 且 ordinal 不符：ordinal++，以原 SLLI24／SRAI24 明確 sign-extend8，再進 index++。
- index 增到37：保留原 c，離開掃描。

原 scan SCC 精確有13個指令 nodes。已核對的 leaf 不改 S2 index、S7 limit 或其他 S registers；index 只從0每輪加1、到37退出。因而在 code identity、無外部干擾、frame／object 存取正常等前提下，最多掃描37輪。ordinal 也最多增加37次，因此在這個有界路徑不會達到 signed8 的負值範圍。

這些是原指令與有限 counter domain 的推導，沒有執行 target loop。若指令／資料存取 fault、frame words 被 alias 覆寫、或存在未排除的 interrupt／reentry／code writer，不能把它當成實機必然返回的保證。

## 保存、寫入範圍與返回值的限制

本體的 direct non-stack stores 只有 object byte311與byte310，leaf 沒有任何 memory store。selector 保存／恢復 RA@44、S0@40、S1@36、S2@32、S3@28、S4@24、S5@20、S6@16、S7@12，接著 SP+=48、RET。要恢復原 caller registers，仍需要這些 frame words 有效並在物件寫入等期間保持。

byte310最後得到選中的 index 或原 c；掃描耗盡並不證明它是有 set bit 的候選，也不保證值在0..36。A0保留最後 probe 的 AND1結果，不能額外命名為「選擇成功」旗標。

例如條件性資料 c=1、d=2、captured pair 只有bit36為1：targetOrdinal=1，但唯一 set bit 的 ordinal是0；掃描可耗盡並保留c=1，最後 A0卻為1。這只是說明 operand 合約不支持 success-flag 推論，不是實際資料可達性或裝置行為證據。

## 重播與剩餘工作

[檢查器](check_v4160_local_selector_static.py) 與 [完整 ledger](v4160-local-selector-static.json)：

```text
python analysis/check_v4160_local_selector_static.py
python -O analysis/check_v4160_local_selector_static.py
```

一般及 `-O` 模式逐 byte 重現 ledger，核對四個完整本體、callback joins、leaf 精確 clobbers、九個 frame fields、13-node SCC 與排名所需的 index／limit definitions，並拒絕40個指定 operand mutations。主機算術包含65,536個byte-sum cases、56,064個remainder-domain cases與9,216個pair/count代數cases；沒有執行 selector或leaf。

接續仍需展開第二個 local selector `0x417dc`／`0x4181c`、其他 callback helpers、完整 config gates／copy 合約、實際 installed binding，以及 object/global writers與欄位界線。這個 selector 的有限掃描不會解除上層 callback 的 termination 或 frame／payload 保存期未知。
