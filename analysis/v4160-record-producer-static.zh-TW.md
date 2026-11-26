# v4.1.60：record 建立端、獨立 node 與先串接後初始化

日期：2026-11-26。承接 [兩種內建 record handlers](v4160-builtin-record-handlers-static.zh-TW.md)，追查第一組16筆record的建立端。[檢查器](check_v4160_record_producer_static.py)／[ledger](v4160-record-producer-static.json) 固定兩版本完整指令、條件性CFG、所有stores、呼叫參數與消費端對應。

**此函式先找callback word為零的record，再另外配置16-byte node；node先串入鏈表，之後才初始化欄位、寫record及可選輸出index。** record第三個word來自入口A4，與node+4同源，可在額外保存條件下接到literal0的fresh flag判斷。未證實際provider、計時單位、事件送達或atomic registration。

僅離線讀檔、解碼、靜態圖與主機代數，沒有執行或模擬target ISA、allocator、node list、arena、callback、provider或MMIO。C重建覆蓋率不變，原BIN與既有分析未改寫。

## 完整本體與參數命名

| 候選 | range（終點不含） | bytes／instructions | SHA-256 |
| --- | --- | --- | --- |
| V1.31 | `43414..43520` | 268／97 | `29d76ad5a42d8e18963f91612f71693c26830228176b6efa20d7e017173262fd` |
| V1.40 | `434a0..435ac` | 268／97 | `ead8c94e325f34c8ebbe837ba926b2d170ca2e4433d79e34c73a8ff42011aeed` |

合計 **536 bytes／194 instructions／52個靜態store位置**。所有97條／版本均有獨立opcode／operand／target guards，另核對完整hash、兩個SCC、GPR writes與restore cut set。沿用固定APP／carrier／SDK header、LLVM來源hash／Git blobs與28 vectors的條件性ISA解讀；`3aa1`依該profile解作SH至node+2，不採用一般disassembler的FSD顯示。

以下只按編碼命名入口參數，不補未證的API型別或物理單位：

| 入口register | 保存register | 寫入用途 |
| --- | --- | --- |
| A0 | S3 | record+0 callback word |
| A1 | S6 | record+4 argument word |
| A2 | S7 | node+8 word |
| A3 | S4 | 可選U8輸出index的pointer |
| A4 | S5 | node+4與record+8 word |

這些S值均跨過未知callee／allocation；能否保持入口值仍需保存條件。

## globals與前置呼叫

| 角色 | V1.31 | V1.40 |
| --- | --- | --- |
| metadata M | `2000319c` | `200031ec` |
| 前置provider pointer M+68 | `200031e0` | `20003230` |
| node list head M+76 | `200031e8` | `20003238` |
| arena pointer slot M+144 | `2000322c` | `2000327c` |
| fallback pointer M+132（config+52） | `20003220` | `20003270` |

入口一律先建立48-byte frame，保存RA／S0..S8，讀控制word `4002420c` 至S1、寫零、FENCE.I，才判斷完整A0是否為零。A0=0正常續行會恢復控制word並回覆2；不是沒有MMIO前置存取的純參數檢查。

A0非零時，保存A0..A4後，直接呼叫fresh U32[M+68]，**沒有本機null guard**。A0..A4仍是原入口值，其他ambient registers也可被觀察。正常返回後的scalar A0沒有本機consumer；函式重新讀arena pointer並建立scan常數。provider的記憶體、副作用、保存與返回仍未證，不能只因這個scalar reply被忽略就略去該call。

## 先掃16個callback word，再配置16-byte node

arena base只在scan前fresh讀一次，記P0。index i由0至15，依序讀 `U32[P0+12*i]`：

- 非零：i加一，繼續。
- 零：停止scan，準備配置；不讀該record的+4／+8作空槽判斷。
- 16次分開的讀取均觀察到非零：正常回覆8。這不是同一時刻整個arena的snapshot。

scan迴圈中沒有call，SCC為相對入口offsets `106,110,114,116,250,252`。索引、base、code與存取有效的前提下，至多16次scan讀取；不代表其他callee或append loop也必然終止。

找到空callback word後，AUIPC/JALR數值target為 **`20000040`**，參數：

```text
A0=16
A1=ff00
A2=0             # 剛才讀出的空callback word
A3=12            # stride常數
A4=P0
A5=16            # scan bound
```

這不是message allocation wrapper。沿用完整core合約，request rounding R=16、選small head、low16 tag=ff00；在fit且header有效的條件下B>24才split。非零回覆Q也不自動證明合法16-byte extent、ownership或與arena／frame不重疊。

### allocation失敗與兩個不同fallback邊

core回覆零後，producer再fresh讀M+132。非零才以A0=4、A1=0呼叫，其他register是core返回後的live值。**其scalar reply不作配置結果，也不重試配置；正常續行恢復控制word、回覆11。**

core本身另有sentinel失敗callback：若search抵達sentinel且當時fallback word非零，以A0=1、A1=`0010ff00`、A2=0呼叫，正常失敗路徑仍強制回覆零。producer隨後可能再讀同一storage slot並呼叫4／0。兩次是不同時間的fresh reads，不能宣稱一定呼叫兩次、pointer相同或fallback能補出成功Q。

## Q與arena record的角色不同

Q來自本次16-byte配置；arena base由另一個global pointer slot載入。兩種來源／用途不同，仍不構成runtime nonalias證明。

Q非零時fresh讀list head。head為零就先寫head=Q；否則沿每個node的+12讀next，找到零next後先寫tail.next=Q。append SCC為相對offsets `240,242,244`；沒有iteration bound、cycle guard或pointer有效性檢查。穩定cycle可能不返回。

兩種link stores都位於共享初始化區段之前。沒有callee替它們完成初始化，也不能把前置控制word操作擅自當成已證互斥或atomic publication。

### 原指令初始化順序

1. `U8[Q+0]=0`。
2. fresh讀arena pointer得P1。
3. 計算one-hot `1<<i`。
4. `U32[Q+12]=0`。
5. `U32[Q+8]=saved entry A2`。
6. `U16[Q+2]=low16(1<<i)`。
7. `U32[Q+4]=saved entry A4`。
8. 依序向 `P1+12*i` 的+0／+4／+8寫saved entry A0／A1／A4。
9. 若then-live S4非零，以SB將low8(i)存至該pointer。
10. 恢復控制word，A0=0，恢復frame並RET。

node的明示field coverage為15個bytes，**byte1沒有直接node欄位store**；未宣稱實際byte1必定未寫或為非零，因為allocator、舊內容、alias與外部writer另有條件。對i=0..15，one-hot可完整放入U16、輸出index可完整放入U8；這不保證output pointer有效。

找到空槽使用P0，真正寫record卻使用core返回後的fresh P1，**沒有再次檢查目的record是否仍空**。所以scan與write不能無條件視為同一筆、同一時刻的record狀態。

## 接回literal0消費者

producer相對arena只使用offset `12*i`，即名義第一組16筆／192 bytes。literal0消費者則以 `12*(16*g+k)` 選record；只有g=0、i=k、producer／consumer所讀base相同且context／內容保持等條件下，兩者才對上。

producer把entry A4同時寫到node+4與record+8。literal0在callback後fresh讀的是 **P′+12*k+8，沒有group項**；在上述對應與保存條件下，該word為零才清selected record的+0／+4，非零保留。它不清+8，也不在這裡釋放Q或arena。

這是欄位來源關係，不等於已證A4的計時／週期單位，也不證明node+2 mask已被送入handler。node-list消費者、producer的實際callers、其他group建立端與event delivery仍需追查。

## 正常status與保存界線

| 正常回覆A0 | 本機路徑 |
| --- | --- |
| 2 | 入口callback word為零，經控制word前置／恢復路徑 |
| 8 | 16次分開的scan讀取皆非零 |
| 11 | core回零，optional fallback正常續行後仍失敗返回 |
| 0 | link、node／record stores、optional output store及恢復路徑完成 |

所有本機RET路徑都必經四個控制word restore位置之一；checker用靜態圖cut set核對。epilogue不再改A0。這只證明編碼中的restore／status順序，不能把0當成事件已送達、ownership有效或硬體同步完成的收據。

unknown provider、core與fallback的正常返回及S／SP／saved frame保存，valid／nonaliasing Q、list、arena、globals、frame、output，以及無外部干擾都是條件。append終止性沒有由16-slot scan上界推出。

## 重播與實際輸出

```text
python analysis/check_v4160_record_producer_static.py
python -O analysis/check_v4160_record_producer_static.py
```

兩模式均實際輸出：

```text
PASS: 16 node-mask/group cases; 65520 split-gap identities; node byte1 exclusion; 12 specified raw mutations
PASS: 2 complete producers, 536 bytes/194 instructions/52 stores; node/arena distinction; link-before-initialization
PASS: exact ledger replay; status/consumer edges conditional; provider/ownership/delivery UNPROVED; NO target execution
```

cases為主機one-hot／field widths、第一組offsets、U16 fit-size域與split門檻代數，不建立或走訪target list／records。十二個raw mutations改callback gate、scan bound／read、allocation request、fallback load／status、head store、SH offset、node來源word、record stores及tail.next store，均要求命中特定semantic guard；不以全檔hash不符或任意exception當成通過。

預設只讀重算並精確比對JSON；`--write`只建立不存在的ledger。重播需十五個已發布Python dependency模組，本機固定APP、兩份carrier、SDK header與LLVM來源／vectors；candidate輸入未隨本次發布，僅clone repo不足以重跑。

後續仍需沿producer callers、linked-node消費與事件派送追查實參／保存期，並保留pre-call／fallback的實際provider、全域pointer穩定性與ownership未知。
