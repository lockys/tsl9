#!/usr/bin/env python3
"""Bind three complete registered callback functions C/C++ function bodies; no target execution."""
import argparse,hashlib,json,runpy,subprocess,sys
from collections import Counter
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
K=json.loads((HERE/'integration-v1.json').read_bytes())
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(rel):return runpy.run_path(str(ROOT/rel),run_name='positive_static_library')
Q=lib('experiments/tsl9-registered-callbacks/verify-source-v1.py')
N=lib('experiments/tsl9-registered-callbacks/build-v1.py')
E=lib(N['S']['reader'])['ELF']
portable,encoded=N['portable'],N['encoded']
OUTPUT='UNRESOLVED-STARTUP-REGISTERED-CALLBACKS.o'
def parent(mode):return ROOT/K['parent_folder']/mode/K['parent_object']
def native(mode):return ROOT/K['curation_folder']/K['unit']/mode/'curated/unit.o'
def gm(e):
    rows=[s for s in e.symbols if s['info']>>4];m={s['name']:s for s in rows}
    need(len(m)==len(rows)and all(s['section']!=0xfff1 for s in rows),'Unique globals; no ABS providers')
    return m
def inventory(folder):return {p.name:dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(folder.iterdir())if p.is_file()}
def source_proof(llvm):
    need(sha(ROOT/K['source_proof'])==K['source_proof_sha256'],'Pinned complete source extension receipt')
    proof=Q['proof'](llvm)
    need(proof['total_source_comparisons']==186 and proof['total_source_objects']==372,'Current complete source proof')
    for mode in ('c','cpp'):
        need(sha(parent(mode))==K['parent_sha256'],'Actual retained startup component')
        facts=N['audit_object'](native(mode))
        need(facts==proof['modes'][mode]['registered_callbacks'],'Actual curated3220B registered callback original-byte audit')
    return proof
def audit_component(path,mode):
    p,o,e=E(parent(mode)),E(native(mode)),E(path);pm,om,em=gm(p),gm(o),gm(e)
    need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual non-executable RISC-V ET_REL')
    alloc={'.boot_code':(6,26416),'.initializer':(2,128),'.vectors':(2,328),'.feature_tables':(2,60),'.callback_constants':(2,62),'.callback_flow_constants':(2,96),'.incoming_constants':(2,40)}
    need({s['name']for s in e.sections if s['flags']&2 and s['size']}==set(alloc),'Only genuine code and exact readonly allocations')
    for name,(flags,size)in alloc.items():
        s=e.section(name);need((s['type'],s['flags'],s['address'],s['size'])==(1,flags,0,size),'Exact diagnostic section extent')
    need(e.section('.callback_flow_constants')['align']==4,'Actual readonly data alignment')
    need(set(em)==set(pm)|set(om)|set(K['aliases']),'Exact actual global inventory')
    offsets={};pieces=[p.data('.boot_code')];at=23196
    for r in K['regions']:
        name=r['name'];f=om[name]
        need(name not in pm or not pm[name]['section'],'No duplicate genuine parent definition')
        need(f['info']==18 and f['size']==r['bytes']and f['value']==0,'Full actual new region')
        offsets[name]=at;pieces.append(o.data(o.sections[f['section']]));at+=f['size']
        actual=em[name]
        need((actual['info'],actual['other'],actual['size'],actual['value'],e.sections[actual['section']]['name'])==(18,0,f['size'],offsets[name],'.boot_code'),'Exact real code owner/extent')
    need(at==26416 and e.data('.boot_code')==b''.join(pieces),'All parent23196B and new3220B compiled code carriers preserved')
    for section in ('.initializer','.vectors','.feature_tables','.callback_constants','.callback_flow_constants','.incoming_constants'):need(e.data(section)==p.data(section),'Every retained data/table carrier unchanged')
    need(set(K['resolved_providers'])=={r['name']for r in K['regions']if r['name']in pm and not pm[r['name']]['section']},'Exactly three genuine original pending entries')
    for provider in K['resolved_providers']:
        region=next(r for r in K['regions']if r['name']==provider)
        need(pm[provider]['section']==0 and region['start']==int(provider.rsplit('_',1)[1],16),'Genuine body at the original unresolved entry PC')
    for name,f in pm.items():
        a=em[name]
        if f['section']:
            need((a['info'],a['other'],a['size'],a['value'],e.sections[a['section']]['name'])==(f['info'],f['other'],f['size'],f['value'],p.sections[f['section']]['name']),'Every retained code/data/alias role unchanged')
        elif name not in K['aliases']and name not in om:
            need(a['info']==16 and a['section']==a['value']==a['size']==0,'Every other true parent dependency remains explicit')
    for alias,target in K['aliases'].items():
        a,t=em[alias],em[target]
        need(t['info']==18 and t['size']>0 and e.sections[t['section']]['name']=='.boot_code','Alias target is genuine code')
        need(a['info']==18 and a['other']==a['size']==0 and a['section']==t['section']and a['value']==t['value'],'Exact real-entry alias; no stub')
        need(int(alias.rsplit('_',1)[1],16)==int(target.rsplit('_',1)[1],16),'Original entry PC identity')
    expected=Counter()
    for source,is_new in [(p,False),(o,True)]:
        m=gm(source)
        for rel in source.relocations:
            s=source.symbols[rel['symbol']]
            if s['info']>>4:
                t=em[s['name']];role=(t['name'],t['info'],t['other'],t['size'],e.sections[t['section']]['name']if t['section']else'',t['value'])
            elif is_new:
                candidates=[x for x in m.values()if x['info']==18 and x['section']==s['section']and x['value']<=s['value']<x['value']+x['size']]
                need(len(candidates)==1 and s['info']==s['other']==s['size']==0,'Single real owner of local HI anchor')
                owner=candidates[0];role=(s['name'],0,0,0,'.boot_code',offsets[owner['name']]+s['value']-owner['value'])
            else:
                need(s['section']>0 and s['section']!=0xfff1,'True retained local reference')
                role=(s['name'],s['info'],s['other'],s['size'],p.sections[s['section']]['name'],s['value'])
            if is_new:
                candidates=[x for x in m.values()if x['section']==rel['section']and x['size']and x['value']<=rel['offset']<x['value']+x['size']]
                need(len(candidates)==1,'One true code/data source owner per new reference')
                owner=candidates[0]
                need(owner['info']==18,'Every new relocation source is genuine code; no new data')
                section='.boot_code';offset=offsets[owner['name']]+rel['offset']-owner['value']
            else:section=p.sections[rel['section']]['name'];offset=rel['offset']
            expected[(section,offset,rel['type'],rel['addend'],role)]+=1
    actual=Counter()
    for rel in e.relocations:
        s=e.symbols[rel['symbol']];role=(s['name'],s['info'],s['other'],s['size'],e.sections[s['section']]['name']if s['section']else'',s['value'])
        actual[(e.sections[rel['section']]['name'],rel['offset'],rel['type'],rel['addend'],role)]+=1
    need(actual==expected and len(e.relocations)==1726,'All1726 global/local/code/data typed-reference roles preserved')
    undefined=sorted(n for n,f in em.items()if not f['section'])
    need(undefined==K['remaining_undefined']and len(undefined)==115,'Exactly115 true remaining provider symbols')
    parent_undefined={n for n,f in pm.items()if not f['section']}
    need(sorted(set(undefined)-parent_undefined)==K['new_undefined'] and len(K['new_undefined'])==28,'Exactly28 newly exposed code/static-address dependencies;no substitutes')
    fs=[f for f in em.values()if f['info']==18 and f['section']]
    need(sum(bool(f['size'])for f in fs)==2280 and sum(not f['size']for f in fs)==71,'2280 genuine code regions and71 retained true aliases')
    return dict(passed=True,mode=mode,code_bytes=26416,original_instructions=9078,data_bytes=714,FUNC=2280,true_aliases=71,RELA=1726,UND=undefined,
        new_code_bytes=3220,new_original_instructions=1032,new_data_bytes=0,new_true_aliases=0,
        resolved_original_providers=K['resolved_providers'],no_new_external_providers=False,new_external_providers=K['new_undefined'],
        all_parent23196B_code_and714B_data_preserved=True,all_new_code_carriers_and_reference_roles_preserved=True,
        three_registered_callback_functions_are_genuine_code=True,native_object_sha256=sha(path),
        original_arithmetic_frames_ROM_and_callback_ports_retained=True,concurrent_state_semantics_proved=False,
        original_address_placement_proved=False,private_ABI_proved=False,
        physical_MCU_ROM_RAM_IRQ_OTA_proved=False,executable=False,ABS_providers=0,no_stub_added=True,
        target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False,
        negative_cases_executed=0,firmware_BIN_generated=False,firmware_ready=False)

def inputs(llvm):
    paths={Path(__file__),HERE/'integration-v1.json',HERE/'joined-v1.ld',ROOT/K['source_proof']}
    paths.update(Path(x)for x in Q['inputs'](llvm))
    for mode in ('c','cpp'):paths.update([parent(mode),native(mode)])
    return {str(p):dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(paths)}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True)
    g=p.add_mutually_exclusive_group(required=True);g.add_argument('--output',type=Path);g.add_argument('--replay',type=Path)
    a=p.parse_args();llvm=a.tool_dir.resolve();proof=source_proof(llvm);before=portable(inputs(llvm),llvm);out=(a.replay or a.output).resolve()
    need(out.parent==HERE/'build','Owned output path')
    if a.replay:
        saved=json.loads((out/'measurement.json').read_bytes())
        need(saved['inputs']==before and saved['source_proof']==proof,'Actual inputs/source proof unchanged')
        for mode in ('c','cpp'):
            need(saved['modes'][mode]['artifacts']==inventory(out/mode),'Whole retained component artifact inventory')
            need(saved['modes'][mode]['result']==audit_component(out/mode/OUTPUT,mode),'Actual native integration replay')
        print(json.dumps(dict(passed=True,mode='read-only-registered-callbacks-integration-replay',code_bytes=26416,data_bytes=714,RELA=1726,UND=115,firmware_ready=False)));return
    need(not out.exists(),'Create-only native output');record=dict(schema='TSL9-registered-callbacks-integration-build-v1',inputs=before,source_proof=proof,modes={})
    for mode in ('c','cpp'):
        f=out/mode;f.mkdir(parents=True);commands=[]
        for label,argv in [('link',[str(llvm/'ld.lld.exe'),'-r','--no-relax','-T',str(HERE/'joined-v1.ld'),str(parent(mode)),str(native(mode)),'-o',str(f/OUTPUT)]),('read',[str(llvm/'llvm-objdump.exe'),'-dr','-t','-h',str(f/OUTPUT)])]:
            proc=subprocess.run(argv,cwd=ROOT,capture_output=True,timeout=120);(f/(label+'.log')).write_bytes(portable((proc.stdout+proc.stderr).decode('utf8','replace'),llvm).encode('utf8'));commands.append(dict(label=label,argv=argv,exit=proc.returncode))
            need(proc.returncode==0,'Actual link/read failed; log retained')
        result=audit_component(f/OUTPUT,mode);(f/'verification.json').write_bytes(encoded(result))
        record['modes'][mode]=dict(result=result,commands=commands,artifacts=inventory(f))
        print(json.dumps({k:v for k,v in result.items()if k!='UND'}|dict(UND_count=len(result['UND']))))
    need(before==portable(inputs(llvm),llvm),'All actual producer inputs unchanged')
    (out/'measurement.json').write_bytes(encoded(portable(record,llvm)))
if __name__=='__main__':
    try:main()
    except Exception as e:
        msg=str(e)
        for p,t in [(ROOT,'$'+'{PROJECT_ROOT}'),(Path.home(),'$'+'{USERPROFILE}')]:msg=msg.replace(str(p),t).replace(p.as_posix(),t)
        print(json.dumps(dict(passed=False,error_type=type(e).__name__,reason=msg)),file=sys.stderr);sys.exit(1)
