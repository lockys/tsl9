# `0x17f72` 的取消結果：在回呼派送處被覆蓋

在原 APP，`0x18340` 不是呼叫 `0x17cf4`。它呼叫 `0x9124`，四個參數依序為函式地址 `0x17cf4`、1、50、0。非零延遲路徑先找既有相同函式；若沒有且找到空槽，`0x921c` 才把函式地址寫到 `表基址 + 12*i + 4`。表滿、未派送或記錄被換掉，均不能據此斷言回呼有執行。

派送端用相同基址 `0x2000be08`、步距 12，從記錄 +4 讀目標到 a3、從 +8 讀參數到 a0。若 `0x9058: jalr a3` 選到 `0x17cf4`，且該函式走到兩個 byte 判斷均為零的路徑，`0x17f72` 以自身函式地址呼叫 `0x90b0`。其後還原 ra、s0、s1 與 SP，不改 a0。

因此，即使這次取消真的回 6，它也只傳到 `0x905a`：該處第一條 `li a0,1` 無條件覆蓋它。隨後算的是 `low16((1 << (live_s0 & 31)) ^ live_s1)`，不是取消狀態。這不排除先前的表項寫入或其他副作用；也不證明真機派送、服務結果或所有間接呼叫者。

以 Python 3 傳入 decoded BIN，核對原指令、兩個 PC-relative 函式地址、三個表基址及 JAL 目的：

```python
from hashlib import sha256
from pathlib import Path
import sys
b=Path(sys.argv[1]).read_bytes();base=32768
def ck(v):
    if not v: raise ValueError('callback evidence mismatch')
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
def w(p): return int.from_bytes(b[p-base:p-base+4],'little')
def pair(p):
    x,y=w(p),w(p+4);r=x>>7&31
    ck(x&127==23 and y&0x707f==19 and y>>7&31==r and y>>15&31==r)
    return (p+(x&0xfffff000)+(y>>20^2048)-2048)&0xffffffff
def call(p):
    x=w(p);ck(x&4095==0xef);d=(x>>31<<20)|(x&0xff000)|(x>>20&1)<<11|(x>>21&1023)<<1
    return p+(d^1048576)-1048576
ck(pair(0x18330)==pair(0x17f6a)==0x17cf4 and call(0x18340)==0x9124 and call(0x17f72)==0x90b0)
ck(pair(0x9132)==pair(0x9188)==pair(0x9034)==0x2000be08)
for p,h in [(0x18328,'8146130620038545'),(0x921a,'ca97c8c32380870023a44701'),(0x903c,'ae84ba97d44381ce03c707008847'),(0x9058,'8296054533158500258d42054181'),(0x17cf4,'011106ce22cc26ca'),(0x17f76,'f2406244d24405618280')]:
    v=bytes.fromhex(h);ck(b[p-base:p-base+len(v)]==v)
print('PASS: registration and self-cancel targets; three table bases; indirect callback result overwritten at 0x905a')
```
