# 256-byte 配置失敗：何時才讀取 cfg+52？

`0x4406a` 這次呼叫的標記是 `0x004e`，不是稍後讀頁所用的 `0x4e01/02`。在 V1.31 搬移後的配置器中，256 大於分界 52，故讀 **大區塊游標 `0x20003190`**，而非小區塊游標 `0x20003194`。`0x20000088` 讀終止節點指標，`0x2000008c` 比較；每次跳過不合用的區塊，只從其 header 取後繼再比較，沒有把 cfg+52 暫存在迴圈內。

* 依[設定來源](v4160-allocator-failure-slot-origin.zh-TW.md)及[第二次配置前的寫址](v4160-second-allocation-frontier.zh-TW.md)，在指定初始化、有效 heap 與堆疊、參考回呼正常返回且無干擾的條件下，`0x20003220`（cfg+52）仍為零。更嚴格的名義布局有足夠空間，連終止節點分支都不需要走。
* 若搜尋確實抵達終止節點，`0x20000094` **此時才讀** cfg+52。讀到零就轉 `0x2000005a` 還原外設控制值，設 a0=0；沒有失敗回呼。讀到非零才到 `0x200000a0` 間接呼叫，參數為 `(1,0x0100004e)`，即 `(256 << 16) | 78`。後者的副作用未知，不能靠配置器最後返回零來排除。這一槽不是校準回呼槽 cfg+48。

重現：傳入 V1.31 carrier 和 rasm2 路徑。使用兩種合成串列（游標已是終止節點、先跳過一個佔用區塊），各測零與非零失敗回呼；比對**完整載入順序**。從參數已通過非零檢查的 `0x20000066` 起，停在零結果出口或間接呼叫前，不執行未知回呼或設備。`0x200000ae` 依 Xwchc 解讀為從 header+6 讀半字。

```python
from hashlib import sha256
from pathlib import Path
import sys,subprocess,re
def ck(v):
    if not v: raise ValueError('second alloc trace mismatch')
b=Path(sys.argv[1]).read_bytes();ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22' and b[0x4062:0x4066].hex()=='9305e004');base=0x20000040;code={}
for line in subprocess.check_output([sys.argv[2],'-a','riscv','-b','32','-s',hex(base),'-D',b[0x2b0:0x380].hex()],text=True).splitlines():
    h,n,raw,o,*args=line.split();p=int(h,16);i=0x2b0+p-base;ck(b[i:i+int(n)]==bytes.fromhex(raw));code[p]=int(n),o,''.join(args).split(',')
H=0x200045ac;E=0x2000b184;S=0x20003220
for head in (E,H):
    for hook in (0,0x1000):
        r=dict(a0=256,a1=78,s0=0x12345678);mem={0x20003190:head,0x2000318c:E,H+6:1,H:E,S:hook};pc=base+0x26;loads=[];stores=[]
        for _ in range(64):
            if pc in (base+0x60,base+0xc4):break
            at=pc;n,o,x=code[pc];pc+=n;t=x[0];v=lambda k:r[k] if k in r else int(k,0)
            if at==base+0x6e:ck(b[0x31e:0x320].hex()=='7a21');addr=r['a0']+6;loads.append(addr);r['a4']=mem[addr]&65535
            elif o in ('lw','sw'):
                d,k=re.fullmatch(r'(\d+)\((\w+)\)',x[1]).groups();addr=r[k]+int(d)
                if o=='lw':loads.append(addr);r[t]=mem[addr]
                else:stores.append((addr,r[t]))
            elif o in ('lui','li'):r[t]=v(x[1])<<(12 if o=='lui' else 0)
            elif o in ('addi','slli','srli','andi','or'):
                l,h=map(v,x[1:]);r[t]=(l+h if o=='addi' else l<<h if o=='slli' else l>>h if o=='srli' else l&h if o=='andi' else l|h)&0xffffffff
            elif o=='j':pc=v(t)
            elif o in ('bltu','bne','beqz','bnez'):
                take=r[t]<v(x[1]) if o=='bltu' else r[t]!=v(x[1]) if o=='bne' else (r[t]==0)==(o=='beqz');pc=v(x[-1]) if take else pc
            else:raise ValueError(o)
        ck(loads==[0x20003190,0x2000318c]+([H+6,H] if head==H else [])+[S]);ck((pc,r['a0'],stores)==((base+0x60,1,[]) if hook else (base+0xc4,0,[(0x4002420c,0x12345678)])))
        if hook:ck(code[pc][1:]==('jalr',['a4']) and r['a4']==hook and r['a1']==0x0100004e)
print('PASS: 4 sentinel traces; live hook read, call arguments and null exit verified')
```
