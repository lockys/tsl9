#!/usr/bin/env python3
"""Isolated 0x9f74 candidate; numeric GP witness is not a runtime binding."""
import argparse, hashlib, importlib.util, tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('gp_verify',HERE.parent/'v4160-gp-leaves-offline'/'verify_compiled.py');gp=importlib.util.module_from_spec(s);s.loader.exec_module(gp)

def main():
 p=argparse.ArgumentParser();p.add_argument('bin',type=Path);p.add_argument('llvm_bin',type=Path);a=p.parse_args()
 raw=a.bin.read_bytes();gp.verify.require(hashlib.sha256(raw).hexdigest()==gp.verify.IMAGE_SHA256,'firmware SHA')
 original=raw[0x9f74-gp.verify.IMAGE_BASE:0x9f7a-gp.verify.IMAGE_BASE]
 gp.verify.require(original==bytes.fromhex('a387010a8280'),'original bytes')
 clang=a.llvm_bin/('clang.exe' if (a.llvm_bin/'clang.exe').exists() else 'clang')
 ld=a.llvm_bin/('ld.lld.exe' if (a.llvm_bin/'ld.lld.exe').exists() else 'ld.lld')
 source=(HERE/'candidate.c').read_text(encoding='utf-8')
 statement='tsl9_9f74_data = 0;';gp.verify.require(source.count(statement)==1,'mutation anchor')
 with tempfile.TemporaryDirectory(prefix='tsl9-9f74-') as tmp:
  root=Path(tmp);obj=root/'leaf.o';elf=root/'leaf.elf';script=root/'layout.ld'
  for lang,std in [('c','c11'),('c++','c++17')]:
   for variant,text in [('candidate',source),('nonzero',source.replace(statement,'tsl9_9f74_data = 1;')),('no-store',source.replace(statement,'(void)0;'))]:
    unit=root/'unit.c';unit.write_text(text,encoding='utf-8')
    gp.run([clang,'--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-Oz','-fno-pic','-msmall-data-limit=8','-ffreestanding','-fno-builtin','-x',lang,'-std='+std,'-c',unit,'-o',obj])
    for label,base,target,link_flags in [('reference',0x20004000,0x200040af,['--relax','--relax-gp']),('wrong-offset',0x20004000,0x200040b0,['--relax','--relax-gp']),('shifted-pair',0x20004004,0x200040b3,['--relax','--relax-gp']),('no-relax',0x20004000,0x200040af,['--no-relax'])]:
     script.write_text('__global_pointer$ = '+hex(base)+';\ntsl9_9f74_data = '+hex(target)+';\nSECTIONS { .text.tsl9_9f74_candidate 0x9f74 : { *(.text.tsl9_9f74_candidate) } }\n')
     gp.run([ld,*link_flags,'-T',script,obj,'-o',elf])
     leaf=gp.executable_section(elf.read_bytes(),0x9f74)
     expect=variant=='candidate' and label in ('reference','shifted-pair')
     gp.verify.require((leaf==original)==expect,'unexpected bytes '+lang+' '+variant+' '+label)
     print(lang,variant,label,leaf.hex(),'match='+str(leaf==original))
 print('LIMIT: isolated numeric linking only; no proof of actual GP, ABI, callback reachability, or hardware')
 print('NOTE: the candidate needs GP relaxation for byte identity; stock no-relax layout needs a separate integration strategy')
if __name__=='__main__':main()
