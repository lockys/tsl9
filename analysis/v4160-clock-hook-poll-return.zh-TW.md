# 輪詢成功後：回傳低 16 位，並寫回 16 個外設快照

若[輪詢](v4160-clock-hook-poll.zh-TW.md)已退出，令 B=`0x40012400`、F 為 `0x197f0` 的 frame SP。`0x198dc → 0x18a66` 對 B+76 做 **32-bit 讀取**，移位取低 16 位（不帶符號），在 `0x198e0` 將結果以 word 存到 F+28。這不是輪詢的 B+0，也不是 16-bit 匯流排讀取。

`0x198e6 → 0x188e2(B)` 再把 `0x198ea` 保存到 F−4；在 `0x4002100c` 設 bit 9，再重新讀取並清 bit 9。隨後依序寫回先前快照的 16 個 **word**：`0x40021018、0x40021004`，再到 B 加上 `4、8、44、48、52、12、16、20、24、28、32、36、40、56`。頭十個值來自 s11..s2，最後六個取自 F+4..+24。這是寫回先前的值，不等於實際外設狀態完全恢復。`0x1991e` 重讀 F+28，`0x19948` 將它移入 a0；最後以還原的 ra 返回。若回到 V1.31 參考呼叫者，`0x43d3e` 只寫結果低半字至 `0x200031a4`。

因此名義非別名堆疊、記憶體讀寫成功且正常返回時，此尾段不直接寫 `0x2000321c`。測試對 16 個快照給不同值，以免寫錯順序仍通過；另分開提供兩次外設讀值。此處不保證輪詢成功、裝置使用該 ROM 或沒有中斷。重現時依序傳 decoded APP 與 rasm2 路徑：

```python
from pathlib import Path
from hashlib import sha256
import sys,subprocess,re
def ck(v):
    if not v: raise ValueError('return trace mismatch')
b=Path(sys.argv[1]).read_bytes();ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667');code={}
for p,e in [(0x198d8,0x1995c),(0x18a66,0x18a6e),(0x188e2,0x1890a),(0x19160,0x1917e)]:
    for l in subprocess.check_output([sys.argv[2],'-a','riscv','-b','32','-s',hex(p),'-D',b[p-32768:e-32768].hex()],text=True).splitlines():
        h,n,raw,o,*args=l.split();n=int(n);ck(int(h,16)==p and bytes.fromhex(raw)==b[p-32768:p-32768+n]);code[p]=(n,o,''.join(args).split(','));p+=n
    ck(p==e)
B=0x40012400;F=0x2000fed0;P=0x4002100c;M=0xffffffff
for sample in (0,0x12348000,0xffff0000,0xa5a5ffff):
    snap=[0x100+i for i in range(16)];r={'s0':B-1024,'sp':F,**{'s'+str(11-i):x for i,x in enumerate(snap[:10])}};saved={F+124:0x43d3a,**{F+120-4*i:0x900+i for i in range(12)}};mem={**saved,**{F+4+4*i:x for i,x in enumerate(snap[10:])},B+76:sample};reads=[];writes=[];pc=0x198d8;ports=iter((0x41,0x80000242))
    for _ in range(150):
        if pc==0x43d3a:break
        n,o,x=code[pc];pc+=n;t=x[0];v=lambda k:r[k] if k in r else int(k,0)
        if o in ('lw','sw'):
            off,reg=re.fullmatch(r'(\d+)\((\w+)\)',x[1]).groups();addr=int(off)+r[reg]
            if o=='lw':reads.append(addr);r[t]=next(ports) if addr==P else mem[addr]
            else:writes.append((addr,r[t]));mem[addr]=r[t]
        elif o=='jal':ck(t=='ra');r[t]=pc;pc=v(x[1])
        elif o=='j':pc=v(t)
        elif o=='ret':pc=r['ra']&~1
        elif o=='bne':pc=v(x[2]) if r[t]!=v(x[1]) else pc
        elif o=='beqz':pc=v(x[1]) if not r[t] else pc
        elif o in ('mv','li','lui'):r[t]=(v(x[1])<<(12 if o=='lui' else 0))&M
        elif o=='not':r[t]=~v(x[1])&M
        elif o in ('addi','and','or','slli','srli'):
            a,c=map(v,x[1:]);r[t]=(a+c if o=='addi' else a&c if o=='and' else a|c if o=='or' else a<<c if o=='slli' else a>>c)&M
        else:raise ValueError(o)
    dst=[0x40021018,0x40021004]+[B+i for i in (4,8,44,48,52,12,16,20,24,28,32,36,40,56)]
    ck(writes==[(F+28,sample&65535),(F-4,0x198ea),(P,0x241),(P,0x80000042)]+list(zip(dst,snap)))
    ck(reads.count(B+76)==1 and reads.count(P)==2 and pc==0x43d3a and r['a0']==sample&65535 and r['sp']==F+128 and all(r['s'+str(i)]==0x900+i for i in range(12)))
print('PASS: 4 result patterns; 20 ordered word stores, 16 distinct snapshots, restored return state')
```
