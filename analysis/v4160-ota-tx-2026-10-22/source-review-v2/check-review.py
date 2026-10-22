#!/usr/bin/env python3
"""Narrow JSON-shape correction for the immutable original TX source proof."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'source-review'
OLD_SEAL = '46da5762a0bc46c15a04ad6b2bf0f890a001de66b8ac006d0c507529505d76e2'
KEYS = ('decoded_rows', 'direct_local_written_GPRs', 'basic_block_extents', 'raw_operand_controls', 'source_roles', 'source_RELA', 'source_directives', 'incoming_instruction_fields')

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def need(value, message):
    if not value: raise ValueError(message)
def canonical(value): return json.loads(json.dumps(value))
def compare(fresh, selected):
    for key in KEYS:
        need(canonical(fresh[key]) == selected[key], 'Fresh exact raw/source proof ' + key)

def controls(selected):
    import copy
    tuple_shape = copy.deepcopy(selected)
    tuple_shape['basic_block_extents'] = [tuple(v) for v in tuple_shape['basic_block_extents']]
    compare(tuple_shape, selected)
    cases = []
    for name, change in (
        ('tuple_boundary_value', lambda r: r['basic_block_extents'].__setitem__(0, (r['basic_block_extents'][0][0] + 2, r['basic_block_extents'][0][1]))),
        ('list_boundary_value', lambda r: r['basic_block_extents'][0].__setitem__(1, r['basic_block_extents'][0][1] - 2)),
        ('reversed_extent', lambda r: r['basic_block_extents'].__setitem__(0, r['basic_block_extents'][0][::-1])),
        ('missing_extent', lambda r: r['basic_block_extents'].pop()),
        ('tuple_wrong_arity', lambda r: r['basic_block_extents'].__setitem__(0, tuple(r['basic_block_extents'][0]) + (0,))),
    ):
        changed = copy.deepcopy(selected)
        change(changed)
        try: compare(changed, selected)
        except ValueError: cases.append({'case': name, 'rejected': True})
        else: raise ValueError('Accepted structural control ' + name)
    return cases

def inspect(root, firmware, objects=()):
    need(sha(OLD / 'seal.json') == OLD_SEAL, 'Exact immutable original source-review seal')
    original_seal = read(OLD / 'seal.json')
    for name, pin in original_seal['members'].items():
        path = (OLD / name).resolve(strict=True)
        need(path.parent == OLD and sha(path) == pin, 'Original immutable member ' + name)
    if (HERE / 'seal.json').exists():
        for name, pin in read(HERE / 'seal.json')['members'].items():
            path = (HERE / name).resolve(strict=True)
            need(path.parent == HERE and sha(path) == pin, 'V2 immutable member ' + name)
    spec = importlib.util.spec_from_file_location('TX_v2_original_proof', OLD / 'proof.py')
    proof = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(proof)
    fresh = proof.inspect(Path(root).resolve(), Path(firmware).resolve(), objects)
    selected = read(OLD / 'source-proof.json')
    compare(fresh, selected)
    need(fresh['basic_block_extents'] != selected['basic_block_extents'], 'Explicit original tuple/list mismatch reproduced')
    contract = read(OLD / 'contracts.json')
    need(contract['extent']['bytes'] == 280 and contract['extent']['instructions'] == 96 and contract['direct_local_written_GPRs'] == fresh['direct_local_written_GPRs'], 'Unchanged original contract binding')
    rejected = controls(selected)
    return {'passed': True, 'source_bytes': 280, 'instruction_count': 96, 'old_seal_sha256': OLD_SEAL,
            'old_public_checker_tuple_list_failure_reproduced': True, 'json_shape_correction_only': True,
            'raw_source_and40controls_rechecked': True, 'normalization_controls_rejected': len(rejected),
            'normalization_controls': rejected, 'owned_RELA': 11, 'external_incoming': 9,
            'incoming_linked_calls': 8, 'incoming_no_link_tails': 1,
            'selected_actual_carrier_readbacks': selected['actual_archived_carriers_replayed'],
            'actual_archived_carriers_replayed': fresh['actual_archived_carriers_replayed'],
            'actual_carriers': fresh['actual_carriers'], 'bundle_sealed': (HERE / 'seal.json').exists(),
            'reconstructed_C_CPP_tested': False, 'opaque_callee_preservation_proved': False,
            'target_execution': False, 'ISA_emulation': False, 'hardware': False, 'OTA_ready': False}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', type=Path, required=True)
    p.add_argument('--firmware', type=Path, required=True)
    p.add_argument('--object', type=Path, action='append', default=[])
    a = p.parse_args()
    print(json.dumps(inspect(a.project_root, a.firmware, a.object)))
if __name__ == '__main__': main()
