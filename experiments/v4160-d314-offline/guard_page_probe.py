"""Windows x64 offline probe; compiles a transformed candidate, not the original.

All generated sources, objects and executables live in a temporary directory.
The macro replaces only the external storage binding with a pointer lvalue;
the negative control additionally inserts a volatile write and restore.
"""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile

CANDIDATE_SHA256 = '278463f304c61bccc9bb6e6c685411466865ecbd4009d01775a8974e4d6f84f9'
DECL = 'extern volatile unsigned short tsl9_d314_data __attribute__((visibility("hidden")));'
BODY = 'unsigned int __tsl9v4160_call_d314(void) { return tsl9_d314_data != 0; }'
MUTANT = ('unsigned int __tsl9v4160_call_d314(void) { '
          'unsigned short old = tsl9_d314_data; tsl9_d314_data = (unsigned short)(old ^ 1); '
          'tsl9_d314_data = old; return tsl9_d314_data != 0; }')
WRONG_ADDRESS = ('unsigned int __tsl9v4160_call_d314(void) { '
                 'probe_storage[1] = 7; return tsl9_d314_data != 0; }')
HOST = r'''
#ifdef __cplusplus
extern "C" {
#endif
__declspec(dllimport) void * __stdcall VirtualAlloc(void *, unsigned long long, unsigned long, unsigned long);
__declspec(dllimport) int __stdcall VirtualProtect(void *, unsigned long long, unsigned long, unsigned long *);
__declspec(dllimport) unsigned int __stdcall SetErrorMode(unsigned int);
__declspec(dllimport) void __stdcall ExitProcess(unsigned int);
__declspec(dllimport) void * __stdcall AddVectoredExceptionHandler(unsigned long, void *);
volatile unsigned short *probe_storage;
struct exception_record {
    unsigned long code, flags;
    struct exception_record *nested;
    void *address;
    unsigned long count;
    unsigned long long info[15];
};
struct exception_pointers { struct exception_record *record; void *context; };
long __stdcall exception_handler(struct exception_pointers *p) {
    if (p && p->record && p->record->code == 0xc0000005UL &&
        p->record->count >= 2 && p->record->info[0] == 1 &&
        p->record->info[1] == (unsigned long long)probe_storage) ExitProcess(21);
    return 0; /* continue searching for unrelated faults */
}
unsigned int __tsl9v4160_call_d314(void);
#ifdef __cplusplus
}
#endif
void mainCRTStartup(void) {
    unsigned long previous = 0;
    unsigned int result;
    SetErrorMode(0x0001 | 0x0002 | 0x8000);
    if (!AddVectoredExceptionHandler(1, (void *)exception_handler)) ExitProcess(15);
    probe_storage = (volatile unsigned short *)VirtualAlloc(0, 4096, 0x3000, 0x04);
    if (!probe_storage) ExitProcess(10);
    *probe_storage = TEST_VALUE;
    if (!VirtualProtect((void *)probe_storage, 4096, 0x02, &previous)) ExitProcess(11);
    if (previous != 0x04) ExitProcess(12);
    result = __tsl9v4160_call_d314();
    if (result != (TEST_VALUE != 0)) ExitProcess(13);
    if (*probe_storage != TEST_VALUE) ExitProcess(14);
    ExitProcess(0);
}
'''


def run(cmd):
    p = subprocess.run([str(x) for x in cmd], capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(f"command failed ({p.returncode}): {cmd}\n{p.stdout}\n{p.stderr}")


def main():
    if os.name != 'nt':
        raise RuntimeError('Windows only')
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('candidate', 'clang', 'link', 'sdk-lib'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    for path in (args.candidate, args.clang, args.link, args.sdk_lib):
        if not path.is_file():
            raise FileNotFoundError(path)
    raw = args.candidate.read_bytes()
    if hashlib.sha256(raw).hexdigest() != CANDIDATE_SHA256:
        raise ValueError('candidate SHA-256 differs from pinned source')
    original = raw.decode('utf-8')
    if original.count(DECL) != 1 or original.count(BODY) != 1:
        raise RuntimeError('candidate changed: refusing an ambiguous transformation')
    binding = 'extern volatile unsigned short *probe_storage;\n#define tsl9_d314_data (*probe_storage)'
    transformed = original.replace(DECL, binding)
    with tempfile.TemporaryDirectory(prefix='d314-guard-') as tmp:
        root = Path(tmp)
        for language in ('c', 'c++'):
            for variant in ('candidate', 'mutant', 'wrong_address'):
                source = transformed if variant == 'candidate' else transformed.replace(BODY, MUTANT if variant == 'mutant' else WRONG_ADDRESS)
                cfile = root / 'candidate.txt'
                cfile.write_text(source, encoding='utf-8')
                obj = root / 'candidate.obj'
                flags = [args.clang.resolve(), '-target', 'x86_64-pc-windows-msvc', '-fno-stack-protector', '-O2', '-x', language, '-c']
                run(flags + [cfile, '-o', obj])
                for value in (0, 1, 65535):
                    hfile = root / 'host.txt'
                    hfile.write_text(HOST, encoding='utf-8')
                    hobj = root / 'host.obj'
                    exe = root / 'probe.exe'
                    run(flags + [f'-DTEST_VALUE={value}', hfile, '-o', hobj])
                    run([args.link.resolve(), '/nologo', '/nodefaultlib', '/subsystem:console', '/entry:mainCRTStartup',
                         f'/out:{exe}', obj, hobj, args.sdk_lib.resolve()])
                    p = subprocess.run([str(exe)], capture_output=True, timeout=10)
                    code = p.returncode & 0xffffffff
                    expected = {'candidate': 0, 'mutant': 21, 'wrong_address': 0xc0000005}[variant]
                    print(f'{language} {variant} value={value}: 0x{code:08X}', flush=True)
                    if code != expected:
                        raise RuntimeError(f'expected exit 0x{expected:08X}; stdout={p.stdout!r}, stderr={p.stderr!r}')
    if hashlib.sha256(args.candidate.read_bytes()).hexdigest() != CANDIDATE_SHA256:
        raise ValueError('candidate changed during test')
    print('PASS: transformed candidate succeeded; write/restore mutant hit verified write violation at storage.')
    print('Limit: host x64 RAM read-only page only; no original binding, firmware, hardware or read-side-effects tested.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        sys.exit(1)
