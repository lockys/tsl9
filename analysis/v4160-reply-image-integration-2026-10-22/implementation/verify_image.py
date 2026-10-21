"""Fresh C/C++ plus explicit source-owned ABI scheduling; no RV32 execution."""
import argparse,collections,hashlib,importlib.util,json,os,re,shlex,struct,sys,uuid
from pathlib import Path
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;MODEL='experiments/tsl9-v4160-reply-image-integration';ROM='__tsl9v4160_rom_entry';IMAGE='NOT-FLASH-VALIDATED-reply-integrated.bin'
MANIFEST_SHA='09bfe0613a88a395b048a397530f62e49b199e890c3d2fc04285ca44887915fe'
REPLY_OWNER='.text.tsl9v4160.ota_handler_9b8e';REPLY_NATIVE='.text.tsl9_ota_page_reply_9b8e'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,d):p.write_bytes((json.dumps(d,indent=2)+'\n').encode())
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def case(root,slug):return next(p for p in (root/'analysis'/slug,root/'apk-analysis'/('tsl9-'+slug)) if p.is_dir())
def context(root,firmware=None):
    root=Path(root).resolve();model=root/MODEL;need(sha(model/'source-manifest.json')==MANIFEST_SHA,'portable twelve-function source ledger');m=read(model/'source-manifest.json');need(sha(model/'original-image-layout.ld')==m['layout_sha256'],'original691 layout')
    old=case(root,'v4160-irq-image-integration-2026-10-21')/'integration/verify_image.py';need(sha(old)=='1929598ffc723937e8cd6bcafbe507fb5ff23f6d9541f00043bdadcb44f3455a','immutable generic storage helpers');V=module('eleven_original_layout_helpers',old);ctx=V.context(root)
    flash_path=case(root,'v4160-flash-register-prefix-2026-10-22')/'implementation/verify_native.py';need(sha(flash_path)=='832035fea10ca77b3f48631f368b2d7e7a9c4cfb3d3509a5585a63718bd79be8','frozen100B native compiler/checker');F=module('eleven_flash_native_helpers',flash_path);f=F.context(root,firmware)
    for n,pin in m['source_files'].items():need(sha(root/n)==pin,'pinned source/header '+n)
    plan=case(root,'v4160-flash-entry-order-2026-10-22')/'image-plan';need(sha(plan/'seal.json')==m['entry_order_plan_seal_sha256'],'sealed eleven-owner plan')
    for r in read(plan/'seal.json')['members']:need(sha(plan/r['path'])==r['sha256'],'plan member')
    scheduler=root/'experiments/tsl9-v4160-frame-schedule/schedule.py'
    for name,pin in m['frame_schedule_source_files'].items():need(sha(root/name)==pin,'pinned explicit scheduler source '+name)
    S=module('register_image_explicit_scheduling',scheduler)
    reply_path=case(root,'v4160-ota-page-reply-2026-10-22')/'implementation/verify_native.py';need(sha(reply_path)==m['reply_native_profile']['sha256'],'sealed readable reply profile/checker');R=module('twelve_reply_native',reply_path);reply=R.context(root)
    boundary_path=case(root,'v4160-ota-page-reply-2026-10-22')/'integration-plan/probe-boundary.py';need(sha(boundary_path)==m['reply_boundary_filter']['sha256'],'exact zero-byte reply boundary filter');B=module('twelve_reply_boundary_filter',boundary_path)
    for name,pin in m['reply_order_source_files'].items():need(sha(root/name)==pin,'pinned standalone reply ordering source')
    ctx.update(schedule=S,scheduler=scheduler,root=root,V=V,manifest=m,model=model,Flash=F,flash=f,Reply=R,reply=reply,Boundary=B,native_code_sha256={r['new_C_symbol']:r['native_object_sha256'] for r in m['selected_sections']},plan_retained=m['retained_storage'])
    return ctx
def units(ctx,mode):
    root=ctx['root'];rows=ctx['manifest']['selected_sections'];result=[]
    for label,name,main in [('main','interrupt_callframe.c',True),('helpers','rcc_helpers.c',False)]:result.append(dict(label=label,source=root/'experiments/tsl9-v4160-irq-callframe/src'/name,flags=ctx['CF'].profile_flags(ctx['cf'],mode,main),rows=[r for r in rows if r['family']=='IRQ' and (r['bytes']==144)==main]))
    for address,(name,limit,allowed) in ctx['flash']['profile'].NAMES.items():result.append(dict(label='flash-'+name,source=root/'experiments/tsl9-v4160-flash-register-prefix/src/flash_native.c',flags=ctx['flash']['profile'].flags(address,mode),rows=[r for r in rows if r['family']=='Flash' and r['originalVA']==address]))
    result.append(dict(label='reply',source=root/'experiments/tsl9-v4160-ota-page-reply/src/page_reply.c',flags=ctx['Reply'].flags(mode),rows=[r for r in rows if r['originalVA']==0x9b8e]))
    need(len(result)==9 and sum(len(x['rows']) for x in result)==12,'nine typed source units twelve functions');return result
def adapter(rows):
    text='#include <stdint.h>\n#ifdef __cplusplus\nextern "C" {\n#endif\n'
    for r in rows:
        n=r['new_C_symbol'];params='uint32_t a0,uint32_t a1,uint32_t a2' if r['originalVA']==0x9b8e else ('void' if r['originalVA']==0x9a42 else ('uint32_t a0,uint32_t a1' if r['family']=='IRQ' or r['originalVA'] in (0x9c0a,0x18ef2) else 'uint32_t a0'))
        text+='uint32_t '+n+'('+params+') __attribute__((section("'+r.get('typed_input_section',r['name'])+'"),used,noinline));\n'
        if r['originalVA']!=0x9b8e:text+='extern __typeof__('+n+') '+r['global_alias']+' __attribute__((alias("'+n+'")));\n'
    return text+'#ifdef __cplusplus\n}\n#endif\n'
def original_image(root,ctx,explicit=None):
    path,raw=ctx['CF'].original_image(root,ctx['cf'],explicit);need(sha(path)==ctx['manifest']['original_image_sha256'],'fixed original source image');return path,raw
def branch(raw,site):
    w=int.from_bytes(raw,'little');size=len(raw)
    def sx(v,n):return v-(1<<n) if v>>(n-1) else v
    if size==2:
        need(w&3==1 and w>>13 in (6,7),'RVC conditional branch encoding');imm=((w>>12)&1)<<8|((w>>10)&3)<<3|((w>>5)&3)<<6|((w>>3)&3)<<1|((w>>2)&1)<<5
        return dict(width=2,condition='eq' if w>>13==6 else 'ne',rs1=8+((w>>7)&7),rs2=0,target=site+sx(imm,9))
    need(size==4 and w&127==0x63 and (w>>12)&7 in (0,1),'RV32 conditional branch encoding');imm=((w>>31)&1)<<12|((w>>25)&63)<<5|((w>>8)&15)<<1|((w>>7)&1)<<11
    return dict(width=4,condition='eq' if ((w>>12)&7)==0 else 'ne',rs1=(w>>15)&31,rs2=(w>>20)&31,target=site+sx(imm,13))
def selected_gate(e,ctx):
    V=ctx['V'];m=ctx['manifest'];names={r.get('typed_input_section',r['name']) for r in m['selected_sections']};need(set(V.alloc(e))==names,'exact twelve typed input owner sections');expected=[]
    for r in m['selected_sections']:
        owner=r.get('typed_input_section',r['name']);s=e.byname[owner];need({k:s[k] for k in ('type','flags','size','alignment','entry_size')}==m['section_metadata'][r['name']],'original typed allocation metadata')
        need(hashlib.sha256(e.data(s)).hexdigest()==r['typed_provider_object_sha256'],'typed input function-body identity '+r['new_C_symbol'])
        for n in ([r['new_C_symbol']] if r['originalVA']==0x9b8e else [r['new_C_symbol'],r['global_alias']]):expected.append(dict(name=n,owner=owner,offset=0,bytes=r['bytes'],info=18,other=0))
    need(V.counter([r for r in V.globals_(e) if r['owner']!='UND'])==V.counter(expected),'exact eleven original FUNC aliases plus twelve public typed FUNCs')
    return dict(functions=12,bytes=650,original_FUNC_aliases=11,public_C_FUNCs=12,reply_original_NOTYPE_boundary_in_raw=True)
def branch_discharge(e,ctx):
    m=ctx['manifest'];V=ctx['V'];outside=[V.relocation(e,r) for r in e.relocations if r['owner'] not in {x['name'] for x in m['selected_sections']}];result=[]
    for r in m['old_selected_RELA']:
        if r['type'] not in (16,44):continue
        owner=next(x for x in m['selected_sections'] if x['name']==r['owner']);target=r['symbol'];need(target['owner']==r['owner'] and not r['addend'] and target['info']==target['bytes']==target['other']==0,'exact old private self-branch role')
        need(not any(x['symbol']['name']==target['name'] for x in outside),'no recorded outside branch-label references')
        old=bytes.fromhex(r['original_branch_bytes']);native=e.data(e.byname[r['owner']])[r['offset']:r['offset']+len(old)];a=branch(old,r['offset']);b=branch(native,r['offset'])
        need(a==b and old==native and a['target']==target['offset'] and a['width']==(2 if r['type']==44 else 4),'exact branch PC/type/target and zero-or-register condition role')
        need(not any(s['name']==target['name'] for s in e.symbols),'old private label is discharged, never numeric alias/provider')
        result.append(dict(original_RELA=r,original_branch_bytes=old.hex(),native_branch_bytes=native.hex(),original_decoded=a,native_decoded=b,recorded_outside_references=0,full_GPR_prefix_equivalence=False))
    need(len(result)==11 and sum('direct_closure' in r['original_RELA']['owner'] for r in result)==6 and sum(r['original_RELA']['owner']==REPLY_OWNER for r in result)==1,'four IRQ/six Flash/one reply private branch roles exactly discharged');return result
def merged_gate(e,ctx,scheduled=True):
    V=ctx['V'];m=ctx['manifest'];selected={r['name'] for r in m['selected_sections']};need(e.kind==1 and e.flags==1 and V.und(e)=={ROM},'partial RV32 RVC ELF and sole ROM UND');result=V.metadata_gate(e,ctx,m['allocations'])
    for n,proof in m['retained_storage'].items():need(hashlib.sha256(V.data(e,e.byname[n])).hexdigest()==proof['sha256'],'all679 original partial-storage digests')
    for r in m['selected_sections']:need(hashlib.sha256(e.data(e.byname[r['name']])).hexdigest()==r['native_object_sha256' if scheduled else 'typed_provider_object_sha256'],'all twelve typed partial function bodies')
    outside=[V.relocation(e,r) for r in e.relocations if r['owner'] not in selected];need(len(outside)==8257 and V.digest(sorted(outside,key=lambda x:json.dumps(x,sort_keys=True)))==m['retained_RELA_semantic_sha256'],'all8257 outside RELA roles/sites/types/addends/multiplicities')
    owned=[V.relocation(e,r) for r in e.relocations if r['owner'] in selected];wanted=[]
    for r in m['old_selected_RELA']:
        if r['type']!=17:continue
        r=json.loads(json.dumps(r));target=next((x for x in m['selected_sections'] if x['global_alias']==r['symbol']['name']),None)
        if target is not None:r['symbol']['name']=target['new_C_symbol']
        wanted.append(r)
    need(V.counter(owned)==V.counter(wanted) and len(owned)==12,'exact twelve source-site JALs, including retained TX FUNC, no branch RELA/hidden helpers')
    for b in m['section_relative_bindings']:need(V.counter([V.role(e,s) for s in e.symbols if s['name']==b['name']])==V.counter([b['role']]),'all53 canonical relative binding roles')
    discharge=branch_discharge(e,ctx);before,oldmeta=V.normalized_symbols(m['baseline_symbol_roles'],[r['original_RELA']['symbol'] for r in discharge]);after,newmeta=V.normalized_symbols([V.role(e,s) for s in e.symbols]);extra=[dict(name=r['new_C_symbol'],owner=r['name'],offset=0,bytes=r['bytes'],info=18,other=0) for r in m['selected_sections']]
    need(V.counter(after)==V.counter(before+extra),'every nonmetadata original role preserved except exact eleven discharged locals plus twelve new FUNCs')
    need(V.counter([r for r in oldmeta if r['info']&15==3])==V.counter([r for r in newmeta if r['info']&15==3]),'all original SECTION role metadata')
    def mapping(rows,owner=None,retained=False):return V.counter([{**r,'name':r['name'].split('.')[0]} for r in rows if re.fullmatch(r'\$[dx]\.\d+',r['name']) and (r['owner']==owner if owner else r['owner'] not in selected and r['owner'] not in ('ABS','.comment'))])
    need(mapping(oldmeta)==mapping(newmeta),'all retained allocated mapping roles modulo measured assembler ordinals')
    files=[dict(name=n,owner='ABS',offset=0,bytes=0,info=4,other=0) for n in ['interrupt_callframe.c','rcc_helpers.c']+['flash_native.c']*6+['page_reply.c']]
    need(V.counter([r for r in newmeta if r['info']&15==4])==V.counter([r for r in oldmeta if r['info']&15==4]+files),'34 retained plus eight actual typed FILE records')
    for owner in ('ABS','.comment'):
        expected=mapping(oldmeta,owner)+V.counter([dict(name='$d',owner=owner,offset=0,bytes=0,info=0,other=0)]*9);need(mapping(newmeta,owner)==expected,'exact measured nine typed nonstorage '+owner+' markers')
    maps=[r for r in newmeta if re.fullmatch(r'\$[dx]\.\d+',r['name']) and r['owner'] in selected];need(len(maps)==12 and all(r['name'].startswith('$x.') and r['offset']==r['bytes']==r['info']==r['other']==0 for r in maps),'one instruction mapping per typed section')
    need(not any(r['symbol']['index']==0xfff1 and r['symbol']['name'].startswith('$d.') for r in e.relocations),'metadata ABS mappings are never providers')
    incoming=[r for r in outside if r['symbol']['owner'] in selected];need(V.counter(incoming)==V.counter(m['external_incoming_RELA']) and len(incoming)==21 and all(r['symbol']['offset']==0 for r in incoming),'all twenty-one original incoming entry references')
    need(len(e.relocations)==len(outside)+len(owned),'measured full relocation partition')
    return dict(**result,retained_storage_sections=679,RELA=len(e.relocations),outside_RELA=len(outside),owned_RELA=len(owned),discharged_branches=discharge,canonical_relative_bindings=53,incoming_RELA=21,old_metadata=oldmeta,new_metadata=newmeta)
def image_gate(path,e,ctx,original):
    r=ctx['V'].image_gate(path,e,ctx,original)
    for item in ctx['manifest']['selected_sections']:need(e.data(e.byname[item['name']])==bytes.fromhex(item['native_linked_bytes']),'all twelve linked bodies exactly sealed linked native bytes')
    expected={};actual={};loads=[]
    for s in ctx['V'].alloc(e).values():
        permissions=4|(2 if s['flags']&1 else 0)|(1 if s['flags']&4 else 0)
        for address in range(s['address'],s['address']+s['size']):need(address not in expected,'no overlapping allocated memory');expected[address]=permissions
    phoff=struct.unpack_from('<I',e.raw,28)[0];stride,count=struct.unpack_from('<HH',e.raw,42)
    for i in range(count):
        typ,off,va,lma,filesz,memsz,flags,align=struct.unpack_from('<8I',e.raw,phoff+i*stride)
        if typ!=1:continue
        need(va==lma and filesz<=memsz<=len(expected) and flags in (4,5,6),'bounded LOAD memory/permission extent')
        for address in range(va,va+memsz):need(address not in actual and expected.get(address)==flags,'LOAD memory exactly assigned section permissions, no overlap/hidden tail');actual[address]=flags
        loads.append(dict(VA=va,LMA=lma,file_bytes=filesz,memory_bytes=memsz,permissions=flags,alignment=align))
    need(actual==expected,'all original allocated memory, including RAM, mapped exactly once')
    r.update(differences_from_previous_IRQ_image=ctx['manifest']['differences_from_previous_IRQ_image'],LOAD_memory_coverage=loads,LOAD_mapped_memory_bytes=len(actual),extra_mapped_memory_bytes=0,actual_direct_call_frontiers=jump_gate(e,ctx));return r

def jump_fields(raw,pc):
    w=int.from_bytes(raw,'little');size=len(raw)
    def sx(v,n):return v-(1<<n) if v>>(n-1) else v
    if size==2:
        need(w&3==1 and w>>13 in (1,5),'actual RVC JAL/J encoding, no relocation-type inference');imm=((w>>12)&1)<<11|((w>>11)&1)<<4|((w>>9)&3)<<8|((w>>8)&1)<<10|((w>>7)&1)<<6|((w>>6)&1)<<7|((w>>3)&7)<<1|((w>>2)&1)<<5;rd=1 if w>>13==1 else 0;target=pc+sx(imm,12)
    else:
        need(size==4 and w&127==0x6f,'actual RV32 JAL opcode');imm=((w>>31)&1)<<20|((w>>21)&1023)<<1|((w>>20)&1)<<11|((w>>12)&255)<<12;rd=(w>>7)&31;target=pc+sx(imm,21)
    need(rd in (0,1),'source direct calls/tails only write RA or no link');return dict(width=size,rd=rd,target=target,return_link=pc+size if rd==1 else None,raw_hex=raw.hex())

def jump_gate(e,ctx):
    m=ctx['manifest'];result={}
    for family,records in [('incoming',m['external_incoming_RELA']),('owned',[r for r in m['old_selected_RELA'] if r['type']==17])]:
        rows=[]
        for r in records:
            source=e.byname[r['owner']];pc=source['address']+r['offset'];body=e.data(source);offset=r['offset'];size=4 if body[offset]&3==3 else 2;actual=jump_fields(body[offset:offset+size],pc);target=m['allocations'][r['symbol']['owner']]['originalVA']+r['symbol']['offset']+r['addend'];need(actual['target']==target,'actual encoded call target agrees with original semantic RELA role');rows.append(dict(PC=pc,source_RELA=r,**actual))
        result[family]=rows
    need(len(result['incoming'])==21 and len(result['owned'])==12,'actual21 incoming and12 owned encoded jump frontiers');reply=[r for r in result['incoming'] if r['PC']==0x9df4];need(len(reply)==1 and (reply[0]['width'],reply[0]['rd'],reply[0]['target'],reply[0]['return_link'])==(2,1,0x9b8e,0x9df6),'actual9DF4 is C.JAL RA9DF6, not a no-link tail jump');return result

def linked_gate(e,ctx):
    V=ctx['V'];m=ctx['manifest'];need(e.kind==2 and e.flags==1 and not e.relocations and not V.und(e),'fully resolved numeric witness only');result=V.metadata_gate(e,ctx,m['allocations'],True);need(struct.unpack_from('<I',e.raw,24)[0]==0x8000,'original image entry')
    for r in m['selected_sections']:
        for name,info,size in [(r['new_C_symbol'],18,r['bytes']),(r['global_alias'],r.get('original_global_alias_info',18),r.get('original_global_alias_bytes',r['bytes']))]:
            wanted=dict(name=name,owner=r['name'],offset=0,bytes=size,info=info,other=0);need(V.counter([V.role(e,s,True) for s in e.symbols if s['name']==name])==V.counter([wanted]),'real original boundary and typed FUNC role')
    for b in m['section_relative_bindings']:need(V.counter([V.role(e,s,True) for s in e.symbols if s['name']==b['name']])==V.counter([b['role']]),'all linked canonical relative roles')
    original_globals=[x for x in m['baseline_symbol_roles'] if x['name'] and x['info']>>4 in (1,2) and x['owner']!='UND'];extras=[dict(name=r['new_C_symbol'],owner=r['name'],offset=0,bytes=r['bytes'],info=18,other=0) for r in m['selected_sections']];rom=dict(name=ROM,owner='ABS',offset=0x40000,bytes=0,info=16,other=0)
    need(V.counter(V.globals_(e,True))==V.counter(original_globals+extras+[rom]),'all original globals, twelve real C FUNCs, numeric ROM only');return result

def bindings_source(ctx):
    text=ctx['V'].bindings_source(ctx['manifest']);old='  KEEP(*('+REPLY_OWNER+'))\n';need(text.count(old)==1,'one original reply output owner');return text.replace(old,old+'  KEEP(*('+REPLY_NATIVE+'))\n')

def filtered_source(ctx,original,groups):
    return ctx['Boundary'].filter_source(original) if REPLY_OWNER in groups else ctx['V'].filtered_source(original,groups)

def reply_gate(folder,ctx,receipt=None):
    R=ctx['Reply'];c=ctx['reply'];raw=c['a'].object_contract(c['decoder'],c['elf'],folder/'reply.o',c['original']);ordered=c['a'].object_contract(c['decoder'],c['elf'],folder/'reply-ordered.o',c['original'],True);ir=c['a'].ir_contract((folder/'reply.ll').read_text());r=c['schedule'].replay(ctx['root'],receipt or folder/'reply-order.json');need(len(r['proof']['changed_file_offsets'])==28,'only28 declared standalone ABI-order bytes')
    return dict(compiler_component=raw,ordered_component=ordered,IR=ir,ABI_order_receipt=r,compiler_alone_final_order=False,unknown_resident_ABI_proved=False)

def resource_gate(folder,ctx):
    text=(folder/'compiler-resource-dir.log').read_text().strip();need(len(text.splitlines())==1,'one actual Clang resource-directory result');directory=Path(text).resolve();need(directory.is_dir(),'actual compiler resource directory');pins={}
    for row in ctx['manifest']['compiler_resource_header_inputs']:
        p=(directory/row['resource_relative']).resolve();need(p.is_relative_to(directory) and sha(p)==row['sha256'],'actual resource-relative compiler header identity');pins[str(p)]=row['sha256']
    ctx['resource_headers']=pins;ctx['resource_directory']=directory;return dict(directory=str(directory),headers=[dict(path=p,sha256=pin) for p,pin in pins.items()],discovery_log_sha256=sha(folder/'compiler-resource-dir.log'),all_TUs_use_MD=True)

def address_significance_gate(folder,ctx,merged=None):
    E=ctx['ELF'];V=ctx['V'];name='.llvm_addrsig';inputs=[];raw_payload=b'';typed_payload=b''
    for label,paths in [('raw',[folder/('carrier-'+Path(n).stem+'.o') for n in ctx['manifest']['source_units']]),('typed',[folder/('reply-ordered.o' if u['label']=='reply' else u['label']+'.o') for u in units(ctx,'c')])]:
        for p in paths:
            e=E(p);s=e.byname[name];need((s['type'],s['flags'],s['address'],s['info'],s['alignment'],s['entry_size'])==(0x6fff4c03,0x80000000,0,0,1,0) and s['link'] in e.symbol_tables,'actual excluded input addrsig metadata');payload=e.data(s);roles=[];at=0
            while at<len(payload):
                index=0;shift=0
                while True:
                    need(at<len(payload) and shift<=28,'bounded ULEB address-significance index');byte=payload[at];at+=1;index|=(byte&127)<<shift
                    if not byte&128:break
                    shift+=7
                need(index<len(e.symbol_tables[s['link']]),'actual input addrsig symtab index');roles.append(dict(index=index,role=V.role(e,e.symbol_tables[s['link']][index])))
            inputs.append(dict(unit=p.name,bytes=len(payload),payload=payload.hex(),actual_symbol_roles=roles))
            if label=='raw':raw_payload+=payload
            else:typed_payload+=payload
    reply=inputs[-1];need(reply['unit']=='reply-ordered.o' and reply['payload']=='05' and reply['actual_symbol_roles']==[dict(index=5,role=dict(name='tsl9_ota_page_reply_9b8e',owner=REPLY_NATIVE,offset=0,bytes=124,info=18,other=0))],'one new native excluded addrsig index5 names actual FUNC124')
    expected=raw_payload+typed_payload;need(len(expected)==57 and hashlib.sha256(expected[:-1]).hexdigest()=='d5602214c38b22935e3ca6f19485c27a1fb60d011c5e27eaec2941238f32fa9d','sealed prior56-byte metadata prefix plus one actual new native byte')
    for p,wanted in [(folder/'raw-carriers.o',raw_payload),(folder/'typed-providers.o',typed_payload),(folder/'pre-frame-integrated.o',expected),(folder/'source-integrated.o',expected)]:
        e=merged if merged is not None and p.name=='source-integrated.o' else E(p);s=e.byname[name];need((s['type'],s['flags'],s['address'],s['link'],s['info'],s['alignment'],s['entry_size'])==(0x6fff4c03,0x80000000,0,0,0,1,0) and e.data(s)==wanted,'only exact observed input metadata concatenation, never runtime provider');need(not any(r['symbol']['index']==s['index'] for r in e.relocations),'excluded metadata not a relocation provider')
    need(name not in E(folder/'ADDRESS-WITNESS-ONLY.elf').byname,'excluded address-significance metadata absent from linked witness');return dict(actual_inputs=inputs,merged_bytes=57,new_native_bytes=1,new_native_symbol_index=5,excluded_from_final_ELF=True)
def frame_gate(folder,ctx,receipt=None):
    E=ctx['ELF'];S=ctx['schedule'];before=E(folder/'pre-frame-integrated.o');after=E(folder/'source-integrated.o');policy_path=ctx['scheduler'].with_name('frame-policy.json')
    policy=read(policy_path);payload,proofs,changed=S.plan(before,policy,['irq','quarter'])
    need(payload==after.raw and len(changed)==14,'exact actual fourteen-byte declared save-word permutation only')
    need(before.sections==after.sections and before.symbols==after.symbols and before.relocations==after.relocations,'unchanged actual section/symbol/RELA metadata')
    receipt=receipt or folder/'frame-scheduling.json';r=read(receipt)
    expected=dict(schema='TSL9-explicit-ABI-frame-scheduling-receipt-v1',passed=True,tool_sha256=sha(ctx['scheduler']),policy_sha256=sha(policy_path),parser_sha256=S.PARSER_SHA,input=dict(path=(folder/'pre-frame-integrated.o').relative_to(ctx['root']).as_posix(),bytes=len(before.raw),sha256=hashlib.sha256(before.raw).hexdigest()),output=dict(path=(folder/'source-integrated.o').relative_to(ctx['root']).as_posix(),bytes=len(after.raw),sha256=hashlib.sha256(after.raw).hexdigest()),functions=proofs,changed_file_offsets=changed,section_metadata_symbols_RELA_identical=True,original_BIN_read_for_generation=False,new_opcodes_generated=False,padding_added=False,pipeline='C/C++ compiler output followed by explicit source-owned ABI frame scheduling',compiler_alone_emitted_scheduled_order=False,computed_interior_entries_proved_absent=False,target_execution=False,ISA_emulation=False,hardware=False,OTA_ready=False)
    need(r==expected,'complete current scheduling policy/tool/pre-post/receipt identity')
    return dict(passed=True,input_sha256=hashlib.sha256(before.raw).hexdigest(),output_sha256=hashlib.sha256(after.raw).hexdigest(),receipt_sha256=sha(receipt),changed_bytes=len(changed),functions=proofs,compiler_alone_emitted_scheduled_order=False,original_BIN_read_for_generation=False)

def static_checks(folder,ctx,original):
    V=ctx['V'];E=ctx['ELF'];m=ctx['manifest'];selected={r['name'] for r in m['selected_sections']};raw=E(folder/'raw-carriers.o');V.metadata_gate(raw,ctx,set(m['allocations'])-selected);anchor=raw.byname[REPLY_OWNER];need(anchor['size']==0 and anchor['flags']==6 and anchor['alignment']==2,'raw reply zero-byte AX anchor')
    expected=[dict(name=n,owner=REPLY_OWNER,offset=0,bytes=0,info=info,other=0) for n,info in [('__tsl9v4160_ota_code_9b8e',16),('.Lota_handler_00009b8e',0)]];need(V.counter([V.role(raw,s) for s in raw.symbols if s['name'] and s['index']==anchor['index']])==V.counter(expected),'only exact NOTYPE0/local0 reply boundary roles in raw carrier')
    typed=selected_gate(E(folder/'typed-providers.o'),ctx);compiler_merged=merged_gate(E(folder/'pre-frame-integrated.o'),ctx,False);frame=frame_gate(folder,ctx);reply=reply_gate(folder,ctx);merged=merged_gate(E(folder/'source-integrated.o'),ctx);linked=E(folder/'ADDRESS-WITNESS-ONLY.elf');layout=linked_gate(linked,ctx);image=image_gate(folder/IMAGE,linked,ctx,original)
    F=ctx['flash'];ir={};attributes=[];T=E(folder/'typed-providers.o')
    for u in units(ctx,'c'):
        unit=E(folder/(u['label']+'.o'));markers=[V.role(unit,s) for s in unit.symbols if s['name'].startswith('$d.') and 0<s['index']<len(unit.sections) and unit.sections[s['index']]['name']=='.riscv.attributes'];need(len(markers)==1 and all(markers[0][k]==v for k,v in dict(offset=0,bytes=0,info=0,other=0).items()),'one actual typed input attribute marker')
        attributes.append(dict(unit=u['label'],input=markers[0],merged_role={**markers[0],'owner':'ABS'}))
        if u['label'].startswith('flash-'):
            name=u['label'][6:];text=(folder/(u['label']+'.ll')).read_text(encoding='utf-8');ir[name]=F['program_checker'].ir_program(text) if name=='program' else F['old_patterns'].ir_contract(name,text)
    normalize=lambda rows:V.counter([{**r,'name':'$d'} for r in rows]);actual_abs=[V.role(T,s) for s in T.symbols if s['name'].startswith('$d.') and s['index']==0xfff1]
    need(normalize(actual_abs)==normalize([r['merged_role'] for r in attributes]),'nine actual input attributes markers become nine exact unreferenced ABS metadata roles')
    return dict(raw_allocations=679,typed=typed,pre_frame_merged=compiler_merged,explicit_reply_ordering=reply,explicit_frame_scheduling=frame,typed_attribute_origins=attributes,excluded_address_significance=address_significance_gate(folder,ctx),merged=merged,linked=layout,image=image,LLVM_IRQ_IR=ctx['CF'].ir_gate(folder),LLVM_Flash_IR=ir,compiler_resource_discovery=resource_gate(folder,ctx),pointwise_equivalence=False,asynchronous_equivalence=False,ROM_provider=False,physical_compatibility=False,OTA_ready=False,target_execution=False)
def build(root,folder,ctx,tools,mode,original):
    V=ctx['V'];m=ctx['manifest'];folder.mkdir(parents=True);filtered=folder/'filtered';filtered.mkdir();commands=[];objects=[];changes=[];groups=collections.defaultdict(dict)
    r,output=V.run([tools['clang'],'-print-resource-dir'],folder,'compiler-resource-dir');commands.append(r);resource_gate(folder,ctx)
    for r in m['selected_sections']:groups[r['producer']][r['name']]=r
    for n in m['source_units']:
        original_source=root/n;source=original_source
        if n in groups:
            source=filtered/source.name;source.write_bytes(filtered_source(ctx,original_source.read_bytes(),groups[n]));proof=next(r for r in m['filtered_carrier_units'] if r['path']==n);need(sha(source)==proof['filtered_sha256'],'exact five source filters');changes.append(dict(source=n,original_sha256=sha(original_source),filtered_sha256=sha(source),removed_sections=sorted(groups[n])))
        out=folder/('carrier-'+source.stem+'.o');argv=[tools['clang'],'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-fno-builtin','-fno-stack-protector','-Wall','-Wextra','-Werror','-x','c' if mode=='c' else 'c++','-std=c11' if mode=='c' else '-std=c++17','-I',original_source.parent,'-MD','-MF',out.with_suffix('.d'),'-MT',out.name,'-c',source,'-o',out];r,_=V.run(argv,folder,'compile-'+source.stem);commands.append(r);objects.append(out)
    r,_=V.run([tools['linker'],'-r','--no-relax',*objects,'-o',folder/'raw-carriers.o'],folder,'merge-raw-carriers');commands.append(r);typed=[]
    for unit in units(ctx,mode):
        label=unit['label'];ad=folder/(label+'-adapter.h');ad.write_bytes(adapter(unit['rows']).encode());out=folder/(label+'.o')
        for kind,action,dest in [('object',['-c'],out),('IR',['-S','-emit-llvm'],folder/(label+'.ll'))]:
            deps=['-MD','-MF',out.with_suffix('.d'),'-MT',out.name] if kind=='object' else [];r,_=V.run([tools['clang'],*unit['flags'],'-include',ad,*deps,*action,unit['source'],'-o',dest],folder,'typed-'+label+'-'+kind);commands.append(r)
        if label=='reply':
            r,_=V.run([tools['python'],'-B',ctx['reply']['ordering'],'--project-root',root,'--input',out,'--output',folder/'reply-ordered.o','--receipt',folder/'reply-order.json'],folder,'explicit-reply-ordering');commands.append(r);typed.append(folder/'reply-ordered.o')
        else:typed.append(out)
    r,_=V.run([tools['linker'],'-r','--no-relax',*typed,'-o',folder/'typed-providers.o'],folder,'merge-typed');commands.append(r);selected_gate(ctx['ELF'](folder/'typed-providers.o'),ctx)
    script=folder/'canonical53.ld';script.write_bytes(bindings_source(ctx).encode());r,_=V.run([tools['linker'],'-r','--no-relax','-T',script,folder/'raw-carriers.o',folder/'typed-providers.o','-o',folder/'pre-frame-integrated.o'],folder,'merge-source-integrated');commands.append(r)
    merged_gate(ctx['ELF'](folder/'pre-frame-integrated.o'),ctx,False)
    r,_=V.run([tools['python'],'-B',ctx['scheduler'],'--project-root',root,'--input',folder/'pre-frame-integrated.o','--output',folder/'source-integrated.o','--receipt',folder/'frame-scheduling.json'],folder,'explicit-frame-scheduling');commands.append(r)
    # Publish a diagnostic inventory before strict admission so blockers are inspectable.
    e=ctx['ELF'](folder/'source-integrated.o');write(folder/'first-inventory.json',dict(allocations=len(V.alloc(e)),RELA=len(e.relocations),UND=sorted(V.und(e)),typed_compile_TUs=9,raw_compile_TUs=34,commands=commands));merged_gate(e,ctx)
    layout=ctx['model']/'original-image-layout.ld';strict=folder/'STRICT-MISSING-ROM.elf';r,error=V.run([tools['linker'],'--no-relax','--error-limit=0','-T',layout,folder/'source-integrated.o','-o',strict],folder,'strict-final-link',1);commands.append(r);need(not strict.exists() and set(re.findall(r'undefined symbol: (\w+)',error))=={ROM},'strict link rejects sole unknown ROM provider')
    numeric=folder/'NUMERIC-ROM-WITNESS-ONLY.ld';numeric.write_bytes(('/* Numeric address only: no ROM bytes/provider/runtime proof. */\n'+ROM+' = 0x40000;\n').encode());r,_=V.run([tools['linker'],'--no-relax','-T',layout,'-T',numeric,folder/'source-integrated.o','-o',folder/'ADDRESS-WITNESS-ONLY.elf'],folder,'numeric-witness-final-link');commands.append(r);r,_=V.run([tools['objcopy'],'-O','binary',folder/'ADDRESS-WITNESS-ONLY.elf',folder/IMAGE],folder,'export-new-offline-image');commands.append(r)
    return commands,changes,static_checks(folder,ctx,original)
def dependency_rule(path,target,primary,adapter_path=None):
    text=path.read_text(encoding='utf-8').replace('\\\n','').replace('\\\r\n','');need(': ' in text,'bounded Make dependency rule');left,right=text.split(': ',1);need(left.strip()==target,'dependency target matches actual compile -MT')
    paths=[Path(token).resolve() for token in shlex.split(right,posix=True)];need(paths and paths[0]==primary.resolve(),'dependency primary source matches actual -c source')
    if adapter_path is not None:need(adapter_path.resolve() in paths,'dependency rule contains its own forced-include adapter')
    return paths
def dependency_specs(root,folder,ctx):
    filtered={r['producer'] for r in ctx['manifest']['selected_sections']};specs={}
    for name in ctx['manifest']['source_units']:
        original=root/name;primary=folder/'filtered'/original.name if name in filtered else original;stem='carrier-'+original.stem;specs[stem+'.d']=(stem+'.o',primary,None)
    for u in units(ctx,'c'):specs[u['label']+'.d']=(u['label']+'.o',u['source'],folder/(u['label']+'-adapter.h'))
    return specs

def resource_dependencies(paths,ctx):
    result={}
    for p in paths:
        if not p.is_relative_to(ctx['root']):need(str(p) in ctx['resource_headers'] and sha(p)==ctx['resource_headers'][str(p)],'only actual discovered/pinned compiler resource headers outside project');result[str(p)]=ctx['resource_headers'][str(p)]
    return result
def dependency_gate(root,folder,ctx):
    files=list(folder.glob('*.d'));specs=dependency_specs(root,folder,ctx);need(len(files)==43 and {p.name for p in files}==set(specs),'exact43 compiler dependency files/compile associations');seen=set();generated=set();resources=set();rules=[]
    for path in files:
        target,primary,ad=specs[path.name];paths=dependency_rule(path,target,primary,ad);external=resource_dependencies(paths,ctx);rules.append(dict(file=path.name,target=target,primary_source=primary.relative_to(root).as_posix(),adapter=ad.relative_to(root).as_posix() if ad else None,compiler_resource_headers=external))
        for p in paths:
            if not p.is_relative_to(root):need(str(p) in ctx['resource_headers'] and sha(p)==ctx['resource_headers'][str(p)],'only actual discovered/pinned compiler resource headers outside project');resources.add(str(p))
            elif p.is_relative_to(folder.resolve()):generated.add(p.relative_to(folder).as_posix())
            else:
                name=p.relative_to(root).as_posix();need(name in ctx['manifest']['source_files'] and sha(p)==ctx['manifest']['source_files'][name],'all native includes pinned, no HOST path');seen.add(name)
    filtered={r['producer'] for r in ctx['manifest']['selected_sections']};wanted=set(ctx['manifest']['source_files'])-filtered
    generated_wanted={'filtered/'+Path(n).name for n in filtered}|{u['label']+'-adapter.h' for u in units(ctx,'c')}
    need(seen==wanted and generated==generated_wanted and resources==set(ctx['resource_headers']),'exact observed original/generated/compiler-header input closure')
    return dict(compile_TUs=43,dependency_rules=43,rule_associations=sorted(rules,key=lambda r:r['file']),pinned_project_files=len(seen),generated_inputs=sorted(generated),compiler_resource_headers_included=True,compiler_resource_headers={p:ctx['resource_headers'][p] for p in sorted(resources)},compiler_resource_header_TUs=sum(bool(r['compiler_resource_headers']) for r in rules),all_TUs_MD=True)
def snapshot(root,ctx,tools,firmware):
    pins=ctx['V'].snapshot(root,ctx,tools);pins.update(ctx['flash']['pins']);pins.update({str(root/n):pin for n,pin in ctx['manifest']['frame_schedule_source_files'].items()});pins.update({str(root/n):pin for n,pin in ctx['manifest']['reply_order_source_files'].items()});pins.update({str(root/n):pin for n,pin in ctx['reply']['pins'].items()});pins.update(ctx.get('resource_headers',{}))
    for p in (Path(__file__).resolve(),firmware):pins[str(p.resolve())]=sha(p)
    plan=case(root,'v4160-reply-image-integration-2026-10-22')/'image-plan';need(sha(plan/'seal.json')=='8ad4c5328ed0baa66eb88c00cdf2c9dd9563a9472e3ee068f11e120ea23b8342','sealed actual twelve-owner plan');pins[str(plan/'seal.json')]=sha(plan/'seal.json')
    for row in read(plan/'seal.json')['members']:pins[str(plan/row['path'])]=row['sha256']
    for slug,sub in [('v4160-flash-entry-order-2026-10-22','image-plan'),('v4160-flash-register-prefix-2026-10-22','implementation')]:
        base=case(root,slug)/sub;pins[str(base/'seal.json')]=sha(base/'seal.json')
        for row in read(base/'seal.json')['members']:pins[str(base/row['path'])]=row['sha256']
    ctx['V'].stability(pins);return pins
def command_gate(root,folder,ctx,mode,commands,tools):
    V=ctx['V'];m=ctx['manifest'];labels={r['label']:r for r in commands};need(len(labels)==len(commands)==61,'exact59 compiler/link/export/query invocations plus two explicit ABI ordering commands')
    sequence=['compiler-resource-dir']+['compile-'+Path(n).stem for n in m['source_units']]+['merge-raw-carriers']
    for u in units(ctx,mode):sequence+=['typed-'+u['label']+'-object','typed-'+u['label']+'-IR']+(['explicit-reply-ordering'] if u['label']=='reply' else [])
    sequence+=['merge-typed','merge-source-integrated','explicit-frame-scheduling','strict-final-link','numeric-witness-final-link','export-new-offline-image'];need([r['label'] for r in commands]==sequence,'exact chronological source compile/standalone reply order/merge/frame order/link/export provenance')
    filtered={r['producer'] for r in m['selected_sections']}
    for name in m['source_units']:
        original=root/name;source=folder/'filtered'/original.name if name in filtered else original;out=folder/('carrier-'+original.stem+'.o')
        argv=[str(tools['clang']),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-fno-builtin','-fno-stack-protector','-Wall','-Wextra','-Werror','-x','c' if mode=='c' else 'c++','-std=c11' if mode=='c' else '-std=c++17','-I',str(original.parent),'-MD','-MF',str(out.with_suffix('.d')),'-MT',out.name,'-c',str(source),'-o',str(out)]
        need(labels['compile-'+original.stem]['argv']==argv,'exact raw-carrier source/profile/output')
        if name in filtered:
            rows={r['name']:r for r in m['selected_sections'] if r['producer']==name};need(source.read_bytes()==filtered_source(ctx,original.read_bytes(),rows),'only exact selected quoted blocks removed/preserved zero boundary')
    for u in units(ctx,mode):
        label=u['label'];ad=folder/(label+'-adapter.h');need(ad.read_bytes()==adapter(u['rows']).encode(),'exact owning-TU section/FUNC alias adapter')
        for kind,action,suffix in [('object',['-c'],'.o'),('IR',['-S','-emit-llvm'],'.ll')]:
            deps=['-MD','-MF',str(folder/(label+'.d')),'-MT',label+'.o'] if kind=='object' else [];expected=[str(tools['clang']),*u['flags'],'-include',str(ad),*deps,*action,str(u['source']),'-o',str(folder/(label+suffix))]
            need(labels['typed-'+label+'-'+kind]['argv']==expected,'unchanged exact typed compile profile/source/output')
    need((folder/'canonical53.ld').read_bytes()==bindings_source(ctx).encode(),'exact canonical53 source-relative script plus owning reply section merge')
    numeric='/* Numeric address only: no ROM bytes/provider/runtime proof. */\n'+ROM+' = 0x40000;\n';need((folder/'NUMERIC-ROM-WITNESS-ONLY.ld').read_bytes()==numeric.encode(),'sole explicit numeric ROM witness')
    link=str(tools['linker']);layout=str(ctx['model']/'original-image-layout.ld');specs={
      'merge-raw-carriers':[link,'-r','--no-relax',*[str(folder/('carrier-'+Path(n).stem+'.o')) for n in m['source_units']],'-o',str(folder/'raw-carriers.o')],
      'compiler-resource-dir':[str(tools['clang']),'-print-resource-dir'],
      'explicit-reply-ordering':[str(tools['python']),'-B',str(ctx['reply']['ordering']),'--project-root',str(root),'--input',str(folder/'reply.o'),'--output',str(folder/'reply-ordered.o'),'--receipt',str(folder/'reply-order.json')],
      'merge-typed':[link,'-r','--no-relax',*[str(folder/('reply-ordered.o' if u['label']=='reply' else u['label']+'.o')) for u in units(ctx,mode)],'-o',str(folder/'typed-providers.o')],
      'merge-source-integrated':[link,'-r','--no-relax','-T',str(folder/'canonical53.ld'),str(folder/'raw-carriers.o'),str(folder/'typed-providers.o'),'-o',str(folder/'pre-frame-integrated.o')],
      'explicit-frame-scheduling':[str(tools['python']),'-B',str(ctx['scheduler']),'--project-root',str(root),'--input',str(folder/'pre-frame-integrated.o'),'--output',str(folder/'source-integrated.o'),'--receipt',str(folder/'frame-scheduling.json')],
      'strict-final-link':[link,'--no-relax','--error-limit=0','-T',layout,str(folder/'source-integrated.o'),'-o',str(folder/'STRICT-MISSING-ROM.elf')],
      'numeric-witness-final-link':[link,'--no-relax','-T',layout,'-T',str(folder/'NUMERIC-ROM-WITNESS-ONLY.ld'),str(folder/'source-integrated.o'),'-o',str(folder/'ADDRESS-WITNESS-ONLY.elf')],
      'export-new-offline-image':[str(tools['objcopy']),'-O','binary',str(folder/'ADDRESS-WITNESS-ONLY.elf'),str(folder/IMAGE)]}
    for label,argv in specs.items():need(labels[label]['argv']==argv,'source-only link/export command, no cached object/BIN input')
    for r in commands:
        need(Path(r['argv'][0]) in tools.values() and sha(folder/r['log'])==r['log_sha256'],'actual declared LLVM tool and log')
        need(r['exit']!=0 if r['label']=='strict-final-link' else r['exit']==0,'only strict missing-ROM operation rejects')
    text=(folder/'strict-final-link.log').read_text(encoding='utf-8');need(not (folder/'STRICT-MISSING-ROM.elf').exists() and set(re.findall(r'undefined symbol: (\w+)',text))=={ROM},'actual strict failure solely missing ROM provider')
    return dict(commands=61,LLVM_commands=59,explicit_ABI_scheduling_commands=2,compile_TUs=43,raw_TUs=34,IRQ_TUs=2,Flash_TUs=6,reply_TUs=1,strict_missing_ROM_rejected=True,all_TUs_MD=True)
def negative_controls(folder,ctx,original,create=True,recorded=None):
    E=ctx['ELF'];obj=E(folder/'source-integrated.o');linked=E(folder/'ADDRESS-WITNESS-ONLY.elf');m=ctx['manifest'];output=folder/'negative-controls';rows=[]
    if create:output.mkdir()
    def symoff(e,name):
        for sec in e.sections:
            if sec['type']==2:
                for i,s in enumerate(e.symbol_tables[sec['index']]):
                    if s['name']==name:return sec['offset']+i*16
        raise ValueError('counterexample symbol unavailable')
    cases=['retained_storage_byte','Flash_program_byte','program_extent94','alias_ABS','alias_NOTYPE','relative_label_value','outside_RELA_addend','owned_RELA_addend','missing_outside_RELA','RAM_PROGBITS','extra_ALLOC_comment','FILE_role_removed','mapping_role_changed','linked_wrong_VA','linked_FUNC_size','LOAD_wrong_LMA','LOAD_RAM_memsz','LOAD_wrong_permissions','image_outside_byte','image_unscheduled_IRQ','image_unscheduled_quarter','image_truncated','image_appended','reply_boundary_FUNC','reply_boundary_size124','reply_local_entry_ABS','reply_code_byte','image_unscheduled_reply','image_incoming_no_link','excluded_addrsig_byte']
    selected={r['name'] for r in m['selected_sections']}
    for tag in cases:
        image=tag.startswith('image_');is_linked=tag.startswith('linked_') or tag.startswith('LOAD_');e=linked if is_linked else obj;raw=bytearray((folder/IMAGE).read_bytes() if image else e.raw)
        def shfield(section,delta,value):struct.pack_into('<I',raw,struct.unpack_from('<I',raw,32)[0]+section['index']*40+delta,value)
        if tag=='retained_storage_byte':raw[e.byname['.text.tsl9v4160.image_entry']['offset']]^=1
        elif tag=='Flash_program_byte':raw[e.byname['.text.tsl9v4160.direct_closure_18ef2']['offset']+6]^=0x10
        elif tag=='program_extent94':shfield(e.byname['.text.tsl9v4160.direct_closure_18ef2'],20,94)
        elif tag=='alias_ABS':struct.pack_into('<H',raw,symoff(e,'__tsl9v4160_call_18ef2')+14,0xfff1)
        elif tag=='alias_NOTYPE':raw[symoff(e,'__tsl9v4160_call_18ef2')+12]=16
        elif tag=='reply_boundary_FUNC':raw[symoff(e,'__tsl9v4160_ota_code_9b8e')+12]=18
        elif tag=='reply_boundary_size124':struct.pack_into('<I',raw,symoff(e,'__tsl9v4160_ota_code_9b8e')+8,124)
        elif tag=='reply_local_entry_ABS':struct.pack_into('<H',raw,symoff(e,'.Lota_handler_00009b8e')+14,0xfff1)
        elif tag=='reply_code_byte':raw[e.byname[REPLY_OWNER]['offset']+0x42]^=4
        elif tag=='excluded_addrsig_byte':raw[e.byname['.llvm_addrsig']['offset']+e.byname['.llvm_addrsig']['size']-1]^=1
        elif tag=='relative_label_value':
            at=symoff(e,m['section_relative_bindings'][0]['name'])+4;struct.pack_into('<I',raw,at,struct.unpack_from('<I',raw,at)[0]+2)
        elif tag in ('outside_RELA_addend','owned_RELA_addend','missing_outside_RELA'):
            sec=next(s for s in e.sections if s['type']==4 and s['size'] and ((e.sections[s['info']]['name'] in selected)==(tag=='owned_RELA_addend')))
            if tag=='missing_outside_RELA':shfield(sec,20,sec['size']-12)
            else:at=sec['offset']+8;struct.pack_into('<i',raw,at,struct.unpack_from('<i',raw,at)[0]+2)
        elif tag=='RAM_PROGBITS':shfield(e.byname['.bss.tsl9v4160.ram'],4,1)
        elif tag=='extra_ALLOC_comment':shfield(e.byname['.comment'],8,e.byname['.comment']['flags']|2)
        elif tag=='FILE_role_removed':
            s=next(s for s in e.symbols if s['info']&15==4 and s['name']=='flash_native.c');struct.pack_into('<I',raw,symoff(e,s['name']),0)
        elif tag=='mapping_role_changed':
            s=next(s for s in e.symbols if s['name'].startswith('$d.') and 0<s['index']<len(e.sections) and e.sections[s['index']]['name'] not in selected and e.sections[s['index']]['flags']&2);struct.pack_into('<H',raw,symoff(e,s['name'])+14,0xfff1)
        elif tag=='linked_wrong_VA':shfield(e.byname['.text.tsl9v4160.code_continuation_9c0a'],12,0x9c0c)
        elif tag=='linked_FUNC_size':struct.pack_into('<I',raw,symoff(e,'__tsl9v4160_call_18ef2')+8,94)
        elif tag in ('LOAD_wrong_LMA','LOAD_RAM_memsz','LOAD_wrong_permissions'):
            off=struct.unpack_from('<I',raw,28)[0];stride,count=struct.unpack_from('<HH',raw,42);at=next(off+i*stride for i in range(count) if struct.unpack_from('<I',raw,off+i*stride)[0]==1);struct.pack_into('<I',raw,at+12,struct.unpack_from('<I',raw,at+12)[0]+4)
            if tag!='LOAD_wrong_LMA':
                raw=bytearray(e.raw)
                if tag=='LOAD_RAM_memsz':at=next(off+i*stride for i in range(count) if struct.unpack_from('<I',raw,off+i*stride)[0]==1 and struct.unpack_from('<I',raw,off+i*stride+16)[0]==0);struct.pack_into('<I',raw,at+20,struct.unpack_from('<I',raw,at+20)[0]+4)
                else:struct.pack_into('<I',raw,at+24,struct.unpack_from('<I',raw,at+24)[0]^1)
        elif tag=='image_outside_byte':raw[0]^=1
        elif tag in ('image_unscheduled_IRQ','image_unscheduled_quarter'):
            address=0x9a42 if tag=='image_unscheduled_IRQ' else 0x9c0a;length=8 if tag=='image_unscheduled_IRQ' else 6;owner=next(x['name'] for x in m['selected_sections'] if x['originalVA']==address);pre=E(folder/'pre-frame-integrated.o');raw[address-0x8000+2:address-0x8000+2+length]=pre.data(pre.byname[owner])[2:2+length]
        elif tag=='image_unscheduled_reply':
            pre=E(folder/'reply.o');body=pre.data(pre.byname[REPLY_NATIVE])
            for begin,end in ((2,0x16),(0x58,0x60)):raw[0x9b8e-0x8000+begin:0x9b8e-0x8000+end]=body[begin:end]
        elif tag=='image_incoming_no_link':raw[0x9df4-0x8000+1]^=0x80
        elif tag=='image_truncated':raw=raw[:-1]
        elif tag=='image_appended':raw+=b'\0'
        path=output/(tag+('.bin' if image else '.elf' if is_linked else '.o'))
        if create:path.write_bytes(raw)
        else:need(path.read_bytes()==bytes(raw),'exact actual negative bytes '+tag)
        try:
            if image:image_gate(path,linked,ctx,original)
            elif tag=='excluded_addrsig_byte':address_significance_gate(folder,ctx,E(path))
            elif tag.startswith('LOAD_'):image_gate(folder/IMAGE,E(path),ctx,original)
            elif is_linked:linked_gate(E(path),ctx)
            else:merged_gate(E(path),ctx)
        except (ValueError,AssertionError) as error:reason=str(error)
        else:raise ValueError('accepted actual ELF/RELA/image negative '+tag)
        rows.append(dict(case=tag,path=path.relative_to(folder).as_posix(),sha256=sha(path),rejected=True,reason=reason))
    if recorded is not None:need(rows==recorded,'actual mutation replay identities/reasons')
    return rows
def dependency_controls(folder,ctx,create=True,recorded=None):
    output=folder/'negative-controls';positive=folder/'flash-program.d';spec=dependency_specs(ctx['root'],folder,ctx)[positive.name];raw=positive.read_bytes();target,primary,ad=spec;rows=[];paths=dependency_rule(positive,target,primary,ad)
    def rule(name,inputs):return name+': '+' '.join(p.as_posix().replace('\\','\\\\').replace(' ','\\ ').replace('#','\\#').replace('\t','\\\t') for p in inputs)+'\n'
    wrong_primary=list(paths);wrong_primary[0]=ctx['root']/ctx['manifest']['source_units'][0];wrong_adapter=[folder/'flash-status-adapter.h' if p==ad.resolve() else p for p in paths]
    wrong_resource=[ctx['resource_directory']/'include/not-stdint.h' if str(p) in ctx['resource_headers'] else p for p in paths]
    changes=[('dependency_wrong_MT',rule('wrong-target.o',paths)),('dependency_wrong_primary',rule(target,wrong_primary)),('dependency_wrong_adapter',rule(target,wrong_adapter)),('dependency_wrong_resource_header',rule(target,wrong_resource))]
    for tag,new in changes:
        payload=new.encode();need(payload!=raw,'actual per-rule dependency mutation');path=output/(tag+'.d')
        if create:path.write_bytes(payload)
        else:need(path.read_bytes()==payload,'exact retained dependency negative bytes')
        try:resource_dependencies(dependency_rule(path,target,primary,ad),ctx)
        except ValueError as error:reason=str(error)
        else:raise ValueError('accepted dependency/source association negative')
        rows.append(dict(case=tag,path=path.relative_to(folder).as_posix(),sha256=sha(path),rejected=True,reason=reason))
    if recorded is not None:need(rows==recorded,'actual dependency control replay')
    return rows

def scheduling_controls(folder,ctx,create=True,recorded=None):
    positive=read(folder/'frame-scheduling.json');rows=[]
    for label in ('wrong-input-hash','wrong-policy-hash','false-compiler-only-claim','missing-quarter-proof'):
        value=json.loads(json.dumps(positive))
        if label=='wrong-input-hash':value['input']['sha256']='0'*64
        elif label=='wrong-policy-hash':value['policy_sha256']='0'*64
        elif label=='false-compiler-only-claim':value['compiler_alone_emitted_scheduled_order']=True
        else:value['functions']=value['functions'][:1]
        path=folder/'negative-controls'/('frame-'+label+'.json');payload=(json.dumps(value,indent=2)+'\n').encode()
        if create:path.write_bytes(payload)
        else:need(path.read_bytes()==payload,'exact actual scheduling receipt mutation')
        try:frame_gate(folder,ctx,path)
        except ValueError as error:reason=str(error)
        else:raise ValueError('accepted scheduling evidence counterexample '+label)
        rows.append(dict(case=label,path=path.relative_to(folder).as_posix(),sha256=sha(path),rejected=True,reason=reason))
    reply=read(folder/'reply-order.json')
    for label in ('wrong-reply-input','wrong-reply-policy'):
        value=json.loads(json.dumps(reply))
        if label=='wrong-reply-input':value['input']['sha256']='0'*64
        else:value['policy_sha256']='0'*64
        path=folder/'negative-controls'/(label+'.json');payload=(json.dumps(value,indent=2)+'\n').encode()
        if create:path.write_bytes(payload)
        else:need(path.read_bytes()==payload,'exact standalone reply receipt mutation')
        try:reply_gate(folder,ctx,path)
        except ValueError as error:reason=str(error)
        else:raise ValueError('accepted standalone reply ordering counterexample')
        rows.append(dict(case=label,path=path.relative_to(folder).as_posix(),sha256=sha(path),rejected=True,reason=reason))
    if recorded is not None:need(rows==recorded,'actual scheduling control replay')
    return rows

def recipe_controls(root,folder,ctx,mode,commands,tools,create=True,recorded=None):
    changed=json.loads(json.dumps(commands));a=next(i for i,r in enumerate(changed) if r['label']=='explicit-reply-ordering');b=next(i for i,r in enumerate(changed) if r['label']=='merge-typed');changed[a],changed[b]=changed[b],changed[a];path=folder/'negative-controls/recipe_wrong_chronology.json';payload=(json.dumps(changed,indent=2)+'\n').encode()
    if create:path.write_bytes(payload)
    else:need(path.read_bytes()==payload,'exact chronological recipe counterexample')
    try:command_gate(root,folder,ctx,mode,changed,tools)
    except ValueError as error:reason=str(error)
    else:raise ValueError('accepted reordering of actual scheduling/merge provenance')
    rows=[dict(case='recipe_wrong_chronology',path=path.relative_to(folder).as_posix(),sha256=sha(path),rejected=True,reason=reason)]
    if recorded is not None:need(rows==recorded,'actual chronological recipe counterexample replay')
    return rows
def replay(root,receipt,firmware=None):
    root=Path(root).resolve();receipt=Path(receipt).resolve();ctx=context(root,firmware);ctx['root']=root;path,original=original_image(root,ctx,firmware);r=read(receipt);folder=receipt.parent;V=ctx['V']
    need(r['passed'] and r['mode'] in ('c','cpp') and r['manifest_sha256']==MANIFEST_SHA and r['runner_sha256']==sha(Path(__file__)),'current successful image source/runner/language identities')
    need(r['source_files']==ctx['manifest']['source_files'] and r['firmware_sha256']==sha(path),'current source/firmware identity');tools={k:Path(x['path']) for k,x in r['tools'].items()};need(set(tools)=={'clang','linker','objcopy','python'},'exact three declared LLVM tools')
    for k,p in tools.items():need(sha(p)==r['tools'][k]['sha256'],'actual compiler/linker/objcopy identities')
    resource_gate(folder,ctx);need(snapshot(root,ctx,tools,path)==r['input_stability_pins'],'current exact source/proof/tool/runner snapshot')
    for name,meta in r['artifacts'].items():
        p=(folder/name).resolve();need(p.is_relative_to(folder) and p.stat().st_size==meta['bytes'] and sha(p)==meta['sha256'],'actual artifact/log/dependency/image pin')
    checks=static_checks(folder,ctx,original);checks['native_dependency_closure']=dependency_gate(root,folder,ctx);checks['actual_commands']=command_gate(root,folder,ctx,r['mode'],r['commands'],tools);negative_controls(folder,ctx,original,False,r['actual_negative_controls']);dependency_controls(folder,ctx,False,r['actual_dependency_controls']);scheduling_controls(folder,ctx,False,r['actual_scheduling_controls']);recipe_controls(root,folder,ctx,r['mode'],r['commands'],tools,False,r['actual_recipe_controls']);need(json.loads(json.dumps(checks))==r['checks'],'actual complete source/ELF/LOAD/image proof replay')
    return dict(passed=True,receipt=str(receipt),sha256=sha(receipt),artifacts_checked=len(r['artifacts']),compile_TUs=43,RELA=checks['merged']['RELA'],image_sha256=checks['image']['sha256'],differences=len(checks['image']['differences']),target_execution=False,flashable=False)
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=H.parents[2]);p.add_argument('--tool-dir',type=Path);p.add_argument('--clang');p.add_argument('--linker');p.add_argument('--objcopy');p.add_argument('--firmware',type=Path);p.add_argument('--language',choices=['c','cpp','both'],default='both');p.add_argument('--build-root',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
    if a.replay:
        need(not any((a.tool_dir,a.clang,a.linker,a.objcopy,a.build_root)),'tool/build overrides apply to fresh compilation only')
        need(a.language=='both' or read(a.replay)['mode']==a.language,'explicit replay language matches recorded mode')
        print(json.dumps(replay(root,a.replay,a.firmware)));return
    ctx=context(root,a.firmware);ctx['root']=root;V=ctx['V'];firmware,original=original_image(root,ctx,a.firmware);tools={k:V.resolve_tool(getattr(a,k),a.tool_dir,n) for k,n in [('clang','clang'),('linker','ld.lld'),('objcopy','llvm-objcopy')]};tools['python']=Path(sys.executable).resolve();pins=snapshot(root,ctx,tools,firmware);base=a.build_root.resolve() if a.build_root else root/MODEL/'build'/('source-integrated-'+uuid.uuid4().hex);need(base.is_relative_to(root) and not base.exists(),'create-only build root inside project');results=[]
    for mode in (['c','cpp'] if a.language=='both' else [a.language]):
        folder=base/mode;commands,changes,checks=build(root,folder,ctx,tools,mode,original);pins.update(ctx['resource_headers']);checks['native_dependency_closure']=dependency_gate(root,folder,ctx);checks['actual_commands']=command_gate(root,folder,ctx,mode,commands,tools);controls=negative_controls(folder,ctx,original);depcontrols=dependency_controls(folder,ctx);schedulecontrols=scheduling_controls(folder,ctx);recipecontrols=recipe_controls(root,folder,ctx,mode,commands,tools);V.stability(pins)
        r=dict(schema='TSL9-explicit-twelve-function-source-image-v1',passed=True,mode=mode,manifest_sha256=MANIFEST_SHA,runner_sha256=sha(Path(__file__)),source_files=ctx['manifest']['source_files'],input_stability_pins=pins,commands=commands,filtered_sources=changes,checks=checks,actual_negative_controls=controls,actual_dependency_controls=depcontrols,actual_scheduling_controls=schedulecontrols,actual_recipe_controls=recipecontrols,artifacts={p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in folder.rglob('*') if p.is_file()},tools={k:dict(path=str(v),sha256=sha(v)) for k,v in tools.items()},firmware_sha256=sha(firmware),target_execution=False,emulation=False,network=False,hardware=False,ROM_provider=False,flashable=False,OTA_ready=False);write(folder/'verification.json',r);results.append(dict(mode=mode,receipt=str(folder/'verification.json'),sha256=sha(folder/'verification.json'),image=str(folder/IMAGE),image_sha256=sha(folder/IMAGE)))
    if len(results)==2:need(results[0]['image_sha256']==results[1]['image_sha256'],'C11/C++17 fresh source-derived images identical')
    print(json.dumps(dict(passed=True,results=results,flashable=False,OTA_ready=False)))
if __name__=='__main__':main()
