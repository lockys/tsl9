"""Enumerate static address ownership; no payload reads or target execution."""
import collections, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAP = ROOT / 'experiments/tsl9-original-layout/build/event-word-table-data-v1/c/layout-map.json'
EXPECTED = '1905c36e2d059e14674dd054430c8049da77c53a4eabbf56d3ef9aa981a2ac71'
data = MAP.read_bytes()
if hashlib.sha256(data).hexdigest() != EXPECTED:
    raise SystemExit('Layout map differs from the reviewed input')
mapping = json.loads(data)
owners = [o for o in mapping['owners'] if o['info'] == 17]
def owner(start, end):
    matches = [o for o in owners if o['original_PC'] <= start and o['original_PC'] + o['bytes'] >= end]
    if len(matches) > 1:
        raise ValueError('Overlapping complete DATA owners')
    return matches[0]['name'] if matches else None
def classify(base, width):
    groups = collections.defaultdict(list)
    for index in range(256):
        name = owner(base + width * index, base + width * (index + 1))
        if name is not None:
            groups[name].append(index)
    return groups
counter = classify(0x1ab48, 2)
rows = classify(0x1a078, 16)
expected_counter = {
    'tsl9_input_counter_read_window_1ab48': list(range(0, 4)),
    'tsl9_remaining_record_dispatch_static_data_1ab50': list(range(4, 8)),
    'tsl9_runtime_service_threshold_bytes_1ab58': list(range(8, 12)),
    'tsl9_runtime_reset_initializer': list(range(12, 76)),
}
if dict(counter) != expected_counter or sum(map(len, rows.values())) != 149:
    raise SystemExit('Ownership differs from the reviewed enumeration')
sequence = collections.Counter()
for channel in range(4):
    for state in range(256):
        start = 0x1a638 + 6 * (2 * channel + state)
        end = start + 6
        if start < 0x1a6a0 and end > 0x1a69c:
            category = 'excluded'
        elif start < 0x8000 or end > 0x1ac00:
            category = 'outside'
        else:
            name = owner(start, end)
            category = ('dedicated' if name == 'tsl9_sequence_compare_read_window_1a638'
                        else 'other_owner' if name else 'multiple_or_missing')
        sequence[category] += 1
expected_sequence = {'dedicated': 20, 'other_owner': 872, 'excluded': 8,
                     'outside': 52, 'multiple_or_missing': 72}
if dict(sequence) != expected_sequence:
    raise SystemExit('Sequence ownership differs from the reviewed enumeration')
print(json.dumps({'passed': True, 'input_counter_indices': 256,
    'single_data_owner_indices': 76, 'dedicated_window_indices': 4,
    'other_owner_indices': 72, 'not_single_owner_indices': 180,
    'mode_rows': 256, 'single_data_owner_rows': 149,
    'not_single_owner_rows': 107, 'sequence_channel_state_pairs': 1024,
    'sequence_owner_categories': dict(sequence), 'semantic_membership_proved': False,
    'runtime_reachability_proved': False, 'payload_read': False,
    'target_executed': False}, sort_keys=True))
