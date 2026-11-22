"""Reference carrier and rasm2 args. Offline selected call/return/tail edge, not device IO."""
from pathlib import Path
from hashlib import sha256
import re,subprocess,sys
M=0xffffffff

def load(blob,tool):
    if sha256(blob).hexdigest()!='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22':raise ValueError('reference mismatch')
    code={}
    for lo,hi in [(0x638ea,0x63944),(0x64302,0x6430e)]:
        raw=blob[lo-0x40000:hi-0x40000];p=lo
        for line in subprocess.check_output([tool,'-a','riscv','-b','32','-s',hex(lo),'-D',raw.hex()],text=True).splitlines():
            addr,n,h,o,*args=line.split();n=int(n)
            if int(addr,16)!=p or bytes.fromhex(h)!=raw[p-lo:p-lo+n]:raise ValueError('decode mismatch')
            code[p]=(n,o,''.join(args).split(','));p+=n
        if p!=hi:raise ValueError('window mismatch')
    return code

def check(code,cfg,samples,sp):
    B=0x40024100;saved=0x537b6;pc=0x64302;r={'sp':sp};events=[];calls=[];i=0
    for _ in range(64):
        if pc==0x641b0:break
        at=pc;n,o,x=code[pc];pc+=n;t=x[0]
        if o in ('lw','lbu','sw'):
            d,k=re.fullmatch(r'(-?\d+)\((\w+)\)',x[1]).groups();p=(r[k]+int(d))&M
            if o=='sw':v=r[t]
            elif p in (B,B+44):v=samples[i];i+=1;r[t]=v
            else:v={sp+12:saved,0x20003508:B,0x20003200:cfg}[p];r[t]=v
            events.append((o,p,v))
        elif o=='jal':calls.append((at,pc));r['ra']=pc;pc=int(x[-1],0)
        elif o=='j':pc=int(t,0)
        elif o=='ret':pc=r['ra']&~1
        else:
            def val(a):return r[a] if a in r else int(a,0)
            y=val(x[1]);z=val(x[2]) if len(x)>2 else 0
            if o=='lui':v=y<<12
            elif o=='li':v=y
            elif o=='addi':v=y+z
            elif o=='slli':v=y<<(z&31)
            elif o=='or':v=y|z
            elif o in ('and','andi'):v=y&z
            else:raise ValueError((at,o))
            r[t]=v&M
    a,b,c=samples
    want=[('lw',0x20003508,B),('lw',B,a),('sw',B,a|0x800000),('lw',B,b),('sw',B,b|0x10000000),('sw',B+52,464),('lbu',0x20003200,cfg),('sw',B+44,0x80010ec8|((cfg&63)<<25)),('lw',B+44,c),('sw',B+44,(c&0x81ffffff)|((cfg&63)<<25)),('sw',B+32,0x90083),('lw',sp+12,saved)]
    if events!=want or calls!=[(0x64302,0x64306)] or (pc,r['sp'],r['ra'])!=(0x641b0,sp+16,saved):raise ValueError('call/IO/return mismatch')

if __name__=='__main__':
    code=load(Path(sys.argv[1]).read_bytes(),sys.argv[2]);count=0
    for cfg in range(256):
        for s in [(0,0,0),(M,M,M),(0,0xa5a5a5a5,0x12345678),(0x11223344,0,0x80000000)]:
            for sp in (0x2000ff40,0x2000ff60):check(code,cfg,s,sp);count+=1
    print(f'PASS: {count} traces; six stores, three independently supplied MMIO reads, return to 64306 and tail to 641b0')
