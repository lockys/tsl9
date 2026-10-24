"""Derive the complete18834/1973C C/private-register scopes from pinned static evidence."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[2]
FRONTIER=ROOT/'analysis/clock-original-2026-10-24/evidence.json'
EXPECTED='22164fed5e2f848bbaed5d231995a471162e087c19e7ed6b41a58b755b4f8a2e'
def main():
    assert hashlib.sha256(FRONTIER.read_bytes()).hexdigest()==EXPECTED
    frontier=json.loads(FRONTIER.read_bytes());functions=frontier['selected_functions']
    ops=[x for f in functions for x in f['operations']]
    assert len(functions)==2 and len(ops)==69 and sum(x['size']for x in ops)==214
    by={x['addr']:x for x in ops};entries={f['start']:f['entry']for f in functions};leaders=set(entries)
    for x in ops:
        if x.get('jump')in by:leaders.add(x['jump'])
        if x['type']in ('cjmp','jmp','ret')and x['addr']+x['size']in by:leaders.add(x['addr']+x['size'])
    starts=sorted(leaders);assert len(starts)==16
    def name(pc):return entries.get(pc,'tsl9_clock_original_block_'+format(pc,'x'))
    A={'a'+str(i)for i in range(6)}
    lines=[
        '#include <stdint.h>',
        '#if !defined(__riscv) || __riscv_xlen != 32',
        '#error Original RV32 private regions only; not a host clock model.',
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
        '/* Complete18834..188E2 query and1973C..19764 field-update scopes:214B/69i.',
        ' * C arithmetic/volatile access plus explicit GP and local-control ports.',
        ' * Preserve fresh peripheral reads,GP+64 byte lookup,and GP+108 readback/stores.',
        ' * A2 is written only in the external-source branch; no entry snapshot/restore.',
        ' * Fields preserve unsigned DIVU,8-bit quotient and GP+382/GP+380 store widths.',
        ' * These16 regions require original adjacency and are not normal C ABI functions.',
        ' * No physical clock,MCU,resident,GP/table ownership,IRQ or OTA proof. */',
        ''
    ]
    regions=[];controls=[]
    for i,start in enumerate(starts):
        limit=next(f['end']for f in functions if f['start']<=start<f['end'])
        end=min(starts[i+1],limit)if i+1<len(starts)else limit
        subset=[x for x in ops if start<=x['addr']<end];raw=bytes.fromhex(''.join(x['bytes']for x in subset))
        assert len(raw)==end-start
        regions.append(dict(name=name(start),start=start,end=end,bytes=len(raw),original_sha256=hashlib.sha256(raw).hexdigest()))
        lines.extend(['/* Original '+format(start,'X')+'..'+format(end,'X')+' */','REGION void '+name(start)+'(void)','{','    REGS;'])
        for x in subset:
            pc=x['addr'];op=x['opcode'];mn=op.split(' ')[0]
            args=[v.strip()for v in op[len(mn):].strip().split(',')]if' 'in op else[]
            statement=None
            if x['type']in ('cjmp','jmp'):
                target=x['jump'];assert target in by
                typ=16 if x['size']==4 else 44 if x['type']=='cjmp'else 45
                assert x['type']=='cjmp'or x['size']==2
                reloc={16:'R_RISCV_BRANCH',44:'R_RISCV_RVC_BRANCH',45:'R_RISCV_RVC_JUMP'}[typ]
                label='.Lclock_original_edge_'+format(pc,'x')
                if x['type']=='jmp':ins='c.j '+label
                elif x['size']==2:ins='c.'+mn+' '+','.join(args[:-1])+','+label
                else:ins=mn+' '+','.join(args[:-1])+','+label
                body=label+':\n.option push\n.option '+('norvc'if x['size']==4 else'rvc')+'\n'+ins+'\n.option pop\n.reloc .-'+str(x['size'])+','+reloc+','+name(target)+'\n'
                statement='PORT('+json.dumps(body)+');'
                controls.append(dict(owner=name(start),offset=pc-start,PC=pc,size=x['size'],type=typ,target=name(target),target_PC=target))
            elif mn=='li'and args[0]in A:statement=args[0]+' = UINT32_C('+str(int(args[1],0))+'); LIVE;'
            elif mn=='lui'and args[0]in A:statement=args[0]+' = UINT32_C('+hex((int(args[1],0)<<12)&0xffffffff)+'); LIVE;'
            elif mn in ('add','and','mul','divu')and all(a in A for a in args):
                a,b,c=args;statement=a+' = '+b+' '+{'add':'+','and':'&','mul':'*','divu':'/'}[mn]+' '+c+'; LIVE;'
            elif mn in ('addi','andi','slli','srli')and args[0]in A and args[1]in A:
                a,b,c=args;token={'addi':'+','andi':'&','slli':'<<','srli':'>>'}[mn]
                val=hex(int(c,0)&0xffffffff)+'u'if mn in('addi','andi')else str(int(c,0))+'u'
                statement=a+' = '+b+' '+token+' '+val+'; LIVE;'
            elif mn=='srl'and all(a in A for a in args):
                a,b,c=args;statement=a+' = '+b+' >> ('+c+' & 31u); LIVE;'
            elif mn in ('lbu','lw','sb','sh','sw'):
                reg=args[0];mem=re.fullmatch(r'(-?\d+)\((\w+)\)',args[1]);assert mem
                off,base=int(mem[1]),mem[2];bits={'lbu':8,'lw':32,'sb':8,'sh':16,'sw':32}[mn]
                if base in A and reg in A:
                    address=base+(' + '+str(off)+'u'if off>=0 else' - '+str(-off)+'u')
                    ptr='(volatile uint'+str(bits)+'_t *)(uintptr_t)('+address+')'
                    statement=(reg+' = *'+ptr if mn.startswith('l')else'*'+ptr+' = (uint'+str(bits)+'_t)'+reg)+'; LIVE;'
            if statement is None:
                assert mn in ('addi','lw','sw','sb','sh','ret')
                body=('.option push\n.option norvc\n'+op+'\n.option pop\n')if x['size']==4 else op
                statement='PORT('+json.dumps(body)+');'
            lines.append('    '+statement)
        lines.extend(['    __builtin_unreachable();','}',''])
    assert len(regions)==16 and len(controls)==11
    print(json.dumps(dict(source='\n'.join(lines),regions=regions,controls=controls,PC_relative_pairs=[],literal_data=None,
        undefined=[],frontier=FRONTIER.relative_to(ROOT).as_posix(),frontier_sha256=EXPECTED)))
if __name__=='__main__':main()
