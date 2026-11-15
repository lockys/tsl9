#!/usr/bin/env python3
"""Real toolchain negative controls for 0x81f8 byte comparison (offline)."""
import argparse,hashlib,importlib.util,json,subprocess,tempfile
from pathlib import Path
spec=importlib.util.spec_from_file_location('probe',Path(__file__).with_name('probe.py'))
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=p.ROOT);parser.add_argument('--manifest',type=Path);parser.add_argument('--ndk-bin',type=Path,default=p.TOOLS);args=parser.parse_args()
 image=(args.root/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
 if hashlib.sha256(image).hexdigest()!=p.SHA:raise ValueError('reference SHA-256 mismatch')
 ref=image[0x1f8:0x202]
 profile=json.loads((args.manifest or args.root/'src/source-build-manifest.json').read_text(encoding='utf-8-sig'))['code_profiles']['queue-consumer-a0-a5']
 anchor='return tsl9_state_81f8_byte;'
 if p.SOURCE.count(anchor)!=1:raise ValueError('mutation anchor missing or ambiguous')
 cases=[('candidate',p.SOURCE,True),('increment',p.SOURCE.replace(anchor,'return tsl9_state_81f8_byte + 1;'),False),('constant',p.SOURCE.replace(anchor,'return 0;'),False)]
 with tempfile.TemporaryDirectory(prefix='81f8-negative-') as tmp:
  d=Path(tmp);(d/'link.ld').write_text('tsl9_state_81f8_byte = 0x2000beea; SECTIONS { .text 0x81f8 : { *(.text*) } }')
  for lang in ('c','cpp'):
   for name,source,equal in cases:
    (d/'leaf.c').write_text(source)
    subprocess.run([str(args.ndk_bin/'clang.exe'),*profile[lang],'-fpic','-c',str(d/'leaf.c'),'-o',str(d/'leaf.o')],check=True,capture_output=True)
    subprocess.run([str(args.ndk_bin/'ld.lld.exe'),'--no-relax','-T',str(d/'link.ld'),'-o',str(d/'leaf.elf'),str(d/'leaf.o')],check=True,capture_output=True)
    got=p.section((d/'leaf.elf').read_bytes());same=got==ref
    print(f'{lang} {name}: {got.hex()} equals original={same}')
    if same!=equal:raise ValueError(f'{lang} {name}: unexpected comparison')
 print('PASS: both semantics mutants rejected in C and C++; offline byte comparison only')
if __name__=='__main__':main()
