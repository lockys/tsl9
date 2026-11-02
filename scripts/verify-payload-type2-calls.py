#!/usr/bin/env python3
"""Check newly visible type-2 calls without exposing authentication content."""
import argparse,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser();p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
a=p.parse_args();out=a.out.resolve()
if out.exists() or out==ROOT or ROOT in out.parents: raise SystemExit('Output must be a new directory outside the project')
out.mkdir(parents=True);base=out/'prior'
proc=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/verify-payload-jump-effects.py'),
                     '--tool-dir',str(a.tool_dir),'--out',str(base)],capture_output=True,text=True)
if proc.returncode: raise ValueError('Baseline failed: '+proc.stderr[:1000])
f=json.loads(proc.stdout)
if not f['passed'] or f['hardware_validated'] or f['global_type_bounds_proved']: raise ValueError('Unexpected baseline')
tool=a.tool_dir/('llvm-objdump.exe' if (a.tool_dir/'llvm-objdump.exe').is_file() else 'llvm-objdump')
def decode(text):
    rows={}
    for line in text.splitlines():
        m=re.match(r'^\s*([0-9a-f]+):\s+(?:[0-9a-f]{2}\s+)+(.*?)\s*$',line)
        if m:rows[int(m[1],16)]=re.sub(r'\s+',' ',re.sub(r'\s*<[^>]*>','',m[2])).strip()
    return rows
caller={0x14066:'mv s1, a0',0x14068:'mv s0, a2',0x1406a:'mv s2, a3',
        0x1416a:'li a1, 0x1',0x1416c:'mv a0, s1',0x1416e:'jal 0x13e0e',
        0x14486:'li a5, 0xc0',0x1448a:'bne a1, a5, 0x14098',
        0x1448e:'li a4, 0x1',0x14490:'lbu a5, 0x0(s0)',0x14494:'bne s2, a4, 0x147e4',
        0x14498:'beq a5, s2, 0x147c6',0x1449c:'beqz a5, 0x147ae',
        0x144a0:'li a4, 0x2',0x144a2:'bne a5, a4, 0x14098',
        0x144a6:'li a1, 0x2',0x144a8:'mv a0, s1',0x144aa:'jal 0x13ba6',
        0x147c6:'li a1, 0x2',0x147c8:'mv a0, s1',0x147ca:'jal 0x13ba6',
        0x147f4:'li a1, 0x2',0x147f6:'mv a0, s1',0x147f8:'jal 0x13ba6',
        0x14928:'li a1, 0x2',0x1492a:'mv a0, s1',0x1492c:'jal 0x13ba6'}
setter={0x13e0e:'li a4, 0x2',0x13e10:'auipc a5, 0x1fff9',0x13e14:'addi a5, a5, -0x67c',
        0x13e18:'beq a1, a4, 0x13e3a',0x13e1c:'li a4, 0x1',0x13e1e:'beq a1, a4, 0x13e2e',
        0x13e2e:'lhu a4, 0x2(a5)',0x13e32:'bne a0, a4, 0x13e62',
        0x13e36:'li a4, 0x0',0x13e38:'j 0x13e72',0x13e62:'li a4, 0x1',
        0x13e64:'bne a1, a4, 0x13e82',0x13e68:'lhu a4, 0x6(a5)',
        0x13e6c:'bne a0, a4, 0x13e80',0x13e70:'li a4, 0x1',
        0x13e72:'slli a4, a4, 0x2',0x13e74:'add a5, a5, a4',
        0x13e76:'li a4, 0x1',0x13e78:'sb a4, 0x4(a5)',
        0x13e7c:'sb zero, 0x5(a5)',0x13e80:'ret'}
if ((0x13e10+(0x1fff9<<12)-0x67c)&0xffffffff)!=0x2000c794:
    raise ValueError('Unexpected flag base')
results=[]
for mode in ('c','cpp'):
    link=base/'table'/'link';obj=link/('opaque-provider-'+mode+'.o')
    text=subprocess.check_output([str(tool),'-D','--mattr=+m,+a,+c,+zicsr','--adjust-vma=0x14056',
                                  '--section=.tsl9_full_code',str(obj)],text=True)
    rows=decode(text)
    if any(rows.get(pc)!=v for pc,v in caller.items()):raise ValueError('Caller instruction mismatch')
    elf=link/('NOT-FLASHABLE-conditional-full-'+mode+'.elf')
    text=subprocess.check_output([str(tool),'-d','--mattr=+m,+a,+c','--start-address=0x13e0e',
                                  '--stop-address=0x13e82',str(elf)],text=True)
    rows=decode(text)
    if any(rows.get(pc)!=v for pc,v in setter.items()):raise ValueError('Flag setter instruction mismatch')
    results.append({'mode':mode,'caller_instruction_checks':len(caller),'flag_instruction_checks':len(setter),
                    'type2_direct_sites':4})
print(json.dumps({'passed':True,'results':results,'specific_path_conditions_only':True,
                  'device_state_or_reachability_proved':False,'target_executed':False,'hardware_validated':False}))
