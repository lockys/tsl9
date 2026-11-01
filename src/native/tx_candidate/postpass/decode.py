"""Bounded RV32 instruction-field decoding as data; no CPU state or execution."""
import sys
sys.dont_write_bytecode=True
ENTRY=0x8a56
END=0x8b6e
def need(value,message):
    if not value:raise ValueError(message)
def sx(value,bits):return value-(1<<bits) if value&(1<<(bits-1)) else value
def decode(raw,pc):
    need(len(raw)>=2,'Whole instruction halfword');h=int.from_bytes(raw[:2],'little');size=4 if h&3==3 else 2;need(len(raw)>=size,'Whole instruction word');w=int.from_bytes(raw[:size],'little')
    row={'PC':pc,'bytes':size,'raw_hex':raw[:size].hex()}
    def done(op,rd=None,rs1=None,rs2=None,immediate=None,target=None,width=None):
        row.update(op=op,rd=rd,rs1=rs1,rs2=rs2,immediate=immediate,target=target,memory_width=width);return row
    if size==4:
        opcode=w&127;rd=(w>>7)&31;rs1=(w>>15)&31;rs2=(w>>20)&31;f=(w>>12)&7;top=w>>25
        if opcode in (0x37,0x17):return done('lui' if opcode==0x37 else 'auipc',rd,immediate=w&0xfffff000)
        if opcode==0x13:
            if f in (0,4,7):return done({0:'addi',4:'xori',7:'andi'}[f],rd,rs1,immediate=sx(w>>20,12))
            if f in (1,5) and top==0:return done('slli' if f==1 else 'srli',rd,rs1,immediate=rs2)
        if opcode==0x33 and f==0 and top in (0,1):return done('add' if top==0 else 'mul',rd,rs1,rs2)
        if opcode==3 and f in (2,4,5):return done({2:'lw',4:'lbu',5:'lhu'}[f],rd,rs1,immediate=sx(w>>20,12),width={2:32,4:8,5:16}[f])
        if opcode==0x23 and f in (0,1,2):return done({0:'sb',1:'sh',2:'sw'}[f],rs1=rs1,rs2=rs2,immediate=sx((top<<5)|((w>>7)&31),12),width={0:8,1:16,2:32}[f])
        if opcode==0x63 and f in (0,1,6):
            imm=(((w>>31)&1)<<12)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)|(((w>>7)&1)<<11);return done({0:'beq',1:'bne',6:'bltu'}[f],rs1=rs1,rs2=rs2,target=pc+sx(imm,13))
        if opcode==0x6f:
            imm=(((w>>31)&1)<<20)|(((w>>12)&255)<<12)|(((w>>20)&1)<<11)|(((w>>21)&1023)<<1);return done('jal',rd,target=pc+sx(imm,21))
    else:
        q=h&3;f=h>>13;rd=(h>>7)&31;rs2=(h>>2)&31;ci=sx((((h>>12)&1)<<5)|rs2,6)
        if q==1 and f==0:return done('addi',rd,rd,immediate=ci)
        if q==1 and f==2:return done('addi',rd,0,immediate=ci)
        if q==1 and f==3:
            if rd==2:
                imm=(((h>>12)&1)<<9)|(((h>>6)&1)<<4)|(((h>>5)&1)<<6)|(((h>>3)&3)<<7)|(((h>>2)&1)<<5);return done('addi',2,2,immediate=sx(imm,10))
            need(rd not in (0,2) and ci!=0,'Admitted C.LUI');return done('lui',rd,immediate=(ci<<12)&0xffffffff)
        if q==1 and f==4 and ((h>>10)&3)==0 and not h&0x1000:return done('srli',8+((h>>7)&7),8+((h>>7)&7),immediate=rs2)
        if q==1 and f in (1,5):
            imm=(((h>>12)&1)<<11)|(((h>>11)&1)<<4)|(((h>>9)&3)<<8)|(((h>>8)&1)<<10)|(((h>>7)&1)<<6)|(((h>>6)&1)<<7)|(((h>>3)&7)<<1)|(((h>>2)&1)<<5);return done('jal',1 if f==1 else 0,target=pc+sx(imm,12))
        if q==2 and f==0 and not h&0x1000:return done('slli',rd,rd,immediate=rs2)
        if q==2 and f==2:
            imm=(((h>>12)&1)<<5)|(((h>>4)&7)<<2)|(((h>>2)&3)<<6);return done('lw',rd,2,immediate=imm,width=32)
        if q==2 and f==6:
            imm=(((h>>9)&15)<<2)|(((h>>7)&3)<<6);return done('sw',rs1=2,rs2=rs2,immediate=imm,width=32)
        if q==2 and f==4:
            high=(h>>12)&1
            if rs2:return done('add',rd,rd,rs2) if high else done('mv',rd,rs2)
            need(rd!=0,'Nonzero C.JR/C.JALR source');return done('jalr',1 if high else 0,rd,immediate=0)
    raise ValueError('Unadmitted instruction form at '+hex(pc))
