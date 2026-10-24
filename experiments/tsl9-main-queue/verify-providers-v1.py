#!/usr/bin/env python3
"""Audit genuine current C/C++ provider objects; select only the complete820C leaf anddeduplicatedrecord C unit."""
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
S=json.loads((HERE/'spec-v1.json').read_bytes())
def need(ok,message):
    if not ok:raise ValueError(message)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
need(sha(ROOT/S['shared_helper'])=='1f6e3673c24a5d85c62d55ec8d8390b80225577010d81c8aba5c4b6750e208b5','Frozen instruction-encoding helper')
need(sha(ROOT/S['reader'])=='112e90f7a1786bd1e388718e80086ba937035364d926c89cd5875eba68ce543a','Frozen native ELF reader')
B=runpy.run_path(str(ROOT/S['shared_helper']))
E=runpy.run_path(str(ROOT/S['reader']))['ELF']
portable,encoded=B['portable'],B['encoded']

def pins(llvm):
    for path,pin in S['pins'].items():need(sha(ROOT/path)==pin,'Pinned actual provider input')
    need(sha(ROOT/S['firmware'])==S['firmware_sha256'],'Original firmware identity')
    for name,pin in S['tools'].items():need(sha(llvm/name)==pin,'Pinned actual local linker/reader')

def audit_object(path,regions,undefined,selected=False):
    e=E(path);fw=(ROOT/S['firmware']).read_bytes()
    need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual RISC-V ET_REL')
    globals_=[f for f in e.symbols if f['info']>>4];gm={f['name']:f for f in globals_}
    need(len(gm)==len(globals_)and set(gm)=={r['name']for r in regions}|set(undefined),'Exact genuine provider globals')
    for name in undefined:
        f=gm[name];need(f['info']==16 and f['section']==f['value']==f['size']==0,'Explicit undefined NOTYPE dependency')
    starts={r['start']:r['name']for r in regions}
    ext={int(name.rsplit('_',1)[1],16):name for name in undefined}
    expected=Counter();owned=set();count=noncontrol=total=resolved=0;edges=[]
    for region in regions:
        f=gm[region['name']];sec=e.sections[f['section']]
        need(f['info']==18 and f['other']==0 and f['value']==0 and f['size']==region['bytes'],'Actual full-sized region')
        need(sec['flags']==6 and sec['type']==1 and sec['address']==0 and sec['size']==f['size'],'Exact code allocation')
        need(sec['name']==(selected if selected else'.text.'+f['name']),'Owned selected/original section')
        need(sec['index']not in owned,'One real code owner per section');owned.add(sec['index'])
        raw=e.data(sec);original=fw[region['start']-0x8000:region['end']-0x8000]
        need(hashlib.sha256(original).hexdigest()==region['original_sha256'],'Original PC-span identity')
        normalized=bytearray(raw);ops=[];at=0
        while at<len(raw):
            width=4 if original[at]&3==3 else 2
            need(at+width<=len(raw)and(4 if raw[at]&3==3 else 2)==width,'Complete original instruction width')
            ops.append((at,width));at+=width
        pcs={region['start']+off for off,width in ops}
        rels={r['offset']:r for r in e.relocations if r['section']==sec['index']}
        need(len(rels)==sum(r['section']==sec['index']for r in e.relocations),'No duplicate native reference site')
        for off,width in ops:
            pc=region['start']+off;edge=B['decode_control'](original[off:off+width],pc)
            if edge:
                kind,target=edge
                if off in rels:
                    rel=rels[off];name=starts.get(target,ext.get(target))
                    need(name is not None and rel['type']==kind and rel['addend']==0,'Original encoded target with typed native reference')
                    symbol=e.symbols[rel['symbol']]
                    need(symbol['name']==name,'Correct actual target symbol')
                    if name in undefined:need(symbol['section']==0 and symbol['info']==16,'Explicit real child dependency')
                    else:need(symbol['info']==18 and symbol['section']>0 and symbol['value']==0,'Genuine same-unit target')
                    w,mask=B['MASKS'][kind];a=int.from_bytes(raw[off:off+w],'little');b=int.from_bytes(original[off:off+w],'little')
                    need(w==width and a&mask==b&mask and a&(~mask&((1<<(8*w))-1))==0,'Exact opcode/register bits and zero native displacement')
                    normalized[off:off+w]=(a|B['immediate'](kind,target-pc)).to_bytes(w,'little')
                    expected[(sec['index'],off,kind,0,name)]+=1
                    edges.append(dict(PC=pc,type=kind,target_PC=target,target=name,typed_reference=True))
                else:
                    need(target in pcs and raw[off:off+width]==original[off:off+width],'Resolved native branch stays inside its genuine full-sized function')
                    resolved+=1;edges.append(dict(PC=pc,type=kind,target_PC=target,target=region['name'],typed_reference=False))
            else:
                need(off not in rels,'No undeclared noncontrol relocation')
                noncontrol+=width
            count+=1
        need(bytes(normalized)==original,'All original provider bytes after static original-VA encoding')
        total+=len(raw)
    actual=Counter((r['section'],r['offset'],r['type'],r['addend'],e.symbols[r['symbol']]['name'])for r in e.relocations)
    need(actual==expected,'Complete exact native typed-reference inventory')
    need({s['index']for s in e.sections if s['flags']&2 and s['size']}==owned,'Every allocated byte genuinely owned')
    return dict(passed=True,code_bytes=total,instructions=count,FUNC=len(regions),RELA=len(e.relocations),
                resolved_intra_function_controls=resolved,noncontrol_bytes_equal=noncontrol,UND=sorted(undefined),
                control_edges=edges,native_object_sha256=sha(path),all_original_VA_encoded_bytes_equal=True,
                target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,
                network=False,negative_cases_executed=0,firmware_BIN_generated=False)

def object_path(provider,mode,folder):
    if provider['selection']=='clear':return folder/mode/'selected-clear.o'
    if provider['selection']=='derived-record':return folder/mode/'selected-record.o'
    return ROOT/provider['objects'][mode]

def dependencies(folder,llvm):
    C=runpy.run_path(str(ROOT/S['curation_checker']))
    return portable(C['dependencies'](folder,'origin',llvm.parent/'lib/clang/18'),llvm)

def source_selection(llvm):
    value=runpy.run_path(str(ROOT/S['source_deriver']))['derive']()
    need(value['source'].encode()==(ROOT/S['selected_source']).read_bytes(),'Exact C definition-only selection derivation')
    need(value['omitted_symbol']=='tsl9_program_disarm_93ee'and value['only_one_complete_C_definition_omitted'],'One duplicate C definition omitted')
    C=runpy.run_path(str(ROOT/S['curation_checker']))
    manifest=json.loads((ROOT/S['manifest']).read_bytes())
    unit=next(x for x in manifest['native_units']if x['name']=='record-program')
    need(S['selected_flags']=={mode:C['flags'](unit,mode)for mode in ('c','cpp')},'Exactly the current source compiler profile')
    need(sha(llvm.parent/'lib/clang/18/include/stdint.h')==S['stdint_sha256'],'Pinned compiler header')
    for mode in ('c','cpp'):
        e=E(ROOT/S['parent_component']/mode/S['parent_object'])
        f=next(x for x in e.symbols if x['name']=='tsl9_program_disarm_93ee')
        raw=e.data(e.sections[f['section']])[f['value']:f['value']+f['size']]
        original=(ROOT/S['firmware']).read_bytes()[0x93ee-0x8000:0x9410-0x8000]
        need(f['info']==18 and f['size']==34 and raw==original,'Parent already owns the exact genuine34B omitted body')
    return value

def projected_bodies_equal(full,selected,regions):
    a,b=E(full),E(selected)
    am={f['name']:f for f in a.symbols if f['info']>>4}
    bm={f['name']:f for f in b.symbols if f['info']>>4}
    for region in regions:
        x,y=am[region['name']],bm[region['name']]
        need(a.data(a.sections[x['section']])==b.data(b.sections[y['section']]),'Each retained compiler body unchanged by C selection')
        def refs(e,f):
            return Counter((r['offset'],r['type'],r['addend'],e.symbols[r['symbol']]['name'])
                           for r in e.relocations if r['section']==f['section'])
        need(refs(a,x)==refs(b,y),'Each retained typed reference unchanged by C selection')
    return True

def inventory(folder):
    return {p.name:dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(folder.iterdir())if p.is_file()}

def audit(folder,llvm):
    pins(llvm);source_selection(llvm);result={}
    for mode in ('c','cpp'):
        jobs={}
        for provider in S['providers']:
            full=audit_object(ROOT/provider['objects'][mode],provider['regions'],provider['undefined'])
            selected=(audit_object(object_path(provider,mode,folder),provider['selected_regions'],
                                   provider['selected_undefined'],
                                   '.provider_clear_code'if provider['selection']=='clear'else False)
                      if provider['selection']!='none'else full)
            if provider['selection']=='derived-record':
                projected_bodies_equal(ROOT/provider['objects'][mode],object_path(provider,mode,folder),provider['selected_regions'])
            jobs[provider['unit']]=dict(full_source=full,selected=selected)
        total=sum(x['selected']['code_bytes']for x in jobs.values())
        count=sum(x['selected']['instructions']for x in jobs.values())
        refs=sum(x['selected']['RELA']for x in jobs.values())
        defs={r['name']for provider in S['providers']for r in provider['selected_regions']}
        und={name for x in jobs.values()for name in x['selected']['UND']}
        parent=E(ROOT/S['parent_component']/mode/S['parent_object'])
        existing={f['name']for f in parent.symbols if f['info']>>4 and f['section']}
        remaining=sorted(und-defs-existing-set(S['aliases']))
        need(total==1464 and len(defs)==59 and remaining==['tsl9_queue_external_12abe','tsl9_queue_external_14d2e'],
             'Complete1464B selected flow withtwo explicit larger dispatch gaps')
        result[mode]=dict(jobs=jobs,selected_bytes=total,selected_instructions=count,selected_FUNC=59,
                          selected_RELA=refs,remaining_internal_provider_gaps=remaining,record_selection_dependencies=dependencies(folder/mode,llvm),
                          artifacts=inventory(folder/mode))
    return result

def inputs(llvm):
    paths=[Path(__file__),HERE/'spec-v1.json',HERE/'clear-v1.ld',ROOT/S['firmware'],llvm.parent/'lib/clang/18/include/stdint.h']
    paths += [ROOT/path for path in S['pins']]
    paths += [llvm/name for name in S['tools']]
    return {str(p):dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(set(paths))}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True)
    group=p.add_mutually_exclusive_group(required=True);group.add_argument('--output',type=Path);group.add_argument('--replay',type=Path)
    a=p.parse_args();llvm=a.tool_dir.resolve();pins(llvm);before=portable(inputs(llvm),llvm)
    if a.replay:
        out=a.replay.resolve();need(out.parent==HERE/'build','Owned retained provider output')
        saved=json.loads((out/'measurement.json').read_bytes())
        need(saved['inputs']==before and saved['modes']==audit(out,llvm),'Complete retained provider evidence replay')
        print(json.dumps(dict(passed=True,mode='read-only-normal-provider-closure-replay',selected_bytes=1464,target_executed=False)));return
    out=a.output.resolve();need(out.parent==HERE/'build'and not out.exists(),'Create-only owned selection')
    source_selection(llvm)
    for mode in ('c','cpp'):
        folder=out/mode;folder.mkdir(parents=True)
        provider=next(x for x in S['providers']if x['selection']=='clear')
        audit_object(ROOT/provider['objects'][mode],provider['regions'],provider['undefined'])
        recipes=[('select-clear',[str(llvm/'ld.lld.exe'),'-r','--gc-sections','--no-relax','--undefined=tsl9_queue_clear_820c',
                                  '-T',str(HERE/'clear-v1.ld'),str(ROOT/provider['objects'][mode]),'-o',str(folder/'selected-clear.o')]),
                 ('compile-record',[str(llvm/'clang.exe')]+S['selected_flags'][mode]+
                    ['-MD','-MF',str(folder/'unit.d'),'-MT','unit.o','-c',str(ROOT/S['selected_source']),'-o',str(folder/'selected-record.o')]),
                 ('read-clear',[str(llvm/'llvm-objdump.exe'),'-dr','-t','-h',str(folder/'selected-clear.o')]),
                 ('read-record',[str(llvm/'llvm-objdump.exe'),'-dr','-t','-h',str(folder/'selected-record.o')])]
        for label,argv in recipes:
            proc=subprocess.run(argv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
            (folder/(label+'.log')).write_bytes(proc.stdout)
            need(proc.returncode==0,'Actual source selection compile/read failed; log retained')
    facts=audit(out,llvm);need(before==portable(inputs(llvm),llvm),'All actual inputs unchanged during selection')
    report=dict(schema='TSL9-main-queue-native-selection-v1',inputs=before,modes=facts,
                executable_firmware_bytes_copied_from_original=False,target_executed=False,network=False)
    (out/'measurement.json').write_bytes(encoded(portable(report,llvm)))
    print(json.dumps(dict(passed=True,modes={mode:{key:value for key,value in job.items()if key not in ('jobs','artifacts')}for mode,job in facts.items()})))
if __name__=='__main__':
    try:main()
    except Exception as error:
        print(json.dumps(dict(passed=False,error=str(error))),file=sys.stderr);raise SystemExit(1)
