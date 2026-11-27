# task5 V34 下游：訊息建立、分段記錄與 word-copy 原指令合約

接續 [table0／cleanup](v4160-task5-object-static.zh-TW.md) 與 [APP 配置來源](v4160-task5-config-provenance-static.zh-TW.md)，本階段補齊 V34 adapter 尾跳後的兩個候選函式，並驗證它使用的 word-copy helper。

| 完整函式 | V1.31 | V1.40 | 每份 bytes／指令 |
| --- | --- | --- | --- |
| V34 target | `0x530FE..0x5334A` | `0x531A6..0x533F8` | 588B／207i；594B／209i |
| word-copy 的 FLASH source | `0x405DC..0x4060C` | `0x4061C..0x4064C` | 48B／16i |
| word-copy 的條件性 RAM target | `0x2000036C..0x2000039C` | 同左 | 兩來源 bytes 相同 |

按兩個來源 profile 計數，新增完整原指令驗證 **1,278B／448i**。兩份 V34 本機 CFG 均為 DAG，各有 20／21 條語法路徑；word-copy 有一個計數迴圈。所有新增 bytes 均與原 sparse HEX 擷取內容相符。這些是候選 reference 的靜態證據，尚未證明實際 installed provider；C 重建覆蓋率不變。

## 入口、版本差異與返回值

以下命名僅供資料流描述：I=entry A0，mode=entry A1，L=entry A2，S=entry A3。一般 ABI 的 L 是完整 RV32 值，不能整體當成 unsigned byte。

既有 table0 呼叫鏈則提供：

```text
I    = fresh U16[O+8]
mode = fresh U8[node+8]
L    = fresh U8[node+12]
S    = (sampled U32[node+4] + 2) mod 2^32
```

兩版先判斷 mode==2。V1.31 將其他 mode 全部送入記錄延續路徑；V1.40 只接受 mode==1 進入該路徑，其他 mode 返回 **255**。

V1.40 的新增 BNE 位於 `0x53312`（entry+`0x16C`），原 bytes 為 `e390f5f0`。獨立拆解 B-immediate 得位移 **−256**，目標為 `0x53212`（entry+`0x6C`），先執行 `ADDI S1,x0,255`；之後才進入 entry+`0x70` 的 epilogue。checker 另將跳轉改成略過該賦值的 +`0x70` 作為專項錯誤案例，必須拒絕。

正常返回與 callee 保存等前提下，完整本機返回類別均是 **0、1、2、4、255**。其主要來源如下：

| 返回值 | 本機分支來源 |
| --- | --- |
| 2 | mode2 的 fresh credit byte 為零 |
| 4 | mode2 的 payload header 超過相應 signed 比較界線 |
| 255 | 特定長度不符、message／payload 路徑未取得所測指標，或 V1.40 不支援的 mode |
| 1 | 延續路徑長度為零，或 signed 容量比較失敗後的清理路徑 |
| 0 | 已複製、仍未組完、嘗試送出，甚至完成時 message 配置失敗後的清理路徑 |

因此不能把 0 當作「已成功送達」。語法路徑列舉也不代表每一條都實際可達，或巢狀 callee 必然返回。

## mode2：先讀 header，再決定配置／複製路徑

第一個 fresh credit byte 來源為 `0x20002FA4`／`0x20002FF4`。為零就返回 2，尚未讀 payload；否則先讀 S 與 S+1 的兩個 bytes，形成 little-endian K，再讀 U16 maximum M=`0x200031FC`／`0x2000324C`。這兩個 payload bytes 的存取發生在 L 的檢查之前，來源範圍必須另外有效。

比較為 signed `K >= M-3`，成立時返回 4。M 為 U16，故 M<=3 時沒有被接受的 K；M>=4 時接受 K<=M−4。不能將函式內其他含 RV32 加減的 signed 判斷任意改成 unsigned 長度檢查。

### K 恰為 L−4：建立 12-byte 訊息並使用 word-copy

此路徑呼叫 message allocator `0x20000236`，要求 12 bytes。非零訊息指標記為 Q：

```text
U16[Q+0] = 0xFF90
U16[Q+2] = low16(I)
U8 [Q+4] = 2
U16[Q+6] = low16(L)

P = private_core(low16(L)+5,0x8001)
U32[Q+8] = P
```

message 返回 null 時返回 255。payload core 直接返回 null 時，嘗試 private release(Q)，再返回 255；這只是 cleanup attempt，不是釋放成功的證明。

P 非零時，重新讀取 credit 並減一，以 byte 寫回。接著呼叫：

```text
word_copy(P,(S-2) mod 2^32,(low16(L)+5)>>2)
Q8_fresh = U32[Q+8]
U32[Q+8] = (Q8_fresh+2) mod 2^32
sender(fresh outgoing_task,Q)
return 0                     // sender scalar reply 未被檢查
```

這裡保存的是 **fresh Q8+2**，不是 word-copy 返回的 advanced A0。只有 Q8 在 copy 後保留 P，才能把它寫成 P+2。

table0 傳入的 S 原本就是 sampled node4+2，word-copy 使用 S−2，算術上會回到 sampled node4。這只接通指標位移，沒有證明該 base 的配置來源、alignment、extent 或保存期。

### K 不等於 L−4：使用索引記錄

若 signed `K < L-3` 就返回 255；否則使用索引記錄。record byte10 非零且 word0 非零時，先對舊 payload 嘗試 private release，再要求 `core(low16(K+4),0x8001)`。

此處有重要的 fresh-pointer 界線：**core 前捕獲的 array base 用來寫入返回指標，但分支測試使用 core 後重新讀取的 array base。** 因此，所測 record pointer 為零不等於直接測 core 返回值；兩份 base 的身分與內容保持，才可進一步推論同一筆配置結果。

被測 fresh record pointer 非零時，設 record byte10=1、重新讀 credit 後減一，呼叫 byte-copy(ptr,S,L)。之後再讀 record array，寫 record6=low16(L)、record4=K，返回 0。這些 fresh reads 不自動構成同一份 snapshot。

## word-copy 的長度單位與配置界線

新 helper 先讀 `0x4002420C`、寫零並含 FENCE.I，之後才檢查 destination、source 及 count。三者任一為零時不搬資料；正常離開時恢復 control word。這裡僅核對原指令，沒有執行 control／MMIO。

非零輸入時，它每次做一個 **4-byte LW／SW**，source、destination 各增加 4，count 減一。正常完成 N 次後：

```text
A0 = destination + 4*N        // mod 2^32
A1 = source + 4*N             // mod 2^32
A2 = 0
```

沒有 frame、nested call、S-register 或 RA 寫入。它是 forward word-copy，沒有 alignment、extent、overlap 或 address-wrap 檢查，也不是 memmove／原子快照。

令 l=low16(L)。V34 的實際 copy 與既有 core 的 rounding 為：

```text
N = (l+5)>>2
copied_bytes = 4*N = roundup4(l+2)
core_rounded = ((l+8)&0xFFFF)&0xFFFC
```

copy 從 S−2 開始，最多還需讀取 S+L 之後的 3 bytes。完整 65,536 個 l 的算術分類顯示：**l=65528..65535 時，core rounding 小於 copy extent**；不能只因 core 返回非零，就推論其範圍足夠。這是一般輸入域的合約缺口，不是實際可達錯誤或可利用性結論。

目前 table0 提供 byte L；exact-match 路徑可收斂為 4..255，此域沒有上述 rounding 回繞。若上一輪 APP maximum=251 的來源又保持至這次 fresh M 讀取，則進一步有 K<=247、L<=251，最大 copy extent 為 256 bytes。這個附加來源保存條件仍未無條件封閉。

## 記錄延續、送出與保存期

record array pointer 來源為 fresh U32[`0x20003318`／`0x20003368`]，索引位移為：

```text
offset = 12*((I-1)&0xFFFF)
```

沒有本機 key／array extent／null-array guard。I=0 會得到 index=65535；不能將 registry key 的存在直接當成此 array 的容量證明。

延續路徑先讀 record6=current、record0=buffer。current 為零或 signed 容量比較失敗時，走 optional release／clear record0，再清 fresh record6／byte10，返回 1。

其他情況先 byte-copy(buffer+current,S,L)，再讀 fresh record length，將 low16(fresh current+L) 寫回。未等於 fresh record4+4 時返回 0；相等時建立上述 12-byte 訊息，將**既有 record payload pointer**放入 Q8，嘗試 sender，然後清 fresh record6／byte10、返回 0。此送出分支沒有清 record0，因此仍需處理保存的 pointer alias 與 ownership。

若完成時 message allocator 返回 null，函式會嘗試清理 record payload、清長度／flag，仍返回 0。各 release 的 scalar 結果均未檢查。

outgoing task byte 是 `0x20003314`／`0x20003364`，與先前 builder 的 task source 不同，實際綁定仍待追查。既有 sender 可能拒絕訊息並嘗試 cleanup；V34 忽略 sender 返回值。private release 不會遞迴釋放 Q8 指向的 payload。故返回 0、credit 更新或 message pointer 發布，都不能單獨證明送達、ownership transfer、無遺留配置或 payload 保存期。

credit byte 也與 private release 對 tag `0x8001` 的條件性 increment 對上；V34 在特定 payload 路徑 decrement。checker 只驗證 modulo256 的數值反向關係，沒有建立全域可用數量不變式，也沒有假設實際 release 成功或沒有其他 writers。

## 驗證與後續

[checker](check_v4160_task5_v34_static.py) 與 [精確 ledger](v4160-task5-v34-static.json)

```powershell
python -B analysis/check_v4160_task5_v34_static.py
python -O -B analysis/check_v4160_task5_v34_static.py
```

448 條新指令逐條變異、44 個標準 load type 變異，以及 V1.40 錯誤 epilogue 目標案例均須被拒絕。核對完整 CFG、20／21 條 DAG 語法路徑、每條 CFG 邊、全部 nested targets，以及 65,536 個 length／maximum／ID 的 scalar 域。message allocator、private core、private release、byte-copy、sender 與 table0 均重用既有原指令合約，不重算為新增 bytes。

一般與 `-O` 須逐 byte 重現 ledger。沒有 mutable target register／RAM／heap／queue 模型，沒有執行或模擬韌體、provider、callback、MMIO 或硬體。GitHub 僅發布這三份分析／驗證檔案。後續仍需追查 record／task／credit 寫入者、下游訊息消費及 payload release、實際 provider 綁定與實機進展。
