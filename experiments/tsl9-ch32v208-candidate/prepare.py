"""Prepare a conditional CH32V208 Runtime link from guarded C/C++ objects.

No target execution or networking. Generated carrier bytes come only from the
retained original Runtime; no source-external bytes or ROM body are fabricated.
"""
from pathlib import Path
import argparse, hashlib, json, runpy

RUNTIME_SHA = '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'
PRODUCT_SHA = '76466902d3d7092657f3edc2a9207f20890770d9cc2c788cd04b74a21efe39e7'
VERIFY_SHA = 'b45c1d454a0ccd76efae1a863275e94ed4a71fcee773bc211dab90d543d21a79'

def require(ok, reason):
    if not ok:
        raise AssertionError(reason)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def write_new(path, text):
    require(not path.exists(), 'Preserve generated output: '+str(path))
    path.write_text(text, encoding='utf-8', newline='\n')

def prepare(project, runtime, output, mode):
    project, runtime, output = map(lambda p: Path(p).resolve(), (project, runtime, output))
    require(output.is_dir() and not any(output.iterdir()), 'Fresh empty build directory')
    require(sha(project/'export-manifest.json') == PRODUCT_SHA and
            sha(project/'verification-r81.json') == VERIFY_SHA, 'Original product profile identity')
    verification = read(project/'verification-r81.json')
    rows = [r for r in verification['actual_destination_languages'] if r['mode'] == mode]
    require(len(rows) == 1, 'One retained compiler-language receipt')
    row = rows[0]
    producer_path = Path(row['producer'])
    require(sha(producer_path) == row['producer_sha256'] and sha(row['audit']) == row['audit_sha256'],
            'Retained native producer and audit identities')
    producer = read(producer_path)
    require(producer['strict_exit'] != 0 and sha(producer['strict_log']) == producer['strict_log_sha256'],
            'Original strict failure is retained')
    for path, digest in producer['sources'].items():
        require(sha(path) == digest, 'Guarded active native source changed')
    require(sha(producer['baseline_receipt']) == producer['baseline_receipt_sha256'], 'Baseline receipt identity')
    baseline = read(producer['baseline_receipt'])
    for path, digest in baseline['source_sha256'].items():
        require(sha(path) == digest, 'Guarded legacy C/C++ source changed')
    for tool in ('compiler', 'linker'):
        require(sha(baseline[tool]) == baseline[tool+'_sha256'], 'Toolchain identity')
    core = project/'experiments/tsl9-lookup-domain-closure'
    cfg = read(core/'layout/closure.json')
    source = runtime.read_bytes()
    require(len(source) == 76800 and sha(runtime) == RUNTIME_SHA, 'Original Runtime carrier identity')
    memory = producer['objects']['memory']
    require(sha(memory['path']) == memory['sha256'] == row['memory_sha256'], 'Core object identity')
    elf = runpy.run_path(str(core/'audit-native.py'))['ELF'](memory['path'])
    undefined = sorted({s['name'] for s in elf.symbols if s['index'] == 0 and s['binding'] in (1, 2) and s['name']})
    require(undefined == ['__tsl9_opaque_address_19d10', '__tsl9_rom_entry'], 'Only the two explicitly modeled external addresses')
    groups = sorted(cfg['output_groups'], key=lambda g: g['original_va'])
    spans, gaps, previous = [], [], 0x8000
    for g in groups:
        section = elf.names[g['output_section']]
        lo, size = g['original_va'], g['bytes']
        require(section['size'] == size and section['type'] == 1 and section['addr'] == 0,
                'Expected relocatable mapped section')
        require(previous <= lo and lo+size <= 0x1ac00, 'Nonoverlapping original Flash coverage')
        if lo != previous:
            gaps.append(dict(va=previous, bytes=lo-previous, section=f'.tsl9_carrier_{previous:08x}'))
        spans.append(dict(va=lo, bytes=size, section=g['output_section'], kind=g['kind']))
        previous = lo+size
    if previous != 0x1ac00:
        gaps.append(dict(va=previous, bytes=0x1ac00-previous, section=f'.tsl9_carrier_{previous:08x}'))
    require(len(spans) == 667 and sum(s['bytes'] for s in spans) == 76447 and
            len(gaps) == 25 and sum(g['bytes'] for g in gaps) == 353, 'Complete unchanged coverage cohort')
    ram = cfg['memory']['ram']
    require(ram['origin'] == 0x20004000 and ram['bytes'] == 35152, 'Original numeric RAM extent')
    mapped_names = {s['section'] for s in spans}
    extra = [s for s in elf.allocated() if s['name'] not in mapped_names]
    require(len(extra) == 1 and extra[0]['name'] == ram['output_section'] and
            extra[0]['type'] == 8 and extra[0]['size'] == ram['bytes'], 'RAM remains one NOBITS section')
    lines = ['/* Known original carrier gaps, not recovered semantic C/C++ functions. */',
             '/* No bytes beyond [0x8000,0x1AC00) and no ROM code are supplied. */']
    for g in gaps:
        raw = source[g['va']-0x8000:g['va']-0x8000+g['bytes']]
        g.update(source_offset=g['va']-0x8000, sha256=hashlib.sha256(raw).hexdigest(),
                 provenance='retained-original-carrier; semantics unreconstructed')
        lines.append(f'static const unsigned char carrier_{g["va"]:08x}[{len(raw)}]')
        lines.append(f'__attribute__((used, aligned(1), section("{g["section"]}"))) = {{')
        for off in range(0, len(raw), 16):
            lines.append('  '+', '.join(f'0x{x:02x}' for x in raw[off:off+16])+',')
        lines.append('};')
    write_new(output/'carrier.c', '\n'.join(lines)+'\n')
    script = ['/* Conditional candidate addresses, NOT verified hardware/ROM providers. */',
              'OUTPUT_ARCH(riscv)', 'ENTRY(tsl9_image_entry)',
              'PHDRS { runtime PT_LOAD FLAGS(5); ram PT_LOAD FLAGS(6); }',
              '__tsl9_rom_entry = 0x40000;', '__tsl9_opaque_address_19d10 = 0x19d10;', 'SECTIONS {']
    for s in sorted(spans+gaps, key=lambda s: s['va']):
        n, va, size = s['section'], s['va'], s['bytes']
        script.append(f' {n} 0x{va:x} : {{ KEEP(*({n})) }} :runtime')
        script.append(f' ASSERT(ADDR({n}) == 0x{va:x} && SIZEOF({n}) == {size}, "Flash section shape {n}")')
    script.extend([
        ' .tsl9_runtime_ram 0x20004000 (NOLOAD) : { KEEP(*(.tsl9_runtime_ram)) } :ram',
        ' ASSERT(SIZEOF(.tsl9_runtime_ram) == 35152, "Original numeric RAM extent")',
        ' .text 0 : { *(.text) } :NONE', ' ASSERT(SIZEOF(.text) == 0, "Unexpected generic text")',
        ' .data 0 : { *(.data) } :NONE', ' ASSERT(SIZEOF(.data) == 0, "Unexpected generic data")',
        ' .bss 0 (NOLOAD) : { *(.bss) } :NONE', ' ASSERT(SIZEOF(.bss) == 0, "Unexpected generic bss")',
        ' .riscv.attributes 0 : { *(.riscv.attributes) } :NONE', ' .comment 0 : { *(.comment) } :NONE',
        ' .symtab 0 : { *(.symtab) } :NONE', ' .shstrtab 0 : { *(.shstrtab) } :NONE',
        ' .strtab 0 : { *(.strtab) } :NONE',
        ' /DISCARD/ : { *(.note.GNU-stack) *(.llvm_addrsig) }', '}'])
    write_new(output/'candidate.ld', '\n'.join(script)+'\n')
    objcopy = Path(baseline['linker']).parent/'llvm-objcopy.exe'
    plan = dict(schema='CH32V208-conditional-Runtime-plan-v1', mode=mode, project=str(project),
        runtime=dict(path=str(runtime), bytes=len(source), sha256=RUNTIME_SHA, base=0x8000, end_exclusive=0x1ac00),
        compiler=baseline['compiler'], flags=baseline['flags'], linker=baseline['linker'], objcopy=str(objcopy),
        tool_sha256=dict(compiler=sha(baseline['compiler']), linker=sha(baseline['linker']), objcopy=sha(objcopy)),
        retained_producer=dict(path=str(producer_path), sha256=row['producer_sha256'],
            audit=row['audit'], audit_sha256=row['audit_sha256'], strict_exit=producer['strict_exit'],
            strict_log=producer['strict_log'], strict_log_sha256=producer['strict_log_sha256']),
        core_object=memory, core_source_count=len(baseline['source_sha256'])+len(producer['sources']),
        mapped_sections=spans, carrier_gaps=gaps, ram=dict(section='.tsl9_runtime_ram', va=0x20004000, bytes=35152),
        external_address_assumptions=[dict(name='__tsl9_rom_entry', value=0x40000, kind='address-only; resident code and ABI unverified'),
            dict(name='__tsl9_opaque_address_19d10', value=0x19d10, kind='address-only; full U8 domain still lacks 272 source bytes')],
        no_source_external_padding=True, ROM_body_supplied=False, target_ready=False, ota_verified=False,
        goal_complete=False, network=False, target_executed=False, hardware=False, emulation=False)
    plan['generated_sha256'] = {n:sha(output/n) for n in ('carrier.c','candidate.ld')}
    write_new(output/'plan.json', json.dumps(plan, indent=2)+'\n')
    return dict(passed=True, mode=mode, plan=str(output/'plan.json'), reconstructed_section_bytes=76447,
                retained_carrier_bytes=353, source_external_bytes=0, target_ready=False)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--project-root', required=True); p.add_argument('--runtime', required=True)
    p.add_argument('--output', required=True); p.add_argument('--mode', choices=['c','cpp'], required=True)
    a = p.parse_args()
    print(json.dumps(prepare(a.project_root, a.runtime, a.output, a.mode)))
