#!/usr/bin/env python3
"""Audit the source-topology candidate without demanding byte identity."""
import argparse
import json
from pathlib import Path
import runpy
import sys

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent


def inspect(root,firmware,folder):
    p=runpy.run_path(str(HERE/'predicates.py'))
    n=p['prior'](root)
    checked=n['inspect_native'](root,folder,firmware)
    context=n['context'](root,firmware)
    rows=context['raw']['validate'](context['original'])
    original_gates=[r for r in rows if r['op']=='jalr' and(r['rd'],r['rs1'])==(1,15)]
    actual=checked['checked_subset']
    before=[r['PC']+r['bytes'] for r in original_gates]
    after=[r['PC']+r['bytes'] for r in actual['gates']]
    p['need'](before==after,'Actual source-only candidate restores both opaque call RA values')
    gap=checked['gap_ledger']
    return dict(schema='TSL9-TX-source-topology-candidate-review-v1',
                actual_compiler_object_and_IR_read=True,checked_subset_passed=True,
                original_gate_RAs=before,actual_gate_RAs=after,
                original_gate_RA_values_preserved=True,
                bytes=checked['bytes'],instructions=checked['instructions'],
                fits_original_extent=checked['bytes']<=280,
                if_linked_at_original_entry_uncovered_tail_bytes=max(0,280-checked['bytes']),
                component_size_equals_original_extent=checked['bytes']==280,
                actual_original_placement_proved=False,
                original_guard_before_frame=gap['entryguard_precedes_frame'],
                original_restore_frontiers_preserved=gap['source_restore_RA_S1_S2_S3_before_descriptor'] and
                                                       gap['source_S0_restore_precedes_ROMtail_load'],
                original_ABI_admitted=False,whole_image_admitted=False,
                byte_identity_is_acceptance_requirement=False,
                original_unknown_ROM_contract_preservation_proved=False,
                static_checks=checked,
                admissible_changes=p['ADMISSIBLE'],required_observations=p['REQUIRED'],
                target_execution=False,ISA_emulation=False)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--project-root',type=Path,required=True)
    parser.add_argument('--firmware',type=Path,required=True)
    parser.add_argument('--folder',type=Path,required=True)
    parser.add_argument('--receipt',type=Path,required=True)
    args=parser.parse_args()
    result=inspect(args.project_root.resolve(),args.firmware.resolve(),args.folder.resolve())
    if args.receipt.exists():
        raise ValueError('Create-only candidate receipt')
    args.receipt.parent.mkdir(parents=True,exist_ok=True)
    args.receipt.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    print(json.dumps(dict(actual_compiler_object_and_IR_read=True,
                         original_gate_RA_values_preserved=True,bytes=result['bytes'],
                         instructions=result['instructions'],
                         original_ABI_admitted=False,
                         actual_operand_controls=len(result['static_checks']['operand_controls']))))


if __name__=='__main__':
    main()
