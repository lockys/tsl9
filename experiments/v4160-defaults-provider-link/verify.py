"""Link the bounded defaults OBJECT with a pinned fresh-source APP aggregate."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
NAME = 'tsl9_settings_default_data_1a69c'
SECTION = '.rodata.tsl9_defaults_read_window_1a69c'
IMAGE_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
WITNESSES = {'tsl9_boot_resident_40000': 0x40000, 'tsl9_incoming_external_14056': 0x14056,
             'tsl9_input_state_decoders_static_data_1ab48': 0x1ab48,
             'tsl9_record_field_transitions_static_data_1a078': 0x1a078,
             'tsl9_registered_callbacks_static_data_1a638': 0x1a638,
             '__tsl9v4160_data_2000b18c': 0x2000b18c}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args, successful=True):
    result = subprocess.run([str(x) for x in args], capture_output=True, text=True, timeout=120)
    if successful:
        need(result.returncode == 0, 'compiler/linker command failed: ' + result.stderr[:600])
    return result


def facts(path, ELF):
    e = ELF(path)
    need(e.header[0] == 1 and not e.program_headers, 'nonloadable ET_REL input')
    sections = {s['name']: (s['type'], s['flags'], s['align'], s['size'], None if s['type'] == 8 else e.data(s))
                for s in e.sections if s['flags'] & 2 and s['size']}
    owners = {s['name']: (s['info'], s['other'], 'ABS' if s['section'] == 0xfff1 else e.sections[s['section']]['name'], s['value'], s['size'])
              for s in e.symbols if s['info'] >> 4 and s['section']}
    undefined = {s['name'] for s in e.symbols if s['info'] >> 4 and not s['section']}
    relocations = sorted((e.sections[v['section']]['name'], v['offset'], v['type'], v['addend'], e.symbols[v['symbol']]['name'])
                         for v in e.relocations)
    return sections, owners, undefined, relocations


def mapped(e):
    memory = {}
    for s in e.sections:
        if s['flags'] & 2 and s['size']:
            data = e.data(s)
            need(len(data) == s['size'], 'file-backed diagnostic section')
            for i, byte in enumerate(data):
                address = s['address'] + i
                need(address not in memory, 'no overlapping coordinate bytes')
                memory[address] = byte
    return memory


def validate_unit(path, ELF, facts):
    sections, owners, undefined, relocations = facts(path, ELF)
    need(sections == {SECTION: (1, 2, 1, 4, bytes.fromhex('31323334'))}, 'exact four-byte readonly defaults section')
    need(owners == {NAME: (17, 0, SECTION, 0, 4)}, 'one four-byte global OBJECT provider')
    need(not undefined and not relocations, 'defaults OBJECT has no imported or relocated bytes')


def original_consumer(image):
    raw = image[0x131a0 - 0x8000:0x131b6 - 0x8000]
    need(raw.hex() == '938741058843fc441146977500009385254f31058297', 'original caller window')
    hi = int.from_bytes(raw[10:14], 'little')
    lo = int.from_bytes(raw[14:18], 'little')
    need(hi & 0x7f == 0x17 and hi >> 7 & 31 == 11, 'AUIPC A1')
    need(lo & 0x707f == 0x13 and lo >> 7 & 31 == 11 and lo >> 15 & 31 == 11, 'ADDI A1,A1')
    immediate = lo >> 20
    if immediate & 0x800:
        immediate -= 4096
    need((0x131aa + (hi & 0xfffff000) + immediate) & 0xffffffff == 0x1a69c, 'original caller forms exact source address')
    need(raw[8:10] == bytes.fromhex('1146'), 'original C.LI A2,4')
    return {'pointer_hi_PC': '0x131aa', 'pointer_low_PC': '0x131ae', 'source_address': '0x1a69c',
            'requested_length': 4, 'indirect_call_PC': '0x131b4', 'actual_provider_behavior_proved': False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tool-dir', type=Path, required=True)
    parser.add_argument('--parent-build', type=Path, required=True, help='Pinned compact build directory containing source/ and diagnostic-c.ld')
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    spec = json.loads((HERE / 'inputs.json').read_bytes())
    for path, digest in spec['project_pins'].items():
        need(sha(ROOT / path) == digest, 'project input identity: ' + path)
    for path, digest in spec['parent_pins'].items():
        need(sha(args.parent_build / path) == digest, 'frozen fresh-source parent identity: ' + path)
    tools = {name: next(p for p in [args.tool_dir / (name + '.exe'), args.tool_dir / name] if p.is_file())
             for name in ('clang', 'ld.lld')}
    for name, digest in spec['tools'].items():
        need(sha(tools[name]) == digest, 'tool identity: ' + name)
    ELF = runpy.run_path(str(HERE / 'elf_reader.py'))['ELF']
    image_path = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
    need(sha(image_path) == IMAGE_SHA, 'original image identity')
    image = image_path.read_bytes()
    need(len(image) == 76800 and image[0x1269c:0x126a0] == bytes.fromhex('31323334'), 'original four-byte source window')
    consumer = original_consumer(image)
    out = args.output_dir.resolve()
    need(not out.exists() and out.parent.is_dir(), 'new output directory required')
    out.mkdir()
    modes = {}
    for mode, language, standard in [('c', 'c', 'c11'), ('cpp', 'c++', 'c++17')]:
        parent = args.parent_build / 'source' / ('NOT-FLASHABLE-candidate-aliases-' + mode + '.o')
        before = facts(parent, ELF)
        need(before[2] == set(WITNESSES) | {NAME, 'tsl9_runtime_reset_stack_top'}, 'exact eight genuine parent dependencies')
        refs = [r for r in before[3] if r[-1] == NAME]
        need(refs == [('.text.tsl9_settings_defaults_block_1318a', 32, 23, 0, NAME)],
             'one actual parent PCREL_HI20 at1318a+32=131aa')
        unit, linked = out / (mode + '-defaults.o'), out / (mode + '-linked.o')
        run([tools['clang'], '--target=riscv32-unknown-elf', '-march=rv32imac_zicsr', '-mabi=ilp32',
             '-ffreestanding', '-Oz', '-x', language, '-std=' + standard, '-c', HERE / 'defaults.c', '-o', unit])
        validate_unit(unit, ELF, facts)
        added = facts(unit, ELF)
        need(not set(before[0]) & set(added[0]) and not set(before[1]) & set(added[1]),
             'new section and global owner do not replace any parent definition')
        run([tools['ld.lld'], '-m', 'elf32lriscv', '-r', '--no-relax', parent, unit, '-o', linked])
        after = facts(linked, ELF)
        need(after == ({**before[0], **added[0]}, {**before[1], **added[1]}, before[2] - {NAME}, before[3]),
             'all parent allocated sections, global/weak definitions and relocation roles retained; only defaults UND resolved')
        base = ELF(args.parent_build / ('NOT-FLASHABLE-compact-source-layout-' + mode + '.elf'))
        old_bytes = mapped(base)
        need(len(old_bytes) == 73672 and not set(range(0x1a69c, 0x1a6a0)) & old_bytes.keys(), 'parent 73672 bytes and free defaults gap')
        script = (args.parent_build / ('diagnostic-' + mode + '.ld')).read_text('utf-8')
        need(script.count('SECTIONS {\n') == 1, 'one parent layout anchor')
        insertion = ' .defaults_source 0x1a69c : SUBALIGN(1) { KEEP(*(' + SECTION + ')) } :NONE\n'
        layout = out / (mode + '.ld')
        layout.write_text(script.replace('SECTIONS {\n', 'SECTIONS {\n' + insertion), encoding='utf-8')
        command = [tools['ld.lld'], '--no-undefined', '--no-relax', '-T', layout, linked]
        strict_path = out / (mode + '-STRICT.elf')
        strict = run([*command, '-o', strict_path], successful=False)
        missing = set(re.findall(r'undefined symbol: ([^\r\n]+)', strict.stderr))
        need(strict.returncode != 0 and missing == set(WITNESSES) and not strict_path.exists(), 'strict link now has exactly six remaining dependencies')
        # Omit the new OBJECT: the real consumer must still require its provider.
        negative = run([tools['ld.lld'], '--no-undefined', '--no-relax', '-T', layout, parent,
                        *['--defsym=' + k + '=' + hex(v) for k, v in WITNESSES.items()],
                        '-o', out / (mode + '-MISSING.elf')], successful=False)
        need(negative.returncode != 0 and set(re.findall(r'undefined symbol: ([^\r\n]+)', negative.stderr)) == {NAME},
             'omitting defaults source leaves its genuine consumer unresolved')
        diagnostic = out / (mode + '-NONLOADABLE.elf')
        run([*command, *['--defsym=' + k + '=' + hex(v) for k, v in WITNESSES.items()], '-o', diagnostic])
        e = ELF(diagnostic)
        current = mapped(e)
        need(all(current.get(p) == b for p, b in old_bytes.items()), 'every parent original-coordinate byte retained')
        need({p: current[p] for p in current.keys() - old_bytes.keys()}
             == dict(zip(range(0x1a69c, 0x1a6a0), bytes.fromhex('31323334'))), 'exactly four original defaults bytes added')
        symbol = [s for s in e.symbols if s['name'] == NAME]
        need(len(symbol) == 1 and (symbol[0]['value'], symbol[0]['size'], symbol[0]['info']) == (0x1a69c, 4, 17)
             and symbol[0]['section'] not in (0, 0xfff1), 'real section-backed four-byte provider, not numeric alias')
        section = e.sections[symbol[0]['section']]
        need((section['type'], section['flags'], section['address'], section['size']) == (1, 2, 0x1a69c, 4),
             'final provider occupies precisely one readonly four-byte section')
        need(len(current) == 73676 and e.header[3] == 0 and not any(p[0] == 1 for p in e.program_headers), 'nonloadable extended diagnostic')
        difference = [p for p, b in current.items() if b != image[p - 0x8000]]
        need(len(difference) == 93 and all(0x8a56 <= p < 0x8b6e for p in difference), 'only inherited 93-byte TX candidate difference')
        modes[mode] = {'parent_UND': 8, 'partial_link_UND': sorted(after[2]), 'strict_UND': sorted(missing),
                       'parent_coordinate_bytes_retained': 73672, 'extended_bytes': 73676, 'added_bytes': 4,
                       'consumer_PCREL_HI20_references': len(refs), 'missing_source_rejected': True,
                       'selected_bytes_sha256': hashlib.sha256(bytes(current[p] for p in sorted(current))).hexdigest(),
                       'diagnostic_sha256': sha(diagnostic), 'original_TX_different_bytes': len(difference)}
    need(modes['c']['selected_bytes_sha256'] == modes['cpp']['selected_bytes_sha256'], 'C/C++ original-coordinate bytes equal')
    for path, digest in spec['parent_pins'].items():
        need(sha(args.parent_build / path) == digest, 'parent inputs unchanged after link')
    result = {'passed': True, 'consumer': consumer, 'modes': modes, 'provider_resolved': NAME,
              'defaults_are_observed_opaque_literal': True, 'unified_manifest_updated': False,
              'main_build_pipeline_modified': False, 'new_flashable_BIN': False, 'target_executed': False,
              'inputs_sha256': {p.name: sha(p) for p in [HERE / 'verify.py', HERE / 'defaults.c', HERE / 'inputs.json',
                                                        HERE / 'elf_reader.py', HERE / 'test_unit.py']}}
    (out / 'receipt.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
