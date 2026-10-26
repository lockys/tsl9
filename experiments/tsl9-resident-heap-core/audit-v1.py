#!/usr/bin/env python3
"""Audit two conditional SDK heap bodies and their nonloadable message composition."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
MESSAGE=ROOT/'experiments/tsl9-resident-message-api'
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(p),run_name='heap_candidate_static_library')
def composition(path,inputs,N):
    ELF=lib(ROOT/N['S']['reader'])['ELF']
    def facts(p):
        e=ELF(p);need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Nonloadable actual RISC-V ET_REL')
        allocated={s['name']:(s['flags'],e.data(s))for s in e.sections if s['flags']&2 and s['size']}
        symbols={s['name']:(s['info'],s['other'],e.sections[s['section']]['name'],s['value'],s['size'])for s in e.symbols if s['info']>>4 and s['section']}
        und=sorted(s['name']for s in e.symbols if s['info']>>4 and not s['section'])
        rel=sorted((e.sections[r['section']]['name'],r['offset'],r['type'],r['addend'],e.symbols[r['symbol']]['name'])for r in e.relocations)
        return allocated,symbols,und,rel
    alloc={};symbols={};rel=[];original_und=[]
    for p in inputs:
        a,s,u,r=facts(p);need(not set(alloc).intersection(a)and not set(symbols).intersection(s),'Distinct real message/heap definitions')
        alloc.update(a);symbols.update(s);rel+=r;original_und+=u
    actual=facts(path)
    need(actual==(alloc,symbols,[],sorted(rel)),'Partial link preserves every allocated byte,positive symbol and relocation; two genuine heap imports resolve')
    need(set(original_und)=={'tsl9_candidate_heap_allocate_20000040','tsl9_candidate_heap_release_20000110'},'Exactly the preceding two genuine heap imports')
    need(sum(len(b)for flags,b in alloc.values())==584 and len(symbols)==51 and len(rel)==37,'Exact four-body candidate composition')
    independent=lib(ROOT/'experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path)
    need(independent['passed'],'Independent complete ELF readers agree')
    return dict(passed=True,object_sha256=sha(path),CODE_bytes=584,instructions=207,positive_FUNC_regions=51,relocations=37,named_UND=[],resolved_named_heap_imports=2,
        every_input_CODE_byte_and_typed_relocation_retained=True,independent_readers=independent,
        raw_RAM_dependencies_provided=False,opaque_callback_provided=False,runtime_closed=False,
        actual_original_address_link_performed=False,linked_into_APP=False,new_BIN=False,firmware_ready=False)
def audit(llvm,link_trial=None):
    N=lib(HERE/'build-v1.py');N['pins'](llvm);EV=N['EV'];B=N['B']
    saved=json.loads((HERE/'build/native-v1/measurement.json').read_bytes())
    need(saved['inputs']==N['portable'](N['inputs'](llvm),llvm)and saved['candidate_contract']==N['candidate_contract'](),'All original heap proof inputs retained')
    native={}
    for mode in ['c','cpp']:
        f=HERE/'build/native-v1'/mode;job=saved['modes'][mode]
        need(job['artifacts']==N['inventory'](f)and job['dependencies']==N['portable'](N['dependencies'](f,llvm),llvm),'Actual object/log/dependency identities retained')
        native[mode]=N['audit_object'](f/'unit.o');need(native[mode]==job['result'],'Fresh native heap byte audit')
    need(native['c']['object_sha256']==native['cpp']['object_sha256'],'Identical heap C/C++ objects')
    previous=lib(MESSAGE/'audit-v1.py')['audit'](llvm)
    need(previous==json.loads((MESSAGE/'audit-result-v1.json').read_bytes()),'Preceding SDK message audit retained unchanged')
    ops={o['addr']:o for f in EV['selected_functions']for o in f['operations']}
    def at(pc,want):need(ops[pc]['opcode']==want,'Exact semantic evidence instruction '+hex(pc))
    for pc,want in [(0x2000004a,'lw s0, 524(a5)'),(0x2000004e,'sw zero, 524(a5)'),(0x20000052,'fence.i'),(0x2000005e,'sw s0, 524(a5)'),(0x20000066,'addi a5, a0, 3'),(0x2000006e,'andi a5, a5, -4'),(0x20000074,'li a4, 52'),(0x20000080,'lw a0, 404(a4)'),(0x20000088,'lw a3, 396(a4)'),(0x20000094,'lw a4, 544(a4)'),(0x2000009e,'li a0, 1'),(0x200000a0,'jalr a4'),(0x200000a2,'j 0x2000005a'),(0x200000a8,'lw a0, 400(a4)'),(0x200000ae,'qk.c.lhu a4, 6(a0)'),(0x200000b2,'qk.c.lhu a4, 4(a0)'),(0x200000c0,'li a6, 8'),(0x200000d2,'addi a2, a5, 8'),(0x200000dc,'qk.c.sh a4, 4(a2)'),(0x200000e8,'qk.c.sh a5, 4(a0)'),(0x200000f0,'qk.c.sh a1, 6(a0)'),(0x200000f4,'addi a0, a0, 8'),(0x20000100,'sw s0, 524(a5)'),(0x20000114,'lw a6, 524(a5)'),(0x20000118,'sw zero, 524(a5)'),(0x2000011c,'fence.i'),(0x20000122,'sw a6, 524(a5)'),(0x20000154,'qk.c.lhu a2, 6(a5)'),(0x20000162,'lbu a4, -92(a2)'),(0x20000168,'sb a4, -92(a2)'),(0x20000178,'sh zero, 6(a5)'),(0x200001ae,'lw a4, 0(a5)')]:at(pc,want)
    graphs=[]
    for f in EV['selected_functions']:
        local={o['addr']:o for o in f['operations']};pending=[(f['start'],False)];seen=set();returns=[];calls=[]
        while pending:
            pc,restored=pending.pop()
            if (pc,restored)in seen:continue
            need(pc in local,'Every candidate CFG position owned');seen.add((pc,restored));o=local[pc]
            if pc in [0x2000004e,0x20000118]:restored=False
            if pc in [0x2000005e,0x20000100,0x20000122]:restored=True
            if o['opcode']=='ret':returns.append(dict(PC=pc,local_restore_store_seen=restored));continue
            after=pc+o['size'];d=B['decode_control'](bytes.fromhex(o['bytes']),pc)
            if pc==0x200000a0:
                calls.append(dict(PC=pc,pointer_storage=0x20003220,callee_provided=False));nexts=[after]
            elif d:
                kind,target=d;need(kind in [16,44,45],'Only local jumps/branches besides the explicit callback')
                nexts=[target,after]if kind in [16,44]else[target]
            else:nexts=[after]
            for nxt in nexts:need(nxt in local,'No local instruction gap');pending.append((nxt,restored))
        need({pc for pc,state in seen}==set(local)and returns and all(v['local_restore_store_seen']for v in returns),'Complete local syntactic CFG; normal-return paths contain restore stores')
        graphs.append(dict(start=f['start'],end=f['end'],instructions=len(local),returns=returns,opaque_calls=calls,
            local_CFG_positions_closed_assuming_callback_returns=True,termination_proved=False,physical_restoration_guaranteed=False))
    need(sum(len(g['opaque_calls'])for g in graphs)==1,'One real opaque callback')
    other=ROOT/'analysis/wch-resident-candidate-2026-10-21/carrier/REFERENCE-CANDIDATE-ONLY-00040000-0006EC56.bin'
    need(sha(other)=='b02cf8ec6829425a558887bd6bc10d28ae1f0e2e9e1850333f0bab6088e9e941','Pinned second public SDK carrier')
    entry=json.loads((ROOT/'analysis/wch-resident-candidate-2026-10-21/resident-entry/contract.json').read_bytes())['entry']['raw_operands']
    need((entry['copy1_source'],entry['copy1_destination'])==(0x402f0,0x20000040),'Independent V1.40 copy bias')
    raw=other.read_bytes();versions=[]
    for f in EV['selected_functions']:
        a=N['original'](f['start'],f['end']);off=0x402f0+f['start']-0x20000040-0x40000;b=raw[off:off+len(a)]
        need(len(a)==len(b),'Complete bounded second SDK body')
        changed=[];normalized=bytearray(b)
        expected_changes={0x20000080,0x20000088,0x20000094,0x200000a8,0x200000c2,0x2000012c,0x20000134,0x20000162,0x20000168,0x20000170,0x2000017c,0x20000190,0x200001b8}
        for o in f['operations']:
            at=o['addr']-f['start'];left=a[at:at+o['size']];right=b[at:at+o['size']]
            if left==right:continue
            need(o['addr']in expected_changes and len(left)==4,'Only explicitly reviewed RAM immediate differences')
            x=int.from_bytes(left,'little');y=int.from_bytes(right,'little');opcode=x&127
            def signed(v):return v-4096 if v&2048 else v
            if opcode in [3,19]:
                mask=0xfffff;old=signed(x>>20);new=signed(y>>20)
            else:
                need(opcode==35,'One real S-type byte store');mask=0x01fff07f
                old=signed(((x>>25)<<5)|((x>>7)&31));new=signed(((y>>25)<<5)|((y>>7)&31))
            need(x&mask==y&mask and new-old==80,'Same opcode/registers; each RAM immediate differs by exactly +0x50')
            normalized[at:at+4]=left;changed.append(dict(PC=o['addr'],V131_immediate=old,V140_immediate=new,delta=80))
        need(bytes(normalized)==a and {v['PC']for v in changed}=={pc for pc in expected_changes if f['start']<=pc<f['end']},'All other helper bytes identical; no guessed normalization')
        versions.append(dict(start=f['start'],end=f['end'],bytes=len(a),raw_bytes_equal=a==b,different_byte_positions=sum(x!=y for x,y in zip(a,b)),V140_source_flash=off+0x40000,
            changed_immediate_instructions=changed,all_other_bytes_equal=True,all_changed_immediates_delta=80,installed_RAM_layout_proved=False))
    combined={};out=HERE/'build'/('composition-v1'if link_trial is None else link_trial)
    if link_trial:need(Path(link_trial).name==link_trial and not out.exists(),'Create-only nonloadable composition trial')
    for mode in ['c','cpp']:
        inputs=[MESSAGE/'build/native-v1'/mode/'unit.o',HERE/'build/native-v1'/mode/'unit.o'];f=out/mode
        if link_trial:
            f.mkdir(parents=True);argv=[str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(p)for p in inputs],'-o',str(f/'candidate.o')]
            p=subprocess.run(argv,capture_output=True,timeout=120);(f/'link.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8')
            need(p.returncode==0,'Candidate partial link failed; local log retained')
        combined[mode]=composition(f/'candidate.o',inputs,N)
    need(combined['c']['object_sha256']==combined['cpp']['object_sha256'],'Identical actual partial-link objects')
    return dict(schema='TSL9-public-SDK-heap-audit-v1',passed=True,SDK_candidate_only=True,native_results=native,local_CFG=graphs,composition=combined,
        raw_dependencies=EV['raw_dependencies'],opaque_transfers=EV['opaque_transfers'],candidate_contract=saved['candidate_contract'],SDK_version_comparison=versions,
        limits=dict(installed_ROM_identity_proved=False,physical_Xwchc_profile_proved=False,raw_RAM_dependencies_provided=False,opaque_callback_provided=False,runtime_closed=False,
            APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,linked_into_APP=False,new_BIN=False,firmware_ready=False,goal_complete=False),
        target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--link-trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        result=audit(a.tool_dir.resolve(),a.link_trial)
        if a.output:
            out=HERE/a.output;need(out.parent==HERE and not out.exists(),'Create-only portable audit receipt');out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(passed=True,CODE_bytes=420,instructions=145,local_CFG_bodies=len(result['local_CFG']),SDK_version_comparison=result['SDK_version_comparison'],composition={k:{a:b for a,b in v.items()if a!='independent_readers'}for k,v in result['composition'].items()},limits=result['limits'])))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
