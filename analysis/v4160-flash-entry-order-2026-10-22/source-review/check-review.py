#!/usr/bin/env python3
"""Read-only source/delta/receipt review, with optional actual archive replay."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

OLD='experiments/tsl9-v4160-flash-native'
NEW='experiments/tsl9-v4160-flash-entry-order'
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def case(root,slug):return next(p for p in (root/'analysis'/slug,root/'apk-analysis'/('tsl9-'+slug)) if p.is_dir())
def sealed(folder,pin):
    need(sha(folder/'seal.json')==pin,'Exact retained seal')
    for row in read(folder/'seal.json')['members']:
        p=(folder/row['path']).resolve(strict=True);p.relative_to(folder.resolve());need(sha(p)==row['sha256'] and p.stat().st_size==row['bytes'],'Sealed member '+row['path'])
def source_delta(root):
    old=root/OLD/'src';new=root/NEW/'src'
    text=(old/'flash_native.c').read_text(encoding='utf-8')
    changes=[
      ('FN_READ(0x18ef6u,FN_ADD(base,FN_K(16u)),before);\n    destination=FN_AND(destination,FN_K(0xffffff00u));','FN_READ(0x18ef6u,FN_ADD(base,FN_K(16u)),before);\n    destination=FN_ALIGN0(destination);'),
      ('FN_READ(0x18f02u,FN_ADD(base,FN_K(12u)),status);status=FN_AND(status,FN_K(1u));','FN_READ(0x18f02u,FN_ADD(base,FN_K(12u)),status);status=FN_POLL5_AND(status,1u);'),
      ('while(FN_POLL_TRUE(0x18f06u,status,1u));FN_CHECK_FLOW(); }\n','while(FN_POLL_TRUE(0x18f06u,status,1u));FN_CHECK_FLOW(); }\n    base=FN_BASE4();\n'),
      ('FN_READ(0x18f0cu,FN_ADD(base,FN_K(12u)),status);status=FN_AND(status,FN_K(2u));','FN_READ(0x18f0cu,FN_ADD(base,FN_K(12u)),status);status=FN_POLL5_AND(status,2u);'),
      ('while(FN_POLL_TRUE(0x18f10u,status,2u));FN_CHECK_FLOW(); }\n','while(FN_POLL_TRUE(0x18f10u,status,2u));FN_CHECK_FLOW(); }\n    base=FN_BASE4();\n')]
    for a,b in changes:need(text.count(a)==1,'One exact intended core delta');text=text.replace(a,b)
    need(text.encode()==(new/'flash_native.c').read_bytes(),'No other C source changes')
    text=(old/'native_io.h').read_text(encoding='utf-8')
    for a,b in [('#define FN_MASK3(v) FN_K(v)\n','#define FN_MASK3(v) FN_K(v)\n#define FN_ALIGN0(v) FN_AND((v),FN_K(0xffffff00u))\n#define FN_POLL5_AND(v,mask) FN_AND((v),FN_K(mask))\n'),('#define FN_MASK3(v) FN_FIXED_VALUE("a3",(v))\n','#define FN_MASK3(v) FN_FIXED_VALUE("a3",(v))\n#define FN_ALIGN0(v) FN_FIXED_VALUE("a0",FN_AND(FN_FIXED_VALUE("a0",(v)),FN_K(0xffffff00u)))\n#define FN_POLL5_AND(v,mask) FN_FIXED_VALUE("a5",FN_AND((v),FN_K(mask)))\n')]:
        need(text.count(a)==1,'One exact primitive insertion');text=text.replace(a,b)
    need(text.encode()==(new/'native_io.h').read_bytes(),'Only declared native/host macro insertions')
    for name in ('flash_native.h','host_io.c','host_io.h'):need((old/name).read_bytes()==(new/name).read_bytes(),'Unchanged public/provider source '+name)
    need((root/OLD/'tests/test_flash.c').read_bytes()==(root/NEW/'tests/test_flash.c').read_bytes(),'Unchanged canonical test source')
    need((root/NEW/'verify_host.py').read_bytes().replace(NEW.encode(),OLD.encode())==(root/OLD/'verify_host.py').read_bytes(),'Host guard runner changes only model path')
def effect_pins(root,here,r):
    for name,pin in r['input_pins'].items():
        normalized=name.replace('\\','/')
        if '/experiments/' in normalized:p=root/('experiments/'+normalized.split('/experiments/',1)[1])
        elif '/scripts/' in normalized:p=root/('scripts/'+normalized.split('/scripts/',1)[1])
        else:p=here/normalized.rsplit('/',1)[-1]
        need(sha(p)==pin,'Actual fresh effect source/oracle/guard pin')
def effect_archive(root,here,folder,r):
    need(read(folder/'verification.json')==r,'Actual original independent receipt')
    guard=module('entry_effect_replay_guard',root/NEW/'verify_host.py')
    need(sha(Path(r['compiler']['path']))==r['compiler']['sha256'],'Actual host compiler')
    for row in [r['positive'],*r['actually_compiled_mutants']]:
        base=folder/row['case']
        for name,pin in row['artifacts'].items():
            p=(base/name).resolve(strict=True);p.relative_to(base.resolve());need(sha(p)==pin['sha256'] and p.stat().st_size==pin['bytes'],'Actual independent artifact')
        exe=base/row['commands'][1]['argv'][0].replace('\\','/').rsplit('/',1)[-1]
        need(guard.host_executable(exe)==row['commands'][1]['host_executable_guard'],'Every retained effect executable is matching host code')
        for command in row['commands']:need(sha(base/command['log'])==command['log_sha256'],'Actual compile/run log')
        need(row['commands'][0]['exit']==0,'Actual independent compile succeeded')
        if row['mutation_file']:need(row['commands'][1]['exit']!=0 and 'REVIEW_FAIL ' in (base/'tests.log').read_text(encoding='utf-8'),'Actual independent semantic rejection')
        else:need(row['commands'][1]['exit']==0 and read(base/'tests.log')==r['positive']['result'],'Actual independent positive output')
        for p in (root/NEW/'src').glob('*'):
            if not p.is_file():continue
            expected=p.read_bytes()
            if p.name==row['mutation_file']:
                text=expected.decode();need(text.count(row['anchor'])==row['anchor_count'],'Unique actual source-control anchor');expected=text.replace(row['anchor'],row['replacement']).encode()
            need((base/'src'/p.name).read_bytes()==expected,'Actual independent source copy is exact or precisely mutated')
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',type=Path,required=True);p.add_argument('--firmware',type=Path);p.add_argument('--host-archive',type=Path);p.add_argument('--native-archive',type=Path);p.add_argument('--effects-archive',type=Path);a=p.parse_args();root=a.project_root.resolve(strict=True);here=Path(__file__).resolve().parent;r=read(here/'review.json')
    for x in r['project_inputs']:need(sha(root/x['path'])==x['sha256'],'Exact reviewed project input '+x['path'])
    for x in r['case_inputs']:need(sha(case(root,x['case'])/x['path'])==x['sha256'],'Exact reviewed case input')
    oldcase=case(root,'v4160-flash-native-2026-10-22')
    for relative,pin in [('review','173c8790e2deaad0ae6ac29bea2cabdbc8be2c13b68edefc3d5beb37c545488c'),('review-v2','028a6dd7dc7530f4befe1c1eff3343ae5fa251c9b3c1dee78f5d272f5ceab9b7')]:sealed(oldcase/relative,pin)
    for x in read(oldcase/'review/review.json')['model_inputs']:
        if x['path'].startswith(OLD+'/src/') or x['path'].startswith(OLD+'/tests/'):need(sha(root/x['path'])==x['sha256'],'Exact prior core/test preserved')
    source_delta(root);source=oldcase/'source';sealed(source,'dff9a51e3b59bbdddd150dde37614753bb3c3b440d7bde2f9402c8b6e9a2bce4')
    need(sha(here/'source-inventory.json')==r['source_inventory_sha256'] and sha(here/'component-review.json')==r['component_review_sha256'],'Exact independent source/component observations')
    source_inventory=read(here/'source-inventory.json');need(source_inventory['tail_raw']=='758f98cb8280' and len(source_inventory['original_carrier']['incoming_RELA'])==23,'Bound original tail and incoming roles')
    component=read(here/'component-review.json');need(component['passed'] and component['program']['A0_alignment_offset']==6 and len(component['raw_native_semantic_controls'])==3,'Independent actual-component early-order/tail/CFG evidence')
    cli=r['CLI_option_receipt'];need(sha(here/cli['path'])==cli['sha256'],'Selected actual explicit-path CLI test result');options=read(here/cli['path'])
    need(options['passed'] and options['runner_sha256']==sha(here.parent/'implementation/verify_native.py') and options['script_sha256']==sha(here.parent/'implementation/test_cli_options.py') and options['alternate_reference_compile_passed'] and options['same_explicit_reference_replay_passed'] and options['wrong_default_context_rejected'] and options['target_execution'] is False,'Explicit --firmware reaches compile and replay; wrong receipt context rejected')
    raw_checked=False
    if a.firmware:
        raw=a.firmware.read_bytes();need(hashlib.sha256(raw).hexdigest()==source_inventory['firmware_sha256'] and len(raw)==76800,'Exact ID2966 original')
        decoder=module('entry_review_source_decoder',source/'inspect.py');proof=read(source/'source-proof.json');need(decoder.facts(raw)==proof['ledger'],'All262B/99 original instructions')
        for x in proof['raw_negatives']:
            data=bytearray(raw);off=x['PC']-0x8000;replacement=bytes.fromhex(x['after']);need(data[off:off+len(replacement)].hex()==x['before'],'Actual source control anchor');data[off:off+len(replacement)]=replacement
            try:decoder.facts(data)
            except ValueError:pass
            else:raise ValueError('Source negative accepted')
        tail=module('entry_tail_check',here/'inspect-source.py');need(tail.tail_contract(decoder,raw)==source_inventory['tail_rows'],'Actual original live tail')
        for x in source_inventory['tail_semantic_controls']:
            changed=bytearray(raw);off=x['PC']-0x8000;changed[off:off+2]=bytes.fromhex(x['replacement'])
            try:tail.tail_contract(decoder,changed)
            except ValueError:pass
            else:raise ValueError('Original tail semantic control accepted')
        raw_checked=True
    modes={'host':set(),'native':set(),'effects':set()}
    for x in r['receipts']:
        selected=here/x['path'];need(sha(selected)==x['sha256'],'Exact actual selected result');v=read(selected);kind=x['kind'];mode=v.get('mode',v.get('language'));modes[kind].add(mode);need(v['passed'],'Actual successful verification')
        if kind=='host':
            need(v['tests']=={'passed':True,'groups':5,'cases':481,'checks':247191,'synthetic_provider':True,'RV32_execution':False} and len(v['actual_compiled_controls'])==6,'Fresh canonical host coverage/controls')
            need(v['runner_sha256']==sha(root/NEW/'verify_host.py'),'Current guarded host runner')
            need(v['source_sha256']=={p.relative_to(root/NEW).as_posix():sha(p) for d in ('src','tests') for p in (root/NEW/d).glob('*') if p.is_file()},'Current canonical compiled source/test pins')
            if a.host_archive:
                actual=a.host_archive/x['archive_path'];need(sha(actual)==x['sha256'],'Actual selected host archive receipt');module('entry_canonical_host_replay',root/NEW/'verify_host.py').replay(root,actual)
        elif kind=='native':
            c=v['checks'];need(c['allocated_function_bytes']==262 and c['instructions']==99 and c['unowned_original_program_tail_bytes']==0 and c['original_A0_memory_event_order'],'Actual100B natural component gate')
            need(c['program_contract']['bytes']==100 and c['program_contract']['known_interior_offsets']==[16,26,40,56,82],'Current branch target roles')
            retained=b''.join(bytes.fromhex(row['raw_hex']) for row in c['program_contract']['rows'])
            need(hashlib.sha256(retained).hexdigest()==next(f['sha256'] for f in component['functions'] if f['name']=='program'),'Exact retained native program bytes')
            native_decoder=module('entry_retained_decoder',source/'inspect.py');own=module('entry_retained_component_check',here/'inspect-component.py')
            need(own.program_contract(retained,native_decoder)==component['program'],'Independent retained native program semantic recheck')
            for control in component['raw_native_semantic_controls']:
                changed=bytearray(retained);changed[control['offset']]^=control['xor']
                try:own.program_contract(changed,native_decoder)
                except ValueError:pass
                else:raise ValueError('Independent native byte control accepted')
            need(v['runner_sha256']==sha(here.parent/'implementation/verify_native.py') and v['artifacts']['COMPONENT-ONLY-NOT-FIRMWARE.elf']['sha256']==component['new_component_sha256'],'Final native runner and exact independently inspected component')
            need(all(c[k] is False for k in ('full_instruction_boundary_equivalence','pointwise_async_equivalence','nonreturn_physical_GPR_prefix_equivalence','full_image_integration','firmware_BIN_produced','OTA_ready')),'Required unresolved gates remain false')
            if a.native_archive:
                actual=a.native_archive/x['archive_path'];need(sha(actual)==x['sha256'],'Actual selected native archive receipt');module('entry_formal_native_replay',here.parent/'implementation/verify_native.py').replay(root,actual,firmware=a.firmware)
        else:
            need(v['positive']['result']=={'passed':True,'groups':1,'cases':12,'checks':8964,'synthetic_effects_only':True} and v['actual_mutants_rejected']==12 and v['host_executables_guarded']==13,'Fresh independent oracle and twelve compiled controls')
            need(v['oracle_sha256']=='d2387b7983052b2b3b863223eaf3873e00435a1bd03b5833ba31a4c7ad569705','Immutable original oracle bytes');effect_pins(root,here,v)
            for row in [v['positive'],*v['actually_compiled_mutants']]:need(row['commands'][1]['host_executable_guard']['sha256']==row['executable_sha256'],'Actual guarded independent executable')
            need(any(row['mutation_file']=='native_io.h' and 'FN_ALIGN0' in row['anchor'] for row in v['actually_compiled_mutants']),'Alignment control targets the new host macro')
            if a.effects_archive:
                actual=a.effects_archive/x['archive_path'];need(sha(actual/'verification.json')==x['sha256'],'Actual selected independent archive receipt');effect_archive(root,here,actual,v)
    need(all(v=={'c','cpp'} for v in modes.values()),'Both modes for all three evidence classes')
    if (here/'seal.json').is_file():sealed(here,sha(here/'seal.json'))
    print(json.dumps({'passed':True,'raw_source_and20controls_rechecked':raw_checked,'actual_archived_artifacts_replayed':any((a.host_archive,a.native_archive,a.effects_archive)),'fresh_independent_cases_per_language':12,'fresh_independent_checks_per_language':8964,'fresh_independent_compiled_controls':24,'natural_component_bytes':262,'program_bytes':100,'full_image_integration':False,'target_execution':False,'OTA_ready':False},sort_keys=True))
if __name__=='__main__':main()
