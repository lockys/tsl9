"""Parse retained bounded disassembly operands, never execute instructions."""
import re
NAMES = ('zero','ra','sp','gp','tp','t0','t1','t2','s0','s1','a0','a1','a2','a3','a4','a5','a6','a7','s2','s3','s4','s5','s6','s7','s8','s9','s10','s11','t3','t4','t5','t6')
def reg(s): return NAMES.index(s)
def number(s): return int(s, 0)
def parse(x):
    text=x['opcode']; op,*tail=text.split(' ',1); a=[] if not tail else [s.strip() for s in tail[0].split(',')]
    r=dict(PC=x['addr'],bytes=x['size'],raw_hex=x['bytes'],op=op,rd=None,rs1=None,rs2=None,immediate=None,target=None,memory_width=None)
    if op in ('lw','lbu','sw'):
        match=re.fullmatch(r'(-?(?:0x[0-9a-f]+|[0-9]+))\((\w+)\)',a[1])
        if not match: raise ValueError('Bounded memory operand')
        r.update(rs1=reg(match[2]),immediate=number(match[1]),memory_width=8 if op=='lbu' else 32)
        r['rs2' if op=='sw' else 'rd']=reg(a[0])
    elif op=='lui': r.update(rd=reg(a[0]),immediate=(number(a[1])<<12)&0xffffffff)
    elif op in ('addi','ori','andi','xori','slli','srli'): r.update(rd=reg(a[0]),rs1=reg(a[1]),immediate=number(a[2]))
    elif op in ('and','or','sll','mul','sltu'): r.update(rd=reg(a[0]),rs1=reg(a[1]),rs2=reg(a[2]))
    elif op=='li': r.update(op='addi',rd=reg(a[0]),rs1=0,immediate=number(a[1]))
    elif op=='not': r.update(op='xori',rd=reg(a[0]),rs1=reg(a[1]),immediate=-1)
    elif op=='snez': r.update(op='sltu',rd=reg(a[0]),rs1=0,rs2=reg(a[1]))
    elif op in ('beqz','bnez'): r.update(op='beq' if op=='beqz' else 'bne',rs1=reg(a[0]),rs2=0,target=number(a[1]))
    elif op=='bleu': r.update(op='bgeu',rs1=reg(a[1]),rs2=reg(a[0]),target=number(a[2]))
    elif op in ('bltu','bgeu'): r.update(rs1=reg(a[0]),rs2=reg(a[1]),target=number(a[2]))
    elif op=='j': r.update(op='jal',rd=0,target=number(a[0]))
    elif op=='ret': r.update(op='jalr',rd=0,rs1=1,immediate=0)
    else: raise ValueError('Unadmitted retained mnemonic '+text)
    return r
