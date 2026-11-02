#!/usr/bin/env python3
"""Find adjacent LUI/AUIPC plus standard memory/address operations near state."""
import argparse,hashlib,json,runpy
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--firmware',type=Path,required=True);p.add_argument('--layout',type=Path,required=True);p.add_argument('--reader',type=Path,required=True);a=p.parse_args()
image=a.firmware.read_bytes();layout=a.layout;reader=a.reader
assert hashlib.sha256(image).hexdigest()=='28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89'
assert hashlib.sha256(layout.read_bytes()).hexdigest()=='28360fab7c267bb635f1dfce1d3330903b2ebc113dd02872c9336d2d1264d0a7'
assert hashlib.sha256(reader.read_bytes()).hexdigest()=='a56503572e8b65308ae1c8978ba5a6d44d0a20cd969315dc1b12103b59a9b43a'
E=runpy.run_path(str(reader))['ELF'];secs=[x for x in E(layout).sections if x['flags']&6==6 and x['size']]
assert len(secs)==6 and sum(x['size'] for x in secs)==69412
spans=[(x['address'],x['size']) for x in secs]+[(0x14056,0xc34)]
target=(0x2000414c,0x20004150);hits=[];pairs=0
def decode_pair(x,y,pc):
    op=x&127;reg=(x>>7)&31
    if op not in (0x17,0x37) or not reg or y&3!=3 or (y>>15)&31!=reg:return None
    opcode=y&127;funct=(y>>12)&7;kind=None;width=0
    if opcode==3 and funct in (0,1,2,4,5):kind='load';width={0:1,1:2,2:4,4:1,5:2}[funct];imm=y>>20
    elif opcode==0x23 and funct in (0,1,2):kind='store';width=1<<funct;imm=((y>>25)<<5)|((y>>7)&31)
    elif opcode==0x13 and funct==0:kind='address';width=1;imm=y>>20
    if not kind:return None
    imm-=4096 if imm&2048 else 0
    return ((pc if op==0x17 else 0)+(x&0xfffff000)+imm)&0xffffffff,width,kind
assert decode_pair(0x200047b7,0x14c78793,0)==(0x2000414c,1,'address')
assert decode_pair(0x200047b7,0x14c7a783,0)==(0x2000414c,4,'load')
assert decode_pair(0x200047b7,0x15078793,0)==(0x20004150,1,'address')
assert decode_pair(0x200047b7,0x14c70793,0) is None
synthetic_sw=((332>>5)<<25)|(10<<20)|(15<<15)|(2<<12)|((332&31)<<7)|0x23
assert decode_pair(0x20003797,synthetic_sw,0x1000)==(0x2000414c,4,'store')
for start,size in spans:
    d=image[start-0x8000:start-0x8000+size];i=0
    while i<size:
        n=4 if d[i]&3==3 else 2
        if i+n>size:raise ValueError('Truncated instruction')
        if n==4 and i+8<=size:
            x=int.from_bytes(d[i:i+4],'little');y=int.from_bytes(d[i+4:i+8],'little')
            pair=decode_pair(x,y,start+i)
            if pair:
                pairs+=1;val,width,kind=pair
                if val<target[1] and target[0]<val+width:hits.append({'pc':hex(start+i),'target':hex(val),'width':width,'kind':kind})
        i+=n
print(json.dumps({'passed':True,'adjacent_pairs':pairs,'hits':hits,'synthetic_controls':5,'nonadjacent_excluded':True,'target_executed':False}))
