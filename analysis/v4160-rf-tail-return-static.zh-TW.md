# v4.1.60：RF 的兩條返回路徑及尾段 snapshot

接續 [設定呼叫鏈](v4160-radio-config-chain-static.zh-TW.md)，本輪封閉 `63eda／63fc4` 與本機 reset leaf 的指定入口路徑，並核對完整 `641b0／6429a` 尾段。條件式保存證據推進到第二個 linked call 前；其後四個 callees 仍未封閉，因此整個尾段及 initializer 的實際返回仍未證明。

程式：[check_v4160_rf_tail_return_static.py](check_v4160_rf_tail_return_static.py)。證據：[v4160-rf-tail-return-static.json](v4160-rf-tail-return-static.json)。僅檢查原 bytes、operands、CFG、frame／讀寫集合與整數／區間等式，不執行或模擬目標 ISA、MMIO、FENCE.I、callback 或裝置。仍是兩份 resident 候選的合約，C 重建覆蓋率不變。

## 完整本體

| 項目 | V131 範圍 | V140 範圍 | bytes／指令 | stores／loads |
|---|---|---|---:|---:|
| RF | `63eda..63fa0` | `63fc4..6408a` | 198／72 | 11／19 |
| reset leaf | `63e58..63eda` | `63f42..63fc4` | 130／48 | 8／16 |
| 外層 tail | `641b0..64298` | `6429a..64382` | 232／79 | 18／23 |

範圍右端不含。每版共 560 bytes／199 指令，全部指令另有 operand guards，local CFG 無環。RF 在普通 RET 後仍有從前面分支可達的 code，一併納入。RF 有一個 direct call 及一個 indirect callback site；tail 有五個 direct calls。CFG 的 call-to-link edges 以 callee 正常返回為條件，不代表所有呼叫已封閉。

## A0=13、入口 state1 的 RF 返回

沿用前輪 mapping、fresh pointer／state 保存、有效非別名 frame 與無不利 MMIO／FENCE.I／IRQ／DMA／重入等干擾前提。state 基址為 V131 `20003514`、V140 `20003564`。

RF 先配置 16-byte frame，保存 RA／S0／S1／S2；fresh 讀 `4002420c` 到 S2，SW0 至同地址，再出現 FENCE.I。接著從 parent 發布的 pointer fresh 讀 `40024200`，取低兩位。

| fresh word 低兩位 | 指定入口的後續路徑 | 正常返回時 state+7 |
|---|---|---:|
| 0 | 直接進入 epilogue | 1 |
| 1、2、3 | 排除 callback 及特殊欄位分支，清 flag byte，再呼叫 reset leaf | 0 |

非零路徑 fresh state1 與3不相等，排除 RF+76 的間接 callback。保存的入參13又與6／7不相等；後續各次 fresh state1 排除6／7／8分支，因此不讀寫 state+8／+9 的特殊欄位路徑，直接到 RF+112。只清 V131 `20002efc`／V140 `20002f4c` 的 byte，再呼叫 reset。這不是任意 state／入參下 callback 不可達的證明。

兩條指定路徑與 reset 均沒有 A0 定義，所以返回時 A0仍13。RF 在返回前將 **S2 中自己讀到的 snapshot** SW 回 `4002420c`，還原保存的 registers／16-byte frame，再 RET 至 outer tail link `641fc／642e6`。

## reset 的 fresh 來源與保存界線

reset 無 frame、巢狀 call，只定義 A2..A5。當 fresh descriptor slot `2000350c／2000355c` 仍為 parent 發布的0時，兩個 descriptor-derived pointer RMW stores 不可達。所選路徑只有下列五個 MMIO word stores，再清 state+7 的 byte：

| 順序 | 條件式 CPU 地址 | 資料 |
|---:|---|---|
| 1 | `40024250` | `fresh & fffffff8` |
| 2 | `40024200` | `fresh OR 8` |
| 3 | `40024100` | `(fresh & fffffe7f) OR 80` |
| 4 | `40025008` | `fresh & ffcdffff` |
| 5 | `40024250` | 0 |

表中數字以十六進位表示，各個 fresh 指各次原指令取樣，不能合成一致的硬體 snapshot。第二筆寫入後再次讀 `40024200` 的 bit3，只決定略過或執行四個 NOP；沒有迴圈，不是硬體完成輪詢。也不能從剛才 OR8 的 CPU 寫入就斷言 fresh bit3 為1。

清除 mask 源自 `ffce0000-1=ffcdffff`，其 complement 是 **`00320000`**。清除 mask 與外層 tail 的 OR mask `00330000` 不互為反向：`ffcdffff & 00330000 = 00010000`。本輪不把這組操作稱為完整還原。

descriptor 非零的一般路徑仍含兩個 pointer-derived OR stores，不能沿用上述保存結論。所選路徑的固定 flag／state writes，另與 B296、count／capacity／ctx gate、table pointer／最大 table、名義 node、task bytes 及所需 pointer slots 做區間分離核對。

## 外層 snapshot 與新的截止點

outer tail 在呼叫 RF 前 fresh 讀 snapshot 到 **S4**；RF 內部再 fresh 讀另一個 snapshot 到 **S2**。即使 outer 已 SW0，仍不能把 inner snapshot 假定為0，也不能假定兩個 snapshot 相等。它們各自的 CPU store-source 配對與硬體最終狀態是不同證據。

兩條 RF 返回路徑均保存 tail 所需 S0／S1／S4、SP 與保存字。RF 後才重新設置 S2／S3／S5 為 `20003000`；不需要假定它們入 RF 時已是後續基址。

tail+76 到+150沒有本機分支。維持各次 pointer load 的 mapping 前提時，依序對 `40024100` 做三次 fresh RMW，對 `40025008` OR `00330000`，再對 `40024250` 寫93。本輪截止在下一個 call **之前**：

| 版本 | call PC | 目標 |
|---|---|---|
| V131 | `64246` | `6645c` |
| V140 | `64330` | `6659a` |

此時 outer 的32-byte frame仍在，S4仍持有 outer snapshot；state可能為1或0，不能在非零 low2 路徑後繼續假定為1。ctx gate5、count6及前輪欄位在明示保存條件下仍可保存。

## 完整 tail 的返回義務

後續 linked callees 為 V131 `6645c,67198,662da,6636e`，V140 `6659a,672d6,66418,664ac`。若它們都正常返回，保存所需 S0..S5、SP、frame words、fresh pointer slots，且存取正常／無不利干擾，tail 後段才可依序執行 MMIO RMW、清 `40024250`、清 state+7、將 S4 SW 回 `4002420c`，再還原七個保存字／SP32並 RET。這是本機指令所要求的未驗證義務，不是已完成的返回證明。

三個 early exits 都跳到 tail+214 epilogue，且位於 outer snapshot 讀取之前；它們不清 state，也不執行 S4 的 control 寫回。指定入口 state1／matching pointer 路徑會排除這三個 exits。

## 重現與下一步

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_rf_tail_return_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_rf_tail_return_static.py
```

一般與 `-O` 均要求 ledger 逐 bytes 相同，核對原 APP／SDK／候選身分及既有證據鏈。兩版合計拒絕386個 operand mutations及12個非本輪支援的 NOP／FENCE.I 編碼變體；另檢查 branch／mask identities、所選 paths、frame saves／restores與區間排除。非支援編碼不等同架構上非法。

下一步展開 `6645c／6659a` 及其後 callees，釐清正常返回與保存條件；實際 installed provider、物理 MMIO 效果與後續物件保存期仍未證明。
