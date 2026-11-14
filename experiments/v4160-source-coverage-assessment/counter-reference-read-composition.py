#!/usr/bin/env python3
"""Compose APP provider return gate with a conditional V1.31 reference read."""
import argparse,hashlib,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def load(name,file):
    s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
ref=load('ref','counter-reference-read-ccc.py');app=load('app','counter-precheck-provider-8a82.py')
def need(v,msg):
    if not v:raise ValueError(msg)
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);root=p.parse_args().root
    img=(root/app.BIN).read_bytes();need(len(img)==76800 and hashlib.sha256(img).hexdigest()==app.SHA,'APP identity');need(app.decode(img[0xa82:0xa96])==0x4013c,'APP slot')
    path=root/ref.REF
    if not path.exists():raise SystemExit('SKIP (nonzero): reference carrier unavailable')
    data=path.read_bytes();need(hashlib.sha256(data).hexdigest()==ref.SHA,'reference identity')
    for pc,h in ref.WINDOWS:
        b=bytes.fromhex(h);need(data[pc-0x40000:pc-0x40000+len(b)]==b,'reference bytes')
    for handle in range(65536):
        for value in (0,1,2,255):
            records=[(handle,value),(handle,1)]
            result,events=ref.project(handle,records,2)
            call=app.boundary(0x20004000,handle,0x4b456,result)
            need(result==value and call[2]==0x4b456 and call[-1]==(0x8acc if value==1 else 0x8a96),'first match composition')
            need(len(events)==2,'early stop')
    for value in range(256):
        result,events=ref.project(7,[(8,value)],1)
        need(result==0 and app.boundary(0x20004000,7,0x4b456,result)[-1]==0x8a96 and len(events)==1,'no match')
    print('PASS: 262144 matched and 256 nonmatching synthetic compositions; result 1 selects 0x8acc')
    print('LIMIT: segmented models, candidate V1.31 Xwchc, stable records, no alias/interrupts and normal return assumed; installed provider, ABI, reachability and device behavior unverified')
if __name__=='__main__':main()
