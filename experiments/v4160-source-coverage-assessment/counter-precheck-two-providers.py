#!/usr/bin/env python3
"""Conditionally combine call, halfword gate, and second call projections."""
import argparse,hashlib,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def load(name,file):
    spec=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
first=load('first','counter-precheck-provider-8a82.py')
gate=load('gate','counter-precheck-provider-next-8a96.py')
second=load('second','counter-precheck-second-provider.py')
def need(value,message):
    if not value:raise ValueError(message)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=ROOT);img=(ap.parse_args().root/first.BIN).read_bytes()
    need(len(img)==76800 and hashlib.sha256(img).hexdigest()==first.SHA,'APP identity')
    need(first.decode(img[0xa82:0xa96])==0x4013c,'slot');gate.decode(img[0xa96:0xa9e]);second.check(img[0xa9e:0xabe])
    count=0
    for h in range(65536):
        for r1 in (0,1,2):
            for r2 in (0,1):
                head=first.boundary(0x20004000,h,0x1111,r1);count+=1
                if r1==1:
                    need(head[-1]==0x8acc,'first return');continue
                need(head[-1]==0x8a96,'first fallthrough')
                # Synthetic unchanged registers and matching second halfword.
                address,_,dest=gate.project(0x20004000,h,h)
                need(address==0x2000409a and dest==0x8a9e,'gate')
                # Target word is re-read and deliberately differs from first.
                c,pc,a2=second.project(0x20004000,h,0x2223,r2)
                if h==0xfffe:need((c,pc,a2)==(None,0x8abe,None),'sentinel')
                else:need(c==(h,0x20004080,0x2222,0x8ab6) and pc==(0x8ace if r2 else 0x8abe) and a2==1,'second return')
    print(f'PASS: {count} synthetic split-boundary cases; second target may differ from first')
    print('LIMIT: modeled then-live state is supplied, not produced by provider; segmented projection is not uninterrupted execution or evidence of installed provider, reachability or hardware')
if __name__=='__main__':main()
