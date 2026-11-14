#!/usr/bin/env python3
"""Two APP call boundaries with a stable reference candidate CCC table."""
import argparse,hashlib,importlib.util,itertools
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def load(name,file):
    s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
ref=load('ref','counter-reference-read-ccc.py');first=load('first','counter-precheck-provider-8a82.py');gate=load('gate','counter-precheck-provider-next-8a96.py');second=load('second','counter-precheck-second-provider.py')
def need(v,msg):
    if not v:raise ValueError(msg)
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);root=p.parse_args().root
    img=(root/first.BIN).read_bytes();need(len(img)==76800 and hashlib.sha256(img).hexdigest()==first.SHA,'APP identity')
    need(first.decode(img[0xa82:0xa96])==0x4013c,'APP slot');gate.decode(img[0xa96:0xa9e]);second.check(img[0xa9e:0xabe])
    path=root/ref.REF
    if not path.exists():raise SystemExit('SKIP (nonzero): reference carrier unavailable')
    raw=path.read_bytes();need(hashlib.sha256(raw).hexdigest()==ref.SHA,'reference identity')
    for pc,h in ref.WINDOWS:
        b=bytes.fromhex(h);need(raw[pc-0x40000:pc-0x40000+len(b)]==b,'reference bytes')
    values=(0,1,2,255);handles=(3,4,0xfffe)
    total=same=distinct=0
    for h1,h2,v1,v2,capacity in itertools.product(handles,handles,values,values,(0,1,2)):
        records=[(3,v1),(4,v2)];r1,_=ref.project(h1,records,capacity);b1=first.boundary(0x20004000,h1,0x4b456,r1);total+=1
        if r1==1:need(b1[-1]==0x8acc,'first success');continue
        need(gate.project(0x20004000,h2,h2)[2]==0x8a9e,'gate')
        if h2==0xfffe:need(second.project(0x20004000,h2,0x4b456,0)[0] is None,'sentinel');continue
        r2,_=ref.project(h2,records,capacity);call,dest,_=second.project(0x20004000,h2,0x4b456,r2)
        need(call is not None and dest==(0x8ace if r2==1 else 0x8abe),'second result')
        if h1==h2:
            same+=1;need(r2==r1 and dest==0x8abe,'same handle stable table')
        elif r2==1:distinct+=1
    need(same>0 and distinct>0,'missing cases')
    print(f'PASS: {total} synthetic cases, {same} same-handle fallthroughs and {distinct} distinct-handle second successes')
    print('LIMIT: assumes same candidate in both slots, Xwchc decoding, stable table/capacity, preserved state, successful accesses and return; noncontinuous projections, not hardware or reachability')
if __name__=='__main__':main()
