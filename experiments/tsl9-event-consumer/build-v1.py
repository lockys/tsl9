#!/usr/bin/env python3
"""Compile original EVENT-CONSUMER context C/C++ regions; inspect objects without execution."""
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
    e=elf(path);fw=(ROOT/S['firmware']).read_bytes()
    need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual RISC-V ET_REL')
    globals_=[s for s in e.symbols if s['info']>>4];gm={s['name']:s for s in globals_}
    need(len(gm)==len(globals_)and set(gm)=={r['name']for r in S['regions']}|set(S['undefined']),'Exact original region/provider inventory')
    for name in S['undefined']:
        f=gm[name];need(f['info']==16 and f['section']==0 and f['value']==0 and f['size']==0,'Explicit unresolved real provider')
    wanted=[(gm[x['owner']]['section'],x['offset'],x['type'],0,x['target'])for x in S['controls']]
    actual=[(x['section'],x['offset'],x['type'],x['addend'],e.symbols[x['symbol']]['name'])for x in e.relocations]
    need(sorted(actual)==sorted(wanted),'Exact owned typed control references')
    need(hashlib.sha256(b''.join(fw[x['start']-0x8000:x['end']-0x8000]for x in S['ranges'])).hexdigest()==S['original_sha256'],'Pinned original continuous534B range')
    owners=set();code=0;count=0;noncontrol=0;concatenated=[]
    for region in S['regions']:
        f=gm[region['name']];sec=e.sections[f['section']]
        need(f['info']==18 and f['other']==0 and f['value']==0 and f['size']==region['bytes'],'Genuine full-size basic block')
        need(sec['name']=='.text.'+f['name']and sec['flags']==6 and sec['type']==1 and sec['address']==0 and sec['size']==f['size'],'Exact code allocation')
        need(sec['index']not in owners,'Distinct code owner');owners.add(sec['index'])
        raw=e.data(sec);original=fw[region['start']-0x8000:region['end']-0x8000]
        need(hashlib.sha256(original).hexdigest()==region['original_sha256'],'Original block identity')
        normalized=bytearray(raw);local=[x for x in S['controls']if x['owner']==region['name']]
        for edge in local:
            off=edge['offset'];kind=edge['type'];width,mask=B['MASKS'][kind]
            need(width==edge['size']and off+width<=len(raw),'Whole original control window')
            a=int.from_bytes(raw[off:off+width],'little');b=int.from_bytes(original[off:off+width],'little')
            need(a&mask==b&mask and a&(~mask&((1<<(width*8))-1))==0,'Exact opcode/register bits and zero native displacement')
            need(B['decode_control'](original[off:off+width],edge['PC'])==(kind,edge['target_PC']),'Actual original encoded edge')
            normalized[off:off+width]=(a|B['immediate'](kind,edge['target_PC']-edge['PC'])).to_bytes(width,'little')
        need(bytes(normalized)==original,'Complete original block after static original-VA encoding')
        at=0
        while at<len(raw):
            width=4 if raw[at]&3==3 else 2
            need(at+width<=len(raw),'Complete original instruction');at+=width;count+=1
        code+=len(raw);noncontrol+=len(raw)-sum(x['size']for x in local);concatenated.append(bytes(normalized))
    need(code==534 and count==187 and len(owners)==35,'Complete534B187i35blocks')
    need(b''.join(concatenated)==b''.join(fw[x['start']-0x8000:x['end']-0x8000]for x in S['ranges']),'Original complete order within continuous callback family')
    need({x['index']for x in e.sections if x['flags']&2 and x['size']}==owners,'Every allocated byte owned')
    return dict(passed=True,code_bytes=534,instructions=187,FUNC=35,UND=len(S['undefined']),RELA=23,
        undefined=S['undefined'],native_object_sha256=sha(path),complete_original_VA_encoded_bytes_equal=True,
        noncontrol_bytes_equal=noncontrol,original_direct_references=23,
        original_address_placement_proved=False,original_frame_sizes=[16,32,48],
        original_entry_PCs=[0x17666,0x176a0,0x176f8],original_shared_event_restore_retained=True,
        fresh_GP_queue_count_and_post_call_updates_retained=True,original_signed_REM_port_retained=True,
        raw_table_index_not_bounded_by_later_remainder=True,original_table_address=0x1aae8,
        original_literal_callbacks_remain_placement_dependent=True,
        resident_pointer_sources=['40058','4004C'],four_indirect_calls_retained=True,
        entry_and_callee_ABI_proved=False,physical_MCU_or_peripheral_proved=False,
        target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,
        network=False,negative_cases_executed=0,firmware_BIN_generated=False,firmware_ready=False)

def inputs(llvm):
    paths=[Path(__file__),HERE/'spec-v1.json',SHARED,ROOT/S['source'],ROOT/S['firmware'],
           ROOT/S['reader'],ROOT/S['curation_checker'],ROOT/S['reference_candidate'],ROOT/S['source_deriver'],llvm.parent/'lib/clang/18/include/stdint.h']
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
    for key in('source','firmware','reader','curation_checker','reference_candidate','source_deriver'):
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
        print(json.dumps(dict(passed=True,mode='read-only-normal-EVENT-CONSUMER-replay',languages=['c','cpp'],target_executed=False)));return
    need(a.trial and Path(a.trial).name==a.trial,'Single owned trial name')
    out=HERE/'build'/a.trial;need(not out.exists(),'Create-only trial folder')
    report=dict(schema='TSL9-original-EVENT-CONSUMER-native-build-v1',inputs=before,modes={})
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
