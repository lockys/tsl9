# code4 路由至 task8：type A0 消費、release flag 與 status19

接續 [task6 decoder／forwarder](v4160-task6-decoder-forward-static.zh-TW.md)，本階段接通 code4 的條件性目的 task，並補齊 task8 的 type `0xA0` handler 與其 payload decoder。兩候選合計 **904B／334 條指令**，所有新增 bytes 均由原 sparse HEX 完整覆蓋，與 candidate bytes 相符。這不是實際 installed provider、送達或 ownership 的證明，C 重建覆蓋率不變。

| 完整函式，右端不含 | V1.31 | V1.40 | 每份 bytes／指令 |
| --- | --- | --- | --- |
| task8 handler | `0x4A808..0x4A940` | `0x4A8A0..0x4A9D8` | 312B／111i |
| task8 payload decoder | `0x4469E..0x4472A` | `0x44732..0x447BE` | 140B／56i |

兩份函式的本機 CFG 均為 DAG，backward address jumps 沒有形成本機迴圈；callee 正常返回仍是前提。

## 路由來源：code4 → task8，code6 是另一條路

既有 44-byte selector 位於 `0x4D9EC`／`0x4DA84`。ID8 initializer 保存入口 task ID，返回後重新載入，以完整常數 A1=4 呼叫 selector。對應的 routing row0 位於 `0x20003320`／`0x20003370`，先寫 task byte+2，再寫 gate halfword+0。

在既有選定註冊、frame、table、欄位及正常返回等保存條件成立時：

- code4：row0 gate=4、task=8，對應 task handler `0x4A808`／`0x4A8A0`。
- code6：另一個 initializer 提供 row2 gate=6、task=9，對應 `0x502B4`／`0x5034E`，本次未展開該 consumer。
- code7：只有在初始 48-byte clear 完成，且除已知 row0／1／2 寫入外沒有其他 writer 的附加條件下，才能保留 row3 gate=0 的結論。

selector 的一般介面有重要界線：guard 檢查 low16(code−4)，index 乘12卻使用完整 RV32 差值。不能將所有通過 guard 的一般輸入都限制在48-byte table內；本次 row 範圍結論只套用已固定的常數4／5／6等呼叫域。task byte 與 gate 是分開寫入，沒有原子發布或一致快照證明。

task8 handler 的 receive 又 fresh 讀取獨立保存的 ID byte `0x200033AD`／`0x200033FD`。它同樣源於 initializer 保存的入口 ID，但 sender 的 routing task 與 receiver 的 ID 仍需要跨時序保存，不能僅憑兩處都曾寫8就宣稱實際 dispatch。

## Handler 的事件與釋放順序

令 E 為完整 entry A1。此 handler 只處理 bit15：沒有該 bit 就返回0；有 bit15時保存完整 E，向既有 receive 取一筆訊息。

- receive 返回 null：返回 E XOR `0x8000`。
- 非零訊息 M 的 byte0 不是 `0xA0`：略過本次 decoder，嘗試 public message cleanup，再返回 E XOR `0x8000`。
- type A0：**先將自身 SP+11 的 release flag 寫成1**，再呼叫 decoder(M,SP+20)，將 decoder 的 scalar 回覆保存為 R。

decoder 的非零回覆會略過 tuple opcode／flag 解讀，直接走共用 release-flag 檢查。回覆0時才依 fresh tuple opcode／flag 選擇 callback、report helper 或直接走共用區塊。

共用 payload cleanup 為：

```text
if fresh U8[SP+11] != 0:
    P = fresh U32[original M+8]
    if P != 0:
        private_release(P)        // 0x20000110，原指標不加減
```

這是對原 message pointer 欄位的 fresh 讀取，不是使用 decoder 輸出的 body pointer。release scalar 結果沒有被檢查，實際 ownership／header／extent 仍未證明。

## Callback 可以改寫 release flag

兩個間接 callback 來源 word 分別為 `0x20002F6C`／`0x20002FBC`，以及 `0x20002F70`／`0x20002FC0`。本機給它們的參數形狀為：

```text
(fresh U16[M+2], &tuple_at_SP20, &release_flag_at_SP11)
```

它們可以透過傳入位址改變 flag／tuple；保存的 R 也可能改為 callback 回覆。因而入口 flag=1 不能無條件延伸到 callback 後。必要的 S registers、SP、RA 與 saved slots 保存，和明確允許修改的 flag／tuple，是不同的合約。

opcode 的初始分類使用 decoded low6 值：固定 mask `0x14300001` 在0..28域選到0、20、21、26、28；另有31..63範圍。其他路徑還區分奇偶、fresh callback word 與 tuple flag。這些分類不代表 callbacks 已安裝或一定被呼叫。

相關 report helper `0x448CC`／`0x44960`、ID helper `0x4D962`／`0x4D9FA` 及 callback 本體尚未封閉；不替它們指定產品用途或 payload 保存行為。

## R=19 是不同的退出合約

在會呼叫 ID helper 的共用後段，handler 檢查所保存的 R。**R=19 時直接進 epilogue，略過 public message cleanup，也略過 event-bit XOR，返回原完整 E。** 其他相應路徑才 cleanup 原 M，並返回 E XOR `0x8000`。

R 是 handler 保存的 decoder／callback 回覆，不是 tuple 的 status byte。已展開的 decoder 正常回覆僅0／1，另有本機缺 callback 時的6；在必要 callee 保存條件下，19仍須來自 callback 等待釐清的合約。

payload cleanup 的檢查位於 R=19 分支之前。因此 status19 路徑可以略過 message cleanup，但先前仍可能已嘗試 private payload release。不能宣稱所有非零訊息都會被釋放，也不能由 event 未清除推論 M 仍在 queue、已由某處安全保存或可再次使用。

## Payload decoder：一個前綴 byte，可能再排除12個尾端 bytes

decoder 捕獲 U16[M+6] 為 L。L=0 直接返回1，不寫 output。L>0 時取 P=U32[M+8] 並讀第一個 byte b，沒有新的 payload null／extent guard。

| 條件 | body length | tuple status | scalar 回覆 | 寫 output |
| --- | --- | --- | --- | --- |
| L=0 | — | — | 1 | 否 |
| b bit7=0，L>0 | L−1 | 0 | 0 | 是 |
| b bit7=1，L<=12 | — | — | 1 | 否 |
| b bit7=1，L>12，aux 回零 | L−13 | 1 | 0 | 是 |
| b bit7=1，L>12，aux 回非零 | L−13 | 2 | b bit6 | 是 |

extended 路徑的 auxiliary callee 是 `0x50160`／`0x501FA`，版本差不能一律平移152。其參數為：

```text
(fresh U16[M+2], 1, P, L−12, (P+L−12) mod 2^32)
```

該 helper 的副作用、讀取範圍與用途仍未閉合。本輪只證明其回覆被轉成零／非零，再形成 status1／2；不把該回覆直接當成 decoder 回覆。

成功形成 tuple 時，本機寫入：

| Output offset | 寫入 |
| --- | --- |
| byte0 | status |
| byte1 | b bit6 |
| byte2 | b & 63，即內層 opcode |
| halfword4 | body length |
| word8 | body length非零時 P+1，否則0 |

bytes3、6、7沒有本機寫入。對 extended 路徑，body pointer 仍是 **P+1**，並不是 P+13；其長度排除一個 prefix byte 及12個 trailing bytes。L=13時 body length=0，body pointer被寫零。

routing code4 和這裡的內層 opcode 不同：前者來自先前8-byte tuple的 code，決定目的 task；後者是 payload 第一個 byte 的 low6，不能因 code4 就假定 opcode=4。

前輪條件性 layout 的 message M8 可能為原配置 base+6；本次 body pointer 因而可能為 base+7。但 private cleanup 仍傳送 fresh 原 M8，沒有改用 body pointer，也不代表 exact base 或目前 ownership。

## 部分初始化與借用保存期

handler 使用48-byte frame，saved slots 位於+32..47；release flag在+11，decoder output在+20..31，兩者均避開 saved slots。decoder 使用32-byte child frame，其 saved slots也與 caller output區間分離。這些是已固定指令的相對區間證據，實體 alias、外部 writer 與 callback 仍需保存前提。

decoder 的早期拒絕不寫 output；caller 的非零回覆分支會先略過 tuple 解讀。另一方面，status2且 bit6=1時，decoder雖返回1，output其實已寫入，不能將「非零回覆」統一解釋成未產出 tuple。

傳給 callback 的 SP+11／SP+20 都是 caller frame 內的借用位址，本輪沒有證明 callback 不會保存它們。完整 payload lifetime、status19、message retention與實際 provider綁定仍未閉合。

## 驗證

[checker](check_v4160_task8_typea0_static.py) 與 [精確 ledger](v4160-task8-typea0-static.json)

```powershell
python -B analysis/check_v4160_task8_typea0_static.py
python -O -B analysis/check_v4160_task8_typea0_static.py
```

334條新指令逐條變異、24個標準 load-type 變異、兩個將 event XOR 改為 OR 的案例均須拒絕。本檢查器的靜態 decoder 補上標準 RV32 XOR operand 解碼，與原 bytes／獨立反組譯相符，並核對32,768組 register-field encoding vectors；沒有執行任何 target instruction。

完整 operands、hash、CFG、call sites、DAG路徑及 releaseflag／status19選定路徑均固定；scalar核對完整 event／length halfword域、512個 first-byte／aux-result組合、opcode分類、route範圍與 frame區間。既有 selector、initializer、receive、public／private cleanup重用，不重算新增 bytes。

一般與 `-O` 須逐 byte 重現 ledger。全程離線 bytes／CFG／不可變路徑與 host整數等式，沒有 target register／RAM／heap／queue模型，沒有執行韌體、callback、provider、MMIO或硬體。GitHub僅新增本輪三份分析／驗證檔案。
