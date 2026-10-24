#!/usr/bin/env python3
"""Compile and partially link complete original state/callback code; never execute it."""
import argparse
from collections import Counter
import hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
K=json.loads((HERE/'integration-v1.json').read_bytes())
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(rel):return runpy.run_path(str(ROOT/rel),run_name='positive_static_library')
Q=lib('experiments/tsl9-state-callbacks/verify-source-v1.py')
N=lib('experiments/tsl9-state-callbacks/build-v1.py')
P=lib('experiments/tsl9-dispatch-tables/integrate-v2.py')
V=lib('experiments/tsl9-record-providers/verify-providers-v1.py')
E=lib(N['S']['reader'])['ELF']
portable,encoded=N['portable'],N['encoded']
OUTPUT='UNRESOLVED-STARTUP-STATE-CALLBACKS.o'
def gm(e):
    rows=[s for s in e.symbols if s['info']>>4];m={s['name']:s for s in rows}
    need(len(m)==len(rows)and all(s['section']!=0xfff1 for s in rows),'Unique global roles; no ABS providers')
    return m
def parent(mode):return ROOT/K['parent_folder']/mode/K['parent_object']
def obj(provider,mode,out):
    if provider['unit']=='state-access':return out/'selection'/mode/'unit.o'
    return ROOT/K['curation_folder']/provider['unit']/mode/'curated/unit.o'
def inventory(folder):
    return {p.name:dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(folder.iterdir())if p.is_file()}
def selection_text():
    import re
    p=K['providers'][0];text=(ROOT/p['source']).read_text()
    for region in p['omitted_regions']:
        text,n=re.subn(r'(?:REGION|FRAME) void '+re.escape(region['name'])+r'\(void\)\n\{.*?^\}\n','',text,flags=re.S|re.M)
        need(n==1,'Exactly one complete duplicate definition removed')
    return '/* Derived from curated state_access.c; original 82A8-82D2 is supplied by the real parent. */\n'+text
def source_proof(llvm):
    for path,pin in K['source_pins'].items():need(sha(ROOT/path)==pin,'Pinned source/helper input '+path)
    need((ROOT/K['selected_state_source']).read_text()==selection_text(),'Exact full-definition-only C selection')
    need(K['new_code_bytes']==2388 and sum(r['bytes']for p in K['providers']for r in p['regions'])==2388,'Complete selected code scope')
    proof=Q['proof'](llvm)
    need(proof['total_source_comparisons']==140 and proof['total_source_objects']==280,'Complete current source and pointer-data proof')
    for name,pin in N['S']['tools'].items():need(sha(llvm/name)==pin,'Pinned actual tool')
    return proof

def selected_audit(mode,out):
    p=K['providers'][0]
    e=E(obj(p,mode,out))
    undefined=sorted(s['name']for s in gm(e).values()if not s['section'])
    fact=V['audit_object'](obj(p,mode,out),p['regions'],undefined)
    need(fact['code_bytes']==294 and fact['FUNC']==20 and fact['RELA']==10,'Exact nonduplicate state-access selection')
    need(undefined==['tsl9_state_external_13c4e'],'Exact selected true provider dependency')
    full=E(ROOT/K['curation_folder']/'state-access'/mode/'curated/unit.o');fm=gm(full)
    par=E(parent(mode));pm=gm(par)
    def refs(e,f):
        result=[]
        for r in e.relocations:
            if r['section']==f['section']and f['value']<=r['offset']<f['value']+f['size']:
                s=e.symbols[r['symbol']]
                result.append((r['offset']-f['value'],r['type'],r['addend'],s['name'],s['info'],s['other'],s['size']))
        return sorted(result)
    omitted_bytes=omitted_references=0
    for region in p['omitted_regions']:
        a=fm[region['name']];b=pm[region['name']]
        need(a['info']==b['info']==18 and a['size']==b['size']==region['bytes'],'Real retained duplicate owner')
        need(full.data(full.sections[a['section']])[a['value']:a['value']+a['size']]==par.data(par.sections[b['section']])[b['value']:b['value']+b['size']],'Every duplicate byte supplied by actual parent')
        ar,br=refs(full,a),refs(par,b)
        need(ar==br,'Every duplicate typed reference has the same real target role')
        omitted_bytes+=a['size'];omitted_references+=len(ar)
    need(omitted_bytes==42 and omitted_references==2,'Exact 42-byte/two-reference parent ownership')
    return dict(passed=True,selected=fact,duplicate_parent_bytes=42,duplicate_parent_references=2)

def audit_component(path,mode,out):
    e,p=E(path),E(parent(mode));em,pm=gm(e),gm(p)
    need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual non-executable RISC-V ET_REL')
    alloc={'.boot_code':(6,12224),'.initializer':(2,128),'.vectors':(2,328),'.feature_tables':(2,60)}
    need({s['name']for s in e.sections if s['flags']&2 and s['size']}==set(alloc),'Only exact genuine code and retained data')
    for name,(flags,size)in alloc.items():
        s=e.section(name);need(s['flags']==flags and s['type']==1 and s['size']==size and s['address']==0,'Exact diagnostic allocation')
    additions=[(q,E(obj(q,mode,out)))for q in K['providers']]
    names=set(pm)|set(K['aliases']);owners={};offsets={};at=9836;pieces=[p.data('.boot_code')]
    fw=(ROOT/N['S']['firmware']).read_bytes();new_i=0
    for provider,o in additions:
        m=gm(o);names.update(m)
        for region in provider['regions']:
            name=region['name'];f=m[name]
            need(name not in owners and not(name in pm and pm[name]['section']),'No duplicate code owner')
            need(f['info']==18 and f['value']==0 and f['size']==region['bytes'],'Actual full-size new code region')
            owners[name]=(o,f,region);offsets[name]=at;at+=f['size'];pieces.append(o.data(o.sections[f['section']]))
            raw=fw[region['start']-0x8000:region['end']-0x8000];off=0
            while off<len(raw):
                width=4 if raw[off]&3==3 else 2;need(off+width<=len(raw),'Whole original selected instruction');off+=width;new_i+=1
    need(at==12224 and len(owners)==287 and e.data('.boot_code')==b''.join(pieces),'Exact original parent9836B plus selected2388B compiled carriers')
    for name in ('.initializer','.vectors','.feature_tables'):
        need(e.data(name)==p.data(name),'All parent data and relative-table carriers unchanged')
    need(set(em)==names,'Exact merged definition/dependency/alias inventory')
    for name,f in pm.items():
        actual=em[name]
        if f['section']:
            need((actual['info'],actual['other'],actual['size'],actual['value'],e.sections[actual['section']]['name'])==(f['info'],f['other'],f['size'],f['value'],p.sections[f['section']]['name']),'Every retained code/data/alias owner')
        elif name not in owners and name not in K['aliases']:
            need(actual['section']==actual['value']==actual['size']==0 and actual['info']==16,'Every other genuine parent gap remains explicit')
    for name,(o,f,region)in owners.items():
        s=em[name]
        need((s['info'],s['other'],s['size'],s['value'],e.sections[s['section']]['name'])==(18,0,f['size'],offsets[name],'.boot_code'),'Every new real code owner/extent')
    for alias,target in K['aliases'].items():
        a,b=em[alias],em[target]
        need(b['info']==18 and b['size']>0 and e.sections[b['section']]['name']=='.boot_code','Alias target is actual nonzero code')
        need(a['info']==18 and a['size']==a['other']==0 and a['section']==b['section']and a['value']==b['value'],'Genuine entry alias; no stub or ABS address')
        need(int(alias.rsplit('_',1)[1],16)==int(target.rsplit('_',1)[1],16),'Alias preserves literal original entry PC')
    expected=Counter()
    for o,is_new in [(p,False)]+[(v,True)for _,v in additions]:
        m=gm(o)
        for rel in o.relocations:
            s=o.symbols[rel['symbol']]
            if s['info']>>4:
                target=em[s['name']];section=e.sections[target['section']]['name']if target['section']else''
                role=(target['name'],target['info'],target['other'],target['size'],section,target['value'])
            elif is_new:
                candidates=[v for v in m.values()if v['info']==18 and v['section']==s['section']and v['value']<=s['value']<v['value']+v['size']]
                need(len(candidates)==1 and s['info']==0 and s['size']==s['other']==0,'One real code owner for local PC-relative anchor')
                owner=candidates[0]
                role=(s['name'],s['info'],s['other'],s['size'],'.boot_code',offsets[owner['name']]+s['value']-owner['value'])
            else:
                need(s['section']>0 and s['section']!=0xfff1,'Retained genuine local reference')
                role=(s['name'],s['info'],s['other'],s['size'],p.sections[s['section']]['name'],s['value'])
            if is_new:
                candidates=[v for v in m.values()if v['info']==18 and v['section']==rel['section']and v['value']<=rel['offset']<v['value']+v['size']]
                need(len(candidates)==1,'One real source owner for each new relocation')
                owner=candidates[0];section='.boot_code';off=offsets[owner['name']]+rel['offset']-owner['value']
            else:
                section=p.sections[rel['section']]['name'];off=rel['offset']
            expected[(section,off,rel['type'],rel['addend'],role)]+=1
    actual=Counter()
    for rel in e.relocations:
        s=e.symbols[rel['symbol']];section=e.sections[s['section']]['name']if s['section']else''
        role=(s['name'],s['info'],s['other'],s['size'],section,s['value'])
        actual[(e.sections[rel['section']]['name'],rel['offset'],rel['type'],rel['addend'],role)]+=1
    need(actual==expected and len(e.relocations)==807,'All807 inherited/new global/local/data typed-reference roles')
    undefined=sorted(n for n,s in em.items()if not s['section'])
    need(undefined==K['remaining_undefined']and len(undefined)==79,'Exact79 genuine remaining providers')
    fs=[s for s in em.values()if s['info']==18 and s['section']]
    need(sum(bool(s['size'])for s in fs)==1070 and sum(not s['size']for s in fs)==54,'1070 real regions and54 genuine aliases')
    return dict(passed=True,mode=mode,code_bytes=12224,original_code_instructions=3461+new_i,new_code_bytes=2388,new_code_instructions=new_i,
        data_bytes=516,FUNC=1070,true_entry_aliases=54,new_true_entry_aliases=28,RELA=807,UND=undefined,
        native_object_sha256=sha(path),all_parent_code_data_and_table_carriers_unchanged=True,
        all_new_compiled_code_carriers_and_typed_reference_roles_preserved=True,
        original42B_and_two_controls_deduplicated_to_actual_parent=True,whole_state_events1308B_retained=True,
        getter_and_common_notify_dependencies_bound=True,original_address_placement_proved=False,
        memory_ownership_proved=False,private_ABI_proved=False,physical_MCU_ROM_IRQ_OTA_proved=False,
        executable=False,ABS_providers=0,no_stub_added=True,firmware_BIN_generated=False,firmware_ready=False,
        target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False,negative_cases_executed=0)

def inputs(llvm,out):
    paths={Path(__file__),HERE/'integration-v1.json',HERE/'joined-v1.ld',ROOT/K['selected_state_source']}
    paths.update(Path(p)for p in Q['inputs'](llvm))
    paths.update(ROOT/p for p in K['source_pins'])
    for mode in ('c','cpp'):
        paths.add(parent(mode))
        paths.update(obj(p,mode,out)for p in K['providers'])
    return {str(p):dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(paths)}
def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--tool-dir',type=Path,required=True)
    g=a.add_mutually_exclusive_group(required=True);g.add_argument('--output',type=Path);g.add_argument('--replay',type=Path)
    args=a.parse_args();llvm=args.tool_dir.resolve();out=(args.replay or args.output).resolve()
    need(out.parent==HERE/'build','Owned native output directory')
    proof=source_proof(llvm)
    C=lib('scripts/verify-curated-source.py');flags={m:C['flags']({'profile':'ring-bank'},m)for m in ('c','cpp')}
    if args.replay:
        need(out.is_dir(),'Actual retained output')
        record=json.loads((out/'measurement.json').read_bytes())
        need(record['source_proof']==proof and record['inputs']==portable(inputs(llvm,out),llvm),'All actual producer inputs/source proof unchanged')
        for mode in ('c','cpp'):
            f=out/'selection'/mode;j=record['selection'][mode]
            need(j['artifacts']==inventory(f)and j['audit']==selected_audit(mode,out),'Exact retained selection artifact audit')
            need(j['dependencies']==portable(C['dependencies'](f,'origin',llvm.parent/'lib/clang/18'),llvm),'All actual selection dependencies unchanged')
            need(record['modes'][mode]['artifacts']==inventory(out/mode),'Whole retained component output inventory')
            need(record['modes'][mode]['result']==audit_component(out/mode/OUTPUT,mode,out),'Actual retained whole-component replay')
        print(json.dumps(dict(passed=True,mode='read-only-state-callback-integration-replay',code_bytes=12224,data_bytes=516,RELA=807,UND=79,firmware_ready=False)));return
    need(not out.exists(),'Create-only output')
    record=dict(schema='TSL9-state-callback-integration-build-v1',source_proof=proof,selection={},modes={})
    for mode in ('c','cpp'):
        f=out/'selection'/mode;f.mkdir(parents=True)
        argv=[str(llvm/'clang.exe')]+flags[mode]+['-MD','-MF',str(f/'unit.d'),'-MT','unit.o','-c',str(ROOT/K['selected_state_source']),'-o',str(f/'unit.o')]
        result=subprocess.run(argv,cwd=ROOT,capture_output=True,timeout=120);(f/'compile.log').write_bytes(result.stdout+result.stderr)
        need(result.returncode==0,'Selected actual C/C++ compilation failed; log retained')
        record['selection'][mode]=dict(argv=argv,exit=0,audit=selected_audit(mode,out),dependencies=portable(C['dependencies'](f,'origin',llvm.parent/'lib/clang/18'),llvm),artifacts=inventory(f))
    before=portable(inputs(llvm,out),llvm)
    for mode in ('c','cpp'):
        f=out/mode;f.mkdir();commands=[]
        for label,argv in [('link',[str(llvm/'ld.lld.exe'),'-r','--no-relax','-T',str(HERE/'joined-v1.ld'),str(parent(mode))]+[str(obj(p,mode,out))for p in K['providers']]+['-o',str(f/OUTPUT)]),('read',[str(llvm/'llvm-objdump.exe'),'-dr','-t','-h',str(f/OUTPUT)])]:
            p=subprocess.run(argv,cwd=ROOT,capture_output=True,timeout=120);(f/(label+'.log')).write_bytes(p.stdout+p.stderr);commands.append(dict(label=label,argv=argv,exit=p.returncode))
            need(p.returncode==0,'Actual native link/read failed; log retained')
        result=audit_component(f/OUTPUT,mode,out);(f/'verification.json').write_bytes(encoded(result))
        record['modes'][mode]=dict(result=result,commands=commands,artifacts=inventory(f))
        print(json.dumps({k:v for k,v in result.items()if k!='UND'}|dict(UND_count=len(result['UND']))))
    need(before==portable(inputs(llvm,out),llvm),'All actual inputs unchanged during native link')
    record['inputs']=before;(out/'measurement.json').write_bytes(encoded(portable(record,llvm)))
if __name__=='__main__':
    try:main()
    except Exception as e:
        msg=str(e)
        for p,t in [(ROOT,'$'+'{PROJECT_ROOT}'),(Path.home(),'$'+'{USERPROFILE}')]:
            msg=msg.replace(str(p),t).replace(p.as_posix(),t)
        print(json.dumps(dict(passed=False,error_type=type(e).__name__,reason=msg)),file=sys.stderr);sys.exit(1)
