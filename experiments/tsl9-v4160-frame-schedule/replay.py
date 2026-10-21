"""Read-only replay of explicit ABI scheduling against both actual objects."""
import argparse
import json
from pathlib import Path

import schedule as S


def replay(root, receipt):
    root, receipt = root.resolve(), receipt.resolve()
    S.need(receipt.is_relative_to(root), 'Receipt remains inside the project')
    value = json.loads(receipt.read_bytes())
    source = (root / value['input']['path']).resolve()
    destination = (root / value['output']['path']).resolve()
    S.need(all(p.is_relative_to(root) for p in (source, destination)), 'Explicit project-local objects')
    S.need(len({source, destination, receipt}) == 3, 'Three distinct actual artifact paths')
    policy_path = S.HERE / 'frame-policy.json'
    policy = json.loads(policy_path.read_bytes())
    ELF = S.load_parser(root)
    before, after = ELF(source), ELF(destination)
    selected = [item['function'] for item in value['functions']]
    payload, proofs, changed = S.plan(before, policy, selected)
    S.need(after.raw == payload, 'Actual output equals the complete planned input permutation')
    S.need(before.sections == after.sections and before.symbols == after.symbols
           and before.relocations == after.relocations, 'Identical actual metadata, symbols and RELA')
    expected = dict(
        schema='TSL9-explicit-ABI-frame-scheduling-receipt-v1', passed=True,
        tool_sha256=S.digest(Path(S.__file__).read_bytes()),
        policy_sha256=S.digest(policy_path.read_bytes()), parser_sha256=S.PARSER_SHA,
        input=dict(path=source.relative_to(root).as_posix(), bytes=len(before.raw), sha256=S.digest(before.raw)),
        output=dict(path=destination.relative_to(root).as_posix(), bytes=len(payload), sha256=S.digest(payload)),
        functions=proofs, changed_file_offsets=changed, section_metadata_symbols_RELA_identical=True,
        original_BIN_read_for_generation=False, new_opcodes_generated=False, padding_added=False,
        pipeline='C/C++ compiler output followed by explicit source-owned ABI frame scheduling',
        compiler_alone_emitted_scheduled_order=False, computed_interior_entries_proved_absent=False,
        target_execution=False, ISA_emulation=False, hardware=False, OTA_ready=False)
    S.need(value == expected, 'Complete receipt matches current tools, policy and both actual objects')
    return dict(passed=True, actual_objects_replayed=2, functions=len(proofs), changed_bytes=len(changed),
                input_sha256=expected['input']['sha256'], output_sha256=expected['output']['sha256'],
                receipt_sha256=S.digest(receipt.read_bytes()), read_only=True,
                original_BIN_read_for_generation=False, target_execution=False, OTA_ready=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=Path, default=S.HERE.parents[1])
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(replay(args.project_root, args.receipt)))
