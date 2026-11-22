# 最後一個 word 已寫，不等於寫頁回呼已返回

接續[資料迴圈](v4160-page-write-loop-trace.zh-TW.md)。從最後一次資料 store 已完成、位移仍為 252 的 `0x18f2a` 起，使用 v4.1.60 原 APP 指令一路追到回呼返回點。三次等待按下表排序；等待中的分支只回到該次狀態讀取，不會再寫頁資料。

|讀取 PC|條件滿足才前進|若停在此處|
|---|---|---|
|`0x18f2a`|儲存控制器狀態 bit 1 為 0|最後一次位移加 4 還沒執行。|
|`0x18f44`|同一狀態 word 的 bit 0 為 0|迴圈已退出，但 `0x18ef2` 尚未返回。|
|`0x1978c`|計時器狀態 bit 0 為 **1**|`0x18ef2` 與 `0x18eb6` 均已返回，寫頁回呼還沒還原自己的堆疊。|

只有第三關通過後，`0x197e6/0x197e8` 才重讀保存的 ra、s0，將 a0 設為零並還原 SP。在已核對的 caller frame 下返回 `0x440c0`，而不是直接返回 APP 初始化出口。計時器參數使用 `gp+382` 的 byte 乘以 1；不能從該數值反推出裝置上的實際等待時間。這段正常路徑的九筆 store 都是外設 word，不寫 `cfg+48`。結論限於所列指令、成功存取與未變的保存區；不保證裝置會給出任一退出條件。

重跑：傳 decoded APP、rasm2 路徑。三關各自延遲 0/1/3 次再通過，另在每一關連續八次未就緒後停下。每次狀態採樣保留無關高位，不把整個暫存器簡化成零／非零。

```python
from pathlib import Path
from hashlib import sha256
from itertools import product
import re,subprocess,sys
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v:raise ValueError('write return waits mismatch')
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667');code={}
for lo,hi in [(0x18f2a,0x18f56),(0x197dc,0x197f0),(0x18eb6,0x18ec4),(0x19764,0x1979a)]:
    p=lo
    for line in subprocess.check_output([sys.argv[2],'-a','riscv','-b','32','-s',hex(lo),'-D',b[lo-0x8000:hi-0x8000].hex()],text=True).splitlines():
        addr,n,h,o,*x=line.split();n=int(n);ck(int(addr,16)==p and bytes.fromhex(h)==b[p-0x8000:p-0x8000+n]);code[p]=n,o,''.join(x).split(',');p+=n
    ck(p==hi)
F=0x40022000;T=0xe000f000;S=0x2000ff00;G=0x20004000;M=0xffffffff;gates=[0x18f2a,0x18f44,0x1978c];dest=[F+16]*3+[T+4,T+16,T+20,T,T,T]
for delays in list(product((0,1,3),repeat=3))+[(-1,0,0),(0,-1,0),(0,0,-1)]:
    pc=gates[0];r=dict(sp=S,gp=G,a4=F,a2=256,a5=252,ra=0x197dc);mem={F+16:0x10000,T+4:9,T:2,G+382:73,S+28:0x440c0,S+24:0x200031ec};reads=[];writes=[];returns=[]
    for _ in range(220):
        if pc==0x440c0 or (pc in gates and delays[gates.index(pc)]<0 and reads.count(pc)==8):break
        here=pc;n,o,x=code[pc];pc+=n;t=x[0];v=lambda s:r[s] if s in r else int(s,0)
        if o in ('lw','lbu','sw'):
            d,k=re.fullmatch(r'(\d+)\((\w+)\)',x[1]).groups();a=r[k]+int(d)
            if o=='sw':mem[a]=r[t];writes.append((a,r[t]))
            elif here in gates:
                j=gates.index(here);ck(a==(F+12 if j<2 else T+4));ready=0<=delays[j]<=reads.count(here);reads.append(here);r[t]=0x80|((2,1,0)[j] if not ready else (0,0,1)[j])
            else:r[t]=mem[a]&(255 if o=='lbu' else M)
        elif o in ('li','lui'):r[t]=(v(x[1])<<(12 if o=='lui' else 0))&M
        elif o in ('addi','andi','and','ori','or','mul'):
            l,h=map(v,x[1:]);r[t]=(l+h if o=='addi' else l*h if o=='mul' else l&h if o.startswith('and') else l|h)&M
        elif o=='bne':pc=v(x[2]) if r[t]!=v(x[1]) else pc
        elif o in ('bnez','beqz'):pc=v(x[1]) if bool(r[t])==(o=='bnez') else pc
        elif o=='jal':r[t]=pc;pc=v(x[1])
        elif o=='ret':pc=r['ra']&~1;returns.append(pc)
        else:raise ValueError(o)
    expected=[]
    for gate,d in zip(gates,delays):
        expected += [gate]*(8 if d<0 else d+1)
        if d<0:break
    j=delays.index(-1) if -1 in delays else 3;count=(0,1,8,9)[j];ck(reads==expected and [a for a,_ in writes]==dest[:count] and pc==(gates+[0x440c0])[j])
    ck(returns==[0x197dc,0x197e0,0x197e6,0x440c0][:(0,0,2,4)[j]])
    if j==3:ck(r['a0']==0 and r['s0']==0x200031ec and r['sp']==S+32 and writes[4:6]==[(T+16,73),(T+20,0)])
print('PASS: 27 returns to 0x440c0; 3 bounded waits; 9 peripheral stores on return')
```
