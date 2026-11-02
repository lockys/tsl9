#!/usr/bin/env python3
"""Bounded static scan for GP+167 direct writes and writer value shape."""
import argparse,hashlib,json,runpy,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--firmware',type=Path,required=True);p.add_argument('--layout',type=Path,required=True);p.add_argument('--reader',type=Path,required=True);p.add_argument('--r2',type=Path,required=True);a=p.parse_args()
def sha(b):return hashlib.sha256(b).hexdigest()
image=a.firmware.read_bytes()
if len(image)!=76800 or sha(image)!='28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89':raise ValueError('Candidate image changed')
if sha(a.layout.read_bytes())!='28360fab7c267bb635f1dfce1d3330903b2ebc113dd02872c9336d2d1264d0a7' or sha(a.reader.read_bytes())!='a56503572e8b65308ae1c8978ba5a6d44d0a20cd969315dc1b12103b59a9b43a':raise ValueError('Layout or reader changed')
elf=runpy.run_path(str(a.reader))['ELF'](a.layout);secs=[s for s in elf.sections if s['flags']&6==6 and s['size']]
if len(secs)!=6 or sum(s['size'] for s in secs)!=69412:raise ValueError('Selected extent changed')
spans=[(s['address'],s['size']) for s in secs]+[(0x14056,0x14c8a-0x14056)]
ordered=sorted(spans)
if any(x[0]+x[1]>y[0] for x,y in zip(ordered,ordered[1:])):raise ValueError('Overlapping ranges')
def is_write(x):
    if x&127!=0x23 or (x>>12)&7 not in (0,1,2) or (x>>15)&31!=3:return False
    offset=((x>>25)<<5)|((x>>7)&31);offset-=4096 if offset&2048 else 0
    return offset<=167<offset+(1<<((x>>12)&7))
def make_store(offset,funct):
    offset&=4095
    return ((offset>>5)<<25)|(3<<15)|(funct<<12)|((offset&31)<<7)|0x23
assert is_write(make_store(167,0)) and is_write(make_store(164,2)) and not is_write(make_store(163,2)) and not is_write(make_store(168,0))
hits=[];counts=[]
for start,size in spans:
    if start<0x8000 or start+size>0x1ac00:raise ValueError('Unexpected range')
    d=image[start-0x8000:start-0x8000+size];i=0;count=0
    while i<size:
        n=4 if d[i]&3==3 else 2
        if i+n>size:raise ValueError('Instruction truncated')
        if n==4 and is_write(int.from_bytes(d[i:i+4],'little')):hits.append(start+i)
        i+=n;count+=1
    counts.append(count)
if sum(counts[:6])!=23602 or counts[-1]!=1008 or hits!=[0x93a2]:raise ValueError('Writer inventory changed')
cmd=[str(a.r2),'-q','-a','riscv','-b','32','-m','0x8000','-c','s 0x9396; pdj 6',str(a.firmware)]
ops=json.loads(subprocess.run(cmd,capture_output=True,text=True,check=True).stdout)
expected={0x9396:'sub a0, s0, a0',0x939a:'lw ra, 28(sp)',0x939c:'lw s0, 24(sp)',0x939e:'seqz a0, a0',0x93a2:'sb a0, 167(gp)',0x93a6:'addi sp, sp, 32'}
if {x['addr']:x['opcode'].lower() for x in ops}!=expected:raise ValueError('Writer instructions changed')
assert {int(x==0) for x in range(256)}=={0,1}
print(json.dumps({'passed':True,'instructions_scanned':sum(counts),'direct_store_addresses':[hex(x) for x in hits],
 'writer_direct_value_domain':[0,1],'synthetic_boundaries':4,'indirect_writers_excluded':True,
 'global_domain_proved':False,'target_executed':False,'hardware_validated':False}))
