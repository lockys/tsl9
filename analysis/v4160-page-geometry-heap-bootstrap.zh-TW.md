# 首次讀取頁長之前：堆積區初始化會改寫那三個 byte 嗎？

V1.31 參考程式 `0x43b88` 呼叫 `0x43104`；它確實寫 RAM，且兩個區塊標頭的地址來自設定值。不能只看 `0x43b3e` 本體就排除這次寫入。在 APP 提供的堆積基址 `0x2000418c`、長度 `0x7000` 仍有效的條件下，第一個標頭是 `0x200043ac`，第二個是 `0x200045ac`。內層 `0x430e0` 沿兩個標頭計算可用量，到 `0x2000b184` 哨兵便返回，不讀哨兵的下一筆，也不寫記憶體。`0x4316c` 將結果的低半字寫到 `0x200031a2`，不是頁長 `0x200031f8`。

另一個容易混淆的呼叫是進入讀頁前的 `0x43c00 → 0x4329a`：它只將 `0x20003198` 的 word 清零，再返回 `0x43c04`。這兩個呼叫在下列名義模型中都保留 `cfg+12..14`；**不是從預設值設定完成到讀頁入口的連續執行證明**。兩次呼叫之間還有配置器和對配置結果的填零；更早還有 `cfg+44` 回呼。若堆積基址、長度、映射或 stack 不符，不能直接套用這份寫址清單。

重跑：傳 decoded APP、V1.31 主段與 rasm2。以下從指令建立及遍歷串列；WCH 壓縮半字存取採 Xwchc 解讀。所有寫入都先記錄實際地址再比對，非實機記憶體觀測。

```python
from pathlib import Path
from hashlib import sha256
import subprocess,re,sys
a,b=(Path(s).read_bytes() for s in sys.argv[1:3]);tool=sys.argv[3]
def ck(x):
    if not x:raise ValueError('bootstrap footprint mismatch')
ck([sha256(x).hexdigest() for x in (a,b)]==['0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'])
ck(a[0x11a3a:0x11a4a].hex()=='97a7fe1f938727753ec89d67231af100');H=0x19a3a+0x1ffea000+1874;C=0x200031ec;S=0x2000ff40;M=0xffffffff
code={};wch={0x4311c:('da23','lhu','a4,4(a5)'),0x43152:('56a2','sh','a3,4(a2)'),0x4315e:('5ea3','sh','a5,4(a4)'),0x430f8:('f623','lhu','a3,6(a5)'),0x430fc:('d623','lhu','a3,4(a5)')}
for lo,hi in [(0x430e0,0x43174),(0x4329a,0x432a4),(0x43b88,0x43b8c),(0x43c00,0x43c06)]:
    p=lo
    for line in subprocess.check_output([tool,'-a','riscv','-b','32','-s',hex(lo),'-D',b[lo-0x40000:hi-0x40000].hex()],text=True).splitlines():
        address,n,h,o,*args=line.split();n=int(n);ck(int(address,16)==p and bytes.fromhex(h)==b[p-0x40000:p-0x40000+n]);args=''.join(args)
        if p in wch:k,o,args=wch[p];ck(h==k)
        code[p]=n,o,args.split(',');p+=n
    ck(p==hi)
for geometry in (b'\x00\x01\x03',b'\xff\xff\x00'):
    mem={};writes=[];walk=[];r=dict(sp=S,zero=0)
    def put(p,n,v):mem.update({p+i:v>>(8*i)&255 for i in range(n)})
    def get(p,n):return sum(mem[p+i]<<(8*i) for i in range(n))
    put(C,4,H);put(C+4,2,0x7000);put(C+12,3,int.from_bytes(geometry,'little'))
    for start,end in [(0x43b88,0x43b8c),(0x43c00,0x43c04)]:
        pc=start
        for _ in range(128):
            if pc==end:break
            here=pc;n,o,x=code[pc];pc+=n;t=x[0];v=lambda s:r[s] if s in r else int(s,0)
            if o in ('lw','lhu','sw','sh'):
                d,k=re.fullmatch(r'(\d+)\((\w+)\)',x[1]).groups();p=r[k]+int(d);w=2 if o in ('lhu','sh') else 4
                if o[0]=='s':put(p,w,r[t]);writes.append((p,w))
                else:r[t]=get(p,w)
                if here==0x43100:walk.append(p)
            elif o in ('li','lui'):r[t]=(v(x[1])<<(12 if o=='lui' else 0))&M
            elif o in ('addi','add','sub','srli'):
                l,h=map(v,x[1:]);r[t]=(l-h if o=='sub' else l>>h if o=='srli' else l+h)&M
            elif o=='jal':r['ra']=pc;pc=v(x[-1])
            elif o=='ret':pc=r['ra']&~1
            elif o=='j':pc=v(t)
            elif o in ('bleu','bne','bnez'):
                take=r[t]!=0 if o=='bnez' else r[t]<=v(x[1]) if o=='bleu' else r[t]!=v(x[1]);pc=v(x[-1]) if take else pc
            else:raise ValueError(o)
        ck(pc==end and r['sp']==S)
    X,Y,Z=0x200043ac,0x200045ac,0x2000b184
    ck(walk==[X,Y] and get(X,4)==Y and get(Y,4)==Z and get(0x200031a2,2)==Z-X-16)
    ck(writes==[(0x20003194,4),(0x2000318c,4),(S-4,4),(0x20003190,4),(X,4),(X+4,2),(X+6,2),(Y,4),(Y+4,2),(Y+6,2),(0x200031a2,2),(0x20003198,4)])
    ck(all(p+w<=C+12 or C+15<=p for p,w in writes) and get(C+12,3)==int.from_bytes(geometry,'little'))
print('PASS: 2 geometry inputs; 2 linked headers, 12 ordered stores per case, geometry unchanged')
```
