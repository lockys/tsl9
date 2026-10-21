#!/usr/bin/env python3
"""Static original-caller and bounded direct-transfer candidate audit."""
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
SPANS=((0x9008,0x901A,8),(0x9250,0x9290,19),(0x9A42,0x9AD2,46),
       (0x9F4C,0x9F74,15),(0x131C2,0x131E2,10))
OLD_SEALS=(
    ('apk-analysis/tsl9-v4160-system-clock-query-2026-10-21/source/final-audit.json','ebf0521f52c5142d1dc7969aaca17bb1c7567065165eba4c88fd4523e30b6a51'),
    ('apk-analysis/tsl9-v4160-interrupt-init-2026-10-21/abi-review/final-audit.json','0ff5d04207572f5f0cb9e4168de5583f28e15901938b47428d1664d90b26451a'),
)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def need(okay,message):
    if not okay:raise RuntimeError(message)
def signed(value,bits):return value-(1<<bits) if value&(1<<(bits-1)) else value

def direct(data,pc):
    if len(data)<2:return None
    half=int.from_bytes(data[:2],'little')
    if half&3==3 and len(data)>=4:
        word=int.from_bytes(data[:4],'little')
        if word&127!=0x6f:return None
        immediate=(((word>>31)&1)<<20)|(((word>>12)&255)<<12)|(((word>>20)&1)<<11)|(((word>>21)&1023)<<1)
        return dict(pc=pc,target=(pc+signed(immediate,21))&0xffffffff,size=4,rd=(word>>7)&31,encoding='JAL',bytes=data[:4].hex())
    if half&3==1 and half>>13 in (1,5):
        immediate=(((half>>12)&1)<<11)|(((half>>11)&1)<<4)|(((half>>9)&3)<<8)|(((half>>8)&1)<<10)|(((half>>7)&1)<<6)|(((half>>6)&1)<<7)|(((half>>3)&7)<<1)|(((half>>2)&1)<<5)
        return dict(pc=pc,target=(pc+signed(immediate,12))&0xffffffff,size=2,rd=1 if half>>13==1 else 0,encoding='C.JAL' if half>>13==1 else 'C.J',bytes=data[:2].hex())
    return None

def audit(image,r2):
    data=image.read_bytes();need(len(data)==76800 and sha(image)==ORIGINAL_SHA,'Exact original ID2966 runtime')
    references=[]
    for relative,expected in OLD_SEALS:
        p=ROOT/relative;need(sha(p)==expected,'Existing immutable source seal')
        seal=json.loads(p.read_text())
        for member in seal['members']:
            q=p.parent/member['path'];need(q.stat().st_size==member['bytes'] and sha(q)==member['sha256'],'Existing immutable source member')
        references.append(dict(path=relative,sha256=expected))
    command=';'.join('pdj 50 @ '+hex(start) for start,_,_ in SPANS)
    process=subprocess.run([str(r2),'-2','-a','riscv','-b','32','-m','0x8000','-q','-c',command,str(image)],capture_output=True,text=True,check=True,timeout=60)
    groups=[json.loads(line) for line in process.stdout.splitlines() if line.startswith('[')]
    need(len(groups)==len(SPANS),'One static group per bounded span')
    retained=[];by_pc={}
    for (start,end,count),group in zip(SPANS,groups):
        rows=[row for row in group if start<=row['addr']<end]
        need(len(rows)==count,'Complete bounded instruction count');cursor=start
        for row in rows:
            need(row['addr']==cursor,'Contiguous original instructions')
            need(data[cursor-0x8000:cursor-0x8000+row['size']].hex()==row['bytes'],'Original instruction bytes')
            by_pc[cursor]=row;cursor+=row['size']
        need(cursor==end,'Exact bounded source end')
        retained.append(dict(start=start,end_exclusive=end,source_bytes=end-start,instructions=count,
            sha256=hashlib.sha256(data[start-0x8000:end-0x8000]).hexdigest(),
            rows=[{k:row[k] for k in ('addr','size','bytes','opcode','jump','fail') if k in row} for row in rows]))
    expected_calls=((0x900C,0x9250,0x900E),(0x9254,0x18834,0x9258),(0x9258,0x9A42,0x925C),
                    (0x925C,0x1973C,0x9260),(0x9260,0x9F4C,0x9264),(0x9264,0x131C2,0x9268))
    for pc,target,continuation in expected_calls:
        need(by_pc[pc]['jump']==target and by_pc[pc]['fail']==continuation,'Exact direct call and return link')
        decoded=direct(data[pc-0x8000:pc-0x8000+4],pc)
        need(decoded and decoded['target']==target and decoded['rd']==1,'Independent direct-format decode')
    need(by_pc[0x131CA]['opcode']=='lui a1, 0x8078','A1 killed before callback')
    need(by_pc[0x131CE]['opcode']=='li a2, 112','A2 killed before callback')
    need(by_pc[0x131D8]['opcode']=='auipc a0, 0x1fff9','A0 killed before callback')
    need(by_pc[0x131E0]['opcode']=='jalr a5','First opaque callback boundary')
    need(by_pc[0x131C6]['opcode']=='lw a5, 76(a5)','Fresh opaque callback pointer at 0x4004C')
    need(by_pc[0x9A50]['opcode']=='csrc 0x800, s2' and by_pc[0x9AC2]['opcode']=='csrs 0x800, s2','Intervening CSR clear/set boundaries')
    old_irq=json.loads((ROOT/'apk-analysis/tsl9-v4160-interrupt-init-2026-10-21/abi-review/verification.json').read_text(encoding='utf-8-sig'))
    old_clock=json.loads((ROOT/'apk-analysis/tsl9-v4160-system-clock-query-2026-10-21/source/retained-source.json').read_text())
    a3_rows=[row for part in retained if part['start'] in (0x9A42,0x9F4C,0x131C2) for row in part['rows']]
    a3_rows += [row for part in old_irq['ranges'] if part['start']!=0x9A42 for row in part['rows']]
    a3_rows += old_clock['groups']['derive1973c']
    need(len(a3_rows)==130 and all(not re.search(r'\ba3\b',row['opcode']) for row in a3_rows),'A3 has no direct reference in concrete passthrough bodies/helper paths')
    targets={0x9250,0x18834,0x1973C};candidates=[]
    for offset in range(0,len(data)-1,2):
        decoded=direct(data[offset:offset+4],0x8000+offset)
        if decoded and decoded['target'] in targets:candidates.append(decoded)
    need([(x['pc'],x['target']) for x in candidates]==[(0x900C,0x9250),(0x9254,0x18834),(0x925C,0x1973C)],'Bounded direct-format candidates')
    for pc,target in ((0x900E,0x8180),(0x9268,0x8E88),(0x928C,0x17BF6)):
        decoded=direct(data[pc-0x8000:pc-0x8000+4],pc);need(decoded and decoded['target']==target,'Forward/backward immediate decoding check')
    return dict(schema='TSL9-clock-caller-static-source-audit-v1',passed=True,
        original_sha256=ORIGINAL_SHA,original_bytes=76800,source_base=0x8000,
        tool_sha256=sha(r2),source_references=references,source_bytes=298,source_instructions=98,
        ranges=retained,known_calls=[dict(pc=p,target=t,continuation=c) for p,t,c in expected_calls],
        direct_scan=dict(halfword_positions=len(data)//2,target_entries=sorted(targets),raw_candidates=candidates,
            candidate_code_boundary_proof=False,computed_indirect_calls_covered=False,whole_program_xrefs_complete=False),
        first_unresolved_callback=dict(call_pc=0x131E0,pointer_read_pc=0x131C6,pointer_address=0x4004C,
            a3_exposed=True,consumption_proved=False,a3_passthrough_static_rows=130),
        original_executed=False,ISA_emulation=False,hardware=False,network=False,original_ABI_proved=False,OTA_ready=False)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image',type=Path,required=True);parser.add_argument('--r2',type=Path,required=True)
    args=parser.parse_args();print(json.dumps(audit(args.image.resolve(),args.r2.resolve()),indent=2))

if __name__=='__main__':main()
