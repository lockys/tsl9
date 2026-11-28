"""Compile the instruction-reconstructed original TX with its real RAM relocation."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import runpy
import subprocess

HERE = Path(__file__).resolve().parent
SECTION = '.text.tsl9_tx_composite'
RAM = '__tsl9v4160_data_2000b18c'
TX_SHA = '3b01d76ded6b08cb239ca3c8d7e789db8b0b7149d4c6d4e48c50d987a1ef2f0b'
SOURCE_SHA = '2f2c6ce39e35f131b5cce098cee3a9877a9e9cefc2fd498dc54f47dfa8b9ad7e'
ELF = runpy.run_path(str(HERE / 'postpass/elf32.py'))['ELF']


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def flags(mode):
    allowed = {1, 2, 5, 6, 7, *range(10, 18), *range(28, 32)}
    common = ['--target=riscv32-unknown-elf', '-march=rv32imac_zicsr', '-mabi=ilp32', '-Oz',
              '-mllvm', '-enable-machine-outliner=never', '-ffreestanding', '-fno-builtin',
              '-fno-stack-protector', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables',
              '-mno-relax', '-ffunction-sections', '-fdata-sections', '-Wall', '-Wextra', '-Werror']
    common += ['-ffixed-x' + str(i) for i in range(1, 32) if i not in allowed]
    return common + ['-x', 'c' if mode == 'c' else 'c++', '-std=c11' if mode == 'c' else '-std=c++17'] + (['-fno-exceptions'] if mode == 'cpp' else [])


def run(args, success=True):
    result = subprocess.run([str(x) for x in args], capture_output=True, text=True, timeout=120)
    if success:
        need(result.returncode == 0, 'compiler/linker failed: ' + result.stderr[:600])
    return result


def check_unit(elf):
    allocated = [s for s in elf.sections if s['flags'] & 2 and s['size']]
    need(elf.kind == 1 and len(allocated) == 1, 'one real TX section')
    owner = allocated[0]
    need((owner['name'], owner['type'], owner['flags'], owner['size'], owner['alignment'])
         == (SECTION, 1, 6, 280, 2), 'exact executable 280-byte TX owner')
    expected = {'tx_study': (0, 280), 'tsl9_filter_external_8a56': (0, 0),
                '__tsl9v4160_call_8a56': (0, 8), 'tsl9_tx_oversized_return': (278, 2)}
    for name, (value, size) in expected.items():
        symbols = [s for s in elf.symbols if s['name'] == name]
        need(len(symbols) == 1, 'unique TX symbol: ' + name)
        s = symbols[0]
        need((s['value'], s['size'], s['info'], s['other'], s['index']) == (value, size, 18, 0, owner['index']),
             'TX entry/return ownership: ' + name)
    need({s['name'] for s in elf.symbols if s['name'] and s['index'] == 0 and s['info'] >> 4} == {RAM},
         'real RAM provider remains undefined')
    roles = [(r['owner'], r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in elf.relocations]
    need(roles == [(SECTION, 128, 23, RAM, 0), (SECTION, 132, 24, '.Lpcrel_tx_ram', 0)], 'two genuine TX RAM relocations')
    anchor = elf.relocations[1]['symbol']
    need(anchor['index'] == owner['index'] and anchor['value'] == 128, 'LO12 uses the actual local HI20 anchor')


def linked_bytes(elf):
    section = elf.byname[SECTION]
    need(section['address'] == 0x8a56 and section['size'] == 280, 'original TX placement')
    data = elf.data(section)
    need(hashlib.sha256(data).hexdigest() == TX_SHA, 'linked original TX byte identity')
    return data


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--tool-dir', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--candidate', type=Path, help='Optional read-only 280-byte comparison in a caller-selected image')
    a = p.parse_args()
    out = a.out.resolve()
    need(not out.exists() and not out.is_relative_to(HERE), 'new output outside TX source directory')
    need(digest(HERE / 'original_tx.c') == SOURCE_SHA, 'pinned instruction source')
    tools = {n: next(x for x in [a.tool_dir / (n + '.exe'), a.tool_dir / n] if x.is_file()) for n in ('clang', 'ld.lld')}
    need(digest(tools['clang']) == '047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6'
         and digest(tools['ld.lld']) == 'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f', 'pinned LLVM tools')
    candidate = None
    if a.candidate:
        need(a.candidate.stat().st_size == 76800, 'candidate image length')
        with a.candidate.open('rb') as stream:
            stream.seek(0xa56)
            candidate = stream.read(280)
        need(hashlib.sha256(candidate).hexdigest() == TX_SHA, 'candidate original TX window')
    out.mkdir(parents=True)
    script = out / 'tx-only.ld'
    script.write_text('OUTPUT_ARCH(riscv)\nPHDRS { evidence PT_NULL FLAGS(0); }\nSECTIONS { .text.tsl9_tx_composite 0x8a56 : { *(.text.tsl9_tx_composite) } :NONE /DISCARD/ : { *(.comment) *(.note*) *(.riscv.attributes) *(.llvm_addrsig) } }\n', encoding='utf-8')
    for mode in ('c', 'cpp'):
        unit = out / ('symbolic-' + mode + '.o')
        run([tools['clang'], *flags(mode), '-c', HERE / 'original_tx.c', '-o', unit])
        check_unit(ELF(unit))
        command = [tools['ld.lld'], '--no-undefined', '--no-relax', '-T', script, unit]
        missing = run([*command, '-o', out / ('STRICT-NO-RAM-' + mode + '.elf')], success=False)
        need(missing.returncode != 0 and set(re.findall(r'undefined symbol: ([^\r\n]+)', missing.stderr)) == {RAM}, 'strict RAM dependency retained')
        dest = out / ('NOT-FLASHABLE-TX-ONLY-' + mode + '.elf')
        run([*command, '--defsym=' + RAM + '=0x2000b18c', '-o', dest])
        data = linked_bytes(ELF(dest))
        need(candidate is None or candidate == data, 'optional candidate TX comparison')
        (out / ('NOT-FLASHABLE-TX-ONLY-' + mode + '.bin')).write_bytes(data)
        wrong = out / ('WRONG-RAM-' + mode + '.elf')
        run([*command, '--defsym=' + RAM + '=0x2000b190', '-o', wrong])
        try:
            linked_bytes(ELF(wrong))
        except ValueError as error:
            need(str(error) == 'linked original TX byte identity', 'wrong RAM control fails for the intended reason')
        else:
            raise ValueError('wrong RAM provider accepted')
    report = {'passed': True, 'languages': ['c', 'cpp'], 'tx_bytes': 280, 'tx_digest_matches': True,
              'candidate_bytes_read': 280 if candidate is not None else 0, 'symbolic_RAM_dependency': True,
              'object_postpass_used': False, 'firmware_read': False if candidate is None else 'bounded optional TX window',
              'source_sha256': SOURCE_SHA, 'linked_TX_sha256': TX_SHA, 'flashable': False, 'target_executed': False}
    (out / 'verification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
