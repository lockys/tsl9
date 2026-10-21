"""Source-bound residual entries; compile/link/inspect only, never export firmware."""
import argparse,collections,hashlib,json,re,runpy,struct,sys,uuid
from pathlib import Path

ROOT=Path(__file__).resolve().parent;W=ROOT.parents[1]
OLD=runpy.run_path(str(ROOT/'verify-reachable-code-extension.py'))
BASE=OLD['BASE'];ELF=OLD['ELF'];BIN=OLD['BIN'];run=OLD['run'];need=OLD['need']
sha=OLD['sha'];digest=OLD['digest'];read=OLD['read'];roles=OLD['roles'];sym_offset=OLD['sym_offset']
OLD_GATE_SHA='e4a9f183ac2d7f440e4bd87cbba2135ce161ba3570e40e09de58461dbaff6a95'
FIRMWARE_SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
OLD_OBJECT_SHA='8791561ee79341c8f6b9f2b2b7c1f73406f9ed321d883c170cff227341863d92'

def allocations_gate(obj,allocations):
    actual=[s['name']for s in obj.sections if s['flags']&2 and s['size']]
    need(len(actual)==len(set(actual))==len(allocations)and set(actual)==set(allocations),
         'Exact inherited and new storage union')

def inherited_gate(before,after,allocations):
    for name in allocations:
        need(all(before.byname[name][k]==after.byname[name][k]
                 for k in ['type','flags','size','alignment','data']),
             'Every inherited allocation field and byte retained: '+name)

def record_offset(obj,section,offset,typ):
    matches=[]
    for table in obj.sections:
        if table['type']!=4 or obj.sections[table['info']]['name']!=section:continue
        for at in range(table['offset'],table['offset']+table['size'],12):
            roff,info,_=struct.unpack_from('<IIi',obj.raw,at)
            if roff==offset and info&255==typ:matches.append(at)
    need(len(matches)==1,'Unique actual relocation record')
    return matches[0]

def raw_relocation_roles(elf,resolve=None):
    """Preserve raw S-role and signed A, independent of section/symbol indices."""
    def symbol_role(table,index):
        strings=elf.sections[table['link']]['data']
        at=index*16;name,value,size,info,other,owner=struct.unpack_from('<IIIBBH',table['data'],at)
        name=strings[name:strings.index(0,name)].decode()
        section=elf.sections[owner]['name']if 0<owner<0xff00 else str(owner)
        if resolve is not None and owner==0 and name and info>>4 in(1,2)and name in resolve.symbol:
            old=resolve.symbol[name]
            if old['index']!=0:
                other=resolve.raw[sym_offset(resolve,name)+13]
                return(name,resolve.sections[old['index']]['name']if old['index']<0xff00 else str(old['index']),
                    old['value'],old['size'],(old['bind']<<4)|old['type'],other)
        return(name,section,value,size,info,other)
    result=collections.Counter()
    for table in elf.sections:
        if table['type']!=4:continue
        symbols=elf.sections[table['link']]
        need(symbols['type']==2 and symbols['size']%16==0,'Actual linked raw SYMTAB')
        owner=elf.sections[table['info']]['name']
        for at in range(0,table['size'],12):
            off,info,addend=struct.unpack_from('<IIi',table['data'],at)
            result[(owner,off,info&255,symbol_role(symbols,info>>8),addend)]+=1
    return result

def raw_role_gate(before,unit,after,plan):
    oldroles,newroles=roles(before,set()),roles(after,set())
    need(not oldroles-newroles,'Every inherited symbol occurrence retained')
    globals_before={s['name']for s in before.symbols if s['name']and s['bind']in(1,2)}
    extras=collections.Counter()
    for role,count in roles(unit,globals_before).items():
        if role==('', '0',0,0,0,0):continue
        name,section,value,size,info,other=role
        if section=='.riscv.attributes':
            need((value,size,info,other)==(0,0,0,0),'Exact local attributes metadata')
            section=str(0xfff1)
        extras[(name,section,value,size,info,other)]+=count
    for s in plan['sections']:
        key=('',s['name'],0,0,3,0)
        need(extras[key]in(0,1),'One actual new output SECTION record');extras[key]=1
    need(newroles-oldroles==extras,'Exact raw unit metadata and SECTION normalization')

def integrated_gate(obj,before,unit,plan,oldplan,allocations,addresses,semantics,definitions,raw,prior):
    OLD['gate'](obj,plan,allowed_definitions=definitions)
    allocations_gate(obj,allocations);inherited_gate(before,obj,prior['allocations'])
    raw_role_gate(before,unit,obj,plan)
    need(OLD['relocation_semantics'](obj,allocations,addresses)==semantics,
         'Exact full semantic relocation Counter, including inherited multiplicity')
    need(raw_relocation_roles(obj)==raw_relocation_roles(before)+raw_relocation_roles(unit,before),
         'Exact raw relocation target roles and signed addends retained')
    need(BASE['und'](obj)==BASE['und'](before),'All original23 canonical contracts stay true UND')
    OLD['fixed_table_check'](obj,oldplan,allocations,raw)

def countercases(obj,audit,plan,oldplan,folder,prior):
    first=plan['sections'][0];symbol=next(s for s in plan['defined_symbols']if s['section']==first['name'])
    control=next(r for r in plan['relocations']if r['type_number']in(17,45))
    low=next(r for r in plan['relocations']if r['type_number']in(24,25))
    negative=next(r for r in oldplan['relocations']if r['addend']==-346)
    dataitem=next(s for s in oldplan['sections']if s['kind']=='RO')
    inherited_global=next(s for s in obj.symbols if s['name']and s['bind']==1 and
        s['index']!=0 and s['name']not in {x['name']for x in plan['defined_symbols']})
    local=next(s for s in obj.symbols if s['name'].startswith('.L')and s['bind']==0 and 0<s['index']<0xff00)
    out=[]
    tags=['ABS_provider','wrong_type','wrong_size','offset1','hidden','writable','code_bit',
          'unplanned_GLOBAL','unplanned_ABS','control_addend','missing_low',
          'inherited_data_bit','inherited_negative_addend_sign','inherited_fixed_table_byte',
          'inherited_global_visibility','inherited_local_value','equivalent_S_plus_A_rewrite']
    for tag in tags:
        data=bytearray(obj.raw);spot=sym_offset(obj,symbol['name']);section=obj.byname[first['name']]
        if tag=='ABS_provider':struct.pack_into('<H',data,spot+14,0xfff1)
        elif tag=='wrong_type':data[spot+12]=0x12
        elif tag=='wrong_size':struct.pack_into('<I',data,spot+8,2)
        elif tag=='offset1':struct.pack_into('<I',data,spot+4,1)
        elif tag=='hidden':data[spot+13]=2
        elif tag=='writable':struct.pack_into('<I',data,struct.unpack_from('<I',data,32)[0]+section['index']*40+8,7)
        elif tag=='code_bit':data[section['offset']]^=1
        elif tag in('unplanned_GLOBAL','unplanned_ABS'):
            loc=sym_offset(obj,local['name']);data[loc+12]=(data[loc+12]&15)|16
            if tag=='unplanned_ABS':struct.pack_into('<H',data,loc+14,0xfff1)
        elif tag in('control_addend','missing_low','inherited_negative_addend_sign'):
            rel=low if tag=='missing_low'else negative if tag.startswith('inherited')else control
            loc=record_offset(obj,rel['section'],rel['offset'],rel['type_number'])
            if tag=='missing_low':struct.pack_into('<I',data,loc+4,struct.unpack_from('<I',data,loc+4)[0]&0xffffff00)
            else:struct.pack_into('<i',data,loc+8,346 if tag.startswith('inherited')else rel['addend']+2)
        elif tag=='inherited_data_bit':data[obj.byname[dataitem['name']]['offset']]^=1
        elif tag=='inherited_fixed_table_byte':
            table=oldplan['existing_original_VA_fixed_tables'][0]
            data[obj.byname[table['section']]['offset']+table['section_offset']]^=1
        elif tag=='inherited_global_visibility':data[sym_offset(obj,inherited_global['name'])+13]=2
        elif tag=='inherited_local_value':struct.pack_into('<I',data,sym_offset(obj,local['name'])+4,local['value']+2)
        else:
            loc=record_offset(obj,negative['section'],negative['offset'],negative['type_number'])
            _,info,addend=struct.unpack_from('<IIi',data,loc);old=obj.symbols[info>>8]
            replacement=next((i,s)for i,s in enumerate(obj.symbols)if s['type']==3 and s['index']==old['index'])
            index,symbol2=replacement
            struct.pack_into('<Ii',data,loc+4,(index<<8)|(info&255),addend+old['value']-symbol2['value'])
        path=folder/('COUNTERCASE-residual-'+tag+'.o');path.write_bytes(data)
        try:audit(ELF(path))
        except AssertionError as error:reason=str(error)
        else:raise AssertionError('Accepted actual ELF countercase '+tag)
        out.append(dict(case=tag,path=str(path),sha256=sha(path),rejected=True,reason=reason))
    return out

def coverage(witness,allocations,raw):
    begin,end=0x8000,0x8000+len(raw)
    admitted=bytearray(len(raw));loadbytes={}
    for s in allocations.values():
        if s['kind']=='RAM':continue
        off=s['originalVA']-begin;admitted[off:off+s['bytes']]=b'\x01'*s['bytes']
    # Parse actual ELF32 program headers; require unambiguous file-backed LOAD bytes.
    phoff=struct.unpack_from('<I',witness.raw,28)[0]
    entsize,count=struct.unpack_from('<HH',witness.raw,42)
    need(entsize==32,'Actual ELF32 program header width')
    for index in range(count):
        typ,off,va,_,filesz,_,_,_=struct.unpack_from('<8I',witness.raw,phoff+index*entsize)
        if typ!=1:continue
        need(off+filesz<=len(witness.raw),'File-backed LOAD within ELF')
        for address in range(max(begin,va),min(end,va+filesz)):
            value=witness.raw[off+address-va]
            need(address not in loadbytes or loadbytes[address]==value,'No ambiguous LOAD bytes')
            loadbytes[address]=value
    gaps=[];i=0
    while i<len(raw):
        if admitted[i]:i+=1;continue
        start=i
        while i<len(raw)and not admitted[i]:i+=1
        addresses=range(begin+start,begin+i)
        backed=sum(a in loadbytes for a in addresses)
        mismatch=sum(a in loadbytes and loadbytes[a]!=raw[a-begin]for a in addresses)
        gaps.append(dict(originalVA=begin+start,end_exclusive=begin+i,bytes=i-start,
            source_sha256=digest(raw[start:i]),file_backed_LOAD_bytes=backed,
            LOAD_mismatch_bytes=mismatch,uncovered_bytes=i-start-backed))
    return dict(source_coverage_bytes=sum(admitted),unrepresented_bytes=len(raw)-sum(admitted),
        file_backed_LOAD_padding_bytes=sum(x['file_backed_LOAD_bytes']for x in gaps),
        LOAD_padding_mismatch_bytes=sum(x['LOAD_mismatch_bytes']for x in gaps),
        uncovered_bytes=sum(x['uncovered_bytes']for x in gaps),gaps=gaps)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--current-receipt',type=Path,default=ROOT/'build/reachable-code-extension-f9e3d9060b7d455e9fe0a1301b219abe/verification.json')
    p.add_argument('--plan',type=Path,default=ROOT/'evidence/residual-entry-plan.json')
    p.add_argument('--proof-root',type=Path);p.add_argument('--firmware',type=Path)
    p.add_argument('--expect-missing-baseline',action='store_true');a=p.parse_args()
    need(sha(ROOT/'verify-reachable-code-extension.py')==OLD_GATE_SHA,'Unchanged frozen656 verifier')
    prior=read(a.current_receipt);plan=read(a.plan);oldplan=read(ROOT/'evidence/reachable-code-plan.json')
    need(prior['passed']and prior['schema']=='ID2966-reachable-code-native-extension-v1'and
         len(prior['allocations'])==656 and prior['source_coverage_bytes']==76300,'Actual656 baseline')
    if a.firmware is None:
        a.firmware=next((W/n for n in ['exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin',
            'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin']if(W/n).is_file()),None)
    need(a.firmware is not None and sha(a.firmware)==FIRMWARE_SHA,'Original source ID2966 required')
    raw=a.firmware.read_bytes();new_semantics=OLD['source_gate'](plan,raw,prior)
    need(len(plan['sections'])==4 and all(s['kind']=='code'for s in plan['sections'])and
        sum(s['bytes']for s in plan['sections'])==120 and len(plan['instructions'])==42 and
        len(plan['relocations'])==13 and not plan['existing_original_VA_fixed_tables'],
        'Exactly four residual entries120B42instructions13RELA, no new data/table')
    need([(s['originalVA'],s['bytes'])for s in plan['sections']]==
         [(0x10c34,2),(0x10c36,68),(0x10d2e,2),(0x10d30,48)],'Exact entry intervals')
    need(len(plan['defined_symbols'])==4 and all(s['elf_type']==0 and s['size']==0
         for s in plan['defined_symbols']),'Private NOTYPE0 anchors only; no C ABI claim')
    for field in ['source','header']:need(sha(ROOT/plan[field])==plan[field+'_sha256'],'Reviewed new source/header')
    for name,h in prior['source_files'].items():need(sha(ROOT/name)==h,'Every inherited source retained')
    if a.proof_root is None:
        a.proof_root=next((W/n for n in ['apk-analysis/tsl9-v4160-residual-frontier-2026-10-21',
            'analysis/v4160-residual-frontier-2026-10-21']if(W/n).is_dir()),None)
    need(a.proof_root is not None,'Actual source proofs')
    need(len(plan['proofs'])==1 and plan['proofs'][0]['scope']=='code'and
         plan['proofs'][0]['sha256']=='289056e66fc359ffe0158569aba369839abad4337e3bb906b89b3e723d303087',
         'Pinned independent conditional-entry admission')
    for item in plan['proofs']:
        path=a.proof_root/item['scope']/item['seal']
        need(sha(path)==item['sha256']and read(path)['passed'],'Exact completed independent proof')
        for member in read(path)['members']:
            child=(path.parent/member['path']).resolve()
            need(child.is_relative_to(a.proof_root.resolve())and child.stat().st_size==member['bytes']and
                 sha(child)==member['sha256'],'Actual sealed source member')
    before=ELF(Path(prior['modes']['c']['integrated_object']))
    need(digest(before.raw)==prior['modes']['c']['integrated_sha256']==OLD_OBJECT_SHA,'Actual current656 object')
    if a.expect_missing_baseline:
        try:OLD['gate'](before,plan)
        except AssertionError as error:
            need(str(error).startswith('Missing reachable native section:'),'Expected missing-code RED')
            print(json.dumps(dict(expected_red=True,reason=str(error))));return
        raise AssertionError('Baseline unexpectedly provides residual entries')
    work=ROOT/'build'/('residual-entry-extension-'+uuid.uuid4().hex);work.mkdir(parents=True)
    oldproof=next((W/n for n in ['apk-analysis/tsl9-v4160-reachable-data-2026-10-21',
        'analysis/v4160-reachable-data-2026-10-21']if(W/n).is_dir()),None)
    need(oldproof is not None,'Retained unchanged656 proofs')
    _,output=run([sys.executable,'-X','utf8','-B',ROOT/'verify-reachable-code-extension.py',
        '--current-receipt',prior['baseline_receipt'],'--firmware',a.firmware.resolve(),
        '--proof-root',oldproof],work,'unchanged656-gate')
    fresh_path=Path(json.loads(output.decode().strip().splitlines()[-1])['receipt']);base=read(fresh_path)
    need(base['passed']and base['allocations']==prior['allocations'],'Fresh unchanged656 gate')
    allocations=dict(base['allocations'])
    for s in plan['sections']:allocations[s['name']]=dict(s,end_exclusive=s['originalVA']+s['bytes'])
    layout=work/'original-address-layout.ld';text='OUTPUT_ARCH(riscv)\nENTRY(__tsl9v4160_image_entry)\nSECTIONS {\n'
    for name,s in sorted(allocations.items(),key=lambda kv:kv[1]['originalVA']):
        text+=' '+name+' '+hex(s['originalVA'])+(' (NOLOAD)'if s['kind']=='RAM'else'')+' : { KEEP(*('+name+')) }\n ASSERT(SIZEOF('+name+')=='+str(s['bytes'])+', "Original size changed")\n'
    layout.write_text(text+' /DISCARD/ : { *(.comment) *(.note.GNU-stack) }\n}\n')
    modes={}
    for mode,language,std in [('c','c','c11'),('cpp','c++','c++17')]:
        folder=work/mode;folder.mkdir();before=ELF(Path(base['modes'][mode]['integrated_object']))
        bw=ELF(fresh_path.parent/mode/'ADDRESS-WITNESS-ONLY.elf')
        need(digest(before.raw)==prior['modes'][mode]['integrated_sha256']==OLD_OBJECT_SHA,'Actual old native object')
        addresses={n:bw.symbol[n]['value']for n in BASE['und'](before)}
        need(len(addresses)==23 and len(before.relocations)==8267,'Old true23UND/8267RELA')
        for name,info in plan['expected_undefined_symbols'].items():
            need(name not in addresses or addresses[name]==info['originalVA'],'Preserve canonical address')
            addresses[name]=info['originalVA']
        op=folder/'residual-entry.o'
        run([BIN/'clang.exe','--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32',
            '-ffreestanding','-fno-builtin','-fno-stack-protector','-Wall','-Wextra','-Werror',
            '-x',language,'-std='+std,'-c',ROOT/plan['source'],'-o',op],folder,'compile-residual-entry')
        unit=ELF(op);OLD['gate'](unit,plan,allowed_definitions={s['name']for s in plan['defined_symbols']})
        allocations_gate(unit,{s['name']:s for s in plan['sections']})
        need(BASE['und'](unit)==set(plan['expected_undefined_symbols']),'Every new reference declared')
        need(OLD['relocation_semantics'](unit,allocations,addresses)==new_semantics,'Actual new semantic RELA')
        mp=folder/'native-extension.o'
        run([BIN/'ld.lld.exe','-r','--no-relax',base['modes'][mode]['integrated_object'],op,'-o',mp],folder,'integrate-residual-entry')
        merged=ELF(mp);definitions={s['name']for s in before.symbols if s['name']and s['index']!=0 and s['bind']in(1,2)}|{s['name']for s in plan['defined_symbols']}
        semantics=OLD['relocation_semantics'](before,allocations,addresses)+new_semantics
        audit=lambda obj:integrated_gate(obj,before,unit,plan,oldplan,allocations,addresses,semantics,definitions,raw,prior)
        audit(merged);need(len(merged.relocations)==8280 and len(allocations)==660,'Actual660 allocations/8280RELA')
        expected_und=BASE['und'](before)
        strict=folder/'strict-incomplete.elf'
        _,errors=run([BIN/'ld.lld.exe','--no-relax','--error-limit=0','-T',layout,mp,'-o',strict],folder,'strict-final-link',False)
        need(not strict.exists()and set(re.findall(r'undefined symbol: (\w+)',errors.decode(errors='replace')))==expected_und,'Strict link rejects exactly original23 dependencies')
        numeric=folder/'ADDRESS-WITNESS-ONLY.ld'
        numeric.write_text('/* Address obligations, not resident or callback implementations. */\n'+''.join(n+' = '+hex(addresses[n])+';\n'for n in sorted(expected_und)))
        wp=folder/'ADDRESS-WITNESS-ONLY.elf'
        run([BIN/'ld.lld.exe','--no-relax','-T',layout,'-T',numeric,mp,'-o',wp],folder,'numeric-address-witness')
        witness=ELF(wp);OLD['gate'](witness,plan,True);allocations_gate(witness,allocations)
        for name,s in allocations.items():
            sec=witness.byname[name]
            need(sec['address']==s['originalVA']and sec['size']==s['bytes'],'Every original allocation placement')
            if s['kind']!='RAM':need(sec['data']==raw[s['originalVA']-0x8000:s['originalVA']-0x8000+s['bytes']],'Every admitted original source byte')
        for name in base['allocations']:need(bw.byname[name]['data']==witness.byname[name]['data'],'Every inherited final byte retained')
        tables=OLD['fixed_table_check'](witness,oldplan,allocations,raw,True)
        account=coverage(witness,allocations,raw)
        need(account['source_coverage_bytes']==76420 and account['unrepresented_bytes']==380,'Actual source accounting')
        modes[mode]=dict(passed=True,integrated_object=str(mp),integrated_sha256=sha(mp),numeric_witness_sha256=sha(wp),
            undefined_symbols=sorted(expected_und),relocations=len(merged.relocations),allocation_sections=len(allocations),
            strict_rejected=True,inherited_fixed_tables=tables,coverage=account,
            actual_countercases=countercases(merged,audit,plan,oldplan,folder,prior))
    need(modes['c']['integrated_sha256']==modes['cpp']['integrated_sha256']and
         modes['c']['numeric_witness_sha256']==modes['cpp']['numeric_witness_sha256']and
         modes['c']['coverage']==modes['cpp']['coverage'],'Actual C/C++ artifacts and accounting identical')
    sources=dict(base['source_files'])
    for name in [plan['source'],plan['header'],str(a.plan.resolve().relative_to(ROOT)),Path(__file__).name]:sources[name]=sha(ROOT/name)
    result=dict(schema='ID2966-residual-entry-native-extension-v1',passed=True,firmware_sha256=digest(raw),
        source_files=sources,baseline_receipt=str(fresh_path),baseline_receipt_sha256=sha(fresh_path),
        allocations=allocations,modes=modes,new_code_bytes=120,new_RO_bytes=0,source_coverage_bytes=76420,
        original_C_ABIs_proved=False,opaque_callee_ABIs_proved=False,IRQ_ABI_proved=False,
        firmware_executed=False,emulation=False,network=False,hardware=False,native_bin=False,ota_verified=False)
    out=work/'verification.json';out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,receipt=str(out),sha256=sha(out),new_code_bytes=120,new_RO_bytes=0,
        remaining_UND=23,source_coverage_bytes=76420,native_BIN=False,OTA_ready=False)))

if __name__=='__main__':main()
