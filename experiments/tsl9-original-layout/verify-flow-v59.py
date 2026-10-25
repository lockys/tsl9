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
  "../tsl9-grid-read-windows/spec-v2.json": "edd6646971da614579c5932b27beb51187e348afdf262f83558ca6682f6f4366"
}
ELF_SHA='8c9f414f847c28c7adf6bb2c85245cde67cc2dd89e4b619c30340fad5ba3b519'
def analyze(mode,b):
    folder=HERE/'build/grid-read-windows-v2'/mode
    path=folder/'NONLOADABLE-ORIGINAL-LAYOUT.elf'
    need(digest(path)==ELF_SHA,'Actual original-layout ELF identity')
    e=b['E'](b['source'](mode));plan=b['derive'](e);b['validate_original'](e,plan)
    b['audit_split'](folder/'split-C-payload.o',e,plan)
    linked=b['E'](path);result=b['audit_link'](path,e,plan)
    need(result['original_coordinate_bytes_equal']==68265,'All genuine original byte carriers')
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
    need(len(insns)==21938,'All18324 instructions')
    imports={i['original_reference_PC']:i for i in plan['imports']}
    direct=[];indirect=[];traps=[];privileged_returns=[];ordinary_gaps=[];call_returns=[];counts=Counter()
    actual_control={(r['offset'],r['type']):r for r in linked.relocations if r['type'] in (16,17,44,45)}
    need(len(actual_control)==4228,'All3388 typed direct-control relocations')
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
    need(len(direct)==4245 and sum(d['reference_kind']=='unchanged_intra_owner_immediate' for d in direct)==17,'All3405 immediate transfers including17 unchanged local-body branches')
    need(not ordinary_gaps and all(r['position_owned'] for r in call_returns),'All ordinary sequential and call-return positions have real compiled instructions')
    boundary=[t for t in traps if t['PC']==0x8034]
    need(len(boundary)==1 and boundary[0]['encoding']=='EBREAK' and boundary[0]['next_sequential_PC']==0x8038,'Original breakpoint/vector boundary retained')
    need(any(o['info']==17 and o['original_PC']==0x8038 and o['bytes']==328 for o in plan['owners']),'Actual vector data starts at8038')
    source_undefined=[s for s in e.symbols if s['info']>>4 and s['section']==0]
    need(len(source_undefined)==22,'Source implementation still has22 genuine undefined providers')
    ranks=Counter(d['source_provider'] for d in direct if d['source_provider'])
    literal_only=sorted(s['name']for s in source_undefined if s['name']not in ranks)
    need(len(literal_only)==20,'Twenty genuine literal-only dependencies remain unprovided')
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
    need(Counter(types[n]for n in literal_names)==Counter({'opaque-data-address':1,'opaque-static-data-address':18,'unbounded-static-data-address':1}),'Twenty remaining dependencies retain the third unresolved grid bound;only the two locally bounded grid providers resolve')
    previous_roles={v['source_symbol']:v['reference_kind']for v in json.loads((HERE/'build/record-sequence-pool-flow-v2/c-flow.json').read_bytes())['literal_only_provider_roles']}
    resolved_grid_names={f'tsl9_record_field_transitions_static_data_{pc:x}'for pc in (0x19ed8,0x1a018)}
    need(set(previous_roles)==literal_names|resolved_grid_names and all(previous_roles[name]==types[name]for name in literal_names),'Every remaining literal source keeps its exact previously verified role')
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
    return dict(schema='TSL9-static-native-transfer-positions-v17',mode=mode,ELF_sha256=ELF_SHA,
        instructions=21938,direct_transfers=direct,counts=dict(counts),direct_target_roles=dict(Counter(d['target_role'] for d in direct)),
        indirect_transfers=indirect,traps=traps,privileged_returns=privileged_returns,
        ordinary_next_position_gaps=ordinary_gaps,call_return_positions=call_returns,
        original_breakpoint_vector_boundary=boundary[0],
        source_unreconstructed_providers=len(source_undefined),literal_only_provider_roles=literal_roles,mixed_direct_and_address_provider_roles=mixed_roles,static_table_dispatch=table_flow,phase_table_dispatch=phase_flow,notification_table_dispatches=notification_flow,record_table_dispatches=record_tables,record_lookup_dispatch=record_lookup,guarded_jump_tables=11,sequence_pool_bindings=sequence_bindings,sequence_literal_read_envelopes=literal_envelopes,real_zero_size_DATA_labels=6,new_sequence_DATA_labels=3,sequence_global_pointer_limit_bound_proved=False,grid_pool_bindings=grid_bindings,grid_read_envelopes=grid_envelopes,new_grid_DATA_labels=2,grid_global_state_bounds_proved=False,third_grid_dependency_unresolved=True,bounded_copy_sources=copy_sources,copy_bound_preconditions=copy_facts['preconditions'],copy_bound_argument=copy_facts['bound_argument'],external_direct_provider_ranking=[dict(source_symbol=n,direct_reference_count=c) for n,c in ranks.most_common()],
        all_ordinary_fallthrough_and_call_return_positions_owned=True,
        indirect_trap_and_privileged_return_runtime_targets_proved=False,
        whole_CFG_or_reachability_proved=False,physical_MCU_ROM_RAM_IRQ_OTA_proved=False,
        firmware_ready=False,firmware_BIN_generated=False,target_executed=False,HOST_model_executed=False,
        ISA_emulated=False,hardware_accessed=False,network=False)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--trial');p.add_argument('--replay',type=Path)
    a=p.parse_args();need(bool(a.trial)!=bool(a.replay),'One create-only trial or read-only replay')
    for path,pin in PINS.items():need(digest(HERE/path)==pin,'Pinned measured input '+path)
    b=runpy.run_path(str(HERE/'build-v59.py'),run_name='positive_static_library')
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
