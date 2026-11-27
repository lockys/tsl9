# V34 至 task6：task／record 來源與條件性 payload 清理

接續 [V34 下游與 word-copy](v4160-task5-v34-static.zh-TW.md)，本階段接通它的 outgoing task、record array 來源，以及下游 task6 handler／一般 message parser。新增兩個完整函式、兩份候選，共 **888B／334 條指令**；原 sparse HEX 完整覆蓋並與 candidate bytes 相符。

| 完整範圍，右端不含 | V1.31 | V1.40 | 每份 bytes／指令 |
| --- | --- | --- | --- |
| task6 handler | `0x4DBF2..0x4DCCC` | `0x4DC8A..0x4DD64` | 218B／76i |
| 一般 message parser | `0x4E1AE..0x4E290` | `0x4E246..0x4E328` | 226B／91i |

候選來源、欄位幾何及正常返回等前提仍必須成立，不能據此宣稱實機已使用這套 provider、訊息確實送達或 payload 保存期已閉合。C 重建覆蓋率不變。

## outgoing task 與兩個不同的 callback

V34 sender 的 fresh task byte `0x20003314`／`0x20003364`，正是既有 ID6 initializer `0x4DA70`／`0x4DB08` 在 +108 發布的欄位。initializer 先保存入口 A0，完成第一個 callee 後重新載入，再寫低 byte；它不使用該 callee 的返回值作為 task ID。

既有外層登記的條件性路徑提供 ID6、count7，對應 handler 就是本次 `0x4DBF2`／`0x4DC8A`。這和 initializer 尾段放入另一張 callback table 的 `0x4D916`／`0x4D9AE` **是不同入口**。

handler 處理 message event 時也從上述 task byte 重新讀取 ID，交給 receive `0x2000028C`；不是直接沿用 dispatcher 的入口 A0。因此 sender、receive、event repost 的欄位來源已接通，但仍須證明兩次 fresh 讀值保持、註冊表未被改寫、queue 接受及 dispatch 實際發生。

## record array 的配置與容量界線

同一 initializer 的 +308 發布 `0x20003318`／`0x20003368`，正是 V34 的 record array slot：

```text
g1 = first fresh U8 getter
P  = private_core(12*g1,0x4C06)
record_array_slot = P             // 在 null check、fill 之前發布
if P != 0:
    g2 = second fresh U8 getter
    fill(P,0,12*g2)
```

兩個 getter 都讀 `0x200033B4`／`0x20003404`，但中間有 allocator 呼叫，不能無條件令 g1=g2。以最低請求 extent `12*g1` 作界線時，`g2<=g1` 是 fill 長度足夠的條件之一，仍需要非零有效配置、正常 fill、無衝突 alias 等前提。P 也可能為零；先發布 pointer 不代表 array 已就緒或原子初始化。

getter 的 unsigned-byte 域給出請求 0..3060 bytes，沒有 U16 截斷或額外 rounding。若保留 resource writer 的 q，才可收緊至 q=0..66。既有 APP packed halfword `0x0E3F` 的高位 byte 提供 F+21=14；在 copy、fresh 設定及兩個 getter 都保留的來源案例下，q=g1=g2=5，record array 請求 **60 bytes／5 rows**。

resource pool 另有 `60*q` 的配置，同一來源案例是 **300 bytes**，存於另一個 slot。不能拿這份 pool 的大小作為 `12*q` record array 的 extent。

V34 的位移為 `12*((U16(I)-1)&0xFFFF)`。以已知最低請求範圍驗證完整 row 時，界線是 **1<=I<=g1**；I=0 會回繞到 index65535。registry key 存在不等於此條件成立，也不能依未證明的 allocator slack 放寬 array 容量。

## V34 的 `0xFF90` 走一般 parser

在 receive 返回有效非零 M、訊息內容保留與必要 code／frame／task 等前提下：

1. handler 檢查 byte M0 是否為 `0x90`；其他型別略過 parser，進入外層 message cleanup。
2. M0=`0x90` 時，檢查 byte M1 是否為 19（`0x13`）。
3. V34 寫入的 halfword `0xFF90` 對應 M0=`0x90`、M1=`0xFF`，因此選擇一般 parser `0x4E1AE`／`0x4E246`，不是內建的 status19 分支。
4. 一般 parser 正常返回後，handler 忽略其 scalar 回覆，將原本保存的 M 傳給 public cleanup `0x431BA`／`0x43246`。
5. handler 再返回完整 entry event word XOR `0x8000`，沒有把結果限位為 U16。

receive 返回 null 時，略過 message cleanup，但仍走該 event-word 返回路徑。所有「之後」均以先前 callee 正常返回且保存必要欄位為前提，不是實際執行證據。

## payload 清理與 message 本體清理是兩個呼叫

一般 parser 使用 48-byte frame，保存原 M 與 U16[M+2]。第一個 callee 是 decoder，參數為 `(SP+24,M)`。本階段只固定其入口與 call site，尚未閉合 decoder 寫入的 tuple；其後對 fresh SP+28、SP+24 等欄位的判斷仍取決於該 callee 與其他 writers。

parser 的 cleanup 區塊直接做：

```text
payload = fresh U32[original M+8]
if payload != 0:
    private_release(payload)       // 0x20000110；原指標不加減
ID_helper(saved U16[M+2],1)
```

傳給 private release 的是 **fresh 原 M8**，不是 decoder 輸出 SP+28。parser 沒有本機 M8 clear，其直接 stores 全部在自身 frame。完整 parser 本機 CFG 是 DAG；每版 52 條語法路徑中，23 條包含這個直接 private-release call，29 條不包含。這些數字不是實際執行頻率或可達性比例。

另有 forwarding 類分支：例如 routing code4 的 forwarder 返回 0，可以離開 parser 而不呼叫上述 private release。其他 case helpers／forwarders 仍未展開，不能只憑 call 名稱認定它們取得 ownership 或稍後會釋放 payload。

handler 正常返回鏈在 parser 之後另對原 M 做 public cleanup。既有 public wrapper 核對 message marker，再可能呼叫 private release；沒有遞迴釋放 M8 的本機合約。因此不能把外層 cleanup 當作 payload 已釋放的證據，也不能忽略 parser 內的條件性 payload cleanup。

V34 full-match 分支在保存條件下發布的 M8 是 P+2。這種 interior pointer 是否能被 private release 找到，需符合其 containing-header／extent／有效 heap metadata 等條件；不是將指標減 8 就得到 header，也沒有證明此時仍擁有該配置。

## handler 其他分支與精確存取範圍

bit15 優先於 bit0。沒有 bit15、但有 bit0 時，handler 呼叫尚未閉合的 pending wrapper `0x4E9CA`／`0x4EA62`。它返回非零，且另一次 fresh inline-counter byte 非零時，才 request event(fresh task,1)；然後返回完整 event word XOR1。兩個 handled bits 都沒有時直接返回 0，不是保留其他 event bits。

status19 分支使用另一個 byte `0x20002FA2`／`0x20002FF2`；它和 V34 tag `0x8001` 使用的 credit `0x20002FA4`／`0x20002FF4` 不同。

此分支先取 N=U8[M+2]、captured cap=U8[`0x200031FB`／`0x2000324B`]，然後 N 次讀取 **U8[M+6+2*i]**。步距是 2，但 load 寬度是 **1 byte**：

```text
next = min((previous + sampled_byte) & 0xFF, captured_cap)
```

先取低 byte 再選 min，不能替換成 saturating addition；例如 255+1 先回繞為 0。N=0 不寫 inline counter；N>0 在迴圈完成後寫最後值，再重新讀 counter 決定是否 repost event1。

在有效存取、無干擾等前提下，N<=255 提供最多255次的本機迴圈界線。N>0 的最高讀取位置為 M+(2*N+4)，故最低涵蓋 extent 為 `2*N+5` bytes，最大515；函式沒有本機 message-length 驗證。保持 `0xFF90` 的 V34 訊息不走此 status19 路徑，不能將兩種訊息布局混用。

## 驗證及尚未完成部分

[checker](check_v4160_task6_v34_consumer_static.py) 與 [精確 ledger](v4160-task6-v34-consumer-static.json)

```powershell
python -B analysis/check_v4160_task6_v34_consumer_static.py
python -O -B analysis/check_v4160_task6_v34_consumer_static.py
```

334 條新指令逐條變異、14 個標準 unsigned load 改變 type 的專項變異須被拒絕；核對完整 boundaries／hash／CFG、全部 call sites、兩版 parser 各52條 DAG 路徑、特定接收／cleanup／forwarding 路徑及原 HEX bytes。scalar 核對包括65,536個 event word、65,536個 byte 加法、130,816個 cap 組合、256個 count，以及327,680個 ID／capacity 組合。

完整 task6 handler／parser 不等於完整 nested-call closure。後續仍需展開132-byte decoder、56-byte bounds-adjust、case helpers／forwarders、pending wrapper，追查實際綁定、其他 writers、payload handoff 與 release 後保存期。既有 task／record producer、getter、receive、public／private cleanup 等合約重用，不重算為新增 bytes。

一般與 `-O` 須逐 byte 重現 ledger。全程僅離線 bytes、CFG、不可變路徑與 host 整數／區間等式；沒有 target register／RAM／heap／queue 模型，沒有執行或模擬韌體、provider、callback、MMIO 或硬體。GitHub 僅新增這三份分析／驗證檔案。
