"""Source-integrated offline image compiler/static admission; never executes RV32.

The exported image is NOT-FLASH-VALIDATED. A numeric ROM address is not a ROM
provider. Readable C replaces only five sections; all other carriers stay raw.
"""
import argparse,collections,hashlib,importlib.util,json,os,re,shlex,shutil,struct,subprocess,sys,uuid
from pathlib import Path
H=Path(__file__).resolve().parent
MODEL='experiments/tsl9-v4160-irq-image-integration'
MANIFEST_SHA='d952159ab2bf7c5294bc433510b88a7c19b23295ba11b0e7ab3d4a1ed39b1ce7'
CF_SEAL='adf95bbe0f92f012e790b8226abc80c7ec6f6ec483bcdd31e91e34526afbc83b'
ROM='__tsl9v4160_rom_entry'
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def case(root,slug):
    for p in (root/'apk-analysis'/('tsl9-'+slug),root/'analysis'/slug):
        if p.is_dir():return p
    raise ValueError('missing published/local case '+slug)
def context(root):
    model=root/MODEL;need(sha(model/'source-manifest.json')==MANIFEST_SHA,'pinned portable baseline/source manifest')
    m=read(model/'source-manifest.json');need(sha(model/'original-image-layout.ld')==m['layout_sha256'],'unchanged full691 layout')
    plan=case(root,'v4160-irq-callframe-2026-10-21')/'image-plan'
    need(sha(plan/'seal.json')==m['plan_seal_sha256'] and sha(plan/'verification.json')==m['plan_verification_sha256'],'pinned integration plan')
    for f in read(plan/'seal.json')['files']:need(sha(plan/f['path'])==f['sha256'],'integration plan sealed members')
    cf=case(root,'v4160-irq-callframe-2026-10-21')/'compiler-review'
    need(sha(cf/'final-audit.json')==CF_SEAL,'pinned actual callframe native proof')
    for name,pin in read(cf/'final-audit.json')['members'].items():need(sha(cf/name)==pin,'pinned callframe proof member')
    C=module('image_callframe',cf/'verify_callframe.py');c=C.load_context(root)
    for n,pin in m['source_files'].items():need(sha(root/n)==pin,'unchanged native compile source/header '+n)
    native=read(cf/'receipts/c.json')['checks']['objects']
    native_sha={n:f['code_sha256'] for group in native.values() for n,f in group['functions'].items()}
    return dict(manifest=m,CF=C,cf=c,ELF=c['ELF'],model=model,native_code_sha256=native_sha)
def role(e,s,linked=False):
    i=s['index'];owner=e.sections[i]['name'] if 0<i<len(e.sections) else ('UND' if i==0 else 'ABS')
    return dict(name=s['name'],owner=owner,offset=s['value']-(e.sections[i]['address'] if linked and 0<i<len(e.sections) else 0),bytes=s['size'],info=s['info'],other=s['other'])
def relocation(e,r):return dict(owner=r['owner'],offset=r['offset'],type=r['type'],addend=r['addend'],symbol=role(e,r['symbol']))
def counter(rows):return collections.Counter(json.dumps(x,sort_keys=True,separators=(',',':')) for x in rows)
def alloc(e):return {s['name']:s for s in e.sections if s['flags']&2 and s['size']}
def data(e,s):return b'' if s['type']==8 else e.data(s)
def globals_(e,linked=False):return [role(e,s,linked) for s in e.symbols if s['name'] and s['info']>>4 in (1,2)]
def und(e):return {s['name'] for s in e.symbols if s['name'] and s['index']==0}
def run(argv,folder,label,expected=0):
    p=subprocess.run([str(x) for x in argv],capture_output=True,cwd=folder,timeout=180)
    raw=p.stdout+p.stderr;log=folder/(label+'.log');log.write_bytes(raw)
    need((p.returncode==0) if expected==0 else (p.returncode!=0),label+' unexpected exit; inspect '+str(log))
    return dict(label=label,argv=[str(x) for x in argv],exit=p.returncode,log=log.name,log_sha256=sha(log)),raw.decode('utf-8',errors='replace')
def filtered_source(raw,selected):
    lines=raw.decode('utf-8').splitlines(keepends=True);keep=[];removing=None;removed=[]
    for line in lines:
        content=line.strip()
        if content.startswith('"'):
            asm=json.loads(content)
            if asm.startswith('.section '):
                section=asm.split(',',1)[0].split(' ',1)[1]
                need(removing is None,'selected block must end with exact .size before next section')
                if section in selected:removing=section;removed.append(section)
            if removing is not None:
                wanted=selected[removing]
                if asm=='.size '+wanted['global_alias']+','+str(wanted['bytes'])+'\n':removing=None
                continue
        need(removing is None or content.startswith('"'),'only exact quoted assembly removed')
        keep.append(line)
    need(removing is None and set(removed)==set(selected) and len(removed)==len(selected),'exact selected block allowlist removed once')
    return ''.join(keep).encode('utf-8')
def adapter(rows):
    text='#include <stdint.h>\n#ifdef __cplusplus\nextern "C" {\n#endif\n'
    for r in rows:
        params='void' if r['bytes']==144 else 'uint32_t mask,uint32_t enabled'
        text+='uint32_t '+r['new_C_symbol']+'('+params+') __attribute__((section("'+r['name']+'"),used,noinline));\n'
        text+='extern __typeof__('+r['new_C_symbol']+') '+r['global_alias']+' __attribute__((alias("'+r['new_C_symbol']+'")));\n'
    return text+'#ifdef __cplusplus\n}\n#endif\n'
def bindings_source(m):
    groups=collections.defaultdict(list)
    for b in m['section_relative_bindings']:groups[b['role']['owner']].append(b)
    text='/* Source-proven section-relative labels; no numeric ABS providers. */\nSECTIONS {\n'
    for n,s in sorted(m['allocations'].items()):
        text+=' '+n+' 0'+(' (NOLOAD)' if s['kind']=='RAM' else '')+' : {\n'
        for b in groups[n]:text+='  '+b['name']+' = '+b['expression']+';\n'
        text+='  KEEP(*('+n+'))\n }\n ASSERT(SIZEOF('+n+')=='+str(s['bytes'])+', "partial storage size")\n'
    return text+'}\n'
def metadata_gate(e,ctx,names,linked=False):
    m=ctx['manifest'];actual=alloc(e);need(set(actual)==set(names),'exact allocated section ownership; no hidden .eh_frame/data/padding section')
    for n in names:
        s=actual[n];need({k:s[k] for k in ('type','flags','size','alignment','entry_size')}==m['section_metadata'][n],'original allocation metadata '+n)
        if linked:need(s['address']==m['allocations'][n]['originalVA'],'all691 original VAs '+n)
    return dict(allocations=len(actual),allocated_bytes=sum(s['size'] for s in actual.values()),file_backed_sections=sum(s['type']!=8 for s in actual.values()))
def selected_gate(e,ctx):
    m=ctx['manifest'];rows=m['selected_sections'];names={r['name'] for r in rows}
    metadata_gate(e,ctx,names)
    expected=[]
    for r in rows:
        need(hashlib.sha256(e.data(e.byname[r['name']])).hexdigest()==ctx['native_code_sha256'][r['new_C_symbol']],'five native partial-section byte hashes match sealed compiler proof')
        for name in (r['new_C_symbol'],r['global_alias']):expected.append(dict(name=name,owner=r['name'],offset=0,bytes=r['bytes'],info=18,other=0))
    need(counter([r for r in globals_(e) if r['owner']!='UND'])==counter(expected),'five actual original aliases and five public typed global FUNC providers')
    return dict(allocated_bytes=264,original_global_FUNC_aliases=5,public_C_FUNC_names=5)
def normalized_symbols(rows,discharged=()):
    result=[];metadata=[]
    for r in rows:
        r=dict(r);n=r['name']
        if r['info']&15==4:metadata.append(r);continue # explicit FILE inventory below
        if r['info']&15==3:metadata.append(r);continue # SECTION regenerated by actual partial link
        if re.fullmatch(r'\$[dx]\.\d+',n):metadata.append(r);continue
        if not n:continue
        if r in discharged:continue # exact four original roles, not a wildcard
        result.append(r)
    return result,metadata
def merged_gate(e,ctx):
    m=ctx['manifest'];selected={r['name'] for r in m['selected_sections']};need(e.kind==1 and e.flags==1,'RV32IMAC partial ELF')
    result=metadata_gate(e,ctx,m['allocations'])
    need(len(e.relocations)==8276 and und(e)=={ROM},'8276 actual RELA and sole real ROM UND')
    retained=[]
    for n in set(m['allocations'])-selected:
        s=e.byname[n];expected=next(x for x in m['section_metadata'] if x==n)
        # Storage digest comes from the reviewed plan; NOBITS is logical empty.
        original=ctx['plan_retained'][n]
        need(hashlib.sha256(data(e,s)).hexdigest()==original['sha256'],'every686 retained storage hash '+expected)
    for r in m['selected_sections']:need(hashlib.sha256(e.data(e.byname[r['name']])).hexdigest()==ctx['native_code_sha256'][r['new_C_symbol']],'actual five partial native sections equal sealed native code')
    outside=[relocation(e,r) for r in e.relocations if r['owner'] not in selected]
    need(len(outside)==8270 and digest(sorted(outside,key=lambda x:json.dumps(x,sort_keys=True)))==m['retained_RELA_semantic_sha256'],'all8270 outside RELA full role/site/type/signedaddend/multiplicity unchanged')
    new=[relocation(e,r) for r in e.relocations if r['owner'] in selected]
    wanted=[];public={r['new_C_symbol']:r for r in m['selected_sections']}
    for r in m['old_selected_RELA']:
        if r['type']==44:continue
        r=json.loads(json.dumps(r));old=r['symbol'];target=next(x for x in m['selected_sections'] if x['global_alias']==old['name'])
        r['symbol']['name']=target['new_C_symbol'];wanted.append(r)
    need(counter(new)==counter(wanted),'only six original-offset main JALs to proven typed helper FUNC roles, no helper RELA')
    for b in m['section_relative_bindings']:need(counter([role(e,s) for s in e.symbols if s['name']==b['name']])==counter([b['role']]),'all53 source-relative canonical roles')
    discharged=[r['symbol'] for r in m['old_selected_RELA'] if r['type']==44]
    need(len(discharged)==4 and len(counter(discharged))==4,'only four exact old private branch roles discharged')
    before,oldmeta=normalized_symbols(m['baseline_symbol_roles'],discharged)
    after,newmeta=normalized_symbols([role(e,s) for s in e.symbols])
    added=[dict(name=r['new_C_symbol'],owner=r['name'],offset=0,bytes=r['bytes'],info=18,other=0) for r in m['selected_sections']]
    need(counter(after)==counter(before+added),'every nonmetadata original symbol role retained plus exactly5 public FUNCs')
    # Independently limit metadata inventories instead of waiving arbitrary symbols.
    section_old=[r for r in oldmeta if r['info']&15==3];section_new=[r for r in newmeta if r['info']&15==3]
    need(counter(section_old)==counter(section_new),'all actual local SECTION role metadata preserved')
    oldmaps=[r for r in oldmeta if re.fullmatch(r'\$[dx]\.\d+',r['name'])];newmaps=[r for r in newmeta if re.fullmatch(r'\$[dx]\.\d+',r['name'])]
    def nmaps(rows,exclude):
        return counter([{**r,'name':r['name'].split('.')[0]} for r in rows if r['owner'] not in exclude and r['owner'] not in ('.comment','ABS')])
    need(nmaps(oldmaps,selected)==nmaps(newmaps,selected),'all retained allocated mapping roles preserved with only assembler ordinal renumbering')
    old_abs=[{**r,'name':r['name'].split('.')[0]} for r in oldmaps if r['owner']=='ABS'];new_abs=[{**r,'name':r['name'].split('.')[0]} for r in newmaps if r['owner']=='ABS']
    need(counter(new_abs)==counter(old_abs+[dict(name='$d',owner='ABS',offset=0,bytes=0,info=0,other=0)]*2),'preserve all old ABS mappings and add only two measured zero-valued local nonstorage mappings')
    oldcomments=[{**r,'name':'$d'} for r in oldmaps if r['owner']=='.comment'];newcomments=[{**r,'name':'$d'} for r in newmaps if r['owner']=='.comment']
    need(counter(newcomments)==counter(oldcomments+[dict(name='$d',owner='.comment',offset=0,bytes=0,info=0,other=0)]*2),'exact original comment mappings plus two new compiler comment markers')
    need(not any(r['symbol']['index']==0xfff1 and r['symbol']['name'].startswith('$d.') for r in e.relocations),'new ABS mapping metadata is unreferenced, never a provider')
    files_old=[r for r in oldmeta if r['info']&15==4];files_new=[r for r in newmeta if r['info']&15==4]
    need(counter(files_new)==counter(files_old+[dict(name=n,owner='ABS',offset=0,bytes=0,info=4,other=0) for n in ('interrupt_callframe.c','rcc_helpers.c')]),'exact34 original FILE roles plus2 readable source FILE records')
    need(all(r['owner'] in selected and r['offset']==0 and r['info']==0 and r['bytes']==r['other']==0 and r['name'].startswith('$x.') for r in newmaps if r['owner'] in selected),'exact selected native instruction mapping roles')
    need(len([r for r in newmaps if r['owner'] in selected])==5,'one native mapping per selected function')
    incoming=[r for r in outside if r['symbol']['owner'] in selected]
    need(counter(incoming)==counter(m['external_incoming_RELA']),'all8 original entry-only incoming aliases preserved')
    return dict(**result,retained_storage_sections=686,RELA=8276,outside_RELA=8270,owned_RELA=6,discharged_helper_branch_RELA=4,canonical_relative_bindings=53,
        incoming_RELA=8,public_C_FUNC_names=5,old_metadata=oldmeta,new_metadata=newmeta)
def linked_gate(e,ctx):
    m=ctx['manifest'];need(e.kind==2 and e.flags==1 and not e.relocations and not und(e),'fully numerically resolved witness ELF, not missing-ROM provider proof')
    result=metadata_gate(e,ctx,m['allocations'],True)
    need(struct.unpack_from('<I',e.raw,24)[0]==0x8000,'original image entry')
    for r in m['selected_sections']:
        for name in (r['global_alias'],r['new_C_symbol']):
            wanted=dict(name=name,owner=r['name'],offset=0,bytes=r['bytes'],info=18,other=0)
            need(counter([role(e,s,True) for s in e.symbols if s['name']==name])==counter([wanted]),'actual linked original/public FUNC aliases')
    for b in m['section_relative_bindings']:need(counter([role(e,s,True) for s in e.symbols if s['name']==b['name']])==counter([b['role']]),'linked canonical labels remain section-relative')
    original_globals=[x for x in m['baseline_symbol_roles'] if x['name'] and x['info']>>4 in (1,2) and x['owner']!='UND']
    extras=[dict(name=r['new_C_symbol'],owner=r['name'],offset=0,bytes=r['bytes'],info=18,other=0) for r in m['selected_sections']]
    rom=dict(name=ROM,owner='ABS',offset=0x40000,bytes=0,info=16,other=0)
    need(counter(globals_(e,True))==counter(original_globals+extras+[rom]),'all original linked globals plus5publicFUNC and sole explicit numeric ROM witness')
    return result
def image_gate(path,e,ctx,original):
    m=ctx['manifest'];raw=path.read_bytes();need(len(raw)==76800,'exact76800 exported bytes')
    source={};load={};ram=0
    for n,s in alloc(e).items():
        if s['type']==8:need(n=='.bss.tsl9v4160.ram' and s['size']==35160,'only original RAM NOBITS');ram+=s['size'];continue
        need(s['type']==1,'only real PROGBITS exported source carriers')
        for i,b in enumerate(e.data(s)):
            a=s['address']+i;need(a not in source,'no overlapping source section bytes');source[a]=b
    need(set(source)==set(range(0x8000,0x1ac00)) and ram==35160,'all76800 bytes section-backed, no padding/fallback, RAM excluded')
    phoff=struct.unpack_from('<I',e.raw,28)[0];stride,count=struct.unpack_from('<HH',e.raw,42);need(stride==32,'ELF32 program header stride')
    for i in range(count):
        typ,off,va,lma,filesz,memsz,flags,align=struct.unpack_from('<8I',e.raw,phoff+i*stride)
        if typ!=1:continue
        need(va==lma and filesz<=memsz and off+filesz<=len(e.raw),'real LOAD VMA=LMA and bounded extent')
        need(not filesz or 0x8000<=va<va+filesz<=0x1ac00,'no file-backed LOAD outside original image')
        for j in range(filesz):
            a=va+j;b=e.raw[off+j];need(a not in load or load[a]==b,'unambiguous LOAD bytes');load[a]=b
    need(source==load and bytes(source[a] for a in range(0x8000,0x1ac00))==raw,'actual section bytes=LOAD bytes=exported bytes')
    diffs=[dict(address=0x8000+i,original=a,native=b) for i,(a,b) in enumerate(zip(original,raw)) if a!=b]
    need(diffs==m['expected_differences'],'exact eight admitted prologue differences including byte values; all other76792bytes original')
    return dict(bytes=76800,sha256=sha(path),differences=diffs,section_backed_bytes=76800,padding_bytes=0,NOBITS_bytes_exported=0,ROM_bytes_supplied=0)
def static_checks(folder,ctx,original):
    E=ctx['ELF'];m=ctx['manifest'];selected={r['name'] for r in m['selected_sections']}
    carrier=E(folder/'raw-carriers.o');metadata_gate(carrier,ctx,set(m['allocations'])-selected)
    need(not any(r['symbol']['name'] in {s['new_C_symbol'] for s in m['selected_sections']} for r in carrier.relocations),'raw carriers do not depend on invented public providers')
    typed=E(folder/'typed-providers.o');t=selected_gate(typed,ctx)
    typed_attrs=[]
    for unit in ('main','helpers'):
        e=E(folder/(unit+'.o'));attrs=[role(e,s) for s in e.symbols if s['name'].startswith('$d.') and 0<s['index']<len(e.sections) and e.sections[s['index']]['name']=='.riscv.attributes']
        need(len(attrs)==1 and all(attrs[0][k]==v for k,v in dict(offset=0,bytes=0,info=0,other=0).items()),'one exact local input attributes marker per typed TU')
        rows=[role(typed,s) for s in typed.symbols if s['name']==attrs[0]['name'] and s['index']==0xfff1]
        need(rows==[{**attrs[0],'owner':'ABS'}],'actual attributes merge converts only this measured local marker to ABS0')
        typed_attrs.append(dict(unit=unit,input=attrs[0],partial=rows[0]))
    merged=merged_gate(E(folder/'source-integrated.o'),ctx)
    linked=E(folder/'ADDRESS-WITNESS-ONLY.elf');l=linked_gate(linked,ctx)
    image=image_gate(folder/'NOT-FLASH-VALIDATED-irq-callframe.bin',linked,ctx,original)
    return dict(raw_allocations=686,typed=t,typed_attributes_metadata=typed_attrs,merged=merged,linked=l,image=image,original_pointwise_equivalence_proved=False,asynchronous_equivalence_proved=False,
        strict_provider_link_passed=False,full_physical_compatibility_proved=False,OTA_ready=False,target_execution=False,emulation=False)
def build(root,folder,ctx,tools,mode,original):
    m=ctx['manifest'];folder.mkdir(parents=True);units=[];commands=[];source_changes=[]
    filtered=folder/'filtered';filtered.mkdir();groups=collections.defaultdict(dict)
    for r in m['selected_sections']:groups[r['producer']][r['name']]=r
    for n in m['source_units']:
        source=root/n;original_source=source
        if n in groups:
            raw=source.read_bytes();out=filtered/source.name;out.write_bytes(filtered_source(raw,groups[n]));source=out
            source_changes.append(dict(source=n,original_sha256=sha(original_source),filtered=out.name,filtered_sha256=sha(out),removed_sections=sorted(groups[n])))
        out=folder/('carrier-'+source.stem+'.o');cmd=[tools['clang'],'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-fno-builtin','-fno-stack-protector','-Wall','-Wextra','-Werror','-x','c' if mode=='c' else 'c++','-std=c11' if mode=='c' else '-std=c++17','-I',original_source.parent,'-MMD','-MF',out.with_suffix('.d'),'-MT',out.name,'-c',source,'-o',out]
        r,_=run(cmd,folder,'compile-'+source.stem);commands.append(r);units.append(out)
    r,_=run([tools['linker'],'-r','--no-relax',*units,'-o',folder/'raw-carriers.o'],folder,'merge-raw-carriers');commands.append(r)
    typed=[]
    for label,name,is_main in [('main','interrupt_callframe.c',True),('helpers','rcc_helpers.c',False)]:
        rows=[r for r in m['selected_sections'] if (r['bytes']==144)==is_main];ad=folder/(label+'-adapter.h');ad.write_text(adapter(rows),encoding='utf-8')
        source=root/'experiments/tsl9-v4160-irq-callframe/src'/name;out=folder/(label+'.o')
        flags=ctx['CF'].profile_flags(ctx['cf'],mode,is_main)
        for label2,extra,dest in [('object',['-c'],out),('IR',['-S','-emit-llvm'],folder/(label+'.ll'))]:
            deps=['-MMD','-MF',out.with_suffix('.d'),'-MT',out.name] if label2=='object' else []
            r,_=run([tools['clang'],*flags,'-include',ad,*deps,*extra,source,'-o',dest],folder,'typed-'+label+'-'+label2);commands.append(r)
        typed.append(out)
    r,_=run([tools['linker'],'-r','--no-relax',*typed,'-o',folder/'typed-providers.o'],folder,'merge-typed');commands.append(r)
    script=folder/'canonical53.ld';script.write_text(bindings_source(m),encoding='utf-8')
    r,_=run([tools['linker'],'-r','--no-relax','-T',script,folder/'raw-carriers.o',folder/'typed-providers.o','-o',folder/'source-integrated.o'],folder,'merge-source-integrated');commands.append(r)
    ctx['plan_retained']={x['name']:x for x in read(case(root,'v4160-irq-callframe-2026-10-21')/'image-plan/verification.json')['retained_allocations']}
    merged_gate(ctx['ELF'](folder/'source-integrated.o'),ctx)
    layout=ctx['model']/'original-image-layout.ld'
    strict=folder/'STRICT-MISSING-ROM.elf';r,error=run([tools['linker'],'--no-relax','--error-limit=0','-T',layout,folder/'source-integrated.o','-o',strict],folder,'strict-final-link',1);commands.append(r)
    need(not strict.exists() and set(re.findall(r'undefined symbol: (\w+)',error))=={ROM},'actual strict link rejects sole missing ROM resident')
    script=folder/'NUMERIC-ROM-WITNESS-ONLY.ld';script.write_text('/* Numeric address only: no ROM bytes/provider/runtime proof. */\n'+ROM+' = 0x40000;\n',encoding='utf-8')
    r,_=run([tools['linker'],'--no-relax','-T',layout,'-T',script,folder/'source-integrated.o','-o',folder/'ADDRESS-WITNESS-ONLY.elf'],folder,'numeric-witness-final-link');commands.append(r)
    r,_=run([tools['objcopy'],'-O','binary',folder/'ADDRESS-WITNESS-ONLY.elf',folder/'NOT-FLASH-VALIDATED-irq-callframe.bin'],folder,'export-new-offline-image');commands.append(r)
    checks=static_checks(folder,ctx,original)
    ir=ctx['CF'].ir_gate(folder);checks['LLVM_IR']=ir
    return commands,source_changes,checks
def resolve_tool(override,directory,name):
    p=override or (directory/(name+('.exe' if os.name=='nt' else '')) if directory else shutil.which(name));need(p and Path(p).is_file(),'missing local LLVM '+name);return Path(p).resolve()
def dependency_gate(root,folder,ctx):
    seen=set();generated=set();files=list(folder.glob('*.d'));need(len(files)==36,'actual native dependency outputs for all36 compile TUs')
    for p in files:
        text=p.read_text(encoding='utf-8').replace('\\\n','').replace('\\\r\n','')
        need(': ' in text,'bounded compiler Make dependency rule')
        for token in shlex.split(text.split(': ',1)[1],posix=True):
            q=Path(token).resolve();need(q.is_file(),'actual compiler header/source dependency exists')
            if q.is_relative_to(folder.resolve()):generated.add(q.relative_to(folder).as_posix())
            else:
                n=q.relative_to(root).as_posix();need(n in ctx['manifest']['source_files'] and sha(q)==ctx['manifest']['source_files'][n],'all actual native includes are pinned, no HOST_TEST path');seen.add(n)
    expected=set(ctx['manifest']['source_files'])-{'experiments/tsl9-v4160-startup/src/initialization_native.c','experiments/tsl9-v4160-startup/src/frontier_native.c'}
    need(seen==expected and generated=={'filtered/initialization_native.c','filtered/frontier_native.c','main-adapter.h','helpers-adapter.h'},'exact compiler-observed71 original files plus4 generated source/adapter inputs')
    return dict(dependency_rules=36,pinned_native_files=len(seen),generated_files=sorted(generated),all_native_headers_pinned=True)
def snapshot(root,ctx,tools):
    paths={str(root/n):pin for n,pin in ctx['manifest']['source_files'].items()}
    for p in (Path(__file__).resolve(),ctx['model']/'source-manifest.json',ctx['model']/'original-image-layout.ld'):paths[str(p)]=sha(p)
    for slug,seal in [('v4160-irq-callframe-2026-10-21/compiler-review','final-audit.json'),('v4160-irq-callframe-2026-10-21/image-plan','seal.json'),('v4160-irq-callframe-2026-10-21/source-plan','seal.json'),('v4160-interrupt-init-2026-10-21/source','final-audit.json'),('v4160-irq-native-2026-10-21/compiler-review','final-audit.json')]:
        name,sub=slug.split('/',1);base=case(root,name)/sub;paths[str(base/seal)]=sha(base/seal);d=read(base/seal);members=d.get('members',d.get('files'))
        rows=members.items() if isinstance(members,dict) else [(r['path'],r['sha256']) for r in members]
        for n,pin in rows:paths[str(base/n)]=pin
    for p in tools.values():paths[str(p)]=sha(p)
    for n,pin in paths.items():need(sha(Path(n))==pin,'stable input snapshot member')
    return paths
def stability(pins):
    for n,pin in pins.items():need(sha(Path(n))==pin,'input/tool/runner changed during build '+n)
def command_gate(root,folder,ctx,mode,commands,tools):
    labels={r['label']:r for r in commands};need(len(labels)==len(commands)==44,'exact44 bounded source compiler/link/export invocations')
    m=ctx['manifest'];groups={r['producer'] for r in m['selected_sections']}
    for n in m['source_units']:
        original=root/n;source=folder/'filtered'/original.name if n in groups else original
        row=labels['compile-'+original.stem];argv=row['argv'];expected=[str(tools['clang']),'--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-fno-builtin','-fno-stack-protector','-Wall','-Wextra','-Werror','-x','c' if mode=='c' else 'c++','-std=c11' if mode=='c' else '-std=c++17','-I',str(original.parent),'-MMD','-MF',str(folder/('carrier-'+original.stem+'.d')),'-MT','carrier-'+original.stem+'.o','-c',str(source),'-o',str(folder/('carrier-'+original.stem+'.o'))]
        need(argv==expected,'exact original-carrier compile profile/source/output '+n)
    for unit,name,is_main in [('main','interrupt_callframe.c',True),('helpers','rcc_helpers.c',False)]:
        flags=ctx['CF'].profile_flags(ctx['cf'],mode,is_main);source=root/'experiments/tsl9-v4160-irq-callframe/src'/name
        for label,action,suffix in [('object',['-c'],'.o'),('IR',['-S','-emit-llvm'],'.ll')]:
            deps=['-MMD','-MF',str(folder/(unit+'.d')),'-MT',unit+'.o'] if label=='object' else []
            expected=[str(tools['clang']),*flags,'-include',str(folder/(unit+'-adapter.h')),*deps,*action,str(source),'-o',str(folder/(unit+suffix))]
            need(labels['typed-'+unit+'-'+label]['argv']==expected,'exact proved typed compile profile '+unit+label)
    need((folder/'canonical53.ld').read_text(encoding='utf-8')==bindings_source(m),'actual source-relative53binding script')
    need((folder/'NUMERIC-ROM-WITNESS-ONLY.ld').read_text(encoding='utf-8')=='/* Numeric address only: no ROM bytes/provider/runtime proof. */\n'+ROM+' = 0x40000;\n','sole numeric ROM witness script')
    for r in m['selected_sections']:
        p=root/r['producer'];group={x['name']:x for x in m['selected_sections'] if x['producer']==r['producer']}
        need((folder/'filtered'/p.name).read_bytes()==filtered_source(p.read_bytes(),group),'exact filtered-source provenance, unchanged remainder')
    for unit,is_main in [('main',True),('helpers',False)]:need((folder/(unit+'-adapter.h')).read_text(encoding='utf-8')==adapter([r for r in m['selected_sections'] if (r['bytes']==144)==is_main]),'exact owning-TU section/FUNC alias adapter')
    for row in commands:
        log=folder/row['log'];need(sha(log)==row['log_sha256'],'actual command log hash')
        need(row['exit']!=0 if row['label']=='strict-final-link' else row['exit']==0,'all actual command exits; only strict ROM link rejects')
        need(Path(row['argv'][0]) in tools.values(),'only declared local LLVM tools were invoked')
    strict=labels['strict-final-link'];text=(folder/strict['log']).read_text(encoding='utf-8')
    need(set(re.findall(r'undefined symbol: (\w+)',text))=={ROM} and not (folder/'STRICT-MISSING-ROM.elf').exists(),'actual strict failure log identifies sole missing ROM and no output')
    need(strict['argv']==[str(tools['linker']),'--no-relax','--error-limit=0','-T',str(ctx['model']/'original-image-layout.ld'),str(folder/'source-integrated.o'),'-o',str(folder/'STRICT-MISSING-ROM.elf')],'strict actual original691 layout command')
    link=str(tools['linker']);specs={
      'merge-raw-carriers':[link,'-r','--no-relax',*[str(folder/('carrier-'+Path(n).stem+'.o')) for n in m['source_units']],'-o',str(folder/'raw-carriers.o')],
      'merge-typed':[link,'-r','--no-relax',str(folder/'main.o'),str(folder/'helpers.o'),'-o',str(folder/'typed-providers.o')],
      'merge-source-integrated':[link,'-r','--no-relax','-T',str(folder/'canonical53.ld'),str(folder/'raw-carriers.o'),str(folder/'typed-providers.o'),'-o',str(folder/'source-integrated.o')],
      'numeric-witness-final-link':[link,'--no-relax','-T',str(ctx['model']/'original-image-layout.ld'),'-T',str(folder/'NUMERIC-ROM-WITNESS-ONLY.ld'),str(folder/'source-integrated.o'),'-o',str(folder/'ADDRESS-WITNESS-ONLY.elf')],
      'export-new-offline-image':[str(tools['objcopy']),'-O','binary',str(folder/'ADDRESS-WITNESS-ONLY.elf'),str(folder/'NOT-FLASH-VALIDATED-irq-callframe.bin')]}
    for label,argv in specs.items():need(labels[label]['argv']==argv,'exact source-only merge/link/export recipe '+label)
    return dict(commands=44,compile_TUs=36,strict_missing_ROM_rejected=True)
def negative_controls(folder,ctx,original,create=True,recorded=None):
    E=ctx['ELF'];obj=E(folder/'source-integrated.o');linked=E(folder/'ADDRESS-WITNESS-ONLY.elf');m=ctx['manifest'];rows=[]
    output=folder/'negative-controls'
    if create:output.mkdir()
    cases=['retained_storage_byte','native_body_byte','alias_ABS','alias_NOTYPE','relative_label_value','RELA_addend','missing_RELA','RAM_PROGBITS','extra_allocated_comment','linked_wrong_VA','LOAD_wrong_LMA','image_outside_byte','image_reverted_save_byte','image_truncated','image_appended']
    def symoff(e,name):
        for sec in e.sections:
            if sec['type']==2:
                for i,s in enumerate(e.symbol_tables[sec['index']]):
                    if s['name']==name:return sec['offset']+i*16
        raise ValueError('missing countercase symbol')
    for tag in cases:
        is_image=tag.startswith('image_');is_linked=tag.startswith('linked_') or tag.startswith('LOAD_');e=linked if is_linked else obj
        raw=bytearray((folder/'NOT-FLASH-VALIDATED-irq-callframe.bin').read_bytes() if is_image else e.raw)
        if tag=='retained_storage_byte':raw[e.byname['.text.tsl9v4160.image_entry']['offset']]^=1
        elif tag=='native_body_byte':raw[e.byname['.text.tsl9v4160.init_9a42']['offset']+10]^=1
        elif tag=='alias_ABS':struct.pack_into('<H',raw,symoff(e,'__tsl9v4160_call_9a42')+14,0xfff1)
        elif tag=='alias_NOTYPE':raw[symoff(e,'__tsl9v4160_call_9a42')+12]=16
        elif tag=='relative_label_value':
            off=symoff(e,m['section_relative_bindings'][0]['name'])+4;struct.pack_into('<I',raw,off,struct.unpack_from('<I',raw,off)[0]+2)
        elif tag in ('RELA_addend','missing_RELA'):
            sec=next(s for s in e.sections if s['type']==4 and s['size'])
            if tag=='RELA_addend':off=sec['offset']+8;struct.pack_into('<i',raw,off,struct.unpack_from('<i',raw,off)[0]+1)
            else:off=struct.unpack_from('<I',raw,32)[0]+sec['index']*40+20;struct.pack_into('<I',raw,off,sec['size']-12)
        elif tag=='RAM_PROGBITS':struct.pack_into('<I',raw,struct.unpack_from('<I',raw,32)[0]+e.byname['.bss.tsl9v4160.ram']['index']*40+4,1)
        elif tag=='extra_allocated_comment':struct.pack_into('<I',raw,struct.unpack_from('<I',raw,32)[0]+e.byname['.comment']['index']*40+8,50)
        elif tag=='linked_wrong_VA':struct.pack_into('<I',raw,struct.unpack_from('<I',raw,32)[0]+e.byname['.text.tsl9v4160.init_9a42']['index']*40+12,0x9a44)
        elif tag=='LOAD_wrong_LMA':
            off=struct.unpack_from('<I',raw,28)[0];stride,count=struct.unpack_from('<HH',raw,42)
            at=next(off+i*stride for i in range(count) if struct.unpack_from('<I',raw,off+i*stride)[0]==1);struct.pack_into('<I',raw,at+12,struct.unpack_from('<I',raw,at+12)[0]+4)
        elif tag=='image_outside_byte':raw[0]^=1
        elif tag=='image_reverted_save_byte':raw[0x9a44-0x8000]=original[0x9a44-0x8000]
        elif tag=='image_truncated':raw=raw[:-1]
        elif tag=='image_appended':raw+=b'\0'
        path=output/(tag+('.bin' if is_image else '.elf' if is_linked else '.o'))
        if create:path.write_bytes(raw)
        else:need(path.read_bytes()==bytes(raw),'exact retained actual negative artifact '+tag)
        try:
            if is_image:image_gate(path,linked,ctx,original)
            elif tag=='LOAD_wrong_LMA':image_gate(folder/'NOT-FLASH-VALIDATED-irq-callframe.bin',E(path),ctx,original)
            elif is_linked:linked_gate(E(path),ctx)
            else:merged_gate(E(path),ctx)
        except (ValueError,AssertionError) as ex:reason=str(ex)
        else:raise ValueError('accepted actual negative artifact '+tag)
        rows.append(dict(case=tag,path=path.relative_to(folder).as_posix(),sha256=sha(path),rejected=True,reason=reason))
    if recorded is not None:need(rows==recorded,'actual negative-control replay reasons/pins')
    return rows
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=H.parents[2]);p.add_argument('--tool-dir',type=Path);p.add_argument('--clang');p.add_argument('--linker');p.add_argument('--objcopy');p.add_argument('--firmware',type=Path);p.add_argument('--language',choices=['c','cpp','both'],default='both');p.add_argument('--build-root',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve();ctx=context(root)
    ctx['plan_retained']={x['name']:x for x in read(case(root,'v4160-irq-callframe-2026-10-21')/'image-plan/verification.json')['retained_allocations']}
    firmware,original=ctx['CF'].original_image(root,ctx['cf'],a.firmware)
    if a.replay:
        result=replay(root,a.replay,ctx,original);print(json.dumps(result));return
    tools={k:resolve_tool(getattr(a,k),a.tool_dir,n) for k,n in [('clang','clang'),('linker','ld.lld'),('objcopy','llvm-objcopy')]};pins=snapshot(root,ctx,tools)
    work=(a.build_root.resolve() if a.build_root else ctx['model']/'build'/('source-integrated-'+uuid.uuid4().hex));need(not work.exists(),'create-only fresh build root');work.mkdir(parents=True);results=[]
    for mode in (['c','cpp'] if a.language=='both' else [a.language]):
        folder=work/mode;commands,changes,checks=build(root,folder,ctx,tools,mode,original)
        checks['native_dependency_closure']=dependency_gate(root,folder,ctx)
        checks['actual_commands']=command_gate(root,folder,ctx,mode,commands,tools)
        controls=negative_controls(folder,ctx,original);stability(pins)
        artifacts={f.relative_to(folder).as_posix():dict(bytes=f.stat().st_size,sha256=sha(f)) for f in folder.rglob('*') if f.is_file()}
        result=dict(schema='TSL9-source-integrated-IRQ-image-v1',passed=True,mode=mode,manifest_sha256=MANIFEST_SHA,runner_sha256=sha(Path(__file__)),source_files=ctx['manifest']['source_files'],
            tools={k:dict(path=str(v),sha256=sha(v)) for k,v in tools.items()},input_stability_pins=pins,firmware_sha256=sha(firmware),filtered_sources=changes,commands=commands,checks=checks,actual_negative_controls=controls,artifacts=artifacts,
            scope='offline source-derived storage image; only five selected typed functions',strict_ROM_provider=False,numeric_ROM_witness_only=True,pointwise_equivalence=False,asynchronous_equivalence=False,flashable=False,OTA_ready=False,hardware=False,network=False,target_execution=False,emulation=False)
        receipt=folder/'verification.json';write(receipt,result);results.append(dict(mode=mode,receipt=str(receipt),sha256=sha(receipt),image=str(folder/'NOT-FLASH-VALIDATED-irq-callframe.bin'),image_sha256=checks['image']['sha256']))
    if len(results)==2:need(results[0]['image_sha256']==results[1]['image_sha256'],'C/C++ new images identical')
    print(json.dumps(dict(passed=True,results=results,source_bytes=76800,differences=8,flashable=False,OTA_ready=False)))
def replay(root,receipt,ctx=None,original=None):
    root=Path(root).resolve();receipt=Path(receipt).resolve()
    ctx=ctx or context(root)
    ctx['plan_retained']={x['name']:x for x in read(case(root,'v4160-irq-callframe-2026-10-21')/'image-plan/verification.json')['retained_allocations']}
    if original is None:_,original=ctx['CF'].original_image(root,ctx['cf'])
    r=read(receipt);folder=receipt.parent
    need(r['passed'] is True and r['mode'] in ('c','cpp') and r['source_files']==ctx['manifest']['source_files'],'receipt success/language/current exactsourcepins')
    need(r['manifest_sha256']==MANIFEST_SHA and r['runner_sha256']==sha(Path(__file__)),'same sealed source manifest/runner')
    tools={k:Path(v['path']) for k,v in r['tools'].items()};need(set(tools)=={'clang','linker','objcopy'},'exact declared LLVM tools')
    for k,p in tools.items():need(sha(p)==r['tools'][k]['sha256'],'actual same local compiler/linker/objcopy pin')
    need(snapshot(root,ctx,tools)==r['input_stability_pins'],'all actual source/proof/runner/tool input pins match before-and-after snapshot')
    for n,x in r['artifacts'].items():
        q=(folder/n).resolve();need(q.is_relative_to(folder.resolve()) and q.stat().st_size==x['bytes'] and sha(q)==x['sha256'],'actual artifact/log pin '+n)
    now=static_checks(folder,ctx,original);now['LLVM_IR']=ctx['CF'].ir_gate(folder)
    now['native_dependency_closure']=dependency_gate(root,folder,ctx);now['actual_commands']=command_gate(root,folder,ctx,r['mode'],r['commands'],tools)
    negative_controls(folder,ctx,original,False,r['actual_negative_controls'])
    need(json.loads(json.dumps(now))==r['checks'],'replayed all actual image/ELF/IR checks')
    return dict(passed=True,receipt=str(receipt),sha256=sha(receipt),artifacts_checked=len(r['artifacts']),source_bytes=76800,differences=8,flashable=False,target_execution=False)
if __name__=='__main__':main()
