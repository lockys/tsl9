"""Prove conditional lookup rows and compile readonly C/C++ DATA; never run targets."""
import argparse,hashlib,json,re,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;R=HERE.parents[1]
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def lib(p):return runpy.run_path(str(R/p),run_name='lookup_rows_static_library')
def portable(v,llvm):
    if isinstance(v,dict):return {portable(k,llvm):portable(x,llvm)for k,x in v.items()}
    if isinstance(v,list):return [portable(x,llvm)for x in v]
    if isinstance(v,str):
        for p,t in [(llvm,'${LLVM_BIN}'),(R,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:v=v.replace(str(p),t).replace(p.as_posix(),t)
    return v
def pinned(llvm):
    E=read(HERE/'inputs-v1.json')
    for p,h in E['reference_inputs'].items():need(sha(R/p)==h,'Frozen source/native/proof input: '+p)
    for n,h in E['tools'].items():need(sha(llvm/n)==h,'Pinned local tool '+n)
    need(sha(llvm.parent/'lib/clang/18/include/stdint.h')==E['stdint_sha256'],'Pinned freestanding header')
    need(sha(HERE/'lookup_mode_rows.v1.c')==E['source_sha256'],'Exact selected48-byte C/C++ DATA source')
    return E
def reaching(f,ops,g,site,reg):
    pure={'beqz','bne','beq','bnez','bltu','j','ret'};stores={'sb','sw'}
    results={'auipc','lbu','lw','li','add','addi','andi','ori','slli','or','rem','lui','mv'}
    volatile={'ra','t0','t1','t2','t3','t4','t5','t6','a0','a1','a2','a3','a4','a5','a6','a7'}
    incoming={p:set()for p in g};incoming[f['start']].add(-1);todo=[f['start']]
    while todo:
        pc=todo.pop();o=ops[pc];mn=o['opcode'].split()[0]
        need(mn in pure|stores|results|{'jal'},'No unmodelled register writer')
        writes=(mn in results and o['opcode'].partition(' ')[2].split(',')[0]==reg)or(mn=='jal'and reg in volatile)
        out={pc}if writes else incoming[pc]
        for n in g[pc]:
            before=len(incoming[n]);incoming[n]|=out
            if len(incoming[n])!=before:todo.append(n)
    return incoming[site]
def sx(v,n):return v-(1<<n)if v&(1<<(n-1))else v
def memory_pair(ops,high,low,kind):
    h=int.from_bytes(bytes.fromhex(ops[high]['bytes']),'little');l=int.from_bytes(bytes.fromhex(ops[low]['bytes']),'little')
    need(low==high+4 and ops[high]['size']==ops[low]['size']==4 and h&127==0x17 and(h>>7)&31==(l>>15)&31,'Actual sequential AUIPC base')
    need(l&127==({'load':3,'store':0x23}[kind]),'Actual memory operation')
    imm=((l>>25)<<5)|((l>>7)&31)if kind=='store'else l>>20
    return (high+sx(h&0xfffff000,32)+sx(imm,12))&0xffffffff
def contract(E):
    P=R/'experiments/tsl9-APP-residual-access-audit';prior=read(P/'verification-v1.json')
    need(prior['passed']and prior['native_source_proof']==dict(C_H_files=159,source_comparisons=266,source_objects=532,positive_allocated_bytes=73374),'Retained successful full source proof')
    # Replay only its specific access stage; the unchanged full532-object proof is retained.
    ns=runpy.run_path(str(P/'verify-v1.py'),run_name='lookup_prior_access');ns['E']=read(P/'inputs-v1.json');ns['L']=ns['lib']('experiments/tsl9-original-layout/build-v65.py')
    text=(P/'verify-v1.py').read_text('utf-8');a=text.index("    elf=L['E'](R/E['APP_ELF'])");z=text.index("    return dict(schema='TSL9-APP-residual",a)
    exec(compile('def access_stage():\n'+text[a:z]+'    return facts,access\n',str(P/'verify-v1.py'),'exec'),ns);facts,access=ns['access_stage']()
    need(facts==prior['gap_map']and access==prior['access_contract'],'Fresh specific prior bounds stage')
    need(access['mode_reaching_definitions']==[0xcf0a,0xcf7a]and access['nibble_domain']==[0,15],'Original consumer definitions retained')
    raw=(R/E['firmware']).read_bytes();EL=lib(E['reader'])['ELF'];elf=EL(R/E['APP_ELF'])
    need(elf.header[0]==2 and not any(h[0]==1 for h in elf.program_headers),'Existing APP diagnostic is nonloadable')
    for mode in ['c','cpp']:need(sha(R/E['APP_ELF'].replace('/c/','/'+mode+'/'))==E['APP_ELF_sha256'],'Actual complete original-coordinate diagnostics unchanged')
    B=lib('experiments/tsl9-original-startup/build-v1.py');V=lib('experiments/tsl9-original-RF-tx-path/audit-v1.py');functions={};graphs={};cfgs=[]
    for path,start,frame in [(E['setter_evidence'],0xd07c,16),(E['consumer_evidence'],0xcedc,0)]:
        f=next(f for f in read(R/path)['selected_functions']if f['start']==start);at=start
        for o in f['operations']:need(o['addr']==at,'Contiguous complete selected function');at+=o['size']
        need(at==f['end']and not any(a<f['end']and start<z for a,z in E['withheld_ranges']),'No withheld CODE selected')
        data=raw[start-0x8000:f['end']-0x8000];need(data==b''.join(bytes.fromhex(o['bytes'])for o in f['operations']),'Actual original selected function bytes')
        sections=[s for s in elf.sections if s['flags']&6==6 and s['address']<=start and f['end']<=s['address']+s['size']];need(len(sections)==1,'Unique real CODE witness');s=sections[0]
        need(elf.data(s)[start-s['address']:f['end']-s['address']]==data,'Original and compiled C/C++ diagnostic bytes equal')
        external={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))};ops,g,cfg=V['whole_cfg'](f,B,external,frame);functions[start]=(f,ops);graphs[start]=g;cfgs.append(cfg)
    f,ops=functions[0xd07c];g=graphs[0xd07c]
    need(reaching(f,ops,g,0xd0c8,'a5')=={0xd0b6,0xd0c0,0xd0d8},'Exactly three final reaching store definitions; call clobbers modelled')
    packed=[]
    for high,low,value,mode in [(0xd0b2,0xd0b6,0x01000501,5),(0xd0bc,0xd0c0,0x01000401,4),(0xd0d4,0xd0d8,0x01000201,2)]:
        need(reaching(f,ops,g,low,'a5')=={high},'Every low literal has one real upper definition')
        h=int.from_bytes(bytes.fromhex(ops[high]['bytes']),'little');l=int.from_bytes(bytes.fromhex(ops[low]['bytes']),'little')
        need(h&127==0x37 and(h>>7)&31==15 and l&0x707f==0x13 and(l>>7)&31==(l>>15)&31==15,'Actual LUI/ADDI literal fields')
        actual=((h&0xfffff000)+sx(l>>20,12))&0xffffffff;need(actual==value,'Exact packed state word')
        bs=actual.to_bytes(4,'little');need(list(bs)==[1,mode,0,1],'Mode is second byte, distinct from phase third byte')
        packed.append(dict(upper_PC=high,definition_PC=low,packed_word=value,state_bytes=list(bs),lookup_mode=mode))
    need(memory_pair(ops,0xd0c4,0xd0c8,'store')==0x2000bf38 and ops[0xd0c8]['opcode']=='sw a5, -396(a4)','Actual32-bit state store reaches all four bytes')
    f,ops=functions[0xcedc]
    need(memory_pair(ops,0xcf06,0xcf0a,'load')==0x2000bf39 and ops[0xcf0a]['opcode']=='lbu a4, 51(a4)','Actual lookup mode byte BF39')
    need(memory_pair(ops,0xcee6,0xceea,'load')==memory_pair(ops,0xcf70,0xcf74,'store')==0x2000bf3a,'Phase reads/writes BF3A, not mode')
    need(ops[0xcf66]['opcode']=='li a2, 3'and ops[0xcf6c]['opcode']=='rem a3, a3, a2'and ops[0xcf74]['opcode']=='sb a3, -54(a2)','Actual phase modulo store operands')
    rows=[];owner=access['owner_range'];selected=[]
    for m in [0,2,4,5]:
        start=0x1a078+16*m;end=start+16;need(not any(a<end and start<z for a,z in E['withheld_ranges']),'Selected row excludes withheld ranges')
        owned=owner[0]<=start and end<=owner[1]
        if m:need(all(not(a<end and start<z)for a,z in [(s['address'],s['address']+s['size'])for s in elf.sections if s['flags']&2 and s['size']]),'Each new row genuinely uncovered');selected.extend(range(start,end))
        rows.append(dict(mode=m,start=start,end=end,bytes=16,already_owned=owned,new_experimental_DATA=not owned))
    need(len(selected)==48 and len(set(selected))==48,'Exactly48 new selected original DATA bytes')
    zero=raw[0x1a078-0x8000:0x1a088-0x8000];shape=[]
    for row in rows[1:]:
        data=raw[row['start']-0x8000:row['end']-0x8000]
        need(len({v^zero[i]for i,v in enumerate(data)})==1,'Selected rows share a constant XOR offset to existing indexed row0')
        shape.append(dict(mode=row['mode'],bytes=16,distinct_values=len(set(data)),printable_bytes=sum(32<=v<127 for v in data),cross_row_XOR_constant=True))
    return dict(passed=True,functions=cfgs,reference_CODE_bytes=300,reference_instructions=sum(v['instructions']for v in cfgs),state_word=0x2000bf38,lookup_mode_byte=0x2000bf39,phase_byte=0x2000bf3a,store_PC=0xd0c8,store_width_bytes=4,packed_definitions=packed,store_reaching_definitions=[0xd0b6,0xd0c0,0xd0d8],conditional_lookup_mode_domain=[0,2,4,5],nibble_domain=[0,15],rows=rows,new_DATA_bytes=48,existing_DATA_bytes=16,lookup_data_shape=shape,conditions=['Normal original function entries and valid caller memory/registers','Known D0C8 store completed before the selected consumer','Mode byte unchanged by other code, SDK, interrupts or DMA','Record buffer does not alias the fixed four-byte state'],all_writers_or_global_mode_invariant_proved=False,original_full_table_extent_proved=False,full_provider_binding_justified=False,prior_access_stage_replayed=True,full532_object_source_proof_rerun=False)
def audit_object(path,E):
    EL=lib(E['reader'])['ELF'];e=EL(path);need(e.header[0]==1 and not e.program_headers,'Actual ET_REL object without load segments')
    alloc=[s for s in e.sections if s['flags']&2 and s['size']];need(len(alloc)==3 and sum(s['size']for s in alloc)==48,'Exactly three16-byte allocated sections')
    need(all(s['type']==1 and s['flags']==2 and s['size']==16 and s['align']==4 and s['address']==0 for s in alloc),'Readonly file-backed DATA only; no physical-address layout')
    need(not e.relocations and not any(s['name']and s['info']&15!=4 and s['section']in [0,0xfff1]for s in e.symbols),'No relocations, named UND or ABS providers; FILE metadata is not a provider')
    obj=[s for s in e.symbols if s['size']];need(len(obj)==3 and all(s['info']==17 and s['size']==16 and s['value']==0 for s in obj),'Exactly three positive global OBJECT labels; zero CODE/FUNC')
    raw=(R/E['firmware']).read_bytes();rows=[]
    for m,pc in [(2,0x1a098),(4,0x1a0b8),(5,0x1a0c8)]:
        name=f'tsl9_lookup_mode_row_{m}_{pc:x}';ss=[s for s in obj if s['name']==name];need(len(ss)==1,'Exact typed row symbol');s=e.sections[ss[0]['section']]
        need(s['name']=='.rodata.'+name and e.data(s)==raw[pc-0x8000:pc-0x8000+16],'Actual DATA bytes equal allowed original row')
        rows.append(dict(mode=m,original_start=pc,bytes=16,name=name))
    independent=lib('experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path)
    need(independent['passed'],'Independent full ELF structure/bytes/symbol agreement')
    return dict(passed=True,object_sha256=sha(path),CODE_bytes=0,DATA_bytes=48,positive_OBJECT_regions=3,positive_FUNC_regions=0,relocations=0,named_UND=0,ABS_providers=0,rows=rows,independent_reader=independent,original_address_link_performed=False,linked_into_APP=False)
def run(llvm,trial=None,replay=None):
    E=pinned(llvm);proof=contract(E);source=HERE/'lookup_mode_rows.v1.c';result={};out=HERE/'build'/(trial if trial else 'native-v1')
    if trial:need(Path(trial).name==trial and not out.exists(),'Create-only owned native trial')
    else:need(replay is not None and replay.resolve()==out,'Replay only known owned artifact folder')
    for mode,language,std in [('c','c','c11'),('cpp','c++','c++17')]:
        folder=out/mode
        if trial:
            folder.mkdir(parents=True);argv=[str(llvm/'clang.exe'),'--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-Oz','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-mno-relax','-fdata-sections','-Wall','-Wextra','-Werror','-x',language,'-std='+std,'-MD','-MF',str(folder/'unit.d'),'-MT','unit.o','-c',str(source),'-o',str(folder/'unit.o')]
            p=subprocess.run(argv,cwd=R,capture_output=True,timeout=120);(folder/'compile.log').write_text(portable((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual native DATA compile; logs retained')
            deps=(folder/'unit.d').read_text('utf-8');need(str(source).replace('\\','/')in deps.replace('\\\n','').replace('\\','/')and 'stdint.h'in deps,'Actual compiler source and freestanding header dependencies')
            (folder/'unit.d').write_text(portable(deps,llvm),encoding='utf-8')
        result[mode]=audit_object(folder/'unit.o',E)
    need(result['c']==result['cpp'],'Actual C11/C++17 results and complete object identity equal');pinned(llvm)
    v=dict(schema='TSL9-conditional-lookup-mode-rows-v1',passed=True,checker_sha256=sha(__file__),inputs_sha256=sha(HERE/'inputs-v1.json'),source_sha256=sha(source),state_contract=proof,native=result,new_CODE_bytes=0,new_experimental_DATA_bytes=48,formal_APP_source_C_H_files_unchanged=159,formal_APP_covered_bytes_unchanged=73374,formal_APP_byte_coverage_unchanged=95.54,compiler_UND_unchanged=6,source_curated=False,provider_resolved=False,original_address_link_performed=False,linked_into_APP=False,withheld_payload_or_individual_hash_output=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
    if trial:
        dest=HERE/'verification-v1.json'
        if dest.exists():need(v==read(dest),'Existing successful receipt must match; never overwrite')
        else:dest.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
    else:need(v==read(HERE/'verification-v1.json'),'Fresh positive static/native replay equals exact receipt')
    return v
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--tool-dir',type=Path,required=True);g=p.add_mutually_exclusive_group(required=True);g.add_argument('--trial');g.add_argument('--replay',type=Path);a=p.parse_args()
    try:
        v=run(a.tool_dir.resolve(),a.trial,a.replay);print(json.dumps(dict(passed=True,new_experimental_DATA_bytes=48,new_CODE_bytes=0,languages=['C11','C++17'],formal_APP_byte_coverage=95.54,compiler_UND=6,provider_resolved=False,new_BIN=False)))
    except Exception as error:
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=portable(str(error),a.tool_dir.resolve()))));raise SystemExit(1)
