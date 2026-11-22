# 初始化讀取回呼：從間接呼叫追到比較結果

範圍是 V1.31 參考呼叫端 `0x44052` 到 `0x4405c` 的分支，包括 v4.1.60 APP `0x1979a` 及參考 RAM 複製函式的返回。沿用[三欄通過條件](v4160-cfg-read-gate-44022.zh-TW.md)、名義 SP 和 RAM 副本；下列檢查新增跨兩次間接呼叫的連續指令軌跡，而非把回呼結果直接注入比較。

以 SP=`0x2000ff20`、讀取起點 A=`0x08077c00`，實際順序為：保存返回位址到 `0x2000ff1c`（word），清外設 `0x4002420c`（word），把 A 起算的四個 byte 逐一寫到 `0x2000ff2c..0x2000ff2f`，最後將外設原讀值寫回。這七次 store 都與校準回呼槽 `[0x2000321c,0x20003220)` 分離。這是參考程式的 CPU 寫址，不是實際裝置的儲存或外設觀測。

APP 回傳零，但呼叫端不以零判斷成功：重讀 cfg+8 和堆疊上的 little-endian word，相等到 `0x44038`，不等到 `0x44060`。檢查用原值及每一位單獨翻轉的 32 個不同值，驗兩次呼叫邊界、寫入位址／寬度／值與分支。未涵蓋不等分支的後續寫入。

重現：依序傳 decoded APP、V1.31 carrier、rasm2 路徑。有限解譯，只處理這條成功存取路徑；外設模型只記錄可見讀寫。

```python
from pathlib import Path
from hashlib import sha256
import sys,subprocess,re
def ck(v):
    if not v: raise ValueError('read trace mismatch')
a,b=[Path(f).read_bytes() for f in sys.argv[1:3]]
ck(sha256(a).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667' and sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22');code={}
for p,data in [(0x44052,b[0x4052:0x4060]),(0x1979a,a[0x1179a:0x117b8]),(0x20000332,b[0x5a2:0x5dc])]:
    i=0
    for line in subprocess.check_output([sys.argv[3],'-a','riscv','-b','32','-s',hex(p),'-D',data.hex()],text=True).splitlines():
        h,n,raw,o,*args=line.split();n=int(n);ck(int(h,16)==p+i and bytes.fromhex(raw)==data[i:i+n]);code[p+i]=n,o,''.join(args).split(',');i+=n
    ck(i==len(data))
A=0x08077c00;S=0x2000ff20;C=0x200031ec;P=0x4002420c;M=0xffffffff
for sample in [A]+[A^(1<<i) for i in range(32)]:
    r=dict(sp=S,a0=A,a5=0x1979a,s0=C,zero=0);mem={};writes=[];calls=[];pc=0x44052
    def put(p,n,v):mem.update({p+i:v>>(8*i)&255 for i in range(n)})
    for p,v in [(A,sample),(C+8,A),(P,0x56781234),(0x4004c,int.from_bytes(b[76:80],'little'))]:put(p,4,v)
    for _ in range(100):
        if pc in (0x44038,0x44060):break
        n,o,x=code[pc];pc+=n;t=x[0];val=lambda k:r[k] if k in r else int(k,0)
        if o in ('lw','lbu','sw','sb'):
            d,k=re.fullmatch(r'(\d+)\((\w+)\)',x[1]).groups();p=r[k]+int(d);w=4 if o in ('sw','lw') else 1
            if o in ('lw','lbu'):r[t]=sum(mem[p+i]<<(8*i) for i in range(w))
            else:v=r[t]&((1<<(8*w))-1);writes.append((p,w,v));put(p,w,v)
        elif o in ('li','mv','lui'):r[t]=val(x[1])<<(12 if o=='lui' else 0)
        elif o in ('add','addi','slli'):
            l,h=map(val,x[1:]);r[t]=(l<<h if o=='slli' else l+h)&M
        elif o=='jalr':r['ra']=pc;pc=r[t]&~1;calls.append((pc,r['a0'],r['a1'],r['a2']))
        elif o=='ret':pc=r['ra']&~1
        elif o=='j':pc=val(t)
        elif o in ('beq','bne','beqz','bnez'):
            rhs=0 if o.endswith('z') else val(x[1]);pc=val(x[-1]) if (r[t]==rhs)==o.startswith('beq') else pc
        elif o!='fence.i':raise ValueError(o)
    ck(calls==[(0x1979a,A,1,S+12),(0x20000332,S+12,A,4)])
    ck(writes==[(S-4,4,0x44058),(P,4,0)]+[(S+12+i,1,sample>>(8*i)&255) for i in range(4)]+[(P,4,0x56781234)])
    ck(all(p+n<=C+48 or C+52<=p for p,n,v in writes) and r['sp']==S and r['a0']==0 and pc==(0x44038 if sample==A else 0x44060))
print('PASS: 33 traces, two indirect calls, seven ordered stores, both comparison exits')
```
