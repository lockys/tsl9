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
  "build-v41.py": "9767058f6854183f610135ae95f79ecd8e2bbac822de0846d0f6e926548296d1",
  "spec-v38.json": "768d20fbe75416b6d4d2468bd4cb0061914aae2aad4da5ee56facd250d68486c",
  "build/selector-storage-v1/measurement.json": "555160fd2e16fe609453f8d968a65268edea9b6829a160c4093d7b8bc60cfd26"
}
ELF_SHA='44839f13059d15231747ac09a58615c57c8b025fb39466b3fdaff2f3579b5666'
def analyze(mode,b):
    folder=HERE/'build/selector-storage-v1'/mode
    path=folder/'NONLOADABLE-ORIGINAL-LAYOUT.elf'
    need(digest(path)==ELF_SHA,'Actual original-layout ELF identity')
    e=b['E'](b['source'](mode));plan=b['derive'](e);b['validate_original'](e,plan)
    b['audit_split'](folder/'split-C-payload.o',e,plan)
    linked=b['E'](path);result=b['audit_link'](path,e,plan)
    need(result['original_coordinate_bytes_equal']==45658,'All genuine original byte carriers')
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
    need(len(insns)==15200,'All15200 instructions')
    imports={i['original_reference_PC']:i for i in plan['imports']}
    direct=[];indirect=[];traps=[];privileged_returns=[];ordinary_gaps=[];call_returns=[];counts=Counter()
    actual_control={(r['offset'],r['type']):r for r in linked.relocations if r['type'] in (16,17,44,45)}
    need(len(actual_control)==2498,'All2498 typed direct-control relocations')
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
    need({(d['PC'],d['kind']) for d in direct if d['reference_kind']=='applied_native_relocation'}==set(actual_control),'One-to-one coverage of all2498 applied native direct-control relocations')
    need(len(direct)==2515 and sum(d['reference_kind']=='unchanged_intra_owner_immediate' for d in direct)==17,'All2515 immediate transfers including17 unchanged local-body branches')
    need(not ordinary_gaps and all(r['position_owned'] for r in call_returns),'All ordinary sequential and call-return positions have real compiled instructions')
    boundary=[t for t in traps if t['PC']==0x8034]
    need(len(boundary)==1 and boundary[0]['encoding']=='EBREAK' and boundary[0]['next_sequential_PC']==0x8038,'Original breakpoint/vector boundary retained')
    need(any(o['info']==17 and o['original_PC']==0x8038 and o['bytes']==328 for o in plan['owners']),'Actual vector data starts at8038')
    source_undefined=[s for s in e.symbols if s['info']>>4 and s['section']==0]
    need(len(source_undefined)==122,'Source implementation still has122 genuine undefined providers')
    ranks=Counter(d['source_provider'] for d in direct if d['source_provider'])
    literal_only=sorted(s['name']for s in source_undefined if s['name']not in ranks)
    need(len(literal_only)==21,'Twenty-one genuine literal-only dependencies remain unprovided')
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
    need(not mixed,'No remaining mixed direct/address provider reference')
    need(all(n in ranks for n in mixed),'The mixed reference has actual direct control edges')
    need(Counter(types[n]for n in literal_names)==Counter({'opaque-data-address':1,'opaque-static-data-address':20}),'Retained opaque default,twenty static references and no unprovided callback remain address-only')
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
    return dict(schema='TSL9-static-native-transfer-positions-v13',mode=mode,ELF_sha256=ELF_SHA,
        instructions=15200,direct_transfers=direct,counts=dict(counts),direct_target_roles=dict(Counter(d['target_role'] for d in direct)),
        indirect_transfers=indirect,traps=traps,privileged_returns=privileged_returns,
        ordinary_next_position_gaps=ordinary_gaps,call_return_positions=call_returns,
        original_breakpoint_vector_boundary=boundary[0],
        source_unreconstructed_providers=122,literal_only_provider_roles=literal_roles,mixed_direct_and_address_provider_roles=mixed_roles,static_table_dispatch=table_flow,phase_table_dispatch=phase_flow,external_direct_provider_ranking=[dict(source_symbol=n,direct_reference_count=c) for n,c in ranks.most_common()],
        all_ordinary_fallthrough_and_call_return_positions_owned=True,
        indirect_trap_and_privileged_return_runtime_targets_proved=False,
        whole_CFG_or_reachability_proved=False,physical_MCU_ROM_RAM_IRQ_OTA_proved=False,
        firmware_ready=False,firmware_BIN_generated=False,target_executed=False,HOST_model_executed=False,
        ISA_emulated=False,hardware_accessed=False,network=False)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--trial');p.add_argument('--replay',type=Path)
    a=p.parse_args();need(bool(a.trial)!=bool(a.replay),'One create-only trial or read-only replay')
    for path,pin in PINS.items():need(digest(HERE/path)==pin,'Pinned measured input '+path)
    b=runpy.run_path(str(HERE/'build-v41.py'),run_name='positive_static_library')
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
        privileged_returns=len(r['privileged_returns']),source_unreconstructed_providers=122,firmware_ready=False)))
if __name__=='__main__':
    try:main()
    except Exception as e:
        msg=str(e)
        for p,t in [(ROOT,'$'+'{PROJECT_ROOT}'),(Path.home(),'$'+'{USERPROFILE}')]:
            for form in [str(p),p.as_posix()]:msg=msg.replace(form.replace('\\','\\\\'),t).replace(form,t)
        print(json.dumps(dict(passed=False,error_type=type(e).__name__,reason=msg)),file=sys.stderr);sys.exit(1)
