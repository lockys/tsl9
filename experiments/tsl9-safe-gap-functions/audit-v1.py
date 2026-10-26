#!/usr/bin/env python3
"""Read-only native-object and conservative candidate-body CFG audit; no target execution."""
import argparse,hashlib,json,runpy
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def need(ok,label):
    if not ok:raise ValueError(label)

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def audit(llvm):
    M=runpy.run_path(str(HERE/'build-v1.py'),run_name='native_library')
    S=M['S'];B=M['B'];saved=json.loads((HERE/'build/native-v1/measurement.json').read_bytes())
    need(saved['inputs']==M['portable'](M['inputs'](llvm),llvm),'Every actual native input retained')
    results={}
    for mode in ['c','cpp']:
        folder=HERE/'build/native-v1'/mode;job=saved['modes'][mode]
        need(job['artifacts']==M['inventory'](folder),'Complete retained output inventory')
        need(job['dependencies']==M['portable'](M['dependencies'](folder,llvm),llvm),'Exact compiler dependency closure')
        result=M['audit_object'](folder/'unit.o')
        need(result==job['result'],'Fresh two-reader native-object audit')
        results[mode]=result
    need(results['c']['native_object_sha256']==results['cpp']['native_object_sha256'],'Actual C/C++ object identity')
    evidence=json.loads((ROOT/S['reference_candidate']).read_bytes())
    fs=evidence['selected_functions'];ops={o['addr']:o for f in fs for o in f['operations']}
    by_region={r['name']:r for r in S['regions']}
    external={x['target_PC']:x['target']for x in S['controls']+S['PC_relative_pairs']if x['target']in S['undefined']}
    provider=M['elf'](ROOT/S['provider_elf'])
    for pc,name in external.items():
        ss=[s for s in provider.symbols if s['name']==name]
        need(len(ss)==1 and ss[0]['value']==pc and ss[0]['info']==18 and ss[0]['size']>0 and ss[0]['section']not in [0,0xfff1],'Real measured positive external FUNC provider')
    graph=[];indirect=[];direct=[]
    for f in fs:
        local={o['addr']:o for o in f['operations']};pending=[f['start']];seen=set();terminals=[]
        while pending:
            pc=pending.pop()
            if pc in seen:continue
            need(pc in local,'Every traversed position is a whole original instruction in this candidate body')
            seen.add(pc);o=local[pc];raw=bytes.fromhex(o['bytes']);after=pc+o['size'];d=B['decode_control'](raw,pc)
            successors=[]
            if d:
                kind,target=d;word=int.from_bytes(raw,'little')
                call=(kind==17 and (word>>7)&31==1)or(kind==45 and(word>>13)&7==1)
                conditional=kind in [16,44]
                direct.append(dict(PC=pc,target_PC=target,kind=kind,call=call,conditional=conditional))
                if conditional:
                    need(target in local,'Conditional target stays inside actual body');successors=[target,after]
                elif call:
                    need(target in ops or target in external,'Call target is a selected instruction or measured provider');successors=[after]
                elif target in local:successors=[target]
                else:
                    need(target in external or target in {v['start']for v in fs},'Tail ends at an actual formal entry')
                    terminals.append(dict(PC=pc,kind='direct-tail',target_PC=target))
            elif o['opcode']=='ret':terminals.append(dict(PC=pc,kind='return'))
            elif o['opcode'].startswith('jalr '):
                indirect.append(dict(PC=pc,kind='opaque-indirect-call',normal_return_position=after,runtime_target_proved=False));successors=[after]
            elif o['opcode'].startswith('jr '):
                indirect.append(dict(PC=pc,kind='opaque-indirect-tail',runtime_target_proved=False));terminals.append(dict(PC=pc,kind='opaque-indirect-tail'))
            else:successors=[after]
            for target in successors:
                need(target in local,'No ordinary sequential or call-return position gap');pending.append(target)
        need(seen==set(local),'Every selected instruction statically reachable from the candidate entry, assuming calls return')
        need(terminals,'Candidate body has a real return or explicit tail')
        graph.append(dict(entry=f['start'],end=f['end'],original_instructions=len(local),static_positions=len(seen),terminals=terminals,invocation_proved=False))
    need(len(direct)==43 and len(indirect)==7,'Exact43 direct and seven non-return indirect transfers')
    need(sum(x['kind']=='opaque-indirect-call'for x in indirect)==3,'Three opaque indirect calls')
    need(sum(x['kind']=='opaque-indirect-tail'for x in indirect)==4,'Four opaque indirect tails')
    def at(pc,op):need(ops[pc]['opcode']==op,'Observed instruction '+hex(pc))
    for pc in [0x13660,0x136d0,0x13740]:
        at(pc,'lui a5, 0x40');at(pc+4,'lw a5, 112(a5)')
    for pc in [0x13670,0x136e0,0x13750]:at(pc,'li a0, 12')
    for pc,op in [(0x13676,'li a5, -85'),(0x136e6,'li a5, -70'),(0x1375c,'li a5, -71'),(0x1367e,'addi a5, gp, 96'),(0x136ee,'addi a5, gp, 88'),(0x1376c,'addi a5, gp, 104'),(0x13772,'addi a5, gp, 100'),(0x16c72,'addi a5, a0, -1'),(0x16c76,'andi a5, a5, 255'),(0x16c7a,'li a4, 1'),(0x16c7c,'bltu a4, a5, 0x16cc2'),(0x14cd2,'jal ra, 0x821e'),(0x14cda,'jal ra, 0x821e'),(0x14ce6,'jal ra, 0x821e'),(0x14cec,'jal ra, 0x829e')]:at(pc,op)
    for pc in [0x136be,0x1372e,0x137ae,0x13f5c]:at(pc,'lw t1, 104(a5)')
    for pc in [0x136a4,0x13714,0x13794]:
        ps=[x for x in S['PC_relative_pairs']if x['PC']==pc]
        need(len(ps)==1 and ps[0]['target_PC']==0x13f36,'All three record wrappers load the measured shared callback address')
    manifest=ROOT/'src/source-manifest.json';m=json.loads(manifest.read_bytes())
    need(len(m['files'])==158,'Formal source inventory unchanged')
    return dict(schema='TSL9-safe-gap-native-static-audit-v1',passed=True,
        source=S['source'],source_sha256=sha(ROOT/S['source']),checkers={p.relative_to(ROOT).as_posix():sha(p)for p in [HERE/'audit-v1.py',HERE/'build-v1.py',HERE/'derive-v1.py']},
        native_results=results,candidate_bodies=10,code_bytes=764,original_instructions=288,positive_native_FUNC_regions=64,
        direct_controls=direct,non_return_indirect_transfers=indirect,body_graph=graph,typed_CODE_address_pairs=S['PC_relative_pairs'],
        all_764_original_VA_encoded_bytes_equal=True,actual_original_address_link_placement_proved=False,
        external_positive_FUNC_providers=len(external),new_DATA_provided=False,
        formal_source_C_H_files=158,formal_source_manifest_sha256=sha(manifest),formal_curated_byte_coverage_percent=94.54,
        experimental_bytes_added_to_formal_coverage=False,all_candidate_runtime_invocations_proved=False,
        physical_ROM_identity_and_ABI_proved=False,hardware_startup_RAM_IRQ_OTA_compatibility_proved=False,
        target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False,
        negative_cases_executed=0,firmware_BIN_generated=False,firmware_ready=False,goal_complete=False)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--output',type=Path)
    a=p.parse_args();result=audit(a.tool_dir.resolve())
    if a.output:
        output=a.output if a.output.is_absolute() else HERE/a.output
        need(output.resolve().parent==HERE and not output.exists(),'Create-only experiment receipt')
        output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items()if k not in ['native_results','body_graph','direct_controls','non_return_indirect_transfers','typed_CODE_address_pairs','checkers']}))

if __name__=='__main__':
    try:main()
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:
            message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
