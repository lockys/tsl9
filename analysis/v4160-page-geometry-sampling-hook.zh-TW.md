# 頁面設定：從取樣回呼入口連續走到返回

若 V1.31 的 cfg+44 指向 v4.1.60 APP `0x197f0`，以入口 SP=`0x2000ff50` 進入，名義路徑的 CPU 寫入只落在堆疊與外設，不覆蓋頁長與頁數 `[0x200031f8,0x200031fb)`。與分段驗證不同，這裡不在子呼叫之間重設暫存器或記憶體。就緒時，先讀 `0x4001244c` 再回傳低 16 位；四次輪詢均未就緒的對照停在下一輪開始，沒有取樣或返回。不是對實機 ROM、中斷、DMA、完成時間或整段初始化的證明。

重現：以下 Python 的參數依序為 decoded APP、rasm2。只解譯測試走到的指令；外設讀值為合成輸入。

```python
from hashlib import sha256
from pathlib import Path
import re, subprocess, sys

def ck(v):
    if not v: raise ValueError('sampling hook trace mismatch')
b=Path(sys.argv[1]).read_bytes();ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667');code={}
for p,e in [(0x197f0,0x1995c),(0x8520,0x854a),(0x19124,0x19142),(0x1908c,0x1909e),(0x188e2,0x189fe),(0x19160,0x1917e),(0x18a66,0x18aa6)]:
    for line in subprocess.check_output([sys.argv[2],'-a','riscv','-b','32','-s',hex(p),'-D',b[p-32768:e-32768].hex()],text=True).splitlines():
        a,n,h,o,*args=line.split();n=int(n);ck(int(a,16)==p and bytes.fromhex(h)==b[p-32768:p-32768+n]);code[p]=n,o,''.join(args).split(',');p+=n
    ck(p==e)
M=0xffffffff;B=0x40012400;S=0x2000ff50;F=S-128;G=0x200031f8;R=0x43d3a
for seed in (0,0x9d73ffff):
 for polls in ((2,),(0,1,2),(0,4,1,0)):
    pc=0x197f0;mem={G:0,G+1:1,G+2:3};saved={'s'+str(i):seed^i for i in range(12)};r=dict(saved,sp=S,ra=R,zero=0);stores=[];k=samples=0;calls=[]
    for _ in range(500):
        if pc==R or (pc==0x198c6 and k==len(polls)):break
        at=pc;n,o,x=code[pc];pc+=n;t=x[0];v=lambda s:r[s] if s in r else int(s,0)
        if o in ('lw','lbu','sw','sb'):
            d,base=re.fullmatch(r'(\d+)\((\w+)\)',x[1]).groups();p=(r[base]+int(d))&M;w=4 if o in ('lw','sw') else 1
            if o[0]=='s':
                stores.append((p,w));mem.update({p+i:r[t]>>(8*i)&255 for i in range(w)})
            elif p==B:r[t]=polls[k];k+=1
            elif p==B+76:r[t]=seed;samples+=1
            else:r[t]=sum(mem.get(p+i,(seed>>(8*((p+i)%4)))&255)<<(8*i) for i in range(w))
        elif o=='jal':ck(t=='ra');r[t]=pc;pc=v(x[1]);calls.append(at)
        elif o=='ret':pc=r['ra']&~1
        elif o=='j':pc=v(t)
        elif o in ('beqz','bnez','bne','bltu','bleu'):
            take=not r[t] if o=='beqz' else bool(r[t]) if o=='bnez' else r[t]!=v(x[1]) if o=='bne' else r[t]<v(x[1]) if o=='bltu' else r[t]<=v(x[1]);pc=v(x[-1]) if take else pc
        elif o in ('li','mv','lui','not','snez'):
            a=v(x[1]);r[t]=(a<<12 if o=='lui' else ~a if o=='not' else int(a!=0) if o=='snez' else a)&M
        elif o in ('add','addi','and','andi','or','ori','mul','sll','slli','srli'):
            a,c=map(v,x[1:]);r[t]=(a+c if o in ('add','addi') else a&c if o in ('and','andi') else a|c if o in ('or','ori') else a*c if o=='mul' else a>>(c&31) if o=='srli' else a<<(c&31))&M
        else:raise ValueError(o)
    ready=bool(polls[-1]&2);ck(k==len(polls) and samples==int(ready) and calls.count(0x198ca)==k)
    ck(all((F-4<=p and p+w<=S) or (w==4 and p in {0x40021004,0x4002100c,0x40021018,*range(B+4,B+57,4)}) for p,w in stores))
    ck(all(p+w<=G or G+3<=p for p,w in stores) and bytes(mem[G+i] for i in range(3))==b'\x00\x01\x03')
    if ready:ck(pc==R and r['sp']==S and r['a0']==seed&65535 and all(r[s]==a for s,a in saved.items()))
    else:ck(pc==0x198c6 and r['sp']==F)
print('PASS: 4 complete callbacks, 2 bounded waits; every store excludes all 3 geometry bytes')
```
