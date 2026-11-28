#!/usr/bin/env python3
"""Rebuild the integrated V4.1.60 candidate with opaque original spans."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
EXPECTED = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
parser = argparse.ArgumentParser()
parser.add_argument('--tool-dir', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
out = args.out.resolve()
if out.exists() or out == ROOT or ROOT in out.parents:
    raise SystemExit('Output must be a new directory outside the project')
clang = args.tool_dir / ('clang.exe' if (args.tool_dir / 'clang.exe').is_file() else 'clang')
if not clang.is_file():
    raise SystemExit('LLVM clang missing')
payload = json.loads((ROOT / 'src/native/tx_candidate/full-image-payload.json').read_text(encoding='utf-8'))
if payload['schema'] != 'tsl9-v4160-opaque-payload-v1':
    raise ValueError('Unexpected payload schema')
ranges = payload['ranges']
if [(x['start'], x['end']) for x in ranges] != [(0x14056, 0x14c8a), (0x1a69c, 0x1a6a0)]:
    raise ValueError('Unexpected payload ranges')
raw = [bytes.fromhex(x['hex']) for x in ranges]
if any(len(data) != item['end'] - item['start'] or hashlib.sha256(data).hexdigest() != item['sha256']
       for item, data in zip(ranges, raw)):
    raise ValueError('Payload length or digest mismatch')
out.mkdir(parents=True)
spans_dir = out / 'selected'
p = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/build-source-spans.py'),
                    '--tool-dir', str(args.tool_dir), '--out', str(spans_dir)],
                   capture_output=True, text=True)
if p.returncode:
    raise ValueError('Selected source build failed: ' + p.stderr[:1000])
facts = json.loads(p.stdout)
if not facts['passed'] or facts['complete_firmware'] or facts['flashable']:
    raise ValueError('Unexpected selected source result')
conditional_dir = out / 'conditional-link'
p = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/verify-conditional-full-payload-link.py'),
                    '--tool-dir', str(args.tool_dir), '--out', str(conditional_dir)],
                   capture_output=True, text=True)
if p.returncode:
    raise ValueError('Conditional full link failed: ' + p.stderr[:1000])
conditional = json.loads(p.stdout)
if (not conditional['passed'] or conditional['global_index_bounds_proved'] or conditional['ram_ownership_proved']
    or conditional['installed_rom_proved'] or conditional['hardware_validated'] or conditional['flashable']
    or len(conditional['results']) != 2
    or any(x['strict_undefined'] != ['tsl9_boot_resident_40000'] or x['section_backed_new_symbols'] != 1
           or x['conditional_data_aliases'] != 3 or x['negative_section_controls'] != 2
           for x in conditional['results'])):
    raise ValueError('Unexpected conditional link evidence')
manifest = json.loads((spans_dir / 'NOT-FLASHABLE-spans.json').read_text(encoding='utf-8'))
reader = runpy.run_path(str(ROOT / 'src/native/tx_candidate/postpass/elf32.py'))['ELF']
fragment_tools = runpy.run_path(str(ROOT / 'scripts/source-ota-epilogue.py'))
compile_epilogue, compile_entry, compile_more, compile_ae, compile_ad, compile_dispatch, compile_dispatch2, compile_dispatch3, compile_dispatch4, compile_dispatch5, compile_dispatch6, compile_dispatch7, compile_dispatch8, compile_dispatch9, compile_dispatch10, compile_dispatch11, compile_dispatch12, compile_dispatch13, compile_dispatch14, compile_dispatch15, compile_dispatch16, compile_dispatch17, compile_dispatch18, compile_dispatch19, compile_dispatch20, compile_dispatch21, compile_dispatch22, compile_dispatch23, compile_dispatch24, compile_dispatch25, compile_dispatch26 = (fragment_tools['compile_fragment'], fragment_tools['compile_entry'], fragment_tools['compile_more'], fragment_tools['compile_ae'], fragment_tools['compile_ad'], fragment_tools['compile_dispatch'], fragment_tools['compile_dispatch2'], fragment_tools['compile_dispatch3'], fragment_tools['compile_dispatch4'], fragment_tools['compile_dispatch5'], fragment_tools['compile_dispatch6'], fragment_tools['compile_dispatch7'], fragment_tools['compile_dispatch8'], fragment_tools['compile_dispatch9'], fragment_tools['compile_dispatch10'], fragment_tools['compile_dispatch11'], fragment_tools['compile_dispatch12'], fragment_tools['compile_dispatch13'], fragment_tools['compile_dispatch14'], fragment_tools['compile_dispatch15'], fragment_tools['compile_dispatch16'], fragment_tools['compile_dispatch17'], fragment_tools['compile_dispatch18'], fragment_tools['compile_dispatch19'], fragment_tools['compile_dispatch20'], fragment_tools['compile_dispatch21'], fragment_tools['compile_dispatch22'], fragment_tools['compile_dispatch23'], fragment_tools['compile_dispatch24'], fragment_tools['compile_dispatch25'], fragment_tools['compile_dispatch26'])
compile_dispatch27 = fragment_tools['compile_dispatch27']
compile_dispatch28 = fragment_tools['compile_dispatch28']
compile_dispatch29 = fragment_tools['compile_dispatch29']
compile_dispatch30 = fragment_tools['compile_dispatch30']
compile_dispatch31 = fragment_tools['compile_dispatch31']
compile_dispatch32 = fragment_tools['compile_dispatch32']
compile_dispatch33 = fragment_tools['compile_dispatch33']
compile_dispatch34 = fragment_tools['compile_dispatch34']
compile_dispatch35 = fragment_tools['compile_dispatch35']
compile_dispatch36 = fragment_tools['compile_dispatch36']
compile_dispatch37 = fragment_tools['compile_dispatch37']
compile_dispatch38 = fragment_tools['compile_dispatch38']
compile_dispatch39 = fragment_tools['compile_dispatch39']
compile_dispatch40 = fragment_tools['compile_dispatch40']
compile_dispatch41 = fragment_tools['compile_dispatch41']
compile_dispatch42 = fragment_tools['compile_dispatch42']
compile_dispatch43 = fragment_tools['compile_dispatch43']
compile_dispatch44 = fragment_tools['compile_dispatch44']
compile_dispatch45 = fragment_tools['compile_dispatch45']
compile_dispatch46 = fragment_tools['compile_dispatch46']
compile_dispatch47 = fragment_tools['compile_dispatch47']
compile_dispatch48 = fragment_tools['compile_dispatch48']
compile_dispatch49 = fragment_tools['compile_dispatch49']
compile_dispatch50 = fragment_tools['compile_dispatch50']
compile_dispatch51 = fragment_tools['compile_dispatch51']
compile_dispatch52 = fragment_tools['compile_dispatch52']
compile_dispatch53 = fragment_tools['compile_dispatch53']
compile_dispatch54 = fragment_tools['compile_dispatch54']
compile_dispatch55 = fragment_tools['compile_dispatch55']
compile_dispatch56 = fragment_tools['compile_dispatch56']
compile_dispatch57 = fragment_tools['compile_dispatch57']
compile_dispatch58 = fragment_tools['compile_dispatch58']
compile_dispatch59 = fragment_tools['compile_dispatch59']
compile_dispatch60 = fragment_tools['compile_dispatch60']
compile_dispatch61 = fragment_tools['compile_dispatch61']
compile_dispatch62 = fragment_tools['compile_dispatch62']
compile_dispatch63 = fragment_tools['compile_dispatch63']
compile_dispatch64 = fragment_tools['compile_dispatch64']
compile_dispatch65 = fragment_tools['compile_dispatch65']
compile_dispatch66 = fragment_tools['compile_dispatch66']
compile_dispatch67 = fragment_tools['compile_dispatch67']
compile_dispatch68 = fragment_tools['compile_dispatch68']
compile_dispatch69 = fragment_tools['compile_dispatch69']
compile_dispatch70 = fragment_tools['compile_dispatch70']
compile_dispatch71 = fragment_tools['compile_dispatch71']
compile_dispatch72 = fragment_tools['compile_dispatch72']
compile_dispatch73 = fragment_tools['compile_dispatch73']
compile_dispatch74 = fragment_tools['compile_dispatch74']
compile_dispatch75 = fragment_tools['compile_dispatch75']
compile_dispatch76 = fragment_tools['compile_dispatch76']
compile_dispatch77 = fragment_tools['compile_dispatch77']
compile_dispatch78 = fragment_tools['compile_dispatch78']
compile_dispatch79 = fragment_tools['compile_dispatch79']
compile_dispatch80 = fragment_tools['compile_dispatch80']
results = []
for mode in ('c', 'cpp'):
    epilogue = compile_epilogue(args.tool_dir, out, mode, reader)
    entry = compile_entry(args.tool_dir, out, mode, reader)
    more = compile_more(args.tool_dir, out, mode, reader)
    ae = compile_ae(args.tool_dir, out, mode, reader)
    dispatch79 = compile_dispatch79(args.tool_dir, out, mode, reader)
    if dispatch79 != raw[0][0xcc:0x124]:
        raise ValueError('Compiled dispatcher 14122 differs from original bytes')
    ad = compile_ad(args.tool_dir, out, mode, reader)
    dispatch80 = compile_dispatch80(args.tool_dir, out, mode, reader)
    if dispatch80 != raw[0][0x156:0x180]:
        raise ValueError('Compiled dispatcher 141ac differs from original bytes')
    dispatch = compile_dispatch(args.tool_dir, out, mode, reader)
    dispatch2 = compile_dispatch2(args.tool_dir, out, mode, reader)
    dispatch3 = compile_dispatch3(args.tool_dir, out, mode, reader)
    dispatch4 = compile_dispatch4(args.tool_dir, out, mode, reader)
    dispatch5 = compile_dispatch5(args.tool_dir, out, mode, reader)
    dispatch6 = compile_dispatch6(args.tool_dir, out, mode, reader)
    dispatch7 = compile_dispatch7(args.tool_dir, out, mode, reader)
    dispatch8 = compile_dispatch8(args.tool_dir, out, mode, reader)
    dispatch9 = compile_dispatch9(args.tool_dir, out, mode, reader)
    dispatch10 = compile_dispatch10(args.tool_dir, out, mode, reader)
    dispatch11 = compile_dispatch11(args.tool_dir, out, mode, reader)
    dispatch12 = compile_dispatch12(args.tool_dir, out, mode, reader)
    dispatch13 = compile_dispatch13(args.tool_dir, out, mode, reader)
    dispatch14 = compile_dispatch14(args.tool_dir, out, mode, reader)
    dispatch15 = compile_dispatch15(args.tool_dir, out, mode, reader)
    dispatch16 = compile_dispatch16(args.tool_dir, out, mode, reader)
    dispatch17 = compile_dispatch17(args.tool_dir, out, mode, reader)
    dispatch18 = compile_dispatch18(args.tool_dir, out, mode, reader)
    dispatch19 = compile_dispatch19(args.tool_dir, out, mode, reader)
    dispatch20 = compile_dispatch20(args.tool_dir, out, mode, reader)
    dispatch21 = compile_dispatch21(args.tool_dir, out, mode, reader)
    dispatch22 = compile_dispatch22(args.tool_dir, out, mode, reader)
    dispatch23 = compile_dispatch23(args.tool_dir, out, mode, reader)
    dispatch24 = compile_dispatch24(args.tool_dir, out, mode, reader)
    dispatch25 = compile_dispatch25(args.tool_dir, out, mode, reader)
    dispatch26 = compile_dispatch26(args.tool_dir, out, mode, reader)
    dispatch78 = compile_dispatch78(args.tool_dir, out, mode, reader)
    if dispatch78 != raw[0][0xc22:0xc34]:
        raise ValueError('Compiled dispatcher 14c78 differs from original bytes')
    dispatch77 = compile_dispatch77(args.tool_dir, out, mode, reader)
    if dispatch77 != raw[0][0xbfa:0xc22]:
        raise ValueError('Compiled dispatcher 14c50 differs from original bytes')
    dispatch76 = compile_dispatch76(args.tool_dir, out, mode, reader)
    if dispatch76 != raw[0][0xbdc:0xbfa]:
        raise ValueError('Compiled dispatcher 14c32 differs from original bytes')
    dispatch75 = compile_dispatch75(args.tool_dir, out, mode, reader)
    if dispatch75 != raw[0][0xbd2:0xbdc]:
        raise ValueError('Compiled dispatcher 14c28 differs from original bytes')
    dispatch74 = compile_dispatch74(args.tool_dir, out, mode, reader)
    if dispatch74 != raw[0][0xbba:0xbd2]:
        raise ValueError('Compiled dispatcher 14c10 differs from original bytes')
    dispatch73 = compile_dispatch73(args.tool_dir, out, mode, reader)
    if dispatch73 != raw[0][0xba0:0xbba]:
        raise ValueError('Compiled dispatcher 14bf6 differs from original bytes')
    dispatch72 = compile_dispatch72(args.tool_dir, out, mode, reader)
    if dispatch72 != raw[0][0xb8e:0xba0]:
        raise ValueError('Compiled dispatcher 14be4 differs from original bytes')
    dispatch71 = compile_dispatch71(args.tool_dir, out, mode, reader)
    if dispatch71 != raw[0][0xb84:0xb8e]:
        raise ValueError('Compiled dispatcher 14bda differs from original bytes')
    dispatch70 = compile_dispatch70(args.tool_dir, out, mode, reader)
    if dispatch70 != raw[0][0xb6a:0xb84]:
        raise ValueError('Compiled dispatcher 14bc0 differs from original bytes')
    dispatch69 = compile_dispatch69(args.tool_dir, out, mode, reader)
    if dispatch69 != raw[0][0xb62:0xb6a]:
        raise ValueError('Compiled dispatcher 14bb8 differs from original bytes')
    dispatch68 = compile_dispatch68(args.tool_dir, out, mode, reader)
    if dispatch68 != raw[0][0xb46:0xb62]:
        raise ValueError('Compiled dispatcher 14b9c differs from original bytes')
    dispatch67 = compile_dispatch67(args.tool_dir, out, mode, reader)
    if dispatch67 != raw[0][0xb36:0xb46]:
        raise ValueError('Compiled dispatcher 14b8c differs from original bytes')
    dispatch66 = compile_dispatch66(args.tool_dir, out, mode, reader)
    if dispatch66 != raw[0][0xb0e:0xb36]:
        raise ValueError('Compiled dispatcher 14b64 differs from original bytes')
    dispatch65 = compile_dispatch65(args.tool_dir, out, mode, reader)
    if dispatch65 != raw[0][0xafa:0xb0e]:
        raise ValueError('Compiled dispatcher 14b50 differs from original bytes')
    dispatch64 = compile_dispatch64(args.tool_dir, out, mode, reader)
    if dispatch64 != raw[0][0xae4:0xafa]:
        raise ValueError('Compiled dispatcher 14b3a differs from original bytes')
    dispatch63 = compile_dispatch63(args.tool_dir, out, mode, reader)
    if dispatch63 != raw[0][0xac6:0xae4]:
        raise ValueError('Compiled dispatcher 14b1c differs from original bytes')
    dispatch62 = compile_dispatch62(args.tool_dir, out, mode, reader)
    if dispatch62 != raw[0][0xab2:0xac6]:
        raise ValueError('Compiled dispatcher 14b08 differs from original bytes')
    dispatch61 = compile_dispatch61(args.tool_dir, out, mode, reader)
    if dispatch61 != raw[0][0xa9e:0xab2]:
        raise ValueError('Compiled dispatcher 14af4 differs from original bytes')
    dispatch60 = compile_dispatch60(args.tool_dir, out, mode, reader)
    if dispatch60 != raw[0][0xa7e:0xa9e]:
        raise ValueError('Compiled dispatcher 14ad4 differs from original bytes')
    dispatch59 = compile_dispatch59(args.tool_dir, out, mode, reader)
    if dispatch59 != raw[0][0xa48:0xa7e]:
        raise ValueError('Compiled dispatcher 14a9e differs from original bytes')
    dispatch58 = compile_dispatch58(args.tool_dir, out, mode, reader)
    if dispatch58 != raw[0][0xa40:0xa48]:
        raise ValueError('Compiled dispatcher 14a96 differs from original bytes')
    dispatch57 = compile_dispatch57(args.tool_dir, out, mode, reader)
    if dispatch57 != raw[0][0xa16:0xa40]:
        raise ValueError('Compiled dispatcher 14a6c differs from original bytes')
    dispatch56 = compile_dispatch56(args.tool_dir, out, mode, reader)
    if dispatch56 != raw[0][0xa00:0xa16]:
        raise ValueError('Compiled dispatcher 14a56 differs from original bytes')
    dispatch55 = compile_dispatch55(args.tool_dir, out, mode, reader)
    if dispatch55 != raw[0][0x9ea:0xa00]:
        raise ValueError('Compiled dispatcher 14a40 differs from original bytes')
    dispatch54 = compile_dispatch54(args.tool_dir, out, mode, reader)
    if dispatch54 != raw[0][0x9ce:0x9ea]:
        raise ValueError('Compiled dispatcher 14a24 differs from original bytes')
    dispatch53 = compile_dispatch53(args.tool_dir, out, mode, reader)
    if dispatch53 != raw[0][0x9c8:0x9ce]:
        raise ValueError('Compiled dispatcher 14a1e differs from original bytes')
    dispatch52 = compile_dispatch52(args.tool_dir, out, mode, reader)
    if dispatch52 != raw[0][0x9a6:0x9c8]:
        raise ValueError('Compiled dispatcher 149fc differs from original bytes')
    dispatch51 = compile_dispatch51(args.tool_dir, out, mode, reader)
    if dispatch51 != raw[0][0x994:0x9a6]:
        raise ValueError('Compiled dispatcher 149ea differs from original bytes')
    dispatch50 = compile_dispatch50(args.tool_dir, out, mode, reader)
    if dispatch50 != raw[0][0x97e:0x994]:
        raise ValueError('Compiled dispatcher 149d4 differs from original bytes')
    dispatch49 = compile_dispatch49(args.tool_dir, out, mode, reader)
    if dispatch49 != raw[0][0x96c:0x97e]:
        raise ValueError('Compiled dispatcher 149c2 differs from original bytes')
    dispatch48 = compile_dispatch48(args.tool_dir, out, mode, reader)
    if dispatch48 != raw[0][0x95a:0x96c]:
        raise ValueError('Compiled dispatcher 149b0 differs from original bytes')
    dispatch47 = compile_dispatch47(args.tool_dir, out, mode, reader)
    if dispatch47 != raw[0][0x944:0x95a]:
        raise ValueError('Compiled dispatcher 1499a differs from original bytes')
    dispatch46 = compile_dispatch46(args.tool_dir, out, mode, reader)
    if dispatch46 != raw[0][0x920:0x944]:
        raise ValueError('Compiled dispatcher 14976 differs from original bytes')
    dispatch45 = compile_dispatch45(args.tool_dir, out, mode, reader)
    if dispatch45 != raw[0][0x91e:0x920]:
        raise ValueError('Compiled dispatcher 14974 differs from original bytes')
    dispatch44 = compile_dispatch44(args.tool_dir, out, mode, reader)
    if dispatch44 != raw[0][0x91a:0x91e]:
        raise ValueError('Compiled dispatcher 14970 differs from original bytes')
    dispatch43 = compile_dispatch43(args.tool_dir, out, mode, reader)
    if dispatch43 != raw[0][0x912:0x91a]:
        raise ValueError('Compiled dispatcher 14968 differs from original bytes')
    dispatch42 = compile_dispatch42(args.tool_dir, out, mode, reader)
    if dispatch42 != raw[0][0x90e:0x912]:
        raise ValueError('Compiled dispatcher 14964 differs from original bytes')
    dispatch41 = compile_dispatch41(args.tool_dir, out, mode, reader)
    if dispatch41 != raw[0][0x8f6:0x90e]:
        raise ValueError('Compiled dispatcher 1494c differs from original bytes')
    dispatch40 = compile_dispatch40(args.tool_dir, out, mode, reader)
    if dispatch40 != raw[0][0x8de:0x8f6]:
        raise ValueError('Compiled dispatcher 14934 differs from original bytes')
    dispatch39 = compile_dispatch39(args.tool_dir, out, mode, reader)
    if dispatch39 != raw[0][0x8d2:0x8de]:
        raise ValueError('Compiled dispatcher continuation differs from original bytes')
    dispatch38 = compile_dispatch38(args.tool_dir, out, mode, reader)
    if dispatch38 != raw[0][0x8c4:0x8d2]:
        raise ValueError('Compiled dispatcher continuation differs from original bytes')
    dispatch37 = compile_dispatch37(args.tool_dir, out, mode, reader)
    if dispatch37 != raw[0][0x8a6:0x8c4]:
        raise ValueError('Compiled dispatcher continuation differs from original bytes')
    dispatch36 = compile_dispatch36(args.tool_dir, out, mode, reader)
    if dispatch36 != raw[0][0x888:0x8a6]:
        raise ValueError('Compiled dispatcher continuation differs from original bytes')
    dispatch35 = compile_dispatch35(args.tool_dir, out, mode, reader)
    if dispatch35 != raw[0][0x85e:0x888]:
        raise ValueError('Compiled dispatcher continuation differs from original bytes')
    dispatch34 = compile_dispatch34(args.tool_dir, out, mode, reader)
    if dispatch34 != raw[0][0x844:0x85e]:
        raise ValueError('Compiled dispatcher continuation differs from original bytes')
    dispatch33 = compile_dispatch33(args.tool_dir, out, mode, reader)
    if dispatch33 != raw[0][0x838:0x844]:
        raise ValueError('Compiled dispatcher branch differs from original bytes')
    dispatch32 = compile_dispatch32(args.tool_dir, out, mode, reader)
    if dispatch32 != raw[0][0x828:0x838]:
        raise ValueError('Compiled dispatcher loop setup differs from original bytes')
    dispatch31 = compile_dispatch31(args.tool_dir, out, mode, reader)
    if dispatch31 != raw[0][0x7f2:0x828]:
        raise ValueError('Compiled dispatcher continuation differs from original bytes')
    dispatch30 = compile_dispatch30(args.tool_dir, out, mode, reader)
    if dispatch30 != raw[0][0x7d8:0x7f2]:
        raise ValueError('Compiled dispatcher cases differ from original bytes')
    dispatch29 = compile_dispatch29(args.tool_dir, out, mode, reader)
    if dispatch29 != raw[0][0x7ba:0x7d8]:
        raise ValueError('Compiled dispatcher continuation differs from original bytes')
    dispatch28 = compile_dispatch28(args.tool_dir, out, mode, reader)
    if dispatch28 != raw[0][0x79e:0x7ba]:
        raise ValueError('Compiled dispatcher continuation differs from original bytes')
    dispatch27 = compile_dispatch27(args.tool_dir, out, mode, reader)
    if dispatch27 != raw[0][0x78e:0x79e]:
        raise ValueError('Compiled dispatcher guard differs from original bytes')
    if dispatch26 != raw[0][0x758:0x78e]:
        raise ValueError('Compiled dispatcher two-cases differs from original bytes')
    if dispatch25 != raw[0][0x71e:0x758]:
        raise ValueError('Compiled dispatcher three-halfword differs from original bytes')
    if dispatch24 != raw[0][0x6e8:0x71e]:
        raise ValueError('Compiled dispatcher table-cases differs from original bytes')
    if dispatch23 != raw[0][0x6c4:0x6e8]:
        raise ValueError('Compiled dispatcher filter-tail differs from original bytes')
    if dispatch22 != raw[0][0x692:0x6c4]:
        raise ValueError('Compiled dispatcher extra-mask differs from original bytes')
    if dispatch21 != raw[0][0x656:0x692]:
        raise ValueError('Compiled dispatcher mask-leaf differs from original bytes')
    if dispatch20 != raw[0][0x624:0x656]:
        raise ValueError('Compiled dispatcher compare-mask differs from original bytes')
    if dispatch19 != raw[0][0x5e0:0x624]:
        raise ValueError('Compiled dispatcher extra halfword differs from original bytes')
    if dispatch18 != raw[0][0x590:0x5e0]:
        raise ValueError('Compiled dispatcher mix differs from original bytes')
    if dispatch17 != raw[0][0x54a:0x590]:
        raise ValueError('Compiled dispatcher word pack differs from original bytes')
    if dispatch16 != raw[0][0x520:0x54a]:
        raise ValueError('Compiled dispatcher halfword pack differs from original bytes')
    if dispatch15 != raw[0][0x4fc:0x520]:
        raise ValueError('Compiled dispatcher case-2 differs from original bytes')
    if dispatch14 != raw[0][0x4d8:0x4fc]:
        raise ValueError('Compiled dispatcher jump-table differs from original bytes')
    if dispatch13 != raw[0][0x4a2:0x4d8]:
        raise ValueError('Compiled dispatcher command-176 differs from original bytes')
    if dispatch12 != raw[0][0x46c:0x4a2]:
        raise ValueError('Compiled dispatcher command-240 differs from original bytes')
    if dispatch11 != raw[0][0x424:0x46c]:
        raise ValueError('Compiled dispatcher command-192 differs from original bytes')
    if dispatch10 != raw[0][0x3f0:0x424]:
        raise ValueError('Compiled dispatcher command-186 differs from original bytes')
    if dispatch9 != raw[0][0x394:0x3f0]:
        raise ValueError('Compiled dispatcher command-175 differs from original bytes')
    if dispatch8 != raw[0][0x34e:0x394]:
        raise ValueError('Compiled dispatcher ordinal differs from original bytes')
    if dispatch7 != raw[0][0x31a:0x34e]:
        raise ValueError('Compiled dispatcher gate differs from original bytes')
    if dispatch6 != raw[0][0x2d8:0x31a]:
        raise ValueError('Compiled dispatcher copy differs from original bytes')
    if dispatch5 != raw[0][0x2a6:0x2d8]:
        raise ValueError('Compiled dispatcher table-check differs from original bytes')
    if dispatch4 != raw[0][0x26a:0x2a6]:
        raise ValueError('Compiled dispatcher check differs from original bytes')
    if dispatch3 != raw[0][0x232:0x26a]:
        raise ValueError('Compiled dispatcher branch differs from original bytes')
    if dispatch2 != raw[0][0x1da:0x232]:
        raise ValueError('Compiled dispatcher continuation differs from original bytes')
    if dispatch != raw[0][0x180:0x1da]:
        raise ValueError('Compiled dispatcher differs from original bytes')
    if ad != raw[0][0x124:0x156]:
        raise ValueError('Compiled command path differs from original bytes')
    if ae != raw[0][0x86:0xcc]:
        raise ValueError('Compiled command path differs from original bytes')
    if more != raw[0][0x50:0x86]:
        raise ValueError('Compiled dispatch continuation differs from original bytes')
    if entry != raw[0][:0x42]:
        raise ValueError('Compiled entry differs from original bytes')
    if epilogue != raw[0][0x42:0x50]:
        raise ValueError('Compiled epilogue differs from original bytes')
    selected = [entry + epilogue + more + ae + dispatch79 + ad + dispatch80 + dispatch + dispatch2 + dispatch3 + dispatch4 + dispatch5 + dispatch6 + dispatch7 + dispatch8 + dispatch9 + dispatch10 + dispatch11 + dispatch12 + dispatch13 + dispatch14 + dispatch15 + dispatch16 + dispatch17 + dispatch18 + dispatch19 + dispatch20 + dispatch21 + dispatch22 + dispatch23 + dispatch24 + dispatch25 + dispatch26 + dispatch27 + dispatch28 + dispatch29 + dispatch30 + dispatch31 + dispatch32 + dispatch33 + dispatch34 + dispatch35 + dispatch36 + dispatch37 + dispatch38 + dispatch39 + dispatch40 + dispatch41 + dispatch42 + dispatch43 + dispatch44 + dispatch45 + dispatch46 + dispatch47 + dispatch48 + dispatch49 + dispatch50 + dispatch51 + dispatch52 + dispatch53 + dispatch54 + dispatch55 + dispatch56 + dispatch57 + dispatch58 + dispatch59 + dispatch60 + dispatch61 + dispatch62 + dispatch63 + dispatch64 + dispatch65 + dispatch66 + dispatch67 + dispatch68 + dispatch69 + dispatch70 + dispatch71 + dispatch72 + dispatch73 + dispatch74 + dispatch75 + dispatch76 + dispatch77 + dispatch78]
    source = '#ifdef __cplusplus\nextern "C" {\n#endif\n'
    for i, data in enumerate(selected):
        source += '__attribute__((used,section(".tsl9_payload_' + str(i) + '"))) extern const unsigned char payload_' + str(i) + '[] = {'
        source += ','.join(str(x) for x in data) + '};\n'
    source += '#ifdef __cplusplus\n}\n#endif\n'
    src = out / ('opaque-payload-' + mode + '.c')
    src.write_text(source, encoding='ascii')
    obj = out / ('opaque-' + mode + '.o')
    command = [str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32',
               '-ffreestanding', '-fno-common', '-x', 'c' if mode == 'c' else 'c++',
               '-c', str(src), '-o', str(obj)]
    p = subprocess.run(command, capture_output=True, text=True)
    if p.returncode:
        raise ValueError('Opaque source compilation failed: ' + p.stderr[:1000])
    elf = reader(obj)
    compiled = [elf.data(elf.byname['.tsl9_payload_' + str(i)]) for i in range(1)]
    if compiled != raw[:1]:
        raise ValueError('Compiled opaque bytes differ')
    item = next(x for x in manifest['outputs'] if x['mode'] == mode)
    data = (spans_dir / item['file']).read_bytes()
    spans = item['spans']
    if [(x['start'], x['end']) for x in spans] != [(0x8000, 0x14056), (0x14c8a, 0x1ac00)]:
        raise ValueError('Unexpected source spans')
    image = bytearray()
    for i, span in enumerate(spans):
        part = data[span['file_offset']:span['file_offset'] + span['length']]
        if len(part) != span['end'] - span['start']:
            raise ValueError('Short source span')
        image.extend(part)
        if i < len(compiled):
            image.extend(compiled[i])
    digest = hashlib.sha256(image).hexdigest()
    if len(image) != 76800 or digest != EXPECTED:
        raise ValueError('Reconstructed candidate digest mismatch')
    linked = conditional_dir / ('NOT-FLASH-VALIDATED-conditional-link-' + mode + '.bin')
    if linked.read_bytes() != image:
        raise ValueError('Conditional link and assembled candidate differ')
    dest = out / ('NOT-FLASH-VALIDATED-v4160-source-' + mode + '.bin')
    with dest.open('xb') as stream:
        stream.write(image)
    if dest.read_bytes() != image:
        raise ValueError('Output readback mismatch')
    results.append({'mode': mode, 'bytes': len(image), 'sha256': digest, 'file': dest.name})
report = {'passed': True, 'outputs': results, 'opaque_original_bytes': 3128,
                  'compiled_default_bytes_replacing_carrier': 4,
                  'compiled_epilogue_bytes_replacing_carrier': 14,
                  'compiled_entry_bytes_replacing_carrier': 66,
                  'compiled_more_bytes_replacing_carrier': 54,
                  'compiled_ae_bytes_replacing_carrier': 70,
                  'compiled_ad_bytes_replacing_carrier': 50,
                  'compiled_dispatch_bytes_replacing_carrier': 90,
                  'compiled_dispatch2_bytes_replacing_carrier': 88,
                  'compiled_dispatch3_bytes_replacing_carrier': 56,
                  'compiled_dispatch4_bytes_replacing_carrier': 60,
                  'compiled_dispatch5_bytes_replacing_carrier': 50,
                  'compiled_dispatch6_bytes_replacing_carrier': 66,
                  'compiled_dispatch7_bytes_replacing_carrier': 52,
                  'compiled_dispatch8_bytes_replacing_carrier': 70,
                  'compiled_dispatch9_bytes_replacing_carrier': 92,
                  'compiled_dispatch10_bytes_replacing_carrier': 52,
                  'compiled_dispatch11_bytes_replacing_carrier': 72,
                  'compiled_dispatch12_bytes_replacing_carrier': 54,
                  'compiled_dispatch13_bytes_replacing_carrier': 54,
                  'compiled_dispatch14_bytes_replacing_carrier': 36,
                  'compiled_dispatch15_bytes_replacing_carrier': 36,
                  'compiled_dispatch16_bytes_replacing_carrier': 42,
                  'compiled_dispatch17_bytes_replacing_carrier': 70,
                  'compiled_dispatch18_bytes_replacing_carrier': 80,
                  'compiled_dispatch19_bytes_replacing_carrier': 68,
                  'compiled_dispatch20_bytes_replacing_carrier': 50,
                  'compiled_dispatch21_bytes_replacing_carrier': 60,
                  'compiled_dispatch22_bytes_replacing_carrier': 50,
                  'compiled_dispatch23_bytes_replacing_carrier': 36,
                  'compiled_dispatch24_bytes_replacing_carrier': 54,
                  'compiled_dispatch25_bytes_replacing_carrier': 58,
                  'compiled_dispatch26_bytes_replacing_carrier': 54,
                  'compiled_dispatch27_bytes_replacing_carrier': 16,
                  'compiled_dispatch28_bytes_replacing_carrier': 28,
                  'compiled_dispatch29_bytes_replacing_carrier': 30,
                  'compiled_dispatch30_bytes_replacing_carrier': 26,
                  'compiled_dispatch31_bytes_replacing_carrier': 54,
                  'compiled_dispatch33_bytes_replacing_carrier': 12,
                  'compiled_dispatch35_bytes_replacing_carrier': 42,
                  'compiled_dispatch36_bytes_replacing_carrier': 30,
                   'compiled_dispatch45_bytes_replacing_carrier': 2,
                   'compiled_dispatch46_bytes_replacing_carrier': 36,
                   'compiled_dispatch47_bytes_replacing_carrier': 22,
                   'compiled_dispatch52_bytes_replacing_carrier': 34,
                   'compiled_dispatch53_bytes_replacing_carrier': 6,
                   'compiled_dispatch54_bytes_replacing_carrier': 28,
                   'compiled_dispatch55_bytes_replacing_carrier': 22,
                   'compiled_dispatch56_bytes_replacing_carrier': 22,
                    'compiled_dispatch57_bytes_replacing_carrier': 42,
                    'compiled_dispatch58_bytes_replacing_carrier': 8,
                    'compiled_dispatch59_bytes_replacing_carrier': 54,
                    'compiled_dispatch60_bytes_replacing_carrier': 32,
                    'compiled_dispatch61_bytes_replacing_carrier': 20,
                    'compiled_dispatch62_bytes_replacing_carrier': 20,
                    'compiled_dispatch63_bytes_replacing_carrier': 30,
                    'compiled_dispatch64_bytes_replacing_carrier': 22,
                    'compiled_dispatch65_bytes_replacing_carrier': 20,
                    'compiled_dispatch66_bytes_replacing_carrier': 40,
                    'compiled_dispatch75_bytes_replacing_carrier': 10,
                    'compiled_dispatch76_bytes_replacing_carrier': 30,
                    'compiled_dispatch79_bytes_replacing_carrier': 88,
                    'compiled_dispatch80_bytes_replacing_carrier': 42,
    'compiled_dispatch78_bytes_replacing_carrier': 18,
                    'compiled_dispatch77_bytes_replacing_carrier': 40,
                    'compiled_dispatch74_bytes_replacing_carrier': 24,
                    'compiled_dispatch73_bytes_replacing_carrier': 26,
                    'compiled_dispatch72_bytes_replacing_carrier': 18,
                    'compiled_dispatch71_bytes_replacing_carrier': 10,
                     'compiled_dispatch70_bytes_replacing_carrier': 26,
                    'compiled_dispatch69_bytes_replacing_carrier': 8,
                    'compiled_dispatch68_bytes_replacing_carrier': 28,
                    'compiled_dispatch67_bytes_replacing_carrier': 16,
                   'compiled_dispatch51_bytes_replacing_carrier': 18,
                   'compiled_dispatch50_bytes_replacing_carrier': 22,
                   'compiled_dispatch49_bytes_replacing_carrier': 18,
                   'compiled_dispatch48_bytes_replacing_carrier': 18,
                   'compiled_dispatch44_bytes_replacing_carrier': 4,
                   'compiled_dispatch43_bytes_replacing_carrier': 8,
                   'compiled_dispatch42_bytes_replacing_carrier': 4,
                   'compiled_dispatch41_bytes_replacing_carrier': 24,
                   'compiled_dispatch40_bytes_replacing_carrier': 24,
                   'compiled_dispatch39_bytes_replacing_carrier': 12,
                   'compiled_dispatch38_bytes_replacing_carrier': 14,
                   'compiled_dispatch37_bytes_replacing_carrier': 30,
                  'compiled_dispatch34_bytes_replacing_carrier': 26,
                  'compiled_dispatch32_bytes_replacing_carrier': 16,
                  'conditional_link_verified': True, 'conditional_data_aliases': 3,
                  'resident_rom_still_undefined_in_strict_link': True,
                  'global_index_bounds_proved': False, 'ram_ownership_proved': False,
                  'historical_candidate_read_during_build': False,
                  'semantics_recovered': False, 'hardware_validated': False, 'flashable_proved': False}
(out / "verification.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
print(json.dumps(report))
