"""V1.31 reference BIN, rasm2: default callback branch up to the next helper.
Synthetic RAM/peripheral samples, no interrupts; not a live binding or device test.
"""
import hashlib,re,subprocess,sys
from pathlib import Path
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v:raise ValueError('default branch mismatch')
ck(hashlib.sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
code={}
for lo,hi in [(0x55634,0x5563a),(0x63e58,0x63eda),(0x556d0,0x556d8)]:
    p=lo; z=b[lo-0x40000:hi-0x40000]
    for line in subprocess.check_output([sys.argv[2],'-a','riscv','-b','32','-s',hex(lo),'-D',z.hex()],text=True).splitlines():
        a,n,h,op=line.split(maxsplit=3);n=int(n);ck(int(a,16)==p and bytes.fromhex(h)==z[p-lo:p-lo+n]);code[p]=(p+n,op.replace(',','').split());p+=n
    ck(p==hi)
T,X,B=0x40024200,0x40024100,0x40025000
for desc in (0,0x20006000):
    for sample in (0,8):
        r={'zero':0,'s0':0x20005000};m={0x2000353c:T,0x20003508:X,0x20003590:B,0x2000350c:desc,T:4,T+80:15,X:0xffff,B+8:0xffffffff};ws=[];pc=0x55634
        if desc:m.update({desc+4:X+4,desc+8:16,desc+16:X+12,desc+20:64,X+4:2,X+12:4})
        for step in range(100):
            if pc==0x53d98:break
            at=pc;pc,x=code[pc];op=x[0];t=x[1] if len(x)>1 else None
            if op in ('lw','sw','sb'):
                d,k=re.fullmatch(r'(-?\d+)\((\w+)\)',x[2]).groups();p=r[k]+int(d)
                if op=='lw':r[t]=sample if at==0x63e6e else m[p]
                else:m[p]=r[t] if op=='sw' else r[t]&255;ws.append((p,4 if op=='sw' else 1,m[p]))
            elif op=='jal':r['ra']=pc;pc=int(x[-1],0)
            elif op=='j':pc=int(t,0)
            elif op=='ret':pc=r['ra']
            elif op=='beqz':pc=int(x[2],0) if r[t]==0 else pc
            elif op=='lui':r[t]=int(x[2],0)<<12
            elif op=='mv':r[t]=r[x[2]]
            elif op not in ('nop',):
                y=r[x[2]];v=r[x[3]] if op in ('or','and') else int(x[3],0)
                r[t]={'or':y|v,'ori':y|v,'and':y&v,'andi':y&v,'addi':y+v,'srli':y>>(v&31)}[op]&0xffffffff
        expected=[(T+80,4,8),(T,4,12),(X,4,0xfeff),(B+8,4,0xffcdffff),(T+80,4,0)]
        if desc:expected.extend([(X+4,4,18),(X+12,4,68)])
        ck(ws==expected+[(0x2000351b,1,0)] and pc==0x53d98 and r['ra']==0x556d6 and r['a0']==0x20005000)
print('PASS: 4 default-branch traces; 6/8 ordered stores; next call 0x53d98(object)')
