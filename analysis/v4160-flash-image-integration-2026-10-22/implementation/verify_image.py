"""Fresh source-only eleven-function offline image integration; no RV32 execution."""
import argparse,collections,hashlib,importlib.util,json,os,re,shlex,struct,uuid
from pathlib import Path
H=Path(__file__).resolve().parent;MODEL='experiments/tsl9-v4160-flash-image-integration';ROM='__tsl9v4160_rom_entry';IMAGE='NOT-FLASH-VALIDATED-irq-and-flash.bin'
MANIFEST_SHA='afe5eba6e7b6af15c9556fa9c9a366e5c4713dcbf343b16d2d8077eb6c1b4b1c'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,d):p.write_bytes((json.dumps(d,indent=2)+'\n').encode())
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def case(root,slug):return next(p for p in (root/'analysis'/slug,root/'apk-analysis'/('tsl9-'+slug)) if p.is_dir())
def context(root):
    root=Path(root).resolve();model=root/MODEL;need(sha(model/'source-manifest.json')==MANIFEST_SHA,'portable eleven-function source ledger');m=read(model/'source-manifest.json');need(sha(model/'original-image-layout.ld')==m['layout_sha256'],'original691 layout')
    old=case(root,'v4160-irq-image-integration-2026-10-21')/'integration/verify_image.py';need(sha(old)=='1929598ffc723937e8cd6bcafbe507fb5ff23f6d9541f00043bdadcb44f3455a','immutable generic storage helpers');V=module('eleven_original_layout_helpers',old);ctx=V.context(root)
    flash_path=case(root,'v4160-flash-entry-order-2026-10-22')/'implementation/verify_native.py';need(sha(flash_path)=='0f96c209bb486581056ea3b68fbe4581dfeb4ff48fc03cba9a07e2e80dd7fa89','frozen100B native compiler/checker');F=module('eleven_flash_native_helpers',flash_path);f=F.context(root)
    for n,pin in m['source_files'].items():need(sha(root/n)==pin,'pinned source/header '+n)
    plan=case(root,'v4160-flash-entry-order-2026-10-22')/'image-plan';need(sha(plan/'seal.json')==m['entry_order_plan_seal_sha256'],'sealed eleven-owner plan')
    for r in read(plan/'seal.json')['members']:need(sha(plan/r['path'])==r['sha256'],'plan member')
    ctx.update(root=root,V=V,manifest=m,model=model,Flash=F,flash=f,native_code_sha256={r['new_C_symbol']:r['native_object_sha256'] for r in m['selected_sections']},plan_retained=m['retained_storage'])
    return ctx
def units(ctx,mode):
    root=ctx['root'];rows=ctx['manifest']['selected_sections'];result=[]
    for label,name,main in [('main','interrupt_callframe.c',True),('helpers','rcc_helpers.c',False)]:result.append(dict(label=label,source=root/'experiments/tsl9-v4160-irq-callframe/src'/name,flags=ctx['CF'].profile_flags(ctx['cf'],mode,main),rows=[r for r in rows if r['family']=='IRQ' and (r['bytes']==144)==main]))
    for address,(name,limit,allowed) in ctx['flash']['profile'].NAMES.items():result.append(dict(label='flash-'+name,source=root/'experiments/tsl9-v4160-flash-entry-order/src/flash_native.c',flags=ctx['flash']['profile'].flags(address,mode),rows=[r for r in rows if r['family']=='Flash' and r['originalVA']==address]))
    need(len(result)==8 and sum(len(x['rows']) for x in result)==11,'eight typed source units eleven functions');return result
def adapter(rows):
    text='#include <stdint.h>\n#ifdef __cplusplus\nextern "C" {\n#endif\n'
    for r in rows:
        n=r['new_C_symbol'];params='void' if r['originalVA']==0x9a42 else ('uint32_t a0,uint32_t a1' if r['family']=='IRQ' or r['originalVA'] in (0x9c0a,0x18ef2) else 'uint32_t a0')
        text+='uint32_t '+n+'('+params+') __attribute__((section("'+r['name']+'"),used,noinline));\nextern __typeof__('+n+') '+r['global_alias']+' __attribute__((alias("'+n+'")));\n'
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
    V=ctx['V'];m=ctx['manifest'];names={r['name'] for r in m['selected_sections']};V.metadata_gate(e,ctx,names);expected=[]
    for r in m['selected_sections']:
        need(hashlib.sha256(e.data(e.byname[r['name']])).hexdigest()==r['native_object_sha256'],'typed body exactly sealed actual native component '+r['new_C_symbol'])
        expected.extend(dict(name=n,owner=r['name'],offset=0,bytes=r['bytes'],info=18,other=0) for n in (r['new_C_symbol'],r['global_alias']))
    need(V.counter([r for r in V.globals_(e) if r['owner']!='UND'])==V.counter(expected),'exact eleven original FUNC aliases plus eleven public typed FUNCs')
    return dict(functions=11,bytes=526,original_FUNC_aliases=11,public_C_FUNCs=11)
def branch_discharge(e,ctx):
    m=ctx['manifest'];V=ctx['V'];outside=[V.relocation(e,r) for r in e.relocations if r['owner'] not in {x['name'] for x in m['selected_sections']}];result=[]
    for r in m['old_selected_RELA']:
        if r['type'] not in (16,44):continue
        owner=next(x for x in m['selected_sections'] if x['name']==r['owner']);target=r['symbol'];need(target['owner']==r['owner'] and not r['addend'] and target['info']==target['bytes']==target['other']==0,'exact old private self-branch role')
        need(not any(x['symbol']['name']==target['name'] for x in outside),'no recorded outside branch-label references')
        old=bytes.fromhex(r['original_branch_bytes']);native=e.data(e.byname[r['owner']])[r['offset']:r['offset']+len(old)];a=branch(old,r['offset']);b=branch(native,r['offset'])
        need(a['target']==b['target']==target['offset'] and a['width']==b['width']==(2 if r['type']==44 else 4) and a['condition']==b['condition'] and a['rs2']==b['rs2'],'exact branch PC/type/target and zero-or-register condition role')
        need(not any(s['name']==target['name'] for s in e.symbols),'old private label is discharged, never numeric alias/provider')
        result.append(dict(original_RELA=r,original_branch_bytes=old.hex(),native_branch_bytes=native.hex(),original_decoded=a,native_decoded=b,recorded_outside_references=0,full_GPR_prefix_equivalence=False))
    need(len(result)==10 and sum('direct_closure' in r['original_RELA']['owner'] for r in result)==6,'four IRQ and six Flash private branch roles exactly discharged');return result
def merged_gate(e,ctx):
    V=ctx['V'];m=ctx['manifest'];selected={r['name'] for r in m['selected_sections']};need(e.kind==1 and e.flags==1 and V.und(e)=={ROM},'partial RV32 RVC ELF and sole ROM UND');result=V.metadata_gate(e,ctx,m['allocations'])
    for n,proof in m['retained_storage'].items():need(hashlib.sha256(V.data(e,e.byname[n])).hexdigest()==proof['sha256'],'all680 original partial-storage digests')
    for r in m['selected_sections']:need(hashlib.sha256(e.data(e.byname[r['name']])).hexdigest()==r['native_object_sha256'],'all eleven typed partial bodies')
    outside=[V.relocation(e,r) for r in e.relocations if r['owner'] not in selected];need(len(outside)==8259 and V.digest(sorted(outside,key=lambda x:json.dumps(x,sort_keys=True)))==m['retained_RELA_semantic_sha256'],'all8259 outside RELA roles/sites/types/addends/multiplicities')
    owned=[V.relocation(e,r) for r in e.relocations if r['owner'] in selected];wanted=[]
    for r in m['old_selected_RELA']:
        if r['type']!=17:continue
        r=json.loads(json.dumps(r));target=next(x for x in m['selected_sections'] if x['global_alias']==r['symbol']['name']);r['symbol']['name']=target['new_C_symbol'];wanted.append(r)
    need(V.counter(owned)==V.counter(wanted) and len(owned)==11,'exact eleven source-site JALs, no branch RELA or hidden helper records')
    for b in m['section_relative_bindings']:need(V.counter([V.role(e,s) for s in e.symbols if s['name']==b['name']])==V.counter([b['role']]),'all53 canonical relative binding roles')
    discharge=branch_discharge(e,ctx);before,oldmeta=V.normalized_symbols(m['baseline_symbol_roles'],[r['original_RELA']['symbol'] for r in discharge]);after,newmeta=V.normalized_symbols([V.role(e,s) for s in e.symbols]);extra=[dict(name=r['new_C_symbol'],owner=r['name'],offset=0,bytes=r['bytes'],info=18,other=0) for r in m['selected_sections']]
    need(V.counter(after)==V.counter(before+extra),'every nonmetadata original role preserved except exact ten discharged locals plus eleven new FUNCs')
    need(V.counter([r for r in oldmeta if r['info']&15==3])==V.counter([r for r in newmeta if r['info']&15==3]),'all original SECTION role metadata')
    def mapping(rows,owner=None,retained=False):return V.counter([{**r,'name':r['name'].split('.')[0]} for r in rows if re.fullmatch(r'\$[dx]\.\d+',r['name']) and (r['owner']==owner if owner else r['owner'] not in selected and r['owner'] not in ('ABS','.comment'))])
    need(mapping(oldmeta)==mapping(newmeta),'all retained allocated mapping roles modulo measured assembler ordinals')
    files=[dict(name=n,owner='ABS',offset=0,bytes=0,info=4,other=0) for n in ['interrupt_callframe.c','rcc_helpers.c']+['flash_native.c']*6]
    need(V.counter([r for r in newmeta if r['info']&15==4])==V.counter([r for r in oldmeta if r['info']&15==4]+files),'34 retained plus eight actual typed FILE records')
    for owner in ('ABS','.comment'):
        expected=mapping(oldmeta,owner)+V.counter([dict(name='$d',owner=owner,offset=0,bytes=0,info=0,other=0)]*8);need(mapping(newmeta,owner)==expected,'exact measured eight typed nonstorage '+owner+' markers')
    maps=[r for r in newmeta if re.fullmatch(r'\$[dx]\.\d+',r['name']) and r['owner'] in selected];need(len(maps)==11 and all(r['name'].startswith('$x.') and r['offset']==r['bytes']==r['info']==r['other']==0 for r in maps),'one instruction mapping per typed section')
    need(not any(r['symbol']['index']==0xfff1 and r['symbol']['name'].startswith('$d.') for r in e.relocations),'metadata ABS mappings are never providers')
    incoming=[r for r in outside if r['symbol']['owner'] in selected];need(V.counter(incoming)==V.counter(m['external_incoming_RELA']) and len(incoming)==20 and all(r['symbol']['offset']==0 for r in incoming),'all twenty original incoming entry references')
    need(len(e.relocations)==len(outside)+len(owned),'measured full relocation partition')
    return dict(**result,retained_storage_sections=680,RELA=len(e.relocations),outside_RELA=len(outside),owned_RELA=len(owned),discharged_branches=discharge,canonical_relative_bindings=53,incoming_RELA=20,old_metadata=oldmeta,new_metadata=newmeta)
def image_gate(path,e,ctx,original):
    r=ctx['V'].image_gate(path,e,ctx,original)
    for item in ctx['manifest']['selected_sections']:need(e.data(e.byname[item['name']])==bytes.fromhex(item['native_linked_bytes']),'all eleven linked bodies exactly sealed linked native bytes')
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
    r.update(differences_from_previous_IRQ_image=ctx['manifest']['differences_from_previous_IRQ_image'],LOAD_memory_coverage=loads,LOAD_mapped_memory_bytes=len(actual),extra_mapped_memory_bytes=0);return r
def static_checks(folder,ctx,original):
    V=ctx['V'];E=ctx['ELF'];m=ctx['manifest'];selected={r['name'] for r in m['selected_sections']};raw=E(folder/'raw-carriers.o');V.metadata_gate(raw,ctx,set(m['allocations'])-selected);typed=selected_gate(E(folder/'typed-providers.o'),ctx);merged=merged_gate(E(folder/'source-integrated.o'),ctx);linked=E(folder/'ADDRESS-WITNESS-ONLY.elf');layout=V.linked_gate(linked,ctx);image=image_gate(folder/IMAGE,linked,ctx,original)
    F=ctx['flash'];ir={};attributes=[];T=E(folder/'typed-providers.o')
    for u in units(ctx,'c'):
        unit=E(folder/(u['label']+'.o'));markers=[V.role(unit,s) for s in unit.symbols if s['name'].startswith('$d.') and 0<s['index']<len(unit.sections) and unit.sections[s['index']]['name']=='.riscv.attributes'];need(len(markers)==1 and all(markers[0][k]==v for k,v in dict(offset=0,bytes=0,info=0,other=0).items()),'one actual typed input attribute marker')
        attributes.append(dict(unit=u['label'],input=markers[0],merged_role={**markers[0],'owner':'ABS'}))
        if u['label'].startswith('flash-'):
            name=u['label'][6:];text=(folder/(u['label']+'.ll')).read_text(encoding='utf-8');ir[name]=F['program_checker'].check_program_ir(text) if name=='program' else F['old_patterns'].ir_contract(name,text)
    normalize=lambda rows:V.counter([{**r,'name':'$d'} for r in rows]);actual_abs=[V.role(T,s) for s in T.symbols if s['name'].startswith('$d.') and s['index']==0xfff1]
    need(normalize(actual_abs)==normalize([r['merged_role'] for r in attributes]),'eight actual input attributes markers become eight exact unreferenced ABS metadata roles')
    return dict(raw_allocations=680,typed=typed,typed_attribute_origins=attributes,merged=merged,linked=layout,image=image,LLVM_IRQ_IR=ctx['CF'].ir_gate(folder),LLVM_Flash_IR=ir,pointwise_equivalence=False,asynchronous_equivalence=False,ROM_provider=False,physical_compatibility=False,OTA_ready=False,target_execution=False)
def build(root,folder,ctx,tools,mode,original):
    V=ctx['V'];m=ctx['manifest'];folder.mkdir(parents=True);filtered=folder/'filtered';filtered.mkdir();commands=[];objects=[];changes=[];groups=collections.defaultdict(dict)
    for r in m['selected_sections']:groups[r['producer']][r['name']]=r
    for n in m['source_units']:
        original_source=root/n;source=original_source
        if n in groups:
            source=filtered/source.name;source.write_bytes(V.filtered_source(original_source.read_bytes(),groups[n]));proof=next(r for r in m['filtered_carrier_units'] if r['path']==n);need(sha(source)==proof['filtered_sha256'],'exact four source filters');changes.append(dict(source=n,original_sha256=sha(original_source),filtered_sha256=sha(source),removed_sections=sorted(groups[n])))
        out=folder/('carrier-'+source.stem+'.o');argv=[tools['clang'],'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-fno-builtin','-fno-stack-protector','-Wall','-Wextra','-Werror','-x','c' if mode=='c' else 'c++','-std=c11' if mode=='c' else '-std=c++17','-I',original_source.parent,'-MMD','-MF',out.with_suffix('.d'),'-MT',out.name,'-c',source,'-o',out];r,_=V.run(argv,folder,'compile-'+source.stem);commands.append(r);objects.append(out)
    r,_=V.run([tools['linker'],'-r','--no-relax',*objects,'-o',folder/'raw-carriers.o'],folder,'merge-raw-carriers');commands.append(r);typed=[]
    for unit in units(ctx,mode):
        label=unit['label'];ad=folder/(label+'-adapter.h');ad.write_bytes(adapter(unit['rows']).encode());out=folder/(label+'.o')
        for kind,action,dest in [('object',['-c'],out),('IR',['-S','-emit-llvm'],folder/(label+'.ll'))]:
            deps=['-MMD','-MF',out.with_suffix('.d'),'-MT',out.name] if kind=='object' else [];r,_=V.run([tools['clang'],*unit['flags'],'-include',ad,*deps,*action,unit['source'],'-o',dest],folder,'typed-'+label+'-'+kind);commands.append(r)
        typed.append(out)
    r,_=V.run([tools['linker'],'-r','--no-relax',*typed,'-o',folder/'typed-providers.o'],folder,'merge-typed');commands.append(r);selected_gate(ctx['ELF'](folder/'typed-providers.o'),ctx)
    script=folder/'canonical53.ld';script.write_bytes(V.bindings_source(m).encode());r,_=V.run([tools['linker'],'-r','--no-relax','-T',script,folder/'raw-carriers.o',folder/'typed-providers.o','-o',folder/'source-integrated.o'],folder,'merge-source-integrated');commands.append(r)
    # Publish a diagnostic inventory before strict admission so blockers are inspectable.
    e=ctx['ELF'](folder/'source-integrated.o');write(folder/'first-inventory.json',dict(allocations=len(V.alloc(e)),RELA=len(e.relocations),UND=sorted(V.und(e)),typed_compile_TUs=8,raw_compile_TUs=34,commands=commands));merged_gate(e,ctx)
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
def dependency_gate(root,folder,ctx):
    files=list(folder.glob('*.d'));specs=dependency_specs(root,folder,ctx);need(len(files)==42 and {p.name for p in files}==set(specs),'exact42 compiler dependency files/compile associations');seen=set();generated=set();rules=[]
    for path in files:
        target,primary,ad=specs[path.name];paths=dependency_rule(path,target,primary,ad);rules.append(dict(file=path.name,target=target,primary_source=primary.relative_to(root).as_posix(),adapter=ad.relative_to(root).as_posix() if ad else None))
        for p in paths:
            need(p.is_relative_to(root),'no nonproject dependency in non-system MMD closure')
            if p.is_relative_to(folder.resolve()):generated.add(p.relative_to(folder).as_posix())
            else:
                name=p.relative_to(root).as_posix();need(name in ctx['manifest']['source_files'] and sha(p)==ctx['manifest']['source_files'][name],'all native includes pinned, no HOST path');seen.add(name)
    filtered={r['producer'] for r in ctx['manifest']['selected_sections']};wanted=set(ctx['manifest']['source_files'])-filtered
    generated_wanted={'filtered/'+Path(n).name for n in filtered}|{u['label']+'-adapter.h' for u in units(ctx,'c')}
    need(seen==wanted and generated==generated_wanted and len(seen)==72 and len(generated)==12,'exact72 original inputs and12 generated filtered/adapter inputs')
    return dict(compile_TUs=42,dependency_rules=42,rule_associations=sorted(rules,key=lambda r:r['file']),non_system_pinned_project_files=72,generated_inputs=sorted(generated),compiler_resource_headers_included=False)
def snapshot(root,ctx,tools,firmware):
    pins=ctx['V'].snapshot(root,ctx,tools);pins.update(ctx['flash']['pins'])
    for p in (Path(__file__).resolve(),ctx['model']/'prepare_manifest.py',firmware):pins[str(p.resolve())]=sha(p)
    for slug,sub in [('v4160-flash-entry-order-2026-10-22','image-plan'),('v4160-flash-entry-order-2026-10-22','implementation')]:
        base=case(root,slug)/sub;pins[str(base/'seal.json')]=sha(base/'seal.json')
        for row in read(base/'seal.json')['members']:pins[str(base/row['path'])]=row['sha256']
    ctx['V'].stability(pins);return pins
def command_gate(root,folder,ctx,mode,commands,tools):
    V=ctx['V'];m=ctx['manifest'];labels={r['label']:r for r in commands};need(len(labels)==len(commands)==56,'exact56 source compile/IR/link/export invocations')
    filtered={r['producer'] for r in m['selected_sections']}
    for name in m['source_units']:
        original=root/name;source=folder/'filtered'/original.name if name in filtered else original;out=folder/('carrier-'+original.stem+'.o')
        argv=[str(tools['clang']),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-fno-builtin','-fno-stack-protector','-Wall','-Wextra','-Werror','-x','c' if mode=='c' else 'c++','-std=c11' if mode=='c' else '-std=c++17','-I',str(original.parent),'-MMD','-MF',str(out.with_suffix('.d')),'-MT',out.name,'-c',str(source),'-o',str(out)]
        need(labels['compile-'+original.stem]['argv']==argv,'exact raw-carrier source/profile/output')
        if name in filtered:
            rows={r['name']:r for r in m['selected_sections'] if r['producer']==name};need(source.read_bytes()==V.filtered_source(original.read_bytes(),rows),'only exact selected quoted blocks removed')
    for u in units(ctx,mode):
        label=u['label'];ad=folder/(label+'-adapter.h');need(ad.read_bytes()==adapter(u['rows']).encode(),'exact owning-TU section/FUNC alias adapter')
        for kind,action,suffix in [('object',['-c'],'.o'),('IR',['-S','-emit-llvm'],'.ll')]:
            deps=['-MMD','-MF',str(folder/(label+'.d')),'-MT',label+'.o'] if kind=='object' else [];expected=[str(tools['clang']),*u['flags'],'-include',str(ad),*deps,*action,str(u['source']),'-o',str(folder/(label+suffix))]
            need(labels['typed-'+label+'-'+kind]['argv']==expected,'unchanged exact typed compile profile/source/output')
    need((folder/'canonical53.ld').read_bytes()==V.bindings_source(m).encode(),'exact canonical53 source-relative script')
    numeric='/* Numeric address only: no ROM bytes/provider/runtime proof. */\n'+ROM+' = 0x40000;\n';need((folder/'NUMERIC-ROM-WITNESS-ONLY.ld').read_bytes()==numeric.encode(),'sole explicit numeric ROM witness')
    link=str(tools['linker']);layout=str(ctx['model']/'original-image-layout.ld');specs={
      'merge-raw-carriers':[link,'-r','--no-relax',*[str(folder/('carrier-'+Path(n).stem+'.o')) for n in m['source_units']],'-o',str(folder/'raw-carriers.o')],
      'merge-typed':[link,'-r','--no-relax',*[str(folder/(u['label']+'.o')) for u in units(ctx,mode)],'-o',str(folder/'typed-providers.o')],
      'merge-source-integrated':[link,'-r','--no-relax','-T',str(folder/'canonical53.ld'),str(folder/'raw-carriers.o'),str(folder/'typed-providers.o'),'-o',str(folder/'source-integrated.o')],
      'strict-final-link':[link,'--no-relax','--error-limit=0','-T',layout,str(folder/'source-integrated.o'),'-o',str(folder/'STRICT-MISSING-ROM.elf')],
      'numeric-witness-final-link':[link,'--no-relax','-T',layout,'-T',str(folder/'NUMERIC-ROM-WITNESS-ONLY.ld'),str(folder/'source-integrated.o'),'-o',str(folder/'ADDRESS-WITNESS-ONLY.elf')],
      'export-new-offline-image':[str(tools['objcopy']),'-O','binary',str(folder/'ADDRESS-WITNESS-ONLY.elf'),str(folder/IMAGE)]}
    for label,argv in specs.items():need(labels[label]['argv']==argv,'source-only link/export command, no cached object/BIN input')
    for r in commands:
        need(Path(r['argv'][0]) in tools.values() and sha(folder/r['log'])==r['log_sha256'],'actual declared LLVM tool and log')
        need(r['exit']!=0 if r['label']=='strict-final-link' else r['exit']==0,'only strict missing-ROM operation rejects')
    text=(folder/'strict-final-link.log').read_text(encoding='utf-8');need(not (folder/'STRICT-MISSING-ROM.elf').exists() and set(re.findall(r'undefined symbol: (\w+)',text))=={ROM},'actual strict failure solely missing ROM provider')
    return dict(commands=56,compile_TUs=42,raw_TUs=34,IRQ_TUs=2,Flash_TUs=6,strict_missing_ROM_rejected=True)
def negative_controls(folder,ctx,original,create=True,recorded=None):
    E=ctx['ELF'];obj=E(folder/'source-integrated.o');linked=E(folder/'ADDRESS-WITNESS-ONLY.elf');m=ctx['manifest'];output=folder/'negative-controls';rows=[]
    if create:output.mkdir()
    def symoff(e,name):
        for sec in e.sections:
            if sec['type']==2:
                for i,s in enumerate(e.symbol_tables[sec['index']]):
                    if s['name']==name:return sec['offset']+i*16
        raise ValueError('counterexample symbol unavailable')
    cases=['retained_storage_byte','Flash_program_byte','program_extent94','alias_ABS','alias_NOTYPE','relative_label_value','outside_RELA_addend','owned_RELA_addend','missing_outside_RELA','RAM_PROGBITS','extra_ALLOC_comment','FILE_role_removed','mapping_role_changed','linked_wrong_VA','linked_FUNC_size','LOAD_wrong_LMA','LOAD_RAM_memsz','LOAD_wrong_permissions','image_outside_byte','image_revert_IRQ','image_revert_Flash','image_truncated','image_appended']
    selected={r['name'] for r in m['selected_sections']}
    for tag in cases:
        image=tag.startswith('image_');is_linked=tag.startswith('linked_') or tag.startswith('LOAD_');e=linked if is_linked else obj;raw=bytearray((folder/IMAGE).read_bytes() if image else e.raw)
        def shfield(section,delta,value):struct.pack_into('<I',raw,struct.unpack_from('<I',raw,32)[0]+section['index']*40+delta,value)
        if tag=='retained_storage_byte':raw[e.byname['.text.tsl9v4160.image_entry']['offset']]^=1
        elif tag=='Flash_program_byte':raw[e.byname['.text.tsl9v4160.direct_closure_18ef2']['offset']+6]^=0x10
        elif tag=='program_extent94':shfield(e.byname['.text.tsl9v4160.direct_closure_18ef2'],20,94)
        elif tag=='alias_ABS':struct.pack_into('<H',raw,symoff(e,'__tsl9v4160_call_18ef2')+14,0xfff1)
        elif tag=='alias_NOTYPE':raw[symoff(e,'__tsl9v4160_call_18ef2')+12]=16
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
        elif tag in ('image_revert_IRQ','image_revert_Flash'):
            address=0x9a44 if tag=='image_revert_IRQ' else m['differences_from_previous_IRQ_image'][0]['address'];raw[address-0x8000]=original[address-0x8000]
        elif tag=='image_truncated':raw=raw[:-1]
        elif tag=='image_appended':raw+=b'\0'
        path=output/(tag+('.bin' if image else '.elf' if is_linked else '.o'))
        if create:path.write_bytes(raw)
        else:need(path.read_bytes()==bytes(raw),'exact actual negative bytes '+tag)
        try:
            if image:image_gate(path,linked,ctx,original)
            elif tag.startswith('LOAD_'):image_gate(folder/IMAGE,E(path),ctx,original)
            elif is_linked:ctx['V'].linked_gate(E(path),ctx)
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
    changes=[('dependency_wrong_MT',rule('wrong-target.o',paths)),('dependency_wrong_primary',rule(target,wrong_primary)),('dependency_wrong_adapter',rule(target,wrong_adapter))]
    for tag,new in changes:
        payload=new.encode();need(payload!=raw,'actual per-rule dependency mutation');path=output/(tag+'.d')
        if create:path.write_bytes(payload)
        else:need(path.read_bytes()==payload,'exact retained dependency negative bytes')
        try:dependency_rule(path,target,primary,ad)
        except ValueError as error:reason=str(error)
        else:raise ValueError('accepted dependency/source association negative')
        rows.append(dict(case=tag,path=path.relative_to(folder).as_posix(),sha256=sha(path),rejected=True,reason=reason))
    if recorded is not None:need(rows==recorded,'actual dependency control replay')
    return rows
def replay(root,receipt,firmware=None):
    root=Path(root).resolve();receipt=Path(receipt).resolve();ctx=context(root);ctx['root']=root;path,original=original_image(root,ctx,firmware);r=read(receipt);folder=receipt.parent;V=ctx['V']
    need(r['passed'] and r['mode'] in ('c','cpp') and r['manifest_sha256']==MANIFEST_SHA and r['runner_sha256']==sha(Path(__file__)),'current successful image source/runner/language identities')
    need(r['source_files']==ctx['manifest']['source_files'] and r['firmware_sha256']==sha(path),'current source/firmware identity');tools={k:Path(x['path']) for k,x in r['tools'].items()};need(set(tools)=={'clang','linker','objcopy'},'exact three declared LLVM tools')
    for k,p in tools.items():need(sha(p)==r['tools'][k]['sha256'],'actual compiler/linker/objcopy identities')
    need(snapshot(root,ctx,tools,path)==r['input_stability_pins'],'current exact source/proof/tool/runner snapshot')
    for name,meta in r['artifacts'].items():
        p=(folder/name).resolve();need(p.is_relative_to(folder) and p.stat().st_size==meta['bytes'] and sha(p)==meta['sha256'],'actual artifact/log/dependency/image pin')
    checks=static_checks(folder,ctx,original);checks['native_dependency_closure']=dependency_gate(root,folder,ctx);checks['actual_commands']=command_gate(root,folder,ctx,r['mode'],r['commands'],tools);negative_controls(folder,ctx,original,False,r['actual_negative_controls']);dependency_controls(folder,ctx,False,r['actual_dependency_controls']);need(json.loads(json.dumps(checks))==r['checks'],'actual complete source/ELF/LOAD/image proof replay')
    return dict(passed=True,receipt=str(receipt),sha256=sha(receipt),artifacts_checked=len(r['artifacts']),compile_TUs=42,RELA=checks['merged']['RELA'],image_sha256=checks['image']['sha256'],differences=len(checks['image']['differences']),target_execution=False,flashable=False)
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=H.parents[2]);p.add_argument('--tool-dir',type=Path);p.add_argument('--clang');p.add_argument('--linker');p.add_argument('--objcopy');p.add_argument('--firmware',type=Path);p.add_argument('--language',choices=['c','cpp','both'],default='both');p.add_argument('--build-root',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
    if a.replay:print(json.dumps(replay(root,a.replay,a.firmware)));return
    ctx=context(root);ctx['root']=root;V=ctx['V'];firmware,original=original_image(root,ctx,a.firmware);tools={k:V.resolve_tool(getattr(a,k),a.tool_dir,n) for k,n in [('clang','clang'),('linker','ld.lld'),('objcopy','llvm-objcopy')]};pins=snapshot(root,ctx,tools,firmware);base=a.build_root.resolve() if a.build_root else root/MODEL/'build'/('source-integrated-'+uuid.uuid4().hex);need(base.is_relative_to(root) and not base.exists(),'create-only build root inside project');results=[]
    for mode in (['c','cpp'] if a.language=='both' else [a.language]):
        folder=base/mode;commands,changes,checks=build(root,folder,ctx,tools,mode,original);checks['native_dependency_closure']=dependency_gate(root,folder,ctx);checks['actual_commands']=command_gate(root,folder,ctx,mode,commands,tools);controls=negative_controls(folder,ctx,original);depcontrols=dependency_controls(folder,ctx);V.stability(pins)
        r=dict(schema='TSL9-eleven-readable-source-image-v1',passed=True,mode=mode,manifest_sha256=MANIFEST_SHA,runner_sha256=sha(Path(__file__)),source_files=ctx['manifest']['source_files'],input_stability_pins=pins,commands=commands,filtered_sources=changes,checks=checks,actual_negative_controls=controls,actual_dependency_controls=depcontrols,artifacts={p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in folder.rglob('*') if p.is_file()},tools={k:dict(path=str(v),sha256=sha(v)) for k,v in tools.items()},firmware_sha256=sha(firmware),target_execution=False,emulation=False,network=False,hardware=False,ROM_provider=False,flashable=False,OTA_ready=False);write(folder/'verification.json',r);results.append(dict(mode=mode,receipt=str(folder/'verification.json'),sha256=sha(folder/'verification.json'),image=str(folder/IMAGE),image_sha256=sha(folder/IMAGE)))
    if len(results)==2:need(results[0]['image_sha256']==results[1]['image_sha256'],'C11/C++17 fresh source-derived images identical')
    print(json.dumps(dict(passed=True,results=results,flashable=False,OTA_ready=False)))
if __name__=='__main__':main()
