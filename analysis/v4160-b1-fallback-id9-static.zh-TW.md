# v4.1.60：ID9 向量發布、配置保存與 ID10 返回

接續 [ID8 至 ID9 串接](v4160-b1-fallback-id8-static.zh-TW.md)，本輪把第四個 initializer 的九筆向量寫入、local ID9／record2、callback-register 尾跳與下一次 task 登記接起來。在所選保存與 fresh metadata 條件下，終點為 ID10／count11，停在第五個 outer initializer 呼叫前。

檢查器：[check_v4160_b1_fallback_id9_static.py](check_v4160_b1_fallback_id9_static.py)；證據：[JSON ledger](v4160-b1-fallback-id9-static.json)。使用原始 bytes、不可變 CFG、固定區間與閉合索引／frame 證明；沒有執行或模擬目標，也沒有建立可變 target RAM／heap／provider／MMIO／IRQ 模型。本輪新增 C 重建 bytes 為0，原始 bin 不變。

## 九筆向量寫入的邊界

令 G=`0x20003000`，V1.31 的 δ=0、V1.40 的 δ=80。向量函式完整106 bytes，只有 A4／A5 定義、九筆 word stores，沒有 loads、calls 或 frame。九筆恰好覆蓋 `[G+904+δ,G+940+δ)` 的36 bytes；CB48 結束於 G+904+δ，local ID7 位於 G+940+δ，兩端都沒有重疊。

| 項目 | V1.31 候選 | V1.40 候選 |
|---|---|---|
| ID9 initializer | `0x50412` | `0x504ac` |
| Vector 函式 | `0x50368` | `0x50402` |
| Active B word，寫零 | `0x20003388` | `0x200033d8` |
| Active A word，寫零 | `0x2000338c` | `0x200033dc` |
| Vector B base | `0x20003390` | `0x200033e0` |
| 額外清零 word | `0x2000339c` | `0x200033ec` |
| Vector A base | `0x200033a0` | `0x200033f0` |

六個非零 code pointers 分別是：

| 向量 | V1.31 | V1.40 |
|---|---|---|
| A | `0x5091a, 0x50668, 0x4f39e` | `0x509ba, 0x50708, 0x4f436` |
| B | `0x517a0, 0x5134e, 0x515ee` | `0x51840, 0x513ee, 0x5168e` |

兩個 profile 各自核對操作數與完整 SHA-256，不能把全部位址差異當作同一個 relocation。Initializer 的直接呼叫清單只有 vectors 與既有 selector leaf，再尾跳 callback-register；它不呼叫 activation selectors，也不執行發布的 code pointers。

因此在匹配程式、合法不別名存取、沒有不利介入寫入的前提下，兩個 active words 在本輪終點仍為零。這只描述該初始化邊界，不表示之後不會啟用。Flags byte `G+944+δ` 沒有被本輪寫入，其來源與 activation 呼叫順序仍未證明。

## Local ID9 與 record2

完整42-byte initializer 以32-byte frame 保存入口 ID9／RA，從 SP+12 重載 ID9，寫入 local byte `G+943+δ`，再以 A0=9、A1=6 呼叫既有 selector。Caller 固定的 selector6 選 record index2，依序寫 ID byte9、selector 半字6：

| 寫入 | V1.31 | V1.40 |
|---|---|---|
| Local ID9 byte | `0x200033af` | `0x200033ff` |
| Record2 selector 半字6 | `0x20003338` | `0x20003388` |
| Record2 ID byte9 | `0x2000333a` | `0x2000338a` |

Record0 的 selector4／ID8 與 record1 的 selector5／ID7 都保留。通用 selector 的 low16 guard 仍不足以證明任意 upper16 輸入的 record 範圍；本輪只接原 caller 明確載入的 A1=6。

## 1024組既有配置的保存

十二筆固定 stores 為九筆 vector words、local ID9 byte 與兩筆 record2 stores。檢查器逐筆排除對沿用的 fallback、F 前94 bytes、F+94 的 `ff00`／F+96 的零 byte、q／r 來源、pool pointers、saved ID6、local ID7／ID8、record0／1、task metadata、timer、flags 與既有 entry0..9 的覆蓋。

另明列 ID8 的 pool／middle／end pointer words、Hook A／B words 與兩個已清零 words。對768組 ID8 正配置與256組零分支逐列檢查先前 resource／first 或 second／third pool owners、ID8 新 payload／header、各 remainder headers，以及完整第一張 table payload。本輪沒有配置或 fill 呼叫，所以這些 header 不再被重用或分割。

Callback table 的單筆 store 是另一個預期發布，不能宣稱整個 CB48 不變。檢查器把所有可能 slot 的 store 範圍分別排除於配置 owners、vector writes 相鄰區與 protected fields 之外；後續 task entry10 的 store 也另行檢查。

這些是不可變區間計算，沒有 heap／RAM 內容重播。實體不別名、有效 frames／metadata、匹配的原始程式與 required ABI 保存、沒有不利 IRQ／DMA／重入／外部寫入等前提仍須成立。

## 第三次 callback 登記

Initializer 還原 RA、釋放32-byte frame，把非零 callback pointer `0x4f516／0x4f5ae` 送入既有 leaf，使用不更新 RA 的尾跳。Leaf 的普通 RET 因此返回 outer entry+72。所選階段的同時存活 frame 為 outer16＋initializer32=48 bytes；vectors、selector 與 callback-register 都沒有額外 frame。

- q>0：前兩次登記保留 slots0／1 的非零 pointer，其餘 resource 清零值也保留，則第三次登記選 slot2。
- q=0：單次 leaf 仍有原始13條 CFG 路徑。若每次非零前綴觀察與成功寫入的非零 pointer 都保留，且中間無介入寫入，三次掃描的插入索引必須嚴格遞增；一旦全滿便持續全滿。以 index12代表全滿，共299組三元組：220組三次插入、66組第三次全滿、12組第二次起全滿、1組三次皆滿。

299組索引關係是額外保存條件下的純整數結論，沒有把逐槽 fresh reads 當成原子一致快照。Leaf 插入時回覆 `(A0,A1,A2)=(0,0,12)`；全滿時回覆 `(19,最後觀察到的非零slot11 word,12)`。Outer 不測試這個 A0，登記失敗仍會到下一次 task 登記。

## ID10／count11 終點與未完成流程

若 fresh count10、capacity至少14、table pointer仍為 T=`0x200047f4`，registrar 把 handler `0x6cc4c／0x6ce38` 發布到 entry10=`0x2000481c`，count 更新11，回覆 A0=10、A2=11，A1 保留 callback-register 結果。Entry10 是第一張 table payload 內的預期更新，不覆蓋 entry0..9 或其他配置 owners。

終點為 V1.31 `0x6dd6a → 0x6c300`／V1.40 `0x6df5a → 0x6c4ec`，fallback0、gate5、saved ID6、local ID7／ID8／ID9、task count11。第五個 initializer 尚未串接。

本輪也重核 activation selectors、已發布 callback 與 vector consumer 的原指令／有限 CFG 證書，但沒有把它們接入已完成的初始化呼叫鏈。Callback 中的 `0x20000a94` provider、consumer 的 lookup／indirect call／後續尾跳、flags 寫入來源、vector targets 的實際消費與完整跨事件保存／釋放期仍未完成驗證。固定 code-pointer stores 不代表 callback 已執行。

兩個候選各有11個 strict sparse HEX 範圍核對；重核740 bytes／250個本輪原指令護欄、44條額外 runtime CFG 證書、合計1549組變異拒絕、1024組既有配置與299組條件性索引三元組。正常與 `-O` 模式均須重算並逐 byte 比對 ledger：

```powershell
python analysis/check_v4160_b1_fallback_id9_static.py
python -O analysis/check_v4160_b1_fallback_id9_static.py
```

實際 installed 綁定、fresh source／header writers、其他配置／失敗分支、物理副作用與實機功能仍未完成驗證。本輪結果是條件性靜態保存與返回證明，沒有提高可用韌體或實機驗收的宣稱。
