"""Independent bounded source/ELF role audit. No instruction execution."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
OWNER='.text.tsl9v4160.code_continuation_8a56'
PUBLIC='__tsl9v4160_call_8a56'
FW='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
PARSER='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
RAW='da17e505ec2b58cada40a80a12a645b7fa21c116ce76666544168f2c4ff6c6a7'
BASE='5e7695221b39aca03e9cdf3a8478597d78a401cc1bcfaa609c5343df4d526d31'

def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def load(n,p):
    spec=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def case(root,n):return next(p for p in (root/'analysis'/n,root/'apk-analysis'/('tsl9-'+n)) if p.is_dir())
def context(root):
    root=Path(root).resolve(strict=True);p=case(root,'v4160-irq-native-2026-10-21')/'compiler-review/elf32.py';q=case(root,'v4160-ota-tx-2026-10-22')/'source-review/raw.py'
    need(sha(p)==PARSER and sha(q)==RAW,'Immutable bounded parsers');return root,load('thirteen_roles_elf',p).ELF,load('thirteen_roles_raw',q).decode
def role(e,s,project=False):
    index=s['index'];owner=e.sections[index]['name'] if 0<index<len(e.sections) else 'ABS' if index==65521 else 'UND' if index==0 else str(index)
    return dict(name=s['name'],owner=owner,offset=s['value']-(e.sections[index]['address'] if e.kind==2 and 0<index<len(e.sections) else 0),bytes=8 if project and s['name']==PUBLIC else s['size'],info=s['info'],other=s['other'])
def relas(e,project=False):
    return sorted([dict(owner=r['owner'],offset=r['offset'],type=r['type'],addend=r['addend'],symbol=role(e,r['symbol'],project)) for r in e.relocations],key=lambda x:json.dumps(x,sort_keys=True))
def incoming(e):return [r for r in relas(e,True) if r['owner']!=OWNER and r['symbol']['owner']==OWNER]
def slice_at(e,owner,offset):return e.data(e.byname[owner])[offset:offset+4]
def link_records(e,allocations,decode,records=None):
    rows=[]
    for r in incoming(e) if records is None else records:
        pc=allocations[r['owner']]['originalVA']+r['offset'];d=decode(slice_at(e,r['owner'],r['offset']),pc)
        need(d['op']=='jal' and d['rd'] in (0,1),'Actual incoming JAL/C.JAL width/link')
        rows.append(dict(PC=pc,owner=r['owner'],offset=r['offset'],type=r['type'],addend=r['addend'],bytes=d['bytes'],rd=d['rd'],link=pc+d['bytes'] if d['rd']==1 else None,target=d['target']))
    return sorted(rows,key=lambda r:r['PC'])
def snapshot(root):
    root,E,decode=context(root);base=root/'experiments/tsl9-v4160-reply-image-integration/build/formal-v1/c/source-integrated.o';need(sha(base)==BASE,'Exact baseline full twelve ET_REL');e=E(base)
    manifest=root/'experiments/tsl9-v4160-reply-image-integration/source-manifest.json';m=read(manifest);outside=[r for r in relas(e,True) if r['owner']!=OWNER]
    return dict(schema='ID2966-thirteen-image-source-role-reference-v1',baseline_object_sha256=BASE,baseline_manifest_sha256=sha(manifest),TX_owner=OWNER,original_TX_body_sha256=hashlib.sha256(e.data(e.byname[OWNER])).hexdigest(),original_owner_roles=sorted([role(e,s) for s in e.symbols if s['index']==e.byname[OWNER]['index']],key=lambda r:json.dumps(r,sort_keys=True)),original_owned_RELA=[r for r in relas(e) if r['owner']==OWNER],nonTX_RELA_count=len(outside),nonTX_RELA_projected_sha256=digest(outside),incoming_RELA=incoming(e),incoming_machine=link_records(e,m['allocations'],decode),allocations=m['allocations'],baseline_addrsig_hex=e.data(e.byname['.llvm_addrsig']).hex(),private_roles={'control_targets':[0x8b6c,0x8a96,0x8acc,0x8abe,0x8ace,0x8b0a,0x8b52],'PCREL_anchor':0x8ad6},original_BIN_codegen_input=False)
def metadata(root,firmware):
    root,E,decode=context(root);ref=read(HERE/'reference.json');need(sha(firmware)==FW and firmware.stat().st_size==76800,'Exact source reference firmware');body=firmware.read_bytes()[0xa56:0xb6e];need(hashlib.sha256(body).hexdigest()==ref['original_TX_body_sha256'],'VA8000 file mapping original TX280')
    need(ref['nonTX_RELA_count']==8258 and len(ref['incoming_RELA'])==9 and len(ref['original_owned_RELA'])==11,'Closed baseline counts')
    need(all(r['addend']==0 for r in ref['original_owned_RELA']) and sorted(r['type'] for r in ref['original_owned_RELA'])==[16]*8+[23,24,45],'Original eight standard branches/one compressed jump/HI+LO, all addend0')
    for row in ref['incoming_machine']:
        d=decode(firmware.read_bytes()[row['PC']-0x8000:row['PC']-0x8000+4],row['PC']);need((d['rd'],d['bytes'],d['target'])==(row['rd'],row['bytes'],0x8a56),'Original raw incoming target/rd/width')
    model=root/'experiments/tsl9-v4160-tx-image-integration';old=root/'experiments/tsl9-v4160-tx-register-abi';entry=(model/'adapter/entry.S').read_text(encoding='utf-8');oldentry=(old/'adapter/entry.S').read_text(encoding='utf-8')
    expected=oldentry.replace('/* Narrow returning entry adapter; all body logic is compiled typed C/C++. */','/* Source-owned narrow runtime entry: canonical resident symbol, real FUNC8. */').replace('tsl9_ota_tx_8a56',PUBLIC);need(entry==expected,'Exact source-owned entry rename only; no alias/encoder/raw code bytes')
    pins={'adapter/valid_body.c':'dd98bd9e6298f8c7d76e86744eea8b10ddceb81dce71d8b5bbb456f7fe7b6be0','adapter/return_leaf.c':'aac07d0d13ecf39b0c9773670e0bd6323e3624bff3e38ecac53685dccccb6732','src/tx_native.c':'6b32db73aff79b57174d3315198a339ceb41bbe653f1a88976abea3a9d049530','src/tx_io.h':'f3ba14c8adfe24d07f83338cbe82699c8668087fd3792cd5c6a2f6988671c7e7','src/tx_native.h':'5360c8c710bd57311fb92bc10f9880caf2881ad83604e9a567bdfb19f40d4db6'}
    for name,pin in pins.items():need(sha(old/name)==pin,'Exact immutable typed TX source '+name)
    return root,E,decode,ref
def gate(e,linked,ref,decode):
    need(e.kind==1 and linked.kind==2,'Actual ET_REL and linked ET_EXEC');section=e.byname[OWNER];need((section['size'],section['type'],section['flags'],section['alignment'])==(280,1,6,2),'Original TX allocation280 remains')
    expected=[('',0,0,3),('$x.0',0,0,0),('$x.0',8,0,0),('$x.0',278,0,0),('.Lpcrel_hi0',128,0,0),(PUBLIC,0,8,18),('tsl9_tx_oversized_return',278,2,18)]
    roles=[role(e,s) for s in e.symbols if s['index']==section['index']];bodies=[r for r in roles if r['name'] in ('tsl9_tx_valid_body','_ZL18tsl9_tx_valid_bodyjjjj')];need(len(bodies)==1 and (bodies[0]['offset'],bodies[0]['bytes'],bodies[0]['info'],bodies[0]['other'])==(8,270,2,0),'Real LOCAL typed body270')
    expected.append((bodies[0]['name'],8,270,2));need(sorted((r['name'],r['offset'],r['bytes'],r['info']) for r in roles)==sorted(expected) and all(r['other']==0 for r in roles),'Exactly eight honest TX owner roles')
    public=[s for s in e.symbols if s['name']==PUBLIC];need(len(public)==1 and public[0]['index']==section['index'],'One real section-defined canonical FUNC8, no numeric/ABS provider')
    outside=[r for r in relas(e) if r['owner']!=OWNER];need(len(outside)==8258 and digest(outside)==ref['nonTX_RELA_projected_sha256'],'All8258 nonTX RELA unchanged except explicit canonical size projection')
    owned=[r for r in relas(e) if r['owner']==OWNER];expect=[dict(owner=OWNER,offset=4,type=16,addend=0,symbol=next(r for r in roles if r['name']=='tsl9_tx_oversized_return')),dict(owner=OWNER,offset=132,type=24,addend=0,symbol=next(r for r in roles if r['name']=='.Lpcrel_hi0'))]
    ram=[s for s in e.symbols if s['name']=='__tsl9v4160_data_2000b18c'];need(len(ram)==1,'One genuine RAM role');rr=role(e,ram[0]);need((rr['owner'],rr['offset'],rr['bytes'],rr['info'],rr['other'])==('.bss.tsl9v4160.ram',29068,0,16,0),'Actual allocated RAM role; no ABS alias');expect.append(dict(owner=OWNER,offset=128,type=23,addend=0,symbol=rr));need(digest(owned)==digest(sorted(expect,key=lambda x:json.dumps(x,sort_keys=True))),'Exactly new branch + genuine HI/LO RELA all addend0')
    calls=link_records(linked,ref['allocations'],decode,ref['incoming_RELA']);expectcalls=copy.deepcopy(ref['incoming_machine'])
    for r in expectcalls:r['target']=0x8a56
    need(calls==expectcalls,'Nine actual final call targets/widths/rd/link including sole13EAC rd0')
    for r in link_records(e,ref['allocations'],decode):need({k:v for k,v in r.items() if k!='target'}=={k:v for k,v in next(x for x in expectcalls if x['PC']==r['PC']).items() if k!='target'},'ET_REL links do not assume relocated immediate already resolved')
    body=linked.data(linked.byname[OWNER]);need(decode(body,0x8a56)['rd']==15 and decode(body,0x8a56)['immediate']==1039,'Typed entry bound');d=decode(body[4:],0x8a5a);need((d['op'],d['rs1'],d['rs2'],d['target'])==('bltu',15,13,0x8b6c),'Entry guard before frame targets genuine returning leaf');ret=decode(body[278:],0x8b6c);need((ret['op'],ret['rd'],ret['rs1'])==('jalr',0,1),'Actual typed RET preserves A0 and uses live RA')
    return dict(passed=True,original_regions=13,real_provider_functions=15,TX_FUNC_sizes=[8,270,2],nonTX_RELA=8258,incoming=9,sole_unlinked_entry=0x13eac,new_TX_RELA=3,original_private_control_roles=7,original_private_PCREL_roles=1,whole_ABI_admitted=False)
def origins(folder,e,ref,E):
    names=['tx-entry.o','tx-valid_body-ordered.o','tx-return_leaf.o'];objects=[E(folder/n) for n in names];attrs=[]
    for obj in objects:attrs.append(sum(s['name'].startswith('$d') and 0<s['index']<len(obj.sections) and obj.sections[s['index']]['name']=='.riscv.attributes' for s in obj.symbols))
    need(attrs==[1,1,1],'Three actual provider attribute-marker origins, including assembler')
    payloads=[o.data(o.byname['.llvm_addrsig']) if '.llvm_addrsig' in o.byname else b'' for o in objects];need(payloads==[b'',b'\x02',b''],'Only typed body contributes one actual addrsig byte')
    need(e.data(e.byname['.llvm_addrsig'])==bytes.fromhex(ref['baseline_addrsig_hex'])+b'\x02','Exact baseline57 plus body metadata byte; not allocated code')
    return dict(attribute_marker_origins=attrs,addrsig_baseline_bytes=57,addrsig_added_bytes=1)
def actual(root,firmware,folder):
    root,E,decode,ref=metadata(root,firmware);folder=Path(folder).resolve(strict=True);e=E(folder/'source-integrated.o');linked=E(folder/'ADDRESS-WITNESS-ONLY.elf');result=gate(e,linked,ref,decode);result['actual_provider_metadata_origins']=origins(folder,e,ref,E);return result
