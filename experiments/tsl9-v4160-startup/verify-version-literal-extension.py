"""Add one real original literal object after the unchanged current native gate.

This compiles/links and inspects artifacts only. A numeric-address witness is
not executable firmware, a resident implementation or an OTA image.
"""
import argparse
import collections
import hashlib
import json
import re
import runpy
import struct
import subprocess
import sys
import uuid
from pathlib import Path

_paths = __import__("runpy").run_path(str(next(p for p in Path(__file__).resolve().parents if (p / "scripts/project_paths.py").is_file()) / "scripts/project_paths.py"))

ROOT = Path(__file__).resolve().parent
W = ROOT.parents[1]
BIN = _paths["llvm_bin"]()
NAME = '__tsl9v4160_address_1ab1c'
SECTION = '.rodata.tsl9v4160.version_literal_1ab1c'
VA = 0x1AB1C
FIRMWARE_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
OLD_OBJECT_SHA = '65eb6581e6855ad15771fd3d0348c9d192de19253dbde46f94a7c3a962db03d7'
OLD_WITNESS_SHA = '06d6ebd4f3fd889d24248624ff6e7d7ab2927817dcc6e7c0730b8d768d196ed8'
LITERAL = b'CH32V20x_BLE_LIB_V1.3\0'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())
ELF = runpy.run_path(str(ROOT / 'verify.py'))['ELF']

def need(ok, message):
    if not ok: raise AssertionError(message)

def run(argv, folder, label, success=True):
    process = subprocess.run([str(x) for x in argv], cwd=folder,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             timeout=240, check=False)
    log = folder / (label + '.log'); log.write_bytes(process.stdout)
    need((process.returncode == 0) == success, 'Tool result: ' + label)
    return dict(argv=[str(x) for x in argv], exit=process.returncode,
                log=str(log), log_sha256=sha(log)), process.stdout

def defined(elf):
    return {s['name']:(elf.sections[s['index']]['name'], s['value'], s['size'], s['type'], s['bind'])
            for s in elf.symbols if s['name'] and s['bind'] == 1 and 0 < s['index'] < 0xFF00}

def und(elf):
    return {s['name'] for s in elf.symbols if s['name'] and s['index'] == 0}

def symbol_offset(elf):
    found = []
    for table in elf.sections:
        if table['type'] != 2: continue
        strings = elf.sections[table['link']]['data']
        for offset in range(0, table['size'], 16):
            name_at = struct.unpack_from('<I', table['data'], offset)[0]
            name = strings[name_at:strings.index(0, name_at)].decode('ascii')
            if name == NAME: found.append(table['offset'] + offset)
    need(len(found) == 1, 'Single actual canonical symbol record')
    return found[0]

def literal_gate(elf, linked=False):
    need(SECTION in elf.byname and NAME in elf.symbol, 'Actual named literal storage')
    sec = elf.byname[SECTION]; sym = elf.symbol[NAME]
    need((sec['type'], sec['flags'], sec['size'], sec['alignment']) == (1, 2, 22, 1), 'Literal is exactly one RO22 allocation')
    need(sec['data'] == LITERAL, 'Every literal byte and NUL is original')
    need((sym['index'], sym['bind'], sym['type'], sym['size'], sym['value']) ==
         (sec['index'], 1, 1, 22, VA if linked else 0), 'Real global OBJECT22 at its own section, no alias or ABS')
    need(elf.raw[symbol_offset(elf) + 13] == 0, 'Default visibility retained')
    need(not linked or sec['address'] == VA, 'Original literal numeric placement')

def literal_countercases(elf, folder):
    symbol_at = symbol_offset(elf)
    out = []
    for tag in ['ABS_same_numeric', 'FUNC_type', 'size21', 'offset1', 'local_binding', 'wrong_byte', 'missing_NUL', 'writable_section', 'wrong_section', 'hidden_visibility']:
        bad = bytearray(elf.raw); sec = elf.byname[SECTION]
        if tag == 'ABS_same_numeric':
            struct.pack_into('<H', bad, symbol_at + 14, 0xFFF1)
            struct.pack_into('<I', bad, symbol_at + 4, VA)
        elif tag == 'FUNC_type': bad[symbol_at + 12] = 0x12
        elif tag == 'size21': struct.pack_into('<I', bad, symbol_at + 8, 21)
        elif tag == 'offset1': struct.pack_into('<I', bad, symbol_at + 4, 1)
        elif tag == 'local_binding': bad[symbol_at + 12] = 1
        elif tag == 'wrong_byte': bad[sec['offset'] + 20] ^= 1
        elif tag == 'missing_NUL': bad[sec['offset'] + 21] = 1
        elif tag == 'writable_section':
            headers = struct.unpack_from('<I', bad, 32)[0]
            struct.pack_into('<I', bad, headers + sec['index'] * 40 + 8, 3)
        elif tag == 'wrong_section':
            other = next(s for s in elf.sections if s['flags'] == 2 and s['size'] and s['name'] != SECTION)
            struct.pack_into('<H', bad, symbol_at + 14, other['index'])
        elif tag == 'hidden_visibility': bad[symbol_at + 13] = 2
        path = folder / ('COUNTERCASE-literal-' + tag + '.o'); path.write_bytes(bad)
        try: literal_gate(ELF(path))
        except AssertionError as error: reason = str(error)
        else: raise AssertionError('Accepted actual ELF mutant: ' + tag)
        out.append(dict(case=tag, path=str(path), sha256=sha(path), rejected=True, reason=reason))
    return out

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--firmware', type=Path)
    parser.add_argument('--current-receipt', type=Path, default=ROOT / 'build/data-anchor-extension-6120e1adb9f944db95d8a72ddfd9e955/gatt-ingress-verification.json')
    parser.add_argument('--proof', type=Path)
    args = parser.parse_args()
    if args.firmware is None:
        args.firmware = next((W / name for name in [
            'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin',
            'exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'] if (W / name).exists()), None)
    need(args.firmware is not None and sha(args.firmware) == FIRMWARE_SHA, 'Exact original ID2966 source')
    raw = args.firmware.read_bytes(); need(len(raw) == 76800 and raw[VA-0x8000:VA-0x8000+22] == LITERAL, 'Original literal, including excluded NUL')
    prior = read(args.current_receipt)
    need(prior['passed'] and len(prior['allocations']) == 640 and prior['firmware_sha256'] == FIRMWARE_SHA, 'Reviewed current640 baseline')
    need(not any(s['originalVA'] < VA + 22 and VA < s['originalVA'] + s['bytes']
                 for s in prior['allocations'].values()), 'Literal occupies an existing unrepresented gap')
    for name, digest in prior['source_files'].items(): need(sha(ROOT / name) == digest, 'Frozen baseline source changed')
    need(sha(Path(prior['baseline_receipt'])) == prior['baseline_receipt_sha256'], 'Frozen parent input')
    if args.proof is None:
        args.proof = next((W / name for name in [
            'apk-analysis/tsl9-v4160-literal-contract-2026-10-21/independent-literal/review.json',
            'analysis/v4160-literal-contract-2026-10-21/independent-literal/review.json'] if (W / name).exists()), None)
    need(args.proof is not None, 'Independent original literal role proof required')
    proof = read(args.proof)
    need(proof['passed'] and not proof['blocking_findings'] and sha(args.proof) ==
         'e396fd95376f501547fc015cb7a39b9d26ae6e029f6053a73aab49aab913a0d7', 'Exact independent literal role proof')
    seal_path = args.proof.parent/'final-audit.json'
    need(sha(seal_path) == '8c0cc78ad80e480acf9f0e131782e6f7d00aa17e46664a0b096da99c0a693d50', 'Exact completed proof seal')
    seal = read(seal_path)
    need(seal['passed'] and seal['sealed'], 'Independent proof terminal PASS')
    for row in seal['members']:
        p = (seal_path.parent/row['path']).resolve()
        need(p.is_relative_to(seal_path.parent.resolve()) and p.stat().st_size == row['bytes'] and sha(p) == row['sha256'], 'Independent sealed member')
    work = ROOT / 'build' / ('version-literal-extension-' + uuid.uuid4().hex)
    work.mkdir(parents=True, exist_ok=False)
    frozen = ROOT / 'verify-gatt-ingress-extension.py'
    need(sha(frozen) == prior['source_files'][frozen.name], 'Retain unchanged frozen frontier verifier')
    _, log = run([sys.executable, '-X', 'utf8', '-B', frozen,
                  '--spec', ROOT / 'evidence/residual-callbacks-integration.json',
                  '--firmware', args.firmware.resolve(), '--baseline-receipt', prior['baseline_receipt']],
                 work, 'unchanged-current-gate')
    current_path = Path(json.loads(log.decode('utf-8').strip().splitlines()[-1])['receipt'])
    current = read(current_path)
    need(current['passed'] and current['allocations'] == prior['allocations'], 'Fresh unchanged complete native gate passed')
    allocations = dict(current['allocations'])
    allocations[SECTION] = dict(name=SECTION, originalVA=VA, end_exclusive=VA+22,
                               bytes=22, kind='RO', flags=2, alignment=1,
                               sha256=hashlib.sha256(LITERAL).hexdigest(),
                               capture_role='reconstructed_expected_version_literal_storage')
    layout = work / 'original-address-layout.ld'
    text = 'OUTPUT_ARCH(riscv)\nENTRY(__tsl9v4160_image_entry)\nSECTIONS {\n'
    for name, row in sorted(allocations.items(), key=lambda item:item[1]['originalVA']):
        text += ' ' + name + ' ' + hex(row['originalVA']) + (' (NOLOAD)' if row['kind']=='RAM' else '') + ' : { KEEP(*(' + name + ')) }\n'
        text += ' ASSERT(SIZEOF(' + name + ')==' + str(row['bytes']) + ', "Original allocation changed")\n'
    layout.write_text(text + ' /DISCARD/ : { *(.comment) *(.note.GNU-stack) }\n}\n', encoding='utf-8')
    modes = {}
    for mode, language, std in [('c','c','c11'), ('cpp','c++','c++17')]:
        folder = work / mode; folder.mkdir(); commands = []
        old_path = Path(current['modes'][mode]['integrated_object']); old = ELF(old_path)
        old_witness = ELF(current_path.parent / mode / 'ADDRESS-WITNESS-ONLY.elf')
        need(sha(old_path) == OLD_OBJECT_SHA and hashlib.sha256(old_witness.raw).hexdigest() == OLD_WITNESS_SHA, 'Fresh frozen actual object and witness')
        need(len(und(old)) == 31 and NAME in und(old) and len(old.relocations) == 8107, 'Actual prior dependency/relocation scope')
        addresses = {n:old_witness.symbol[n]['value'] for n in und(old)}
        need(addresses[NAME] == VA, 'Original numeric target identity')
        obj = folder / 'version-literal.o'
        command, _ = run([BIN/'clang.exe','--target=riscv32-unknown-elf','-march=rv32imac','-mabi=ilp32',
                          '-ffreestanding','-fno-builtin','-fno-stack-protector','-Wall','-Wextra','-Werror',
                          '-x',language,'-std='+std,'-c',ROOT/'src/version_literal_native.c','-o',obj], folder,'compile-literal')
        commands.append(command); unit = ELF(obj); literal_gate(unit)
        need(not und(unit) and not unit.relocations and set(defined(unit)) == {NAME}, 'Data-only literal unit, no runtime dependency')
        need({s['name'] for s in unit.sections if s['flags']&2 and s['size']} == {SECTION}, 'Only real new RO22 storage')
        merged_path = folder / 'native-extension.o'
        command,_ = run([BIN/'ld.lld.exe','-r','--no-relax',old_path,obj,'-o',merged_path],folder,'integrate-real-literal')
        commands.append(command); merged = ELF(merged_path); literal_gate(merged)
        need(und(merged) == und(old)-{NAME}, 'Exactly one data contract closed, other30 remain true UND')
        need(set(defined(merged)) == set(defined(old))|{NAME}, 'Only one new allocated global provider')
        need(all(defined(merged)[n] == row for n,row in defined(old).items()), 'All prior typed allocated providers unchanged')
        need({s['name'] for s in merged.sections if s['flags']&2 and s['size']} == set(allocations), 'Exact641 allocations, no hidden storage')
        for name, row in current['allocations'].items():
            before, after = old.byname[name], merged.byname[name]
            need(all(before[k] == after[k] for k in ['type','flags','size','alignment','data']), 'Every inherited section unchanged')
        def normalized(elf, relocation):
            sym = elf.symbols[relocation['symbol_index']]
            if sym['index'] == 0:
                base = addresses[sym['name']] if sym['name'] else 0
            elif sym['index'] == 0xFFF1: base = sym['value']
            else: base = allocations[elf.sections[sym['index']]['name']]['originalVA'] + sym['value']
            return (base + relocation['addend']) & 0xFFFFFFFF
        def records(elf):
            return collections.Counter((r['section'],r['offset'],r['type'],normalized(elf,r)) for r in elf.relocations)
        need(len(merged.relocations) == 8107 and records(old) == records(merged), 'Every semantic RELA occurrence preserved')
        selected = [r for r in merged.relocations if r['target'] == NAME]
        need(len(selected) == 1 and selected[0]['type'] == 23 and selected[0]['addend'] == 0 and
             allocations[selected[0]['section']]['originalVA'] + selected[0]['offset'] == 0x199FC,
             'Sole original HI points to the real literal, no manufactured references')
        strict = folder / 'strict-incomplete.elf'
        command, errors = run([BIN/'ld.lld.exe','--no-relax','--error-limit=0','-T',layout,merged_path,'-o',strict],folder,'strict-final-link',False)
        commands.append(command)
        remaining = und(merged)
        need(not strict.exists() and set(re.findall(r'undefined symbol: (\w+)',errors.decode('utf-8','replace'))) == remaining, 'Strict final link still rejects exactly30 unresolved contracts')
        witness_script = folder / 'ADDRESS-WITNESS-ONLY.ld'
        witness_script.write_text('/* Numeric obligations only. NOT implementations or firmware. */\n' +
                                  ''.join(n+' = '+hex(addresses[n])+';\n' for n in sorted(remaining)), encoding='utf-8')
        witness_path = folder / 'ADDRESS-WITNESS-ONLY.elf'
        command,_ = run([BIN/'ld.lld.exe','--no-relax','-T',layout,'-T',witness_script,merged_path,'-o',witness_path],folder,'numeric-address-witness')
        commands.append(command); witness = ELF(witness_path); literal_gate(witness,True)
        for name,row in allocations.items():
            sec = witness.byname[name]
            need(sec['address'] == row['originalVA'] and sec['size'] == row['bytes'], 'Every actual witness placement exact')
            if row['kind'] != 'RAM': need(sec['data'] == raw[row['originalVA']-0x8000:row['originalVA']-0x8000+row['bytes']], 'Every captured code/RO byte still original')
        need(witness.byname['.text.tsl9v4160.frontier_199e2']['data'] == old_witness.byname['.text.tsl9v4160.frontier_199e2']['data'], 'All caller instructions numerically identical to old witness')
        cases = literal_countercases(merged,folder)
        modes[mode] = dict(passed=True,commands=commands,integrated_object=str(merged_path),integrated_sha256=sha(merged_path),
                           numeric_witness_sha256=sha(witness_path),undefined_symbols=sorted(remaining),
                           code_bytes=70764,RO_bytes=3730,allocation_sections=len(allocations),relocations=len(merged.relocations),
                           strict_rejected=True,new_OBJECT_size=22,actual_countercases=cases)
    need(modes['c']['integrated_sha256'] == modes['cpp']['integrated_sha256'] and
         modes['c']['numeric_witness_sha256'] == modes['cpp']['numeric_witness_sha256'], 'Both languages produce identical actual artifacts')
    sources = dict(current['source_files'])
    for name in ['src/version_literal_native.c','src/version_literal_native.h',Path(__file__).name]: sources[name] = sha(ROOT/name)
    report = dict(schema='ID2966-version-literal-native-extension-v1',passed=True,firmware_sha256=FIRMWARE_SHA,
                  source_files=sources,baseline_receipt=str(current_path),baseline_receipt_sha256=sha(current_path),
                  independent_literal_proof=str(args.proof.resolve()),independent_literal_proof_sha256=sha(args.proof),
                  allocations=allocations,modes=modes,new_closed_contract=NAME,new_real_storage_bytes=22,
                  code_bytes=70764,RO_bytes=3730,source_coverage_bytes=74494,original_image_bytes=76800,
                  original_C_object_extent_proved=False,resident_maximum_read_extent_proved=False,
                  original_resident_identity_proved=False,IRQ_ABI_proved=False,
                  firmware_executed=False,emulation=False,network=False,hardware=False,native_bin=False,ota_verified=False)
    out = work/'verification.json'; out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,receipt=str(out),sha256=sha(out),new_real_storage_bytes=22,
                          remaining_UND=30,source_bytes=74494,native_BIN=False,OTA_ready=False)))

if __name__ == '__main__': main()
