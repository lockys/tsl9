"""Unified bounded TX decoder; opaque calls are scripted state transitions only."""
import struct

MASK=0xffffffff
def need(ok,message):
    if not ok: raise ValueError(message)
def sx(n,bits): return n-(1<<bits) if n&(1<<(bits-1)) else n

class Memory:
    def __init__(self,regions):
        self.regions=[(a,bytearray(b)) for a,b in regions];self.events=bytearray()
        ordered=sorted((a,a+len(b)) for a,b in self.regions)
        need(all(0<=a<b<=1<<32 for a,b in ordered),'bounded regions')
        need(all(a[1]<=b[0] for a,b in zip(ordered,ordered[1:])),'disjoint regions')
    def event(self,*fields): self.events.extend(struct.pack('<4I',*fields))
    def access(self,a,w,v=None):
        need(w in (1,2,4) and a%w==0,'aligned access')
        for base,data in self.regions:
            i=a-base
            if 0<=i and i+w<=len(data):
                if v is None: v=int.from_bytes(data[i:i+w],'little');kind=1
                else:
                    v&=(1<<(8*w))-1;data[i:i+w]=v.to_bytes(w,'little');kind=2
                self.event(kind,a,w,v);return v
        raise ValueError('unmapped access')

class Whole:
    def __init__(self,image):
        self.code={};pc=0x8a56
        while pc<0x8b6c:
            off=pc-0x8000;half=int.from_bytes(image[off:off+2],'little');size=4 if half&3==3 else 2
            need(pc+size<=0x8b6c,'instruction boundary')
            self.code[pc]=(int.from_bytes(image[off:off+size],'little'),size);pc+=size
    def run(self,regions,registers,actions,budget=16*65535+1024):
        need(len(registers)==32 and registers[0]==0 and all(type(x) is int and 0<=x<=MASK for x in registers),'registers')
        need(isinstance(actions,list) and len(actions)<=2,'bounded actions')
        for a in actions:
            need(set(a)=={'target','result','registers','writes'},'action fields')
            need(all(type(a[k]) is int and 0<=a[k]<=MASK for k in ('target','result')) and a['target']%2==0,'action target/result')
            need(isinstance(a['registers'],dict) and all(type(k) is int and 1<=k<32 and k!=10 and type(v) is int and 0<=v<=MASK for k,v in a['registers'].items()),'register changes')
            need(isinstance(a['writes'],list) and len(a['writes'])<=4,'bounded writes')
            for address,width,value in a['writes']:
                need(all(type(v) is int for v in (address,width,value)) and 0<=address<=MASK and width in (1,2,4) and address%width==0 and 0<=value<=MASK,'write domain')
        m=Memory(regions);r=list(registers);pc=0x8a56;calls=0
        def put(k,v):
            if k:r[k]=v&MASK
        for _ in range(budget):
            if pc in (0x8b50,0x8aca,0x8b6c):return m.regions,r,bytes(m.events),pc,calls,0
            if pc==0x8ace:
                m.event(5,pc,4,0)
                for j,v in enumerate(r):m.event(6,j,4,v)
                if r[8]>65535:return m.regions,r,bytes(m.events),pc,calls,6
            need(pc in self.code,'bounded PC');p=pc;w,size=self.code[pc];pc+=size
            if size==4:
                op,rd,f,a,b=w&127,w>>7&31,w>>12&7,w>>15&31,w>>20&31
                if op==0x13 and f in (0,4,7):
                    imm=sx(w>>20,12)
                    put(rd,r[a]+imm if f==0 else r[a]^imm if f==4 else r[a]&imm)
                elif op==0x13 and w>>25==0 and f in (1,5):put(rd,r[a]<<b if f==1 else r[a]>>b)
                elif op==0x33 and f==0 and w>>25 in (0,1):put(rd,r[a]+r[b] if w>>25==0 else r[a]*r[b])
                elif op==0x17:put(rd,p+(w&0xfffff000))
                elif op==0x23 and f in (0,1):
                    off=sx((w>>25<<5)|(w>>7&31),12);m.access((r[a]+off)&MASK,1<<f,r[b])
                elif op==0x37:put(rd,w&0xfffff000)
                elif op==3 and f in (2,4,5):put(rd,m.access((r[a]+sx(w>>20,12))&MASK,4 if f==2 else 2 if f==5 else 1))
                elif op==0x63 and f in (0,1,6):
                    off=(w>>31)<<12|(w>>7&1)<<11|(w>>25&63)<<5|(w>>8&15)<<1
                    take=r[a]==r[b] if f==0 else r[a]!=r[b] if f==1 else r[a]<r[b]
                    if take:pc=p+sx(off,13)
                else:raise ValueError('unsupported RV32 instruction')
            else:
                q,f,rd,rs2=w&3,w>>13,w>>7&31,w>>2&31
                imm=sx((w>>2&31)|(w>>7&32),6)
                if q==2 and f==6:
                    off=(w>>9&15)<<2|(w>>7&3)<<6;m.access((r[2]+off)&MASK,4,r[rs2])
                elif q==2 and f==2 and rd:
                    off=(w>>12&1)<<5|(w>>4&7)<<2|(w>>2&3)<<6;put(rd,m.access((r[2]+off)&MASK,4))
                elif q==2 and f==0 and rd and not w&0x1000:put(rd,r[rd]<<rs2)
                elif q==2 and f==4 and w&0x1000 and rd and rs2:put(rd,r[rd]+r[rs2])
                elif q==1 and f==4 and w>>10&3==0 and not w&0x1000:put(8+(w>>7&7),r[8+(w>>7&7)]>>(w>>2&31))
                elif q==1 and f==5:
                    off=(w>>12&1)<<11|(w>>11&1)<<4|(w>>9&3)<<8|(w>>8&1)<<10|(w>>7&1)<<6|(w>>6&1)<<7|(w>>3&7)<<1|(w>>2&1)<<5
                    pc=p+sx(off,12)
                elif q==1 and f==3 and rd==2:
                    off=(w>>12&1)<<9|(w>>6&1)<<4|(w>>5&1)<<6|(w>>3&3)<<7|(w>>2&1)<<5
                    put(2,r[2]+sx(off,10))
                elif q==1 and f==3 and rd not in (0,2):put(rd,imm<<12)
                elif q==1 and f==0 and rd:put(rd,r[rd]+imm)
                elif q==1 and f==2 and rd:put(rd,imm)
                elif q==2 and f==4 and not w&0x1000 and rd and rs2:put(rd,r[rs2])
                elif q==2 and f==4 and w&0x1000 and rd and not rs2:
                    target=r[rd]&~1;put(1,pc);m.event(3,target,pc,calls)
                    for j,v in enumerate(r):m.event(4,j,4,v)
                    need(calls<len(actions),'missing scripted return');a=actions[calls];calls+=1
                    need(target==a['target'],'scripted target mismatch')
                    for address,width,value in a['writes']:m.access(address,width,value)
                    put(10,a['result'])
                    for k,v in a['registers'].items():put(k,v)
                else:raise ValueError('unsupported RVC instruction')
        raise ValueError('entry budget exceeded')
