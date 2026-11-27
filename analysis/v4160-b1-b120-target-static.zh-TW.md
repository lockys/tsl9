# v4.1.60：B+120 完整目標、B+125 等待與返回合約

本次把上一階段 B+120 publisher 的數值目標接到完整函式，封閉三處固定 B+125 bit1 等待、各自的重新讀取／清除，以及兩種普通返回。也固定了算術、callback 與私有服務的呼叫實參；未知callee的行為繼續保留為邊界。

[驗證程式](check_v4160_b1_b120_target_static.py)與 [JSON ledger](v4160-b1-b120-target-static.json)只解析原始bytes、完整operands、strict sparse HEX、不可變CFG與host整數關係。沒有執行或模擬目標ISA、clock、RAM、MMIO、callback、provider、packet或裝置。

| resident參考候選 | 完整半開區間 | bytes／指令 |
|---|---|---:|
| V131 | `[0x5d5c4,0x5d9ac)` | 1,000／307 |
| V140 | `[0x5d70c,0x5daf4)` | 1,000／307 |

新增原指令驗證共 **2,000 bytes、614條指令**。兩個完整本體都結束於上一階段parser入口之前，不將相鄰本體合併。原始publisher、dispatch、IRQ零分支及22-byte setter重驗後重用，不重複計入新增。既有C重建覆蓋率不變；實際installed provider也尚未證明。

每版完整307條指令、40個standard typed loads、9個QingKe窄存取、62個loads及35個stores均固定。35個stores包含6個frame saves與29個非frame位置。全部21個call sites都有link，沒有本機external tail。

## B+120 的來源與兩種返回

V131固定 B=`0x200033b8`，V140 B=`0x20003408`。完整publisher寫入 B+120的值，恰為本次兩個入口；完整dispatch則fresh讀B+120並以已擷取N作A0間接呼叫，沒有null guard。Encoded reaching definitions核對該讀取仍使用形成B的定義；中途callee保存及真實publication順序仍需前提。

本體先讀入口N+124 byte，沒有先檢查N本身：

- **讀到0：** 直接跳至+0x3e6普通RET，不建立frame、不呼叫子函式、沒有data stores。本機A0保持入口N；不能把這條路當成固定返回0。
- **非0：** 建立32-byte frame，保存RA、S0..S4。所有21個call sites及正常RET都被這組frame保存位置支配。

正常返回共用+0x12a..+0x142尾段：fresh讀U16[N+136]，加1後寫回低16位，恢復frame，普通RET。65535會回繞到0；它不是已證明單調遞增的全域事件計數。A0保持當時路徑留下的值，沒有共同success常數。

## 可選初始化與後續獨立觀察

入口擷取的N+124恰為18，且兩次fresh U16[N+130]與U16[N+136]相等時，才依序：

1. 請求copy `(N+160,0x200034be／0x2000350e,5)`。
2. 呼叫`0x57ad8／0x57c18(N+160)`。
3. 把回覆低8位寫N+129，並寫N+124=4。

隨後呼叫RAM `0x200017d6(N)`及`0x63eda／0x63fc4(2)`，再fresh讀N+172與N+124。較早寫入的4不能取代這次獨立觀察，更不能只靠局部store排除後面的N+124==3分支。

完整本體直接存取N需要至少 **176 bytes**，包含word N+172；copy request需要N+160..164可寫。實際allocation extent、copy完成、private callee副作用及物件保存期仍未閉合。

## 三處 B+125 bit1 等待與重新讀取後的清除

下列offset相對各自1,000-byte入口，兩版一致：

| 位置 | 等待fresh byte的bit1 | 等待離開後另讀byte | 清除store |
|---|---|---|---|
| 第一條N+124==3路徑 | +0x92 | +0x9a | +0xa2 |
| 另一條N+124==3路徑 | +0x296 | +0x29e | +0x2a6 |
| 後段自行arming路徑 | +0x3a2 | +0x3aa | +0x3b4 |

每個wait都是LBU、AND2、BEQZ回到LBU的三指令cycle。離開後重新讀同一固定B+125，再AND252寫回，清掉這個**後來snapshot**的bits0／1並保存其餘observed bits；不是直接清除等待時擷取的byte，也不是原子消費。

完整IRQ零分支的OR2 store已重驗，地址與這三處fixed B+125相同。這關閉了位元相容的writer／reader對應。要使某次wait實際看見某次IRQ store，仍需要真實綁定、派送、正常存取與中途保存證據；沒有timeout或有限polling進展保證。

第三條路徑先對fresh B+125 OR1，在算術／動態H相關操作後才進入wait；OR1設定的是bit0，本機沒有因此先設定bit1。IRQ裡的OR8則設定bit3，不是這三個wait的直接退出條件。

固定B+125和動態 **N+125的地址**分開處理。本體兩處將N+125作A3傳給另一個服務，沒有就地把它當成上述全域旗標，也未證明N與B的物件身分或非別名。

## Clock pointer：四次使用擷取值，五次fresh載入

在主要分支前，從固定slot `0x200031e0／0x20003230`讀function pointer到A3。原指令reaching definitions證明+0xa6、+0x152、+0x2aa、+0x314的間接call使用這個擷取值。這些call sites沒有自行重新讀slot，也沒有null guard。

另外五個call sites，則各由自己的fresh slot load供應A5：+0x20e、+0x216、+0x224、+0x31c、+0x32e。兩處獨立三指令cycle反覆載入／呼叫clock，直到回覆與先前保存的fullword不相等：

```text
+0x212 → +0x216 → +0x218 → 相等時回+0x212
+0x318 → +0x31c → +0x31e → 相等時回+0x318
```

這些是scalar比較，沒有已證明的單位、monotonicity、更新來源或等待上限。call可能回覆變化、一直相等或不正常返回，均不由局部CFG替裝置決定。跨callee的S registers、SP、RA與saved frame保存也是合約前提。

## 整數算式與尚未套用的算術helper合約

多處以U16[N+134]與fresh或保存的U16 scale相乘，加400，unsigned DIVU 800。在這兩個乘數確實保持U16來源的前提下：

```text
q = floor((a*b+400)/800), a,b ∈ [0,65535]
0 ≤ q ≤ 5,368,545
65535²+400 < 2³²
```

因此這個參數域的乘積加400不會溢出U32。後續word相加與條件性減去fresh modulus-like word，是原指令的低32位關係；缺少有效範圍與循環不變量時，不能直接命名為一般modulo或實際時間。

兩處linked call `0x6df1a／0x6e10a`之前，MUL／MULHU把U32 scalar D乘1,000,000的low／high words放A0／A1，A2是U16來源K，A3=0。乘積小於2^52，但 **K>0沒有本機guard**。

先前這個helper的config-specific算術證明使用另一個參數域，不能套用到這裡的fullword分子或K=0情況。本次只固定實參構造與呼叫後`low32(2*A0)`寫向H+108，不宣稱helper回覆公式、physical timing或硬體已完成操作。

## 其他發布、borrowed pointers與CPU stores

本體兩處以RAM setter `0x2000078a`發布literal **`0x5c9b4／0x5cafc`**；完整22-byte setter與first-copy映射已重驗。它發布的值不同於前幾階段的completion `0x65de6／0x65ed0`。部分路徑先寫S+7=11，但仍未證明後續callback交付、flag保存或執行順序。

兩處向`0x43414／0x434a0`傳入本體literal、N、當時算出的A2及N+125地址。尚未證明這個服務的保存／借用合約或是否保存指標。另有`0x57ad8／0x57c18`、RAM `0x200017d6`、`0x43ed2／0x43f5e`與`0x5d006／0x5d14e`等callee，其reply與副作用沒有由函式名稱推定。

N+148／N+152的word stores在本體中用作scalar算術結果，不被本機解參考成packet目的地。另一處fresh N+172指標會被用來寫+9／+10，所需動態範圍至少11 bytes；它不是先前nonnull觀察自動保證仍相同的指標。

有一個固定CPU地址word-store：`[0xe000e204]=0x02000000`。這裡只固定原始地址與資料，不推定實際interrupt routing或裝置副作用。其餘動態H stores也保留各次pointer來源，不能合併成同一硬體snapshot。

本體沒有直接讀S+36或N+80來取得packet buffer；copy至N+160與經N+172的writes也沒有已證明的物件等同性。資料內容producer、ingress長度、指標ownership／保存期仍待釐清。

## 重播

每版CFG完整涵蓋307個nodes、336個edges；所有edges都有可重建的語法入口至返回見證。精確五個cyclic SCC，分別是三個B+125 waits及兩個clock-equality waits，每組3個nodes。這些見證不證明輸入可行性、callee返回、async交付或有限進展。

檢查614個逐指令變異與80個typed-load變異全部被拒絕；另核對256個mask bytes、65,536個U16 counter值、327,680組U16乘數cases及fullword乘積邊界。一般與`-O`模式需逐byte重放同一JSON，並重新驗證完整上游證據鏈。

```powershell
python analysis/check_v4160_b1_b120_target_static.py
python -O analysis/check_v4160_b1_b120_target_static.py
```

接續優先展開私有callee、`0x5c9b4／0x5cafc` callback及本輪算術helper實參域。實際provider綁定、派送順序、資料來源與長度、完整物件保存期仍未完成。
