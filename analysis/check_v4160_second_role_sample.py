"""Usage: python SCRIPT decoded-app.bin reference-v131.bin. Stop at the second role's branch.
Assumes mapped V1.31 slots, s0=0x40000 and normal helper return. The helper's
post-state is injected, not a claim it can produce arbitrary IDs on hardware.
"""
from pathlib import Path
from hashlib import sha256
import sys


def need(ok, label):
    if not ok: raise ValueError(label)


def sx(x,n): return x-(1<<n) if x & (1<<(n-1)) else x


def inspect(app, rom):
    w=lambda p:int.from_bytes(rom[p-0x40000:p-0x40000+4],'little')
    op=int.from_bytes(app[0xeb8:0xebc],'little');need(op&0xfffff==0x42783 and app[0xebc:0xebe]==bytes.fromhex('8297'),'APP indirect call')
    slot=0x40000+sx(op>>20,12); entry=w(slot)
    need((slot,entry)==(0x401ac,0x6dd86),'role slot')
    raw=rom[entry-0x40000:entry-0x40000+30];need(raw.hex()=='411106c6efc0aea7b737002083c7575f1307d00ffd1793f7f70f6372f706','role prefix')
    j=w(entry+4); imm=(j>>31<<20)|((j>>12&255)<<12)|((j>>20&1)<<11)|((j>>21&1023)<<1)
    helper=entry+4+sx(imm,21); address=(w(entry+8)&0xfffff000)+sx(w(entry+12)>>20,12)
    br=w(entry+26); disp=(br>>31<<12)|((br>>7&1)<<11)|((br>>25&63)<<5)|((br>>8&15)<<1)
    return helper,address,w(entry+16)>>20,w(entry+22)>>20,entry+30,entry+26+sx(disp,13)


def trace(fields, incoming, initial, after, helper_result):
    helper,address,limit,mask,fall,skip=fields; ram={address:initial}; events=[]
    events.append(('call',helper,incoming));ram[address]=after; a0=helper_result
    sample=ram[address];events.append(('read',address,sample))
    return (skip if ((sample-1)&mask)<=limit else fall),a0,events


if __name__=='__main__':
    app,rom=[Path(p).read_bytes() for p in sys.argv[1:]]
    need([sha256(b).hexdigest() for b in (app,rom)]==['0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'],'identity')
    f=inspect(app,rom);need(f==(0x5a004,0x200035f5,253,255,0x6dda4,0x6de04),'decoded fields')
    n=0
    for status in (0,24):
        for before in (0,11,255):
            for after in range(256):
                for result in (0,24,0xffffffff):
                    dest,a0,events=trace(f,status,before,after,result)
                    need(events==[('call',0x5a004,status),('read',0x200035f5,after)] and a0==result and dest==(0x6dda4 if after in (0,255) else 0x6de04),'fresh byte vs status');n+=1
    print(f'PASS: {n} projections; incoming status forwarded to helper; branch samples post-call byte; 0/255 enter registration block, 1..254 skip')
