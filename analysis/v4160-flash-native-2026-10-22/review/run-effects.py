#!/usr/bin/env python3
"""Compile owned host code only against an independent expected-effect oracle."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import uuid

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def need(value,message):
    if not value:raise ValueError(message)
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root',type=Path,required=True)
    parser.add_argument('--language',choices=['c','cpp'],required=True)
    args=parser.parse_args();project=args.project_root.resolve(strict=True);root=Path(__file__).resolve().parent
    model=project/'experiments/tsl9-v4160-flash-native/src';source=model/'flash_native.c';host=model/'host_io.c'
    oracle=root/'expected-effects.c';helper=project/'scripts/portable_verify.py'
    spec=importlib.util.spec_from_file_location('host_tools',helper);tools=importlib.util.module_from_spec(spec);spec.loader.exec_module(tools)
    compiler,env,msvc=tools.compiler_for(args.language);compiler_sha=sha(compiler)
    inputs=[*sorted(model.glob('*')),oracle,helper,Path(__file__).resolve()]
    pins={str(p):sha(p) for p in inputs if p.is_file()}
    build=root/'build'/('effects-'+uuid.uuid4().hex+'-'+args.language);build.mkdir(parents=True)
    flags=(['/nologo','/W4','/WX','/Od','/TP' if args.language=='cpp' else '/TC','/std:c++17' if args.language=='cpp' else '/std:c11','/DTSL9_FLASH_HOST_TEST=1','/I'+str(model),'/Fo'+str(build)+os.sep] if msvc else ['-x','c++' if args.language=='cpp' else 'c','-std=c++17' if args.language=='cpp' else '-std=c11','-O0','-Wall','-Wextra','-Werror','-DTSL9_FLASH_HOST_TEST=1','-I',str(model)])
    def command(argv,log):
        result=subprocess.run([str(x) for x in argv],cwd=build,env=env,capture_output=True,encoding='utf-8',errors='replace',timeout=90)
        log.write_bytes((result.stdout+result.stderr).encode('utf-8'));return result
    def check(name,body=None):
        chosen=source
        if body is not None:chosen=build/(name+'.c');chosen.write_bytes(body.encode('utf-8'))
        executable=build/(name+('.exe' if os.name=='nt' else ''))
        argv=([compiler,*flags,chosen,host,oracle,'/Fe'+str(executable),'/link','/INCREMENTAL:NO'] if msvc else [compiler,*flags,chosen,host,oracle,'-o',executable])
        compiled=command(argv,build/(name+'-compile.log'));need(compiled.returncode==0,'Actual compile must pass: '+name)
        result=command([executable],build/(name+'-run.log'))
        if body is None:
            need(result.returncode==0,'Expected-effect positive run');value=json.loads(result.stdout)
            need(value['passed'] and value['groups']==1 and value['cases']==12,'Six entries, two independent scenarios each')
        else:
            need(result.returncode!=0 and 'REVIEW_FAIL ' in result.stderr,'Actual compiled behavior mutant rejection: '+name)
            value={'rejected':True,'exit':result.returncode,'reason':result.stderr.strip()}
        return {'executable_sha256':sha(executable),'result':value}
    positive=check('positive');raw=source.read_text(encoding='utf-8')
    mutations=[
      ('unlock-key-order','FN_WRITE(0x18ea8u,FN_ADD(base,FN_K(4u)),key1);','FN_WRITE(0x18ea8u,FN_ADD(base,FN_K(4u)),key2);',1),
      ('status-not49','FN_CALL_STATUS(FN_K(49u))','FN_CALL_STATUS(FN_K(48u))',1),
      ('align128','FN_AND(destination,FN_K(0xffffff00u))','FN_AND(destination,FN_K(0xffffff80u))',2),
      ('erase-wrong-final-mask','FN_MASK3(0xfffdffffu)','FN_MASK3(0xfffeffffu)',1),
      ('program-wrong-mode','FN_MASK3(0x10000u)','FN_MASK3(0x20000u)',1),
      ('write-before-source-read','FN_READ(0x18f1eu,FN_ADD(source,FN_K(offset)),last_word);','FN_WRITE(0x18f26u,FN_ADD(destination,FN_K(offset)),FN_K(0u));FN_READ(0x18f1eu,FN_ADD(source,FN_K(offset)),last_word);',1),
      ('per-word-poll-wrong-bit','FN_POLL_TRUE(0x18f2eu,status,2u)','FN_POLL_TRUE(0x18f2eu,status,1u)',1),
      ('cached-CTRL-before-commit','FN_READ(0x18f36u,FN_ADD(base,FN_K(16u)),before);','/* omitted required fresh CTRL read */',1),
      ('status-return-zero','FN_RET_STATUS(status,base)','FN_RET_STATUS(FN_K(0u),base)',1),
      ('lock-wrong-A5','FN_RET_UNLOCK(incoming_a0,mask,base,after)','FN_RET_UNLOCK(incoming_a0,mask,base,before)',1),
      ('stride8','offset+=4u;','offset+=8u;',1),
      ('cached-frame-source','FN_FRAME_RELOAD(source);','/* removed live frame source reload */',1)
    ]
    negatives=[]
    for name,anchor,replacement,count in mutations:
        need(raw.count(anchor)==count,'Frozen source mutation anchor '+name)
        negatives.append({'name':name,**check(name,raw.replace(anchor,replacement))})
    need(all(sha(Path(n))==pin for n,pin in pins.items()) and sha(compiler)==compiler_sha,'Unchanged source/oracle/compiler')
    receipt={'schema':'TSL9-independent-expected-flash-effects-v1','passed':True,'language':args.language,'source_pins':pins,'compiler':str(compiler),'compiler_sha256':compiler_sha,'positive':positive,'actually_compiled_mutants':negatives,'actual_mutants_rejected':len(negatives),'host_only':True,'native_register_proof':False,'target_execution':False,'ISA_emulation':False,'hardware':False,'network':False}
    encoded=(json.dumps(receipt,indent=2)+'\n').encode('utf-8');(build/'verification.json').write_bytes(encoded)
    selected=root/'receipts'/('effects-'+build.name+'.json');selected.parent.mkdir(exist_ok=True);selected.write_bytes(encoded)
    print(json.dumps({'passed':True,'receipt':str(selected),'sha256':sha(selected),'positive':positive['result'],'actual_mutants_rejected':len(negatives)},sort_keys=True))
if __name__=='__main__':main()
