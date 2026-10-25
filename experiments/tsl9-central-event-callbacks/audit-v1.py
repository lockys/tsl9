"""Static control-boundary proof over original bytes; no target execution."""
import hashlib,json,runpy
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def need(ok,label):
    if not ok:raise ValueError(label)
def audit():
    spec=json.loads((HERE/'spec-v1.json').read_text())
    evidence=json.loads((HERE/'evidence-v1.json').read_text())
    fw=(ROOT/spec['firmware']).read_bytes()
    need(hashlib.sha256(fw).hexdigest()==spec['firmware_sha256'],'Original image identity')
    shared=ROOT/'experiments/tsl9-original-startup/build-v1.py'
    need(hashlib.sha256(shared.read_bytes()).hexdigest()=='1f6e3673c24a5d85c62d55ec8d8390b80225577010d81c8aba5c4b6750e208b5','Pinned control decoder')
    decoder=runpy.run_path(str(shared),run_name='static_control_library')['decode_control']
    old_root=ROOT/'experiments/tsl9-central-callback-leaves'
    old_summary=json.loads((old_root/'summary.json').read_text())
    need(hashlib.sha256((old_root/'audit-v1.py').read_bytes()).hexdigest()==old_summary['checkers']['audit-v1.py'],'Pinned original table guard checker')
    tables=runpy.run_path(str(old_root/'audit-v1.py'),run_name='static_guard_library')['audit']()
    table_targets={int(x,16) for x in tables['event_table_targets']}
    functions=evidence['selected_functions'];entries={f['start'] for f in functions}
    formal=json.loads((ROOT/'experiments/tsl9-original-layout/build/callback-prefix-data-v2/c/layout-map.json').read_text())['owners']
    formal_entries={s['original_PC'] for s in formal if s['info']==18}
    total=0;results=[]
    for f in functions:
        ops={o['addr']:o for o in f['operations']};at=f['start']
        for pc,o in sorted(ops.items()):
            raw=bytes.fromhex(o['bytes']);need(pc==at and len(raw)==o['size'],'Whole contiguous original instruction')
            need(raw==fw[pc-0x8000:pc-0x8000+len(raw)],'Every original instruction byte')
            need(not any(s['original_PC']<=pc<s['original_PC']+s['bytes'] for s in formal),'No duplicate formal ownership')
            at+=len(raw)
        need(at==f['end'],'Exact candidate function end')
        queue=[f['start']];seen=set();tails=[];opaque=[];calls=[]
        while queue:
            pc=queue.pop()
            if pc in seen:continue
            need(pc in ops,'Control target is an actual instruction boundary')
            seen.add(pc);o=ops[pc];nextpc=pc+o['size'];kind=o['type']
            successors=[]
            if kind in ('call','ucall'):
                successors=[nextpc]
                calls.append(dict(PC=pc,direct_target=o.get('jump'),indirect=kind=='ucall'))
            elif kind in ('jmp','cjmp'):
                edge=decoder(bytes.fromhex(o['bytes']),pc)
                need(edge is not None and edge[1]==o['jump'],'Independent original direct-control target')
                target=edge[1]
                if target in ops:successors.append(target)
                else:
                    need(kind=='jmp' and target in entries|formal_entries,'Explicit tail to another selected/formal entry')
                    tails.append(dict(PC=pc,target=target))
                if kind=='cjmp':successors.append(nextpc)
            elif kind=='rjmp':
                if pc==0x1156e:successors=sorted(table_targets)
                else:
                    need(pc in [0x11264,0x1152a],'Exactly retained opaque register tail boundaries')
                    opaque.append(dict(PC=pc,opcode=o['opcode']))
            elif kind!='ret':successors=[nextpc]
            queue.extend(successors)
        need(seen==set(ops),'Every retained instruction reachable in conservative static function CFG')
        total+=len(seen)
        results.append(dict(start=f['start'],end=f['end'],bytes=f['end']-f['start'],instructions=len(ops),
                            CFG_reached_instructions=len(seen),direct_tails=tails,opaque_register_tails=opaque,calls=calls))
    need(total==645,'All 645 original instructions accounted for')
    need(next(f for f in results if f['start']==0x11266)['direct_tails']==[{'PC':0x11352,'target':0x11252}],'Actual shared-tail dependency retained')
    return dict(passed=True,functions=results,original_code_bytes=1938,original_instructions=645,
                CFG_kind='conservative static paths; no feasibility or global runtime proof',
                event_jump_table_entries=17,event_jump_table_targets=sorted(table_targets),
                event_jump_table_DATA_provided=False,typed_address_pairs=2,
                curated_integration=False,formal_coverage_percent=89.03,
                installed_ROM_ABI_verified=False,global_RAM_bounds_verified=False,target_executed=False,new_BIN=False)
if __name__=='__main__':print(json.dumps(audit()))
