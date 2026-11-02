#!/usr/bin/env python3
"""Bounded instruction scan for direct GP references to settings pointer storage."""
import argparse,hashlib,json,runpy
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--firmware',type=Path,required=True);p.add_argument('--layout',type=Path,required=True);p.add_argument('--reader',type=Path,required=True)
a=p.parse_args()
def sha(b):return hashlib.sha256(b).hexdigest()
image=a.firmware.read_bytes()
if len(image)!=76800 or sha(image)!='28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89':raise ValueError('Candidate image changed')
if sha(a.layout.read_bytes())!='28360fab7c267bb635f1dfce1d3330903b2ebc113dd02872c9336d2d1264d0a7' or sha(a.reader.read_bytes())!='a56503572e8b65308ae1c8978ba5a6d44d0a20cd969315dc1b12103b59a9b43a':raise ValueError('Layout or reader changed')
elf=runpy.run_path(str(a.reader))['ELF'](a.layout)
sections=[s for s in elf.sections if s['flags']&6==6 and s['size']]
if len(sections)!=6 or sum(s['size'] for s in sections)!=69412:raise ValueError('Selected code extents changed')
spans=[(s['address'],s['size']) for s in sections]+[(0x14056,0x14c8a-0x14056)]
ordered=sorted(spans)
if any(x[0]+x[1]>y[0] for x,y in zip(ordered,ordered[1:])):raise ValueError('Overlapping code extents')
def classify(word):
    if (word>>15)&31 != 3:return None
    op,funct=word&127,(word>>12)&7
    if op==0x23 and funct in (0,1,2):
        imm=((word>>25)<<5)|((word>>7)&31);imm-=4096 if imm&2048 else 0
        width=1<<funct
        return 'store' if imm<88 and 84<imm+width else None
    if op==0x13 and funct==0:
        imm=word>>20;imm-=4096 if imm&2048 else 0
        return 'address' if 81<=imm<88 else None
    return None
assert classify(0x0431aa23)=='store'
assert classify(0x05418293)=='address'
def store(offset,funct):
    value=offset&4095
    return ((value>>5)<<25)|(3<<15)|(funct<<12)|((value&31)<<7)|0x23
assert classify(store(81,2))=='store' and classify(store(80,2)) is None
assert classify(store(87,0))=='store' and classify(store(88,0)) is None
hits=[];counts=[];next_zero_loads=0;other_followups=[]
for start,size in spans:
    if not (0x8000<=start and start+size<=0x1ac00):raise ValueError('Unexpected extent')
    data=image[start-0x8000:start-0x8000+size];at=0;count=0
    while at<size:
        n=4 if data[at]&3==3 else 2
        if at+n>size:raise ValueError('Truncated instruction')
        kind=classify(int.from_bytes(data[at:at+4],'little')) if n==4 else None
        if kind:
            word=int.from_bytes(data[at:at+4],'little')
            hits.append({'pc':hex(start+at),'kind':kind})
            if kind=='address':
                rd=(word>>7)&31;imm=word>>20;imm-=4096 if imm&2048 else 0
                follow=data[at+4:at+8];h=int.from_bytes(follow[:2],'little')
                if len(follow)<2:raise ValueError('Address formation ends at section boundary')
                standard=len(follow)>=4 and h&3==3 and (int.from_bytes(follow,'little')&0x707f)==0x2003 and (int.from_bytes(follow,'little')>>15)&31==rd and int.from_bytes(follow,'little')>>20==0
                compressed=h&3==0 and (h>>13)&7==2 and ((h>>7)&7)+8==rd and (h&0x1c60)==0
                if imm==84 and (standard or compressed):next_zero_loads+=1
                else:other_followups.append({'pc':hex(start+at),'gp_offset':imm})
        at+=n;count+=1
    counts.append(count)
if counts[:6] and sum(counts[:6])!=23602:raise ValueError('Instruction boundaries changed')
print(json.dumps({'passed':True,'selected_code_bytes':69412,'additional_window_bytes':0x14c8a-0x14056,
 'selected_instructions':sum(counts[:6]),'additional_instructions':counts[-1],
 'direct_stores':[h for h in hits if h['kind']=='store'],
 'address_formations':[h for h in hits if h['kind']=='address'],
 'following_zero_offset_word_loads':next_zero_loads,'other_followups':other_followups,
 'indirect_writers_excluded':True,'reachable_paths_proved':False,'target_executed':False}))
