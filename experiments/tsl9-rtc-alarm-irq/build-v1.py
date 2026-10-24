#!/usr/bin/env python3
"""Compile original RTC context C/C++ regions; inspect objects without execution."""
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
    globals_=[s for s in e.symbols if s['info']>>4];gm={s['name']:s for s in globals_}
    need(len(gm)==len(globals_)and set(gm)=={r['name']for r in S['regions']},'Only five real original definitions')
    fw=(ROOT/S['firmware']).read_bytes();owners=set();count=0;total=0;noncontrol=0
    regions={r['name']:r for r in S['regions']}
    expected=[]
    for row in S['controls']:
        owner=gm[row['owner']]
        expected.append((owner['section'],row['offset'],17,0,row['target']))
    actual=[(r['section'],r['offset'],r['type'],r['addend'],e.symbols[r['symbol']]['name'])for r in e.relocations]
    need(sorted(actual)==sorted(expected),'Only four exact original typed direct references')
    for region in S['regions']:
        f=gm[region['name']];sec=e.sections[f['section']]
        need(f['info']==18 and f['other']==0 and f['value']==0 and f['size']==region['bytes'],'Full genuine code region')
        need(sec['name']=='.text.'+f['name']and sec['flags']==6 and sec['type']==1 and sec['address']==0 and sec['size']==f['size'],'Exact code allocation')
        need(sec['index']not in owners,'Unique region owner');owners.add(sec['index'])
        raw=e.data(sec);original=fw[region['start']-0x8000:region['end']-0x8000]
        need(hashlib.sha256(original).hexdigest()==region['original_sha256'],'Pinned original region')
        normalized=bytearray(raw);local=[x for x in S['controls']if x['owner']==region['name']]
        for edge in local:
            off=edge['offset'];word=int.from_bytes(raw[off:off+4],'little')
            need(word==0x6f|(edge['rd']<<7),'Exact no-immediate native JAL port')
            pc=region['start']+off;target=regions[edge['target']]['start'];delta=target-pc
            need(delta%2==0 and -(1<<20)<=delta<(1<<20),'Representable original direct edge')
            bits=delta&0x1fffff
            value=0x6f|(edge['rd']<<7)|((bits>>20&1)<<31)|((bits>>1&1023)<<21)|((bits>>11&1)<<20)|((bits>>12&255)<<12)
            normalized[off:off+4]=value.to_bytes(4,'little')
        need(bytes(normalized)==original,'All original region bytes after static original-VA edge encoding')
        at=0
        while at<len(raw):
            width=4 if raw[at]&3==3 else 2
            need(at+width<=len(raw),'Whole original instruction');at+=width;count+=1
        total+=len(raw);noncontrol+=len(raw)-4*len(local)
    need(total==78 and count==23 and noncontrol==62,'Complete78B23i and62 unchanged non-control bytes')
    need({s['index']for s in e.sections if s['flags']&2 and s['size']}==owners,'Every allocated code byte owned')
    poll=gm['tsl9_rtc_wait_19272'];poll_bytes=e.data(e.sections[poll['section']])
    need(poll_bytes.hex()=='373700408357478093f70702e5df8280','Original repeated halfword load/AND32/backedge/RET')
    entry=gm['tsl9_rtc_alarm_entry_19bd4']
    need(e.data(e.sections[entry['section']])[-4:].hex()=='73002030','Original MRET')
    return dict(passed=True,code_bytes=78,instructions=23,FUNC=5,UND=0,RELA=4,
        native_object_sha256=sha(path),complete_original_VA_encoded_bytes_equal=True,
        noncontrol_bytes_equal=62,original_direct_references=4,original_polling_backedge_retained=True,
        frame_allocated=False,GP_flag_offset=392,word_write_address=0x40010414,
        halfword_read_write_address=0x40002804,wait_mask=32,clear_mask_at_IRQ=2,
        callback_or_IRQ_ABI_proved=False,physical_MCU_or_peripheral_proved=False,
        target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,
        network=False,negative_cases_executed=0,firmware_BIN_generated=False,firmware_ready=False)

def inputs(llvm):
    paths=[Path(__file__),HERE/'spec-v1.json',SHARED,ROOT/S['source'],ROOT/S['firmware'],
           ROOT/S['reader'],ROOT/S['curation_checker'],ROOT/S['reference_candidate'],llvm.parent/'lib/clang/18/include/stdint.h']
    paths += [llvm/name for name in S['tools']]
    return {str(p):dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(set(paths))}
def inventory(folder):
    return {p.name:dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(folder.iterdir())if p.is_file()}
def dependencies(folder,llvm):
    return runpy.run_path(str(ROOT/S['curation_checker']))['dependencies'](folder,'origin',llvm.parent/'lib/clang/18')
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True)
    group=p.add_mutually_exclusive_group(required=True);group.add_argument('--trial');group.add_argument('--replay',type=Path)
    a=p.parse_args();llvm=a.tool_dir.resolve()
    for key in('source','firmware','reader','curation_checker','reference_candidate'):
        need(sha(ROOT/S[key])==S[key+'_sha256'],'Pinned '+key)
    for name,pin in S['tools'].items():need(sha(llvm/name)==pin,'Pinned '+name)
    need(sha(llvm.parent/'lib/clang/18/include/stdint.h')==S['stdint_sha256'],'Pinned compiler header')
    C=runpy.run_path(str(ROOT/S['curation_checker']))
    need(S['flags']=={m:C['flags']({'profile':S['profile']},m)for m in('c','cpp')},'Exact existing compiler profile')
    before=portable(inputs(llvm),llvm)
    if a.replay:
        out=a.replay.resolve();need(out.parent==HERE/'build','Owned retained native trial')
        saved=json.loads((out/'measurement.json').read_bytes());need(saved['inputs']==before,'Every actual input unchanged')
        for mode in('c','cpp'):
            f=out/mode;job=saved['modes'][mode]
            need(job['artifacts']==inventory(f),'Whole retained native output inventory')
            need(job['result']==audit_object(f/'unit.o'),'Actual original-code native replay')
            need(job['dependencies']==portable(dependencies(f,llvm),llvm),'All compiler dependencies unchanged')
        print(json.dumps(dict(passed=True,mode='read-only-normal-RTC-replay',languages=['c','cpp'],target_executed=False)));return
    need(a.trial and Path(a.trial).name==a.trial,'Single owned trial name')
    out=HERE/'build'/a.trial;need(not out.exists(),'Create-only trial folder')
    report=dict(schema='TSL9-original-RTC-native-build-v1',inputs=before,modes={})
    for mode in('c','cpp'):
        f=out/mode;f.mkdir(parents=True);commands=[]
        recipes=[('compile',[str(llvm/'clang.exe')]+S['flags'][mode]+
                  ['-MD','-MF',str(f/'unit.d'),'-MT','unit.o','-c',str(ROOT/S['source']),'-o',str(f/'unit.o')]),
                 ('read',[str(llvm/'llvm-objdump.exe'),'-dr','-t','-h',str(f/'unit.o')])]
        for label,argv in recipes:
            result=subprocess.run(argv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
            (f/(label+'.log')).write_bytes(result.stdout);commands.append(dict(label=label,argv=argv,exit=result.returncode))
            need(result.returncode==0,'Actual '+label+' failed; original log retained')
        facts=audit_object(f/'unit.o')
        report['modes'][mode]=dict(result=facts,commands=commands,dependencies=portable(dependencies(f,llvm),llvm),artifacts=inventory(f))
        print(json.dumps(dict(mode=mode,**facts)))
    need(before==portable(inputs(llvm),llvm),'All inputs unchanged during actual compilation')
    (out/'measurement.json').write_bytes(encoded(portable(report,llvm)))
if __name__=='__main__':
    try:main()
    except(ValueError,OSError,subprocess.SubprocessError)as error:
        message=str(error)
        for path,token in[(ROOT,'$'+'{PROJECT_ROOT}'),(Path.home(),'$'+'{USERPROFILE}')]:
            message=message.replace(str(path),token).replace(path.as_posix(),token)
        print('FAIL: '+message,file=sys.stderr);sys.exit(1)
