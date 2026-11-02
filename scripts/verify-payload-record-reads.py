#!/usr/bin/env python3
"""Check direct record access callers and the retained record-copy ABI."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser()
p.add_argument('--tool-dir',type=Path,required=True)
p.add_argument('--out',type=Path,required=True)
a=p.parse_args()
out=a.out.resolve()
if out.exists() or out==ROOT or ROOT in out.parents: raise SystemExit('Output must be a new directory outside the project')
out.mkdir(parents=True)
link=out/'link'
proc=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/verify-conditional-full-payload-link.py'),
                     '--tool-dir',str(a.tool_dir),'--out',str(link)],capture_output=True,text=True)
if proc.returncode: raise ValueError('Conditional link failed: '+proc.stderr[:1000])
facts=json.loads(proc.stdout)
if not facts['passed'] or facts['hardware_validated'] or facts['installed_rom_proved']:
    raise ValueError('Unexpected link result')
tool=a.tool_dir/('llvm-objdump.exe' if (a.tool_dir/'llvm-objdump.exe').is_file() else 'llvm-objdump')
calls={0x14572:(0x1456c,0x1456e,0x14570,1),
       0x1459c:(0x1457e,0x14590,0x14596,11),
       0x145e2:(0x145a8,0x145b4,0x145b6,5),
       0x14632:(0x14626,0x14628,0x1462a,6),
       0x1465c:(0x1463e,0x14650,0x14656,7),
       0x14676:(0x14668,0x1466e,0x14670,3),
       0x14770:(0x1476a,0x1476c,0x1476e,4)}
callee={0x82a8:'lui a5, 0x40',0x82ac:'lw t1, 0x4c(a5)',0x82b0:'li a5, 0xc',
        0x82b2:'mul a1, a1, a5',0x82b6:'auipc a5, 0x20004',
        0x82ba:'addi a5, a5, -0xfe',0x82be:'mv a4, a2',0x82c0:'li a2, 0xc',
        0x82c2:'add a5, a5, a1',0x82c4:'beqz a0, 0x82cc',
        0x82c6:'mv a1, a5',0x82c8:'mv a0, a4',0x82ca:'jr t1'}
def decode(text):
    rows={}
    for line in text.splitlines():
        m=re.match(r'^\s*([0-9a-f]+):\s+(?:[0-9a-f]{2}\s+)+(.*?)\s*$',line)
        if m:
            ins=re.sub(r'\s+',' ',re.sub(r'\s*<[^>]*>','',m[2])).strip()
            rows[int(m[1],16)]=ins
    return rows
results=[]
for mode in ('c','cpp'):
    obj=link/('opaque-provider-'+mode+'.o')
    raw=subprocess.check_output([str(tool),'-D','--mattr=+m,+a,+c,+zicsr','--adjust-vma=0x14056',
                                 '--section=.tsl9_full_code',str(obj)],text=True)
    rows=decode(raw)
    found={pc for pc,ins in rows.items() if re.fullmatch(r'(?:j|jal) 0x82a8',ins)}
    if found!=set(calls): raise ValueError('Record caller set changed')
    for pc,(a2pc,a1pc,a0pc,index) in calls.items():
        if (rows.get(a2pc) not in ('addi a2, sp, 0x24','addi a2, sp, 0x30') or
            rows.get(a1pc)!='li a1, '+hex(index) or rows.get(a0pc)!='li a0, 0x1' or
            rows.get(pc)!='jal 0x82a8'):
            raise ValueError('Record call setup changed')
        setters={'a0':a0pc,'a1':a1pc,'a2':a2pc}
        for q,ins in rows.items():
            if not min(setters.values())<q<pc: continue
            op,_,args=ins.partition(' ')
            if op in ('j','jal','jalr','jr','ret') or op.startswith('b'):
                raise ValueError('Unexpected branch in argument setup')
            if op not in ('sb','sh','sw') and args:
                dest=args.split(',',1)[0]
                if dest in setters and q>setters[dest]:
                    raise ValueError('Argument overwritten')
    elf=link/('NOT-FLASHABLE-conditional-full-'+mode+'.elf')
    body=decode(subprocess.check_output([str(tool),'-d','--mattr=+m,+a,+c',
                    '--start-address=0x82a8','--stop-address=0x82d2',str(elf)],text=True))
    if any(body.get(pc)!=ins for pc,ins in callee.items()):
        raise ValueError('Record callee instruction evidence differs')
    if (0x82b6+(0x20004<<12)-0xfe)&0xffffffff!=0x2000c1b8:
        raise ValueError('Record base mismatch')
    if any(index==14 for _,_,_,index in calls.values()):
        raise ValueError('Unexpected index 14')
    results.append({'mode':mode,'direct_call_sites':len(calls),'indexes':[x[3] for x in calls.values()],
                    'callee_instruction_checks':len(callee)})
print(json.dumps({'passed':True,'results':results,'resident_copy_semantics_proved':False,
                  'other_writers_excluded':False,'target_executed':False,'hardware_validated':False}))
