"""Independent emitted-operand text normalization, with no expected-count shortcut."""
import re

REGS=['zero','ra','sp','gp','tp','t0','t1','t2','s0','s1','a0','a1','a2','a3','a4','a5',
      'a6','a7','s2','s3','s4','s5','s6','s7','s8','s9','s10','s11','t3','t4','t5','t6']


def number(s):return int(s.strip().split()[0],0)
def reg(s):return REGS.index(s.strip())


def parse(text):
    result=[]
    for line in text.splitlines():
        m=re.match(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*(\S+)\s*(.*)$',line)
        if not m:continue
        pc=int(m[1],16);raw=bytes.fromhex(m[2]);op=m[3]
        args=[s.strip() for s in m[4].split(',')] if m[4] else []
        row=dict(PC=pc,bytes=len(raw),raw_hex=raw.hex(),op=op,rd=None,rs1=None,rs2=None,
                 immediate=None,target=None,memory_width=None)
        if op in ('lui','auipc'):
            value=(number(args[1])<<12)&0xffffffff
            row.update(rd=reg(args[0]),immediate=value)
        elif op=='li':row.update(op='addi',rd=reg(args[0]),rs1=0,immediate=number(args[1]))
        elif op in ('addi','andi','xori','slli','srli','srai'):
            row.update(rd=reg(args[0]),rs1=reg(args[1]),immediate=number(args[2]))
        elif op in ('add','sub','xor','mul','and','or'):
            row.update(rd=reg(args[0]),rs1=reg(args[1]),rs2=reg(args[2]))
        elif op=='mv':
            row.update(rd=reg(args[0]),rs1=reg(args[1]))
            if len(raw)==4:row.update(op='addi',immediate=0)
        elif op in ('lw','lbu','lhu','lh','sw','sb','sh'):
            match=re.fullmatch(r'([^()]+)\(([^()]+)\)',args[1])
            row.update(rs1=reg(match[2]),immediate=number(match[1]),
                       memory_width={'lw':32,'sw':32,'lbu':8,'sb':8,'lhu':16,'lh':16,'sh':16}[op])
            row['rd' if op.startswith('l') else 'rs2']=reg(args[0])
        elif op in ('beq','bne','blt','bge','bltu','bgeu'):
            row.update(rs1=reg(args[0]),rs2=reg(args[1]),target=number(args[2]))
        elif op in ('beqz','bnez','bgez','bltz'):
            row.update(op={'beqz':'beq','bnez':'bne','bgez':'bge','bltz':'blt'}[op],
                       rs1=reg(args[0]),rs2=0,target=number(args[1]))
        elif op=='blez':row.update(op='bge',rs1=0,rs2=reg(args[0]),target=number(args[1]))
        elif op=='j':row.update(op='jal',rd=0,target=number(args[0]))
        elif op=='jal':row.update(rd=1 if len(args)==1 else reg(args[0]),target=number(args[-1]))
        elif op=='ret':row.update(op='jalr',rd=0,rs1=1,immediate=0)
        elif op in ('jr','jalr'):row.update(op='jalr',rd=0 if op=='jr' else 1,rs1=reg(args[0]),immediate=0)
        else:raise ValueError('Unadmitted actual LLVM form '+line)
        result.append(row)
    return result
