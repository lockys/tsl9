# Setup 可選欄位、長度比較與完整 packed-word helper

接續 [setup 入口前段](v4160-b1-setup-entry-static.zh-TW.md)，本輪展開 bit9／bit10 兩條可選欄位路徑至第一個長度比較，並完整核對它們呼叫的 `0x63d6a／0x63e54` helper。

新增證據為 **308 bytes／94 條窗口指令**及 **204 bytes／74 條完整 helper 指令**。setup 本身仍未展開至返回。[Python checker](check_v4160_b1_setup_options_static.py) 與 [固定 JSON ledger](v4160-b1-setup-options-static.json) 保存完整 operands、來源 hashes、CFG、fresh-sample 關係及兩個 caller 的串接。全程只讀 bytes／strict sparse HEX，沒有目標執行、模擬、可變 packet／buffer／IRQ／provider 模型或硬體操作。

| 新範圍 | V131 | V140 | 每版 bytes／指令 |
|---|---|---|---|
| setup options 窗口 | `[0x5d0f4,0x5d18e)` | `[0x5d23c,0x5d2d6)` | 154／47 |
| 完整 helper | `[0x63d6a,0x63dd0)` | `[0x63e54,0x63eba)` | 102／37 |

## Bit9：固定 header byte 與另一次 helper 取樣

沿用前段 P=S8、held Q=S5。fresh U32[P+84] bit9 非零才進入第一個分支：

```text
byte[Q+3] = 4
c0 = fresh U8[P+182]
b0 = fresh U8[P+181]
base0 = fresh U32[P+76]
byte[base0+4] = low8((c0 << 6) | b0)
byte[Q+2] = low8(fresh U8[Q+2] + 1)

z = fresh U8[P+184]
y = fresh U8[P+181]
x = fresh U8[P+182]
helper(x,y,z,0)
```

P+181 沒有先限制為低六位，因此是 OR，不能直接稱為兩個不重疊欄位的串接。helper 實參 x/y 是**重新讀取**的 byte，不保證等於先前寫入 header 使用的 c0/b0。新讀出的 P+76 也不保證等於 held Q。

## Helper：保持 A0，保留兩次 R+0 的讀值差異

helper 的入口 x/y/z/w 為完整 U32 暫存器值。這裡的 setup caller 將前三者以 unsigned byte 載入，w=0。令 G=`0x20003000`，H=`G+1300／1380`：

```text
若 x != 0：
    byte[0x40022048] = fresh U8[0x40022048] | 2
byte[H+10] = low8(y << 3)
R = fresh U32[G+1288／1368]
word[R+100] = low32((y << 3) | (z << 8) | x)
word[R+100] = (另一筆 fresh U32[R+100] & 0xff87ffff) | 0x00280000
word[R+100] = 再一筆 fresh U32[R+100] | 4
a = fresh U32[R+0]
若 w != 0：word[R+0] = a | 0x20000000
否則：
    b = 另一筆 fresh U32[R+0]
    word[R+0] = (b & 0xdfffffff) | (a & 0x20000000)
RET，A0 仍為 x
```

`w=0` 是**保留第一個 sample 的 bit29、其餘 bits 來自第二個 sample**。它不是強制清除 bit29，也不是對單一 word sample 做 RMW。R+100 的三次 store／fresh reload 同樣不能縮成一筆原子 store 或直接認定為硬體最終狀態。

helper 只有 A1..A5 定義，沒有 SP／RA／GP／S register 定義、frame 或子呼叫。這補上本機暫存器合約，仍不排除 R pointee 與物件／frame 的別名或實體暫存器讀寫效果。

重用 [完整 record callback](v4160-b1-record-callback-static.zh-TW.md) 的 1618-byte 本體，亦確認其 `+0x3ea` 以 fresh U8[P+182]、U8[P+181]、U8[P+184]、0 呼叫同一 helper。兩個 caller 都沒有把物件指標直接作為前四個語意實參；這不等於整體指標不保存或物件彼此相同。

## Bit10：兩個 byte 使用獨立 pointer、index 與 word 取樣

第一個分支跳過或 helper 正常返回後，再讀 fresh U32[P+84] bit10。bit9 與 bit10 並非同一筆 word snapshot。

bit10 非零時：

```text
flags = fresh U8[Q+3]
base1 = fresh U32[P+76]
i1 = fresh U8[Q+2]
byte[Q+3] = flags | 8
u1 = fresh U16[P+138]
byte[base1+i1+3] = low8(u1)

i2 = fresh U8[Q+2]
base2 = fresh U32[P+76]
p = fresh U8[P+127]
u2 = fresh U16[P+138]
byte[base2+i2+4] = low8((p << 4) | ((u2 >> 8) & 15))

byte[Q+2] = low8(fresh U8[Q+2] + 2)
```

三次 Q+2 取樣、兩次 P+76 取樣及兩次 P+138 取樣均保持獨立，因此尚不能證明兩次寫入連續，也不能把它們合併為一次 U16 copy。沒有 pointer null、extent 或 capacity 檢查保護這些 stores。

只有在 P/Q 相同且有效、相關欄位穩定、沒有別名／外部改寫，且呼叫正常返回等條件下，才可將前段的 Q+2=2、Q+3=0 合成下表：

| bit9 分支 | bit10 分支 | 條件性 Q+2 | 條件性 Q+3 |
|---|---|---|---|
| 跳過 | 跳過 | 2 | 0 |
| 執行 | 跳過 | 3 | 4 |
| 跳過 | 執行 | 4 | 8 |
| 執行 | 執行 | 5 | 12 |

這是封閉數值關係，不是實際 buffer、輸入可達性、寫入容量或 IRQ 進展的證明。完整擴展 prefix 的 P 讀取至 P+184，所需直接 P extent 至少 185 bytes；實際配置大小仍未建立。

## 長度比較在可選寫入之後

兩條可選路徑接合後才執行：

```text
c = fresh U8[Q+2]
length = fresh U16[P+132]
threshold = signed32(low32(253-c))
若 threshold >= length：跳至 setup+0x396
否則：繼續 setup+0x188
```

原指令是 **signed BGE**。threshold 的數值範圍為 -2..253，c=254／255 時不會通過這個比較。這個比較發生在先前 stores 之後，不能用作那些寫入的容量保證。

本輪與舊 prefix 串接成每版 392-byte 的連續區段，全部 133 條 CFG edges 有 8 條語法出口路徑覆蓋，前往 `+0x188／+0x396`。兩個出口仍有 80-byte frame 存活，完整 setup 的其餘分支、frame 還原、payload 保存及返回尚未驗證。

## 驗證

```powershell
python analysis/check_v4160_b1_setup_options_static.py
python -O analysis/check_v4160_b1_setup_options_static.py
```

完整 helper 有 38 條 edge、4 條語法路徑、6 個 stores；options 窗口有 7 個 stores。負向核對包含 **168 個逐指令變異、42 個 typed-load funct3 變異**，並固定三個 Xwchc byte store 的 bytes／width。

純 host 整數核對包含 65536 個 OR-byte 組合、196608 個 U16／byte 邊界族、262144 個獨立 R+0 sample 組合，以及 393216 個 signed-length 比較族。比較族只涵蓋指定的六種 count 與全部 U16 length，沒有宣稱窮舉全部 count／length pair；沒有建立可變 target buffer 或 packet 模型。原有驗證鏈、輸入身份、strict sparse HEX 與固定 ledger 也一併重跑。

本輪 APP C 重建覆蓋不變。仍需展開 `+0x188／+0x396` 後續長度調整與資料組裝，確認實際 pointer／provider、別名、IRQ 順序、完整返回與消費釋放保存期。
