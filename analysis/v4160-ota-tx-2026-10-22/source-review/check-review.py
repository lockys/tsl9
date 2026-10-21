#!/usr/bin/env python3
"""Recheck original280B source/40 controls, with optional actual carrier roles."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def need(v,m):
    if not v:raise ValueError(m)
def inspect(root,firmware,objects=()):
    for name,pin in read(HERE/'seal.json')['members'].items():
        path=(HERE/name).resolve(strict=True);need(path.parent==HERE and sha(path)==pin,'Immutable TX source-review member '+name)
    spec=importlib.util.spec_from_file_location('TX_closed_source_proof',HERE/'proof.py');proof=importlib.util.module_from_spec(spec);spec.loader.exec_module(proof);fresh=proof.inspect(root,firmware,objects);selected=read(HERE/'source-proof.json');contract=read(HERE/'contracts.json')
    for key in ('decoded_rows','direct_local_written_GPRs','basic_block_extents','raw_operand_controls','source_roles','source_RELA','source_directives','incoming_instruction_fields'):
        need(fresh[key]==selected[key],'Fresh exact raw/source proof '+key)
    need(contract['extent']['bytes']==280 and contract['extent']['instructions']==96 and contract['direct_local_written_GPRs']==fresh['direct_local_written_GPRs'],'Manual contract extent/direct-write binding')
    return {'passed':True,'source_bytes':280,'instruction_count':96,'raw_source_and40controls_rechecked':True,'owned_RELA':11,'external_incoming':9,'incoming_linked_calls':8,'incoming_no_link_tails':1,'selected_actual_carrier_readbacks':selected['actual_archived_carriers_replayed'],'actual_archived_carriers_replayed':fresh['actual_archived_carriers_replayed'],'reconstructed_C_CPP_tested':False,'opaque_callee_preservation_proved':False,'target_execution':False,'ISA_emulation':False,'hardware':False,'OTA_ready':False}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',type=Path,required=True);p.add_argument('--firmware',type=Path,required=True);p.add_argument('--object',type=Path,action='append',default=[]);a=p.parse_args();print(json.dumps(inspect(a.project_root.resolve(),a.firmware.resolve(),a.object)))
if __name__=='__main__':main()
