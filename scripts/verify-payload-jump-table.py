#!/usr/bin/env python3
"""Verify a bounded source-carried dispatch table and its actual consumer."""
import argparse
import json
from pathlib import Path
import re
import runpy
import struct
import subprocess
import sys

ROOT=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser()
p.add_argument('--tool-dir',type=Path,required=True)
p.add_argument('--out',type=Path,required=True)
a=p.parse_args()
out=a.out.resolve()
if out.exists() or out==ROOT or ROOT in out.parents:
    raise SystemExit('Output must be a new directory outside the project')
out.mkdir(parents=True)
link=out/'link'
proc=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/verify-conditional-full-payload-link.py'),
                     '--tool-dir',str(a.tool_dir),'--out',str(link)],capture_output=True,text=True)
if proc.returncode: raise ValueError('Conditional link failed: '+proc.stderr[:1000])
facts=json.loads(proc.stdout)
if not facts['passed'] or facts['hardware_validated'] or facts['installed_rom_proved']:
    raise ValueError('Unexpected link result')
tool=a.tool_dir/('llvm-objdump.exe' if (a.tool_dir/'llvm-objdump.exe').is_file() else 'llvm-objdump')
reader=runpy.run_path(str(ROOT/'src/native/tx_candidate/postpass/elf32.py'))['ELF']
expected={0x144c2:'li a5, 0xd0',0x144c6:'beq a1, a5, 0x14512',
          0x14512:'lbu a5, 0x0(s0)',0x14516:'li a4, 0x4',
          0x14518:'bltu a4, a5, 0x14098',0x1451c:'auipc a4, 0x6',
          0x14520:'addi a4, a4, 0x188',0x14524:'slli a5, a5, 0x2',
          0x14526:'add a5, a5, a4',0x14528:'lw a5, 0x0(a5)',
          0x1452a:'add a5, a5, a4',0x1452c:'jr a5'}
targets=[0x1452e,0x1453e,0x1454a,0x1473e,0x14748]
results=[]
for mode in ('c','cpp'):
    obj=link/('opaque-provider-'+mode+'.o')
    text=subprocess.check_output([str(tool),'-D','--mattr=+m,+a,+c,+zicsr','--adjust-vma=0x14056',
                                  '--section=.tsl9_full_code',str(obj)],text=True)
    rows={}
    for line in text.splitlines():
        m=re.match(r'^\s*([0-9a-f]+):\s+(?:[0-9a-f]{2}\s+)+(.*?)\s*$',line)
        if m:
            instruction=re.sub(r'\s+',' ',re.sub(r'\s*<[^>]*>','',m[2])).strip()
            rows[int(m[1],16)]=instruction
    if any(rows.get(pc)!=ins for pc,ins in expected.items()):
        raise ValueError('Dispatch instruction evidence differs')
    if any(target not in rows for target in targets):
        raise ValueError('Target is not a decoded instruction boundary')
    base=(0x1451c+(0x6<<12)+0x188)&0xffffffff
    if base!=0x1a6a4: raise ValueError('Unexpected PC-relative base')
    image=(link/('NOT-FLASH-VALIDATED-conditional-link-'+mode+'.bin')).read_bytes()
    table=image[base-0x8000:base-0x8000+20]
    if len(table)!=20: raise ValueError('Short table')
    values=struct.unpack('<5i',table)
    calculated=[(base+x)&0xffffffff for x in values]
    if calculated!=targets: raise ValueError('Unexpected table targets')
    elf=reader(link/('NOT-FLASHABLE-conditional-full-'+mode+'.elf'))
    for offset in range(20):
        address=base+offset
        owners=[s for s in elf.sections if s['flags']&2 and s['type']==1 and s['address']<=address<s['address']+s['size']]
        if len(owners)!=1 or elf.data(owners[0])[address-owners[0]['address']]!=table[offset]:
            raise ValueError('Table lacks unique matching section backing')
    for index in range(256):
        if (index<=4)!=(index in range(5)): raise ValueError('Unsigned guard mismatch')
    mutated=bytearray(table);mutated[0]^=1
    if [(base+x)&0xffffffff for x in struct.unpack('<5i',mutated)]==targets:
        raise ValueError('Mutated table negative control failed')
    results.append({'mode':mode,'checked_instructions':len(expected),'entries':5,'guard_inputs':256,
                    'table_base':hex(base),'targets':[hex(x) for x in targets]})
print(json.dumps({'passed':True,'results':results,'candidate_execution':False,'table_entry_reachability_proved':False,
                  'installed_rom_proved':False,'hardware_validated':False,'flashable':False}))
