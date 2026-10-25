#!/usr/bin/env python3
"""Compile original SELECTOR-STORAGE context C/C++ regions; inspect objects without execution."""
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
    data_names={d['name']for d in S['literal_data']}
    need(len(gm)==len(globals_)and set(gm)=={r['name']for r in S['regions']}|set(S['undefined'])|data_names,'Exact code/data/provider global inventory')
    for name in S['undefined']:
        s=gm[name];need(s['info']==16 and s['section']==s['value']==s['size']==s['other']==0,'Genuine undefined NOTYPE provider')
    owned=set();expected=[];total=count=noncontrol=0
    for r in S['regions']:
        f=gm[r['name']];sec=e.sections[f['section']]
        need(f['info']==18 and f['other']==0 and f['value']==0 and f['size']==r['bytes'],'Actual full-size original basic block')
        need(sec['name']=='.text.'+f['name']and sec['flags']==6 and sec['type']==1 and sec['address']==0 and sec['size']==f['size'],'Exact code allocation')
        need(sec['index']not in owned,'One real code owner');owned.add(sec['index'])
        raw=e.data(sec);original=fw[r['start']-0x8000:r['end']-0x8000]
        need(hashlib.sha256(original).hexdigest()==r['original_sha256'],'Original block identity')
        normalized=bytearray(raw);controls=[x for x in S['controls']if x['owner']==r['name']]
        for edge in controls:
            off,kind=edge['offset'],edge['type'];width,mask=B['MASKS'][kind]
            need(off+width<=len(raw)and width==edge['size'],'Whole original control')
            a=int.from_bytes(raw[off:off+width],'little');b=int.from_bytes(original[off:off+width],'little')
            need(a&mask==b&mask and a&(~mask&((1<<(width*8))-1))==0,'Exact control opcode/register bits and zero native displacement')
            need(B['decode_control'](original[off:off+width],edge['PC'])==(kind,edge['target_PC']),'Original encoded direct edge')
            normalized[off:off+width]=(a|B['immediate'](kind,edge['target_PC']-edge['PC'])).to_bytes(width,'little')
            expected.append((sec['index'],off,kind,0,edge['target']))
        pairs=[x for x in S['PC_relative_pairs']if x['owner']==r['name']]
        for pair in pairs:
            off=pair['offset'];need(off+8<=len(raw),'Complete original AUIPC/ADDI pair')
            label='.Lselector_storage_literal_'+format(pair['PC'],'x')
            anchors=[s for s in e.symbols if s['name']==label]
            need(len(anchors)==1,'Actual single local HI anchor')
            anchor=anchors[0]
            need(anchor['info']==anchor['other']==anchor['size']==0 and anchor['section']==sec['index']and anchor['value']==off,'Exact local HI owner/offset')
            delta=(pair['target_PC']-pair['PC'])&0xffffffff
            for where,kind,mask,imm,target in [(off,23,0xfff,(delta+0x800)&0xfffff000,pair['target']),(off+4,24,0xfffff,(delta&0xfff)<<20,label)]:
                a=int.from_bytes(raw[where:where+4],'little');b=int.from_bytes(original[where:where+4],'little')
                need(a&mask==b&mask and a&(~mask&0xffffffff)==0,'Exact original literal opcode/register and zero symbolic displacement')
                normalized[where:where+4]=((a&mask)|imm).to_bytes(4,'little')
                expected.append((sec['index'],where,kind,0,target))
        need(bytes(normalized)==original,'Complete original code after static original-VA encoding')
        at=0
        while at<len(raw):
            width=4 if raw[at]&3==3 else 2;need(at+width<=len(raw),'Whole actual instruction');at+=width;count+=1
        total+=len(raw);noncontrol+=len(raw)-sum(x['size']for x in controls)-8*len(pairs)
    need(len(S['literal_data'])==4 and sum(d['bytes']for d in S['literal_data'])==61,'Four exact readonly lookup objects')
    for d in S['literal_data']:
        ds=gm[d['name']];sec=e.sections[ds['section']]
        need((ds['info'],ds['other'],ds['value'],ds['size'])==(17,0,0,d['bytes']),'Genuine full-size global DATA object')
        need((sec['name'],sec['type'],sec['flags'],sec['address'],sec['size'],sec['align'])==(d['section'],1,2,0,d['bytes'],1),'Exact readonly byte alignment/allocation')
        data_raw=e.data(sec)
        need(data_raw==fw[d['start']-0x8000:d['end']-0x8000] and data_raw.hex()==d['raw_hex'] and hashlib.sha256(data_raw).hexdigest()==d['original_sha256'],'Actual original lookup bytes;no padding or synthetic table')
        need(sec['index']not in owned,'Unique readonly data owner');owned.add(sec['index'])
    actual=[(x['section'],x['offset'],x['type'],x['addend'],e.symbols[x['symbol']]['name'])for x in e.relocations]
    need(sorted(actual)==sorted(expected)and len(actual)==26,'All26 original controls and0 typed static-address pairs')
    need({s['index']for s in e.sections if s['flags']&2 and s['size']}==owned,'Every allocated code/data byte owned')
    need(total==252 and count==81 and len(S['regions'])==28,'Complete252B81i28regions')
    return dict(passed=True,code_bytes=total,original_instructions=count,FUNC=len(S['regions']),original_functions=len(json.loads((ROOT/S['reference_candidate']).read_bytes())['selected_functions']),data_bytes=61,readonly_objects=4,lookup_bytes_equal_original=True,
        RELA=len(actual),direct_control_relocations=len(S['controls']),UND=S['undefined'],noncontrol_bytes_equal=noncontrol,
        all_original_code_VA_encoded_bytes_equal=True,original_C_dataflow_and_private_ROM_ports_retained=True,
        native_object_sha256=sha(path),original_address_placement_proved=False,
        concurrent_state_semantics_proved=False,private_caller_ABI_proved=False,
        physical_MCU_ROM_RAM_IRQ_OTA_proved=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,
        hardware_accessed=False,network=False,negative_cases_executed=0,firmware_BIN_generated=False,firmware_ready=False)

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
    evidence=json.loads((ROOT/S['reference_candidate']).read_bytes())
    fw=(ROOT/S['firmware']).read_bytes()
    selected=evidence['selected_functions']
    need(len(selected)==1 and sum(len(f['operations'])for f in selected)==81,'Complete retained1-function81i evidence')
    for f in selected:
        at=f['start']
        for op in f['operations']:
            raw=bytes.fromhex(op['bytes'])
            need(op['addr']==at and len(raw)==op['size'] and raw==fw[at-0x8000:at-0x8000+len(raw)],'Contiguous original instruction identity')
            need(len(raw)==(4 if raw[0]&3==3 else 2),'Original instruction width')
            at+=len(raw)
        need(at==f['end'],'Whole retained original function')
    derived=subprocess.run([sys.executable,'-X','utf8','-B',str(ROOT/S['source_deriver'])],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60)
    need(derived.returncode==0,'Pinned source derivation')
    generated=json.loads(derived.stdout)
    need((ROOT/S['source']).read_text()==generated['source'],'Exact generated original-region C source')
    need(generated['regions']==S['regions'] and generated['controls']==S['controls'] and generated['PC_relative_pairs']==S['PC_relative_pairs'] and generated['literal_data']==S['literal_data'],'Exact derived region/control inventory')
    before=portable(inputs(llvm),llvm)
    if a.replay:
        out=a.replay.resolve();need(out.parent==HERE/'build','Owned retained native trial')
        saved=json.loads((out/'measurement.json').read_bytes());need(saved['inputs']==before,'Every actual input unchanged')
        for mode in('c','cpp'):
            f=out/mode;job=saved['modes'][mode]
            need(job['artifacts']==inventory(f),'Whole retained native output inventory')
            need(job['result']==audit_object(f/'unit.o'),'Actual original-code native replay')
            need(job['dependencies']==portable(dependencies(f,llvm),llvm),'All compiler dependencies unchanged')
        print(json.dumps(dict(passed=True,mode='read-only-normal-SELECTOR-STORAGE-replay',languages=['c','cpp'],target_executed=False)));return
    need(a.trial and Path(a.trial).name==a.trial,'Single owned trial name')
    out=HERE/'build'/a.trial;need(not out.exists(),'Create-only trial folder')
    report=dict(schema='TSL9-original-SELECTOR-STORAGE-native-build-v1',inputs=before,modes={})
    for mode in('c','cpp'):
        f=out/mode;f.mkdir(parents=True);commands=[]
        recipes=[('compile',[str(llvm/'clang.exe')]+S['flags'][mode]+
                  ['-MD','-MF',str(f/'unit.d'),'-MT','unit.o','-c',str(ROOT/S['source']),'-o',str(f/'unit.o')]),
                 ('read',[str(llvm/'llvm-objdump.exe'),'-dr','-t','-h',str(f/'unit.o')])]
        for label,argv in recipes:
            result=subprocess.run(argv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
            (f/(label+'.log')).write_bytes(portable(result.stdout.decode('utf8','replace'),llvm).encode('utf8'));commands.append(dict(label=label,argv=argv,exit=result.returncode))
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
