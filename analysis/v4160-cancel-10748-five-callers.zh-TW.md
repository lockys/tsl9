# 0x10748 最後一次取消：五個直接上層都先覆寫 a0

原 v4.1.60 APP，假設 `0x1070a` 經最後的尾跳 `0x10748 → 0x90b0` 正常返回且下列取指與資料存取成功。追的是返回暫存器的原值，不是假設取消沒有其他副作用。

|呼叫點|第一個使用或改寫 a0 的位置|
|---|---|
|0x12a74、0x12aa6|0x12a78、0x12aaa：`lw a0,12(sp)`。隨後判斷的是重新載入的字。|
|0x12b2c|0x12b30 呼叫 0x129c4，進入時仍帶著原值；其直線前綴只調整堆疊、保存其他暫存器與初始化資料，0x129e0 以 `sp+12` 覆寫 a0。不是因為跨越 call 就算丟棄。|
|0x147fc|0x14800 讀 `u16[s0+2]`。值為 0、0x1000、0x2000 時，分別於 0x14812、0x1482e、0x14838 將 a0 設為 0、1、2；其餘值走 0x14848，於 0x14856 設為 `sp+48`。沒有按取消碼選路。|
|0x14930|0x14934 起先讀兩個 byte、組字及寫 stack，再載入服務指標與設定 a1；0x14956 以 `sp+51` 覆寫 a0，之後才間接呼叫。|

此表補齊[尾跳盤點](v4160-cancel-tail-upper-edges.zh-TW.md)中 0x1070a 那一列，不涵蓋間接上層或其他取消尾跳。下列核對原始指令視窗，並從分支編碼和匯入的半字推導四種出口的次數；不是全 CPU 模擬。傳入 decoded BIN 路徑即可重跑。

```python
import hashlib, sys
from collections import Counter
from pathlib import Path
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v: raise ValueError('10748 caller mismatch')
def at(p,n): return b[p-0x8000:p-0x8000+n]
ck(hashlib.sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
for p,h in [(0x10748,'6f809f96'),(0x12a74,'efd07fc93245'),(0x12aa6,'efd05fc63245'),(0x12b2c,'efd0ffbdeff05fe9'),(0x129c4,'397122dc26da4ad84ed606de014485490549b94402ca230b810005046800'),(0x147fc,'efb0fff08357240005676384e70209676386e70285ef0145'),(0x1482e,'0545'),(0x14838,'0945'),(0x14848,'b709040083a789041306000781450818'),(0x14930,'efb0bfdd83470400034714001376f90fa207d98f2318f1022309c102b7070400fc479305240013053103')]:
    v=bytes.fromhex(h);ck(at(p,len(v))==v)
def sx(x,n):return (x^(1<<(n-1)))-(1<<(n-1))
def branch(p):
    x=int.from_bytes(at(p,4),'little');return p+sx(x>>31<<12|(x>>7&1)<<11|(x>>25&63)<<5|(x>>8&15)<<1,13)
x=int.from_bytes(at(0x14810,2),'little');other=0x14810+sx((x>>12&1)<<8|(x>>10&3)<<3|(x>>5&3)<<6|(x>>3&3)<<1|(x>>2&1)<<5,9)
t1,t2=branch(0x14806),branch(0x1480c);counts=Counter(t1 if v==4096 else t2 if v==8192 else other if v else 0x14812 for v in range(65536))
ck(counts=={0x14812:1,0x1482e:1,0x14838:1,0x14848:65533});print('PASS: 5 caller prefixes; 65536 halfwords; four paths overwrite a0')
```
