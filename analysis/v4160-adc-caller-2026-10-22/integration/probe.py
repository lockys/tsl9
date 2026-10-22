#!/usr/bin/env python3
"""Link a real caller relocation and C function; pack an offline unvalidated image."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import runpy
import struct
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ENTRY = 'tsl9_adc_config_1892e'
ORIGIN, SITE, CODE, PAGE = 0x8000, 0x19896, 0x1b000, 1024
BASE_SHA = '3be918942c03de99c8a5f3fb7d6eba40ab9af63930020efb7f4cac07cc9a10ee'
FW_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
PARSER_SHA = '00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
TOOLS = {'clang': '047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
         'ld.lld': 'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f',
         'llvm-objdump': 'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa'}


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def case(root, name):
    return next(p for p in (root / 'analysis' / name, root / 'apk-analysis' / ('tsl9-' + name)) if p.is_dir())


def module(path):
    spec = importlib.util.spec_from_file_location('adc_integration_' + path.parent.name + '_' + path.stem, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def context(root):
    parser = case(root, 'v4160-irq-native-2026-10-21') / 'compiler-review/elf32.py'
    need(sha(parser) == PARSER_SHA, 'Exact bounded ELF reader')
    E = runpy.run_path(str(parser))['ELF']
    source = module(case(root, 'v4160-adc-config-2026-10-22') / 'source-review/check.py')
    decode = source.context(root)[3]
    review = module(case(root, 'v4160-adc-caller-2026-10-22') / 'abi-review/review.py')
    return E, decode, review, parser


def inputs(root, record):
    _, _, review, parser = context(root)
    result = review.replay(root, Path(record['abi_receipt']))
    need(result['normal_caller_projection']['conditionally_supported']
         and not result['physical_ABI_proved'] and not result['full_original_callee_ABI_proved'],
         'Independent conditional caller projection, not physical ABI')
    paths = [HERE / 'probe.py', HERE / 'call_site.s', HERE / 'caller.ld', parser,
             Path(record['baseline']), Path(record['firmware']), Path(record['abi_receipt']),
             Path(record['native_folder']) / 'native.o', Path(record['native_folder']) / 'verification.json',
             case(root, 'v4160-adc-caller-2026-10-22') / 'implementation/seal.json',
             case(root, 'v4160-adc-caller-2026-10-22') / 'abi-review/seal.json',
             Path(sys.executable).resolve(), *map(Path, record['tools'].values())]
    return {str(p): sha(p) for p in paths}


def recipes(folder, record):
    tools = record['tools']; native = Path(record['native_folder']) / 'native.o'
    return [('assemble-caller', [tools['clang'], '--target=riscv32-unknown-elf',
             '-march=rv32imac_zicsr_zifencei', '-mabi=ilp32', '-mno-relax', '-x', 'assembler',
             '-c', HERE / 'call_site.s', '-o', folder / 'call_site.o']),
            ('link-real-C', [tools['ld.lld'], '--gc-sections', '--no-relax', '-T', HERE / 'caller.ld',
             folder / 'call_site.o', native, '-Map=' + str(folder / 'linked.map'), '-o', folder / 'linked.elf']),
            ('complete-static-disassembly', [tools['llvm-objdump'], '--mattr=+m,+a,+c,+zicsr,+zifencei',
             '-d', '-r', folder / 'linked.elf'])]


def loads(e):
    start = struct.unpack_from('<I', e.raw, 28)[0]
    size, count = struct.unpack_from('<HH', e.raw, 42)
    need(size == 32 and start + size * count <= len(e.raw), 'Bounded actual ELF program headers')
    return [dict(zip(('type', 'offset', 'vaddr', 'paddr', 'filesz', 'memsz', 'flags', 'align'),
                     struct.unpack_from('<8I', e.raw, start + i * size))) for i in range(count)]


def image_gate(image, baseline, patch, code):
    at = SITE - ORIGIN
    need(len(image) == len(baseline) + PAGE == 78848, 'Exactly one appended runtime page')
    need(image[:at] == baseline[:at] and image[at:at + 4] == patch
         and image[at + 4:len(baseline)] == baseline[at + 4:], 'Only original caller may change in preimage')
    need(image[len(baseline):len(baseline) + len(code)] == code, 'Actual linked C bytes')
    need(image[len(baseline) + len(code):] == bytes([255]) * (PAGE - len(code)), 'Explicit non-code FF page tail')


def inspect(root, folder, record):
    need(record['source_pins'] == inputs(root, record), 'Current sources, objects, tools and independent proof')
    for name, pin in TOOLS.items():
        need(sha(record['tools'][name]) == pin, 'Exact existing LLVM tool')
    expected = recipes(folder, record)
    need([(c['label'], c['argv']) for c in record['commands']] == [(n, list(map(str, a))) for n, a in expected],
         'Exact assembler/linker recipes')
    for c in record['commands']:
        need(c['exit'] == 0 and sha(folder / c['log']) == c['sha256'], 'Actual successful tool log')
    E, decode, _, _ = context(root)
    baseline = Path(record['baseline']).read_bytes(); firmware = Path(record['firmware']).read_bytes()
    need(sha(record['baseline']) == BASE_SHA and len(baseline) == 77824 and ORIGIN + len(baseline) == CODE,
         'Original source-wired preimage and exact append boundary')
    need(sha(record['firmware']) == FW_SHA and len(firmware) == 76800, 'Actual original ID2966')
    at = SITE - ORIGIN
    old = decode(firmware[at:at + 4], SITE)
    need(old['op'] == 'jal' and old['rd'] == 1 and old['target'] == 0x1892e
         and baseline[at:at + 4] == firmware[at:at + 4], 'Actual original caller, unmodified in baseline')
    patch_object = E(folder / 'call_site.o')
    need(patch_object.kind == 1 and len(patch_object.relocations) == 1, 'One real caller relocation')
    relocation = patch_object.relocations[0]
    need(relocation['owner'] == '.text.tsl9_adc_call_site' and relocation['offset'] == 0
         and relocation['type'] == 17 and relocation['addend'] == 0
         and relocation['symbol']['name'] == ENTRY and relocation['symbol']['index'] == 0,
         'R_RISCV_JAL to a real undefined C symbol, no numerical provider or relaxation')
    e = E(folder / 'linked.elf'); native = E(Path(record['native_folder']) / 'native.o')
    need(e.kind == 2 and e.flags == 1 and not e.relocations, 'Actual fully linked RV32/RVC object')
    need(not any(s['index'] == 0 and s['name'] for s in e.symbols), 'No unresolved provider')
    need(not any(s['index'] == 0xfff1 and s['info'] >> 4 for s in e.symbols), 'No global ABS provider')
    allocated = [s for s in e.sections if s['flags'] & 2 and s['size']]
    need({s['name'] for s in allocated} == {'.caller', '.adc'} and all(s['type'] == 1 and s['flags'] == 6 for s in allocated),
         'Only two actual executable allocations, no NOBITS or hidden data')
    funcs = [s for s in e.symbols if s['info'] & 15 == 2 and s['size']]
    need(len(funcs) == 1 and funcs[0]['name'] == ENTRY and funcs[0]['value'] == CODE and funcs[0]['size'] == 110,
         'Only genuine selected C function retained; four other globals actually GC removed')
    original_func = next(s for s in native.symbols if s['name'] == ENTRY and s['info'] & 15 == 2)
    code = e.function_bytes(funcs[0]); need(code == native.function_bytes(original_func), 'Relocation preserves real C machine bytes')
    caller = e.byname['.caller']; adc = e.byname['.adc']; patch = e.data(caller)
    need(caller['address'] == SITE and caller['size'] == 4 and adc['address'] == CODE and adc['size'] == 110,
         'Actual source patch and C placement extents')
    row = decode(patch, SITE)
    need(row['op'] == 'jal' and row['rd'] == 1 and row['target'] == CODE, 'Actual caller enters linked C; RA remains1989A')
    segments = [p for p in loads(e) if p['type'] == 1]
    need(len(segments) == 2, 'Exactly two actual LOADs')
    for segment, section in zip(segments, (caller, adc)):
        need(segment['vaddr'] == segment['paddr'] == section['address']
             and segment['filesz'] == segment['memsz'] == section['size'] and segment['flags'] == 5
             and segment['offset'] == section['offset'], 'LOAD exactly owns section bytes, no holes or headers')
    image = (folder / 'NOT-FLASH-VALIDATED-adc-caller-bank.bin').read_bytes()
    image_gate(image, baseline, patch, code)
    controls = []
    for offset, label in [(0, 'inherited_byte'), (at + 0, 'caller_opcode'), (len(baseline), 'C_payload'), (len(image) - 1, 'page_tail')]:
        changed = bytearray(image); changed[offset] ^= 1
        try:
            image_gate(bytes(changed), baseline, patch, code)
        except ValueError:
            controls.append(dict(case=label, offset=offset, rejected=True))
        else:
            raise ValueError('Accepted mutated candidate image')
    return dict(passed=True,mode=record['mode'],bytes=len(image),sha256=sha(folder / 'NOT-FLASH-VALIDATED-adc-caller-bank.bin'),
                baseline_sha256=BASE_SHA,preimage_bytes=77824,caller_PC=SITE,caller_return=SITE + 4,target=CODE,
                changed_preimage_offsets=[i for i,(a,b) in enumerate(zip(baseline,image)) if a != b],
                real_C_function_bytes=110,code_sha256=hashlib.sha256(code).hexdigest(),
                appended_page_bytes=1024,non_code_FF_page_tail_bytes=914,raw_BIN_execute_permissions_encoded=False,
                LOADs=segments,UND=0,RELA=0,global_ABS_providers=0,unused_real_functions_GC_removed=4,
                raw_image_controls=controls,normal_caller_projection_conditional=True,
                full_original_callee_ABI_proved=False,fault_async_IRQ_equivalence=False,
                Flash_NV_ownership_proved=False,installed_ROM_proved=False,hardware_OTA_proved=False,
                target_execution=False,ISA_emulation=False,rebuilt_flashable_BIN=False)


def replay(root, path):
    r = read(path); folder = path.parent
    need(r['artifacts'] == {p.relative_to(folder).as_posix(): dict(bytes=p.stat().st_size,sha256=sha(p))
                           for p in folder.rglob('*') if p.is_file() and p != path}, 'Complete immutable integration archive')
    result = inspect(root, folder, r); need(result == r['result'], 'Actual integration readback equals receipt')
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', required=True, type=Path); p.add_argument('--replay', type=Path)
    for name in ('tool-dir','native-folder','abi-receipt','baseline','firmware','build-root'):
        p.add_argument('--' + name, type=Path)
    a = p.parse_args(); root = a.project_root.resolve()
    if a.replay:
        need(all(getattr(a,n.replace('-','_')) is None for n in ('tool-dir','native-folder','abi-receipt','baseline','firmware','build-root')), 'Read-only replay')
        print(json.dumps(replay(root,a.replay.resolve()))); return
    need(all(getattr(a,n.replace('-','_')) is not None for n in ('tool-dir','native-folder','abi-receipt','baseline','firmware','build-root')), 'Explicit inputs required')
    folder = a.build_root.resolve(); owner = case(root,'v4160-adc-caller-2026-10-22') / 'build'
    need(folder.is_relative_to(owner) and folder != owner and not folder.exists(), 'Create-only integration build')
    tools = {n: next(x.resolve() for x in (a.tool_dir / (n + '.exe'),a.tool_dir / n) if x.is_file()) for n in TOOLS}
    record = dict(mode=read(a.native_folder / 'verification.json')['mode'],native_folder=str(a.native_folder.resolve()),
                  abi_receipt=str(a.abi_receipt.resolve()),baseline=str(a.baseline.resolve()),firmware=str(a.firmware.resolve()),
                  tools={n:str(v) for n,v in tools.items()})
    for n,path in tools.items(): need(sha(path) == TOOLS[n], 'Pinned LLVM before invocation')
    record['source_pins'] = inputs(root,record); folder.mkdir(parents=True); tmp=folder/'compiler-temp';tmp.mkdir()
    env=dict(os.environ,TMP=str(tmp),TEMP=str(tmp)); commands=[]
    for label,argv in recipes(folder,record):
        r=subprocess.run(list(map(str,argv)),cwd=folder,env=env,capture_output=True,timeout=120)
        log=folder/(label+'.log');log.write_bytes(r.stdout+r.stderr)
        commands.append(dict(label=label,argv=list(map(str,argv)),exit=r.returncode,log=log.name,sha256=sha(log)))
        need(r.returncode == 0,'Actual tool failed: '+str(log))
    E,_,_,_=context(root); e=E(folder/'linked.elf'); baseline=a.baseline.read_bytes();at=SITE-ORIGIN
    image=bytearray(baseline);image[at:at+4]=e.data(e.byname['.caller']);code=e.data(e.byname['.adc'])
    need(len(code)==110 and ORIGIN+len(baseline)==CODE,'Actual append extent before packing')
    image.extend(code);image.extend(bytes([255])*(PAGE-len(code)))
    (folder/'NOT-FLASH-VALIDATED-adc-caller-bank.bin').write_bytes(image)
    record['commands']=commands;record['result']=inspect(root,folder,record)
    record['artifacts']={x.relative_to(folder).as_posix():dict(bytes=x.stat().st_size,sha256=sha(x)) for x in folder.rglob('*') if x.is_file()}
    path=folder/'verification.json';path.write_bytes((json.dumps(record,indent=2)+'\n').encode())
    print(json.dumps(replay(root,path)))


if __name__ == '__main__':
    main()
