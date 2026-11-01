#!/usr/bin/env python3
"""Compile, order and link only TX; compare just the permitted 280-byte window."""
import argparse
import hashlib
import json
import runpy
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument('--tool-dir', type=Path, required=True)
p.add_argument('--candidate', type=Path, help='Optionally compare the bounded candidate window')
p.add_argument('--out', type=Path, required=True)
p.add_argument('--project-root', type=Path, default=HERE.parents[2])
a = p.parse_args()
ROOT = a.project_root.resolve()
out = a.out.resolve()
if out.exists() or out == HERE or HERE in out.parents:
    raise SystemExit('Output must be new and outside source tree')
tx_sha = '8b129d84cbd65062315ec8197f7cbabb0eae7a4dfec4dca5bf39861851a525b9'
candidate_tx = None
if a.candidate:
    if a.candidate.stat().st_size != 76800: raise SystemExit('Unexpected candidate size')
    with a.candidate.open('rb') as f:
        f.seek(0x8a56 - 0x8000)
        candidate_tx = f.read(280)
    if len(candidate_tx) != 280 or hashlib.sha256(candidate_tx).hexdigest() != tx_sha:
        raise SystemExit('Candidate TX window does not match pinned reference')
post = HERE/'postpass/schedule.py'
policy = post.with_name('policy.json')
for path, digest in ((post, 'a85c69682952a963ff233e76b2f0247b42084b8eab05248f53690f3fb5ef337a'), (policy, '370ea3f33c0164b83a04ee7623bc8507dc8da1e628af7de011ccb951f4dba9a2')):
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest: raise SystemExit('Postpass source or policy changed')
out.mkdir(parents=True)
subprocess.run([sys.executable, '-B', str(HERE/'verify.py'), '--tool-dir', str(a.tool_dir), '--out', str(out/'pre')], check=True, capture_output=True, text=True)
scheduler = runpy.run_path(str(post)); ctx = scheduler['context'](ROOT); scheduler['policy_gate'](policy)
linker = a.tool_dir / ('ld.lld.exe' if (a.tool_dir/'ld.lld.exe').is_file() else 'ld.lld')
objcopy = a.tool_dir / ('llvm-objcopy.exe' if (a.tool_dir/'llvm-objcopy.exe').is_file() else 'llvm-objcopy')
script = out/'tx-only.ld'
script.write_text('OUTPUT_ARCH(riscv)\nENTRY(__tsl9v4160_call_8a56)\nSECTIONS { .text.tsl9_tx_composite 0x8A56 : { KEEP(*(.text.tsl9_tx_entry)) KEEP(*(.text.tsl9_tx_valid_body)) KEEP(*(.text.tsl9_tx_oversized_return)) } /DISCARD/ : { *(.comment) *(.note*) *(.riscv.attributes) *(.llvm_addrsig) } }\nASSERT(SIZEOF(.text.tsl9_tx_composite) == 280, "TX size mismatch")\n', encoding='utf-8')
for mode in ('c', 'cpp'):
    before = out/'pre'/('valid_body-'+mode+'.o')
    ordered, _ = scheduler['transform'](ctx['ELF'](before), ctx['decode'])
    after = out/('valid_body-ordered-'+mode+'.o');after.write_bytes(ordered)
    parts = [out/'pre'/('entry-'+mode+'.o'), after, out/'pre'/('return_leaf-'+mode+'.o')]
    base = [str(linker), '-m', 'elf32lriscv', '--no-relax', '--build-id=none', '-T', str(script), *map(str, parts)]
    strict = subprocess.run([*base, '-o', str(out/('STRICT-NO-RAM-'+mode+'.elf'))], capture_output=True, text=True)
    if strict.returncode == 0 or '__tsl9v4160_data_2000b18c' not in strict.stderr:
        raise SystemExit('Strict missing-RAM-provider check failed')
    elf = out/('NOT-FLASHABLE-TX-ONLY-'+mode+'.elf')
    subprocess.run([*base, '--defsym=__tsl9v4160_data_2000b18c=0x2000B18C', '-o', str(elf)], check=True)
    binary = out/('NOT-FLASHABLE-TX-ONLY-'+mode+'.bin')
    subprocess.run([str(objcopy), '-O', 'binary', '--only-section=.text.tsl9_tx_composite', str(elf), str(binary)], check=True)
    linked_tx = binary.read_bytes()
    if len(linked_tx) != 280 or hashlib.sha256(linked_tx).hexdigest() != tx_sha:
        raise SystemExit('Linked TX differs from pinned digest: ' + mode)
    if candidate_tx is not None and linked_tx != candidate_tx:
        raise SystemExit('Linked TX differs from bounded candidate window: '+mode)
print(json.dumps({'passed': True, 'languages': ['c', 'cpp'], 'tx_bytes': 280, 'tx_digest_matches': True,
                  'candidate_tx_matches': True if candidate_tx is not None else None,
                  'candidate_bytes_read': 280 if candidate_tx is not None else 0, 'ram_provider': 'address witness only',
                  'complete_firmware': False, 'flashable': False, 'target_executed': False}))
