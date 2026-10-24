#!/usr/bin/env python3
"""Derive eleven complete original-coordinate byte getters; static arithmetic only."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2]
EVIDENCE=ROOT/'analysis/callback-read-leaves-2026-10-24/evidence.json'
FW=ROOT/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
def need(ok,label):
    if not ok:raise ValueError(label)
def generate():
    fw=FW.read_bytes()
    need(hashlib.sha256(fw).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','Exact original firmware')
    e=json.loads(EVIDENCE.read_bytes());selected=e['selected_functions']
    need(len(selected)==11,'Eleven selected complete leaves')
    lines=['#include <stdint.h>','#if !defined(__riscv) || __riscv_xlen != 32','#error Original RV32 private entries only; no host state model.','#endif','#ifdef __cplusplus','#define ENTRY extern "C"','#else','#define ENTRY','#endif',
    '#define REGION ENTRY __attribute__((used,noinline,noreturn,aligned(2)))',
    '#define REGS register uint32_t a0 __asm__("a0"); __asm__ volatile("":"=r"(a0)::"memory")',
    '#define LIVE __asm__ volatile("":"+r"(a0)::"memory")',
    '#define PORT(code) __asm__ volatile(code:"+r"(a0)::"memory")','',
    '/* Eleven complete byte getters:94B/29 instructions. C volatile loads keep',
    ' * original AUIPC or live GP addressing; RET is an explicit private ABI port.',
    ' * Link at each original PC before interpreting PC-relative data addresses.',
    ' * Field meaning, concurrent state, physical RAM and OTA remain unproved. */','']
    regions=[];facts=[]
    for f in selected:
        ops=f['operations'];raw=b''.join(bytes.fromhex(o['bytes'])for o in ops)
        at=f['start']
        for op in ops:
            b=bytes.fromhex(op['bytes'])
            need(op['addr']==at and len(b)==op['size']==(4 if b[0]&3==3 else 2),'Contiguous actual instruction')
            at+=len(b)
        need(at==f['end'] and raw==fw[f['start']-0x8000:f['end']-0x8000] and raw[-2:]==b'\x82\x80','Whole original leaf ending RET')
        name=f['name'];regions.append(dict(name=name,start=f['start'],end=f['end'],bytes=len(raw),original_sha256=hashlib.sha256(raw).hexdigest()))
        lines += [f"/* Original0x{f['start']:X}..0x{f['end']:X}. */",f'REGION void {name}(void)','{','    REGS;']
        if len(ops)==3:
            hi=int.from_bytes(bytes.fromhex(ops[0]['bytes']),'little')
            lo=int.from_bytes(bytes.fromhex(ops[1]['bytes']),'little')
            need(hi&0xfff==0x517 and lo&0xfffff==0x54503,'AUIPC A0 and LBU A0,imm(A0)')
            imm=lo>>20;imm=imm-4096 if imm&2048 else imm
            target=(f['start']+(hi&0xfffff000)+imm)&0xffffffff
            lines += [f'    PORT(".option push\\n.option norvc\\nauipc a0, 0x{hi>>12:x}\\n.option pop\\n");',
                      f'    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x{imm&0xffffffff:08x})); LIVE;']
            facts.append(dict(name=name,load_PC=ops[1]['addr'],base='original_PC_relative_A0',byte_address=target,unsigned_byte_to_A0=True))
        else:
            need(len(ops)==2,'Only LBU/RET or AUIPC/LBU/RET')
            lo=int.from_bytes(bytes.fromhex(ops[0]['bytes']),'little')
            need(lo&0xfffff==0x1c503,'LBU A0,imm(GP)')
            imm=lo>>20;imm=imm-4096 if imm&2048 else imm
            lines += ['    register uintptr_t original_gp __asm__("gp");',
                      '    __asm__ volatile("":"=r"(original_gp)::"memory");',
                      f'    a0 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x{imm&0xffffffff:08x})); LIVE;']
            facts.append(dict(name=name,load_PC=ops[0]['addr'],base='live_GP',GP_offset=imm,unsigned_byte_to_A0=True,GP_runtime_value_proved=False))
        lines += ['    PORT("ret");','    __builtin_unreachable();','}','']
    need(sum(r['bytes']for r in regions)==94 and sum(len(f['operations'])for f in selected)==29,'Complete94B29i')
    return dict(source='\n'.join(lines),regions=regions,controls=[],PC_relative_pairs=[],literal_data=None,read_facts=facts)
if __name__=='__main__':print(json.dumps(generate(),ensure_ascii=True))
