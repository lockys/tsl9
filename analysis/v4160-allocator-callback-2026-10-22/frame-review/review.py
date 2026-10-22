"""Static frame/reply-object projection; no instruction-state evaluation or target execution."""
import argparse,hashlib,json,re,runpy,uuid
from pathlib import Path
import source_delta

HERE=Path(__file__).resolve().parent
FW='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
NAME='tsl9_ota_handler_native_9c4a'
COMMON={1:44,8:40,9:36,18:32,19:28,20:24,21:20}
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def closed():
    if (HERE/'seal.json').exists():
        for n,pin in read(HERE/'seal.json')['members'].items():need(sha(HERE/n)==pin,'Closed frame review member '+n)
def case(root,n):return next(p for p in (root/'apk-analysis'/('tsl9-'+n),root/'analysis'/n) if p.is_dir())
def context(root):
    p=case(root,'v4160-ota-handler-compact-2026-10-22')/'ABI-review/native.py'
    need(sha(p)=='1b378718c84e31bf7a6f03a3f3f22f9db755d6b804dd410b29f0224559b1dca9','Immutable field reader')
    n=runpy.run_path(str(p));fields,llvm,ctx=n['context'](root)
    capture=runpy.run_path(str(case(root,'v4160-ota-handler-2026-10-22')/'source-review/capture-source.py'))
    decode,E=capture['context'](root)
    return fields,llvm,ctx,decode,E
def projection(rows):
    first=rows[0];need(first['op']=='addi' and first['rd']==first['rs1']==2 and first['immediate']<0,'Actual frame subtraction')
    frame=-first['immediate'];need(frame%16==0,'Actual frame alignment')
    saves=[]
    for r in rows[1:]:
        if r['op']!='sw' or r['rs1']!=2:break
        saves.append(dict(PC=r['PC'],register=r['rs2'],slot=r['immediate']))
    save_map={r['register']:r['slot'] for r in saves};need(len(save_map)==len(saves),'Distinct saved registers')
    need(len({r['slot'] for r in saves})==len(saves) and all(0<=r['slot']<=frame-4 and r['slot']%4==0 for r in saves),'Distinct bounded save words')
    restores=[dict(PC=r['PC'],register=r['rd'],slot=r['immediate']) for r in rows if r['op']=='lw' and r['rs1']==2 and r['rd'] in save_map]
    need(all(r['slot']==save_map[r['register']] for r in restores),'Every actual callee-save reload uses its own saved slot')
    need(sorted(r['register'] for r in restores)==sorted(save_map),'Each selected saved register has exactly one actual reload')
    stores=[dict(PC=r['PC'],slot=r['immediate'],source_register=r['rs2']) for r in rows if r['op']=='sb' and r['rs1']==2]
    slots=sorted({r['slot'] for r in stores});adjacent=len(slots)==2 and slots[1]==slots[0]+1
    pointers=[dict(PC=r['PC'],register=r['rd'],slot=r['immediate']) for r in rows if r['op']=='addi' and r['rs1']==2 and r['rd']!=2 and r['immediate'] in slots]
    overlap=[dict(saved_register=s['register'],saved_slot=s['slot'],reply_slot=slot) for s in saves for slot in slots if s['slot']<=slot<s['slot']+4]
    extra_SP_words=[dict(PC=r['PC'],op=r['op'],register=r['rs2'],slot=r['immediate']) for r in rows if r['op']=='sw' and r['rs1']==2 and r['PC'] not in {s['PC'] for s in saves}]
    return dict(frame_bytes=frame,saves=saves,restores=restores,common7_slots_match_original=all(save_map.get(k)==v for k,v in COMMON.items()),
        common7_entry_relative_addresses_match_original=all(save_map.get(k,0)-frame==v-48 for k,v in COMMON.items()),
        save_order_matches_original=[s['register'] for s in saves]==[8,18,1,9,19,20,21],extra_saved_registers=[r for r in saves if r['register'] not in COMMON],
        reply_byte_stores=stores,reply_slots=slots,two_adjacent_SP_byte_slots=adjacent,reply_pointer_materializations=pointers,
        reply_saved_word_overlap=overlap,other_SP_word_stores=extra_SP_words,
        entry_relative_reply_offset=slots[0]-frame if adjacent else None,original_entry_relative_reply_offset=-36,
        numeric_reply_pointer_matches_original=adjacent and slots[0]-frame==-36,
        independent_reply_storage_projection=adjacent and bool(pointers) and not overlap and not any(w['slot']<=x<w['slot']+4 for w in extra_SP_words for x in slots),
        complete_lifetime_or_physical_ABI_proved=False)
def original(root,firmware):
    _,_,_,decode,_=context(root);need(sha(firmware)==FW and Path(firmware).stat().st_size==76800,'Actual official ID2966')
    raw=Path(firmware).read_bytes();expected=read(case(root,'v4160-ota-handler-2026-10-22')/'source-review/instructions.json')
    rows=[];at=0x9c4a
    while at<0x9e5c:
        row=decode(raw[at-0x8000:],at);rows.append(row);at+=row['bytes']
    need(rows==expected,'All169 original handler operand rows match retained source')
    measured=projection(rows);need(measured['frame_bytes']==48 and measured['reply_slots']==[12,13] and measured['common7_slots_match_original'],'Original frame/reply source')
    caller=[];at=0x1408e
    while at<0x140a6:
        row=decode(raw[at-0x8000:],at);caller.append(row);at+=row['bytes']
    need([(r['op'],r['rd'],r['rs1'],r['rs2'],r['immediate'],r['target']) for r in caller]==
        [('mv',13,18,None,None,None),('mv',12,8,None,None,None),('mv',10,9,None,None,None),('jal',1,None,None,None,0x9c4a),
         ('lw',1,2,None,188,None),('lw',8,2,None,184,None),('lw',9,2,None,180,None),('lw',18,2,None,176,None),('lw',19,2,None,172,None),
         ('addi',2,2,None,192,None),('jalr',0,1,None,0,None)],'Exact original caller inputs and fresh-return frame projection')
    uid=case(root,'v4160-ota-handler-compact-2026-10-22')/'callee-review'
    refs=runpy.run_path(str(uid/'review.py'));refs['closed'](uid,'5b915632290d82c30545fa9ec517fc96bb67d706abf71f592e53354c3a622a8c')
    actual=refs['rows'](raw[0x12ba:0x1334],0x92ba,decode)
    need(actual==read(uid/'app-instructions.json'),'Bounded122B UID builder/comparator actual operand rows')
    return dict(handler=measured,caller_rows=caller,caller_checks_A0_status_after_return=False,caller_restores_S7=False,
        UID_App_bytes=122,UID_invalid_length_fastpath_preserves_S_GP_SP=True,UID_nested_frame_bytes=[32,16],
        UID_or_resident_observes_handler_reply_numeric_address_proved=False,unknown_ROM_preservation_assumed=False)
def native(root,folder):
    fields,llvm,ctx,_,E=context(root);folder=Path(folder).resolve(strict=True);record=read(folder/'verification.json')
    stem='native_alias' if (folder/'native_alias.o').exists() else 'ota_handler'
    names=[stem+'.o',stem+'.ll',stem+'.d'];artifacts={}
    for n in names:
        p=folder/n;item=dict(bytes=p.stat().st_size,sha256=sha(p));need(record['artifacts'][n]==item,'Actual generation receipt binds '+n);artifacts[n]=item
    source_current={p:Path(p).is_file() and sha(p)==pin for p,pin in record['source_pins'].items()}
    need(all(source_current.values()),'Current actual generation source/tool/header pins; stale hypotheses are historical only')
    e=E(folder/(stem+'.o'));found=[s for s in e.symbols if s['name']==NAME];need(len(found)==1,'Unique actual C kernel')
    s=found[0];need(s['info']==18 and s['other']==0 and 0<s['index']<len(e.sections),'Truthful allocated GLOBAL C function')
    sec=e.sections[s['index']];need(sec['flags']&6==6 and s['value']==0 and s['size']==sec['size'],'Actual complete function extent, not a fabricated size')
    blob=e.function_bytes(s);rows=fields['rows'](blob,0,ctx);text=(folder/(stem+'.ll')).read_text()
    if stem=='native_alias':need(hashlib.sha256(blob).hexdigest()=='b486c6eed0d3465c8947fd338e790f1441f29c64827a47b20e1fada18ff863af','Actual delivered568 baseline identity')
    log='alias-disassembly.log' if stem=='native_alias' else 'complete-static-disassembly.log'
    need([{k:v for k,v in r.items() if k!='offset'} for r in rows]==llvm['parse']((folder/log).read_text()),'Every actual raw field agrees with LLVM output')
    calls=[r for r in e.relocations if r['type']==17];need(len(calls)==12 and len(e.relocations)==20 and all(r['symbol']['index']==0 for r in e.relocations),'Unchanged12direct/20RELA genuineUND topology')
    asm=[x for x in text.splitlines() if 'asm sideeffect "jal' in x]
    prefix=','.join(['={x'+str(i)+'}' for i in range(10,18)]+['{x'+str(i)+'}' for i in range(10,18)])
    need(len(asm)==13 and all(prefix in x and '~{memory}' in x for x in asm),'Actual full8 call bridges retained')
    loop=runpy.run_path(str(case(root,'v4160-ota-handler-compact-2026-10-22')/'ABI-review/loop.py'))
    response=loop['response_ir'](text);measured=projection(rows)
    return dict(folder=str(folder),mode=record['mode'],actual_bytes=len(blob),actual_instructions=len(rows),function=dict(name=s['name'],bytes=s['size'],owner=sec['name']),
        artifacts=artifacts,producer_receipt_sha256=sha(folder/'verification.json'),all_generation_source_pins_current=all(source_current.values()),
        stale_source_pin_paths=[p for p,okay in source_current.items() if not okay],measured=measured,IR_response=response,
        all_allocated_function_symbols=[dict(name=x['name'],bytes=x['size'],offset=x['value']) for x in e.symbols if x['info']&15==2 and 0<x['index']<len(e.sections)],
        source_delta=source_delta.inspect(root) if stem=='ota_handler' else None,full8_bridges=True,full_ABI_admitted=False)
def controls(root,folder):
    fields,_,ctx,_,E=context(root);folder=Path(folder);stem='native_alias' if (folder/'native_alias.o').exists() else 'ota_handler'
    e=E(folder/(stem+'.o'));s=next(s for s in e.symbols if s['name']==NAME);body=e.function_bytes(s);rows=fields['rows'](body,0,ctx);normal=projection(rows)
    need(normal['independent_reply_storage_projection'],'Actual independent current reply storage')
    out=HERE/'build'/('controls-'+uuid.uuid4().hex);out.mkdir(parents=True)
    # Negative-only raw changes, never production assembly or generated target providers.
    wrong=bytearray(body)
    for r in rows:
        if r['rs1']!=2:continue
        at=r['PC'];word=int.from_bytes(wrong[at:at+r['bytes']],'little')
        if r['op']=='sb' and r['immediate'] in normal['reply_slots']:
            want=12+(r['immediate']-normal['reply_slots'][0]);need(r['bytes']==4 and 0<=want<32,'Bounded negative store field')
            word^=(r['immediate']^want)<<7
        elif r['op']=='addi' and r['rd']!=2 and r['immediate']==normal['reply_slots'][0]:
            need(r['bytes']==4,'Bounded negative pointer field');word^=(r['immediate']^12)<<20
        wrong[at:at+r['bytes']]=word.to_bytes(r['bytes'],'little')
    mutated=projection(fields['rows'](bytes(wrong),0,ctx))
    need(mutated['reply_saved_word_overlap'] and not mutated['independent_reply_storage_projection'],'Forced numeric SP12 aliases saved register; rejected as safe storage')
    sec=e.sections[s['index']];data=bytearray(e.raw);data[sec['offset']:sec['offset']+len(body)]=wrong
    path=out/'forced-SP12-overlap.o';path.write_bytes(data)
    results=[dict(case='forced_reply_SP12_overlaps_saved_S7',rejected=True,actual_mutated_ELF_sha256=sha(path),overlap=mutated['reply_saved_word_overlap'])]
    restore=next(r for r in rows if r['op']=='lw' and r['rs1']==2 and r['rd']==23);found=None
    for bit in range(restore['bytes']*8):
        wrong=bytearray(body);wrong[restore['PC']+bit//8]^=1<<(bit%8)
        try:changed=fields['rows'](bytes(wrong),0,ctx);one=next(r for r in changed if r['PC']==restore['PC'])
        except ValueError:continue
        if one['op']!=restore['op'] or one['rd']!=restore['rd'] or one['rs1']!=2 or one['immediate']==restore['immediate']:continue
        try:projection(changed)
        except ValueError as error:
            if 'reload uses its own saved slot' in str(error):found=(bytes(wrong),one['immediate']);break
    need(found is not None,'Actual savedS7 restore mismatch control')
    data=bytearray(e.raw);data[sec['offset']:sec['offset']+len(body)]=found[0];path=out/'wrong-S7-restore-slot.o';path.write_bytes(data)
    results.append(dict(case='savedS7_restored_from_wrong_slot',rejected=True,actual_mutated_ELF_sha256=sha(path),wrong_slot=found[1]))
    return results
def inspect(root,firmware,folder=None):
    root=Path(root).resolve(strict=True);closed();result=dict(schema='TSL9-reply-frame-independent-v1',passed=True,metadata_only=False,actual_original_firmware_read=True,
        original=original(root,firmware),actual_native_artifacts_read=bool(folder),new_compile_or_HOST=False,target_execution=False,ISA_emulation=False,hardware_OTA_proved=False)
    if folder:result['native']=native(root,folder)
    result['borrowed_saved_word_example']=dict(kind='Static little-endian storage overlap algebra, not target execution',original_saved_S7=0xa1b2c3d4,
        reply_bytes=[5,1],overwritten_saved_word=(0xa1b2c3d4&0xffff0000)|0x0105,caller_has_no_S7_restore=True,
        same_numeric_pointer_sufficient=False,requires_real_nonoverlapping_storage_or_explicit_backup_restore=True)
    return result
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--firmware',required=True,type=Path)
    p.add_argument('--folder',type=Path);p.add_argument('--receipt',type=Path);p.add_argument('--replay',type=Path);p.add_argument('--controls',action='store_true');a=p.parse_args()
    if a.replay:
        need(not a.receipt and not a.folder and not a.controls,'Readonly replay mode');saved=read(a.replay);got=inspect(a.project_root,a.firmware,Path(saved['folder']) if saved['folder'] else None)
        want=dict(saved['result']);want.pop('focused_actual_controls',None)
        need(got==want,'Exact actual frame readback');print(json.dumps(got));return
    need(a.receipt and not a.receipt.exists() and (not a.folder or not a.receipt.resolve().is_relative_to(a.folder.resolve())),'Explicit create-only report outside input folder');got=inspect(a.project_root,a.firmware,a.folder)
    if a.controls:
        need(a.folder,'Actual folder for focused controls');got['focused_actual_controls']=controls(a.project_root.resolve(),a.folder.resolve())
    a.receipt.parent.mkdir(parents=True,exist_ok=True)
    with a.receipt.open('xb') as f:f.write((json.dumps(dict(folder=str(a.folder.resolve()) if a.folder else None,result=got),indent=2)+'\n').encode())
    print(json.dumps(got))
if __name__=='__main__':main()
