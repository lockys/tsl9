#!/usr/bin/env python3
"""Static Flash ownership/reference evidence; no compilation or target execution."""
import argparse
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import re

FW='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
OBJ='646dbe43772be3858223dd6ec7f022c0252deba5879f3d3ab98da2940c9edb97'
LAYOUT='651a8f14d09e373cb5523ec12f97d1fcce3ff26a51b3d835ae55d0239945507b'
ELF='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
RANGES=((0x9c0a,64),(0x18e90,8),(0x18e98,30),(0x18eb6,14),(0x18ec4,46),(0x18ef2,100))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def module(name,p):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def case(root,slug):
    for p in (root/'apk-analysis'/('tsl9-'+slug),root/'analysis'/slug):
        if p.is_dir():return p
    raise ValueError('Missing local/published case '+slug)
def selected(address):return next((a for a,n in RANGES if a<=address<a+n),None)
def sealed(folder,pin):
    need(sha(folder/'seal.json')==pin,'Prior source seal')
    for row in read(folder/'seal.json')['members']:need(sha(folder/row['path'])==row['sha256'],'Sealed source member '+row['path'])
def tail_contract(decoder,raw):
    rows=[decoder.decode(raw,pc) for pc in (0x18f50,0x18f52,0x18f54)]
    expected=[('and',14,14,13,None),('sw',None,15,14,16),('ret',None,1,None,None)]
    need([(r['op'],r['rd'],r['rs1'],r['rs2'],r['immediate']) for r in rows]==expected,'All six tail bytes implement final mask/store/return')
    return rows
def analyze(root,firmware,original,layout,integrated=None,receipt=None):
    need(sha(firmware)==FW and firmware.stat().st_size==76800,'Exact ID2966 raw image')
    raw=firmware.read_bytes();source=case(root,'v4160-flash-native-2026-10-22')/'source'
    sealed(source,'dff9a51e3b59bbdddd150dde37614753bb3c3b440d7bde2f9402c8b6e9a2bce4')
    parser=case(root,'v4160-reset-memory-2026-10-21')/'compiler-review/elf32.py'
    direct_path=case(root,'v4160-placement-2026-10-21')/'source-review/check-placement.py'
    need(sha(parser)==ELF,'Reviewed ELF parser')
    placement=module('entry_direct_static',direct_path);need(sha(direct_path)=='b1818f285558d7120e919fc59f58bcf0d6d1313d7bc631fa51f5bf51fd2e3ee2','Reviewed direct-target decoder')
    decoder=module('entry_original_decoder',source/'inspect.py');proof=read(source/'source-proof.json')
    need(decoder.facts(raw)==proof['ledger'],'Reuse full262B/99instruction source proof')
    tail=tail_contract(decoder,raw);negative=[]
    for pc,h in ((0x18f50,'798f'),(0x18f52,'98c7'),(0x18f54,'0281')):
        changed=bytearray(raw);changed[pc-0x8000:pc-0x8000+2]=bytes.fromhex(h)
        try:tail_contract(decoder,changed)
        except ValueError:negative.append({'PC':pc,'replacement':h,'rejected':True})
        else:raise ValueError('Tail semantic control accepted')
    need(sha(original)==OBJ and sha(layout)==LAYOUT,'Exact original carrier and full layout')
    bindings={n:int(a,16) for n,a in re.findall(r'^\s*(\S+)\s+(0x[0-9a-f]+)(?:\s+\(NOLOAD\))?\s*:',layout.read_text(encoding='utf-8'),re.M)}
    need(len(bindings)==691,'All original layout address bindings')
    parser_module=module('entry_elf_parser',parser)
    def inspect(objpath,expected_rela):
        e=parser_module.ELF(objpath);need(len(e.relocations)==expected_rela,'Known carrier relocation count')
        def address(s):
            if s['index']==0xfff1:return s['value']
            if 0<s['index']<len(e.sections):
                base=bindings.get(e.sections[s['index']]['name'])
                return None if base is None else base+s['value']
            return 0 if not s['name'] and not s['value'] else None
        owners=[];definitions=[]
        for entry,size in RANGES:
            matches=[s for s in e.sections if bindings.get(s['name'])==entry and s['flags']&2 and s['size']]
            need(len(matches)==1,'Unique whole-function original owner');s=matches[0]
            need(s['size']==size and s['flags']==6 and e.data(s)==raw[entry-0x8000:entry-0x8000+size],'Flash source retained exactly in this carrier')
            owners.append({'entry':entry,'bytes':size,'section':s['name'],'sha256':hashlib.sha256(e.data(s)).hexdigest()})
        for s in e.symbols:
            a=address(s)
            if a is not None and selected(a) is not None and s['name']:
                definitions.append({'address':a,'name':s['name'],'size':s['size'],'info':s['info'],'other':s['other'],'owner':e.sections[s['index']]['name'] if 0<s['index']<len(e.sections) else 'ABS','offset':s['value']})
        references=[];unresolved=[]
        for r in e.relocations:
            a=address(r['symbol'])
            if a is None:unresolved.append({'owner':r['owner'],'offset':r['offset'],'type':r['type'],'symbol':r['symbol']['name'],'addend':r['addend']});continue
            target=(a+r['addend'])&0xffffffff
            if selected(target) is None:continue
            site=bindings.get(r['owner']);site=None if site is None else site+r['offset']
            role=('direct_control' if r['type'] in (16,17,44,45) else 'low_anchor_not_runtime_entry' if r['type'] in (24,25) else 'address_formation' if r['type'] in (23,26) else 'absolute_word' if r['type']==1 else 'expression_term')
            references.append({'source':site,'owner':r['owner'],'offset':r['offset'],'target':target,'type':r['type'],'role':role,'symbol':r['symbol']['name'],'symbol_value':r['symbol']['value'],'addend':r['addend'],'target_is_entry':target==selected(target),'external_to_target_function':selected(site)!=selected(target) if site is not None else True})
        direct=[];boundaries=0
        for s in e.sections:
            if s['flags']&6!=6 or not s['size'] or s['name'] not in bindings:continue
            body=e.data(s);offset=0
            while offset<len(body):
                n=4 if body[offset]&3==3 else 2;need(offset+n<=len(body),'Section instruction extent');pc=bindings[s['name']]+offset;boundaries+=1
                found=placement.direct(body[offset:offset+n],pc)
                if found and selected(found[1]) is not None:direct.append({'source':pc,'target':found[1],'op':found[0],'rd':found[2],'target_is_entry':found[1]==selected(found[1]),'external_to_target_function':selected(pc)!=selected(found[1])})
                offset+=n
        ordered=lambda rows:sorted(rows,key=lambda r:json.dumps(r,sort_keys=True))
        return {'sha256':sha(objpath),'RELA':len(e.relocations),'instruction_boundaries_inspected':boundaries,'owners':owners,'symbol_definitions':ordered(definitions),'incoming_RELA':ordered(references),'incoming_RELA_type_counts':dict(sorted(collections.Counter(str(r['type']) for r in references).items())),'admitted_direct_targets':ordered(direct),'unresolved_RELA':ordered(unresolved),'absence_of_other_computed_targets_proved':False}
    old=inspect(original,8280);current=None
    if integrated or receipt:
        need(integrated is not None and receipt is not None,'Integrated object and actual receipt are a pair')
        r=read(receipt);need(r['passed'] and r['checks']['merged']['RELA']==8276,'Existing partial IRQ integration receipt')
        pin=r['artifacts']['source-integrated.o'];need(sha(integrated)==pin['sha256'] and integrated.stat().st_size==pin['bytes'],'Actual integrated object pinned by receipt')
        current=inspect(integrated,8276)
        need(old['owners']==current['owners'] and old['symbol_definitions']==current['symbol_definitions'] and old['incoming_RELA']==current['incoming_RELA'] and old['admitted_direct_targets']==current['admitted_direct_targets'],'Flash ownership/definitions/references unchanged across prior IRQ integration')
    return {'schema':'ID2966-flash-entry-order-original-source-v1','passed':True,'firmware_sha256':FW,'layout_sha256':LAYOUT,'source_seal_sha256':'dff9a51e3b59bbdddd150dde37614753bb3c3b440d7bde2f9402c8b6e9a2bce4','full_original_source_bytes':262,'full_original_instructions':99,'tail_raw':raw[0x18f50-0x8000:0x18f56-0x8000].hex(),'tail_rows':tail,'tail_semantic_controls':negative,'early_alignment_row':decoder.decode(raw,0x18efa),'original_carrier':old,'prior_partial_IRQ_integrated_carrier':current,'no_padding_or_free_tail_claim':True,'target_execution':False,'ISA_emulation':False,'network':False,'hardware':False,'new_BIN':False,'OTA_ready':False}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',type=Path,required=True);p.add_argument('--firmware',type=Path,required=True);p.add_argument('--original-object',type=Path,required=True);p.add_argument('--layout',type=Path,required=True);p.add_argument('--integrated-object',type=Path);p.add_argument('--integrated-receipt',type=Path);p.add_argument('--output',type=Path);p.add_argument('--reference',type=Path);a=p.parse_args()
    r=analyze(a.project_root.resolve(strict=True),a.firmware,a.original_object,a.layout,a.integrated_object,a.integrated_receipt)
    if a.reference:need(r==read(a.reference),'Exact bound source/reference inventory')
    if a.output:
        output=a.output.resolve();output.relative_to(Path(__file__).resolve().parent);need(not output.exists(),'Create-only own source inventory');output.write_bytes((json.dumps(r,indent=2)+'\n').encode('utf-8'))
    print(json.dumps({'passed':True,'tail':r['tail_raw'],'original_RELA':8280,'integrated_RELA':8276 if r['prior_partial_IRQ_integrated_carrier'] else None,'Flash_RELA_refs':len(r['original_carrier']['incoming_RELA']),'Flash_direct_refs':len(r['original_carrier']['admitted_direct_targets']),'target_execution':False}))
if __name__=='__main__':main()
