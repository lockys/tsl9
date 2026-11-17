"""Strict parsing and comparison of per-mode aggregate undefined inventories."""
import json

MODES = ('c', 'cpp')


def inventory(stderr, label, mode, count):
    if mode not in MODES:
        raise ValueError('invalid mode')
    prefix = label + ' '
    records = [line[len(prefix):] for line in stderr.splitlines() if line.startswith(prefix)]
    if len(records) != 1 or not records[0].startswith(mode + ' '):
        raise ValueError('missing, duplicate or wrong-mode inventory')
    names = json.loads(records[0][len(mode) + 1:])
    if not isinstance(names, list) or len(names) != count or any(not isinstance(x, str) or not x for x in names) or len(set(names)) != count:
        raise ValueError('malformed inventory')
    return set(names)


def exact_delta(baseline, observed, case):
    if len(baseline) != 81 or 'negative_extra' in baseline or 'tsl9_ab72_data' not in baseline:
        return False
    if case == 'extra-undefined':
        return observed == baseline | {'negative_extra'}
    if case == 'missing-witness':
        return observed == baseline - {'tsl9_ab72_data'}
    raise ValueError('invalid case')
