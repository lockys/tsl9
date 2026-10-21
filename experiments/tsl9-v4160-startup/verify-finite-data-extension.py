"""Finite RO data extension. Static compilation/ELF inspection only, no BIN."""
import argparse,collections,hashlib,json,re,runpy,struct,subprocess,sys,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parent; W=ROOT.parents[1]
BASE=runpy.run_path(str(ROOT/'verify-version-literal-extension.py'))
ELF=BASE['ELF']; BIN=BASE['BIN']; run=BASE['run']; need=BASE['need']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())

def sym_offset(elf,name):
    rows=[]
    for table in elf.sections:
        if table['type']!=2:continue
        strings=elf.sections[table['link']]['data']
        for off in range(0,table['size'],16):
            start=struct.unpack_from('<I',table['data'],off)[0]
            if strings[start:strings.index(0,start)].decode()==name:rows.append(table['offset']+off)
    need(len(rows)==1,'Unique actual symbol record: '+name)
    return rows[0]

def gate(elf,items,linked=False):
    for item in items:
        need(item['name'] in elf.symbol and item['section'] in elf.byname,'Every finite view has storage')
        sym=elf.symbol[item['name']]; sec=elf.byname[item['section']]
        need((sec['type'],sec['flags'],sec['size'],sec['alignment'])==(1,2,item['bytes'],1),'Exact RO allocation, no filler')
        need(sec['data']==bytes.fromhex(item['raw_hex']),'Every finite source byte original')
        need((sym['index'],sym['bind'],sym['type'],sym['size'],sym['value'])==
             (sec['index'],1,1,item['bytes'],item['originalVA'] if linked else 0),'Real own OBJECT, not alias/ABS')
        need(elf.raw[sym_offset(elf,item['name'])+13]==0,'Default visibility')
        need(not linked or sec['address']==item['originalVA'],'Original placement')

def roles(elf,skip):
    result=collections.Counter()
    for table in elf.sections:
        if table['type']!=2:continue
        strings=elf.sections[table['link']]['data']
        for off in range(0,table['size'],16):
            name,value,size,info,other,index=struct.unpack_from('<IIIBBH',table['data'],off)
            name=strings[name:strings.index(0,name)].decode()
            if name in skip:continue
            section=elf.sections[index]['name'] if 0<index<0xff00 else str(index)
            result[(name,section,value,size,info,other)]+=1
    return result

def countercases(elf,items,folder):
    first=items[0]; string=next(x for x in items if x['kind']=='NUL-literal')
    seq=next(x for x in items if x['kind']=='conditional-U16-view')
    out=[]
    for tag in ['ABS','FUNC','short_size','offset1','writable','wrong_section','hidden',
                'payload_byte','NUL_byte','U16_byte']:
        item=string if tag=='NUL_byte' else seq if tag=='U16_byte' else first
        data=bytearray(elf.raw); at=sym_offset(elf,item['name']); sec=elf.byname[item['section']]
        if tag=='ABS':struct.pack_into('<H',data,at+14,0xfff1);struct.pack_into('<I',data,at+4,item['originalVA'])
        elif tag=='FUNC':data[at+12]=0x12
        elif tag=='short_size':struct.pack_into('<I',data,at+8,item['bytes']-1)
        elif tag=='offset1':struct.pack_into('<I',data,at+4,1)
        elif tag=='writable':struct.pack_into('<I',data,struct.unpack_from('<I',data,32)[0]+sec['index']*40+8,3)
        elif tag=='wrong_section':struct.pack_into('<H',data,at+14,elf.byname[items[1]['section']]['index'])
        elif tag=='hidden':data[at+13]=2
        elif tag=='NUL_byte':data[sec['offset']+item['bytes']-1]=1
        else:data[sec['offset']]^=1
        path=folder/('COUNTERCASE-finite-data-'+tag+'.o');path.write_bytes(data)
        try:gate(ELF(path),items)
        except AssertionError as error:reason=str(error)
        else:raise AssertionError('Accepted actual ELF countercase '+tag)
        out.append(dict(case=tag,path=str(path),sha256=sha(path),rejected=True,reason=reason))
    return out

def main():
    p=argparse.ArgumentParser();p.add_argument('--current-receipt',type=Path,default=ROOT/'build/version-literal-extension-e18f9d93ea074c468930b7192aeeb65d/verification.json')
    p.add_argument('--firmware',type=Path);p.add_argument('--proof-root',type=Path)
    a=p.parse_args(); plan_path=ROOT/'evidence/finite-data-plan.json';plan=read(plan_path);items=plan['items']
    if a.firmware is None:
        a.firmware=next((W/n for n in ['firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin','exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'] if (W/n).exists()),None)
    need(a.firmware is not None and sha(a.firmware)==plan['firmware_sha256']==BASE['FIRMWARE_SHA'],'Pinned original source')
    raw=a.firmware.read_bytes();prior=read(a.current_receipt)
    need(prior['passed'] and prior['schema']=='ID2966-version-literal-native-extension-v1' and len(prior['allocations'])==641,'Explicit641/30 native frontier')
    need(sha(ROOT/plan['source'])==plan['source_sha256'] and sha(ROOT/plan['header'])==plan['header_sha256'],'Declared source/header')
    need(len(items)==10 and len({x['name'] for x in items})==10 and len({x['section'] for x in items})==10 and sum(x['bytes'] for x in items)==232,'Exactly ten unique finite views')
    closed={x['name'] for x in items if x['closes_canonical_data_identity']}
    need(len(closed)==7 and sum(x['bytes'] for x in items if x['closes_canonical_data_identity'])==58,'Seven canonical identities,58 bytes')
    for item in items:
        need(raw[item['originalVA']-0x8000:item['originalVA']-0x8000+item['bytes']]==bytes.fromhex(item['raw_hex']),'Plan source bytes')
        need(not any(s['originalVA']<item['originalVA']+item['bytes'] and item['originalVA']<s['originalVA']+s['bytes'] for s in prior['allocations'].values()),'No baseline allocation duplicated')
    ranges=sorted((x['originalVA'],x['originalVA']+x['bytes']) for x in items)
    need(all(left[1]<=right[0] for left,right in zip(ranges,ranges[1:])),'No new overlap or padding')
    if a.proof_root is None:
        a.proof_root=next((W/n for n in ['apk-analysis/tsl9-v4160-data-frontier-2026-10-21','analysis/v4160-data-frontier-2026-10-21'] if (W/n).exists()),None)
    need(a.proof_root is not None,'Independent role proofs required')
    for proof in plan['proofs']:
        path=a.proof_root/proof['scope']/proof['seal']; need(sha(path)==proof['sha256'],'Bound exact completed role proof')
        seal=read(path);need(seal['passed'],'Role proof passed')
        rows=seal.get('members',seal.get('files'));rows=[dict(path=k,**v) for k,v in rows.items()] if isinstance(rows,dict) else rows
        need(rows,'Actual sealed members')
        for row in rows:
            file=(path.parent/row['path']).resolve()
            need(file.is_relative_to(a.proof_root.resolve()) and file.stat().st_size==row['bytes'] and sha(file)==row['sha256'],'Actual role-proof member')
    for name,digest in prior['source_files'].items():need(sha(ROOT/name)==digest,'Frozen prior native source')
    work=ROOT/'build'/('finite-data-extension-'+uuid.uuid4().hex);work.mkdir(parents=True,exist_ok=False)
    # Keep the complete prior gate unchanged, including its own frozen gate.
    _,log=run([sys.executable,'-X','utf8','-B',ROOT/'verify-version-literal-extension.py',
               '--current-receipt',prior['baseline_receipt'],'--proof',prior['independent_literal_proof'],
               '--firmware',a.firmware.resolve()],work,'unchanged641-gate')
    baseline_path=Path(json.loads(log.decode().strip().splitlines()[-1])['receipt']);base=read(baseline_path)
    need(base['allocations']==prior['allocations'] and base['passed'],'Fresh641 gate, unchanged originalVA storage')
    alloc=dict(base['allocations'])
    for x in items:alloc[x['section']]=dict(name=x['section'],originalVA=x['originalVA'],end_exclusive=x['originalVA']+x['bytes'],bytes=x['bytes'],kind='RO',flags=2,alignment=1,sha256=x['sha256'],capture_role=x['kind'])
    layout=work/'original-address-layout.ld';text='OUTPUT_ARCH(riscv)\nENTRY(__tsl9v4160_image_entry)\nSECTIONS {\n'
    for name,s in sorted(alloc.items(),key=lambda x:x[1]['originalVA']):
        text+=' '+name+' '+hex(s['originalVA'])+(' (NOLOAD)' if s['kind']=='RAM' else '')+' : { KEEP(*('+name+')) }\n ASSERT(SIZEOF('+name+')=='+str(s['bytes'])+', "Original size changed")\n'
    layout.write_text(text+' /DISCARD/ : { *(.comment) *(.note.GNU-stack) }\n}\n',encoding='utf-8')
    modes={}
    for mode,language,std in [('c','c','c11'),('cpp','c++','c++17')]:
        folder=work/mode;folder.mkdir();commands=[];before_path=Path(base['modes'][mode]['integrated_object']);before=ELF(before_path)
        before_witness=ELF(baseline_path.parent/mode/'ADDRESS-WITNESS-ONLY.elf')
        need(sha(before_path)==prior['modes'][mode]['integrated_sha256']=='2683ebb66dfa5f0107dbaca35495cdf629ca645698f223cc7f266554bce16aac','Actual prior native object')
        addresses={n:before_witness.symbol[n]['value'] for n in BASE['und'](before)}
        need(len(addresses)==30 and closed<=set(addresses),'Actual current30 frontier and seven candidates')
        obj=folder/'finite-data.o'
        cmd,_=run([BIN/'clang.exe','--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32','-ffreestanding','-fno-builtin','-fno-stack-protector','-Wall','-Wextra','-Werror','-x',language,'-std='+std,'-c',ROOT/plan['source'],'-o',obj],folder,'compile-finite-data');commands.append(cmd)
        unit=ELF(obj);gate(unit,items)
        need(not BASE['und'](unit) and not unit.relocations and set(BASE['defined'](unit))=={x['name'] for x in items},'Standalone data-only unit, no hidden providers')
        need({s['name'] for s in unit.sections if s['flags']&2 and s['size']}=={x['section'] for x in items},'Only ten finite RO allocations')
        merged_path=folder/'native-extension.o';cmd,_=run([BIN/'ld.lld.exe','-r','--no-relax',before_path,obj,'-o',merged_path],folder,'integrate-finite-data');commands.append(cmd)
        merged=ELF(merged_path);gate(merged,items)
        need(BASE['und'](merged)==set(addresses)-closed and len(BASE['und'](merged))==23,'Exactly seven data names resolved, other23 stay UND')
        need({s['name'] for s in merged.sections if s['flags']&2 and s['size']}==set(alloc),'Exact651 allocations')
        for name in base['allocations']:
            need(all(before.byname[name][key]==merged.byname[name][key] for key in ['type','flags','size','alignment','data']),'Every inherited section unchanged')
        oldroles,newroles=roles(before,closed),roles(merged,closed)
        need(not oldroles-newroles,'Every inherited symbol occurrence, including locals/visibility, retained')
        extras=newroles-oldroles
        private={x['name'] for x in items if not x['closes_canonical_data_identity']}
        newsections={x['section'] for x in items}
        expected_extras=collections.Counter()
        for role,count in roles(unit,closed).items():
            if role==('', '0', 0, 0, 0, 0):continue # one output null symbol
            name,section,value,size,info,other=role
            if section=='.riscv.attributes':
                # lld merges the nonallocated RISC-V attributes rather than
                # concatenating their input positions; its LOCAL mapping
                # record becomes SHN_ABS. This is not a global provider.
                need((value,size,info,other)==(0,0,0,0) and
                     unit.byname[section]['type']==0x70000003 and not unit.byname[section]['flags']&2,
                     'Exact input attributes mapping metadata')
                section=str(0xfff1)
            expected_extras[(name,section,value,size,info,other)]+=count
        # lld also emits a real section symbol for each new output section.
        expected_extras.update(('',name,0,0,3,0) for name in newsections)
        need(extras==expected_extras,'Exact compiled-unit metadata plus output SECTION records; no extra alias/provider')
        def norm(elf,r):
            s=elf.symbols[r['symbol_index']]
            b=(addresses[s['name']] if s['name'] else 0) if s['index']==0 else s['value'] if s['index']==0xfff1 else alloc[elf.sections[s['index']]['name']]['originalVA']+s['value']
            return (b+r['addend'])&0xffffffff
        def relas(elf):return collections.Counter((r['section'],r['offset'],r['type'],norm(elf,r)) for r in elf.relocations)
        need(len(merged.relocations)==8107 and relas(before)==relas(merged),'All8107 semantic RELA occurrences unchanged')
        strict=folder/'strict-incomplete.elf';cmd,errors=run([BIN/'ld.lld.exe','--no-relax','--error-limit=0','-T',layout,merged_path,'-o',strict],folder,'strict-final-link',False);commands.append(cmd)
        need(not strict.exists() and set(re.findall(r'undefined symbol: (\w+)',errors.decode(errors='replace')))==BASE['und'](merged),'Strict link rejects exactly23 remaining contracts')
        numeric=folder/'ADDRESS-WITNESS-ONLY.ld';numeric.write_text('/* Numeric witness only; no resident or callback implementation. */\n'+''.join(n+' = '+hex(addresses[n])+';\n' for n in sorted(BASE['und'](merged))),encoding='utf-8')
        witness_path=folder/'ADDRESS-WITNESS-ONLY.elf';cmd,_=run([BIN/'ld.lld.exe','--no-relax','-T',layout,'-T',numeric,merged_path,'-o',witness_path],folder,'numeric-address-witness');commands.append(cmd)
        witness=ELF(witness_path);gate(witness,items,True)
        for name,s in alloc.items():
            sec=witness.byname[name];need(sec['address']==s['originalVA'] and sec['size']==s['bytes'],'Every original allocation placement')
            if s['kind']!='RAM':need(sec['data']==raw[s['originalVA']-0x8000:s['originalVA']-0x8000+s['bytes']],'Every code/RO byte original')
        for name in base['allocations']:need(before_witness.byname[name]['data']==witness.byname[name]['data'],'Every inherited linked byte unchanged')
        modes[mode]=dict(passed=True,commands=commands,integrated_object=str(merged_path),integrated_sha256=sha(merged_path),numeric_witness_sha256=sha(witness_path),undefined_symbols=sorted(BASE['und'](merged)),relocations=8107,allocation_sections=651,code_bytes=70764,RO_bytes=3962,strict_rejected=True,actual_countercases=countercases(merged,items,folder))
    need(modes['c']['integrated_sha256']==modes['cpp']['integrated_sha256'] and modes['c']['numeric_witness_sha256']==modes['cpp']['numeric_witness_sha256'],'C/CPP actual artifacts agree')
    sources=dict(base['source_files'])
    for name in [plan['source'],plan['header'],'evidence/finite-data-plan.json',Path(__file__).name]:sources[name]=sha(ROOT/name)
    result=dict(schema='ID2966-finite-data-native-extension-v1',passed=True,firmware_sha256=plan['firmware_sha256'],source_files=sources,baseline_receipt=str(baseline_path),baseline_receipt_sha256=sha(baseline_path),allocations=alloc,modes=modes,closed_data_identities=sorted(closed),private_conditional_views=sorted(private),new_real_RO_bytes=232,source_coverage_bytes=74726,original_C_object_extents_proved=False,opaque_callee_ABIs_proved=False,IRQ_ABI_proved=False,firmware_executed=False,emulation=False,network=False,hardware=False,native_bin=False,ota_verified=False)
    out=work/'verification.json';out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,receipt=str(out),sha256=sha(out),remaining_UND=23,RO_bytes=3962,new_RO_bytes=232,native_BIN=False,OTA_ready=False)))

if __name__=='__main__':main()
