"""Offline original APP -> candidate SNV -> Flash callback contract; no execution."""
import argparse,hashlib,json,re,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def lib(p):return runpy.run_path(str(ROOT/p),run_name='SNV_Flash_static_library')
def canonical(v):return json.loads(json.dumps(v))

def verify(llvm):
    E=load(HERE/'evidence-v1.json')
    for key in ['reference_inputs','whole_reader_inputs']:
        need(all(sha(ROOT/p)==h for p,h in E[key].items()),'All frozen '+key)
    for p,h in [('APP_firmware','APP_sha256'),('SDK_firmware','SDK_sha256'),('primary_header','primary_header_sha256'),('SDK_native_object','SDK_native_object_sha256')]:
        need(sha(ROOT/E[p])==E[h],'Exact '+p)
    prior=lib(E['prior_study']+'/verify-v1.py')['verify'](llvm)
    need(canonical(prior)==load(ROOT/E['prior_verification']),'Fresh previous ledger/native/original APP contract')
    oldledger=load(ROOT/E['prior_ledger']);need(oldledger==prior['ledger'],'Retain previous nineteen conditional rows')
    V=lib('experiments/tsl9-original-RF-tx-path/audit-v1.py')
    B=lib('experiments/tsl9-original-startup/build-v1.py')
    A=lib('experiments/tsl9-original-APP-library-binding/verify-v1.py')
    readroot='experiments/tsl9-resident-root-chain-callees'
    O=lib(readroot+'/verify-ownership-v3.py');sdk_native=O['inspect'](ROOT/E['SDK_native_object'])
    need(sdk_native['passed'],'Unique current SDK native CODE')
    app=(ROOT/E['APP_firmware']).read_bytes();sdk=(ROOT/E['SDK_firmware']).read_bytes()
    op,graphs,owners,appfuncs,sdkfuncs={},{},{},[],[]
    def whole(f,domain):
        start,end=f['start'],f['end'];raw=b''.join(bytes.fromhex(o['bytes'])for o in f['operations'])
        at=f.get('source_start',start);source=sdk if domain=='SDK'else app;base=0x40000 if domain=='SDK'else 0x8000
        need(len(raw)==end-start and raw==source[at-base:at-base+len(raw)],'Every complete '+domain+' original byte')
        if 'original_sha256'in f:need(hashlib.sha256(raw).hexdigest()==f['original_sha256'],'Original body SHA')
        frame=max([int(m[1])for o in f['operations']if(m:=re.fullmatch(r'addi sp, sp, -(\d+)',o['opcode']))]or[0])
        ext={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))}
        oo,g,row=V['whole_cfg'](f,B,ext,frame)
        need(not set(oo)&set(op),'Disjoint complete function scopes')
        op.update(oo);graphs[start]=g;owners.update({p:start for p in oo})
        (sdkfuncs if domain=='SDK'else appfuncs).append(row)
        if domain=='SDK':need(all(p in sdk_native['_byte_map']for p in range(start,end)),'Complete current native SDK owner')
    for scope in E['source_scopes']:
        need(sha(ROOT/scope['path'])==scope['sha256'],'Exact whole-function evidence')
        fs=[f for f in load(ROOT/scope['path'])['selected_functions']if f['start']in scope['entries']]
        need(len(fs)==len(scope['entries']),'All selected whole functions exist')
        for f in fs:whole(f,scope['domain'])
    copyrows=load(ROOT/E['copy_evidence'])['groups']['helper'];mapped=[];delta=0x20000332-0x405a2
    for row in copyrows:
        o={k:row[k]for k in ['addr','size','bytes','opcode']};o['addr']+=delta
        mnemonic=o['opcode'].split()[0]
        roles={'beqz':'cjmp','bnez':'cjmp','bne':'cjmp','j':'jmp','ret':'ret','sw':'store','sb':'store','lw':'load','lbu':'load'}
        o['type']=roles.get(mnemonic,'mov')
        if o['type']in ['cjmp','jmp']:
            o['opcode']=re.sub(r'0x[0-9a-f]+',lambda m:hex(int(m[0],16)+delta),o['opcode'])
        mapped.append(o)
    whole(dict(start=0x20000332,end=0x2000036c,source_start=0x405a2,operations=mapped),'SDK')
    need(len(appfuncs)==8 and len(sdkfuncs)==4 and sum(f['bytes']for f in appfuncs)==632 and sum(f['bytes']for f in sdkfuncs)==718,'Eight APP / four SDK complete functions')
    EL=lib(readroot+'/elf_reader-v7.py')['ELF'];Other=lib('analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py')['ELF']
    witnesses={}
    for mode,path in E['APP_native_diagnostic_paths'].items():
        need(sha(ROOT/path)==E['APP_native_diagnostic_sha256'],'Existing native APP diagnostic identity')
        e,other=EL(ROOT/path),Other(ROOT/path)
        need(e.header[0]==other.kind==2 and e.header[1]==243 and not any(p[0]==1 for p in e.program_headers),'Existing nonloadable diagnostic only')
        for f in appfuncs:
            x,own=A['native_bytes'](e,f['start'],f['end'],True);y,own2=A['native_bytes'](other,f['start'],f['end'],True)
            need(x==y==app[f['start']-0x8000:f['end']-0x8000] and own==own2,'Every selected APP byte through two independent native readers')
        witnesses[mode]=dict(sha256=sha(ROOT/path),bytes=632,functions=8)
    def exact(values):
        for p,s in values.items():need(op[p]['opcode']==s,f'Exact SNV/Flash operand at {p:#x}: expected {s}; found {op[p]["opcode"]}')
    def dom(root,site,pcs):
        need(all(site not in V['reachable'](graphs[root],root,skip=p)for p in pcs),'Full CFG dominance for initialization/argument ordering')
    def lui_add(pc,next_pc,reg):
        hi=int.from_bytes(bytes.fromhex(op[pc]['bytes']),'little');lo=int.from_bytes(bytes.fromhex(op[next_pc]['bytes']),'little')
        need(hi&127==0x37 and (hi>>7)&31==reg and lo&0x707f==0x13 and (lo>>7)&31==reg and (lo>>15)&31==reg,'Independent LUI/ADDI literal decoder')
        return((hi&0xfffff000)+A['sx'](lo>>20,12))&0xffffffff
    def far(pc):
        hi=int.from_bytes(bytes.fromhex(op[pc]['bytes']),'little');lo=int.from_bytes(bytes.fromhex(op[pc+4]['bytes']),'little')
        need(hi&127==0x17 and lo&0x707f==0x67 and (hi>>7)&31==(lo>>15)&31,'Actual AUIPC/JALR pair')
        return(pc+(hi&0xfffff000)+A['sx'](lo>>20,12))&0xffffffff
    read=A['address_pair'](op,0x19a76);write=A['address_pair'](op,0x19a80)
    addr=lui_add(0x19a4a,0x19a4e,15)
    need((read,write,addr)==(0x1979a,0x197be,0x08077c00),'Original actual Flash callback and SNV address literals')
    exact({0x19a36:'addi a0, sp, 16',0x19a38:'jalr a5',0x19a52:'sw a5, 24(sp)',
        0x19a54:'lui a5, 0x1',0x19a56:'addi a4, a5, -2045',0x19a5a:'sh a4, 30(sp)',
        0x19a7e:'sw a4, 72(sp)',0x19a88:'sw a4, 76(sp)',0x19aea:'addi a0, sp, 16',0x19aec:'jalr a5'})
    need((0x1000-2045)==0x803 and (0x803&255)==3,'Packed SNVNum=3 / BufNumber=8')
    dom(0x199e2,0x19aec,[0x19a38,0x19a52,0x19a5a,0x19a7e,0x19a88])
    stores=[A['store'](o)for p,o in op.items()if 0x199e2<=p<0x19b16 and A['store'](o)]
    need(not any(rs==2 and off<30 and 28<off+width for rs,rd,width,off in stores),'No explicit SP store overwrites zero SNVBlock at SP28..30')
    # Earlier proof verifies actual MAC copy SP40..46. This is not a whole
    # program alias analysis or proof of the initial memset provider at runtime.
    exact({0x43cda:'li a2, 64',0x43cde:'mv a1, s1',0x43ce0:'addi a0, s0, 492',
        0x43cf0:'qk.c.lhu a4, 12(a5)',0x43cf2:'bnez a4, 0x43cfa',0x43cf4:'li a4, 256',0x43cf8:'qk.c.sh a4, 12(a5)',
        0x43cfa:'qk.c.lbu a4, 14(a5)',0x43cfc:'bnez a4, 0x43d02',0x43d4c:'jal 0x43b3e',0x43c04:'jal 0x44022',
        0x43d4e:'li a5, 0',0x43d56:'mv a0, a5'})
    dom(0x43c7e,0x43d4c,[0x43ce8,0x43cf0,0x43cf2])
    need(graphs[0x43c7e][0x43cf2]==[0x43cfa,0x43cf4] and graphs[0x43c7e][0x43cf4]==[0x43cf8]
         and graphs[0x43c7e][0x43cf8]==[0x43cfa] and graphs[0x43c7e][0x43cfc]==[0x43d02,0x43cfe],
         'Zero block takes original 256-byte default; nonzero count skips count default')
    dom(0x43b3e,0x43c04,[0x43c00])
    exact({0x4404a:'lw a5, 56(s0)',0x4404c:'beqz a5, 0x44038',0x4404e:'lw a4, 60(s0)',0x44050:'beqz a4, 0x44038',
        0x44052:'addi a2, sp, 12',0x44054:'li a1, 1',0x44056:'jalr a5',0x44058:'lw a4, 8(s0)',0x4405a:'lw a5, 12(sp)',
        0x4405c:'beq a4, a5, 0x44038',0x44060:'qk.c.lhu a0, 12(s0)',0x4407c:'beqz a0, 0x44038',
        0x4407e:'qk.c.lhu a2, 12(s0)',0x44080:'li a1, 255',0x44084:'li s2, 0',
        0x4408e:'qk.c.lbu a5, 14(s0)',0x44090:'lw a2, 32(s1)',0x44092:'blt s2, a5, 0x440ac',
        0x440ac:'qk.c.lhu a1, 12(s0)',0x440ae:'lw a0, 8(s0)',0x440b0:'lw a4, 60(s0)',
        0x440b2:'mul a5, a1, s2',0x440b6:'srli a1, a1, 0x2',0x440b8:'addi s2, s2, 1',
        0x440ba:'add a0, a0, a5',0x440bc:'sw a0, 0(a2)',0x440be:'jalr a4',0x440c0:'j 0x4408e'})
    dom(0x44022,0x44056,[0x4404a,0x4404e,0x44052,0x44054])
    dom(0x44022,0x440be,[0x4405c,0x4407c,0x44084,0x440b0,0x440bc])
    need(far(0x4406a)==0x20000040 and far(0x44086)==0x2000039c and far(0x44098)==0x20000110,
         'Real allocator, fill and free helpers behind original far pairs')
    exact({0x1979a:'lui a5, 0x40',0x1979e:'lw a5, 76(a5)',0x197a2:'mv a4, a2',0x197a6:'slli a2, a1, 0x2',
        0x197aa:'mv a1, a0',0x197ac:'mv a0, a4',0x197ae:'jalr a5',0x197b2:'li a0, 0',
        0x197c4:'sw a2, 12(sp)',0x197c6:'mv s0, a0',0x197c8:'jal ra, 0x18e98',0x197ce:'jal ra, 0x18ec4',
        0x197d2:'lw a2, 12(sp)',0x197d4:'mv a0, s0',0x197d6:'mv a1, a2',0x197d8:'jal ra, 0x18ef2',
        0x197dc:'jal ra, 0x18eb6',0x197e0:'li a0, 1',0x197e2:'jal ra, 0x19764',0x197ea:'li a0, 0'})
    need(int.from_bytes(sdk[0x4c:0x50],'little')==0x20000332,'Actual candidate copy slot word')
    exact({0x20000346:'li a5, 0',0x20000348:'bnez a2, 0x20000354',0x20000354:'add a3, a1, a5',
        0x20000358:'lbu a6, 0(a3)',0x2000035c:'add a3, a0, a5',0x20000360:'addi a5, a5, 1',
        0x20000362:'sb a6, 0(a3)',0x20000366:'bne a2, a5, 0x20000354'})
    exact({0x18ece:'andi a0, a0, -256',0x18efa:'andi a0, a0, -256',0x18f0c:'lw a5, 12(a4)',
        0x18f0e:'andi a5, a5, 2',0x18f10:'bnez a5, 0x18f0c',0x18f16:'li a2, 256',
        0x18f1a:'add a3, a1, a5',0x18f1e:'lw a6, 0(a3)',0x18f22:'add a3, a0, a5',0x18f26:'sw a6, 0(a3)',
        0x18f30:'addi a5, a5, 4',0x18f32:'bne a5, a2, 0x18f1a',0x19770:'lbu a4, 382(gp)',
        0x19774:'mul a2, a4, a0',0x19790:'beqz a4, 0x1978c'})
    dom(0x18ef2,0x18f26,[0x18f10,0x18f16,0x18f1e])
    dom(0x197be,0x197ee,[0x197c8,0x197ce,0x197d2,0x197d8,0x197dc,0x197e2,0x197ea])
    # Fixed original arithmetic, not execution of a concrete/synthetic target state.
    block,count=256,3;pages=[addr+block*i for i in range(count)]
    need(pages==[0x08077c00,0x08077d00,0x08077e00] and all(p&255==0 for p in pages),'Three aligned logical page arguments without RV32 wrap')
    newrows=[dict(PC=0x44056,outcome='conditional-target',target_original_PC=read,pointer_slot=0x20003224),
             dict(PC=0x440be,outcome='conditional-target',target_original_PC=write,pointer_slot=0x20003228)]
    oldsites={r['PC']for r in oldledger['rows']};rest={r['PC']for r in oldledger['other_sites']}
    need(not oldsites&{r['PC']for r in newrows} and {r['PC']for r in newrows}<=rest,'Two distinct new sites from the thirty-two unjoined sites')
    conditions=['matching installed ROM profile remains required and unproved','known original 64-byte configuration copy and SDK defaults',
        'valid disjoint memory and stacks, stable config/heap pointers and callback fields',
        'original private ABI, normal callee returns, no IRQ/reentrant overwrite',
        'valid logical NVM window and MMIO mapping; polling termination not proved',
        'page arguments apply only if first marker differs, a valid 256-byte allocation is returned and the initialization loop completes']
    contract=dict(passed=True,conditional_new_bindings=newrows,conditions=conditions,
        original_config=dict(SNVAddr=addr,SNVBlock_before_defaults=0,SNVNum=count,BufNumber=8,readFlashCB=read,writeFlashCB=write,source_SP_offset=16),
        effective_SNVBlock=block,logical_page_arguments=pages,logical_window=[addr,addr+block*count],physical_NVM_geometry_or_alias_proved=False,
        read=dict(SDK_site=0x44056,words=1,copy_bytes=4,SDK_destination='entry SDK SP+12',APP_frame_bytes=16,
                  candidate_copy_entry=0x20000332,copy_touches_MMIO_4002420C=True,normal_return_A0=0,return_code_validates_copy=False),
        write=dict(SDK_site=0x440be,SDK_num_words=64,APP_ignores_entry_A1=True,fixed_program_bytes=256,word_reads_and_stores=64,
                   source_span=[0,256],SDK_heap_request_bytes=256,SDK_fill_byte=255,buffer_word0='current logical page address',
                   APP_frame_bytes=32,source_saved_at_own_SP12_and_reloaded_after_erase=True,
                   direct_callees=[0x18e98,0x18ec4,0x18ef2,0x18eb6,0x19764],normal_return_A0=0,
                   helper_results_checked=False,allocation_capacity_proved=False,delay_requires_live_GP_byte382_and_MMIO=True),
        marker_equal_path_skips_writes=True,buffer_allocation_failure_returns_1=True,
        only_first_page_marker_is_compared=True,all_three_page_contents_validated=False,
        BLEInit_overwrites_nested_SNV_status=True,BLE_success_does_not_prove_SNV_persistence=True,
        loop_extent_is_conditional_not_execution_or_hardware_success=True)
    return dict(schema='TSL9-original-SNV-Flash-binding-verification-v1',passed=True,checker_sha256=sha(__file__),evidence_sha256=sha(HERE/'evidence-v1.json'),
        contract=contract,APP_functions=appfuncs,SDK_functions=sdkfuncs,APP_native_witnesses=witnesses,
        APP_reference_CODE_bytes=632,SDK_reference_CODE_bytes=718,reference_instructions=sum(f['instructions']for f in appfuncs+sdkfuncs),
        inherited_conditional_bindings_retained=19,cumulative_conditional_bindings=21,cumulative_conditional_targets=16,
        cumulative_conditional_skips=5,not_joined_in_cumulative_ledger=30,missing_function_count_not_inferred=True,
        prior_composition=prior['composition'],APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,
        new_target_CODE_bytes=0,new_target_DATA_bytes=0,new_target_compilation=False,inherited_startup_source_gap_bytes=4,
        physical_compatibility_proved=False,Flash_callback_effects_closed=False,actual_global_binding_before_any_dispatch_proved=False,
        runtime_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,
        target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',required=True,type=Path);p.add_argument('--write-receipt',action='store_true');a=p.parse_args()
    try:
        v=verify(a.tool_dir.resolve())
        if a.write_receipt:
            dest=HERE/'verification-v1.json';need(not dest.exists(),'Create-only SNV/Flash receipt');dest.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(passed=True,APP_bytes=632,SDK_bytes=718,instructions=v['reference_instructions'],new_conditional_sites=2,
            SNVAddr=hex(v['contract']['original_config']['SNVAddr']),SNVBlock=256,SNVNum=3,new_BIN=False,firmware_ready=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
