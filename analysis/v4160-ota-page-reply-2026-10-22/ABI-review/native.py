#!/usr/bin/env python3
"""Independent static reply ABI comparison. No CPU or resident-provider execution."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode=True
ENTRY=0x9b8e
NAME='tsl9_ota_page_reply_9b8e'
WINDOWS=((2,0x16),(0x58,0x60))
PINS={'source-proof.py':'47747b92bcc3618c8e53bdadd1c640164ef34def3ffd32f0fcffc2f63defa895','source-proof.json':'bc8a3d7645b03140240e4aaa331004d8c84bb5a8c5f2597687751010c38d6d22','elf32.py':'00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'}
def need(v,m):
    if not v:raise ValueError(m)
def sha(b):return hashlib.sha256(b).hexdigest()
def load(path,name,pin):
    need(sha(path.read_bytes())==pin,'Pinned independent dependency '+path.name)
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def context(root):
    cases=[root/'apk-analysis/tsl9-v4160-ota-page-reply-2026-10-22',root/'analysis/v4160-ota-page-reply-2026-10-22'];case=next(p for p in cases if p.is_dir());source=case/'source-review'
    decoder=load(source/'source-proof.py','reply_ABI_source',PINS['source-proof.py'])
    proof=source/'source-proof.json';need(sha(proof.read_bytes())==PINS['source-proof.json'],'Pinned independent source ledger');ledger=json.loads(proof.read_bytes());original=bytes.fromhex(''.join(r['raw_hex'] for r in ledger['decoded_rows']));decoder.validate(original)
    parser=next(p for p in [root/'apk-analysis/tsl9-v4160-irq-native-2026-10-21/compiler-review/elf32.py',root/'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py'] if p.is_file());elf=load(parser,'reply_ABI_ELF',PINS['elf32.py']);return decoder,elf,original
def normalized(body,original):
    need(len(body)==124,'Exact124B actual native extent');return body[:0x52]+original[0x52:0x56]+body[0x56:]
def body_contract(decoder,body,original,scheduled=False):
    rows=decoder.rows(body);normal=normalized(body,original);reference=decoder.validate(original)
    if scheduled:need(normal==original,'Scheduled native body equals all50 source instructions except relocated TXJAL')
    else:
        for begin,end in WINDOWS:
            got=[r['raw_hex'] for r in rows if begin<=r['PC']-ENTRY<end];want=[r['raw_hex'] for r in reference if begin<=r['PC']-ENTRY<end]
            need(Counter(got)==Counter(want),'Compiler-owned occurrence-aware ABI window inventory')
        excluded=set(range(0x52,0x56))|{i for a,b in WINDOWS for i in range(a,b)}
        need(all(normal[i]==original[i] for i in range(124) if i not in excluded),'No non-ABI-window native differences')
    bypc={r['PC']:r for r in rows}
    need([(bypc[ENTRY+o]['op'],bypc[ENTRY+o]['rd'],bypc[ENTRY+o]['rs1']) for o in (0x20,0x46,0x6a,0x7a)]==[('jalr',1,15),('jalr',1,15),('jalr',0,6),('jalr',0,1)],'Allocator/copy linkRA, free no-linkT1, null no-linkRA')
    need(bypc[ENTRY+0x22]['target']==ENTRY+0x6c,'Unchanged null branch frontier')
    need(bypc[ENTRY+0x52]['op']=='jal' and bypc[ENTRY+0x52]['rd']==1,'Actual TX JAL writesRA')
    return {'bytes':124,'instructions':50,'source_body_sha256':sha(original),'observed_body_sha256':sha(body),'scheduled_all_source_words':scheduled,'compiler_only_pointwise_identity':normal==original,'unaltered_control_offsets':[0x20,0x22,0x46,0x52,0x6a,0x6c,0x7a],'normal_tail_no_new_RA':True,'null_other_caller_saved_provider_defined':True,'unknown_resident_ABI':True,'hardware_validated':False,'rows':rows}
def object_contract(decoder,elf_module,path,original,scheduled=False):
    e=elf_module.ELF(path);need(e.kind==1,'Actual ET_REL component');symbols=[s for s in e.symbols if s['name']==NAME];need(len(symbols)==1,'Unique native reply symbol');s=symbols[0];need((s['size'],s['info'],s['other'])==(124,18,0),'Actual GLOBAL FUNC124 defaultvisibility');owner=e.sections[s['index']];need(owner['flags']==6 and owner['size']==124 and s['value']==0,'Unique AX owner124 at0')
    need(sum(1 for x in e.sections if x['name']==owner['name'])==1,'Unique selected owner name');need(not any(x['size'] and any(t in x['name'] for t in ('eh_frame','debug_frame','sframe')) for x in e.sections),'No implicit unwind representation')
    need([x['name'] for x in e.symbols if x['index']==0 and x['name']]==['__tsl9v4160_call_8a56'],'Sole explicit TX provider undefined')
    rel=[r for r in e.relocations if r['owner']==owner['name']];need(len(e.relocations)==len(rel)==1,'Sole owned TX relocation');r=rel[0];need((r['offset'],r['type'],r['addend'],r['symbol']['name'])==(0x52,17,0,'__tsl9v4160_call_8a56'),'TX JAL4B relocation role')
    for x in e.symbols:
        if x['index']==owner['index']:need(not any(a<=x['value']<b for a,b in WINDOWS),'No interior ABI-window symbol anchor')
    result=body_contract(decoder,e.function_bytes(s),original,scheduled);result.update(object_sha256=sha(e.raw),owner=owner['name'],sole_TX_relocation=rel);return result
def ir_contract(text):
    tx=re.findall(r'(%\d+) = tail call \{ i32, i32, i32, i32 \} asm sideeffect "jal ra, __tsl9v4160_call_8a56"[^\n]+',text);need(len(tx)==1,'One explicit four-output rawTX primitive');tx=tx[0]
    outputs=[]
    for field in (1,2):
        m=re.findall(r'(%\d+) = extractvalue \{ i32, i32, i32, i32 \} '+re.escape(tx)+r', '+str(field)+r'\b',text);need(len(m)==1,'Unique postTX A'+str(field)+' extraction');outputs+=m
    tail=re.findall(r'(%\d+) = musttail call (?:noundef )?i32 (%\d+)\(i32 noundef (%\d+), i32 noundef (%\d+), i32 noundef (%\d+)\)',text);need(len(tail)==1,'One real three-register musttail adapter');ret,target,a0,a1,a2=tail[0];need([a1,a2]==outputs,'Forward live postTX A1/A2, not entry command/index');need('ret i32 '+ret in text,'Direct return of musttail result')
    opaque=[line for line in text.splitlines() if 'asm sideeffect "jalr ra, $3, 0"' in line];need(len(opaque)==2,'Two opaque allocator/copy calls')
    for line in opaque:
        for reg in [1,13,14,16,17,5,6,7,28,29,30,31]:need('~{x'+str(reg)+'}' in line,'Honest opaque caller-saved clobber x'+str(reg))
        for reg in [10,11,12,15]:need('={x'+str(reg)+'}' in line,'Read/write opaque result x'+str(reg))
    txline=next(line for line in text.splitlines() if 'asm sideeffect "jal ra, __tsl9v4160_call_8a56"' in line)
    for reg in [1,14,15,16,17,5,6,7,28,29,30,31]:need('~{x'+str(reg)+'}' in txline,'Honest TX caller-saved clobber x'+str(reg))
    for reg in [10,11,12,13]:need('={x'+str(reg)+'}' in txline,'Read/write TX output x'+str(reg))
    need(text.count('load volatile i32')==3 and text.count('store volatile i8')==2,'Three fresh volatile pointer slots/two header bytes')
    return {'IR_sha256':sha(text.encode()),'opaque_calls':2,'TX_output_fields_forwarded_to_tail':[1,2],'release_signature_proved':False,'full_resident_SP_S_register_ABI_proved':False}
def pair_contract(elf_module,before,after):
    pre=elf_module.ELF(before);post=elf_module.ELF(after);need(len(pre.raw)==len(post.raw),'Scheduling preserves actual object length');s=next(s for s in pre.symbols if s['name']==NAME);owner=pre.sections[s['index']];start=owner['offset']+s['value'];allowed={start+i for a,b in WINDOWS for i in range(a,b)};changes=[i for i,(a,b) in enumerate(zip(pre.raw,post.raw)) if a!=b];need(changes and set(changes)<=allowed,'Only28 source-owned ABI-window bytes may change; all metadata/RELA/other storage identical')
    need(pre.sections==post.sections and pre.symbols==post.symbols and pre.relocations==post.relocations,'Exact decoded owner/symbol/RELA preservation')
    return {'compiler_object_sha256':sha(pre.raw),'scheduled_object_sha256':sha(post.raw),'actual_changed_bytes':len(changes),'changed_function_offsets':[i-start for i in changes],'source_order_restoration_layer':True,'universal_pre_post_semantic_commutation_claimed':False}
def controls(decoder,body,original,text):
    checks=[]
    for name,offset,mask in [('allocator_no_link',0x20,0x1000),('copy_target_S1',0x46,0x300),('free_links_RA',0x6a,0x1000),('null_target_T1',0x7a,0x380),('header_source_A1',0x2c,0x4000),('frame_size',0,0x20),('copy_full_index_shift',0x42,4)]:
        mutant=bytearray(body);n=4 if mutant[offset]&3==3 else 2;w=int.from_bytes(mutant[offset:offset+n],'little')^mask;mutant[offset:offset+n]=w.to_bytes(n,'little')
        try:body_contract(decoder,bytes(mutant),original)
        except (ValueError,KeyError):checks.append({'name':name,'rejected':True});continue
        raise ValueError('Raw mutant accepted: '+name)
    txlines=text.splitlines();txlines=[line.replace('~{x14},','') if 'asm sideeffect "jal ra, __tsl9v4160_call_8a56"' in line else line for line in txlines]
    for name,mutant in [('musttail_removed',text.replace('musttail call','tail call')),('TX_A1_substituted',re.sub(r'(musttail call (?:noundef )?i32 %\d+\(i32 noundef %\d+, i32 noundef )%\d+',r'\g<1>%1',text)),('opaque_T1_clobber_omitted',text.replace('~{x6},','')),('TX_A4_clobber_omitted','\n'.join(txlines))]:
        try:ir_contract(mutant)
        except ValueError:checks.append({'name':name,'rejected':True});continue
        raise ValueError('IR mutant accepted: '+name)
    return checks
def review(root,folder,scheduled=None):
    decoder,elf,original=context(root);obj=folder/'page_reply.o';ir=folder/'page_reply.ll';native=object_contract(decoder,elf,obj,original);text=ir.read_text(encoding='utf-8');proof={'schema':'TSL9-page-reply-independent-native-ABI-v1','passed':True,'compiler_component':native,'IR':ir_contract(text)};proof['negative_controls']=controls(decoder,elf.ELF(obj).function_bytes(next(s for s in elf.ELF(obj).symbols if s['name']==NAME)),original,text)
    if scheduled:proof['explicit_scheduled_component']=object_contract(decoder,elf,scheduled,original,True);proof['explicit_scheduling_pair']=pair_contract(elf,obj,scheduled)
    return proof
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);p.add_argument('--folder',type=Path,required=True);p.add_argument('--scheduled',type=Path);p.add_argument('--report',type=Path);a=p.parse_args();result=review(a.project_root.resolve(),a.folder.resolve(),a.scheduled.resolve() if a.scheduled else None);data=(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode();
    if a.report:need(not a.report.exists(),'Create-only independent report');a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_bytes(data)
    print(json.dumps({'passed':True,'instructions':50,'raw_IR_controls':len(result['negative_controls']),'scheduled':bool(a.scheduled)}))
if __name__=='__main__':main()
