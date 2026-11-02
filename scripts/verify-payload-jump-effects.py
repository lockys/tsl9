#!/usr/bin/env python3
"""Check bounded jump-table case arguments and the original type setter."""
import argparse,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser()
p.add_argument('--tool-dir',type=Path,required=True)
p.add_argument('--out',type=Path,required=True)
a=p.parse_args();out=a.out.resolve()
if out.exists() or out==ROOT or ROOT in out.parents: raise SystemExit('Output must be a new directory outside the project')
out.mkdir(parents=True);base=out/'table'
proc=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/verify-payload-jump-table.py'),
                     '--tool-dir',str(a.tool_dir),'--out',str(base)],capture_output=True,text=True)
if proc.returncode: raise ValueError('Jump-table validation failed: '+proc.stderr[:1000])
facts=json.loads(proc.stdout)
if not facts['passed'] or facts['hardware_validated'] or facts['table_entry_reachability_proved']:
    raise ValueError('Unexpected table baseline')
tool=a.tool_dir/('llvm-objdump.exe' if (a.tool_dir/'llvm-objdump.exe').is_file() else 'llvm-objdump')
def decode(text):
    rows={}
    for line in text.splitlines():
        m=re.match(r'^\s*([0-9a-f]+):\s+(?:[0-9a-f]{2}\s+)+(.*?)\s*$',line)
        if m: rows[int(m[1],16)]=re.sub(r'\s+',' ',re.sub(r'\s*<[^>]*>','',m[2])).strip()
    return rows
case_checks={
 0x1452e:'mv a0, s1',0x14530:'li a1, 0x0',0x14532:'jal 0x13ba6',
 0x1453e:'mv a0, s1',0x14540:'li a1, 0x3',0x14542:'jal 0x13ba6',
 0x1454a:'li a1, 0x3',0x1454c:'mv a0, s1',0x1454e:'jal 0x13ba6',
 0x1473e:'li a1, 0x4',0x14740:'mv a0, s1',0x14742:'jal 0x13ba6',
 0x14748:'li a1, 0x3',0x1474a:'mv a0, s1',0x1474c:'jal 0x13ba6'}
setter={
 0x13ba6:'auipc a4, 0x1fff9',0x13baa:'lhu a4, -0x410(a4)',
 0x13bae:'auipc a5, 0x1fff9',0x13bb2:'addi a5, a5, -0x41a',
 0x13bb6:'beq a0, a4, 0x13bce',0x13bba:'lhu a4, 0x6(a5)',
 0x13bbe:'bne a0, a4, 0x13bcc',0x13bc2:'li a4, 0x1',
 0x13bc4:'slli a4, a4, 0x2',0x13bc6:'add a5, a5, a4',
 0x13bc8:'sb a1, 0x5(a5)',0x13bcc:'ret',0x13bce:'li a4, 0x0',
 0x13bd0:'j 0x13bc4'}
types=[0,3,3,4,3]
if any(t==2 for t in types) or ((0x13bae+(0x1fff9<<12)-0x41a)&0xffffffff)!=0x2000c794:
    raise ValueError('Setter address or type control mismatch')
results=[]
for mode in ('c','cpp'):
    link=base/'link';obj=link/('opaque-provider-'+mode+'.o')
    text=subprocess.check_output([str(tool),'-D','--mattr=+m,+a,+c,+zicsr','--adjust-vma=0x14056',
                                  '--section=.tsl9_full_code',str(obj)],text=True)
    rows=decode(text)
    if any(rows.get(pc)!=ins for pc,ins in case_checks.items()):
        raise ValueError('Case argument instruction mismatch')
    elf=link/('NOT-FLASHABLE-conditional-full-'+mode+'.elf')
    text=subprocess.check_output([str(tool),'-d','--mattr=+m,+a,+c',
            '--start-address=0x13ba6','--stop-address=0x13bd2',str(elf)],text=True)
    rows=decode(text)
    if any(rows.get(pc)!=ins for pc,ins in setter.items()):
        raise ValueError('Setter instruction mismatch')
    results.append({'mode':mode,'case_instruction_checks':len(case_checks),
                    'setter_instruction_checks':len(setter),'case_type_values':types})
print(json.dumps({'passed':True,'results':results,'all_paths_reachable_proved':False,
                  'global_type_bounds_proved':False,'target_executed':False,'hardware_validated':False}))
