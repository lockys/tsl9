#!/usr/bin/env python3
"""Verify dispatcher bounds and release request without accessing device data."""
import argparse,hashlib,json,re,struct,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--firmware',type=Path,required=True);p.add_argument('--resident',type=Path,required=True);p.add_argument('--header',type=Path,required=True);p.add_argument('--r2',type=Path,required=True);a=p.parse_args()
def sha(b):return hashlib.sha256(b).hexdigest()
image=a.firmware.read_bytes();ref=a.resident.read_bytes();header=a.header.read_bytes()
if len(image)!=76800 or sha(image)!='28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89':raise ValueError('Candidate changed')
if sha(ref)!='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22' or sha(header)!='647a185941fedeb6ba16d544d9bca91a6f53219bb649a5513b59abeb21a9a94c':raise ValueError('Reference changed')
if not re.search(rb'#define\s+tmos_msg_deallocate\s+.*uint8_t\s*\*msg_ptr.*BLE_LIB_JT\(13\)',header):raise ValueError('Release signature changed')
if struct.unpack_from('<I',ref,0x68)[0]!=0x431ba:raise ValueError('Reference slot changed')
expected={0x142c0:'li a1, 14',0x142c2:'addi a0, s2, 4',0x142c6:'jal ra, 0x92f2',0x142ca:'seqz s3, a0',
0x142ce:'addi a4, s2, 36',0x142d2:'addi a3, s2, 40',0x142d6:'li a2, 94',0x142da:'lbu a5, 0(a4)',
0x142de:'addi a5, a5, -32',0x142e0:'andi a5, a5, 255',0x142e4:'bltu a2, a5, 0x14a1e',
0x142e8:'addi a4, a4, 1',0x142ea:'bne a3, a4, 0x142da',0x142ee:'lui a5, 0x40',
0x142f2:'lw a5, 104(a5)',0x142f4:'mv a0, s2',0x142f6:'jalr a5',0x142f8:'beqz s3, 0x14a24',
0x14a1e:'li s3, 0',0x14a20:'j 0x142ee'}
observed={}
for start,count in ((0x142c0,18),(0x14a1e,2)):
    cmd=[str(a.r2),'-q','-a','riscv','-b','32','-m','0x8000','-c',f's {start}; pdj {count}',str(a.firmware)]
    for x in json.loads(subprocess.run(cmd,capture_output=True,text=True,check=True).stdout):observed[x['addr']]=x['opcode'].lower()
if observed!=expected:raise ValueError('Dispatcher instruction mismatch')
assert 0<=4 and 4+14<=76 and 0<=36<40<=76
assert all((((x-32)&255)<=94)==(32<=x<=126) for x in range(256))
bad=dict(observed);bad[0x142e4]='bgeu a2, a5, 0x14a1e';assert bad!=expected
print(json.dumps({'passed':True,'instructions':len(expected),'validation_request_offset':4,'validation_request_length':14,
 'field_offset':36,'field_length':4,'reference_release_slot':13,'negative_control':True,
 'actual_memory_proved':False,'installed_rom_proved':False,'target_executed':False}))
