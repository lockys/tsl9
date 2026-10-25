#!/usr/bin/env python3
"""Compile real C/C++ pointer data and inspect typed ELF relocations, never execute."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
S=json.loads((HERE/'spec-v2.json').read_bytes())
SHARED=ROOT/'experiments/tsl9-original-startup/build-v1.py'
SHARED_SHA='1f6e3673c24a5d85c62d55ec8d8390b80225577010d81c8aba5c4b6750e208b5'
def need(ok,message):
    if not ok:raise ValueError(message)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
need(sha(SHARED)==SHARED_SHA,'Unchanged normal-artifact helper')
B=runpy.run_path(str(SHARED))
portable=B['portable']
encoded=B['encoded']

def elf(path):
    return runpy.run_path(str(ROOT/S['reader']))['ELF'](path)

def source_path(variant):
    return ROOT/S['source' if variant=='origin' else 'curated_source']

def dependencies(folder,variant,llvm):
    C=runpy.run_path(str(ROOT/S['curation_checker']))
    return C['dependencies'](folder,variant,llvm.parent/'lib/clang/18')

def audit_object(path):
    return runpy.run_path(str(ROOT/S['standalone_verifier']),run_name='readonly_data_audit')['audit_object'](path)

def complete_projection_equal(left,right):
    a,b=elf(left),elf(right)
    need([s['name']for s in a.sections]==[s['name']for s in b.sections],'Complete same section inventory')
    need(all(a.data(s)==b.data(b.section(s['name']))for s in a.sections
             if s['name']and s['name']not in('.symtab','.strtab')),'Every nonsymbol carrier byte equal')
    need([s for s in a.symbols if s['info']&15!=4]==
         [s for s in b.symbols if s['info']&15!=4],'Every non-FILE symbol record equal')
    need([s['name']for s in a.symbols if s['info']&15==4]==['callback_prefix_data.v1.c']and
         [s['name']for s in b.symbols if s['info']&15==4]==['callback_prefix_data.c'],'Only the known local FILE identity changes')
    return True

def inputs(llvm,variants):
    paths=[Path(__file__),HERE/'spec-v2.json',SHARED,ROOT/S['firmware'],
           ROOT/S['reader'],ROOT/S['curation_checker'],ROOT/S['evidence'],ROOT/S['standalone_verifier'],llvm.parent/'lib/clang/18/include/stdint.h']
    paths += [ROOT/p for p in S['support_inputs']]
    paths += [source_path(v)for v in variants]
    paths += [llvm/n for n in S['tools']]
    return {str(p):dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(set(paths))}

def inventory(folder):
    return {p.name:dict(bytes=p.stat().st_size,sha256=sha(p))
            for p in sorted(folder.iterdir())if p.is_file()}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tool-dir',type=Path,required=True)
    p.add_argument('--include-curated',action='store_true')
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument('--trial')
    group.add_argument('--replay',type=Path)
    a=p.parse_args();llvm=a.tool_dir.resolve()
    saved=json.loads((a.replay/'measurement.json').read_bytes())if a.replay else None
    variants=saved['variants']if saved else ['origin','curated']if a.include_curated else ['origin']
    need(variants in (['origin'],['origin','curated']),'Known explicit source scope')
    for key in ('firmware','reader','curation_checker','evidence','standalone_verifier'):
        need(sha(ROOT/S[key])==S[key+'_sha256'],'Pinned '+key)
    for p,pin in S['support_inputs'].items():need(sha(ROOT/p)==pin,'Pinned DATA derivation support input')
    for v in variants:need(sha(source_path(v))==S['source_sha256'],'Exact unchanged '+v+' C source')
    for name,pin in S['tools'].items():need(sha(llvm/name)==pin,'Pinned local '+name)
    need(sha(llvm.parent/'lib/clang/18/include/stdint.h')==S['stdint_sha256'],'Pinned header')
    C=runpy.run_path(str(ROOT/S['curation_checker']))
    need(S['flags']=={m:C['flags']({'profile':S['profile']},m)for m in('c','cpp')},'Exact existing compiler profile')
    derived=runpy.run_path(str(ROOT/S['audit']),run_name='readonly_static_audit')['audit']()
    need(derived['passed']and derived['selected_argument_bytes']==109,'Actual original fixed-length argument windows')
    before=portable(inputs(llvm,variants),llvm)
    if saved:
        out=a.replay.resolve()
        need(out.parent==HERE/'build'and saved['inputs']==before,'Owned retained artifact input set')
        for mode in ('c','cpp'):
            for variant in variants:
                f=out/mode/variant
                job=saved['modes'][mode][variant]
                need(job['artifacts']==inventory(f),'Complete retained native output inventory')
                need(job['result']==audit_object(f/'unit.o'),'Actual typed relative-table object replay')
                need(job['dependencies']==portable(dependencies(f,variant,llvm),llvm),'Complete unchanged compiler dependencies')
            if len(variants)==2:
                complete_projection_equal(out/mode/'origin/unit.o',out/mode/'curated/unit.o')
        print(json.dumps(dict(passed=True,mode='read-only-callback-prefix-data-replay',variants=variants,
                              languages=['c','cpp'],target_executed=False)))
        return
    need(a.trial and Path(a.trial).name==a.trial,'Single owned trial name')
    out=HERE/'build'/a.trial
    need(not out.exists(),'Create-only output folder')
    report=dict(schema='TSL9-callback-prefix-data-native-build-v2',inputs=before,variants=variants,modes={})
    for mode in ('c','cpp'):
        report['modes'][mode]={}
        for variant in variants:
            f=out/mode/variant;f.mkdir(parents=True)
            commands=[]
            recipes=[
                ('compile',[str(llvm/'clang.exe')]+S['flags'][mode]+
                 ['-MD','-MF',str(f/'unit.d'),'-MT','unit.o','-c',str(source_path(variant)),'-o',str(f/'unit.o')]),
                ('read',[str(llvm/'llvm-objdump.exe'),'-dr','-t','-h',str(f/'unit.o')])]
            for label,argv in recipes:
                result=subprocess.run(argv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
                (f/(label+'.log')).write_bytes(portable(result.stdout.decode('utf8','replace'),llvm).encode('utf8'))
                commands.append(dict(label=label,argv=argv,exit=result.returncode))
                need(result.returncode==0,'Actual '+label+' failed; original log retained')
            # The frozen dependency reader expects compile.log, which is retained above.
            deps=dependencies(f,variant,llvm);facts=audit_object(f/'unit.o')
            report['modes'][mode][variant]=dict(result=facts,commands=commands,
                dependencies=portable(deps,llvm),artifacts=inventory(f))
            print(json.dumps(dict(mode=mode,variant=variant,**facts)))
        if len(variants)==2:
            need(complete_projection_equal(out/mode/'origin/unit.o',out/mode/'curated/unit.o'),
                 'Actual original/curated complete projection equality')
    need(before==portable(inputs(llvm,variants),llvm),'Actual inputs unchanged during native compilation')
    (out/'measurement.json').write_bytes(encoded(portable(report,llvm)))

if __name__=='__main__':
    try:main()
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'$'+'{PROJECT_ROOT}'),(Path.home(),'$'+'{USERPROFILE}')]:
            message=message.replace(str(path),token).replace(path.as_posix(),token)
        print('FAIL: '+message,file=sys.stderr);sys.exit(1)
