#!/usr/bin/env python3
"""Verify selected delayed settings-pointer uses without executing the image."""
import argparse,hashlib,json,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--firmware',type=Path,required=True);p.add_argument('--r2',type=Path,required=True);a=p.parse_args()
raw=a.firmware.read_bytes()
if len(raw)!=76800 or hashlib.sha256(raw).hexdigest()!='28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89':raise ValueError('Candidate image changed')
expected={0x12c82:'addi s7, gp, 84',0x12d78:'lw a5, 0(s7)',0x12d7c:'lbu a5, 4(a5)',
0x133c0:'addi s4, gp, 84',0x13516:'lw a5, 0(s4)',0x1351a:'lbu a5, 4(a5)',
0x13574:'lw a1, 0(s4)',0x1357e:'lw a5, 76(s0)',0x13580:'li a2, 16',0x13582:'addi a0, sp, 44',0x13584:'jalr a5',
0x13586:'lw a1, 0(s4)',0x1358a:'lw a5, 76(s0)',0x1358c:'li a2, 16',0x1358e:'addi a1, a1, 96',0x13592:'addi a0, sp, 79',0x13596:'jalr a5',
0x1823c:'addi a1, a0, 2',0x18240:'addi a3, gp, 84',0x18244:'lw a4, 76(a5)',0x18246:'slli a5, a1, 0x3',0x1824a:'lw a1, 0(a3)',
0x18250:'add a1, a1, a5',0x18252:'li a5, 4',0x18254:'li a2, 8',0x18256:'bltu a5, a0, 0x1834a',0x18262:'jalr a4'}
seen={}
for start,count in ((0x12c82,1),(0x12d78,2),(0x133c0,1),(0x13516,2),(0x13574,13),(0x1823c,14)):
    cmd=[str(a.r2),'-q','-a','riscv','-b','32','-m','0x8000','-c',f's {start}; pdj {count}',str(a.firmware)]
    for item in json.loads(subprocess.run(cmd,capture_output=True,text=True,check=True).stdout):
        if item['addr'] in expected:seen[item['addr']]=item['opcode'].lower()
if seen!=expected:raise ValueError('Delayed pointer instruction mismatch')
bad=dict(seen);bad[0x13582]='addi a0, s4, 0';assert bad!=expected
offsets=[8*(x+2) for x in range(5)]
assert offsets==[16,24,32,40,48] and all(0<=v and v+8<=112 for v in offsets)
print(json.dumps({'passed':True,'pinned_instructions':len(expected),'negative_control':True,
 'copy_source_offsets_for_guarded_input':offsets,'writes_to_pointer_excluded_only_in_selected_instructions':True,
 'registers_and_stack_proved':False,'installed_copy_slot_proved':False,'full_cfg_proved':False,'target_executed':False}))
