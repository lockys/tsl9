# B1 gate 的實際表項、物件槽位與 P+276 來源串接

接續[輸入解析與兩個 caller gates](v4160-b1-recompute-callers-static.zh-TW.md)，本輪定位到兩處外層間接派送：兩者都以 **P+23 的 byte、最大索引 42**查同一張 43 項表，其中 **20→gateflag，21→gate80**。也把 key 的 W+276 writer 接回既有 APP 設定／S+36 來源，並區分 **query／dispatch 的 B+164** 與 **submit 的 B+168**。

[Python checker](check_v4160_b1_gate_source_static.py) 與[固定 JSON ledger](v4160-b1-gate-source-static.json) 保留原始 operands、表項、hashes、選定視窗邊界、parent CFG／定義普查及來源憑證。全程離線讀取原始 bytes／strict sparse HEX，僅核對不可變圖、來源定義與封閉整數關係；沒有目標執行、模擬、可變物件／provider 模型、硬體存取、封包重播或目標網路分析。

## 範圍：選定視窗與完整資料表，未宣稱整個 parent 行為已重建

| 本輪選定程式視窗 | V131 | V140 | 每份 bytes／指令 |
|---|---|---|---|
| parent A 捕捉物件／形成表基址 | `[0x595b8,0x595fc)` | `[0x59700,0x59744)` | 68／22 |
| parent B 捕捉物件／保存表基址 | `[0x61234,0x61284)` | `[0x6131e,0x6136e)` | 80／28 |
| parent A 派送／fallback | `[0x599c2,0x599fc)` | `[0x59b0a,0x59b44)` | 58／21 |
| parent B 派送／fallback | `[0x617ae,0x617ee)` | `[0x61898,0x618d8)` | 64／23 |

兩份候選合計新增 **540 bytes／188 條選定指令**，另固定兩張各 172-byte 的完整表，共 **344 bytes／86 個 word**。本輪沒有新增「已完整重建語意」的函式；視窗有明示的外部 frontier，不能將視窗結尾當成整個 parent 返回。

為核對跨中段的 S0／表基址來源，另外以原始 SHA-256、strict HEX、CFG 及定義普查覆核下列完整 parent 範圍：

| parent | V131 | V140 | 每份 bytes／指令／CFG edges |
|---|---|---|---|
| A | `[0x595b8,0x59d3e)` | `[0x59700,0x59e86)` | 1926／653／732 |
| B | `[0x61234,0x61b1c)` | `[0x6131e,0x61c06)` | 2280／764／837 |

這些 identity／CFG／定義普查範圍共 **8412 bytes**，包含上述視窗，不能再與 540 bytes 相加成新重建量。尚未展開全部 cases、callee 副作用、等待條件或整個 parent 的保存／釋放語意，亦未證明迴圈進展。

## 43 項表與兩處真實查表指令

V131 表為 `[0x6e540,0x6e5ec)`，V140 為 `[0x6e730,0x6e7dc)`。完整 43 個原始 word 及其 hashes 均固定在 checker／ledger；不是只從單一 pointer 字串推測表範圍。

兩處派送先讀 fresh byte P+13，恰為 **3** 才繼續讀 fresh byte P+23。無號索引必須不大於 **42**，才做 `index<<2`、讀取表中的 word、`A0=S0`，以 `JALR A5` 呼叫。

| 零起算索引 | V131 表項位置 → 目標 | V140 表項位置 → 目標 |
|---|---|---|
| 20 | `0x6e590 → 0x5c7ac`（gateflag） | `0x6e780 → 0x5c8f4` |
| 21 | `0x6e594 → 0x5c74e`（gate80） | `0x6e784 → 0x5c896` |

這些目標接回前一階段完整核對的 gates。兩處 callsites 分別為 `0x599f6／0x59b3e` 與 `0x617ea／0x618d4`，沒有本機 target null guard。原始表項對上原始目標，仍不等於 installed table、執行時路由或 callback invocation 已證明；其他 41 個目標的完整語意不在本輪展開。

## 物件來源是 B+164，表基址的保存方式不同

令 B=`0x200033b8／0x20003408`。兩個 parent 都從 **fresh U32[B+164]** 捕捉物件到 S0，並不是直接把入口 A0 當作派送物件。固定 cell 為 `0x2000345c／0x200034ac`。

完整 parent CFG 的 reaching-definition 核對，確認在選定 `A0=S0` 前，S0 的最後本機定義是這次捕捉，並非 epilogue 的 S0 restore；call 前 A0 的最後定義也正是該 `MV`。這種靜態資料流以中間 callees 保存必要的 callee-saved registers／frame 為前提，不是暫存器機器的執行重播。

- parent A：用 S6 保存形成好的表基址。在選定查表 add 前，S6 的 reaching definition 為 `parent+0x40` 的 ADDI，其來源是 `+0x20` 的 LUI。
- parent B：先形成表基址並存入 **SP+12**，在查表時重新載入。S6 在中段 `+0x29a` 另有定義，因此不能直接假設查表當時 S6 仍是表基址。checker 核對 SP+12 只有一個本機直接 store，形成值正確，且該 store 支配選定 reload；本機解除 frame 的路徑不能回到這個 reload。

以上還需要 stack word、S0、表內容不被 callees／alias／外部 writer 破壞，且捕捉的 P 仍有效。沒有本機 P null／物件 extent 證明，也未證明整個 callback 的呼叫、返回或 lifetime。

## 回覆後不是直接返回；第二處 fallback 還有 callee

兩處都以完整 A0 是否為非零，決定進入 fallback。回覆零時，parent A 跳到 `0x599aa／0x59af2`，parent B 繼續到 `0x617ee／0x618d8`，都已在本輪派送視窗之外。

fallback **重新讀 P+23**，不能沿用查表前的索引。fresh 值恰為 7 時略過以下 stores；其他值則依序：

1. 將 fresh key 的低 byte 寫 P+45。
2. fresh 讀 P+168 word，OR 1 後寫回 P+168。
3. parent B 另以 `A0=S0` 呼叫 **`0x5a23e／0x5a386(P)`**，才離開視窗；parent A 在這個 fallback 沒有對應 call。

該 fallback callee 的副作用、pointer 保存及後續處理尚未展開。這裡的 P+168 是 **物件相對欄位**，不同於全域 B+168 的 pointer cell。

接回完整 gate 合約時，可保留一個容易混淆的差異：gate80 在其內部呼叫過解析函式後，不論解析回覆 0、1 或 2，都強制回覆 **0** 給外層；因此其內部非零分支不會直接觸發這裡的 fallback。gateflag 則將解析拒絕 1 保留為 1，會進入外層 fallback；解析 0／2 的 handled arms 仍強制回覆 0。兩個 gate 自己的先決條件不符時也返回 1。這些串接仍受實際綁定、fresh 欄位及正常返回條件限制。

## P+276 writer：是 key 的固定槽位快照，不是配置回覆

重用完整 `key 0x59e64／0x59fac`（各 416 bytes）原指令，確認：

- `key+0x14` 做 lookup，`+0x18` 將其回覆 W 保存在 S0，null 分支不進入此 writer。
- 後續另一次 allocator 請求的回覆先存 **W+272**；只有非零路徑才到以下 W+276 writer。該配置的 64～260 要求大小，不是 W+276 所指來源的長度。
- `key+0x90` 重新讀固定 word **`0x20003538／0x20003588`**，將 held 指標值在 `+0xa0` 寫到 **W+276**。它沒有在這裡複製來源內容、做 refcount 或驗證 pointed bytes。

這個 fixed word 正好是既有 buffer-origin 證據的 **S+36**，S=`0x20003514／0x20003564`。完整 APP builder、設定 initializer 與 RF publisher 的條件性來源鏈為：

```text
APP 設定 literal H=0x2000418c
  → resident config word0（須 matching copy／保存條件）
  → RF publisher fresh X
  → S+36=X
  → key 稍後重新讀 S+36
  → lookup 物件 W+276
```

不同時點的 fresh reads 不能合併成同一觀察值。key 的後續 callees、其他 writers、物件 identity、publication 順序及來源保存期仍可能影響這條鏈。

若 W 最後確為 gate 的 P，欄位保持、來源仍存活且可讀，解析才會讀到這個指標。名義 H 的 272-byte 前綴在數值上容得下 Q+3～Q+10 的 **11-byte 存取需求**，但不是 ingress 真實長度、初始化、allocation、ownership 或硬體寫入的證明。

## Query／dispatch 的橋接槽位與 submit 的相鄰槽位

重用完整 RAM query `0x20001122`（620 bytes），其選定成功 suffix 在 `+0x1c4` 將保存的入口 P 發布到 **B+164**，然後明確返回 0。這與兩個 parent 的 capture cell 完全相符，形成一條**有條件的 query→dispatch 固定槽位橋接**。

若要將 parent 的 S0 等同於該 query P，仍需證明發布發生在捕捉之前、中間沒有 clear／overwrite／alias 干擾、來源 P 有效，以及 matching provider 與必要 register／frame 保存。query 的這個成功 suffix 並沒有直接呼叫上述兩個 parents，不能憑同一 cell 推定實際執行順序。

完整 submit `0x59d3e／0x59e86`（各 256 bytes）發布 W 的位置則是 **B+168**，即 `0x20003460／0x200034b0`，與 B+164 是相鄰且不同的 word。不能用 submit 的 publication 代替 query 的橋接，也未證明 key lookup W、query P 與兩個 parent 捕捉的物件為同一個。

## 驗證與仍需追查的部分

```powershell
python analysis/check_v4160_b1_gate_source_static.py
python -O analysis/check_v4160_b1_gate_source_static.py
```

checker 重跑祖先驗證、APP／SDK／兩份候選身份、strict sparse HEX 及固定 ledger；四個程式視窗逐 operand 核對，兩張完整表逐 word 固定。parent 的完整來源 hash、CFG hash、call／暫存器定義普查支持選定資料流，沒有將其當成全部行為已重建或 loop progress 已證明。

負向檢查包含 **188 個指令位置、8 個 typed-load funct3、344 個 table bytes**，必須全部被拒絕。另對全部 256 個 byte keys 核對 `key<=42` 恰限制在 172-byte 表內，並核對 fixed-cell 地址、相鄰 word 差異與名義前綴幾何；沒有 target execution、frame／heap／provider 的可變模型。

仍需追查 Q 的實際 byte producer／ingress 長度、key W／query P／parent P 的同一性與發布／清零順序、實際 provider 綁定，以及完整 parent cases、fallback callee `0x5a23e／0x5a386`、節點消費／釋放與保存期。此次沒有增加既有 C 重建分子或更新 **95.75%** 靜態重建快照，也未宣稱完整可用韌體已驗證。
