"""V1.31/Xwchc response owner, zero flag. Start at the pending-helper call.
Descriptor inputs model the preceding encoder; release is observed, not executed.
Run with the SHA-pinned reference binary as argv[1]. No device I/O.
"""
import check_v131_cmd6_pending_slot as slot


def attempt(m, desc, ident, d):
    # s0 is this invocation's saved response pointer; desc+4 carries the same D.
    m.update({desc+i:v for i,v in enumerate(b'\x05\0\x08\0'+d.to_bytes(4,'little'))})
    b=slot.b; pc=0x4eb08; a0=ident; s1=ident; releases=[]; log=None
    for _ in range(20):
        at=pc; i=pc-0x40000; w=int.from_bytes(b[i:i+4],'little'); h=w&65535
        pc+=4 if h&3==3 else 2
        if w&4095==0xef:
            off=w>>31<<20|(w&0xff000)|(w>>20&1)<<11|(w>>21&1023)<<1
            slot.ck(at+slot.sx(off,21)==0x4e4cc)
            a0,log=slot.run(m,desc,a0)
        elif h==0xbff9: pc=at-34 # c.j 4eaea
        elif h==0x84aa: s1=a0
        elif h==0xc511:
            if a0==0: pc=at+12
        elif h==0x8522: a0=d
        elif w==0x1ffb1097:
            j=int.from_bytes(b[i+4:i+8],'little'); slot.ck(j&0xfffff==0x80e7)
            slot.ck(at+(w&0xfffff000)+slot.sx(j>>20,12)==0x20000110)
            releases.append(a0); a0=0x12345678; pc+=4
        elif h in (0x50f2,0x5462): pass # loads of ra and s0, neither used by result move
        elif h==0x8526: return s1,releases,log # a0=s1; stop before remaining restores
        else: raise ValueError(hex(at))
    raise ValueError('step bound')

row=slot.row; desc=slot.desc; count=0
for old,new in ((0x2000460e,0x2000480e),(0x2000480e,0x2000460e)):
    for tag1,tag2 in ((11,12),(12,11),(11,11)):
        m={row+i:0 for i in range(12)}
        rc,rel,_=attempt(m,desc,tag1,old); slot.ck((rc,rel)==(0,[]))
        saved=bytes(m[row+i] for i in range(12))
        slot.ck(saved[4:]==old.to_bytes(4,'little')+b'\x08\0'+tag1.to_bytes(2,'little'))
        rc,rel,log=attempt(m,desc,tag2,new)
        slot.ck((rc,rel,log)==(22,[new],[('r',desc,2,5),('r',row+4,4,old)]))
        slot.ck(bytes(m[row+i] for i in range(12))==saved); count+=1
print(f'PASS: {count} two-response pairs; occupied row unchanged, only new D passed to release, caller result 22')
