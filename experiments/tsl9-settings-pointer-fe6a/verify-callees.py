#!/usr/bin/env python3
"""Verify selected FE6A callee instructions and bounded direct stores."""
import argparse,hashlib,json,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--firmware',type=Path,required=True);p.add_argument('--r2',type=Path,required=True);a=p.parse_args()
blob=a.firmware.read_bytes()
if len(blob)!=76800 or hashlib.sha256(blob).hexdigest()!='28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89':raise ValueError('Candidate image changed')
def window(start,end):
    cmd=[str(a.r2),'-q','-a','riscv','-b','32','-m','0x8000','-c',f's {start}; pdj {end-start}',str(a.firmware)]
    raw=json.loads(subprocess.run(cmd,capture_output=True,text=True,check=True).stdout)
    ops=[x for x in raw if start<=x['addr']<end]
    if not ops or ops[0]['addr']!=start or ops[-1]['addr']+ops[-1]['size']!=end:raise ValueError('Window bounds changed')
    return [(x['addr'],x['opcode'].lower()) for x in ops]
leaves={0x828c:(0x829e,[(0x828c,'auipc a0, 0x20004'),(0x8290,'lbu a0, -728(a0)'),(0x8294,'sltiu a0, a0, 4'),(0x8298,'xori a0, a0, 1'),(0x829c,'ret')]),
0x81ee:(0x81f8,[(0x81ee,'auipc a0, 0x20004'),(0x81f2,'lbu a0, -793(a0)'),(0x81f6,'ret')]),
0xa9de:(0xa9e8,[(0xa9de,'auipc a0, 0x20001'),(0xa9e2,'lbu a0, 1278(a0)'),(0xa9e6,'ret')])}
for start,(end,expected) in leaves.items():
    if window(start,end)!=expected:raise ValueError('Read-only leaf changed')
clock=window(0x81b0,0x81ca)
expected_clock=[(0x81b0,'lui a5, 0x40'),(0x81b4,'lw a5, 124(a5)'),(0x81b6,'addi sp, sp, -16'),(0x81b8,'sw ra, 12(sp)'),(0x81ba,'jalr a5'),(0x81bc,'li a5, 10'),(0x81be,'mul a0, a0, a5'),(0x81c2,'lw ra, 12(sp)'),(0x81c4,'addi sp, sp, 16'),(0x81c6,'srli a0, a0, 0x4'),(0x81c8,'ret')]
if clock!=expected_clock:raise ValueError('Clock wrapper changed')
cancel=window(0x90b0,0x9124);by=dict(cancel)
key={0x90b2:'auipc a5, 0x20003',0x90b6:'addi a5, a5, -682',0x90c4:'li a4, 15',0x90cc:'li a5, 12',0x90de:'jalr a5',0x90fe:'sw zero, 4(s1)',0x9102:'sw zero, 8(s1)',0x9106:'lw t1, 92(a5)',0x910e:'jr t1',0x9114:'bne s0, a4, 0x90c6'}
if any(by.get(k)!=v for k,v in key.items()):raise ValueError('Cancel function key instruction changed')
stores=[x for x in cancel if x[1].split()[0] in ('sb','sh','sw','sd')]
expected_stores=[(0x90ba,'sw s0, 8(sp)'),(0x90bc,'sw s1, 4(sp)'),(0x90be,'sw ra, 12(sp)'),(0x90fe,'sw zero, 4(s1)'),(0x9102,'sw zero, 8(s1)')]
if stores!=expected_stores:raise ValueError('Unexpected cancel function store')
base=0x90b2+0x20003000-682;gp=0x20004000
assert base==0x2000be08 and 0x828c+0x20004000-728==0x2000bfb4 and 0x81ee+0x20004000-793==0x2000bed5 and 0xa9de+0x20001000+1278==0x2000bedc
for i in range(15):
    for offset in (4,8):
        assert not (base+12*i+offset<gp+88 and gp+84<base+12*i+offset+4)
bad=list(stores)+[(0x9100,'sw zero, 84(gp)')];assert bad!=expected_stores
print(json.dumps({'passed':True,'read_only_leaves':len(leaves),'clock_resident_indirect':True,'cancel_resident_indirect':True,'cancel_explicit_stores':len(stores),'negative_control':True,'callee_rom_effects_proved':False,'stack_nonoverlap_proved':False,'interrupts_proved':False,'target_executed':False}))
