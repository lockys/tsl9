# 串列插入的兩道條件：哪一個先寫？

在 V1.31 參考映像找到同一條初始化路徑處理[插入入口的兩道條件](v4160-list-first-insertion.zh-TW.md)。令 `B=0x200033b8`；這些是靜態寫入，不是實機事件時間。

|順序|指令|效果|
|---|---|---|
|1|`0x5369c..0x536ac`，`0x536d2`|讀取 word `B+208`，與 `0x072d79ff` 做 OR，把結果寫至 `B+216` (`0x20003490`)。無論舊值為何，bit 6 均為 1。不是從 `B+216` 讀回再設位。|
|2|`0x536ca` 取樣，`0x536da` 寫入|先讀 `0x200031fa`（設定結構 `0x200031ec+14`）的一個 byte，再將同一值寫到 `B+193`、`B+201`；後者 `0x20003481` 才是入口比較的上限。因此**取樣發生在 bit 寫入之前，上限落地在其之後**。|

若先前 296-byte 清零成功、計數未被其他寫入改變，則 `B[200]=0`；在這兩筆寫入之後，入口的這兩道條件能否通過只取決於取樣是否非零。既有[設定值分析](v4160-44060-temp-buffer-stores.zh-TW.md)的名目值是 3，不代表當時一定讀到 3。更重要的是：首次角色判斷 `0x55be2` 在 `0x55bf8 → 0x5362e` **之前**。這次初始化不能用來解釋判斷前已通過插入條件。

另外 `0x6a600` 也寫位移 201，但在 `0x6a596` 入口路徑，其基址是從 `0x20003438` 讀出的物件指標，而非 B 常數。舊物件 byte 非零時還會跳過這筆寫入；不能單憑位移相同列為另一筆固定上限寫入。其他間接寫入及更早呼叫未排除。

重現：以 V1.31 carrier 路徑為參數。核對指令、解碼位址與遮罩，窮舉 byte 比較；不執行設備。

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('gate writer evidence mismatch')
def raw(p,h):
    v=bytes.fromhex(h);ck(b[p-0x40000:p-0x40000+len(v)]==v)
def w(p):return int.from_bytes(b[p-0x40000:p-0x40000+4],'little')
def imm(p):return (w(p)>>20^2048)-2048
def dest(p):return (w(p)>>25<<5)|(w(p)>>7&31)
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22');raw(0x53632,'b7340020');raw(0x53670,'1384843b');raw(0x5369c,'0327040d2322f40eb7872d079387f79f5d8f');raw(0x536b8,'37390020d58f1309c91e232af40c232ef40c8347e9002328e40c232ce40ca300f40ca304f40c');raw(0x55be2,'83c7f719411106c689eb');raw(0x55bf8,'efd07fa3');raw(0x6a596,'b737002083a78743c9c3');raw(0x6a5d0,'83c6970c89ca');raw(0x6a600,'a384c70c')
B=(w(0x53632)&0xfffff000)+imm(0x53670);mask=(w(0x536a4)&0xfffff000)+imm(0x536a8);cfg=(w(0x536b8)&0xfffff000)+imm(0x536be)+imm(0x536ca);ck((mask,cfg,B+dest(0x536d2),B+dest(0x536da))==(0x072d79ff,0x200031fa,0x20003490,0x20003481));ck(mask&64 and imm(0x5369c)==208 and 0x20003000+imm(0x6a59a)==0x20003438)
passes=[sum(n<c for n in range(256)) for c in range(256)];ck(passes==list(range(256)));print('PASS: mask, sample, store order; 65536 count/limit pairs')
```
