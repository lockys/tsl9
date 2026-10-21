"""Compile/link our C/C++ callframe component; never execute RV32."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import uuid

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PREVIOUS=ROOT/'apk-analysis/tsl9-v4160-irq-native-2026-10-21/compiler-review'
if not PREVIOUS.is_dir():PREVIOUS=ROOT/'analysis/v4160-irq-native-2026-10-21/compiler-review'
sys.path.insert(0,str(PREVIOUS))
import verify_native as V
from elf32 import ELF


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--language',choices=['c','cpp','both'],default='c')
    p.add_argument('--tool-dir',type=Path,default=V.NDK)
    a=p.parse_args();results=[]
    tools={k:V.resolve_tool(None,a.tool_dir,n) for k,n in [('clang','clang'),('linker','ld.lld'),('objdump','llvm-objdump')]}
    inputs=[ROOT/'experiments/tsl9-v4160-irq-callframe/src'/n for n in ['interrupt_callframe.c','callframe_io.h','rcc_helpers.c']]
    pins={str(p):sha(p) for p in inputs}
    for mode in ['c','cpp'] if a.language=='both' else [a.language]:
        b=ROOT/'experiments/tsl9-v4160-irq-callframe/build'/('probe-'+uuid.uuid4().hex+'-'+mode);b.mkdir(parents=True)
        helper_flags=V.flags(mode)+(['-fno-exceptions'] if mode=='cpp' else [])
        flags=[f for f in helper_flags if f not in {'-ffixed-x1','-ffixed-x2','-ffixed-x8','-ffixed-x9','-ffixed-x18'}]
        commands=[]
        for label,src,options in [('helpers',inputs[2],helper_flags),('main',inputs[0],flags)]:
            for suffix,action in [('.o',['-c']),('.ll',['-S','-emit-llvm'])]:
                cmd,_=V.run([tools['clang'],*options,*action,src,'-o',b/(label+suffix)],b,label+suffix)
                commands.append(cmd)
        ld=b/'placements.ld'
        sections=[' .irq 0x9a42 : { *(.text.'+V.ENTRY+') }']
        sections+=[' .rcc_'+hex(addr)[2:]+' '+hex(addr)+' : { *(.text.'+name+') }' for name,addr in V.HELPERS.items()]
        ld.write_text('ENTRY('+V.ENTRY+')\nSECTIONS {\n'+'\n'.join(sections)+'\n}\n',encoding='utf8')
        linked=b/'COMPONENT-ONLY-NOT-FIRMWARE.elf'
        cmd,_=V.run([tools['linker'],'--no-relax','--no-undefined','-T',ld,b/'main.o',b/'helpers.o','-o',linked],b,'link');commands.append(cmd)
        cmd,text=V.run([tools['objdump'],'--disassemble',linked],b,'disassembly');commands.append(cmd)
        e=ELF(linked);functions={}
        for s in e.symbols:
            if s['info']&15==2 and s['size']:
                blob=e.function_bytes(s)
                functions[s['name']]=dict(address=s['value'],bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest(),raw=blob.hex())
        result=dict(mode=mode,functions=functions,source_sha256=pins,helper_flags=helper_flags,main_flags=flags,
                    tools={k:dict(path=str(t),sha256=sha(t)) for k,t in tools.items()},commands=commands,
                    linked_ELF_sha256=sha(linked),disassembly_sha256=sha(b/'disassembly.log'),
                    target_execution=False,ISA_emulation=False,BIN_created=False,OTA_ready=False)
        (b/'probe.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
        results.append(dict(mode=mode,probe=str(b/'probe.json'),sha256=sha(b/'probe.json'),
                            functions={n:{k:v[k] for k in ['address','bytes','sha256']} for n,v in functions.items()}))
    if any(sha(Path(p))!=h for p,h in pins.items()):raise RuntimeError('Source changed during compile')
    print(json.dumps(dict(results=results,OTA_ready=False)))


if __name__=='__main__':main()
