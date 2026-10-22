"""Retained bounded raw-field kernel; excludes old HOST/build/report code."""
import hashlib
import struct

digest = lambda data: hashlib.sha256(data).hexdigest()
sx = lambda value, bits: value - (1 << bits) if value & (1 << (bits - 1)) else value

def raw_contract(image,snapshot):
    assert digest(image)=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
    rows=snapshot['instructions'];assert len(rows)==93 and snapshot['sha256']=='e0debe8b77025cfb56144045a0aa7524b7a2cd2ad0bd3daa2d880408ad9758f5'
    assert digest(image[0x1874a-0x8000:0x18834-0x8000])==snapshot['sha256']
    pc=0x1874a;by={}
    for x in rows:
        n=4 if int.from_bytes(image[pc-0x8000:pc-0x8000+2],'little')&3==3 else 2
        assert x['addr']==pc and x['size']==n and x['bytes']==image[pc-0x8000:pc-0x8000+n].hex();by[pc]=x;pc+=n
    assert pc==0x18834
    word=lambda p:struct.unpack_from('<I',image,p-0x8000)[0]
    half=lambda p:struct.unpack_from('<H',image,p-0x8000)[0]
    def clui(p,rd):
        h=half(p);assert(h&3,h>>13,h>>7&31)==(1,3,rd);return(sx(((h>>12&1)<<5)|(h>>2&31),6)<<12)&0xffffffff
    def ci(p,rd,funct,imm):
        h=half(p);assert(h&3,h>>13,h>>7&31,sx(((h>>12&1)<<5)|(h>>2&31),6))==(1,funct,rd,imm)
    def branch(p,funct,rs1,rs2,target):
        v=word(p);d=sx(((v>>31&1)<<12)|((v>>25&63)<<5)|((v>>8&15)<<1)|((v>>7&1)<<11),13)
        assert(v&127,v>>12&7,v>>15&31,v>>20&31,p+d)==(0x63,funct,rs1,rs2,target)
    def lui(p,rd):
        v=word(p);assert(v&127,v>>7&31)==(0x37,rd);return v&0xfffff000
    reg=lui(0x1874a,15);assert reg==0x40021000
    for p,rd in[(0x1879c,13),(0x187b8,15),(0x187d2,15),(0x18812,13)]:assert lui(p,rd)==reg
    masks={0x18750:lui(0x18750,13)}
    for p in(0x18768,0x18774,0x18780,0x187d8):ci(p+4,13,0,-1);masks[p]=(lui(p,13)-1)&0xffffffff
    assert list(masks.values())==[0xf8ff0000,0xfef6ffff,0xfffbffff,0xff80ffff,0xffc0ffff]
    assert lui(0x1878a,14)==0x009f0000 and clui(0x18796,13)==0x10000 and clui(0x187a0,14)==0x1000 and lui(0x1875e,12)==0x20000
    assert lui(0x187f4,13)==0x00290000 and lui(0x187fe,13)==0x01000000
    ci(0x18754,2,0,-16);ci(0x187aa,15,0,1);ci(0x1882c,2,0,16);ci(0x187c6,15,2,1);ci(0x187cc,15,2,1);ci(0x18822,14,2,8)
    for p,rd,rs,imm,funct in[(0x18756,14,14,1,6),(0x187e6,14,14,1024,6),(0x1881c,14,14,2,6),(0x187be,14,15,14,1),(0x18808,13,14,6,1)]:
        v=word(p);assert(v&127,v>>12&7,v>>7&31,v>>15&31,sx(v>>20,12))==(0x13,funct,rd,rs,imm)
    branch(0x187b4,1,15,14,0x187a2);branch(0x187c2,5,14,0,0x18830);branch(0x187ce,1,14,15,0x1882c);branch(0x1880c,5,13,0,0x18806);branch(0x18828,1,15,14,0x18824)
    h=half(0x187b0);d=sx(((h>>12&1)<<8)|((h>>10&3)<<3)|((h>>5&3)<<6)|((h>>3&3)<<1)|((h>>2&1)<<5),9)
    assert(h&3,h>>13,8+(h>>7&7),0x187b0+d)==(1,7,15,0x187b8)
    h=half(0x18832);d=sx(((h>>12&1)<<11)|((h>>11&1)<<4)|((h>>9&3)<<8)|((h>>8&1)<<10)|((h>>7&1)<<6)|((h>>6&1)<<7)|((h>>3&7)<<1)|((h>>2&1)<<5),12)
    assert(h&3,h>>13,0x18832+d)==(1,5,0x187ca)
    for pc,rd,imm in[(0x18816,14,-4),(0x18826,15,12)]:
        h=half(pc);assert(h&3,h>>13,h>>10&3,8+(h>>7&7),sx(((h>>12&1)<<5)|(h>>2&31),6))==(1,4,2,rd,imm)
    for pc,rd,rs2,op in[(0x18762,14,13,3),(0x1876e,14,13,3),(0x1877a,14,13,3),(0x18786,14,13,3),(0x18798,14,13,2),(0x187a4,15,12,3),(0x187ee,14,13,3),(0x187f8,14,13,2),(0x18802,14,13,2)]:
        h=half(pc);assert(h&3,h>>13,h>>10&3,h>>12&1,8+(h>>7&7),8+(h>>2&7),h>>5&3)==(1,4,3,0,rd,rs2,op)
    memory=[];written=set()
    for pc,x in sorted(by.items()):
        h=half(pc);q=h&3;f=h>>13
        if x['size']==4:
            v=word(pc)
            if v&127 in(0x37,0x17,3,0x13,0x33,0x6f,0x67,0x73):written.add(v>>7&31)
        elif q==0 and f in(2,6):
            imm=((h>>10&7)<<3)|((h>>6&1)<<2)|((h>>5&1)<<6);base=8+(h>>7&7);operand=8+(h>>2&7)
            memory.append(dict(PC=pc,kind='READ32'if f==2 else'WRITE32',base_register=base,offset=imm,operand_register=operand))
            if f==2:written.add(operand)
        elif q==2 and f in(2,6):
            operand=h>>7&31 if f==2 else h>>2&31
            imm=((h>>12&1)<<5)|((h>>4&7)<<2)|((h>>2&3)<<6)if f==2 else((h>>9&15)<<2)|((h>>7&3)<<6)
            memory.append(dict(PC=pc,kind='READ32'if f==2 else'WRITE32',base_register=2,offset=imm,operand_register=operand))
            if f==2:written.add(operand)
        elif q==1 and f in(0,2,3):written.add(h>>7&31)
        elif q==1 and f==4:written.add(8+(h>>7&7))
    assert 10 not in written and {x['offset']for x in memory if x['base_register']==2}=={8,12}
    assert by[0x18830]['opcode']=='sw zero, 12(sp)'and by[0x18832]['opcode']=='j 0x187ca'and half(0x1882e)==0x8082
    rmw=[dict(read_PC=a,write_PC=b,offset=o,keep=k,set=s)for a,b,o,k,s in[(0x1874e,0x1875a,0,0xffffffff,1),(0x1875c,0x18764,4,0xf8ff0000,0),(0x18766,0x18770,0,0xfef6ffff,0),(0x18772,0x1877c,0,0xfffbffff,0),(0x1877e,0x18788,4,0xff80ffff,0),(0x18794,0x1879a,0,0xffffffff,0x10000),(0x187d6,0x187de,4,0xffffffff,0),(0x187e0,0x187e2,4,0xffffffff,0),(0x187e4,0x187ea,4,0xffffffff,0x400),(0x187ec,0x187f0,4,0xffc0ffff,0),(0x187f2,0x187fa,4,0xffffffff,0x290000),(0x187fc,0x18804,0,0xffffffff,0x1000000),(0x18810,0x18818,4,0xfffffffc,0),(0x1881a,0x18820,4,0xffffffff,2)]]
    for r in rmw:
        a=next(x for x in memory if x['PC']==r['read_PC']);z=next(x for x in memory if x['PC']==r['write_PC']);assert a['kind']=='READ32'and z['kind']=='WRITE32'and a['offset']==z['offset']==r['offset']
    return dict(original_start=0x1874a,original_end_exclusive=0x18834,bytes=234,instructions=93,sha256=snapshot['sha256'],register_base=reg,live_frame_offsets=[8,12],ordinary_unaliased_counter_terminal=4096,first_poll_mask=0x20000,fresh_status_PC=0x187bc,fresh_status_branch_PC=0x187c2,PLL_poll_bit=25,switch_poll_mask=12,switch_poll_expected=8,cold_tail=dict(store_PC=0x18830,return_to_shared_PC=0x187ca),original_a0_explicitly_written=False,original_return_is_success_code_proved=False,memory_accesses=memory,RMW_order=rmw)
