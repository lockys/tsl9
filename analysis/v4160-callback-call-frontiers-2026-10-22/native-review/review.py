#!/usr/bin/env python3
"""Read-only call-site signatures and reaching definitions; no target execution."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
OLD='apk-analysis/tsl9-v4160-callback-registers-2026-10-22/ABI-review/'
SOURCE='apk-analysis/tsl9-v4160-event-callback-2026-10-22/source-review/instructions.json'
PINS={OLD+'fields.py':'373d78c75feb58fcbf621d924733249786c8243197f8eef4e0a52e33e304b413',
      OLD+'llvm.py':'c52cc458441eab2038ff4bb5064666ec87af3b2345f5c8b99cf9fdcc0ffb0fd5',
      SOURCE:'f269b4091c82d540935b90d0a1d72c2ab9230cf78ef2640f969bfabb9a737448'}
FW_SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
ELF_SHA='7dd7f616477b6d64f6ba41a748b8bd0844531af33a76f61fb9bcc411b2c1bc0c'
NAME='tsl9_callback_native_8614'
MODEL_PINS={'experiments/tsl9-v4160-callback-registers/src/callback.c':'c3b59b7438991cd5c0d48a793b47cdde5e0ed6a3a8c311dd8e2e451cc0460739',
            'experiments/tsl9-v4160-callback-registers/src/callback.h':'4c61e9746cb30b18c9ae5cabef1e5618bfd003379df47d34f17d668bf7fc9f0b',
            'experiments/tsl9-v4160-callback-registers/src/io.h':'08838df777b5fc441637e02fe6539fb24e42b238c9d87ddf4bf03ab84df87e01'}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def need(value,message):
    if not value:raise ValueError(message)


def locate(root,relative):
    path=root/relative
    if not path.exists() and relative.startswith('apk-analysis/tsl9-'):
        path=root/relative.replace('apk-analysis/tsl9-','analysis/',1)
    need(path.is_file(),'Required pinned evidence '+relative)
    return path


def setup(root):
    paths={name:locate(root,name) for name in PINS}
    for name,path in paths.items():need(sha(path)==PINS[name],'Pinned static source/helper '+name)
    fields=runpy.run_path(str(paths[OLD+'fields.py']))
    llvm=runpy.run_path(str(paths[OLD+'llvm.py']))
    trace=runpy.run_path(str(HERE/'trace.py'));ir=runpy.run_path(str(HERE/'ir.py'))
    return fields,llvm,trace,ir,json.loads(paths[SOURCE].read_bytes())


def provenance(root,folder,pre):
    formal=json.loads((folder/'verification.json').read_bytes())
    probe=json.loads((pre/'probe.json').read_bytes())
    need(formal['schema']=='TSL9-callback-live-GP-reserved-register-component-v1'
         and probe['schema']=='TSL9-callback-fresh-GP-bridge-probe-v1','Exact unchanged formal/probe schemas')
    need(formal['mode']==probe['mode']==folder.name,'Actual IR generation language association')
    need(formal['raw_folder'].replace('\\','/').endswith('/'+pre.relative_to(root).as_posix()),
         'Formal raw-provider path identifies the selected IR folder')
    for name in ('callback.ll','callback.o','probe.json'):
        path=pre/name;actual=dict(bytes=path.stat().st_size,sha256=sha(path))
        need(formal['raw_artifacts'][name]==actual,'Formal record binds actual raw artifact '+name)
        if name!='probe.json':need(probe['artifacts'][name]==actual,'Actual probe binds same IR/object '+name)
    for name in ('callback-ordered.o','COMPONENT-ONLY-NOT-FIRMWARE.elf'):
        path=folder/name;actual=dict(bytes=path.stat().st_size,sha256=sha(path))
        need(formal['artifacts'][name]==actual,'Formal ordered output binds the actual code '+name)
    for relative,pin in MODEL_PINS.items():
        need(sha(locate(root,relative))==pin,'Current selected source remains unchanged '+relative)
        for record in (formal,probe):
            values=[v for k,v in record['source_pins'].items() if k.replace('\\','/').endswith('/'+relative)]
            need(values==[pin],'Formal/probe source generation pin '+relative)
    return dict(formal_receipt_sha256=sha(folder/'verification.json'),
                probe_sha256=sha(pre/'probe.json'),current_source_pins=MODEL_PINS,
                actual_IR_object_formal_association_checked=True,
                archive_byte_readback_only=True,compiler_rerun=False)


def forwarding(trace,rows,matched):
    flow=trace['reaching'](rows,'opaque-all')
    send=matched['descriptor_send']['PC'];gate=matched['gate_after_copy']['PC']
    for reg in (13,14):
        need(flow['IN'][send][reg]==frozenset({('opaque',gate,reg)}),
             'Physical descriptor-send A3/A4 originate in the matched earlier gate outputs')
    return {'A3_A4_from_gate_after_copy':True,'assumption':'same earlier opaque outputs at matched gate'}


def dead_halfword(rows,loadpc,storepc,killpc,callpc):
    bypc={r['PC']:r for r in rows};load=bypc[loadpc];reg=load['rd']
    need(load['op'] in ('lh','lhu') and load['memory_width']==16,'Actual halfword load')
    before=[r for r in rows if loadpc<r['PC']<killpc]
    uses=[r for r in before if reg in (r['rs1'],r['rs2'])]
    need(len(uses)==1 and uses[0]['PC']==storepc and uses[0]['op']=='sh'
         and uses[0]['rs2']==reg and uses[0]['memory_width']==16,'Only low16 SH use before the kill')
    need(not any(r['rd']==reg for r in before),'No earlier redefinition hides another use')
    kill=bypc[killpc];need(kill['rd']==reg and reg not in (kill['rs1'],kill['rs2']),
                         'Actual register definition kills the loaded halfword')
    need(killpc<callpc and bypc[callpc]['op']=='jalr','Kill precedes the matched call')
    return dict(load=load,only_use=uses[0],kill=kill,call=callpc,
                signed_extension_dead_at_call=True,intermediate_fault_interrupt_equivalence=False)


def rejects(action):
    try:action()
    except (ValueError,KeyError):return True
    raise ValueError('A focused counterexample was incorrectly admitted')


def controls(raw,base,ctx,fields,trace,ir,text,matched):
    out={}
    def decode(body):return fields['rows'](body,base,ctx)
    def alter(pc,mask):
        b=bytearray(raw);offset=pc-base;width=2 if b[offset]&3!=3 else 4
        word=int.from_bytes(b[offset:offset+width],'little')^mask
        b[offset:offset+width]=word.to_bytes(width,'little');return decode(bytes(b))
    # Change only the actual 32-bit D4 target load immediate, not a fabricated row.
    pc=matched['descriptor_send']['target_loads'][0]['PC']
    out['changed_D4_pointer_slot_rejected']=rejects(lambda:trace['labels'](alter(pc,4<<20)))
    # Change physical C.LI a2,0 to C.LI a3,0 at the actual call setup.
    send=matched['descriptor_send']['PC'];rows=decode(raw)
    zero=[r for r in rows if r['PC']<send and r['rd']==12 and r['rs1']==0 and r['immediate']==0][-1]
    out['A3_passthrough_kill_rejected']=rejects(lambda:forwarding(trace,alter(zero['PC'],1<<7),matched))
    parsed=ir['labels'](text)['descriptor_send'];value=parsed['args'][4]
    line=next(line for line in text.splitlines() if parsed['SSA']+' =' in line)
    changed=line.replace(', i32 '+value+',',', i32 0,',1)
    need(changed!=line,'Actual SSA A4 operand changed for a counterexample')
    out['SSA_A4_substitution_rejected']=rejects(lambda:ir['labels'](text.replace(line,changed,1)))
    shuffled=[rows[0],*reversed(rows[1:])]
    scrambled=trace['labels'](shuffled)[0]
    need({n:v['PC'] for n,v in scrambled.items()}=={n:v['PC'] for n,v in matched.items()},
         'Reversing stored row order does not change semantic correspondence')
    out['row_order_independence_positive']=True
    return out


def inspect(root,folder,firmware=None,ir_folder=None):
    root=Path(root).resolve();folder=Path(folder).resolve()
    need(folder.is_relative_to(root),'Actual folder must be in the selected project root')
    pre=Path(ir_folder).resolve() if ir_folder else folder.parent.parent/'pre'/folder.name
    need(pre.is_relative_to(root),'Explicit/inferred IR provider stays inside project root')
    fields,llvm,trace,ir,original=setup(root);ctx=fields['context'](root);E=ctx['ELF']
    source_provenance=provenance(root,folder,pre)
    ep=folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf';objp=folder/'callback-ordered.o';ll=pre/'callback.ll'
    elf=E(ep);obj=E(objp)
    need(sha(ep)==ELF_SHA,'Actual unchanged selected624 linked ELF, not an arbitrary new component')
    symbols=[s for s in elf.symbols if s['name']==NAME]
    need(len(symbols)==1 and symbols[0]['size']==624 and symbols[0]['info']==18,'One actual GLOBAL FUNC624')
    symbol=symbols[0];raw=elf.function_bytes(symbol);base=symbol['value']
    osymbol=next(s for s in obj.symbols if s['name']==NAME)
    need(obj.function_bytes(osymbol)==raw,'Actual ordered object supplies every linked function byte')
    need(not [s for s in elf.symbols if s['index']==0 and s['name']],'Actual component has no undefined named symbols')
    native=fields['rows'](raw,base,ctx)
    normalized=llvm['parse']((folder/'complete-static-disassembly.log').read_text())
    need([{k:v for k,v in row.items() if k!='offset'} for row in native]==normalized,
         'All actual223 raw decoded operands agree with independent LLVM transcript')
    need(len(native)==223 and len(original)==217,'Measured actual and original instruction coverage')
    firmware_read=False
    if firmware:
        fw=Path(firmware).resolve();need(sha(fw)==FW_SHA,'Official readonly current runtime input')
        body=fw.read_bytes()[0x614:0x88c]
        need(body==bytes.fromhex(''.join(r['raw_hex'] for r in original)),'Original217 rows cover actual632 bytes')
        firmware_read=True
    old,oldflow=trace['labels'](original);new,newflow=trace['labels'](native)
    text=ll.read_text();ssa=ir['labels'](text)
    need(set(old)==set(new)==set(ssa) and len(old)==15,'Fifteen uniquely identified signatures; no rank pairing')
    mapping={}
    for name in sorted(old):
        a,b,c=old[name],new[name],ssa[name]
        need(a['slot']==b['slot']==c['slot'] and b['target_register']==c['target_register'],
             'Independent raw target-load and SSA signatures agree '+name)
        need(a['possible_earlier_calls']==b['possible_earlier_calls'],'Matched possible-earlier-call CFG '+name)
        mapping[name]=dict(original=a,native=b,IR=c,
                           original_RA_offset=a['RA']-0x8614,native_RA_offset=b['RA']-base,
                           RA_offsets_equal=a['RA']-0x8614==b['RA']-base)
    passthrough={'original':forwarding(trace,original,old),'native':forwarding(trace,native,new)}
    halfword={'original':dead_halfword(original,0x8800,0x8808,0x880c,old['descriptor_send']['PC']),
              'native':dead_halfword(native,0x120a,0x120e,0x121a,new['descriptor_send']['PC'])}
    # These are observed physical differences, not automatic failure under an installed ROM ABI.
    pold=old['gate_before_capacity']['PC'];pnew=new['gate_before_capacity']['PC']
    need(trace['constants'](oldflow,pold,23)=={0x40000},'Original S7 nominal resident base')
    need(trace['constants'](newflow,pnew,20)=={0xffff7ff4},'Actual pending native S4 scratch mask')
    ns7=newflow['IN'][pnew][23]
    need(len(ns7)==1 and next(iter(ns7))[0]=='instruction','Native S7 has an actual local definition')
    ns7row=newflow['rows'][next(iter(ns7))[1]]
    need(ns7row['op']=='lhu' and ns7row['memory_width']==16,'Actual native S7 is unsigned16 queue read')
    gaps=dict(first_receive_S2_original=trace['constants'](oldflow,old['message_receive']['PC'],18),
              first_receive_S2_native_definitions=[trace['definition'](d,newflow,{}) for d in
                                                  sorted(newflow['IN'][new['message_receive']['PC']][18])],
              pending_original_S7_nominal=0x40000,pending_native_S7_definition=ns7row,
              pending_native_S7_range=[0,65535],pending_native_S4_mask=0xffff7ff4,
              same_physical_S_roles=False,
              relevance='Conditional obligation for unknown resident code observing implicit registers; not an automatic functional ABI failure',
              candidate_resident_specific_closure='Not evaluated by this checker; requires separately pinned resident bodies/contract')
    gaps['first_receive_S2_original']=sorted(gaps['first_receive_S2_original'] or [])
    counter=controls(raw,base,ctx,fields,trace,ir,text,new)
    artifact_paths={'ordered_ELF':ep,'ordered_object':objp,'LLVM':folder/'complete-static-disassembly.log','IR':ll}
    artifacts={n:dict(path=p.relative_to(root).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
               for n,p in artifact_paths.items()}
    return dict(schema='TSL9-callback-call-frontiers-independent-v1',passed=True,
                actual_native_artifacts_read=True,actual_call_frontiers_checked=True,
                original_firmware_read=firmware_read,original217_source_fields_checked=True,
                actual_folder=folder.relative_to(root).as_posix(),actual_ir_folder=pre.relative_to(root).as_posix(),
                artifact_pins=artifacts,source_pins=PINS,helper_pins={n:sha(HERE/n) for n in ('trace.py','ir.py','review.py')},
                formal_IR_provenance_checked=True,source_provenance=source_provenance,
                bytes=624,instructions=223,original_instructions=217,matched_semantic_sites=15,
                semantic_matching_basis='Actual target LW source, literal argument discriminator, CFG ancestors and independent LLVM SSA; no address-order pairing',
                correspondence=mapping,source_frontiers=trace['frontiers'](original,old),
                native_frontiers=trace['frontiers'](native,new),descriptor_send=passthrough,
                halfword_extension=halfword,physical_register_observations=gaps,focused_controls=counter,
                nominal_slot_assumption='Conventional callee-saved register preservation only for matching; opaque-all frontiers separately retained',
                entire_call_prefix_equivalent=False,RA_contract_proved=False,unknown_ROM_contract_proved=False,
                full_original_ABI_admitted=False,whole632_ownership_proved=False,placement_admitted=False,
                source_changed=False,HOST_rerun=False,target_execution=False,ISA_emulation=False,hardware_OTA_proved=False)


def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path)
    p.add_argument('--folder',type=Path);p.add_argument('--ir-folder',type=Path);p.add_argument('--firmware',type=Path)
    p.add_argument('--receipt',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
    if a.replay:
        need(not any((a.folder,a.ir_folder,a.receipt)),'Readonly replay uses recorded actual artifact paths')
        old=json.loads(a.replay.read_bytes())
        need(bool(a.firmware)==old['original_firmware_read'],'Replay preserves explicit firmware-read mode')
        result=inspect(root,root/old['actual_folder'],a.firmware,root/old['actual_ir_folder'])
        need(result==old,'Exact actual call-frontier replay')
    else:
        need(a.folder is not None and a.receipt is not None and not a.receipt.exists(),'Explicit actual folder and create-only receipt')
        result=inspect(root,a.folder,a.firmware,a.ir_folder)
        need(not a.receipt.resolve().is_relative_to(a.folder.resolve()),'Receipt outside unchanged prior native artifact folder')
        a.receipt.parent.mkdir(parents=True,exist_ok=True)
        a.receipt.write_bytes((json.dumps(result,indent=2,ensure_ascii=False)+'\n').encode('utf8'))
    print(json.dumps({k:result[k] for k in ('passed','actual_native_artifacts_read','actual_call_frontiers_checked',
                                           'original_firmware_read','matched_semantic_sites','full_original_ABI_admitted')}))


if __name__=='__main__':main()
