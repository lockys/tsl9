"""Independent source/scheduling/ELF/image ABI review. Default metadata checks never read build artifacts."""
from pathlib import Path
import argparse,copy,hashlib,json,runpy,struct,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SHA=lambda b:hashlib.sha256(b).hexdigest()
MANIFEST_SHA='743c087e24760779073cd27ef06b7355b9f61ced6a8b14a2e9fc410d3fa10c5e'
PRIOR_REVIEW='de1a55014e3db06fc909cadd92a746c9922b08bcdecfa0bcb28862f98d1f9ca0'
SCHEDULER_SHA='dc680558aca230a54e1fc05f68960f85f4566b0928787caef21839cdd876535d'
POLICY_SHA='2af7789f91ceabca11fc29eb264991b96f40664555cdfe08964284f1470a694d'
MODEL='experiments/tsl9-v4160-register-image-integration'
IMAGE='NOT-FLASH-VALIDATED-register-scheduled.bin'
PRODUCER_SHA='73d3fb0525d5f47c772632a2e397533d86fd3b58e2a26feeecfbd06ddac1bdb1'


def need(v,why):
    if not v:raise ValueError(why)


def metadata(root):
    manifest=root/MODEL/'source-manifest.json';need(SHA(manifest.read_bytes())==MANIFEST_SHA,'frozen source manifest');m=json.loads(manifest.read_bytes())
    for name,h in m['source_files'].items():need(SHA((root/name).read_bytes())==h,'current original/typed source '+name)
    for name,h in m['frame_schedule_source_files'].items():need(SHA((root/name).read_bytes())==h,'source-owned scheduling file '+name)
    scheduler=root/'experiments/tsl9-v4160-frame-schedule/schedule.py';policy=scheduler.with_name('frame-policy.json');need(SHA(scheduler.read_bytes())==SCHEDULER_SHA and SHA(policy.read_bytes())==POLICY_SHA,'frozen scheduling tool/policy')
    return dict(passed=True,manifest_sha256=MANIFEST_SHA,source_files=len(m['source_files']),scheduling_files=len(m['frame_schedule_source_files']),actual_build_artifacts_read=False,actual_build_replayed=False),m


def context(root,firmware=None):
    result,m=metadata(root);prior=root/'apk-analysis/tsl9-v4160-flash-image-integration-2026-10-22/ABI-review/review.py'
    if not prior.is_file():prior=root/'analysis/v4160-flash-image-integration-2026-10-22/ABI-review/review.py'
    need(SHA(prior.read_bytes())==PRIOR_REVIEW,'immutable independent whole-image parser/role gates');old=runpy.run_path(str(prior));ctx=old['context'](root,firmware=firmware);ctx['prior']=old;ctx['new_manifest']=m;ctx['schedule']=runpy.run_path(str(root/'experiments/tsl9-v4160-frame-schedule/schedule.py'));ctx['policy']=json.loads((root/'experiments/tsl9-v4160-frame-schedule/frame-policy.json').read_bytes());return ctx


def scheduled(pre,post,receipt,ctx):
    payload,proofs,changes=ctx['schedule']['plan'](pre,ctx['policy'],['irq','quarter']);need(payload==post.raw,'actual post-object equals source-owned permutation of actual compiler object');need(len(changes)==14,'exact14 changed save bytes');need(pre.sections==post.sections and pre.symbols==post.symbols and pre.relocations==post.relocations,'every section/symbol/RELA role unchanged through scheduling')
    need(receipt['schema']=='TSL9-explicit-ABI-frame-scheduling-receipt-v1' and receipt['passed'],'actual scheduling receipt schema/pass');need(receipt['tool_sha256']==SCHEDULER_SHA and receipt['policy_sha256']==POLICY_SHA,'scheduling provenance source pins');need(receipt['input']['sha256']==SHA(pre.raw) and receipt['output']['sha256']==SHA(post.raw) and receipt['functions']==proofs and receipt['changed_file_offsets']==changes,'actual pre/post/proof/offset bindings');need(not receipt['compiler_alone_emitted_scheduled_order'] and not receipt['original_BIN_read_for_generation'] and not receipt['new_opcodes_generated'] and not receipt['padding_added'],'explicit compiler-plus-scheduling provenance, no fallback/templates')
    return dict(compiler_object_sha256=SHA(pre.raw),scheduled_object_sha256=SHA(post.raw),changed_file_offsets=changes,functions=proofs,all_other_bytes_and_metadata_roles_unchanged=True,compiler_alone_emitted_final_order=False)


def bodies(pre,post,linked,ctx):
    old=ctx['prior'];selected=ctx['selected'];functions=[];calls=[];rows_byowner={};boundaries={}
    for owner,a in selected.items():
        va=a['originalVA'];size=a['bytes'];original=ctx['original'][va-0x8000:va-0x8000+size];body=old['data'](linked,linked.byname[owner]);need(body==original,'all eleven actual linked typed bodies identical to original '+owner);ref=ctx['references'][va];symbol=next(s for s in linked.symbols if s['name']==ref['name']);need(symbol['value']==va and symbol['size']==size and symbol['info']==18 and symbol['other']==0,'original typed FUNC ABI/entry/extent')
        patched=bytearray(old['data'](pre,pre.byname[owner]));relocs=[r for r in pre.relocations if r['owner']==owner]
        for r in relocs:
            need(r['type']==17 and r['addend']==0 and old['role'](pre,r['symbol'])['owner'] in selected and r['symbol']['value']==0,'only explicit original-entry JAL fixups');jump=old['direct_jump'](body,r['offset'],va);target=selected[old['role'](pre,r['symbol'])['owner']]['originalVA'];need(jump['rd']==1 and jump['bytes']==4 and jump['target']==target,'actual JAL target/link register');word=int.from_bytes(patched[r['offset']:r['offset']+4],'little');need(word&127==0x6f and (word>>7)&31==1,'actual compiler JAL opcode/RA link');patched[r['offset']:r['offset']+4]=body[r['offset']:r['offset']+4];calls.append(jump)
        expected=ctx['references'][va]['code'] if va in (0x9a42,0x9c0a) else original;need(bytes(patched)==expected,'pre-scheduling compiler body equals sealed compiler frame contract or original leaf')
        if ref['family']=='IRQ':
            offsets=[];pc=0
            while pc<size:
                width=4 if int.from_bytes(body[pc:pc+2],'little')&3==3 else 2;ctx['idecode'](body[pc:pc+width],va+pc);offsets.append(pc);pc+=width
            need(pc==size,'full original IRQ instruction coverage');boundaries[owner]={va+x for x in offsets}
        else:
            rows=ctx['flash']['raw_rows'](body,ctx['decode']);rows_byowner[owner]=rows;boundaries[owner]={va+r['offset'] for r in rows}
        functions.append(dict(name=ref['name'],owner=owner,address=va,bytes=size,original_code_sha256=SHA(original),actual_code_sha256=SHA(body),whole_original_instruction_identity=True))
    need(len(functions)==11 and sum(f['bytes'] for f in functions)==526 and len(calls)==11,'all526 typed bytes/eleven calls');need(all(c['link'] in next(v for n,v in boundaries.items() if selected[n]['originalVA']<=c['site']<selected[n]['originalVA']+selected[n]['bytes']) for c in calls),'all JAL RA continuations are original instruction boundaries')
    branches=[]
    for r in ctx['new_manifest']['old_selected_RELA']:
        if r['type'] not in (16,44):continue
        owner=r['owner'];va=selected[owner]['originalVA'];raw=bytes.fromhex(r['original_branch_bytes']);actual=old['data'](linked,linked.byname[owner])[r['offset']:r['offset']+len(raw)];need(actual==raw,'each discharged branch retains exact original bytes');need(not any(s['name']==r['symbol']['name'] for s in post.symbols),'private branch symbol truly discharged');branches.append(dict(owner=owner,site=va+r['offset'],target=va+r['symbol']['offset'],bytes=len(raw),original_hex=raw.hex(),actual_hex=actual.hex()))
    need(len(branches)==10,'four IRQ plus six Flash branch discharges')
    incoming=[]
    for r in ctx['plan']['checks']['incoming']:
        owner=r['owner'];va=ctx['manifest']['allocations'][owner]['originalVA'];jump=old['direct_jump'](old['data'](linked,linked.byname[owner]),r['offset'],va);expected=next(x for x in ctx['facts']['incoming'] if x['site']==jump['site']);need(jump==expected,'all twenty actual incoming width/rd/target/RA contracts');incoming.append(jump)
    program_owner=next(n for n,a in selected.items() if a['originalVA']==0x18ef2);program=rows_byowner[program_owner];interiors=[dict(address=0x18ef2+x,row=next(r for r in program if r['offset']==x)) for x in (0x10,0x1a,0x28,0x38,0x52)]
    return dict(functions=functions,typed_JALs=sorted(calls,key=lambda x:x['site']),ten_branch_discharges=branches,twenty_actual_incoming=sorted(incoming,key=lambda x:x['site']),program_known_interiors=interiors,all_original_program_boundaries_preserved=True,all_eleven_original_instruction_streams_identical=True,hardware_or_full_async_proof=False)


def image_check(linked,image,ctx):
    actual=ctx['prior']['scatter'](linked,ctx);need(image==actual==ctx['original'],'complete actual76800 image equals linked scatter and original source, without differences');need(struct.unpack_from('<I',linked.raw,24)[0]==0x8000,'original image entry8000');return dict(bytes=len(image),sha256=SHA(image),differences_from_original=0,all690_file_backed_owners_covered=True,complete_scatter_without_holes_or_padding=True,new_typed_bytes_tied_to_actual_compiler_objects=True,hardware_or_OTA_proof=False)


def verify(pre,post,linked,image,frame,ctx):
    return dict(scheduling=scheduled(pre,post,frame,ctx),roles=ctx['prior']['sections_and_roles'](post,linked,ctx),LOAD=ctx['prior']['program_headers'](linked),machine=bodies(pre,post,linked,ctx),image=image_check(linked,image,ctx))


def command_associations(root,folder,r,ctx):
    commands=r['commands'];need(len(commands)==57 and len({x['label'] for x in commands})==57,'57 distinct actual recipes');compile_=[x for x in commands if '-c' in x['argv']];IR=[x for x in commands if '-emit-llvm' in x['argv']];need(len(compile_)==42 and len(IR)==8,'42 actual object compilations and8 actual LLVM IR recipes');outputs={};artifacts=r['artifacts'];logs=[]
    for c in commands:
        need(c['exit']==(1 if c['label']=='strict-final-link' else 0),'sole expected strict missing-ROM failure');p=folder/c['log'];need(SHA(p.read_bytes())==c['log_sha256'],'actual command log '+c['label']);logs.append(dict(label=c['label'],sha256=c['log_sha256'],exit=c['exit']))
        argv=c['argv']
        if '-o' in argv:
            p=Path(argv[argv.index('-o')+1]).resolve();need(p.parent==folder.resolve(),'actual output stays in mode directory');name=p.name
            if c['exit']==0:need(name in artifacts and SHA((folder/name).read_bytes())==artifacts[name]['sha256'],'actual command output artifact association');need(name not in outputs,'unique actual successful producer for output');outputs[name]=c['label']
    comp_labels={x['label'] for x in compile_};expected_carriers={'compile-'+Path(n).stem for n in ctx['new_manifest']['source_units']};need(expected_carriers<=comp_labels and len(expected_carriers)==34,'34 original carrier units are actually compiled')
    need({c['label'] for c in IR}=={'typed-'+s+'-IR' for s in ('main','helpers','flash-quarter','flash-status','flash-unlock','flash-lock','flash-erase','flash-program')},'eight expected actual typed IR recipes')
    scheduling=next(c for c in commands if c['label']=='explicit-frame-scheduling');need('-B' in scheduling['argv'],'actual scheduler Python invocation disables bytecode writes');need('--input' in scheduling['argv'] and Path(scheduling['argv'][scheduling['argv'].index('--input')+1]).name=='compiler-integrated.o' and Path(scheduling['argv'][scheduling['argv'].index('--output')+1]).name=='source-integrated.o','actual scheduling command links actual pre/post files')
    exporter=next(c for c in commands if c['label']=='export-new-offline-image');need(Path(exporter['argv'][-1]).name==IMAGE and Path(exporter['argv'][-2]).name=='ADDRESS-WITNESS-ONLY.elf','actual export reads linked ELF, never original firmware')
    need('source-integrated.o' not in outputs and outputs['compiler-integrated.o']=='merge-source-integrated','scheduler separate from compiler merge provenance')
    for name,pin in r['source_files'].items():need(SHA((root/name).read_bytes())==pin,'actual producer source pin '+name)
    for t in r['tools'].values():
        p=Path(t['path'])
        if p.is_file():need(SHA(p.read_bytes())==t['sha256'],'present actually observed tool identity')
    return dict(actual_commands=57,actual_compilation_units=42,actual_typed_IR=8,all_successful_output_associations=len(outputs),all57_log_associations=logs,source_files_checked=len(r['source_files']),strict_missing_ROM_failure_preserved=True,physical_tool_execution_repeated=False,detailed_primary_MT_header_dependency_closure_reviewed_separately=True)


def bounded_controls(root,folder,r,pre,post,linked,image,frame,ctx):
    records=[]
    def rejected(name,kind,before,after,gate):
        need(before!=after,'bounded control actually changes input')
        try:gate()
        except (ValueError,KeyError,IndexError,struct.error) as exc:reason=str(exc)
        else:raise ValueError('bounded control accepted '+name)
        records.append(dict(name=name,kind=kind,original_sha256=SHA(before),mutated_sha256=SHA(after),rejected=True,reason=reason))
    rejected('unscheduled-object-as-final','actual ELF bytes',post.raw,pre.raw,lambda:scheduled(pre,pre,frame,ctx))
    changed=copy.deepcopy(frame);changed['compiler_alone_emitted_scheduled_order']=True;before=json.dumps(frame,sort_keys=True).encode();after=json.dumps(changed,sort_keys=True).encode();rejected('false-compiler-only-provenance','actual receipt field',before,after,lambda:scheduled(pre,post,changed,ctx))
    owner=next(n for n,a in ctx['selected'].items() if a['originalVA']==0x9a42);s=linked.byname[owner];pos=s['offset']+0x1c;raw=bytearray(linked.raw);word=struct.unpack_from('<I',raw,pos)[0];struct.pack_into('<I',raw,pos,word&~(31<<7));mutant=ctx['ELF'](ctx['prior']['BytesInput'](bytes(raw)));rejected('linked-JAL-ra-changed-to-tail','actual ELF bytes',linked.raw,bytes(raw),lambda:bodies(pre,post,mutant,ctx))
    bad=bytes([image[0]^1])+image[1:];rejected('one-exported-image-byte','actual exported bytes',image,bad,lambda:image_check(linked,bad,ctx))
    changed=copy.deepcopy(r);command=next(c for c in changed['commands'] if c['label']=='export-new-offline-image');command['argv'][-2]=str(root/'original-firmware.bin');before=json.dumps(r['commands'],sort_keys=True).encode();after=json.dumps(changed['commands'],sort_keys=True).encode();rejected('export-source-not-linked-ELF','actual command transcript',before,after,lambda:command_associations(root,folder,changed,ctx))
    need(len(records)==5,'only five new bounded integration controls');return records


def actual(root,folder,firmware=None):
    ctx=context(root,firmware);receipt=folder/'verification.json';r=json.loads(receipt.read_bytes());need(r['schema']=='TSL9-explicit-register-scheduled-source-image-v1' and r['passed'] and r['manifest_sha256']==MANIFEST_SHA,'actual producer receipt schema/pass/manifest')
    if PRODUCER_SHA:need(r['runner_sha256']==PRODUCER_SHA,'explicit final producer runner')
    paths=dict(pre=folder/'compiler-integrated.o',post=folder/'source-integrated.o',linked=folder/'ADDRESS-WITNESS-ONLY.elf',image=folder/IMAGE,frame=folder/'frame-scheduling.json');ELF=ctx['ELF'];pre=ELF(paths['pre']);post=ELF(paths['post']);linked=ELF(paths['linked']);image=paths['image'].read_bytes();frame=json.loads(paths['frame'].read_bytes());checks=verify(pre,post,linked,image,frame,ctx);recipes=command_associations(root,folder,r,ctx);controls=bounded_controls(root,folder,r,pre,post,linked,image,frame,ctx)
    for name,pin in r['artifacts'].items():
        p=folder/name;need(p.stat().st_size==pin['bytes'] and SHA(p.read_bytes())==pin['sha256'],'all actual producer artifact byte pins '+name)
    artifacts={name:dict(bytes=p.stat().st_size,sha256=SHA(p.read_bytes())) for name,p in paths.items()};return dict(schema='TSL9-independent-register-image-ABI-actual-v1',passed=True,folder=ctx['prior']['relative'](root,folder),actual_build_replayed=True,metadata_only=False,reviewer_sha256=SHA(Path(__file__).read_bytes()),producer=dict(mode=r['mode'],receipt_sha256=SHA(receipt.read_bytes()),runner_sha256=r['runner_sha256'],manifest_sha256=r['manifest_sha256']),artifacts=artifacts,checks=checks,command_provenance=recipes,bounded_new_integration_controls=controls,producer_artifact_count=len(r['artifacts']),generated_build_artifacts_in_seal=False,target_execution=False,ISA_emulation=False,network=False,hardware_or_OTA_proof=False)


def replay(root,path,folder=None,firmware=None):
    r=json.loads(path.read_bytes());need(r['schema']=='TSL9-independent-register-image-ABI-actual-v1' and r['passed'],'independent actual ABI receipt schema/pass');need(r['reviewer_sha256']==SHA(Path(__file__).read_bytes()),'independent ABI source pin');folder=folder or root/r['folder'];need((folder/'verification.json').is_file(),'actual build absent: default check is metadata-only; actual replay needs the matching freshly built --folder');new=actual(root,folder,firmware);need(new==r,'fresh actual pre/post/scheduler/ELF/image/57recipe replay');return dict(passed=True,actual_build_replayed=True,image_sha256=new['checks']['image']['sha256'],bounded_integration_controls=5,generated_build_artifacts_in_seal=False)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',type=Path,default=ROOT);p.add_argument('--folder',type=Path);p.add_argument('--firmware',type=Path);p.add_argument('--report','--receipt',dest='report',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
    if a.replay:print(json.dumps(replay(root,a.replay.resolve(),a.folder.resolve() if a.folder else None,a.firmware),sort_keys=True));return
    if a.folder:
        need(a.report is not None,'explicit actual replay requires --report');r=actual(root,a.folder.resolve(),a.firmware);a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_bytes((json.dumps(r,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode());print(json.dumps(dict(passed=True,actual_build_replayed=True,report=str(a.report),sha256=SHA(a.report.read_bytes()),image_sha256=r['checks']['image']['sha256'])))
    else:print(json.dumps(metadata(root)[0],sort_keys=True))


if __name__=='__main__':main()
