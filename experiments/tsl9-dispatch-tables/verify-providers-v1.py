#!/usr/bin/env python3
"""Positive static audits of actual C/C++ dispatch code and signed-relative tables."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys
import subprocess
from collections import Counter
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
S=json.loads((HERE/'spec-v1.json').read_bytes())
def need(ok,message):
    if not ok:raise ValueError(message)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
for key in ('code_checker','feature_checker','feature_builder','feature_spec','code_checker_spec','reader','shared_helper'):
    need(sha(ROOT/S[key])==S['pins'][S[key]],'Frozen positive helper/provenance input')
V=runpy.run_path(str(ROOT/S['code_checker']))
F=runpy.run_path(str(ROOT/S['feature_checker']),run_name='positive_static_library')
E=V['E']
portable,encoded=V['portable'],V['encoded']
need(F['S']['firmware_sha256']==S['firmware_sha256']and F['S']['tables']==S['tables'],'Exact original two-table metadata')
need(F['S']['reader_sha256']=='112e90f7a1786bd1e388718e80086ba937035364d926c89cd5875eba68ce543a','Frozen feature ELF reader')

def pins(llvm):
    for path,pin in S['pins'].items():need(sha(ROOT/path)==pin,'Pinned actual C/C++ provider input')
    need(sha(ROOT/S['firmware'])==S['firmware_sha256'],'Original firmware identity')
    for name,pin in S['tools'].items():need(sha(llvm/name)==pin,'Pinned local link/read tool')

def selected_regions(provider):
    return [r for r in provider['regions']if r['name']not in provider.get('omitted_names',[])]

def object_path(provider,mode,folder=None):
    return folder/mode/'unit.o'if provider.get('omitted_names')else ROOT/provider['objects'][mode]

def dependencies(folder,llvm):
    C=runpy.run_path(str(ROOT/S['curation_checker']))
    return portable(C['dependencies'](folder,'origin',llvm.parent/'lib/clang/18'),llvm)

def source_selection(llvm):
    result=runpy.run_path(str(ROOT/S['source_deriver']))['derive']()
    need(result['source'].encode()==(ROOT/S['selected_source']).read_bytes(),'Exact three-definition C selection')
    provider=next(p for p in S['providers']if p.get('omitted_names'))
    need(sorted(x['name']for x in result['omitted_definitions'])==sorted(provider['omitted_names']),'Only three genuine clock definitions omitted')
    C=runpy.run_path(str(ROOT/S['curation_checker']))
    m=json.loads((ROOT/S['manifest']).read_bytes());u=next(x for x in m['native_units']if x['name']==provider['unit'])
    need(S['selected_flags']=={mode:C['flags'](u,mode)for mode in ('c','cpp')},'Unchanged actual compiler profile')
    need(sha(llvm.parent/'lib/clang/18/include/stdint.h')==S['stdint_sha256'],'Pinned compiler header')
    fw=(ROOT/S['firmware']).read_bytes()
    for mode in ('c','cpp'):
        parent=E(ROOT/S['parent_component']/mode/S['parent_object'])
        full=E(ROOT/provider['objects'][mode])
        for region in provider['regions']:
            if region['name']not in provider['omitted_names']:continue
            a=next(x for x in parent.symbols if x['name']==region['name'])
            b=next(x for x in full.symbols if x['name']==region['name'])
            raw=parent.data(parent.sections[a['section']])[a['value']:a['value']+a['size']]
            need(a['info']==b['info']==18 and a['size']==b['size']==region['bytes']and
                 raw==full.data(full.sections[b['section']])==
                 fw[region['start']-0x8000:region['end']-0x8000],'Parent owns the exact original clock body')
            need(not any(r['section']==a['section']and a['value']<=r['offset']<a['value']+a['size']
                         for r in parent.relocations),'Omitted clock body has no hidden typed references')
    return result

def projected_bodies_equal(full,selected,regions):
    a,b=E(full),E(selected)
    am={x['name']:x for x in a.symbols if x['info']>>4}
    bm={x['name']:x for x in b.symbols if x['info']>>4}
    for region in regions:
        x,y=am[region['name']],bm[region['name']]
        need(a.data(a.sections[x['section']])==b.data(b.sections[y['section']]),'Every retained actual compiler body unchanged')
        def refs(e,f):
            return Counter((r['offset'],r['type'],r['addend'],e.symbols[r['symbol']]['name'])
                           for r in e.relocations if r['section']==f['section'])
        need(refs(a,x)==refs(b,y),'Every retained typed reference unchanged')
    return True


def audit_feature(path,provider):
    unit=next(x for x in F['S']['units']if x['name']==provider['unit'])
    need({r['name']:(r['start'],r['bytes'])for r in provider['regions']}==
         {name:(pc,size)for name,pc,size in unit['definitions']},'Exact original code definition metadata')
    fw=(ROOT/S['firmware']).read_bytes()
    e,code=F['native'](Path(path).read_bytes(),unit,fw)
    count=0
    for raw in code.values():
        off=0
        while off<len(raw):
            width=4 if raw[off]&3==3 else 2
            need(off+width<=len(raw),'Whole original instruction');off+=width;count+=1
    table_facts=[]
    all_defs={name:(pc,size)for name,pc,size in
              [row for u in F['S']['units']for row in u['definitions']]}
    by_pc={pc:name for name,(pc,size)in all_defs.items()}
    for table in provider['tables']:
        sec,original=F['table_gate'](e,table,table['section'])
        need(hashlib.sha256(original).hexdigest()==table['sha256']and
             original==fw[table['address']-0x8000:table['address']-0x8000+table['bytes']],
             'Every original signed-relative table word')
        targets=[dict(index=i,original_PC=pc,symbol=by_pc[pc],genuine_region_bytes=all_defs[by_pc[pc]][1])
                 for i,pc in enumerate(table['targets'])]
        table_facts.append(dict(name=table['name'],original_address=table['address'],bytes=table['bytes'],
            original_sha256=table['sha256'],bindings=targets,ADD32_and_SUB32_references=2*len(targets),
            every_target_is_genuine_defined_source_region=True,canonical_symbolic_carrier_zero=True))
    return dict(passed=True,code_bytes=sum(len(raw)for raw in code.values()),instructions=count,
        FUNC=len(code),RELA=len(e.relocations),
        UND=sorted(x['name']for x in e.symbols if x['info']>>4 and not x['section']),
        table_bytes=sum(x['bytes']for x in table_facts),tables=table_facts,
        all_original_code_and_table_bytes_equal_after_static_encoding=True,
        native_object_sha256=sha(path),positive_native_and_table_gate_only=True,
        legacy_verify_or_negative_functions_called=False,target_executed=False,
        HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False,
        firmware_BIN_generated=False)

def mode_audit(mode,folder,llvm):
    result={}
    for provider in S['providers']:
        path=object_path(provider,mode,folder)
        if provider['kind']=='feature':
            facts=audit_feature(path,provider)
        else:
            full=V['audit_object'](ROOT/provider['objects'][mode],provider['regions'],provider['undefined'])
            if provider.get('omitted_names'):
                facts=V['audit_object'](path,selected_regions(provider),provider['selected_undefined'])
                projected_bodies_equal(ROOT/provider['objects'][mode],path,selected_regions(provider))
                facts.update(full_source_audit=full,C_selection_dependencies=dependencies(folder/mode,llvm))
            else:facts=full
            facts.update(table_bytes=0,tables=[])
        need(facts['UND']==provider.get('selected_undefined',provider['undefined']),'Every actual source dependency explicit')
        result[provider['unit']]=facts
    total=sum(x['code_bytes']for x in result.values());data=sum(x['table_bytes']for x in result.values())
    need(total==2736 and data==60 and sum(x['FUNC']for x in result.values())==269,'Complete code/table source scope')
    defs={r['name']for r in S['all_selected_regions']}
    need(len(defs)==269,'No duplicate selected genuine body')
    parent=E(ROOT/S['parent_component']/mode/S['parent_object'])
    parent_defs={x['name']for x in parent.symbols if x['info']>>4 and x['section']}
    need(not(defs&parent_defs),'No duplicate parent/provider body')
    und={name for facts in result.values()for name in facts['UND']}
    table_bindings=[b for facts in result.values()for table in facts['tables']for b in table['bindings']]
    need(len(table_bindings)==15 and all(b['symbol']in defs for b in table_bindings),'All15 table bindings have genuine selected bodies')
    return dict(jobs=result,selected_bytes=total,selected_data_bytes=data,
        selected_instructions=sum(x['instructions']for x in result.values()),selected_FUNC=269,
        selected_RELA=sum(x['RELA']for x in result.values()),
        remaining_new_provider_gaps=sorted(und-defs-parent_defs),table_bindings=15,
        original_table_words_verified=True,all_table_targets_source_defined=True)

def inventory(folder):
    return {p.name:dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(folder.iterdir())if p.is_file()}

def audit(folder,llvm):
    pins(llvm);source_selection(llvm)
    return {mode:dict(result=mode_audit(mode,folder,llvm),artifacts=inventory(folder/mode))for mode in ('c','cpp')}

def inputs(llvm):
    paths=[Path(__file__),HERE/'spec-v1.json',ROOT/S['firmware'],llvm.parent/'lib/clang/18/include/stdint.h']
    paths += [ROOT/path for path in S['pins']]
    paths += [llvm/name for name in S['tools']]
    return {str(p):dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(set(paths))}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True)
    group=p.add_mutually_exclusive_group(required=True);group.add_argument('--output',type=Path);group.add_argument('--replay',type=Path)
    a=p.parse_args();llvm=a.tool_dir.resolve();pins(llvm);before=portable(inputs(llvm),llvm)
    if a.replay:
        out=a.replay.resolve();need(out.parent==HERE/'build','Owned retained provider receipt')
        saved=json.loads((out/'measurement.json').read_bytes())
        need(saved['inputs']==before and saved['modes']==audit(out,llvm),'Complete actual code/table replay')
        print(json.dumps(dict(passed=True,mode='read-only-code-and-table-provider-replay',code_bytes=2736,table_bytes=60,target_executed=False)));return
    out=a.output.resolve();need(out.parent==HERE/'build'and not out.exists(),'Create-only owned native audit')
    source_selection(llvm)
    for mode in ('c','cpp'):
        folder=out/mode;folder.mkdir(parents=True)
        cmd=[str(llvm/'clang.exe')]+S['selected_flags'][mode]+[
            '-MD','-MF',str(folder/'unit.d'),'-MT','unit.o','-c',str(ROOT/S['selected_source']),'-o',str(folder/'unit.o')]
        proc=subprocess.run(cmd,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
        (folder/'compile.log').write_bytes(proc.stdout)
        need(proc.returncode==0,'Actual unchanged-body C selection compile failed; log retained')
        facts=mode_audit(mode,out,llvm);(folder/'verification.json').write_bytes(encoded(facts))
    result=audit(out,llvm)
    need(before==portable(inputs(llvm),llvm),'All actual inputs unchanged during static audit')
    (out/'measurement.json').write_bytes(encoded(portable(dict(
        schema='TSL9-dispatch-code-tables-native-audit-v1',inputs=before,modes=result,
        original_bytes_copied_to_executable=False,target_executed=False,network=False),llvm)))
    print(json.dumps(dict(passed=True,modes={mode:{k:v for k,v in job['result'].items()if k not in ('jobs','remaining_new_provider_gaps')}|
                         dict(remaining_new_provider_gaps=len(job['result']['remaining_new_provider_gaps']))
                         for mode,job in result.items()})))
if __name__=='__main__':
    try:main()
    except Exception as error:
        print(json.dumps(dict(passed=False,error=str(error))),file=sys.stderr);raise SystemExit(1)
