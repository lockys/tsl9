#!/usr/bin/env python3
"""Create this review's final source/metadata bundle after explicit producer freeze."""
import argparse
import hashlib
import json
from pathlib import Path
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def write(p,value):
    data=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
    if p.exists():need(p.read_bytes()==data,'Existing identical final evidence only');return
    p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);a=p.parse_args();root=a.project_root.resolve();here=Path(__file__).resolve().parent;case=here.parent;model=root/'experiments/tsl9-v4160-ota-page-reply';native=case/'implementation/verify_native.py';need(sha(native)=='d80564844da68c0946e53395b64a08c7e4c169b416088a849043861592a4b90d','Explicit final frozen native CLI')
    expected={'c':'97b50c6d1de459468a0b175c3a0240412a2203b6c5ef98fcbb152e76a0212392','cpp':'3d5a7e8ed9e72dbf84d9d5d38f1f6b37f216346392f4a391400ff55489f57e22'};bound={}
    for mode,pin in expected.items():
        folder=model/'build/formal-native-final'/mode;receipt=folder/'verification.json';need(sha(receipt)==pin,'Explicit final actual producer '+mode+' receipt');actual=read(here/'build'/('final-'+mode+'.json'));need(actual['actual_sha256']['verification.json']==pin and actual['linked']['all_source_instruction_bytes_equal'],'Actual independent final linked result');need(len(actual['native']['negative_controls'])==11 and len(actual['linked_controls'])==3,'Bounded final controls')
        for name,value in actual['actual_sha256'].items():need(sha(folder/name)==value,'Unchanged final actual artifact '+name)
        audit=read(here/'build'/('order-prototype-'+mode)/'audit.json');need(audit['input_sha256']==sha(folder/'page_reply.o'),'Prototype malformed matrix uses exact final compiler object');need((len(audit['actual_ELF_controls']),len(audit['path_controls']),len(audit['receipt_controls']))==(18,5,3),'Actual bounded scheduling matrix');write(here/'metadata'/('final-'+mode+'.json'),actual);write(here/'metadata'/('order-audit-'+mode+'.json'),audit)
        producer=read(receipt)
        for name in ('page_reply.c','page_reply.h','reply_io.h','host_io.c','host_io.h'):
            relative=(model/'src'/name).relative_to(root).as_posix();need(producer['input_sha256'][relative]==sha(root/relative),'Final actual five-source closure')
        bound[mode]={'producer_receipt':receipt.relative_to(root).as_posix(),'producer_receipt_sha256':pin,'independent_receipt_sha256':sha(here/'metadata'/('final-'+mode+'.json')),'compiler_object_sha256':sha(folder/'page_reply.o'),'ordered_object_sha256':sha(folder/'source-ordered.o'),'linked_ELF_sha256':sha(folder/'ADDRESS-WITNESS-ONLY.elf'),'source':{name:sha(model/'src'/name) for name in ('page_reply.c','page_reply.h','reply_io.h','host_io.c','host_io.h')}}
    source_seal=case/'source-review/seal.json';order_seal=case/'scheduling-review/seal.json';need(sha(source_seal)=='2fe1ed8e78cbb6e054a0368c330b5d1d15f9c75bc0510769340371464b3d32f3','Independent immutable source seal');need(sha(order_seal)=='eaaa06854f003879d3630608aabab01fcaafaa38f7e073f2185c64f3a938ab54','Explicit frozen scheduling seal')
    write(here/'closure.json',{'schema':'TSL9-reply-ABI-review-final-binding-v1','passed':True,'producer_native_CLI_sha256':sha(native),'source_seal_sha256':sha(source_seal),'scheduling_seal_sha256':sha(order_seal),'selected_actual_modes':bound,'published_build_artifacts':False,'default_verification':'metadata-only; no actual build replay','actual_replay':'review.py --project-root ROOT --replay NEW_REPORT.json','whole_image_integration':False,'resident_ROM_ABI_verified':False,'hardware_OTA_validated':False,'target_execution':False,'ISA_emulation':False})
    need((here/'README.md').read_bytes()==(here/'readme.zh-TW.md').read_bytes(),'Default README equals full Traditional Chinese copy');members=sorted(p for p in here.rglob('*') if p.is_file() and 'build' not in p.relative_to(here).parts and '__pycache__' not in p.relative_to(here).parts and p.name!='seal.json');need(all(p.suffix in ('.py','.sh','.md','.json') for p in members),'Only source and metadata members')
    for path in members:
        raw=path.read_bytes();need(b'\r' not in raw and raw.endswith(b'\n') and not raw.endswith(b'\n\n'),'UTF8 LF and one EOF newline: '+path.name);raw.decode('utf-8')
    write(here/'seal.json',{'schema':'TSL9-reply-ABI-review-seal-v1','passed':True,'files':[{'path':p.relative_to(here).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in members],'default_mode':'metadata-only','actual_build_artifacts_included':False,'target_execution':False,'hardware_OTA_admitted':False});print(json.dumps({'passed':True,'members':len(members),'seal_sha256':sha(here/'seal.json')}))
if __name__=='__main__':main()
