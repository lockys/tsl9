#!/usr/bin/env python3
"""Compile only, or replay normal native artifacts. No target or model execution."""
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
MASKS={16:(4,0x01fff07f),17:(4,0x00000fff),44:(2,0xe383),45:(2,0xe003),
       23:(4,0x00000fff),24:(4,0x000fffff)}

def need(ok,message):
    if not ok:
        raise ValueError(message)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def encoded(v):
    return (json.dumps(v,sort_keys=True,indent=2,ensure_ascii=True)+'\n').encode()

def portable(v,llvm):
    pairs=[(llvm.parent/'lib/clang/18','$'+'{CLANG_RESOURCE}'),
           (llvm,'$'+'{LLVM_BIN}'),(ROOT,'$'+'{PROJECT_ROOT}')]
    if isinstance(v,str):
        for p,t in pairs:
            for form in (str(p),p.as_posix()):
                v=v.replace(form,t)
        return v
    if isinstance(v,list):
        return [portable(x,llvm) for x in v]
    if isinstance(v,dict):
        return {portable(k,llvm):portable(x,llvm) for k,x in v.items()}
    return v

def sx(v,n):
    return v-(1<<n) if v&(1<<(n-1)) else v

def decode_control(raw,pc):
    v=int.from_bytes(raw,'little')
    if len(raw)==4 and v&127==0x6f:
        d=((v>>31)<<20)|(((v>>12)&255)<<12)|(((v>>20)&1)<<11)|(((v>>21)&1023)<<1)
        return 17,(pc+sx(d,21))&0xffffffff
    if len(raw)==4 and v&127==0x63:
        d=((v>>31)<<12)|(((v>>7)&1)<<11)|(((v>>25)&63)<<5)|(((v>>8)&15)<<1)
        return 16,(pc+sx(d,13))&0xffffffff
    if len(raw)==2 and v&0xe003 in (0xc001,0xe001):
        d=(((v>>12)&1)<<8)|(((v>>10)&3)<<3)|(((v>>5)&3)<<6)|(((v>>3)&3)<<1)|(((v>>2)&1)<<5)
        return 44,(pc+sx(d,9))&0xffffffff
    if len(raw)==2 and v&0xe003 in (0x2001,0xa001):
        d=(((v>>12)&1)<<11)|(((v>>11)&1)<<4)|(((v>>9)&3)<<8)|(((v>>8)&1)<<10)|(((v>>7)&1)<<6)|(((v>>6)&1)<<7)|(((v>>3)&7)<<1)|(((v>>2)&1)<<5)
        return 45,(pc+sx(d,12))&0xffffffff
    return None

def expected(fw,region):
    start,end=region['start'],region['end']
    raw=fw[start-0x8000:end-0x8000]
    need(hashlib.sha256(raw).hexdigest()==region['original_sha256'],'Original region identity')
    result={};at=0;instructions=0
    while at<len(raw):
        width=4 if raw[at]&3==3 else 2
        need(at+width<=len(raw),'Whole recorded instruction')
        decoded=decode_control(raw[at:at+width],start+at)
        if decoded:
            result[at]=dict(kind=decoded[0],target=decoded[1])
        at+=width;instructions+=1
    for pair in S['PC_relative_pairs']:
        if start<=pair['PC']<end:
            off=pair['PC']-start
            result[off]=dict(kind=23,target=pair['target'])
            result[off+4]=dict(kind=24,target=pair['target'],HI_offset=off)
    return raw,result,instructions

def immediate(kind,d):
    d&=0xffffffff
    if kind==17:
        return (((d>>20)&1)<<31)|(((d>>1)&1023)<<21)|(((d>>11)&1)<<20)|(((d>>12)&255)<<12)
    if kind==16:
        return (((d>>12)&1)<<31)|(((d>>5)&63)<<25)|(((d>>1)&15)<<8)|(((d>>11)&1)<<7)
    if kind==44:
        return (((d>>8)&1)<<12)|(((d>>3)&3)<<10)|(((d>>6)&3)<<5)|(((d>>1)&3)<<3)|(((d>>5)&1)<<2)
    need(kind==45,'Recorded immediate kind')
    return (((d>>11)&1)<<12)|(((d>>4)&1)<<11)|(((d>>8)&3)<<9)|(((d>>10)&1)<<8)|(((d>>6)&1)<<7)|(((d>>7)&1)<<6)|(((d>>1)&7)<<3)|(((d>>5)&1)<<2)

def audit_object(path):
    E=runpy.run_path(str(ROOT/S['reader']))['ELF']
    e=E(path);fw=(ROOT/S['firmware']).read_bytes()
    need(e.header[0]==1 and not e.program_headers,'ET_REL with no program headers')
    funcs=[x for x in e.symbols if x['info']&15==2]
    need({f['name'] for f in funcs}=={r['name'] for r in S['regions']},'Exact genuine region definitions')
    globals_=[x for x in e.symbols if x['info']>>4]
    need(len({x['name'] for x in globals_})==len(globals_),'Unique normal global symbols')
    need(all(x['section']!=0xfff1 for x in globals_),'No absolute provider substitutes')
    need(all((x['info']==18 and x['section']>0)or(x['info']==16 and x['section']==0)for x in globals_),'Real FUNC or unresolved NOTYPE roles')
    by_name={f['name']:f for f in funcs};owned=set();relocations=[];total_i=0;total_b=0
    for region in S['regions']:
        f=by_name[region['name']];sec=e.sections[f['section']]
        need(f['info']==18 and f['other']==0 and f['value']==0,'Strong exact region start')
        need(f['size']==region['bytes'],f"{f['name']}: actual size {f['size']} expected {region['bytes']}")
        need(sec['name']=='.text.'+f['name'] and sec['flags']==6 and sec['address']==0 and sec['size']==f['size'],'Exact region allocation')
        need(sec['index'] not in owned,'Distinct region owner');owned.add(sec['index'])
        actual=e.data(sec);original,wanted,n=expected(fw,region)
        rows=[r for r in e.relocations if r['section']==sec['index']]
        need(len(rows)==len(wanted) and len({r['offset']for r in rows})==len(rows),'Complete normal relocation inventory')
        patched=bytearray(actual);mask=bytearray(b'\xff'*len(actual))
        for rel in rows:
            at=rel['offset'];kind=rel['type']
            need(at in wanted and kind==wanted[at]['kind'] and rel['addend']==0,'Exact recorded relocation kind/addend')
            width,bits=MASKS[kind];need(0<=at<=len(actual)-width,'Owned relocation extent')
            symbol=e.symbols[rel['symbol']];dest=wanted[at]['target'];pc=region['start']+at
            if kind==24:
                hi=wanted[at]['HI_offset']
                need(symbol['info']==0 and symbol['section']==sec['index'] and symbol['value']==hi,'Actual same-owner HI label')
                delta=(dest-(region['start']+hi))&0xffffffff
                encoded_immediate=(delta&0xfff)<<20
            else:
                need(int(symbol['name'].rsplit('_',1)[1],16)==dest,'Exact original direct or literal destination')
                if dest in {r['start']for r in S['regions']}:
                    need(symbol['info']==18 and symbol['section']>0 and symbol['value']==0,'Genuine local target')
                else:
                    need(symbol['info']==16 and symbol['section']==0,'Explicit unresolved external target')
                if kind==23:
                    encoded_immediate=((dest-pc+0x800)&0xfffff000)
                else:
                    encoded_immediate=immediate(kind,dest-pc)
            mask[at:at+width]=bits.to_bytes(width,'little')
            val=int.from_bytes(actual[at:at+width],'little')
            patched[at:at+width]=((val&bits)|encoded_immediate).to_bytes(width,'little')
            relocations.append(dict(PC=pc,type=kind,target=dest,symbol=symbol['name']))
        need(all(((a^b)&m)==0 for a,b,m in zip(actual,original,mask)),f"{f['name']}: nonrelocation bits differ; actual={actual.hex()} original={original.hex()}")
        need(bytes(patched)==original,'Data-only original-VA relocation encoding equals full original bytes')
        total_i+=n;total_b+=len(actual)
    allocated={s['index']for s in e.sections if s['flags']&2 and s['size']}
    need(allocated==owned and len(e.relocations)==len(relocations),'All allocated bytes and relocations owned')
    sites=S['indirect_sites']
    for site in sites:
        carrier=fw[site['PC']-0x8000:site['PC']-0x8000+2]
        need(carrier.hex()==site['bytes'],'Original indirect-call/tail encoding')
    return dict(passed=True,code_bytes=total_b,instructions=total_i,FUNC=len(funcs),RELA=len(relocations),
                direct_control_RELA=sum(r['type']in(16,17,44,45)for r in relocations),
                PC_relative_RELA=sum(r['type']in(23,24)for r in relocations),
                UND=sorted(x['name']for x in globals_ if x['section']==0),
                native_object_sha256=sha(path),all_code_bytes_equal_after_data_only_original_VA_relocation=True,
                relocations=relocations,indirect_calls_and_tails=sites,provider_implementations_assumed=False,
                target_executed=False,ISA_emulated=False,HOST_model_executed=False,hardware_accessed=False,
                network=False,negative_cases_executed=0,firmware_BIN_generated=False,firmware_ready=False)

def inputs(llvm):
    paths=[Path(__file__),HERE/'spec-v2.json',ROOT/S['source'],ROOT/S['firmware'],ROOT/S['reader'],
           ROOT/S['curation_checker'],ROOT/S['author'],ROOT/S['source_map'],llvm.parent/'lib/clang/18/include/stdint.h']
    paths += [llvm/name for name in S['tools']]
    return {str(p):dict(bytes=p.stat().st_size,sha256=sha(p))for p in paths}

def inventory(folder):
    return {p.name:dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(folder.iterdir())if p.is_file()}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True)
    group=p.add_mutually_exclusive_group(required=True);group.add_argument('--trial');group.add_argument('--replay',type=Path)
    a=p.parse_args();llvm=a.tool_dir.resolve()
    for key in ('source','firmware','reader','curation_checker','author','source_map'):
        need(sha(ROOT/S[key])==S[key+'_sha256'],'Pinned '+key)
    for name,pin in S['tools'].items():
        need(sha(llvm/name)==pin,'Pinned local '+name)
    need(sha(llvm.parent/'lib/clang/18/include/stdint.h')==S['stdint_sha256'],'Pinned compiler header')
    C=runpy.run_path(str(ROOT/S['curation_checker']))
    need(S['flags']=={m:C['flags']({'profile':S['profile']},m)for m in ('c','cpp')},'Existing exact compiler profile')
    if a.replay:
        folder=a.replay.resolve();need(folder.parent==HERE/'build','Owned retained trial')
        saved=json.loads((folder/'measurement.json').read_bytes())
        need(saved['inputs']==portable(inputs(llvm),llvm),'All actual replay input identities')
        for mode in ('c','cpp'):
            need(saved['modes'][mode]['artifacts']==inventory(folder/mode),'Complete actual retained artifact inventory')
            need(saved['modes'][mode]['result']==audit_object(folder/mode/'native.o'),'Read-only native replay equality')
        print(json.dumps(dict(passed=True,mode='read-only-normal-artifact-replay',languages=['c','cpp'],target_executed=False)))
        return
    need(a.trial and Path(a.trial).name==a.trial,'Single owned trial name')
    out=HERE/'build'/a.trial;need(not out.exists(),'Create-only trial')
    before=inputs(llvm);report=dict(schema='TSL9-state-events-native-build-v2',inputs=before,modes={})
    for mode in ('c','cpp'):
        f=out/mode;f.mkdir(parents=True);commands=[];result={}
        recipes=[('compile',[str(llvm/'clang.exe')]+S['flags'][mode]+['-MD','-MF',str(f/'native.d'),'-MT','native.o','-c',str(ROOT/S['source']),'-o',str(f/'native.o')]),
                 ('IR',[str(llvm/'clang.exe')]+S['flags'][mode]+['-S','-emit-llvm',str(ROOT/S['source']),'-o',str(f/'native.ll')]),
                 ('read',[str(llvm/'llvm-objdump.exe'),'-dr','-t','-h',str(f/'native.o')])]
        try:
            for label,argv in recipes:
                c=subprocess.run(argv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
                (f/(label+'.log')).write_bytes(c.stdout);commands.append(dict(label=label,argv=argv,exit=c.returncode,log_sha256=sha(f/(label+'.log'))))
                need(c.returncode==0,'Actual '+label+' failed; retained log')
            result=audit_object(f/'native.o')
        except (ValueError,KeyError,IndexError) as error:
            result=dict(passed=False,error=str(error))
        report['modes'][mode]=dict(result=result,commands=commands,artifacts=inventory(f))
        print(json.dumps(dict(mode=mode,**{k:v for k,v in result.items()if k not in ('relocations','UND')})))
    need(before==inputs(llvm),'Inputs unchanged during compilation')
    (out/'measurement.json').write_bytes(encoded(portable(report,llvm)))
    need(all(v['result']['passed']for v in report['modes'].values()),'Normal native artifact audit failed; original trial retained')

if __name__=='__main__':
    try:
        main()
    except (ValueError,OSError) as e:
        print('FAIL: '+str(e),file=sys.stderr);sys.exit(1)
