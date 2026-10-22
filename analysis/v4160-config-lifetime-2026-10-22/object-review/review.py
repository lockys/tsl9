"""Independent declared-object/frame projection; static source/IR/ELF only."""
import argparse,hashlib,json,re,runpy,sys,uuid
from collections import Counter
from pathlib import Path
import delta

HERE=Path(__file__).resolve().parent
NAME='tsl9_ota_handler_native_9c4a'
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def case(root,n):return next(p for p in (root/'apk-analysis'/('tsl9-'+n),root/'analysis'/n) if p.is_dir())
def closed():
    if (HERE/'seal.json').exists():
        for n,pin in read(HERE/'seal.json')['members'].items():need(sha(HERE/n)==pin,'Closed object-review member '+n)
def context(root):
    p=case(root,'v4160-allocator-callback-2026-10-22')/'frame-review/review.py'
    need(sha(p)=='629cae8ea2f236c51d55946a69afec8f7a6cf1734bdf4d54c84feceb06849eed','Immutable prior frame reader')
    sys.path.insert(0,str(p.parent))
    try:m=runpy.run_path(str(p))
    finally:sys.path.pop(0)
    return m
def ir_object(text):
    allocations=[list(x) for x in re.findall(r'^\s*(%\d+) = alloca (.*)$',text,re.M)]
    need(len(allocations)==1 and allocations[0][1].startswith('[4 x i8], align 4'),'Actual full4-byte aligned backing IR allocation')
    ptr=allocations[0][0];users=[line.strip() for line in text.splitlines() if re.search(r'ptr '+re.escape(ptr)+r'(?:,|\)| to )',line)]
    second=re.compile(r'getelementptr inbounds i8, ptr '+re.escape(ptr)+r', i32 1(?:,|$)')
    need(users and all('store volatile i8 ' in line or second.search(line) or 'ptrtoint ptr '+ptr in line or '@llvm.lifetime.' in line for line in users),
         'Backing users only first-byte stores, second-byte GEP, lifetime and explicit opaque-call pointer')
    need(any('ptrtoint ptr '+ptr+' to i32' in line for line in users),'Actual opaque-call pointer derives from full4B object start')
    need(any('store volatile i8 ' in line and 'ptr '+ptr in line for line in users),'Actual first response byte written')
    second_ssa=next(line.split(' = ',1)[0] for line in users if second.search(line))
    need('store volatile i8 1, ptr '+second_ssa in text,'Actual second response byte remains1')
    second_users=[line.strip() for line in text.splitlines() if re.search(r'ptr '+re.escape(second_ssa)+r'(?:,|\)| to )',line)]
    need(all('store volatile i8 ' in line or '@llvm.lifetime.' in line for line in second_users),'Second-byte pointer has no larger memory access')
    calls=[line for line in text.splitlines() if 'asm sideeffect "jal' in line]
    prefix=','.join(['={x'+str(i)+'}' for i in range(10,18)]+['{x'+str(i)+'}' for i in range(10,18)])
    need(len(calls)==13 and all(prefix in x and '~{memory}' in x and all('~{x'+str(i)+'}' in x for i in (1,5,6,7,28,29,30,31)) for x in calls),'All13 raw8 read/write opaque bridges and caller clobbers retained')
    packet=[line for line in calls if 'jal ra,__tsl9v4160_conditional_code_13e98' in line]
    need(len(packet)==1,'One actual shared packet bridge')
    args=packet[0].rsplit('"(',1)[1].split(') #',1)[0].split(', ')
    need(len(args)==8 and all(a.startswith('i32 ') for a in args),'Actual raw8 packet operands')
    pointer,length=args[2][4:],args[3][4:]
    definitions={m.group(1):m.group(2) for line in text.splitlines() if (m:=re.match(r'\s*(%\w+) = (.*)',line))}
    def incoming(ssa):
        need(definitions.get(ssa,'').startswith('phi i32 '),'Actual packet pointer/length is an explicit shared phi')
        return {label:value.strip() for value,label in re.findall(r'\[\s*([^,]+),\s*(%[\w.]+)\s*\]',definitions[ssa])}
    pointers,lengths=incoming(pointer),incoming(length)
    need(len(lengths)==2 and set(lengths.values())=={'0','2'} and pointers.keys()==lengths.keys(),'Only correlated S2/E0 packet lengths, never4')
    for label,count in lengths.items():
        if count=='0':need(pointers[label]=='0','Empty packet path also has null pointer')
        else:need(definitions.get(pointers[label])=='ptrtoint ptr '+ptr+' to i32','Length2 path points to first byte of owned4B backing')
    need('@llvm.lifetime.start.p0(i64 4, ptr nonnull '+ptr+')' in text and '@llvm.lifetime.end.p0(i64 4, ptr nonnull '+ptr+')' in text,'Actual complete4B object lifetime, no shrink to2')
    return dict(backing_allocation=allocations,users=users,second_byte_users=second_users,declared_backing_bytes=4,observed_response_bytes=2,
        packet_lengths_by_path=dict(owned_reply=2,empty_reply=0),correlated_packet_pointer_length=True,full8_call_bridges=13,upper_two_bytes_initialized_locally=False,unknown_provider_read_footprint_proved=False)
def storage(rows,projection,backing_bytes=4):
    p=projection(rows);need(p['two_adjacent_SP_byte_slots'],'Actual adjacent first two byte writes')
    start=p['reply_slots'][0];need(start>=0 and start+backing_bytes<=p['frame_bytes'],'Entire declared backing within real frame')
    need(p['reply_pointer_materializations'] and all(x['slot']==start for x in p['reply_pointer_materializations']),'Actual materialized pointer to first backing byte')
    backing=range(start,start+backing_bytes)
    for r in rows:
        if r['rs1']!=2 or r['memory_width'] is None:continue
        span=range(r['immediate'],r['immediate']+r['memory_width']//8)
        if set(span)&set(backing):need(r['op']=='sb' and r['immediate'] in (start,start+1),'No save/spill/load/word-initialization aliases any declared backing byte')
    need(p['frame_bytes']==48 and len(p['saves'])==8 and p['reply_slots']==[12,13] and p['numeric_reply_pointer_matches_original'],'Measured8saves/48frame/entryminus36 projection')
    need(not p['reply_saved_word_overlap'] and not p['other_SP_word_stores'],'No borrowed saved-slot/hiddenSPword storage')
    need(p['common7_entry_relative_addresses_match_original'],'Seven original save addresses remain correct relative to entry')
    return dict(projection=p,full_backing_SP_range=[12,16],full_backing_entry_range=[-36,-32],full4B_nonoverlap=True,
                original_numeric_reply_pointer_matched=True,physical_prefix_or_whole_ABI_proved=False)
def inspect(root,folder,firmware):
    root=Path(root).resolve(strict=True);folder=Path(folder).resolve(strict=True);closed();m=context(root);fields,llvm,ctx,_,E=m['context'](root)
    record=read(folder/'verification.json');need(record['mode'] in ('c','cpp'),'Actual candidate language')
    for name in ('ota_handler.o','ota_handler.ll','ota_handler.d','complete-static-disassembly.log'):
        p=folder/name;need(record['artifacts'][name]==dict(bytes=p.stat().st_size,sha256=sha(p)),'Actual generation artifact '+name)
    for path,pin in record['source_pins'].items():need(Path(path).is_file() and sha(path)==pin,'Current actual source/tool/header pin '+path)
    e=E(folder/'ota_handler.o');s=[x for x in e.symbols if x['name']==NAME];need(len(s)==1,'One actual C kernel')
    s=s[0];need(s['info']==18 and s['other']==0 and 0<s['index']<len(e.sections),'Truthful allocated GLOBAL function')
    need([x for x in e.symbols if x['info']&15==2 and 0<x['index']<len(e.sections)]==[s],'One real allocated C function, no invented aliases')
    sec=e.sections[s['index']];need(sec['flags']&6==6 and s['value']==0 and s['size']==sec['size'],'Actual full allocated extent, no fake size')
    need([x for x in e.sections if x['flags']&2 and x['size']]==[sec],'No extra helper/padding allocations')
    body=e.function_bytes(s);rows=fields['rows'](body,0,ctx)
    need([{k:v for k,v in r.items() if k!='offset'} for r in rows]==llvm['parse']((folder/'complete-static-disassembly.log').read_text()),'Every raw operand equals actual LLVM output')
    need(len(e.relocations)==20 and sum(r['type']==17 for r in e.relocations)==12 and all(r['symbol']['index']==0 for r in e.relocations),'Actual20RELA/12JAL obligations stay genuineUND')
    direct={'__tsl9v4160_ota_code_92f2':4,'__tsl9v4160_call_9c0a':1,'__tsl9v4160_call_9124':4,'__tsl9v4160_ota_code_13f66':1,'__tsl9v4160_conditional_code_13e98':1,'__tsl9v4160_ota_code_9b8e':1}
    expected=Counter({(17,name):count for name,count in direct.items()})
    expected.update({(kind,name):count for name,count in {'__tsl9v4160_ota_code_8e18':2,'__tsl9v4160_ota_code_9ee0':1,'__tsl9v4160_captured_body_99e8':1}.items() for kind in (26,27)})
    need(Counter((r['type'],r['symbol']['name']) for r in e.relocations)==expected and all(r['owner']==sec['name'] and r['addend']==0 for r in e.relocations),'Same six callees/threecallback obligations and exact actual relocation roles')
    source_delta=delta.inspect(root);original=m['original'](root,firmware);obj=ir_object((folder/'ota_handler.ll').read_text());place=storage(rows,m['projection'])
    return dict(schema='TSL9-independent-reply-object-review-v1',passed=True,metadata_only=False,actual_original_firmware_read=True,actual_native_artifacts_read=True,
        folder=folder.relative_to(root).as_posix(),mode=record['mode'],actual_bytes=len(body),actual_instructions=len(rows),
        object_sha256=sha(folder/'ota_handler.o'),IR_sha256=sha(folder/'ota_handler.ll'),producer_receipt_sha256=sha(folder/'verification.json'),
        original_frame=original['handler'],source_delta=source_delta,IR_object=obj,storage=place,
        physical_callee_saved_register_contract_proved=False,unknown_allocator_callback_footprint_proved=False,full_ABI_admitted=False,
        new_link=False,new_BIN=False,HOST_rerun=False,target_execution=False,ISA_emulation=False,hardware_OTA_proved=False)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--firmware',required=True,type=Path)
    p.add_argument('--folder',type=Path);p.add_argument('--receipt',type=Path);p.add_argument('--replay',type=Path);p.add_argument('--controls',action='store_true');a=p.parse_args();root=a.project_root.resolve(strict=True)
    if a.replay:
        need(not a.folder and not a.receipt and not a.controls,'Readonly replay mode');saved=read(a.replay);got=inspect(root,root/saved['result']['folder'],a.firmware)
        wanted=dict(saved['result']);wanted.pop('focused_actual_controls',None)
        need(got==wanted,'Canonical readonly actual replay');print(json.dumps(got));return
    need(a.folder and a.receipt and not a.receipt.exists() and not a.receipt.resolve().is_relative_to(a.folder.resolve()),'Explicit actual folder/create-only outside receipt')
    got=inspect(root,a.folder,a.firmware)
    if a.controls:
        import controls
        got['focused_actual_controls']=controls.run(sys.modules[__name__],root,a.folder.resolve())
    a.receipt.parent.mkdir(parents=True,exist_ok=True)
    with a.receipt.open('xb') as f:f.write((json.dumps(dict(result=got),indent=2)+'\n').encode())
    print(json.dumps(got))
if __name__=='__main__':main()
