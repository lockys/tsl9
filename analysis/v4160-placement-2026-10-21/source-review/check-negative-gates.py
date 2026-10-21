#!/usr/bin/env python3
"""Bounded ownership/reference controls, not a firmware placement solver."""
import copy
import json
import importlib.util
from pathlib import Path

def main():
    root=Path(__file__).resolve().parent
    spec=importlib.util.spec_from_file_location('placement_reference_gate',root/'check-placement.py')
    checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
    original=json.loads((root/'reference-inventory.json').read_text(encoding='utf-8'))
    ranges={x['name']:x for x in original['owned_ranges']}
    rejected=[]
    for label,name,size in [('reset_leaf_78','reset_memory',78),('reset_fragment_80','reset_memory',80),
                            ('query_196','query',196),('false_irq_original_176','irq_init',176)]:
        r=ranges[name]
        if r['start']+size<=r['end_exclusive']:
            raise ValueError('Ownership overrun unexpectedly admitted')
        rejected.append({'control':label,'requested_bytes':size,'owned_bytes':r['bytes'],
                         'overrun_bytes':size-r['bytes'],'rejected':True})
    transcript=[]
    bad=copy.deepcopy(original);bad['owned_ranges'][3]['bytes']=176
    transcript.append(('wrong_original_irq_extent',bad))
    bad=copy.deepcopy(original);bad['owned_ranges'][4]['bytes']=22
    transcript.append(('wrong_original_helper_extent',bad))
    for address,label in [(0x99f2,'omit_other_helper_caller'),(0x18906,'omit_tail_caller')]:
        bad=copy.deepcopy(original)
        bad['known_direct_references']=[x for x in bad['known_direct_references'] if x['source']!=address]
        transcript.append((label,bad))
    bad=copy.deepcopy(original);bad['relocation_references']=[x for x in bad['relocation_references'] if x['type']!=24]
    transcript.append(('erase_PCREL_anchor_constraints',bad))
    bad=copy.deepcopy(original);bad['unknown_computed_targets_excluded']=True
    transcript.append(('invent_computed_target_absence',bad))
    bad=copy.deepcopy(original);bad['padding_free_space_proved']=True
    transcript.append(('invent_free_padding',bad))
    bad=copy.deepcopy(original);bad['known_indirect_transfers']['count']=0
    transcript.append(('erase_unknown_indirect_inventory',bad))
    for name,bad in transcript:
        try:
            checker.validate_reference(original,bad)
        except ValueError:
            pass
        else:
            raise ValueError('Changed reference transcript admitted: '+name)
    fits=[{'name':'fields38','requested_bytes':38,'owned_bytes':ranges['fields']['bytes'],
           'capacity_only':38<=ranges['fields']['bytes'],'ABI_or_placement_proved':False},
          {'name':'old_irq118','requested_bytes':118,'owned_bytes':ranges['irq_init']['bytes'],
           'capacity_only':118<=ranges['irq_init']['bytes'],'ABI_or_placement_proved':False}]
    print(json.dumps({'passed':True,'ownership_overrun_controls':rejected,
                      'reference_transcript_mutations_rejected':[x[0] for x in transcript],
                      'capacity_only_counterexamples':fits,'native_compiled_controls':0,
                      'firmware_placement_accepted':False,'new_BIN_produced':False,
                      'target_execution':False,'ISA_emulation':False,'hardware':False},indent=2))

if __name__=='__main__':main()
