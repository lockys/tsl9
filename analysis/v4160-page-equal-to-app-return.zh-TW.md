# 讀頁相等：從回呼返回一直走到 APP，沒有再呼叫配置器

在 v4.1.60 APP 的三個欄位均非零、讀頁回呼已正常返回的前提下，V1.31 參考程式從 `0x44058` 比較兩個**重新載入**的 word。若相等，就不進入第二次配置、填頁、寫頁或釋放。以下把比較、三層返回及中間的任務表登記接成同一次指令追蹤，停在 APP `0x19aee`，不以各函式分別返回成功代替。

在名義堆疊、保存值及表基址 `T=0x200047f4` 下，相等路徑只有四次寫入：[三個函式表 word 和一個計數 byte](v4160-role-internal-table-writes.zh-TW.md)，順序是表、表、計數、表。內層返回 1，APP 收到 0。這段**既不讀也不寫 cfg+48**，所以保留的是進入比較時的值，不會把不同值修復為 `0x197b8`。比較不等則在 `0x44060` 交給[另一路徑](v4160-clock-hook-mismatch-paths.zh-TW.md)，不能套用四次寫入的結論。

重現：傳 V1.31 carrier、rasm2 路徑。兩條壓縮 byte 指令按 Xwchc 處理；其他指令按反組譯執行。每一個計數 byte 均測兩個不同槽初值及兩種比較結果。這是合成 RAM 的有限路徑，不證設備頁內容、實際 ROM 或回呼一定返回。

```python
from pathlib import Path
from hashlib import sha256
import subprocess,sys,re
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x:raise ValueError('page return mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22');code={}
for lo,hi in [(0x44058,0x44060),(0x44038,0x44046),(0x43c06,0x43c4e),(0x43d4e,0x43d5c)]:
    p=lo
    for line in subprocess.check_output([sys.argv[2],'-a','riscv','-b','32','-s',hex(lo),'-D',b[lo-0x40000:hi-0x40000].hex()],text=True).splitlines():
        addr,n,raw,op,*args=line.split();n=int(n);ck(int(addr,16)==p and bytes.fromhex(raw)==b[p-0x40000:p-0x40000+n]);x=''.join(args).split(',')
        if p==0x43c06:ck(raw=='1c30');op,x='lbu',['a5','1(s0)']
        if p==0x43c3e:ck(raw=='18b0');op,x='sb',['a4','1(s0)']
        code[p]=n,op,x;p+=n
    ck(p==hi)
S=0x2000ff20;C=0x200031ec;N=0x2000319d;T=0x200047f4;A=0x08077c00
for n in range(256):
 for hook in (0,0x197b8):
  for equal in (False,True):
    r=dict(sp=S,s0=C,a0=0);mem={};writes=[];reads=[];rets=[];pc=0x44058
    def put(p,w,v):mem.update({p+i:(v>>(8*i))&255 for i in range(w)})
    def get(p,w):return sum(mem[p+i]<<(8*i) for i in range(w))
    for p,v in [(C+8,A),(C+48,hook),(S+12,A if equal else A^1),(0x200031c4,T),(S+28,0x43c06),(S+24,N-1),(S+20,0x20003000),(S+16,0),(S+44,0x43d4e),(S+40,0),(S+36,0),(S+60,0x19aee),(S+56,0),(S+52,0)]:put(p,4,v)
    put(N,1,n)
    for _ in range(70):
        if pc in (0x44060,0x19aee):break
        width,o,x=code[pc];pc+=width;t=x[0];val=lambda k:r[k] if k in r else int(k,0)
        if o in ('lw','lbu','sw','sb'):
            d,k=re.fullmatch(r'(\d+)\((\w+)\)',x[1]).groups();p=r[k]+int(d);w=4 if o in ('lw','sw') else 1
            if o in ('lw','lbu'):reads.append((p,w));r[t]=get(p,w)
            else:v=r[t]&((1<<(8*w))-1);put(p,w,v);writes.append((p,w,v))
        elif o in ('li','mv','lui'):r[t]=val(x[1])<<(12 if o=='lui' else 0)
        elif o in ('add','addi','slli','andi'):
            l,h=map(val,x[1:]);r[t]=(l<<h if o=='slli' else l&h if o=='andi' else l+h)&0xffffffff
        elif o=='beq':pc=val(x[2]) if r[t]==r[x[1]] else pc
        elif o=='ret':pc=r['ra']&~1;rets.append((pc,r['a0']))
        else:raise ValueError(o)
    ck(reads[:2]==[(C+8,4),(S+12,4)] and all(p+w<=C+48 or p>=C+52 for p,w in reads) and get(C+48,4)==hook)
    if equal:ck(pc==0x19aee and r['sp']==S+64 and rets==[(0x43c06,1),(0x43d4e,1),(0x19aee,0)] and writes==[(T+4*n,4,0x432a4),(T+4*((n+1)&255),4,0x43326),(N,1,(n+3)&255),(T+4*((n+2)&255),4,0x43326)])
    else:ck(pc==0x44060 and not rets and not writes)
print('PASS: 512 equal returns, 512 mismatch boundaries; cfg+48 preserved')
```
