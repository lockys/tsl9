"""Verify sparse HEX admission, inclusive startup copy and real data-only C/C++ union."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def lib(p):return runpy.run_path(str(ROOT/p),run_name='initial_data_audit_library')
def canonical(v):return json.loads(json.dumps(v))
def sparse_hex(path):
    memory={};base=0;count=0;eof=False;types={}
    for line in path.read_text('ascii').splitlines():
        need(line.startswith(':')and not eof,'Bounded HEX records before EOF')
        record=bytes.fromhex(line[1:]);need(len(record)==record[0]+5 and sum(record)%256==0,'Actual Intel HEX length and checksum')
        count+=1;n,kind=record[0],record[3];addr=int.from_bytes(record[1:3],'big');data=record[4:4+n];types[kind]=types.get(kind,0)+1
        if kind==0:
            for i,b in enumerate(data):
                p=base+addr+i;need(0x40000<=p<0x70000 and p not in memory,'Unique bounded original HEX address');memory[p]=b
        elif kind==2:need(n==2 and addr==0,'Extended segment record');base=int.from_bytes(data,'big')<<4
        elif kind==3:need(n==4 and addr==0,'Original start-segment metadata')
        elif kind==1:need(n==0 and addr==0,'Actual HEX EOF');eof=True
        else:raise ValueError('Unadmitted HEX record type')
    need(eof and count==11973 and len(memory)==191244,'Complete original sparse HEX inventory')
    return memory,dict(records=count,data_bytes=len(memory),record_types=types)
def startup_contract(E):
    need(sha(ROOT/E['SDK_hex'])==E['SDK_hex_sha256'],'Exact public SDK HEX')
    m,info=sparse_hex(ROOT/E['SDK_hex']);main=(ROOT/E['SDK_firmware']).read_bytes()
    need(sha(ROOT/E['SDK_firmware'])==E['SDK_sha256']and bytes(m[p]for p in range(0x40000,0x6ea66))==main,'Main carrier equals actual contiguous HEX segment')
    source_map=load(ROOT/'analysis/wch-resident-candidate-2026-10-21/carrier-dec2023/source-map.json');segments=[];covered=set()
    for s in source_map['segments']:
        addresses=set(range(s['start'],s['end_exclusive']));need(not addresses&covered,'No overlapping sparse segment');covered.update(addresses)
        p=ROOT/'analysis/wch-resident-candidate-2026-10-21/carrier-dec2023'/s['path']
        need(p.stat().st_size==s['bytes']and sha(p)==s['sha256']and p.read_bytes()==bytes(m[a]for a in range(s['start'],s['end_exclusive'])),'Every actual sparse segment byte')
        segments.append(dict(start=s['start'],end=s['end_exclusive'],bytes=s['bytes'],sha256=s['sha256']))
    need(len(segments)==17 and sum(s['bytes']for s in segments)==len(m)and covered==set(m),'All seventeen disjoint segments retained,not one flattened image')
    G=lib('analysis/resident-entry-reference-2026-10-21/source/inspect-source.py');v=G['gate'](main)
    need(v['first']==[0x402b0,0x20000040,0x20002e70]and v['second']==[0x6eaa4,0x20002e70,0x20002ef8]and v['zero']==[0x20002ef8,0x20003614],'Actual raw-decoded startup constants and inclusive guards')
    # gate independently decodes the unsigned >= guard at40280, READ32,
    # increments and the following WRITE32; no target-state simulation.
    first_words=(v['first'][2]-v['first'][1])//4+1;second_words=(v['second'][2]-v['second'][1])//4+1
    need((first_words,second_words)==(2957,35),'Inclusive end words produce11828B and140B')
    wanted=range(v['second'][0],v['second'][0]+4*second_words);missing=[p for p in wanted if p not in m]
    need(missing==list(range(0x6eb2c,0x6eb30)),'Exactly four unprovided final READ32 bytes')
    raw=bytes(m[p]for p in range(E['source_start'],E['source_end']))
    need(raw==(ROOT/E['segment']).read_bytes()and sha(ROOT/E['segment'])==E['segment_sha256']and len(raw)==136,'Exact separately captured initial-state prefix')
    seed_ram=0x20002ec8;seed_source=E['source_start']+seed_ram-E['conditional_RAM_start'];seed=int.from_bytes(bytes(m[p]for p in range(seed_source,seed_source+4)),'little')
    need(seed_source==0x6eafc and seed==0x012f81c3,'Source-backed conditional seed initialization word')
    return dict(passed=True,HEX=info,segments=segments,first_copy=dict(source=[0x402b0,0x430e4],destination=[0x20000040,0x20002e74],words=2957,bytes=11828),
        second_copy=dict(source=[0x6eaa4,0x6eb30],destination=[0x20002e70,0x20002efc],words=35,bytes=140,
            provided_prefix_source=[0x6eaa4,0x6eb2c],provided_prefix_destination=[0x20002e70,0x20002ef8],provided_bytes=136,
            missing_source=[0x6eb2c,0x6eb30],unprovided_load_destination=[0x20002ef8,0x20002efc]),
        zero_helper=dict(destination=[0x20002ef8,0x20003618],words=456,bytes=1824,executes_only_after_normal_copy_return=True),
        later_zero_does_not_justify_skipping_unprovided_READ32=True,missing_capture_is_not_proof_of_physical_read_failure=True,
        initial_seed=dict(RAM=seed_ram,source=seed_source,value=seed,prefix_word_index=22,conditional_write_precedes_missing_load=True,
            requires='known bytes actually copied, normal earlier memory operations, matching ROM/ISA/RAM and unchanged live context',
            seed_at_first_random_call_or_entropy_proved=False),
        no_holes_filled=True,complete_startup_or_MRET_context_proved=False,installed_ROM_identity_proved=False)
def composition(path,inputs,N,O):
    P=lib('experiments/tsl9-sdk-unique-code-ownership/audit-v1.py');EL=lib('experiments/tsl9-resident-root-chain-callees/elf_reader-v7.py')['ELF']
    aa,dd,uu,rr={},{},set(),[]
    for p in inputs:
        a,d,u,r=P['facts'](p,EL);need(not set(aa)&set(a)and not set(dd)&set(d),'Unique real section and symbol owners');aa.update(a);dd.update(d);uu.update(u);rr+=r
    need(P['facts'](path,EL)==(aa,dd,uu-set(dd),sorted(rr)),'Every selected byte,symbol and relocation retained')
    before=O['inspect'](inputs[0]);after=O['inspect'](path)
    need(before['passed']and after['passed']and after['_byte_map']==before['_byte_map']and after['_typed_relations']==before['_typed_relations'],'All existing CODE and typed relations unchanged')
    ev=N['E'];data={**before['non_CODE_allocations'],ev['section']:dict(type=1,flags=2,size=136,alignment=4,sha256=ev['segment_sha256'])}
    need(after['non_CODE_allocations']==data and not after['named_UND']and after['CODE_bytes']==35324,'Only one genuine readonly136B data allocation added; zero named UND')
    independent=lib('experiments/tsl9-resident-root-chain-callees/compare-readers-v3.py')['audit'](path);need(independent['passed'],'Independent whole native readers')
    return dict(**O['public'](after),DATA_bytes=392,instructions=12195,allocated_bytes=35716,independent_readers=independent,
        every_input_byte_symbol_relocation_retained=True,new_CODE_bytes=0,new_DATA_bytes=136,
        actual_original_address_link_performed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False)
def audit(llvm,link=False):
    E=load(HERE/'evidence-v1.json')
    need(all(sha(ROOT/p)==h for p,h in E['reference_inputs'].items())and all(sha(ROOT/p)==h for p,h in E['whole_reader_inputs'].items()),'All frozen source/native/reader references')
    prior=lib(E['prior_study']+'/verify-v1.py')['verify'](llvm);need(canonical(prior)==load(ROOT/E['prior_verification']),'Fresh complete prior callback/native/source chain')
    contract=startup_contract(E);N=lib('experiments/tsl9-resident-initial-data-prefix/build-v1.py');units=N['replay'](llvm)
    O=lib('experiments/tsl9-resident-root-chain-callees/verify-ownership-v3.py');folder=HERE/'build/composition-v1'
    if link:need(not folder.exists(),'Create-only data partial link')
    composed={}
    for mode in ['c','cpp']:
        inputs=[ROOT/E['parent_study']/'build/composition-v1'/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];p=folder/mode
        need(sha(inputs[0])==prior['prior_composition']['object_sha256']and sha(inputs[1])==units[mode]['object_sha256'],'Exact current parent and new data objects')
        if link:
            p.mkdir(parents=True);proc=subprocess.run([str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(x)for x in inputs],'-o',str(p/'candidate.o')],capture_output=True,timeout=120)
            (p/'link.log').write_text(N['portable']((proc.stdout+proc.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(proc.returncode==0,'Actual nonloadable partial link; log retained')
        composed[mode]=composition(p/'candidate.o',inputs,N,O)
    need(composed['c']==composed['cpp'],'Identical actual complete C/C++ composition objects')
    return dict(schema='TSL9-initial-data-prefix-audit-v1',passed=True,checker_sha256=sha(__file__),builder_sha256=sha(HERE/'build-v1.py'),
        evidence_sha256=sha(HERE/'evidence-v1.json'),contract=contract,native_results=units,composition=composed,
        new_CODE_bytes=0,new_DATA_bytes=136,new_instructions=0,APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,
        inherited_conditional_sites=35,inherited_startup_source_gap_bytes=4,installed_ROM_identity_proved=False,
        physical_RAM_capacity_proved=False,physical_ISA_IRQ_or_Flash_compatibility_proved=False,complete_startup_proved=False,
        linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,
        target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--link',action='store_true');p.add_argument('--write-receipt',action='store_true');a=p.parse_args()
    try:
        v=audit(a.tool_dir.resolve(),a.link)
        if a.write_receipt:
            dest=HERE/'audit-result-v1.json';need(not dest.exists(),'Create-only data audit receipt');dest.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(passed=True,new_DATA_bytes=136,composition_CODE_bytes=35324,composition_DATA_bytes=392,
            missing_startup_source_bytes=4,conditional_initial_seed=hex(v['contract']['initial_seed']['value']),new_BIN=False,firmware_ready=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
