# task6 decoder、指標區間檢查與 tuple 轉送

接續 [V34 至 task6 的條件性清理](v4160-task6-v34-consumer-static.zh-TW.md)，本階段封閉 decoder、type validator、bounds-adjust 與 forwarder 的完整本機合約。兩候選合計 **660B／250 條指令**，原 sparse HEX 完整覆蓋並與 candidate bytes 相符。這是附條件的 reference 證據，尚未證明實際 installed provider、訊息送達或 payload ownership；C 重建覆蓋率不變。

| 完整函式，右端不含 | V1.31 | V1.40 | 每份 bytes／指令 |
| --- | --- | --- | --- |
| decoder | `0x4DED0..0x4DF54` | `0x4DF68..0x4DFEC` | 132B／52i |
| type validator | `0x4D5A0..0x4D5D0` | `0x4D638..0x4D668` | 48B／17i |
| bounds-adjust FLASH source | `0x40454..0x4048C` | `0x40494..0x404CC` | 56B／17i |
| bounds-adjust RAM target | `0x200001E4..0x2000021C` | 同左 | 條件性 source mapping |
| forwarder | `0x4E290..0x4E2EE` | `0x4E328..0x4E386` | 94B／39i |

## decoder：先清 pointer 欄位，失敗不寫兩個 halfwords

decoder 入口為 `(out,M)`，out 指向 8-byte tuple。第一條指令就是 `SW0[out+4]`，早於任何 message 驗證；out 本身沒有 null guard。

其順序為：

1. 要求 U8[M+4]=2、U16[M+6]>3，否則返回 1。
2. 取 sampled P0=U32[M+8]，先讀前兩個 payload bytes 形成 K，檢查完整等式 `K+4 == sampled U16[M+6]`；只有相等才讀接下來兩個 bytes 形成 code。沒有 payload null／extent guard，也沒有原子快照保證。
3. code=4..7 直接接受；其他 code 要求 type validator(code) 返回非零。
4. 成功分支**重新讀取 fresh P1=U32[M+8]**，之後才寫 out+2=K、out+0=code，呼叫 bounds-adjust(P1,−4)，將回覆寫到 out+4，返回 0。

因此 K、code 源自 P0，輸出 pointer 卻使用 P1。兩份指標與內容是否相同，需要保存證據，不能只因欄位地址相同就合併。

| Tuple 欄位 | 成功路徑 | 拒絕路徑的本機寫入 |
| --- | --- | --- |
| U16 out+0 | code | 不寫入 |
| U16 out+2 | K | 不寫入 |
| word out+4 | bounds-adjust 回覆 | 保持入口所寫的零 |

decoder 不檢查 bounds-adjust 是返回新指標、原指標或零；完成該呼叫後一律返回 0。不能把 0 解讀成指標已成功調整。

在 out、frame、message、payload、heap 等必要區間分離且無外部干擾的前提下，本次兩個 read-only callees 不會修改 M8；這提供有限的本機保存合約，並不取代實際 pointer／code／provider 的保存證據。

## type validator：另一份 16-byte array

type validator 捕獲 unsigned count byte `0x20002FA0`／`0x20002FF0` 與 array pointer `0x20002F98`／`0x20002FE8`，以 16-byte 步距掃描。每次 fresh 讀 U16[row+2]，只有非零且等於完整輸入 code 時，返回 row pointer；掃完 count 筆則返回零。

它沒有 store、call、frame、null／extent guard，最多255次讀取的界線仍以有效正常存取及必要暫存器保持為前提。零 tag 永遠不命中；若 match 的 row address 為零，回覆仍是零，不能忽略實際配置與非零地址條件。

這份 array 是既有 initializer 的 `16*count`、tag `0x4C05` 來源。它與 V34 的 **12-byte record array、tag `0x4C06`、slot `0x20003318`／`0x20003368` 不同**，也與 inline counter byte 不同。其他 code 的實際登錄與 row writers 尚待追查；本輪沒有假設任何 code 已登錄。

## bounds-adjust：減去 delta，並檢查兩個端點

helper 的核心算術是：

```text
candidate = (original - entry_delta) mod 2^32
```

所以 decoder 傳入 delta=`0xFFFFFFFC`（−4）時，candidate 是 **original+4**。checker 另將原 SUB 改成 ADD 作為錯誤符號案例，兩候選都必須拒絕。

helper 捕獲 head、sentinel，逐筆讀 next header。它只有在某次讀到的同一個 header 區間同時符合下列 unsigned 比較時，才返回 candidate：

```text
payload_start = (H+8) mod 2^32
payload_start <= original  < next
payload_start <= candidate < next
```

若正常掃到 sentinel 而沒有通過，就返回 original。candidate 先被放入 A0 但之後檢查失敗的路徑，會在正常耗盡時重新載回 original，不能把中途 A0 的值當作最終回覆。

這個 helper 沒有 store、call、frame，也不搬移 bytes、不 free、不改 tag。它沒有檢查 allocated／free 狀態、exact allocation base、剩餘長度或 ownership；兩個 pointer 都在區間裡，也不代表後續整段 body 都在區間裡。header list 是否有限、next 是否有效、H+8 是否沒有回繞及 actual heap 是否保持，仍需另外證明。

## 與 V34 的 P+2／P+6 幾何串接

上一輪 V34 full-match 的條件性配置形狀為：copy 從 base P 開始，message M8 在保存條件下為 P+2。若 decoder 的 fresh M8 仍為此值，且 bounds-adjust 接受該調整：

```text
原 M8            = P+2
decoded pointer  = P+6
decoded length K = L-4
```

對目前 table0 提供 byte L 的 exact-match 域 4..255，共252個值，純區間等式得到：

```text
body end offset = 6+(L-4) = L+2
L+2 <= 4*floor((L+5)/4) = copied bytes
```

所以此限定域的 body 幾何可落在 copy 所涵蓋的 bytes 內。這仍以指標保持、正常且有效配置／copy、區間不衝突與調整真的通過等前提為條件，不是一般 U16 長度 ABI 的安全證明。前輪完整長度域的 rounding 回繞限制仍保留。

原 M8 與 decoded pointer 是不同欄位。父 parser 的 payload cleanup 仍重新讀取並傳送**原 M8**給 private release，而不是用 decoded pointer 替換它。

## forwarder：複製 tuple，建立 type `0xA0` 訊息

入口為 `(target_task,ID,tuple_pointer)`。forwarder 向既有 message allocator 要求 12 bytes；返回 null 就回覆 1。非零新訊息 Q 的內容為：

```text
U16[Q+0] = 0x00A0
U16[Q+2] = low16(ID)

tuple_pointer != 0:
    byte_copy(Q+4,tuple_pointer,8)
else:
    fill(Q+4,0,8)

sender(saved_target_task,Q)
return 0                       // sender scalar reply 被忽略
```

這個 copy8 將 code、decoded length、pointer word 放到 Q+4、Q+6、Q+8。它保存的是 tuple 內的 **pointer 值**，沒有直接把 caller 的 tuple stack address 保存到 message；也沒有複製 payload 本體或增加 reference count。

父 parser 的 tuple 位於自身 48-byte frame 的 +24..31，與 parent saved registers、decoder／forwarder 的 32-byte child-frame saves 區間分離。這只封閉相應 frame offset 的幾何，不證明 message、heap、實體 alias 或非同步存取有效。

新訊息 type 是 `0xA0`，與原 `0xFF90` 不同。target task 來自父 parser routing row 的 fresh byte；實際 destination、接受、消費及 payload release 尚未閉合。即使 sender 拒絕並嘗試清理 Q，forwarder 仍返回 0，因此不能以此認定 payload 已有接手者。

## 返回父 parser 的界線

在相同 tuple、正常 frame／code 存取與無干擾等前提下，decoder 的拒絕結果是 `(reply=1,out4=0)`；父 parser 會轉入前輪已驗證的條件性 cleanup：若 fresh 原 M8 非零，就嘗試 private release，之後外層才可能清理原訊息本體。

decoder 成功但 out4=0 時，不能強行當作有效解碼指標。父 parser 的 zero-output 分支與 forwarding 分支不同，仍必須沿原指令判斷。

成功 forwarding 返回 0 的分支可以使父 parser 略過直接 payload release；forwarder 配置失敗回 1 則可導向 cleanup。這些分支尚未證明真正的 ownership transfer。其他 parser case helpers、forwarded-message consumer、pending wrapper 與動態 row writers 仍是後續工作。

## 驗證

[checker](check_v4160_task6_decoder_forward_static.py) 與 [精確 ledger](v4160-task6-decoder-forward-static.json)

```powershell
python -B analysis/check_v4160_task6_decoder_forward_static.py
python -O -B analysis/check_v4160_task6_decoder_forward_static.py
```

250條指令逐條變異、10個標準 load-type 變異，以及兩個錯誤符號案例須被拒絕；固定全部 operands、hash、完整 CFG、callee targets、decoder／forwarder DAG 路徑與 bounds-adjust 不可變路徑見證。scalar 核對涵蓋完整 code／size halfword 域、pointer subtraction／interval、252個 V34 限定長度及 nested-frame 區間。

既有 message allocator、byte-copy、fill、sender、initializer 與父 parser 合約重用，不重算為新增 bytes。一般與 `-O` 須逐 byte 重現 ledger。沒有 target register／RAM／heap／queue 模型，沒有執行或模擬韌體、provider、callback、MMIO 或硬體。GitHub 僅新增本輪三份分析／驗證檔案。
