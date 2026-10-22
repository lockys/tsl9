#!/usr/bin/env python3
"""Original register/source default, optional actual native provenance replay."""
import argparse,json,importlib.util
from pathlib import Path
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def load(name,p):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def inspect(root,firmware,receipt=None):
    root=Path(root).resolve(strict=True);firmware=Path(firmware).resolve(strict=True);P=load('callback_owned_register_proof',HERE/'proof.py');G=load('callback_live_GP_source',HERE/'gp.py')
    if (HERE/'seal.json').exists():
        for n,pin in P.read(HERE/'seal.json')['members'].items():P.need(P.sha(HERE/n)==pin,'Immutable independent source/register review '+n)
    root,blob,rows,decode,E=P.context(root,firmware);facts=P.source_gate(rows);facts['GP_ports']=P.uses(rows,3);facts['controls']=P.controls(blob,0x8614,rows,decode,P.source_gate);P.need(facts==P.read(HERE/'original-contract.json'),'All actual original operands/frame/GP constraints and four targeted controls');identity=G.source_identity(P,root);pins=P.read(HERE/'review-inputs.json');P.need(identity['source_files']==pins['source_files'],'Reviewed frozen three-source refinement')
    producer=P.case(root,'v4160-callback-registers-2026-10-22')/'implementation/verify_native.py';P.need(P.sha(producer)==pins['producer_runner_sha256'],'Final reviewed native runner')
    for n,pin in pins['producer_dependencies'].items():P.need(P.sha(producer.parent/n)==pin,'Reviewed actual source/profile reader '+n)
    result=dict(schema='ID2966-callback-owned-register-source-review-v1',passed=True,original_instructions_redecoded=217,original_raw_controls_reused_from_sealed_proof=26,old26_controls_rerun=False,new_source_constraint_controls=4,original_explicit_S10_ports=0,original_explicit_S11_ports=0,original_direct_SP0_words=0,original_GP_ports=6,current_source_refinement=identity,actual_native_artifacts_replayed=False,actual_native_source_compile_provenance_replayed=False,HOST_tests_rerun=False,ROM_preserves_GP_S10_S11_proved=False,whole_original_ABI_admitted=False,original_placement_admitted=False,remaining_eight_bytes_owned_or_safe=False,target_execution=False,ISA_emulation=False,network=False,hardware=False,OTA_ready=False)
    if receipt:
        receipt=Path(receipt).resolve(strict=True);r=P.read(receipt);P.need(r['passed'] and r['mode'] in ('c','cpp'),'Actual explicit native formal receipt');folder=receipt.parent;V=load('callback_independent_native_provenance',HERE/'provenance.py');provenance,raw,r=V.ordered(P,root,receipt);pre,pre_rows=P.artifact(raw,decode,E);post,post_rows=P.artifact(folder,decode,E);pre_gate=P.candidate_gate(pre_rows);post_gate=P.candidate_gate(post_rows);ir=(raw/'callback.ll').read_text(encoding='utf-8');gp=G.machine(P,post_rows,ir);e=E(folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf');s=next(s for s in e.symbols if s['name']=='tsl9_callback_native_8614');code=e.function_bytes(s);controls=P.controls(code,s['value'],post_rows,decode,P.candidate_gate);controls.append(G.control(P,code,s['value'],post_rows,decode,ir));replay=load('callback_current_native_replay',producer).replay(root,receipt);P.need(replay['passed'],'Actual formal native/pass replay')
        source_returns=sorted(c['RA']-0x8614 for c in facts['opaque_call_links']);actual_returns=sorted(c['return_offset'] for c in post['call_links']);result.update(actual_native_artifacts_replayed=True,actual_native_source_compile_provenance_replayed=True,mode=r['mode'],receipt_sha256=P.sha(receipt),source_provenance=provenance,before=pre,after=post,before_register_frame_gate=pre_gate,after_register_frame_gate=post_gate,actual_GP_gate=gp,actual_native_controls=controls,actual_native_control_count=len(controls),call_return_offset_set_equal_source=source_returns==actual_returns,native_bytes=post['bytes'],native_instructions=post['instruction_rows'],numeric_fit_only=post['bytes']<=632,uncovered_original_bytes=632-post['bytes'],producer_actual_replay_passed=True)
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--firmware',required=True,type=Path);p.add_argument('--receipt',type=Path);a=p.parse_args();print(json.dumps(inspect(a.project_root,a.firmware,a.receipt)))
