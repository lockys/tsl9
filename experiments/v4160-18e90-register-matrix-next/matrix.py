"""Offline, static RISC-V register reservation matrix. Never executes ELF."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BIN = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
NDK = Path(r'C:\Users\locky\AppData\Local\Android\Sdk\ndk\27.1.12297006\toolchains\llvm\prebuilt\windows-x86_64\bin')
CLANG, LD = NDK / 'clang.exe', NDK / 'ld.lld.exe'
PINS = {'source': 'a2a291bc18c69ec4911de3e46149234e9d968ea2fac0f5df3180edb180aa0536',
        'bin': '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667',
        'clang': '047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
        'ld': 'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f'}
SYMBOL = 'candidate_18e90_direct'
ADDRESS = 0x18e90
EXPECTED = bytes.fromhex('b7270240c8c78280')
KNOWN = ['b7250240c8c58280', '3726024048c68280', 'b7250240c8c58280', 'b7260240c8c68280',
         'b7250240c8c58280', '3726024048c68280', 'b7250240c8c58280', '3727024048c78280',
         'b7250240c8c58280', '3726024048c68280', 'b7250240c8c58280', 'b7260240c8c68280',
         'b7250240c8c58280', '3726024048c68280', 'b7250240c8c58280', 'b7270240c8c78280']


def check(ok, why):
    if not ok:
        raise ValueError(why)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def pinned(path, name, size=None):
    data = path.read_bytes()
    check(size is None or len(data) == size, name + ' size')
    check(digest(data) == PINS[name], name + ' digest')
    return data


def span(data, offset, size):
    check(offset >= 0 and size >= 0 and offset + size <= len(data), 'ELF truncated')
    return data[offset:offset + size]


def cstring(data, offset):
    check(0 <= offset < len(data), 'string offset')
    end = data.find(b'\0', offset)
    check(end >= 0, 'unterminated string')
    return data[offset:end].decode('ascii')


def elf(data, typ, addr):
    """Read ELF32 LE sections, symbol and load mapping; return full .text bytes."""
    check(span(data, 0, 16) == b'\x7fELF\x01\x01\x01' + b'\0' * 9, 'ELF ident')
    h = struct.unpack('<16sHHIIIIIHHHHHH', span(data, 0, 52))
    _, kind, machine, version, entry, phoff, shoff, flags, ehsize, phsize, phnum, shsize, shnum, stridx = h
    check(kind == typ and machine == 243 and version == 1 and ehsize == 52, 'ELF header')
    check(shsize == 40 and 0 < shnum and stridx < shnum, 'section header metadata')
    sections = [struct.unpack('<IIIIIIIIII', span(data, shoff + i * shsize, 40)) for i in range(shnum)]
    namesec = sections[stridx]
    names = span(data, namesec[4], namesec[5])
    texts = [(i, s) for i, s in enumerate(sections) if cstring(names, s[0]) == '.text']
    check(len(texts) == 1, 'unique .text')
    textidx, text = texts[0]
    _, stype, sflags, saddr, off, size, _, _, _, _ = text
    check(stype == 1 and sflags & 6 == 6 and size > 0, 'text section type/flags/size')
    check(saddr == (0 if typ == 1 else addr), 'text address')
    content = span(data, off, size)
    check(all(not (s[1] in (4, 9) and s[7] == textidx and s[5]) for s in sections), 'text relocations')
    symtabs = [s for s in sections if s[1] == 2]
    check(len(symtabs) == 1, 'unique symtab')
    sym = symtabs[0]
    check(sym[9] == 16 and sym[5] % 16 == 0 and sym[6] < shnum, 'symtab structure')
    strings = sections[sym[6]]
    stringdata = span(data, strings[4], strings[5])
    found = []
    for i in range(sym[5] // 16):
        n, value, length, info, other, index = struct.unpack('<IIIBBH', span(data, sym[4] + 16 * i, 16))
        if cstring(stringdata, n) == SYMBOL:
            found.append((value, length, info, other, index))
    check(len(found) == 1, 'unique function symbol')
    value, length, info, other, index = found[0]
    check(value == (0 if typ == 1 else addr) and length == size and info == 0x12 and index == textidx, 'function entry/size/section')
    if typ == 2:
        check(entry == addr and phsize == 32 and phnum > 0, 'executable entry')
        overlaps = []
        for i in range(phnum):
            p = struct.unpack('<IIIIIIII', span(data, phoff + i * phsize, 32))
            ptype, poff, vaddr, paddr, filesz, memsz, pflags, align = p
            # Also catch malformed file ranges extending past p_memsz.
            extent = max(filesz, memsz)
            if ptype == 1 and extent and vaddr < addr + size and addr < vaddr + extent:
                overlaps.append(p)
        check(len(overlaps) <= 1, 'conflicting PT_LOAD overlap')
        check(len(overlaps) == 1, 'executable PT_LOAD mapping')
        _, poff, vaddr, _, filesz, memsz, pflags, _ = overlaps[0]
        check(pflags & 1 and filesz <= memsz and vaddr <= addr and
              addr + size <= vaddr + filesz and addr + size <= vaddr + memsz and
              poff + addr - vaddr == off, 'executable PT_LOAD mapping')
        span(data, poff, filesz)
    else:
        check(entry == 0, 'relocatable entry')
    return content, off


def validate_bin(image):
    check(len(image) == 76800, 'bin size')
    check(digest(image) == PINS['bin'], 'bin digest')
    window = image[ADDRESS - 0x8000:ADDRESS - 0x8000 + len(EXPECTED)]
    check(window == EXPECTED, 'BIN window')
    return window


def validate_rel(data, expected, addr):
    content, _ = elf(data, 1, addr)
    check(content == expected, 'ET_REL full bytes mismatch')
    return content


def validate_exec(data, expected, addr):
    content, _ = elf(data, 2, addr)
    check(content == expected, 'ET_EXEC full bytes mismatch')
    return content


def validate_outputs(obj, exe, image, expected, addr, expected_match):
    window = validate_bin(image)
    ob = validate_rel(obj, expected, addr)
    ex = validate_exec(exe, expected, addr)
    check(ob == ex, 'ET_REL/ET_EXEC full bytes mismatch')
    matches = ex == window
    check(matches == expected_match, 'matrix regression match')
    return ex, matches


def run(command, cwd, expect=0):
    env = dict(os.environ)
    env['TEMP'] = env['TMP'] = str(cwd)
    p = subprocess.run([str(x) for x in command], cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
    check((p.returncode == 0) if expect == 0 else (p.returncode != 0), 'command status: ' + repr(command) + '\n' + p.stderr.decode(errors='replace'))
    return {'argv': [str(x) for x in command], 'returncode': p.returncode,
            'stdout': p.stdout.decode(errors='replace'), 'stderr': p.stderr.decode(errors='replace')}


def build(out, source, image, mask, opt, addr=ADDRESS):
    out.mkdir()
    src = out / 'leaf.c'
    src.write_bytes(source)
    obj, exe = out / 'leaf.o', out / 'leaf.elf'
    flags = [f'-ffixed-x{11+i}' for i in range(4) if mask & (1 << i)]
    cc = [CLANG, '--target=riscv32-unknown-elf', '-march=rv32imac_zicsr', '-mabi=ilp32', '-std=c11', '-ffreestanding', '-fno-pic', '-fno-stack-protector', opt, *flags, '-c', src, '-o', obj]
    link = [LD, '-m', 'elf32lriscv', '--no-relax', '-Ttext=' + hex(addr), '-e', SYMBOL, obj, '-o', exe]
    commands = [run(cc, out), run(link, out)]
    ex, matches = validate_outputs(obj.read_bytes(), exe.read_bytes(), image,
                                   bytes.fromhex(KNOWN[mask]), addr, mask == 15)
    return {'mask': mask, 'fixed': [f'x{11+i}' for i in range(4) if mask & (1 << i)], 'opt': opt,
            'size': len(ex), 'bytes': ex.hex(), 'matches_bin': matches, 'commands': commands,
            'object_sha256': digest(obj.read_bytes()), 'exec_sha256': digest(exe.read_bytes())}


def reject(label, action, reason):
    try:
        action()
    except (ValueError, FileNotFoundError) as e:
        check((reason in str(e)) if isinstance(e, FileNotFoundError) else (reason == str(e)),
              label + ' wrong failure: ' + str(e))
        return {'case': label, 'rejected': str(e)}
    raise ValueError(label + ' accepted')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True, help='new directory directly within this experiment')
    args = ap.parse_args()
    out = (HERE / args.out).resolve()
    check(out.parent == HERE and not out.exists(), 'output must be a new direct child')
    source = pinned(HERE / 'leaf.c', 'source')
    image = BIN.read_bytes()
    validate_bin(image)
    pinned(CLANG, 'clang'); pinned(LD, 'ld')
    out.mkdir()
    versions = {'clang': run([CLANG, '--version'], out), 'ld': run([LD, '--version'], out)}
    results = [build(out / (opt[1:] + '-' + format(mask, 'x')), source, image, mask, opt)
               for opt in ('-Oz', '-O1') for mask in range(16)]
    neg = out / 'negative'
    neg.mkdir()
    wrong = build(neg / 'wrong-address-recompiled', source, image, 0, '-Oz', ADDRESS + 4)
    wrongpath = neg / 'wrong-address-recompiled' / 'leaf.elf'
    objdata = (out / 'Oz-0' / 'leaf.o').read_bytes()
    exedata = (out / 'Oz-0' / 'leaf.elf').read_bytes()
    expected = bytes.fromhex(KNOWN[0])
    def accept(obj=objdata, exe=exedata, bin_data=image):
        return validate_outputs(obj, exe, bin_data, expected, ADDRESS, False)
    tests = [reject('recompiled wrong VMA/entry', lambda: accept(exe=wrongpath.read_bytes()), 'text address')]
    tests.append(reject('missing pinned BIN', lambda: pinned(neg / 'absent.bin', 'bin', 76800), 'absent.bin'))
    missing = run([CLANG, '--target=riscv32-unknown-elf', '-std=c11', '-c', neg / 'absent.c', '-o', neg / 'missing.o'], neg, expect=1)
    check('absent.c' in missing['stderr'], 'missing input diagnostic')
    tests.append({'case': 'missing source compile', 'command': missing})
    missing_obj = run([LD, '-m', 'elf32lriscv', '-Ttext=0x18e90', '-e', SYMBOL, neg / 'absent.o', '-o', neg / 'missing.elf'], neg, expect=1)
    check('absent.o' in missing_obj['stderr'], 'missing object diagnostic')
    tests.append({'case': 'missing object link', 'command': missing_obj})
    raw = bytearray(exedata)
    _, offset = elf(raw, 2, ADDRESS)
    raw[offset] ^= 1
    (neg / 'mutated.elf').write_bytes(raw)
    exe_mutation = lambda: accept(exe=bytes(raw))
    tests.append(reject('ELF raw section mutation', exe_mutation, 'ET_EXEC full bytes mismatch'))
    badentry = bytearray(exedata)
    struct.pack_into('<I', badentry, 24, ADDRESS + 4)
    (neg / 'bad-entry.elf').write_bytes(badentry)
    tests.append(reject('ELF raw entry mutation', lambda: accept(exe=bytes(badentry)), 'executable entry'))
    rawobj = bytearray(objdata)
    _, objoff = elf(rawobj, 1, ADDRESS)
    rawobj[objoff] ^= 1
    (neg / 'mutated.o').write_bytes(rawobj)
    obj_mutation = lambda: accept(obj=bytes(rawobj))
    tests.append(reject('ET_REL raw section mutation', obj_mutation, 'ET_REL full bytes mismatch'))
    badbin = bytearray(image)
    badbin[ADDRESS - 0x8000] ^= 1
    bin_mutation = lambda: accept(bin_data=bytes(badbin))
    tests.append(reject('wrong BIN raw byte', bin_mutation, 'bin digest'))

    # Repurpose the original non-code PT_LOAD without changing the valid code PT_LOAD.
    # Both extra segments have a different offset, one file-backed and one zero-filled.
    h = struct.unpack('<16sHHIIIIIHHHHHH', exedata[:52])
    phoff, phsize, phnum = h[5], h[9], h[10]
    loads = [i for i in range(phnum) if struct.unpack_from('<I', exedata, phoff + i * phsize)[0] == 1]
    check(len(loads) == 2, 'negative fixture PT_LOAD count')
    for label, filesz, memsz, vaddr in [('nonexec-different-offset', 8, 8, ADDRESS),
                                         ('zero-fill-different-offset', 0, 8, ADDRESS),
                                         ('invalid-filesz-over-memsz', 8, 0, ADDRESS),
                                         ('partial-overlap', 4, 4, ADDRESS + 4)]:
        conflict = bytearray(exedata)
        struct.pack_into('<IIIIIIII', conflict, phoff + loads[0] * phsize,
                         1, 0, vaddr, vaddr, filesz, memsz, 4, 1)
        (neg / (label + '.elf')).write_bytes(conflict)
        tests.append(reject('ELF PT_LOAD ' + label, lambda: accept(exe=bytes(conflict)),
                            'conflicting PT_LOAD overlap'))

    # The *same* negative tests must fail if a production acceptance guard is removed.
    def bypass_guard(name, replacement, action, label, reason):
        original = globals()[name]
        try:
            globals()[name] = replacement
            return reject('disabled ' + name, lambda: reject(label, action, reason), label + ' accepted')
        finally:
            globals()[name] = original
    tests.append(bypass_guard('validate_rel', lambda *args: expected, obj_mutation,
                              'ET_REL raw section mutation', 'ET_REL full bytes mismatch'))
    tests.append(bypass_guard('validate_exec', lambda *args: expected, exe_mutation,
                              'ELF raw section mutation', 'ET_EXEC full bytes mismatch'))
    conflict_action = lambda: accept(exe=(neg / 'nonexec-different-offset.elf').read_bytes())
    tests.append(bypass_guard('validate_exec', lambda *args: expected, conflict_action,
                              'ELF PT_LOAD nonexec-different-offset', 'conflicting PT_LOAD overlap'))
    tests.append(bypass_guard('validate_bin', lambda *args: EXPECTED, bin_mutation,
                              'wrong BIN raw byte', 'bin digest'))
    summary = {'python': sys.version, 'python_optimize': sys.flags.optimize, 'pins': PINS, 'bin_path': str(BIN),
               'bin_window': EXPECTED.hex(), 'source_original': 'experiments/v4160-18e90-direct-c/candidate.c',
               'versions': versions, 'results': results, 'negative': tests, 'wrong_address_case': wrong}
    (out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    for r in results:
        print(f"{r['opt']} mask={r['mask']:x} fixed={','.join(r['fixed']) or '-':15} size={r['size']:2} bytes={r['bytes']} match={r['matches_bin']}")
    print('negative tests:', ', '.join(x['case'] for x in tests))
    print('receipt:', out / 'summary.json')


if __name__ == '__main__':
    main()
