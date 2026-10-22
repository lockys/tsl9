"""Single-instruction fields only; no CPU state, execution or ISA interpreter."""
def need(v,m):
    if not v:raise ValueError(m)
def sx(v,n):return v-(1<<n) if v&(1<<(n-1)) else v
def decode(raw,pc,base):
    try:return base(raw,pc)
    except ValueError:pass
    need(len(raw)>=2,'Whole halfword');h=int.from_bytes(raw[:2],'little');size=4 if h&3==3 else 2;need(len(raw)>=size,'Whole instruction');w=int.from_bytes(raw[:size],'little')
    def row(op,rd=None,rs1=None,rs2=None,immediate=None,target=None,width=None):return dict(PC=pc,bytes=size,raw_hex=raw[:size].hex(),op=op,rd=rd,rs1=rs1,rs2=rs2,immediate=immediate,target=target,memory_width=width)
    if size==4:
        opcode=w&127;rd=(w>>7)&31;rs1=(w>>15)&31;rs2=(w>>20)&31;f=(w>>12)&7;top=w>>25
        if opcode==0x13 and f==5 and top==32:return row('srai',rd,rs1,immediate=rs2)
        if opcode==0x33 and f==0 and top==32:return row('sub',rd,rs1,rs2)
        if opcode==0x33 and f==4 and top==0:return row('xor',rd,rs1,rs2)
        if opcode==0x63 and f in (4,5,7):
            imm=(((w>>31)&1)<<12)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)|(((w>>7)&1)<<11);return row({4:'blt',5:'bge',7:'bgeu'}[f],rs1=rs1,rs2=rs2,target=pc+sx(imm,13))
    else:
        q=h&3;f=h>>13;rs1=8+((h>>7)&7);rs2=8+((h>>2)&7)
        if q==0 and f in (2,6):
            imm=(((h>>5)&1)<<6)|(((h>>10)&7)<<3)|(((h>>6)&1)<<2)
            return row('lw',rs2,rs1,immediate=imm,width=32) if f==2 else row('sw',rs1=rs1,rs2=rs2,immediate=imm,width=32)
        if q==1 and f==4 and ((h>>10)&3)==1 and not h&0x1000:return row('srai',rs1,rs1,immediate=(h>>2)&31)
        if q==1 and f==4 and ((h>>10)&3)==2:
            imm=(((h>>12)&1)<<5)|((h>>2)&31);return row('andi',rs1,rs1,immediate=sx(imm,6))
        if q==1 and f==4 and ((h>>10)&3)==3 and not h&0x1000:
            sub=(h>>5)&3
            if sub in (0,1):return row('sub' if sub==0 else 'xor',rs1,rs1,rs2)
        if q==1 and f in (6,7):
            imm=(((h>>12)&1)<<8)|(((h>>10)&3)<<3)|(((h>>5)&3)<<6)|(((h>>3)&3)<<1)|(((h>>2)&1)<<5);return row('beq' if f==6 else 'bne',rs1=rs1,rs2=0,target=pc+sx(imm,9))
    raise ValueError('Unadmitted raw instruction '+hex(pc)+' '+raw[:size].hex())
