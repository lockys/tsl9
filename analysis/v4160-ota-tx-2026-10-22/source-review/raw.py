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

# Exact independent operand contract, reviewed against original bytes and static
# disassembly; not generated from this decoder or a CPU/ESIL state machine.
# PC,op,rd,rs1,rs2,immediate,target,memory-width.
EXPECTED=[
 (0x8a56,'addi',15,0,None,1039,None,None),(0x8a5a,'bltu',None,15,13,None,0x8b6c,None),
 (0x8a5e,'addi',2,2,None,-32,None,None),(0x8a60,'sw',None,2,8,24,None,32),
 (0x8a62,'sw',None,2,9,20,None,32),(0x8a64,'sw',None,2,18,16,None,32),
 (0x8a66,'sw',None,2,19,12,None,32),(0x8a68,'sw',None,2,1,28,None,32),
 (0x8a6a,'lhu',14,3,None,150,None,16),(0x8a6e,'mv',18,10,None,None,None,None),
 (0x8a70,'mv',8,13,None,None,None,None),(0x8a72,'mv',9,12,None,None,None,None),
 (0x8a74,'mv',19,11,None,None,None,None),(0x8a76,'bne',None,14,10,None,0x8a96,None),
 (0x8a7a,'lui',15,None,None,65536,None,None),(0x8a7c,'addi',15,15,None,-2,None,None),
 (0x8a7e,'beq',None,14,15,None,0x8a96,None),(0x8a82,'lui',15,None,None,0x40000,None,None),
 (0x8a86,'lw',15,15,None,316,None,32),(0x8a8a,'addi',11,3,None,128,None,None),
 (0x8a8e,'jalr',1,15,None,0,None,None),(0x8a90,'addi',15,0,None,1,None,None),
 (0x8a92,'beq',None,10,15,None,0x8acc,None),(0x8a96,'lhu',15,3,None,154,None,16),
 (0x8a9a,'bne',None,15,18,None,0x8abe,None),(0x8a9e,'lui',15,None,None,65536,None,None),
 (0x8aa0,'addi',15,15,None,-2,None,None),(0x8aa2,'beq',None,18,15,None,0x8abe,None),
 (0x8aa6,'lui',15,None,None,0x40000,None,None),(0x8aaa,'lw',15,15,None,316,None,32),
 (0x8aae,'addi',11,3,None,128,None,None),(0x8ab2,'mv',10,18,None,None,None,None),
 (0x8ab4,'jalr',1,15,None,0,None,None),(0x8ab6,'addi',15,0,None,1,None,None),
 (0x8ab8,'addi',12,0,None,1,None,None),(0x8aba,'beq',None,10,15,None,0x8ace,None),
 (0x8abe,'lw',1,2,None,28,None,32),(0x8ac0,'lw',8,2,None,24,None,32),
 (0x8ac2,'lw',9,2,None,20,None,32),(0x8ac4,'lw',18,2,None,16,None,32),
 (0x8ac6,'lw',19,2,None,12,None,32),(0x8ac8,'addi',2,2,None,32,None,None),
 (0x8aca,'jalr',0,1,None,0,None,None),(0x8acc,'addi',12,0,None,0,None,None),
 (0x8ace,'addi',15,0,None,1062,None,None),(0x8ad2,'mul',15,12,15,None,None,None),
 (0x8ad6,'auipc',13,None,None,0x20002000,None,None),(0x8ada,'addi',13,13,None,1718,None,None),
 (0x8ade,'lui',14,None,None,0xffff8000,None,None),(0x8ae0,'xori',14,14,None,-171,None,None),
 (0x8ae4,'andi',11,8,None,255,None,None),(0x8ae8,'addi',15,15,None,6,None,None),
 (0x8aea,'add',15,15,13,None,None,None),(0x8aec,'sh',None,15,14,0,None,16),
 (0x8af0,'sb',None,15,11,4,None,8),(0x8af4,'srli',14,8,None,8,None,None),
 (0x8af8,'add',11,11,19,None,None,None),(0x8afa,'sb',None,15,14,3,None,8),
 (0x8afe,'add',14,14,11,None,None,None),(0x8b00,'sb',None,15,19,2,None,8),
 (0x8b04,'andi',14,14,None,255,None,None),(0x8b08,'addi',11,0,None,0,None,None),
 (0x8b0a,'slli',10,11,None,16,None,None),(0x8b0e,'srli',10,10,None,16,None,None),
 (0x8b10,'bltu',None,10,8,None,0x8b52,None),(0x8b14,'add',15,15,8,None,None,None),
 (0x8b16,'sb',None,15,14,5,None,8),(0x8b1a,'addi',15,0,None,1062,None,None),
 (0x8b1e,'mul',15,12,15,None,None,None),(0x8b22,'addi',8,8,None,6,None,None),
 (0x8b24,'slli',12,12,None,2,None,None),(0x8b26,'lw',1,2,None,28,None,32),
 (0x8b28,'lw',9,2,None,20,None,32),(0x8b2a,'lw',18,2,None,16,None,32),
 (0x8b2c,'lw',19,2,None,12,None,32),(0x8b2e,'addi',11,0,None,1,None,None),
 (0x8b30,'add',15,15,13,None,None,None),(0x8b32,'sh',None,15,8,2,None,16),
 (0x8b36,'sh',None,15,0,4,None,16),(0x8b3a,'addi',15,3,None,148,None,None),
 (0x8b3e,'add',12,12,15,None,None,None),(0x8b40,'lw',8,2,None,24,None,32),
 (0x8b42,'lui',15,None,None,0x40000,None,None),(0x8b46,'lw',6,15,None,80,None,32),
 (0x8b4a,'lbu',10,12,None,0,None,8),(0x8b4e,'addi',2,2,None,32,None,None),
 (0x8b50,'jalr',0,6,None,0,None,None),(0x8b52,'add',10,9,11,None,None,None),
 (0x8b56,'lbu',10,10,None,0,None,8),(0x8b5a,'add',16,15,11,None,None,None),
 (0x8b5e,'addi',11,11,None,1,None,None),(0x8b60,'add',14,14,10,None,None,None),
 (0x8b62,'sb',None,16,10,5,None,8),(0x8b66,'andi',14,14,None,255,None,None),
 (0x8b6a,'jal',0,None,None,None,0x8b0a,None),(0x8b6c,'jalr',0,1,None,0,None,None)
]
def rows(body):
    need(len(body)==280,'Exact source280B');pc=ENTRY;result=[]
    while pc<END:
        row=decode(body[pc-ENTRY:],pc);result.append(row);pc+=row['bytes']
    need(pc==END and len(result)==96,'Exact source96-instruction geometry');return result
def validate(body):
    result=rows(body);keys=('PC','op','rd','rs1','rs2','immediate','target','memory_width');need([tuple(row[key] for key in keys) for row in result]==EXPECTED,'All96 independent operand/order contracts');return result
