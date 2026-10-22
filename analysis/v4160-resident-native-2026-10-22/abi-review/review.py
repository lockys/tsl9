#!/usr/bin/env python3
"""Static actual RV32 object/IR review. No link, execution or ISA-state model."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
OLD_REVIEW='35eebcc1d05a3883ec7639dcac037a063bc6146abf4da640ca796c10c6d36a90'
MODEL='experiments/tsl9-resident-memory-native'
NAMES={'compare':'tsl9_native_compare_200004bc','fill':'tsl9_native_fill_2000039c','copy':'tsl9_native_copy_20000332'}
# Complete measured final-profile operand inventory, not an instruction-state
# evaluator. It binds each branch/loop/data role; raw identity is not required.
# PC, operation, rd, rs1, rs2, immediate, direct target, memory width.
PATTERNS={
 'compare':[(0,'lui',16,None,None,0x40024000,None,None),(4,'lw',15,16,None,524,None,32),(8,'sw',None,16,0,524,None,32),(12,'fence.i',None,None,None,None,None,None),(16,'addi',13,0,None,0,None,None),(18,'beq',None,10,0,None,44,None),(20,'beq',None,12,0,None,44,None),(22,'mv',13,12,None,None,None,None),(24,'lbu',14,10,None,0,None,8),(28,'bne',None,14,11,None,42,None),(32,'addi',13,13,None,-1,None,None),(34,'addi',10,10,None,1,None,None),(36,'bne',None,13,0,None,24,None),(38,'addi',13,0,None,1,None,None),(40,'jal',0,None,None,None,44,None),(42,'addi',13,0,None,0,None,None),(44,'sw',None,16,15,524,None,32),(48,'mv',10,13,None,None,None,None),(50,'jalr',0,1,None,0,None,None)],
 'fill':[(0,'lui',17,None,None,0x40024000,None,None),(4,'lw',14,17,None,524,None,32),(8,'sw',None,17,0,524,None,32),(12,'fence.i',None,None,None,None,None,None),(16,'beq',None,10,0,None,42,None),(18,'beq',None,12,0,None,42,None),(20,'add',16,12,10,None,None,None),(24,'mv',15,12,None,None,None,None),(26,'addi',13,10,None,1,None,None),(30,'addi',15,15,None,-1,None,None),(32,'sb',None,10,11,0,None,8),(36,'mv',10,13,None,None,None,None),(38,'bne',None,15,0,None,26,None),(40,'mv',10,16,None,None,None,None),(42,'sw',None,17,14,524,None,32),(46,'jalr',0,1,None,0,None,None)],
 'copy':[(0,'lui',16,None,None,0x40024000,None,None),(4,'lw',17,16,None,524,None,32),(8,'sw',None,16,0,524,None,32),(12,'fence.i',None,None,None,None,None,None),(16,'beq',None,10,0,None,46,None),(18,'beq',None,11,0,None,46,None),(20,'beq',None,12,0,None,46,None),(22,'add',5,12,10,None,None,None),(26,'mv',13,11,None,None,None,None),(28,'mv',14,10,None,None,None,None),(30,'lbu',15,13,None,0,None,8),(34,'sb',None,14,15,0,None,8),(38,'addi',14,14,None,1,None,None),(40,'addi',13,13,None,1,None,None),(42,'bne',None,14,5,None,30,None),(46,'sw',None,16,17,524,None,32),(50,'jalr',0,1,None,0,None,None)]}
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def write(p,v):p.write_bytes((json.dumps(v,indent=2)+'\n').encode('utf8'))
def case(root,slug):return next(p for p in (root/'apk-analysis'/('tsl9-'+slug),root/'analysis'/slug) if p.is_dir())
def module(p):
    s=importlib.util.spec_from_file_location('resident_native_'+p.stem,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def context(root):
    p=case(root,'v4160-resident-memory-2026-10-22')/'model-review/review.py';need(sha(p)==OLD_REVIEW,'Closed bounded decoders/reference source reader');old=module(p);_,native=old.contexts(root);fields,llvm,ctx=native.context(root);previous=ctx['extension']
    def extended(raw,pc,base):
        word=int.from_bytes(raw[:4],'little')
        if raw[:4]==bytes.fromhex('0f100000'):return dict(PC=pc,bytes=4,raw_hex=raw[:4].hex(),op='fence.i',rd=None,rs1=None,rs2=None,immediate=None,target=None,memory_width=None)
        if len(raw)>=4 and word&0x707f==0x67:
            imm=word>>20
            return dict(PC=pc,bytes=4,raw_hex=raw[:4].hex(),op='jalr',rd=(word>>7)&31,rs1=(word>>15)&31,rs2=None,immediate=imm-4096 if imm&2048 else imm,target=None,memory_width=None)
        return previous(raw,pc,base)
    ctx['extension']=extended
    return old,fields,llvm,ctx
def parse_sections(text,llvm):
    pieces=re.split(r'Disassembly of section ([^\n:]+):',text);out={}
    for i in range(1,len(pieces),2):
        rows=[]
        for line in pieces[i+1].splitlines():
            if re.match(r'^\s*[0-9a-f]+:\s+0f 10 00 00\s+fence\.i\s*$',line):
                pc=int(line.split(':')[0],16);rows.append(dict(PC=pc,bytes=4,raw_hex='0f100000',op='fence.i',rd=None,rs1=None,rs2=None,immediate=None,target=None,memory_width=None))
            else:rows.extend(llvm['parse'](re.sub(r' <[^>]*>','',line)))
        out[pieces[i]]=rows
    return out
def source(root):
    old,_,_,_=context(root);original=old.sources(root);contract=read(HERE/'source-contracts.json')
    need(contract['source_review_seal']==sha(case(root,'v4160-resident-memory-2026-10-22')/'model-review/seal.json'),'Original source-only seal')
    pins=read(HERE/'reference-pins.json')
    for relative,pin in pins['sources'].items():need(sha(root/relative)==pin,'Frozen native/source inputs '+relative)
    return dict(passed=True,original=original,metadata_only=True,actual_native_artifacts_read=False,physical_ABI_proved=False,target_execution=False)
def leaf_kernel(leaf,rows):
    keys=('PC','op','rd','rs1','rs2','immediate','target','memory_width')
    need([tuple(x[k] for k in keys) for x in rows]==PATTERNS[leaf],'Complete measured direct-leaf semantic operand/CFG inventory '+leaf)
    writes={x['rd'] for x in rows if x['rd'] not in(None,0)}
    need(not writes.intersection((1,2,3,4,8,9,11,12,18,19,20,21,22,23,24,25,26,27)),'No public SP/RA/GP/S/A1/A2 writes')
    return dict(guard_before_argument_tests=True,real_fence_i=True,saved_MMIO_restored_on_all_normal_exits=True,normal_result_projection=True,normal_A1_A2_unchanged=True,no_SP_RA_GP_S_writes=True,forward_ordered_bytes=True,full_original_register_ABI=False,asynchronous_prefix_equivalence=False)
def ir_kernel(ir,name):
    match=re.search(r'^define[^\n]*@'+name+r'\([^\n]*\)[^\n]*\{\n(.*?)^}',ir,re.M|re.S);need(match is not None,'Bounded actual wrapper IR body')
    body=match[1];saved=re.search(r'(%\d+) = load volatile i32, ptr inttoptr \(i32 1073889804 to ptr\)',body);need(saved is not None,'Real volatile guard read')
    zero='store volatile i32 0, ptr inttoptr (i32 1073889804 to ptr)';restore='store volatile i32 '+saved[1]+', ptr inttoptr (i32 1073889804 to ptr)'
    need(body.count('load volatile i32')==1 and body.count('store volatile i32')==2 and zero in body and restore in body,'Single guard read/zero/saved restore, no context writes')
    need(body.index(saved[0])<body.index(zero)<body.index('asm sideeffect "fence.i"')<body.index(restore),'Actual IR guard/fence/restore ordering')
    bridge='asm sideeffect "", "={x10},={x11},={x12},{x10},{x11},{x12},~{memory}"'
    need(body.count(bridge)==1 and re.search(re.escape(bridge)+r'\(i32 %\d+, i32 %1, i32 %2\)',body) is not None,'Opaque full-width returnA0 plus unchanged original input1/input2')
    need('alloca' not in body and not re.search(r'call[^\n]*@[A-Za-z_]',body),'No local context allocation or runtime callee hidden in actual wrapper IR')
    return dict(direct_volatile_guard=True,real_fence_memory_clobber=True,fullwidth_A1_A2_return_bindings=True,local_context_erased=True)
def raw_controls(blobs,fields,ctx):
    controls=[]
    for leaf,at,bit,label in [('compare',28,20,'full_expected_A1_register'),('fill',42,20,'restore_saved_word_not_other_register'),('copy',30,12,'byte_load_not_halfword')]:
        blob=bytearray(blobs[leaf]);blob[at+bit//8]^=1<<(bit%8);rows=fields['rows'](bytes(blob),0,ctx)
        try:leaf_kernel(leaf,rows)
        except ValueError:controls.append(dict(case=label,leaf=leaf,offset=at,bit=bit,mutated_body_sha256=hashlib.sha256(blob).hexdigest(),rejected=True));continue
        raise ValueError('Accepted actual raw operand control '+label)
    return controls
def inspect(root,folder):
    root=Path(root).resolve();folder=Path(folder).resolve();source(root);_,fields,llvm,ctx=context(root)
    pins=read(HERE/'reference-pins.json');producer=case(root,'v4160-resident-native-2026-10-22')/'implementation/probe.py';need(sha(producer)==pins['producer'],'Frozen actual compiler/provenance reader')
    provenance=module(producer).replay(root,folder/'verification.json');record=read(folder/'verification.json')
    e=ctx['ELF'](folder/'native.o');need(e.kind==1 and e.flags==1,'Actual RV32/RVC ET_REL')
    funcs=[f for f in e.symbols if f['info']&15==2 and f['size']];alloc=[s for s in e.sections if s['flags']&2 and s['size']]
    need(all(s['type']==1 and s['flags']==6 for s in alloc),'Only actual executable code allocations')
    expected=set(NAMES.values())|{v.replace('tsl9_native_','tsl9_candidate_') for v in NAMES.values()}|{'ml_port_read8','ml_port_read32','ml_port_write8','ml_port_write32','ml_port_fence_i'}
    need(len(funcs)==11 and {f['name'] for f in funcs}==expected and all(f['info']==18 and f['other']==0 for f in funcs),'All eleven true global FUNC definitions, no hidden helper')
    need({s['index'] for s in alloc}=={f['index'] for f in funcs} and len(alloc)==len(funcs),'Every real allocation is owned by exactly one reported function')
    need(not any(s['index']==0xfff1 and s['info']>>4 for s in e.symbols),'No absolute provider aliases')
    undefined=sorted({s['name'] for s in e.symbols if s['name'] and s['index']==0})
    parsed=parse_sections((folder/'complete-static-disassembly.log').read_text(),llvm);reports=[];rows_by_name={};blobs={}
    for f in funcs:
        s=e.sections[f['index']];need(f['value']==0 and f['size']==s['size'],'Complete real allocated function, no borrowed interior/tail')
        rows=fields['rows'](e.function_bytes(f),0,ctx);need([{k:v for k,v in x.items() if k!='offset'} for x in rows]==parsed[s['name']],'Every actual raw operand equals complete LLVM text')
        starts={x['PC'] for x in rows};need(all(x['target'] is None or x['target'] in starts for x in rows),'All encoded direct targets are real local boundaries')
        writes=sorted({x['rd'] for x in rows if x['rd'] not in (None,0)})
        stack_changes=[[x['PC'],x['immediate']] for x in rows if x['op']=='addi' and x['rd']==x['rs1']==2]
        memory=[{k:x[k] for k in ('PC','op','rd','rs1','rs2','immediate','memory_width')} for x in rows if x['memory_width'] is not None]
        relas=[x for x in e.relocations if x['owner']==s['name']]
        calls=[{k:x[k] for k in ('PC','op','rd','rs1','immediate','target')} for x in rows if x['op'] in ('jal','jalr') and not(x['op']=='jalr' and x['rd']==0 and x['rs1']==1 and x['immediate']==0)]
        reports.append(dict(name=f['name'],bytes=f['size'],instructions=len(rows),info=f['info'],section=s['name'],code_sha256=hashlib.sha256(e.function_bytes(f)).hexdigest(),written_GPRs=writes,stack_changes=stack_changes,memory=memory,fence_i_sites=[x['PC'] for x in rows if x['op']=='fence.i'],control_transfers=calls,relocations=relas))
        rows_by_name[f['name']]=rows
        if f['name'] in NAMES.values():blobs[next(k for k,v in NAMES.items() if v==f['name'])]=e.function_bytes(f)
    need(set(NAMES.values())<={f['name'] for f in funcs},'All three genuine public numeric wrappers')
    ir=(folder/'native.ll').read_text();entries={}
    for leaf,name in NAMES.items():
        match=re.search(r'^define[^\n]*\bi32 @'+name+r'\(([^\n]*)\)[^\n]*\{',ir,re.M);need(match is not None,'Real i32-return wrapper '+leaf)
        need(len(re.findall(r'\bi32\b',match[1]))==3 and 'sret' not in match[1] and 'ptr' not in match[1],'Exactly three full-width input arguments, no context/sret '+leaf)
        rows=rows_by_name[name];contract=read(HERE/'source-contracts.json')['leaves'][leaf]
        written=sorted({x['rd'] for x in rows if x['rd'] not in (None,0)})
        size=next(x['bytes'] for x in reports if x['name']==name)
        entries[leaf]=dict(name=name,original_bytes=contract['bytes'],new_bytes=size,byte_length_fits_only=size<=contract['bytes'],original_full_extent_ownership_proved=False,written_GPRs=written,additional_own_written_GPRs=sorted(set(written)-set(contract['own_written_GPRs_excluding_zero'])),A1_own_written=11 in written,A2_own_written=12 in written,SP_own_written=2 in written,RA_own_written=1 in written,kernel=leaf_kernel(leaf,rows),IR=ir_kernel(ir,name))
    need(not undefined and not e.relocations,'Final actual object has no unresolved providers or runtime call relocations')
    return dict(passed=True,actual_native_artifacts_read=True,mode=record['mode'],producer_receipt_sha256=sha(folder/'verification.json'),producer_provenance_replayed=provenance['passed'],object_sha256=sha(folder/'native.o'),IR_sha256=sha(folder/'native.ll'),functions=reports,total_function_bytes=sum(x['bytes'] for x in reports),total_instructions=sum(x['instructions'] for x in reports),RELA=len(e.relocations),undefined_symbols=undefined,entries=entries,actual_raw_controls=raw_controls(blobs,fields,ctx),linked=False,BIN_exported=False,target_execution=False,ISA_emulation=False,physical_ABI_proved=False,installed_provider_proved=False)
def replay(root,p):
    r=read(p);need(r['checker_sha256']==sha(HERE/'review.py'),'Frozen actual checker identity');checked=inspect(root,Path(r['folder']));need(checked==r['result'],'Actual native readback equals receipt');return checked
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);p.add_argument('--folder',type=Path);p.add_argument('--receipt',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
    if a.replay:need(a.folder is None and a.receipt is None,'Readonly replay');result=replay(root,a.replay.resolve())
    elif a.folder:
        need(a.receipt is not None and not a.receipt.exists(),'Create-only review receipt');result=inspect(root,a.folder);a.receipt.parent.mkdir(parents=True,exist_ok=True);write(a.receipt,dict(schema='TSL9-resident-direct-native-independent-review-v1',checker_sha256=sha(HERE/'review.py'),folder=str(a.folder.resolve()),result=result))
    else:need(a.receipt is None,'Metadata-only mode');result=source(root)
    print(json.dumps(result))
