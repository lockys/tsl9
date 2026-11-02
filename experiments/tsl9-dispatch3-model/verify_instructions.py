#!/usr/bin/env python3
"""Check dispatch instructions and pinned public WCH reference slots."""
import argparse,hashlib,json,re,struct,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--firmware',type=Path,required=True);p.add_argument('--resident',type=Path,required=True);p.add_argument('--header',type=Path,required=True);p.add_argument('--r2',type=Path,required=True);a=p.parse_args()
def sha(b):return hashlib.sha256(b).hexdigest()
image=a.firmware.read_bytes();ref=a.resident.read_bytes();header=a.header.read_bytes()
if len(image)!=76800 or sha(image)!='28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89':raise ValueError('Candidate changed')
if sha(ref)!='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22' or sha(header)!='647a185941fedeb6ba16d544d9bca91a6f53219bb649a5513b59abeb21a9a94c':raise ValueError('Reference changed')
if not re.search(rb'#define\s+tmos_msg_allocate\s+.*uint16_t\s+len.*BLE_LIB_JT\(15\)',header):raise ValueError('Allocation signature changed')
if not re.search(rb'#define\s+tmos_memcpy\s+.*void\s*\*dst.*const\s+void\s*\*src.*uint32_t\s+len.*BLE_LIB_JT\(6\)',header):raise ValueError('Copy signature changed')
if struct.unpack_from('<I',ref,0x70)[0]!=0x20000236 or struct.unpack_from('<I',ref,0x4c)[0]!=0x20000332:raise ValueError('Candidate slot changed')
expected={0x14288:'li a5, 162',0x1428c:'beq a1, a5, 0x149fc',0x14290:'li a5, 163',0x14294:'bne a1, a5, 0x14098',
0x14298:'li a5, 76',0x1429c:'bne s2, a5, 0x14a24',0x142a0:'lui a5, 0x40',0x142a4:'lw a5, 112(a5)',0x142a6:'li a0, 76',
0x142aa:'jalr a5',0x142ac:'mv s2, a0',0x142ae:'beqz a0, 0x14a24',0x142b2:'lui a5, 0x40',0x142b6:'lw a5, 76(a5)',
0x142b8:'li a2, 76',0x142bc:'mv a1, s0',0x142be:'jalr a5'}
cmd=[str(a.r2),'-q','-a','riscv','-b','32','-m','0x8000','-c','s 0x14288; pdj 17',str(a.firmware)]
ops=json.loads(subprocess.run(cmd,capture_output=True,text=True,check=True).stdout)
if {x['addr']:x['opcode'].lower() for x in ops}!=expected:raise ValueError('Dispatcher instructions changed')
assert 0x40034+15*4==0x40070 and 0x40034+6*4==0x4004c
bad=dict(expected);bad[0x142ae]='bnez a0, 0x14a24';assert bad!=expected
print(json.dumps({'passed':True,'instructions':len(expected),'reference_slots_checked':2,'negative_control':True,'installed_rom_proved':False,'target_executed':False}))
