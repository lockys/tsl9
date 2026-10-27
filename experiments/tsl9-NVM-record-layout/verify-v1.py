"""Decode original NVM records and compile numeric requirements;never execute them."""
import argparse,hashlib,json,re,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(ROOT/p),run_name='NVM_layout_static_library')
def canonical(v):return json.loads(json.dumps(v))
def sx(v,n):return v-(1<<n)if v&(1<<(n-1))else v
def immediate(o,rd,rs):
    w=int.from_bytes(bytes.fromhex(o['bytes']),'little');need(o['size']==4 and w&0x707f==0x13 and(w>>7)&31==rd and(w>>15)&31==rs,'Independent actual ADDI fields');return sx(w>>20,12)
def static_contract(S,E):
    raw=(ROOT/E['firmware']).read_bytes();B=lib('experiments/tsl9-original-startup/build-v1.py');V=lib('experiments/tsl9-original-RF-tx-path/audit-v1.py');C=lib('experiments/tsl9-original-APP-early-IRQ/verify-v1.py');A=lib('experiments/tsl9-original-APP-library-binding/verify-v1.py');P=lib('experiments/tsl9-original-RF-task-path/elf_reader-v6.py')['ELF'];I=lib('analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py')['ELF'];ops={};graphs={};functions=[]
    for f in E['references']:
        bb=raw[f['start']-0x8000:f['end']-0x8000];need(hashlib.sha256(bb).hexdigest()==f['original_sha256']and b''.join(bytes.fromhex(o['bytes'])for o in f['operations'])==bb,'Every actual original CODE byte');at=f['start']
        for o in f['operations']:need(o['addr']==at and o['size']==(4 if bytes.fromhex(o['bytes'])[0]&3==3 else 2),'Whole original instruction boundaries');at+=o['size']
        need(at==f['end'],'Complete selected interval');external={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))};oo,g,v=V['whole_cfg'](f,B,external,16 if f['start']==0x131c2 else 272);ops.update(oo);graphs[f['start']]=g;functions.append(v)
    need(len(functions)==7 and sum(v['bytes']for v in functions)==628 and sum(v['instructions']for v in functions)==189,'Seven actual complete original functions628B/189i')
    for mode in ['c','cpp']:
        p=ROOT/'experiments/tsl9-original-layout/build/safe-gap-v2'/mode/'NONLOADABLE-ORIGINAL-LAYOUT.elf';need(sha(p)==E['diagnostic_ELF_sha256'],'Retained diagnostic identity');a,b=P(p),I(p);need(a.header[0]==b.kind==2 and not any(h[0]==1 for h in a.program_headers),'Existing nonloadable diagnostic,not firmware')
        for f in E['references']:
            x,xo=A['native_bytes'](a,f['start'],f['end'],True);y,yo=A['native_bytes'](b,f['start'],f['end'],True);need(x==y==raw[f['start']-0x8000:f['end']-0x8000]and xo==yo,'All selected C/C++ diagnostic bytes equal original through independent readers')
    def upper(hi,lo,rd):return(C['constant'](ops[hi],rd)+immediate(ops[lo],rd,rd))&0xffffffff
    def pair(pc):return A['address_pair'](ops,pc)
    read_rows=[(0x131ca,0x131d4,0x131d8,0x131ce,0x131e0,None,0x13204,0x1316a),(0x1320e,0x13216,0x1321a,0x13212,0x13222,0x13224,0x13234,0x12e86),(0x1323e,0x13246,0x1324a,0x13242,0x13252,0x13254,0x13264,0x12f18),(0x1326e,0x13276,0x1327a,0x13272,0x13282,0x13284,0x13294,0x12f7a),(0x1329e,0x132a6,0x132aa,0x132a2,0x132b2,0x132b4,0x132c4,0x13084),(0x132ce,0x132d6,0x132da,0x132d2,0x132e2,0x132e4,0x132f8,0x13108)]
    writers={};writer_rows=[]
    for f in E['references'][1:]:
        p=f['start'];oo={o['addr']:o for o in f['operations']};need(oo[p]['opcode']=='lui a5, 0x40'and oo[p+4]['opcode']=='lw a5, 76(a5)'and oo[p+12]['opcode']=='mv a0, sp'and oo[p+26]['opcode']=='jalr a5'and oo[p+32]['opcode']=='mv a1, sp','Actual writer table/sourceSP ports');n=C['constant'](oo[p+14],12);source=pair(p+18);destination=upper(p+28,p+34,10);need(B['decode_control'](bytes.fromhex(oo[p+38]['bytes']),p+38)[1]==0x9c0a,'All six writers call actual same256-byte Flash transaction')
        need(oo[p+6]['opcode']=='addi sp, sp, -272'and oo[p+8]['opcode']=='sw ra, 268(sp)'and oo[p+42]['opcode']=='lw ra, 268(sp)'and oo[p+46]['opcode']=='addi sp, sp, 272','Actual all six frame/RA save-restore layout');need([o['addr']for o in f['operations']if o['opcode'].split()[0]in ['sw','sb','sh']]==[p+8],'Only explicit local store is savedRA;no local fill of remaining source bytes')
        need(all(p+48 not in V['reachable'](graphs[p],p,skip=pc)for pc in [p+26,p+38]),'Copy and Flash call dominate writer normal return');w=dict(start=p,end=f['end'],source=source,copy_count=n,copy_call=p+26,source_buffer='ownSP',own_frame=272,saved_RA_offset=268,Flash_destination=destination,Flash_call=p+38,CPU_program_bytes=256,additional_source_initialization_unproved_bytes=256-n,source_extent_within_frame_and_disjoint_RA=True);need(destination not in writers,'One unique writer per numeric page');writers[destination]=w;writer_rows.append(w)
    records=[];main=graphs[0x131c2]
    for i,(hi,lo,dest,count,call,guard,fallback_pc,fallback)in enumerate(read_rows):
        source=upper(hi,lo,11);ram=pair(dest);n=C['constant'](ops[count],12);need(ops[call]['opcode']=='jalr a5'and source in writers,'Read path has corresponding actual writer');wr=writers[source];need((wr['source'],wr['copy_count'])==(ram,n),'Independent read arguments match actual writer source/count')
        need(B['decode_control'](bytes.fromhex(ops[fallback_pc]['bytes']),fallback_pc)[1]==fallback,'Actual conditional fallback target')
        if i==0:
            gaddr=0x2000c2a8;gsize=4;need(ops[0x131f6]['opcode']=='lbu a5, 12(a4)'and pair(0x131e2)==ram and pair(0x131ea)==ram+4 and ops[0x13200]['opcode']=='bleu a5, a2, 0x132fc','Retained four-byte ASCII guard');condition='four ASCII bytes32..126'
        else:
            o=ops[guard+4];w=int.from_bytes(bytes.fromhex(o['bytes']),'little');need(o['size']==4 and w&0x707f==0x4003 and(w>>7)&31==14 and(w>>15)&31==14,'Independent original LBU A4,(A4) fields');u=int.from_bytes(bytes.fromhex(ops[guard]['bytes']),'little');need(u&127==0x17 and(u>>7)&31==14,'Actual guard AUIPC A4');gaddr=(guard+(u&0xfffff000)+sx(w>>20,12))&0xffffffff;gsize=1;condition='marker byte0x5A';need(ops[guard+8]['opcode']=='li a5, 90','Original marker literal')
        need(ram<=gaddr and gaddr+gsize<=ram+n,'Every guard lies inside its actually copied record');need(all(later[4]not in V['reachable'](main,0x131c2,skip=call)for later in read_rows[i+1:]),'Earlier record reads dominate later reads in whole normal-return CFG')
        records.append(dict(index=i,source=source,source_end_exclusive=source+n,RAM=ram,RAM_end_exclusive=ram+n,bytes=n,call_PC=call,guard_address=gaddr,guard_bytes=gsize,guard=condition,fallback_PC=fallback_pc,fallback_target=fallback,writer=wr))
    expected=[(0x08077a00,0x2000c29c,112),(0x08077900,0x2000c494,256),(0x08077800,0x2000c30c,256),(0x08077700,0x2000c594,256),(0x08077600,0x2000c694,256),(0x08077500,0x2000c40c,133)];need([(v['source'],v['RAM'],v['bytes'])for v in records]==expected,'All six actual source/RAM/count triples')
    h=(ROOT/S['header']).read_text('utf-8')
    for i,(source,ram,n)in enumerate(expected):
        for field,value in [('SOURCE',source),('RAM',ram),('BYTES',n)]:
            mat=re.search(r'^#define TSL9_NVM_'+str(i)+'_'+field+r' (?:UINT32_C\((0x[0-9a-f]+)\)|(\d+)u)$',h,re.M);need(mat and int(mat[1]or mat[2],0)==value,'C/C++ header fields equal independently decoded original records')
    ordered=sorted(records,key=lambda v:v['RAM']);need(all(a['RAM_end_exclusive']<=b['RAM']for a,b in zip(ordered,ordered[1:])),'Numeric nonoverlapping RAM intervals');total=sum(v['bytes']for v in records);lo,hi=ordered[0]['RAM'],ordered[-1]['RAM_end_exclusive'];need((total,lo,hi,hi-lo-total)==(1269,0x2000c29c,0x2000c794,3),'Actual payload sum/RAM span and three-byte gap')
    need(sorted(writers)==list(range(0x08077500,0x08077b00,256))and all(v['source']%256==0 for v in records),'Six distinct contiguous256-byte numeric program pages')
    reset=json.loads((ROOT/'experiments/tsl9-trap-profile-contract/evidence-v1.json').read_bytes());need(reset['zero_start']==0x20004080 and reset['zero_end']==0x2000c958 and reset['zero_start']<=lo<hi<=reset['zero_end'],'All buffers within original numeric reset zero interval,not an ownership/after-IRQ proof')
    return dict(passed=True,reference_CODE_bytes=628,reference_instructions=189,complete_functions=7,original_and_both_C_Cpp_native_bytes_equal=True,independent_ELF_readers=2,functions=functions,records=records,writers=writer_rows,record_payload_bytes=1269,RAM_span=[lo,hi],RAM_span_bytes=1272,RAM_gap_bytes=3,numeric_program_range=[0x08077500,0x08077b00],numeric_program_span_bytes=1536,flat_flash_base_assumption=0x08000000,conditional_flat_map_minimum_end_offset=0x77b00,flat_map_or_physical_capacity_proved=False,all_record_guards_inside_copy=True,marker_match_is_not_full_integrity_or_CRC_proof=True,additional_stack_source_initialization_unproved=dict(record0_bytes=144,record5_bytes=123),all_source_contents_or_private_identifiers_observed=False,reset_zero_numeric_coverage=True,buffer_ownership_or_alias_or_IRQ_stability_proved=False,hardware_NVM_map_proved=False,Flash_commit_or_poll_termination_proved=False)
def verify(llvm,refs,trial=None):
    S=json.loads((HERE/'spec-v1.json').read_bytes());need(all(sha(ROOT/p)==h for p,h in S['inputs'].items()),'All original/curated/prior proof inputs retained');need(all(sha(ROOT/S[k])==S[k+'_sha256']for k in ['source','header','evidence']),'Exact numeric sources and evidence');E=json.loads((ROOT/S['evidence']).read_bytes());prior=lib(E['prior_study']+'/audit-v1.py')['audit'](llvm,refs);need(canonical(prior)==json.loads((ROOT/E['prior_study']/'audit-result-v1.json').read_bytes())and sha(ROOT/E['prior_study']/'audit-result-v1.json')==E['prior_receipt_sha256'],'Fresh complete prior SDK/APP/native/IRQ/CFG proof');contract=static_contract(S,E);N=lib('experiments/tsl9-resident-range-random/build-v1.py');N['pins'](llvm);need(S['flags']==N['S']['flags']and S['tools']==N['S']['tools'],'Exact pinned compile flags/tools')
    folder=HERE/'build'/('native-v1'if trial is None else trial);measurement=folder/'measurement.json';inputs={str(p):dict(bytes=p.stat().st_size,sha256=sha(p))for p in [Path(__file__),HERE/'spec-v1.json',ROOT/S['source'],ROOT/S['header'],ROOT/S['evidence']]};inputs=N['portable'](inputs,llvm)
    if trial:need(Path(trial).name==trial and not folder.exists(),'Fresh create-only numeric compilation')
    saved=None if trial else json.loads(measurement.read_bytes());results={};artifacts={};dependencies={}
    if saved:need(saved['inputs']==inputs,'All actual contract compilation inputs retained')
    ELF=lib('experiments/tsl9-original-RF-task-path/elf_reader-v6.py')['ELF'];Compare=lib('experiments/tsl9-original-RF-task-path/compare-readers-v2.py')['audit']
    for mode in ['c','cpp']:
        f=folder/mode
        if trial:
            f.mkdir(parents=True);argv=[str(llvm/'clang.exe'),*S['flags'][mode],'-MD','-MF',str(f/'unit.d'),'-MT','unit.o','-c',str(ROOT/S['source']),'-o',str(f/'unit.o')];p=subprocess.run(argv,capture_output=True,timeout=120);(f/'compile.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual C/C++ numeric assertion compilation failed;trial retained')
        p=f/'unit.o';e=ELF(p);need(e.header[0]==1 and e.header[1]==243 and not e.program_headers and not e.relocations and not any(s['flags']&2 and s['size']for s in e.sections)and not any(s['info']>>4 for s in e.symbols),'Actual RV32 ET_REL has no allocated bytes,providers or imports');ind=Compare(p);need(ind['passed'],'Independent complete ELF reader agreement');results[mode]=dict(passed=True,object_sha256=sha(p),allocated_bytes=0,primary_record_fields=6,independent_readers=ind);artifacts[mode]=N['inventory'](f);dependencies[mode]=N['portable'](N['dependencies'](f,llvm),llvm)
        if saved:need(saved['modes'][mode]==dict(result=results[mode],artifacts=artifacts[mode],dependencies=dependencies[mode]),'Every native artifact,include and original compile result retained')
    need(results['c']==results['cpp'],'Actual C11/C++17 contract objects identical')
    if trial:measurement.write_text(json.dumps(dict(inputs=inputs,modes={m:dict(result=results[m],artifacts=artifacts[m],dependencies=dependencies[m])for m in ['c','cpp']}),indent=2)+'\n',encoding='utf-8')
    return dict(schema='TSL9-NVM-record-layout-verification-v1',passed=True,checker_sha256=sha(__file__),prior_rand_receipt_sha256=E['prior_receipt_sha256'],contract=contract,native_results=results,APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,SDK_CODE_bytes_unchanged=20490,SDK_DATA_bytes_unchanged=256,SDK_named_UND_unchanged=10,inherited_startup_source_gap_bytes=4,new_target_CODE_bytes=0,numeric_assertion_compilation_only=True,physical_ROM_RAM_ISA_IRQ_compatibility_proved=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--reference-root',type=Path,required=True);p.add_argument('--build-trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        v=verify(a.tool_dir.resolve(),a.reference_root.resolve(),a.build_trial)
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only NVM layout receipt');dest.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(passed=True,records=6,reference_CODE_bytes=628,reference_instructions=189,RAM_payload_bytes=1269,RAM_gap_bytes=3,additional_source_initialization_unproved=[144,123],numeric_assertion_allocated_bytes=0,physical_NVM_map_proved=False,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
