#!/usr/bin/env python3
"""Derive two complete original pointer/payload support functions; static bytes only."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2]
def need(ok,label):
    if not ok:raise ValueError(label)
def generate():
    evidence=json.loads((ROOT/'analysis/callback-support-2026-10-24/evidence.json').read_bytes())
    fw=(ROOT/evidence['firmware']).read_bytes()
    need(hashlib.sha256(fw).hexdigest()==evidence['firmware_sha256'],'Original firmware')
    fs=evidence['selected_functions'];need([f['start']for f in fs]==[0xd1a8,0x16dac],'Both original entries')
    for f in fs:
        at=f['start']
        for op in f['operations']:
            b=bytes.fromhex(op['bytes']);need(op['addr']==at and len(b)==op['size']==(4 if b[0]&3==3 else 2),'Complete contiguous instruction')
            need(b==fw[at-0x8000:at-0x8000+len(b)],'Actual original instruction');at+=len(b)
        need(at==f['end'],'Full selected extent')
    need(sum(len(f['operations'])for f in fs)==18,'All18 original instructions')
    def control(pc,kind,target):
        mn='bltu a4,a5' if kind==16 else 'jal ra'
        return f'    PORT(".Lcallback_support_{pc:x}:\\n.option push\\n.option norvc\\n{mn},.Lcallback_support_{pc:x}\\n.option pop\\n.reloc .-4,R_RISCV_'+('BRANCH'if kind==16 else'JAL')+f',{target}\\n");'
    header=['#include <stdint.h>','#if !defined(__riscv) || __riscv_xlen != 32','#error Original RV32 private regions only; not a host transport model.','#endif','#ifdef __cplusplus','#define ENTRY extern "C"','#else','#define ENTRY','#endif',
    '#define REGION ENTRY __attribute__((used,noinline,noreturn,aligned(2)))',
    '#define REGS register uint32_t a0 __asm__("a0"),a1 __asm__("a1"),a2 __asm__("a2"),a3 __asm__("a3"),a4 __asm__("a4"),a5 __asm__("a5"); __asm__ volatile("":"=r"(a0),"=r"(a1),"=r"(a2),"=r"(a3),"=r"(a4),"=r"(a5)::"memory")',
    '#define LIVE __asm__ volatile("":"+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5)::"memory")',
    '#define PORT(code) __asm__ volatile(code:"+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5)::"memory")','',
    '/* D1A8 returns original-coordinate pointer2000BF48,without dereferencing it.',
    ' * Complete16DAC preserves low-byte guard,full A0,32B frame,zero2B payload,',
    ' * caller return address,and actual16CC4 call. These five regions require',
    ' * original adjacency and private register context; physical roles are unknown. */','']
    bodies=[
      ('tsl9_callback_flow_external_d1a8',0xd1a8,0xd1b2,[
       '    PORT(".option push\\n.option norvc\\nauipc a0, 0x1ffff\\n.option pop\\n");',
       '    a0 = a0 + UINT32_C(0xfffffda0); LIVE;','    PORT("ret");']),
      ('tsl9_callback_flow_external_16dac',0x16dac,0x16dba,[
       '    a5 = a0 - UINT32_C(1); LIVE;','    a5 = a5 & UINT32_C(255); LIVE;',
       '    a4 = UINT32_C(1); LIVE;',control(0x16db6,16,'tsl9_callback_support_block_16dd2')]),
      ('tsl9_callback_support_block_16dba',0x16dba,0x16dcc,[
       '    PORT("addi sp, sp, -32");','    register uintptr_t frame __asm__("sp");',
       '    __asm__ volatile("":"=r"(frame)::"memory");',
       '    a1 = frame + UINT32_C(12); LIVE;','    a3 = UINT32_C(0); LIVE;','    a2 = UINT32_C(2); LIVE;',
       '    PORT("sw ra, 28(sp)");','    *(volatile uint16_t *)(uintptr_t)(frame + UINT32_C(12)) = 0; LIVE;',
       control(0x16dc8,17,'tsl9_channel_external_16cc4')]),
      ('tsl9_callback_support_block_16dcc',0x16dcc,0x16dd2,[
       '    PORT("lw ra, 28(sp)");','    PORT("addi sp, sp, 32");','    PORT("ret");']),
      ('tsl9_callback_support_block_16dd2',0x16dd2,0x16dd4,['    PORT("ret");'])]
    lines=header;regions=[]
    for name,start,end,body in bodies:
        lines += [f'/* Original0x{start:X}..0x{end:X}. */',f'REGION void {name}(void)','{','    REGS;',*body,'    __builtin_unreachable();','}','']
        raw=fw[start-0x8000:end-0x8000]
        regions.append(dict(name=name,start=start,end=end,bytes=end-start,original_sha256=hashlib.sha256(raw).hexdigest()))
    controls=[dict(owner=bodies[1][0],offset=10,PC=0x16db6,size=4,type=16,target=bodies[4][0],target_PC=0x16dd2),
              dict(owner=bodies[2][0],offset=14,PC=0x16dc8,size=4,type=17,target='tsl9_channel_external_16cc4',target_PC=0x16cc4)]
    need(sum(r['bytes']for r in regions)==50,'All50 original bytes')
    return dict(source='\n'.join(lines),regions=regions,controls=controls,PC_relative_pairs=[],literal_data=None,
      pointer_address=0x2000bf48,guard='((A0-1)&255)<=1;fullA0 retained',stack_frame_bytes=32,payload_bytes=2,payload_store_offset=12,
      RA_save_offset=28,callee_PC=0x16cc4)
if __name__=='__main__':print(json.dumps(generate(),ensure_ascii=True))
