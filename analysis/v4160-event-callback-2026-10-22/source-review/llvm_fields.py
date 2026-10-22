"""Independent LLVM operand-text normalization; no target execution."""
import re
REGS=['zero','ra','sp','gp','tp','t0','t1','t2','s0','s1','a0','a1','a2','a3','a4','a5','a6','a7','s2','s3','s4','s5','s6','s7','s8','s9','s10','s11','t3','t4','t5','t6']
def number(s):return int(s.strip().split()[0],0)
def reg(s):return REGS.index(s.strip())
def parse(text):
    rows=[]
    for line in text.splitlines():
        m=re.match(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*(\S+)\s*(.*)$',line)
        if not m:continue
        pc=int(m[1],16);raw=bytes.fromhex(m[2]);op=m[3];a=[s.strip() for s in m[4].split(',')] if m[4] else [];r=dict(PC=pc,bytes=len(raw),raw_hex=raw.hex(),op=op,rd=None,rs1=None,rs2=None,immediate=None,target=None,memory_width=None)
        if op in ('lui','auipc'):r.update(rd=reg(a[0]),immediate=(number(a[1])<<12)&0xffffffff)
        elif op=='li':r.update(op='addi',rd=reg(a[0]),rs1=0,immediate=number(a[1]))
        elif op in ('addi','andi','xori','slli','srli','srai'):r.update(rd=reg(a[0]),rs1=reg(a[1]),immediate=number(a[2]))
        elif op in ('add','sub','xor','mul'):r.update(rd=reg(a[0]),rs1=reg(a[1]),rs2=reg(a[2]))
        elif op=='mv':
            r.update(rd=reg(a[0]),rs1=reg(a[1]))
            if len(raw)==4:r.update(op='addi',immediate=0)
        elif op in ('lw','lbu','lhu','sw','sb','sh'):
            mem=re.fullmatch(r'([^()]+)\(([^()]+)\)',a[1]);r.update(rs1=reg(mem[2]),immediate=number(mem[1]),memory_width={'lw':32,'sw':32,'lbu':8,'sb':8,'lhu':16,'sh':16}[op]);r['rd' if op.startswith('l') else 'rs2']=reg(a[0])
        elif op in ('beq','bne','blt','bge','bltu','bgeu'):r.update(rs1=reg(a[0]),rs2=reg(a[1]),target=number(a[2]))
        elif op in ('beqz','bnez','bgez'):r.update(op={'beqz':'beq','bnez':'bne','bgez':'bge'}[op],rs1=reg(a[0]),rs2=0,target=number(a[1]))
        elif op=='blez':r.update(op='bge',rs1=0,rs2=reg(a[0]),target=number(a[1]))
        elif op=='j':r.update(op='jal',rd=0,target=number(a[0]))
        elif op=='jal':r.update(rd=1 if len(a)==1 else reg(a[0]),target=number(a[-1]))
        elif op=='ret':r.update(op='jalr',rd=0,rs1=1,immediate=0)
        elif op in ('jr','jalr'):r.update(op='jalr',rd=0 if op=='jr' else 1,rs1=reg(a[0]),immediate=0)
        else:raise ValueError('Unadmitted LLVM text form '+line)
        rows.append(r)
    if len(rows)!=217:raise ValueError('Exactly217 independent LLVM instructions')
    return rows
