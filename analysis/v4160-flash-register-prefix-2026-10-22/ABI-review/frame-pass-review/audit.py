"""Independent guard and actual-object audit of the source-owned save scheduler; no BIN generation."""
from pathlib import Path
import argparse,hashlib,json,runpy,struct,subprocess,sys,uuid
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
SHA=lambda b:hashlib.sha256(b).hexdigest()
SCHEDULER_SHA='dc680558aca230a54e1fc05f68960f85f4566b0928787caef21839cdd876535d'
POLICY_SHA='2af7789f91ceabca11fc29eb264991b96f40664555cdfe08964284f1470a694d'


def need(v,why):
    if not v:raise ValueError(why)


class BytesInput:
    def __init__(self,b):self.b=b
    def read_bytes(self):return self.b


def negatives(e,policy,tool,ctx):
    old=ctx['prior'];ELF=ctx['ELF'];records=[];rule=policy['functions']['irq'];s=e.byname[rule['section']];start=s['offset']+2;shoff=struct.unpack_from('<I',e.raw,32)[0]
    def test(name,b,selected=('irq','quarter')):
        try:tool['plan'](ELF(BytesInput(bytes(b))),policy,list(selected))
        except (ValueError,KeyError,IndexError,struct.error) as err:reason=str(err);rejected=True
        else:reason='accepted';rejected=False
        records.append(dict(name=name,actual_object_sha256=SHA(e.raw),mutated_sha256=SHA(bytes(b)),rejected=rejected,reason=reason))
    def replace(name,p,b):
        raw=bytearray(e.raw);need(raw[p:p+len(b)]!=b,'actual negative changes bytes');raw[p:p+len(b)]=b;test(name,raw)
    first=struct.unpack_from('<H',e.raw,start)[0]
    for name,mask in [('wrong-save-register',4),('wrong-save-slot',0x200),('high-save-slot64',0x80),('wrong-store-width',1<<13)]:replace(name,start,struct.pack('<H',first^mask))
    first=struct.unpack_from('<H',e.raw,s['offset'])[0];replace('wrong-frame-size',s['offset'],struct.pack('<H',first^0x40))
    p=old['symbol_offset'](e,lambda x:x['name']==rule['symbol']);replace('local-not-public-FUNC',p+12,b'\x02');replace('hidden-not-default-visibility',p+13,b'\x02');replace('wrong-function-size',p+8,struct.pack('<I',146))
    candidates=[(table,i,a) for table,entries in e.symbol_tables.items() for i,a in enumerate(entries) if a['index']==s['index'] and a['name'].startswith('$x') and a['value']==0]
    need(len(candidates)==1,'one actual entry mapping');table,i,a=candidates[0];replace('interior-symbol-anchor',e.sections[table]['offset']+i*16+4,struct.pack('<I',2))
    relocation=next(r for r in e.relocations if r['owner']==s['name']);p=old['rela_offset'](e,lambda r:r==relocation);replace('relocation-site-in-prefix',p,struct.pack('<I',2))
    relsec=next(a for a in e.sections if a['type']==4 and a['info']==s['index']);entries=e.symbol_tables[relsec['link']];indices=[i for i,a in enumerate(entries) if a['index']==s['index'] and a['info']==3];need(len(indices)==1,'one actual SECTION reference symbol');b=bytearray(e.raw);struct.pack_into('<I',b,p+4,(indices[0]<<8)|relocation['type']);struct.pack_into('<i',b,p+8,2);test('recorded-target-in-prefix',b)
    attrs=e.byname['.riscv.attributes'];shstr=e.sections[struct.unpack_from('<H',e.raw,50)[0]];replace('unwind-provider',shstr['offset']+attrs['name_offset'],b'.eh_frame\0')
    comment=e.byname['.comment'];replace('aliased-comment-storage',shoff+comment['index']*40+16,struct.pack('<I',start))
    replace('duplicate-selected-owner-name',shoff+comment['index']*40,struct.pack('<I',s['name_offset']))
    replace('ET_EXEC-input',16,struct.pack('<H',2));replace('program-header-present',44,struct.pack('<H',1));replace('hardfloat-flags',36,struct.pack('<I',5))
    second=struct.unpack_from('<H',e.raw,start+2)[0];replace('overlapping-save-slots',start+2,struct.pack('<H',(second&~0x1f80)|(struct.unpack_from('<H',e.raw,start)[0]&0x1f80)))
    test('empty-selection',e.raw,());test('duplicate-selection',e.raw,('irq','irq'))
    scheduled,_,_=tool['plan'](e,policy,['irq','quarter']);test('double-application',scheduled)
    need(len(records)==21,'bounded twentyone object guard controls');return records


def linked_review(before,after,merged,ctx):
    old=ctx['prior'];roles=old['sections_and_roles'](merged,after,ctx);loads=old['program_headers'](after);changed=[]
    allowed={0x9a44,0x9a46,0x9a48,0x9a4a,0x9c0c,0x9c0e,0x9c10}
    for name,s in old['alloc'](before).items():
        t=after.byname[name];a=old['data'](before,s);b=old['data'](after,t);need(len(a)==len(b),'same section extent after actual link')
        for i,(x,y) in enumerate(zip(a,b)):
            if x!=y:changed.append(s['address']+i);need((s['address']+i)&~1 in allowed,'only actual seven compiled store words differ')
    need(len(changed)==14,'exact fourteen changed linked bytes')
    incoming=[]
    for r in ctx['plan']['checks']['incoming']:
        owner=r['owner'];va=ctx['manifest']['allocations'][owner]['originalVA'];a=old['direct_jump'](old['data'](before,before.byname[owner]),r['offset'],va);b=old['direct_jump'](old['data'](after,after.byname[owner]),r['offset'],va);need(a==b,'all twenty actual incoming width/rd/target/RA contracts');incoming.append(b)
    functions=[]
    for va,name,size in [(0x9a42,'tsl9_rebuild_interrupt_registers_9a42',144),(0x9c0a,'tsl9_flash_quarter_9c0a',64)]:
        s=next(s for s in after.symbols if s['name']==name);body=after.function_bytes(s);need(body==ctx['original'][va-0x8000:va-0x8000+size],'actual linked scheduled frame function exactly original instructions');functions.append(dict(name=name,bytes=size,sha256=SHA(body),whole_original_function_identity=True))
    return dict(roles=roles,LOAD=loads,changed_linked_addresses=changed,twenty_actual_incoming=incoming,functions=functions,whole_image_instruction_semantic_equivalence=False,original_BIN_used_for_verification_only=True)


def audit(root,out):
    path=root/'experiments/tsl9-v4160-frame-schedule/schedule.py';policy_path=path.with_name('frame-policy.json');tool_pin=SHA(path.read_bytes());policy_pin=SHA(policy_path.read_bytes());need(tool_pin==SCHEDULER_SHA and policy_pin==POLICY_SHA,'explicit frozen scheduler/policy');tool=runpy.run_path(str(path));policy=json.loads(policy_path.read_bytes());old_path=root/'apk-analysis/tsl9-v4160-flash-image-integration-2026-10-22/ABI-review/review.py'
    if not old_path.is_file():old_path=root/'analysis/v4160-flash-image-integration-2026-10-22/ABI-review/review.py'
    need(SHA(old_path.read_bytes())=='4d7e1b4ffa5101347970a662390c4cb8ff6455161e47d6e68f2144a27b8ca7e1','sealed prior independent whole-image checker');old=runpy.run_path(str(old_path));ctx=old['context'](root);ctx['prior']=old;ELF=ctx['ELF'];build=HERE/'build'/('audit-'+uuid.uuid4().hex);build.mkdir(parents=True);transforms=[];links=[]
    for mode in ('c','cpp'):
        baseline=root/'experiments/tsl9-v4160-flash-image-integration/build/formal-final'/mode;receipt_raw=(baseline/'verification.json').read_bytes();r=json.loads(receipt_raw);expected={'c':'c92decef824aa6ec561ce17205ecd722c37a70b710c8289b0e436eca7185e59b','cpp':'afc2097b10855038e6fb861b9fbcbaf79dbd804924b784cf96f9afd8a5ba5ebb'};need(SHA(receipt_raw)==expected[mode],'actual source compiler baseline receipt');folder=build/mode;folder.mkdir()
        for unit,filename,selected in [('merged','source-integrated.o',['irq','quarter']),('irq','main.o',['irq']),('quarter','flash-quarter.o',['quarter'])]:
            compiler_source=baseline/filename;source=folder/(unit+'-compiler-input.o');raw=compiler_source.read_bytes();need(SHA(raw)==r['artifacts'][filename]['sha256'],'exact actual compiler artifact provenance');source.write_bytes(raw);dest=folder/(unit+'-scheduled.o');receipt=folder/(unit+'-scheduling.json');before=ELF(source);value=tool['transform'](root,source,dest,receipt,selected);after=ELF(dest);need(before.sections==after.sections and before.symbols==after.symbols and before.relocations==after.relocations,'independent metadata/symbol/RELA equality');need(len(value['changed_file_offsets'])==({'merged':14,'irq':8,'quarter':6}[unit]),'exact changed bytes per actual object')
            transforms.append(dict(mode=mode,unit=unit,compiler_origin=old['relative'](root,compiler_source),compiler_receipt_sha256=expected[mode],input=old['relative'](root,source),input_sha256=SHA(before.raw),output=old['relative'](root,dest),output_sha256=SHA(after.raw),receipt=old['relative'](root,receipt),receipt_sha256=SHA(receipt.read_bytes()),changed_bytes=len(value['changed_file_offsets']),section_metadata_symbols_RELA_unchanged=True))
        before_path=folder/'compiler-witness.elf';before_raw=(baseline/'ADDRESS-WITNESS-ONLY.elf').read_bytes();need(SHA(before_raw)==r['artifacts']['ADDRESS-WITNESS-ONLY.elf']['sha256'],'actual previous compiler witness provenance');before_path.write_bytes(before_raw)
        command=next(c['argv'] for c in r['commands'] if c['label']=='numeric-witness-final-link');argv=[str(folder/'merged-scheduled.o') if Path(a).resolve()==(baseline/'source-integrated.o').resolve() else a for a in command];argv[argv.index('-o')+1]=str(folder/'ADDRESS-WITNESS-ONLY.elf');linker=Path(argv[0]);linkpin=SHA(linker.read_bytes());done=subprocess.run(argv,capture_output=True,timeout=60);log=folder/'link.log';log.write_bytes(done.stdout+done.stderr);need(done.returncode==0 and SHA(linker.read_bytes())==linkpin,'actual unchanged-profile numeric witness link');checks=linked_review(ELF(before_path),ELF(folder/'ADDRESS-WITNESS-ONLY.elf'),ELF(folder/'merged-scheduled.o'),ctx);links.append(dict(mode=mode,argv=argv,exit=done.returncode,linker_sha256=linkpin,compiler_witness=old['relative'](root,before_path),compiler_witness_sha256=SHA(before_raw),ELF=old['relative'](root,folder/'ADDRESS-WITNESS-ONLY.elf'),ELF_sha256=SHA((folder/'ADDRESS-WITNESS-ONLY.elf').read_bytes()),log=old['relative'](root,log),log_sha256=SHA(log.read_bytes()),checks=checks))
    guard=negatives(ELF(root/'experiments/tsl9-v4160-flash-image-integration/build/formal-final/c/source-integrated.o'),policy,tool,ctx)
    source=root/'experiments/tsl9-v4160-flash-image-integration/build/formal-final/c/main.o';original_pin=SHA(source.read_bytes());path_controls=[]
    for label in ('input-output','input-receipt','output-receipt'):
        dest=build/(label+'.o');receipt=build/(label+'.json');a,b,c=(source,source,receipt) if label=='input-output' else ((source,dest,source) if label=='input-receipt' else (source,dest,dest))
        try:tool['transform'](root,a,b,c,['irq'])
        except ValueError as err:reason=str(err)
        else:raise ValueError('aliased path accepted '+label)
        need(SHA(source.read_bytes())==original_pin and not dest.exists() and not receipt.exists(),'all path-alias rejections precede writes')
        path_controls.append(dict(name=label,rejected=True,source_unchanged=True,no_output_created=True,reason=reason))
    need(SHA(path.read_bytes())==tool_pin and SHA(policy_path.read_bytes())==policy_pin,'scheduler and policy stable before/after independent audit')
    result=dict(schema='TSL9-independent-frame-scheduler-object-audit-v1',passed=all(r['rejected'] for r in guard),reviewer_sha256=SHA(Path(__file__).read_bytes()),scheduler_sha256=tool_pin,policy_sha256=policy_pin,transforms=transforms,actual_links=links,actual_object_guard_controls=guard,all_three_path_alias_controls=path_controls,original_BIN_read_by_transform=False,new_BIN_generated=False,target_execution=False,ISA_emulation=False,network=False,unknown_computed_interior_entries_proved_absent=False,full_async_or_hardware_proof=False)
    out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes((json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode());return dict(passed=result['passed'],report=str(out),sha256=SHA(out.read_bytes()),object_guard_controls=len(guard),accepted_controls=[r['name'] for r in guard if not r['rejected']],actual_transforms=6,actual_links=2)


def replay(root,path):
    r=json.loads(path.read_bytes());need(r['schema']=='TSL9-independent-frame-scheduler-object-audit-v1' and r['passed'],'final scheduler audit receipt');need(r['reviewer_sha256']==SHA(Path(__file__).read_bytes()),'independent frame audit source pin')
    scheduler=root/'experiments/tsl9-v4160-frame-schedule/schedule.py';policy_path=scheduler.with_name('frame-policy.json');need(SHA(scheduler.read_bytes())==r['scheduler_sha256']==SCHEDULER_SHA and SHA(policy_path.read_bytes())==r['policy_sha256']==POLICY_SHA,'frozen actual scheduler/policy');tool=runpy.run_path(str(scheduler));policy=json.loads(policy_path.read_bytes())
    old_path=root/'apk-analysis/tsl9-v4160-flash-image-integration-2026-10-22/ABI-review/review.py'
    if not old_path.is_file():old_path=root/'analysis/v4160-flash-image-integration-2026-10-22/ABI-review/review.py'
    need(SHA(old_path.read_bytes())=='4d7e1b4ffa5101347970a662390c4cb8ff6455161e47d6e68f2144a27b8ca7e1','prior sealed whole-image checker');old=runpy.run_path(str(old_path));ctx=old['context'](root);ctx['prior']=old;ELF=ctx['ELF'];inputs={};outputs={}
    for t in r['transforms']:
        before_path=old['input_path'](root,t['input']);after_path=old['input_path'](root,t['output']);receipt=old['input_path'](root,t['receipt']);a=ELF(before_path);b=ELF(after_path);need(SHA(a.raw)==t['input_sha256'] and SHA(b.raw)==t['output_sha256'] and SHA(receipt.read_bytes())==t['receipt_sha256'],'actual retained pre/post/receipt pins');selected=['irq','quarter'] if t['unit']=='merged' else [t['unit']];payload,proofs,changed=tool['plan'](a,policy,selected);need(payload==b.raw and len(changed)==t['changed_bytes'],'fresh pure scheduling plan equals actual output');need(a.sections==b.sections and a.symbols==b.symbols and a.relocations==b.relocations,'all metadata/symbol/RELA exact')
        rec=json.loads(receipt.read_bytes());need(rec['passed'] and rec['tool_sha256']==SCHEDULER_SHA and rec['policy_sha256']==POLICY_SHA and rec['input']['sha256']==SHA(a.raw) and rec['output']['sha256']==SHA(b.raw) and rec['functions']==proofs and rec['changed_file_offsets']==changed,'actual transform receipt semantic replay');need(not rec['original_BIN_read_for_generation'] and not rec['new_opcodes_generated'] and not rec['padding_added'] and not rec['compiler_alone_emitted_scheduled_order'],'explicit scheduling provenance boundary');inputs[t['mode'],t['unit']]=a;outputs[t['mode'],t['unit']]=b
    need(len(inputs)==6,'six distinct actual transformations')
    for t in r['actual_links']:
        before=ELF(old['input_path'](root,t['compiler_witness']));after=ELF(old['input_path'](root,t['ELF']));log=old['input_path'](root,t['log']);need(SHA(before.raw)==t['compiler_witness_sha256'] and SHA(after.raw)==t['ELF_sha256'] and SHA(log.read_bytes())==t['log_sha256'] and t['exit']==0,'actual static linked witnesses/logs');need(linked_review(before,after,outputs[t['mode'],'merged'],ctx)==t['checks'],'all691 role/LOAD/frame/20incoming contracts replay')
    need(negatives(inputs['c','merged'],policy,tool,ctx)==r['actual_object_guard_controls'],'all21 actual-object mutation controls replay')
    need(len(r['all_three_path_alias_controls'])==3 and {x['name'] for x in r['all_three_path_alias_controls']}=={'input-output','input-receipt','output-receipt'} and all(x['rejected'] and x['source_unchanged'] and x['no_output_created'] for x in r['all_three_path_alias_controls']),'retained all3 actual pre-write alias rejection results')
    return dict(passed=True,transforms=6,actual_linked_witnesses=2,actual_object_controls=21,actual_prewrite_path_alias_controls=3,tool_execution_or_file_writes_in_replay=False,unknown_computed_interior_entries_proved_absent=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',type=Path,default=ROOT);p.add_argument('--report',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args()
    if a.replay:result=replay(a.project_root.resolve(),a.replay.resolve())
    else:need(a.report is not None,'fresh audit requires --report');result=audit(a.project_root.resolve(),a.report.resolve())
    print(json.dumps(result,sort_keys=True))
