"""Source-bound native extension. Compile/link/inspect only; never emits a BIN."""
import argparse,collections,hashlib,json,re,runpy,struct,sys,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parent;W=ROOT.parents[1]
PREV=runpy.run_path(str(ROOT/'verify-finite-data-extension.py'))
BASE=PREV['BASE'];ELF=PREV['ELF'];BIN=PREV['BIN'];run=PREV['run'];need=PREV['need']
roles=PREV['roles'];sym_offset=PREV['sym_offset']
DIRECT=runpy.run_path(str(ROOT/'verify-dependencies.py'))['direct_target']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
digest=lambda b:hashlib.sha256(b).hexdigest()
read=lambda p:json.loads(p.read_bytes())
sx=lambda x,n:x-(1<<n)if x&(1<<(n-1))else x
MASKS={17:0xfffff000,16:0xfe000f80,23:0xfffff000,
       24:0xfff00000,25:0xfe000f80,45:0x1ffc,44:0x1c7c}

def gate(elf,plan,linked=False,allowed_definitions=None):
    """Inspect actual storage and symbol records, including immediate templates."""
    if allowed_definitions is not None:
        actual=[s for s in elf.symbols if s['name']and s['index']!=0 and s['bind']in(1,2)]
        need(len(actual)==len(allowed_definitions)and {s['name']for s in actual}==set(allowed_definitions)and
             all(s['bind']==1 for s in actual),'Exact declared global definitions; no extra ABS/weak/alias provider')
    sections={s['name']:s for s in plan['sections']}
    for name,item in sections.items():
        need(name in elf.byname,'Missing reachable native section: '+name)
        sec=elf.byname[name]
        need((sec['type'],sec['flags'],sec['size'],sec['alignment'])==
             (1,item['flags'],item['bytes'],item['alignment']),'Exact new allocation/flags/alignment')
        expected=item['sha256']if linked else item['pre_relocation_sha256']
        need(digest(sec['data'])==expected,'Original final bytes or exact relocation template')
        need(not linked or sec['address']==item['originalVA'],'Original VA placement')
    for item in plan['defined_symbols']:
        name=item['name'];need(name in elf.symbol,'Missing actual new symbol')
        sym=elf.symbol[name];section=sections[item['section']];sec=elf.byname[item['section']]
        value=item['originalVA']if linked else item['originalVA']-section['originalVA']
        need((sym['index'],sym['bind'],sym['type'],sym['size'],sym['value'])==
             (sec['index'],1,item['elf_type'],item['size'],value),'Actual new symbol role, no alias/ABS')
        need(elf.raw[sym_offset(elf,name)+13]==0,'Default visibility')

def relocation_semantics(elf,allocations,unresolved):
    def address(symbol):
        if symbol['index']==0:
            need(not symbol['name']or symbol['name']in unresolved,'Every UND address obligation declared')
            return unresolved.get(symbol['name'],0)
        if symbol['index']==0xfff1:return symbol['value']
        section=elf.sections[symbol['index']]
        need(section['name']in allocations,'Allocated relocation owner')
        return allocations[section['name']]['originalVA']+symbol['value']
    return collections.Counter((r['section'],r['offset'],r['type'],
        (address(elf.symbols[r['symbol_index']])+r['addend'])&0xffffffff)for r in elf.relocations)

def fixed_table_check(elf,plan,allocations,raw,linked=False):
    results=[]
    starts={i['va']for i in plan['instructions']}
    for table in plan['existing_original_VA_fixed_tables']:
        name=table['section'];s=allocations[name];sec=elf.byname[name]
        va,off=table['originalVA'],table['section_offset']
        need(va==s['originalVA']+off and table['bytes']==68 and len(table['entries'])==17,'Original fixed17 table interval')
        need(sec['size']==s['bytes']==191 and digest(sec['data'])==s['sha256'],'Every old191 byte retained')
        need(not any(r['section']==name and off<=r['offset']<off+68 for r in elf.relocations),'Fixed table has no new symbolic RELA')
        for i,row in enumerate(table['entries']):
            need(row['index']==i,'Fixed table domain order')
            word=struct.unpack_from('<I',sec['data'],off+4*i)[0]
            target=(va+word)&0xffffffff
            need(word==row['original_u32'] and target==row['target'] and target in starts,'Fixed table raw expression to proved instruction start')
            need(raw[va-0x8000+4*i:va-0x8000+4*i+4]==word.to_bytes(4,'little'),'Fixed table source bytes')
            owners=[(n,v)for n,v in allocations.items()if v['kind']=='code'and v['originalVA']<=target<v['originalVA']+v['bytes']]
            need(len(owners)==1,'Fixed table target has unique real code storage')
            owner,data=owners[0];at=target-data['originalVA'];width=4 if raw[target-0x8000]&3==3 else 2
            if linked:need(elf.byname[owner]['data'][at:at+width]==raw[target-0x8000:target-0x8000+width],'Actual final table target bytes')
        results.append(dict(section=name,entries=17,symbolic_table_relocations=0,original_VA_obligation=True))
    need(len(results)==1,'Exactly one new fixed-table audit, no duplicate storage')
    return results

def source_gate(plan,raw,prior):
    need(plan['schema']=='ID2966-reachable-code-plan-v1'and plan['source_firmware_sha256']==digest(raw),'Explicit source-bound plan')
    sections=plan['sections'];ranges=sorted((s['originalVA'],s['originalVA']+s['bytes'])for s in sections)
    need(len({s['name']for s in sections})==len(sections)and all(a[1]<=b[0]for a,b in zip(ranges,ranges[1:])),'Unique nonoverlapping new storage')
    for s in sections:
        need(s['kind']in('code','RO')and s['flags']==(6 if s['kind']=='code'else 2),'Only genuine code/RO storage')
        need(digest(raw[s['originalVA']-0x8000:s['originalVA']-0x8000+s['bytes']])==s['sha256'],'Every source region original')
        need(not any(s['originalVA']<v['originalVA']+v['bytes']and v['originalVA']<s['originalVA']+s['bytes']for v in prior['allocations'].values()),'No inherited storage duplicated')
    instructions={i['va']:i for i in plan['instructions']}
    need(len(instructions)==len(plan['instructions']),'Unique source instruction starts')
    owners={};templates={s['name']:bytearray(raw[s['originalVA']-0x8000:s['originalVA']-0x8000+s['bytes']])for s in sections}
    for s in sections:
        if s['kind']!='code':continue
        pc=s['originalVA']
        while pc<s['originalVA']+s['bytes']:
            need(pc in instructions,'Full captured instruction partition')
            i=instructions[pc];n=4 if raw[pc-0x8000]&3==3 else 2
            need(i['bytes']==n and i['raw_hex']==raw[pc-0x8000:pc-0x8000+n].hex(),'Raw width and source bytes')
            owners[pc]=s;pc+=n
        need(pc==s['originalVA']+s['bytes'],'Section ends at an instruction boundary')
    need(set(instructions)==set(owners),'No unowned code records')
    relocs=collections.Counter((r['section'],r['offset'],r['type_number'],(r['target_originalVA']+r['addend'])&0xffffffff)for r in plan['relocations'])
    expected=collections.Counter();lows=set()
    for pc,i in instructions.items():
        s=owners[pc];n=i['bytes'];word=int.from_bytes(bytes.fromhex(i['raw_hex']),'little')
        direct=DIRECT(pc,n,word)
        if direct:
            typ,target=direct;expected[(s['name'],pc-s['originalVA'],typ,target&0xffffffff)]+=1
        if n==4 and word&127==0x17:
            need(pc+4 in instructions,'Every AUIPC has a proved next low instruction')
            low=int.from_bytes(bytes.fromhex(instructions[pc+4]['raw_hex']),'little');op=low&127
            need(instructions[pc+4]['bytes']==4 and op in(3,0x13,0x23)and
                 (op!=0x13 or (low>>12)&7==0)and(low>>15)&31==(word>>7)&31,'Raw AUIPC low opcode/register/ADDI pairing')
            immediate=((low>>25)<<5|(low>>7)&31)if op==0x23 else low>>20
            target=(pc+sx(word&0xfffff000,32)+sx(immediate,12))&0xffffffff
            expected[(s['name'],pc-s['originalVA'],23,target)]+=1
            lo_owner=owners[pc+4];expected[(lo_owner['name'],pc+4-lo_owner['originalVA'],25 if op==0x23 else 24,pc)]+=1;lows.add(pc+4)
    need(relocs==expected,'Every raw direct/PCREL obligation, with exact multiplicity')
    for r in plan['relocations']:
        name,at,typ=r['section'],r['offset'],r['type_number'];need(typ in MASKS,'Explicit supported relocation kind')
        s=next(s for s in sections if s['name']==name);pc=s['originalVA']+at;i=instructions[pc]
        n=i['bytes'];word=int.from_bytes(templates[name][at:at+n],'little')
        templates[name][at:at+n]=(word&~MASKS[typ]).to_bytes(n,'little')
    for s in sections:need(digest(templates[s['name']])==s['pre_relocation_sha256'],'Independently masked relocation template')
    return relocs

def countercases(obj,plan,folder,allocations,addresses,semantics,allowed_definitions,raw):
    first=next(s for s in plan['sections']if s['kind']=='code')
    symbol=next(s for s in plan['defined_symbols']if s['section']==first['name'])
    dataitem=next(s for s in plan['sections']if s['kind']=='RO');out=[]
    def audit(candidate):
        gate(candidate,plan,allowed_definitions=allowed_definitions)
        need(relocation_semantics(candidate,allocations,addresses)==semantics,'Exact full actual semantic RELA')
        fixed_table_check(candidate,plan,allocations,raw)
    def relocation_offset(section,offset,typ):
        matches=[]
        for table in obj.sections:
            if table['type']!=4:continue
            if obj.sections[table['info']]['name']!=section:continue
            for at in range(table['offset'],table['offset']+table['size'],12):
                roff,info,addend=struct.unpack_from('<IIi',obj.raw,at)
                if roff==offset and info&255==typ:matches.append(at)
        need(len(matches)==1,'Unique actual new relocation record');return matches[0]
    control=next(r for r in plan['relocations']if r['type_number']in(17,45))
    low=next(r for r in plan['relocations']if r['type_number']in(24,25))
    negative=next(r for r in plan['relocations']if r['addend']==-346)
    for tag in ['ABS_provider','wrong_type','wrong_size','offset1','hidden','writable','code_bit','data_bit',
                'unplanned_GLOBAL','unplanned_ABS','control_addend','missing_low','negative_addend_sign','fixed_table_byte']:
        data=bytearray(obj.raw);at=sym_offset(obj,symbol['name']);section=obj.byname[first['name']]
        if tag=='ABS_provider':struct.pack_into('<H',data,at+14,0xfff1)
        elif tag=='wrong_type':data[at+12]=0x11 if symbol['elf_type']!=1 else 0x12
        elif tag=='wrong_size':struct.pack_into('<I',data,at+8,symbol['size']+2)
        elif tag=='offset1':struct.pack_into('<I',data,at+4,1)
        elif tag=='hidden':data[at+13]=2
        elif tag=='writable':struct.pack_into('<I',data,struct.unpack_from('<I',data,32)[0]+section['index']*40+8,7)
        elif tag=='code_bit':data[section['offset']]^=1
        elif tag=='data_bit':data[obj.byname[dataitem['name']]['offset']]^=1
        elif tag in('unplanned_GLOBAL','unplanned_ABS'):
            local=next(s for s in obj.symbols if s['name'].startswith('.L')and s['bind']==0 and 0<s['index']<0xff00)
            spot=sym_offset(obj,local['name']);data[spot+12]=(data[spot+12]&15)|16
            if tag=='unplanned_ABS':struct.pack_into('<H',data,spot+14,0xfff1)
        elif tag in('control_addend','missing_low','negative_addend_sign'):
            rel=low if tag=='missing_low'else negative if tag=='negative_addend_sign'else control
            spot=relocation_offset(rel['section'],rel['offset'],rel['type_number'])
            if tag=='missing_low':struct.pack_into('<I',data,spot+4,struct.unpack_from('<I',data,spot+4)[0]&0xffffff00)
            else:struct.pack_into('<i',data,spot+8,346 if tag=='negative_addend_sign'else rel['addend']+2)
        else:
            table=plan['existing_original_VA_fixed_tables'][0]
            data[obj.byname[table['section']]['offset']+table['section_offset']]^=1
        p=folder/('COUNTERCASE-reachable-'+tag+'.o');p.write_bytes(data)
        try:audit(ELF(p))
        except AssertionError as error:reason=str(error)
        else:raise AssertionError('Accepted actual ELF countercase '+tag)
        out.append(dict(case=tag,path=str(p),sha256=sha(p),rejected=True,reason=reason))
    return out

def main():
    p=argparse.ArgumentParser();p.add_argument('--current-receipt',type=Path,default=ROOT/'build/finite-data-extension-190bd08439fa480cbb4400235344099e/verification.json')
    p.add_argument('--plan',type=Path,default=ROOT/'evidence/reachable-code-plan.json')
    p.add_argument('--proof-root',type=Path);p.add_argument('--firmware',type=Path);p.add_argument('--expect-missing-baseline',action='store_true');a=p.parse_args()
    plan=read(a.plan);prior=read(a.current_receipt)
    need(prior['passed']and prior['schema']=='ID2966-finite-data-native-extension-v1'and len(prior['allocations'])==651,'Actual current651 baseline')
    if a.firmware is None:a.firmware=next((W/n for n in ['exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin','firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin']if(W/n).is_file()),None)
    need(a.firmware is not None and sha(a.firmware)=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','Original ID2966 required')
    raw=a.firmware.read_bytes();new_semantics=source_gate(plan,raw,prior)
    for field in ['source','header']:need(sha(ROOT/plan[field])==plan[field+'_sha256'],'Reviewed new source/header')
    for name,h in prior['source_files'].items():need(sha(ROOT/name)==h,'Every frozen inherited source retained')
    if a.proof_root is None:a.proof_root=next((W/n for n in ['apk-analysis/tsl9-v4160-reachable-data-2026-10-21','analysis/v4160-reachable-data-2026-10-21']if(W/n).is_dir()),None)
    need(a.proof_root is not None,'Actual sealed role proofs')
    for item in plan['proofs']:
        path=a.proof_root/item['scope']/item['seal'];need(sha(path)==item['sha256'],'Exact independent proof seal')
        sealed=read(path);need(sealed['passed'],'Independent proof passed')
        for member in sealed['members']:
            child=(path.parent/member['path']).resolve();need(child.is_relative_to(a.proof_root.resolve())and child.stat().st_size==member['bytes']and sha(child)==member['sha256'],'Actual sealed member')
    if a.expect_missing_baseline:
        obj=ELF(Path(prior['modes']['c']['integrated_object']))
        try:gate(obj,plan)
        except AssertionError as error:need(str(error).startswith('Missing reachable native section:'),'Expected missing-code RED');print(json.dumps(dict(expected_red=True,baseline_sha256=digest(obj.raw),reason=str(error))));return
        raise AssertionError('Baseline unexpectedly provides new code')
    work=ROOT/'build'/('reachable-code-extension-'+uuid.uuid4().hex);work.mkdir(parents=True)
    old_proof=next((W/n for n in ['apk-analysis/tsl9-v4160-data-frontier-2026-10-21','analysis/v4160-data-frontier-2026-10-21']if(W/n).is_dir()),None)
    need(old_proof is not None,'Retained unchanged651 proof root')
    _,output=run([sys.executable,'-X','utf8','-B',ROOT/'verify-finite-data-extension.py','--current-receipt',prior['baseline_receipt'],'--firmware',a.firmware.resolve(),'--proof-root',old_proof],work,'unchanged651-gate')
    fresh_path=Path(json.loads(output.decode().strip().splitlines()[-1])['receipt']);base=read(fresh_path)
    need(base['passed']and base['allocations']==prior['allocations'],'Fresh unchanged651 gate')
    allocations=dict(base['allocations'])
    for s in plan['sections']:allocations[s['name']]=dict(s,end_exclusive=s['originalVA']+s['bytes'])
    layout=work/'original-address-layout.ld';text='OUTPUT_ARCH(riscv)\nENTRY(__tsl9v4160_image_entry)\nSECTIONS {\n'
    for name,s in sorted(allocations.items(),key=lambda kv:kv[1]['originalVA']):
        text+=' '+name+' '+hex(s['originalVA'])+(' (NOLOAD)'if s['kind']=='RAM'else'')+' : { KEEP(*('+name+')) }\n ASSERT(SIZEOF('+name+')=='+str(s['bytes'])+', "Original size changed")\n'
    layout.write_text(text+' /DISCARD/ : { *(.comment) *(.note.GNU-stack) }\n}\n')
    modes={}
    for mode,language,std in [('c','c','c11'),('cpp','c++','c++17')]:
        folder=work/mode;folder.mkdir();before=ELF(Path(base['modes'][mode]['integrated_object']));bw=ELF(fresh_path.parent/mode/'ADDRESS-WITNESS-ONLY.elf')
        need(digest(before.raw)==prior['modes'][mode]['integrated_sha256']=='25c605fdaa870e985da07dc290ed73dae1caed57e2e7609f2ce9129094701872','Actual old native object')
        addresses={n:bw.symbol[n]['value']for n in BASE['und'](before)}
        need(len(addresses)==23,'Old true23 unresolved')
        for name,info in plan['expected_undefined_symbols'].items():
            need(name not in addresses or addresses[name]==info['originalVA'],'Preserve every canonical address identity')
            addresses[name]=info['originalVA']
        objpath=folder/'reachable-code.o'
        run([BIN/'clang.exe','--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-fno-builtin','-fno-stack-protector','-Wall','-Wextra','-Werror','-x',language,'-std='+std,'-c',ROOT/plan['source'],'-o',objpath],folder,'compile-reachable-code')
        unit=ELF(objpath);gate(unit,plan,allowed_definitions={s['name']for s in plan['defined_symbols']})
        need({s['name']for s in unit.sections if s['flags']&2 and s['size']}=={s['name']for s in plan['sections']},'Only reviewed new code/RO allocations')
        need(BASE['und'](unit)==set(plan['expected_undefined_symbols']),'Every new reference declared')
        need(relocation_semantics(unit,allocations,addresses)==new_semantics,'Actual compiled new semantic RELA')
        mergedpath=folder/'native-extension.o';run([BIN/'ld.lld.exe','-r','--no-relax',Path(base['modes'][mode]['integrated_object']),objpath,'-o',mergedpath],folder,'integrate-reachable-code')
        allowed_definitions={s['name']for s in before.symbols if s['name']and s['index']!=0 and s['bind']in(1,2)}|{s['name']for s in plan['defined_symbols']}
        merged=ELF(mergedpath);gate(merged,plan,allowed_definitions=allowed_definitions)
        need({s['name']for s in merged.sections if s['flags']&2 and s['size']}==set(allocations),'Exact inherited and new storage union')
        for name in base['allocations']:need(all(before.byname[name][k]==merged.byname[name][k]for k in ['type','flags','size','alignment','data']),'Every inherited section unchanged')
        need(relocation_semantics(merged,allocations,addresses)==relocation_semantics(before,allocations,addresses)+new_semantics,'Every inherited and new semantic relocation occurrence')
        oldroles,newroles=roles(before,set()),roles(merged,set());need(not oldroles-newroles,'Every inherited symbol occurrence retained')
        globals_before={s['name']for s in before.symbols if s['name']and s['bind']in(1,2)}
        extras=collections.Counter()
        for role,count in roles(unit,globals_before).items():
            if role==('', '0',0,0,0,0):continue
            name,section,value,size,info,other=role
            if section=='.riscv.attributes':
                need((value,size,info,other)==(0,0,0,0),'Exact local attributes metadata');section=str(0xfff1)
            extras[(name,section,value,size,info,other)]+=count
        for s in plan['sections']:
            key=('',s['name'],0,0,3,0);need(extras[key]in(0,1),'One actual new output SECTION record');extras[key]=1
        need(newroles-oldroles==extras,'Exact unit metadata and section normalization, no extra provider/alias')
        expected_und=BASE['und'](before)|(BASE['und'](unit)-set(BASE['defined'](before)))
        need(BASE['und'](merged)==expected_und,'All original opaque contracts remain unresolved')
        fixed_table_check(merged,plan,allocations,raw)
        strict=folder/'strict-incomplete.elf';_,errors=run([BIN/'ld.lld.exe','--no-relax','--error-limit=0','-T',layout,mergedpath,'-o',strict],folder,'strict-final-link',False)
        need(not strict.exists()and set(re.findall(r'undefined symbol: (\w+)',errors.decode(errors='replace')))==expected_und,'Strict link rejects actual remaining dependencies')
        numeric=folder/'ADDRESS-WITNESS-ONLY.ld';numeric.write_text('/* Numeric obligations only. No resident/callback provider. */\n'+''.join(n+' = '+hex(addresses[n])+';\n'for n in sorted(expected_und)))
        wp=folder/'ADDRESS-WITNESS-ONLY.elf';run([BIN/'ld.lld.exe','--no-relax','-T',layout,'-T',numeric,mergedpath,'-o',wp],folder,'numeric-address-witness')
        witness=ELF(wp);gate(witness,plan,True)
        for name,s in allocations.items():
            sec=witness.byname[name];need(sec['address']==s['originalVA']and sec['size']==s['bytes'],'Every original allocation placement')
            if s['kind']!='RAM':need(sec['data']==raw[s['originalVA']-0x8000:s['originalVA']-0x8000+s['bytes']],'Every admitted final code/RO source byte')
        for name in base['allocations']:need(bw.byname[name]['data']==witness.byname[name]['data'],'Every inherited linked byte unchanged')
        tables=fixed_table_check(witness,plan,allocations,raw,True)
        modes[mode]=dict(passed=True,integrated_object=str(mergedpath),integrated_sha256=sha(mergedpath),numeric_witness_sha256=sha(wp),undefined_symbols=sorted(expected_und),relocations=len(merged.relocations),allocation_sections=len(allocations),strict_rejected=True,fixed_tables=tables,actual_countercases=countercases(merged,plan,folder,allocations,addresses,relocation_semantics(merged,allocations,addresses),allowed_definitions,raw))
    need(modes['c']['integrated_sha256']==modes['cpp']['integrated_sha256']and modes['c']['numeric_witness_sha256']==modes['cpp']['numeric_witness_sha256'],'Actual C/C++ artifacts identical')
    sources=dict(base['source_files'])
    for name in [plan['source'],plan['header'],str(a.plan.resolve().relative_to(ROOT)),Path(__file__).name]:sources[name]=sha(ROOT/name)
    newcode=sum(s['bytes']for s in plan['sections']if s['kind']=='code');newro=sum(s['bytes']for s in plan['sections']if s['kind']=='RO')
    result=dict(schema='ID2966-reachable-code-native-extension-v1',passed=True,firmware_sha256=digest(raw),source_files=sources,baseline_receipt=str(fresh_path),baseline_receipt_sha256=sha(fresh_path),allocations=allocations,modes=modes,new_code_bytes=newcode,new_RO_bytes=newro,source_coverage_bytes=74726+newcode+newro,original_C_ABIs_proved=False,opaque_callee_ABIs_proved=False,IRQ_ABI_proved=False,firmware_executed=False,emulation=False,network=False,hardware=False,native_bin=False,ota_verified=False)
    out=work/'verification.json';out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,receipt=str(out),sha256=sha(out),new_code_bytes=newcode,new_RO_bytes=newro,remaining_UND=len(modes['c']['undefined_symbols']),native_BIN=False,OTA_ready=False)))
if __name__=='__main__':main()
