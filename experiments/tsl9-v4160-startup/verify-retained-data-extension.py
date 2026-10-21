"""Source-backed data fragments and pointer constants; never emit firmware."""
import argparse,collections,json,re,runpy,struct,sys,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parent;W=ROOT.parents[1]
ADDRESS=runpy.run_path(str(ROOT/'verify-callback-address-bindings.py'))
CORE=ADDRESS['PREV'];BASE=ADDRESS['BASE'];ELF=ADDRESS['ELF'];BIN=ADDRESS['BIN']
run=ADDRESS['run'];need=ADDRESS['need'];sha=ADDRESS['sha'];digest=ADDRESS['digest'];read=ADDRESS['read']
roles=ADDRESS['roles'];sym_offset=ADDRESS['sym_offset'];sx=ADDRESS['sx']
DATA=[0x19de0,0x19dfc,0x1a078,0x1a0d8,0x1a430,0x1a454,0x1a478,0x1a638,0x1a668,0x1a674,0x1aae8,0x1ab48]
RECORDS={0x19de0:[0x8b90,0,0x85c8],0x19dfc:[0,0x888c,0],
         0x1a668:[0x10d30,0x10d2e,0],0x1a674:[0x10c36,0x11544,0x10c34]}
PROOFS={
    'data-obligations':'2dfcdcc1647b49ed29fd94636665e742d8a59ca49406e79c0c1d53c652267165',
    'record-views':'8c588d92302d05ef6345f9f536a62b4d2b9bf15b75dcd19f1b62dc145315037c',
    'retained-read-domains':'78b3c10befe74d2c13d276abceb2d7036bf5ded800d7eda082f114d4dc7b08aa'}

def intervals(points):
    rows=[]
    for a in sorted(points):
        if rows and rows[-1][1]==a:rows[-1][1]=a+1
        else:rows.append([a,a+1])
    return rows

def expected_sections(base,raw):
    # Dense potential readset is separately source-proved, not an observed device trace.
    admitted=set()
    for s in base['allocations'].values():
        if s['kind']=='RAM':continue
        a,b=s['originalVA'],s['originalVA']+s['bytes']
        if a<0x1ac00 and b>0x1a078:
            need(s['kind']=='RO','No instruction storage reclassified as data')
            admitted.update(range(max(a,0x1a078),min(b,0x1ac00)))
    gaps=intervals(set(range(0x1a078,0x1ac00))-admitted)
    need(len(gaps)==17 and sum(b-a for a,b in gaps)==261,'Complete available source/read-domain difference')
    spans=[[0x19de0,0x19dec],[0x19dfc,0x19e08]]
    for a,b in gaps:
        if(a,b)==(0x1a636,0x1a680):spans.extend([[a,0x1a668],[0x1a668,0x1a674],[0x1a674,b]])
        else:spans.append([a,b])
    spans.sort();need(len(spans)==21 and sum(b-a for a,b in spans)==285,'Exactly21 genuine RO fragments285B')
    out=[]
    for a,b in spans:
        need(0x8000<=a<b<=0x8000+len(raw),'No source-exterior byte supplied')
        need(not any(a<s['originalVA']+s['bytes']and s['originalVA']<b for s in base['allocations'].values()),'No inherited storage duplication')
        data=raw[a-0x8000:b-0x8000]
        out.append(dict(name='.rodata.tsl9v4160.retained_data_'+format(a,'x'),
            symbol='__tsl9v4160_retained_data_'+format(a,'x'),originalVA=a,bytes=b-a,kind='RO',flags=2,alignment=1,
            sha256=digest(data),raw_hex=data.hex(),capture_role='observed-three-word-record-view'if a in RECORDS else'available-original-read-fragment'))
    return out

def allocations_union(base,sections):
    result=dict(base['allocations'])
    for s in sections:result[s['name']]=dict(s,end_exclusive=s['originalVA']+s['bytes'])
    return result

def expected_bindings(before,base,allocations,raw):
    result=[]
    for va in DATA:
        name='__tsl9v4160_'+('conditional_address_'if va in(0x1a638,0x1a668,0x1a674)else'address_')+format(va,'x')
        need(sum(s['name']==name for s in before.symbols)==1,'Exactly one original data address symbol')
        s=before.symbol[name];need((s['index'],s['bind'],s['type'],s['size'],s['value'])==(0,1,0,0,0),'Original address-only UND role')
        owners=[(n,v)for n,v in allocations.items()if v['originalVA']<=va<v['originalVA']+v['bytes']]
        need(len(owners)==1 and owners[0][1]['kind']=='RO','Every address has unique real RO byte storage')
        section,item=owners[0]
        refs=[r for r in before.relocations if r['target']==name]
        need(len(refs)==1 and refs[0]['type']==23 and refs[0]['addend']==0,'Exactly one source HI20 data-address obligation')
        r=refs[0];pc=base['allocations'][r['section']]['originalVA']+r['offset']
        hi,lo=struct.unpack_from('<II',raw,pc-0x8000)
        need(hi&127==0x17 and lo&127==0x13 and(lo>>12)&7==0 and
            (hi>>7)&31==(lo>>15)&31==(lo>>7)&31,'Original own-register AUIPC/ADDI materialization')
        need((pc+sx(hi&0xfffff000,32)+sx(lo>>20,12))&0xffffffff==va,'Original encoded data pointer constant')
        lows=[q for q in before.relocations if q['section']==r['section']and q['offset']==r['offset']+4]
        need(len(lows)==1 and lows[0]['type']==24 and lows[0]['addend']==0,'One original LOW12_I at next instruction')
        low=before.symbols[lows[0]['symbol_index']]
        need(low['index']==before.byname[r['section']]['index']and low['value']==r['offset'],'LOW owns the correct HI')
        result.append(dict(name=name,originalVA=va,section=section,offset=va-item['originalVA'],
            reference_section=r['section'],reference_offset=r['offset'],referenceVA=pc,
            raw_HI_LOW=raw[pc-0x8000:pc-0x8000+8].hex(),elf_type=0,size=0))
    return result

def label_script(allocations,bindings):
    text='/* Data address labels only. Complete read domains and runtime ABI remain unproved. */\nOUTPUT_ARCH(riscv)\nSECTIONS {\n'
    for n,s in allocations.items():
        text+=' '+n+' 0'+(' (NOLOAD)'if s['kind']=='RAM'else'')+' : {\n'
        for b in bindings:
            if b['section']==n:text+=' '+b['name']+' = . + '+str(b['offset'])+';\n'
        text+=' KEEP(*('+n+'))\n }\n'
    return text+'}\n'

def globals_gate(obj,names):
    rows=[s for s in obj.symbols if s['name']and s['index']!=0 and s['bind']in(1,2)]
    need(len(rows)==len(names)and {s['name']for s in rows}==names and all(s['bind']==1 for s in rows),'Exact real globals, no extra ABS/weak/alias provider')

def storage_gate(obj,sections,linked=False):
    for s in sections:
        need(s['name']in obj.byname and s['symbol']in obj.symbol,'Every available fragment has actual storage')
        sec=obj.byname[s['name']];sym=obj.symbol[s['symbol']]
        need((sec['type'],sec['flags'],sec['size'],sec['alignment'])==(1,2,s['bytes'],1),'Exact finite RO allocation and alignment')
        need(sec['data']==bytes.fromhex(s['raw_hex']),'Every available original data byte retained')
        need((sym['index'],sym['value'],sym['bind'],sym['type'],sym['size'])==
            (sec['index'],s['originalVA']if linked else 0,1,1,s['bytes']),'Exact private fragment OBJECT, not original object-extent claim')
        need(obj.raw[sym_offset(obj,s['symbol'])+13]==0,'Default fragment visibility')
        need(not linked or sec['address']==s['originalVA'],'Original data VA placement')

def record_gate(obj,allocations,raw,linked=False):
    result=[]
    for va,words in RECORDS.items():
        owners=[(n,s)for n,s in allocations.items()if s['originalVA']==va and s['bytes']==12 and s['kind']=='RO']
        need(len(owners)==1,'One actual12B observed record view')
        name,_=owners[0];sec=obj.byname[name]
        need(list(struct.unpack('<3I',sec['data']))==words and sec['data']==raw[va-0x8000:va-0x8000+12],'All observed record words and nulls original')
        need(not any(r['section']==name for r in obj.relocations),'Record words use explicit original-VA fixed semantics, no added R32')
        for index,target in enumerate(words):
            if target==0:continue
            code=[(n,s)for n,s in allocations.items()if s['kind']=='code'and s['originalVA']<=target<s['originalVA']+s['bytes']]
            need(len(code)==1,'Every nonzero record word has real code storage')
            n,s=code[0];value=target if linked else target-s['originalVA']
            anchors=[p for p in obj.symbols if p['name']and p['index']==obj.byname[n]['index']and
                p['value']==value and p['bind']==1 and p['type']==0 and p['size']==0]
            need(anchors,'Record target is exact existing private instruction entry')
            if linked:
                sec2=obj.byname[n];off=target-s['originalVA'];width=4 if raw[target-0x8000]&3==3 else 2
                need(sec2['address']==s['originalVA']and sec2['data'][off:off+width]==raw[target-0x8000:target-0x8000+width],'Actual fixed-VA target instruction bytes')
        result.append(dict(originalVA=va,words=words,bytes=12,symbolic_R32=0,original_VA_fixed=True,
            original_C_object_extent_proved=False,actual_resident_read_extent_proved=False))
    return result

def binding_gate(obj,before,allocations,bindings,addresses):
    need(obj.kind==1,'Actual relocatable data-binding object')
    CORE['allocations_gate'](obj,allocations);CORE['inherited_gate'](before,obj,allocations)
    names={b['name']for b in bindings}
    expected=collections.Counter((b['name'],b['section'],b['offset'],0,16,0)for b in bindings)
    need(collections.Counter({k:v for k,v in roles(obj,set()).items()if k[0]in names})==expected,'Exactly12 section-backed data labels, no duplicate/ABS/OBJECT extent')
    need(roles(obj,names)==roles(before,names),'Every nonbinding raw symbol occurrence retained')
    definitions={s['name']for s in before.symbols if s['name']and s['index']!=0 and s['bind']in(1,2)}|names
    globals_gate(obj,definitions)
    need(BASE['und'](obj)==BASE['und'](before)-names=={'__tsl9v4160_rom_entry'},'Only data addresses resolved; actual resident remains UND')
    need(CORE['OLD']['relocation_semantics'](obj,allocations,addresses)==
         CORE['OLD']['relocation_semantics'](before,allocations,addresses),'All original semantic relocation expressions unchanged')
    expected=collections.Counter();lookup={b['name']:b for b in bindings}
    for(key,count)in CORE['raw_relocation_roles'](before).items():
        owner,off,typ,role,addend=key
        if role[0]in lookup:
            b=lookup[role[0]];need(role==(b['name'],'0',0,0,16,0),'Exact original data UND role')
            role=(b['name'],b['section'],b['offset'],0,16,0)
        expected[(owner,off,typ,role,addend)]+=count
    need(CORE['raw_relocation_roles'](obj)==expected,'Exact data-address RELA target-role transition; signed A/site/type retained')

def raw_section_symbols(obj,owner):
    rows=[]
    for table in obj.sections:
        if table['type']!=2:continue
        need(table['entsize']==16 and table['size']%16==0,'Actual ELF32 symbol records')
        strings=obj.sections[table['link']]['data']
        for index in range(table['size']//16):
            at=index*16;name,value,size,info,other,section=struct.unpack_from('<IIIBBH',table['data'],at)
            if section!=obj.byname[owner]['index']or info&15!=3:continue
            name=strings[name:strings.index(0,name)].decode();refs=[]
            for rela in obj.sections:
                if rela['type']!=4 or rela['link']!=table['index']:continue
                need(rela['entsize']==12 and rela['size']%12==0,'Actual ELF32 RELA records')
                for pos in range(0,rela['size'],12):
                    off,rinfo,addend=struct.unpack_from('<IIi',rela['data'],pos)
                    if rinfo>>8==index:refs.append(dict(section=obj.sections[rela['info']]['name'],offset=off,type=rinfo&255,addend=addend))
            rows.append(dict(table=table['index'],index=index,role=[name,owner,value,size,info,other],references=refs))
    return rows

def unreferenced_new_sections(unit,merged,bound,before,allocations):
    old={s['name']for s in before.sections if s['flags']&2 and s['size']}
    new=set(allocations)-old
    need(len(new)==21 and sum(allocations[n]['bytes']for n in new)==285,'Only21 new finite RO carriers may omit generated SECTION metadata')
    result=[]
    for owner in sorted(new):
        allocation=allocations[owner]
        need((allocation['kind'],allocation['flags'],allocation['alignment'])==('RO',2,1),'Only new RO storage SECTION metadata')
        stages={}
        for label,obj,count in [('unit',unit,0),('merge',merged,1),('bound',bound,1)]:
            section=obj.byname[owner]
            need((section['type'],section['flags'],section['size'],section['alignment'])==(1,2,allocation['bytes'],1),'Actual new finite PROGBITS carrier')
            records=raw_section_symbols(obj,owner)
            need(len(records)==count and all(x['role']==['',owner,0,0,3,0]and not x['references']for x in records),
                 'Only exact new unreferenced anonymous SECTION records may disappear')
            stages[label]=dict(records=records,absent=count==0)
        result.append(dict(role=['',owner,0,0,3,0],count=1,originalVA=allocation['originalVA'],stages=stages,
            reason='new_linker_generated_unreferenced_local_SECTION_omitted_by_final_link'))
    return result

def linked_roles_gate(witness,baseline,bound,before,names,allocations,bindings,unit,merged):
    old=roles(before,names);partial=roles(bound,names)
    need(not old-partial,'All nonbinding original symbols remain')
    extras=collections.Counter();discarded=[];unit_roles=roles(unit,set())
    section_omissions=unreferenced_new_sections(unit,merged,bound,before,allocations)
    omitted={tuple(x['role']):x for x in section_omissions}
    for role,count in(partial-old).items():
        name,owner,value,size,info,other=role
        if role in omitted:
            need(count==1,'One newly generated anonymous SECTION record')
            discarded.append(omitted[role]);continue
        if owner=='.comment':
            section=unit.byname[owner]
            metadata={k:section[k]for k in ['type','flags','size','alignment','entsize']}
            need(re.fullmatch(r'\$d\.\d+',name)is not None and (value,size,info,other)==(0,0,0,0)and
                 unit_roles[role]==count and tuple(metadata.values())==(1,48,159,1,1)and not section['flags']&2 and
                 not any(r['section']==owner or r['target']==name for r in unit.relocations),
                 'Only actual new unit nonallocated comment mapping metadata may be discarded')
            discarded.append(dict(role=list(role),count=count,section_metadata=metadata,section_data_sha256=digest(section['data']),
                reason='new_unit_local_mapping_marker_in_explicitly_discarded_nonallocated_comment'))
            continue
        if owner in allocations:value+=allocations[owner]['originalVA']
        extras[(name,owner,value,size,info,other)]+=count
    need(roles(witness,names)==roles(baseline,names)+extras,'All inherited final symbol records plus exact linked unit metadata')
    expected=collections.Counter((b['name'],b['section'],b['originalVA'],0,16,0)for b in bindings)
    need(collections.Counter({k:v for k,v in roles(witness,set()).items()if k[0]in names})==expected,'Exactly12 real final data labels')
    return discarded

def linked_metadata_countercases(witness,baseline,bound,before,names,allocations,bindings,unit,merged,folder):
    out=[]
    def audit(w,b):return linked_roles_gate(w,baseline,b,before,names,allocations,bindings,unit,merged)
    records=unreferenced_new_sections(unit,merged,bound,before,allocations)
    for tag in ['referenced_new_SECTION','new_SECTION_visibility','inherited_SECTION_metadata']:
        obj=bound;data=bytearray(obj.raw)
        if tag=='inherited_SECTION_metadata':
            old={s['name']for s in before.sections if s['flags']&2 and s['size']}
            table=next(s for s in obj.sections if s['type']==2)
            matches=[]
            for owner in sorted(old):matches.extend(raw_section_symbols(obj,owner))
            need(matches,'Actual inherited final SECTION available for negative test')
            row=matches[0];table=obj.sections[row['table']];data[table['offset']+row['index']*16+13]=2
        else:
            row=records[0]['stages']['bound']['records'][0];table=obj.sections[row['table']]
            if tag=='new_SECTION_visibility':data[table['offset']+row['index']*16+13]=2
            else:
                rela=next(s for s in obj.sections if s['type']==4 and s['link']==table['index']and s['size'])
                at=rela['offset'];info=struct.unpack_from('<I',data,at+4)[0]
                struct.pack_into('<I',data,at+4,(row['index']<<8)|(info&255))
        path=folder/('COUNTERCASE-linked-'+tag+('.elf'if obj is witness else'.o'));path.write_bytes(data)
        try:audit(ELF(path)if obj is witness else witness,ELF(path)if obj is bound else bound)
        except AssertionError as error:reason=str(error)
        else:raise AssertionError('Accepted metadata countercase '+tag)
        out.append(dict(case=tag,path=str(path),sha256=sha(path),rejected=True,reason=reason))
    return out

def countercases(obj,audit,sections,bindings,folder):
    first=bindings[0];private=sections[0];out=[]
    ref=next(r for r in obj.relocations if r['target']==first['name'])
    low=next(r for r in obj.relocations if r['section']==ref['section']and r['offset']==ref['offset']+4)
    tags=['ABS_data_label','FUNC_data_label','OBJECT_extent','wrong_label_offset','duplicate_data_label',
          'private_size','data_byte','writable_data','ROM_ABS_provider','HI_addend','missing_LOW',
          'equivalent_private_target','record_pointer_word','old_code_byte','old_local_visibility','interior_label_zero']
    for tag in tags:
        data=bytearray(obj.raw);spot=sym_offset(obj,first['name']);sec=obj.byname[private['name']]
        if tag=='ABS_data_label':struct.pack_into('<H',data,spot+14,0xfff1)
        elif tag=='FUNC_data_label':data[spot+12]=0x12
        elif tag=='OBJECT_extent':data[spot+12]=0x11;struct.pack_into('<I',data,spot+8,12)
        elif tag=='wrong_label_offset':struct.pack_into('<I',data,spot+4,first['offset']+1)
        elif tag in('duplicate_data_label','old_local_visibility'):
            local=next(s for s in obj.symbols if s['name'].startswith('.L')and s['bind']==0 and 0<s['index']<0xff00)
            at=sym_offset(obj,local['name'])
            if tag=='duplicate_data_label':struct.pack_into('<I',data,at,struct.unpack_from('<I',data,spot)[0])
            else:data[at+13]=2
        elif tag=='private_size':struct.pack_into('<I',data,sym_offset(obj,private['symbol'])+8,private['bytes']+1)
        elif tag=='data_byte':data[sec['offset']]^=1
        elif tag=='writable_data':struct.pack_into('<I',data,struct.unpack_from('<I',data,32)[0]+sec['index']*40+8,3)
        elif tag=='ROM_ABS_provider':struct.pack_into('<H',data,sym_offset(obj,'__tsl9v4160_rom_entry')+14,0xfff1)
        elif tag in('HI_addend','missing_LOW','equivalent_private_target'):
            r=low if tag=='missing_LOW'else ref;at=CORE['record_offset'](obj,r['section'],r['offset'],r['type'])
            if tag=='HI_addend':struct.pack_into('<i',data,at+8,1)
            elif tag=='missing_LOW':struct.pack_into('<I',data,at+4,struct.unpack_from('<I',data,at+4)[0]&0xffffff00)
            else:
                index=next(i for i,s in enumerate(obj.symbols)if s['name']==private['symbol'])
                struct.pack_into('<I',data,at+4,(index<<8)|r['type'])
                struct.pack_into('<i',data,at+8,first['offset'])
        elif tag=='record_pointer_word':data[obj.byname['.rodata.tsl9v4160.retained_data_1a674']['offset']]^=2
        elif tag=='old_code_byte':
            old=next(s for s in obj.sections if s['flags']==6 and s['size']);data[old['offset']]^=1
        else:
            interior=next(b for b in bindings if b['offset']>0)
            struct.pack_into('<I',data,sym_offset(obj,interior['name'])+4,0)
        path=folder/('COUNTERCASE-retained-'+tag+'.o');path.write_bytes(data)
        try:audit(ELF(path))
        except AssertionError as error:reason=str(error)
        else:raise AssertionError('Accepted retained-data actual ELF mutant '+tag)
        out.append(dict(case=tag,path=str(path),sha256=sha(path),rejected=True,reason=reason))
    return out

def verify_proofs(plan,root):
    need(len(PROOFS)==3 and len(plan['proofs'])==3 and
         {r['scope']for r in plan['proofs']}==set(PROOFS),'Three pinned independent admission scopes')
    for row in plan['proofs']:
        path=root/row['scope']/row['seal']
        need(row['sha256']==PROOFS[row['scope']]and sha(path)==row['sha256']and read(path)['passed'],'Exact completed admission seal')
        for member in read(path)['members']:
            p=(path.parent/member['path']).resolve()
            need(p.is_relative_to(root.resolve())and p.stat().st_size==member['bytes']and sha(p)==member['sha256'],'Actual sealed admission member')

def main():
    p=argparse.ArgumentParser();p.add_argument('--current-receipt',type=Path,required=True)
    p.add_argument('--proof-root',type=Path,required=True);p.add_argument('--firmware',type=Path)
    p.add_argument('--plan',type=Path,default=ROOT/'evidence/retained-data-plan.json')
    p.add_argument('--bindings',type=Path,default=ROOT/'evidence/retained-data-addresses.json')
    p.add_argument('--expect-missing-baseline',action='store_true');a=p.parse_args()
    need(sha(ROOT/'verify-callback-address-bindings.py')=='5b03f76a31bd527a96669d26491f2f0a32ddf7ac91c563ae7b380a5f89b31c6c','Unchanged complete13-UND verifier')
    prior=read(a.current_receipt);plan=read(a.plan);spec=read(a.bindings)
    need(prior['passed']and prior['schema']=='ID2966-callback-address-native-bindings-v1'and
         len(prior['allocations'])==660 and prior['source_coverage_bytes']==76420,'Actual current660/13 native stage')
    for name,h in prior['source_files'].items():need(sha(ROOT/name)==h,'Every inherited source unchanged')
    if a.firmware is None:a.firmware=next((W/n for n in [
        'exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin',
        'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin']if(W/n).is_file()),None)
    need(a.firmware is not None and sha(a.firmware)==CORE['FIRMWARE_SHA'],'Exact original ID2966 source')
    raw=a.firmware.read_bytes();sections=expected_sections(prior,raw)
    need(plan['schema']=='ID2966-retained-data-native-plan-v1'and plan['source_firmware_sha256']==digest(raw),'Source-bound finite-data plan')
    need(plan['source']=='src/retained_data_native.c'and plan['header']=='src/retained_data_native.h','Exact local native source/header')
    need([{k:s[k]for k in sections[0]}for s in plan['sections']]==sections,'Exact admitted21 source fragments, not arbitrary hole fill')
    for field in ['source','header']:need(sha(ROOT/plan[field])==plan[field+'_sha256'],'Reviewed native C/C++ source/header')
    verify_proofs(plan,a.proof_root)
    bp=Path(prior['modes']['c']['integrated_object']);before=ELF(bp)
    need(sha(bp)==prior['modes']['c']['integrated_sha256']=='9952f90244819aa224ccbfd2b3de951b62507d4e6557e7eb75be65fe9cab457f','Actual13-UND baseline C object')
    allocations=allocations_union(prior,sections);bindings=expected_bindings(before,prior,allocations,raw)
    need(spec['schema']=='ID2966-retained-data-addresses-v1'and spec['source']=='layout/retained-data-addresses.ld'and spec['native_plan_sha256']==sha(a.plan)and
         spec['bindings']==bindings and spec['data_runtime_contracts_closed']==0 and spec['OTA_ready']is False,'Address constants separated from unproved runtime contracts')
    need(sha(ROOT/spec['source'])==spec['source_sha256']and
         (ROOT/spec['source']).read_text()==label_script(allocations,bindings),'Exact true-section data-label linker source')
    if a.expect_missing_baseline:
        try:storage_gate(before,sections)
        except AssertionError as error:
            need(str(error)=='Every available fragment has actual storage','Expected missing-data RED')
            print(json.dumps(dict(expected_red=True,reason=str(error))));return
        raise AssertionError('Baseline unexpectedly provides new285 source bytes')
    work=ROOT/'build'/('retained-data-extension-'+uuid.uuid4().hex);work.mkdir(parents=True)
    oldproof=next((W/n for n in ['apk-analysis/tsl9-v4160-contract-audit-2026-10-21',
        'analysis/v4160-contract-audit-2026-10-21']if(W/n).is_dir()),None)
    need(oldproof is not None,'Retained complete13-UND proof root')
    _,output=run([sys.executable,'-X','utf8','-B',ROOT/'verify-callback-address-bindings.py',
        '--current-receipt',prior['baseline_receipt'],'--proof-root',oldproof,'--firmware',a.firmware.resolve()],work,'unchanged13-gate')
    fresh_path=Path(json.loads(output.decode().strip().splitlines()[-1])['receipt']);base=read(fresh_path)
    need(base['passed']and base['allocations']==prior['allocations'],'Fresh full13-UND native gate')
    allocations=allocations_union(base,sections);need(len(allocations)==681,'Exactly681 allocated sections')
    layout=work/'original-address-layout.ld';text='OUTPUT_ARCH(riscv)\nENTRY(__tsl9v4160_image_entry)\nSECTIONS {\n'
    for n,s in sorted(allocations.items(),key=lambda kv:kv[1]['originalVA']):
        text+=' '+n+' '+hex(s['originalVA'])+(' (NOLOAD)'if s['kind']=='RAM'else'')+' : { KEEP(*('+n+')) }\n ASSERT(SIZEOF('+n+')=='+str(s['bytes'])+', "Original size changed")\n'
    layout.write_text(text+' /DISCARD/ : { *(.comment) *(.note.GNU-stack) }\n}\n')
    modes={};names={b['name']for b in bindings};oldplan=read(ROOT/'evidence/reachable-code-plan.json')
    for mode,lang,std in [('c','c','c11'),('cpp','c++','c++17')]:
        folder=work/mode;folder.mkdir();bp=Path(base['modes'][mode]['integrated_object']);before=ELF(bp)
        bw=ELF(fresh_path.parent/mode/'ADDRESS-WITNESS-ONLY.elf')
        need(sha(bp)==prior['modes'][mode]['integrated_sha256'],'Actual C/C++ baseline identity')
        addresses={n:bw.symbol[n]['value']for n in BASE['und'](before)}
        need(len(addresses)==13 and expected_bindings(before,base,allocations,raw)==bindings,'Same13 obligations and12 original pointer constants')
        up=folder/'retained-data.o'
        run([BIN/'clang.exe','--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32',
            '-ffreestanding','-fno-builtin','-fno-stack-protector','-Wall','-Wextra','-Werror','-x',lang,
            '-std='+std,'-c',ROOT/plan['source'],'-o',up],folder,'compile-retained-data')
        unit=ELF(up);need(unit.kind==1 and not unit.relocations and not BASE['und'](unit),'Finite literal data unit; no code, dependency or relocation')
        globals_gate(unit,{s['symbol']for s in sections});storage_gate(unit,sections)
        CORE['allocations_gate'](unit,{s['name']:s for s in sections})
        mp=folder/'data-storage-merged.o'
        run([BIN/'ld.lld.exe','-r','--no-relax',bp,up,'-o',mp],folder,'merge-real-data-storage')
        merged=ELF(mp);CORE['allocations_gate'](merged,allocations);CORE['inherited_gate'](before,merged,base['allocations']);storage_gate(merged,sections)
        CORE['raw_role_gate'](before,unit,merged,plan)
        need(CORE['raw_relocation_roles'](merged)==CORE['raw_relocation_roles'](before),'Storage merge preserves all8280 raw RELA roles/addends')
        need(BASE['und'](merged)==BASE['und'](before),'Storage-only merge closes no pointer/runtime contract')
        globals_gate(merged,{s['name']for s in before.symbols if s['name']and s['index']!=0 and s['bind']in(1,2)}|{s['symbol']for s in sections})
        op=folder/'native-data-addresses.o'
        run([BIN/'ld.lld.exe','-r','--no-relax','-T',ROOT/spec['source'],mp,'-o',op],folder,'bind-data-addresses')
        obj=ELF(op)
        def audit(e):
            binding_gate(e,merged,allocations,bindings,addresses);storage_gate(e,sections)
            record_gate(e,allocations,raw)
        audit(obj);need(len(obj.relocations)==8280,'No new symbolic R32 or other relocation')
        strict=folder/'strict-incomplete.elf'
        _,errors=run([BIN/'ld.lld.exe','--no-relax','--error-limit=0','-T',layout,op,'-o',strict],folder,'strict-final-link',False)
        need(not strict.exists()and set(re.findall(r'undefined symbol: (\w+)',errors.decode(errors='replace')))=={'__tsl9v4160_rom_entry'},'Strict link rejects missing resident implementation')
        numeric=folder/'ADDRESS-WITNESS-ONLY.ld';numeric.write_text('/* Original resident address obligation only; no implementation or ABI. */\n__tsl9v4160_rom_entry = 0x40000;\n')
        wp=folder/'ADDRESS-WITNESS-ONLY.elf'
        run([BIN/'ld.lld.exe','--no-relax','-T',layout,'-T',numeric,op,'-o',wp],folder,'numeric-address-witness')
        witness=ELF(wp);CORE['allocations_gate'](witness,allocations);storage_gate(witness,sections,True)
        discarded_metadata=linked_roles_gate(witness,bw,obj,before,names,allocations,bindings,unit,merged)
        for n,s in allocations.items():
            sec=witness.byname[n];need(sec['address']==s['originalVA']and sec['size']==s['bytes'],'Every original VA/size allocation')
            if s['kind']!='RAM':need(sec['data']==raw[s['originalVA']-0x8000:s['originalVA']-0x8000+s['bytes']],'Every admitted code/data byte original')
        for n in base['allocations']:need(witness.byname[n]['data']==bw.byname[n]['data'],'Every inherited final byte unchanged')
        records=record_gate(witness,allocations,raw,True)
        CORE['OLD']['fixed_table_check'](witness,oldplan,allocations,raw,True)
        coverage=CORE['coverage'](witness,allocations,raw)
        need(coverage['source_coverage_bytes']==76705 and coverage['unrepresented_bytes']==95,'Actual original-source coverage, no exterior data invented')
        modes[mode]=dict(passed=True,unit_object=str(up),unit_sha256=sha(up),storage_merge_object=str(mp),storage_merge_sha256=sha(mp),
            integrated_object=str(op),integrated_sha256=sha(op),numeric_witness_sha256=sha(wp),undefined_symbols=['__tsl9v4160_rom_entry'],
            relocations=len(obj.relocations),allocation_sections=len(allocations),strict_rejected=True,coverage=coverage,
            discarded_new_unit_metadata=discarded_metadata,fixed_original_VA_records=records,
            linked_metadata_countercases=linked_metadata_countercases(witness,bw,obj,before,names,allocations,bindings,unit,merged,folder),
            actual_countercases=countercases(obj,audit,sections,bindings,folder))
    need(all(modes['c'][k]==modes['cpp'][k]for k in ['unit_sha256','storage_merge_sha256','integrated_sha256','numeric_witness_sha256','coverage']),
        'Actual C/C++ unit, merge, bindings, final bytes and accounting identical')
    sources=dict(base['source_files'])
    for n in [plan['source'],plan['header'],str(a.plan.resolve().relative_to(ROOT)),str(a.bindings.resolve().relative_to(ROOT)),spec['source'],Path(__file__).name]:sources[n]=sha(ROOT/n)
    result=dict(schema='ID2966-retained-data-native-extension-v1',passed=True,firmware_sha256=digest(raw),
        source_files=sources,baseline_receipt=str(fresh_path),baseline_receipt_sha256=sha(fresh_path),allocations=allocations,modes=modes,
        bindings=bindings,resolved_data_addresses=12,callback_runtime_contracts_still_unproved=base['callback_runtime_contracts_still_unproved'],
        data_runtime_contracts_still_unproved=sorted(names),unprovided_source_exterior_read_union_bytes=1144,
        new_code_bytes=0,new_RO_bytes=285,source_coverage_bytes=76705,original_data_object_extents_proved=False,
        data_runtime_domains_complete=False,original_C_ABIs_proved=False,opaque_callee_ABIs_proved=False,IRQ_ABI_proved=False,
        firmware_executed=False,emulation=False,network=False,hardware=False,native_bin=False,ota_verified=False)
    out=work/'verification.json';out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,receipt=str(out),sha256=sha(out),new_RO_bytes=285,resolved_data_addresses=12,
        ELF_UND=1,source_coverage_bytes=76705,data_runtime_domains_complete=False,native_BIN=False,OTA_ready=False)))

if __name__=='__main__':main()

