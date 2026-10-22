"""Only additional fields used by this original handler; no CPU state."""
def decode(raw,pc,previous):
    try:return previous(raw,pc)
    except ValueError:pass
    h=int.from_bytes(raw[:2],'little');size=4 if h&3==3 else 2
    if len(raw)<size:raise ValueError('Whole instruction')
    w=int.from_bytes(raw[:size],'little')
    def row(op,rd,rs1,rs2=None,immediate=None):return dict(PC=pc,bytes=size,raw_hex=raw[:size].hex(),op=op,rd=rd,rs1=rs1,rs2=rs2,immediate=immediate,target=None,memory_width=None)
    if size==4 and w&127==0x33 and (w>>12)&7==6 and w>>25==0:return row('or',(w>>7)&31,(w>>15)&31,(w>>20)&31)
    if size==2:
        if h&3==1 and h>>13==4 and (h>>10)&3==3 and not h&0x1000 and (h>>5)&3==2:
            r=8+((h>>7)&7);return row('or',r,r,8+((h>>2)&7))
        if h&3==0 and h>>13==0:
            imm=(((h>>7)&15)<<6)|(((h>>11)&3)<<4)|(((h>>5)&1)<<3)|(((h>>6)&1)<<2)
            if imm:return row('addi',8+((h>>2)&7),2,immediate=imm)
    raise ValueError('Unadmitted handler instruction '+hex(pc))
