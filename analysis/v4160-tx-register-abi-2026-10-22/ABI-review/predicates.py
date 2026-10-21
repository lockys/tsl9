#!/usr/bin/env python3
"""Source-derived TX ABI predicates; no ISA state execution or emulation."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys

sys.dont_write_bytecode = True
PRIOR = '24ade8f364d00cbc6c7afc2239f13d67fef4f6822647fc4525c05cd9e64bd5eb'


def need(value, message):
    if not value:
        raise ValueError(message)


def H(payload):
    return hashlib.sha256(payload).hexdigest()


def source(root, path):
    direct = root / path
    if direct.is_file():
        return direct
    need(path.startswith('apk-analysis/tsl9-'), 'Known canonical source path')
    return root / ('analysis/' + path[len('apk-analysis/tsl9-'):])


def prior(root):
    path = source(root, 'apk-analysis/tsl9-v4160-ota-tx-2026-10-22/ABI-review/native.py')
    need(H(path.read_bytes()) == PRIOR, 'Immutable previous source/object decoder checks')
    return runpy.run_path(str(path))


def commutative_word_relation(a, b):
    """A syntactic same-operation identity, not evaluation on a virtual CPU."""
    if a['op'] not in ('add', 'mul', 'beq', 'bne') or b['op'] != a['op']:
        return False
    if a['bytes'] != b['bytes'] or a['rd'] != b['rd']:
        return False
    if a['immediate'] != b['immediate'] or a['memory_width'] is not None or b['memory_width'] is not None:
        return False
    if sorted((a['rs1'], a['rs2'])) != sorted((b['rs1'], b['rs2'])):
        return False
    # Branch-PC/target correspondence is a separate obligation. This relation
    # establishes only the symmetric predicate, not control-flow equivalence.
    return True


def word_controls(rows):
    row = next(r for r in rows if r['op'] == 'mul')
    swapped = dict(row, rs1=row['rs2'], rs2=row['rs1'])
    need(commutative_word_relation(row, swapped), 'MUL operand reversal relation')
    results = []
    for name, changed in [('changed_destination', dict(swapped, rd=12)),
                          ('different_operation', dict(swapped, op='and')),
                          ('new_memory_effect', dict(swapped, memory_width=32)),
                          ('different_operand', dict(swapped, rs1=3))]:
        need(not commutative_word_relation(row, changed), 'Reject broader commutation: ' + name)
        results.append(dict(name=name, rejected=True, scope='decoded operand relation, not actual compiled mutant'))
    return results


def inspect(root, firmware, folder):
    n = prior(root)
    context = n['context'](root, firmware)
    original = context['raw']['validate'](context['original'])
    e = context['ELF'](folder / 'tx_native.o')
    symbol, _ = n['object_contract'](e)
    body = e.function_bytes(symbol)
    rows = n['rows'](body, context)
    actual = n['kernel'](rows)
    original_rows = n['rows'](context['original'], context)
    one = n['one']
    old = dict(gates=[r for r in original_rows if r['op'] == 'jalr' and
                     (r['rd'],r['rs1']) == (1,15)],
               guard=one(original_rows, lambda r:r['op']=='bltu' and
                         (r['rs1'],r['rs2'])==(15,13), 'Original unsigned entry guard'),
               frame=one(original_rows, lambda r:r['op']=='addi' and
                         (r['rd'],r['rs1'],r['immediate'])==(2,2,-32), 'Original frame allocation'),
               RAM_PCREL_pair=[one(original_rows,lambda r:r['op']=='auipc' and
                                    r['rd']==13, 'Original resolved RAM PCREL anchor')])
    matches = []
    for a in original:
        for b in rows:
            if commutative_word_relation(a, b) and (a['rs1'], a['rs2']) != (b['rs1'], b['rs2']):
                matches.append(dict(original=a, candidate=b,
                                    same_opcode_and_operand_register_set=True,
                                    incoming_GPR_values_equal_proved=False,
                                    logical_role_correspondence_proved=False,
                                    same_PC_proved=a['PC'] == b['PC'],
                                    same_width_and_destination=True,
                                    control_correspondence_proved=a['op'] not in ('beq', 'bne'),
                                    whole_function_equivalence=False))
    original_gate = [dict(site=r['PC'], RA=r['PC'] + r['bytes']) for r in old['gates']]
    candidate_gate = [dict(site=r['PC'], RA=r['PC'] + r['bytes']) for r in actual['gates']]
    def prefix_saves(rules, first_gate):
        return [dict(PC=r['PC'], GPR=r['rs2'], slot=r['immediate'], width=r['memory_width'])
                for r in rules if r['PC'] < first_gate and r['op']=='sw' and r['rs1']==2]
    original_saves = prefix_saves(original_rows, original_gate[0]['site'])
    candidate_saves = prefix_saves(rows, candidate_gate[0]['site'])
    def store_set(saves):
        return sorted((r['GPR'],r['slot'],r['width']) for r in saves)
    return dict(schema='TSL9-TX-ABI-predicate-frontier-v1', actual_original_and_object_read=True,
                firmware_sha256=H(firmware.read_bytes()), object_sha256=H(e.raw),
                original_bytes=len(context['original']), candidate_bytes=len(body),
                original_gate_links=original_gate, candidate_gate_links=candidate_gate,
                corresponding_gate_RA_equal=[a['RA'] == b['RA'] for a,b in zip(original_gate,candidate_gate)],
                original_prefix_saves=original_saves, candidate_prefix_saves=candidate_saves,
                same_prefix_slot_register_width_set=store_set(original_saves)==store_set(candidate_saves),
                prefix_store_order_equal=[(r['GPR'],r['slot']) for r in original_saves]==
                                        [(r['GPR'],r['slot']) for r in candidate_saves],
                frame_store_commutation_assumptions=['normal completion of every access',
                    'no asynchronous/fault-prefix observation', 'saved source GPRs unmodified before their saves',
                    'common SP and disjoint slot words at the compared completed boundary'],
                original_guard_before_frame=old['guard']['offset'] < old['frame']['offset'],
                candidate_guard_before_frame=actual['guard']['offset'] < actual['frame']['offset'],
                original_RAM_anchor=old['RAM_PCREL_pair'][0]['PC'],
                candidate_RAM_anchor=actual['RAM_PCREL_pair'][0]['PC'],
                RAM_anchor_PC_identity_required=False,
                RAM_same_resolved_A3_and_actual_RELA_pair_required=True,
                commutative_shape_candidates=matches, relation_controls=word_controls(original),
                required_observations=REQUIRED, admissible_changes=ADMISSIBLE,
                original_ABI_admitted=False, whole_image_admitted=False,
                target_execution=False, ISA_emulation=False, physical_ROM_behavior_proved=False)


REQUIRED = {
    'oversized_entry': 'No stack/memory write or saved-register alteration before A3>1039 early return; A0 entrycontext, A5=1039, caller RA/SP retained',
    'frame': 'Live SP minus32; original five fresh word saves at slots24/20/16/12/28 and captures; alias/fault claims require original observable order',
    'opaque_gate': 'Fresh target LW32 at4013C and original live argument/residue GPRs; unknown provider makes RA and live SP/S/GP part of conservative call boundary',
    'gate_two': 'A2/A3 remain post-first-gate residues; A2=1 even on failed second predicate; no invented normalized status',
    'loop': 'Low16 counter compared to live S0, full32 counter addresses, read-before-write forward alias feedback, exact volatile widths/order',
    'success_frame_frontier': 'Fresh RA/S1/S2/S3 restores before descriptor stores; fresh S0 restore before ROM target load; do not commute potentially aliasing memory reads/writes',
    'tail': 'Fresh target LW32 at40050, task LBU through liveGP+94+4lane, A0/A1/A2/A3 and source residues retained, frame restored, JR T1 without new RA',
    'entry_and_roles': 'Preserve all known incoming target/rd/RA and externally retained role bindings; map internal branches and PCREL anchors by actual use, not blanket private-name exemption',
}
ADMISSIBLE = {
    'commutative_ADD_MUL': 'Same width/rd/GPR inputs and u32 operation can swap rs1/rs2; no raw identity requirement. Moved instructions still need dependency/frontier proof',
    'symmetric_BEQ_BNE': 'Operands may reverse with same predicate. Target/PC correspondence must be independently established',
    'local_branch_topology': 'Inversion plus alternate layout may qualify with complete actual CFG/continuation/role proof and no changed observable opaque call boundary; byte identity alone is not the criterion',
    'PCREL_location': 'Anchor may move if genuine HI/LO pairing resolves the same numeric data symbol into A3, uses stay ordered, and no known incoming/retained anchor role is lost',
    'frame_memory_commutation': 'Only with a separately established no-alias/no-fault/no-interrupt assumption for the claimed scope; current unknown ROM and raw source do not establish it',
    'ordinary_C_entry_split': 'A no-frame guard wrapper and musttail body are a possible source topology, not admitted until actual native prefix, RA/SP/GPR residue and total extent are audited',
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument('--firmware', type=Path, required=True)
    parser.add_argument('--folder', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    result = inspect(args.project_root.resolve(), args.firmware.resolve(), args.folder.resolve())
    need(not args.receipt.exists(), 'Create-only predicate receipt')
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
    print(json.dumps(dict(actual_original_and_object_read=True,
                         corresponding_gate_RA_equal=result['corresponding_gate_RA_equal'],
                         original_ABI_admitted=False, predicate_controls=len(result['relation_controls']))))


if __name__ == '__main__':
    main()
