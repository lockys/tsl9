"""Actual-object scheduling/replay checks; no target code is executed."""
import argparse
import copy
import json
from pathlib import Path

import replay as R
import schedule as S


def create(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as out:
        out.write(payload)


def encoded(value):
    return (json.dumps(value, indent=2) + '\n').encode('utf8')


def verify(root, inputs, build):
    root, build = root.resolve(), build.resolve()
    S.need(build.is_relative_to(root) and not build.exists(), 'Fresh project-local verification directory')
    results = []
    for mode, source in inputs:
        directory = build / mode
        output, receipt = directory / 'scheduled.o', directory / 'scheduling.json'
        value = S.transform(root, source, output, receipt, ['irq', 'quarter'])
        actual = R.replay(root, receipt)
        S.need(actual['changed_bytes'] == 14, 'Exactly four IRQ and three quarter save halfwords reordered')
        negatives = []

        def reject(name, mutant):
            path = directory / 'controls' / (name + '.json')
            create(path, encoded(mutant))
            try:
                R.replay(root, path)
            except (ValueError, KeyError, IndexError):
                negatives.append(dict(name=name, rejected=True, receipt_sha256=S.digest(path.read_bytes())))
            else:
                raise ValueError('Accepted actual control ' + name)

        mutant = copy.deepcopy(value)
        mutant['tool_sha256'] = '0' * 64
        reject('stale-tool', mutant)
        mutant = copy.deepcopy(value)
        mutant['compiler_alone_emitted_scheduled_order'] = True
        reject('compiler-alone-claim', mutant)
        mutant = copy.deepcopy(value)
        mutant['changed_file_offsets'] = mutant['changed_file_offsets'][:-1]
        reject('incomplete-changed-offsets', mutant)
        mutant = copy.deepcopy(value)
        mutant['output']['bytes'] += 1
        reject('false-output-size', mutant)
        mutant = copy.deepcopy(value)
        mutant['input'], mutant['output'] = mutant['output'], mutant['input']
        reject('reversed-input-output', mutant)

        for name, at in [('output-slot-tamper', value['changed_file_offsets'][0]),
                         ('output-unrelated-tamper', len(output.read_bytes()) - 1)]:
            data = bytearray(output.read_bytes())
            data[at] ^= 1
            forged = directory / 'controls' / (name + '.o')
            create(forged, data)
            mutant = copy.deepcopy(value)
            mutant['output'] = dict(path=forged.relative_to(root).as_posix(), bytes=len(data), sha256=S.digest(data))
            reject(name, mutant)
        results.append(dict(mode=mode, positive=actual, receipt=receipt.relative_to(root).as_posix(),
                            actual_receipt_controls=negatives))
    report = dict(schema='TSL9-frame-schedule-actual-object-verification-v1', passed=True,
                  driver_sha256=S.digest(Path(__file__).read_bytes()),
                  replay_sha256=S.digest(Path(R.__file__).read_bytes()),
                  scheduling_sha256=S.digest(Path(S.__file__).read_bytes()), results=results,
                  fresh_C_CPP_compilation=False, actual_archived_input_objects=True,
                  target_execution=False, ISA_emulation=False, hardware=False, OTA_ready=False)
    create(build / 'verification.json', encoded(report))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=Path, default=S.HERE.parents[1])
    parser.add_argument('--input-c', type=Path, required=True)
    parser.add_argument('--input-cpp', type=Path, required=True)
    parser.add_argument('--build-root', type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.project_root, [('c', args.input_c), ('cpp', args.input_cpp)], args.build_root)
    print(json.dumps(dict(passed=True, actual_input_objects=2, scheduled_and_replayed_objects=2,
                         receipt_controls_per_language=7, fresh_C_CPP_compilation=False,
                         report=str(args.build_root / 'verification.json'), target_execution=False, OTA_ready=False)))
