"""Bind three actual table providers while retaining every measured CODE/DATA role."""
import argparse,hashlib,json,runpy,subprocess,sys
from collections import Counter
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OUTPUT='UNRESOLVED-EXPERIMENTAL-CENTRAL-TABLES.o'
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(ROOT/p),run_name='offline_table_component_library')
N=lib('experiments/tsl9-central-callback-tables/build-v1.py')
S=N['S'];E=lib(S['reader'])['ELF']
OLD=lib('experiments/tsl9-central-event-callbacks/integrate-v1.py')
def paths(mode):return [ROOT/S['parent_component']/mode/S['parent_object'],HERE/'build/native-v1'/mode/'unit.o']
def source_proof(llvm):
    prior=OLD['source_proof'](llvm)
    saved=json.loads((HERE/'build/native-v1/measurement.json').read_text())
    need(saved['inputs']==N['inputs'](llvm),'Every compiled DATA input unchanged')
    need(saved['static_audit']==N['static_audit'](),'Fresh original-cell and dispatcher contract')
    for mode in ['c','cpp']:
        parent,native=paths(mode)
        need(sha(parent)==S['parent_sha256'],'Exact previously measured code component')
        need(OLD['audit'](parent,mode)['passed'],'Fresh whole parent CODE/DATA/reference proof')
        need(N['audit_object'](native)==saved['modes'][mode],'Fresh exact 92-byte DATA object proof')
    return dict(passed=True,parent=prior,new_DATA_bytes=92,new_positive_OBJECTs=3,
                new_callback_relocations=5,curated_integration=False)
def audit(path,mode):
    ins=[E(p) for p in paths(mode)];out=E(path)
    maps=[N['globals_of'](e) for e in ins];pm,nm=maps;gm=N['globals_of'](out)
    need(out.header[0]==1 and out.header[1]==243 and not out.program_headers,'Nonloadable RV32 ET_REL')
    need(set(gm)==set(pm)|set(nm)==set(pm),'Existing named dependencies become real providers; no extra global names')
    allocations={}
    for e in ins:
        for sec in e.sections:
            if not (sec['flags']&2 and sec['size']):continue
            need(sec['name'] not in allocations,'Distinct actual allocations')
            allocations[sec['name']]=(sec['type'],sec['flags'],sec['size'],sec['align'])
            need(out.data(sec['name'])==e.data(sec),'Every parent and new DATA allocation byte retained')
    need({s['name']:(s['type'],s['flags'],s['size'],s['align']) for s in out.sections if s['flags']&2 and s['size']}==allocations,'Only original allocations plus selected table DATA')
    def role(v,e):return (v['name'],v['info'],v['other'],v['value'],v['size'],e.sections[v['section']]['name'] if v['section'] else '')
    for e,m in zip(ins,maps):
        for name,v in m.items():
            if v['section']:need(role(gm[name],out)==role(v,e),'Every real provider and alias retains exact storage/type')
            elif not gm[name]['section']:need(role(gm[name],out)==role(v,e),'Every remaining dependency stays explicit')
    expected=Counter()
    for e in ins:
        for r in e.relocations:
            target=e.symbols[r['symbol']]
            target_role=role(gm[target['name']],out) if target['info']>>4 else role(target,e)
            expected[(e.sections[r['section']]['name'],r['offset'],r['type'],r['addend'],target_role)]+=1
    actual=Counter((out.sections[r['section']]['name'],r['offset'],r['type'],r['addend'],role(out.symbols[r['symbol']],out)) for r in out.relocations)
    need(expected==actual and len(out.relocations)==4972,'All 4972 source/type/addend/actual target roles')
    provided={d['name'] for d in S['data_regions']}
    before={n for n,v in pm.items() if not v['section']};after={n for n,v in gm.items() if not v['section']}
    need(len(before)==9 and len(after)==6 and before-after==provided and not after-before,'Exactly three genuine DATA dependencies resolve')
    code=[v for v in gm.values() if v['section'] and v['info']==18 and v['size']]
    data=[v for v in gm.values() if v['section'] and v['info']==17 and v['size']]
    need(len(code)==5846 and sum(v['size'] for v in code)==66600,'All original and new CODE retained')
    need(len(data)==54 and sum(v['size'] for v in data)==3922,'Exactly three actual table objects add 92 bytes')
    labels={n for n,v in gm.items() if v['section'] and v['info']==17 and not v['size']}
    need(labels=={n for n,v in pm.items() if v['section'] and v['info']==17 and not v['size']} and len(labels)==6,'All six real DATA labels retained')
    need(sum(v['info']==18 and v['section'] and not v['size'] for v in gm.values())==71,'All actual CODE aliases retained')
    need(sum(s['size'] for s in out.sections if s['flags']&2)==70522,'Every allocated byte owned without added padding')
    bindings=[]
    for d in S['data_regions']:
        v=gm[d['name']];sec=out.sections[v['section']]
        need(v['info']==17 and v['size']==d['bytes'] and sec['name']==d['section'] and sec['flags']==2,'Every table is actual readonly OBJECT storage')
        for index,(target,name) in enumerate(zip(d['targets'],d['target_symbols'])):
            if not target:
                need(out.data(sec)[index*4:index*4+4]==bytes(4),'Original null callback cell retained')
                continue
            fn=gm[name]
            need(fn['info']==18 and fn['section'] and fn['size']>0 and out.sections[fn['section']]['flags']==6,'Every event/callback target has real positive CODE backing')
            if d['kind']=='callback-function-pointers':
                rows=[r for r in out.relocations if r['section']==sec['index'] and r['offset']==4*index]
                need(len(rows)==1 and rows[0]['type']==1 and rows[0]['addend']==0 and out.symbols[rows[0]['symbol']]['name']==name,'Every non-null callback uses the actual typed CODE relocation')
            else:
                value=int.from_bytes(out.data(sec)[4*index:4*index+4],'little',signed=True)
                need((d['start']+value)&0xffffffff==target,'Every signed event cell identifies its measured original CODE entry')
            bindings.append(dict(table=d['name'],index=index,original_target=target,CODE_provider=name,positive_CODE_bytes=fn['size'],callback_relocation=d['kind']=='callback-function-pointers'))
    need(len(bindings)==22,'All seventeen event cells and five non-null callback cells')
    comparison=lib('experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path)
    return dict(passed=True,CODE_bytes=66600,DATA_bytes=3922,new_DATA_bytes=92,positive_FUNC=5846,
                positive_DATA_OBJECTs=54,real_DATA_labels=6,true_CODE_aliases=71,RELA=4972,UND=sorted(after),
                resolved_DATA_providers=sorted(provided),table_CODE_bindings=bindings,
                all_prior_allocations_and_reference_roles_preserved=True,independent_readers=comparison,
                object_sha256=sha(path),unprovided_candidate_callback_CODE_targets=[],
                compiler_UND_is_not_complete_runtime_gap_inventory=True,original_coordinate_link_performed=False,
                curated_integration=False,formal_coverage_percent=89.03,installed_ROM_ABI_verified=False,
                original_declaration_extents_proved=False,target_executed=False,new_BIN=False,firmware_ready=False)
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tool-dir',type=Path,required=True);parser.add_argument('--trial',required=True)
    args=parser.parse_args();llvm=args.tool_dir.resolve()
    need(Path(args.trial).name==args.trial,'Single owned trial name')
    source=source_proof(llvm);out=HERE/'build'/args.trial;need(not out.exists(),'Create-only table-component trial')
    report=dict(source_proof=source,modes={})
    for mode in ['c','cpp']:
        folder=out/mode;folder.mkdir(parents=True)
        argv=[str(llvm/'ld.lld.exe'),'-m','elf32lriscv','-r','--no-relax','-o',str(folder/OUTPUT),*[str(p) for p in paths(mode)]]
        result=subprocess.run(argv,capture_output=True,timeout=60)
        log=result.stderr.decode('utf-8',errors='replace').replace(str(ROOT),'PROJECT_ROOT').replace(str(Path.home()),'USERPROFILE')
        (folder/'link.log').write_text(log,encoding='utf-8');need(result.returncode==0,'Partial link failed; local diagnostic retained')
        report['modes'][mode]=audit(folder/OUTPUT,mode)
    need(report['modes']['c']['object_sha256']==report['modes']['cpp']['object_sha256'],'Identical measured C/C++ components')
    (out/'measurement.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report['modes']['c'].items() if k!='table_CODE_bindings'}))
if __name__=='__main__':main()
