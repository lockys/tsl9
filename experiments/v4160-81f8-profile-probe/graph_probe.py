#!/usr/bin/env python3
"""Replace one owner in a three-unit relocatable graph; offline experiment only."""
import argparse,hashlib,importlib.util,json,re,subprocess,tempfile
from pathlib import Path
spec=importlib.util.spec_from_file_location('probe',Path(__file__).with_name('probe.py'));p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
HASHES={'direct_successors_native.c':'150096a17a9cdc945edc563a9bcbc49b64eba1301910d27d3ef7cb6fed46f5c6','direct_followup_native.c':'2b3bf57faf0babf8cf6f3f91f6aad52b2e3bdf12aac538b9882b43d70a75039c','post_table_code_native.c':'80fafcb75df886e324b2d7b58ccbe0311f7f054aaaa71c8fcb08185bb71d7370'}
START='    ".section .text.tsl9v4160.direct_successors_81f8,\\"ax\\",@progbits\\n"\n'
END='    ".section .text.tsl9v4160.direct_successors_8248,\\"ax\\",@progbits\\n"\n'
CANDIDATE='''#ifdef __cplusplus
extern "C" {
#endif
extern volatile unsigned char tsl9_81f8_data __attribute__((visibility("hidden")));
__attribute__((section(".text.tsl9v4160.direct_successors_81f8"),used,noinline,aligned(2))) unsigned int __tsl9v4160_call_81f8(void) { return tsl9_81f8_data; }
#ifdef __cplusplus
}
#endif
'''
def main():
 a=argparse.ArgumentParser();a.add_argument('--root',type=Path,default=p.ROOT);a.add_argument('--source-root',type=Path);a.add_argument('--ndk-bin',type=Path,default=p.TOOLS);args=a.parse_args();root=args.root;src=args.source_root or root/'experiments/tsl9-v4160-startup/src'
 image=(root/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
 if hashlib.sha256(image).hexdigest()!=p.SHA:raise ValueError('image SHA mismatch')
 sources={}
 for name,sha in HASHES.items():
  data=(src/name).read_bytes().replace(b'\r\n',b'\n')
  if hashlib.sha256(data).hexdigest()!=sha:raise ValueError('source SHA mismatch: '+name)
  sources[name]=data.decode('utf-8').replace('\r\n','\n')
 original=sources['direct_successors_native.c']
 if original.count(START)!=1 or original.count(END)!=1:raise ValueError('owner boundaries missing')
 modified=original[:original.index(START)]+original[original.index(END):]
 flags=['--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-Oz','-ffreestanding','-mno-relax','-I',str(src)]
 def run(cmd):return subprocess.run([str(x) for x in cmd],check=True,capture_output=True,text=True)
 with tempfile.TemporaryDirectory(prefix='81f8-graph-') as tmp:
  d=Path(tmp);(d/'modified.c').write_text(modified,encoding='utf-8');(d/'candidate.c').write_text(CANDIDATE);(d/'link.ld').write_text('tsl9_81f8_data = 0x2000beea; SECTIONS { .text 0x81f8 : { *(.text.tsl9v4160.direct_successors_81f8) } }')
  for lang,std in (('c','c11'),('c++','c++17')):
   objects=[]
   for name in ('modified.c','direct_followup_native.c','post_table_code_native.c','candidate.c'):
    source=(d/name if name in ('modified.c','candidate.c') else src/name);obj=d/(name+'.o')
    run([args.ndk_bin/'clang.exe',*flags,'-x',lang,'-std='+std,*(['-fpic'] if name=='candidate.c' else []),'-c',source,'-o',obj]);objects.append(obj)
   graph=d/'graph.o';run([args.ndk_bin/'ld.lld.exe','-r',*objects,'-o',graph])
   syms=run([args.ndk_bin/'llvm-readelf.exe','-sW',graph]).stdout
   matches=[line for line in syms.splitlines() if re.search(r'\b__tsl9v4160_call_81f8$',line)]
   if len(matches)!=1 or not re.search(r'\bFUNC\s+GLOBAL\s+DEFAULT\s+\d+',matches[0]):raise ValueError('owner definition missing or ambiguous: '+repr(matches))
   rel=run([args.ndk_bin/'llvm-readelf.exe','-rW',graph]).stdout
   callers=[line for line in rel.splitlines() if re.search(r'\b__tsl9v4160_call_81f8\b',line)]
   if len(callers)!=2 or any('R_RISCV_JAL' not in line for line in callers):raise ValueError('caller relocations not preserved: '+repr(callers))
   elf=d/'leaf.elf';run([args.ndk_bin/'ld.lld.exe','--no-relax','--gc-sections','-e','__tsl9v4160_call_81f8','-T',d/'link.ld','-o',elf,graph]);got=p.section(elf.read_bytes())
   if got!=image[0x1f8:0x202]:raise ValueError('leaf mismatch')
   print(f'{lang}: one owner, {len(callers)} JAL references, final bytes {got.hex()}')
 print('LIMIT: three-source partial graph; no complete firmware link or execution')
if __name__=='__main__':main()
