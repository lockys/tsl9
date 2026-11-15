#!/usr/bin/env python3
"""Offline 81f8 pure-C profile comparison; not a project integration."""
import argparse,hashlib,importlib.util,json,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SOURCE='''extern volatile unsigned char tsl9_state_81f8_byte __attribute__((visibility("hidden")));
#ifdef __cplusplus
extern "C"
#endif
__attribute__((used,noinline,aligned(2))) unsigned int tsl9_state_leaf_entry_81f8(void) { return tsl9_state_81f8_byte; }
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);a=p.parse_args();root=a.root
 s=importlib.util.spec_from_file_location('verify',root/'experiments/v4160-81f8-pure-c/verify.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
 data=(root/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes();ref=v.reference(data)
 manifest=json.loads((root/'src/source-build-manifest.json').read_text(encoding='utf-8'));profiles=manifest['code_profiles']['queue-consumer-a0-a5']
 with tempfile.TemporaryDirectory(prefix='81f8-profile-') as tmp:
  d=Path(tmp);(d/'leaf.c').write_text(SOURCE);(d/'link.ld').write_text('tsl9_state_81f8_byte = 0x2000beea; SECTIONS { .text 0x81f8 : { *(.text*) } }')
  for lang in ('c','cpp'):
   for pic in (False,True):
    cmd=[str(v.TOOLS/'clang.exe'),*profiles[lang],*(['-fpic'] if pic else []),'-c',str(d/'leaf.c'),'-o',str(d/'leaf.o')]
    subprocess.run(cmd,check=True,capture_output=True)
    subprocess.run([str(v.TOOLS/'ld.lld.exe'),'--no-relax','-T',str(d/'link.ld'),'-o',str(d/'leaf.elf'),str(d/'leaf.o')],check=True,capture_output=True)
    got=v.section((d/'leaf.elf').read_bytes());print(f'{lang} pic={pic}: {got.hex()} original={ref.hex()} equal={got==ref}')
    if pic and got!=ref:raise ValueError('PIC no longer matches original')
 print('LIMIT: isolated linked leaf, current manifest flags; no aggregate, ABI, live GP or hardware proof')
if __name__=='__main__':main()
