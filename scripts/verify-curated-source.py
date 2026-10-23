#!/usr/bin/env python3
"""Check curated source provenance; optionally compile/read objects, never execute them."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import sys
import uuid

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / 'src/source-manifest.json'
PARSER = ROOT / 'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py'
PARSER_SHA = '00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metadata():
    manifest = json.loads(MANIFEST.read_bytes())
    need(manifest['schema'] == 'TSL9-curated-source-v1', 'Unknown source manifest')
    paths = [x['destination'] for x in manifest['files']]
    need(len(paths) == len(set(paths)), 'Unique destination paths')
    actual = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'src').rglob('*') if p.is_file() and p.suffix in {'.c', '.h', '.cc', '.cpp', '.hpp'}}
    need(set(paths) == actual, 'Complete curated C/C++ inventory')
    for item in manifest['files']:
        origin, dest = ROOT / item['origin'], ROOT / item['destination']
        need(origin.resolve().is_relative_to(ROOT / 'experiments') and dest.resolve().is_relative_to(ROOT / 'src'), 'Bounded source paths')
        need(sha(origin) == item['origin_sha256'] and sha(dest) == item['sha256'], 'Source hash: ' + item['destination'])
        expected = origin.read_text(encoding='utf-8').replace('\r\n', '\n').rstrip() + '\n'
        for old, new in item['replacements']:
            need(expected.count(old) == 1, 'Unique recorded source adaptation')
            expected = expected.replace(old, new)
        need(dest.read_bytes() == expected.encode('utf-8'), 'Exact recorded adaptations: ' + item['destination'])
    for unit in manifest['native_units']:
        need(sha(ROOT / unit['origin_unit']) == unit['origin_unit_sha256'], 'Pinned original translation unit')
    need(sha(PARSER) == PARSER_SHA, 'Unchanged separate ELF reader')
    return manifest


def flags(unit, mode):
    kind = unit['profile']
    clock = kind in ('clock-query', 'clock-fields')
    irq = kind in ('irq-bank', 'delay-bank')
    spi = kind == 'spi-a0-a3-a4-a5'
    packet = kind in ('packet-a0-a5', 'irq-adapter-a0-a5', 'irq-provider-a0-a1-a2-a4-a5', 'queue-consumer-a0-a5', 'queue-small-a0-a5', 'queue-filter-a0-a5', 'transport-a0-a6', 'record-a0-a5', 'record-predicate-a0-a4-a5', 'peripheral-a0-a6', 'tagged-a0-a5')
    ring = kind == 'ring-bank'
    result = ['--target=riscv32-unknown-elf', '-march=' + ('rv32imac' if clock else 'rv32imac_zicsr' if irq or spi or packet or ring else 'rv32imac_zicsr_zifencei'),
              '-mabi=ilp32', '-Os' if clock else '-Oz']
    if not clock:
        result += ['-mllvm', '-enable-machine-outliner=never']
    result += ['-ffreestanding', '-fno-builtin', '-fno-stack-protector', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables',
               '-mno-relax', '-ffunction-sections', '-fdata-sections', '-Wall', '-Wextra', '-Werror',
               '-x', 'c' if mode == 'c' else 'c++', '-std=c11' if mode == 'c' else '-std=c++17']
    if mode == 'cpp' and not (clock or irq):
        result += ['-fno-exceptions']
    if clock or irq:
        allowed = {10, 12, 13, 14, 15} if kind == 'delay-bank' else {13, 14, 15} if kind == 'clock-query' else {14, 15} if kind == 'clock-fields' else {10, 11, 14, 15}
        result += ['-ffixed-x' + str(n) for n in range(1, 32) if n not in allowed]
    elif kind == 'boot-clock':
        result += ['-ffixed-x' + str(n) for n in range(1, 32) if n not in {2, 12, 13, 14, 15}]
    elif kind == 'runtime-reset':
        result += ['-ffixed-x' + str(n) for n in range(1, 32) if n not in {2, 5, 10, 11, 12}]
    elif kind == 'leaf-a4-a5':
        result += ['-ffixed-x' + str(n) for n in range(1, 32) if n not in {14, 15}]
    elif kind == 'consumer-a0-a4-a5':
        result += ['-ffixed-x' + str(n) for n in range(1, 32) if n not in {10, 14, 15}]
    elif kind == 'receiver-a0-a5':
        result += ['-ffixed-x' + str(n) for n in range(1, 32) if n not in {10, 11, 12, 13, 14, 15}]
    elif kind == 'provider-a0-a5':
        result += ['-ffixed-x' + str(n) for n in range(1, 32) if n not in {10, 11, 12, 13, 14, 15}]
    elif kind == 'spi-a0-a3-a4-a5':
        result += ['-ffixed-x' + str(n) for n in range(1, 32) if n not in {10, 13, 14, 15}]
    elif kind in ('packet-a0-a5', 'irq-adapter-a0-a5', 'queue-consumer-a0-a5', 'queue-filter-a0-a5', 'record-a0-a5', 'tagged-a0-a5'):
        result += ['-ffixed-x' + str(n) for n in range(1, 32) if n not in {10, 11, 12, 13, 14, 15}]
    elif kind in ('transport-a0-a6', 'peripheral-a0-a6'):
        result += ['-ffixed-x' + str(n) for n in range(1, 32) if n not in {10, 11, 12, 13, 14, 15, 16}]
    elif kind == 'record-predicate-a0-a4-a5':
        result += ['-ffixed-x' + str(n) for n in range(1, 32) if n not in {10, 14, 15}]
    elif kind == 'queue-small-a0-a5':
        result += ['-ffixed-x' + str(n) for n in range(1, 32) if n not in {10, 15}]
    elif kind == 'irq-provider-a0-a1-a2-a4-a5':
        result += ['-ffixed-x' + str(n) for n in range(1, 32) if n not in {10, 11, 12, 14, 15}]
    elif kind == 'ring-bank':
        result += ['-ffixed-x' + str(n) for n in range(1, 32) if n not in {6, 10, 11, 12, 13, 14, 15, 16, 17, 28}]
    elif kind == 'adc-bank':
        result += ['-ffixed-x' + str(n) for n in range(5, 32) if n not in range(10, 17)]
    return result


def command(tools, unit, mode, variant, folder):
    source = ROOT / unit['origin_unit' if variant == 'origin' else 'curated_unit']
    return [tools['clang'], *flags(unit, mode), '-c', '-MD', '-MF', folder / 'unit.d', '-MT', 'unit.o', source, '-o', folder / 'unit.o']


def facts(path, reader, allow_data=False):
    elf = reader(path)
    need(elf.kind == 1 and elf.flags == 1, 'Actual RV32 RVC relocatable object')
    funcs = sorted([dict(name=s['name'], binding=s['info'] >> 4, bytes=s['size'], code_sha256=hashlib.sha256(elf.function_bytes(s)).hexdigest())
                    for s in elf.symbols if s['info'] & 15 == 2 and s['size']], key=lambda x: x['name'])
    alloc = [dict(name=s['name'], bytes=s['size'], flags=s['flags'], type=s['type'], sha256=None if s['type']==8 else hashlib.sha256(elf.data(s)).hexdigest())
             for s in elf.sections if s['flags'] & 2 and s['size']]
    reloc = [dict(owner=x['owner'], offset=x['offset'], type=x['type'], addend=x['addend'], symbol=x['symbol']['name']) for x in elf.relocations]
    und = sorted({s['name'] for s in elf.symbols if s['name'] and s['index'] == 0 and s['info'] >> 4 in (1, 2)})
    absolute = sorted({s['name'] for s in elf.symbols if s['index'] == 0xfff1 and s['info'] >> 4 in (1, 2)})
    need((funcs or (allow_data and alloc and not und and not reloc and all(s['flags']==2 or s['type']==8 for s in alloc))) and not absolute,
         'Genuine functions or explicitly admitted data unit without global ABS providers')
    return dict(functions=funcs, allocated_sections=alloc, allocated_bytes=sum(x['bytes'] for x in alloc), relocations=reloc, UND=und, global_ABS=absolute)


def dependencies(folder, variant, resource):
    text = (folder / 'unit.d').read_text(encoding='utf-8').replace('\\\n', ' ')
    target, separator, tail = text.partition(':')
    need(separator and target == 'unit.o', 'Compiler dependency target')
    paths = {Path(re.sub(r'\\(.)', r'\1', token)).resolve() for token in re.findall(r'(?:\\.|[^\s])+', tail)}
    allowed = ROOT / ('src' if variant == 'curated' else 'experiments')
    need(paths and all(p.is_relative_to(allowed) or p.is_relative_to(resource) for p in paths), 'Active include closure stays in selected source tree and compiler resources')
    return {str(p): sha(p) for p in sorted(paths)}


def inventory(base):
    return {p.relative_to(base).as_posix(): sha(p) for p in base.rglob('*') if p.is_file() and p != base / 'verification.json'}


def inputs(manifest):
    paths = {Path(__file__).resolve(), MANIFEST, PARSER}
    for item in manifest['files']:
        paths.update([ROOT / item['origin'], ROOT / item['destination']])
    for unit in manifest['native_units']:
        paths.add(ROOT / unit['origin_unit'])
    return {str(p): sha(p) for p in sorted(paths)}


def audit(base, record, manifest):
    need(record['schema'] == 'TSL9-curated-source-object-comparison-v1', 'Known build schema')
    need(base.is_relative_to(ROOT / 'build/curated-source') and record['inputs'] == inputs(manifest), 'Owned build and exact unchanged inputs')
    tools = {n: Path(v['path']) for n, v in record['tools'].items()}
    need(set(tools) == {'clang'} and all(sha(tools[n]) == record['tools'][n]['sha256'] for n in tools), 'Actual compiler unchanged')
    resource = Path(record['resource_dir'])
    need(sha(base / 'resource.log') == record['resource_log_sha256'], 'Retained compiler resource output')
    need(Path((base / 'resource.log').read_text().strip()).resolve() == resource, 'Actual compiler resource path')
    reader = runpy.run_path(str(PARSER))['ELF']
    results, expected_jobs = [], []
    for unit in manifest['native_units']:
        for mode in ('c', 'cpp'):
            pair = []
            for variant in ('origin', 'curated'):
                folder = base / unit['name'] / mode / variant
                argv = [str(x) for x in command(tools, unit, mode, variant, folder)]
                expected_jobs.append(dict(unit=unit['name'], mode=mode, variant=variant, argv=argv, exit=0, log_sha256=sha(folder / 'compile.log')))
                deps = dependencies(folder, variant, resource)
                pair.append(facts(folder / 'unit.o', reader, unit['name']=='startup-data'))
                need(deps == record['dependencies'][folder.relative_to(base).as_posix()], 'Complete actual header hashes')
            need(pair[0] == pair[1], 'Function code/allocation/relocations differ after source organization: ' + unit['name'] + '/' + mode)
            if unit['name'] == 'init-mask':
                need(pair[1]['functions'] == [dict(name='tsl9_rebuild_register_mask_19106', binding=1, bytes=30,
                     code_sha256='69724f8e22551d238b67e52e25b3c1cbcaa62db28756da9b59a5c96ff7f16d87')], 'Exact original initialization leaf')
            if unit['name'] == 'init-write-sequence':
                need(pair[1]['functions']==[dict(name='tsl9_init_writes_9f4c',binding=1,bytes=40,
                     code_sha256='59ac44eddd4fe4b479d624b08d57d3a8eea6b0cfd273db45b22ec972bb0e38d7')]
                     and not pair[1]['UND'] and not pair[1]['relocations']
                     and pair[1]['allocated_bytes']==40
                     and len(pair[1]['allocated_sections'])==1
                     and pair[1]['allocated_sections'][0]['flags']==6,
                     'Whole 40-byte initialization write leaf; physical peripheral identity and whole startup unproved')
            if unit['name'] == 'irq-flag-leaf':
                need(pair[1]['functions']==[dict(name='tsl9_irq_flag_leaf_16fb6',binding=1,bytes=76,
                     code_sha256='034c35bc979f6b1385f135ad466d7303c31429d9323484a6290314885ad26f85')]
                     and not pair[1]['UND'] and not pair[1]['relocations']
                     and pair[1]['allocated_bytes']==76
                     and len(pair[1]['allocated_sections'])==1
                     and pair[1]['allocated_sections'][0]['flags']==6,
                     'Whole 76-byte status/flag IRQ leaf; complete IRQ entry context and physical hardware unproved')
            if unit['name'] == 'irq-flag-consumer':
                need(pair[1]['functions'] == [
                     dict(name='tsl9_flag_consumer_body', binding=1, bytes=54,
                          code_sha256='9172fbe7045d0324403bdecd1bf6adef23063708e1d56002adad5ad7f6167ce0'),
                     dict(name='tsl9_flag_consumer_entry_17002', binding=1, bytes=8,
                          code_sha256='541ee72019f08804888b256bd0e83014f2c569eb0e0b3bbf6aa8859eb4f6febc')]
                     and pair[1]['UND'] == ['tsl9_receive_entry_16b0a']
                     and pair[1]['relocations'] == [
                         dict(owner='.text.tsl9_flag_consumer_body', offset=n, type=17,
                              addend=0, symbol='tsl9_receive_entry_16b0a') for n in (14, 40)]
                     and pair[1]['allocated_bytes'] == 62
                     and [(s['name'], s['bytes'], s['flags'], s['type'])
                          for s in pair[1]['allocated_sections']] == [
                              ('.text.tsl9_flag_consumer_entry_17002', 8, 6, 1),
                              ('.text.tsl9_flag_consumer_body', 54, 6, 1)],
                     'Measured caller object with exactly two open calls; adjacency and original non-call bytes require separate component verifier')
            if unit['name'] == 'receive-wrapper':
                need(pair[1]['functions'] == [
                     dict(name='tsl9_receive_body', binding=1, bytes=56,
                          code_sha256='a078c685273e6562c855e9e89e34ed9a81736020a73f941b8d5737ddc04e20b1'),
                     dict(name='tsl9_receive_entry_16b0a', binding=1, bytes=14,
                          code_sha256='14eaa914556aaabc7372a9d55c4df77c10d1b2b941caf75126ac89dff8bbc70e')]
                     and pair[1]['UND'] == ['tsl9_receive_buffer_entry_16a7c', 'tsl9_register_read_entry_16994',
                                            'tsl9_register_write_entry_16a30']
                     and pair[1]['relocations'] == [
                         dict(owner='.text.tsl9_receive_body', offset=at, type=17, addend=0, symbol=name)
                         for at, name in [(0, 'tsl9_register_read_entry_16994'),
                                          (18, 'tsl9_receive_buffer_entry_16a7c'),
                                          (32, 'tsl9_receive_buffer_entry_16a7c'),
                                          (52, 'tsl9_register_write_entry_16a30')]]
                     and pair[1]['allocated_bytes'] == 70
                     and [(s['name'], s['bytes'], s['flags'], s['type'])
                          for s in pair[1]['allocated_sections']] == [
                              ('.text.tsl9_receive_entry_16b0a', 14, 6, 1),
                              ('.text.tsl9_receive_body', 56, 6, 1)],
                     'Receiver with four explicit open calls; separate verifier checks physical ports and pipeline linkage, not firmware readiness')
            provider = {
                'register-read': ('tsl9_register_read_entry_16994', 'tsl9_register_read_body', 68,
                    '708967fc3d835d45fe0665ec6f4339d0699fe7e9d28d2724a4a703c35e6ca842', (34, 42, 48)),
                'register-write': ('tsl9_register_write_entry_16a30', 'tsl9_register_write_body', 72,
                    'e353a75d5f75d1c2a2a8f9a33d805bf81fe59b26cd1b5489daefc3a60e5e0b93', (36, 44, 52)),
            }.get(unit['name'])
            if provider:
                entry, body, size, code_pin, sites = provider
                need(pair[1]['functions'] == sorted([
                     dict(name=entry, binding=1, bytes=4,
                          code_sha256='ebd7cd0772b876a27b944db11292d9d2a9964546bdfac87c32dd522230eedb5f'),
                     dict(name=body, binding=1, bytes=size, code_sha256=code_pin)], key=lambda x: x['name'])
                     and pair[1]['UND'] == ['tsl9_spi_transfer_entry_16896']
                     and pair[1]['relocations'] == [
                         dict(owner='.text.'+body, offset=at, type=17, addend=0,
                              symbol='tsl9_spi_transfer_entry_16896') for at in sites]
                     and pair[1]['allocated_bytes'] == 4+size
                     and [(s['name'], s['bytes'], s['flags'], s['type'])
                          for s in pair[1]['allocated_sections']] == [
                              ('.text.'+entry, 4, 6, 1), ('.text.'+body, size, 6, 1)],
                     'Original register-provider code outside three open SPI calls; separate verifier checks frame/slots/GPIO and pipeline linkage')
            if unit['name'] == 'spi-transfer':
                regions = [
                    ('tsl9_spi_transfer_entry_16896', 8, '7f26fb137901cc64a48db59174b41db37688008e3df16571b8bd818f3329d4dc'),
                    ('tsl9_spi_tx_poll_1689e', 8, '43068783c42f65107925427fd8315446af8974f41fabcb47739c64acf8e2f0c5'),
                    ('tsl9_spi_tx_ready_168a6', 16, 'a2e7f4ad6c08e6892bc9d970e6f51c8d418703d6ef0c0383a929b691d7f8a2f7'),
                    ('tsl9_spi_rx_poll_168b6', 8, 'b8313f910f50805168364919a92ca5af50511051eba014e671b92346180f14f8'),
                    ('tsl9_spi_rx_done_168be', 10, '64b2d800f1106e4120e8945478a00b7ccc2c3e37d4554751c7c4a347274dc99b'),
                    ('tsl9_spi_tx_wait_168c8', 8, 'da6a2b409c5225c45305d7e49665a17af75c0e9148d6ae36fccf13a055280692'),
                    ('tsl9_spi_timeout_168d0', 4, '9c28941eb64aa06520e1ff0e0058871b3bfbcea0b07d72ad58477e8d0d7350cb'),
                    ('tsl9_spi_rx_wait_168d4', 10, '45617f06137de470f74f6aa33092020b2949ca144491c77687811e930ff873c1'),
                ]
                relocations = [
                    ('tsl9_spi_tx_poll_1689e', 6, 44, 'tsl9_spi_tx_wait_168c8'),
                    ('tsl9_spi_rx_poll_168b6', 6, 44, 'tsl9_spi_rx_wait_168d4'),
                    ('tsl9_spi_tx_wait_168c8', 6, 44, 'tsl9_spi_tx_poll_1689e'),
                    ('tsl9_spi_rx_wait_168d4', 6, 44, 'tsl9_spi_rx_poll_168b6'),
                    ('tsl9_spi_rx_wait_168d4', 8, 45, 'tsl9_spi_timeout_168d0'),
                ]
                need(pair[1]['functions'] == sorted([
                     dict(name=n, binding=1, bytes=z, code_sha256=h) for n, z, h in regions], key=lambda x: x['name'])
                     and pair[1]['allocated_sections'] == [dict(name='.text.'+n, bytes=z, flags=6, type=1, sha256=h)
                          for n, z, h in regions]
                     and pair[1]['allocated_bytes'] == 72 and not pair[1]['UND']
                     and pair[1]['relocations'] == [dict(owner='.text.'+owner, offset=at, type=kind, addend=0, symbol=target)
                          for owner, at, kind, target in relocations],
                     'Eight private SPI regions and five defined RVC ports; separate nominal-link verifier proves original72B, not ordinary C ABI or firmware readiness')
            if unit['name'] == 'packet-receive':
                regions = [
                    ('tsl9_receive_buffer_entry_16a7c', 14, '101a382fcf71900631fe5dc97b6e0cab025169982e2acac53bb12cea36974088'),
                    ('tsl9_packet_receive_body', 116, 'b1a6d7d72e3ef5099c2d52aef686d396e89aeb04436d8da196e51fa5f2b4208f'),
                    ('tsl9_packet_receive_finish_16afe', 12, '0688d624f9b479028d25e4fa4abd146dfc2d31a83027e163c46a9a50d8914c2d'),
                ]
                relocations = [
                    (20, 17, 'tsl9_spi_transfer_entry_16896'),
                    (32, 17, 'tsl9_spi_transfer_entry_16896'),
                    (38, 17, 'tsl9_spi_transfer_entry_16896'),
                    (74, 44, 'tsl9_packet_receive_finish_16afe'),
                    (92, 16, 'tsl9_packet_receive_finish_16afe'),
                    (112, 17, 'tsl9_ring_insert_entry_12bc8'),
                ]
                need(pair[1]['functions'] == sorted([
                     dict(name=n, binding=1, bytes=z, code_sha256=h) for n, z, h in regions], key=lambda x: x['name'])
                     and pair[1]['allocated_sections'] == [dict(name='.text.'+n, bytes=z, flags=6, type=1, sha256=h)
                          for n, z, h in regions]
                     and pair[1]['allocated_bytes'] == 142 and not pair[1]['global_ABS']
                     and pair[1]['UND'] == ['tsl9_ring_insert_entry_12bc8', 'tsl9_spi_transfer_entry_16896']
                     and pair[1]['relocations'] == [dict(owner='.text.tsl9_packet_receive_body', offset=at,
                          type=kind, addend=0, symbol=target) for at, kind, target in relocations],
                     'Three private architectural regions with 120 original noncontrol bytes; six pending relocations need separate adjacency/ABI evidence, not firmware readiness')
            if unit['name'] == 'irq-provider':
                regions = [
                    ('tsl9_irq_provider_18d78', 18, '768c26f4bc8120f70b78b54f501973e47f188f17151bb6155f9d00275119b328'),
                    ('tsl9_irq_provider_standard_18d8a', 8, 'f1fb8fa6ddc64973cfb807577252763272e8079836acefecc7acf4dadc174efd'),
                    ('tsl9_irq_provider_common_18d92', 108, 'a2d47d86eedb93d61bf6a13bc4a8bff5040d8b399c65baa8ad5909da4f160981'),
                    ('tsl9_irq_provider_bank0_18dfe', 10, '8f92d05c88032ebb9b0446388802b40c9c4a5e049eb4e76c4ad7a161c2877a23'),
                    ('tsl9_irq_provider_extended_18e08', 10, '591775067bcef9479e316c4d9ee9fe23835b684c2568a84025ca01032e9351fb'),
                    ('tsl9_irq_provider_bank1_18e12', 10, 'b7c975b1366122e19f4bb75ab1da3e19f42404e4ff2e6d1321d115db36afe7d8'),
                ]
                edges = [
                    ('tsl9_irq_provider_18d78', 16, 44, 'tsl9_irq_provider_extended_18e08'),
                    ('tsl9_irq_provider_common_18d92', 106, 44, 'tsl9_irq_provider_bank1_18e12'),
                    ('tsl9_irq_provider_extended_18e08', 8, 45, 'tsl9_irq_provider_common_18d92'),
                ]
                need(pair[1]['functions'] == sorted([
                    dict(name=n, binding=1, bytes=z, code_sha256=h) for n, z, h in regions], key=lambda x: x['name'])
                    and pair[1]['allocated_sections'] == [
                        dict(name='.text.'+n, bytes=z, flags=6, type=1, sha256=h) for n, z, h in regions]
                    and pair[1]['allocated_bytes'] == 164 and not pair[1]['UND']
                    and pair[1]['relocations'] == [
                        dict(owner='.text.'+owner, offset=offset, type=kind, addend=0, symbol=target)
                        for owner, offset, kind, target in edges],
                    'Six private provider regions and three defined edges; nominal verifier proves original164B/fresh reads/registers, not IRQ/silicon or firmware readiness')
            if unit['name'] == 'queue-small-providers':
                regions = [
                    ('tsl9_queue_status_81aa', 6, '887c2bfb847a7e013acebac38c8be3f2bed06fd44305080ad6fc7ca3593e8fc3'),
                    ('tsl9_queue_clear_820c', 18, '643c424c37ca788946153c36cbfaebb37644464f84cc49f7fe2ff92b7c7c2b90'),
                ]
                need(pair[1]['functions'] == sorted([
                    dict(name=n, binding=1, bytes=z, code_sha256=h) for n, z, h in regions], key=lambda x: x['name'])
                    and pair[1]['allocated_sections'] == [
                        dict(name='.text.'+n, bytes=z, flags=6, type=1, sha256=h) for n, z, h in regions]
                    and pair[1]['allocated_bytes'] == 24 and not pair[1]['UND'] and not pair[1]['relocations'],
                    'Two actual C leaves6/18B with fully assembler-resolved local branch; source-copy proof does not prove original placement, consumer composition or firmware readiness')
            if unit['name'] == 'tagged-dispatch':
                regions = [
                    ('tsl9_dispatch_external_16b7c', 16, '7555b3ff425bfe27d122aa9f0fa3751b0474b3b146aff45df72527c948acff8b'),
                    ('tsl9_tagged_config_16b8c', 16, '17883f6c5542aee34744e26c3904c97d8b95cc2ae662fa2e8d843c36f2cac7c9'),
                    ('tsl9_tagged_frame_16b9c', 12, '63171dcd3b860fff2c39673390d00c53a96f142593ede9e24d94a7dc2e6286e2'),
                    ('tsl9_tagged_length_16ba8', 10, '5469b9d86ae87c8659771ef3a672fdebef3a93e531522e8db7f31baaa2b835fe'),
                    ('tsl9_tagged_header_16bb2', 32, '96ee0b2191cb6ea5e2e6af8686afef2de6e7075663d233624bcb8ba55fd8961e'),
                    ('tsl9_tagged_payload_16bd2', 40, '2108f92a4956bc700f688bc30ea72f79506fd262974c756d99aace8e71eeb4ef'),
                    ('tsl9_tagged_loop_setup_16bfa', 4, '5aa13f56a2a40d8db468e1b0331efbced5ae2b64482a5034fe5661da78b446be'),
                    ('tsl9_tagged_loop_16bfe', 22, '16ea94d3d1f26c28988d440f76548fe1dffb603f1e211a1403b579ab65f704b7'),
                    ('tsl9_tagged_send_16c14', 28, '8876ee5a6c0f2cbfe038e2bb2fde9f9bcf4b0637623260f64ee53133514f41ae'),
                    ('tsl9_tagged_request_16c30', 14, 'df514c0a8d44351703e77d6a5f1fea9ff9c2b91599dfb0999ebb27d7863f0e50'),
                    ('tsl9_tagged_status_16c3e', 20, 'd722a9d5a53a7ee3b1fe3cb2c9bbb26386859cb1c9117481282a6a691429d9b4'),
                    ('tsl9_tagged_finish_16c52', 16, '6fdfaeea019a0e0af3a293b252ee98fc085112b3a4b557bc99a257cd74da0f4a'),
                    ('tsl9_tagged_busy_16c62', 10, '481ae38d48d1fac7662a3ff96f344955364caeb467c42d46dfe0b7e068d653ec'),
                    ('tsl9_tagged_invalid_16c6c', 2, '06a82e72be7d2ece7c31910654dd3b389ee65282466e1b34daa1d60b0d3b42e3'),
                    ('tsl9_tagged_early_16c6e', 4, '9357712eb4a240a5427265f17c9e858a95d8d53bdcfe72f1583660a9819053f9'),
                ]
                edges = [
                    ('tsl9_dispatch_external_16b7c', 12, 16, 'tsl9_tagged_invalid_16c6c'),
                    ('tsl9_tagged_config_16b8c', 14, 44, 'tsl9_tagged_early_16c6e'),
                    ('tsl9_tagged_length_16ba8', 6, 16, 'tsl9_tagged_finish_16c52'),
                    ('tsl9_tagged_header_16bb2', 28, 17, 'tsl9_tagged_external_8520'),
                    ('tsl9_tagged_loop_16bfe', 14, 17, 'tsl9_register_read_entry_16994'),
                    ('tsl9_tagged_loop_16bfe', 20, 44, 'tsl9_tagged_busy_16c62'),
                    ('tsl9_tagged_send_16c14', 24, 17, 'tsl9_tagged_external_168de'),
                    ('tsl9_tagged_request_16c30', 10, 17, 'tsl9_tagged_external_1693e'),
                    ('tsl9_tagged_status_16c3e', 6, 17, 'tsl9_register_read_entry_16994'),
                    ('tsl9_tagged_busy_16c62', 2, 16, 'tsl9_tagged_loop_16bfe'),
                    ('tsl9_tagged_busy_16c62', 8, 45, 'tsl9_tagged_finish_16c52'),
                ]
                need(pair[1]['functions'] == sorted([
                    dict(name=n,binding=1,bytes=z,code_sha256=h) for n,z,h in regions],key=lambda x:x['name'])
                    and pair[1]['allocated_sections'] == [
                        dict(name='.text.'+n,bytes=z,flags=6,type=1,sha256=h) for n,z,h in regions]
                    and pair[1]['allocated_bytes'] == 246
                    and pair[1]['UND'] == ["tsl9_register_read_entry_16994","tsl9_tagged_external_168de","tsl9_tagged_external_1693e","tsl9_tagged_external_8520"]
                    and not pair[1]['global_ABS']
                    and pair[1]['relocations'] == [
                        dict(owner='.text.'+n,offset=o,type=k,addend=0,symbol=t) for n,o,k,t in edges],
                    'Fifteen private246B regions/11pending controls/four genuine UND retain exact source-object bodies; then-live stack/register ports are not ordinary ABI, provider composition or firmware readiness')
            if unit['name'] == 'peripheral-write':
                regions = [
                    ('tsl9_dispatch_external_18ca4', 34, '117dfb3a3f1c230701512ac1faff9633d91a8bddb11f039ae709872c6aa8573e'),
                    ('tsl9_peripheral_selected_18cc6', 38, '8b0f63979071194cc551121f7c7b54efc9a3a67b7a628c42e5f1710a57a8e084'),
                    ('tsl9_peripheral_metadata_18cec', 110, 'e89ecf760d1080fdffd0aecf750a2750f0bf9f641f4a4f332f5a4620b5120af3'),
                    ('tsl9_peripheral_finish_18d5a', 4, '2dba7664a0b80ec332186fa935d7713ce577e84f92dde7a55d2ca1e635effea1'),
                    ('tsl9_peripheral_select0_18d5e', 4, 'ba6f93ecbcd031a0ef95a185c0a5fa8f8062b797ac9c819a4404da23a6f4439c'),
                    ('tsl9_peripheral_select1_18d62', 4, '28e4f78951addc44a8cf469bb107400afb870512519c49d32b721ab3a3c1c7be'),
                    ('tsl9_peripheral_alternate_18d66', 18, 'fab5a3a9124532a5b80a9fd1e474633edbff220d46b59a6122ebde5e95a3c626'),
                ]
                edges = [
                    ('tsl9_dispatch_external_18ca4', 6, 16, 'tsl9_peripheral_select0_18d5e'),
                    ('tsl9_dispatch_external_18ca4', 16, 16, 'tsl9_peripheral_select1_18d62'),
                    ('tsl9_dispatch_external_18ca4', 28, 16, 'tsl9_peripheral_finish_18d5a'),
                    ('tsl9_peripheral_selected_18cc6', 24, 44, 'tsl9_peripheral_alternate_18d66'),
                    ('tsl9_peripheral_select0_18d5e', 2, 45, 'tsl9_peripheral_selected_18cc6'),
                    ('tsl9_peripheral_select1_18d62', 2, 45, 'tsl9_peripheral_selected_18cc6'),
                    ('tsl9_peripheral_alternate_18d66', 16, 45, 'tsl9_peripheral_metadata_18cec'),
                ]
                need(pair[1]['functions'] == sorted([
                    dict(name=n, binding=1, bytes=z, code_sha256=h) for n,z,h in regions],key=lambda x:x['name'])
                    and pair[1]['allocated_sections'] == [
                        dict(name='.text.'+n,bytes=z,flags=6,type=1,sha256=h) for n,z,h in regions]
                    and pair[1]['allocated_bytes'] == 212 and not pair[1]['UND']
                    and pair[1]['relocations'] == [
                        dict(owner='.text.'+n,offset=o,type=k,addend=0,symbol=t) for n,o,k,t in edges],
                    'Seven private212B regions and seven genuine pending controls; nominal whole-original proof is separate from source-copy equality and physical firmware readiness')
            if unit['name'] == 'record-predicate':
                name = 'tsl9_dispatch_external_821e'
                pin = '4af30f18b196e304a5b6d30bb167ee2a02c567c4ffcf4e36bb4f72e6204bcdcd'
                need(pair[1]['functions'] == [dict(name=name, binding=1, bytes=42, code_sha256=pin)]
                     and pair[1]['allocated_sections'] == [dict(name='.text.'+name, bytes=42, flags=6, type=1, sha256=pin)]
                     and pair[1]['allocated_bytes'] == 42 and not pair[1]['UND'] and not pair[1]['relocations'],
                     'One complete original42B/15i predicate; source equality does not establish GP/memory/IRQ or firmware readiness')
            if unit['name'] == 'record-dispatch':
                regions = [
                    ('tsl9_queue_external_12a08', 12, 'e7bcac7f140b8e55de4726bdf047e433134849d4c1ae0dbd7e28a231d7a0298a'),
                    ('tsl9_dispatch_status_12a14', 2, 'c57aa6a4279377063b17c554d3e33a3490e67a9a65e9d9e4ced2e6c2301d1cd7'),
                    ('tsl9_dispatch_ID_12a16', 10, '0e22610b42410b43c5b454a1aa54ff39f928f6ff55d26fe0dbd1b97016a4aa87'),
                    ('tsl9_dispatch_query_12a20', 8, '95ddd71bde22e4e24b8cd11af59a6e7564fc54fcbb82513f2d1867e7574bb005'),
                    ('tsl9_dispatch_tag_12a28', 6, '1fff6d6a046d95cbf88f3c7d4e9da5fefa988feaf6c2b0bddeceec16991117d5'),
                    ('tsl9_dispatch_copy_12a2e', 34, '56e5092e3b6a322ae156ffff2c32611fde2e8c0f00169bc699b0fe1a5cd4d658'),
                    ('tsl9_dispatch_peripheral_12a50', 14, '33b5904c8f2b3a0c4c22b3dbf5ecc354f98caef3f666e2eb836125188be4dbd9'),
                    ('tsl9_dispatch_finish_12a5e', 8, 'b0805dbb6b57307623b544f18b6ae086d0024607adbba3f3c43944984c8c5c84'),
                    ('tsl9_dispatch_tagged_12a66', 8, '2e37ed26ba9ac0da23a0ef499161b42709bf82fda093533dec882c2c63869f7b'),
                ]
                edges = [
                    ('tsl9_queue_external_12a08', 8, 17, 'tsl9_queue_external_81aa'),
                    ('tsl9_dispatch_status_12a14', 0, 44, 'tsl9_dispatch_query_12a20'),
                    ('tsl9_dispatch_ID_12a16', 6, 16, 'tsl9_dispatch_finish_12a5e'),
                    ('tsl9_dispatch_query_12a20', 2, 17, 'tsl9_dispatch_external_821e'),
                    ('tsl9_dispatch_query_12a20', 6, 44, 'tsl9_dispatch_finish_12a5e'),
                    ('tsl9_dispatch_tag_12a28', 4, 44, 'tsl9_dispatch_tagged_12a66'),
                    ('tsl9_dispatch_peripheral_12a50', 10, 17, 'tsl9_dispatch_external_18ca4'),
                    ('tsl9_dispatch_tagged_12a66', 2, 17, 'tsl9_dispatch_external_16b7c'),
                    ('tsl9_dispatch_tagged_12a66', 6, 45, 'tsl9_dispatch_finish_12a5e'),
                ]

                need(pair[1]['functions'] == sorted([
                    dict(name=n, binding=1, bytes=z, code_sha256=h) for n, z, h in regions], key=lambda x: x['name'])
                    and pair[1]['allocated_sections'] == [
                        dict(name='.text.'+n, bytes=z, flags=6, type=1, sha256=h) for n, z, h in regions]
                    and pair[1]['allocated_bytes'] == 102
                    and pair[1]['UND'] == sorted(['tsl9_queue_external_81aa', 'tsl9_dispatch_external_821e',
                                                 'tsl9_dispatch_external_18ca4', 'tsl9_dispatch_external_16b7c'])
                    and pair[1]['relocations'] == [
                        dict(owner='.text.'+owner, offset=at, type=kind, addend=0, symbol=target)
                        for owner, at, kind, target in edges],
                    'Nine private102B regions with4 real UND and9 pending controls. All74 whole noncontrol bytes/689 retained bits and then-live frame/call residues require the separate formal checker; not physical firmware readiness')
            if unit['name'] == 'transport-frame':
                regions = [
                    ('tsl9_filter_external_8a56', 8, '487c6497a4cdd3be5d1018e698b41718911d4f4e55c950749df0587a5b69fb99'),
                    ('tsl9_transport_frame_8a5e', 28, 'bd8820e474fdbaa88c3e78fa10c67e4c26c12a6f336d9419c9f30536346a9a29'),
                    ('tsl9_transport_first_8a7a', 22, '5e05e1908298292725f46deaa0965504ed78f273a11365930a64c9912472bebf'),
                    ('tsl9_transport_first_result_8a90', 6, '2825abb712313e407039a5408d13c40eff1aafe5afe21bdda2b0b8524823df82'),
                    ('tsl9_transport_second_8a96', 32, '57212634633f2bd2921798e224c6ef06bb29d029a6f7837d3a69d75d7b0cb4fc'),
                    ('tsl9_transport_second_result_8ab6', 8, '31228a28aac242ce247efd7cef8d196d609e3938b48650737a7cefea156840d5'),
                    ('tsl9_transport_reject_8abe', 14, 'e17a53ead25bd1a6fe0a310d0d21e5de5d89c8273e1e27d1919183fe17b55ac7'),
                    ('tsl9_transport_select0_8acc', 2, '6a632187a3abf9bebb66d43368fccd612f631cbcfb6fdcc90337233c41ff1c7a'),
                    ('tsl9_transport_pack_8ace', 60, '8ef4caa383cbac0fe8f88537008b4513ec65c48c6cf4d39aeb89d77f92ca338a'),
                    ('tsl9_transport_test_8b0a', 10, '04322d6fd6038c11eb526b48469f31e0326d8429a0d19cdaba3b96380b0429a1'),
                    ('tsl9_transport_finish_8b14', 62, 'aebf41c8da4c992eb96144b63d6f8385a09ff5e058eedc6abe66643fe5b85c11'),
                    ('tsl9_transport_copy_8b52', 26, '143abdbf675255dee05bf932901b1d601769989e1c4491ea77f8305d84ad4c34'),
                    ('tsl9_transport_bare_return_8b6c', 2, '7529d4e6ceb037815e2664a7277abb404b02f0bf9ddbf5c11658f52448221cba'),
                ]
                edges = [
                    ('tsl9_filter_external_8a56', 4, 16, 'tsl9_transport_bare_return_8b6c'),
                    ('tsl9_transport_frame_8a5e', 24, 16, 'tsl9_transport_second_8a96'),
                    ('tsl9_transport_first_8a7a', 4, 16, 'tsl9_transport_second_8a96'),
                    ('tsl9_transport_first_result_8a90', 2, 16, 'tsl9_transport_select0_8acc'),
                    ('tsl9_transport_second_8a96', 4, 16, 'tsl9_transport_reject_8abe'),
                    ('tsl9_transport_second_8a96', 12, 16, 'tsl9_transport_reject_8abe'),
                    ('tsl9_transport_second_result_8ab6', 4, 16, 'tsl9_transport_pack_8ace'),
                    ('tsl9_transport_test_8b0a', 6, 16, 'tsl9_transport_copy_8b52'),
                    ('tsl9_transport_copy_8b52', 24, 45, 'tsl9_transport_test_8b0a'),
                ]
                need(pair[1]['functions'] == sorted([
                    dict(name=n, binding=1, bytes=z, code_sha256=h) for n, z, h in regions], key=lambda x: x['name'])
                    and pair[1]['allocated_sections'] == [
                        dict(name='.text.'+n, bytes=z, flags=6, type=1, sha256=h) for n, z, h in regions]
                    and pair[1]['allocated_bytes'] == 280 and not pair[1]['UND']
                    and pair[1]['relocations'] == [
                        dict(owner='.text.'+owner, offset=at, type=kind, addend=0, symbol=target)
                        for owner, at, kind, target in edges],
                    'Thirteen private280B transport regions and9 pending local edges; source-copy equality is separate from typed/SSA/opaque-call/physical compatibility proofs')
            if unit['name'] == 'queue-filter':
                regions = [
                    ('tsl9_queue_external_82d2', 54, 'b2b79614061f2ccc59cadfe7a5fc41da6674926c3d0ce21b881bd8de9483781e'),
                    ('tsl9_filter_scan_8308', 32, 'b13863c4779d5c59dc3966c930c7a4fe9b28f755b448808be34888b69f36f7d5'),
                    ('tsl9_filter_pack_8328', 48, '2bd4fe589cd5a6cc85cb147a5f55160528429e6cd15a9075cb28056ffff4c414'),
                    ('tsl9_filter_emit_8358', 18, 'be32c019e9db23c873d4e608e94fe09a1015f2cbbe4846bb15680a69649d0c16'),
                    ('tsl9_filter_test_836a', 4, '4dd9686eb458bbfb45cfe08dc3a1dd0cc04825c845fc274398717f473e164796'),
                    ('tsl9_filter_finish_836e', 28, '227907f1d643e603d33edefd0f6339b9e475e13a4654167e21f68bfdcc3997ee'),
                    ('tsl9_filter_second_838a', 4, 'f04b6f869015ca51affa2faa6f060d45eac6a2ef0cda466f36c44248d008ce04'),
                ]
                edges = [
                    ('tsl9_filter_scan_8308', 10, 16, 'tsl9_filter_test_836a'),
                    ('tsl9_filter_scan_8308', 18, 16, 'tsl9_filter_test_836a'),
                    ('tsl9_filter_scan_8308', 30, 44, 'tsl9_filter_test_836a'),
                    ('tsl9_filter_pack_8328', 6, 16, 'tsl9_filter_test_836a'),
                    ('tsl9_filter_emit_8358', 16, 45, 'tsl9_filter_external_8a56'),
                    ('tsl9_filter_test_836a', 0, 16, 'tsl9_filter_second_838a'),
                    ('tsl9_filter_second_838a', 2, 45, 'tsl9_filter_scan_8308'),
                ]
                need(pair[1]['functions'] == sorted([
                    dict(name=n, binding=1, bytes=z, code_sha256=h) for n, z, h in regions], key=lambda x: x['name'])
                    and pair[1]['allocated_sections'] == [
                        dict(name='.text.'+n, bytes=z, flags=6, type=1, sha256=h) for n, z, h in regions]
                    and pair[1]['allocated_bytes'] == 188
                    and pair[1]['UND'] == ['tsl9_filter_external_8a56']
                    and pair[1]['relocations'] == [
                        dict(owner='.text.'+owner, offset=at, type=kind, addend=0, symbol=target)
                        for owner, at, kind, target in edges],
                    'Seven private188B filter regions and7 pending edges; one real UND compressed link-call8A56. Separate typed/SSA checker proves166 whole noncontrol bytes, then-live registers and C.JAL RA; not original placement or firmware readiness')
            if unit['name'] == 'queue-consumer':
                regions = [
                    ('tsl9_queue_entry_12c58', 46, 'b62b7b72fe9434d4f8074ef21e434b91f56c2b2bf3350be8d8ec4099ead404e5'),
                    ('tsl9_queue_scan_12c86', 32, 'bc696cee29f69cb20c69150dbc8164d3a09f3f0bb00765b3fe9b8bd9188fff28'),
                    ('tsl9_queue_release_12ca6', 14, 'd7b85d950e815d38e8656a916588982e82ca74061763e6f6faca71891838ecaa'),
                    ('tsl9_queue_validate_12cb4', 58, '54a596cdf010829ba79c5b8e8140b848e4caa52100036c554ba827e727c180e9'),
                    ('tsl9_queue_advance_12cee', 10, '45d704a3c96dca21c1f6a85f19602bbf29ccfed5842290d3bf3c7a82ebc7707c'),
                    ('tsl9_queue_finish_12cf8', 22, 'fd023936c707df0065acdb505542c01aac895b4b7a048a1e7c9cbaf0c76d5ee0'),
                    ('tsl9_queue_zero_12d0e', 52, 'c8757cd2eb587e8f9bd479c3d6d351b46aebca83661b37c5934e556fa0fea897'),
                    ('tsl9_queue_emit_12d42', 10, '8668966d892db043fd45de554f967eb3db61decb14f04bc051174c5eb0529c0d'),
                    ('tsl9_queue_response_12d4c', 44, '57c7452d79fa688548fbc9da4c4cd94e1cc00f8ff03336f68c5e94f6d1dc166a'),
                    ('tsl9_queue_other_12d78', 26, 'c3276890fc580c91a057a2e672630d17fcb4ad264bdec1fca6bd101e67c0efd5'),
                ]
                edges = [
                    ('tsl9_queue_scan_12c86', 14, 44, 'tsl9_queue_advance_12cee'),
                    ('tsl9_queue_release_12ca6', 10, 17, 'tsl9_queue_external_82d2'),
                    ('tsl9_queue_validate_12cb4', 0, 44, 'tsl9_queue_advance_12cee'),
                    ('tsl9_queue_validate_12cb4', 6, 16, 'tsl9_queue_other_12d78'),
                    ('tsl9_queue_validate_12cb4', 16, 16, 'tsl9_queue_advance_12cee'),
                    ('tsl9_queue_validate_12cb4', 28, 16, 'tsl9_queue_advance_12cee'),
                    ('tsl9_queue_validate_12cb4', 40, 16, 'tsl9_queue_advance_12cee'),
                    ('tsl9_queue_validate_12cb4', 48, 44, 'tsl9_queue_zero_12d0e'),
                    ('tsl9_queue_validate_12cb4', 54, 16, 'tsl9_queue_response_12d4c'),
                    ('tsl9_queue_advance_12cee', 6, 16, 'tsl9_queue_scan_12c86'),
                    ('tsl9_queue_zero_12d0e', 0, 17, 'tsl9_queue_external_820c'),
                    ('tsl9_queue_zero_12d0e', 8, 17, 'tsl9_queue_external_9454'),
                    ('tsl9_queue_zero_12d0e', 14, 17, 'tsl9_queue_external_9b36'),
                    ('tsl9_queue_zero_12d0e', 30, 17, 'tsl9_queue_external_12abe'),
                    ('tsl9_queue_zero_12d0e', 46, 16, 'tsl9_queue_emit_12d42'),
                    ('tsl9_queue_emit_12d42', 4, 17, 'tsl9_queue_external_12abe'),
                    ('tsl9_queue_emit_12d42', 8, 45, 'tsl9_queue_advance_12cee'),
                    ('tsl9_queue_response_12d4c', 8, 16, 'tsl9_queue_advance_12cee'),
                    ('tsl9_queue_response_12d4c', 38, 17, 'tsl9_queue_external_12a08'),
                    ('tsl9_queue_response_12d4c', 42, 45, 'tsl9_queue_advance_12cee'),
                    ('tsl9_queue_other_12d78', 10, 44, 'tsl9_queue_advance_12cee'),
                    ('tsl9_queue_other_12d78', 12, 17, 'tsl9_queue_external_81aa'),
                    ('tsl9_queue_other_12d78', 16, 44, 'tsl9_queue_advance_12cee'),
                    ('tsl9_queue_other_12d78', 20, 17, 'tsl9_queue_external_14d2e'),
                    ('tsl9_queue_other_12d78', 24, 45, 'tsl9_queue_advance_12cee'),
                ]
                need(pair[1]['functions'] == sorted([
                    dict(name=n, binding=1, bytes=z, code_sha256=h) for n, z, h in regions], key=lambda x: x['name'])
                    and pair[1]['allocated_sections'] == [
                        dict(name='.text.'+n, bytes=z, flags=6, type=1, sha256=h) for n, z, h in regions]
                    and pair[1]['allocated_bytes'] == 314
                    and pair[1]['UND'] == ['tsl9_queue_external_12a08', 'tsl9_queue_external_12abe', 'tsl9_queue_external_14d2e', 'tsl9_queue_external_81aa', 'tsl9_queue_external_820c', 'tsl9_queue_external_82d2', 'tsl9_queue_external_9454', 'tsl9_queue_external_9b36']
                    and pair[1]['relocations'] == [
                        dict(owner='.text.'+owner, offset=at, type=kind, addend=0, symbol=target)
                        for owner, at, kind, target in edges],
                    'Ten private queue regions with25 pending edges/eight genuine UND; separate formal checker proves107 instructions/230 complete noncontrol bytes/2163 retained bits, not resolved calls or firmware readiness')
            if unit['name'] == 'ring-irq-adapter':
                regions = [
                    ('tsl9_ring_irq_entry_12c24', 14, '203ff4761ab235fd4dc972c1319ac55557cab310bf1eb01c58dfe7fa5583a094'),
                    ('tsl9_ring_irq_frame_12c32', 10, 'ad3c0f1a060b6e9dc02eaf0538b61b6b24d28936f0b7fd52625ae283969720ab'),
                    ('tsl9_ring_irq_dispatch_12c3c', 18, '6a1fbdb870d4e659c6d5b907a1596dc94cde23db9a96fe8bb8799f6dffa731db'),
                    ('tsl9_ring_irq_finish_12c4e', 6, '0bec86c6da5a0b7ae81fe8c9270303a2abb145a525d5b7986c0f673d1d464857'),
                    ('tsl9_ring_irq_empty_12c54', 4, '1e7046a0a49788a582f66b43e7121816806539f4491168ed6b45d72da350013a'),
                ]
                edges = [
                    ('tsl9_ring_irq_entry_12c24', 12, 44, 'tsl9_ring_irq_empty_12c54'),
                    ('tsl9_ring_irq_frame_12c32', 6, 17, 'tsl9_irq_provider_18d78'),
                    ('tsl9_ring_irq_dispatch_12c3c', 14, 17, 'tsl9_ring_insert_entry_12bc8'),
                ]
                need(pair[1]['functions'] == sorted([
                    dict(name=n, binding=1, bytes=z, code_sha256=h) for n, z, h in regions], key=lambda x: x['name'])
                    and pair[1]['allocated_sections'] == [
                        dict(name='.text.'+n, bytes=z, flags=6, type=1, sha256=h) for n, z, h in regions]
                    and pair[1]['allocated_bytes'] == 52
                    and pair[1]['UND'] == ['tsl9_irq_provider_18d78', 'tsl9_ring_insert_entry_12bc8']
                    and pair[1]['relocations'] == [
                        dict(owner='.text.'+owner, offset=at, type=kind, addend=0, symbol=target)
                        for owner, at, kind, target in edges],
                    'Five private IRQ regions;42 original noncontrol bytes and three honest pending edges; then-live SP/MRET and full IRQ/provider ABI need separate proof')
            if unit['name'] == 'ring-insert':
                regions = [
                    ('tsl9_ring_insert_entry_12bc8', 8, '157b2d92ee3de3dd29a04ed155700152f87a87db4fcbb174b147c2c7ddc1809d'),
                    ('tsl9_ring_init_12bd0', 16, 'f7710fc92bad19150fa81576d8ff876a010a63ece699187c888ad1041b5656f9'),
                    ('tsl9_ring_scan_12be0', 50, '328952811c295258582acaf02c687783e2a5e05d557724c2c0e743c909ee245b'),
                    ('tsl9_ring_finish_12c12', 10, '5337349bd213a4afedd4bb2b40e85f8a135ca2a3ee774b3c2da607774b084509'),
                    ('tsl9_ring_advance_12c1c', 8, '4a289d9c0208485c9f3f4d40d21817af5c24f6629d979aa0769d1a1cf0a9e068'),
                ]
                edges = [
                    ('tsl9_ring_scan_12be0', 18, 16, 'tsl9_ring_advance_12c1c'),
                    ('tsl9_ring_advance_12c1c', 2, 16, 'tsl9_ring_scan_12be0'),
                    ('tsl9_ring_advance_12c1c', 6, 45, 'tsl9_ring_finish_12c12'),
                ]
                need(pair[1]['functions'] == sorted([
                    dict(name=n, binding=1, bytes=z, code_sha256=h) for n, z, h in regions], key=lambda x: x['name'])
                    and pair[1]['allocated_sections'] == [
                        dict(name='.text.'+n, bytes=z, flags=6, type=1, sha256=h) for n, z, h in regions]
                    and pair[1]['allocated_bytes'] == 92 and not pair[1]['UND']
                    and pair[1]['relocations'] == [
                        dict(owner='.text.'+owner, offset=at, type=kind, addend=0, symbol=target)
                        for owner, at, kind, target in edges],
                    'Five private ring regions with three defined edges; nominal verifier proves original92B and PC-derived base, not resident identity or firmware readiness')
            if unit['name'] == 'delay-registers':
                need(pair[1]['functions'] == [dict(name='tsl9_delay_registers_19764', binding=1, bytes=54,
                     code_sha256='0bcb7577e755f1ca9736b0fd0b05e4d3f0a0e1e0cd3a59976b947191d3df74a4')], 'Exact original delay leaf')
            if unit['name'] == 'nv-read-registers':
                need(pair[1]['functions'] == [dict(name='tsl9_nv_read_registers_1979a', binding=1, bytes=30,
                     code_sha256='55eaeff68d528f2e86c97ce41148fa5ef921bd325a35e86d439df5a1cc6dedda')] and
                     not pair[1]['UND'] and not pair[1]['relocations'], 'Measured read register projection; dynamic slot provider and full equivalence remain unknown')
            if unit['name'] == 'nv-read-live-count':
                need(pair[1]['functions'] == [dict(name='tsl9_nv_read_live_count_1979a', binding=1, bytes=30,
                     code_sha256='05b184cb6e192355342a6b6e71a7db136f2d53aa7aa33a341fb1551f4b49f58a')] and
                     not pair[1]['UND'] and not pair[1]['relocations'], 'Measured direct-A2 read call projection only; ordering and dynamic provider remain unknown')
            if unit['name'] == 'boot-clock-prefix':
                need(pair[1]['functions'] == [
                    dict(name='tsl9_clock_prefix_body',binding=1,bytes=220,code_sha256='ec199e4c071f4b65e096b3514dfdf566962581a93f2fc9f52c04d064613b8885'),
                    dict(name='tsl9_clock_prefix_entry',binding=1,bytes=12,code_sha256='235e2cf36d914ddf21c5f547ef9fdac03cbc88074b99075a04d453d053f59b49')]
                    and not pair[1]['UND'] and not pair[1]['relocations']
                    and pair[1]['allocated_bytes']==232
                    and all(x['flags']==6 and x['type']==1 for x in pair[1]['allocated_sections']),
                    'Measured 232B clock entry/body without internal jumps; linked fall-through adjacency needs the separate fit verifier, full IRQ/fault/physical behavior unproved')
            if unit['name'] == 'nv-write-frame-contract':
                need(pair[1]['functions'] == [dict(name='tsl9_nv_write_frame_contract_197be', binding=1, bytes=50,
                     code_sha256='f7d326d05b196a3e08ce65713327008b3709b20903f1dba328546cf3e1ea4e9c')], 'Measured callback frame/source contract, not whole-original code equality')
                callees = ['tsl9_flash_unlock_18e98', 'tsl9_flash_erase_18ec4', 'tsl9_flash_program_18ef2', 'tsl9_flash_lock_18eb6', 'tsl9_delay_registers_19764']
                need(pair[1]['UND'] == sorted(callees) and [x['symbol'] for x in pair[1]['relocations']] == callees and
                     [x['offset'] for x in pair[1]['relocations']] == [10, 16, 26, 30, 36] and
                     all(x['type'] == 17 for x in pair[1]['relocations']), 'Five actual JAL relocations to real provider roles')
            results.append(dict(unit=unit['name'], mode=mode, complete_object_projection_equal=True, facts=pair[1]))
    need(record['commands'] == expected_jobs, 'Complete exact successful compiler recipe list')
    return results


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tool-dir', type=Path, help='Local LLVM bin directory; no tools are downloaded.')
    p.add_argument('--build-root', type=Path, help='New directory below build/curated-source; defaults to a UUID.')
    p.add_argument('--replay', type=Path, help='Read-only verification.json from an existing build.')
    a = p.parse_args()
    manifest = metadata()
    if a.replay:
        need(not a.tool_dir and not a.build_root, 'Replay does not compile')
        receipt = a.replay.resolve(); base = receipt.parent
        record = json.loads(receipt.read_bytes())
        need(record['artifacts'] == inventory(base), 'Complete actual build inventory')
        results = audit(base, record, manifest)
        need(results == record['results'], 'Read-only replay equality')
        print(json.dumps(dict(passed=True, mode='read-only-replay', comparisons=len(results), target_execution=False)))
        return
    if not a.tool_dir:
        need(not a.build_root, '--build-root requires --tool-dir')
        print(json.dumps(dict(passed=True, mode='source-metadata', source_files=len(manifest['files']), native_units=len(manifest['native_units']), compiler_invoked=False, target_execution=False)))
        return
    tools = {'clang': (a.tool_dir / ('clang.exe' if os.name == 'nt' else 'clang')).resolve()}
    need(all(p.is_file() for p in tools.values()), 'Missing local clang; supply --tool-dir')
    base = (a.build_root or ROOT / 'build/curated-source' / uuid.uuid4().hex).resolve()
    need(base.is_relative_to(ROOT / 'build/curated-source') and base != ROOT / 'build/curated-source' and not base.exists(), 'New owned build directory only')
    base.mkdir(parents=True)
    resource_run = subprocess.run([str(tools['clang']), '-print-resource-dir'], capture_output=True, timeout=30)
    (base / 'resource.log').write_bytes(resource_run.stdout)
    need(resource_run.returncode == 0, 'Compiler resource query failed')
    resource = Path(resource_run.stdout.decode().strip()).resolve()
    record = dict(schema='TSL9-curated-source-object-comparison-v1', inputs=inputs(manifest),
                  tools={n: dict(path=str(v), sha256=sha(v)) for n, v in tools.items()}, resource_dir=str(resource),
                  resource_log_sha256=sha(base / 'resource.log'), commands=[], dependencies={})
    for unit in manifest['native_units']:
        for mode in ('c', 'cpp'):
            for variant in ('origin', 'curated'):
                folder = base / unit['name'] / mode / variant
                folder.mkdir(parents=True)
                argv = [str(x) for x in command(tools, unit, mode, variant, folder)]
                result = subprocess.run(argv, cwd=folder, capture_output=True, timeout=120)
                (folder / 'compile.log').write_bytes(result.stdout + result.stderr)
                need(result.returncode == 0, 'Compilation failed; inspect ' + str(folder / 'compile.log'))
                record['commands'].append(dict(unit=unit['name'], mode=mode, variant=variant, argv=argv, exit=0, log_sha256=sha(folder / 'compile.log')))
                record['dependencies'][folder.relative_to(base).as_posix()] = dependencies(folder, variant, resource)
    record['results'] = audit(base, record, manifest)
    record['artifacts'] = inventory(base)
    (base / 'verification.json').write_bytes((json.dumps(record, indent=2) + '\n').encode())
    print(json.dumps(dict(passed=True, mode='actual-object-comparison', comparisons=len(record['results']), receipt=str(base / 'verification.json'),
                          legacy_reference_tests_rerun=False, linked_firmware=False, target_execution=False, network=False)))


if __name__ == '__main__':
    main()
