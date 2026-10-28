"""Static counter/ROM-fill provenance and real readonly C/C++ DATA; no target execution."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;R=HERE.parents[1]
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def lib(p):return runpy.run_path(str(R/p),run_name='input_counter_static_library')
def portable(v,llvm):
    if isinstance(v,dict):return {portable(k,llvm):portable(x,llvm)for k,x in v.items()}
    if isinstance(v,list):return [portable(x,llvm)for x in v]
    if isinstance(v,str):
        for p,t in [(llvm,'${LLVM_BIN}'),(R,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:v=v.replace(str(p),t).replace(p.as_posix(),t)
    return v
def sx(v,n):return v-(1<<n)if v&(1<<(n-1))else v
def pinned(llvm):
    E=read(HERE/'inputs-v1.json')
    for p,h in E['pins'].items():need(sha(R/p)==h,'Frozen source/native/reference input '+p)
    for n,h in E['tools'].items():need(sha(llvm/n)==h,'Pinned actual local tool '+n)
    need(sha(llvm.parent/'lib/clang/18/include/stdint.h')==E['stdint_sha256'],'Pinned freestanding header');need(sha(HERE/'counter_data.v1.c')==E['source_sha256'],'Exactly selected8-byte DATA source');return E
def reaching(f,ops,g,site,reg):
    pure={'beqz','bne','beq','bnez','bltu','j','ret','jr'};stores={'sb','sw'};results={'auipc','lbu','lhu','lw','li','add','addi','andi','ori','slli','srli','or','lui','mv','seqz','snez','mul'};volatile={'ra','t0','t1','t2','t3','t4','t5','t6','a0','a1','a2','a3','a4','a5','a6','a7'}
    incoming={p:set()for p in g};incoming[f['start']].add(-1);todo=[f['start']]
    while todo:
        pc=todo.pop();o=ops[pc];mn=o['opcode'].split()[0];call=o['type']in ['call','ucall'];need(mn in pure|stores|results|{'jal','jalr'},'No unmodelled register writer')
        writes=(mn in results and o['opcode'].partition(' ')[2].split(',')[0]==reg)or(call and reg in volatile);out={pc}if writes else incoming[pc]
        for n in g[pc]:
            before=len(incoming[n]);incoming[n]|=out
            if len(incoming[n])!=before:todo.append(n)
    return incoming[site]
def GP_inventory(elf):
    rows=[];aliases=[];count=0;total=0
    for s in elf.sections:
        if s['flags']&6!=6 or not s['size']:continue
        need(not(s['address']<0x14c8a and s['address']+s['size']>0x14056),'No withheld CODE selected');data=elf.data(s);at=0;total+=len(data)
        while at<len(data):
            size=4 if data[at]&3==3 else 2;need(at+size<=len(data),'Whole selected instruction');h=int.from_bytes(data[at:at+size],'little');pc=s['address']+at;at+=size;count+=1
            if size!=4 or(h>>15)&31!=3:continue
            opcode=h&127;funct=(h>>12)&7
            if opcode==3 and funct in [0,1,2,4,5]:imm=sx(h>>20,12);width={0:1,1:2,2:4,4:1,5:2}[funct];role='read';reg=(h>>7)&31
            elif opcode==0x23 and funct in [0,1,2]:imm=sx(((h>>25)<<5)|((h>>7)&31),12);width={0:1,1:2,2:4}[funct];role='write';reg=(h>>20)&31
            elif opcode==0x13 and funct==0:aliases.append(dict(PC=pc,GP_offset=sx(h>>20,12),destination_register=(h>>7)&31));continue
            else:continue
            if imm<=176<imm+width:rows.append(dict(PC=pc,GP_offset=imm,width_bytes=width,role=role,value_register=reg))
    need((total,count)==(69412,23602),'All selected original APP CODE,not the excluded body')
    need([v['PC']for v in rows]==[0xa0f2,0xa0fa,0xa146,0xa33a,0xa344]and len(aliases)==196,'Exact explicit GP-overlapping accesses and ADDI address-take inventory')
    return dict(selected_CODE_bytes=total,instructions=count,explicit_accesses=rows,GP_address_takes=aliases,all_writers_or_dynamic_aliases_proved=False,excluded_CODE_scanned=False)
def contract(E):
    EL=lib(E['APP_reader'])['ELF'];elf=EL(R/E['APP_ELF']);raw=(R/E['firmware']).read_bytes();B=lib('experiments/tsl9-original-startup/build-v1.py');V=lib('experiments/tsl9-original-RF-tx-path/audit-v1.py');selected={};graphs={};cfgs=[]
    for path,start,frame in [(E['consumer_evidence'],0xa054,48),(E['writer_evidence'],0xa2ee,16),(E['reset_evidence'],0xa37c,0)]:
        f=next(f for f in read(R/path)['selected_functions']if f['start']==start);data=raw[start-0x8000:f['end']-0x8000];need(data==b''.join(bytes.fromhex(o['bytes'])for o in f['operations']),'Whole actual original selected function bytes')
        sections=[s for s in elf.sections if s['flags']&6==6 and s['address']<=start and f['end']<=s['address']+s['size']];need(len(sections)==1,'One real CODE witness');s=sections[0];need(elf.data(s)[start-s['address']:f['end']-s['address']]==data,'Original APP and actual C/C++ native bytes equal')
        external={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))};ops,g,cfg=V['whole_cfg'](f,B,external,frame);selected[start]=(f,ops);graphs[start]=g;cfgs.append(cfg)
    need(sum(v['bytes']for v in cfgs)==592 and sum(v['instructions']for v in cfgs)==201,'Complete592 APP bytes/201 instructions,including post-return arms')
    updates=[]
    for start,load,increment,mask,store in [(0xa054,0xa0f2,0xa0f6,0xa0f8,0xa0fa),(0xa2ee,0xa33a,0xa33e,0xa340,0xa344)]:
        f,ops=selected[start];g=graphs[start];need([ops[p]['opcode']for p in [load,increment,mask,store]]==['lbu a5, 176(gp)','addi a5, a5, 1','andi a5, a5, 3','sb a5, 176(gp)'],'Both explicit writes use exact masked increment')
        for use,definition in [(increment,load),(mask,increment),(store,mask)]:need(reaching(f,ops,g,use,'a5')=={definition},'Unique actual reaching definition for every masked store')
        updates.append(dict(load_PC=load,increment_PC=increment,mask_PC=mask,store_PC=store,expression='(old_byte+1)&3',stored_domain=[0,3]))
    f,ops=selected[0xa054];g=graphs[0xa054]
    expected={0xa146:'lbu a5, 176(gp)',0xa14a:'slli a4, a5, 0x1',0xa14e:'auipc a5, 0x11',0xa152:'addi a5, a5, -1542',0xa156:'add a5, a5, a4',0xa158:'lhu a5, 0(a5)'};need(all(ops[p]['opcode']==v for p,v in expected.items()),'Exact byte-index/halfword lookup expression')
    for use,definition,reg in [(0xa14a,0xa146,'a5'),(0xa156,0xa14a,'a4'),(0xa156,0xa152,'a5'),(0xa158,0xa156,'a5')]:need(reaching(f,ops,g,use,reg)=={definition},'All actual read-address definitions retained')
    hi=int.from_bytes(bytes.fromhex(ops[0xa14e]['bytes']),'little');lo=int.from_bytes(bytes.fromhex(ops[0xa152]['bytes']),'little');need((0xa14e+sx(hi&0xfffff000,32)+sx(lo>>20,12))&0xffffffff==0x1ab48,'Raw base resolves exactly1AB48')
    bypass=0xa158 in V['reachable'](g,f['start'],skip=0xa0fa);need(bypass,'Masked store does not dominate read in the ordinary-entry CFG;do not invent a local unconditional bound')
    start,end=0x1ab48,0x1ab48+2*255+2;need(end==0x1ad48,'Byte-only conservative envelope512 bytes');need(not any(s['flags']&2 and s['size']and s['address']<0x1ab50 and 0x1ab48<s['address']+s['size']for s in elf.sections),'All selected8 original DATA bytes genuinely unowned')
    f,reset=selected[0xa37c];need([o['opcode']for o in f['operations']]==['lui a5, 0x40','lw t1, 72(a5)','li a2, 5','li a1, 0','addi a0, gp, 172','jr t1'],'Actual reset-style tail arguments,not a guessed memset implementation')
    carrier=(R/E['SDK_carrier']).read_bytes();need(int.from_bytes(carrier[72:76],'little')==0x2000039c,'Actual candidate table slot40048')
    sf=next(f for f in read(R/E['SDK_evidence'])['selected_functions']if f['start']==0x2000039c);mapped=sf['start']-0x20000000+0x40270;need(carrier[mapped-0x40000:mapped-0x40000+sf['end']-sf['start']]==b''.join(bytes.fromhex(o['bytes'])for o in sf['operations']),'Complete candidate RAM function agrees with carrier-copy coordinates')
    SO=lib(E['SDK_ownership']);sdk=SO['inspect'](R/E['SDK_object']);need(sdk['passed'],'Real selected SDK object has unique original-PC ownership');sm={o['addr']:o for o in sf['operations']};sgext={d[1]for o in sf['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))};so,sg,scfg=V['whole_cfg'](sf,B,sgext,0);relations=set(sdk['_typed_relations'])
    for pc,o in sm.items():
        original=bytes.fromhex(o['bytes']);native=bytes(sdk['_byte_map'][p]for p in range(pc,pc+o['size']));d=B['decode_control'](original,pc)
        if d:
            kind,target=d;width,mask=B['MASKS'][kind];need(width==len(original)and int.from_bytes(native,'little')&mask==int.from_bytes(original,'little')&mask,'Actual native control opcode/register fields')
            need(json.dumps([['CODE',pc],kind,0,['CODE',target]],separators=(',',':'))in relations,'Exact source-PC typed native branch relation')
        else:need(native==original,'Every actual candidate noncontrol native byte equal')
    expected_sdk={0x2000039c:'lui a4, 0x40024',0x200003a0:'lw a5, 524(a4)',0x200003a4:'sw zero, 524(a4)',0x200003a8:'fence.i',0x200003ac:'beqz a0, 0x200003b4',0x200003ae:'add a4, a0, a2',0x200003b2:'bnez a2, 0x200003be',0x200003b4:'lui a4, 0x40024',0x200003b8:'sw a5, 524(a4)',0x200003bc:'ret',0x200003be:'addi a0, a0, 1',0x200003c0:'sb a1, -1(a0)',0x200003c4:'bne a0, a4, 0x200003be',0x200003c8:'j 0x200003b4'};need({p:o['opcode']for p,o in sm.items()}==expected_sdk,'Whole candidate fill loop and saved/zeroed/restored MMIO,not only a misleading18-byte symbol prefix')
    need(sg[0x200003be]==[0x200003c0]and sg[0x200003c0]==[0x200003c4]and set(sg[0x200003c4])=={0x200003be,0x200003c8},'Exact byte-store loop,increment and endpoint comparison')
    # Symbolic finite-range consequence for the literal length5; no ISA or target simulation.
    fill=dict(APP_entry=0xa37c,tail_PC=0xa38c,candidate_table_slot=0x40048,candidate_target=0x2000039c,candidate_function_bytes=46,candidate_function_instructions=14,candidate_CFG=scfg,destination_GP_offset=172,length_argument=5,fill_byte=0,conditional_GP_write_interval=[172,177],counter_offset=176,counter_cleared_to=0,loop_store_PC=0x200003c0,MMIO_address=0x4002420c,MMIO_saved_zeroed_and_restored=True,MMIO_physical_meaning_or_effects_proved=False,GP_preserved_by_candidate_body=True,installed_ROM_identity_proved=False,requires='Actual installed slot equals this whole candidate;Valid nonzero nonwrapping RAM destination disjoint from MMIO control word;valid MMIO;normal instructions/no faults or interfering writes.')
    inv=GP_inventory(elf);shape=(R/E['firmware']).read_bytes()[0x1ab48-0x8000:0x1ab50-0x8000];need(len(shape)==8,'Exactly one8-byte selected DATA window')
    return dict(passed=True,APP_functions=cfgs,APP_reference_bytes=592,APP_reference_instructions=201,SDK_reference_bytes=46,SDK_reference_instructions=14,GP_counter_offset=176,explicit_updates=updates,conditional_candidate_fill=fill,GP_inventory=inv,read_PC=0xa158,read_width_bytes=2,base=0x1ab48,expression='base+2*counter',conservative_byte_counter_domain=[0,255],conservative_window=[start,end],conservative_bytes=512,bytes_outside_provided_APP=328,masked_store_dominates_read=False,ordinary_entry_CFG_bypass_exists=bypass,bypass_path_runtime_feasibility_proved=False,conditional_counter_domain=[0,3],conditional_read_window=[0x1ab48,0x1ab50],conditional_read_bytes=8,conditional_halfword_cells=4,conditions=['A known masked store completed,or the identified candidate fill completed normally','Actual counter byte remains0..3 until the read,including callees/interrupts/DMA/aliases','Normal original entries,stable GP,valid RAM disjoint from caller buffers and MMIO control word,and saved-register contracts'],original_full_table_extent_proved=False,all_writers_or_global_counter_invariant_proved=False,full_provider_binding_justified=False,DATA_role_is_indexed_numeric_lookup=True,physical_feature_or_packet_semantics_identified=False)
def audit_data(path,E):
    EL=lib(E['APP_reader'])['ELF'];e=EL(path);alloc=[s for s in e.sections if s['flags']&2 and s['size']];need(e.header[0]==1 and not e.program_headers and len(alloc)==1,'Actual nonloadable DATA-only ET_REL');s=alloc[0];need((s['name'],s['type'],s['flags'],s['size'],s['align'],s['address'])==('.rodata.tsl9_input_counter_read_window_1ab48',1,2,8,4,0),'Exactly8 readonly DATA bytes,not physical placement')
    owners=[s for s in e.symbols if s['size']];need(len(owners)==1 and owners[0]['name']=='tsl9_input_counter_read_window_1ab48'and owners[0]['info']==17 and owners[0]['size']==8 and owners[0]['value']==0,'One real positive DATA OBJECT;no opaque-provider alias')
    need(not e.relocations and not any(s['name']and s['info']&15!=4 and s['section']in [0,0xfff1]for s in e.symbols),'No new imports,relocations or ABS providers');raw=(R/E['firmware']).read_bytes();need(e.data(alloc[0])==raw[0x1ab48-0x8000:0x1ab50-0x8000],'All8 actual native DATA bytes equal original selected window');ind=lib('experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path);need(ind['passed'],'Independent entire DATA object reader agreement');return dict(passed=True,object_sha256=sha(path),CODE_bytes=0,DATA_bytes=8,positive_OBJECTs=1,relocations=0,named_UND=0,ABS_providers=0,independent_readers=ind)
def compose(path,inputs,E):
    EL=lib(E['APP_reader'])['ELF'];F=lib('experiments/tsl9-sdk-unique-code-ownership/audit-v1.py');a,d,u,r=F['facts'](inputs[0],EL);aa,dd,uu,rr=F['facts'](inputs[1],EL);need(not set(a)&set(aa)and not set(d)&set(dd)and not uu and not rr,'Distinct real DATA-only extension')
    need(F['facts'](path,EL)==({**a,**aa},{**d,**dd},u-set(dd),sorted(r+rr))and len(u)==6 and not set(dd)&u,'Every allocated input byte/global symbol/typed relocation retained;all six imports remain')
    e=EL(path);need(sum(s['size']for s in e.sections if s['flags']&6==6)==69412 and sum(s['size']for s in e.sections if s['flags']&2 and not s['flags']&4)==4018,'Exact69412 CODE and4018 DATA;no padding');ind=lib('experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path);need(ind['passed'],'Independent complete APP-plus-DATA object readers agree');return dict(passed=True,object_sha256=sha(path),CODE_bytes=69412,DATA_bytes=4018,allocated_bytes=73430,relocations=len(e.relocations),compiler_UND=6,all_input_allocated_bytes_global_symbols_and_typed_relocations_retained=True,independent_readers=ind,original_address_link_performed=False,source_curated=False)
def run(llvm,trial=None,record_replay=False):
    E=pinned(llvm);proof=contract(E);out=HERE/'build'/(trial if trial else'native-v1')
    if trial:need(Path(trial).name==trial and not out.exists(),'Create-only experimental native folder')
    native={};composition={}
    for mode,language,std in [('c','c','c11'),('cpp','c++','c++17')]:
        f=out/mode;parent=R/E['APP_component'].replace('/c/','/'+mode+'/');need(sha(parent)==E['APP_component_sha256'],'Current real160-source APP component retained')
        if trial:
            f.mkdir(parents=True);argv=[str(llvm/'clang.exe'),'--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-Oz','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-mno-relax','-fdata-sections','-Wall','-Wextra','-Werror','-x',language,'-std='+std,'-c',str(HERE/'counter_data.v1.c'),'-o',str(f/'unit.o')];p=subprocess.run(argv,cwd=R,capture_output=True,timeout=120);(f/'compile.log').write_text(portable((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual DATA compile succeeded;log retained')
        native[mode]=audit_data(f/'unit.o',E)
        if trial:
            p=subprocess.run([str(llvm/'ld.lld.exe'),'-r','--no-relax',str(parent),str(f/'unit.o'),'-o',str(f/'candidate.o')],capture_output=True,timeout=120);(f/'link.log').write_text(portable((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual partial composition completed;log retained')
        composition[mode]=compose(f/'candidate.o',[parent,f/'unit.o'],E)
    need(native['c']==native['cpp']and composition['c']==composition['cpp'],'Actual C11/C++17 DATA and complete partial compositions identical');pinned(llvm)
    v=dict(schema='TSL9-input-counter-conditional-DATA-native-verification-v2',passed=True,checker_sha256=sha(__file__),inputs_sha256=sha(HERE/'inputs-v1.json'),state_contract=proof,native=native,composition=composition,new_experimental_DATA_bytes=8,new_CODE_bytes=0,formal_source_C_H_files_unchanged=160,formal_APP_covered_bytes_unchanged=73422,formal_APP_byte_coverage_unchanged=95.6,compiler_UND_unchanged=6,source_curated=False,original_address_link_performed=False,provider_resolved=False,withheld_payload_or_individual_hash_output=False,installed_ROM_RAM_IRQ_Flash_OTA_proved=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
    dest=HERE/'verification-v2.json'
    if trial or record_replay:need(not dest.exists(),'Create-only native/state proof receipt');dest.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
    else:need(v==read(dest),'Fresh specific static/native replay equals successful receipt')
    return v
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--trial');p.add_argument('--record-replay',action='store_true');a=p.parse_args()
    try:
        v=run(a.tool_dir.resolve(),a.trial,a.record_replay);print(json.dumps(dict(passed=True,APP_reference_bytes=592,SDK_reference_bytes=46,new_experimental_DATA_bytes=8,APP_partial_CODE=69412,APP_partial_DATA=4018,compiler_UND=6,formal_APP_byte_coverage=95.6,provider_resolved=False,new_BIN=False)))
    except Exception as error:print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=portable(str(error),a.tool_dir.resolve()))));raise SystemExit(1)
