# v4.1.60：tagged 派送、兩次長度與本機傳輸合約

本階段承接 [record 派送與指標邊界](v4160-record-dispatch-static.zh-TW.md)，完整展開 `0x16b7c`、query／send／update 及其唯一傳輸 leaf。所有直接軟體 callee 都有原 bytes 合約；fresh copy slot 的實際 provider、指標保存與實體 MMIO 行為仍未知。

僅做原 bytes 解碼、operands／完整局部 CFG／stores 核對及主機算術，沒有執行或模擬 target ISA、stack／copy 狀態、provider、callback、MMIO 或裝置。既有 C 工作已包含這些區段，本階段不增加 C 重建 bytes 或覆蓋率。

[檢查器](check_v4160_tagged_dispatch_static.py) 與 [指令／CFG／長度 footprint ledger](v4160-tagged-dispatch-static.json)。

## 完整本體與固定身分

區間採半開；保留 RET 後的局部 cold blocks 與明示迴圈 backedges。

| 角色 | APP 區間 | bytes | 指令 | stores |
|---|---|---:|---:|---:|
| tagged 派送 | `0x16b7c..0x16c72` | 246 | 86 | 10 |
| send | `0x168de..0x1693e` | 96 | 36 | 7 |
| update | `0x1693e..0x16994` | 86 | 32 | 7 |
| query | `0x16994..0x169dc` | 72 | 26 | 5 |
| transfer leaf | `0x16896..0x168de` | 72 | 25 | 1 |
| 本階段五個本體 | | **572** | **205** | **30** |
| 重用並重新核對的 fill | `0x8520..0x85c8` | 168 | 55 | 19 |

APP 長度 76,800 bytes、base `0x8000`，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。每個本體的 SHA-256、所有指令 operands、邊界、可達局部節點與 backedges 均固定；也重算上游資料鏈與既有 SDK／candidate／sparse 覆蓋證據。沒有把候選 resident 當成 installed provider。

## 入口拒絕順序與 ambient A1

令 O 為入口 A0。依序判斷：

1. fresh `U8[O+11]` 必須為 1／2，否則返回 4；尚未讀 GP slot、配置或長度，沒有 frame stores。
2. fresh `U8[U32[GP+84]+4]` bit 3 設定則返回 4；尚未建立 frame 或讀長度。
3. 配置 64-byte frame、保存 RA／S0–S3，再讀初次長度 `L0=U8[O+2]`。L0>8 經 epilogue 返回 4；A5=4 由較早的配置路徑保留，沒有進 fill 或 copy。
4. L0=0..8 才建立封包。長度 0 仍會到 copy 呼叫點。

前階段 tagged 路徑可能帶進最早來源的 ambient A1；本體在第一個 A1 寫入之前沒有讀 A1，於 `0x16bc4` 明確設 A1=0，才呼叫 fill。故該舊 A1 不作第一個巢狀呼叫的明示來源參數。拒絕路徑可讓它保持原值；其他暫存器、先前逃逸別名或 provider 保存也沒有因此被抹除或排除。

## frame、fill11 與 copy 的精確位置

令 S 為新 SP，即 tagged 入口 SP−64。

| S 相對位置 | 本機內容／用途 |
|---|---|
| +12、+13、+14 | selector bytes `0x30,0x40,0x50` |
| +15 | 本段沒有初始化；send 起點在 +16，不包含此洞 |
| +16 | `low8(fresh U16[O] >> 3)` |
| +17 | `low8(fresh U16[O] << 5)`，與上一列使用同一次 ID load |
| +18..+28 | fill11 先由高位址往低位址清零 |
| +20 | fill 後寫入 L0 |
| +21 起 | 向 copy provider 提出的目的範圍，長度 L0 |
| +44、+48、+52、+56、+60 | 保存 S3／S2／S1／S0／RA 的 words |

`0x8520(S+18,0,11)` 的 computed target 為 `0x856a`，逐次 byte store 到 S+28、27、…、18，再 RET；此具體短路徑沒有 nested call 或 frame。完整 fill 本體也重新核對，包括其較長輸入的 bulk／prefix／computed-return 路徑，沒有將短路徑的暫存器非寫入推廣到所有輸入。

ID 在 fill 之後 fresh load。兩個輸出 ID bytes 只保留 ID 的低 11 bits；不宣稱保留整個 16-bit ID。之後 `0x16bf8` 以 `(A0=S+21,A1=O+3,A2=L0)` 呼叫 fresh `[0x4004c]`，scalar 回覆未測。實際複製／保存指標／其他記憶體效果仍未知。

只有實際 copy 符合參考合約、必要 context 與記憶體保存、有效且無不利別名等前提下，才能說本機 S+16..28 已有初始化來源，且 L0<=8 的 copy 不碰 selector 或保存暫存器範圍。這不是 provider 已被辨識或不會保存 O+3／S+21 的證據。

## 最多三個 selector 與重新讀取長度

copy 返回後才設 S1=0、S3=3。每次讀 fresh selector `U8[S+12+S1]`，並以 fresh tag 呼叫 query。回覆 bit 3 設定則 S1++，到 3 返回 4；否則使用該 selector，依序：

```text
send  (fresh tag, low8(selector+1), S+16, low8(fresh U8[O+2]+5))
update(fresh tag, selector, 8, 8)
query (fresh tag, selector)
```

最後 query 回覆與 `0x70` 相交非零則返回 4，否則返回 0。send／update 的回覆未用來判斷成功。每個 tag 也都有 fresh load，不能把入口已驗證為 1／2 自動套到後續每次呼叫。

selector、send buffer 與 loop 的界定依賴實際 copy 正常返回、必要 frame／S0 保存、有效 accesses 及沒有不利的 MMIO／frame 別名或 IRQ／writer 干擾。三個本機 wrappers 的所需保存已能由原指令與完整 leaf 界定，沒有單憑一般 C ABI 假設。

### 初次上限不等於後次長度上限

令後次 fresh 長度為 L1，send count `N=(L1+5)&255`。未另證物件保存時，L1 可與 L0 不同。全部 256 個 L1 的 footprint 均寫入 ledger；以下是純主機區間算術，不執行任何越界存取，也不證明這些長度實際可達。

| N 門檻 | send 讀 `[S+16,S+16+N)` 的區間關係 |
|---|---|
| N>=14 | 開始包含 S+29，超過本段 fill／header／參考 copy 所涵蓋的連續前綴 |
| N>=29 | 開始包含 S+44，進入保存 S3；更長時依序包含其餘保存 words |
| N>=49 | 開始包含 S+64，越過 tagged frame 上界 |
| L1=250 | N=255 |
| L1=251 | N=0，仍提出兩次 send 前綴傳輸，但不讀 buffer bytes |

「未由本段填入」不等於該記憶體必然未初始化、無效或為零。若 L1=L0 且 L0=0..8，則 N=5+L0，send 範圍恰為 S+16..S+20+L0，包含五個 header bytes 及本次 copy 的 L0 bytes；這是條件性穩定長度合約。

## 三個 wrappers 與完整 transfer leaf

三個 wrapper 均先按入口 tag bits 0／1 分別向 `0x40010814` 寫 word 16／1，正常末段向 `0x40010810` 寫 word 17。這是 numeric stores，不推定實體片選或裝置狀態。

| wrapper | 依序傳入 `0x16896` 的 A0 | 回覆處理 |
|---|---|---|
| query | `3, 保存的入口 A1, 0` | 第三次 A0 留至返回 |
| send | `2, 保存的入口 A1, 逐次 fresh buffer bytes` | 不依回覆中止 buffer 迴圈；保留末次回覆 |
| update | `5, 保存的入口 A1, 保存的入口 A2, 保存的入口 A3` | 第四次 A0 留至返回 |

send 的 32-byte frame 保存 caller S0／S1／RA，另存入口 A1；S0 成為 buffer cursor，S1 成為 end pointer，逐 byte 讀取並遞增 cursor。從 tagged caller 進來時，保存的 caller S0 正是 O，故原物件指標仍出現在巢狀 frame，不能說已全域抹除。query／update 的參數 reload 也依賴其 frame 沒有被不利寫入破壞。

完整 leaf `0x16896` 無 frame、callee 或 S／SP／GP／RA／A1 寫入，只改 A0／A3／A4／A5：

1. 以 byte counter 255 起，最多 255 次 fresh `U16[0x40013008]` bit 1 取樣；全未設就返回 0，沒有 DATA store／read。
2. 若 ready，寫入 `U16[0x4001300c]=low16(入口 A0)`。
3. 另設 counter 255，最多 255 次 fresh status bit 0 取樣；全未設返回 0，沒有 DATA read。
4. 若第二階段 ready，讀 `U16[0x4001300c]&255` 返回。

兩種逾時與正常讀到零都可能返回 0。因此 query bit 3 清零、最後 `reply&0x70==0` 或 tagged 返回 0，均不是實體傳送或 ACK 成功的證據。每次 fresh read 必須獨立，沒有主張硬體能產生任意取樣序列。

在穩定長度 L0=L1=L、前 k 個 selector busy、下一個可用，且所有相依 calls／accesses 正常完成的限定下，leaf 呼叫次數為 `17+L+3*k`（L=0..8、k=0..2）；全部三個 busy 則為 9 次。這只是已閉合本機軟體的呼叫計數。

## 重播與尚未解決的保存條件

```text
python analysis/check_v4160_tagged_dispatch_static.py
python -O analysis/check_v4160_tagged_dispatch_static.py
```

一般／`-O` 均重算並逐 byte 比對 ledger，驗證 65,536 組配置／初次長度、65,536 個 ID、2,304 組獨立 L0／L1、各 256 個 tag／status 分類、27 個穩定長度呼叫計數，以及 18 個指定原指令 mutation 的精確 operand guard。沒有執行先前 CPU／MMIO fixture。

下一步需追查 O+2／O+11 的 writers、後次長度與 tag 的實際可達來源、copy provider 的實際綁定與保存條件，以及更廣的物件／stack 保存期。主機端證據可以界定 numeric 操作和條件性 pointer flow，仍不能消除硬體副作用、並行 writer／IRQ 或 provider ownership 的未知。
