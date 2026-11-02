#!/usr/bin/env python3
"""Bounded direct address scan; never emit firmware operands or payload."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parent.parent
TARGETS={0x200040b0:'counter',0x2000bf39:'mode',0x2000bf3a:'phase'}
TARGETS.update({0x2000414c+i:'sequence_state' for i in range(4)})
BRANCHES={'j','jal','jalr','ret','beq','bne','blt','bge','bltu','bgeu','beqz','bnez','blez','bgez','bltz','bgtz'}
WIDTHS={'sb':1,'sh':2,'sw':4,'lb':1,'lbu':1,'lh':2,'lhu':2,'lw':4}
def scan(rows):
    regs={'gp':0x20004000,'zero':0}
    hits=[]
    for pc,op,args in rows:
        try:
            if op=='auipc' and len(args)==2:
                regs[args[0]]=(pc+(int(args[1],0)<<12))&0xffffffff
            elif op=='lui' and len(args)==2:
                regs[args[0]]=(int(args[1],0)<<12)&0xffffffff
            elif op=='addi' and len(args)==3:
                dest,src,imm=args
                if src in regs: regs[dest]=(regs[src]+int(imm,0))&0xffffffff
                else: regs.pop(dest,None)
            elif op=='mv' and len(args)==2:
                if args[1] in regs: regs[args[0]]=regs[args[1]]
                else: regs.pop(args[0],None)
            elif op in WIDTHS and len(args)==2:
                operand=re.fullmatch(r'(-?(?:0x[0-9a-f]+|[0-9]+))\(([a-z][a-z0-9]*)\)',args[1])
                if operand and operand[2] in regs:
                    address=(regs[operand[2]]+int(operand[1],0))&0xffffffff
                    for target,label in TARGETS.items():
                        if address<=target<address+WIDTHS[op]:
                            hits.append({'pc':pc,'operation':op,'target':label})
                if op.startswith('l'): regs.pop(args[0],None)
            elif op in BRANCHES:
                regs={'gp':0x20004000,'zero':0}
            elif args and op not in ('fence','fence.i','ecall','ebreak','nop'):
                regs.pop(args[0],None)
        except ValueError:
            regs={'gp':0x20004000,'zero':0}
    return hits
def decode(text):
    rows=[]
    for line in text.splitlines():
        m=re.match(r'^\s*([0-9a-f]+):\s+(?:[0-9a-f]{2}\s+)+(.*?)\s*$',line)
        if not m: continue
        pc=int(m[1],16)
        if not 0x14056<=pc<0x14c8a: raise ValueError('Unexpected address')
        ins=re.sub(r'\s*<[^>]*>','',m[2]);parts=ins.split(None,1)
        if parts[0].startswith('.') or '<unknown>' in m[2]: raise ValueError('Undecoded bytes')
        rows.append((pc,parts[0],[x.strip() for x in parts[1].split(',')] if len(parts)>1 else []))
    if len({x[0] for x in rows})!=len(rows): raise ValueError('Duplicate address')
    return rows
positive=[(0x14056,'sb',['a0','0xb0(gp)']),
          (0x14058,'addi',['a4','gp','0x14c']),(0x1405c,'sw',['a0','0(a4)']),
          (0x14056,'auipc',['a5','0x1fff8']),(0x1405a,'sb',['a0','-285(a5)'])]
control=scan(positive)
if len(control)!=6 or {x['target'] for x in control}!={'counter','sequence_state','mode'}:
    raise ValueError('Positive controls failed')
if scan([(0x14056,'auipc',['a5','0x1fff8']),(0x1405a,'j',['0x14060']),
         (0x14060,'sb',['a0','-285(a5)'])]):
    raise ValueError('Branch barrier control failed')
p=argparse.ArgumentParser()
p.add_argument('--tool-dir',type=Path,required=True)
p.add_argument('--out',type=Path,required=True)
a=p.parse_args()
out=a.out.resolve()
if out.exists() or out==ROOT or ROOT in out.parents: raise SystemExit('Output must be a new directory outside the project')
out.mkdir(parents=True)
linked=out/'link'
proc=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/verify-conditional-full-payload-link.py'),
                     '--tool-dir',str(a.tool_dir),'--out',str(linked)],capture_output=True,text=True)
if proc.returncode: raise ValueError('Conditional link failed: '+proc.stderr[:1000])
facts=json.loads(proc.stdout)
if not facts['passed'] or facts['hardware_validated'] or facts['installed_rom_proved']:
    raise ValueError('Unexpected link result')
tool=a.tool_dir/('llvm-objdump.exe' if (a.tool_dir/'llvm-objdump.exe').is_file() else 'llvm-objdump')
results=[]
for mode in ('c','cpp'):
    obj=linked/('opaque-provider-'+mode+'.o')
    decoded=subprocess.check_output([str(tool),'-D','--mattr=+m,+a,+c,+zicsr','--adjust-vma=0x14056',
                                     '--section=.tsl9_full_code',str(obj)],text=True)
    rows=decode(decoded);hits=scan(rows)
    if len(rows)!=1008 or hits: raise ValueError('Direct scan result changed; review required')
    results.append({'mode':mode,'decoded_rows':len(rows),'direct_hits':len(hits)})
print(json.dumps({'passed':True,'results':results,'positive_control_hits':len(control),
                  'branch_barrier_tested':True,'global_writers_excluded':False,
                  'target_executed':False,'hardware_validated':False}))
