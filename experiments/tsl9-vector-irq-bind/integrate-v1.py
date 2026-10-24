#!/usr/bin/env python3
"""Bind a genuine existing C/C++ IRQ provider; inspect native artifacts only."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
K=json.loads((HERE/'contract-v1.json').read_bytes())
def need(ok,message):
    if not ok:raise ValueError(message)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
need(sha(ROOT/K['parent_checker'])==K['parent_checker_sha256'],'Frozen genuine parent checker')
P=runpy.run_path(str(ROOT/K['parent_checker']))
V=P['V']
portable,encoded=V['portable'],V['encoded']
OUTPUT='UNRESOLVED-STARTUP-VECTOR-IRQ.o'

def parent(mode):
    return ROOT/K['parent_component']/mode/K['parent_object']

def provider(mode):
    return (ROOT/K['curation']).parent/K['provider_unit']['name']/mode/'curated/unit.o'

def audit_provider(path):
    e=V['elf'](path)
    need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual RISC-V data/code ET_REL')
    allocated=[s for s in e.sections if s['flags']&2 and s['size']]
    need(len(allocated)==1,'Only one genuine allocated IRQ function')
    sec=allocated[0]
    need(sec['name']==K['provider_section']and sec['flags']==6 and sec['type']==1 and
         sec['size']==76 and sec['address']==0,'Exact original76B code section')
    globals_=[s for s in e.symbols if s['info']>>4]
    need(len(globals_)==1,'No IRQ provider substitutes or external declarations')
    f=globals_[0]
    need(f['name']==K['provider_symbol']and f['info']==18 and f['other']==0 and
         f['value']==0 and f['size']==76 and f['section']==sec['index'],'Real strong full-size FUNC')
    need(not e.relocations,'No hidden unresolved IRQ references')
    raw=e.data(sec)
    fw=(ROOT/K['firmware']).read_bytes()
    original=fw[K['provider_entry']-0x8000:K['provider_end']-0x8000]
    need(raw==original and sha(path)==K['provider_object_sha256'],'Entire actual C-compiled IRQ equals original bytes')
    need(hashlib.sha256(raw).hexdigest()==K['original_provider_sha256'],'Original provider body identity')
    at=count=0
    while at<len(raw):
        width=4 if raw[at]&3==3 else 2
        need(at+width<=len(raw),'Whole recorded IRQ instruction')
        at+=width;count+=1
    need(count==21 and raw[-4:]==bytes.fromhex('73002030'),'Complete21-instruction handler ending in MRET')
    return dict(passed=True,bytes=76,instructions=21,FUNC=1,UND=0,RELA=0,
                code_sha256=K['original_provider_sha256'],object_sha256=sha(path),
                complete_original_bytes_equal=True,ends_with_MRET=True,
                IRQ_context_or_C_ABI_proved=False,target_executed=False)

def inputs(llvm):
    paths=[Path(__file__),HERE/'contract-v1.json',HERE/'joined-v1.ld',
           ROOT/K['parent_checker'],ROOT/K['parent_component']/'measurement.json',
           ROOT/K['curation'],ROOT/K['vector_spec'],ROOT/K['reader'],
           ROOT/K['curation_checker'],ROOT/K['firmware'],ROOT/'src/source-manifest.json',
           ROOT/K['provider_unit']['origin_unit'],ROOT/K['provider_unit']['curated_unit']]
    for mode in('c','cpp'):
        paths += [parent(mode),parent(mode).parent/'verification.json',provider(mode)]
    paths += [llvm/n for n in K['tools']]
    return {str(p):dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(set(paths))}

def source_proof(llvm):
    for key in('parent_checker','curation','reader','firmware','curation_checker'):
        need(sha(ROOT/K[key])==K[key+'_sha256'],'Pinned '+key)
    need(sha(ROOT/'src/source-manifest.json')==K['manifest_sha256'],'Exact unchanged80-file manifest')
    manifest=json.loads((ROOT/'src/source-manifest.json').read_bytes())
    need(K['provider_unit']in manifest['native_units'],'Existing exact IRQ source registration')
    need(sha(ROOT/K['provider_unit']['curated_unit'])==K['provider_source_sha256']and
         sha(ROOT/K['provider_unit']['origin_unit'])==K['provider_source_sha256'],'Original and curated IRQ C unchanged')
    for name,pin in K['tools'].items():
        need(sha(llvm/name)==pin,'Pinned native tool '+name)
    current=P['source_proof'](llvm)
    record_path=ROOT/K['parent_component']/'measurement.json'
    need(sha(record_path)==K['parent_receipt_sha256'],'Frozen parent build measurement')
    record=json.loads(record_path.read_bytes())
    need(record['inputs']==portable(P['inputs'](llvm),llvm)and record['source_proof']==current,
         'Every original parent input and whole current source proof unchanged')
    for mode in('c','cpp'):
        need(sha(parent(mode))==K['parent_object_sha256'],'Actual genuine parent component')
        need(P['inventory'](parent(mode).parent)==record['modes'][mode]['artifacts'],'Every retained parent output unchanged')
        need(P['audit_component'](parent(mode),mode)==record['modes'][mode]['result'],'Complete current parent vector/startup audit')
        audit_provider(provider(mode))
    return dict(passed=True,source_C_H_files=80,native_code_units=53,independent_data_units=1,
                current_source_comparisons=108,current_source_objects=216,
                parent_whole_current_input_replay_passed=True,manifest_and_C_sources_unchanged=True,
                new_C_stubs_or_providers_added=False,reused_full_original_IRQ_bytes=76,
                target_executed=False,negative_cases_executed=0)

def globals_by_name(e):
    rows=[s for s in e.symbols if s['info']>>4]
    need(len({s['name']for s in rows})==len(rows),'Unique genuine global symbols')
    need(all(s['section']!=0xfff1 for s in rows),'No ABS provider substitutes')
    return {s['name']:s for s in rows}

def audit_component(path,mode):
    p,n,e=(V['elf'](x)for x in(parent(mode),provider(mode),path))
    pm,nm,em=(globals_by_name(x)for x in(p,n,e))
    need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Unresolved RISC-V ET_REL without loading headers')
    expected_alloc={'.boot_code':(6,648),'.initializer':(2,128),'.vectors':(2,328)}
    need({s['name']for s in e.sections if s['flags']&2 and s['size']}==set(expected_alloc),'All genuine code/data allocations')
    for name,(flags,size)in expected_alloc.items():
        sec=e.section(name)
        need(sec['flags']==flags and sec['type']==1 and sec['size']==size and sec['address']==0,'Exact section and diagnostic VMA0 '+name)
    need(e.data('.boot_code')==p.data('.boot_code')+n.data(K['provider_section']),
         'Whole572B parent code and genuine76B IRQ body preserved')
    need(e.data('.initializer')==p.data('.initializer')and e.data('.vectors')==p.data('.vectors'),
         'All456 parent data carrier bytes unchanged')
    need(set(em)==set(pm)|set(nm),'Exact complete merged global inventory')
    for name,s in pm.items():
        actual=em[name]
        if s['section']:
            need(actual['info']==s['info']and actual['other']==s['other']and actual['size']==s['size']and
                 actual['value']==s['value']and e.sections[actual['section']]['name']==p.sections[s['section']]['name'],
                 'Exact prior code/data owner '+name)
        elif name==K['new_alias']:
            need(actual['info']==18 and actual['other']==0 and actual['size']==0 and
                 actual['value']==572 and e.sections[actual['section']]['name']=='.boot_code',
                 'True section-relative zero-size alias to full real IRQ body')
        else:
            need(actual['section']==0 and actual['info']==s['info']and actual['other']==s['other']and
                 actual['value']==0 and actual['size']==0,'Other unresolved entries remain explicit')
    full=em[K['provider_symbol']]
    alias=em[K['new_alias']]
    need(full['info']==18 and full['other']==0 and full['size']==76 and full['value']==572 and
         e.sections[full['section']]['name']=='.boot_code','Real76B compiled function provider')
    need(alias['section']==full['section']and alias['value']==full['value'],'Alias and full body share actual section ownership')
    code=e.data('.boot_code')[alias['value']:alias['value']+full['size']]
    original=(ROOT/K['firmware']).read_bytes()[K['provider_entry']-0x8000:K['provider_end']-0x8000]
    need(code==original and hashlib.sha256(code).hexdigest()==K['original_provider_sha256'],'Full body at real alias owner equals original')
    expected=Counter()
    for rel in p.relocations:
        sym=p.symbols[rel['symbol']]
        if sym['info']>>4:
            bound=em[sym['name']]
            owner=e.sections[bound['section']]['name']if bound['section']else''
            role=(bound['name'],bound['info'],bound['other'],bound['size'],owner,bound['value'])
        else:
            need(sym['section']>0 and sym['section']!=0xfff1,'Genuine parent local HI-label owner')
            role=(sym['name'],sym['info'],sym['other'],sym['size'],
                  p.sections[sym['section']]['name'],sym['value'])
        expected[(p.sections[rel['section']]['name'],rel['offset'],rel['type'],rel['addend'],role)]+=1
    actual=Counter()
    for rel in e.relocations:
        sym=e.symbols[rel['symbol']]
        owner=e.sections[sym['section']]['name']if sym['section']else''
        role=(sym['name'],sym['info'],sym['other'],sym['size'],owner,sym['value'])
        actual[(e.sections[rel['section']]['name'],rel['offset'],rel['type'],rel['addend'],role)]+=1
    need(actual==expected and len(e.relocations)==144,'Every typed relocation and exact local/global symbol role')
    slot=[rel for rel in e.relocations if e.sections[rel['section']]['name']=='.vectors'and
          rel['offset']==K['vector_word_index']*4]
    need(len(slot)==1 and slot[0]['type']==1 and slot[0]['addend']==0 and
         e.symbols[slot[0]['symbol']]['name']==K['new_alias'],'Original vector slot39 R_RISCV_32 now binds genuine IRQ body')
    spec=json.loads((ROOT/K['vector_spec']).read_bytes())
    need(spec['entries'][39]['word']==K['provider_entry']and
         spec['entries'][39]['symbol']==K['new_alias']and
         spec['start']+39*4==K['vector_original_word_PC'],'Exact original80D4 slot to16FB6')
    restored=bytearray(e.data('.vectors'));bound=external=0
    for row in spec['entries']:
        if not row['symbol']:continue
        target=em[row['symbol']]
        if target['section']:bound+=1
        else:external+=1
        restored[row['index']*4:row['index']*4+4]=row['word'].to_bytes(4,'little')
    original_vectors=(ROOT/K['firmware']).read_bytes()[spec['start']-0x8000:spec['end']-0x8000]
    need(bytes(restored)==original_vectors and bound==56 and external==6,'All original vector words and exact real/external binding counts')
    undefined=sorted(name for name,s in em.items()if not s['section'])
    need(undefined==K['remaining_undefined'],'Exactly seven remaining entries')
    funcs=[s for s in em.values()if s['info']==18 and s['section']]
    need(sum(bool(s['size'])for s in funcs)==100 and sum(not s['size']for s in funcs)==1,'100 genuine nonzero FUNC regions plus one explicit alias')
    return dict(passed=True,mode=mode,code_bytes=648,original_code_instructions=233,
                initializer_bytes=128,vector_carrier_bytes=328,total_data_bytes=456,
                nonzero_FUNC_regions=100,zero_size_FUNC_aliases=1,RELA=144,UND=undefined,
                newly_resolved_parent_entry=K['new_alias'],new_genuine_provider=K['provider_symbol'],
                original_IRQ_bytes=76,original_IRQ_instructions=21,
                original_IRQ_code_sha256=K['original_provider_sha256'],
                parent572B_code_and456B_data_unchanged=True,
                full_IRQ_body_at_alias_equals_original=True,alias_owns_real_full_size_provider=True,
                all_global_local_relocation_targets_owned=True,vector_slot_index=39,
                vector_word_original_PC=K['vector_original_word_PC'],vector_slot_original_target=K['provider_entry'],
                vector_slots_bound_to_real_code=56,vector_slots_still_external=6,
                remaining_unique_vector_entries=5,IRQ_provider_relocations=0,
                no_executable_stub_added=True,ABS_providers=0,
                diagnostic_provider_offset=572,final_original_address_placement_proved=False,
                all_original_vector_words_equal_after_data_only_encoding=True,
                IRQ_register_context_or_physical_peripheral_proved=False,
                typed_address_binding_proves_IRQ_ABI=False,installed_resident_known=False,
                component_sha256=sha(path),ELF_VMA_zero=True,executable=False,
                target_executed=False,ISA_emulated=False,HOST_model_executed=False,
                hardware_accessed=False,network=False,negative_cases_executed=0,
                firmware_BIN_generated=False,firmware_ready=False)

def inventory(folder):
    return {p.name:dict(bytes=p.stat().st_size,sha256=sha(p))
            for p in sorted(folder.iterdir())if p.is_file()}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tool-dir',type=Path,required=True)
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument('--output',type=Path)
    group.add_argument('--replay',type=Path)
    a=p.parse_args();llvm=a.tool_dir.resolve()
    proof=source_proof(llvm);before=portable(inputs(llvm),llvm)
    if a.replay:
        out=a.replay.resolve();need(out.parent==HERE/'build','Owned retained native output')
        saved=json.loads((out/'measurement.json').read_bytes())
        need(saved['inputs']==before and saved['source_proof']==proof,'All retained native producer inputs unchanged')
        for mode in('c','cpp'):
            need(saved['modes'][mode]['artifacts']==inventory(out/mode),'Every retained normal output unchanged')
            need(saved['modes'][mode]['result']==audit_component(out/mode/OUTPUT,mode),'Actual linked IRQ component replay')
        print(json.dumps(dict(passed=True,mode='read-only-normal-vector-IRQ-replay',source_proof=proof)))
        return
    out=a.output.resolve();need(out.parent==HERE/'build'and not out.exists(),'Create-only owned output')
    report=dict(schema='TSL9-vector-IRQ-native-link-v1',inputs=before,source_proof=proof,modes={})
    for mode in('c','cpp'):
        f=out/mode;f.mkdir(parents=True);commands=[];output=f/OUTPUT
        recipes=[('link',[str(llvm/'ld.lld.exe'),'-r','--no-relax','-T',str(HERE/'joined-v1.ld'),
                          str(parent(mode)),str(provider(mode)),'-o',str(output)]),
                 ('read',[str(llvm/'llvm-objdump.exe'),'-dr','-t','-h',str(output)])]
        for label,argv in recipes:
            result=subprocess.run(argv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
            (f/(label+'.log')).write_bytes(result.stdout)
            commands.append(dict(label=label,argv=argv,exit=result.returncode))
            need(result.returncode==0,'Actual '+label+' failed; original log retained')
        audit=audit_component(output,mode)
        (f/'verification.json').write_bytes(encoded(audit))
        report['modes'][mode]=dict(result=audit,commands=commands,artifacts=inventory(f))
        print(json.dumps({k:v for k,v in audit.items()if k!='UND'}|dict(UND_count=len(audit['UND']))))
    need(before==portable(inputs(llvm),llvm),'All actual inputs unchanged during normal link')
    (out/'measurement.json').write_bytes(encoded(portable(report,llvm)))

if __name__=='__main__':
    try:main()
    except(ValueError,OSError,subprocess.SubprocessError)as error:
        message=str(error)
        for path,token in[(ROOT,'$'+'{PROJECT_ROOT}'),(Path.home(),'$'+'{USERPROFILE}')]:
            message=message.replace(str(path),token).replace(path.as_posix(),token)
        print('FAIL: '+message,file=sys.stderr);sys.exit(1)
