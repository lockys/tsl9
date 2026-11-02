#!/usr/bin/env python3
"""Bounded static check of pointer-address uses in the 0xFE6A function."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--firmware',type=Path,required=True);p.add_argument('--r2',type=Path,required=True);a=p.parse_args()
blob=a.firmware.read_bytes()
if len(blob)!=76800 or hashlib.sha256(blob).hexdigest()!='28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89':raise ValueError('Candidate image changed')
cmd=[str(a.r2),'-q','-a','riscv','-b','32','-m','0x8000','-c','s 0xfe6a; pdj 100',str(a.firmware)]
allops=json.loads(subprocess.run(cmd,capture_output=True,text=True,check=True).stdout)
ops=[x for x in allops if 0xfe6a<=x['addr']<0xff44]
if not ops or ops[0]['addr']!=0xfe6a or ops[-1]['addr']+ops[-1]['size']!=0xff44:raise ValueError('Function boundaries changed')
s0=[(x['addr'],x['opcode'].lower()) for x in ops if re.search(r'\bs0\b',x['opcode'])]
expected_s0=[(0xfe7c,'sw s0, 8(sp)'),(0xfe82,'mv s0, a5'),(0xfeb4,'lw a5, 0(s0)'),(0xfee6,'lw s0, 8(sp)')]
stores=[(x['addr'],x['opcode'].lower()) for x in ops if x['opcode'].split()[0].lower() in ('sb','sh','sw','sd','fsw','fsd')]
expected_stores=[(0xfe7c,'sw s0, 8(sp)'),(0xfe7e,'sw s1, 4(sp)'),(0xfe80,'sw ra, 12(sp)'),(0xfea8,'sw a0, 296(gp)'),(0xfec6,'sb a5, 292(gp)'),(0xfedc,'sb a5, 288(gp)'),(0xfee0,'sb zero, 291(gp)'),(0xff10,'sb zero, 292(gp)'),(0xff3c,'sb a5, 288(gp)')]
if s0!=expected_s0 or stores!=expected_stores:raise ValueError('Pointer register use or direct stores changed')
by={x['addr']:x['opcode'].lower() for x in ops}
required={0xfe6a:'addi a5, gp, 84',0xfe6e:'lw a4, 0(a5)',0xfe76:'beqz a4, 0xff42',0xfe82:'mv s0, a5',0xfeb4:'lw a5, 0(s0)',0xfeec:'ret',0xff42:'ret'}
if any(by.get(pc)!=value for pc,value in required.items()):raise ValueError('Key instruction changed')
bad=list(stores);bad.append((0xfeb4,'sw a0, 0(s0)'));assert bad!=expected_stores
assert all(not (offset<88 and 84<offset+width) for offset,width in ((296,4),(292,1),(288,1),(291,1)))
print(json.dumps({'passed':True,'function_start':'0xfe6a','function_end_exclusive':'0xff44','instructions':len(ops),'s0_uses':len(s0),'stores':len(stores),'stack_store_count':3,'gp_store_count':6,'negative_control':True,'callee_effects_proved':False,'stack_nonoverlap_proved':False,'full_runtime_proved':False,'target_executed':False}))
