#!/usr/bin/env python3
"""Audit original copy-source windows and compile readonly C/C++ data; never execute it."""
from pathlib import Path
import argparse,hashlib,json,runpy,subprocess,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SPEC=HERE/'spec-v1.json'
S=json.loads(SPEC.read_bytes())
SHARED='experiments/tsl9-original-startup/build-v1.py'
SHARED_SHA='1f6e3673c24a5d85c62d55ec8d8390b80225577010d81c8aba5c4b6750e208b5'
CMP='experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py'

def need(ok,message):
    if not ok:raise ValueError(message)

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def encode(v):return (json.dumps(v,indent=2,sort_keys=True)+'\n').encode()

def library(p):return runpy.run_path(str(ROOT/p),run_name='offline_copy_library')

def signed(v,bits):return v-(1<<bits)if v&(1<<(bits-1))else v

def source_text(e,fw):
    lines=['#include <stdint.h>','/* Bounded static copy-source windows, NOT identified physical features.',
           ' * Lengths follow original call sites and the complete software-copy body.',
           ' * This file contains readonly DATA only; it is not firmware or a boot image. */',
           '#if defined(__cplusplus)','#define COPY_WINDOW extern "C" __attribute__((used,aligned(4)))',
           '#else','#define COPY_WINDOW __attribute__((used,aligned(4)))','#endif','']
    for o in e['objects']:
        raw=fw[o['start']-0x8000:o['end']-0x8000]
        lines += [f'COPY_WINDOW __attribute__((section("{o["section"]}")))',
                  f'const uint8_t {o["name"]}[{o["bytes"]}] = {{']
        lines += ['    '+', '.join('0x'+format(v,'02x')for v in raw[i:i+12])+','for i in range(0,len(raw),12)]
        lines += ['};','']
    return '\n'.join(lines)

def static_audit():
    need(sha(ROOT/SHARED)==SHARED_SHA,'Frozen bit/control decoder')
    need(sha(ROOT/S['evidence'])==S['evidence_sha256'],'Frozen original evidence')
    e=json.loads((ROOT/S['evidence']).read_bytes())
    fw=(ROOT/e['firmware']).read_bytes()
    need(sha(ROOT/e['firmware'])==e['firmware_sha256']and len(fw)==76800,'Exact official original firmware')
    need(S['objects']==e['objects']and S['bytes']==200,'Two bounded DATA source windows')
    need(sha(ROOT/S['source'])==S['source_sha256']and (ROOT/S['source']).read_text(encoding='utf8')==source_text(e,fw),'Actual C literals derived from original source bytes')
    ops={}
    for f in e['functions']:
        need(sha(ROOT/f['source_evidence'])==f['source_evidence_sha256'],'Retained original function evidence')
        at=f['start']
        for o in f['operations']:
            raw=bytes.fromhex(o['bytes'])
            need(at==o['addr']and len(raw)==o['size']and raw==fw[at-0x8000:at-0x8000+o['size']],'Every original instruction byte and boundary')
            need(o['addr']not in ops,'Unique original instruction')
            ops[at]=o;at+=o['size']
        need(at==f['end'],'Full original function interval')
    need(len(ops)==82 and [(f['start'],f['end'],len(f['operations']))for f in e['functions']]==[(0x12ad0,0x12b24,28),(0x19bf0,0x19ca6,54)],'Complete caller and complete software-copy body')
    decoder=library(SHARED)['decode_control']
    def word(pc):return int.from_bytes(bytes.fromhex(ops[pc]['bytes']),'little')
    def text(pc,expected):need(ops[pc]['opcode']==expected,'Original instruction semantics at '+hex(pc))
    def control(pc,dest,kind):need(decoder(bytes.fromhex(ops[pc]['bytes']),pc)==(kind,dest),'Actual bit-decoded control at '+hex(pc))
    # Derive source pointer, copy length, destination and direct target independently
    # from instruction fields, not adjacent DATA addresses or table guesses.
    calls=[]
    for o in e['objects']:
        hi,lo=word(o['hi_PC']),word(o['lo_PC'])
        need(hi&0xfff==0x597 and lo&0xfffff==0x58593,'Actual AUIPC A1 and ADDI A1,A1')
        target=(o['hi_PC']+(hi&0xfffff000)+signed(lo>>20,12))&0xffffffff
        nword=word(o['length_PC'])
        need(nword&0xfffff==0x613 and signed(nword>>20,12)==o['bytes'],'Actual ADDI A2,X0 copy length')
        w=word(o['destination_PC'])
        offset=(((w>>7)&15)<<6)|(((w>>11)&3)<<4)|(((w>>5)&1)<<3)|(((w>>6)&1)<<2)
        need(ops[o['destination_PC']]['size']==2 and w&0xe003==0 and 8+((w>>2)&7)==10 and offset==4,'Actual compressed SP+4 destination')
        call=word(o['copy_call_PC'])
        need(ops[o['copy_call_PC']]['size']==4 and call&0xfff==0xef,'Actual JAL RA')
        control(o['copy_call_PC'],0x19bf0,17)
        forward=word(o['forward_length_PC'])
        need(forward&0xfffff==0x593 and signed(forward>>20,12)==o['bytes'],'Same length forwarded to subsequent helper')
        need(target==o['start']and o['end']==target+o['bytes']and target%4==0,'Exact original aligned source interval')
        raw=fw[target-0x8000:o['end']-0x8000]
        need(len(raw)==o['bytes']and hashlib.sha256(raw).hexdigest()==o['original_sha256'],'Complete source-window bytes')
        need(not(target<0x1a6a0 and 0x1a69c<o['end']),'Outside protected interval')
        need(4+o['bytes']<=124,'Selected local buffer ends before saved return address')
        calls.append(dict(source_start=target,source_end=o['end'],bytes=o['bytes'],copy_call_PC=o['copy_call_PC'],destination_stack_offset=4,stack_end_exclusive=4+o['bytes'],saved_RA_stack_offset=124,forward_length=o['bytes'],aligned_destination_group_bytes=72,aligned_destination_word_bytes=(o['bytes']//4)*4-72,aligned_destination_tail_bytes=o['bytes']%4))
    text(0x12ad0,'addi sp, sp, -128');text(0x12ad2,'sw ra, 124(sp)')
    text(0x12ae2,'lw ra, 124(sp)');text(0x12ae4,'addi sp, sp, 128')
    control(0x12ad6,0x12aee,16);control(0x12ade,0x12b0c,16)
    control(0x12b06,0x128fe,17);control(0x12b22,0x12b04,45)
    # All original reads/writes are included: two byte loops, a nine-word
    # group (the final load follows source+=36), and a single-word tail loop.
    reads=[(0x19c08,3,4,13,11,0),(0x19c22,3,4,13,11,0),
           (0x19c40,3,2,7,11,0),(0x19c44,3,2,5,11,4),
           (0x19c48,3,2,31,11,8),(0x19c4c,3,2,30,11,12),
           (0x19c50,3,2,29,11,16),(0x19c54,3,2,28,11,20),
           (0x19c58,3,2,6,11,24),(0x19c5c,3,2,17,11,28),
           (0x19c68,3,2,16,11,-4)]
    for pc,opcode,kind,rd,rs,imm in reads:
        w=word(pc)
        need(ops[pc]['size']==4 and w&127==opcode and(w>>12)&7==kind and(w>>7)&31==rd and(w>>15)&31==rs and signed(w>>20,12)==imm,'Actual load fields at '+hex(pc))
    text(0x19c92,'lw a2, 0(a1)')
    need(word(0x19c92)==0x4190,'Actual compressed tail LW encoding')
    writes=[(0x19c10,0,13,-1),(0x19c2a,0,13,-1),
            (0x19c64,2,7,0),(0x19c6c,2,5,4),(0x19c70,2,31,8),
            (0x19c74,2,30,12),(0x19c78,2,29,16),(0x19c7c,2,28,20),
            (0x19c80,2,6,24),(0x19c84,2,17,28),(0x19c8c,2,16,-4),
            (0x19c98,2,12,-4)]
    for pc,kind,rs2,imm in writes:
        w=word(pc);offset=signed(((w>>25)<<5)|((w>>7)&31),12)
        need(ops[pc]['size']==4 and w&127==0x23 and(w>>12)&7==kind and(w>>15)&31==15 and(w>>20)&31==rs2 and offset==imm,'Actual store fields at '+hex(pc))
    arithmetic={0x19bf0:'xor a5, a1, a0',0x19bf4:'andi a5, a5, 3',0x19bf6:'add a4, a0, a2',0x19bfc:'li a5, 3',0x19c02:'mv a5, a0',0x19c0c:'addi a5, a5, 1',0x19c0e:'addi a1, a1, 1',0x19c1a:'andi a3, a0, 3',0x19c1e:'mv a5, a0',0x19c26:'addi a5, a5, 1',0x19c28:'addi a1, a1, 1',0x19c2e:'andi a3, a5, 3',0x19c34:'andi a3, a4, -4',0x19c38:'addi a2, a3, -32',0x19c60:'addi a1, a1, 36',0x19c88:'addi a5, a5, 36',0x19c94:'addi a5, a5, 4',0x19c96:'addi a1, a1, 4'}
    for pc,v in arithmetic.items():text(pc,v)
    branches=[(0x19bfa,0x19c02,44,'bnez a5, 0x19c02'),(0x19bfe,0x19c1a,16,'bltu a5, a2, 0x19c1a'),(0x19c04,0x19ca4,16,'bleu a4, a0, 0x19ca4'),(0x19c14,0x19c08,16,'bltu a5, a4, 0x19c08'),(0x19c20,0x19c34,44,'beqz a3, 0x19c34'),(0x19c32,0x19c20,45,'j 0x19c20'),(0x19c3c,0x19c9c,16,'bleu a2, a5, 0x19c9c'),(0x19c90,0x19c3c,45,'j 0x19c3c'),(0x19c9c,0x19c92,16,'bltu a5, a3, 0x19c92'),(0x19ca0,0x19c08,16,'bltu a5, a4, 0x19c08')]
    for pc,target,kind,op in branches:control(pc,target,kind);text(pc,op)
    for pc in (0x19c18,0x19ca4):need(word(pc)==0x8082,'Original return, not hidden call')
    covered={pc for pc,*_ in reads}|{0x19c92}|{pc for pc,*_ in writes}|set(arithmetic)|{pc for pc,*_ in branches}|{0x19c18,0x19ca4}
    need(covered=={o['addr']for o in e['functions'][1]['operations']},'All54 copy instructions classified, no unexamined memory/control operation')
    for p,k in [('parent_component','parent_component_sha256'),('parent_layout_builder','parent_layout_builder_sha256'),('parent_spec','parent_spec_sha256')]:need(sha(ROOT/e[p])==e[k],'Current parent evidence unchanged')
    layout=library(e['parent_layout_builder']);plan=layout['derive'](layout['E'](ROOT/e['parent_component']))
    need(len(plan['owners'])==5721 and sum(o['bytes']for o in plan['owners'])==67455,'Exact current integrated parent')
    for o in e['objects']:
        need(not any(o['start']<p['original_PC']+p['bytes']and p['original_PC']<o['end']for p in plan['owners']),'No CODE/DATA overlap in selected source windows')
        need(any(p['source_symbol']==o['name']and p['original_reference_PC']==o['start']for p in plan['imports']),'Existing real unresolved DATA import')
    return dict(passed=True,original_instructions=82,complete_copy_instructions=54,classified_copy_instructions=len(covered),independently_decoded_memory_operations=24,bit_decoded_copy_controls=10,calls=calls,source_windows=2,source_bytes=200,excluded_gap_bytes=2,existing_parent_selected_bytes=67455,source_unit_curated_or_integrated=False,feature_meaning_proved=False,original_declared_object_extents_proved=False,
                bound_argument='With valid accessible nonwrapping pointers, byte paths advance both pointers by1. For matched alignment, peeling reaches a word boundary; the 36-byte group runs only for d < floor4(end)-32, hence aligned d <= floor4(end)-36. Its last source load is s+32 (postincrement -4), covering exactly36 bytes. The word loop requires d < floor4(end), hence d+4 <= floor4(end). The byte tail requires d < end. Equal pointer progress bounds every read to the n-byte source window. Length94 or106 is greater than the maximum alignment peel.',
                preconditions=['Original copied source windows remain readable and immutable','Destination stack buffer is valid and accessible','Pointer arithmetic does not wrap','No asynchronous corruption of pointers, stack or code'],target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False,firmware_ready=False)

def object_audit(path):
    e=library(S['reader'])['ELF'](path)
    need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual RISC-V ET_REL')
    alloc={v['name']:v for v in e.sections if v['flags']&2 and v['size']}
    need(set(alloc)=={v['section']for v in S['objects']},'Only the two selected readonly sections')
    rows=[v for v in e.symbols if v['info']>>4];gm={v['name']:v for v in rows}
    need(len(gm)==len(rows)==2 and set(gm)=={v['name']for v in S['objects']},'Exactly two genuine DATA definitions, no imported/stub/ABS providers')
    need(not e.relocations and not any(v['info']&15==2 and v['section']for v in e.symbols),'No relocations or executable functions')
    ev=json.loads((ROOT/S['evidence']).read_bytes());fw=(ROOT/ev['firmware']).read_bytes()
    for d in S['objects']:
        sec=alloc[d['section']];v=gm[d['name']]
        need((sec['type'],sec['flags'],sec['address'],sec['size'],sec['align'])==(1,2,0,d['bytes'],4),'Exact readonly source allocation')
        need((v['info'],v['other'],v['section'],v['value'],v['size'])==(17,0,sec['index'],0,d['bytes']),'Whole actual OBJECT owner')
        need(e.data(sec)==fw[d['start']-0x8000:d['end']-0x8000],'Every compiler DATA byte equals the actual original source window')
    independent=library(CMP)['audit'](path)
    return dict(passed=True,OBJECT=2,FUNC=0,UND=0,RELA=0,allocated_bytes=200,object_sha256=sha(path),independent_readers=independent,integrated=False,firmware_ready=False)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--static-only',action='store_true')
    p.add_argument('--tool-dir',type=Path)
    g=p.add_mutually_exclusive_group();g.add_argument('--trial');g.add_argument('--replay',type=Path)
    a=p.parse_args();facts=static_audit()
    if a.static_only:
        need(not(a.tool_dir or a.trial or a.replay),'Static-only does not compile');print(json.dumps(facts));return
    need(a.tool_dir is not None and bool(a.trial or a.replay),'Explicit tool directory and create-only trial or read-only replay')
    llvm=a.tool_dir.resolve()
    for n,h in S['tools'].items():need(sha(llvm/n)==h,'Pinned local compiler tool '+n)
    need(sha(llvm.parent/'lib/clang/18/include/stdint.h')==S['stdint_sha256'],'Pinned compiler header')
    need(sha(ROOT/S['reader'])==S['reader_sha256']and sha(ROOT/S['curation_checker'])==S['curation_checker_sha256'],'Pinned reader and established compiler profile')
    need(S['flags']=={m:library(S['curation_checker'])['flags']({'profile':S['profile']},m)for m in ('c','cpp')},'Unmodified established data compiler flags')
    paths=[Path(__file__),SPEC,ROOT/S['source'],ROOT/S['evidence'],ROOT/S['reader'],ROOT/S['curation_checker'],ROOT/SHARED,ROOT/CMP,llvm.parent/'lib/clang/18/include/stdint.h']+[llvm/n for n in S['tools']]
    portable=library(SHARED)['portable']
    inputs=portable({str(p):sha(p)for p in paths},llvm)
    if a.replay:
        out=a.replay.resolve();need(out.parent==HERE/'build','Only this experiment output')
        saved=json.loads((out/'measurement.json').read_bytes());need(saved['inputs']==inputs and saved['static']==facts,'All source, tools and static facts unchanged')
        for mode in ('c','cpp'):
            need(saved['modes'][mode]['artifacts']=={v.name:sha(v)for v in sorted((out/mode).iterdir())if v.is_file()},'Complete retained compiler output inventory')
            need(saved['modes'][mode]['audit']==object_audit(out/mode/'unit.o'),'Actual retained C/C++ object replay')
        print(json.dumps(dict(passed=True,mode='read-only-replay',languages=['c','cpp'],data_bytes=200,source_unit_curated_or_integrated=False,firmware_ready=False)));return
    need(Path(a.trial).name==a.trial,'Single trial basename');out=HERE/'build'/a.trial;need(not out.exists(),'Create-only native trial')
    report=dict(schema='TSL9-record-copy-windows-native-measurement-v1',inputs=inputs,static=facts,modes={})
    for mode in ('c','cpp'):
        d=out/mode;d.mkdir(parents=True)
        argv=[str(llvm/'clang.exe')]+S['flags'][mode]+['-MD','-MF',str(d/'unit.d'),'-MT','unit.o','-c',str(ROOT/S['source']),'-o',str(d/'unit.o')]
        proc=subprocess.run(argv,cwd=ROOT,capture_output=True,timeout=120)
        (d/'compile.log').write_text(portable((proc.stdout+proc.stderr).decode('utf8','replace'),llvm),encoding='utf8')
        need(proc.returncode==0,'Native compile failed; local log retained')
        dep=(d/'unit.d').read_text(encoding='utf8');(d/'unit.d').write_text(portable(dep,llvm),encoding='utf8')
        facts_object=object_audit(d/'unit.o')
        report['modes'][mode]=dict(audit=facts_object,command=portable(argv,llvm),artifacts={v.name:sha(v)for v in sorted(d.iterdir())if v.is_file()})
    need(sha(out/'c/unit.o')==sha(out/'cpp/unit.o'),'Complete C and C++ object identity for extern-C readonly data')
    need(inputs==portable({str(p):sha(p)for p in paths},llvm),'Every measured source/tool unchanged')
    (out/'measurement.json').write_bytes(encode(report))
    print(json.dumps(dict(passed=True,languages=['c','cpp'],data_bytes=200,OBJECT=2,FUNC=0,UND=0,RELA=0,object_sha256=sha(out/'c/unit.o'),independent_readers_agree=True,source_unit_curated_or_integrated=False,firmware_ready=False)))

if __name__=='__main__':
    try:main()
    except (ValueError,OSError,subprocess.SubprocessError)as error:
        message=str(error).replace(str(ROOT),'PROJECT_ROOT').replace(str(Path.home()),'USERPROFILE')
        print(json.dumps(dict(passed=False,reason=message)),file=sys.stderr);sys.exit(1)
