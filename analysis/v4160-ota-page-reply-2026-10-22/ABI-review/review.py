#!/usr/bin/env python3
"""Explicit actual component/IR/order/linked-witness review and readonly replay."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import runpy
import struct
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
NATIVE='7c5dc682981fec994c9d5b23b2579371bd1ee352c0220a57c1588c28a099ba08'
ORDER='6e8a137297c7aa7e7cfa1153a7b46ee061269d3912b72180e941c2c942448776'
POLICY='04d9c56c859f36e380d17e180076f8694993842922f3c6153fc68b1fb63e61ea'
def need(v,m):
    if not v:raise ValueError(m)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def native():
    path=HERE/'native.py';need(sha(path)==NATIVE,'Frozen independent native checker');s=importlib.util.spec_from_file_location('reply_abi_final_native',path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class BytesInput:
    def __init__(self,raw):self.raw=raw
    def read_bytes(self):return self.raw
def linked_contract(ELF,decoder,path,original):
    e=ELF(path);need(e.kind==2 and e.flags==1,'Actual RV32/RVC soft-float ET_EXEC witness');need(struct.unpack_from('<I',e.raw,24)[0]==0x9b8e,'Fixed original numeric entry')
    functions=[s for s in e.symbols if s['name']=='tsl9_ota_page_reply_9b8e'];need(len(functions)==1,'One linked compiler function');f=functions[0];need((f['value'],f['size'],f['info'],f['other'])==(0x9b8e,124,18,0),'Fixed124B linked function role');need(e.function_bytes(f)==original,'All124 linked bytes equal independently proven original source');decoder.validate(e.function_bytes(f))
    providers=[s for s in e.symbols if s['name']=='__tsl9v4160_call_8a56'];need(len(providers)==1 and (providers[0]['value'],providers[0]['size'],providers[0]['index'])==(0x8a56,0,0xfff1),'Numeric ABS TX witness only, no provider implementation')
    need(not e.relocations and not any(s['index']==0 and s['name'] for s in e.symbols),'No unresolved relocation/provider')
    owner=e.sections[f['index']];need(owner['flags']==6 and owner['address']==0x9b8e and owner['size']==124,'Exact AX component owner');need([s['index'] for s in e.sections if s['flags']&2 and s['size']]==[owner['index']],'Only124B component allocation; no whole image claim')
    offset=struct.unpack_from('<I',e.raw,28)[0];size,count=struct.unpack_from('<HH',e.raw,42);need(size==32 and offset+size*count<=len(e.raw),'Bounded actual ELF32 program headers');loads=[]
    for i in range(count):
        row=struct.unpack_from('<8I',e.raw,offset+size*i)
        if row[0]==1:
            _,fileoff,va,pa,filesz,memsz,flags,align=row;need(fileoff+filesz<=len(e.raw) and filesz<=memsz and not flags&2,'Bounded nonwritable LOAD');loads.append(row)
    covering=[r for r in loads if r[2]<=0x9b8e and 0x9c0a<=r[2]+r[4] and r[1]+0x9b8e-r[2]==owner['offset']];need(len(covering)==1 and covering[0][6]&5==5,'Actual file-backed executable LOAD covers fixed function')
    return {'ELF_sha256':hashlib.sha256(e.raw).hexdigest(),'linked_body_sha256':hashlib.sha256(original).hexdigest(),'fixed_entry':0x9b8e,'bytes':124,'instructions':50,'TX_target':0x8a56,'TX_link_RA':0x9be4,'all_source_instruction_bytes_equal':True,'numeric_provider_witness_only':True,'whole_image_integrated':False,'hardware_OTA_validated':False}
def linked_controls(ELF,decoder,path,original):
    e=ELF(path);f=next(s for s in e.symbols if s['name']=='tsl9_ota_page_reply_9b8e');owner=e.sections[f['index']];bodies=[];b=bytearray(e.raw);b[owner['offset']+0x52]^=0x80;bodies.append(('TX_does_not_link_RA',bytes(b)))
    for section_index,entries in e.symbol_tables.items():
        for ordinal,symbol in enumerate(entries):
            if symbol['name']=='__tsl9v4160_call_8a56':
                b=bytearray(e.raw);struct.pack_into('<I',b,e.sections[section_index]['offset']+ordinal*16+4,0x8a58);bodies.append(('wrong_ABS_TX_provider',bytes(b)))
    b=bytearray(e.raw);struct.pack_into('<I',b,24,0x9b90);bodies.append(('wrong_original_entry',bytes(b)));results=[]
    for name,payload in bodies:
        try:linked_contract(ELF,decoder,BytesInput(payload),original)
        except ValueError as error:results.append({'name':name,'actual_ELF_bytes_mutated_in_memory':True,'rejected':True,'reason':str(error)});continue
        raise ValueError('Linked actual ELF mutant admitted: '+name)
    return results
def review(root,folder):
    root=root.resolve();folder=folder.resolve();need(folder.is_relative_to(root),'Explicit actual folder inside project root');m=native();decoder,ELFmod,original=m.context(root);actual=m.review(root,folder,folder/'source-ordered.o')
    tool=root/'experiments/tsl9-v4160-reply-abi-order/order.py';need(sha(tool)==ORDER and sha(tool.with_name('order-policy.json'))==POLICY,'Frozen explicit source-owned scheduling layer');api=runpy.run_path(str(tool));ordering=api['replay'](root,folder/'ABI-order.json');need(ordering['input']['sha256']==sha(folder/'page_reply.o') and ordering['output']['sha256']==sha(folder/'source-ordered.o'),'Actual compiler/order provenance association')
    producer=folder/'verification.json';receipt=json.loads(producer.read_bytes());need(receipt.get('schema')=='TSL9-OTA-page-reply-native-v1' and receipt.get('passed') is True and receipt.get('mode') in ('c','cpp'),'Actual producer native receipt')
    recipes=[r['argv'] for r in receipt['commands'] if '-x' in r['argv']];need(len(recipes)==2,'Actual base object and IR compiler recipes');language='c' if receipt['mode']=='c' else 'c++';standard='-std=c11' if language=='c' else '-std=c++17'
    need(all(argv[argv.index('-x')+1]==language and standard in argv for argv in recipes),'Producer mode matches actual object/IR compiler argv');linked=linked_contract(ELFmod.ELF,decoder,folder/'ADDRESS-WITNESS-ONLY.elf',original)
    paths=['page_reply.o','page_reply.ll','source-ordered.o','ABI-order.json','ADDRESS-WITNESS-ONLY.elf','original-entry-component.ld','verification.json'];pins={name:sha(folder/name) for name in paths}
    return {'schema':'TSL9-OTA-page-reply-independent-ABI-final-v1','passed':True,'mode':receipt['mode'],'actual_folder':folder.relative_to(root).as_posix(),'actual_sha256':pins,'native_checker_sha256':NATIVE,'order_tool_sha256':ORDER,'order_policy_sha256':POLICY,'native':actual,'linked':linked,'linked_controls':linked_controls(ELFmod.ELF,decoder,folder/'ADDRESS-WITNESS-ONLY.elf',original),'resident_provider_ABI_proved':False,'computed_entry_absence_proved':False,'whole_image_integrated':False,'hardware_OTA_validated':False,'target_execution':False,'ISA_emulation':False,'network':False}
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);p.add_argument('--folder',type=Path);p.add_argument('--receipt',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
    if a.replay:
        need(a.folder is None and a.receipt is None,'Readonly replay takes only explicit report');old=json.loads(a.replay.read_bytes());result=review(root,root/old['actual_folder']);need(result==old,'Exact actual independent report replay')
    else:
        need(a.folder is not None and a.receipt is not None and not a.receipt.exists(),'Explicit folder and new create-only independent receipt');result=review(root,a.folder);a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
    print(json.dumps({'passed':True,'mode':result['mode'],'actual_build_artifact_replay':True,'linked_source_bytes':124,'native_raw_IR_controls':len(result['native']['negative_controls']),'linked_ELF_controls':len(result['linked_controls']),'hardware_OTA_validated':False}))
if __name__=='__main__':main()
