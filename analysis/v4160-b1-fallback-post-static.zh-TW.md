# v4.1.60：Fallback 保存延伸至 post-config 與 initializer 返回

接續 [fallback 零來源與局部保存](v4160-b1-fallback-source-static.zh-TW.md)。本輪在既有名義 heap、完整 callee 與所選 I/O 條件下，把 `D+52=0` 從 post-config 入口延伸至其 RET，再接回 initializer 的正常返回。

這項結論保留 matching code／provider／mapping、fresh H／L、header／frame／context 保存、正常存取／callee／poll 完成，以及無不良物理別名或外部 writer 等前提。沒有證明實際 boot、NV 操作完成、heap ownership 或後續 APP／wrapper／事件的保存期。

## 呼叫與返回接點

| 接點 | V1.31 | V1.40 |
|---|---|---|
| Post-config 入口 | `0x43b3e` | `0x43bca` |
| Post-config RET | `0x43c4c` | `0x43cd8` |
| Initializer 的 post-config call | `0x43d4c` | `0x43dd8` |
| Initializer 已發布路徑 RET | `0x43d5a` | `0x43de6` |
| Fallback 槽 D+52 | `0x20003220` | `0x20003270` |

Post-config 的完整本體為 272 bytes。八筆固定 stores 與兩個固定 zero fill 目的範圍都避開 fallback。Frame stores 仍需有效、保存且不別名到受保護 RAM。

## Bootstrap 與首筆 table 配置

採用既有 **fresh** `H=0x2000418c, L=0x7000` 的條件，不把 APP 較早 stores 當成實際執行時快照。匹配 bootstrap 的名義結果為：

```text
Small header A = 200043ac，free size 504
Large header B = 200045ac，free size 27600
Sentinel E     = 2000b184
兩個非 sentinel 節點的加總 = 28104
```

原指令已核對 bootstrap 的 header／全域／accounting writes、walker 的無 store 本體及 late reset。名義 header 地址均高於 fallback；walker 兩節點的結果需要實際 links／tag／size 與取樣保持，不能外推到任意串列的終止性。

Post-config 從一個 fresh U8 形成容量 N0。全部 256 個來源 byte 對應 **67 種**容量，N0=14..212、步長3：

```text
q  = 576+6*N0
R  = roundup4(q)，範圍 660..1848
P  = B+8 = 200045b4
T  = P+576 = 200047f4
M  = P+R
```

在名義 large header 保持 free、size27600 等前提下，這次配置必定 fit 並分割，不走 search／sentinel fallback。第一個配置 header、remainder header M 與 fill `[P,P+q)` 都避開 D+52。

要接到後面的 table stores，仍需 `fresh P′=P`、`N1=N2=N0`、配置有效且沒有 header／frame／context 破壞。這些是既有名義 first-allocation 證書的保存條件，並非本輪觀察到的 heap 狀態。

## I/O shortcut

Late reset 是完整 10-byte leaf，只有固定全域 word 清零。後續完整 config-I/O 本體有四類 shortcut：base gate 為零、read callback 為零、write callback 為零，或完成初始四 byte 讀取後與另一次 fresh base 讀值相等。

前面三類不呼叫 read／write callback。相等讀回類則需要匹配 APP read wrapper `0x1979a`、fresh copy 綁定與正常完成的四 byte 搬移。它們只在有效且分離的 I/O／child frames 內寫入，因此在既有 ordinary-memory／MMIO 保存前提下不碰 fallback。

不能用 read wrapper 的回覆零代替讀回相等，也不能把四筆 byte transfer 當作原子 NV word read。匹配且保存 APP 的 NV／read／write 欄位時，也不把 gate 缺值的三類當成其已證實的實際路徑；仍需選用相等或 mismatch 分支及其條件。

Shortcut 的 I/O 回覆為1。Post-config 的後綴沒有 A0 定義，因此其條件式正常回覆也為1。

## Mismatch 的暫存配置與釋放

另外接回已有的名義 mismatch 證書，保留以下 fresh 條件：NV base=`0x08077c00`、length256、record count3、read=`0x1979a`、write=`0x197be`、copy 綁定匹配，以及完成的初始讀回與 fresh base 不等。

對全部67種容量，第一個 remainder header 為 M；第二次配置256 bytes、tag78，從 M fit 並分割：

```text
Temporary payload P2 = M+8
New free header N    = P2+256
```

M／N 的 header stores、fill(P2,ff,256)、每筆 callback 前的 payload word，以及 private release 寫入都落在名義 heap 內，與 fallback 分離。程式的三筆 256-byte NV 目的範圍為：

```text
08077c00..08077d00
08077d00..08077e00
08077e00..08077f00
```

區間均為左閉右開。NV／MMIO 在實體上的副作用仍須不破壞受保護 RAM；本輪沒有執行這些操作或證明它們在硬體完成。

釋放前還需要 fresh cache pointer 與每次 source pointer 保持為同一 P2。原 header B 的 tag1 保持 allocated，M 的 tag78 不觸發 `0x8001` counter，next N 保持 free，才有既有的 **只向後合併**分支。這些來源／headers 條件不能由 private helper 返回或 cache 清零推得。

匹配 APP write family 的軟體寫入限於自身 frames、名義 MMIO 與指定 NV 目的地；所需 context、S2 迴圈計數與 source／frame 保存仍是前提。I/O cache／neighbor 清理在固定低位 RAM，三個 builtin table words 則仍在原 table 配置內。

Mismatch 的 I/O 與 post-config 條件式回覆為0；這不代表 NV 寫入成功、暫存 payload 已清除，或一般釋放路徑都保持同一槽位。

## Builtin table 發布與受保護區間

兩類 I/O 路徑後都需要保存 `T=0x200047f4` 與所需 capacity／count snapshots。初始 count 保持零時，三個 builtin stores 位於 T、T+4、T+8，count 寫成3；它們都位於首筆有效配置內，遠離 fallback。

檢查器另以新增的 fallback 四 bytes 為目標，核對每版 **28 筆共用數值區間**，包含固定 post stores／fills、bootstrap globals／headers、account／control、I/O cache 清理及三個 NV 目的頁；再核對67種容量的首筆配置／table／mismatch 暫存配置與釋放區間。

28 筆是分類區間，有重複地址，也包含只在特定分支使用的區間；不是一次執行的 store 數。普通 frame 及實體映射的分離條件不由這些數值比較自行證明。

## 接回 initializer

前輪已在 matching source／copy／getter 條件下，把 fallback 零值證到 initializer +0xce 呼叫前。本輪若再滿足上述所選 post-config 條件，可證其正常 RET 時仍為零。

Initializer 返回後段 `+0xd0..+0xdc` 沒有 store 或額外 call：先將 A5 設零、恢復保存的 registers，再把 A5 交給 A0。因此它丟棄 post-config 的 I/O 回覆1或0，自己的正常回覆均為0，同時保持 fallback 零 word。

**這個零回覆不能作為 NV／配置成功的驗證。** 證書目前停在 initializer RET，尚未跨越 APP `0x19106`、builder 後段、wrapper、後續登記或 `param774`。

## 驗證

[檢查器](check_v4160_b1_fallback_post_static.py)與[固定 ledger](v4160-b1-fallback-post-static.json)重新套用完整來源／callee 證書，並把九個 resident 本體的全部1114 bytes 接回 strict HEX；APP callback family 由原始 APP 身分與完整 body guards 核對。新增56個原指令位置突變：52個 post-config stores／source／callee／branch／table 接點，以及4個 initializer forced-zero 後段接點。

```powershell
python analysis/check_v4160_b1_fallback_post_static.py
python -O analysis/check_v4160_b1_fallback_post_static.py
```

新增原始 byte 覆蓋為 **0**，APP C 重建覆蓋率不變。仍需補上 initializer 返回後的 APP／wrapper／登記／RF 順序與保存，確認 actual provider／fresh source／header snapshots／physical mapping，並完成其他 I/O 輸入域與整體保留／消費／釋放／通知保存期。

全程離線，只有原 bytes／CFG 與封閉數值區間證書；沒有目標執行、模擬、mutable target model、硬體存取、封包重放或 target network。
