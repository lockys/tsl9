#!/usr/bin/env python3
"""Compile/read five complete SDK callback/LLE/gateway candidates;never execute or install them."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
S=json.loads((HERE/'spec-v1.json').read_bytes());EV=json.loads((ROOT/S['reference_candidate']).read_bytes())
SHARED='experiments/tsl9-original-startup/build-v1.py'
DEPENDENCIES='scripts/verify-curated-source.py'
APP='firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'

def need(ok,label):
    if not ok:raise ValueError(label)

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(ROOT/p),run_name='candidate_message_native_library')
need(sha(ROOT/SHARED)=='1f6e3673c24a5d85c62d55ec8d8390b80225577010d81c8aba5c4b6750e208b5','Frozen original-control decoder')
B=lib(SHARED);portable,encoded=B['portable'],B['encoded']

def original(start,end):
    rows=[f for f in EV['selected_functions']if f['start']<=start and end<=f['end']]
    need(len(rows)==1,'One explicit SDK candidate source mapping');f=rows[0]
    offset=f['source_start']+start-f['start']-0x40000
    return (ROOT/S['firmware']).read_bytes()[offset:offset+end-start]

def dependencies(folder,llvm):return lib(DEPENDENCIES)['dependencies'](folder,'origin',llvm.parent/'lib/clang/18')
def inventory(folder):return {p.name:dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(folder.iterdir())if p.is_file()}

def audit_object(path):
    e=lib(S['reader'])['ELF'](path)
    need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual nonloadable RISC-V ET_REL')
    rows=[s for s in e.symbols if s['info']>>4];gm={s['name']:s for s in rows}
    need(len(rows)==len(gm) and set(gm)=={r['name']for r in S['regions']}|set(S['undefined']),'Exact23 CODE definitions; no invented provider')
    for name in S['undefined']:
        s=gm[name];need((s['info'],s['other'],s['section'],s['value'],s['size'])==(16,0,0,0,0),'Actual referenced NOTYPE UND without fabricated body')
    expected=[];owned=set();count=total=0
    for r in S['regions']:
        s=gm[r['name']];sec=e.sections[s['section']]
        need((s['info'],s['other'],s['value'],s['size'])==(18,0,0,r['bytes']),'Real positive CODE owner')
        need((sec['name'],sec['type'],sec['flags'],sec['address'],sec['size'])==('.text.'+r['name'],1,6,0,r['bytes']),'Exact allocated code section')
        need(sec['index']not in owned,'Unique real allocation');owned.add(sec['index'])
        raw=e.data(sec);reference=original(r['start'],r['end']);normalized=bytearray(raw)
        need(hashlib.sha256(reference).hexdigest()==r['original_sha256'],'Actual mapped SDK reference block')
        for edge in [v for v in S['controls']if v['owner']==r['name']]:
            off,kind=edge['offset'],edge['type'];width,mask=B['MASKS'][kind]
            a=int.from_bytes(raw[off:off+width],'little');b=int.from_bytes(reference[off:off+width],'little')
            need(width==edge['size']and off+width<=len(raw)and a&mask==b&mask and a&(~mask&((1<<(width*8))-1))==0,'Exact direct control opcode/register bits,zero native displacement')
            need(B['decode_control'](reference[off:off+width],edge['PC'])==(kind,edge['target_PC']),'Original direct transfer decoded independently')
            normalized[off:off+width]=(a|B['immediate'](kind,edge['target_PC']-edge['PC'])).to_bytes(width,'little')
            expected.append((sec['index'],off,kind,0,edge['target']))
        for pair in [v for v in S['PC_relative_pairs']if v['owner']==r['name']]:
            off=pair['offset'];label='.Lresident_completion_status_gates_literal_'+format(pair['PC'],'x')
            anchors=[s for s in e.symbols if s['name']==label]
            need(len(anchors)==1,'One real far-call HI anchor');a=anchors[0]
            need((a['info'],a['other'],a['size'],a['section'],a['value'])==(0,0,0,sec['index'],off),'Exact local HI owner/offset')
            delta=(pair['target_PC']-pair['PC'])&0xffffffff
            for at,kind,mask,imm,target in [(off,23,0xfff,(delta+0x800)&0xfffff000,pair['target']),(off+4,24,0xfffff,(delta&0xfff)<<20,label)]:
                a=int.from_bytes(raw[at:at+4],'little');b=int.from_bytes(reference[at:at+4],'little')
                need(at+4<=len(raw)and a&mask==b&mask and a&(~mask&0xffffffff)==0,'Exact far-call opcode/register bits,zero native displacement')
                normalized[at:at+4]=((a&mask)|imm).to_bytes(4,'little');expected.append((sec['index'],at,kind,0,target))
            need(int.from_bytes(reference[off:off+4],'little')&0x7f==0x17 and int.from_bytes(reference[off+4:off+8],'little')&0x707f==0x67,'AUIPC/JALR code call,not an address-only ADDI pair')
        need(bytes(normalized)==reference,'Every246 SDK byte equal after original-context reference encoding')
        at=0
        while at<len(raw):
            width=4 if raw[at]&3==3 else 2;need(at+width<=len(raw),'Whole actual instruction');at+=width;count+=1
        total+=len(raw)
    actual=[(r['section'],r['offset'],r['type'],r['addend'],e.symbols[r['symbol']]['name'])for r in e.relocations]
    need(sorted(actual)==sorted(expected)and len(actual)==9,'Exactly9 direct controls and0 far transfers')
    need(total==246 and count==86 and len(owned)==23,'Five complete actual status gates')
    need({s['index']for s in e.sections if s['flags']&2 and s['size']}==owned,'No extra runtime data,padding or fabricated provider')
    need(sha(ROOT/'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py')=='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141','Pinned independent raw ELF reader')
    comparison=lib('experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path);need(comparison['passed'],'Independent full ELF agreement')
    return dict(passed=True,SDK_candidate_only=True,CODE_bytes=246,instructions=86,positive_FUNC_regions=23,relocations=9,direct_controls=9,far_call_pairs=0,far_tail_pairs=0,
        UND=S['undefined'],raw_RAM_dependencies_not_provided=True,opaque_callbacks_not_provided=0,opaque_call_sites=0,all_indirect_callback_targets_closed=False,runtime_closed=False,independent_readers=comparison,object_sha256=sha(path),all_original_SDK_VA_encoded_bytes_equal=True,
        explicit_conditional_Xwchc_byte_halfword_ports=14,compiler_arch_attribute_is_not_physical_ISA_proof=True,
        installed_ROM_identity_proved=False,actual_original_address_link_performed=False,APP_byte_coverage_unchanged=95.67,
        target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False,new_BIN=False,firmware_ready=False)

def audit_abi(path):
    e=lib(S['reader'])['ELF'](path);need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual RV32 numeric assertion object');need(not any(s['flags']&2 and s['size']for s in e.sections)and not e.relocations and not any(s['info']>>4 for s in e.symbols),'Zero allocation/providers/imports');ind=lib('experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path);need(ind['passed'],'Independent assertion readers');return dict(passed=True,object_sha256=sha(path),RV32_pointer_bytes=4,numeric_layout_assertions_only=True,own_frames=[0,0,0,0,0],allocated_bytes=0,independent_readers=ind,target_executed=False,installed_layout_proved=False)

def candidate_contract():
    need(len(json.loads((ROOT/'src/source-manifest.json').read_bytes())['files'])==162,'FormalAPP source inventory retained');return dict(conditional_SDK_only=True,raw_dependencies=EV['raw_dependencies'],opaque_transfers=EV['opaque_transfers'],real_prior_providers=EV['real_prior_providers'],retained_prior_genuine_UND=EV['retained_prior_genuine_UND'],new_genuine_code_dependencies=EV['new_genuine_code_dependencies'],post_return_branches_and_frame_released_tail_preserved=True,inherited_second_copy_missing_source_bytes=4,installed_ROM_identity_proved=False,runtime_closed=False,hardware_accessed=False)

def inputs(llvm):
    paths={Path(__file__),HERE/'spec-v1.json',ROOT/S['ABI_source'],ROOT/SHARED,ROOT/DEPENDENCIES,ROOT/S['reader'],ROOT/S['source'],ROOT/S['source_deriver'],ROOT/S['reference_candidate'],ROOT/S['firmware'],ROOT/APP,ROOT/'src/source-manifest.json',ROOT/'analysis/safe-gap-integration-2026-10-26/summary.json',ROOT/'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py',ROOT/'experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py',llvm.parent/'lib/clang/18/include/stdint.h'}
    paths.update(ROOT/EV[k]for k in ['header','instruction_reference','mapping_proof']);paths.add(ROOT/EV['official_vectors']['path']);paths.update(llvm/n for n in S['tools'])
    return {str(p):dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(paths)}

def pins(llvm):
    need(sha(ROOT/S['ABI_source'])==S['ABI_source_sha256'],'Pinned original-header compile-only ABI assertions')
    need(sha(ROOT/EV['official_vectors']['path'])==EV['official_vectors']['sha256'],'Pinned official custom instruction vectors')
    for k in ['source','firmware','reader','reference_candidate','source_deriver']:need(sha(ROOT/S[k])==S[k+'_sha256'],'Pinned '+k)
    for k in ['header','instruction_reference','mapping_proof']:need(sha(ROOT/EV[k])==EV[k+'_sha256'],'Pinned conditional SDK '+k)
    for n,h in S['tools'].items():need(sha(llvm/n)==h,'Pinned compiler/tool '+n)
    need(sha(llvm.parent/'lib/clang/18/include/stdint.h')==S['stdint_sha256'],'Pinned compiler resource')
    need(sha(ROOT/DEPENDENCIES)=='1b07fcc89584794389b87c1721e9669285cd5948f9cfbe8be979cf071e7b3832','Frozen dependency parser and register recipe')
    expected={mode:lib(DEPENDENCIES)['flags']({'profile':'queue-consumer-a0-a5'},mode)for mode in ['c','cpp']}
    for flags in expected.values():flags[flags.index('-march=rv32imac_zicsr')]='-march=rv32imac_zicsr_zifencei'
    need(expected==S['flags'],'Exact register recipe plus FENCE.I; No Xwchc instructions occur raw reviewed ports')
    generated=lib(S['source_deriver'])['generate']()
    need(generated['source']==(ROOT/S['source']).read_text(encoding='utf-8'),'Exact generated register-context C source')
    for k in ['regions','controls','PC_relative_pairs','literal_data','undefined']:need(generated[k]==S[k],'Exact typed source inventory '+k)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);g=p.add_mutually_exclusive_group(required=True);g.add_argument('--trial');g.add_argument('--replay',type=Path)
    a=p.parse_args();llvm=a.tool_dir.resolve();pins(llvm);before=portable(inputs(llvm),llvm);contract=candidate_contract()
    if a.replay:
        out=a.replay.resolve();need(out.parent==HERE/'build','Owned retained native trial');saved=json.loads((out/'measurement.json').read_bytes())
        need(saved['inputs']==before and saved['candidate_contract']==contract,'Every retained candidate input unchanged')
        for mode in ['c','cpp']:
            f=out/mode;need(saved['modes'][mode]['artifacts']==inventory(f)and saved['modes'][mode]['result']==audit_object(f/'unit.o'),'Exact retained candidate object')
            need(saved['modes'][mode]['dependencies']==portable(dependencies(f,llvm),llvm),'Exact native include dependencies')
            need(saved['modes'][mode]['ABI_result']==audit_abi(f/'config_abi.o'),'Retained actual compile-only ABI proof')
        print(json.dumps(dict(passed=True,mode='read-only-SDK-candidate-replay',CODE_bytes=246,instructions=86,installed_ROM_identity_proved=False,target_executed=False)));return
    need(a.trial and Path(a.trial).name==a.trial,'One create-only trial name');out=HERE/'build'/a.trial;need(not out.exists(),'Retain existing native trials')
    record=dict(inputs=before,candidate_contract=contract,modes={})
    for mode in ['c','cpp']:
        f=out/mode;f.mkdir(parents=True);jobs=[]
        for label,argv in [('compile',[str(llvm/'clang.exe')]+S['flags'][mode]+['-MD','-MF',str(f/'unit.d'),'-MT','unit.o','-c',str(ROOT/S['source']),'-o',str(f/'unit.o')]),('read',[str(llvm/'llvm-objdump.exe'),'-h','-t','-r',str(f/'unit.o')]),('compile-ABI',[str(llvm/'clang.exe')]+S['flags'][mode]+['-MD','-MF',str(f/'config_abi.d'),'-MT','config_abi.o','-c',str(ROOT/S['ABI_source']),'-o',str(f/'config_abi.o')]),('read-ABI',[str(llvm/'llvm-objdump.exe'),'-h','-t','-r',str(f/'config_abi.o')])]:
            result=subprocess.run(argv,cwd=ROOT,capture_output=True,timeout=120);(f/(label+'.log')).write_text(portable((result.stdout+result.stderr).decode('utf-8','replace'),llvm),encoding='utf-8')
            jobs.append(dict(label=label,argv=portable(argv,llvm),exit=result.returncode));need(result.returncode==0,'Native '+label+' failed; local log retained')
        record['modes'][mode]=dict(result=audit_object(f/'unit.o'),ABI_result=audit_abi(f/'config_abi.o'),commands=jobs,dependencies=portable(dependencies(f,llvm),llvm),artifacts=inventory(f))
    need(record['modes']['c']['result']['object_sha256']==record['modes']['cpp']['result']['object_sha256'],'Identical actual C/C++ objects')
    need(record['modes']['c']['ABI_result']['object_sha256']==record['modes']['cpp']['ABI_result']['object_sha256'],'Identical actual C/C++ ABI assertion objects')
    need(before==portable(inputs(llvm),llvm),'Every input unchanged through compilation')
    (out/'measurement.json').write_bytes(encoded(record));print(json.dumps({k:v for k,v in record['modes']['c']['result'].items()if k!='independent_readers'}))

if __name__=='__main__':
    try:main()
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
