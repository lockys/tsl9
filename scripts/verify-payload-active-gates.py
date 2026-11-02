#!/usr/bin/env python3
"""Trace a conditional dispatcher state into two existing precheck gates."""
import argparse,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser();p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
a=p.parse_args();out=a.out.resolve()
if out.exists() or out==ROOT or ROOT in out.parents:raise SystemExit('Output must be a new directory outside the project')
out.mkdir(parents=True);base=out/'prior'
proc=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/verify-payload-type2-calls.py'),
                    '--tool-dir',str(a.tool_dir),'--out',str(base)],capture_output=True,text=True)
if proc.returncode:raise ValueError('Prior validation failed: '+proc.stderr[:1000])
f=json.loads(proc.stdout)
if not f['passed'] or f['hardware_validated'] or f['device_state_or_reachability_proved']:
    raise ValueError('Unexpected prior result')
tool=a.tool_dir/('llvm-objdump.exe' if (a.tool_dir/'llvm-objdump.exe').is_file() else 'llvm-objdump')
def decode(text):
    rows={}
    for line in text.splitlines():
        m=re.match(r'^\s*([0-9a-f]+):\s+(?:[0-9a-f]{2}\s+)+(.*?)\s*$',line)
        if m:rows[int(m[1],16)]=re.sub(r'\s+',' ',re.sub(r'\s*<[^>]*>','',m[2])).strip()
    return rows
checks={
 0x82d6:'lui s3, 0x10',0x82ee:'li s2, 0x0',0x82f0:'li s4, 0x0',
 0x82f2:'auipc s5, 0x20004',0x82f6:'addi s5, s5, 0x4a2',
 0x82fa:'addi s3, s3, -0x2',0x82fc:'li s6, 0x2',0x8308:'slli s0, s2, 0x2',
 0x830c:'add s0, s0, s5',0x830e:'lhu a5, 0x2(s0)',0x8312:'beq s3, a5, 0x836a',
 0x8316:'lbu a5, 0x5(s0)',0x831a:'bne s6, a5, 0x836a',
 0x831e:'lbu a5, 0x4(s0)',0x8322:'andi a5, a5, 0xff',0x8326:'beqz a5, 0x836a',
 0x832c:'mv s4, a5',0x836a:'beqz s2, 0x838a',0x8372:'mv a0, s4',
 0x838a:'li s2, 0x1',0x838c:'j 0x8308',
 0x83a4:'lui s4, 0x10',0x83ba:'li s3, 0x0',0x83bc:'li a0, 0x0',
 0x839c:'auipc s7, 0x20004',0x83a0:'addi s7, s7, 0x3f8',
 0x83be:'addi s4, s4, -0x2',0x83c6:'slli s2, s3, 0x2',
 0x83ca:'add a5, s7, s2',0x83ce:'lhu a4, 0x2(a5)',0x83d2:'beq s4, a4, 0x8420',
 0x83d6:'lbu a4, 0x5(a5)',0x83da:'li a3, 0x2',0x83dc:'bne a3, a4, 0x8420',
 0x83e0:'lbu s1, 0x4(a5)',0x83e4:'andi s1, s1, 0xff',0x83e8:'beqz s1, 0x8420',
 0x841e:'mv a0, s1',0x8420:'beqz s3, 0x843c',0x843c:'li s3, 0x1',0x843e:'j 0x83c6',
 0x12cb0:'jal 0x82d2',0x12cb4:'bnez a0, 0x12cee',
 0x123a4:'jal 0x838e',0x123a8:'bnez a0, 0x1240c'}
if ((0x82f2+(0x20004<<12)+0x4a2)&0xffffffff)!=0x2000c794 or ((0x839c+(0x20004<<12)+0x3f8)&0xffffffff)!=0x2000c794:
    raise ValueError('Gate bases differ')
def gate(identifier,flag,kind):return identifier!=0xfffe and flag!=0 and kind==2
if not gate(1,1,2) or gate(0xfffe,1,2) or gate(1,0,2) or gate(1,1,3):
    raise ValueError('Gate positive/negative controls failed')
results=[]
for mode in ('c','cpp'):
    elf=base/'prior'/'table'/'link'/('NOT-FLASHABLE-conditional-full-'+mode+'.elf')
    text=subprocess.check_output([str(tool),'-d','--mattr=+m,+a,+c',str(elf)],text=True)
    rows=decode(text)
    if any(rows.get(pc)!=ins for pc,ins in checks.items()):
        raise ValueError('Precheck instruction mismatch')
    results.append({'mode':mode,'instruction_checks':len(checks),'synthetic_gate_controls':4})
print(json.dumps({'passed':True,'results':results,'intervening_writes_excluded':False,
                  'all_paths_or_hardware_proved':False,'target_executed':False}))
