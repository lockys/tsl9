#!/usr/bin/env python3
"""Offline 81f8 pure-C profile comparison; not a project integration."""
import argparse,hashlib,json,struct,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
TOOLS=Path(r'C:\Users\locky\AppData\Local\Android\Sdk\ndk\27.1.12297006\toolchains\llvm\prebuilt\windows-x86_64\bin')
SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
def section(data):
 h=struct.unpack_from('<16sHHIIIIIHHHHHH',data)
 if h[0][:7]!=b'\x7fELF\x01\x01\x01' or h[1:4]!=(2,243,1) or h[11]!=40 or h[6]+h[11]*h[12]>len(data):raise ValueError('invalid ELF')
 sections=[struct.unpack_from('<10I',data,h[6]+i*h[11]) for i in range(h[12])]
 found=[s for s in sections if s[3]==0x81f8]
 if len(found)!=1:raise ValueError('section missing or ambiguous')
 s=found[0]
 if s[1]!=1 or s[2]&6!=6 or not s[5] or s[4]+s[5]>len(data):raise ValueError('invalid code section')
 return data[s[4]:s[4]+s[5]]
SOURCE='''extern volatile unsigned char tsl9_state_81f8_byte __attribute__((visibility("hidden")));
#ifdef __cplusplus
extern "C"
#endif
__attribute__((used,noinline,aligned(2))) unsigned int tsl9_state_leaf_entry_81f8(void) { return tsl9_state_81f8_byte; }
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--manifest',type=Path);p.add_argument('--ndk-bin',type=Path,default=TOOLS);a=p.parse_args();root=a.root
 data=(root/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
 if hashlib.sha256(data).hexdigest()!=SHA:raise ValueError('reference SHA-256 mismatch')
 ref=data[0x1f8:0x202]
 manifest_path=a.manifest or root/'src/source-build-manifest.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8-sig'));profiles=manifest['code_profiles']['queue-consumer-a0-a5']
 with tempfile.TemporaryDirectory(prefix='81f8-profile-') as tmp:
  d=Path(tmp);(d/'leaf.c').write_text(SOURCE);(d/'link.ld').write_text('tsl9_state_81f8_byte = 0x2000beea; SECTIONS { .text 0x81f8 : { *(.text*) } }')
  for lang in ('c','cpp'):
   for pic in (False,True):
    cmd=[str(a.ndk_bin/'clang.exe'),*profiles[lang],*(['-fpic'] if pic else []),'-c',str(d/'leaf.c'),'-o',str(d/'leaf.o')]
    subprocess.run(cmd,check=True,capture_output=True)
    subprocess.run([str(a.ndk_bin/'ld.lld.exe'),'--no-relax','-T',str(d/'link.ld'),'-o',str(d/'leaf.elf'),str(d/'leaf.o')],check=True,capture_output=True)
    got=section((d/'leaf.elf').read_bytes());print(f'{lang} pic={pic}: {got.hex()} original={ref.hex()} equal={got==ref}')
    if pic and got!=ref:raise ValueError('PIC no longer matches original')
 print('LIMIT: isolated linked leaf, current manifest flags; no aggregate, ABI, live GP or hardware proof')
if __name__=='__main__':main()
