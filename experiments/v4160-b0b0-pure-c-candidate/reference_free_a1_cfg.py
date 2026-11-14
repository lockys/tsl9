#!/usr/bin/env python3
"""Check a1 def-before-use on a pinned conditional Xwchc candidate CFG."""
import argparse
import hashlib
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[2]
LEDGER='analysis/v4160-adc-caller-2026-10-22/continuation-review/ledger.json'
LEDGER_SHA='3ac34fb34d52f4c516c148a6f2237daa8e42bbcd025fe0369cadcc6229e81821'
CASES=(('carrier-dec2023','analysis/wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22',0x40380),('carrier','analysis/wch-resident-candidate-2026-10-21/carrier/REFERENCE-CANDIDATE-ONLY-00040000-0006EC56.bin','b02cf8ec6829425a558887bd6bc10d28ae1f0e2e9e1850333f0bab6088e9e941',0x403c0))
BRANCH={'beq','bne','bltu','bgeu','blt','bge'}
OPS={'add','addi','beq','bgeu','bltu','bne','fence.i','jal','jalr','lbu','lui','lw','mv','qk.c.lhu','qk.c.sh','sb','sh','slli','srli','sw'}

def need(ok,msg):
    if not ok: raise ValueError(msg)

def decode_xwch_halfword(raw):
    need(len(raw)==2,'Xwchc width')
    word=int.from_bytes(raw,'little');kind=word&0xe003
    need(kind in (0x2002,0xa002),'Xwchc opcode')
    base=8+((word>>7)&7); reg=8+((word>>2)&7)
    offset=(((word>>10)&7)<<3)|(((word>>5)&3)<<1)
    return ('qk.c.lhu' if kind==0x2002 else 'qk.c.sh',base,reg,offset)

def check_halfword_row(row):
    op,base,reg,offset=decode_xwch_halfword(bytes.fromhex(row['raw_hex']))
    need(row['op']==op and row['rs1']==base and row['immediate']==offset and row['memory_width']==16,'Xwchc operand mismatch')
    if op=='qk.c.lhu':need(row['rd']==reg and row['rs2'] is None,'Xwchc load register')
    else:need(row['rs2']==reg and row['rd'] is None,'Xwchc store register')

def signed(value,bits):
    return value-(1<<bits) if value&(1<<(bits-1)) else value

def check_control_row(row):
    raw=bytes.fromhex(row['raw_hex']);pc=row['PC'];op=row['op']
    if len(raw)==4:
        word=int.from_bytes(raw,'little');need(word&0x7f==0x63,'branch opcode')
        kind={0:'beq',1:'bne',4:'blt',5:'bge',6:'bltu',7:'bgeu'}.get((word>>12)&7)
        imm=((word>>31)&1)<<12|((word>>7)&1)<<11|((word>>25)&0x3f)<<5|((word>>8)&0xf)<<1
        need((op,row['rs1'],row['rs2'],row['target'])==(kind,(word>>15)&31,(word>>20)&31,(pc+signed(imm,13))&0xffffffff),'RV32 branch fields')
    elif len(raw)==2:
        word=int.from_bytes(raw,'little');quad=word&3;funct=word>>13
        if quad==1 and funct in (6,7):
            imm=((word>>12)&1)<<8|((word>>10)&3)<<3|((word>>5)&3)<<6|((word>>3)&3)<<1|((word>>2)&1)<<5
            need((op,row['rs1'],row['rs2'],row['target'])==(('beq' if funct==6 else 'bne'),8+((word>>7)&7),0,(pc+signed(imm,9))&0xffffffff),'compressed branch fields')
        elif quad==1 and funct==5:
            imm=((word>>12)&1)<<11|((word>>11)&1)<<4|((word>>9)&3)<<8|((word>>8)&1)<<10|((word>>7)&1)<<6|((word>>6)&1)<<7|((word>>3)&7)<<1|((word>>2)&1)<<5
            need((op,row['rd'],row['target'])==('jal',0,(pc+signed(imm,12))&0xffffffff),'compressed jump fields')
        else:
            need(word==0x8082 and (op,row['rd'],row['rs1'],row['immediate'])==('jalr',0,1,0),'compressed return')
    else:raise ValueError('control width')

def analyze(rows):
    idx={r['PC']:r for r in rows};need(len(idx)==len(rows),'duplicate PC')
    pending=[(0x20000110,False)];seen=set();reads=set();returns=set();writes=set()
    while pending:
        pc,killed=pending.pop()
        if (pc,killed) in seen:continue
        seen.add((pc,killed));need(pc in idx,'CFG escape');r=idx[pc];op=r['op'];need(op in OPS,'unknown opcode')
        if 11 in (r['rs1'],r['rs2']):
            reads.add(pc);need(killed,f'incoming a1 read at {pc:#x}')
        if r['rd']==11:
            writes.add(pc);killed=True
        if op=='jalr':
            need((r['rd'],r['rs1'],r['immediate'])==(0,1,0),'unexpected indirect exit')
            returns.add((pc,killed));continue
        if op=='jal':
            need(r['rd']==0,'unexpected call');successors=[r['target']]
        elif op in BRANCH:successors=[pc+r['bytes'],r['target']]
        else:successors=[pc+r['bytes']]
        pending.extend((q,killed) for q in successors)
    need(reads=={0x20000180,0x200001a4,0x200001a6,0x200001a8,0x200001cc},'read sites')
    need(writes=={0x20000174,0x200001a4,0x200001a6,0x200001c6},'write sites')
    need(any(not killed for _,killed in returns),'early preserved return absent')
    return len(seen),len(reads),len(returns)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=ROOT);root=parser.parse_args().root
    ledger=(root/LEDGER).read_bytes();need(hashlib.sha256(ledger).hexdigest()==LEDGER_SHA,'ledger hash')
    candidates=json.loads(ledger)['candidates']
    for name,path,digest,flash in CASES:
        p=root/path
        if not p.is_file():raise SystemExit(f'SKIP: missing reference carrier {path}')
        data=p.read_bytes();need(hashlib.sha256(data).hexdigest()==digest,'carrier hash')
        rows=candidates[name]['groups']['free']; cursor=0x20000110
        for r in rows:
            need(r['PC']==cursor,'gap or overlap')
            raw=bytes.fromhex(r['raw_hex']);need(len(raw)==r['bytes'],'width')
            off=flash-0x40000+cursor-0x20000110
            need(data[off:off+len(raw)]==raw,'row/carrier mismatch')
            if r['op'] in ('qk.c.lhu','qk.c.sh'):check_halfword_row(r)
            if r['op'] in BRANCH or r['op'] in ('jal','jalr'):check_control_row(r)
            cursor+=len(raw)
        need(cursor==0x200001e4,'body end')
        n,reads,returns=analyze(rows)
        print(f'PASS: {name}: {len(rows)} pinned rows, {n} CFG states, {reads} a1 read sites, {returns} return states; incoming a1 never read before write')
    print('LIMIT: independently checks branch/jump fields and Xwchc halfword operands; otherwise assumes ledger decoding, conservative syntactic CFG, successful accesses, no interrupts or code modification; early return may preserve a1; not device execution')

if __name__=='__main__':main()
