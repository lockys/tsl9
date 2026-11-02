#!/usr/bin/env python3
"""Check the model's source instruction window, without executing the target."""
import argparse,hashlib,json,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--firmware',type=Path,required=True);p.add_argument('--r2',type=Path,required=True);a=p.parse_args()
data=a.firmware.read_bytes()
if len(data)!=76800 or hashlib.sha256(data).hexdigest()!='28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89':raise ValueError('Candidate image changed')
expected={0x14230:'addi a5, a1, 86',0x14234:'andi a5, a5, 255',0x14238:'li a4, 1',0x1423a:'bltu a4, a5, 0x141fa',
0x1423e:'sw a1, 12(sp)',0x14240:'jal ra, 0x81aa',0x14244:'lw a1, 12(sp)',0x14246:'bnez a0, 0x141fa',
0x14248:'li a3, 0',0x1424a:'li a2, 300',0x1424e:'li a1, 0',0x14250:'auipc a0, 0x0',0x14254:'addi a0, a0, -712',0x14258:'jal ra, 0x9124',0x1425c:'j 0x14098',
0x1425e:'li a5, 193',0x14262:'bltu a5, a1, 0x1427a',0x14266:'li a5, 192',0x1426a:'bleu a5, a1, 0x1423e',
0x1426e:'addi a5, a1, 71',0x14272:'andi a5, a5, 255',0x14276:'li a4, 2',0x14278:'j 0x1423a',
0x1427a:'li a5, 208',0x1427e:'beq a1, a5, 0x1423e',0x14282:'li a5, 240',0x14286:'j 0x141f6',
0x81aa:'lbu a0, 167(gp)',0x81ae:'ret',
0x186de:'addi a0, gp, 128',0x186e2:'auipc a1, 0x1fff4',0x186e6:'addi a1, a1, 630',
0x186ea:'bleu a1, a0, 0x186f8',0x186ee:'sw zero, 0(a0)',0x186f2:'addi a0, a0, 4',0x186f4:'bltu a0, a1, 0x186ee'}
cmd=[str(a.r2),'-q','-a','riscv','-b','32','-m','0x8000','-c','s 0x14230; pdj 27',str(a.firmware)]
ops=json.loads(subprocess.run(cmd,capture_output=True,text=True,check=True).stdout)
for start,count in ((0x81aa,2),(0x186de,7)):
    cmd=[str(a.r2),'-q','-a','riscv','-b','32','-m','0x8000','-c',f's {start}; pdj {count}',str(a.firmware)]
    ops+=json.loads(subprocess.run(cmd,capture_output=True,text=True,check=True).stdout)
actual={x['addr']:x['opcode'].lower() for x in ops}
if actual!=expected:raise ValueError('Dispatcher instruction evidence changed')
assert 0x14250-712==0x13f88
assert 0x186e2+0x1fff4000+630==0x2000c958
assert 0x20004000+128<=0x20004000+167<0x2000c958
negative=dict(actual);negative[0x14262]='bgeu a5, a1, 0x1427a';assert negative!=expected
print(json.dumps({'passed':True,'instructions':len(expected),'synthetic_negative_control':True,'target_executed':False}))
