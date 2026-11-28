"""Static original-APP operands and reset stores; no provider/CSR execution."""
import hashlib
from oracle import need,sx
def nominal(image):
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

def derive(image):
    facts=nominal(image)
    def word(pc):return int.from_bytes(image[pc-0x8000:pc-0x8000+4],'little')
    load,constant,branch=word(0x89fa),word(0x89fe),word(0x8a02)
    need(load&127==3 and load>>12&7==5 and load>>7&31==12 and load>>15&31==3 and sx(load>>20,12)==138,'counter zero-extended halfword load')
    need(constant&0xfffff==0x00713,'counter guard constant register')
    maximum=sx(constant>>20,12)
    need(branch&127==0x63 and branch>>12&7==6 and branch>>15&31==14 and branch>>20&31==12,'unsigned upper guard operands')
    off=(branch>>31)<<12|(branch>>7&1)<<11|(branch>>25&63)<<5|(branch>>8&15)<<1
    need(0x8a02+sx(off,13)==0x8a4c,'over-limit branch clears state')
    u,a=word(0x8a12),word(0x8a16)
    need(u&0xfff==0x697 and a&0xfffff==0x68693,'RX AUIPC/ADDI base')
    base=(0x8a12+(u&0xfffff000)+sx(a>>20,12))&0xffffffff
    need(image[0x8a1a-0x8000:0x8a20-0x8000]==bytes.fromhex('b2962380f600'),'old-count addition and byte store')
    accepted=[(counter,base+counter) for counter in range(65536) if not maximum<counter]
    need(maximum==1039 and len(accepted)==1040,'exhaustive accepted count domain')
    addresses=[a for _,a in accepted]
    need(addresses==list(range(base,base+1040)),'exact destination image')
    need(base==int(facts['nominal_TX_end_exclusive'],16) and base+1040<=int(facts['reset_zero_end_exclusive'],16),'adjacency and reset coverage')
    gp=0x20004000;stores=[]
    for pc,f,source,offset,width in ((0x8a0e,1,14,138,2),(0x89ea,0,14,156,1),(0x8a4c,0,0,156,1),(0x89ae,0,15,165,1)):
        w=word(pc);imm=sx((w>>25<<5)|(w>>7&31),12)
        need(w&127==0x23 and w>>12&7==f and w>>15&31==3 and w>>20&31==source and imm==offset,'selected GP store encoding')
        stores.append((gp+offset,gp+offset+width))
    tx_start=int(facts['nominal_TX_start'],16);tx_end=int(facts['nominal_TX_end_exclusive'],16)
    need(all(end<=tx_start or tx_end<=start for start,end in stores+[(base,base+1040)]),'normal GP slice stores do not overlap TX')
    facts.update(counter_values_checked=65536,payload_write_counter_values=1040,over_limit_counter_values=65536-1040,
        nominal_RX_start=hex(base),nominal_RX_end_exclusive=hex(base+1040),TX_end_equals_RX_start=True,
        payload_store_PC='0x8a1c',payload_store_uses_old_counter=True,normal_GP_slice_writes_disjoint_from_TX=True,
        normal_GP_store_intervals=[[hex(a),hex(b)] for a,b in stores],all_RAM_accesses_isolated=False,
        whole_RX_or_runtime_reachability_proved=False)
    return facts
