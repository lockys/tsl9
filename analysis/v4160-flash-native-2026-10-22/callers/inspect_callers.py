"""Decode bounded original call arguments; no target execution or hardware I/O."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMAGE_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
SOURCE_SEAL = 'dff9a51e3b59bbdddd150dde37614753bb3c3b440d7bde2f9402c8b6e9a2bce4'
PARSER_SHA = '00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
SITES = ((0x12e7a, 0x08077900), (0x12f0c, 0x08077800),
         (0x12f6e, 0x08077700), (0x13078, 0x08077600),
         (0x130fc, 0x08077500), (0x1315e, 0x08077a00))
RECEIVER_SEALS = {
    'flash-reachability/seal.json': 'b30898df66749a5c1ef5600eb53827ae999638044b87c6da1a216a39a2677b19',
    'boot-variants/seal.json': '6b1e505acbdf24fc17760a5cdb00e1e8102c648be5a4c8bfb455048c21d442f2',
}


def need(value, text):
    if not value:
        raise ValueError(text)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf8'))


def write_new(path, value):
    raw = (json.dumps(value, indent=2, sort_keys=True)+'\n').encode('utf8')
    if path.exists():
        need(path.read_bytes() == raw, 'Existing immutable output differs: '+path.name)
    else:
        with path.open('xb') as out:
            out.write(raw)


def scope(root, name):
    for path in (root/'analysis'/name, root/'apk-analysis'/('tsl9-'+name)):
        if path.is_dir():
            return path
    raise ValueError('Missing evidence scope: '+name)


def signed(value, bits):
    return value-(1 << bits) if value & (1 << (bits-1)) else value


def members_unchanged(path):
    seal = read(path)
    members = seal.get('members', seal.get('files'))
    need(members, 'Nonempty retained evidence seal')
    rows = [dict(path=n, sha256=h) for n, h in members.items()] if isinstance(members, dict) else members
    for item in rows:
        actual = (path.parent/item['path']).resolve()
        need(actual.is_relative_to(path.parent.resolve()) and sha(actual) == item['sha256'], 'Unchanged retained source member')


def decode(raw, call_pc, expected):
    need(len(raw) == 14, 'Exactly four complete source instructions')
    lui, move, addi, jal = (int.from_bytes(raw[a:b], 'little')
                            for a, b in ((0, 4), (4, 6), (6, 10), (10, 14)))
    need(lui & 127 == 0x37 and (lui >> 7) & 31 == 10, 'LUI writes original A0')
    need(move == 0x858a, 'C.MV copies live SP into A1')
    need(addi & 0x707f == 0x13 and (addi >> 7) & 31 == 10
         and (addi >> 15) & 31 == 10, 'ADDI reads and writes A0')
    upper, offset = lui & 0xfffff000, signed(addi >> 20, 12)
    address = (upper+offset) & 0xffffffff
    need(address == expected and address & 255 == 0, 'Exact source-bound aligned destination')
    need(jal & 127 == 0x6f and (jal >> 7) & 31 == 1, 'Four-byte JAL writes RA')
    immediate = (((jal >> 31) & 1) << 20) | (((jal >> 21) & 1023) << 1)
    immediate |= (((jal >> 20) & 1) << 11) | (((jal >> 12) & 255) << 12)
    target = (call_pc+signed(immediate, 21)) & 0xffffffff
    need(target == 0x9c0a, 'Actual direct quarter-helper target')
    return dict(call_pc=call_pc, start=call_pc-10, end_exclusive=call_pc+4,
                instructions=4, raw_hex=raw.hex(), upper=upper, signed_addend=offset,
                A0_destination=address, A1='live SP at the source C.MV', target=target,
                RA=call_pc+4, known_write_extent=[address, address+256])


def source_report(image):
    need(len(image) == 76800, 'Original complete image size')
    rows, controls = [], []
    mutations = ((0, 7, 'LUI destination'), (0, 12, 'LUI upper immediate'),
                 (4, 7, 'C.MV destination'), (4, 2, 'C.MV source'),
                 (6, 15, 'ADDI input'), (6, 20, 'ADDI low immediate'),
                 (6, 31, 'ADDI sign'), (10, 0, 'JAL opcode'),
                 (10, 7, 'JAL destination'), (10, 31, 'JAL target'))
    for pc, address in SITES:
        raw = image[pc-10-0x8000:pc+4-0x8000]
        rows.append(decode(raw, pc, address))
        for start, bit, label in mutations:
            changed = bytearray(raw)
            changed[start+bit//8] ^= 1 << (bit % 8)
            try:
                decode(bytes(changed), pc, address)
            except ValueError as error:
                controls.append(dict(call_pc=pc, case=label, rejected=True, reason=str(error)))
            else:
                raise ValueError('Raw mutation unexpectedly admitted')
    # Semantic controls run on their actual four-instruction slice before this
    # whole-file identity gate, so rejection is not merely a digest mismatch.
    need(hashlib.sha256(image).hexdigest() == IMAGE_SHA, 'Exact original ID2966 source')
    need(len(rows) == 6 and len(controls) == 60, 'All selected calls and ten controls each')
    return dict(schema='TSL9-V4160-generic-Flash-quarter-callers-v1', passed=True,
                original_image_sha256=IMAGE_SHA, original_bytes=76800,
                selected_source_bytes=84, selected_instructions=24, calls=rows,
                semantic_raw_negative_controls=controls,
                receiver_envelopes=dict(BOOT_receiver_writes_Runtime=[0x08008000, 0x08020000],
                                        Runtime_receiver_writes_BOOT=[0x08001000, 0x08008000],
                                        bounds_are_outer_receiver_guards=True,
                                        not_a_physical_Flash_capacity_measurement=True),
                conclusion='The quarter helper has confirmed non-OTA call slices outside both outer receiver envelopes; do not add those envelopes to the generic primitive.',
                limits=dict(execution_reachability_proved=False, actual_SP_known=False,
                            settings_semantics_confirmed=False, physical_capacity_proved=False,
                            installed_chip_identified=False, original_execution=False,
                            ISA_emulation=False, hardware=False, network=False, OTA_ready=False))


def elf_crosscheck(root, path, report, original):
    parser = scope(root, 'v4160-irq-native-2026-10-21')/'compiler-review/elf32.py'
    need(sha(parser) == PARSER_SHA, 'Exact retained ELF parser')
    spec = importlib.util.spec_from_file_location('caller_elf', parser)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    elf, owners = module.ELF(path), []
    need(elf.kind == 2, 'Actual linked source-image ELF')
    for row in report['calls']:
        choices = [s for s in elf.sections if s['flags'] & 2 and s['type'] == 1
                   and s['address'] <= row['start'] < row['end_exclusive'] <= s['address']+s['size']]
        need(len(choices) == 1, 'Every slice has exactly one actual allocated owner')
        owner = choices[0]
        need(owner['flags'] & 4, 'Actual executable source section')
        body = elf.data(owner)
        need(body == original[owner['address']-0x8000:owner['address']+owner['size']-0x8000],
             'Every byte of the actual caller owner remains original')
        entries = [s for s in elf.symbols if s['index'] == owner['index'] and s['info'] & 15 == 2
                   and s['value'] == owner['address'] and s['size'] == owner['size']]
        need(entries, 'Actual section-backed whole-function entry role')
        offset = row['start']-owner['address']
        need(body[offset:offset+14].hex() == row['raw_hex'], 'Actual compiled source bytes equal original slice')
        # Assemblers discard unreferenced .L labels. Establish widths from the
        # real declared FUNC entry rather than pretending every label survived.
        boundaries, position = set(), 0
        while position < len(body):
            boundaries.add(owner['address']+position)
            half = int.from_bytes(body[position:position+2], 'little')
            width = 2 if half & 3 != 3 else 4
            need(width == 2 or half & 31 != 31, 'Only admitted 16/32-bit instruction widths')
            need(position+width <= len(body), 'Whole-owner width walk is bounded')
            position += width
        need(all(row['start']+n in boundaries for n in (0, 4, 6, 10)), 'All four original instructions lie on admitted width boundaries')
        owners.append(dict(call_pc=row['call_pc'], owner=owner['name'],
                           owner_sha256=hashlib.sha256(body).hexdigest(),
                           source_entry=owner['address'], original_instruction_boundaries=True,
                           boundary_method='16/32-bit width walk from actual original FUNC entry'))
    return dict(passed=True, ELF_sha256=sha(path), parser_sha256=PARSER_SHA, slices=owners,
                target_execution=False, hardware=False, numeric_ROM_witness_is_not_ROM_proof=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=Path, default=HERE.parents[2])
    parser.add_argument('--firmware', type=Path)
    parser.add_argument('--elf', type=Path)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--seal', action='store_true')
    args = parser.parse_args()
    root = args.project_root.resolve()
    source = scope(root, 'v4160-flash-native-2026-10-22')/'source'
    need(sha(source/'seal.json') == SOURCE_SEAL, 'Independent six-function source seal')
    members_unchanged(source/'seal.json')
    receiver = scope(root, 'v4160-ota-route-2026-10-21')
    for name, pin in RECEIVER_SEALS.items():
        need(sha(receiver/name) == pin, 'Frozen original-source receiver guard proof')
        members_unchanged(receiver/name)
    references = dict(source_seal_sha256=SOURCE_SEAL, receiver_seal_sha256=RECEIVER_SEALS,
                      guard_ranges_are_not_a_physical_capacity_measurement=True,
                      source_proofs_reused_without_claiming_new_execution=True)
    candidates = [args.firmware] if args.firmware else [
        root/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin',
        root/'exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin']
    image_path = next((p for p in candidates if p is not None and p.is_file()), None)
    need(image_path is not None, 'Missing fixed original Runtime image')
    original = image_path.read_bytes()
    report = source_report(original)
    if args.check:
        need(read(HERE/'report.json') == report, 'Exact source replay')
        need(read(HERE/'receiver-evidence.json') == references, 'Exact retained receiver evidence')
    else:
        write_new(HERE/'report.json', report)
        write_new(HERE/'receiver-evidence.json', references)
    compiled = elf_crosscheck(root, args.elf.resolve(), report, original) if args.elf else None
    if args.elf and not args.check:
        write_new(HERE/'compiled-crosscheck.json', compiled)
    if args.seal:
        names = ('inspect_callers.py', 'inspect_callers.sh', 'report.json', 'receiver-evidence.json', 'compiled-crosscheck.json', 'README.md', 'readme.zh-TW.md', 'readme.en.md')
        write_new(HERE/'seal.json', dict(schema='TSL9-generic-Flash-callers-seal-v1',
            members=[dict(path=n, bytes=(HERE/n).stat().st_size, sha256=sha(HERE/n)) for n in names]))
    if (HERE/'seal.json').exists():
        for item in read(HERE/'seal.json')['members']:
            path = (HERE/item['path']).resolve()
            need(path.is_relative_to(HERE) and sha(path) == item['sha256'] and path.stat().st_size == item['bytes'], 'Exact sealed caller evidence')
    print(json.dumps(dict(passed=True, source_bytes=84, source_instructions=24, raw_controls=60,
                          actual_ELF_checked=compiled is not None, report_sha256=sha(HERE/'report.json'),
                          physical_capacity_proved=False, OTA_ready=False)))


if __name__ == '__main__':
    main()
