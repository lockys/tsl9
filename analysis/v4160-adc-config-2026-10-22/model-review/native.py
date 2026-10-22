#!/usr/bin/env python3
"""Independent actual native object/SSA review; no native or ISA execution."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ENTRY='tsl9_adc_config_1892e'
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def write(p,v):Path(p).write_bytes((json.dumps(v,indent=2)+'\n').encode('utf8'))
def module(p):
    s=importlib.util.spec_from_file_location('adc_native_'+p.parent.name+'_'+p.stem,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def source():return module(HERE/'source.py')
def context(root):
    p=source().case(root,'v4160-resident-native-2026-10-22')/'abi-review/review.py';need(sha(p)=='ea95caacce05635160b6e749b6b1684fa1d64bda9f368bc988f19892fdff4bbd','Pinned raw/LLVM native reader');m=module(p);return m,m.context(root)
def stable(root):
    result=source().inspect(root);pins=read(HERE/'reference-pins.json')
    for path,pin in pins['sources'].items():need(sha(source().locate(root,path))==pin,'Frozen independent native input '+path)
    return result
def ir_gate(ir):
    m=re.search(r'^define[^\n]*\bi32 @'+ENTRY+r'\(([^\n]*)\)[^\n]*\{\n(.*?)^}',ir,re.M|re.S)
    need(m is not None and len(re.findall(r'\bi32\b',m[1]))==2 and 'ptr' not in m[1] and 'sret' not in m[1],'Actual public two-u32/u32 signature without hidden context')
    body=m[2];values={'%0':('param',0),'%1':('param',1)};effects=[]
    def value(token):return values[token] if token.startswith('%') else int(token)&0xffffffff
    def op(name,a,b):
        if name=='or':
            terms=[]
            for x in(a,b):terms.extend(x[1:] if isinstance(x,tuple) and x[0]=='or' else [x])
            return tuple(['or',*sorted(terms,key=repr)])
        return (name,a,b)
    for line in body.splitlines():
        x=re.match(r'\s*(%\d+) = add i32 (%\d+), (\d+)$',line)
        if x and values.get(x[2]) in(('param',0),('param',1)):values[x[1]]=('address',values[x[2]][1],int(x[3]));continue
        x=re.match(r'\s*(%\d+) = inttoptr i32 (%\d+) to ptr$',line)
        if x:
            v=value(x[2]);values[x[1]]=('address',v[1],0) if v[0]=='param' else v;continue
        x=re.match(r'\s*(%\d+) = load volatile i(8|32), ptr (%\d+),',line)
        if x:
            address=value(x[3]);effects.append(('read',int(x[2]),address));values[x[1]]=('read',len(effects)-1,int(x[2]));continue
        x=re.match(r'\s*store volatile i(8|32) (%\d+), ptr (%\d+),',line)
        if x:effects.append(('write',int(x[1]),value(x[3]),value(x[2])));continue
        x=re.match(r'\s*(%\d+) = zext i8 (%\d+) to i32$',line)
        if x:values[x[1]]=value(x[2]);continue
        x=re.match(r'\s*(%\d+) = (and|or|shl|add)(?: nuw)?(?: nsw)? i32 (%\d+|-?\d+), (%\d+|-?\d+)$',line)
        if x:values[x[1]]=op(x[2],value(x[3]),value(x[4]));continue
        need(not re.search(r'\b(load|store)\b',line),'No hidden nonvolatile memory access in selected IR')
    sequence=[('read',32,('address',0,4)),('read',32,('address',1,24)),('read',32,('address',1,0)),('read',32,('address',1,28)),('read',32,('address',1,4)),('write',32,('address',0,4)),('read',32,('address',0,8)),('read',32,('address',1,12)),('read',32,('address',1,16)),('read',32,('address',1,8)),('write',32,('address',0,8)),('read',32,('address',0,44)),('read',8,('address',1,20)),('write',32,('address',0,44))]
    need([x[:3] for x in effects]==sequence,'Actual IR fourteen volatile widths/address bases/offsets/order; fresh alias-visible reads')
    R=lambda i:('read',i,8 if i==12 else 32)
    or_=lambda *terms:tuple(['or',*sorted(terms,key=repr)])
    expected=[or_(('and',R(0),0xe0f0feff),R(1),R(2),R(3),('shl',R(4),8)),or_(('and',R(6),0xfff1f7fd),R(7),R(8),('shl',R(9),1)),or_(('and',R(11),0xff0fffff),('and',('add',('shl',R(12),20),0x0ff00000),0x0ff00000))]
    need([x[3] for x in effects if x[0]=='write']==expected,'Actual SSA data dependencies equal fullword masks/OR/shifts and masked byte decrement')
    bridge='asm sideeffect "", "={x10},={x11},{x10},{x11},~{memory}"(i32 %0, i32 %1)'
    need(body.count(bridge)==1 and 'alloca' not in body and not re.search(r'call[^\n]*@[A-Za-z_]',body),'Only genuine A0/A1 exit bridge, no context allocation or runtime calls')
    return dict(public_two_u32_u32=True,volatile_effects=14,fullword_masks_and_shifts=True,byte_decrement_optimized_identity='((u8<<20)+0x0ff00000)&0x0ff00000 equals ((u8-1)&255)<<20',normal_effect_projection=True,alias_fresh_reads=True,hidden_context_sret=False)
def kernel(rows):
    keys=('PC','op','rd','rs1','rs2','immediate','target','memory_width');need([[x[k] for k in keys] for x in rows]==read(HERE/'native-kernel.json'),'Complete actual selected raw operand inventory')
def controls(blob,fields,ctx,ir):
    rows=fields['rows'](blob,0,ctx);kernel(rows);out=[]
    for pc,field,label in((4,'immediate','config24_read_offset'),(0x12,'immediate','first_mask_constant'),(0x62,'rs2','final_store_value_register')):
        original=next(x for x in rows if x['PC']==pc);found=None
        for bit in range(original['bytes']*8):
            b=bytearray(blob);b[pc+bit//8]^=1<<(bit%8)
            try:changed=fields['rows'](bytes(b),0,ctx)
            except ValueError:continue
            row=next((x for x in changed if x['PC']==pc),None);keys=('PC','bytes','op','rd','rs1','rs2','immediate','target','memory_width')
            if row is not None and row[field]!=original[field] and all(row[k]==original[k] for k in keys if k!=field):found=bytes(b),changed,bit,row;break
        need(found is not None,'Bounded single raw operand control');b,changed,bit,row=found
        try:kernel(changed)
        except ValueError:out.append(dict(case=label,PC=pc,bit=bit,original=original[field],mutated=row[field],mutated_body_sha256=hashlib.sha256(b).hexdigest(),rejected=True));continue
        raise ValueError('Accepted incorrect actual raw operand')
    start=ir.index('define dso_local i32 @'+ENTRY);head=ir[:start];body=ir[start:]
    for label,old,new in(('volatile_read_removed','load volatile i32','load i32'),('config_word_shift_8_changed','shl i32 %16, 8','shl i32 %16, 7')):
        need(old in body,'Meaningful actual selected IR control');changed=head+body.replace(old,new,1)
        try:ir_gate(changed)
        except (ValueError,KeyError):out.append(dict(case=label,mutated_IR_sha256=hashlib.sha256(changed.encode()).hexdigest(),rejected=True));continue
        raise ValueError('Accepted incorrect selected IR control')
    return out
def inspect(root,folder):
    root=Path(root).resolve();folder=Path(folder).resolve();stable(root);old,(_,fields,llvm,ctx)=context(root);p=source().case(root,'v4160-adc-config-2026-10-22')/'implementation/probe.py';need(sha(p)==read(HERE/'reference-pins.json')['producer'],'Frozen actual compiler/provenance reader');provenance=module(p).replay(root,folder/'verification.json')
    e=ctx['ELF'](folder/'native.o');need(e.kind==1 and e.flags==1,'Actual RV32/RVC ET_REL');funcs=[f for f in e.symbols if f['info']&15==2 and f['size']];alloc=[s for s in e.sections if s['flags']&2 and s['size']]
    names={ENTRY,'tsl9_adc_config_io','ml_port_read8','ml_port_read32','ml_port_write32'};need(len(funcs)==5 and {f['name'] for f in funcs}==names and all(f['info']==18 and f['other']==0 for f in funcs),'Five genuine global FUNCs')
    need(len(alloc)==5 and all(s['type']==1 and s['flags']==6 for s in alloc) and {s['index'] for s in alloc}=={f['index'] for f in funcs},'One genuine FUNC per complete code allocation')
    need(not e.relocations and not any(s['name'] and s['index']==0 for s in e.symbols) and not any(s['index']==0xfff1 and s['info']>>4 for s in e.symbols),'UND0/RELA0/ABS0; no fake provider')
    parsed=old.parse_sections((folder/'complete-static-disassembly.log').read_text(),llvm);reports=[];selected_rows=None;selected_blob=None
    for f in funcs:
        s=e.sections[f['index']];need(f['value']==0 and f['size']==s['size'],'Whole actual owned function without borrowed code');blob=e.function_bytes(f);rows=fields['rows'](blob,0,ctx)
        need([{k:v for k,v in x.items() if k!='offset'} for x in rows]==parsed[s['name']],'Every raw instruction operand equals independent complete LLVM parser')
        need(all(x['target'] is None for x in rows) and all(x['op'] not in('jal','jalr') or x['op']=='jalr' and x['rd']==0 and x['rs1']==1 and x['immediate']==0 for x in rows),'Straightline functions and genuine RETs only')
        writes=sorted({x['rd'] for x in rows if x['rd'] not in(None,0)});reports.append(dict(name=f['name'],bytes=f['size'],instructions=len(rows),code_sha256=hashlib.sha256(blob).hexdigest(),written_GPRs=writes,frame_or_RA_or_S_GP_TP_writes=sorted(set(writes)&{1,2,3,4,8,9,*range(18,28)}),stack_accesses=[x for x in rows if x['memory_width'] is not None and x['rs1']==2],memory=[x for x in rows if x['memory_width'] is not None]))
        if f['name']==ENTRY:selected_rows=rows;selected_blob=blob
    kernel(selected_rows);selected=next(x for x in reports if x['name']==ENTRY);need(not selected['frame_or_RA_or_S_GP_TP_writes'] and not selected['stack_accesses'],'Measured selected no frame/RA/S/GP/TP writes')
    need(not set(selected['written_GPRs'])&{10,11},'Actual selected A0/A1 preserved by every own instruction');ir=(folder/'native.ll').read_text();ir_result=ir_gate(ir)
    selected=dict(**selected,additional_own_written_GPRs=sorted(set(selected['written_GPRs'])-{13,14,15}),original_bytes=88,byte_length_fits_only=selected['bytes']<=88,IR=ir_result,normal_A0_A1_preserved=True,normal_scratch_liveout_matches_original=False,full_original_register_ABI=False)
    return dict(passed=True,mode=read(folder/'verification.json')['mode'],actual_native_artifacts_read=True,producer_provenance_replayed=provenance['passed'],producer_receipt_sha256=sha(folder/'verification.json'),object_sha256=sha(folder/'native.o'),IR_sha256=sha(folder/'native.ll'),functions=reports,selected=selected,total_function_bytes=sum(x['bytes'] for x in reports),total_instructions=sum(x['instructions'] for x in reports),unused_genuine_global_functions=4,RELA=0,undefined_symbols=[],actual_controls=controls(selected_blob,fields,ctx,ir),physical_ABI_proved=False,installed_identity_proved=False,target_execution=False,ISA_emulation=False,linked=False,BIN_exported=False)
def replay(root,p):
    r=read(p);need(r['checker_sha256']==sha(HERE/'native.py'),'Actual independent native reader identity');result=inspect(root,Path(r['folder']));need(result==r['result'],'Actual native readback equals retained receipt');return result
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--folder',type=Path);p.add_argument('--receipt',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
    if a.replay:need(a.folder is None and a.receipt is None,'Read-only native replay');result=replay(root,a.replay)
    else:
        need(a.folder is not None and a.receipt is not None and not a.receipt.exists(),'Create-only actual review receipt');result=inspect(root,a.folder);write(a.receipt,dict(schema='TSL9-ADC1892E-independent-native-v1',checker_sha256=sha(HERE/'native.py'),folder=str(a.folder.resolve()),result=result))
    print(json.dumps(result))
