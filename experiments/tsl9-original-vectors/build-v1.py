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
S=json.loads((HERE/'spec-v1.json').read_bytes())
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
    e=elf(path)
    need(e.header[0]==1 and not e.program_headers,'Actual data ET_REL without loading headers')
    allocated=[s for s in e.sections if s['flags']&2 and s['size']]
    need(len(allocated)==1,'Only actual readonly vector carrier allocated')
    sec=allocated[0]
    need(sec['name']==S['section'] and sec['type']==1 and sec['flags']==2 and
         sec['size']==S['bytes'] and sec['address']==0,'Exact selected328B data allocation')
    need(not any(s['info']&15==2 and s['section']for s in e.symbols),'No executable functions or fake handler stubs')
    global_symbols=[s for s in e.symbols if s['info']>>4]
    need(all(s['section']!=0xfff1 for s in global_symbols),'No ABS substitutes')
    gm={s['name']:s for s in global_symbols}
    need(len(gm)==len(global_symbols),'Unique global symbols')
    expected_names={row['symbol']for row in S['entries']if row['symbol']}
    need(set(gm)==expected_names|{S['symbol']},'Exact real data and external address inventory')
    owner=gm[S['symbol']]
    need(owner['info']==17 and owner['other']==0 and owner['size']==328 and
         owner['value']==0 and owner['section']==sec['index'],'Actual global328B OBJECT owner')
    for name in expected_names:
        symbol=gm[name]
        need(symbol['info']in(16,18) and symbol['other']==0 and symbol['section']==0 and
             symbol['size']==0 and symbol['value']==0,'Unresolved code-address symbol '+name)
    raw=e.data(sec)
    fw=(ROOT/S['firmware']).read_bytes()
    original=fw[S['start']-0x8000:S['end']-0x8000]
    need(len(original)==328 and hashlib.sha256(original).hexdigest()==S['carrier_sha256'],'Pinned original selected carrier')
    need(len(e.relocations)==62 and all(r['section']==sec['index']for r in e.relocations),'All62 typed data references')
    rels={r['offset']:r for r in e.relocations}
    need(len(rels)==len(e.relocations),'Unique pointer slots')
    restored=bytearray(raw)
    for row in S['entries']:
        at=row['index']*4
        need(int.from_bytes(original[at:at+4],'little')==row['word'],'Each literal source word matches firmware')
        if row['symbol']:
            need(int(row['symbol'].rsplit('_',1)[1],16)==row['word'],'Each named original destination')
            rel=rels.get(at)
            need(rel and rel['type']==1 and rel['addend']==0 and
                 e.symbols[rel['symbol']]['name']==row['symbol'],'Exact R_RISCV_32 target for original slot')
            need(raw[at:at+4]==bytes(4),'Normal zero RELA carrier bits')
            restored[at:at+4]=row['word'].to_bytes(4,'little')
        else:
            need(at not in rels and raw[at:at+4]==bytes(4),'Original null/padding word remains zero without relocation')
    need(bytes(restored)==original,'Every vector-carrier byte original-equal after data-only R_RISCV_32 encoding')
    return dict(passed=True,allocated_bytes=328,OBJECT=1,FUNC=0,RELA=62,UND=61,
                R_RISCV_32=62,null_words=20,object_sha256=sha(path),
                all_words_original_equal_after_data_only_encoding=True,
                all_relocation_slots_types_addends_and_targets_exact=True,
                ABS_providers=0,hardware_IRQ_count_or_table_extent_proved=False,
                stored_function_addresses_prove_C_ABI=False,target_executed=False,
                ISA_emulated=False,HOST_model_executed=False,hardware_accessed=False,
                network=False,negative_cases_executed=0,firmware_BIN_generated=False,
                firmware_ready=False)

def complete_projection_equal(left,right):
    a,b=elf(left),elf(right)
    need([s['name']for s in a.sections]==[s['name']for s in b.sections],'Complete same section inventory')
    need(all(a.data(s)==b.data(b.section(s['name']))for s in a.sections
             if s['name']and s['name']not in('.symtab','.strtab')),'Every nonsymbol carrier byte equal')
    need([s for s in a.symbols if s['info']&15!=4]==
         [s for s in b.symbols if s['info']&15!=4],'Every non-FILE symbol record equal')
    need([s['name']for s in a.symbols if s['info']&15==4]==['boot_vectors.v1.c']and
         [s['name']for s in b.symbols if s['info']&15==4]==['boot_vectors.c'],'Only the known local FILE identity changes')
    return True

def inputs(llvm,variants):
    paths=[Path(__file__),HERE/'spec-v1.json',SHARED,ROOT/S['firmware'],
           ROOT/S['reader'],ROOT/S['curation_checker'],llvm.parent/'lib/clang/18/include/stdint.h']
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
    for key in ('firmware','reader','curation_checker'):
        need(sha(ROOT/S[key])==S[key+'_sha256'],'Pinned '+key)
    for v in variants:need(sha(source_path(v))==S['source_sha256'],'Exact unchanged '+v+' C source')
    for name,pin in S['tools'].items():need(sha(llvm/name)==pin,'Pinned local '+name)
    need(sha(llvm.parent/'lib/clang/18/include/stdint.h')==S['stdint_sha256'],'Pinned header')
    C=runpy.run_path(str(ROOT/S['curation_checker']))
    need(S['flags']=={m:C['flags']({'profile':S['profile']},m)for m in('c','cpp')},'Exact existing compiler profile')
    before=portable(inputs(llvm,variants),llvm)
    if saved:
        out=a.replay.resolve()
        need(out.parent==HERE/'build'and saved['inputs']==before,'Owned retained artifact input set')
        for mode in ('c','cpp'):
            for variant in variants:
                f=out/mode/variant
                job=saved['modes'][mode][variant]
                need(job['artifacts']==inventory(f),'Complete retained native output inventory')
                need(job['result']==audit_object(f/'unit.o'),'Actual normal vector object replay')
                need(job['dependencies']==portable(dependencies(f,variant,llvm),llvm),'Complete unchanged compiler dependencies')
            if len(variants)==2:
                complete_projection_equal(out/mode/'origin/unit.o',out/mode/'curated/unit.o')
        print(json.dumps(dict(passed=True,mode='read-only-normal-vector-replay',variants=variants,
                              languages=['c','cpp'],target_executed=False)))
        return
    need(a.trial and Path(a.trial).name==a.trial,'Single owned trial name')
    out=HERE/'build'/a.trial
    need(not out.exists(),'Create-only output folder')
    report=dict(schema='TSL9-original-vector-data-native-build-v1',inputs=before,variants=variants,modes={})
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
                (f/(label+'.log')).write_bytes(result.stdout)
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
    (out/'measurement.json').write_bytes(encoded(report))

if __name__=='__main__':
    try:main()
    except (ValueError,OSError,subprocess.SubprocessError)as error:
        message=str(error)
        for path,token in [(ROOT,'$'+'{PROJECT_ROOT}'),(Path.home(),'$'+'{USERPROFILE}')]:
            message=message.replace(str(path),token).replace(path.as_posix(),token)
        print('FAIL: '+message,file=sys.stderr);sys.exit(1)
