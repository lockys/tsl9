# v4.1.60：輸出物件派送、stack record 與下游指標保存邊界

承接 [payload／callback 消費端](v4160-payload-consumers-static.zh-TW.md)，這次將 `0xc6a8 → 0x12a08` 接至兩個本機 gates、record 組裝與完整 `0x18ca4`。採原 bytes 靜態解碼、完整 operands／局部 CFG／stores 核對及主機端區間算術，沒有執行或模擬韌體、copy、stack 記憶體、provider 或 MMIO。

結論：tag 非零路徑明示轉交原輸出物件，ambient A1 也仍可能攜帶先前來源；tag 為零路徑改交物件內部位址給 copy，再以本機 stack record 替換 A1。`0x18ca4` 不改 A1，故正常返回時該暫存器仍帶著 record 位址。沒有直接 pointer-field store，不等於沒有保存或外傳。

可重播的 [檢查器](check_v4160_record_dispatch_static.py) 與 [指令／CFG／完整長度 footprint ledger](v4160-record-dispatch-static.json)。既有 C 重建已包含相關區段；本階段不增加 C 重建 bytes，也不提高其覆蓋率。

## 完整本體

區間為半開；包括 RET 後由局部分支進入的區塊，並非只取第一個 RET 之前。

| 角色 | APP 區間 | bytes | 指令 | stores |
|---|---|---:|---:|---:|
| record 派送 | `0x12a08..0x12a6e` | 102 | 35 | 5 |
| probe | `0x81aa..0x81b0` | 6 | 2 | 0 |
| gate | `0x821e..0x8248` | 42 | 15 | 0 |
| 下游資料／暫存器寫入 | `0x18ca4..0x18d78` | 212 | 72 | 8 |
| 合計 | | **362** | **124** | **13** |

APP 為 76,800 bytes，base `0x8000`，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。每個本體的 SHA-256、逐條 operands、所有可達局部節點與無局部迴圈均固定於檢查器及 ledger。亦重新驗證前階段來源鏈、SDK header、兩個 resident 候選、完整 sparse HEX 覆蓋與 sidecars；候選值不代表實際 installed 綁定。

## 兩個本機 gate：不再假設合成回覆

令 O 為 `0x12a08` 入口 A0。本體先配置 48-byte frame，保存 S0／RA，將 O 放入 S0，再直接呼叫 `0x81aa`。

`0x81aa` 只有 fresh `A0=U8[GP+167]` 與 RET，不讀入口 A0／A1，只改 A0。若該 byte 為零，派送端 fresh 讀 `U16[O]`，必須等於 1 才繼續；probe 非零時略過這個 ID 條件。先前 frame stores 如果與 GP／物件資料別名，可能影響後來讀值，不能擅自當成入口快照。

接著 `0x821e(0)` 先讀 `Q=U32[GP+84]`，再讀 `U8[Q+4]`。bit 3 已設就返回零。否則一般入口完整 unsigned A0 必須 <=2，才讀 `U8[GP+193+A0]`，小於 3 返回 1，其餘返回零。本派送呼叫傳的是 0，故其被選狀態 byte 為 `GP+193`。

這個 leaf 沒有 stores、frame 或子呼叫，僅改 A0／A4／A5，保留 A1。派送端 gate 返回零就進 epilogue；通過後才 fresh 讀 `U8[O+11]` 作 tag，沒有先行的整個物件 extent 檢查。

## tag 非零：原物件與 ambient word 到達未知 TX callee

`0x12a66` 將 A0 換回 S0，即 O；`0x12a68` 呼叫 `0x16b7c`，正常返回才進共用 epilogue。在這條局部路徑中，兩個已完整展開的 leaf 都沒有改 A1，派送本體也未改 A1，因此該呼叫入口 A1 等於派送入口的 ambient word。

承接前階段 `0xc776 → 0xc6a8` 時，若實際 copy 符合保留 A1 的參考實作，A1 可能仍是最早的 stack 來源。這是條件性暫存器流向，並非 A1 已被宣告為 `0x16b7c` 的第二參數，也不是 provider 必定保存 A1 或該位址仍有效的證據。`0x16b7c` 在本批仍是未知 callee 邊界。

## tag 為零：原始長度 copy 與 stack record

令 S 為新 SP，即入口 SP−48。先 fresh 讀 row ID 與長度，再依序進行三筆 record stores：

| 新 SP 位移 | 寬度 | 寫入 |
|---|---:|---|
| +20 | 2 | 0 |
| +12 | 4 | fresh `U16[O]` 的零延伸值 |
| +22 | 1 | fresh `n=U8[O+2]` |

`S+16..19` 沒有被這三筆固定 stores 初始化。fresh `[0x4004c]` 的 copy 請求為 `(A0=S+23,A1=O+3,A2=n)`，這個 n 是原先讀入的 byte，沒有先 mask 或 cap。此處明確覆寫 ambient A1，但不能因此排除 copy 保存 O+3 或其他 ambient registers 帶著指標。

copy 正常返回且所需 SP／S0／frame 保存時，再明確設定 `A0=0x40006400,A1=S+12`，直接呼叫完整展開的 `0x18ca4`。其返回 link 為 `0x12a5e`，接著只恢復 RA、S0、SP，沒有另行清除 record bytes 或正規化 A0。

### 長度與 frame 的靜態相交範圍

本體沒有自己的 n 上限。僅在實際 copy 與參考合約相符、有效非回繞存取、必要 context 保存且沒有不利別名等前提下，目的範圍才可寫成 `[S+23,S+23+n)`。檢查器對全部 256 個 n 計算區間，沒有在主機建立或執行 copy／stack 狀態。

| n 的門檻 | 與 frame／讀取範圍的關係 |
|---|---|
| n<8 | 本次 copy 未填滿稍後固定讀取的 `S+23..30`；其餘 bytes 的內容未知 |
| n>=8 | 本次 copy 範圍包含上述八個 payload bytes，不代表整個執行成功 |
| n>=18 | 開始相交保存 S0 的 `S+40..43` |
| n>=22 | 開始相交保存 RA 的 `S+44..47` |
| n>=26 | 開始越過本函式 48-byte frame 的上界 |

這些是條件性的 footprint，沒有證明上游實際可達的長度、不利寫入真的發生，或這些路徑能保持正常返回。原指令的後續 nibble mask 發生在 copy 之後，不能回頭當成 copy 的長度保護。

## `0x18ca4`：fresh 選取、完整 stores 與 A1 返回

令入口 A0=T、A1=P。本體沒有固定的絕對 base literal，這一條 caller 才把 T 設成 `0x40006400`；不將 numeric address 等同已證明的設備用途。

選取依序讀三次 fresh `U32[T+8]`：第一次 bit 26 設定選 bank 0，否則第二次 bit 27 設定選 1，否則第三次 bit 28 設定選 2。皆未命中返回 4，不讀 P、沒有 stores。選中路徑返回 bank，因此 0 也是正常選中值。只有另外證明讀值穩定時，才能把它描述成同一 bitmap 的優先序。

選中時令 `B=T+384+16*bank`。先讀 F=`U8[P+8]`、R=`U8[P+9]` 的位置是在首筆 B store 之後；依序完整八筆 stores 為：

| 次序 | 目的與資料來源 |
|---:|---|
| 1 | `U32[B]=fresh U32[B]&1` |
| 2 | F=0：`(fresh U32[P]<<21) OR R OR fresh U32[B]`；F 非零：`(fresh U32[P+4]<<3) OR R OR F OR fresh U32[B]`，寫 B |
| 3 | `U8[P+10]=fresh U8[P+10]&15`，同時保存該 nibble |
| 4 | `U32[B+4]=fresh U32[B+4]&0xfffffff0` |
| 5 | `U32[B+4]=另一個 fresh U32[B+4] OR 保存的 nibble` |
| 6 | P+12、11、13、14 的有序 byte 讀值組成小端 word，寫 B+8 |
| 7 | P+16、15、17、18 的有序 byte 讀值組成小端 word，寫 B+12 |
| 8 | `U32[B]=另一個 fresh U32[B] OR 1` |

所有移位／word 運算依 RV32 截取。F／R 沒有額外 boolean mask；第 1 筆保留 old bit 0，不等於先關閉；第 5 筆使用另一次 readback，不保證低四位恰等於 record nibble。payload 讀值也不是原子快照。若 P 與 B 範圍別名，或外部 writer／硬體會改讀值，不能沿用先前值。

本體只有 A0、A2–A6 的 encoded 寫入，無 frame、calls 或外部尾跳，不改 A1／SP／RA／GP／S。八筆 stores 包含一筆原 record 的 byte 改寫，所以來源 record 不是唯讀；其餘七筆是 B 範圍 word stores。沒有直接把 A1 的 pointer 值存到 pointer field，但正常返回時 A1 仍保留 P。

在 tag=0 串接中，若先前零 halfword 未遭 copy／alias／writer 改動，P+8／P+9 均為零，故走第一個 ID 分支而不讀 `P+4..7` 的洞。下游仍無條件讀取八個 payload bytes，不依 P+10 nibble 限制；n<8 時其餘 bytes 不能擅自補零。

在正常返回且 frame 未受損的條件下，派送端 epilogue 不覆寫 A1，因此它仍等於入口 SP−36，指向已離開的本機 frame。這不直接證明某個 callee 會在返回後使用它，也不能證明內容已抹除或 ownership 已結束。

## 驗證與下一個邊界

```text
python analysis/check_v4160_record_dispatch_static.py
python -O analysis/check_v4160_record_dispatch_static.py
```

一般／`-O` 均需逐 byte 重播 ledger，並通過 65,536 組 gate byte 分類、256 個長度 footprint、8 組獨立 selector bit triples、256 個 nibble 與 1,024 組 byte placement 算術，以及 18 個指定原指令 mutation 的精確 operand guard。這些是靜態資料與主機算術檢查，不是裝置功能或實際 MMIO 測試。

仍待追查 `0x16b7c` 對 ambient inputs 的使用、O+2／O+11 的其他 writers 與實際可達長度、copy provider 保存條件、installed provider 綁定及實體 MMIO 副作用。現階段不把局部無 pointer-field store 當成完整生命週期證明。
