"""Validate bounded prefix branch targets after TX loop relocation."""
from pathlib import Path
import json,subprocess,sys
root=Path(__file__).resolve().parents[2]
paths=(
 root/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin',
 root/'artifacts/offline-images/ID2966-V4.1.60-tx-integrated/NOT-FLASH-VALIDATED-tx-integrated.bin',
)
start,end=0x8a56,0x8b0a
expected={0x8a5a:0x8b6c,0x8a76:0x8a96,0x8a7e:0x8a96,0x8a92:0x8acc,
          0x8a9a:0x8abe,0x8aa2:0x8abe,0x8aba:0x8ace}
def read(path,pc,size):
    if path.stat().st_size!=76800: raise ValueError('unexpected image size')
    if not (0x8a56<=pc and pc+size<=0x8b6e): raise ValueError('outside bounded TX')
    with path.open('rb') as f:
        f.seek(pc-0x8000)
        data=f.read(size)
    if len(data)!=size: raise ValueError('short window')
    return data
def target(w,pc):
    imm=((w>>31)&1)<<12|((w>>7)&1)<<11|((w>>25)&63)<<5|((w>>8)&15)<<1
    if imm&0x1000: imm-=0x2000
    return pc+imm
for path in paths:
    data=read(path,start,end-start); offsets=[];edges={};indirect=[];returns=[]
    pos=0
    while pos<len(data):
        pc=start+pos; half=int.from_bytes(data[pos:pos+2],'little')
        width=4 if half&3==3 else 2
        if pos+width>len(data): raise ValueError('truncated instruction')
        offsets.append(pc)
        if width==2:
            funct3=half>>13;quadrant=half&3
            if quadrant==1 and funct3 in (1,5,6,7):
                raise ValueError('unexpected compressed direct control transfer')
            if half==0x8082:
                returns.append(pc)
            elif half&0xf07f in (0x8002,0x9002):
                indirect.append(pc)
        else:
            w=int.from_bytes(data[pos:pos+4],'little');opcode=w&127
            if opcode==0x63: edges[pc]=target(w,pc)
            elif opcode==0x6f: raise ValueError('unexpected JAL')
            elif opcode==0x67: indirect.append(pc)
        pos+=width
    if len(offsets)!=62 or edges!=expected: raise ValueError('prefix direct edges changed')
    if indirect!=[0x8a8e,0x8ab4]: raise ValueError('indirect calls changed')
    if returns!=[0x8aca]: raise ValueError('prefix return changed')
    if any(dest not in offsets and dest!=0x8b6c for dest in edges.values()):
        raise ValueError('branch to unexpected boundary')
    if read(path,0x8b6c,2)!=bytes.fromhex('8280'): raise ValueError('shared return changed')
for check in ('check-prefix.py','check-loop.py','check-tail.py'):
    subprocess.run([sys.executable,'-B',str(Path(__file__).with_name(check))],
                   stdout=subprocess.DEVNULL,check=True)
print(json.dumps({'prefix_instructions':62,'direct_branches':len(expected),
 'prefix_indirect_calls':2,'prefix_return':'0x8aca','direct_targets':'prefix boundaries or shared return',
 'loop_and_tail_checks':'passed','scope':'static local CFG; indirect targets, exceptions and external entries unverified',
 'excluded_app_read':False,'target_executed':False}))
