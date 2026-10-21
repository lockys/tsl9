#!/usr/bin/env python3
"""Independent actual12-owner ELF/image review; no target execution or generation."""
from pathlib import Path
import argparse,copy,hashlib,json,runpy,struct,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
BASELINE='c663758a99ff3a10249b9baa11c511826a14cbd239243a0ca4e1b4b540283fdd'
MANIFEST='09bfe0613a88a395b048a397530f62e49b199e890c3d2fc04285ca44887915fe'
OLD='de1a55014e3db06fc909cadd92a746c9922b08bcdecfa0bcb28862f98d1f9ca0'
PARSER='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
FW='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
MODEL='experiments/tsl9-v4160-reply-image-integration'
IMAGE='NOT-FLASH-VALIDATED-reply-integrated.bin'
REPLY='.text.tsl9v4160.ota_handler_9b8e'
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def H(raw):return hashlib.sha256(raw).hexdigest()
def read(p):return json.loads(p.read_bytes())
def case(root,slug):return next(p for p in (root/'apk-analysis'/('tsl9-'+slug),root/'analysis'/slug) if p.is_dir())
def pinned(path,pin):need(sha(path)==pin,'Pinned independent dependency '+path.name);return runpy.run_path(str(path))
def context(root,firmware):
    b=HERE/'baseline.json';need(sha(b)==BASELINE,'Portable independent source-role baseline');baseline=read(b);m=case(root,'v4160-reply-image-integration-2026-10-22')/'image-plan/source-manifest.json';need(sha(m)==MANIFEST,'Frozen actual sourceplan');manifest=read(m);old=pinned(case(root,'v4160-flash-image-integration-2026-10-22')/'ABI-review/review.py',OLD);ELF=pinned(case(root,'v4160-irq-native-2026-10-21')/'compiler-review/elf32.py',PARSER)['ELF'];need(sha(firmware)==FW and firmware.stat().st_size==76800,'Pinned original source firmware')
    selected={r['name']:r for r in manifest['selected_sections']};need(len(selected)==12 and sum(x['bytes'] for x in selected.values())==650,'Twelve typed650-byte extents');return dict(root=root,baseline=baseline,manifest=manifest,old=old,ELF=ELF,original=firmware.read_bytes(),selected=selected)
def address_significance(merged,linked,provider,prefix_sha256='d5602214c38b22935e3ca6f19485c27a1fb60d011c5e27eaec2941238f32fa9d'):
    name='.llvm_addrsig';sig=provider.byname[name];raw=provider.data(sig);need((sig['type'],sig['flags'],sig['address'],sig['info'],sig['alignment'],sig['entry_size'])==(0x6fff4c03,0x80000000,0,0,1,0),'Actual native excluded address-significance attributes');need(len(raw)==1 and not raw[0]&128 and sig['link'] in provider.symbol_tables,'One actual native address-significance symbol');symbol=provider.symbol_tables[sig['link']][raw[0]];need(0<symbol['index']<len(provider.sections) and provider.sections[symbol['index']]['name']=='.text.tsl9_ota_page_reply_9b8e' and (symbol['name'],symbol['value'],symbol['size'],symbol['info'],symbol['other'])==('tsl9_ota_page_reply_9b8e',0,124,18,0),'Actual native address-significance FUNC124 role');current=merged.byname[name];payload=merged.data(current);need((current['type'],current['flags'],current['address'],current['link'],current['info'],current['alignment'],current['entry_size'])==(0x6fff4c03,0x80000000,0,0,0,1,0),'Explicit excluded concatenated address-significance metadata');need(len(payload)==57 and payload.endswith(raw) and H(payload[:-len(raw)])==prefix_sha256,'Only exact actual newnative payload appended to56B prior metadata');need(name not in linked.byname,'Excluded address-significance metadata omitted from linked witness');return dict(prior_bytes=56,new_provider_bytes=1,merged_bytes=57,prior_payload_sha256=prefix_sha256,new_provider_hex=raw.hex(),provider_significant_symbol=symbol['name'],merged_link_field_zero=True,discarded_at_final_link=True)
def roles(merged,linked,c):
    o=c['old'];b=c['baseline'];selected=c['selected'];expected=b['sections'];need(merged.kind==1 and linked.kind==2 and merged.flags==linked.flags==1,'Actual RVC ET_REL/EXEC pair');need(len(merged.byname)==len(merged.sections) and len(linked.byname)==len(linked.sections),'Unique actual section names');ma=o['alloc'](merged);la=o['alloc'](linked);need(set(ma)==set(la)==set(expected) and len(ma)==691,'All691 original allocation owners')
    for name,ref in expected.items():
        a=ma[name];l=la[name];need(all(a[k]==ref[k] for k in ('type','flags','size','alignment','entry_size','address')),'Exact partial owner attributes '+name);need(l['address']==ref['originalVA'] and all(l[k]==ref[k] for k in ('type','flags','size','alignment','entry_size')),'Exact fixed linked owner attributes '+name)
        if name not in selected:need(H(o['data'](merged,a))==ref['merged_sha256'] and H(o['data'](linked,l))==ref['linked_sha256'],'All679 retained owner byte identities '+name)
    for name,pin in b['nonempty_unallocated_data_sha256'].items():
        if name=='.llvm_addrsig':
            address_significance(merged,linked,c['reply_provider'],pin)
        else:need(name in merged.byname and H(merged.data(merged.byname[name]))==pin,'Unallocated compiler metadata payload '+name)
    outside=[o['relocation'](merged,r) for r in merged.relocations if r['owner'] not in selected];need(len(outside)==8257 and H(o['canonical'](sorted(outside,key=lambda r:json.dumps(r,sort_keys=True))).encode())==b['outside_RELA_semantic_sha256'],'All8257 outside actual RELA roles');owned=[o['relocation'](merged,r) for r in merged.relocations if r['owner'] in selected];need(o['count'](owned)==o['count'](b['owned_JAL_RELA']) and len(merged.relocations)==8269,'Exactly12 actual typed JAL RELAs/8269total');need(not linked.relocations,'No linked unresolved relocation')
    globals=o['count'](o['role'](merged,s) for s in merged.symbols if s['name'] and s['info']>>4 in (1,2));need(o['counter_digest'](globals)==b['expected_global_role_digest'],'Exact all global/weak roles, including oldNOTYPE0 and separateFUNC124');locals=o['count'](r for r in o['regular_roles'](merged) if r['info']>>4==0);need(o['counter_digest'](locals)==b['expected_local_role_digest'],'Exact local/SECTION roles after one new private discharge');need(not any(s['name'] in b['discharged_private_names'] for s in merged.symbols),'All11 private labels discharged, no ABS substitutions')
    for binding in b['canonical_bindings']:need(o['count'](o['role'](merged,s) for s in merged.symbols if s['name']==binding['name'])==o['count']([binding['role']]),'Exact53 canonical section-relative bindings')
    meta=o['metadata_counter'](merged);need(meta==o['Counter'](b['expected_metadata']),'Exact compiler metadata: one newFILE/comment/ABSd and replyd→x')
    linkedroles=o['count'](o['regular_roles'](linked,True));wanted=[]
    for r in o['regular_roles'](merged,True):
        r=dict(r)
        if r['owner']=='UND':need(r['name']=='__tsl9v4160_rom_entry','Sole unknown residentROM exterior');r.update(owner='ABS',offset=0x40000)
        wanted.append(r)
    need(o['count'](wanted)==linkedroles,'Every named linked nonmetadata role exact, including numericROM witness');key=o['canonical'](dict(name='$d',owner='.comment',offset=0,bytes=0,info=0,other=0));need(meta[key]==43,'43 actual TU comment mappings');meta[key]-=43;need(+meta==o['metadata_counter'](linked),'Only43 comment mappings dropped at final link')
    reply=next(s for s in merged.symbols if s['name']=='__tsl9v4160_ota_code_9b8e');local=next(s for s in merged.symbols if s['name']=='.Lota_handler_00009b8e');need(o['role'](merged,reply)==dict(name=reply['name'],owner=REPLY,offset=0,bytes=0,info=16,other=0) and o['role'](merged,local)==dict(name=local['name'],owner=REPLY,offset=0,bytes=0,info=0,other=0),'Original reply publicNOTYPE0/localentry0 preserved')
    return dict(allocations=691,retained_storage=679,outside_RELA=8257,total_RELA=8269,owned_JAL_RELA=12,canonical_bindings=53,all_global_local_SECTION_roles_verified=True,reply_NOTYPE0_local0_preserved=True,reply_new_public_FUNC124_separate=True,metadata_TU_count=43,address_significance=address_significance(merged,linked,c['reply_provider']))
def boundaries(body,base):
    result=set();i=0
    while i<len(body):result.add(base+i);width=4 if int.from_bytes(body[i:i+2],'little')&3==3 else 2;need(i+width<=len(body),'Whole actual instruction width');i+=width
    return result
def branch(body,offset,base):
    h=int.from_bytes(body[offset:offset+2],'little');pc=base+offset
    if h&3!=3:
        need(h&3==1 and h>>13 in (6,7),'Actual compressed conditional branch');imm=(((h>>12)&1)<<8)|(((h>>10)&3)<<3)|(((h>>5)&3)<<6)|(((h>>3)&3)<<1)|(((h>>2)&1)<<5);imm=imm-512 if imm&256 else imm;return dict(site=pc,bytes=2,rs1=8+((h>>7)&7),rs2=0,condition='eq' if h>>13==6 else 'ne',target=pc+imm)
    w=int.from_bytes(body[offset:offset+4],'little');need(w&127==0x63 and (w>>12)&7 in (0,1),'Actual32-bitBEQ/BNE');imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1);imm=imm-8192 if imm&4096 else imm;return dict(site=pc,bytes=4,rs1=(w>>15)&31,rs2=(w>>20)&31,condition='eq' if (w>>12)&7==0 else 'ne',target=pc+imm)
def machine(merged,linked,c):
    o=c['old'];selected=c['selected'];functions=[];allbounds={}
    for owner,a in selected.items():
        va=a['originalVA'];body=o['data'](linked,linked.byname[owner]);source=c['original'][va-0x8000:va-0x8000+a['bytes']];need(body==source,'All650 typed linked bytes exact original '+owner);syms=[s for s in linked.symbols if s['name']==a['new_C_symbol']];need(len(syms)==1 and (syms[0]['value'],syms[0]['size'],syms[0]['info'],syms[0]['other'])==(va,a['bytes'],18,0),'Actual separate typed FUNC entry/extent');allbounds[owner]=boundaries(body,va);functions.append(dict(name=a['new_C_symbol'],owner=owner,address=va,bytes=len(body),sha256=H(body),original_instruction_identity=True))
    calls=[]
    for rel in (r for r in merged.relocations if r['owner'] in selected):
        a=selected[rel['owner']];target=o['role'](merged,rel['symbol']);need(target['owner'] in c['baseline']['sections'] and target['offset']==0,'Actual section-relative canonical JAL target');va=c['baseline']['sections'][target['owner']]['originalVA'];call=o['direct_jump'](o['data'](linked,linked.byname[rel['owner']]),rel['offset'],a['originalVA']);need(call['bytes']==4 and call['rd']==1 and call['target']==va and call['link'] in allbounds[rel['owner']],'Actual typedJAL RA/target/continuation');calls.append(call)
    need(len(calls)==12,'Twelve typed JAL sites');reply=next(r for r in calls if r['site']==0x9be0);need((reply['target'],reply['link'])==(0x8a56,0x9be4),'ReplyTX external retained8A56/RA9BE4')
    branches=[]
    for r in c['manifest']['old_selected_RELA']:
        if r['type'] not in (16,44):continue
        a=selected[r['owner']];body=o['data'](linked,linked.byname[r['owner']]);observed=branch(body,r['offset'],a['originalVA']);need(observed['target']==a['originalVA']+r['symbol']['offset'],'Discharged actual branch target preserved');raw=bytes.fromhex(r['original_branch_bytes']);need(body[r['offset']:r['offset']+len(raw)]==raw,'Discharged branch exact original raw word');branches.append(observed)
    need(len(branches)==11,'Eleven actual decoded branch discharges');incoming=[]
    for expected in c['baseline']['incoming']:
        owner=next(n for n,s in c['baseline']['sections'].items() if s['originalVA']<=expected['site']<s['originalVA']+s['size']);base=c['baseline']['sections'][owner]['originalVA'];jump=o['direct_jump'](o['data'](linked,linked.byname[owner]),expected['site']-base,base);need(jump==expected,'All21 incoming actualwidth/rd/target/RA contracts');incoming.append(jump)
    incoming_reply=next(r for r in incoming if r['site']==0x9df4);need((incoming_reply['rd'],incoming_reply['target'],incoming_reply['link'],incoming_reply['raw_hex'])==(1,0x9b8e,0x9df6,'693b'),'Corrected incoming RV32C.JAL, not tail')
    return dict(functions=functions,typed_JALs=sorted(calls,key=lambda r:r['site']),branch_discharges=branches,incoming=incoming,reply_free_tail_PC=0x9bf8,reply_entry_call_links_RA=True,all650_typed_instruction_bytes_original=True,hardware_or_OTA_admitted=False)
def image(linked,payload,c):
    need(len(payload)==76800 and payload==c['old']['scatter'](linked,c)==c['original'],'All76800 exported bytes equal linked690owner scatter and original, no holes/padding');need(struct.unpack_from('<I',linked.raw,24)[0]==0x8000,'Original image entry8000');return dict(bytes=76800,sha256=H(payload),differences_from_original=0,file_backed_owners=690,hardware_or_OTA_admitted=False)
def passes(root,folder,pre,post,c):
    o=c['old'];frame_path=root/'experiments/tsl9-v4160-frame-schedule/schedule.py';frame=pinned(frame_path,'dc680558aca230a54e1fc05f68960f85f4566b0928787caef21839cdd876535d');policy=read(frame_path.with_name('frame-policy.json'));need(sha(frame_path.with_name('frame-policy.json'))=='2af7789f91ceabca11fc29eb264991b96f40664555cdfe08964284f1470a694d','Frozen frame policy');payload,proof,changes=frame['plan'](pre,policy,['irq','quarter']);need(payload==post.raw and len(changes)==14,'Actual merged framepass changes14bytes only');need(pre.sections==post.sections and pre.symbols==post.symbols and pre.relocations==post.relocations,'All framepass metadata exact');receipt=read(folder/'frame-scheduling.json')
    expected=dict(schema='TSL9-explicit-ABI-frame-scheduling-receipt-v1',passed=True,tool_sha256=sha(frame_path),policy_sha256=sha(frame_path.with_name('frame-policy.json')),parser_sha256=PARSER,input=dict(path=(folder/'pre-frame-integrated.o').relative_to(root).as_posix(),bytes=len(pre.raw),sha256=H(pre.raw)),output=dict(path=(folder/'source-integrated.o').relative_to(root).as_posix(),bytes=len(post.raw),sha256=H(post.raw)),functions=proof,changed_file_offsets=changes,section_metadata_symbols_RELA_identical=True,original_BIN_read_for_generation=False,new_opcodes_generated=False,padding_added=False,pipeline='C/C++ compiler output followed by explicit source-owned ABI frame scheduling',compiler_alone_emitted_scheduled_order=False,computed_interior_entries_proved_absent=False,target_execution=False,ISA_emulation=False,hardware=False,OTA_ready=False);need(receipt==expected,'Exact actual framepass provenance receipt, policy, paths, limits and flags')
    reply_path=root/'experiments/tsl9-v4160-reply-abi-order/order.py';reply=pinned(reply_path,'6e8a137297c7aa7e7cfa1153a7b46ee061269d3912b72180e941c2c942448776');r=reply['replay'](root,folder/'reply-order.json');need(len(r['proof']['changed_file_offsets'])==28,'Actual standalone reply order changes28bytes');raw=c['ELF'](folder/'reply.o');ordered=c['ELF'](folder/'reply-ordered.o');symbol=next(s for s in ordered.symbols if s['name']=='tsl9_ota_page_reply_9b8e');need(ordered.function_bytes(symbol)==o['data'](pre,pre.byname[REPLY]),'Actual ordered reply is actual merged source body');need(r['input']['sha256']==H(raw.raw) and r['output']['sha256']==H(ordered.raw),'Exact standalone reply pre/post association')
    return dict(frame_changed_bytes=14,reply_changed_bytes=28,frame_compiler_sha256=H(pre.raw),frame_scheduled_sha256=H(post.raw),reply_compiler_sha256=H(raw.raw),reply_ordered_sha256=H(ordered.raw),compiler_alone_emitted_final_order=False,new_opcode_or_original_BIN_generation_input=False)
def verify(pre,post,linked,payload,c):return dict(roles=roles(post,linked,c),machine=machine(post,linked,c),LOAD=c['old']['program_headers'](linked),image=image(linked,payload,c))
def controls(pre,post,linked,payload,c):
    out=[];o=c['old'];E=c['ELF']
    def reject(name,kind,raw,gate):
        try:gate()
        except (ValueError,KeyError,IndexError,struct.error) as error:out.append(dict(name=name,kind=kind,mutated_sha256=H(raw),rejected=True,reason=str(error)));return
        raise ValueError('Independent actual artifact negative admitted: '+name)
    p=bytearray(linked.raw);caller=next(n for n,s in c['baseline']['sections'].items() if s['originalVA']==0x9c4a);at=linked.byname[caller]['offset']+426;h=int.from_bytes(p[at:at+2],'little');p[at:at+2]=(h^0x8000).to_bytes(2,'little');m=E(o['BytesInput'](bytes(p)));reject('incomingC.JAL_changed_to_no_linkC.J','actual linkedELF',bytes(p),lambda:machine(post,m,c))
    p=bytearray(linked.raw);at=linked.byname[REPLY]['offset']+0x52;w=struct.unpack_from('<I',p,at)[0];struct.pack_into('<I',p,at,w&~(31<<7));m=E(o['BytesInput'](bytes(p)));reject('replyTX_JAL_does_not_linkRA','actual linkedELF',bytes(p),lambda:machine(post,m,c))
    p=bytearray(post.raw);at=o['symbol_offset'](post,lambda s:s['name']=='__tsl9v4160_ota_code_9b8e');p[at+12]=18;struct.pack_into('<I',p,at+8,124);m=E(o['BytesInput'](bytes(p)));reject('oldNOTYPE0_fabricated_FUNC124','actual partialELF',bytes(p),lambda:roles(m,linked,c))
    p=bytearray(linked.raw);offset=struct.unpack_from('<I',p,28)[0];size,n=struct.unpack_from('<HH',p,42);at=next(offset+i*size for i in range(n) if struct.unpack_from('<I',p,offset+i*size)[0]==1);flags=struct.unpack_from('<I',p,at+24)[0];struct.pack_into('<I',p,at+24,flags^2);m=E(o['BytesInput'](bytes(p)));reject('LOAD_permissions_changed','actual linkedELF',bytes(p),lambda:o['program_headers'](m))
    p=bytearray(post.raw);sig=post.byname['.llvm_addrsig'];p[sig['offset']+sig['size']-1]^=1;m=E(o['BytesInput'](bytes(p)));reject('wrong_appended_address_significance_payload','actual partialELF',bytes(p),lambda:address_significance(m,linked,c['reply_provider']))
    p=bytes([payload[0]^1])+payload[1:];reject('one_exported_image_byte','actualBIN',p,lambda:image(linked,p,c));return out
def inspect(root,folder,firmware):
    c=context(root,firmware);E=c['ELF'];c['reply_provider']=E(folder/'reply-ordered.o');pre=E(folder/'pre-frame-integrated.o');post=E(folder/'source-integrated.o');linked=E(folder/'ADDRESS-WITNESS-ONLY.elf');payload=(folder/IMAGE).read_bytes();r=read(folder/'verification.json');result=verify(pre,post,linked,payload,c);result['scheduling']=passes(root,folder,pre,post,c);result['negative_controls']=controls(pre,post,linked,payload,c);return dict(schema='TSL9-twelve-image-independent-ABI-v1',passed=True,mode=r['mode'],actual_build_artifact_replay=True,actual_original_firmware_read=True,actual_folder=folder.relative_to(root).as_posix(),source_plan_sha256=MANIFEST,independent_baseline_sha256=BASELINE,producer_receipt_sha256=sha(folder/'verification.json'),artifacts={n:dict(bytes=(folder/n).stat().st_size,sha256=sha(folder/n)) for n in ('pre-frame-integrated.o','source-integrated.o','ADDRESS-WITNESS-ONLY.elf',IMAGE,'frame-scheduling.json','reply.o','reply-ordered.o','reply-order.json')},checks=result,target_execution=False,ISA_emulation=False,network=False,hardware_OTA_proved=False)
def metadata():
    seal=read(HERE/'seal.json');need(seal['schema']=='TSL9-twelve-image-independent-ABI-seal-v1','Known metadata-only seal')
    for f in seal['files']:
        p=(HERE/f['path']).resolve();need(p.is_relative_to(HERE) and p.stat().st_size==f['bytes'] and sha(p)==f['sha256'],'Unchanged source/metadata seal member')
    return dict(passed=True,mode='metadata-only',actual_build_artifact_replay=False,members=len(seal['files']))
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=HERE.parents[2]);p.add_argument('--firmware',type=Path);p.add_argument('--folder',type=Path);p.add_argument('--receipt',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
    if a.replay:
        need(a.firmware is not None and a.folder is None and a.receipt is None,'Explicit originalFW and readonly report replay');old=read(a.replay);r=inspect(root,root/old['actual_folder'],a.firmware.resolve());need(r==old,'Exact actual independent report replay')
    elif a.folder:
        need(a.firmware is not None and a.receipt is not None and not a.receipt.exists(),'Actual folder requires explicit originalFW and new receipt');r=inspect(root,a.folder.resolve(),a.firmware.resolve());a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode())
    else:need(a.firmware is None and a.receipt is None,'Default checks metadata only');r=metadata()
    print(json.dumps(dict(passed=True,mode=r['mode'],actual_build_artifact_replay=r.get('mode')!='metadata-only',hardware_OTA_proved=False)))
if __name__=='__main__':main()
