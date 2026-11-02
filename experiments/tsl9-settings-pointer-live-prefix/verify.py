#!/usr/bin/env python3
"""Classify bounded linear prefixes after retained pointer-base reads."""
import argparse,json,re,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--firmware',type=Path,required=True);p.add_argument('--layout',type=Path,required=True);p.add_argument('--reader',type=Path,required=True);p.add_argument('--r2',type=Path,required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[2]
scan=root/'experiments/tsl9-settings-pointer-gp-scan/verify.py'
data=json.loads(subprocess.run([sys.executable,'-B',str(scan),'--firmware',str(a.firmware),'--layout',str(a.layout),'--reader',str(a.reader)],capture_output=True,text=True,check=True).stdout)
def classify(text,name):
    mnemonic=text.split()[0];arg=text[len(mnemonic):].strip()
    if mnemonic.startswith('b') or mnemonic in ('j','jr','jal','jalr','ret','mret','ecall','ebreak'):return 'control_flow_boundary'
    if not re.search(r'\b'+name+r'\b',arg):return None
    args=[x.strip() for x in arg.split(',')]
    if mnemonic in ('sb','sh','sw','sd','fsw','fsd'):return 'store_using_address_register'
    if args and args[0]==name:
        return 'modified_using_address' if any(re.search(r'\b'+name+r'\b',x) for x in args[1:]) else 'register_overwritten'
    return 'address_used_or_copied'
assert classify('sw a0, 0(a5)','a5')=='store_using_address_register'
assert classify('mv s0, a5','a5')=='address_used_or_copied'
assert classify('li a5, 0','a5')=='register_overwritten'
assert classify('beqz a0, 0x1000','a5')=='control_flow_boundary'
registers={9:'s1',14:'a4',15:'a5',19:'s3'};out=[]
for site in data['address_retained_after_load']:
    name=registers[site['base_register']]
    cmd=[str(a.r2),'-q','-a','riscv','-b','32','-m','0x8000','-c',f"s {site['pc']}; pdj 26",str(a.firmware)]
    ops=json.loads(subprocess.run(cmd,capture_output=True,text=True,check=True).stdout)
    stop='limit';address=None
    for op in ops[2:]:
        stop_here=classify(op['opcode'].lower(),name)
        if stop_here:stop=stop_here;address=hex(op['addr']);break
    out.append({'site':site['pc'],'stop':stop,'at':address})
expected_overwritten={'0xa234','0xf8ae','0xfbbe','0x131a0','0x15532','0x18584','0x14132'}
expected_boundary={'0xac7c','0xbdc6','0xdf26','0xfe6a','0x155d4','0x171ec','0x142fc'}
if {x['site'] for x in out if x['stop']=='register_overwritten'}!=expected_overwritten or {x['site'] for x in out if x['stop']=='control_flow_boundary'}!=expected_boundary or len(out)!=14:
    raise ValueError('Unexpected bounded prefix classifications')
print(json.dumps({'passed':True,'cases':out,'synthetic_controls':4,'not_full_cfg':True,'target_executed':False,'hardware_validated':False}))
