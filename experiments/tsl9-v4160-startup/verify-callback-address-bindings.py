"""Resolve proved instruction addresses, never claim callback ABI or firmware."""
import argparse,collections,json,re,runpy,struct,sys,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parent;W=ROOT.parents[1]
PREV=runpy.run_path(str(ROOT/'verify-residual-entry-extension.py'))
ELF=PREV['ELF'];BASE=PREV['BASE'];BIN=PREV['BIN'];run=PREV['run'];need=PREV['need']
sha=PREV['sha'];digest=PREV['digest'];read=PREV['read'];roles=PREV['roles'];sym_offset=PREV['sym_offset']
CALLBACKS=[0x901a,0xb0d0,0x11442,0x119c8,0x17476,0x174ee,0x1979a,0x197be,0x197f0,0x1995c]
sx=lambda x,n:x-(1<<n)if x&(1<<(n-1))else x

def label_script(allocations,bindings):
    text='/* Section-relative instruction address labels only. No ABI implementation. */\nOUTPUT_ARCH(riscv)\nSECTIONS {\n'
    for section,s in allocations.items():
        text+=' '+section+' 0'+(' (NOLOAD)'if s['kind']=='RAM'else'')+' : {\n'
        for b in bindings:
            if b['section']==section:text+=' '+b['name']+' = . + '+str(b['offset'])+';\n'
        text+=' KEEP(*('+section+'))\n }\n'
    return text+'}\n'

def expected_bindings(before,baseline,raw):
    bindings=[]
    for va in CALLBACKS:
        name='__tsl9v4160_address_'+format(va,'x');sym=before.symbol[name]
        need(sum(s['name']==name for s in before.symbols)==1,'Exactly one original canonical record')
        need((sym['index'],sym['type'],sym['size'],sym['value'],sym['bind'])==(0,0,0,0,1),'Actual old address-only UND')
        owners=[(n,s)for n,s in baseline['allocations'].items()if s['kind']=='code'and s['originalVA']<=va<s['originalVA']+s['bytes']]
        need(len(owners)==1,'Unique admitted code storage')
        section,s=owners[0];off=va-s['originalVA']
        anchors=[x['name']for x in before.symbols if x['name']and x['bind']==1 and x['type']==0 and
            x['size']==0 and x['index']==before.byname[section]['index']and x['value']==off]
        need(anchors,'Actual existing private NOTYPE0 entry label')
        refs=[r for r in before.relocations if r['target']==name]
        need(len(refs)==1 and refs[0]['type']==23 and refs[0]['addend']==0,'Only one HI20 address use; no inferred function type')
        r=refs[0];pc=baseline['allocations'][r['section']]['originalVA']+r['offset']
        high,low=struct.unpack_from('<II',raw,pc-0x8000)
        need(high&127==0x17 and low&127==0x13 and (low>>12)&7==0 and
            (low>>15)&31==(high>>7)&31 and (low>>7)&31==(high>>7)&31,'Original adjacent own-register AUIPC/ADDI')
        need((pc+sx(high&0xfffff000,32)+sx(low>>20,12))&0xffffffff==va,'Original literal instruction address')
        lows=[q for q in before.relocations if q['section']==r['section']and q['offset']==r['offset']+4]
        need(len(lows)==1 and lows[0]['type']==24 and lows[0]['addend']==0,'One own LOW12_I record')
        target=before.symbols[lows[0]['symbol_index']]
        need(target['index']==before.byname[r['section']]['index']and target['value']==r['offset'],'LOW refers to its own HI instruction')
        bindings.append(dict(name=name,originalVA=va,section=section,offset=off,
            private_anchors=sorted(anchors),reference_section=r['section'],reference_offset=r['offset'],referenceVA=pc,
            raw_HI_LOW=raw[pc-0x8000:pc-0x8000+8].hex(),elf_type=0,size=0))
    return bindings

def binding_gate(obj,before,allocations,bindings,addresses,linked=False):
    need(obj.kind==(2 if linked else 1),'Actual executable witness or relocatable partial kind')
    PREV['allocations_gate'](obj,allocations)
    names={b['name']for b in bindings}
    expected_roles=collections.Counter((b['name'],b['section'],b['originalVA']if linked else b['offset'],0,16,0)for b in bindings)
    actual_roles=collections.Counter({role:count for role,count in roles(obj,set()).items()if role[0]in names})
    need(actual_roles==expected_roles,'Exactly ten new canonical records, no same-name duplicates or alias metadata')
    if not linked:
        PREV['inherited_gate'](before,obj,allocations)
        need(roles(obj,names)==roles(before,names),'Every nonbinding raw symbol occurrence unchanged')
    definitions={s['name']for s in before.symbols if s['name']and s['index']!=0 and s['bind']in(1,2)}|names
    actual=[s for s in obj.symbols if s['name']and s['index']!=0 and s['bind']in(1,2)]
    need(len(actual)==len(definitions)and {s['name']for s in actual}==definitions and
         all(s['bind']==1 for s in actual),'Exact declared globals, no extra ABS/weak/provider')
    for b in bindings:
        s=obj.symbol[b['name']];sec=obj.byname[b['section']]
        need((s['index'],s['type'],s['size'],s['bind'],s['value'])==
            (sec['index'],0,0,1,b['originalVA']if linked else b['offset']),
            'Real source-backed instruction address label, not ABS/FUNC/size contract')
        need(obj.raw[sym_offset(obj,b['name'])+13]==0,'Default address label visibility')
    if linked:return
    need(BASE['und'](obj)==BASE['und'](before)-names,'Only ten proved address obligations resolved')
    need(PREV['OLD']['relocation_semantics'](obj,allocations,addresses)==
         PREV['OLD']['relocation_semantics'](before,allocations,addresses),'Every source semantic relocation unchanged')
    expected=collections.Counter()
    byname={b['name']:b for b in bindings}
    for (owner,off,typ,role,addend),count in PREV['raw_relocation_roles'](before).items():
        if role[0]in byname:
            b=byname[role[0]]
            need(role==(b['name'],'0',0,0,16,0),'Original exact UND role before binding')
            role=(b['name'],b['section'],b['offset'],0,16,0)
        expected[(owner,off,typ,role,addend)]+=count
    need(PREV['raw_relocation_roles'](obj)==expected,'Exact RELA role transition; targets/addends/multiplicity retained')

def countercases(obj,audit,bindings,folder):
    b=bindings[0];out=[]
    ref=next(r for r in obj.relocations if r['target']==b['name'])
    low=next(r for r in obj.relocations if r['section']==ref['section']and r['offset']==ref['offset']+4)
    tags=['ABS_label','FUNC_label','nonzero_size','wrong_offset','hidden','code_byte','writable',
          'unplanned_data_provider','HI_addend','missing_LOW','equivalent_private_target','old_local_value',
          'duplicate_canonical_record','interior_offset_zero']
    for tag in tags:
        data=bytearray(obj.raw);at=sym_offset(obj,b['name']);sec=obj.byname[b['section']]
        if tag=='ABS_label':struct.pack_into('<H',data,at+14,0xfff1)
        elif tag=='FUNC_label':data[at+12]=0x12
        elif tag=='nonzero_size':struct.pack_into('<I',data,at+8,2)
        elif tag=='wrong_offset':struct.pack_into('<I',data,at+4,b['offset']+2)
        elif tag=='hidden':data[at+13]=2
        elif tag=='code_byte':data[sec['offset']+b['offset']]^=1
        elif tag=='writable':struct.pack_into('<I',data,struct.unpack_from('<I',data,32)[0]+sec['index']*40+8,7)
        elif tag=='unplanned_data_provider':
            name=next(n for n in BASE['und'](obj)if n!='__tsl9v4160_rom_entry')
            struct.pack_into('<H',data,sym_offset(obj,name)+14,0xfff1)
        elif tag in('HI_addend','missing_LOW','equivalent_private_target'):
            r=low if tag=='missing_LOW'else ref
            spot=PREV['record_offset'](obj,r['section'],r['offset'],r['type'])
            if tag=='HI_addend':struct.pack_into('<i',data,spot+8,2)
            elif tag=='missing_LOW':struct.pack_into('<I',data,spot+4,struct.unpack_from('<I',data,spot+4)[0]&0xffffff00)
            else:
                index=next(i for i,s in enumerate(obj.symbols)if s['name']==b['private_anchors'][0])
                struct.pack_into('<I',data,spot+4,(index<<8)|r['type'])
        elif tag in('old_local_value','duplicate_canonical_record'):
            local=next(s for s in obj.symbols if s['name'].startswith('.L')and s['bind']==0 and 0<s['index']<0xff00)
            loc=sym_offset(obj,local['name'])
            if tag=='old_local_value':struct.pack_into('<I',data,loc+4,local['value']+2)
            else:struct.pack_into('<I',data,loc,struct.unpack_from('<I',data,at)[0])
        else:
            interior=next(x for x in bindings if x['offset']>0)
            struct.pack_into('<I',data,sym_offset(obj,interior['name'])+4,0)
        p=folder/('COUNTERCASE-address-'+tag+'.o');p.write_bytes(data)
        try:audit(ELF(p))
        except AssertionError as error:reason=str(error)
        else:raise AssertionError('Accepted actual address-label countercase '+tag)
        out.append(dict(case=tag,path=str(p),sha256=sha(p),rejected=True,reason=reason))
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--current-receipt',type=Path,required=True);p.add_argument('--proof-root',type=Path,required=True)
    p.add_argument('--plan',type=Path,default=ROOT/'evidence/callback-address-bindings.json');p.add_argument('--firmware',type=Path)
    p.add_argument('--expect-missing-baseline',action='store_true');a=p.parse_args()
    need(sha(ROOT/'verify-residual-entry-extension.py')=='fbb48013a96758eebd165df80e7b10b13b442936c3aab36e3bee383c80019446','Frozen660 verifier unchanged')
    prior=read(a.current_receipt);plan=read(a.plan)
    need(prior['passed']and prior['schema']=='ID2966-residual-entry-native-extension-v1'and
         len(prior['allocations'])==660 and prior['source_coverage_bytes']==76420,'Actual660 native baseline')
    for name,h in prior['source_files'].items():need(sha(ROOT/name)==h,'Every frozen inherited source retained')
    if a.firmware is None:a.firmware=next((W/n for n in [
        'exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin',
        'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin']if(W/n).is_file()),None)
    need(a.firmware is not None and sha(a.firmware)==PREV['FIRMWARE_SHA'],'Actual original firmware')
    raw=a.firmware.read_bytes();before=ELF(Path(prior['modes']['c']['integrated_object']))
    need(digest(before.raw)==prior['modes']['c']['integrated_sha256']=='72aa6c1ea1c081a56a3601052ced8f445a50e05fe79e311292fa7e05db4a354b','Actual660 C object')
    bindings=expected_bindings(before,prior,raw)
    need(plan['schema']=='ID2966-callback-instruction-address-bindings-v1'and
         plan['source_firmware_sha256']==digest(raw)and plan['bindings']==bindings and
         plan['callback_ABIs_proved']is False and plan['OTA_ready']is False,'Only explicit instruction-address plan')
    need((ROOT/plan['source']).read_text()==label_script(prior['allocations'],bindings)and
         sha(ROOT/plan['source'])==plan['source_sha256'],'Exact reviewed section-label linker source')
    proof=plan['proof'];path=a.proof_root/proof['scope']/proof['seal']
    need(proof['scope']=='callback-obligations'and proof['seal']=='final-audit.json'and
         proof['sha256']=='6ab9a215539bbc8730132faa38a8b28e414f33abaa7d9e1497dfcd7ff870e67a',
         'Pinned independent original instruction-address admission')
    need(sha(path)==proof['sha256']and read(path)['passed'],'Independent callback address evidence')
    for row in read(path)['members']:
        child=(path.parent/row['path']).resolve()
        need(child.is_relative_to(a.proof_root.resolve())and child.stat().st_size==row['bytes']and sha(child)==row['sha256'],'Actual sealed proof member')
    if a.expect_missing_baseline:
        try:binding_gate(before,before,prior['allocations'],bindings,{})
        except AssertionError as error:
            need(str(error)=='Exactly ten new canonical records, no same-name duplicates or alias metadata','Expected missing-address RED')
            print(json.dumps(dict(expected_red=True,reason=str(error))));return
        raise AssertionError('Baseline unexpectedly supplies section-backed labels')
    work=ROOT/'build'/('callback-address-bindings-'+uuid.uuid4().hex);work.mkdir(parents=True)
    oldproof=next((W/n for n in ['apk-analysis/tsl9-v4160-residual-frontier-2026-10-21',
        'analysis/v4160-residual-frontier-2026-10-21']if(W/n).is_dir()),None)
    need(oldproof is not None,'Original660 proof root')
    _,output=run([sys.executable,'-X','utf8','-B',ROOT/'verify-residual-entry-extension.py',
        '--current-receipt',prior['baseline_receipt'],'--proof-root',oldproof,'--firmware',a.firmware.resolve()],work,'unchanged660-gate')
    fresh_path=Path(json.loads(output.decode().strip().splitlines()[-1])['receipt']);base=read(fresh_path)
    need(base['passed']and base['allocations']==prior['allocations'],'Fresh full660 gate')
    allocations=base['allocations'];layout=work/'original-address-layout.ld'
    text='OUTPUT_ARCH(riscv)\nENTRY(__tsl9v4160_image_entry)\nSECTIONS {\n'
    for n,s in sorted(allocations.items(),key=lambda kv:kv[1]['originalVA']):
        text+=' '+n+' '+hex(s['originalVA'])+(' (NOLOAD)'if s['kind']=='RAM'else'')+' : { KEEP(*('+n+')) }\n ASSERT(SIZEOF('+n+')=='+str(s['bytes'])+', "Original size changed")\n'
    layout.write_text(text+' /DISCARD/ : { *(.comment) *(.note.GNU-stack) }\n}\n')
    modes={};names={b['name']for b in bindings};oldplan=read(ROOT/'evidence/reachable-code-plan.json')
    for mode in ['c','cpp']:
        folder=work/mode;folder.mkdir();bp=Path(base['modes'][mode]['integrated_object']);before=ELF(bp)
        bw=ELF(fresh_path.parent/mode/'ADDRESS-WITNESS-ONLY.elf')
        need(sha(bp)==prior['modes'][mode]['integrated_sha256'],'C/C++ baseline identity')
        addresses={n:bw.symbol[n]['value']for n in BASE['und'](before)}
        need(len(addresses)==23 and expected_bindings(before,base,raw)==bindings,'Same ten source-bound input labels')
        op=folder/'native-address-bindings.o'
        run([BIN/'ld.lld.exe','-r','--no-relax','-T',ROOT/plan['source'],bp,'-o',op],folder,'bind-instruction-addresses')
        obj=ELF(op);audit=lambda e:binding_gate(e,before,allocations,bindings,addresses)
        audit(obj);need(len(obj.relocations)==8280,'No new relocation or storage')
        remaining=BASE['und'](before)-names;need(len(remaining)==13,'Thirteen remaining ELF UND, runtime ABI still unproved')
        strict=folder/'strict-incomplete.elf'
        _,errors=run([BIN/'ld.lld.exe','--no-relax','--error-limit=0','-T',layout,op,'-o',strict],folder,'strict-final-link',False)
        need(not strict.exists()and set(re.findall(r'undefined symbol: (\w+)',errors.decode(errors='replace')))==remaining,'Strict still rejects all remaining thirteen dependencies')
        numeric=folder/'ADDRESS-WITNESS-ONLY.ld'
        numeric.write_text('/* Remaining numeric obligations only; never callback ABI or firmware. */\n'+''.join(n+' = '+hex(addresses[n])+';\n'for n in sorted(remaining)))
        wp=folder/'ADDRESS-WITNESS-ONLY.elf'
        run([BIN/'ld.lld.exe','--no-relax','-T',layout,'-T',numeric,op,'-o',wp],folder,'numeric-address-witness')
        witness=ELF(wp)
        need(roles(witness,names)==roles(bw,names),'Every nonbinding final symbol role unchanged, including thirteen numeric obligations')
        expected_roles=collections.Counter((b['name'],b['section'],b['originalVA'],0,16,0)for b in bindings)
        need(collections.Counter({role:count for role,count in roles(witness,set()).items()if role[0]in names})==expected_roles,'Exactly ten actual final address labels')
        # Numeric witness includes the thirteen explicit ABS obligations, unlike the partial object.
        for b in bindings:
            s=witness.symbol[b['name']];sec=witness.byname[b['section']]
            need((s['index'],s['value'],s['type'],s['size'],s['bind'])==
                (sec['index'],b['originalVA'],0,0,1)and witness.raw[sym_offset(witness,b['name'])+13]==0,
                'Witness retains actual section-backed labels, not numeric substitutes')
        PREV['allocations_gate'](witness,allocations)
        for n,s in allocations.items():
            sec=witness.byname[n]
            need(sec['address']==s['originalVA']and sec['size']==s['bytes'],'Original VA placement')
            need(sec['data']==bw.byname[n]['data'],'Every final inherited byte identical')
            if s['kind']!='RAM':need(sec['data']==raw[s['originalVA']-0x8000:s['originalVA']-0x8000+s['bytes']],'Every admitted source byte original')
        PREV['OLD']['fixed_table_check'](witness,oldplan,allocations,raw,True)
        accounting=PREV['coverage'](witness,allocations,raw)
        need(accounting==base['modes'][mode]['coverage'],'No source coverage gain or hidden padding change')
        modes[mode]=dict(passed=True,integrated_object=str(op),integrated_sha256=sha(op),numeric_witness_sha256=sha(wp),
            undefined_symbols=sorted(remaining),relocations=len(obj.relocations),allocation_sections=len(allocations),
            strict_rejected=True,coverage=accounting,actual_countercases=countercases(obj,audit,bindings,folder))
    need(modes['c']['integrated_sha256']==modes['cpp']['integrated_sha256']and
         modes['c']['numeric_witness_sha256']==modes['cpp']['numeric_witness_sha256'],'Actual C/C++ artifacts identical')
    sources=dict(base['source_files'])
    for name in [plan['source'],str(a.plan.resolve().relative_to(ROOT)),Path(__file__).name]:sources[name]=sha(ROOT/name)
    result=dict(schema='ID2966-callback-address-native-bindings-v1',passed=True,source_files=sources,
        firmware_sha256=digest(raw),baseline_receipt=str(fresh_path),baseline_receipt_sha256=sha(fresh_path),
        allocations=allocations,modes=modes,bindings=bindings,resolved_instruction_addresses=10,
        callback_runtime_contracts_still_unproved=sorted(names),new_code_bytes=0,new_RO_bytes=0,source_coverage_bytes=76420,
        original_C_ABIs_proved=False,opaque_callee_ABIs_proved=False,IRQ_ABI_proved=False,
        firmware_executed=False,emulation=False,network=False,hardware=False,native_bin=False,ota_verified=False)
    out=work/'verification.json';out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,receipt=str(out),sha256=sha(out),resolved_instruction_addresses=10,
        remaining_ELF_UND=13,callback_ABIs_proved=False,new_source_bytes=0,native_BIN=False,OTA_ready=False)))
if __name__=='__main__':main()
