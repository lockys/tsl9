#!/usr/bin/env python3
"""Compile original LLE C/C++ regions and inspect actual objects, never execute."""
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
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
need(sha(SHARED)==SHARED_SHA,'Frozen portable native-artifact helper')
B=runpy.run_path(str(SHARED))
portable,encoded=B['portable'],B['encoded']

def elf(path):return runpy.run_path(str(ROOT/S['reader']))['ELF'](path)

def audit_object(path):
    e=elf(path)
    need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual RISC-V ET_REL')
    globals_=[s for s in e.symbols if s['info']>>4]
    gm={s['name']:s for s in globals_}
    need(len(gm)==len(globals_)and set(gm)=={r['name']for r in S['regions']},'Only three genuine original region definitions')
    need(not e.relocations,'No hidden direct provider or relocation')
    fw=(ROOT/S['firmware']).read_bytes()
    original=fw[S['start']-0x8000:S['end']-0x8000]
    need(len(original)==134 and hashlib.sha256(original).hexdigest()==S['original_sha256'],'Pinned complete original134B')
    owners=set();pieces=[];count=0
    for region in S['regions']:
        f=gm[region['name']]
        need(f['info']==18 and f['other']==0 and f['value']==0 and f['size']==region['bytes'],
             'Actual full-size original region '+region['name'])
        s=e.sections[f['section']]
        need(s['name']=='.text.'+f['name']and s['flags']==6 and s['type']==1 and
             s['address']==0 and s['size']==f['size'],'Exact region allocation')
        need(s['index']not in owners,'Distinct code owner');owners.add(s['index'])
        raw=e.data(s);expected=fw[region['start']-0x8000:region['end']-0x8000]
        need(hashlib.sha256(expected).hexdigest()==region['original_sha256']and raw==expected,
             'Whole original region bytes equal')
        at=0
        while at<len(raw):
            width=4 if raw[at]&3==3 else 2
            need(at+width<=len(raw),'Whole recorded instruction')
            at+=width;count+=1
        pieces.append(raw)
    need(b''.join(pieces)==original and count==64,'Complete original134B64i source-order projection')
    need({s['index']for s in e.sections if s['flags']&2 and s['size']}==owners,'Every allocated native byte owned')
    middle=pieces[1]
    need(len(middle)==10 and middle[-4:].hex()==S['indirect_call_bytes'],'Original full-width indirect call retained')
    need(pieces[-1][-4:].hex()=='73002030','Original final MRET retained')
    need(fw[0x851e-0x8000:0x8520-0x8000].hex()==S['trailing_data']['bytes_hex'],
         'Two original trailing zero bytes remain distinct from compiled code')
    return dict(passed=True,code_bytes=134,instructions=64,FUNC=3,UND=0,RELA=0,
                native_object_sha256=sha(path),complete_original_bytes_equal=True,
                frame_bytes=128,saved_and_loaded_register_count=29,GP_saved=False,
                callback_word_address='then-live GP+384',full_width_JALR_retained=True,
                then_live_SP_exit_and_MRET_retained=True,trailing_zero_data_compiled_as_code=False,
                original_callback_identity_or_IRQ_ABI_proved=False,
                target_executed=False,HOST_model_executed=False,ISA_emulated=False,
                hardware_accessed=False,network=False,negative_cases_executed=0,
                firmware_BIN_generated=False,firmware_ready=False)

def inputs(llvm):
    paths=[Path(__file__),HERE/'spec-v1.json',SHARED,ROOT/S['source'],ROOT/S['firmware'],
           ROOT/S['reader'],ROOT/S['curation_checker'],llvm.parent/'lib/clang/18/include/stdint.h']
    paths += [llvm/name for name in S['tools']]
    return {str(p):dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(set(paths))}
def inventory(folder):
    return {p.name:dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(folder.iterdir())if p.is_file()}
def dependencies(folder,llvm):
    C=runpy.run_path(str(ROOT/S['curation_checker']))
    return C['dependencies'](folder,'origin',llvm.parent/'lib/clang/18')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tool-dir',type=Path,required=True)
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument('--trial');group.add_argument('--replay',type=Path)
    a=p.parse_args();llvm=a.tool_dir.resolve()
    for key in('source','firmware','reader','curation_checker'):
        need(sha(ROOT/S[key])==S[key+'_sha256'],'Pinned '+key)
    for name,pin in S['tools'].items():need(sha(llvm/name)==pin,'Pinned local '+name)
    need(sha(llvm.parent/'lib/clang/18/include/stdint.h')==S['stdint_sha256'],'Pinned compiler header')
    C=runpy.run_path(str(ROOT/S['curation_checker']))
    need(S['flags']=={m:C['flags']({'profile':S['profile']},m)for m in('c','cpp')},'Exact existing native compiler profile')
    before=portable(inputs(llvm),llvm)
    if a.replay:
        out=a.replay.resolve();need(out.parent==HERE/'build','Owned retained native trial')
        saved=json.loads((out/'measurement.json').read_bytes())
        need(saved['inputs']==before,'Every actual native producer input unchanged')
        for mode in('c','cpp'):
            f=out/mode
            need(saved['modes'][mode]['artifacts']==inventory(f),'Whole retained native output inventory')
            need(saved['modes'][mode]['result']==audit_object(f/'unit.o'),'Actual original-code native replay')
            need(saved['modes'][mode]['dependencies']==portable(dependencies(f,llvm),llvm),'All compiler dependencies unchanged')
        print(json.dumps(dict(passed=True,mode='read-only-normal-LLE-replay',languages=['c','cpp'],target_executed=False)))
        return
    need(a.trial and Path(a.trial).name==a.trial,'Single owned trial name')
    out=HERE/'build'/a.trial;need(not out.exists(),'Create-only trial folder')
    report=dict(schema='TSL9-original-LLE-native-build-v1',inputs=before,modes={})
    for mode in('c','cpp'):
        f=out/mode;f.mkdir(parents=True);commands=[]
        recipes=[('compile',[str(llvm/'clang.exe')]+S['flags'][mode]+
                  ['-MD','-MF',str(f/'unit.d'),'-MT','unit.o','-c',str(ROOT/S['source']),'-o',str(f/'unit.o')]),
                 ('read',[str(llvm/'llvm-objdump.exe'),'-dr','-t','-h',str(f/'unit.o')])]
        for label,argv in recipes:
            result=subprocess.run(argv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
            (f/(label+'.log')).write_bytes(result.stdout)
            commands.append(dict(label=label,argv=argv,exit=result.returncode))
            need(result.returncode==0,'Actual '+label+' failed; original log retained')
        facts=audit_object(f/'unit.o')
        report['modes'][mode]=dict(result=facts,commands=commands,
                                  dependencies=portable(dependencies(f,llvm),llvm),artifacts=inventory(f))
        print(json.dumps(dict(mode=mode,**facts)))
    need(before==portable(inputs(llvm),llvm),'Inputs unchanged during actual normal compilation')
    (out/'measurement.json').write_bytes(encoded(portable(report,llvm)))

if __name__=='__main__':
    try:main()
    except(ValueError,OSError,subprocess.SubprocessError)as error:
        message=str(error)
        for path,token in[(ROOT,'$'+'{PROJECT_ROOT}'),(Path.home(),'$'+'{USERPROFILE}')]:
            message=message.replace(str(path),token).replace(path.as_posix(),token)
        print('FAIL: '+message,file=sys.stderr);sys.exit(1)
