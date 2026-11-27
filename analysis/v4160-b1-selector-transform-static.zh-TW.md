# v4.1.60：B1 lookup、selector 與逐欄位反相

本輪完整核對兩版本 lookup、selector、transform，共 **636 bytes／228 instructions**。所有 bytes 對回原始 sparse HEX；另重用 comparator／predicate／copy 共 384 bytes。這是條件性靜態合約，不增加既有 C 重建覆蓋率。

| 本體 | V131 | V140 | 每版 bytes／instructions |
| --- | --- | --- | --- |
| lookup linked entry | `20000a94` | `20000a94` | 50／16 |
| lookup FLASH source | `40d04` | `40d44` | 同上，不重算 |
| selector | `6be3c..6bf26` | `6c020..6c10a` | 234／88 |
| transform | `6af42..6af64` | `6b126..6b148` | 34／10 |

[檢查器](check_v4160_b1_selector_transform_static.py) 與 [固定帳本](v4160-b1-selector-transform-static.json) 保存完整 operands、SHA-256、CFG、不可變路徑、原始 HEX、first-copy 映射與主機純量／區間憑證。沒有執行或模擬目標、callback、provider、NV、RAM／heap、MMIO 或硬體。

## Lookup：60-byte 記錄，以 U16 key 比較完整入口值

lookup 分開捕捉 count byte `200033b4 / 20003404` 與 array word `20003354 / 200033a4`。array word 在 count=0 時仍會被讀取，但不會解參照任何 record。

index 從 0 開始，以 stride60 掃描 captured count 筆記錄，每次 fresh 讀 U16[record+2]，與完整入口 A0 比較。第一個命中返回 record base；耗盡返回 0。index 以 low8 遞增，captured count≤255，所以最多探查 255 筆，在退出前不會先 wrap。

這個 leaf 沒有 frame、call、store 或 array-null guard。captured count／array 是否一致、記錄有效 extent、key 唯一性及實際 RAM 綁定仍是條件；入口大於 65535 不能等於零擴展的 U16 key。

接回 [B1 dispatch](v4160-b1-downstream-static.zh-TW.md)，非 `0xffff` ID 命中 P 後，傳給 selector 的是：

```text
type = fresh U8[P+5]
query = P+6
output = 0
```

這是不同於前輪 `20000a48` 的 lookup；兩者記錄步長、key offset 與輸出都不能混用。

## Selector 的四組入口

selector 建立 48-byte frame，保存 query Q 至 S3、可選 output O 至 S2。type 是完整 word，比較沒有 low8 截斷：

| type | 選擇方式 |
| --- | --- |
| 0／1 | 呼叫 `6b50c / 6b6f0(Q)`，捕捉其完整回覆 R |
| 2 | 從記憶體 pool 逐筆比較六個 bytes |
| 3 | 逐筆發出 NV read-request，再經兩個 helper 篩選 |
| 其他 | 返回 fresh U8 record count，不讀 query 或呼叫其他函式 |

type0／1 的 R 與 fresh count 無號比較，只決定是否執行可選 `copy(O,Q,6)`；O=null 或 R 不在界內均略過 copy，但仍返回原完整 R，沒有以 count 取代它。

## Type2：fresh pool／count 與 boolean comparator

index i=0，每次先用 fresh U8 count 決定是否准入，再 fresh 讀 pool word `20002fbc / 2000300c`，請求：

```text
20000442(pool + 16*i + 6, Q, 6)
```

非零回覆選取候選，零則 index 加一並 mask255，繼續 fresh count guard。重用 [既有 comparator](v4160-comparator-tail-static.zh-TW.md)：matching leaf 在正常有效觀察下，全六對相等回 1、首個不同回 0，另有任一 pointer=null 回 1 的特例。因此非零回覆本身不證明有效 pointer 或六-byte equality。

有候選後還會重新讀 count；candidate index 仍在界內且 O 非 null，才呼叫 `6b730 / 6b914(index,O)`。即使這次 count 已變而拒絕額外輸出，仍返回捕捉的 index。

耗盡時返回最新取樣的 count，不是較早的 index 或最初 count。selector 返回、候選後重查及上層 dispatch 的 count 是不同讀取；不能把稍後 `index<count` 單獨當成前一輪搜尋已命中的證明。

## Type3：保留三種不同的回覆判定

每個准入 index i 依序發出：

1. `440c2 / 44156(low16(515+6*i),16,SP)`；非零回覆略過候選。
2. `200004bc(SP,255,16)`；非零回覆略過候選。
3. `46018 / 460b0(SP,Q)`；**零**回覆選取候選，非零則 index 遞增。

步驟 2 重用 [byte predicate](v4160-n136-predicate-static.zh-TW.md)，與步驟 3 或 type2 comparator 是不同合約；matching predicate 的非零表示全部觀察為 FF。這裡沒有把 `46018` 的零回覆直接提升成未知格式的 equality 或成功意義。

候選後的 fresh count／optional output 流程與 type2 共用。兩條掃描路徑在 context 保存與 callees 返回前提下，每個 per-index 操作最多 255 次；不需假定 count 固定。對准入 i≤254，數值地址為 515..2039；read-request 的 A1=16 之單位、實際 output extent、SP buffer 初始化與保存期仍未證明。

## B1 的 output=0 只排除兩個局部額外輸出呼叫

實際 B1 呼叫把 O=0 傳入，selector 保存的 S2 在還原前沒有另行改寫。因此在 S2／frame 保存前提下：

- type0／1 不會執行 `copy(O,Q,6)`。
- type2／3 不會執行 `6b730(index,O)`。

它仍可能呼叫各條路徑的 lookup／compare／NV helpers，並把 query 或 stack pointer 借給它們。這不是整條鏈無副作用、無保存 pointer 或完全同步消費的證明。

## Transform：16 個槽位的 48 bytes 反相，16 bytes 保留

transform 入口 B=A0，沒有 null guard／frame／child call。它設定 end=`B+64 mod 2^32`，執行 16 個 stride4 步驟，每步：

1. fresh 讀 U16[slot+0]，以 XOR −1 反相，SH 回同一個 key。
2. fresh 讀 U8[slot+2]，以 XOR −1 反相，SB 回同一個 value。
3. **slot+3 不讀也不寫。**

正常返回 A0=end pointer，並非固定 status。只有 A0、A4、A5 被本體定義；沒有保存原 pointer word 的直接 store。有效 64-byte 存取、地址／物理 alias、外部干擾與資料保存仍是前提。

其 footprint 為 32 個 key bytes、16 個 value bytes，合計 48 bytes 被反相；其餘 16 個 byte+3 保持不被本 leaf 存取。對固定純量 x，兩次 masked NOT 還原原值的 U16／U8 代數已驗證，但不能直接宣稱 updater 的兩次 transform 抵消：它們之間刻意插入了 key／value 更新。

對前輪 updater 的 SP+16..79，這也收窄了 byte+3 的來源界線：逐筆 record SH／SB 及 transform 都不碰它；H=0 的整區 fill 若完成則仍會清除它，NV／其他 provider 也保留未知效果。不能把 routine 當成對整段 64 bytes 的完整 NOT，也未據此推定外部格式或用途。

## 重播與下一段

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_b1_selector_transform_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_b1_selector_transform_static.py
```

檢查器拒絕 228 個 instruction mutations、10 個 typed-load mutations，核對完整 U16／U8 反相代數、48／16-byte footprint、16 步圖路徑、fresh count 上界與帳本精確重播。host 純量憑證沒有操作目標記憶體或執行 transform；syntactic CFG 見證亦不表示實際可達或 provider 已返回。

仍需展開 `6b50c`／`46018`／`6b730`、NV read/write 的 units／extent／buffer 保存，以及 config callback／context pointer writers。實際 installed provider、NV 內容、callback 保存與完整物件生命週期仍未證明。
