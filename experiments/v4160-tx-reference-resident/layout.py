"""Static original-APP operands and reset stores; no provider/CSR execution."""
import hashlib
from oracle import need,sx
def derive(image):
    need(len(image)==76800 and hashlib.sha256(image).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','layout APP identity')
    def raw(pc,n):return image[pc-0x8000:pc-0x8000+n]
    def pair(pc,rd):
        u,a=int.from_bytes(raw(pc,4),'little'),int.from_bytes(raw(pc+4,4),'little')
        need(u&127==0x17 and u>>7&31==rd and a&127==0x13 and a>>7&31==rd and a>>15&31==rd and a>>12&7==0,'AUIPC/ADDI pair')
        return (pc+(u&0xfffff000)+sx(a>>20,12))&0xffffffff
    gp=pair(0x186aa,3);end=pair(0x186e2,11)
    need(raw(0x186de,4)==bytes.fromhex('13850108'),'reset zero start operand')
    need(raw(0x186ea,14)==bytes.fromhex('6377b500232005001105e36db5fe'),'reset zero guard/store/stride/backedge')
    start=gp+128
    need(start<end and start%4==end%4==0,'reset interval')
    h=int.from_bytes(raw(0x8e92,2),'little')
    need(h&3==1 and h>>13==3 and h>>7&31==12,'setup C.LUI a2')
    amount=(sx((h>>2&31)|(h>>7&32),6)<<12)&0xffffffff
    w=int.from_bytes(raw(0x8e96,4),'little')
    need(w&0xfffff==0x60613,'setup ADDI a2,a2')
    amount=(amount+sx(w>>20,12))&0xffffffff
    destination=pair(0x8e9c,10)
    need(raw(0x8e8c,6)==bytes.fromhex('370404003c44') and raw(0x8e9a,2)==bytes.fromhex('8145') and raw(0x8ea6,2)==bytes.fromhex('8297'),'setup fill-slot/value/call operands')
    need((gp,start,end,destination,amount)==(0x20004000,0x20004080,0x2000c958,0x2000b18c,2124),'nominal bounds')
    zero_words=range(start,end,4)
    tx_end=destination+amount
    need(all(a//4*4 in zero_words for a in range(destination,tx_end)),'every TX byte covered by original reset word stores')
    return dict(reset_zero_start=hex(start),reset_zero_end_exclusive=hex(end),reset_zero_word_stores=len(zero_words),
        nominal_TX_start=hex(destination),nominal_TX_end_exclusive=hex(tx_end),nominal_TX_bytes=amount,
        reset_covers_every_TX_byte=True,later_zero_fill_request=dict(call_PC='0x8ea6',slot='0x40048',A0=hex(destination),A1=0,A2=amount),
        installed_fill_side_effects_proved=False,exclusive_RAM_ownership_proved=False)
