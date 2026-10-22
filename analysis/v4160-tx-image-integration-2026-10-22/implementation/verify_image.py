"""Fresh thirteen-region full image, explicit ABI stages and read-only replay."""
import argparse,collections,hashlib,json,os,re,runpy,struct,subprocess,sys,uuid
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
MODEL='experiments/tsl9-v4160-tx-image-integration';TX='.text.tsl9v4160.code_continuation_8a56';IMAGE='NOT-FLASH-VALIDATED-tx-integrated.bin'
MANIFEST='f95e133f59ed9701b1ae6bb5187fb19f467cefc02bfed1063577bb6df42219a7'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def H(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_bytes())
def write(p,r):p.write_bytes((json.dumps(r,indent=2)+'\n').encode())
def need(v,m):
    if not v:raise ValueError(m)
def case(root,slug):return next(p for p in(root/'analysis'/slug,root/'apk-analysis'/('tsl9-'+slug)) if p.is_dir())
def portable(root,n):
    if n.startswith('apk-analysis/tsl9-'):
        return next(p for p in(root/'analysis'/n[len('apk-analysis/tsl9-'):],root/n) if p.is_file())
    return root/n
def context(root,firmware=None):
    root=root.resolve();model=root/MODEL;need(sha(model/'source-manifest.json')==MANIFEST,'current source-owned thirteen-region ledger');ledger=read(model/'source-manifest.json');P=runpy.run_path(str(HERE/'prototype.py'));B=P['load'](root);ctx=B['context'](root,firmware);need(sha(model/'original-image-layout.ld')==ledger['layout_sha256'],'byte-identical historical layout')
    for n,pin in ledger['source_files'].items():need(sha(root/n)==pin,'source/header ledger identity '+n)
    for n,pin in ledger['TX_order_sources'].items():need(sha(root/n)==pin,'immutable TX scheduling source')
    source=ledger['TX_original_source'];p=portable(root,source['path']);need(sha(p)==source['sha256'],'pinned original TX role/RELA facts')
    selected=case(root,'v4160-tx-register-abi-2026-10-22')/'implementation';need(sha(selected/'seal.json')==ledger['TX']['selected_component_seal_sha256'] and sha(selected/'receipts/native-c.json')==ledger['TX']['selected_component_metadata_sha256'],'sealed actual native component admission metadata')
    ctx.update(root=root,B=B,P=P,ledger=ledger,newmodel=model,txsource=read(p),TXorder=runpy.run_path(str(root/'experiments/tsl9-v4160-tx-register-abi/postpass/schedule.py')))
    return ctx
def role_projection(r):
    r=json.loads(json.dumps(r));s=r['symbol']
    if s['name']=='__tsl9v4160_call_8a56':need((s['owner'],s['offset'],s['bytes'],s['info'],s['other'])==(TX,0,8,18,0),'real canonical runtime entry FUNC8 role');s['bytes']=280
    return r
def tx_parts(e,V,linked=False):
    rows=[V.role(e,s,linked) for s in e.symbols if s['info']&15==2 and s['index']==e.byname[TX]['index']];rows=sorted(rows,key=lambda x:x['offset']);need([(r['offset'],r['bytes'],r['info'],r['other']) for r in rows]==[(0,8,18,0),(8,270,2,0),(278,2,18,0)],'truthful three real section-relative FUNC extents')
    need(rows[0]['name']=='__tsl9v4160_call_8a56' and rows[1]['name'] in('tsl9_tx_valid_body','_ZL18tsl9_tx_valid_bodyjjjj') and rows[2]['name']=='tsl9_tx_oversized_return','source-owned provider names');return rows
def merged_gate(e,ctx,scheduled=True):
    V=ctx['V'];m=ctx['manifest'];B=ctx['B'];selected={r['name'] for r in m['selected_sections']}|{TX};need(e.kind==1 and e.flags==1 and V.und(e)=={B['ROM']},'partial RV32 RVC carrier with sole unknown ROM');facts=V.metadata_gate(e,ctx,m['allocations'])
    for n,pin in m['retained_storage'].items():
        if n!=TX:need(H(V.data(e,e.byname[n]))==pin['sha256'],'all678 retained original partial-storage bytes')
    for r in m['selected_sections']:need(H(e.data(e.byname[r['name']]))==r['native_object_sha256' if scheduled else 'typed_provider_object_sha256'],'all twelve prior typed region bodies')
    if 'expected_TX_partial_payload' in ctx:need(e.data(e.byname[TX])==ctx['expected_TX_partial_payload'],'exact actual three-source TX provider payload, no substituted code')
    outside=[V.relocation(e,r) for r in e.relocations if r['owner'] not in selected];oldoutside=[role_projection(r) if r['symbol']['name']=='__tsl9v4160_call_8a56' else r for r in outside]+ctx['txsource']['owned_RELA'];need(len(outside)==8246 and V.digest(sorted(oldoutside,key=lambda x:json.dumps(x,sort_keys=True)))==m['retained_RELA_semantic_sha256'],'all8246 outside RELA unchanged, exact canonical-size projection and original TX11 subtraction')
    oldowned=[V.relocation(e,r) for r in e.relocations if r['owner'] in selected and r['owner']!=TX];wanted=[]
    for r in m['old_selected_RELA']:
        if r['type']!=17:continue
        r=json.loads(json.dumps(r));target=next((x for x in m['selected_sections'] if x['global_alias']==r['symbol']['name']),None)
        if target is not None:r['symbol']['name']=target['new_C_symbol']
        wanted.append(r)
    need(V.counter([role_projection(r) if r['symbol']['name']=='__tsl9v4160_call_8a56' else r for r in oldowned])==V.counter(wanted),'all twelve prior typed JAL roles, only TX target size changes')
    tx=[V.relocation(e,r) for r in e.relocations if r['owner']==TX];need(sorted((r['offset'],r['type'],r['addend']) for r in tx)==[(4,16,0),(128,23,0),(132,24,0)],'three real standard TX relocations')
    parts=tx_parts(e,V);branch=next(r for r in tx if r['type']==16);need(branch['symbol']==parts[-1],'standard branch targets actual typed returning leaf')
    hi=next(r for r in tx if r['type']==23);lo=next(r for r in tx if r['type']==24);ram=next(b['role'] for b in m['section_relative_bindings'] if b['name']=='__tsl9v4160_data_2000b18c');need(hi['symbol']==ram,'PCREL HI uses actual canonical RAM section-relative provider');need(lo['symbol']['owner']==TX and lo['symbol']['offset']==128 and all(lo['symbol'][k]==0 for k in('bytes','info','other')),'PCREL LO names real body-local anchor')
    need(len(e.relocations)==len(outside)+len(oldowned)+len(tx)==8261,'actual full relocation partition8261')
    for b in m['section_relative_bindings']:need(V.counter([V.role(e,s) for s in e.symbols if s['name']==b['name']])==V.counter([b['role']]),'all53 actual canonical section-relative bindings')
    discharged=B['branch_discharge'](e,ctx);txprivate=[r for r in ctx['txsource']['owner_symbol_roles'] if r['info']==0 and r['name'].startswith('.L')];need(len(txprivate)==8 and not any(s['name'] in {r['name'] for r in txprivate} for s in e.symbols),'seven old TX control labels plus one PCREL anchor retired, never fake providers')
    before,oldmeta=V.normalized_symbols(m['baseline_symbol_roles'],[r['original_RELA']['symbol'] for r in discharged]+txprivate);after,newmeta=V.normalized_symbols([V.role(e,s) for s in e.symbols]);extra=[dict(name=r['new_C_symbol'],owner=r['name'],offset=0,bytes=r['bytes'],info=18,other=0) for r in m['selected_sections']]+parts[1:]+[dict(name='.Lpcrel_hi0',owner=TX,offset=128,bytes=0,info=0,other=0)]
    for r in before:
        if r['name']=='__tsl9v4160_call_8a56':need(r['bytes']==280,'original metadata role');r['bytes']=8
    need(V.counter(after)==V.counter(before+extra),'all nonmetadata original symbol roles retained except explicit TX/old-branch changes and real C providers')
    need(V.counter([r for r in oldmeta if r['info']&15==3])==V.counter([r for r in newmeta if r['info']&15==3]),'all original SECTION roles')
    def mappings(rows,owner=None):return V.counter([{**r,'name':r['name'].split('.')[0]} for r in rows if re.fullmatch(r'\$[dx]\.\d+',r['name']) and(r['owner']==owner if owner else r['owner'] not in selected|{'ABS','.comment'})])
    need(mappings(oldmeta)==mappings(newmeta),'all retained allocated mapping roles modulo measured ordinals')
    files=[dict(name=n,owner='ABS',offset=0,bytes=0,info=4,other=0) for n in ['interrupt_callframe.c','rcc_helpers.c']+['flash_native.c']*6+['page_reply.c','valid_body.c','return_leaf.c']];need(V.counter([r for r in newmeta if r['info']&15==4])==V.counter([r for r in oldmeta if r['info']&15==4]+files),'exact actual raw34 plus eleven typed FILE records')
    for owner,count in [('ABS',12),('.comment',11)]:need(mappings(newmeta,owner)==mappings(oldmeta,owner)+V.counter([dict(name='$d',owner=owner,offset=0,bytes=0,info=0,other=0)]*count),'exact measured nonstorage mapping origin inventory')
    maps=[r for r in newmeta if re.fullmatch(r'\$[dx]\.\d+',r['name']) and r['owner'] in selected];expectedmaps=[dict(name='$x',owner=r['name'],offset=0,bytes=0,info=0,other=0) for r in m['selected_sections']]+[dict(name='$x',owner=TX,offset=o,bytes=0,info=0,other=0) for o in(0,8,278)];need(V.counter([{**r,'name':r['name'].split('.')[0]} for r in maps])==V.counter(expectedmaps),'three genuine TX code mappings plus twelve prior code mappings')
    incoming=[r for r in outside if r['symbol']['owner'] in selected];need(len(incoming)==29 and all(r['symbol']['offset']==0 for r in incoming),'29 measured outside incoming actual entries')
    return dict(**facts,retained_storage_sections=678,outside_RELA=len(outside),prior_owned_JAL=len(oldowned),TX_RELA=len(tx),RELA=len(e.relocations),canonical_bindings=53,outside_incoming=29,real_TX_FUNC_parts=parts,old_TX_control_labels_retired=7,old_TX_PCREL_anchor_retired=1,old_private_branch_roles=discharged,original_FUNC280_role_preserved=False)
def tx_order_gate(folder,ctx,receipt=None):
    before=ctx['ELF'](folder/'tx-valid_body.o');after=ctx['ELF'](folder/'tx-valid_body-ordered.o');M=ctx['TXorder'];c=M['context'](ctx['root']);payload,facts=M['transform'](before,c['decode']);need(payload==after.raw and before.sections==after.sections and before.symbols==after.symbols and before.relocations==after.relocations,'exact source-owned ten compiled-word movement, all other ELF bytes/metadata same');r=read(receipt or folder/'tx-frame-order.json');need(r['facts']==facts and r['input']['sha256']==sha(folder/'tx-valid_body.o') and r['output']['sha256']==sha(folder/'tx-valid_body-ordered.o') and r['compiler_only']==r['new_opcodes_generated']==r['original_BIN_codegen_input']==r['target_execution']==False,'actual TX scheduling receipt identity')
    for p,pin in r['source_pins'].items():need(sha(Path(p))==pin,'actual current TX scheduling source/parser/policy/input identity')
    return dict(changed_bytes=facts['changed_bytes'],explicit_scheduling=True,compiler_only=False)
def input_payloads(folder,ctx,mode):
    E=ctx['ELF'];parts=[folder/'tx-entry.o',folder/'tx-valid_body-ordered.o',folder/'tx-return_leaf.o'];names=['.text.tsl9_tx_entry','.text.tsl9_tx_valid_body','.text.tsl9_tx_oversized_return'];payload=b'';metadata=[]
    for p,n,size in zip(parts,names,(8,270,2)):
        e=E(p);s=e.byname[n];need((s['type'],s['flags'],s['size'],s['alignment'])==(1,6,size,2) and set(ctx['V'].alloc(e))=={n},'exact source-owned TX input allocation');payload+=e.data(s);metadata.append(dict(path=p.name,sha256=sha(p),code_sha256=H(e.data(s))))
    need(ctx['ELF'](folder/'pre-frame-integrated.o').data(ctx['ELF'](folder/'pre-frame-integrated.o').byname[TX])==payload,'fresh merged TX bytes are exactly new assembly plus ordered typed body and typed RET, no fallback/padding');ctx['expected_TX_partial_payload']=payload;return metadata
def image_gate(folder,ctx,original,linked_override=None,image_override=None):
    V=ctx['V'];E=ctx['ELF'];m=ctx['manifest'];e=linked_override if linked_override is not None else E(folder/'ADDRESS-WITNESS-ONLY.elf');image_path=image_override or folder/IMAGE;V.metadata_gate(e,ctx,m['allocations'],True);need(e.kind==2 and V.und(e)==set() and not e.relocations and struct.unpack_from('<I',e.raw,24)[0]==0x8000,'actual fully linked address witness')
    tx=e.data(e.byname[TX]);need(H(tx)==ctx['ledger']['TX']['linked_body_sha256'],'linked TX bytes match sealed source-built280B component identity');parts=tx_parts(e,V,True)
    for r in m['selected_sections']:need(e.data(e.byname[r['name']])==bytes.fromhex(r['native_linked_bytes']),'all twelve prior linked typed bodies exact')
    globals_=[dict(r) for r in m['baseline_symbol_roles'] if r['name'] and r['info']>>4 in(1,2) and r['owner']!='UND']
    for r in globals_:
        if r['name']=='__tsl9v4160_call_8a56':r['bytes']=8
    extras=[dict(name=r['new_C_symbol'],owner=r['name'],offset=0,bytes=r['bytes'],info=18,other=0) for r in m['selected_sections']]+[parts[-1]];rom=dict(name=ctx['B']['ROM'],owner='ABS',offset=0x40000,bytes=0,info=16,other=0);need(V.counter(V.globals_(e,True))==V.counter(globals_+extras+[rom]),'all linked globals unchanged except canonicalFUNC8 and actual typed providers, sole numeric ROM witness')
    for b in m['section_relative_bindings']:need(V.counter([V.role(e,s,True) for s in e.symbols if s['name']==b['name']])==V.counter([b['role']]),'53 linked real relative roles')
    # Original bytes are validation only. Strict generator commands have no original BIN input.
    candidate=original[:0xa56]+tx+original[0xb6e:];overlay={**ctx,'manifest':{**m,'expected_differences':[dict(address=i+0x8000,original=a,native=b) for i,(a,b) in enumerate(zip(original,candidate)) if a!=b]}};facts=V.image_gate(image_path,e,overlay,original);raw=image_path.read_bytes();need(raw==candidate,'whole image equals original outside exact source-built TX280')
    permissions={};loads={};loadfacts=[]
    for s in V.alloc(e).values():
        for a in range(s['address'],s['address']+s['size']):need(a not in permissions,'no allocated-memory overlap');permissions[a]=4|(2 if s['flags']&1 else 0)|(1 if s['flags']&4 else 0)
    phoff=struct.unpack_from('<I',e.raw,28)[0];stride,count=struct.unpack_from('<HH',e.raw,42)
    for i in range(count):
        typ,off,va,lma,filesz,memsz,flags,align=struct.unpack_from('<8I',e.raw,phoff+i*stride)
        if typ!=1:continue
        need(va==lma and filesz<=memsz<=len(permissions) and flags in(4,5,6),'bounded LOAD actual memory/permissions')
        for a in range(va,va+memsz):need(a not in loads and permissions.get(a)==flags,'all LOAD memory exactly section-owned permissions');loads[a]=flags
        loadfacts.append(dict(VA=va,LMA=lma,file_bytes=filesz,memory_bytes=memsz,permissions=flags))
    need(loads==permissions and len(loadfacts)==15,'all15 LOADs map exactly alloriginal storage and RAM, no hidden padding')
    linkedjumps=[]
    records=ctx['manifest']['external_incoming_RELA']+[r for r in ctx['manifest']['old_selected_RELA'] if r['type']==17]
    records += [dict(owner=r['owner'],offset=r['site']-m['allocations'][r['owner']]['originalVA'],type=r['RELA_type'],addend=0,symbol=dict(owner=TX,offset=0)) for r in ctx['txsource']['actual_external_incoming'] if r['owner'] not in {x['name'] for x in m['selected_sections']}]
    for r in records:
        s=e.byname[r['owner']];pc=s['address']+r['offset'];body=e.data(s);size=4 if body[r['offset']]&3==3 else 2;f=ctx['B']['jump_fields'](body[r['offset']:r['offset']+size],pc);need(f['target']==m['allocations'][r['symbol']['owner']]['originalVA']+r['symbol']['offset']+r['addend'],'all retained incoming/priorowned encoded targets');linkedjumps.append(dict(PC=pc,**f))
    need(len(linkedjumps)==41,'actual29outside incoming plus12priorowned direct call/tail frontiers');facts.update(LOADs=loadfacts,outside_TX_identical=True,real_TX_FUNC_parts=parts,encoded_frontiers=linkedjumps);return facts
def addrsig_gate(folder,ctx,mode):
    E=ctx['ELF'];V=ctx['V'];m=ctx['manifest'];rawpaths=[folder/('carrier-'+Path(n).stem+'.o') for n in m['source_units']];typed=[folder/('reply-ordered.o' if u['label']=='reply' else u['label']+'.o') for u in ctx['B']['units'](ctx,mode)]+[folder/'tx-entry.o',folder/'tx-valid_body-ordered.o',folder/'tx-return_leaf.o'];payloads=[];inputs=[]
    for group,paths in [('raw',rawpaths),('typed',typed)]:
        acc=b''
        for p in paths:
            e=E(p);s=e.byname.get('.llvm_addrsig')
            if s is None:need(p.name=='tx-entry.o','only raw assembler lacks excluded addrsig');continue
            need(s['type']==0x6fff4c03 and s['flags']==0x80000000 and s['link'] in e.symbol_tables,'actual excluded metadata with valid input symtab');data=e.data(s);at=0;roles=[]
            while at<len(data):
                index=shift=0
                while True:
                    need(at<len(data) and shift<=28,'bounded addrsig ULEB');b=data[at];at+=1;index|=(b&127)<<shift
                    if not b&128:break
                    shift+=7
                need(index<len(e.symbol_tables[s['link']]),'addrsig actual symbol-index bound');roles.append(V.role(e,e.symbol_tables[s['link']][index]))
            inputs.append(dict(path=p.name,payload=data.hex(),symbol_roles=roles));acc+=data
        payloads.append(acc)
    for name,wanted in [('raw-carriers.o',payloads[0]),('typed-providers.o',payloads[1]),('pre-frame-integrated.o',b''.join(payloads)),('source-integrated.o',b''.join(payloads))]:
        e=E(folder/name);s=e.byname['.llvm_addrsig'];need((s['type'],s['flags'],s['link'],s['info'])==(0x6fff4c03,0x80000000,0,0) and e.data(s)==wanted,'exact allinput excluded-metadata concatenation')
    need('.llvm_addrsig' not in E(folder/'ADDRESS-WITNESS-ONLY.elf').byname,'excluded metadata never exported');return dict(inputs=inputs,merged_bytes=len(b''.join(payloads)),excluded_from_linked_ELF=True)
def static_checks(folder,ctx,original,mode):
    E=ctx['ELF'];V=ctx['V'];m=ctx['manifest'];selected={r['name'] for r in m['selected_sections']}|{TX};raw=E(folder/'raw-carriers.o');V.metadata_gate(raw,ctx,set(m['allocations'])-selected);need(TX not in raw.byname,'raw TX section removed entirely, no raw-byte fallback');payloads=input_payloads(folder,ctx,mode);partial=merged_gate(E(folder/'pre-frame-integrated.o'),ctx,False);ordered=ctx['B']['frame_gate'](folder,ctx);merged=merged_gate(E(folder/'source-integrated.o'),ctx);txorder=tx_order_gate(folder,ctx);reply=ctx['B']['reply_gate'](folder,ctx);image=image_gate(folder,ctx,original);metadata=addrsig_gate(folder,ctx,mode)
    flash={};F=ctx['flash']
    for u in ctx['B']['units'](ctx,mode):
        if u['label'].startswith('flash-'):
            name=u['label'][6:];text=(folder/(u['label']+'.ll')).read_text();flash[name]=F['program_checker'].ir_program(text) if name=='program' else F['old_patterns'].ir_contract(name,text)
    N=runpy.run_path(str(case(ctx['root'],'v4160-ota-tx-2026-10-22')/'ABI-review/native.py'));txIR=N['ir_contract']((folder/'tx-valid_body.ll').read_text());leafIR=(folder/'tx-return_leaf.ll').read_text();need(len(re.findall(r'^define ',leafIR,re.M))==1 and 'ret i32 %0' in leafIR and 'i32 noundef returned %0, i32 noundef %1, i32 noundef %2, i32 noundef %3' in leafIR and not re.search(r'\b(call|asm)\b',leafIR),'real typed returning identity leaf IR, no unreachable surrogate')
    return dict(raw_retained_allocations=len(V.alloc(raw)),merged=merged,pre_frame=partial,old_frame_stage=ordered,reply_stage=reply,TX_frame_stage=txorder,TX_input_parts=payloads,image=image,excluded_metadata=metadata,LLVM_IRQ_IR=ctx['CF'].ir_gate(folder),LLVM_Flash_IR=flash,LLVM_TX_IR=txIR,whole_original_ABI_admitted=False,hardware=False,OTA_ready=False)
def expected_recipes(folder,ctx,mode,tools):
    root=ctx['root'];m=ctx['manifest'];B=ctx['B'];out=[]
    def add(label,args):out.append((label,[str(x) for x in args]))
    add('compiler-resource-dir',[tools['clang'],'-print-resource-dir']);groups=collections.defaultdict(dict)
    for r in m['selected_sections']:groups[r['producer']][r['name']]=r
    txsrc=next(n for n in m['source_units'] if n.endswith('/code_continuation_native.c'));groups[txsrc][TX]=dict(name=TX,global_alias='__tsl9v4160_call_8a56',bytes=280)
    for n in m['source_units']:
        original=root/n;src=folder/'filtered'/original.name if n in groups else original;target=folder/('carrier-'+original.stem+'.o')
        if n in groups:need(src.read_bytes()==B['filtered_source'](ctx,original.read_bytes(),groups[n]),'every exact selected quoted source filter, no source substitution')
        add('compile-'+original.stem,[tools['clang'],'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-fno-builtin','-fno-stack-protector','-Wall','-Wextra','-Werror','-x','c' if mode=='c' else 'c++','-std=c11' if mode=='c' else '-std=c++17','-I',original.parent,'-MD','-MF',target.with_suffix('.d'),'-MT',target.name,'-c',src,'-o',target])
    add('merge-raw-carriers',[tools['linker'],'-r','--no-relax',*[folder/('carrier-'+Path(n).stem+'.o') for n in m['source_units']],'-o',folder/'raw-carriers.o']);typed=[]
    for u in B['units'](ctx,mode):
        label=u['label'];ad=folder/(label+'-adapter.h');need(ad.read_bytes()==B['adapter'](u['rows']).encode(),'exact typed section and alias adapter');target=folder/(label+'.o')
        for kind,actions,suffix in [('object',['-c'],'.o'),('IR',['-S','-emit-llvm'],'.ll')]:
            deps=['-MD','-MF',target.with_suffix('.d'),'-MT',target.name] if kind=='object' else [];add('typed-'+label+'-'+kind,[tools['clang'],*u['flags'],'-include',ad,*deps,*actions,u['source'],'-o',folder/(label+suffix)])
        if label=='reply':add('explicit-reply-ordering',[tools['python'],'-B',ctx['reply']['ordering'],'--project-root',root,'--input',target,'--output',folder/'reply-ordered.o','--receipt',folder/'reply-order.json']);target=folder/'reply-ordered.o'
        typed.append(target)
    profile=runpy.run_path(str(case(root,'v4160-ota-tx-2026-10-22')/'implementation/verify_native.py'));native=root/'experiments/tsl9-v4160-tx-register-abi'
    for label in('valid_body','return_leaf'):
        for kind,actions,suffix in [('object',['-c'],'.o'),('IR',['-S','-emit-llvm'],'.ll')]:
            deps=['-MD','-MF',folder/('tx-'+label+'.d'),'-MT','tx-'+label+'.o'] if kind=='object' else [];add('tx-'+label+'-'+kind,[tools['clang'],*profile['flags'](mode),*deps,*actions,native/'adapter'/(label+'.c'),'-o',folder/('tx-'+label+suffix)])
    add('tx-entry-object',[tools['clang'],'--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-mno-relax','-x','assembler','-c',ctx['newmodel']/'adapter/entry.S','-o',folder/'tx-entry.o']);add('explicit-tx-frame-ordering',[tools['python'],'-B',HERE/'tx_order.py','--project-root',root,'--input',folder/'tx-valid_body.o','--output',folder/'tx-valid_body-ordered.o','--receipt',folder/'tx-frame-order.json']);typed += [folder/'tx-entry.o',folder/'tx-valid_body-ordered.o',folder/'tx-return_leaf.o'];add('merge-typed',[tools['linker'],'-r','--no-relax',*typed,'-o',folder/'typed-providers.o'])
    script=B['bindings_source'](ctx);needle='  KEEP(*('+TX+'))\n';script=script.replace(needle,needle+''.join('  KEEP(*('+n+'))\n' for n in('.text.tsl9_tx_entry','.text.tsl9_tx_valid_body','.text.tsl9_tx_oversized_return')));need((folder/'canonical53.ld').read_bytes()==script.encode(),'actual canonical53 layout with three exact TX source owners')
    add('merge-source-integrated',[tools['linker'],'-r','--no-relax','-T',folder/'canonical53.ld',folder/'raw-carriers.o',folder/'typed-providers.o','-o',folder/'pre-frame-integrated.o']);add('explicit-frame-scheduling',[tools['python'],'-B',ctx['scheduler'],'--project-root',root,'--input',folder/'pre-frame-integrated.o','--output',folder/'source-integrated.o','--receipt',folder/'frame-scheduling.json']);layout=root/'experiments/tsl9-v4160-reply-image-integration/original-image-layout.ld'
    add('strict-final-link',[tools['linker'],'--no-relax','--error-limit=0','-T',layout,folder/'source-integrated.o','-o',folder/'STRICT-MISSING-ROM.elf']);need((folder/'NUMERIC-ROM-WITNESS-ONLY.ld').read_bytes()==(B['ROM']+' = 0x40000;\n').encode(),'sole numeric witness script');add('numeric-witness-final-link',[tools['linker'],'--no-relax','-T',layout,'-T',folder/'NUMERIC-ROM-WITNESS-ONLY.ld',folder/'source-integrated.o','-o',folder/'ADDRESS-WITNESS-ONLY.elf']);add('export-new-offline-image',[tools['objcopy'],'-O','binary',folder/'ADDRESS-WITNESS-ONLY.elf',folder/IMAGE]);need(len(out)==67,'measured67 native and explicit scheduling recipes');return out
def command_gate(folder,ctx,mode,commands,tools):
    expected=expected_recipes(folder,ctx,mode,tools);need([(r['label'],r['argv']) for r in commands]==expected,'exact chronological67 source-only command recipes')
    for r in commands:
        need(sha(folder/r['log'])==r['sha256'],'actual command log identity');need(r['TMP']==r['TEMP']==str(folder/'compiler-temp'),'owned compiler temporary directory');need(r['exit']!=0 if r['label']=='strict-final-link' else r['exit']==0,'actual expected tool exit')
    need(not(folder/'STRICT-MISSING-ROM.elf').exists() and set(re.findall(r'undefined symbol: (\w+)',(folder/'strict-final-link.log').read_text()))=={ctx['B']['ROM']},'actual strict failure only missing ROM provider, no rejected output')
    return dict(commands=67,LLVM_commands=64,explicit_ABI_scheduling_commands=3,compile_TUs=46,raw_TUs=34,typed_C_TUs=11,raw_assembly_TUs=1,strict_missing_ROM_rejected=True)
def dependency_gate(folder,ctx,commands):
    declared=set();project=set();generated=set();resource=set();rules=[];root=ctx['root'];resource_directory=Path((folder/'compiler-resource-dir.log').read_text().strip()).resolve();need(resource_directory.is_dir(),'actual Clang resource-directory result')
    wanted={r['resource_relative']:r['sha256'] for r in ctx['manifest']['compiler_resource_header_inputs']}
    for r in commands:
        a=r['argv']
        if '-MD' not in a:continue
        dep=Path(a[a.index('-MF')+1]);target=a[a.index('-MT')+1];primary=Path(a[a.index('-c')+1]).resolve();adapter=Path(a[a.index('-include')+1]).resolve() if '-include' in a else None;paths=ctx['B']['dependency_rule'](dep,target,primary,adapter);declared.add(dep.resolve());observed=[]
        for p in paths:
            p=p.resolve();observed.append(str(p))
            if p.is_relative_to(folder):need(p.is_file() and (p.parent==folder/'filtered' or p.name.endswith('-adapter.h')),'only exact generated source/adapter dependency');generated.add(p.relative_to(folder).as_posix())
            elif p.is_relative_to(root):name=p.relative_to(root).as_posix();need(name in ctx['ledger']['source_files'] and sha(p)==ctx['ledger']['source_files'][name],'actual dependency matches source ledger');project.add(name)
            else:need(p.is_relative_to(resource_directory),'no undeclared external/system header');rel=p.relative_to(resource_directory).as_posix();need(rel in wanted and sha(p)==wanted[rel],'actual resource-relative standard header identity');resource.add((str(p),sha(p)))
        rules.append(dict(file=dep.name,target=target,primary=str(primary),adapter=str(adapter) if adapter else None,inputs=observed))
    need(declared=={p.resolve() for p in folder.glob('*.d')} and len(declared)==45,'exact45 source-associated MD rules, raw assembly explicitly has no preprocessing/MD')
    need(len(project)==78 and len(generated)==14 and len(resource)==1,'measured78 existing project/14 generated/one observed resource closure')
    return dict(MD_rules=rules,existing_project_inputs=sorted(project),generated_inputs=sorted(generated),resource_inputs=[dict(path=p,sha256=s) for p,s in sorted(resource)],assembly_source=str(ctx['newmodel']/'adapter/entry.S'),assembly_preprocessing=False)
def snapshot(root,ctx,tools,firmware):
    pins=ctx['B']['snapshot'](root,ctx,tools,firmware);pins.update({str(root/n):s for n,s in ctx['ledger']['source_files'].items()});pins.update({str(root/n):s for n,s in ctx['ledger']['TX_order_sources'].items()})
    for p in [HERE/'prototype.py',HERE/'tx_order.py',Path(__file__),ctx['newmodel']/'source-manifest.json',ctx['newmodel']/'original-image-layout.ld',portable(root,ctx['ledger']['TX_original_source']['path'])]:pins[str(p.resolve())]=sha(p)
    native=case(root,'v4160-tx-register-abi-2026-10-22')/'implementation'
    for p in(native/'seal.json',native/'receipts/native-c.json',native/'receipts/native-cpp.json'):pins[str(p.resolve())]=sha(p)
    for n,pin in read(native/'receipts/native-c.json')['source_pins'].items():p=portable(root,n);need(sha(p)==pin,'sealed TX profile/source/parser/ABI proof input');pins[str(p.resolve())]=pin
    ctx['V'].stability(pins);return pins
def negative_controls(folder,ctx,original,mode,create=True,recorded=None):
    E=ctx['ELF'];obj=E(folder/'source-integrated.o');linked=E(folder/'ADDRESS-WITNESS-ONLY.elf');output=folder/'negative-controls';rows=[]
    if create:output.mkdir()
    def symoff(e,name):
        for s in e.sections:
            if s['type']==2:
                for i,r in enumerate(e.symbol_tables[s['index']]):
                    if r['name']==name:return s['offset']+i*16
        raise ValueError('actual negative symbol unavailable')
    for tag in('canonical_FUNC280','canonical_ABS','body_GLOBAL','leaf_wrong_offset','TX_code_byte','outside_storage_byte','outside_RELA_addend','TX_HI_addend','private_anchor_ABS','missing_RELA','extra_ALLOC','linked_TX_byte','linked_wrong_VA','LOAD_wrong_permission','image_outside_TX','image_wrong_TX','image_truncated'):
        image=tag.startswith('image_');is_linked=tag.startswith('linked_') or tag.startswith('LOAD_');e=linked if is_linked else obj;raw=bytearray((folder/IMAGE).read_bytes() if image else e.raw)
        def field(s,delta,value):struct.pack_into('<I',raw,struct.unpack_from('<I',raw,32)[0]+s['index']*40+delta,value)
        if tag=='canonical_FUNC280':struct.pack_into('<I',raw,symoff(e,'__tsl9v4160_call_8a56')+8,280)
        elif tag=='canonical_ABS':struct.pack_into('<H',raw,symoff(e,'__tsl9v4160_call_8a56')+14,0xfff1)
        elif tag=='body_GLOBAL':s=next(s for s in e.symbols if s['info']==2 and s['index']==e.byname[TX]['index']);raw[symoff(e,s['name'])+12]=18
        elif tag=='leaf_wrong_offset':struct.pack_into('<I',raw,symoff(e,'tsl9_tx_oversized_return')+4,276)
        elif tag in('TX_code_byte','linked_TX_byte'):raw[e.byname[TX]['offset']+16]^=1
        elif tag=='outside_storage_byte':raw[e.byname['.text.tsl9v4160.image_entry']['offset']]^=1
        elif tag=='private_anchor_ABS':struct.pack_into('<H',raw,symoff(e,'.Lpcrel_hi0')+14,0xfff1)
        elif tag in('outside_RELA_addend','TX_HI_addend','missing_RELA'):
            s=next(s for s in e.sections if s['type']==4 and s['size'] and((e.sections[s['info']]['name']==TX)==(tag=='TX_HI_addend')))
            if tag=='missing_RELA':field(s,20,s['size']-12)
            else:struct.pack_into('<i',raw,s['offset']+8,2)
        elif tag=='extra_ALLOC':s=e.byname['.comment'];field(s,8,s['flags']|2)
        elif tag=='linked_wrong_VA':field(e.byname[TX],12,0x8a58)
        elif tag=='LOAD_wrong_permission':at=struct.unpack_from('<I',raw,28)[0];struct.pack_into('<I',raw,at+24,7)
        elif tag=='image_outside_TX':raw[0]^=1
        elif tag=='image_wrong_TX':raw[0xa56+4]^=1
        elif tag=='image_truncated':raw=raw[:-1]
        path=output/(tag+('.bin' if image else '.elf' if is_linked else '.o'))
        if create:path.write_bytes(raw)
        else:need(path.read_bytes()==bytes(raw),'exact retained actual negative payload')
        try:
            if image:image_gate(folder,ctx,original,image_override=path)
            elif is_linked:image_gate(folder,ctx,original,linked_override=E(path))
            else:merged_gate(E(path),ctx)
        except (ValueError,AssertionError) as error:reason=str(error)
        else:raise ValueError('accepted actual ELF/RELA/image negative '+tag)
        rows.append(dict(case=tag,path=path.relative_to(folder).as_posix(),sha256=sha(path),rejected=True,reason=reason))
    if recorded is not None:need(rows==recorded,'actual negative-control replay')
    return rows
def provenance_controls(folder,ctx,mode,commands,tools,create=True,recorded=None):
    rows=[];positive=read(folder/'tx-frame-order.json')
    for tag in('tx-order-input','tx-order-policy','tx-order-compiler-only','recipe-chronology','recipe-language','dependency-target','dependency-primary'):
        path=folder/'negative-controls'/(tag+('.d' if tag.startswith('dependency') else '.json'));altered=None
        if tag.startswith('tx-order'):
            altered=json.loads(json.dumps(positive))
            if tag=='tx-order-input':altered['input']['sha256']='0'*64
            elif tag=='tx-order-policy':altered['source_pins'][next(k for k in altered['source_pins'] if k.endswith('policy.json'))]='0'*64
            else:altered['compiler_only']=True
            payload=(json.dumps(altered,indent=2)+'\n').encode()
        elif tag.startswith('recipe'):
            altered=json.loads(json.dumps(commands))
            if tag=='recipe-chronology':i=next(i for i,r in enumerate(altered) if r['label']=='explicit-tx-frame-ordering');altered[i],altered[i+1]=altered[i+1],altered[i]
            else:r=next(r for r in altered if r['label']=='tx-valid_body-object');i=r['argv'].index('-std=c11' if mode=='c' else '-std=c++17');r['argv'][i]='-std=c99'
            payload=(json.dumps(altered,indent=2)+'\n').encode()
        else:
            source=folder/'tx-valid_body.d';text=source.read_text();payload=(text.replace('tx-valid_body.o:', 'wrong.o:',1) if tag=='dependency-target' else text.replace('valid_body.c','return_leaf.c',1)).encode();need(payload!=source.read_bytes(),'meaningful actual .d association mutation')
        if create:path.write_bytes(payload)
        else:need(path.read_bytes()==payload,'actual retained provenance control bytes')
        try:
            if tag.startswith('tx-order'):tx_order_gate(folder,ctx,path)
            elif tag.startswith('recipe'):command_gate(folder,ctx,mode,altered,tools)
            else:ctx['B']['dependency_rule'](path,'tx-valid_body.o',ctx['root']/'experiments/tsl9-v4160-tx-register-abi/adapter/valid_body.c',None)
        except(ValueError,AssertionError) as error:reason=str(error)
        else:raise ValueError('accepted provenance negative '+tag)
        rows.append(dict(case=tag,path=path.relative_to(folder).as_posix(),sha256=sha(path),rejected=True,reason=reason))
    if recorded is not None:need(rows==recorded,'actual provenance control replay')
    return rows
def invocation_gate(root,folder,ctx,r,tools,firmware):
    base=folder.parent;g=r['generation_invocation'];q=r['preflight_query'];a=g['argv'];need(len(a)==13 and a[:5]==[str(tools['python']),'-B',str(HERE/'prototype.py'),'--project-root',str(root)],'exact fresh source generation invocation entry')
    need(a[5]=='--tool-dir' and Path(a[6]).resolve().is_dir() and a[7]=='--language' and a[8] in(r['mode'],'both') and a[9:]==['--build-root',str(base),'--firmware',str(firmware)],'exact generator tool/language/owned-build/original-validation arguments')
    for k,n in [('clang','clang'),('linker','ld.lld'),('objcopy','llvm-objcopy')]:need(ctx['V'].resolve_tool(None,Path(a[6]),n)==tools[k],'generator resolves actual declared native tool')
    for record,name,argv in [(g,'fresh-generation.log',a),(q,'preflight-resource-query.log',[str(tools['clang']),'-print-resource-dir'])]:
        need(record['argv']==argv and record['exit']==0 and Path(record['log']).resolve()==base/name and sha(base/name)==record['sha256'],'actual successful parent generation/query command and bounded log identity')
    result=json.loads((base/'fresh-generation.log').read_bytes());need(result['passed'] and {x['mode'] for x in result['results']}==({'c','cpp'} if a[8]=='both' else {a[8]}),'actual generator JSON language result set')
    for item in result['results']:
        f=base/item['mode'];need(Path(item['receipt']).resolve()==f/'prototype.json' and sha(f/'prototype.json')==item['sha256'] and Path(item['image']).resolve()==f/IMAGE and sha(f/IMAGE)==item['image_sha256'],'actual generator emitted receipt and image association')
    directory=Path((base/'preflight-resource-query.log').read_text().strip()).resolve();need(directory==Path((folder/'compiler-resource-dir.log').read_text().strip()).resolve(),'before-compile resource discovery equals observed native resource query')
    return dict(source_generation_subprocesses=1,preflight_resource_queries=1,source_generation_native_recipes=67,query_and_generation_logs_replayed=True)
def replay(root,receipt,firmware=None):
    root=root.resolve();receipt=receipt.resolve();r=read(receipt);folder=receipt.parent;ctx=context(root,firmware);fw,original=ctx['B']['original_image'](root,ctx,firmware);need(r['passed'] and r['mode'] in('c','cpp') and r['manifest_sha256']==MANIFEST and r['runner_sha256']==sha(Path(__file__)) and r['firmware_sha256']==sha(fw),'current producer/manifest/original validation input');tools={k:Path(v['path']) for k,v in r['tools'].items()};need(set(tools)=={'clang','linker','objcopy','python'},'exact declared native tools and Python')
    for k,p in tools.items():need(sha(p)==r['tools'][k]['sha256'],'actual current compiler/linker/objcopy/Python binary identity')
    pins=snapshot(root,ctx,tools,fw);deps=dependency_gate(folder,ctx,r['commands']);pins.update({x['path']:x['sha256'] for x in deps['resource_inputs']});need(pins==r['input_stability_pins'],'all current exact source/tool/proof/resource inputs')
    need(set(r['artifacts'])=={p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file() and p!=receipt},'complete exact current artifact inventory, no missing IR/dependency/log pins')
    for name,proof in r['artifacts'].items():
        p=(folder/name).resolve();need(p.is_relative_to(folder) and p.stat().st_size==proof['bytes'] and sha(p)==proof['sha256'],'actual artifact/log/source dependency/image identity')
    invocation_gate(root,folder,ctx,r,tools,fw);checks=static_checks(folder,ctx,original,r['mode']);checks['dependencies']=deps;checks['recipes']=command_gate(folder,ctx,r['mode'],r['commands'],tools);negative_controls(folder,ctx,original,r['mode'],False,r['actual_artifact_controls']);provenance_controls(folder,ctx,r['mode'],r['commands'],tools,False,r['actual_provenance_controls']);need(json.loads(json.dumps(checks))==r['checks'],'all actual image/ELF/roles/stages/provenance replayed, no stored passed-flag shortcut')
    return dict(passed=True,receipt=str(receipt),sha256=sha(receipt),artifacts_checked=len(r['artifacts']),compile_TUs=46,RELA=checks['merged']['RELA'],image_sha256=checks['image']['sha256'],TX_difference_bytes=len(checks['image']['differences']),outside_TX_identical=True,whole_original_ABI_admitted=False,target_execution=False,flashable=False)
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=HERE.parents[2]);p.add_argument('--tool-dir',type=Path);p.add_argument('--firmware',type=Path);p.add_argument('--language',choices=['c','cpp','both'],default=None);p.add_argument('--build-root',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
    if a.replay:need(not any((a.tool_dir,a.language,a.build_root)),'fresh-build overrides forbidden during read-only replay');print(json.dumps(replay(root,a.replay,a.firmware)));return
    need(a.tool_dir is not None,'fresh compilation requires explicit local LLVM tool directory');ctx=context(root,a.firmware);mode=a.language or 'both';V=ctx['V'];fw,original=ctx['B']['original_image'](root,ctx,a.firmware);tools={k:V.resolve_tool(None,a.tool_dir,n) for k,n in [('clang','clang'),('linker','ld.lld'),('objcopy','llvm-objcopy')]};tools['python']=Path(sys.executable).resolve();base=a.build_root.resolve() if a.build_root else root/MODEL/'build'/('native-'+uuid.uuid4().hex);need(not base.exists() and base.is_relative_to(root/MODEL/'build'),'create-only new owned build root')
    pins=snapshot(root,ctx,tools,fw);query=subprocess.run([str(tools['clang']),'-print-resource-dir'],capture_output=True,timeout=30);need(query.returncode==0,'actual preflight resource query');resource_dir=Path(query.stdout.decode().strip()).resolve();resource=resource_dir/'include/stdint.h';need(sha(resource)==ctx['manifest']['compiler_resource_header_inputs'][0]['sha256'],'actual resource header before compilation');pins[str(resource)]=sha(resource)
    argv=[str(tools['python']),'-B',str(HERE/'prototype.py'),'--project-root',str(root),'--tool-dir',str(a.tool_dir.resolve()),'--language',mode,'--build-root',str(base),'--firmware',str(fw)];x=subprocess.run(argv,cwd=root,capture_output=True,timeout=1800);need(base.is_dir(),'fresh generator build directory');(base/'fresh-generation.log').write_bytes(x.stdout+x.stderr);(base/'preflight-resource-query.log').write_bytes(query.stdout+query.stderr);need(x.returncode==0,'fresh source generation failed; actual log retained');generated=json.loads(x.stdout);need(generated['passed'],'fresh actual generator result');V.stability(pins);results=[]
    for selected in generated['results']:
        folder=Path(selected['receipt']).parent;proto=read(folder/'prototype.json');language=proto['mode'];checks=static_checks(folder,ctx,original,language);checks['dependencies']=dependency_gate(folder,ctx,proto['commands']);checks['recipes']=command_gate(folder,ctx,language,proto['commands'],tools);controls=negative_controls(folder,ctx,original,language);provenance=provenance_controls(folder,ctx,language,proto['commands'],tools);V.stability(pins)
        r=dict(schema='TSL9-thirteen-region-source-image-v1',passed=True,mode=language,manifest_sha256=MANIFEST,runner_sha256=sha(Path(__file__)),firmware_sha256=sha(fw),input_stability_pins=pins,checks=checks,commands=proto['commands'],actual_artifact_controls=controls,actual_provenance_controls=provenance,artifacts={p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in folder.rglob('*') if p.is_file()},tools={k:dict(path=str(v),sha256=sha(v)) for k,v in tools.items()},generation_invocation=dict(argv=argv,exit=x.returncode,log=str(base/'fresh-generation.log'),sha256=sha(base/'fresh-generation.log')),preflight_query=dict(argv=[str(tools['clang']),'-print-resource-dir'],exit=query.returncode,log=str(base/'preflight-resource-query.log'),sha256=sha(base/'preflight-resource-query.log')),compiler_only=False,whole_original_ABI_admitted=False,target_execution=False,emulation=False,network=False,hardware=False,ROM_provider=False,flashable=False,OTA_ready=False);write(folder/'verification.json',r);results.append(dict(mode=language,receipt=str(folder/'verification.json'),sha256=sha(folder/'verification.json'),image=str(folder/IMAGE),image_sha256=sha(folder/IMAGE)))
    if len(results)==2:need(results[0]['image_sha256']==results[1]['image_sha256'],'C11/C++17 images byte-identical')
    write(base/'formal-results.json',dict(results=results));print(json.dumps(dict(passed=True,results=results,whole_original_ABI_admitted=False,flashable=False,OTA_ready=False)))
if __name__=='__main__':main()
