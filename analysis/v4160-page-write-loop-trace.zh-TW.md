# 寫頁回呼：64 個資料 word 從哪裡讀、寫到哪裡？

[讀頁不等的成功配置路徑](v4160-page-mismatch-to-app-return.zh-TW.md)傳給 APP `0x197be` 的是 `(頁址,64,P)`。但回呼呼叫 `0x18ef2` 時，a1 是從自己堆疊重讀的 **P**，不是 64。子函式將目的頁址向下對齊 256；資料迴圈在 `0x18f16` 自己設上限 256 bytes。依賴前兩個子呼叫正常返回、保存的來源指標與 s0 未變，不依賴入口 a1 留到資料迴圈。

從 `0x18f0c` 逐指令核對：先輪詢狀態 bit 1，清除時遮罩運算使 a5 為零，這就是第一個 word 的位移。其後每次先讀 `P+位移`、再寫 `頁基址+位移`、再輪詢，最後才將位移加 4。等待中的反向分支返回**狀態讀取**，不重讀來源、不重寫資料。因而在名義三頁且正常完成時，每頁 64 次 word 讀及 64 次 word 寫，均不寫 `cfg+48`。若某次寫後一直忙，不能把餘下的 word 算成已寫，也不能據此保證回呼返回。

重跑：傳 decoded APP 和 rasm2 路徑。檢查 stack 保存／重讀與呼叫位元組，從原 APP 解譯迴圈；用帶索引的合成資料逐筆對照地址、值及順序。三個頁址各測立即就緒、每次延後兩次才就緒，以及第 32 個 word 已寫後連續讀忙 8 次便停止觀察。這不是實機燒錄、持久化或無限等待證明；其餘回呼寫址見[本體清單](v4160-cfg60-heap-separation.zh-TW.md)。

```python
from pathlib import Path
from hashlib import sha256
import sys,subprocess,re
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x:raise ValueError('page loop mismatch')
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667');base=0x8000
def raw(p,n):return b[p-base:p-base+n]
ck(raw(0x197be,12).hex()=='011106ce22cc32c62a84eff0' and raw(0x197d2,10).hex()=='32462285b285eff0aff1' and raw(0x18efa,4).hex()=='137505f0');code={};p=0x18f0c
for line in subprocess.check_output([sys.argv[2],'-a','riscv','-b','32','-s',hex(p),'-D',raw(p,0x18f36-p).hex()],text=True).splitlines():
    addr,n,h,o,*args=line.split();n=int(n);ck(int(addr,16)==p and bytes.fromhex(h)==raw(p,n));code[p]=n,o,''.join(args).split(',');p+=n
ck(p==0x18f36);P=0x20004b00;status=0x4002200c
for page in range(0x08077c00,0x08077f00,256):
 for mode in ('ready','delayed','stop'):
    pc=0x18f0c;r=dict(a0=page,a1=P,a4=status-12);ev=[];counts={};words=0
    for _ in range(2500):
        if pc==0x18f36:break
        if mode=='stop' and counts.get(32)==8 and pc==0x18f2a:break
        n,o,x=code[pc];pc+=n;t=x[0];v=lambda k:r[k] if k in r else int(k,0)
        if o in ('lw','sw'):
            d,k=re.fullmatch(r'(\d+)\((\w+)\)',x[1]).groups();a=int(d)+r[k]
            if o=='sw':ev.append(('w',a,r[t]));words+=1
            elif a==status:
                i=counts.get(words,0);counts[words]=i+1;r[t]=2 if (mode=='stop' and words==32) or (mode=='delayed' and i<2) else 0;ev.append(('s',a,r[t]))
            else:ck(P<=a<P+256 and a%4==0);r[t]=0x77110000+(a-P)//4;ev.append(('r',a,r[t]))
        elif o in ('lui','li'):r[t]=v(x[1])<<(12 if o=='lui' else 0)
        elif o in ('add','addi','andi'):r[t]=v(x[1])&v(x[2]) if o=='andi' else v(x[1])+v(x[2])
        elif o=='bnez':pc=v(x[1]) if r[t]!=0 else pc
        elif o=='bne':pc=v(x[2]) if r[t]!=v(x[1]) else pc
        else:raise ValueError(o)
    wait=[('s',status,2)]*(2 if mode=='delayed' else 0)+[('s',status,0)];want=list(wait);limit=32 if mode=='stop' else 64
    for i in range(limit):
        value=0x77110000+i;want += [('r',P+4*i,value),('w',page+4*i,value)];want += [('s',status,2)]*8 if mode=='stop' and i==31 else wait
    ck(ev==want and words==limit and pc==(0x18f2a if mode=='stop' else 0x18f36))
print('PASS: 6 full page-loop traces, 3 partial busy traces; no duplicate data stores during polls')
```
