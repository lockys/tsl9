#!/usr/bin/env python3
"""Bounded original reset/clock static caller audit; no target execution."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ORIGINAL_SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
SPANS=((0x186AA,0x18734,37,'9507502c874a03e2c64a28b186a1f56aba9e85c9989dbf0cc053dabc4045bb4d'),
       (0x1874A,0x18834,93,'e0debe8b77025cfb56144045a0aa7524b7a2cd2ad0bd3daa2d880408ad9758f5'))
REFERENCES=(
    ('experiments/tsl9-v4160-reset-contract/source-map.json','30b0aa7912c2323c26167e023f50f6687f3eb53b70c68ad4bee10ca6fad6726b'),
    ('experiments/tsl9-v4160-reset-contract/src/reset_contract.c','d42375243fc8ba99de54765da85789bb56459c651d8a23d3caf520a63cdd2359'),
    ('experiments/tsl9-v4160-clock-contract/source-map.json','dca1752dd8c2194ee7df6fb85131ced06d39e9e6d19eea59085fd06b6b5041c5'),
    ('experiments/tsl9-resident-entry-reference/source-map.json','95a30cf4b25220538db0d79bb224ceea85259a0c797ec5b407dad2b871748480'),
)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def need(okay,message):
    if not okay:raise RuntimeError(message)
def signed12(value):return value-4096 if value&2048 else value

def pair(data,pc,expected_register):
    offset=pc-0x8000;hi=int.from_bytes(data[offset:offset+4],'little');lo=int.from_bytes(data[offset+4:offset+8],'little')
    need(hi&127==0x17 and (hi>>7)&31==expected_register,'Original AUIPC destination')
    need(lo&127==0x13 and (lo>>12)&7==0 and (lo>>7)&31==expected_register
         and (lo>>15)&31==expected_register,'Own-anchor ADDI pair')
    return (pc+(hi&0xfffff000)+signed12(lo>>20))&0xffffffff

def audit(image,r2):
    data=image.read_bytes();need(len(data)==76800 and sha(image)==ORIGINAL_SHA,'Exact original ID2966 runtime')
    references=[]
    for relative,digest in REFERENCES:
        p=ROOT/relative;need(sha(p)==digest,'Existing source-map/reference identity');references.append(dict(path=relative,sha256=digest))
    command=';'.join('pdj 110 @ '+hex(start) for start,_,_,_ in SPANS)
    proc=subprocess.run([str(r2),'-2','-a','riscv','-b','32','-m','0x8000','-q','-c',command,str(image)],capture_output=True,text=True,check=True,timeout=60)
    groups=[json.loads(line) for line in proc.stdout.splitlines() if line.startswith('[')]
    need(len(groups)==2,'Two bounded static source groups');retained=[];by_pc={}
    for (start,end,count,digest),group in zip(SPANS,groups):
        raw=data[start-0x8000:end-0x8000];need(hashlib.sha256(raw).hexdigest()==digest,'Original span SHA')
        rows=[row for row in group if start<=row['addr']<end];need(len(rows)==count,'Exact bounded instruction count');cursor=start
        for row in rows:
            need(row['addr']==cursor and data[cursor-0x8000:cursor-0x8000+row['size']].hex()==row['bytes'],'Contiguous original instruction bytes')
            by_pc[cursor]=row;cursor+=row['size']
        need(cursor==end,'Exact bounded end')
        retained.append(dict(start=start,end_exclusive=end,bytes=len(raw),instructions=count,sha256=digest,
            rows=[{k:row[k] for k in ('addr','size','bytes','opcode','jump','fail') if k in row} for row in rows]))
    anchors=((0x186AA,3,0x20004000),(0x186B2,2,0x20010000),(0x186BA,10,0x1AB60),
             (0x186E2,11,0x2000C958),(0x18710,5,0x8038),(0x18724,5,0x9008))
    for pc,register,target in anchors:need(pair(data,pc,register)==target,'Original own-PC anchor target')
    memory=[row for row in retained[0]['rows'] if 0x186BA<=row['addr']<0x186F8]
    need(len(memory)==17 and sum(row['size'] for row in memory)==62,'Original memory slice62B/17')
    need(all(row['opcode']!='ret' and 'jal' not in row['opcode'] for row in memory),'Memory slice falls through, not a function return')
    expected={0x186F8:'li t0, 31',0x186FA:'csrw 0xbc0, t0',0x18700:'csrw 0x804, t0',
        0x1870C:'csrs mstatus, t0',0x1871C:'csrw mtvec, t0',0x1872C:'csrw mepc, t0',
        0x1875E:'lui a2, 0x20',0x1882C:'addi sp, sp, 16',0x1882E:'ret'}
    for pc,opcode in expected.items():need(by_pc[pc]['opcode']==opcode,'Exact source obligation instruction')
    need(by_pc[0x18720]['jump']==0x1874A and by_pc[0x18720]['fail']==0x18724,'Original clock call/link')
    need(by_pc[0x18730]['jump']==0x40000 and by_pc[0x18730]['opcode']=='j 0x40000','Terminal source handoff, no local return')
    clock=retained[1]['rows']
    need(all(not re.search(r'\b(?:a0|a1|t0|gp)\b',row['opcode']) for row in clock),'Clock does not reference A0/A1/T0/GP')
    need(all(not re.search(r'\bra\b',row['opcode']) for row in clock),'Clock has no explicit RA write; RET implicitly reads RA')
    need([row['addr'] for row in clock if row['opcode']=='ret']==[0x1882E],'Only original clock return')
    need(all('jal' not in row['opcode'] for row in clock),'Original clock is a no-call body')
    a2_mentions=[row for row in clock if re.search(r'\ba2\b',row['opcode'])]
    need(a2_mentions[0]['addr']==0x1875E and a2_mentions[0]['opcode']=='lui a2, 0x20','Incoming A2 killed before source read')
    need([row['addr'] for row in clock if re.search(r'\bsp\b',row['opcode'])]==
         [0x18754,0x18790,0x18792,0x187A6,0x187A8,0x187AC,0x187AE,0x187B2,0x187C8,0x187CA,0x1882C,0x18830],
         'Exact clock SP frame/access sites')
    last_word=data[0x1ABDC-0x8000:0x1ABE0-0x8000]
    need(last_word.hex()=='a1030000','Original last copy word')
    return dict(schema='TSL9-reset-memory-original-caller-audit-v1',passed=True,
        source_sha256=ORIGINAL_SHA,source_bytes=76800,source_base=0x8000,tool_sha256=sha(r2),
        reference_inputs=references,covered_code_bytes=372,covered_code_instructions=130,ranges=retained,
        original_memory_slice=dict(start=0x186BA,end_exclusive=0x186F8,bytes=62,instructions=17,
            fallthrough=True,has_return=False,copy_words=32,zero_words=8758,last_copy_word=929),
        original_anchor_targets=[dict(pc=p,register=register,target=t) for p,register,t in anchors],
        memory_exit_normal_context=dict(gp=0x20004000,sp=0x20010000,a0=0x2000C958,a1=0x2000C958,a2=0x20004080,t0=929,ra='unchanged incoming value'),
        clock=dict(entry=0x1874A,call_pc=0x18720,return_link=0x18724,ret_pc=0x1882E,
            bytes=234,instructions=93,entry_sp=0x20010000,frame_sp=0x2000FFF0,
            unchanged_explicit=['a0','a1','t0','gp','ra'],first_a2_definition=0x1875E,a2_value=0x20000,may_poll_without_bound=True),
        terminal_rom_context=dict(transfer_pc=0x18730,target=0x40000,gp=0x20004000,sp=0x20010000,
            a0=0x2000C958,a1=0x2000C958,a2=0x20000,t0=0x9008,ra=0x18724,mepc=0x9008,installed_ROM_identity_proved=False),
        original_executed=False,ISA_emulation=False,hardware=False,network=False,new_C_leaf_drop_in_proved=False,OTA_ready=False)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--image',type=Path,required=True);p.add_argument('--r2',type=Path,required=True);a=p.parse_args()
    print(json.dumps(audit(a.image.resolve(),a.r2.resolve()),indent=2))

if __name__=='__main__':main()
