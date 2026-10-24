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
 "build-v20.py": "dde22c51fc72a48bdd66a4fb3e6db78b628a46bfef57c4378123b295a0a26a76",
 "spec-v17.json": "33ca8283f6de488624d1f858c9a802ca070bba92c75c99e5c4c9cef77a4174fb",
 "build/main-initializers-v1/measurement.json": "33db2deb35bb63a28ffe727da7c03358d12237bac85e536245abf6aeec3b49c3"
}
ELF_SHA='0cdedd8659ca4e8bd7f3445dcd54970556a92e65db8db65c53428e2cb575ab05'
def analyze(mode,b):
    folder=HERE/'build/main-initializers-v1'/mode
    path=folder/'NONLOADABLE-ORIGINAL-LAYOUT.elf'
    need(digest(path)==ELF_SHA,'Actual original-layout ELF identity')
    e=b['E'](b['source'](mode));plan=b['derive'](e);b['validate_original'](e,plan)
    b['audit_split'](folder/'split-C-payload.o',e,plan)
    linked=b['E'](path);result=b['audit_link'](path,e,plan)
    need(result['original_coordinate_bytes_equal']==21460,'All genuine original byte carriers')
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
    need(len(insns)==7188,'All7188 instructions')
    imports={i['original_reference_PC']:i for i in plan['imports']}
    direct=[];indirect=[];traps=[];privileged_returns=[];ordinary_gaps=[];call_returns=[];counts=Counter()
    actual_control={(r['offset'],r['type']):r for r in linked.relocations if r['type'] in (16,17,44,45)}
    need(len(actual_control)==1166,'All1166 typed direct-control relocations')
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
    need({(d['PC'],d['kind']) for d in direct if d['reference_kind']=='applied_native_relocation'}==set(actual_control),'One-to-one coverage of all1166 applied native direct-control relocations')
    need(len(direct)==1183 and sum(d['reference_kind']=='unchanged_intra_owner_immediate' for d in direct)==17,'All1183 immediate transfers including17 unchanged local-body branches')
    need(not ordinary_gaps and all(r['position_owned'] for r in call_returns),'All ordinary sequential and call-return positions have real compiled instructions')
    boundary=[t for t in traps if t['PC']==0x8034]
    need(len(boundary)==1 and boundary[0]['encoding']=='EBREAK' and boundary[0]['next_sequential_PC']==0x8038,'Original breakpoint/vector boundary retained')
    need(any(o['info']==17 and o['original_PC']==0x8038 and o['bytes']==328 for o in plan['owners']),'Actual vector data starts at8038')
    source_undefined=[s for s in e.symbols if s['info']>>4 and s['section']==0]
    need(len(source_undefined)==76,'Source implementation still has76 genuine undefined providers')
    ranks=Counter(d['source_provider'] for d in direct if d['source_provider'])
    return dict(schema='TSL9-static-native-transfer-positions-v10',mode=mode,ELF_sha256=ELF_SHA,
        instructions=7188,direct_transfers=direct,counts=dict(counts),direct_target_roles=dict(Counter(d['target_role'] for d in direct)),
        indirect_transfers=indirect,traps=traps,privileged_returns=privileged_returns,
        ordinary_next_position_gaps=ordinary_gaps,call_return_positions=call_returns,
        original_breakpoint_vector_boundary=boundary[0],
        source_unreconstructed_providers=76,external_direct_provider_ranking=[dict(source_symbol=n,direct_reference_count=c) for n,c in ranks.most_common()],
        all_ordinary_fallthrough_and_call_return_positions_owned=True,
        indirect_trap_and_privileged_return_runtime_targets_proved=False,
        whole_CFG_or_reachability_proved=False,physical_MCU_ROM_RAM_IRQ_OTA_proved=False,
        firmware_ready=False,firmware_BIN_generated=False,target_executed=False,HOST_model_executed=False,
        ISA_emulated=False,hardware_accessed=False,network=False)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--trial');p.add_argument('--replay',type=Path)
    a=p.parse_args();need(bool(a.trial)!=bool(a.replay),'One create-only trial or read-only replay')
    for path,pin in PINS.items():need(digest(HERE/path)==pin,'Pinned measured input '+path)
    b=runpy.run_path(str(HERE/'build-v20.py'),run_name='positive_static_library')
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
        privileged_returns=len(r['privileged_returns']),source_unreconstructed_providers=76,firmware_ready=False)))
if __name__=='__main__':
    try:main()
    except Exception as e:
        msg=str(e)
        for p,t in [(ROOT,'$'+'{PROJECT_ROOT}'),(Path.home(),'$'+'{USERPROFILE}')]:
            for form in [str(p),p.as_posix()]:msg=msg.replace(form.replace('\\','\\\\'),t).replace(form,t)
        print(json.dumps(dict(passed=False,error_type=type(e).__name__,reason=msg)),file=sys.stderr);sys.exit(1)
