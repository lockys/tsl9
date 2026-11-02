#!/usr/bin/env python3
"""Check bounded dispatcher instructions and conditional pointer overlap offline."""
import argparse, hashlib, json, subprocess
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--firmware',type=Path,required=True)
p.add_argument('--r2',type=Path,required=True)
a=p.parse_args()
blob=a.firmware.read_bytes()
if len(blob)!=76800 or hashlib.sha256(blob).hexdigest()!='28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89':
    raise SystemExit('Unexpected candidate image')
expected={0x142fc:'addi s1, gp, 84',0x1432e:'lui s2, 0x40',0x14332:'lw a5, 76(s2)',
          0x14336:'lw a0, 0(s1)',0x14338:'li a2, 16',0x1433a:'addi a1, s0, 24',0x1433e:'jalr a5',
          0x14340:'lw a0, 0(s1)',0x14342:'lw a5, 76(s2)',0x14346:'li a2, 16',
          0x14348:'addi a1, s0, 59',0x1434c:'addi a0, a0, 96',0x14350:'jalr a5',
          0x1441c:'addi a5, gp, 84',0x14420:'lw a5, 0(a5)',0x14422:'lbu a4, 4(a5)',
          0x14426:'andi a4, a4, 8',0x14428:'beqz a4, 0x14438',0x1442a:'lbu a4, 4(a5)',
          0x1442e:'andi a4, a4, -9',0x14430:'sb a4, 4(a5)',
          0x186ba:'auipc a0, 0x2',0x186be:'addi a0, a0, 1190',0x186c2:'mv a1, gp',
          0x186c6:'addi a2, gp, 128',0x186ca:'bleu a2, a1, 0x186de',
          0x186ce:'lw t0, 0(a0)',0x186d2:'sw t0, 0(a1)',0x186d6:'addi a0, a0, 4',
          0x186d8:'addi a1, a1, 4',0x186da:'bltu a1, a2, 0x186ce'}
seen={}
for start,count in ((0x142fc,1),(0x1432e,12),(0x1441c,8),(0x186ba,10)):
    cmd=[str(a.r2),'-q','-a','riscv','-b','32','-m','0x8000','-c',f's {start}; pdj {count}',str(a.firmware)]
    result=subprocess.run(cmd,capture_output=True,text=True,check=True)
    for ins in json.loads(result.stdout):
        if ins['addr'] in expected:seen[ins['addr']]=ins['opcode'].lower()
if seen!=expected:raise ValueError('Dispatcher instruction mismatch')
def check(actual):return actual==expected
negative=dict(seen);negative[0x14338]='li a2, 15'
assert not check(negative)
gp=0x20004000
counter=gp+176
assert gp+172+4==counter and gp+80+96==counter
assert all((v & ~8)==v for v in range(4))
source=0x186ba+0x2000+1190
assert source==0x1ab60 and source+84==0x1abb4
initial=int.from_bytes(blob[0x1abb4-0x8000:0x1abb8-0x8000],'little')
assert initial==0x2000c29c
first=(initial,initial+16);second=(initial+96,initial+112)
targets=(gp+84,counter,gp+332,gp+333,gp+334,gp+335)
assert all(not lo<=target<hi for lo,hi in (first,second) for target in targets)
print(json.dumps({'passed':True,'pinned_instructions':len(expected),'negative_control':True,
 'copy1_counter_overlap_if_pointer_is_gp_plus':172,'copy2_counter_overlap_if_pointer_is_gp_plus':80,
 'clear_bit3_preserves_counter_values_0_to_3':True,'reset_initializer_pointer':hex(initial),
 'initial_pointer_copy_windows_avoid_tracked_state':True,'pointer_alias_proved':False,
 'installed_copy_slot_proved':False,'target_executed':False,'hardware_validated':False}))
