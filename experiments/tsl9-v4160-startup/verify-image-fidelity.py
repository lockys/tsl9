"""Compile original-image carriers; export an explicitly unvalidated file fixture."""
import argparse,collections,json,re,runpy,struct,sys,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parent;W=ROOT.parents[1]
PREV=runpy.run_path(str(ROOT/'verify-retained-data-extension.py'));CORE=PREV['CORE'];BASE=PREV['BASE']
ELF=PREV['ELF'];BIN=PREV['BIN'];sha=PREV['sha'];digest=PREV['digest'];read=PREV['read'];need=PREV['need'];run=PREV['run'];roles=PREV['roles']
SOURCE_SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
def sections_for(prior,raw):
    admitted=set()
    for s in prior['allocations'].values():
        if s['kind']=='RAM':continue
        need(0x8000<=s['originalVA']<s['originalVA']+s['bytes']<=0x1ac00,'Original source extent only')
        points=set(range(s['originalVA'],s['originalVA']+s['bytes']))
        need(not admitted&points,'No inherited overlapping storage');admitted|=points
    gaps=PREV['intervals'](set(range(0x8000,0x1ac00))-admitted)
    need(len(gaps)==10 and sum(b-a for a,b in gaps)==95,'Exact complete remaining original-source difference')
    return[dict(name='.rodata.tsl9v4160.image_only_'+format(a,'x'),symbol='__tsl9v4160_image_only_'+format(a,'x'),
        originalVA=a,bytes=b-a,kind='opaque-image',flags=2,alignment=1,raw_hex=raw[a-0x8000:b-0x8000].hex(),
        sha256=digest(raw[a-0x8000:b-0x8000]))for a,b in gaps]

def allocations_for(prior,sections):
    result=dict(prior['allocations'])
    for s in sections:result[s['name']]=dict(s,end_exclusive=s['originalVA']+s['bytes'])
    need(len(result)==691,'Actual691 allocated source/RAM carriers');return result

def merged_gate(obj,before,unit,sections,allocations):
    need(obj.kind==1 and len(obj.relocations)==8280,'Actual relocatable object with unchanged8280 RELA')
    CORE['allocations_gate'](obj,allocations);CORE['inherited_gate'](before,obj,{n:s for n,s in allocations.items()if n not in {x['name']for x in sections}})
    PREV['storage_gate'](obj,sections);CORE['raw_role_gate'](before,unit,obj,dict(sections=sections))
    need(CORE['raw_relocation_roles'](obj)==CORE['raw_relocation_roles'](before),'Every raw inherited RELA site/type/S-role/signed addend/multiplicity unchanged')
    need(BASE['und'](obj)==BASE['und'](before)=={'__tsl9v4160_rom_entry'},'No canonical contract closed by image-only storage')
    names={s['name']for s in before.symbols if s['name']and s['index']!=0 and s['bind']in(1,2)}|{s['symbol']for s in sections}
    PREV['globals_gate'](obj,names)

def linked_gate(witness,oldwitness,obj,before,unit,sections,allocations):
    extras=roles(obj,set())-roles(before,set());need(not roles(before,set())-roles(obj,set()),'Every old partial symbol retained')
    newnames={s['name']for s in sections};discarded=[];expected=collections.Counter()
    for role,count in extras.items():
        name,owner,value,size,info,other=role
        if owner in newnames and name==''and(info&15)==3:
            need(role==('',owner,0,0,3,0)and count==1,'One exact new generated local SECTION')
            u=PREV['raw_section_symbols'](unit,owner);m=PREV['raw_section_symbols'](obj,owner)
            need(not u and len(m)==1 and m[0]['role']==list(role)and not m[0]['references'],'Actual absent unit SECTION and unreferenced merged SECTION by sh_link/index')
            discarded.append(dict(role=list(role),count=count,unit_absent=True,merged_records=m,
                reason='new_generated_unreferenced_SECTION_omitted_by_final_link'));continue
        if owner=='.comment':
            sec=unit.byname[owner];meta={k:sec[k]for k in ['type','flags','size','alignment','entsize']}
            need(re.fullmatch(r'\$d\.\d+',name)is not None and(value,size,info,other)==(0,0,0,0)and
                roles(unit,set())[role]==count==1 and tuple(meta.values())==(1,48,159,1,1)and not unit.relocations,
                'Only exact new nonallocated comment marker omitted')
            discarded.append(dict(role=list(role),count=count,section_metadata=meta,section_data_sha256=digest(sec['data']),
                reason='exact_new_unit_nonallocated_comment_mapping_marker'));continue
        if owner in allocations:value+=allocations[owner]['originalVA']
        expected[(name,owner,value,size,info,other)]+=count
    need(len(discarded)==11 and roles(witness,set())==roles(oldwitness,set())+expected,'Exact original final symbols plus new objects; only11 precise metadata omissions')
    return discarded

def image_gate(path,witness,allocations,raw):
    data=path.read_bytes();need(len(data)==76800 and data==raw and digest(data)==SOURCE_SHA,'Complete offline image fixture equals the original candidate, no offsets/holes/extra bytes')
    source={};load={}
    for n,s in allocations.items():
        sec=witness.byname[n]
        if s['kind']=='RAM':need(sec['type']==8 and not sec['data'],'RAM stays NOBITS, never copied into flat image');continue
        need(sec['type']==1 and sec['address']==s['originalVA']and sec['size']==s['bytes'],'Every original carrier has real original-VA PROGBITS')
        for i,b in enumerate(sec['data']):
            address=sec['address']+i;need(address not in source,'No overlapping source carrier');source[address]=b
    need(set(source)==set(range(0x8000,0x1ac00)),'All76800 bytes are section-backed, zero linker padding credited')
    phoff=struct.unpack_from('<I',witness.raw,28)[0];stride,count=struct.unpack_from('<HH',witness.raw,42)
    need(stride==32,'ELF32 program headers')
    for i in range(count):
        kind,off,va,paddr,filesz,_,_,_=struct.unpack_from('<8I',witness.raw,phoff+i*stride)
        if kind!=1:continue
        need(va==paddr,'Every LOAD LMA/PADDR matches the original VMA; no hidden flat-image address shift')
        need(not filesz or 0x8000<=va<va+filesz<=0x1ac00,'No extra file-backed LOAD outside the original source image')
        need(off+filesz<=len(witness.raw),'Actual file-backed LOAD extent')
        for address in range(max(va,0x8000),min(va+filesz,0x1ac00)):
            b=witness.raw[off+address-va];need(address not in load or load[address]==b,'Unambiguous actual LOAD bytes');load[address]=b
    need(load==source and bytes(source[a]for a in range(0x8000,0x1ac00))==data,'Flat bytes match actual sections and all file-backed LOADs')
    return dict(bytes=len(data),sha256=digest(data),image_base=0x8000,end_exclusive=0x1ac00,all_source_bytes_section_backed=True,
        section_padding_bytes=0,NOBITS_bytes_exported=0,reference_ROM_bytes_supplied=0,flashable_BIN_proved=False)

def countercases(obj,before,unit,sections,allocations,witness,flat,raw,folder):
    rows=[];symoff=PREV['sym_offset'];sec=obj.byname[sections[0]['name']]
    for tag in ['opaque_byte','private_size','NOBITS_carrier','fake_ROM_ABS','inherited_code_byte','RELA_addend','missing_RELA','SECTION_visibility']:
        data=bytearray(obj.raw)
        if tag=='opaque_byte':data[sec['offset']]^=1
        elif tag=='private_size':struct.pack_into('<I',data,symoff(obj,sections[0]['symbol'])+8,53)
        elif tag=='NOBITS_carrier':struct.pack_into('<I',data,struct.unpack_from('<I',data,32)[0]+sec['index']*40+4,8)
        elif tag=='fake_ROM_ABS':struct.pack_into('<H',data,symoff(obj,'__tsl9v4160_rom_entry')+14,0xfff1)
        elif tag=='inherited_code_byte':data[next(s for s in obj.sections if s['flags']==6 and s['size'])['offset']]^=1
        elif tag=='RELA_addend':
            table=next(s for s in obj.sections if s['type']==4 and s['size']);at=table['offset']+8;struct.pack_into('<i',data,at,struct.unpack_from('<i',data,at)[0]+1)
        elif tag=='missing_RELA':
            table=next(s for s in obj.sections if s['type']==4 and s['size']);struct.pack_into('<I',data,struct.unpack_from('<I',data,32)[0]+table['index']*40+20,table['size']-12)
        else:
            row=PREV['raw_section_symbols'](obj,sec['name'])[0];table=obj.sections[row['table']];data[table['offset']+row['index']*16+13]=2
        path=folder/('COUNTERCASE-image-'+tag+'.o');path.write_bytes(data)
        try:merged_gate(ELF(path),before,unit,sections,allocations)
        except AssertionError as e:reason=str(e)
        else:raise AssertionError('Accepted actual ELF image-fidelity countercase '+tag)
        rows.append(dict(case=tag,path=str(path),sha256=sha(path),rejected=True,reason=reason))
    for tag,data in [('changed_byte',bytes([raw[0]^1])+raw[1:]),('truncated',raw[:-1]),('appended',raw+b'\0'),('wrong_image_base',b'\0'*4+raw[:-4])]:
        path=folder/('COUNTERCASE-NOT-FLASH-VALIDATED-'+tag+'.bin');path.write_bytes(data)
        try:image_gate(path,witness,allocations,raw)
        except AssertionError as e:reason=str(e)
        else:raise AssertionError('Accepted invalid flat image '+tag)
        rows.append(dict(case=tag,path=str(path),sha256=sha(path),rejected=True,reason=reason))
    return rows

def main():
    p=argparse.ArgumentParser();p.add_argument('--current-receipt',type=Path,required=True);p.add_argument('--proof-root',type=Path,required=True)
    p.add_argument('--plan',type=Path,default=ROOT/'evidence/image-fidelity-plan.json');p.add_argument('--firmware',type=Path)
    p.add_argument('--expect-missing-baseline',action='store_true');a=p.parse_args()
    need(sha(ROOT/'verify-retained-data-extension.py')=='753637d02c540711014b6eb2b9d664138681106d211a013c591bf66ae2a709bb','Unchanged full681 verifier')
    prior=read(a.current_receipt);need(prior['passed']and len(prior['allocations'])==681 and prior['source_coverage_bytes']==76705,'Actual prior681 native stage')
    for n,h in prior['source_files'].items():need(sha(ROOT/n)==h,'Every inherited source unchanged')
    if a.firmware is None:a.firmware=next((W/n for n in ['firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin','exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin']if(W/n).is_file()),None)
    need(a.firmware is not None and sha(a.firmware)==SOURCE_SHA,'Exact original candidate source');raw=a.firmware.read_bytes();sections=sections_for(prior,raw);plan=read(a.plan)
    need(plan['schema']=='ID2966-opaque-original-image-native-plan-v1'and plan['sections']==sections,'Complete95B source-only carriers, not code/data semantic classification')
    need(plan['source']=='src/image_only_native.c'and plan['header']=='src/image_only_native.h','Exact native source/header')
    for field in ['source','header']:need(sha(ROOT/plan[field])==plan[field+'_sha256'],'Exact reviewed native producer source')
    for proof in plan['proofs']:
        path=a.proof_root/proof['scope']/proof['seal'];need(sha(path)==proof['sha256']and read(path)['passed'],'Completed exact source/producer proof')
        for row in read(path)['members']:
            child=(path.parent/row['path']).resolve();need(child.is_relative_to(path.parent.resolve())and child.stat().st_size==row['bytes']and sha(child)==row['sha256'],'Actual sealed proof member')
    need({x['scope']for x in plan['proofs']}=={'residual-source','opaque-producer'}and len(plan['proofs'])==2,'Two independent opaque-admission scopes')
    if a.expect_missing_baseline:
        try:PREV['storage_gate'](ELF(Path(prior['modes']['c']['integrated_object'])),sections)
        except AssertionError as error:
            need(str(error)=='Every available fragment has actual storage','Expected original storage-gap RED')
            print(json.dumps(dict(expected_red=True,missing_source_bytes=95,reason=str(error))));return
        raise AssertionError('Original681 stage unexpectedly contains opaque source carriers')
    work=ROOT/'build'/('image-fidelity-'+uuid.uuid4().hex);work.mkdir(parents=True)
    oldproof=next(W/n for n in ['apk-analysis/tsl9-v4160-data-addresses-2026-10-21','analysis/v4160-data-addresses-2026-10-21']if(W/n).is_dir())
    _,output=run([sys.executable,'-X','utf8','-B',ROOT/'verify-retained-data-extension.py','--current-receipt',prior['baseline_receipt'],
        '--proof-root',oldproof,'--firmware',a.firmware.resolve()],work,'unchanged681-gate')
    freshpath=Path(json.loads(output.decode().strip().splitlines()[-1])['receipt']);fresh=read(freshpath)
    need(fresh['passed']and fresh['allocations']==prior['allocations'],'Fresh complete681 native gate');alloc=allocations_for(fresh,sections)
    layout=work/'original-image-layout.ld';text='OUTPUT_ARCH(riscv)\nENTRY(__tsl9v4160_image_entry)\nSECTIONS {\n'
    for n,s in sorted(alloc.items(),key=lambda kv:kv[1]['originalVA']):text+=' '+n+' '+hex(s['originalVA'])+(' (NOLOAD)'if s['kind']=='RAM'else'')+' : { KEEP(*('+n+')) }\n ASSERT(SIZEOF('+n+')=='+str(s['bytes'])+', "Storage size changed")\n'
    layout.write_text(text+' /DISCARD/ : { *(.comment) *(.note.GNU-stack) }\n}\n');modes={}
    for mode,lang,std in [('c','c','c11'),('cpp','c++','c++17')]:
        folder=work/mode;folder.mkdir();before=ELF(Path(fresh['modes'][mode]['integrated_object']));bw=ELF(freshpath.parent/mode/'ADDRESS-WITNESS-ONLY.elf')
        need(sha(Path(fresh['modes'][mode]['integrated_object']))==prior['modes'][mode]['integrated_sha256'],'Exact current681 C/C++ object')
        up=folder/'opaque-image.o';run([BIN/'clang.exe','--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-fno-builtin','-fno-stack-protector','-Wall','-Wextra','-Werror','-x',lang,'-std='+std,'-c',ROOT/plan['source'],'-o',up],folder,'compile-opaque-image')
        unit=ELF(up);need(unit.kind==1 and not unit.relocations and not BASE['und'](unit),'Opaque literal unit has no code, RELA or dependency')
        CORE['allocations_gate'](unit,{s['name']:s for s in sections});PREV['storage_gate'](unit,sections);PREV['globals_gate'](unit,{s['symbol']for s in sections})
        op=folder/'source-image-merged.o';run([BIN/'ld.lld.exe','-r','--no-relax',Path(fresh['modes'][mode]['integrated_object']),up,'-o',op],folder,'merge-image-storage')
        obj=ELF(op);merged_gate(obj,before,unit,sections,alloc)
        strict=folder/'strict-incomplete.elf';_,error=run([BIN/'ld.lld.exe','--no-relax','--error-limit=0','-T',layout,op,'-o',strict],folder,'strict-final-link',False)
        need(not strict.exists()and set(re.findall(r'undefined symbol: (\w+)',error.decode(errors='replace')))=={'__tsl9v4160_rom_entry'},'Strict link still rejects actual missing resident')
        numeric=folder/'ADDRESS-WITNESS-ONLY.ld';numeric.write_text('/* Numeric original resident address obligation only. */\n__tsl9v4160_rom_entry = 0x40000;\n')
        wp=folder/'ADDRESS-WITNESS-ONLY.elf';run([BIN/'ld.lld.exe','--no-relax','-T',layout,'-T',numeric,op,'-o',wp],folder,'numeric-original-layout')
        witness=ELF(wp);CORE['allocations_gate'](witness,alloc);PREV['storage_gate'](witness,sections,True)
        omitted=linked_gate(witness,bw,obj,before,unit,sections,alloc)
        for n,s in alloc.items():
            need(witness.byname[n]['address']==s['originalVA'],'Every original allocation VA')
            if s['kind']!='RAM':need(witness.byname[n]['data']==raw[s['originalVA']-0x8000:s['originalVA']-0x8000+s['bytes']],'Every admitted byte still original')
        for n in fresh['allocations']:need(witness.byname[n]['data']==bw.byname[n]['data'],'All inherited final bytes unchanged')
        PREV['record_gate'](witness,alloc,raw,True);CORE['OLD']['fixed_table_check'](witness,read(ROOT/'evidence/reachable-code-plan.json'),alloc,raw,True)
        flat=folder/'NOT-FLASH-VALIDATED-original-layout.bin';run([BIN/'llvm-objcopy.exe','-O','binary',wp,flat],folder,'export-offline-image-fixture')
        image=image_gate(flat,witness,alloc,raw);coverage=CORE['coverage'](witness,alloc,raw)
        need(coverage['source_coverage_bytes']==76800 and coverage['unrepresented_bytes']==0 and not coverage['gaps'],'Full source storage, no gap filling')
        modes[mode]=dict(passed=True,unit_object=str(up),unit_sha256=sha(up),integrated_object=str(op),integrated_sha256=sha(op),
            numeric_witness=str(wp),numeric_witness_sha256=sha(wp),flat_fixture=str(flat),flat_fixture_sha256=sha(flat),image=image,coverage=coverage,
            undefined_symbols=['__tsl9v4160_rom_entry'],strict_rejected=True,discarded_new_unit_metadata=omitted,
            actual_countercases=countercases(obj,before,unit,sections,alloc,witness,flat,raw,folder))
    need(all(modes['c'][k]==modes['cpp'][k]for k in ['unit_sha256','integrated_sha256','numeric_witness_sha256','flat_fixture_sha256','image','coverage']),'C/C++ source-image artifacts identical')
    sources=dict(fresh['source_files'])
    for n in [plan['source'],plan['header'],a.plan.resolve().relative_to(ROOT).as_posix(),Path(__file__).name]:sources[n]=sha(ROOT/n)
    result=dict(schema='ID2966-source-image-fidelity-native-v1',passed=True,firmware_sha256=SOURCE_SHA,source_files=sources,
        baseline_receipt=str(freshpath),baseline_receipt_sha256=sha(freshpath),allocations=alloc,modes=modes,
        original_source_bytes=76800,source_coverage_bytes=76800,new_opaque_image_bytes=95,new_code_bytes=0,new_canonical_contracts_closed=0,
        callback_runtime_contracts_still_unproved=fresh['callback_runtime_contracts_still_unproved'],data_runtime_contracts_still_unproved=fresh['data_runtime_contracts_still_unproved'],
        unprovided_source_exterior_read_union_bytes=1144,reference_ROM_bytes_supplied=0,source_image_BIN_created=True,
        original_data_object_extents_proved=False,data_runtime_domains_complete=False,original_C_ABIs_proved=False,IRQ_ABI_proved=False,
        firmware_executed=False,emulation=False,network=False,hardware=False,flashable_BIN_proved=False,native_runtime_ready=False,ota_verified=False,goal_complete=False)
    path=work/'verification.json';path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,receipt=str(path),sha256=sha(path),source_bytes=76800,opaque_bytes=95,ELF_UND=1,source_image_BIN_created=True,flashable_BIN_proved=False,OTA_ready=False)))
if __name__=='__main__':main()
