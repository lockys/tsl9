# v4.1.60：完整 record callback 與 TX buffer 組裝來源

這次封閉上輪發布的`0x5c9b4／0x5cafc`，接通其實際物件來源、TX buffer stores、copy實參、傳輸服務邊界與返回流程。也定位到來源word為零時的copy略過路徑，以及通知暫存區的一個本機初始化缺口；兩者都保留runtime前提，不推論實機錯誤已發生。

[驗證程式](check_v4160_b1_record_callback_static.py)與 [JSON ledger](v4160-b1-record-callback-static.json)核對完整原始bytes、逐指令operands、strict sparse HEX、不可變CFG與host整數／區間關係。沒有執行或模擬目標ISA、RAM、packet、clock、MMIO、callback、provider或裝置。

| resident參考候選 | 完整半開區間 | bytes／指令 |
|---|---|---:|
| V131 | `[0x5c9b4,0x5d006)` | 1,618／542 |
| V140 | `[0x5cafc,0x5d14e)` | 1,618／542 |

新增原指令驗證合計 **3,236 bytes、1,084條指令**。每版有153個loads、102個stores、25個linked calls，唯一普通RET位於+0x54，沒有external tail。完整身分、版本差異、91個standard typed loads與63個QingKe窄存取都固定，包含兩個原生stack-byte stores。既有C重建覆蓋率不變；參考resident的實際installed身分仍未證明。

## Callback 值的來源與實際 N

完整上游B+120目標中，兩個setter call傳入的literal恰為本次完整入口。完整22-byte setter與48-byte consumer仍被重驗：前者發布hook word，後者擷取word後間接呼叫。這是條件性綁定鏈，沒有證明實際callback曾交付、slot未被替換或trap時序成立。

令V131的S=`0x20003514`、B=`0x200033b8`；V140兩者各加80。Callback建立64-byte frame，保存RA、S0..S8；**不將入口A0當成物件來源**。

先擷取U32[S+24]，以其bit15分支，並從S+40 slot擷取一個H pointer：

- bit15清除：讀H+108。非零則向hook flag `0x20002efc／0x20002f4c`寫1，隨後共同恢復frame／RET。
- bit15設定：從fresh U32[B+88]取得N，沒有N null guard；寫H+100=160，再從N+172取得child。

完整IRQ狀態leaf先前對S+24寫入一個擷取的H+8 word，本次也重驗該store。只有實際路由、mapping、provider與保存條件成立，才能把這個來源連到callback入口；S+24的bit15不是此處fresh讀取的H+8 bit15。

## Child、選定record及動態範圍

令R為最初擷取的child，入口選取：

```text
J = low32(fresh U32[R+12] + 16*captured U8[R+9])
```

J+2、J+1等欄位可決定前段對H+8／H+108的寫入。索引是byte，16-byte stride的最大名義表格範圍是4,096 bytes；但沒有把索引與真實allocation或當時record count連接，因此這個數值界線不是已驗證的array extent。

本體多次重新讀N+172、N+76等word，不能將它們自動等同於先前擷取的R或目的buffer。Encoded reaching definitions另核對所有以S0作基址的明示N存取仍使用+0x5e的N定義；稍後S0被改用作scalar時，沒有把它繼續當成N。

## 條件性固定欄位路徑：36-byte目的範圍

一組gates會檢查另一個fresh N+172所指byte+3是否為1，以及保存R的byte+9與獨立N+176來源的byte+1是否相等。通過後，以+0x13a讀到的N+76保存在S1，以下稱T；以N+176讀到的來源稱Q。

這組gates沒有來源pointer null guard，也不證明兩次child相等。需要有效N／R／Q／T與callee保存條件，才能延伸以下來源合約：

| 目的範圍 | 原指令來源／請求 |
|---|---|
| T+0 | 初始5；依N+53 bit0或N+52==2可改69，再依Q+3的另一次觀察OR128 |
| T+1 | 34 |
| T+2..7 | `copy(T+2,N+54,6)` |
| T+8..13 | `copy(T+8,Q+4,6)` |
| T+14..17 | fresh Q+24..27 bytes |
| T+18..20 | 從Q+20擷取word的低24位分拆 |
| T+21 | N+128==2時3，否則2 |
| T+22..23 | 兩個U16來源平均後的縮放／clamp結果，原始operands固定於ledger |
| T+24..29 | 平均值bytes與Q+14..17的獨立byte／word觀察 |
| T+30..34 | fresh B+262..266 bytes |
| T+35 | 先寫fresh Q+28低5位 |

其後另fresh讀N+76，對該pointer的+35讀取並OR入fresh B+3左移5的低byte。只有再證明這次pointer仍等於T、內容與callee狀態保存，才可把這個額外RMW併入同一目的record。

在matching copy helper、有效來源／目的範圍、正常完成、所需非重疊／別名與保存條件下，direct stores加兩個6-byte copy請求涵蓋T+0..35。這不直接證明來源bytes已初始化、整份record曾一次可見或實際硬體已送出。Q的明示來源範圍最多需要29 bytes。

## 一般record路徑：獨立來源、可選欄位及copy長度

另一條路徑從已選J擷取：

```text
source = U32[J+8]
L = U8[J+3]
```

以保存的T寫header7、初始header-count byte1及flags byte0。依N的獨立flags／欄位觀察，可能加入欄位、要求其他callee、增加count；多個stores則使用重新讀取的N+76目的pointer。

其中一組gate對fresh U8[N+124]計算`(byte−16)&255`，僅0／1進入可選區段。它在fresh N+76加`3+fresh U8[T+2]`處形成9-byte區段：直接寫8、40，請求從固定來源copy5，再寫兩個來源counter bytes。Copy之後還fresh重讀N+124；不能把它與最初的16／17 gate視為同一snapshot。

可選payload copy的實參為：

```text
copy(fresh U32[N+76] + 3 + fresh U8[T+2], captured source, captured L)
```

**source word為零時跳過copy，但接下來的長度算術仍使用L。** 本機沒有在這個分支證明L必為零，也未證明略過區域已有其他writer填好。這是初始化／內容證據的待查界線，不是已觀察到的資料外洩或傳輸錯誤。

來源L及count observation各為byte；這個copy callsite單獨的數值目的end envelope為`3+255+255=513`。它不證明這個組合實際可達、不提供allocation extent，也不能替代中途callee與source／pointer保存限制。

之後以另一次fresh h=U8[T+2]形成：

```text
published = low8(captured L + (h&63) + 1)
N+17 = published
byte[fresh U32[N+76]+1] = published
```

這個byte可回繞；它與copy callsite先前觀察的count可能不同。不能用最終length byte反推所有bytes已形成或曾在有效範圍內複製。

## 傳輸邊界：H+112 存的是 pointer

原指令將fresh N+76寫向fresh H+112，再以A0=0、fresh U8[N+128]及fresh U8[N+17]請求RAM `0x200026ba／0x20002706`。第四實參是當時live register，本階段不任意指定為0。

H+112寫入的是指標word。這些CPU stores與服務請求未證明實際provider接受、傳輸完成或buffer保存至非同步消費結束。此目的來源是N+76；先前parser的資料來源是N+80，兩個word及其資料流等同性仍需另證。

## Polling、hook 及返回

完整CFG有三個cyclic SCC：

- +0x54c／+0x54e：fresh H pointer／word+108反覆觀察，沒有本機timeout。
- +0x57c／+0x580／+0x582：fresh clock slot、間接call與fullword相等比較，沒有clock更新或進展保證。
- +0x640／+0x64a／+0x64e／+0x650：以下有限本機計數迴圈。

兩個間接call sites +0x2e6／+0x38a使用同一個從context word0擷取的function pointer；另外三個使用各自fresh clock-slot loads。它們不是五次相同的fresh observation。

本體可發布RAM callback `0x20001dd4`、以0清hook slot，或再次發布自身literal。Setter的null路徑沒有本機清flag，也不提供取消、排除重入或pointer lifetime保證。

所有本機returns都經同一64-byte frame恢復，沒有共同scalar回覆。Child與provider是否普通返回、保存S registers／SP／RA及frame，仍是跨callee前提。

## 釋放請求、相同地址清零與部分stack輸入

尾段先讀U32[child table+8]；非零時把擷取pointer傳入private `0x20000110`。返回後重新讀child table pointer與byte count，不能沿用釋放前的pointer身分或有效性，也不把請求本身當作已證明free。

隨後的counter從0遞增到擷取的U8 count，最多255次；每次store都寫**同一個保存的table+8地址**為零，沒有按index移動pointer。此局部有限界線以store正常完成、counter／callee／context保存為前提，不替整個callback的其他polling提供進展保證。

另一條通知路徑形成A0=SP+12並呼叫`0x52d80／0x52e28`。完整本機store清單只寫入：

| stack位置 | 本機來源 |
|---|---|
| SP+13 | 保存N的byte+8 |
| SP+14 | 0 |
| SP+15 | fresh N+172所指byte+4 |

**整個函式沒有明示寫SP+12。** 這三個bytes與saved frame words SP+24..63分離，但不足以證明callee所需完整輸入已形成；也不能由本機缺少store推定runtime byte必定未初始化。Callee讀取extent、先前寫入來源、是否保存stack pointer及source／frame lifetime仍待查。

## 驗證及後續

每版542個nodes與577個edges均有可重建的入口／出口語法見證。固定所有loads／stores／calls、來源register definitions、QingKe stack bytes與三個SCC；拒絕 **1,084個指令變異、182個typed-load變異**。

host檢查包括byte索引／stride、255次有限counter域、65,536組header／length scalar關係及U16 counter回繞。一般與`-O`模式需逐byte重放同一JSON，並重新驗證上游完整證據鏈。

```powershell
python analysis/check_v4160_b1_record_callback_static.py
python -O analysis/check_v4160_b1_record_callback_static.py
```

後續需展開私有callee、通知callee與SP+12來源，確認record／payload真正的來源保存條件。實際RX內容、ingress長度、TX provider與交付、pointer相等性、ownership及完整保存期仍未完成。
