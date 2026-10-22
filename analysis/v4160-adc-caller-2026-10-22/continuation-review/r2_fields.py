"""Retained standard operand text only; conditional QK fields use pinned TD."""
import re
NAMES=('zero','ra','sp','gp','tp','t0','t1','t2','s0','s1','a0','a1','a2','a3','a4','a5','a6','a7','s2','s3','s4','s5','s6','s7','s8','s9','s10','s11','t3','t4','t5','t6')
def reg(s):return NAMES.index(s)
def num(s):return int(s,0)
def memory(s):
    m=re.fullmatch(r'(-?(?:0x[0-9a-f]+|[0-9]+))\((\w+)\)',s)
    if not m:raise ValueError('Retained memory operand '+s)
    return num(m[1]),reg(m[2])
def parse(x):
    text=x['opcode'];op,*tail=text.split(' ',1);a=[] if not tail else [s.strip() for s in tail[0].split(',')]
    r=dict(PC=x['addr'],bytes=x['size'],raw_hex=x['bytes'],op=op,rd=None,rs1=None,rs2=None,immediate=None,target=None,memory_width=None)
    if op in ('lw','lbu','lhu','sw','sh','sb'):
        imm,base=memory(a[1]);r.update(rs1=base,immediate=imm,memory_width={'lw':32,'sw':32,'lhu':16,'sh':16,'lbu':8,'sb':8}[op]);r['rs2' if op in ('sw','sh','sb') else 'rd']=reg(a[0])
    elif op in ('lui','auipc'):r.update(rd=reg(a[0]),immediate=(num(a[1])<<12)&0xffffffff)
    elif op in ('addi','andi','slli','srli'):r.update(rd=reg(a[0]),rs1=reg(a[1]),immediate=num(a[2]))
    elif op in ('add','sub','or','mul'):r.update(rd=reg(a[0]),rs1=reg(a[1]),rs2=reg(a[2]))
    elif op=='li':r.update(op='addi',rd=reg(a[0]),rs1=0,immediate=num(a[1]))
    elif op=='mv':r.update(rd=reg(a[0]),rs1=reg(a[1]))
    elif op in ('beqz','bnez'):r.update(op='beq' if op=='beqz' else 'bne',rs1=reg(a[0]),rs2=0,target=num(a[1]))
    elif op=='bleu':r.update(op='bgeu',rs1=reg(a[1]),rs2=reg(a[0]),target=num(a[2]))
    elif op in ('beq','bne','bltu','bgeu','blt'):r.update(rs1=reg(a[0]),rs2=reg(a[1]),target=num(a[2]))
    elif op=='j':r.update(op='jal',rd=0,target=num(a[0]))
    elif op=='jal':r.update(rd=1 if len(a)==1 else reg(a[0]),target=num(a[-1]))
    elif op=='jalr':
        imm,base=memory(a[0]) if '(' in a[0] else (0,reg(a[0]));r.update(rd=1,rs1=base,immediate=imm)
    elif op=='ret':r.update(op='jalr',rd=0,rs1=1,immediate=0)
    elif op=='fence.i':pass
    else:raise ValueError('Unadmitted retained standard mnemonic '+text)
    return r
