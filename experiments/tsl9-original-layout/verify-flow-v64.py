#!/usr/bin/env python3
"""Read-only static transfer arithmetic over measured non-loadable C/C++ layouts."""
import argparse,hashlib,json,runpy,sys
from collections import Counter
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def need(ok,label):
    if not ok:raise ValueError(label)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def enc(x):return (json.dumps(x,sort_keys=True,indent=2,ensure_ascii=True)+'\n').encode()
PINS={
  "build/record-copy-windows-flow-v3/c-flow.json": "ebd3f199c0b35fbfbcf54218bcfe2f940376d195f5f561aadc5515326fa24a25",
  "build-v58.py": "dfeae86d0185cd54c63713adcca0444697106b0ad39444c580bf6c4eed4bd952",
  "spec-v55.json": "d7b325040f0c687d13af7a042838a4f079d2147be989d2298d12f4aef0f763e8",
  "build/record-sequence-pool-v2/measurement.json": "1d0292bae0b31a956c912a6c155e99831fa66775decbaff1c8acdc09069323d1",
  "../tsl9-record-dispatch-tables/inspect-dispatch-tables.py": "94c76e6c02878e8d5a0cecd08e9fa759b21ee65637c93d1a563419f7c9af458e",
  "../tsl9-record-copy-windows/verify-v1.py": "0198fe4c058f34f7fca41007f593e413fd12dbf8a6d70d6e8bd8bb8f3490e894",
  "../tsl9-record-copy-windows/spec-v3.json": "38b9e7093d49f9cde8e7fcad241e2090c28b01ea39425134b700a0b224c68c3a",
  "../tsl9-record-sequence-pool/build-v1.py": "e8981e93a39b3e90aab989e0c8e6b9d6eaa1b5e9ce9d3e76c9d4c04451c3064d",
  "../tsl9-record-sequence-pool/spec-v2.json": "aa0d4cb4159ef58fc5f16080e9272abe056c5487b2ed935d567cf6510d73aaa6",
  "build-v59.py": "30aceee25a22d80cdee23832c46759e9cc49a24b5451f62297d0386d70c7efc0",
  "spec-v56.json": "4eb481a163e6b7869c3e4fd376c96f01e0f45bf6ee43b79d7d2115cace7c2800",
  "build/grid-read-windows-v2/measurement.json": "eda62d94fb1eee97297bd1055d47dbd4faa9ac4cbeacd0887ae6e2f49f80ef6d",
  "build/record-sequence-pool-flow-v2/c-flow.json": "4e8b7d9b5a705977e64a10ec3fec6d7f714fd51888c0ad0338cf4418769a785f",
  "../tsl9-grid-read-windows/audit-v1.py": "8ce952f3646b17acda12334b10e1984b1656c01513b64aa034bae5ed710b83e0",
  "../tsl9-grid-read-windows/spec-v2.json": "edd6646971da614579c5932b27beb51187e348afdf262f83558ca6682f6f4366",
  "build-v60.py": "f1066509196439737e402a2292349eb81f0fa1a11f45cfc62978f35dfd048f95",
  "spec-v57.json": "799c3eb105b0304ec4006da2a561d853e14ba8561e6ce94e047bb2a933e43183",
  "build/central-callbacks-v2/measurement.json": "7b322ce101146ef4636dcda38e5eac056be2aaaf1ac3acd56c340918bfae4680",
  "build/grid-read-windows-flow-v3/c-flow.json": "5ea5ae02241489bc9a0e4baa4b0813545017384a32612f96cc91f32262f037bc",
  "../tsl9-callback-prefix-data/audit-v1.py": "5d796e1656b8b27b081354861b2ac0f74a00530117098aef5c4e9b36780c6b9f",
  "../tsl9-callback-prefix-data/spec-v2.json": "f9bcc6007a27a55a006e19d45e89d28551be212a35979600e732b54a52bc7c59",
  "verify-flow-v60.py": "e427c1f97bf58023e1e457dbb4e5d2988046241c665b40cc47bee7ad083010c2",
  "build-v62.py": "51e7a666f630d52adccd54a1aae367320073b6c1494e9590e1392ea16b311f44",
  "spec-v59.json": "2528e915fcc573a4439c31560740b1a4336106252dd96e21b723292ecdc725c6",
  "../tsl9-central-callback-tables/spec-v2.json": "931a189b2f69162a2eb0b11cc09cd0ace6201339bcbc9ef82a00a256faea6f65",
  "../tsl9-central-callback-tables/integration-v2.json": "135c8d7c197003b87a809bf4cc568b38a0d56f24aeb38f9dab0697f998ea6e22",
  "../tsl9-central-callback-tables/integrate-v2.py": "167e313ed185294da4a9cd7c7e72c0e4a17e604b4e464b79c73abda83d9d81d0",
  "../tsl9-central-callback-tables/source-proof-v2.json": "cecee62ff4eec48b1993a479700b040c03e9343c2b736c1e060e1fe46c4109cf",
  "../tsl9-central-callback-tables/verify-source-v2.py": "a4e3aac58c3a48ae4501f1d2c0449836ea165a9dc6224e1ec8970e4354699f82",
  "../tsl9-central-callback-tables/build/source-proof-v2.json": "37ee062fbfd6d606f1ad06f1370658d49e62e354acb122d1068e6260592b8b65",
  "../tsl9-central-event-callbacks/evidence-v1.json": "270d1a6f9d0c0cad78b3566bd61bf375a125d626534a920420c9dfbce04acfb8",
  "../tsl9-central-event-callbacks/audit-v1.py": "85a48e6220c32a7ad33072921a371f142519b52cc2e60e68c5cad5313724d5a8",
  "../tsl9-central-callback-tables/audit-layout-v2.py": "64960e231f3d73593f4c9ea03bcea06077cae756b63f762bc22e2844943dfb10",
  "build-v63.py": "b8173a2edbbea55e0b057c779d893d90606d02b19f3646a60519c11427ed4bd5",
  "spec-v60.json": "3544afddf3f53646fe00274bbb35d69b102faf7fe4af9e8c9c82c43589086c26",
  "build/secondary-message-v1/measurement.json": "ab8dc999d0673bb98232bdba49c1d5a7ec2981c747920ff8353cebf65856ba12",
  "verify-flow-v62.py": "85e449e4c767c9b632a438fe8043cce89ca9720f3d0b125e63173219705bd976",
  "compare-diagnostic-v1.py": "0d21f34dfa482b1bb9dde0b074bf0456e8bbbd1d509bda2795c287eb7e746965",
  "../tsl9-secondary-message-data/build-v1.py": "13e76c41ec7fab0b0befbdefe6d03a2121f092f83111e89d3fc92c9e4b8ccaa6",
  "../tsl9-secondary-message-data/spec-v1.json": "b9b0f3bacd36d3da62c316d57c56c9bf91c2af77011c48cd929e99ea7d667c46",
  "../tsl9-secondary-message-data/integrate-v1.py": "bef2571c32e2950e0e23577f421c6c8f976f2ae2f0a377e23eb7677f00660df2",
  "../tsl9-secondary-message-data/integration-v1.json": "b9ae22d1b64edff9557190dc85d3261c8f8e0c2fb277a2589647750ace087bd4",
  "../tsl9-secondary-message-dispatch/spec-v1.json": "5975119ee5745e89e384e1d566a6b23b80d10df95bb85bb8d81ee754cdcfb0ce",
  "../tsl9-secondary-message-dispatch/evidence-v1.json": "0a6be723f03c0fb261bd9244ac34d55195b1e4df5adfc3bdbbfd60cd7ede23d1",
  "../tsl9-secondary-message-dispatch/audit-v1.py": "eca934ea41d00d2d56ff83f7e1fc33ef997843bc560847055db69a42b5a3cd42",
  "build-v64.py": "431d9ba575457cb42d001c8d42852963f37f67a321f37ab2e7665efa25f4e754",
  "spec-v61.json": "2a8c9e75de0700791ff2d46a82f8fa23f357a67df55016a87d07e8c1b928ed9b",
  "build/secondary-message-v2/measurement.json": "880b06945c764f65808a74539581e690b781ea978621a7ecf61a940fb78eb210",
  "verify-flow-v63.py": "5effc5f32c76e918851d23ca0da16745c652f993e677cbbe25440175a9033c02",
  "../tsl9-secondary-message-data/verify-source-v2.py": "7471611bf8674c8af52aa10fddb9d9d5727a125fe502ea37e7aa258c4ccb9d6a",
  "../tsl9-secondary-message-data/source-proof-v2.json": "75088e071ddbd0b4a3d92853b6ab0c972a987dd5a73d15f93529fb053441beb4",
  "../tsl9-secondary-message-data/build/source-proof-v2.json": "86be0c4ee7ec9b883dbdcd11dafeca0479cff1a0e81fd1cc9b598dabdeaa8564",
  "../tsl9-secondary-message-data/integrate-v2.py": "9daf27857e6751b1baadb354a61b1a7e7b8fd95243f8a68e5183dfdad0e3d261",
  "../tsl9-secondary-message-data/integration-v2.json": "c0b7e529a255f251e5ca6ac4f68cffc99ae3be7e7b9d14a410ad176f50676e26",
  "../tsl9-secondary-message-data/source-extension-v2.json": "c8b1719872a408946731f5883d921e90486ebf36a03d10695973e7107c173509"
}
ELF_SHA='2225e889f3ada53bff9cc9b832fd9abbdeb7da282abd18be83b4658c9842f3ba'
def analyze(mode,b):
    folder=HERE/'build/secondary-message-v2'/mode
    path=folder/'NONLOADABLE-ORIGINAL-LAYOUT.elf'
    need(digest(path)==ELF_SHA,'Actual original-layout ELF identity')
    e=b['E'](b['source'](mode));plan=b['derive'](e);b['validate_original'](e,plan)
    b['audit_split'](folder/'split-C-payload.o',e,plan)
    linked=b['E'](path);result=b['audit_link'](path,e,plan)
    independent=runpy.run_path(str(HERE/'compare-diagnostic-v1.py'),run_name='independent_diagnostic_decoder')['audit'](path,linked)
    need(result['original_coordinate_bytes_equal']==72610,'All genuine original byte carriers')
    need(result['curated_integration'] and result['source_C_H_files']==158 and result['source_comparisons']==264 and result['source_objects']==528,'Actual complete curated source provenance')
    insns={};owners_by_name={o['name']:o for o in plan['owners']}
    for owner in plan['owners']:
        if owner['info']!=18:continue
        raw=linked.data(owner['section'])[owner['section_offset']:owner['section_offset']+owner['bytes']]
        at=0
        while at<len(raw):
            width=4 if raw[at]&3==3 else 2
            need(at+width<=len(raw),'Whole selected original instruction')
            pc=owner['original_PC']+at
            need(pc not in insns,'Unique actual instruction owner')
            insns[pc]=dict(PC=pc,width=width,raw=raw[at:at+width],owner=owner['name'])
            at+=width
    need(len(insns)==23314,'All23314 instructions')
    imports={i['original_reference_PC']:i for i in plan['imports']}
    direct=[];indirect=[];traps=[];privileged_returns=[];ordinary_gaps=[];call_returns=[];counts=Counter()
    actual_control={(r['offset'],r['type']):r for r in linked.relocations if r['type'] in (16,17,44,45)}
    need(len(actual_control)==4559,'All4559 typed direct-control relocations')
    for pc,o in sorted(insns.items()):
        raw=o['raw'];v=int.from_bytes(raw,'little');w=o['width'];decoded=b['B']['decode_control'](raw,pc)
        follow=True;call=False
        if decoded:
            kind,target=decoded
            if (pc,kind)in actual_control:
                reference_kind='applied_native_relocation'
                r=actual_control[(pc,kind)];sym=linked.symbols[r['symbol']]
                need(sym['value']+r['addend']==target,'Applied transfer target equals actual linked symbolic address')
            else:
                reference_kind='unchanged_intra_owner_immediate'
                owner=owners_by_name[o['owner']]
                need(target in insns and insns[target]['owner']==o['owner'],'Unrelocated transfer stays inside the same genuine compiled body')
                offset=owner['source_offset']+pc-owner['original_PC']
                need(e.data(e.sections[owner['source_section']])[offset:offset+w]==raw,'Intra-owner immediate bytes unchanged from measured compiled source')
            if target in insns:target_role='measured_instruction'
            else:
                need(target in imports,'Every selected direct target is a real mapped instruction or an explicitly unimplemented provider reference')
                target_role='unimplemented_reference_only'
            if kind==17:
                rd=(v>>7)&31;call=rd!=0;follow=call
                role='jal_with_link' if call else 'jump'
            elif kind==45:
                call=((v>>13)&7)==1;follow=call
                role='compressed_call' if call else 'compressed_jump'
            else:role='conditional_branch'
            counts[role]+=1
            direct.append(dict(PC=pc,owner=o['owner'],kind=kind,target_PC=target,target_role=target_role,role=role,reference_kind=reference_kind,
                target_owner=insns.get(target,{}).get('owner'),source_provider=imports.get(target,{}).get('source_symbol')))
        elif w==4 and v&127==0x67:
            need((v>>12)&7==0,'Ordinary JALR encoding')
            rd=(v>>7)&31;rs1=(v>>15)&31;imm=v>>20
            if imm&0x800:imm-=0x1000
            call=rd!=0;follow=call
            indirect.append(dict(PC=pc,owner=o['owner'],rd=rd,rs1=rs1,immediate=imm,encoding='JALR',runtime_target_proved=False))
        elif w==2 and (v&0xf07f)in (0x8002,0x9002) and (v>>7)&31:
            rd=1 if v&0x1000 else 0;call=rd!=0;follow=call
            indirect.append(dict(PC=pc,owner=o['owner'],rd=rd,rs1=(v>>7)&31,immediate=0,encoding='C.JALR' if call else 'C.JR',runtime_target_proved=False))
        elif (w==4 and v in (0x73,0x100073)) or (w==2 and v==0x9002):
            follow=False
            traps.append(dict(PC=pc,owner=o['owner'],encoding='ECALL' if v==0x73 else 'EBREAK',next_sequential_PC=pc+w,
                next_sequential_role='measured_instruction' if pc+w in insns else 'outside_measured_code',
                trap_handler_and_resume_target_proved=False))
        elif w==4 and v in (0x30200073,0x10200073,0x7b200073):
            follow=False
            privileged_returns.append(dict(PC=pc,owner=o['owner'],encoding={0x30200073:'MRET',0x10200073:'SRET',0x7b200073:'DRET'}[v],
                runtime_return_target_proved=False))
        if follow:
            counts['ordinary_next_positions']+=1
            if pc+w not in insns:ordinary_gaps.append(dict(PC=pc,next_PC=pc+w,owner=o['owner']))
        if call:
            call_returns.append(dict(PC=pc,return_PC=pc+w,position_owned=pc+w in insns))
    need({(d['PC'],d['kind']) for d in direct if d['reference_kind']=='applied_native_relocation'}==set(actual_control),'One-to-one coverage of all3388 applied native direct-control relocations')
    need(len(direct)==4576 and sum(d['reference_kind']=='unchanged_intra_owner_immediate' for d in direct)==17,'All4576 immediate transfers including17 unchanged local-body branches')
    need(not ordinary_gaps and all(r['position_owned'] for r in call_returns),'All ordinary sequential and call-return positions have real compiled instructions')
    boundary=[t for t in traps if t['PC']==0x8034]
    need(len(boundary)==1 and boundary[0]['encoding']=='EBREAK' and boundary[0]['next_sequential_PC']==0x8038,'Original breakpoint/vector boundary retained')
    need(any(o['info']==17 and o['original_PC']==0x8038 and o['bytes']==328 for o in plan['owners']),'Actual vector data starts at8038')
    source_undefined=[s for s in e.symbols if s['info']>>4 and s['section']==0]
    need(len(source_undefined)==6,'Six genuine compiler-undefined providers remain')
    ranks=Counter(d['source_provider'] for d in direct if d['source_provider'])
    literal_only=sorted(s['name']for s in source_undefined if s['name']not in ranks)
    need(len(literal_only)==4,'Four genuine literal-only dependencies remain unprovided')
    literal_names=set(literal_only)
    actual_HI_targets={e.symbols[r['symbol']]['name']for r in e.relocations if r['type']==23 and not e.symbols[r['symbol']]['section']}
    # Preserve source address roles and separately classify dependencies which now
    # also have a direct control reference. Do not reinterpret opaque payload bytes.
    types={'tsl9_settings_default_data_1a69c':'opaque-data-address'}
    for rel in b['K']['span_specs']:
        specification=json.loads((ROOT/rel).read_bytes())
        for pair in specification.get('PC_relative_pairs',[]):
            name=pair['target']
            if name not in actual_HI_targets:continue
            kind=pair.get('reference_kind','unclassified-static-address')
            need(name not in types or types[name]==kind,'Consistent original address role')
            types[name]=kind
    need(set(types)==actual_HI_targets and literal_names<=actual_HI_targets,'Every address use has a real HI relocation and source provenance')
    mixed=sorted(actual_HI_targets-literal_names)
    need(not mixed,'No unprovided mixed direct/address dependency remains after genuine FE08 reconstruction')
    need(all(n in ranks for n in mixed),'The mixed reference has actual direct control edges')
    need(Counter(types[n]for n in literal_names)==Counter({'opaque-data-address':1,'opaque-static-data-address':2,'unbounded-static-data-address':1}),'Four remaining literal dependencies retain the third-grid/default/input/loop gaps;callback tables now have real providers')
    previous_roles={v['source_symbol']:v['reference_kind']for v in json.loads((HERE/'build/grid-read-windows-flow-v3/c-flow.json').read_bytes())['literal_only_provider_roles']}
    resolved_prefix_names={v['name']for v in json.loads((ROOT/'experiments/tsl9-callback-prefix-data/spec-v2.json').read_bytes())['data_regions']}
    resolved_callback_names={'tsl9_registered_callbacks_static_data_1a668','tsl9_registered_callbacks_static_data_1a674'}
    need(set(previous_roles)==literal_names|resolved_prefix_names|resolved_callback_names and all(previous_roles[name]==types[name]for name in literal_names),'Every remaining original role retained;only actual positive callback-table providers additionally resolve')
    literal_roles=[dict(source_symbol=n,original_reference_PC=int(n.rsplit('_',1)[1],16),reference_kind=types[n],body_or_data_provided=False)for n in literal_only]
    mixed_roles=[dict(source_symbol=n,original_reference_PC=int(n.rsplit('_',1)[1],16),original_address_reference_kind=types[n],also_has_direct_control_reference=True,body_provided=False)for n in mixed]
    specification=json.loads((ROOT/'experiments/tsl9-action-dispatch/spec-v1.json').read_bytes())
    ep=ROOT/specification['reference_candidate']
    need(digest(ep)==specification['reference_candidate_sha256'],'Pinned raw table/guard evidence')
    evidence=json.loads(ep.read_bytes())
    original_ops={o['addr']:o for f in evidence['selected_functions']for o in f['operations']}
    expected_guard={0x15630:'andi s2, s2, 255',0x15634:'li a5, 252',0x15638:'bltu a5, s2, 0x1578c',0x1563c:'auipc a4, 0x5',0x15640:'addi a4, a4, 184',0x15644:'slli s2, s2, 0x2',0x15646:'add s2, s2, a4',0x15648:'lw a5, 0(s2)',0x1564c:'add a5, a5, a4',0x1564e:'jr a5'}
    for pc,opcode in expected_guard.items():
        need(original_ops[pc]['opcode']==opcode and bytes.fromhex(original_ops[pc]['bytes'])==insns[pc]['raw'],'Actual guard/index/jump instruction identity')
    table=specification['literal_data']
    owner=next(o for o in plan['owners']if o['name']==table['name'])
    need(owner['info']==17 and owner['original_PC']==0x1a6f4 and owner['bytes']==1012,'Actual named table data owner')
    raw=linked.data(owner['section'])[owner['section_offset']:owner['section_offset']+1012]
    need(hashlib.sha256(raw).hexdigest()==table['original_sha256'],'Original table bytes in actual diagnostic ELF')
    targets=[0x1a6f4+int.from_bytes(raw[i:i+4],'little',signed=True)for i in range(0,1012,4)]
    need(targets==table['target_PCs'] and len(set(targets))==174 and all(t in insns and 0x155d0<=t<0x163ac for t in targets),'All253 entries and174 genuine mapped instruction candidates')
    jr=[x for x in indirect if x['PC']==0x1564e]
    need(len(jr)==1 and jr[0]['rs1']==15 and jr[0]['rd']==0,'Actual recorded register-indirect dispatch')
    table_flow=dict(jump_PC=0x1564e,guard_PC=0x15638,table_PC=0x1a6f4,table_bytes=1012,entries=253,unique_targets=174,target_PCs=targets,
        condition='On guard fallthrough,unsigned S2<=252 after ANDI255; no opaque call intervenes before indexed load/jump. Relation to pre-call A0 depends on the unproved private ABI.',
        guard_and_table_original_bytes_proved=True,runtime_index_or_target_observed=False,asynchronous_ABI_interference_excluded=False)
    phase_spec=json.loads((ROOT/'experiments/tsl9-action-primitives/spec-v1.json').read_bytes())
    phase_ep=ROOT/phase_spec['reference_candidate']
    need(digest(phase_ep)==phase_spec['reference_candidate_sha256'],'Pinned original phase evidence')
    phase_evidence=json.loads(phase_ep.read_bytes())
    phase_ops={o['addr']:o for f in phase_evidence['selected_functions']for o in f['operations']}
    phase_guard={0x18062:'lbu a4, -1848(a4)',0x18066:'li a2, 5',0x18072:'bltu a2, a4, 0x1809e',0x18076:'auipc a2, 0x3',0x1807a:'addi a2, a2, -1394',0x1807e:'slli a4, a4, 0x2',0x18080:'add a4, a4, a2',0x18082:'lw a4, 0(a4)',0x18084:'andi a3, a5, 1',0x18088:'li a0, 0',0x1808a:'add a4, a4, a2',0x1808c:'andi a5, a5, 2',0x1808e:'jr a4'}
    for pc,opcode in phase_guard.items():
        need(phase_ops[pc]['opcode']==opcode and bytes.fromhex(phase_ops[pc]['bytes'])==insns[pc]['raw'],'Actual byte-loaded phase guard/index/jump')
    phase_table=phase_spec['literal_data'];po=next(o for o in plan['owners']if o['name']==phase_table['name'])
    need(po['info']==17 and po['original_PC']==0x1ab04 and po['bytes']==24,'Actual named six-entry table owner')
    pr=linked.data(po['section'])[po['section_offset']:po['section_offset']+24]
    need(hashlib.sha256(pr).hexdigest()==phase_table['original_sha256'],'Actual original phase table bytes')
    phase_targets=[0x1ab04+int.from_bytes(pr[i:i+4],'little',signed=True)for i in range(0,24,4)]
    need(phase_targets==phase_table['target_PCs'] and len(set(phase_targets))==4 and all(t in insns and 0x1805a<=t<0x180f0 for t in phase_targets),'All six entries and four measured phase targets')
    pjr=[x for x in indirect if x['PC']==0x1808e]
    need(len(pjr)==1 and pjr[0]['rs1']==14 and pjr[0]['rd']==0,'Actual phase register-indirect transfer')
    phase_flow=dict(jump_PC=0x1808e,guard_PC=0x18072,table_PC=0x1ab04,table_bytes=24,entries=6,unique_targets=4,target_PCs=phase_targets,
        condition='On guard fallthrough,the byte-loaded phase is<=5; no opaque call precedes the indexed jump. Out-of-range branch keeps the explicitly zero mask.',
        guard_and_table_original_bytes_proved=True,runtime_index_or_target_observed=False,asynchronous_interference_excluded=False)
    notification_spec=json.loads((ROOT/'experiments/tsl9-selector-notifications/spec-v1.json').read_bytes())
    notification_path=ROOT/notification_spec['reference_candidate']
    need(digest(notification_path)==notification_spec['reference_candidate_sha256'],'Pinned notification guard evidence')
    notification_evidence=json.loads(notification_path.read_bytes())
    notification_ops={o['addr']:o for f in notification_evidence['selected_functions']for o in f['operations']}
    notification_flow=[]
    expected=[(0x1a13c,5,0xe220,0xe222,0xe226,0xe232,0xe244,'a2','a5',0xebaa),
        (0x1a150,30,0xe268,0xe26a,0xe26e,0xe27a,0xe27e,'a5','a4',0xe288),
        (0x1a1c8,83,0xe80e,0xe812,0xe816,0xe822,0xe826,'s0','a5',0xe72e),
        (0x1a314,10,0xe95e,0xe960,0xe964,0xe970,0xe974,'s1','a5',0xe99a),
        (0x1a33c,61,0xea54,0xea58,0xea5c,0xea68,0xea6c,'a5','a4',0xe99a)]
    for d,values in zip(notification_spec['literal_data'],expected):
        start,n,limit,guard,base,load,jump,index,limitreg,escape=values
        need((d['start'],d['entries'],d['limit_PC'],d['guard_PC'],d['base_PC'],d['load_PC'],d['jump_PC'])==values[:7],'Exact five table extents and dispatch positions')
        no=next(o for o in plan['owners']if o['name']==d['name'])
        need(no['info']==17 and no['original_PC']==start and no['bytes']==n*4 and no['alignment']==4,'Actual aligned full DATA table owner')
        nr=linked.data(no['section'])[no['section_offset']:no['section_offset']+no['bytes']]
        need(hashlib.sha256(nr).hexdigest()==d['original_sha256'] and nr.hex()==d['raw_hex'],'Every actual compiled notification table byte')
        nt=[(start+int.from_bytes(nr[i:i+4],'little',signed=True))&0xffffffff for i in range(0,len(nr),4)]
        need(nt==d['target_PCs'] and all(t in insns and 0xe220<=t<0xebac for t in nt),'All189 original table entries are actual mapped instructions')
        expected_ops={limit:f'li {limitreg}, {n-1}',guard:f'bltu {limitreg}, {index}, {hex(escape)}',
            base+8:f'slli {index}, {index}, 0x2',base+10:f'add {index}, {index}, a4',
            load:f'lw a5, 0({index})',jump:'jr a5'}
        for pc,opcode in expected_ops.items():need(notification_ops[pc]['opcode']==opcode,'Exact original unsigned guard/index/load/jump register chain')
        chain=[o for pc,o in notification_ops.items()if limit<=pc<=jump]
        need(all(bytes.fromhex(o['bytes'])==insns[o['addr']]['raw'] for o in chain),'Every guard-to-dispatch compiled instruction equals original')
        need(not any(o['type']in ('call','ucall')for o in chain),'No opaque call intervenes before table dispatch')
        address=next(q for q in notification_spec['PC_relative_pairs']if q['PC']==base)
        need(address['target_PC']==start and address['data_contents_provided'],'Actual typed native address points to real table data')
        jr=[q for q in indirect if q['PC']==jump]
        need(len(jr)==1 and jr[0]['rs1']==15 and jr[0]['rd']==0,'Actual compiled register-indirect dispatch')
        notification_flow.append(dict(table_PC=start,entries=n,table_bytes=n*4,guard_PC=guard,jump_PC=jump,target_PCs=nt,
            index_expression=d['index_expression'],guard_fallthrough_maximum=n-1,compiled_guard_and_table_bytes_proved=True,
            no_intervening_opaque_call=True,runtime_index_or_target_observed=False,asynchronous_ABI_interference_excluded=False))
    need(len(notification_flow)==5 and sum(x['entries']for x in notification_flow)==189,'All five guarded notification tables')
    record_tables,record_lookup=runpy.run_path(str(ROOT/'experiments/tsl9-record-dispatch-tables/inspect-dispatch-tables.py'),run_name='positive_static_library')['analyze'](b,linked,plan,insns)
    for table in record_tables:
        jumps=[v for v in indirect if v['PC']==table['jump_PC']]
        need(len(jumps)==1 and jumps[0]['rs1']==15 and jumps[0]['rd']==0,'Each new guarded table ends in the actual A5 indirect dispatch')
    copy_module=runpy.run_path(str(ROOT/'experiments/tsl9-record-copy-windows/verify-v1.py'),run_name='copy_source_static_library')
    copy_facts=copy_module['static_audit']()
    copy_evidence=json.loads((ROOT/copy_module['S']['evidence']).read_bytes())
    source_globals=b['global_map'](e)
    linked_globals=b['global_map'](linked)
    firmware=(ROOT/b['K']['firmware']).read_bytes()
    for function in copy_evidence['functions']:
        for operation in function['operations']:
            need(operation['addr']in insns and insns[operation['addr']]['raw']==bytes.fromhex(operation['bytes']),'Every copy-bound instruction is the actual restored original instruction')
    copy_sources=[]
    for data in copy_evidence['objects']:
        source=source_globals[data['name']];actual=linked_globals[data['name']]
        owner=owners_by_name[data['name']]
        need(source['info']==actual['info']==17 and source['size']==actual['size']==data['bytes']and source['section']not in(0,0xfff1)and actual['section']not in(0,0xfff1),'Each copy source binds a genuine whole DATA object')
        need(actual['value']==owner['original_PC']==data['start']and owner['bytes']==data['bytes'],'Each real source OBJECT is placed at its original coordinate')
        section=linked.sections[actual['section']];offset=actual['value']-section['address']
        need(linked.data(section)[offset:offset+data['bytes']]==firmware[data['start']-0x8000:data['end']-0x8000],'Every actual copy-source byte is original-equal')
        pair={}
        for pc,kind in [(data['hi_PC'],23),(data['lo_PC'],24)]:
            hits=[]
            for rel in e.relocations:
                if rel['type']!=kind:continue
                parent,within=b['lookup'](plan,rel['section'],rel['offset'])
                if parent['original_PC']+within==pc:hits.append(rel)
            need(len(hits)==1 and hits[0]['addend']==0,'Exactly one native HI/LO record at each original source operand')
            pair[kind]=hits[0]
        need(e.symbols[pair[23]['symbol']]['name']==data['name']and b['original_value'](e,plan,e.symbols[pair[24]['symbol']])==data['hi_PC'],'Actual HI points to the real DATA provider and LO to its original HI anchor')
        calls=[v for v in direct if v['PC']==data['copy_call_PC']]
        need(len(calls)==1 and calls[0]['target_PC']==0x19bf0 and calls[0]['target_role']=='measured_instruction'and calls[0]['kind']==17,'Each original copy call reaches the measured complete software-copy body')
        copy_sources.append(dict(name=data['name'],source_start=data['start'],source_end=data['end'],bytes=data['bytes'],copy_call_PC=data['copy_call_PC'],HI_PC=data['hi_PC'],LO_PC=data['lo_PC'],real_DATA_owner=True,source_dependency_resolved=True,bytes_original_equal=True,original_declared_object_extent_proved=False))
    need(len(copy_sources)==2 and sum(d['bytes']for d in copy_sources)==200,'Exactly the two bounded original copy-source windows')
    need(not any(o['original_PC']<0x19d68 and 0x19d66<o['original_PC']+o['bytes']for o in plan['owners']),'The original two-byte gap remains unprovided and uncounted')
    sequence=runpy.run_path(str(ROOT/'experiments/tsl9-record-sequence-pool/build-v1.py'),run_name='sequence_literal_source_library')
    sequence_static=sequence['static_audit']()
    sequence_spec=json.loads((ROOT/'experiments/tsl9-record-sequence-pool/spec-v2.json').read_bytes())
    pool_spec=sequence_spec['owner'];pool_source=source_globals[pool_spec['name']];pool_linked=linked_globals[pool_spec['name']]
    need(pool_source['info']==pool_linked['info']==17 and pool_source['size']==pool_linked['size']==178 and pool_linked['value']==0x1a430,'One real178-byte original-coordinate DATA pool')
    pool_section=linked.sections[pool_linked['section']];pool_offset=pool_linked['value']-pool_section['address']
    need(linked.data(pool_section)[pool_offset:pool_offset+178]==firmware[0x1a430-0x8000:0x1a4e2-0x8000],'Every actual pool byte is original-equal')
    need(len(plan['real_DATA_label_bindings'])==6,'The retained boot/sequence labels and two new grid labels remain genuine')
    for binding in plan['real_DATA_label_bindings']:
        sym=linked_globals[binding['name']];owner=linked_globals[binding['owner']]
        need(sym['info']==17 and sym['size']==0 and sym['section']==owner['section']and owner['info']==17 and owner['size']==binding['owner_bytes']and sym['value']==owner['value']+binding['owner_offset']==binding['original_PC'],'Every zero-allocation DATA label is backed by actual original-coordinate storage')
    sequence_bindings=[]
    sequence_pairs={0x1a430:(0xefac,0xefb0),0x1a454:(0xefee,0xeff2),0x1a478:(0xeff8,0xeffc)}
    for label in sequence_spec['labels']:
        sym=source_globals[label['name']];actual=linked_globals[label['name']]
        owner,within=b['lookup'](plan,sym['section'],sym['value'])
        need(owner['name']==pool_spec['name']and within==label['pool_offset']and sym['info']==actual['info']==17 and sym['size']==actual['size']==0,'Each source reference resolves a genuine interior OBJECT label,not an ABS or duplicate owner')
        need(actual['section']==pool_linked['section']and actual['value']==label['original_PC']==pool_linked['value']+label['pool_offset'],'Original data-label coordinate retained')
        hi,lo=sequence_pairs[label['original_PC']];pair={}
        for pc,kind in [(hi,23),(lo,24)]:
            hits=[]
            for rel in e.relocations:
                if rel['type']!=kind:continue
                region,offset=b['lookup'](plan,rel['section'],rel['offset'])
                if region['original_PC']+offset==pc:hits.append(rel)
            need(len(hits)==1 and hits[0]['addend']==0,'Unique actual HI/LO relocation at the original source operand');pair[kind]=hits[0]
        need(e.symbols[pair[23]['symbol']]['name']==label['name']and b['original_value'](e,plan,e.symbols[pair[24]['symbol']])==hi,'The native HI binds the real interior DATA label and LO retains its exact code anchor')
        sequence_bindings.append(dict(name=label['name'],pool_owner=pool_spec['name'],pool_offset=label['pool_offset'],original_PC=actual['value'],actual_symbol_info=actual['info'],actual_symbol_size=actual['size'],actual_section=pool_section['name'],allocated_additional_bytes=0,HI_PC=hi,LO_PC=lo,source_dependency_resolved=True))
    need(len(sequence_bindings)==3,'Exactly three real sequence source providers resolved')
    literal_envelopes=[]
    for binding in sequence_bindings:
        for limit in (17,53):
            start=binding['original_PC'];end=start+2*limit
            need(pool_linked['value']<=start<end<=pool_linked['value']+pool_linked['size'],'Every selected-literal pointer/limit combination has actual pool backing')
            literal_envelopes.append(dict(pointer=start,limit=limit,start=start,end=end,bytes=2*limit,scope='conditional selected literal values only'))
    need(len(literal_envelopes)==6 and sequence_static['global_runtime_pointer_or_limit_bound_proved']is False,'Six literal combinations do not imply a global runtime bound')
    grid=runpy.run_path(str(ROOT/'experiments/tsl9-grid-read-windows/audit-v1.py'),run_name='grid_selected_read_library')['audit']()
    grid_spec=json.loads((ROOT/'experiments/tsl9-grid-read-windows/spec-v2.json').read_bytes())
    grid_owner=grid_spec['owner'];grid_source=source_globals[grid_owner['name']];grid_linked=linked_globals[grid_owner['name']]
    need(grid_source['info']==grid_linked['info']==17 and grid_source['size']==grid_linked['size']==432 and grid_linked['value']==0x19ed8,'One genuine432-byte grid-window DATA pool')
    grid_section=linked.sections[grid_linked['section']];grid_offset=grid_linked['value']-grid_section['address']
    need(linked.data(grid_section)[grid_offset:grid_offset+432]==firmware[0x19ed8-0x8000:0x1a088-0x8000],'Every actual grid pool byte matches the original BIN')
    grid_bindings=[];grid_pairs={0x19ed8:(0xcb26,0xcb2a),0x1a018:(0xcc4a,0xcc4e)}
    for label in grid_spec['labels']:
        sym=source_globals[label['name']];actual=linked_globals[label['name']];owner,within=b['lookup'](plan,sym['section'],sym['value'])
        need(owner['name']==grid_owner['name']and within==label['pool_offset']and sym['info']==actual['info']==17 and sym['size']==actual['size']==0,'Genuine zero-allocation interior OBJECT with actual pool backing')
        need(actual['section']==grid_linked['section']and actual['value']==label['original_PC']==grid_linked['value']+label['pool_offset'],'Every grid label retains its original coordinate')
        hi,lo=grid_pairs[label['original_PC']];pair={}
        for pc,kind in [(hi,23),(lo,24)]:
            hits=[]
            for rel in e.relocations:
                if rel['type']!=kind:continue
                region,offset=b['lookup'](plan,rel['section'],rel['offset'])
                if region['original_PC']+offset==pc:hits.append(rel)
            need(len(hits)==1 and hits[0]['addend']==0,'Unique actual grid HI/LO source relocation');pair[kind]=hits[0]
        need(e.symbols[pair[23]['symbol']]['name']==label['name']and b['original_value'](e,plan,e.symbols[pair[24]['symbol']])==hi,'Actual HI names the backed grid DATA label;LO retains the original local HI anchor')
        grid_bindings.append(dict(name=label['name'],pool_owner=grid_owner['name'],pool_offset=label['pool_offset'],original_PC=actual['value'],actual_symbol_info=actual['info'],actual_symbol_size=actual['size'],actual_section=grid_section['name'],allocated_additional_bytes=0,HI_PC=hi,LO_PC=lo,source_dependency_resolved=True))
    need(len(grid_bindings)==2 and grid['selected_direct_guard_bypasses']==0,'Two bounded DATA source references and no selected direct guard bypass')
    grid_envelopes=[]
    for key in ('first_lookup','second_lookup'):
        window=grid[key];need(grid_linked['value']<=window['base']<window['end']<=grid_linked['value']+grid_linked['size'],'Every conservative selected read window has actual original-coordinate backing')
        grid_envelopes.append(dict(base=window['base'],end=window['end'],maximum_offset=window['maximum_offset'],scope='selected guarded paths;not a global indirect-entry/async bound'))
    unresolved_third='tsl9_record_field_transitions_static_data_1a078'
    need(unresolved_third in literal_names and types[unresolved_third]=='unbounded-static-data-address'and not grid['third_lookup']['mask_clamps_actual_index']and not grid['third_lookup']['source_DATA_provided'],'Third row remains unbounded and its provider unimplemented')
    prefix=runpy.run_path(str(ROOT/'experiments/tsl9-callback-prefix-data/audit-v1.py'),run_name='prefix_original_argument_library')['audit']()
    prefix_spec=json.loads((ROOT/'experiments/tsl9-callback-prefix-data/spec-v2.json').read_bytes())
    prefix_bindings=[]
    for d in prefix_spec['data_regions']:
        sym=source_globals[d['name']];actual=linked_globals[d['name']];owner,within=b['lookup'](plan,sym['section'],sym['value'])
        need(owner['name']==d['name']and within==0 and sym['info']==actual['info']==17 and sym['size']==actual['size']==d['bytes'],'Every fixed argument has actual positive-size readonly OBJECT storage')
        need(actual['value']==d['start']and actual['value']+actual['size']==d['end'],'Every original source argument coordinate retained')
        section=linked.sections[actual['section']];offset=actual['value']-section['address'];raw=linked.data(section)[offset:offset+d['bytes']]
        need(raw==firmware[d['start']-0x8000:d['end']-0x8000],'Every actual linked DATA byte equals the original argument window')
        pair={}
        for pc,kind in [(d['HI_PC'],23),(d['LO_PC'],24)]:
            hits=[]
            for rel in e.relocations:
                if rel['type']!=kind:continue
                source_owner,source_offset=b['lookup'](plan,rel['section'],rel['offset'])
                if source_owner['original_PC']+source_offset==pc:hits.append(rel)
            need(len(hits)==1 and hits[0]['addend']==0,'Unique original fixed-argument HI/LO reference');pair[kind]=hits[0]
        need(e.symbols[pair[23]['symbol']]['name']==d['name']and b['original_value'](e,plan,e.symbols[pair[24]['symbol']])==d['HI_PC'],'HI names the actual DATA owner;LO preserves its exact original code anchor')
        owners=[s for s in linked.sections if s['flags']&4 and s['address']<=d['length_PC']and d['length_PC']+2<=s['address']+s['size']]
        need(len(owners)==1,'Original A2 length instruction has actual CODE backing');code=owners[0];at=d['length_PC']-code['address'];word=int.from_bytes(linked.data(code)[at:at+2],'little');imm=(((word>>12)&1)<<5)|((word>>2)&31);imm=imm-64 if imm&32 else imm
        need(word&0xe003==0x4001 and(word>>7)&31==12 and imm==d['bytes'],'Actual linked C.LI A2 length remains the measured window size')
        prefix_bindings.append(dict(name=d['name'],original_PC=actual['value'],bytes=actual['size'],actual_symbol_info=actual['info'],actual_section=section['name'],HI_PC=d['HI_PC'],LO_PC=d['LO_PC'],length_PC=d['length_PC'],length_argument=d['bytes'],source_dependency_resolved=True,installed_callee_read_contract_proved=False))
    need(len(prefix_bindings)==14 and sum(v['bytes']for v in prefix_bindings)==109,'Fourteen exact source/length bindings,no NUL or padding')
    callback_candidates=prefix['newly_identified_callback_CODE_gaps']
    need(callback_candidates==[0x10c36,0x10d2e,0x10d30,0x11544],'Exact four originally identified candidate callback entries')
    callback_gaps=[pc for pc in callback_candidates if not any(o['info']==18 and o['original_PC']<=pc<o['original_PC']+o['bytes'] for o in plan['owners'])]
    need(not callback_gaps and 'tsl9_registered_callbacks_static_data_1a638' in literal_names and not resolved_callback_names&literal_names,'All four candidate CODE bodies and both callback DATA providers supplied;loop DATA still explicit')
    def table_bindings(d):
        obj=linked_globals[d['name']];section=linked.sections[obj['section']];offset=obj['value']-section['address']
        need(obj['info']==17 and obj['size']==d['bytes'] and obj['value']==d['start'] and section['flags']==2,'Actual original-coordinate readonly DATA owner')
        raw=linked.data(section)[offset:offset+d['bytes']];need(raw==firmware[d['start']-0x8000:d['end']-0x8000],'Actual complete original table bytes')
        rows=[]
        for i,(target,name) in enumerate(zip(d['targets'],d['target_symbols'])):
            cell=raw[4*i:4*i+4]
            actual=d['start']+int.from_bytes(cell,'little',signed=True) if d['kind']=='signed-relative-event-table' else int.from_bytes(cell,'little')
            need(actual==target,'Every actual relative/pointer cell retains its original target')
            if not target:need(name is None and cell==bytes(4),'Original null callback cell');continue
            fn=linked_globals[name];source_fn=source_globals[name]
            need(fn['info']==18 and fn['size']>0 and fn['value']==target and linked.sections[fn['section']]['flags']==6 and b['original_value'](e,plan,source_fn)==target,'Every target backed by positive native CODE at the exact original address')
            if d['kind']=='callback-function-pointers':
                refs=[r for r in linked.relocations if r['offset']==d['start']+4*i and r['type']==1]
                need(len(refs)==1 and refs[0]['addend']==0 and linked.symbols[refs[0]['symbol']]['name']==name,'Actual pointer relocation targets the real CODE provider')
            rows.append(dict(table=d['name'],index=i,original_target=target,CODE_provider=name,positive_CODE_bytes=fn['size'],callback_relocation=d['kind']=='callback-function-pointers'))
        return rows
    def address_pair(pc,name,info):
        refs={}
        for kind,place in [(23,pc),(24,pc+4)]:
            hits=[]
            for rel in e.relocations:
                if rel['type']!=kind:continue
                parent,within=b['lookup'](plan,rel['section'],rel['offset'])
                if parent['original_PC']+within==place:hits.append(rel)
            need(len(hits)==1 and hits[0]['addend']==0,'One actual zero-addend native HI/LO operand');refs[kind]=hits[0]
        need(e.symbols[refs[23]['symbol']]['name']==name and b['original_value'](e,plan,e.symbols[refs[24]['symbol']])==pc,'HI names the actual provider and LO retains the local HI anchor')
        obj=linked_globals[name];need(obj['info']==info and obj['size']>0 and obj['section'] not in [0,0xfff1],'Real positive DATA/CODE provider')
        hi=int.from_bytes(insns[pc]['raw'],'little');lo=int.from_bytes(insns[pc+4]['raw'],'little');imm=lo>>20;imm=imm-4096 if imm&2048 else imm
        need(hi&127==0x17 and lo&0x707f==0x13 and (lo>>15)&31==(hi>>7)&31 and (pc+(hi&0xfffff000)+imm)&0xffffffff==obj['value'],'Actual linked AUIPC/ADDI computes the exact real provider address')
        return dict(HI_PC=pc,LO_PC=pc+4,target=name,target_original_PC=obj['value'],actual_symbol_info=info,positive_provider_bytes=obj['size'],original_operand_bytes_proved=True)
    old_tables=json.loads((ROOT/'experiments/tsl9-central-callback-tables/spec-v2.json').read_text())['data_regions']
    old_names={d['name'] for d in old_tables};old_pairs=[]
    for rel in e.relocations:
        if rel['type']==23 and e.symbols[rel['symbol']]['name'] in old_names:
            parent,within=b['lookup'](plan,rel['section'],rel['offset']);old_pairs.append(address_pair(parent['original_PC']+within,e.symbols[rel['symbol']]['name'],17))
    central=dict(passed=True,table_CODE_bindings=[v for d in old_tables for v in table_bindings(d)],actual_HI_LO_table_arguments=old_pairs,actual_ELF_sha256=ELF_SHA)
    secondary_spec=json.loads((ROOT/'experiments/tsl9-secondary-message-data/spec-v1.json').read_text());secondary_static=runpy.run_path(str(ROOT/'experiments/tsl9-secondary-message-data/build-v1.py'),run_name='actual_secondary_source_contract')['static_audit']()
    secondary_code=json.loads((ROOT/'experiments/tsl9-secondary-message-dispatch/spec-v1.json').read_text());secondary_evidence=json.loads((ROOT/'experiments/tsl9-secondary-message-dispatch/evidence-v1.json').read_text())
    for f in secondary_evidence['selected_functions']:
        for op in f['operations']:need(insns[op['addr']]['raw']==bytes.fromhex(op['bytes']),'Every secondary function/guard/copy argument instruction is the actual linked original instruction')
    secondary_bindings=table_bindings(secondary_spec['data_regions'][0]);new_data_pairs=[address_pair(0x126b8,secondary_spec['data_regions'][0]['name'],17),address_pair(0x155b0,secondary_spec['data_regions'][1]['name'],17)]
    callable_pairs=[address_pair(p['PC'],p['target'],18) for p in secondary_code['PC_relative_pairs'] if p['reference_kind']=='callable-code-address']
    need(len(secondary_bindings)==7 and len(callable_pairs)==5 and secondary_static['passed'],'All seven new event cells,two DATA operands,and five actual callable addresses')
    copy=secondary_spec['data_regions'][1];obj=linked_globals[copy['name']];section=linked.sections[obj['section']];offset=obj['value']-section['address']
    need(obj['value']==0x19dd4 and obj['size']==12 and linked.data(section)[offset:offset+12]==firmware[0x19dd4-0x8000:0x19de0-0x8000],'Actual12-byte original-coordinate copy source')
    copy_call=[v for v in direct if v['PC']==0x155ba];need(len(copy_call)==1 and copy_call[0]['target_PC']==0x19bf0 and copy_call[0]['target_role']=='measured_instruction','Actual new copy call reaches measured CODE')
    need(not any(o['original_PC']<0x19dd4 and 0x19dd2<o['original_PC']+o['bytes'] for o in plan['owners']),'Adjacent two-byte padding remains unprovided')
    guard=b['B']['decode_control'](insns[0x126b4]['raw'],0x126b4);site=[v for v in indirect if v['PC']==0x126e6]
    header_ops=[o for f in secondary_evidence['selected_functions'] for o in f['operations'] if 0x126a8<=o['addr']<=0x126e6]
    need(header_ops and not any(o['type'] in ('call','ucall') for o in header_ops),'No opaque call between secondary event index and indirect dispatch')
    need(guard==(16,0x128fc) and len(site)==1 and site[0]['rd']==0 and site[0]['rs1']==15,'Actual secondary unsigned reject guard and A5 indirect jump')
    secondary_flow=dict(jump_PC=0x126e6,guard_PC=0x126b4,table_PC=0x1a58c,entries=7,unique_targets=6,target_PCs=secondary_spec['data_regions'][0]['targets'],guard_and_table_original_bytes_proved=True,condition='On guard fallthrough,((LBU(message[0])-1)&255)<=6; no opaque call intervenes before the table load/jump. Incoming and asynchronous ABI remain unproved.',runtime_index_or_target_observed=False,asynchronous_ABI_interference_excluded=False)
    hidden=runpy.run_path(str(ROOT/'experiments/tsl9-secondary-message-dispatch/audit-v1.py'),run_name='hidden_existing_dependency')['audit']()['hidden_existing_dependency']
    actual_hidden=b''.join(insns[pc]['raw'] for pc in sorted(insns) if 0x17832<=pc<0x1787c)
    need(hashlib.sha256(actual_hidden).hexdigest()==hidden['consumer_window_sha256'] and not hidden['DATA_provided'] and not hidden['index_globally_bounded'],'Existing unbounded raw-address dependency remains explicit and original-equal')
    need(central['passed'] and len(central['table_CODE_bindings'])==22 and len(central['actual_HI_LO_table_arguments'])==3,'All actual original-coordinate central table CODE and pointer bindings')
    central_evidence=json.loads((ROOT/'experiments/tsl9-central-event-callbacks/evidence-v1.json').read_bytes())
    central_ops={o['addr']:o for f in central_evidence['selected_functions'] for o in f['operations']}
    central_guard={0x11544:'lbu a5, 2(a0)',0x11548:'li a4, 16',0x1154a:'bltu a4, a5, 0x119c6',0x1154e:'auipc a4, 0x9',0x11552:'addi a4, a4, -6',0x11556:'slli a5, a5, 0x2',0x11558:'add a5, a5, a4',0x1155a:'lw a5, 0(a5)',0x1156a:'add a5, a5, a4',0x1156e:'jr a5'}
    for pc,text in central_guard.items():need(central_ops[pc]['opcode']==text and bytes.fromhex(central_ops[pc]['bytes'])==insns[pc]['raw'],'Actual bounded central-event guard/index/jump bytes')
    cs=json.loads((ROOT/'experiments/tsl9-central-callback-tables/spec-v2.json').read_bytes())['data_regions'][0]
    obj=linked_globals[cs['name']];section=linked.sections[obj['section']];offset=obj['value']-section['address'];raw=linked.data(section)[offset:offset+68]
    central_targets=[0x1a548+int.from_bytes(raw[i:i+4],'little',signed=True) for i in range(0,68,4)]
    need(obj['info']==17 and obj['value']==0x1a548 and obj['size']==68 and central_targets==cs['targets'] and len(set(central_targets))==7 and all(t in insns and 0x11544<=t<0x119c8 for t in central_targets),'All seventeen actual event cells and seven measured internal targets')
    site=[v for v in indirect if v['PC']==0x1156e];need(len(site)==1 and site[0]['rd']==0 and site[0]['rs1']==15,'Actual central-event register-indirect dispatch')
    central_flow=dict(jump_PC=0x1156e,guard_PC=0x1154a,table_PC=0x1a548,table_bytes=68,entries=17,unique_targets=7,target_PCs=central_targets,
        condition='On guard fallthrough,unsigned A5<=16 from LBU. No opaque call intervenes before indexed load/jump. Incoming event/callback ABI and asynchronous interference remain unproved.',
        guard_and_table_original_bytes_proved=True,runtime_index_or_target_observed=False,asynchronous_ABI_interference_excluded=False)
    return dict(schema='TSL9-static-native-transfer-positions-v21',mode=mode,ELF_sha256=ELF_SHA,
        source_curated=True,source_C_H_files=158,source_comparisons=264,source_objects=528,independent_diagnostic_reader=independent,instructions=23314,direct_transfers=direct,counts=dict(counts),direct_target_roles=dict(Counter(d['target_role'] for d in direct)),
        indirect_transfers=indirect,traps=traps,privileged_returns=privileged_returns,
        ordinary_next_position_gaps=ordinary_gaps,call_return_positions=call_returns,
        original_breakpoint_vector_boundary=boundary[0],
        source_unreconstructed_providers=len(source_undefined),literal_only_provider_roles=literal_roles,mixed_direct_and_address_provider_roles=mixed_roles,static_table_dispatch=table_flow,phase_table_dispatch=phase_flow,notification_table_dispatches=notification_flow,record_table_dispatches=record_tables,record_lookup_dispatch=record_lookup,guarded_jump_tables=13,secondary_event_table_dispatch=secondary_flow,secondary_event_CODE_bindings=secondary_bindings,secondary_DATA_address_pairs=new_data_pairs,secondary_callable_address_pairs=callable_pairs,secondary_copy_source_contract=secondary_static,hidden_existing_static_DATA_dependencies=[hidden],central_event_table_dispatch=central_flow,central_callback_table_bindings=central,sequence_pool_bindings=sequence_bindings,sequence_literal_read_envelopes=literal_envelopes,real_zero_size_DATA_labels=6,retained_sequence_DATA_labels=3,sequence_global_pointer_limit_bound_proved=False,grid_pool_bindings=grid_bindings,grid_read_envelopes=grid_envelopes,retained_grid_DATA_labels=2,grid_global_state_bounds_proved=False,third_grid_dependency_unresolved=True,callback_prefix_bindings=prefix_bindings,new_prefix_positive_DATA_owners=14,unprovided_candidate_callback_CODE_targets=callback_gaps,compiler_UND_is_not_complete_missing_runtime_target_count=True,installed_prefix_callee_read_contract_proved=False,bounded_copy_sources=copy_sources,copy_bound_preconditions=copy_facts['preconditions'],copy_bound_argument=copy_facts['bound_argument'],external_direct_provider_ranking=[dict(source_symbol=n,direct_reference_count=c) for n,c in ranks.most_common()],
        all_ordinary_fallthrough_and_call_return_positions_owned=True,
        indirect_trap_and_privileged_return_runtime_targets_proved=False,
        whole_CFG_or_reachability_proved=False,physical_MCU_ROM_RAM_IRQ_OTA_proved=False,
        firmware_ready=False,firmware_BIN_generated=False,target_executed=False,HOST_model_executed=False,
        ISA_emulated=False,hardware_accessed=False,network=False)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--trial');p.add_argument('--replay',type=Path)
    a=p.parse_args();need(bool(a.trial)!=bool(a.replay),'One create-only trial or read-only replay')
    for path,pin in PINS.items():need(digest(HERE/path)==pin,'Pinned measured input '+path)
    b=runpy.run_path(str(HERE/'build-v64.py'),run_name='positive_static_library')
    need(digest(ROOT/b['K']['reader'])==b['K']['reader_sha256'],'Frozen reader identity')
    need(digest(ROOT/b['K']['firmware'])==b['K']['firmware_sha256'],'Original firmware identity')
    reports={mode:analyze(mode,b) for mode in ('c','cpp')}
    need({k:v for k,v in reports['c'].items() if k!='mode'}=={k:v for k,v in reports['cpp'].items() if k!='mode'},'Same actual C/C++ transfer evidence')
    if a.trial:
        need(Path(a.trial).name==a.trial,'One owned output directory name')
        out=HERE/'build'/a.trial;need(not out.exists(),'Create-only static flow evidence')
        out.mkdir()
        for mode,r in reports.items():(out/(mode+'-flow.json')).write_bytes(enc(r))
        (out/'inputs.json').write_bytes(enc(dict(builder_pins=PINS,script_sha256=digest(Path(__file__)),layout_ELF_sha256=ELF_SHA)))
    else:
        out=a.replay.resolve();need(out.parent==HERE/'build','Owned read-only flow evidence')
        need(json.loads((out/'inputs.json').read_bytes())==dict(builder_pins=PINS,script_sha256=digest(Path(__file__)),layout_ELF_sha256=ELF_SHA),'All transfer proof input identities')
        for mode,r in reports.items():need(json.loads((out/(mode+'-flow.json')).read_bytes())==r,'Every retained transfer/continuation fact rederived')
    r=reports['c']
    print(json.dumps(dict(passed=True,instructions=r['instructions'],direct_transfers=len(r['direct_transfers']),
        direct_target_roles=r['direct_target_roles'],ordinary_next_position_gaps=len(r['ordinary_next_position_gaps']),
        call_return_positions=len(r['call_return_positions']),indirect_transfers=len(r['indirect_transfers']),traps=len(r['traps']),
        privileged_returns=len(r['privileged_returns']),source_unreconstructed_providers=r['source_unreconstructed_providers'],firmware_ready=False)))
if __name__=='__main__':
    try:main()
    except Exception as e:
        msg=str(e)
        for p,t in [(ROOT,'$'+'{PROJECT_ROOT}'),(Path.home(),'$'+'{USERPROFILE}')]:
            for form in [str(p),p.as_posix()]:msg=msg.replace(form.replace('\\','\\\\'),t).replace(form,t)
        print(json.dumps(dict(passed=False,error_type=type(e).__name__,reason=msg)),file=sys.stderr);sys.exit(1)
