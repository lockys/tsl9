# v4.1.60：JT2 零分支與全域等待旗標的寫入來源

這次封閉 JT2 callback 讀到 hook flag 為零時呼叫的完整 leaf，並把它對固定 B+124 的寫入，接到既有 callback 的 exact-4／bit5 等待。這裡的「零分支」是入口擷取的 flag 值，不是 packet、callback pointer 或來源長度為零。

[驗證程式](check_v4160_b1_irq_zero_static.py)與 [JSON ledger](v4160-b1-irq-zero-static.json)只核對原始 bytes、逐指令 operands、strict sparse HEX、不可變 CFG 與 host 欄位算術。沒有執行或模擬目標 ISA、RAM、packet、MMIO、trap、callback、provider 或裝置。

| 候選 | FLASH 完整半開區間 | 條件性 RAM 座標 | bytes／指令 |
|---|---|---|---:|
| V131 | `[0x42bfe,0x42dbc)` | `[0x2000298e,0x20002b4c)` | 446／158 |
| V140 | `[0x42c8a,0x42e48)` | `[0x200029da,0x20002b98)` | 446／158 |

新增原指令驗證合計 **892 bytes、316 條指令**。每份恰好終止在上輪非零 leaf 的入口之前；兩個本體分開核對，沒有將相鄰視為 fall-through。重驗非零 leaf 共520 bytes，以及下述完整 dispatch 本體2,218 bytes與兩張 table共104 bytes，均不重複計為新增。這是 resident 參考候選的條件性合約，實際 installed provider 及既有 C 重建覆蓋率沒有因此獲得新證明。

## 入口、獨立讀取與 metadata 計數

V131 令 S=`0x20003514`、B=`0x200033b8`、M=`0x2000319c`；V140 三者各加80。入口從 S+40 的 slot 擷取 H 到 A5，整個本體不再重新讀該 slot。需要 R 時，從 S−12 的 slot讀取；H／R 都沒有本機 null／extent guard。

先讀 fresh U32[H+12]，其 bit14 設定時才讀另一個 fresh U32[H+8] 的 bit14。兩次皆設定才依序：

1. 向 H+104 寫 word `ffffffff`。
2. fresh 讀 U32[M+28]，加1後以低32位寫回。
3. 向 H+8 寫 word16384。

V131 計數 word 位於 `0x200031b8`，V140 位於 `0x20003208`。這是普通 load／add／store，沒有本機原子操作；不命名其物理事件，也不宣稱沒有其他 writers 或更新遺失。

全函式共有 **9個 H+8 load sites**：+0x12、+0x32、+0x54、+0x6e、+0x76、+0x8a、+0xd0、+0xfe、+0x122。不是每條路徑都會執行全部位置，各次也不能合成同一快照；H+8 stores 不提供後續 readback 的硬體語義。

## 接收旗標與 P+1 分類

- fresh H+8 bit3 設定：對 fresh S+2 OR1，S+4=128，再向 H+8 寫8。
- 另一 fresh H+8 bit0 設定：對 fresh S+1 OR1，再向 H+8 寫1。
- 後面的 fresh bit2，或僅在其為零時另一 fresh bit1，決定是否進入中段並清 S+5。
- 中段再讀 fresh H+8 bit2：為零時對 fresh S+3 OR1、向 H+8 寫2，再將 fresh R+44 word 的低2位改為1。

中段 bit2 為1時，才讀 fresh R+0 bits12..13。非零選代碼108；為零才讀 fresh H+80 bit5與 `P=fresh U32[S+36]`，接著讀 `U8[P+1]`：

| H+80 bit5 | P+1 byte | 寫入 H+28 的代碼 |
|---|---|---:|
| 1 | 0 | 93 |
| 1 | 1..255 | 107 |
| 0 | 0／1／2／3 | 93／97／101／105 |
| 0 | 4..255 | 107 |

代碼路徑依序寫 H+28、對 fresh S+0 OR1、寫 H+8=4，再更新 fresh R+44 低2位為1。數值關係與上輪非零 leaf 相同，但本次是另一個完整函式與另一組 fresh observations。

P+1 只是分類 operand，沒有長度比較、P null guard 或來源 extent 驗證。該直接讀取需要至少2個可讀 bytes；這不提供後續 completion 所需27-byte extent。函式沒有以 P 作基址的本機 store，仍未找到實際填入 packet bytes 的 producer；H／R 的動態別名與裝置副作用也仍未封閉。

## 固定 B+124／B+125 的新增寫入者

這裡 B 是指令直接形成的固定全域基址，不是從 list 載入的動態 N。不能因 offset124／125相同，就把 B 欄位與 N 欄位視為同一物件。

fresh H+8 bit12 設定時，執行 B+124 區段：

1. 先讀 B+124 bit4。設定時，**另讀一次** B+124，OR32後寫回。
2. bit4未設定時，另讀 fresh B+124 low nibble。等於2就寫整個 byte為4。
3. 若不是2，再讀另一 fresh B+124 low nibble。等於3也寫整個 byte為4，否則本機不寫 B+124。
4. 所有進入這個 bit12 區段的路徑，都會向 H+8 寫4096。

因此 `B+124=4` 是整個 byte 的覆寫，並不保存先前高位旗標。OR32 的來源則不是最初 bit4 判斷所用的 snapshot。

fresh H+8 bit13 設定時，讀 fresh signed byte S+4；負值才寫 S+4=1，然後向 H+8 寫8192。先前可能寫入的128可以在這裡變成1，不能把它當成全函式不變量。

最後 fresh H+8 bit15 設定時，執行 B+125 區段：

- 第一個 fresh B+125 bit0 設定：另讀 fresh B+125，OR2後寫回。
- 第一個 bit0未設定：另讀 fresh B+125 bit2；若設定，再讀一次 fresh B+125，OR8後寫回。
- 其餘路徑不寫 B+125；所有進入 bit15 區段的路徑都向 H+8 寫32768。

上述是具體 stores 與條件，尚未賦予它們協定狀態、完成通知或硬體 acknowledgement 的含義。

## 接通 B+124 的兩種等待

重驗既有完整 dispatch callback `0x55480..0x558a8`／`0x5555e..0x559e0` 及各自完整13-entry table。其 operands、CFG reaching definitions 證明下列等待使用固定 B，而不是通知路徑中重新定義過的另一個 S1 基址：

| 既有等待 | 讀取條件 | 本次找到的相容寫入 |
|---|---|---|
| case95，+0x5a／+0x5e | fresh B+124 恰等於4才離開等待 | leaf 的 literal4 store |
| +0x3d2／+0x3d6／+0x3da | fresh B+124 bit5設定才離開等待 | leaf 的 OR32 store |
| +0x2ba／+0x2be／+0x2c2（V140各+2） | 同樣等待 bit5 | leaf 的 OR32 store |

**這兩種條件不同：literal4會清掉 bit5；OR32 的結果必定不等於4。** 這關閉了特定欄位的條件性 writer／reader 對應，沒有證明同一次 IRQ 會使所有 waits 進展。

需要實際 provider／code／table綁定、真實派送順序、正常讀寫、指令存取範圍有效及中途沒有其他覆寫，才能把某次 store 的值帶到 waiter 的某次 fresh load。先前完整 dispatch 仍有多個 polling／redispatch cycles，沒有因此得到有限返回或 timeout 保證。B+125 的實際消費端普查也尚未完成。

## JT2 零分支的普通返回界線

重用完整 JT2 callback：它先讀 flag並清零；入口擷取值為零時，將 caller RA存到 frame+120，linked-call 本次 leaf，返回後從 frame+120 載回 RA，再普通 RET。這條路不是非零分支的 gateway／MRET 路。

Leaf 有21個 store sites，僅定義 A0..A5，沒有 local call、frame、CSR 指令，也沒有 SP／RA／GP／S registers 的本機定義；唯一 RET 位於+0x14c。它沒有固定scalar回覆，不能把正常返回當成成功狀態。

如果 caller frame、globals、H／R／P extent有效，動態 stores 不別名 frame，且沒有物理副作用／IRQ／DMA／其他 writers干擾，才可延伸 caller RA與其他必要保存條件。沒有實際 context-entry或trap交付證據，也沒有因此證明 callback相對外層 C+12清零的順序、polling進展或完整物件保存期。

## 重播

每版完整158條指令、11個 typed loads、10個 QingKe byte encodings、21個 stores及全部 GPR定義都被核對。每版13,680條不可變局部CFG路徑皆到唯一RET；ledger保留整組路徑摘要及72個代表見證，沒有將語法路徑宣稱為實際裝置可達軌跡。

驗證包括65,536個位元投影cases、65,536組獨立fresh nibble cases與完整byte域的OR／分類關係；拒絕 **316個指令與22個typed-load mutation**。一般與`-O`模式需逐byte重放同一JSON，並重驗完整上游證據鏈。

```powershell
python analysis/check_v4160_b1_irq_zero_static.py
python -O analysis/check_v4160_b1_irq_zero_static.py
```

剩餘工作是實際packet內容producer／ingress長度／初始化條件、B+124／B+125的其他writers與消費端、provider與trap派送順序，以及完整ownership與指標保存期。
