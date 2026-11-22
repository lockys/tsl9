"""V1.31 candidate 641b0: two Xwchc byte samples and one pointer guard, not hardware."""
from pathlib import Path
from hashlib import sha256
import re,subprocess,sys

def decode(blob,tool):
    if sha256(blob).hexdigest()!='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22':raise ValueError('wrong carrier')
    code={}
    for lo,hi in [(0x641b0,0x641fc),(0x64286,0x64298)]:
        p=lo;raw=blob[lo-0x40000:hi-0x40000]
        for line in subprocess.check_output([tool,'-a','riscv','-b','32','-s',hex(lo),'-D',raw.hex()],text=True).splitlines():
            addr,w,h,o,*args=line.split();w=int(w);x=''.join(args).split(',')
            if int(addr,16)!=p or bytes.fromhex(h)!=raw[p-lo:p-lo+w]:raise ValueError('decoder drift')
            if p in (0x641bc,0x641d0):
                if h!='7830':raise ValueError('wrong Xwchc encoding')
                o,x='lbu',['a4','7(s0)'] # conditional WCH interpretation, not standard fld
            code[p]=w,o,x;p+=w
        if p!=hi:raise ValueError('window size')
    return code

def check(code,first,second,ptr):
    S=0x2000ff40;RA=0x537b6;B=0x40024300;IO=0x4002420c;state=0x2000351b;word=0x20003504
    orig={'s'+str(i):0x12340000+i for i in range(6)};r=dict(orig,sp=S,ra=RA,zero=0);m={word:ptr,IO:0xf00f};reads=[];writes=[];pc=0x641b0
    for _ in range(40):
        if pc in (RA,0x63eda):break
        at=pc;n,o,x=code[pc];pc+=n;t=x[0]
        if o in ('lw','sw','lbu'):
            d,k=re.fullmatch(r'(-?\d+)\((\w+)\)',x[1]).groups();p=r[k]+int(d)
            if o=='sw':m[p]=r[t];writes.append((p,r[t]))
            else:
                r[t]=(first if at==0x641bc else second) if o=='lbu' else m[p];reads.append((p,r[t]))
        elif o=='jal':r['ra']=pc;pc=int(x[-1],0)
        elif o=='ret':pc=r['ra']&~1
        elif o in ('beq','bne'):
            if (r[t]==r[x[1]])==(o=='beq'):pc=int(x[-1],0)
        elif o=='lui':r[t]=int(x[1],0)<<12
        elif o=='li':r[t]=int(x[1],0)
        elif o=='addi':r[t]=r[x[1]]+int(x[2],0)
        elif o!='fence.i':raise ValueError((at,o))
    expected=[(state,first)];save=[(S-8,orig['s0']),(S-4,RA)]+[(S-8-4*i,orig['s'+str(i)]) for i in range(1,6)]
    if first!=4:expected.append((state,second))
    if first!=4 and second!=4:expected.append((word,ptr))
    go=first!=4 and second!=4 and ptr==B
    if go:
        expected.append((IO,0xf00f));valid=(pc,r['a0'],r['ra'],r['sp'],r['s4'])==(0x63eda,13,0x641fc,S-32,0xf00f)
    else:
        expected+=save[1:2]+save[:1]+save[2:];valid=pc==RA and r['sp']==S and all(r[k]==v for k,v in orig.items())
    if not valid or reads!=expected or writes!=save+([(IO,0)] if go else []):raise ValueError('guard, stack or IO mismatch')
    return go

if __name__=='__main__':
    c=decode(Path(sys.argv[1]).read_bytes(),sys.argv[2]);counts=[0,0]
    for a in range(256):
        for b in range(256):
            for p in (0x40024300,0x40024304):counts[check(c,a,b,p)]+=1
    print(f'PASS: {counts[0]} early returns, {counts[1]} calls with a0=13; exact ordered reads, writes and stack checked')
