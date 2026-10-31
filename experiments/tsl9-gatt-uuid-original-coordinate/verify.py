"""Build a bounded GATT UUID diagnostic from retained sources; never execute target."""
import argparse
import hashlib
import json
import re
import runpy
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
root = Path(__file__).resolve().parents[2]
pins = {
    'experiments/tsl9-resident-gatt-CCC-write/write_UUID.c': 'ebfbcb2521282ab5b3ac99d14ca2acf21ed987468a3dbd22923b5cb9210dd5ea',
    'experiments/tsl9-original-layout/build/event-word-table-data-v1/c/reference-addresses.o': 'dc6d9f0086e2c6da2b1437a601abf91a833d5aaf1749faa811234cdd90d5263d',
    'experiments/tsl9-original-layout/build/event-word-table-data-v1/c/original-layout.ld': '2cab1617adbd580ef4d3347fb8bf06359e858bfb5a002ae75aae0027e0c502a9',
    'experiments/tsl9-original-layout/build/event-word-table-data-v1/c/NONLOADABLE-ORIGINAL-LAYOUT.elf': 'c79cc33284766865c77345a697c2a76b12b1ab79dbe3b996710f0b6e1ca4d8b0',
    'experiments/tsl9-event-word-table-integration/build/component-v1/c/UNRESOLVED-STARTUP-EVENT-WORD-DATA.o': '93f2fefc4f0d7754e8d58a72967a9507ab4247915ac4af6989d4afc232a10046',
    'experiments/tsl9-resident-root-chain-callees/elf_reader-v7.py': '309ee86cd2d967e40fa29cd34a9ff420f9b5803c4c3931dfd93eec75a7e2a06c',
    'experiments/tsl9-sdk-unique-code-ownership/audit-v1.py': '1b3626d65bf9850562bf23565737178a9c228bedb840e9ef1251091619e5cd63',
}
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def need(condition, message):
    if not condition: raise ValueError(message)
def tool(folder, name):
    candidates = [folder / (name + '.exe'), folder / name]
    return next(p for p in candidates if p.is_file())
def mapped(elf):
    result = {}
    for section in elf.sections:
        if section['flags'] & 2 and section['size']:
            data = elf.data(section)
            need(len(data) == section['size'], 'allocated section has file bytes')
            for i, value in enumerate(data):
                address = section['address'] + i
                need(address not in result, 'no overlapping allocated bytes')
                result[address] = value
    return result
def run(argv):
    result = subprocess.run([str(x) for x in argv], capture_output=True, text=True, timeout=120)
    need(result.returncode == 0, 'compiler or diagnostic linker failed')
    return result
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tool-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True, help='New local directory; never overwritten')
    args = parser.parse_args()
    for path, expected in pins.items(): need(sha(root / path) == expected, 'pinned local input changed: ' + path)
    clang, linker = tool(args.tool_dir, 'clang'), tool(args.tool_dir, 'ld.lld')
    output = args.output_dir.resolve()
    need(not output.exists() and output.parent.is_dir(), 'output must be a new directory with an existing parent')
    output.mkdir()
    layout_dir = root / 'experiments/tsl9-original-layout/build/event-word-table-data-v1/c'
    source = root / 'experiments/tsl9-resident-gatt-CCC-write/write_UUID.c'
    parent = root / 'experiments/tsl9-event-word-table-integration/build/component-v1/c/UNRESOLVED-STARTUP-EVENT-WORD-DATA.o'
    elf_reader = runpy.run_path(str(root / 'experiments/tsl9-resident-root-chain-callees/elf_reader-v7.py'))['ELF']
    facts = runpy.run_path(str(root / 'experiments/tsl9-sdk-unique-code-ownership/audit-v1.py'))['facts']
    old_code, old_data, old_undef, old_reloc = facts(parent, elf_reader)
    need(len(old_undef) == 6, 'six original unresolved providers')
    old_layout = elf_reader(layout_dir / 'NONLOADABLE-ORIGINAL-LAYOUT.elf')
    original = mapped(old_layout)
    need(len(original) == 73538 and not ({0x1ab44, 0x1ab45} & original.keys()), 'original placement gap is free')
    firmware = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
    with firmware.open('rb') as f:
        f.seek(0x1ab44 - 0x8000)
        need(f.read(2) == bytes.fromhex('f1ff'), 'permitted original UUID bytes')
    script = (layout_dir / 'original-layout.ld').read_text('utf-8')
    anchor = ' .original_data_span_0001ab48 0x1ab48'
    need(script.count(anchor) == 1, 'single original layout anchor')
    script = script.replace(anchor, ' .gatt_write_uuid_1ab44 0x1ab44 : SUBALIGN(2) { *(.rodata.tsl9_gatt_write_UUID_1ab44) } :NONE\n' + anchor)
    derived = output / 'diagnostic-layout.ld'
    derived.write_text(script, encoding='utf-8', newline='\n')
    hashes = []
    for tag, language in [('c', 'c'), ('cpp', 'c++')]:
        unit, linked, diagnostic = (output / (tag + suffix) for suffix in ('.o', '-linked.o', '-diagnostic.elf'))
        standard = 'c11' if tag == 'c' else 'c++17'
        run([clang, '-target', 'riscv32', '-march=rv32imac_zicsr', '-mabi=ilp32', '-ffreestanding', '-Oz', '-x', language, '-std='+standard, '-c', source, '-o', unit])
        added_code, added_data, added_undef, added_reloc = facts(unit, elf_reader)
        need(len(added_code) == 1 and not set(old_code) & set(added_code) and len(added_data) == 1 and not set(old_data) & set(added_data) and not added_undef and not added_reloc, 'two-byte source has one unique allocated section and data symbol')
        run([linker, '-m', 'elf32lriscv', '-r', '--no-relax', parent, unit, '-o', linked])
        need(facts(linked, elf_reader) == ({**old_code, **added_code}, {**old_data, **added_data}, old_undef - set(added_data), sorted(old_reloc + added_reloc)), 'partial link preserves every parent owner and relocation')
        run([linker, '--no-relax', '--emit-relocs', '--no-undefined', '--entry=0', '-T', derived, layout_dir / 'reference-addresses.o', unit, '-o', diagnostic])
        elf = elf_reader(diagnostic)
        actual = mapped(elf)
        need(all(actual.get(k) == v for k, v in original.items()), 'all previous original-coordinate bytes retained')
        need({k: actual[k] for k in actual.keys() - original.keys()} == {0x1ab44: 0xf1, 0x1ab45: 0xff}, 'only two actual UUID bytes added')
        need(len(actual) == 73540 and elf.header[3] == 0 and not any(p[0] == 1 for p in elf.program_headers), 'diagnostic is not a loadable firmware')
        hashes.append(sha(diagnostic))
    need(hashes[0] == hashes[1], 'C and C++ diagnostic outputs identical')
    strict = output / 'strict.elf'
    attempt = subprocess.run([str(linker), '--no-relax', '--no-undefined', '--entry=0', '-T', str(derived), str(layout_dir / 'split-C-payload.o'), str(output / 'c.o'), '-o', str(strict)], capture_output=True, text=True, timeout=120)
    missing = set(re.findall(r'undefined symbol: ([^\r\n]+)', attempt.stderr))
    need(attempt.returncode != 0 and missing == old_undef and not strict.exists(), 'strict link retains six genuine unresolved providers')
    print(json.dumps(dict(passed=True, original_bytes=73538, diagnostic_bytes=73540, added_bytes=2, same_c_cpp=True, remaining_unresolved=len(missing), diagnostic_sha256=hashes[0], strict_link_succeeded=False, new_BIN=False, target_executed=False)))
if __name__ == '__main__':
    try: main()
    except Exception as error:
        print(json.dumps(dict(passed=False, error=type(error).__name__, reason=str(error).replace(str(root), '${PROJECT_ROOT}').replace(str(Path.home()), '${USERPROFILE}'))))
        raise SystemExit(1)
