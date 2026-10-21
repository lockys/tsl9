"""Actual native six-function compile/link and pinned independent static review.

No native target is executed. This never exports or patches a firmware image.
"""
import argparse,hashlib,importlib.util,json,os,re,shlex,shutil,struct,subprocess,uuid
from pathlib import Path
H=Path(__file__).resolve().parent;MODEL='experiments/tsl9-v4160-flash-native'
SOURCE_SEAL='dff9a51e3b59bbdddd150dde37614753bb3c3b440d7bde2f9402c8b6e9a2bce4'
PARSER_SHA='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
REVIEW_SHA='0dd857b44c9163d45668f224e5b772f3adfa08e832e58e1c5491b7fa5f1c0554'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,d):p.write_bytes((json.dumps(d,indent=2)+'\n').encode())
def need(v,m):
    if not v:raise ValueError(m)
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def case(root,slug):
    for p in (root/'analysis'/slug,root/'apk-analysis'/('tsl9-'+slug)):
        if p.is_dir():return p
    raise ValueError('missing source case '+slug)
def context(root,firmware=None):
    here=case(root,'v4160-flash-native-2026-10-22');source=here/'source';review=here/'compiler-review/review.py'
    need(sha(source/'seal.json')==SOURCE_SEAL,'frozen ID2966 original source proof')
    pins={str(source/'seal.json'):SOURCE_SEAL}
    for r in read(source/'seal.json')['members']:need(sha(source/r['path'])==r['sha256'],'sealed source member');pins[str(source/r['path'])]=r['sha256']
    need(sha(review)==REVIEW_SHA,'pinned independent six-function normal pattern checker')
    parser=case(root,'v4160-reset-memory-2026-10-21')/'compiler-review/elf32.py';need(sha(parser)==PARSER_SHA,'bounded independent ELF parser');pins[str(parser)]=PARSER_SHA
    D=module('flash_original_decode',source/'inspect.py');E=module('flash_bounded_elf',parser).ELF;A=module('flash_independent_patterns',review);P=module('flash_profile',H/'probe_native.py')
    if firmware is None:firmware=next((root/n for n in ('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin','exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin') if (root/n).is_file()),None)
    need(firmware is not None and sha(firmware)=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','exact offline current firmware reference')
    for p in (review,H/'probe_native.py',Path(__file__).resolve(),firmware):pins[str(p.resolve())]=sha(p)
    for p in (root/MODEL/'src').glob('*'):
        if p.is_file():pins[str(p)]=sha(p)
    return dict(root=root,source=source,review=A,decode=D.decode,ELF=E,profile=P,parser=parser,firmware=firmware,pins=pins)
def run(args,folder,label):
    p=subprocess.run([str(v) for v in args],cwd=folder,capture_output=True,timeout=120);log=folder/(label+'.log');log.write_bytes(p.stdout+p.stderr)
    need(p.returncode==0,label+' failed; inspect '+str(log));return dict(argv=[str(v) for v in args],exit=p.returncode,log=log.name,log_sha256=sha(log))
def resolve_tool(override,directory,name):
    p=override or (directory/(name+('.exe' if os.name=='nt' else '')) if directory else shutil.which(name));need(p and Path(p).is_file(),'missing local tool '+name);return Path(p).resolve()
def link_source(P):return 'ENTRY('+P.symbol(0x9c0a)+')\nSECTIONS {\n'+''.join(' .flash_'+format(a,'x')+' '+hex(a)+' : { *(.text.'+P.symbol(a)+') }\n' for a in P.NAMES)+'}\n'
def dependency_gate(folder,ctx):
    files=list(folder.glob('*.d'));need(len(files)==6,'six actual native dependency files');seen=set()
    for p in files:
        text=p.read_text(encoding='utf-8').replace('\\\n','').replace('\\\r\n','');need(': ' in text,'bounded Make dependency rule')
        for token in shlex.split(text.split(': ',1)[1],posix=True):seen.add(Path(token).resolve())
    wanted={ctx['root']/MODEL/'src'/n for n in ('flash_native.c','flash_native.h','native_io.h')}
    need(seen==wanted,'native project dependency closure exactly three frozen source/header files; no HOST provider')
    return dict(rules=6,non_system_project_files=3,compiler_resource_headers_included=False)
def disassembly_gate(folder,ctx):
    facts={};P=ctx['profile'];E=ctx['ELF'];A=ctx['review']
    for address,(name,limit,allowed) in P.NAMES.items():
        e=E(folder/(name+'.o'));symbol=next(s for s in e.symbols if s['name']==P.symbol(address));body=e.function_bytes(symbol)
        text=(folder/(name+'-disassembly.log')).read_text(encoding='utf-8');m=re.search(r'^([0-9a-f]+) <'+re.escape(P.symbol(address))+r'>:\s*$',text,re.M);need(m is not None and int(m.group(1),16)==0,'actual object disassembly entry')
        cursor=0;lines=[]
        for line in text[m.end():].lstrip('\r\n').splitlines():
            if not line.strip():break
            row=re.fullmatch(r'\s*([0-9a-f]+):\s*((?:[0-9a-f]{2}\s+)+)\t(\S+)\s*(.*?)\s*',line);need(row is not None,'no skipped or unparsed disassembly line')
            off=int(row.group(1),16);raw=bytes.fromhex(row.group(2));need(off==cursor and raw==body[cursor:cursor+len(raw)] and len(raw)==(4 if raw[0]&3==3 else 2),'full contiguous actual raw instruction bytes')
            lines.append(dict(offset=off,bytes=raw.hex(),display_mnemonic=row.group(3)));cursor+=len(raw)
        need(cursor==len(body),'all native function bytes covered, no trailing bytes')
        decoded=A.native_contract(name,body,e.relocations,ctx['decode']);boundaries={r['offset'] for r in decoded};edges={};returns=[]
        for r in decoded:
            off=r['offset'];nextoff=off+r['bytes']
            if r['op']=='ret':edges[off]=[];returns.append(off)
            elif r['op']=='bne':edges[off]=[nextoff,r['target']]
            else:edges[off]=[nextoff]
            need(all(n in boundaries for n in edges[off]),'bounded CFG successor, no escaping or hidden tail')
        seen=set();todo=[0]
        while todo:
            off=todo.pop()
            if off in seen:continue
            seen.add(off);todo.extend(edges[off])
        need(seen==boundaries and returns==[decoded[-1]['offset']],'every instruction statically reachable and sole terminal is final RET; loops remain loops')
        facts[name]=dict(bytes=len(body),original_bytes=limit,fits=len(body)<=limit,instructions=len(decoded),code_sha256=hashlib.sha256(body).hexdigest(),all_disassembly_bytes_covered=True,all_CFG_nodes_reachable=True,branch_backedges=sum(r['op']=='bne' and r['target']<=r['offset'] for r in decoded),normal_pattern_proved=True)
    return facts
def static_checks(folder,ctx,observed_tools):
    folder=folder.resolve();A=ctx['review']
    elf_headers={}
    for name in [r[0] for r in ctx['profile'].NAMES.values()]+['COMPONENT-ONLY-NOT-FIRMWARE']:
        path=folder/(name+('.elf' if name.startswith('COMPONENT') else '.o'));e=ctx['ELF'](path)
        need(e.flags==1 and e.kind==(2 if name.startswith('COMPONENT') else 1),'actual ELF32 RISC-V RVC soft-float object/executable ABI')
        arch=re.search(rb'rv32[a-z0-9_]+',e.data(e.byname['.riscv.attributes']))
        need(arch and all(b'_'+x in arch.group() for x in (b'm',b'a',b'c',b'zicsr')) and not any(b'_'+x in arch.group() for x in (b'f',b'd',b'v')),'actual RV32IMAC_Zicsr integer ISA attributes')
        if e.kind==2:need(not e.relocations and struct.unpack_from('<I',e.raw,24)[0]==0x9c0a,'resolved six-provider component entry/no residual RELA')
        elf_headers[name]=dict(kind=e.kind,flags=e.flags,ISA=arch.group().decode())
    result=A.review(folder,folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf',project_root=ctx['root'],parser_path=ctx['parser'],observed_tools=observed_tools,source_dir=ctx['root']/MODEL/'src',firmware_path=ctx['firmware'])
    need(result['all_six_normal_boundaries_admitted'] and result['all_six_fit'],'all six actual normal contracts and size bounds')
    native=disassembly_gate(folder,ctx);deps=dependency_gate(folder,ctx)
    need((folder/'original-entry-component.ld').read_text(encoding='utf-8')==link_source(ctx['profile']),'actual original-entry component linker source')
    return dict(independent_normal_contract=result,functions=native,ELF_headers=elf_headers,native_dependencies=deps,allocated_function_bytes=sum(x['bytes'] for x in native.values()),original_function_bytes=262,unowned_original_program_tail_bytes=6,
        original_frame_prefix_equivalence=False,pointwise_async_equivalence=False,nonreturn_physical_GPR_prefix_equivalence=False,full_image_integration=False,firmware_BIN_produced=False,OTA_ready=False)
def build(root,folder,ctx,tools,mode):
    folder.mkdir(parents=True);P=ctx['profile'];E=ctx['ELF'];rows=[]
    for address,(name,limit,allowed) in P.NAMES.items():
        commands=[];flags=P.flags(address,mode);out=folder/(name+'.o')
        for suffix,action in [('.o',['-c']),('.ll',['-S','-emit-llvm'])]:
            deps=['-MMD','-MF',str(folder/(name+'.d')),'-MT',name+'.o'] if suffix=='.o' else []
            commands.append(run([tools['clang'],*flags,*deps,*action,root/MODEL/'src/flash_native.c','-o',folder/(name+suffix)],folder,name+suffix))
        e=E(out);fs=[s for s in e.symbols if s['index'] and s['info']&15==2 and s['size']];need(len(fs)==1 and fs[0]['name']==P.symbol(address),'one actual typed function per object')
        commands.append(run([tools['objdump'],'-d',out],folder,name+'-disassembly'))
        rows.append(dict(address=address,name=name,compiled=True,bytes=fs[0]['size'],original_bytes=limit,fits=fs[0]['size']<=limit,code_sha256=hashlib.sha256(e.function_bytes(fs[0])).hexdigest(),relocations=len(e.relocations),UND=sorted({s['name'] for s in e.symbols if not s['index'] and s['name']}),commands=commands))
    script=folder/'original-entry-component.ld';script.write_bytes(link_source(P).encode())
    commands=[run([tools['linker'],'--no-relax','--no-undefined','-T',script,*[folder/(name+'.o') for name,_,_ in P.NAMES.values()],'-o',folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf'],folder,'component-link'),run([tools['objdump'],'-d',folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf'],folder,'component-disassembly')]
    probe=dict(schema='TSL9-readable-flash-first-native-probe-v1',mode=mode,source={p.name:sha(p) for p in (root/MODEL/'src').glob('*') if p.is_file()},functions=rows,link_commands=commands,profile_derived_from_original_write_and_argument_registers=True,target_execution=False,emulation=False,hardware=False,network=False)
    write(folder/'probe.json',probe)
    return probe
def stability(pins):
    for name,pin in pins.items():need(sha(Path(name))==pin,'unchanged actual compile input/tool/proof '+name)
def replay(root,receipt,ctx=None):
    root=Path(root).resolve();receipt=Path(receipt).resolve();ctx=ctx or context(root);r=read(receipt);folder=receipt.parent
    need(r['passed'] is True and r['mode'] in ('c','cpp') and r['runner_sha256']==sha(Path(__file__)),'actual current native runner/receipt mode')
    need(r['source_sha256']=={p.name:sha(p) for p in (root/MODEL/'src').glob('*') if p.is_file()},'current exact native model source snapshot')
    need(r['input_pins']=={**ctx['pins'],**{n:v['before_sha256'] for n,v in r['observed_tools'].items()}},'exact compile source/proof/tool snapshot')
    stability(r['input_pins'])
    for n,meta in r['artifacts'].items():
        p=(folder/n).resolve();need(p.is_relative_to(folder) and p.stat().st_size==meta['bytes'] and sha(p)==meta['sha256'],'actual artifact/log/IR/dependency pin '+n)
    actual=static_checks(folder,ctx,r['observed_tools']);need(json.loads(json.dumps(actual))==r['checks'],'full native static proof replay including directed negatives')
    return dict(passed=True,receipt=str(receipt),sha256=sha(receipt),artifacts_checked=len(r['artifacts']),functions=actual['functions'],native_target_execution=False,full_image_integration=False)
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=H.parents[2]);p.add_argument('--tool-dir',type=Path);p.add_argument('--clang');p.add_argument('--linker');p.add_argument('--objdump');p.add_argument('--firmware',type=Path);p.add_argument('--language',choices=['c','cpp','both'],default='both');p.add_argument('--build-root',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve();ctx=context(root,a.firmware)
    if a.replay:print(json.dumps(replay(root,a.replay,ctx)));return
    tools={k:resolve_tool(getattr(a,k),a.tool_dir,n) for k,n in [('clang','clang'),('linker','ld.lld'),('objdump','llvm-objdump')]};before={str(v):sha(v) for v in tools.values()};pins={**ctx['pins'],**before};stability(pins)
    base=a.build_root.resolve() if a.build_root else root/MODEL/'build'/('native-'+uuid.uuid4().hex);need(base.is_relative_to(root) and not base.exists(),'create-only build root inside project');results=[]
    for mode in (['c','cpp'] if a.language=='both' else [a.language]):
        folder=base/mode;build(root,folder,ctx,tools,mode);observed={n:dict(before_sha256=pin,after_sha256=sha(Path(n))) for n,pin in before.items()};stability(pins)
        checks=static_checks(folder,ctx,observed);stability(pins)
        r=dict(schema='ID2966-readable-flash-native-v1',passed=True,mode=mode,runner_sha256=sha(Path(__file__)),source_sha256={p.name:sha(p) for p in (root/MODEL/'src').glob('*') if p.is_file()},input_pins=pins,observed_tools=observed,checks=checks,
            artifacts={p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in folder.rglob('*') if p.is_file()},
            target_execution=False,ISA_emulation=False,hardware=False,network=False,full_image_integration=False,firmware_BIN_produced=False,OTA_ready=False)
        receipt=folder/'verification.json';write(receipt,r);results.append(dict(mode=mode,receipt=str(receipt),sha256=sha(receipt),functions=checks['functions'],ELF_sha256=sha(folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf')))
    print(json.dumps(dict(passed=True,results=results,target_execution=False,full_image_integration=False,OTA_ready=False)))
if __name__=='__main__':main()
