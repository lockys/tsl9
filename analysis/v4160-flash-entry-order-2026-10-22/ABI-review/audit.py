"""Independent original/94B/100B static comparison and actual six-function review."""
from pathlib import Path
from collections import Counter
import argparse,hashlib,json,runpy,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SHA=lambda b:hashlib.sha256(b).hexdigest()
OLD_PINS={'review.py':'0dd857b44c9163d45668f224e5b772f3adfa08e832e58e1c5491b7fa5f1c0554','seal.json':'777443ff023089f092561f3bc36de2f710603dbeca651a43d4ed158b6b69a87d'}
CORE={'flash_native.c':'c2f85fd50a7def5ff4baf200415e9faa3f2a253dea51c6bc54ae6a139fef960b','flash_native.h':'b26fe2050e88708e7d18257841f5682ac49fcd4b402aac42ffc5aaae649dd7bd','native_io.h':'e0d58fdf1ae5ebc1f497a023443a4e6432f5cd75d987c691a2dcf68b3e64af7e'}


def need(v,why):
    if not v:raise ValueError(why)


def case(root,slug):
    return next(p for p in [root/'apk-analysis'/('tsl9-'+slug),root/'analysis'/slug] if p.is_dir())


def context(root,parser=None):
    oldcase=case(root,'v4160-flash-native-2026-10-22');old=oldcase/'compiler-review'
    for n,h in OLD_PINS.items():need(SHA((old/n).read_bytes())==h,'prior sealed native proof '+n)
    for member in json.loads((old/'seal.json').read_bytes())['members']:
        need(SHA((old/member['path']).read_bytes())==member['sha256'],'prior sealed review member '+member['path'])
    module=runpy.run_path(str(old/'review.py'))
    parser=parser or case(root,'v4160-reset-memory-2026-10-21')/'compiler-review/elf32.py'
    decode,ELF=module['pinned_helpers'](root,parser)
    new=runpy.run_path(str(HERE/'program.py'));need(SHA((HERE/'program.py').read_bytes())=='8896ae7d7ce7b59c2760099d493594cae43e49e177319cd6b78bf56b430eb73a','pure new checker identity')
    return oldcase,module,new,decode,ELF


def program_bytes(ELF,folder):
    path=folder/'program.o';e=ELF(path);s=next(s for s in e.symbols if s['name']=='tsl9_flash_program_18ef2')
    return e.function_bytes(s)


def gap_report(root,prior,firmware,parser=None):
    oldcase,old,new,decode,ELF=context(root,parser)
    raw=firmware.read_bytes();need(SHA(raw)=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','current original identity')
    original=raw[0x18ef2-0x8000:0x18f56-0x8000];original_rows=new['rows'](original,decode)
    report=[]
    for mode in ('c','cpp'):
        prior_report=json.loads((oldcase/'compiler-review'/('review-'+mode+'.json')).read_bytes())
        body=program_bytes(ELF,prior/mode);oldrows=old['native_contract']('program',body,[],decode)
        recorded=next(r for r in prior_report['functions'] if r['name']=='program')
        need(SHA((prior/mode/'program.o').read_bytes())==recorded['object_sha256'],'actual retained94B object')
        source_counts=Counter((r['op'],r['bytes']) for r in original_rows);native_counts=Counter((r['op'],r['bytes']) for r in oldrows)
        removed=source_counts-native_counts;added=native_counts-source_counts
        need(removed==Counter({('lui',4):2}) and added==Counter({('addi',2):1}),'exact width/opcode cause of6B gap')
        before=new['event_projection'](original_rows);after=new['event_projection'](oldrows)
        need(len(original_rows)==38 and len(oldrows)==37 and len(body)==94,'source/native instruction and byte totals')
        report.append(dict(mode=mode,source_bytes=100,source_instructions=38,prior_bytes=94,prior_instructions=37,removed=[dict(op='lui',bytes=4,count=2,source_PCs=[0x18f08,0x18f12])],added=[dict(op='addi',bytes=2,count=1,native_offset=0x20,meaning='LI A5,0')],byte_equation='100 - 2*4 + 2 = 94',instruction_equation='38 - 2 + 1 = 37',A0_ANDI_relocation_changes_byte_count=False,original_events=before,prior94_events=after,original_rows=original_rows,prior_rows=oldrows))
    return report


def original_roles(root,ELF):
    base=root/'experiments/tsl9-v4160-startup/build/image-fidelity-999d8125159a4d80bd6df9153f267002'
    e=ELF(base/'c/source-image-merged.o');receipt=json.loads((base/'verification.json').read_bytes())
    need(SHA(e.raw)=='646dbe43772be3858223dd6ec7f022c0252deba5879f3d3ab98da2940c9edb97','authoritative original carrier')
    need(SHA((base/'verification.json').read_bytes())=='2e6585594c1b02de058e2fbb5838f591a5915efed7bc461b9083e99a2e97b8bd','original layout receipt')
    section=e.byname['.text.tsl9v4160.direct_closure_18ef2']
    syms=[s for s in e.symbols if s['index']==section['index']]
    refs=[dict(source_PC=receipt['allocations'][r['owner']]['originalVA']+r['offset'],**r) for r in e.relocations if r['symbol']['index']==section['index']]
    locals=[s['value'] for s in syms if s['name'].startswith('.Ldirect_closure_')]
    need(locals==[16,26,40,56,82] and len(refs)==7,'actual five local roles/seven RELA')
    external=[r for r in refs if r['owner']!=section['name']]
    need([r['source_PC'] for r in external]==[0x9c34,0x197d8] and all(r['symbol']['value']==0 and r['addend']==0 and r['type']==17 for r in external),'two external entry references, no admitted external interior RELA')
    return dict(carrier_sha256=SHA(e.raw),source_section=section,symbols=syms,RELA=refs,known_interior_offsets=locals,known_external_interior_RELA=[],computed_indirect_incoming_excluded=False)


def inspect(root,folder,prior,firmware,source_dir,parser=None,carrier=True):
    oldcase,old,new,decode,ELF=context(root,parser);rows=[]
    need(SHA(firmware.read_bytes())=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','original identity')
    for n,h in CORE.items():need(SHA((source_dir/n).read_bytes())==h,'frozen100B native source '+n)
    producer=json.loads((folder/'probe.json').read_bytes());need({n:producer['source'][n] for n in CORE}==CORE,'actual producer native core snapshot')
    for name,(address,limit) in old['NAMES'].items():
        path=folder/(name+'.o');e=ELF(path);symbols=[s for s in e.symbols if s['info']&15==2 and s['index'] and s['size']]
        need(len(symbols)==1 and symbols[0]['name']=='tsl9_flash_'+name+'_'+format(address,'x'),'one actual native function')
        body=e.function_bytes(symbols[0]);alloc=[s for s in e.sections if s['flags']&2 and s['size']]
        need(len(alloc)==1 and alloc[0]['index']==symbols[0]['index'] and alloc[0]['flags']==6 and alloc[0]['size']==len(body),'one code allocation/no hidden data')
        text=(folder/(name+'.ll')).read_text(encoding='utf-8')
        if name=='program':
            need(not e.relocations,'program has no hidden dependencies');proof=new['check_program'](body,decode);ir=new['check_program_ir'](text)
        else:
            proof=dict(passed=True,rows=old['native_contract'](name,body,e.relocations,decode),normal_boundary_contract=True)
            ir=dict(passed=True,volatile_counts=old['ir_contract'](name,text))
        rows.append(dict(name=name,address=address,bytes=len(body),limit=limit,fits=len(body)<=limit,object_sha256=SHA(path.read_bytes()),IR_sha256=SHA((folder/(name+'.ll')).read_bytes()),proof=proof,IR=ir))
    linked=old['linked_review'](folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf',folder,decode,ELF,root)
    original=firmware.read_bytes()[0x18ef2-0x8000:0x18f56-0x8000];newbody=program_bytes(ELF,folder)
    original_rows=new['rows'](original,decode);newrows=new['rows'](newbody,decode)
    old_boundaries={r['offset'] for r in original_rows};new_boundaries={r['offset'] for r in newrows}
    need(old_boundaries-new_boundaries=={8} and new_boundaries-old_boundaries=={10},'exact boundary delta despite same size/count')
    gap=gap_report(root,prior,firmware,parser)
    metadata=original_roles(root,ELF) if carrier else json.loads((HERE/'original-roles.json').read_bytes())
    return dict(schema='ID2966-flash-entry-order-independent-ABI-review-v1',passed=True,build_root=folder.relative_to(root).as_posix(),source_pins=CORE,functions=rows,linked_component=linked,gap_100_to94=gap,original_program_roles=metadata,program_same100_byte_extent=True,program_same38_instruction_count=True,known5_interior_roles_retained=True,source_boundaries_lost=[8],new_boundaries_added=[10],program_byte_differences=[dict(offset=i,original=a,native=b) for i,(a,b) in enumerate(zip(original,newbody)) if a!=b],first_CTRL_scratch_original='A5',first_CTRL_scratch_native='A2',normal_boundary_contracts=True,all_sizes_fit=all(r['fits'] for r in rows),full_original_role_identity=False,full_scratch_GPR_prefix_equivalence=False,physical_fault_prefix_equivalence=False,pointwise_async_equivalence=False,full_image_integration=False,original_symbol_aliases_automatically_preserved=False,target_execution=False,emulation=False,network=False,hardware=False,new_BIN=False)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--build-root',type=Path,required=True);p.add_argument('--report',type=Path,required=True);p.add_argument('--project-root',type=Path,default=ROOT);p.add_argument('--prior-build',type=Path);p.add_argument('--firmware',type=Path);p.add_argument('--source-dir',type=Path);p.add_argument('--parser',type=Path);p.add_argument('--retained-roles',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args();root=a.project_root.resolve()
    prior=a.prior_build or root/'experiments/tsl9-v4160-flash-native/build/native-93a4dce3d2154291a48dea3a519f4b3f';fw=a.firmware or root/'exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin';src=a.source_dir or root/'experiments/tsl9-v4160-flash-entry-order/src'
    report=inspect(root,a.build_root.resolve(),prior,fw,src,a.parser,not a.retained_roles);payload=(json.dumps(report,indent=2)+'\n').encode('utf-8')
    if a.check:need(a.report.read_bytes()==payload,'exact readonly replay')
    else:need(a.report.resolve().is_relative_to(HERE),'own report only');a.report.write_bytes(payload);(HERE/'original-roles.json').write_bytes((json.dumps(report['original_program_roles'],indent=2)+'\n').encode('utf-8'))
    print(json.dumps(dict(passed=True,six_normal_contracts=True,all_sizes_fit=report['all_sizes_fit'],program_bytes=100,program_instructions=38,full_role_identity=False)))
