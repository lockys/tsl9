"""Derive the complete19BF0 C/private-register regions from pinned offline evidence."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[2]
FRONTIER=ROOT/'analysis/memory-transfer-2026-10-24/evidence.json'
EXPECTED='90f0bc35a1bbbb474e0720394085f79cd0bf6e530b6cc87b85cd4b1ea58cb713'
def main():
    assert hashlib.sha256(FRONTIER.read_bytes()).hexdigest()==EXPECTED
    frontier=json.loads(FRONTIER.read_bytes());f=frontier['selected_functions'][0];ops=f['operations']
    assert f['start']==0x19bf0 and f['end']==0x19ca6 and len(ops)==54 and sum(x['size']for x in ops)==182
    by={x['addr']:x for x in ops};leaders={f['start']}
    for x in ops:
        if x.get('jump')in by:leaders.add(x['jump'])
        if x['type']in ('cjmp','jmp','ret')and x['addr']+x['size']in by:leaders.add(x['addr']+x['size'])
    starts=sorted(leaders);assert len(starts)==15
    def name(pc):return 'tsl9_callback_flow_external_19bf0' if pc==0x19bf0 else 'tsl9_memory_transfer_block_'+format(pc,'x')
    A={'a'+str(i)for i in range(6)}
    lines=[
        '#include <stdint.h>',
        '#if !defined(__riscv) || __riscv_xlen != 32',
        '#error Original RV32 private regions only; not a host memcpy implementation.',
        '#endif',
        '#ifdef __cplusplus',
        '#define ENTRY extern "C"',
        '#else',
        '#define ENTRY',
        '#endif',
        '#define REGION ENTRY __attribute__((used,noinline,noreturn,aligned(2)))',
        '#define REGS register uint32_t a0 __asm__("a0"),a1 __asm__("a1"),a2 __asm__("a2"),a3 __asm__("a3"),a4 __asm__("a4"),a5 __asm__("a5"); __asm__ volatile("":"=r"(a0),"=r"(a1),"=r"(a2),"=r"(a3),"=r"(a4),"=r"(a5)::"memory")',
        '#define LIVE __asm__ volatile("":"+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5)::"memory")',
        '#define PORT(code) __asm__ volatile(code:"+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5)::"memory")',
        '',
        '/* Complete original19BF0..19CA6 forward transfer,182B/54 instructions.',
        ' * C arithmetic/volatile access plus explicit register and control ports.',
        ' * Original unsigned address tests,byte/word paths and36B bulk order are retained.',
        ' * The bulk path loads8 words,stores1,loads the ninth,then completes the stores.',
        ' * T0/T1/T2/T3/T4/T5/T6/A6/A7 remain original scratch register ports;',
        ' * the pinned profile reserves them from C allocation. A0 is unchanged.',
        ' * These15 regions require original adjacency; they are not normal C ABI functions.',
        ' * No overlap,bounds,trap/IRQ,physical MCU/ROM/RAM or OTA compatibility claim. */',
        ''
    ]
    regions=[];controls=[]
    for i,start in enumerate(starts):
        end=starts[i+1]if i+1<len(starts)else f['end'];subset=[x for x in ops if start<=x['addr']<end]
        raw=bytes.fromhex(''.join(x['bytes']for x in subset))
        assert len(raw)==end-start
        regions.append(dict(name=name(start),start=start,end=end,bytes=len(raw),original_sha256=hashlib.sha256(raw).hexdigest()))
        lines.extend(['/* Original '+format(start,'X')+'..'+format(end,'X')+' */','REGION void '+name(start)+'(void)','{','    REGS;'])
        if start==0x19c40:lines.append('    /* Preserve the original9-word batch register bank and interleaved memory order. */')
        for x in subset:
            pc=x['addr'];op=x['opcode'];mn=op.split(' ')[0];args=[v.strip()for v in op[len(mn):].strip().split(',')]if' 'in op else[]
            statement=None
            if x['type']in ('cjmp','jmp'):
                target=x['jump'];assert target in by
                typ=16 if x['size']==4 else 44 if x['type']=='cjmp'else 45
                assert x['type']=='cjmp'or x['size']==2
                reloc={16:'R_RISCV_BRANCH',44:'R_RISCV_RVC_BRANCH',45:'R_RISCV_RVC_JUMP'}[typ]
                label='.Lmemory_transfer_edge_'+format(pc,'x')
                if x['type']=='jmp':ins='c.j '+label
                elif x['size']==2:ins='c.'+mn+' '+','.join(args[:-1])+','+label
                else:ins=mn+' '+','.join(args[:-1])+','+label
                body=label+':\n.option push\n.option '+('norvc'if x['size']==4 else'rvc')+'\n'+ins+'\n.option pop\n.reloc .-'+str(x['size'])+','+reloc+','+name(target)+'\n'
                statement='PORT('+json.dumps(body)+');'
                controls.append(dict(owner=name(start),offset=pc-start,PC=pc,size=x['size'],type=typ,target=name(target),target_PC=target))
            elif mn=='li'and args[0]in A:statement=args[0]+' = UINT32_C('+str(int(args[1],0))+'); LIVE;'
            elif mn=='mv'and all(a in A for a in args):statement=args[0]+' = '+args[1]+'; LIVE;'
            elif mn in ('add','xor')and all(a in A for a in args):
                a,b,c=args;statement=a+' = '+b+(' + 'if mn=='add'else' ^ ')+c+'; LIVE;'
            elif mn in ('addi','andi')and args[0]in A and args[1]in A:
                a,b,c=args;statement=a+' = '+b+(' + 'if mn=='addi'else' & ')+hex(int(c,0)&0xffffffff)+'u; LIVE;'
            elif mn in ('lbu','lw','sb','sw'):
                reg=args[0];mem=re.fullmatch(r'(-?\d+)\((\w+)\)',args[1]);assert mem
                off,base=int(mem[1]),mem[2];bits=8 if mn in ('lbu','sb')else 32
                if base in A and reg in A:
                    address=base+(' + '+str(off)+'u'if off>=0 else' - '+str(-off)+'u')
                    ptr='(volatile uint'+str(bits)+'_t *)(uintptr_t)('+address+')'
                    statement=(reg+' = *'+ptr if mn.startswith('l')else'*'+ptr+' = (uint'+str(bits)+'_t)'+reg)+'; LIVE;'
            if statement is None:
                assert mn in ('lw','sw','ret')
                body=('.option push\n.option norvc\n'+op+'\n.option pop\n')if x['size']==4 else op
                statement='PORT('+json.dumps(body)+');'
            lines.append('    '+statement)
        lines.extend(['    __builtin_unreachable();','}',''])
    assert len(regions)==15 and len(controls)==10
    print(json.dumps(dict(source='\n'.join(lines),regions=regions,controls=controls,PC_relative_pairs=[],literal_data=None,
        undefined=[],frontier=FRONTIER.relative_to(ROOT).as_posix(),frontier_sha256=EXPECTED)))
if __name__=='__main__':main()

