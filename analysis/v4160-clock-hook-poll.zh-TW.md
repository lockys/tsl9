# 初始化回呼：輪詢前的六次寫入與真正的退出條件

從[已驗證的五個呼叫](v4160-clock-hook-two-calls.zh-TW.md)返回點 `0x1989a` 開始，取 s1=`B=0x40012400`。下表的 X 都是**該次**讀到的 32-bit 外設值，不假定連續讀值相同。

|呼叫點|寫入位址|寫入值|
|---|---|---|
|1989e|B+8|X 或 1（bit 0）|
|198a6|B+4|X 或 `0x04000000`|
|198ac|B+8|X 或 `0x00800000`|
|198b8|B+12|X 或 `0x001c0000`（參數 16、1、7，第一欄位移 18）|
|198b8|B+52|`(X & ~31) | 16`（第二欄位移 0）|
|198c0|B+8|X 或 `0x00500000`|

`0x198ca → 0x18a8e` 每輪重新讀 **B+0**，不是上表反覆寫入的 B+8。返回 `((X & 2) != 0)`；零則 `0x198d6` 跳回 `0x198c6`，非零則抵達 `0x198d8`。重試只重讀，不重做六次設定。本段沒有計時器或重試次數上限，無法據此保證會退出。到這個邊界，名義路徑新增的六次直接寫入都不在 `0x2000321c..0x2000321f`；沒有觀測實機或外設間接作用。

重現：傳 decoded APP 和 rasm2 路徑。以下從原始位元組反組譯並逐條執行選定路徑；每次讀外設注入獨立樣本，驗寫序列、讀取次數和每輪分支。連續四次未置位僅驗四輪，不當成無限執行證明。

```python
from hashlib import sha256
from pathlib import Path
import re,subprocess,sys
def ck(v):
    if not v: raise ValueError('poll evidence mismatch')
b=Path(sys.argv[1]).read_bytes();ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667');code={}
for p,e in [(0x1989a,0x198d8),(0x18986,0x189fe),(0x18a6e,0x18aa6)]:
    for l in subprocess.check_output([sys.argv[2],'-a','riscv','-b','32','-s',hex(p),'-D',b[p-32768:e-32768].hex()],text=True).splitlines():
        addr,n,raw,o,*args=l.split();n=int(n);ck(int(addr,16)==p and bytes.fromhex(raw)==b[p-32768:p-32768+n]);code[p]=(n,o,''.join(args).split(','));p+=n
    ck(p==e)
B=0x40012400;mask=0xffffffff
for polls in ([2],[1,0x80000000,3],[0,1,4,0xfffffffd]):
    xs=[0x10203040,0,17,0xff0000ff,0xffffffef,0x501]; inputs=iter(xs+list(polls));r={'s1':B};pc=0x1989a;reads=[];writes=[];branches=[]
    for _ in range(256):
        if pc==0x198d8 or len(branches)==len(polls):break
        at=pc;n,o,x=code[at];pc+=n;t=x[0];v=lambda k:r[k] if k in r else int(k,0)
        if o=='lw' or o=='sw':
            off,reg=re.fullmatch(r'(\d+)\((\w+)\)',x[1]).groups();loc=r[reg]+int(off)
            if o=='lw':reads.append(loc);r[t]=next(inputs)
            else:writes.append((loc,r[t]))
        elif o=='jal':ck(t=='ra');r[t]=pc;pc=v(x[1])
        elif o=='ret':pc=r['ra']
        elif o=='beqz':
            if not r[t]:pc=v(x[1])
        elif o in ('bltu','bleu'):
            if (r[t]<v(x[1]) if o=='bltu' else r[t]<=v(x[1])):pc=v(x[2])
        elif o in ('li','mv','lui'):r[t]=(v(x[1])<<(12 if o=='lui' else 0))&mask
        elif o=='not':r[t]=~v(x[1])&mask
        elif o=='snez':r[t]=int(v(x[1])!=0)
        elif o in ('or','ori','and','addi','mul','sll'):
            a,c=map(v,x[1:]);r[t]=(a|c if o in ('or','ori') else a&c if o=='and' else a+c if o=='addi' else a*c if o=='mul' else a<<(c&31))&mask
        else:raise ValueError(o)
        if at==0x198d6:branches.append(pc)
    exp=[(B+d,z) for d,z in zip((8,4,8,12,52,8),(xs[0]|1,xs[1]|0x4000000,xs[2]|0x800000,xs[3]|0x1c0000,(xs[4]&~31)|16,xs[5]|0x500000))];ck(writes==exp and reads==[p for p,_ in exp]+[B]*len(polls));ck(branches==[0x198d8 if x&2 else 0x198c6 for x in polls] and pc==branches[-1])
print('PASS: six ordered MMIO writes; immediate exit, delayed exit and four retries')
```
