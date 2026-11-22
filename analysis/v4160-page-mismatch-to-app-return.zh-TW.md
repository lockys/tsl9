# 讀頁不等：APP 狀態相同，快取欄位未必相同

從 `0x44058` 重讀到兩個不相等的 word 起，追到 APP `0x19aee`。使用 V1.31 參考指令、名義堆疊、三頁設定及任務表；把配置、填值、寫頁及釋放各自當成正常返回的呼叫邊界，不以此證明 provider 的內部效果。

|第二次配置|`0x44022` 呼叫者本體的寫入（不含被呼叫者）|內層 / APP 返回值|
|---|---|---|
|返回零|把零寫入 `0x200031bc`；保留相鄰 `0x200031c0`|1 / 0|
|返回 P|存 P；三次把頁址寫到同一個 `[P]`；釋放正常返回後將上述兩個快取 word 均清零|0 / 0|

兩條路徑隨後都有[相同的四次登記寫入](v4160-page-equal-to-app-return.zh-TW.md)。因此不能用 APP 收到 0 判斷配置成功或相鄰 word 已清零。在此名義模型中，直接寫址都與 `cfg+48` 分離；真正的限制是 [配置失敗回呼](v4160-clock-hook-second-alloc-failure.zh-TW.md)、[寫頁回呼與 P 的重讀](v4160-44090-reloaded-buffer.zh-TW.md)及[釋放的條件寫址](v4160-44098-release-write-set.zh-TW.md)。如果任一呼叫不返回，便沒有本報告所述的 APP 返回值。

重跑：傳入 V1.31 carrier 與 rasm2 路徑。以下只執行 caller 指令；外部呼叫檢查目的及參數，注入合成返回、不改 RAM。只統計 caller 的 store。兩個不同快取初值用來區分「保留」與「清零」。

```python
from pathlib import Path
from hashlib import sha256
import sys,re,subprocess
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x:raise ValueError('mismatch return trace')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22');code={}
wch={0x44060:('4a24','lhu','a0,12(s0)'),0x4407e:('5224','lhu','a2,12(s0)'),0x4408e:('7c24','lbu','a5,14(s0)'),0x440ac:('4e24','lhu','a1,12(s0)'),0x43c06:('1c30','lbu','a5,1(s0)'),0x43c3e:('18b0','sb','a4,1(s0)')}
for lo,hi in [(0x44038,0x44046),(0x44058,0x440c2),(0x43c06,0x43c4e),(0x43d4e,0x43d5c)]:
    p=lo
    for line in subprocess.check_output([sys.argv[2],'-a','riscv','-b','32','-s',hex(lo),'-D',b[lo-0x40000:hi-0x40000].hex()],text=True).splitlines():
        addr,n,raw,o,*args=line.split();n=int(n);ck(int(addr,16)==p and bytes.fromhex(raw)==b[p-0x40000:p-0x40000+n]);args=''.join(args)
        if p in wch:h,o,args=wch[p];ck(h==raw)
        code[p]=n,o,args.split(',');p+=n
    ck(p==hi)
S,C,K,T,A,N=0x2000ff20,0x200031ec,0x200031bc,0x200047f4,0x08077c00,0x2000319d
for P in (0,0x20004b00):
 for tag in (0,0x12345678):
  for idx in (0,1,253,254,255):
    r=dict(sp=S,s0=C,a0=0,zero=0);mem={};wr=[];calls=[];rets=[];pc=0x44058
    def put(p,w,v):mem.update({p+i:v>>(i*8)&255 for i in range(w)})
    def get(p,w):return sum(mem[p+i]<<(i*8) for i in range(w))
    for p,v in [(C+8,A),(C+48,0x197b8),(C+60,0x197be),(K+4,tag),(S+12,A^1),(S+28,0x43c06),(S+24,N-1),(S+20,0x20003000),(S+16,0),(S+44,0x43d4e),(S+40,0),(S+36,0),(S+60,0x19aee),(S+56,0),(S+52,0),(0x200031c4,T)]:put(p,4,v)
    put(C+12,2,256);put(C+14,1,3);put(N,1,idx)
    for _ in range(160):
        if pc==0x19aee:break
        here=pc;n,o,x=code[pc];pc+=n;t=x[0];val=lambda k:r[k] if k in r else int(k,0)
        def addr(s):
            d,k=re.fullmatch(r'(-?\d+)\((\w+)\)',s).groups();return (r[k]+int(d))&0xffffffff
        if o in ('lw','lbu','lhu','sb','sw'):
            p=addr(x[1]);w={'lw':4,'lbu':1,'lhu':2,'sb':1,'sw':4}[o]
            if o[0]=='l':r[t]=get(p,w)
            else:v=r[t]&((1<<(8*w))-1);put(p,w,v);wr.append((p,w,v))
        elif o in ('li','mv','lui','auipc'):r[t]=(val(x[1])*(4096 if o in ('lui','auipc') else 1)+(here if o=='auipc' else 0))&0xffffffff
        elif o in ('add','addi','slli','srli','andi','mul'):
            l,h=map(val,x[1:]);r[t]=(l*h if o=='mul' else l<<h if o=='slli' else l>>h if o=='srli' else l&h if o=='andi' else l+h)&0xffffffff
        elif o=='jalr':
            dest=(addr(t) if '(' in t else r[t])&~1;argc={0x20000040:2,0x2000039c:3,0x197be:3,0x20000110:1}[dest];calls.append((dest,*(r['a'+str(i)] for i in range(argc))));r['ra']=pc;r['a0']=P if dest==0x20000040 else 0x55
        elif o=='beqz':pc=val(x[1]) if not r[t] else pc
        elif o=='beq':pc=val(x[2]) if r[t]==val(x[1]) else pc
        elif o=='blt':pc=val(x[2]) if (r[t]^0x80000000)<(val(x[1])^0x80000000) else pc
        elif o=='j':pc=val(t)
        elif o=='ret':pc=r['ra']&~1;rets.append((pc,r['a0']))
        else:raise ValueError(o)
    pages=[A+i*256 for i in range(3)];inner=int(not P);suffix=[(T+4*idx,4,0x432a4),(T+4*((idx+1)&255),4,0x43326),(N,1,(idx+3)&255),(T+4*((idx+2)&255),4,0x43326)]
    ck(calls==[(0x20000040,256,78)]+([(0x2000039c,P,255,256)]+[(0x197be,p,64,P) for p in pages]+[(0x20000110,P)] if P else []))
    ck(wr==[(K,4,P)]+([(P,4,p) for p in pages]+[(K,4,0),(K+4,4,0)] if P else [])+suffix)
    ck(pc==0x19aee and rets==[(0x43c06,inner),(0x43d4e,inner),(pc,0)] and r['sp']==S+64 and get(K+4,4)==(0 if P else tag) and get(C+48,4)==0x197b8)
print('PASS: 20 mismatch traces; both exits reach APP status 0; neighboring cache word differs')
```
