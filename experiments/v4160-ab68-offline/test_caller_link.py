#!/usr/bin/env python3
"""Check isolated caller binding; does not validate stock callers or full image."""
import argparse
import importlib.util
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('ab68_verify', HERE/'verify_compiled.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

CALLER = '''#ifdef __cplusplus
extern "C" {
#endif
extern unsigned int tsl9_ab68(void);
__attribute__((section(".text.caller"), used, noinline))
unsigned int isolated_caller(void) { return tsl9_ab68(); }
#ifdef __cplusplus
}
#endif
'''

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('bin', type=Path)
    parser.add_argument('llvm_bin', type=Path)
    args = parser.parse_args()
    image = args.bin.read_bytes()
    import hashlib
    module.verify.require(hashlib.sha256(image).hexdigest() == module.verify.IMAGE_SHA256, 'firmware SHA-256')
    module.verify.require(image[module.PC-module.verify.IMAGE_BASE:module.PC-module.verify.IMAGE_BASE+10] == module.EXPECTED, 'original bytes')
    source = (HERE/'candidate.c').read_text(encoding='utf-8')
    renamed = source.replace('unsigned int tsl9_ab68(void)', 'unsigned int renamed_ab68(void)')
    module.verify.require(renamed != source, 'rename anchor')
    clang = args.llvm_bin / ('clang.exe' if (args.llvm_bin/'clang.exe').exists() else 'clang')
    ld = args.llvm_bin / ('ld.lld.exe' if (args.llvm_bin/'ld.lld.exe').exists() else 'ld.lld')
    with tempfile.TemporaryDirectory(prefix='tsl9-ab68-caller-') as tmp:
        root = Path(tmp)
        caller, leaf, co, lo, elf, script = (root/'caller.c', root/'leaf.c', root/'caller.o', root/'leaf.o', root/'out.elf', root/'layout.ld')
        caller.write_text(CALLER, encoding='utf-8')
        script.write_text('tsl9_ab68_data = 0x2000bee8;\nSECTIONS { .text.tsl9_ab68 0xab68 : { *(.text.tsl9_ab68) } .text.caller 0x10394 : { *(.text.caller) } }\n')
        for lang, standard in (('c', 'c11'), ('c++', 'c++17')):
            flags = [clang, '--target=riscv32-unknown-elf', '-march=rv32imac_zicsr', '-mabi=ilp32', '-Oz', '-fpic', '-mno-relax', '-ffreestanding', '-fno-builtin', '-x', lang, '-std='+standard, '-c']
            module.helper.run(flags + [caller, '-o', co])
            for name, contents in (('original', source), ('renamed', renamed)):
                leaf.write_text(contents, encoding='utf-8')
                module.helper.run(flags + [leaf, '-o', lo])
                proc = subprocess.run([str(x) for x in (ld, '--no-relax', '-T', script, co, lo, '-o', elf)], capture_output=True, text=True)
                if name == 'original':
                    module.verify.require(proc.returncode == 0, 'positive link failed: '+proc.stderr)
                    module.verify.PC = module.PC
                    module.verify.require(module.helper.executable_section(elf.read_bytes()) == module.EXPECTED, 'leaf bytes')
                else:
                    module.verify.require(proc.returncode != 0 and 'undefined symbol: tsl9_ab68' in proc.stderr, 'rename must fail due to missing symbol')
                print(lang, name, 'linked' if proc.returncode == 0 else 'rejected: undefined tsl9_ab68')
    print('LIMIT: synthetic caller; no stock caller, ROM, runtime or device validation')

if __name__ == '__main__':
    main()
