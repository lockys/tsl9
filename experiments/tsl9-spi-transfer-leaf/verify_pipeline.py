#!/usr/bin/env python3
"""Read existing partial-link evidence only; never compile or execute target code.

This is a 352-byte ET_REL composition, not a resolved executable or firmware.
The prior provider receipt is a pinned historical input, not replayed here.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
READER_PIN = '8c8eb8e01b9fc30eb7150682aa8848e47fe4a1254c6f87b05e657244a11b6de8'
OLD_PIN = 'c9fb372ea89d143d78f192bebf81ddf864d9333be79564958c6cdd6e08f9cc8b'
NEW_PIN = 'a9a3954a732dd1e6253ccf3756505ef8e49c2a0eb2cdefc7944600eea33dc86d'
OLD_RECEIPTS = {'c': '47c78cafe18f470b39eeeb8fbac1cd7e7701b9212269c72b07547305ff06b35b',
                'cpp': 'd9b7e201658fa1f2ae56dd2afad433696ba963057bb8504ae614c4021017caf8'}
PINS = {
 'experiments/tsl9-spi-transfer-leaf/pipeline.ld': '001d7b1647b8f17a1523a5668b47f2f1ce1bc1c6d14b55b3e46ea51c9d93a145',
 'experiments/tsl9-spi-transfer-leaf/component.ld': '755acb8fd08dcd580a1f11394f88ba68f3fb1224ccc6549eea0a9035db4a3a5e',
 'experiments/tsl9-spi-transfer-leaf/src/spi_transfer_ports.c': '1f68851e9ae71d1ef56147e554fdaa53ae0918e2bfac73bad32a110549fe3182',
 'experiments/tsl9-irq-flag-consumer/src/flag_consumer.c': '9edf5f2571991062605863e88adf8028d4d54efc8d3e518c540026bd50b0ef12',
 'experiments/tsl9-receive-wrapper/src/receive_wrapper.c': 'df1e1f0633c50b8b2c9f7a58d2ac1e45664057de107dc04d28eca9e931538cdc',
 'experiments/tsl9-register-read/src/register_read.c': '5d0dfffde0adf21490e9108fbb95920595a851d67ac95b376549e20be3989846',
 'experiments/tsl9-register-write/src/register_write.c': 'd4a0669559aeb497f787c98066db28da8fa9f285bf3b9be2bce574c0ed016f85',
 'experiments/tsl9-register-providers/pipeline.ld': '5099f57908aad1bb13df777b97ca85416c94c95a15037705c3171a13128d94a4',
 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin': '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667',
}
OLD_NAMES = ['tsl9_flag_consumer_entry_17002', 'tsl9_flag_consumer_body',
 'tsl9_receive_entry_16b0a', 'tsl9_receive_body', 'tsl9_register_read_entry_16994',
 'tsl9_register_read_body', 'tsl9_register_write_entry_16a30', 'tsl9_register_write_body']
OLD_STARTS = [0, 8, 62, 76, 132, 136, 204, 208]
OLD_SIZES = [8, 54, 14, 56, 4, 68, 4, 72]
PACKET = 'tsl9_receive_buffer_entry_16a7c'
JALS = [(22, OLD_NAMES[2]), (48, OLD_NAMES[2]), (76, OLD_NAMES[4]),
 (94, PACKET), (108, PACKET), (128, OLD_NAMES[6])] + [
 (x, 'tsl9_spi_transfer_entry_16896') for x in [170, 178, 184, 244, 252, 260]]
CHUNKS = [(0, 0x17002, 62), (62, 0x16b0a, 70), (132, 0x16994, 72),
          (204, 0x16a30, 76), (280, 0x16896, 72)]
SECTION_ROWS = [
 ('', 0, 0, 0, 0, 0, 0, 0, 0, 0),
 ('.pipeline', 1, 6, 0, 52, 352, 0, 0, 2, 0),
 ('.text', 1, 6, 0, 404, 0, 0, 0, 2, 0),
 ('.rela.pipeline', 4, 64, 0, 404, 204, 5, 1, 4, 12),
 ('.llvm_addrsig', 1879002115, 2147483648, 0, 608, 16, 0, 0, 1, 0),
 ('.symtab', 2, 0, 0, 624, 752, 7, 30, 4, 16),
 ('.shstrtab', 3, 0, 0, 1376, 72, 0, 0, 1, 0),
 ('.strtab', 3, 0, 0, 1448, 628, 0, 0, 1, 0)]


def require(ok, why):
    if not ok:
        raise ValueError(why)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def digest(path):
    return sha(Path(path).read_bytes())


def reader():
    path = HERE/'verify.py'
    require(digest(path) == READER_PIN, 'frozen standalone reader pin')
    spec = importlib.util.spec_from_file_location('_tsl9_spi_reader', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def locals_expected():
    rows = [('', 0, 0, 0, 0, 0)]
    for name, start in [('flag_consumer.c', 0), ('receive_wrapper.c', 62),
                        ('register_read.c', 132), ('register_write.c', 204)]:
        entry = 8 if start == 0 else 14 if start == 62 else 4
        rows += [(name, 0, 0, 4, 0, 65521), ('$x.0', start, 0, 0, 0, 1),
                 ('$x.1', start+entry, 0, 0, 0, 1), ('$d.3', 0, 0, 0, 0, 65521)]
    rows += [('', 0, 0, 3, 0, 2), ('', 0, 0, 3, 0, 4),
             ('spi_transfer_ports.c', 0, 0, 4, 0, 65521)]
    rows += [('$x.'+str(i), 280+x, 0, 0, 0, 1)
             for i, x in enumerate([0, 8, 16, 32, 40, 50, 58, 62])]
    return rows+[('$d.9', 0, 0, 0, 0, 65521), ('', 0, 0, 3, 0, 1)]


def contract(e, old, native, firmware, m, full=True):
    require(e.header == [1, 243, 1, 0, 0, 2076, 1, 52, 0, 0, 40, 8, 6]
            and not e.program_headers, 'ET_REL header/extent')
    keys = ['name', 'type', 'flags', 'address', 'offset', 'size', 'link', 'info', 'align', 'entsize']
    require([tuple(s[k] for k in keys) for s in e.sections] == SECTION_ROWS,
            'exact section ownership/metadata, no extra allocated storage')
    require([s['index'] for s in e.sections] == list(range(8)) and len(e.raw) == 2396,
            'complete file/section index extent')
    skeys = ['name', 'value', 'size', 'info', 'other', 'section']
    require([tuple(s[k] for k in skeys) for s in e.symbols[:30]] == locals_expected(),
            'exact local metadata, no local FUNC or aliases')
    names = OLD_NAMES + m.NAMES
    starts = OLD_STARTS + [280+x for x in m.STARTS]
    sizes = OLD_SIZES + m.SIZES
    want = {n: (v, z, 18, 0, 1) for n, v, z in zip(names, starts, sizes)}
    want[PACKET] = (0, 0, 16, 0, 0)
    actual = {s['name']: tuple(s[k] for k in skeys[1:]) for s in e.symbols[30:]}
    require(len(e.symbols) == 47 and len(actual) == 17 and actual == want,
            '16 genuine FUNCs/one UND/no ABS providers, exact values/sizes/binding')
    expected = [(at, 17, name, 0, 1) for at, name in JALS]
    expected += [(280+at, kind, m.NAMES[target], 0, 1) for at, kind, target in m.RELATIONS]
    rels = [(r['offset'], r['type'], e.symbols[r['symbol']]['name'], r['addend'], r['section'])
            for r in e.relocations]
    require(rels == expected, 'exact 17 RELA graph/owner/type/addend')
    defined = [r for r in e.relocations if e.symbols[r['symbol']]['section'] == 1]
    external = [r['offset'] for r in e.relocations if e.symbols[r['symbol']]['section'] == 0]
    require(len(defined) == 15 and external == [94, 108], '15 internal edges/two packet UND calls')
    code = e.data('.pipeline')
    for at, _ in JALS:
        require(code[at:at+4] == (0x6f if at == 128 else 0xef).to_bytes(4, 'little'),
                'zero-immediate genuine JAL/tail-JAL ports')
    for at, kind, target in m.RELATIONS:
        value = 0xc301 if at in [14, 38] else 0xe381 if at in [56, 68] else 0xa001
        require(code[280+at:282+at] == value.to_bytes(2, 'little'),
                'zero-immediate typed RVC ports/registers')
        delta = m.STARTS[target]-at
        require(delta % 2 == 0 and (-(1 << (8 if kind == 44 else 11)) <= delta <
                                   (1 << (8 if kind == 44 else 11))), 'RVC range/alignment')
    excluded = {j+i for j, _ in JALS for i in range(4)} | {
        280+j+i for j, _, _ in m.RELATIONS for i in range(2)}
    selected, original = bytearray(), bytearray()
    for dest, va, size in CHUNKS:
        src = firmware[va-0x8000:va-0x8000+size]
        require(len(src) == size, 'original region bounds')
        for i in range(size):
            if dest+i not in excluded:
                selected.append(code[dest+i]); original.append(src[i])
    require(len(selected) == 294 and selected == original, '294 original noncontrol bytes')
    require(code[:280] == old.data('.pipeline'), 'old 280-byte projection unchanged')
    native_code = b''.join(native.data('.text.'+n) for n in m.NAMES)
    require(code[280:] == native_code, 'actual native SPI 72-byte projection unchanged')
    m.code_contract(code[280:], native=True, full=False)
    if full:
        require(sha(e.raw) == NEW_PIN, 'whole partial-ELF pin')
    return dict(ET_REL=True, allocated_bytes=352, genuine_FUNCs=16, RELA_total=17,
                defined_relocation_targets=15, UND_calls=[94, 108], UND_providers=[PACKET],
                ABS_providers=[], local_ABS_metadata=10, preserved_provider_bytes=280,
                preserved_SPI_bytes=72, original_noncontrol_bytes=294,
                original_noncontrol_sha256=sha(bytes(original)),
                unresolved_machine_JALs=12, unresolved_machine_RVC_ports=5,
                resolved_executable=False, firmware_ready=False,
                sections=e.sections, symbols=e.symbols, relocations=e.relocations)


def negatives(e, old, native, fw, m):
    tests = []
    def add(name, edit):
        changed = copy.deepcopy(e)
        edit(changed)
        try:
            contract(changed, old, native, fw, m, full=False)
        except ValueError as exc:
            tests.append(dict(name=name, rejected=True, whole_hash_enabled=False, reason=str(exc)))
        else:
            raise ValueError('negative control accepted: '+name)
    def sym(name, key, value):
        return lambda x: next(s for s in x.symbols if s['name'] == name).__setitem__(key, value)
    spi = m.NAMES[0]
    add('fake_ABS_packet_provider', sym(PACKET, 'section', 65521))
    add('fake_ABS_SPI_provider', sym(spi, 'section', 65521))
    add('SPI_undefined_again', sym(spi, 'section', 0))
    add('SPI_wrong_value', sym(spi, 'value', 282))
    add('SPI_wrong_size', sym(spi, 'size', 10))
    add('SPI_object_instead_of_FUNC', sym(spi, 'info', 17))
    add('weak_SPI_provider', sym(spi, 'info', 34))
    add('hidden_SPI_provider', sym(spi, 'other', 2))
    add('receiver_wrong_frame_extent', sym(OLD_NAMES[2], 'size', 12))
    add('extra_local_FUNC', lambda x: x.symbols[2].__setitem__('info', 2))
    add('local_ABS_changed', lambda x: x.symbols[4].__setitem__('value', 2))
    add('wrong_ELF_kind', lambda x: x.header.__setitem__(0, 2))
    add('wrong_RVC_ELF_flags', lambda x: x.header.__setitem__(6, 0))
    add('pipeline_writable', lambda x: x.sections[1].__setitem__('flags', 7))
    add('extra_allocated_metadata', lambda x: x.sections[4].__setitem__('flags', 2))
    add('misaligned_pipeline', lambda x: x.sections[1].__setitem__('align', 4))
    add('pipeline_size', lambda x: x.sections[1].__setitem__('size', 350))
    for field, value in [('offset', 296), ('type', 45), ('addend', 2), ('section', 2), ('symbol', 35)]:
        add('RVC_wrong_'+field, lambda x, k=field, v=value: x.relocations[12].__setitem__(k, v))
    add('missing_RELA', lambda x: x.relocations.pop())
    add('duplicate_RELA', lambda x: x.relocations.append(dict(x.relocations[-1])))
    add('JAL_bound_to_packet', lambda x: x.relocations[6].__setitem__('symbol', 35))
    def byte(at, xor):
        def edit(x):
            b = bytearray(x.raw); b[52+at] ^= xor; x.raw = bytes(b)
        return edit
    add('JAL_nonzero_immediate', byte(23, 0x10))
    add('tail_JAL_wrong_rd', byte(128, 0x80))
    add('RVC_nonzero_immediate', byte(294, 0x04))
    add('RVC_wrong_register', byte(294, 0x80))
    add('native_GPIO_instruction_changed', byte(138, 0x04))
    add('SPI_fresh_read_width_changed', byte(288, 0x20))
    add('SPI_timeout_result_changed', byte(338, 0x04))
    return tests


def inventory(directory):
    require(directory.is_dir() and not directory.is_symlink(), 'actual build directory')
    paths = sorted(directory.iterdir())
    require(all(p.is_file() and not p.is_symlink() for p in paths), 'flat inventory/no extra dirs or symlinks')
    return {p.name: digest(p) for p in paths}


def verify(language, provider, spi, pipeline, m):
    require(len({provider, spi, pipeline}) == 3, 'distinct evidence directories')
    before = {str(d): inventory(d) for d in [provider, spi, pipeline]}
    require(set(before[str(pipeline)]) == {'PIPELINE-SPI-OPEN.o', 'recipes.json', 'object.log', 'combine.log'},
            'exact partial pipeline inventory')
    require(set(before[str(spi)]) == {'native.o', 'native.ll', 'native.d', 'linked.elf', 'recipes.json',
             'compile.log', 'IR.log', 'link.log', 'object.log', 'linked.log'}, 'exact SPI producer inventory')
    receipt = provider/'verification.json'
    require(digest(receipt) == OLD_RECEIPTS[language], 'prior provider receipt pin')
    prior = json.loads(receipt.read_text(encoding='utf-8'))
    require(prior['schema'] == 'TSL9-register-providers-open-pipeline-v1' and prior['mode'] == language,
            'provider receipt identity')
    require(before[str(provider)] == dict(prior['artifacts'], **{'verification.json': OLD_RECEIPTS[language]}),
            'prior 33 artifacts/receipt current exact inventory')
    require(digest(provider/'PIPELINE-OPEN.o') == OLD_PIN, 'prior provider actual object pin')
    require(digest(spi/'native.o') == m.NATIVE_PIN, 'native SPI actual object pin')
    recipe = json.loads((pipeline/'recipes.json').read_text(encoding='utf-8'))
    require(isinstance(recipe, list) and len(recipe) == 2, 'two pipeline producer recipes')
    llvm = Path(recipe[0]['argv'][0]).resolve().parent
    ex = lambda n: str(llvm/(n+'.exe'))
    dump = ['--mattr=+m,+a,+c,+zicsr', '-d', '-r', '-t', '-h']
    output = str(pipeline/'PIPELINE-SPI-OPEN.o')
    expected = [dict(label='combine', argv=[ex('ld.lld'), '-r', '--no-relax', '-T', str(HERE/'pipeline.ld'),
                    str(provider/'PIPELINE-OPEN.o'), str(spi/'native.o'), '-o', output], returncode=0),
                dict(label='object', argv=[ex('llvm-objdump')]+dump+[output], returncode=0)]
    require(recipe == expected, 'exact pipeline argv/order/exit records')
    expected_spi = [dict(label=label, argv=argv, returncode=0) for label, argv in m.recipes(ROOT, llvm, spi, language)]
    require(json.loads((spi/'recipes.json').read_text(encoding='utf-8')) == expected_spi,
            'exact five SPI producer recipes/flags/exit records')
    inputs = {ROOT/k: v for k, v in PINS.items()}
    inputs.update({HERE/'verify.py': READER_PIN, receipt: OLD_RECEIPTS[language],
                   provider/'PIPELINE-OPEN.o': OLD_PIN, spi/'native.o': m.NATIVE_PIN})
    inputs[Path(__file__).resolve()] = digest(__file__)
    for tool, value in m.TOOLS.items():
        inputs[llvm/(tool+'.exe')] = value
    inputs[llvm.parent/'lib/clang/18/include/stdint.h'] = m.HEADER_PIN
    before_inputs = {p: digest(p) for p in inputs}
    require(before_inputs == inputs, 'all source/linker/reader/tool/header/original pins')
    md = m.md_contract((spi/'native.d').read_text(encoding='utf-8'), ROOT, llvm, spi)
    source_facts = m.source_contract((ROOT/m.SOURCE).read_text(encoding='utf-8'))
    ir_facts = m.ir_contract((spi/'native.ll').read_text(encoding='utf-8'), language)
    native, linked = m.ELF(spi/'native.o'), m.ELF(spi/'linked.elf')
    m.elf_contract(native, native=True)
    m.elf_contract(linked, native=False)
    require(all((spi/(s+'.log')).read_bytes() == b'' for s in ['compile', 'IR', 'link'])
            and (pipeline/'combine.log').read_bytes() == b'', 'successful producer diagnostics empty')
    for directory, label, target in [(pipeline, 'object', 'PIPELINE-SPI-OPEN.o'),
                                    (spi, 'object', 'native.o'), (spi, 'linked', 'linked.elf')]:
        log = (directory/(label+'.log')).read_text(encoding='utf-8')
        require(str(directory/target) in log and 'file format elf32-littleriscv' in log,
                'dump log identifies exact artifact')
    fw = (ROOT/m.FIRMWARE).read_bytes()
    old, obj = m.ELF(provider/'PIPELINE-OPEN.o'), m.ELF(pipeline/'PIPELINE-SPI-OPEN.o')
    facts = contract(obj, old, native, fw, m)
    controls = negatives(obj, old, native, fw, m)
    after = {str(d): inventory(d) for d in [provider, spi, pipeline]}
    require(before == after and {p: digest(p) for p in inputs} == before_inputs,
            'all evidence/tool/source reader bytes stable across verification')
    def portable(value):
        if isinstance(value, str):
            for path, token in [(llvm, '${LLVM_BIN}'), (llvm.parent/'lib/clang/18/include', '${CLANG_INCLUDE}'),
                                (ROOT, '${PROJECT_ROOT}')]:
                value = value.replace(str(path), token).replace(path.as_posix(), token)
            return value.replace('\\', '/')
        if isinstance(value, dict):
            return {portable(str(k)): portable(v) for k, v in value.items()}
        if isinstance(value, list):
            return [portable(v) for v in value]
        return value
    report = dict(schema='TSL9-SPI-partial-pipeline-read-only-v1', language=language,
       result='PASS', checker_sha256=digest(__file__), inputs_before={str(k): v for k, v in before_inputs.items()},
       inputs_after={str(k): digest(k) for k in inputs}, artifact_inventories_before=before,
       artifact_inventories_after=after, commands=recipe, SPI_producer_commands=expected_spi,
       compiler_dependencies=md, SPI_source=source_facts, SPI_IR=ir_facts, facts=facts,
       negative_controls=controls, prior_provider_receipt=dict(sha256=OLD_RECEIPTS[language],
       pinned_historical_receipt=True, reexecuted=False, artifacts_reread=33,
       historical_checker_dependency_closure_replayed=False), limits=[
       'Only existing producer records and actual artifacts are read; no producer command is rerun.',
       'Prior provider receipt is a pinned historical input; its checker/parser dependency closure is not replayed.',
       'ET_REL JAL and RVC ports retain zero immediates; genuine symbol binding does not resolve machine control flow.',
       'The packet provider is absent; original addresses, whole-image layout and private ABI/hardware are not validated.',
       'No target, ISA, MMIO, timing, interrupt context, hardware or flash execution.'])
    return portable(report)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--language', choices=['c', 'cpp'], required=True)
    ap.add_argument('--provider-build', type=Path, required=True, help='parent of provider c/cpp directories')
    ap.add_argument('--spi-build', type=Path, required=True, help='parent of existing SPI c/cpp directories')
    ap.add_argument('--pipeline-build', type=Path, required=True, help='parent of existing partial-link c/cpp directories')
    ap.add_argument('--output', type=Path, help='optional local receipt directory; only verification.json is written')
    ap.add_argument('--strict-firmware-ready', action='store_true', help='always reject this incomplete ET_REL composition')
    args = ap.parse_args()
    m = reader()
    dirs = [(p.resolve()/args.language) for p in [args.provider_build, args.spi_build, args.pipeline_build]]
    require(all(p.is_relative_to(ROOT) for p in dirs), 'evidence must remain inside project')
    report = verify(args.language, *dirs, m)
    if args.strict_firmware_ready:
        print(json.dumps(dict(result='REJECT', reason='partial ET_REL, packet provider and original layout/ABI not closed')))
        return 1
    encoded = (json.dumps(report, indent=2, ensure_ascii=True)+'\n').encode('utf-8')
    if args.output:
        out = args.output.resolve()
        require(out.is_relative_to(HERE/'build') and not any(out.is_relative_to(d) or d.is_relative_to(out) for d in dirs),
                'receipt output must be separate inside experiment build')
        require(not out.is_symlink(), 'receipt directory must not be a symlink')
        out.mkdir(parents=True, exist_ok=True)
        require(not any(out.iterdir()), 'receipt output directory must be empty; never overwrite evidence')
        (out/'verification.json').write_bytes(encoded)
    print(json.dumps(dict(result=report['result'], language=args.language, bytes=352,
                          genuine_FUNCs=16, RELA=17, negative_controls=len(report['negative_controls']),
                          receipt_sha256=sha(encoded), firmware_ready=False)))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, IndexError) as exc:
        print(json.dumps(dict(result='FAIL', error=str(exc))))
        sys.exit(1)
