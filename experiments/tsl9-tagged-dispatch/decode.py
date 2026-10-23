"""Independent static instruction-field decoder adapted from frozen queue-consumer v1.
No instruction execution or device access. Only this candidate instruction vocabulary.
"""
BASE=0x16b7c

def need(ok,message):
    if not ok:raise ValueError(message)

def sx(n,b):return n-(1<<b) if n&(1<<(b-1)) else n

def decode(code):
    """Static RV32IMAC/Zicsr bit decoding, not instruction execution."""
    rows=[];at=0
    while at<len(code):
        need(at+2<=len(code),'instruction extent');w=int.from_bytes(code[at:at+2],'little');size=4 if w&3==3 else 2
        need(at+size<=len(code),'wide instruction extent')
        if size==4:
            w=int.from_bytes(code[at:at+4],'little');op=w&127;rd=(w>>7)&31;rs=(w>>15)&31;rs2=(w>>20)&31;f3=(w>>12)&7
            if op in (0x37,0x17):ins=['LUI' if op==0x37 else 'AUIPC',rd,w&0xfffff000]
            elif op==0x13 and f3==0:ins=['ADDI',rd,rs,sx(w>>20,12)]
            elif op==0x13 and f3==7:ins=['ANDI',rd,rs,sx(w>>20,12)]
            elif op==0x13 and f3==5 and w>>25==0:ins=['SRLI',rd,rs,rs2]
            elif op==0x33 and f3==3 and w>>25==0:ins=['SLTU',rd,rs,rs2]
            elif op==3 and f3 in (2,4,5):ins=[{2:'LW32',4:'LBU8',5:'LHU16'}[f3],rd,rs,sx(w>>20,12)]
            elif op==0x23 and f3 in (0,1,2):
                offset=((w>>25)<<5)|((w>>7)&31);ins=[{0:'SB8',1:'SH16',2:'SW32'}[f3],rs2,rs,sx(offset,12)]
            elif op==0x33 and f3==0 and w>>25==1:ins=['MUL',rd,rs,rs2]
            elif op==0x73 and f3 in (2,3):ins=['CSRRS' if f3==2 else 'CSRRC',rd,w>>20,rs]
            elif op==0x63 and f3 in (0,1,6):
                imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
                ins=[{0:'BEQ',1:'BNE',6:'BLTU'}[f3],rs,rs2,BASE+at+sx(imm,13)]
            elif op==0x6f:
                imm=((w>>31)<<20)|(((w>>21)&1023)<<1)|(((w>>20)&1)<<11)|(((w>>12)&255)<<12)
                ins=['JAL',rd,BASE+at+sx(imm,21)]
            else:raise ValueError('wide opcode/width outside exact bounded queue instruction families')
        else:
            q=w&3;f3=w>>13;rd=(w>>7)&31;rs2=(w>>2)&31;imm=sx((((w>>12)&1)<<5)|((w>>2)&31),6)
            if q==0 and f3==0:
                n=(((w>>11)&3)<<4)|(((w>>7)&15)<<6)|(((w>>6)&1)<<2)|(((w>>5)&1)<<3)
                need(n!=0,'valid ADDI4SPN');ins=['ADDI',8+((w>>2)&7),2,n]
            elif q==0 and f3==2:
                n=(((w>>10)&7)<<3)|(((w>>6)&1)<<2)|(((w>>5)&1)<<6)
                ins=['LW32',8+((w>>2)&7),8+((w>>7)&7),n]
            elif q==2 and f3==6:
                n=(((w>>9)&15)<<2)|(((w>>7)&3)<<6);ins=['SW32',rs2,2,n]
            elif q==2 and f3==2:
                n=(((w>>12)&1)<<5)|(((w>>4)&7)<<2)|(((w>>2)&3)<<6)
                need(rd!=0,'valid LWSP');ins=['LW32',rd,2,n]
            elif q==1 and f3 in (0,2):ins=['ADDI',rd,rd if f3==0 else 0,imm]
            elif q==1 and f3==3 and rd==2:
                n=(((w>>12)&1)<<9)|(((w>>6)&1)<<4)|(((w>>5)&1)<<6)|(((w>>3)&3)<<7)|(((w>>2)&1)<<5)
                ins=['ADDI',2,2,sx(n,10)]
            elif q==1 and f3==3 and rd not in (0,2):ins=['LUI',rd,(imm<<12)&0xffffffff]
            elif q==2 and f3==0:
                need(not (w>>12)&1,'RV32 SLLI range');ins=['SLLI',rd,rd,(w>>2)&31]
            elif q==1 and f3==4 and ((w>>10)&3) in (0,2):
                rs=8+((w>>7)&7)
                if ((w>>10)&3)==0:need(not (w>>12)&1,'RV32 SRLI range');ins=['SRLI',rs,rs,(w>>2)&31]
                else:ins=['ANDI',rs,rs,imm]
            elif w==0x8082:ins=['RET',1]
            elif q==2 and f3==4 and (w>>12)&1 and rd and not rs2:ins=['JALR',1,rd,0]
            elif q==2 and f3==4 and not (w>>12)&1 and rd and rs2:ins=['MV',rd,rs2]
            elif q==2 and f3==4 and (w>>12)&1 and rd and rs2:ins=['ADD',rd,rd,rs2]
            elif q==1 and f3 in (6,7):
                n=(((w>>12)&1)<<8)|(((w>>10)&3)<<3)|(((w>>5)&3)<<6)|(((w>>3)&3)<<1)|(((w>>2)&1)<<5)
                ins=['BEQZ' if f3==6 else 'BNEZ',8+((w>>7)&7),BASE+at+sx(n,9)]
            elif q==1 and f3==5:
                n=(((w>>12)&1)<<11)|(((w>>11)&1)<<4)|(((w>>9)&3)<<8)|(((w>>8)&1)<<10)|(((w>>7)&1)<<6)|(((w>>6)&1)<<7)|(((w>>3)&7)<<1)|(((w>>2)&1)<<5)
                ins=['J',BASE+at+sx(n,12)]
            else:raise ValueError('compressed opcode/width outside exact bounded queue families')
        rows.append([at,size]+ins);at+=size
    return rows
