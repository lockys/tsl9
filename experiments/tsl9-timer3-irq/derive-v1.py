"""Derive fixed timer basic-block C regions from retained, pinned disassembly."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[2]
FRONTIER=ROOT/'analysis/rtc-alarm-irq-2026-10-24/next-timer-frontier.json'
EXPECTED='f4a5edd30dcfebfd197b36c6db4319e82b601b13838a28b83db6f37c6de27007'
def main():
    assert hashlib.sha256(FRONTIER.read_bytes()).hexdigest()==EXPECTED
    d=json.loads(FRONTIER.read_bytes());ops=[x for x in d['operations']if x['addr']<0x9958]
    assert len(ops)==138 and sum(x['size']for x in ops)==442
    leaders={0x979e};by={x['addr']:x for x in ops}
    for x in ops:
        if x.get('jump')in by:leaders.add(x['jump'])
        if x['type']in ['call','ucall','cjmp','jmp']or x['opcode']=='mret':
            if x['addr']+x['size']in by:leaders.add(x['addr']+x['size'])
    starts=sorted(leaders);name=lambda pc:'tsl9_timer3_'+('entry_'if pc==0x979e else'block_')+format(pc,'x')
    external={0x81b0:'tsl9_channel_external_81b0',0x93ee:'tsl9_program_disarm_93ee'}
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
        '/* Original979E..9958 only. Architectural basic blocks have deliberate',
        ' * fallthrough adjacency. They are not ordinary independently callable C.',
        ' * C unsigned arithmetic/volatile memory use fixed A-register ports.',
        ' * SP/S registers, AUIPC, signed DIV, calls and MRET stay explicit.',
        ' * No target execution, standard IRQ ABI or original-PC placement claim. */',
        '']
    A={'a'+str(i)for i in range(6)}
    def quoted(s):return json.dumps(s)
    for i,start in enumerate(starts):
        end=starts[i+1]if i+1<len(starts)else 0x9958
        subset=[x for x in ops if start<=x['addr']<end]
        original=bytes.fromhex(''.join(x['bytes']for x in subset))
        regions.append(dict(name=name(start),start=start,end=end,bytes=end-start,original_sha256=hashlib.sha256(original).hexdigest()))
        lines.extend(['/* Original '+format(start,'X')+'..'+format(end,'X')+' */','REGION void '+name(start)+'(void)','{','    REGS;'])
        for x in subset:
            pc=x['addr'];op=x['opcode'];mn=op.split(' ')[0];args=[s.strip()for s in op[len(mn):].strip().split(',')]if' 'in op else[]
            code=None
            if x['type']in ['call','jmp','cjmp']:
                target=x['jump'];symbol=name(target)if target in by else external[target]
                typ='R_RISCV_JAL'if x['type']=='call'and x['size']==4 else'R_RISCV_BRANCH'if x['type']=='cjmp'and x['size']==4 else'R_RISCV_RVC_BRANCH'if x['type']=='cjmp'else'R_RISCV_RVC_JUMP'
                label='.Ltimer_edge_'+format(pc,'x')
                if x['type']=='call':ins=('jal ra,'if x['size']==4 else'c.jal ')+label
                elif x['type']=='jmp':ins='c.j '+label
                elif x['size']==2:ins='c.'+mn+' '+','.join(args[:-1])+','+label
                else:ins=mn+' '+','.join(args[:-1])+','+label
                body=label+':\n'+('.option push\n.option norvc\n'if x['size']==4 else'')+ins+'\n'+('.option pop\n'if x['size']==4 else'')+'.reloc .-'+str(x['size'])+','+typ+','+symbol+'\n'
                code='CALL_PORT('+quoted(body)+');'
                controls.append(dict(owner=name(start),offset=pc-start,PC=pc,size=x['size'],type={'R_RISCV_JAL':17,'R_RISCV_BRANCH':16,'R_RISCV_RVC_BRANCH':44,'R_RISCV_RVC_JUMP':45}[typ],target=symbol,target_PC=target))
            elif x['type']=='ucall':
                code='CALL_PORT("c.jalr a5");'
            elif mn=='li'and args[0]in A:code=args[0]+' = UINT32_C('+str(int(args[1],0))+'); LIVE;'
            elif mn=='lui'and args[0]in A:code=args[0]+' = UINT32_C('+hex((int(args[1],0)<<12)&0xffffffff)+'); LIVE;'
            elif mn in ['addi','andi','slli','srli']and args[0]in A and args[1]in A:
                a,b,imm=args;val=int(imm,0)
                token={'addi':'+','andi':'&','slli':'<<','srli':'>>'}[mn]
                v=hex(val&0xffffffff)+'u'if mn in ['addi','andi']else str(val)+'u'
                code=a+' = '+b+' '+token+' '+v+'; LIVE;'
            elif mn in ['add','and','mul']and all(z in A for z in args):
                a,b,c=args;code=a+' = '+b+' '+{'add':'+','and':'&','mul':'*'}[mn]+' '+c+'; LIVE;'
            elif mn in ['lbu','lhu','lw','sb','sh','sw']:
                reg=args[0];mem=re.fullmatch(r'(-?\d+)\((\w+)\)',args[1]);assert mem
                off=int(mem[1]);base=mem[2];bits={'lbu':8,'lhu':16,'lw':32,'sb':8,'sh':16,'sw':32}[mn]
                if base in A and(reg in A or reg=='zero'):
                    address=base+(' + '+str(off)+'u'if off>=0 else' - '+str(-off)+'u')
                    ptr='(volatile uint'+str(bits)+'_t *)(uintptr_t)('+address+')'
                    code=(reg+' = *'+ptr if mn.startswith('l')else'*'+ptr+' = '+('0'if reg=='zero'else'(uint'+str(bits)+'_t)'+reg))+'; LIVE;'
            if code is None:
                outputs=[]
                if args and args[0]in A and mn not in ['sw','sh','sb']:outputs=[args[0]]
                if mn=='div':
                    code='__asm__ volatile('+quoted(op)+':"+r"('+args[0]+'):"r"('+args[2]+'):"memory"); LIVE;'
                elif outputs:
                    code='__asm__ volatile('+quoted(op)+':"=r"('+outputs[0]+')::"memory"); LIVE;'
                else:
                    inputs=[a for a in args[:1]if a in A]
                    code='__asm__ volatile('+quoted(op)+'::'+','.join('"r"('+a+')'for a in inputs)+':"memory"); LIVE;'
            lines.append('    '+code)
        lines.extend(['    __builtin_unreachable();','}',''])
    print(json.dumps(dict(source='\n'.join(lines),regions=regions,controls=controls,frontier=FRONTIER.relative_to(ROOT).as_posix(),frontier_sha256=EXPECTED)))
if __name__=='__main__':main()
