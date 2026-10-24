"""Derive record-consumer basic-block C regions from retained, pinned disassembly."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[2]
FRONTIER=ROOT/'analysis/rf-completion-2026-10-24/next-c776-candidate.json'
EXPECTED='feaeca479cd5a7362e9b15332db71835c5d52c184845912b2b35533fe0ff7b3f'
def main():
    assert hashlib.sha256(FRONTIER.read_bytes()).hexdigest()==EXPECTED
    d=json.loads(FRONTIER.read_bytes());ops=d['operations'];d['ranges']=[{'start':0xc776,'end':0xc798},{'start':0xc798,'end':0xc7aa},{'start':0xc7aa,'end':0xc7e8}]
    assert len(ops)==42 and sum(x['size']for x in ops)==114
    entry_PCs={0xc776,0xc798,0xc7aa};leaders=entry_PCs|{x['start']for x in d['ranges']};by={x['addr']:x for x in ops}
    for x in ops:
        if x.get('jump')in by:leaders.add(x['jump'])
        if x['type']in ['call','ucall','cjmp','jmp','ret','rjmp']or x['opcode']=='mret':
            if x['addr']+x['size']in by:leaders.add(x['addr']+x['size'])
    starts=sorted(leaders);name=lambda pc:'tsl9_record_consumer_'+('entry_'if pc in entry_PCs else'block_')+format(pc,'x')
    external={0xc6a8:'tsl9_record_consumer_provider_c6a8',0xfaf8:'tsl9_record_consumer_provider_faf8',0x82a8:'tsl9_record_consumer_provider_82a8',0x12a08:'tsl9_record_consumer_provider_12a08'}
    regions=[];controls=[];lines=[
        '#include <stdint.h>',
        '#if !defined(__riscv) || __riscv_xlen != 32',
        '#error Original RV32 private regions only; never execute this experiment.',
        '#endif',
        '#ifdef __cplusplus',
        '#define ENTRY extern "C"',
        '#else',
        '#define ENTRY',
        '#endif',
        '#define REGION ENTRY __attribute__((used,noinline,noreturn,aligned(2)))',
        '#define REGS register uint32_t a0 __asm__("a0"),a1 __asm__("a1"),a2 __asm__("a2"),a3 __asm__("a3"),a4 __asm__("a4"),a5 __asm__("a5"); __asm__ volatile("":"=r"(a0),"=r"(a1),"=r"(a2),"=r"(a3),"=r"(a4),"=r"(a5)::"memory")',
        '#define LIVE __asm__ volatile("":"+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5)::"memory")',
        '#define CALL_PORT(code) __asm__ volatile(code:"+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5)::"memory")',
        '',
        '/* OriginalC776..C7E8 only. Architectural basic blocks have deliberate',
        ' * fallthrough adjacency. They are not ordinary independently callable C.',
        ' * C unsigned arithmetic/volatile memory use fixed A-register ports.',
        ' * Copy16B frame/clear tail/conditional callback32B frame remain separate entries.',
        ' * SP/S registers, calls, RA returns and no-link indirect tail transfers stay explicit.',
        ' * No target execution, standard IRQ ABI or original-PC placement claim. */',
        '']
    A={'a'+str(i)for i in range(6)}
    def quoted(s):return json.dumps(s)
    for i,start in enumerate(starts):
        limit=next(x['end']for x in d['ranges']if x['start']<=start<x['end'])
        end=min(starts[i+1],limit)if i+1<len(starts)else limit
        subset=[x for x in ops if start<=x['addr']<end]
        original=bytes.fromhex(''.join(x['bytes']for x in subset))
        regions.append(dict(name=name(start),start=start,end=end,bytes=end-start,original_sha256=hashlib.sha256(original).hexdigest()))
        lines.extend(['/* Original '+format(start,'X')+'..'+format(end,'X')+' */','REGION void '+name(start)+'(void)','{','    REGS;'])
        for x in subset:
            pc=x['addr'];op=x['opcode'];mn=op.split(' ')[0];args=[s.strip()for s in op[len(mn):].strip().split(',')]if' 'in op else[]
            code=None
            if x['type']in ['call','jmp','cjmp']:
                target=x['jump'];symbol=name(target)if target in by else external[target]
                typ='R_RISCV_JAL'if x['type']in ['call','jmp']and x['size']==4 else'R_RISCV_BRANCH'if x['type']=='cjmp'and x['size']==4 else'R_RISCV_RVC_BRANCH'if x['type']=='cjmp'else'R_RISCV_RVC_JUMP'
                label='.Lrecord_control_edge_'+format(pc,'x')
                if x['type']=='call':ins=('jal ra,'if x['size']==4 else'c.jal ')+label
                elif x['type']=='jmp':ins=('jal zero,'if x['size']==4 else'c.j ')+label
                elif x['size']==2:ins='c.'+mn+' '+','.join(args[:-1])+','+label
                else:ins=mn+' '+','.join(args[:-1])+','+label
                body=label+':\n'+('.option push\n.option norvc\n'if x['size']==4 else'')+ins+'\n'+('.option pop\n'if x['size']==4 else'')+'.reloc .-'+str(x['size'])+','+typ+','+symbol+'\n'
                code='CALL_PORT('+quoted(body)+');'
                controls.append(dict(owner=name(start),offset=pc-start,PC=pc,size=x['size'],type={'R_RISCV_JAL':17,'R_RISCV_BRANCH':16,'R_RISCV_RVC_BRANCH':44,'R_RISCV_RVC_JUMP':45}[typ],target=symbol,target_PC=target))
            elif x['type']=='ucall':
                code='CALL_PORT('+quoted('c.jalr '+args[0])+');'
            elif mn=='li'and args[0]in A:code=args[0]+' = UINT32_C('+str(int(args[1],0))+'); LIVE;'
            elif mn=='lui'and args[0]in A:code=args[0]+' = UINT32_C('+hex((int(args[1],0)<<12)&0xffffffff)+'); LIVE;'
            elif mn in ['addi','andi','ori','xori','slli','srli']and args[0]in A and args[1]in A:
                a,b,imm=args;val=int(imm,0)
                token={'addi':'+','andi':'&','ori':'|','xori':'^','slli':'<<','srli':'>>'}[mn]
                v=hex(val&0xffffffff)+'u'if mn in ['addi','andi','ori','xori']else str(val)+'u'
                code=a+' = '+b+' '+token+' '+v+'; LIVE;'
            elif mn in ['add','and','mul','xor','or']and all(z in A for z in args):
                a,b,c=args;code=a+' = '+b+' '+{'add':'+','and':'&','mul':'*','xor':'^','or':'|'}[mn]+' '+c+'; LIVE;'
            elif mn in ['lbu','lhu','lw','sb','sh','sw']:
                reg=args[0];mem=re.fullmatch(r'(-?\d+)\((\w+)\)',args[1]);assert mem
                off=int(mem[1]);base=mem[2];bits={'lbu':8,'lhu':16,'lw':32,'sb':8,'sh':16,'sw':32}[mn]
                if base in A and(reg in A or reg=='zero'):
                    address=base+(' + '+str(off)+'u'if off>=0 else' - '+str(-off)+'u')
                    ptr='(volatile uint'+str(bits)+'_t *)(uintptr_t)('+address+')'
                    code=(reg+' = *'+ptr if mn.startswith('l')else'*'+ptr+' = '+('0'if reg=='zero'else'(uint'+str(bits)+'_t)'+reg))+'; LIVE;'
            if mn=='addi'and x['size']==4 and args[0]==args[1]and -32<=int(args[2],0)<=31:
                code=None  # Preserve original full-width ADDI rather than a compiler-selected C.ADDI.
            if code is None:
                body=('.option push\n.option norvc\n'+op+'\n.option pop\n')if x['size']==4 else op
                code='CALL_PORT('+quoted(body)+');'
            lines.append('    '+code)
        lines.extend(['    __builtin_unreachable();','}',''])
    print(json.dumps(dict(source='\n'.join(lines),regions=regions,controls=controls,frontier=FRONTIER.relative_to(ROOT).as_posix(),frontier_sha256=EXPECTED)))
if __name__=='__main__':main()
