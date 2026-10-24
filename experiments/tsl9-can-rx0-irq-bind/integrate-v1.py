#!/usr/bin/env python3
"""Bind retained C/C++ RX0 IRQ, register-reader and ring regions; no target execution."""
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
need(sha(ROOT/K['original_encoding_helper'])==K['original_encoding_helper_sha256'],'Frozen static instruction encoding helper')
P=runpy.run_path(str(ROOT/K['parent_checker']))
V=P['V']
B=runpy.run_path(str(ROOT/K['original_encoding_helper']))
portable,encoded=V['portable'],V['encoded']
OUTPUT='UNRESOLVED-STARTUP-CAN-RX0.o'

def parent(mode):
    return ROOT/K['parent_component']/mode/K['parent_object']
def native(unit,mode):
    return (ROOT/K['curation']).parent/unit['unit']['name']/mode/'curated/unit.o'
def elf(path):return V['elf'](path)
def global_map(e):
    rows=[s for s in e.symbols if s['info']>>4]
    need(len({s['name']for s in rows})==len(rows),'Unique global symbol inventory')
    need(all(s['section']!=0xfff1 for s in rows),'No ABS provider substitutes')
    return {s['name']:s for s in rows}

def audit_unit(path,unit):
    e=elf(path);gm=global_map(e)
    need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual RISC-V ET_REL')
    need(sha(path)==unit['object_sha256'],'Exact retained native object identity')
    defined={name:s for name,s in gm.items()if s['section']}
    need(set(defined)=={r['name']for r in unit['regions']},'Exact genuine region definitions')
    need(sorted(name for name,s in gm.items()if not s['section'])==unit['UND'],'Exact explicit unit interface')
    need(len(e.relocations)==unit['RELA']==3,'Every recorded native typed edge')
    fw=(ROOT/K['firmware']).read_bytes()
    owner_sections=set();total_bytes=total_i=0;relocation_facts=[]
    restored_span=bytearray()
    for region in unit['regions']:
        f=defined[region['name']];sec=e.sections[f['section']]
        need(f['info']==18 and f['other']==0 and f['value']==0 and f['size']==region['bytes'],
             'Real full-size region definition '+region['name'])
        need(sec['name']=='.text.'+f['name']and sec['flags']==6 and sec['type']==1 and
             sec['size']==f['size']and sec['address']==0,'Exact region allocation')
        need(sec['index']not in owner_sections,'Unique function section owner');owner_sections.add(sec['index'])
        original=fw[region['start']-0x8000:region['end']-0x8000]
        need(hashlib.sha256(original).hexdigest()==region['original_sha256'],'Pinned original region bytes')
        actual=e.data(sec);restored=bytearray(actual)
        rows=[r for r in e.relocations if r['section']==sec['index']]
        need(len({r['offset']for r in rows})==len(rows),'Unique relocation site')
        for rel in rows:
            kind=rel['type'];at=rel['offset']
            need(kind in(16,17,44,45)and rel['addend']==0,'Only original typed control edges')
            width,preserve=B['MASKS'][kind]
            need(0<=at<=len(actual)-width,'Owned control instruction extent')
            pc=region['start']+at
            decoded=B['decode_control'](original[at:at+width],pc)
            target=e.symbols[rel['symbol']]
            need(decoded and decoded[0]==kind and target['info']in(16,18)and target['name']in gm,
                 'Original control kind and genuine global reference')
            destination=int(target['name'].rsplit('_',1)[1],16)
            need(decoded[1]==destination,'Exact independently decoded original destination')
            source_bits=int.from_bytes(actual[at:at+width],'little')
            need((source_bits&preserve)==(int.from_bytes(original[at:at+width],'little')&preserve),
                 'All opcode/register/control condition bits preserved')
            restored[at:at+width]=((source_bits&preserve)|B['immediate'](kind,destination-pc)).to_bytes(width,'little')
            relocation_facts.append(dict(PC=pc,type=kind,target=destination,symbol=target['name']))
        need(bytes(restored)==original,'Whole region original-equal after data-only original-VA control encoding')
        at=0;count=0
        while at<len(original):
            width=4 if original[at]&3==3 else 2
            need(at+width<=len(original),'Whole recorded instruction')
            at+=width;count+=1
        total_i+=count;total_bytes+=len(original);restored_span.extend(restored)
    need({s['index']for s in e.sections if s['flags']&2 and s['size']}==owner_sections,
         'Every allocated native byte owned by a recorded code region')
    need(total_bytes==unit['bytes']and total_i==unit['instructions'],'Whole declared original span and instruction count')
    need(len(relocation_facts)==3 and hashlib.sha256(restored_span).hexdigest()==unit['original_span_sha256'],
         'All three edges and complete original span identity')
    return dict(passed=True,unit=unit['unit']['name'],bytes=total_bytes,instructions=total_i,
                FUNC=len(defined),RELA=3,UND=unit['UND'],object_sha256=sha(path),
                all_bytes_original_equal_after_data_only_encoding=True,
                all_original_destinations_and_control_bits_exact=True,
                relocation_facts=relocation_facts,target_executed=False)

def inputs(llvm):
    paths=[Path(__file__),HERE/'contract-v1.json',HERE/'joined-v1.ld',ROOT/K['parent_checker'],
           ROOT/K['parent_component']/'measurement.json',ROOT/K['curation'],ROOT/K['firmware'],
           ROOT/K['reader'],ROOT/K['curation_checker'],ROOT/K['original_encoding_helper'],
           ROOT/K['vector_spec'],ROOT/'src/source-manifest.json']
    for unit in K['units']:
        paths += [ROOT/unit['unit']['origin_unit'],ROOT/unit['unit']['curated_unit']]
        paths += [native(unit,m)for m in('c','cpp')]
    for mode in('c','cpp'):
        paths += [parent(mode),parent(mode).parent/'verification.json']
    paths += [llvm/name for name in K['tools']]
    return {str(p):dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(set(paths))}

def source_proof(llvm):
    for key in('parent_checker','curation','firmware','reader','curation_checker','original_encoding_helper'):
        need(sha(ROOT/K[key])==K[key+'_sha256'],'Pinned '+key)
    need(sha(ROOT/'src/source-manifest.json')==K['manifest_sha256'],'Exact unchanged80-file manifest')
    manifest=json.loads((ROOT/'src/source-manifest.json').read_bytes())
    for name,pin in K['tools'].items():need(sha(llvm/name)==pin,'Pinned native tool '+name)
    current=P['source_proof'](llvm)
    record_path=ROOT/K['parent_component']/'measurement.json'
    need(sha(record_path)==K['parent_receipt_sha256'],'Genuine retained parent measurement')
    rec=json.loads(record_path.read_bytes())
    need(rec['source_proof']==current and rec['inputs']==portable(P['inputs'](llvm),llvm),
         'Every parent producer input and complete current source proof unchanged')
    for unit in K['units']:
        need(unit['unit']in manifest['native_units'],'Exact existing native source registration')
        need(sha(ROOT/unit['unit']['origin_unit'])==unit['source_sha256']and
             sha(ROOT/unit['unit']['curated_unit'])==unit['source_sha256'],'Original and curated C source unchanged')
    for mode in('c','cpp'):
        need(sha(parent(mode))==K['parent_object_sha256'],'Actual genuine parent component')
        need(rec['modes'][mode]['artifacts']==P['inventory'](parent(mode).parent),'Complete retained parent output inventory')
        need(rec['modes'][mode]['result']==P['audit_component'](parent(mode),mode),'Complete normal parent audit')
        for unit in K['units']:audit_unit(native(unit,mode),unit)
    return dict(passed=True,source_C_H_files=80,native_code_units=53,independent_data_units=1,
                current_source_comparisons=108,current_source_objects=216,
                whole_parent_inputs_and_current_source_replayed=True,
                existing_C_and_manifest_unchanged=True,reused_native_units=3,
                new_original_bytes=308,new_original_instructions=102,
                all_three_units_original_VA_equal=True,target_executed=False,negative_cases_executed=0)

def code_offsets():
    offsets={};at=K['parent_code_bytes']
    for unit in K['units']:
        for region in unit['regions']:
            offsets[region['name']]=at;at+=region['bytes']
    need(at==K['new_code_bytes'],'Exact composed code extent')
    return offsets

def audit_component(path,mode):
    p,e=elf(parent(mode)),elf(path)
    natives=[(elf(native(unit,mode)),unit)for unit in K['units']]
    pm,em=global_map(p),global_map(e)
    maps=[(obj,global_map(obj),unit)for obj,unit in natives]
    offsets=code_offsets()
    need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Unresolved ET_REL without loading headers')
    alloc={'.boot_code':(6,956),'.initializer':(2,128),'.vectors':(2,328)}
    need({s['name']for s in e.sections if s['flags']&2 and s['size']}==set(alloc),'Only genuine code/data sections')
    for name,(flags,size)in alloc.items():
        s=e.section(name)
        need(s['flags']==flags and s['type']==1 and s['size']==size and s['address']==0,'Exact diagnostic section '+name)
    pieces=[p.data('.boot_code')]
    for obj,gm,unit in maps:
        pieces += [obj.data(obj.sections[gm[r['name']]['section']])for r in unit['regions']]
    need(e.data('.boot_code')==b''.join(pieces),'All648 parent and308 new native carrier bytes unchanged')
    need(e.data('.initializer')==p.data('.initializer')and e.data('.vectors')==p.data('.vectors'),
         'Every456 parent data carrier byte unchanged')
    wanted=set(pm)
    for obj,gm,unit in maps:wanted.update(gm)
    need(set(em)==wanted,'Complete merged global symbol inventory')
    for name,actual in em.items():
        if name==K['alias']:
            need(actual['info']==18 and actual['other']==0 and actual['size']==0 and
                 actual['value']==offsets[K['provider_entry_name']]and
                 e.sections[actual['section']]['name']=='.boot_code','Actual section-relative vector alias')
            continue
        definitions=[]
        if name in pm and pm[name]['section']:definitions.append((p,pm[name],False))
        for obj,gm,unit in maps:
            if name in gm and gm[name]['section']:definitions.append((obj,gm[name],True))
        if definitions:
            need(len(definitions)==1,'Exactly one genuine provider definition')
            original,s,is_new=definitions[0]
            owner='.boot_code'if is_new else original.sections[s['section']]['name']
            value=offsets[s['name']]+s['value']if is_new else s['value']
            need(actual['info']==s['info']and actual['other']==s['other']and actual['size']==s['size']and
                 actual['value']==value and e.sections[actual['section']]['name']==owner,'Exact original/full native owner '+name)
        else:
            need(name in pm and actual['section']==0 and actual['info']==pm[name]['info']and
                 actual['value']==0 and actual['size']==0,'Other outstanding entries remain explicit')
    alias=em[K['alias']];entry=em[K['provider_entry_name']]
    need(alias['section']==entry['section']and alias['value']==entry['value']and entry['size']==14,
         'Zero-size alias points at true14B entry within complete52B adapter')
    expected=Counter()
    for original,is_new in[(p,False)]+[(obj,True)for obj,_,_ in maps]:
        for rel in original.relocations:
            s=original.symbols[rel['symbol']]
            owner=original.sections[rel['section']]['name'];at=rel['offset']
            if is_new:
                function_name=owner.removeprefix('.text.')
                need(function_name in offsets,'Every new relocation has a real native code owner')
                owner,at='.boot_code',offsets[function_name]+at
            if s['info']>>4:
                bound=em[s['name']];target=e.sections[bound['section']]['name']if bound['section']else''
                role=(bound['name'],bound['info'],bound['other'],bound['size'],target,bound['value'])
            else:
                need(not is_new and s['section']>0 and s['section']!=0xfff1,'Genuine parent local HI-label owner')
                role=(s['name'],s['info'],s['other'],s['size'],original.sections[s['section']]['name'],s['value'])
            expected[(owner,at,rel['type'],rel['addend'],role)]+=1
    actual=Counter()
    for rel in e.relocations:
        s=e.symbols[rel['symbol']];target=e.sections[s['section']]['name']if s['section']else''
        role=(s['name'],s['info'],s['other'],s['size'],target,s['value'])
        actual[(e.sections[rel['section']]['name'],rel['offset'],rel['type'],rel['addend'],role)]+=1
    need(actual==expected and len(e.relocations)==153,'Every153 typed reference and full local/global target ownership')
    spec=json.loads((ROOT/K['vector_spec']).read_bytes())
    need(spec['entries'][36]['word']==K['vector_original_target']and
         spec['entries'][36]['symbol']==K['alias'],'Exact original vector36 destination')
    slot=[r for r in e.relocations if e.sections[r['section']]['name']=='.vectors'and r['offset']==36*4]
    need(len(slot)==1 and slot[0]['type']==1 and slot[0]['addend']==0 and
         e.symbols[slot[0]['symbol']]['name']==K['alias'],'Original vector36 R_RISCV_32 binds real adapter')
    restored=bytearray(e.data('.vectors'));bound=external=0
    for row in spec['entries']:
        if not row['symbol']:continue
        target=em[row['symbol']]
        if target['section']:bound+=1
        else:external+=1
        restored[row['index']*4:row['index']*4+4]=row['word'].to_bytes(4,'little')
    fw=(ROOT/K['firmware']).read_bytes()
    need(bytes(restored)==fw[spec['start']-0x8000:spec['end']-0x8000]and
         bound==57 and external==5,'Every original vector word and complete binding count')
    undefined=sorted(name for name,s in em.items()if not s['section'])
    need(undefined==K['remaining_undefined'],'Exactly six remaining explicit entries')
    functions=[s for s in em.values()if s['info']==18 and s['section']]
    need(sum(bool(s['size'])for s in functions)==116 and sum(not s['size']for s in functions)==2,
         '116 real architectural regions plus two explicit zero-size aliases')
    # Original byte identity proves the AUIPC carrier, not its value at VMA0.
    init_offset=offsets['tsl9_ring_init_12bd0']+2
    need(e.data('.boot_code')[init_offset:init_offset+8]==fw[0x12bd2-0x8000:0x12bda-0x8000],
         'Original PC-sensitive AUIPC/ADDI port retained without substituting a pointer')
    return dict(passed=True,mode=mode,code_bytes=956,original_code_instructions=335,
                initializer_bytes=128,vector_carrier_bytes=328,total_data_bytes=456,
                nonzero_FUNC_regions=116,zero_size_FUNC_aliases=2,RELA=153,UND=undefined,
                new_code_bytes=308,new_original_instructions=102,new_native_regions=16,
                parent648B_code_and456B_data_unchanged=True,all_new_native_carriers_unchanged=True,
                all_new_code_original_VA_equal=True,all_global_local_relocation_targets_owned=True,
                newly_bound_vector=36,original_vector_word_PC=K['vector_original_word_PC'],
                original_vector_target=K['vector_original_target'],
                vector_slots_bound_to_real_code=57,vector_slots_still_external=5,
                remaining_unique_vector_entries=4,
                real_direct_IRQ_providers_resolved=['tsl9_irq_provider_18d78','tsl9_ring_insert_entry_12bc8'],
                zero_size_alias_owns_real_entry=True,conditional_frame_and_both_MRET_paths_retained=True,
                raw_PC_sensitive_AUIPC_retained=True,original_ring_table_literal_target=K['original_ring_table_literal_target'],
                final_original_address_placement_proved=False,
                resident_indirect_pointer_word=K['resident_pointer_word_address'],
                resident_pointer_identity_or_ABI_proved=False,
                length_and_extended_ID_caller_policy_proved=False,physical_MCU_or_IRQ_context_proved=False,
                component_sha256=sha(path),ELF_VMA_zero=True,executable=False,ABS_providers=0,
                no_executable_stub_added=True,target_executed=False,ISA_emulated=False,
                HOST_model_executed=False,hardware_accessed=False,network=False,
                negative_cases_executed=0,firmware_BIN_generated=False,firmware_ready=False)

def inventory(folder):
    return {p.name:dict(bytes=p.stat().st_size,sha256=sha(p))
            for p in sorted(folder.iterdir())if p.is_file()}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tool-dir',type=Path,required=True)
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument('--output',type=Path);group.add_argument('--replay',type=Path)
    a=p.parse_args();llvm=a.tool_dir.resolve()
    proof=source_proof(llvm);before=portable(inputs(llvm),llvm)
    if a.replay:
        out=a.replay.resolve();need(out.parent==HERE/'build','Owned retained output')
        saved=json.loads((out/'measurement.json').read_bytes())
        need(saved['inputs']==before and saved['source_proof']==proof,'Every retained producer input unchanged')
        for mode in('c','cpp'):
            need(saved['modes'][mode]['artifacts']==inventory(out/mode),'Complete retained normal output inventory')
            need(saved['modes'][mode]['result']==audit_component(out/mode/OUTPUT,mode),'Whole actual native component replay')
        print(json.dumps(dict(passed=True,mode='read-only-normal-CAN-RX0-IRQ-replay',source_proof=proof)))
        return
    out=a.output.resolve();need(out.parent==HERE/'build'and not out.exists(),'Create-only direct output folder')
    report=dict(schema='TSL9-CAN-RX0-IRQ-native-link-v1',inputs=before,source_proof=proof,modes={})
    for mode in('c','cpp'):
        f=out/mode;f.mkdir(parents=True);output=f/OUTPUT;commands=[]
        argv=[str(llvm/'ld.lld.exe'),'-r','--no-relax','-T',str(HERE/'joined-v1.ld'),str(parent(mode))]
        argv += [str(native(unit,mode))for unit in K['units']]
        argv += ['-o',str(output)]
        for label,command in [('link',argv),('read',[str(llvm/'llvm-objdump.exe'),'-dr','-t','-h',str(output)])]:
            result=subprocess.run(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
            (f/(label+'.log')).write_bytes(result.stdout)
            commands.append(dict(label=label,argv=command,exit=result.returncode))
            need(result.returncode==0,'Actual '+label+' failed; original log retained')
        audit=audit_component(output,mode)
        unit_results=[audit_unit(native(unit,mode),unit)for unit in K['units']]
        (f/'verification.json').write_bytes(encoded(audit))
        report['modes'][mode]=dict(result=audit,unit_results=unit_results,commands=commands,artifacts=inventory(f))
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
