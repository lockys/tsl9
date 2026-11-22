"""CLI: python SCRIPT reference-carrier.bin rasm2. Caller-only RV32 trace.
External calls return synthetically, preserving saved registers and stack. No device I/O.
"""
from hashlib import sha256
from pathlib import Path
import re, subprocess, sys

START, END = 0x6d572, 0x6d682
ID, CFG = 0x200035f5, 0x20003201

def check(ok, label):
    if not ok: raise ValueError(label)

def ledger(path, tool):
    b=Path(path).read_bytes();check(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22','identity')
    raw=b[START-0x40000:END-0x40000]; text=subprocess.check_output([tool,'-a','riscv','-b','32','-s',hex(START),'-D',raw.hex()],text=True)
    pc=START; code={}
    for line in text.splitlines():
        a,n,h,o,*args=line.split(); n=int(n);check(int(a,16)==pc and bytes.fromhex(h)==raw[pc-START:pc-START+n],'instruction span')
        code[pc]=(n,o,[k.rstrip(',') for k in args]);pc+=n
    check(pc==END,'end');return code

def trace(code, cfg, shared, result, nested):
    sp=0x2000ffc0; link=0x8eb8; pc=START
    r=dict(sp=sp,ra=link,s0=12,s1=13,s2=14,zero=0); m={CFG:cfg,ID:shared}; calls=[]; idwrites=[]; loads=[]
    def v(k):return r[k] if k in r else int(k,0)
    def addr(k):
        d,b=re.fullmatch(r'(-?\d+)\((\w+)\)',k).groups();return (r[b]+int(d))&0xffffffff
    for _ in range(120):
        if pc==link:break
        at=pc;n,o,x=code[pc];pc+=n;t=x[0] if x else ''
        if o in ('sb','sw','lw','lbu'):
            p=addr(x[1]);w=4 if o in ('sw','lw') else 1
            if o in ('sb','sw'):
                for i in range(w):m[p+i]=v(t)>>(8*i)&255
                if p==ID:idwrites.append((at,m[p]))
            else:r[t]=sum(m[p+i]<<(8*i) for i in range(w));loads.append(p)
        elif o in ('li','lui','auipc','addi','andi'):
            y=v(x[1]);z=v(x[2]) if len(x)>2 else 0
            r[t]=(y if o=='li' else y<<12 if o=='lui' else at+(y<<12) if o=='auipc' else y+z if o=='addi' else y&z)&0xffffffff
        elif o in ('bnez','bne','beq'):
            same=v(t)==(0 if o=='bnez' else v(x[1]));pc=v(x[-1]) if same==(o=='beq') else pc
        elif o in ('jal','jalr'):
            dest=v(x[-1]) if o=='jal' else addr(t)&~1; calls.append((dest,r.get('a0')));r['ra']=pc;r['a0']=result if dest==0x43c4e else nested
        elif o=='j':pc=v(t)
        elif o=='ret':pc=r['ra']&~1
        else:raise ValueError((at,o))
    check((pc,r['sp'],r['s0'],r['s1'],r['s2'])==(link,sp,12,13,14),'return frame')
    gate=bool(cfg&3);attempt=gate and shared==255;success=attempt and result!=255
    check((ID in loads)==gate and idwrites==([(0x6d5b6,result)] if attempt else []),'ID access')
    check(calls[:int(attempt)]==([(0x43c4e,0x6d26c)] if attempt else []),'registration argument')
    check([p for p,_ in calls[int(attempt):]]==([0x4600e,0x2000039c,0x2000039c,0x440c2,0x440c2,0x20000332,0x20000332,0x440c2] if success else []),'nested call order')
    check(r['a0']==(0 if success else 24),'status')

if __name__=='__main__':
    code=ledger(*sys.argv[1:]);count=0
    for cfg in (0,1,2,3,252,253,254,255):
        for shared in range(256):
            for result in ((0,11,254,255) if shared==255 else (11,)):
                for nested in (0,255):trace(code,cfg,shared,result,nested);count+=1
    print(f'PASS: {count} caller traces; all four exit classes return to 8eb8; successful path ignores eight injected callee results')
