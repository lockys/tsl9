# task5 物件與 backing 配置來源：離線原指令驗證

接續 [物件移除、backing reset 與 ID 清理](v4160-task5-removal-static.zh-TW.md)，本階段補上 registry 物件的建立端，以及 B172 backing pointer 的來源與 descriptor 查找。分析目標仍是 ID-2966 V4.1.60 APP（76,800 bytes）；V1.31、V1.40 resident 只是附條件的候選參考，尚未證明為實際 installed provider。

| 完整函式 | V1.31 | V1.40 | 每份 bytes／指令 |
| --- | --- | --- | --- |
| descriptor lookup | `0x57862..0x578A4` | `0x579A2..0x579E4` | 66B／22i |
| backing initializer | `0x578A4..0x57962` | `0x579E4..0x57AA2` | 190B／66i |
| object creator | `0x57962..0x57A1E` | `0x57AA2..0x57B5E` | 188B／64i |

新增驗證合計 **888B／304 條指令**，由原始 sparse HEX 完整擷取並比對 candidate bytes。checker 固定每條 operand、函式 hash、所有 CFG 邊與呼叫目標。這是靜態合約驗證，沒有增加既有 C 重建覆蓋率。

以下 B=`0x200033B8`／`0x20003408`，C=`0x2000319C`／`0x200031EC`。registry 使用 head B156、tail B160、U16 count B180；本次 backing 在 **B172**，與 B164 的另一個物件指標欄位不同。

## 488-byte 物件與發布時機

creator 向 private core `0x20000040` 要求 `(488,611)`，將返回指標保存為 O，再以 fill `0x2000039C` 請求 `(O,0,488)`。fill 呼叫在 O 的 null check 之前。不過既有原指令 fill 合約先檢查 null destination，O=0 時不寫 destination；creator 隨後返回 0。fill 本身含 control-word 存取與 FENCE.I，這裡只核對其 bytes，沒有執行。

非零 O 在匹配的 allocator 合約與有效 heap header 等前提下，是原 core payload pointer；其清零範圍為 O..O+487。後續有兩種發布方式：

- captured head=0：設定 key=1、head=tail=O、count=1，**之後才呼叫 backing initializer**。不檢查初始化返回值，接著讀 fresh tail、寫 `tail.next=0`、清 O10／O14，最後讀 fresh U16[O8] 作為返回值。
- captured head 非零：從 key 1 起，逐一掃描所捕獲的鏈表，找第一個缺少的 key。以 fresh tail 接上 O，tail=O，將 fresh count+1 以 SH 寫回；再讀 fresh tail 並寫 next=0、清 O10／O14、讀回 key。此路徑沒有呼叫 backing initializer。

因此，非零 key 只證明走到建立端的相應返回路徑，**不能單獨證明 backing 已配置成功**。空鏈表路徑會先發布 O，初始化失敗也沒有本機 rollback。fresh tail 的兩個寫入位置都沒有 null guard；正確鏈表與保存期仍依賴欄位、配置及外部 writers 的證據。

### key 耗盡也有 release 後存取

接受的 key 為 1..32767。每次命中就增加 key，從 captured head 重掃；增加到 32768 時，左移 16 位後的 signed 判斷改走耗盡分支。此分支先寫 O8=0，呼叫 private release `0x20000110`，**返回後再讀 U16[O8]**。

這個順序由原指令確認，但尚不能稱為安全的 post-release access，也不能無條件宣稱返回 0。需要先證明 release 實際結果、該存取的 ownership／有效範圍、heap metadata 及其他 writers。這是與上一輪 remove 中「release 後寫 fresh tail」不同的另一個保存期界線。

key 增加有 32768 個純整數檢查；內層鏈表是否有限、捕獲 head 與 key 是否穩定仍是前提。CFG 邊的語法見證沒有被當作實際可達路徑證明。

## backing 大小：16 位截斷與 fresh count

initializer 先讀 B172。若已非零，直接返回當時入口 A0，沒有將既有 backing pointer 載入 A0。若為零，使用下列欄位計算請求：

```text
n = U8[C+95]                  // F=C+80，亦即 F+15
flag = U8[C+164]
h = U16[B+46]

D = n+1 if flag==0 else 2*n    // descriptor 數，0..510
K = D-n                       // 1 或 n
L = 16*D
R = (32*floor((h+33)/32)) & 0xFFFF
W = (L + R*K) & 0xFFFF

P = private_core(W,580)
```

R 等於將 h+2 向上對齊到 32 後再取低 16 位，所以不保證正數。W 已是 16 的倍數，既有 core 的四位元組對齊不會把它還原成截斷前大小。最大截斷前公式值是 16,711,680；傳入 core 的仍是 W。

完整 h 的 65,536 個值映射到 2,048 個 R。對所有 n、flag 的零／非零分類及不同 R，共核對 **1,048,576 組純算術組合**，其中 W=0 有 3,200 組，公式大於 65,535 有 526,219 組。這是值域分類，**不是實際設定分布、可達性或已確認記憶體錯誤**。

core 返回 0 時 initializer 返回 0。返回非零 P 時，它重新讀取 `fresh_n=U8[F+15]`，先發布 B172=P，才開始初始化 descriptor：

```text
payload_cursor = P+16*D
K_after = (D-fresh_n) mod 2^32
payload_rows = min(D,K_after)
```

前 payload_rows 筆寫 `row+4=payload_cursor`、`U16[row+10]=0xFF52`，並將 payload_cursor 增加 R；其餘筆寫 row+4=0、tag=0xFF54。全部筆寫 byte9=0。僅這些欄位有本機寫入，**其他 descriptor bytes 與 payload 內容沒有被此函式清零**。

若 fresh_n 大於 D，unsigned 減法會回繞，此時全部 D 筆均落入 payload 分支。若 fresh_n 保持原 n，payload_rows 才等於原本的 K。即使 W 未截斷，安全 extent 仍須另外滿足新舊欄位保存、配置成功、地址有效與非衝突別名等條件。

迴圈完成後 A0=`P+16*D`（mod 2^32），**返回的是 descriptor 區尾端，base P 保存在 B172**。creator 沒有使用這個返回值。B172 在 descriptor 尚未初始化前就已發布，沒有由這段原指令建立原子發布或同步保證。

## descriptor lookup 與 reset 的串接

lookup 從 fresh n／flag 重新計算 D，並從 B172 指向的區域每次增加 16 bytes，掃到 `P+16*D` 為止。找到第一筆 `U16[row+10]` 等於完整 requested A0，或等於 sentinel `0xFFFF`，就返回該 row；否則返回 0。

初始 tags `0xFF52`／`0xFF54` 並不等於 `0xFFFF`。requested A0 沒有先截成 U16；超過 65535 時，仍可能命中 sentinel 分支。lookup 沒有 backing null guard；D=0 時不讀 row。D<=510 與 16-byte 步距可證明算術上的有限掃描界線，仍須有效可讀記憶體及正常指令行為等前提。

lookup 的 fresh D 不保證等於配置當時 D。上一輪 reset 正是從 **B172** 取得指標並嘗試 release，再清該欄位，因此本次已接通 backing 的建立／查找／reset 來源。但沒有證明其他 writers、實際 provider 或 concurrent readers 的保存期。

registry 中的 O 可與原 488-byte 配置來源串接，但 remove 的 first-key-match 是否仍指向同一個 O，需要 key 唯一性、鏈表與 heap identity 的保存證據。既有 remove 與本次 key 耗盡分支的 release 後存取，均保留為未解合約。

## 驗證與範圍

[checker](check_v4160_task5_allocation_static.py) 與 [精確 ledger](v4160-task5-allocation-static.json)

```powershell
python -B analysis/check_v4160_task5_allocation_static.py
python -O -B analysis/check_v4160_task5_allocation_static.py
```

- 304 條新指令逐條變異拒絕，另有 12 個標準 unsigned load 改成 signed load 的專項變異。
- 完整 operand／hash、closed CFG、每條邊的語法見證、原 HEX bytes 與呼叫鏈核對；三個新函式的全部迴圈切邊後均為 DAG。
- 65,536 個 h、1,048,576 個請求組合、130,816 個 fresh-count 組合、32,768 個 key 增加值的 host 整數核對；沒有 mutable target memory／heap／鏈表模型。
- 重用既有 private core、fill、release 及上一輪 remove／reset 的原指令合約；一般與 `-O` 均要求 ledger 逐 byte 重現。

全程未執行或模擬韌體、target ISA、provider、callback、MMIO 或硬體。GitHub 僅發布這三份分析／驗證檔案。尚需追查設定欄位的實際 writers 與可達值、release 後 ownership、V34 下游、實際 installed provider 綁定及實機功能。這些靜態結果不代表完整可用韌體或功能驗收完成。
