"""Compile the new entry-order model; inspect all bytes without target execution."""
import argparse,hashlib,importlib.util,json,re,struct,types,uuid
from pathlib import Path
H=Path(__file__).resolve().parent
MODEL='experiments/tsl9-v4160-flash-entry-order'
OLD_RUNNER='dc0c966f057a0562f0d51a0289b9b24ce242d47bee0cd397d72fc12bc0a42013'
OLD_SEAL='455829d73f11aaea707c2a95e9c738b2939ee1ec47910c56d3dc70d21f261663'
PROGRAM_CHECKER='8896ae7d7ce7b59c2760099d493594cae43e49e177319cd6b78bf56b430eb73a'
CORE={'flash_native.c':'c2f85fd50a7def5ff4baf200415e9faa3f2a253dea51c6bc54ae6a139fef960b','flash_native.h':'b26fe2050e88708e7d18257841f5682ac49fcd4b402aac42ffc5aaae649dd7bd','native_io.h':'e0d58fdf1ae5ebc1f497a023443a4e6432f5cd75d987c691a2dcf68b3e64af7e'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,d):p.write_bytes((json.dumps(d,indent=2)+'\n').encode())
def need(v,m):
    if not v:raise ValueError(m)
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def case(root,slug):return next(p for p in (root/'analysis'/slug,root/'apk-analysis'/('tsl9-'+slug)) if p.is_dir())
def context(root,firmware=None):
    old=case(root,'v4160-flash-native-2026-10-22')/'implementation/verify_native.py';need(sha(old)==OLD_RUNNER,'immutable prior compiler/parser helper')
    old_seal=old.parent/'seal.json';need(sha(old_seal)==OLD_SEAL,'prior immutable implementation identity')
    profile=old.parent/'probe_native.py';expected=next(r for r in read(old_seal)['members'] if r['path']=='probe_native.py');need(sha(profile)==expected['sha256'],'unchanged original native compiler flag profile')
    N=module('entry_order_compile_helpers',old);N.MODEL=MODEL
    ctx=N.context(root,firmware);A=ctx['review'];program=case(root,'v4160-flash-entry-order-2026-10-22')/'ABI-review/program.py'
    need(sha(program)==PROGRAM_CHECKER,'independent100B program checker');Q=module('entry_order_program_contract',program)
    for n,pin in CORE.items():need(sha(root/MODEL/'src'/n)==pin,'frozen new native source '+n)
    def contract(name,body,relocations,decode):
        if name=='program':
            need(not relocations,'program has no hidden relocations');Q.check_program(body,decode);return A.raw_rows(body,decode)
        return A.native_contract(name,body,relocations,decode)
    ctx.update(legacy=N,old_patterns=A,program_checker=Q,review=types.SimpleNamespace(native_contract=contract))
    ctx['pins'].update({str(old_seal.resolve()):sha(old_seal),str(program.resolve()):sha(program),str(Path(__file__).resolve()):sha(Path(__file__))})
    return ctx
def static_checks(folder,ctx,observed_tools):
    N=ctx['legacy'];A=ctx['old_patterns'];E=ctx['ELF'];P=ctx['profile'];functions=N.disassembly_gate(folder,ctx);ir={};original=ctx['firmware'].read_bytes();controls=[];program_contract=None
    for address,(name,limit,allowed) in P.NAMES.items():
        e=E(folder/(name+'.o'));symbol=[s for s in e.symbols if s['index'] and s['info']&15==2 and s['size']]
        need(len(symbol)==1 and symbol[0]['name']==P.symbol(address),'one true public typed function '+name);s=symbol[0];body=e.function_bytes(s)
        need(e.kind==1 and e.flags==1,'ELF32 RV32 RVC ILP32 object');alloc=[x for x in e.sections if x['flags']&2 and x['size']]
        need(len(alloc)==1 and alloc[0]['index']==s['index'] and alloc[0]['size']==len(body) and alloc[0]['flags']==6,'one exact executable allocation, no writable/EH/hidden storage')
        und=sorted(x['name'] for x in e.symbols if not x['index'] and x['name']);expected=sorted(P.symbol(a) for a in P.NAMES if a!=0x9c0a) if name=='quarter' else []
        need(und==expected,'only five explicit quarter call dependencies')
        arch=re.search(rb'rv32[a-z0-9_]+',e.data(e.byname['.riscv.attributes']));need(arch and all(b'_'+x in arch.group() for x in (b'm',b'a',b'c',b'zicsr')) and not any(b'_'+x in arch.group() for x in (b'f',b'd',b'v')),'actual integer ISA attributes')
        text=(folder/(name+'.ll')).read_text(encoding='utf-8');ir[name]=ctx['program_checker'].check_program_ir(text) if name=='program' else A.ir_contract(name,text)
        if name=='program':program_contract=ctx['program_checker'].check_program(body,ctx['decode'])
        functions[name]['byte_identical_to_original']=body==original[address-0x8000:address-0x8000+limit]
        changed=bytearray(body);changed[0]^=0x10
        try:ctx['review'].native_contract(name,changed,e.relocations,ctx['decode'])
        except ValueError:controls.append(dict(function=name,offset=0,rejected=True))
        else:raise ValueError('raw native mutation accepted '+name)
    deps=N.dependency_gate(folder,ctx);linked=folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf';e=E(linked)
    need(e.kind==2 and e.flags==1 and struct.unpack_from('<I',e.raw,24)[0]==0x9c0a,'strict linked RV32 component entry')
    layout=A.linked_review(linked,folder,ctx['decode'],E,project_root=ctx['root'])
    # The reused checker proves generic allocation/JAL facts. Its old94B-tail label
    # is not used; this model separately requires every original extent occupied.
    layout.pop('remaining_program_tail_ownership_proved',None)
    need(all(f['bytes']==f['original_bytes'] for f in functions.values()) and sum(f['bytes'] for f in functions.values())==262,'all six original extents occupied by actual typed code, no padding')
    need((folder/'original-entry-component.ld').read_text(encoding='utf-8')==N.link_source(P),'exact original-entry layout source')
    probe=read(folder/'probe.json');need(probe['source']=={p.name:sha(p) for p in (ctx['root']/MODEL/'src').glob('*') if p.is_file()},'actual compile source snapshot')
    for row in probe['functions']:
        for c in row['commands']:
            need(c['exit']==0 and sha(folder/c['log'])==c['log_sha256'],'actual compile/disassembly log')
            if '-c' in c['argv'] or '-emit-llvm' in c['argv']:
                argv=c['argv'];flags=P.flags(row['address'],probe['mode']);need(argv[1:1+len(flags)]==flags and str(ctx['root']/MODEL/'src/flash_native.c') in argv,'unchanged exact native compiler profile/source')
    for c in probe['link_commands']:need(c['exit']==0 and sha(folder/c['log'])==c['log_sha256'],'actual strict link/disassembly log')
    for tool,meta in observed_tools.items():need(meta['before_sha256']==meta['after_sha256']==sha(Path(tool)),'unchanged actual LLVM tool')
    return dict(functions=functions,program_contract=program_contract,IR=ir,component_link=layout,native_dependencies=deps,raw_machine_controls=controls,allocated_function_bytes=262,instructions=99,unowned_original_program_tail_bytes=0,original_A0_memory_event_order=True,full_instruction_boundary_equivalence=False,pointwise_async_equivalence=False,nonreturn_physical_GPR_prefix_equivalence=False,full_image_integration=False,firmware_BIN_produced=False,hardware=False,OTA_ready=False)
def replay(root,receipt):
    receipt=Path(receipt).resolve();r=read(receipt);ctx=context(root);N=ctx['legacy'];folder=receipt.parent
    need(r['passed'] and r['runner_sha256']==sha(Path(__file__)) and r['source_sha256']==CORE,'current exact runner/core')
    need(r['input_pins']=={**ctx['pins'],**{n:v['before_sha256'] for n,v in r['observed_tools'].items()}},'exact source/checker/tool snapshot');N.stability(r['input_pins'])
    for n,meta in r['artifacts'].items():
        p=(folder/n).resolve();need(p.is_relative_to(folder) and p.stat().st_size==meta['bytes'] and sha(p)==meta['sha256'],'actual native artifact '+n)
    checks=static_checks(folder,ctx,r['observed_tools']);need(json.loads(json.dumps(checks))==r['checks'],'actual native proof replay')
    return dict(passed=True,receipt=str(receipt),sha256=sha(receipt),artifacts_checked=len(r['artifacts']),allocated_function_bytes=262,instructions=99,target_execution=False,full_image_integration=False)
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=H.parents[2]);p.add_argument('--tool-dir',type=Path);p.add_argument('--clang');p.add_argument('--linker');p.add_argument('--objdump');p.add_argument('--firmware',type=Path);p.add_argument('--language',choices=['c','cpp','both'],default='both');p.add_argument('--build-root',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
    if a.replay:print(json.dumps(replay(root,a.replay)));return
    ctx=context(root,a.firmware);N=ctx['legacy'];tools={k:N.resolve_tool(getattr(a,k),a.tool_dir,n) for k,n in [('clang','clang'),('linker','ld.lld'),('objdump','llvm-objdump')]};before={str(v):sha(v) for v in tools.values()};pins={**ctx['pins'],**before};N.stability(pins)
    base=a.build_root.resolve() if a.build_root else root/MODEL/'build'/('native-'+uuid.uuid4().hex);need(base.is_relative_to(root) and not base.exists(),'create-only build inside project');results=[]
    for mode in (['c','cpp'] if a.language=='both' else [a.language]):
        folder=base/mode;N.build(root,folder,ctx,tools,mode);observed={n:dict(before_sha256=h,after_sha256=sha(Path(n))) for n,h in before.items()};N.stability(pins);checks=static_checks(folder,ctx,observed);N.stability(pins)
        r=dict(schema='ID2966-flash-entry-order-native-v1',passed=True,mode=mode,runner_sha256=sha(Path(__file__)),source_sha256=CORE,input_pins=pins,observed_tools=observed,checks=checks,artifacts={p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in folder.rglob('*') if p.is_file()},target_execution=False,ISA_emulation=False,hardware=False,network=False,full_image_integration=False,firmware_BIN_produced=False,OTA_ready=False)
        receipt=folder/'verification.json';write(receipt,r);results.append(dict(mode=mode,receipt=str(receipt),sha256=sha(receipt),ELF_sha256=sha(folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf')))
    print(json.dumps(dict(passed=True,results=results,target_execution=False,full_image_integration=False)))
if __name__=='__main__':main()
