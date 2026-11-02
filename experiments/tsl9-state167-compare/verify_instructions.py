#!/usr/bin/env python3
"""Check the value-comparison data flow without reading device data."""
import argparse,hashlib,json,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--firmware',type=Path,required=True);p.add_argument('--r2',type=Path,required=True);a=p.parse_args()
image=a.firmware.read_bytes()
if len(image)!=76800 or hashlib.sha256(image).hexdigest()!='28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89':raise ValueError('Candidate image changed')
expected={0x9384:'jal ra, 0x9e84',0x9388:'sw a0, 8(sp)',0x938a:'lhu s0, 10(sp)',0x938e:'sw a1, 12(sp)',
          0x9390:'jal 0x9334',0x9392:'slli s0, s0, 0x10',0x9394:'c.srli s0, s0, 0x10',0x9396:'sub a0, s0, a0',
          0x939e:'seqz a0, a0',0x93a2:'sb a0, 167(gp)',0x93a8:'ret',
          0x9e84:'lui a5, 0x40',0x9e88:'lw a5, 76(a5)',0x9e92:'mv a0, sp',0x9e98:'li a2, 8',
          0x9e9a:'jalr a5',0x9e9e:'lw a0, 0(sp)',0x9ea0:'lw a1, 4(sp)',0x9ea4:'ret',
          0x9f06:'jal ra, 0x937e',0x9f42:'jal ra, 0x937e'}
observed={}
for start,count in ((0x937e,17),(0x9e84,14),(0x9f06,1),(0x9f42,1)):
    cmd=[str(a.r2),'-q','-a','riscv','-b','32','-m','0x8000','-c',f's {start}; pdj {count}',str(a.firmware)]
    for op in json.loads(subprocess.run(cmd,capture_output=True,text=True,check=True).stdout):
        if op['addr'] in expected:observed[op['addr']]=op['opcode'].lower()
if observed!=expected:raise ValueError('Writer comparison instruction changed')
bad=dict(observed);bad[0x938a]='lhu s0, 8(sp)';assert bad!=expected
print(json.dumps({'passed':True,'pinned_instructions':len(expected),'synthetic_negative_control':True,
 'copy_slot_proved':False,'compare_input_runtime_proved':False,'target_executed':False,'sensitive_device_data_read':False}))
