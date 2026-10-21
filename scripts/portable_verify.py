#!/usr/bin/env python3
"""Offline source-proof and host-model verification with a native C/C++ compiler.

Only our selected host tests run. Original firmware is data, never executable.
This entry does not silently replace historical RV32/ELF or hardware gates.
"""
from __future__ import annotations
import argparse
import functools
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIRMWARE = 'ID-2966-V4.1.60-decoded.bin'
CARRIER = 'REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin'
TAIL = 'REFERENCE-CANDIDATE-ONLY-0006EAA4-0006EB2C.bin'
SPECS = {
    'runtime-loop': dict(folder='tsl9-v4160-runtime-loop', scope='v4160-runtime-loop-2026-10-21',
        sources=['src/runtime_loop.c', 'tests/test_runtime_loop.c'], includes=['tsl9-resident-entry-reference'],
        dependencies=[], expected=(6, 1431), proof=dict(bytes=220,instructions=80,raw_operand_mutation_rejections=45)),
    'system-clock-query': dict(folder='tsl9-v4160-system-clock-query', scope='v4160-system-clock-query-2026-10-21',
        sources=['src/system_clock_query.c', 'tests/test_system_clock_query.c'], includes=['tsl9-v4160-runtime-loop','tsl9-resident-entry-reference'],
        dependencies=['tsl9-v4160-runtime-loop/src/runtime_loop.c'], expected=(7,1414),
        proof=dict(target_bytes=214,target_instructions=69,raw_operand_mutation_rejections=50)),
    'resident-entry': dict(folder='tsl9-resident-entry-reference', scope='resident-entry-reference-2026-10-21',
        sources=['src/resident_entry.c','src/reset_entry_bridge.c','tests/test_resident_entry.c'], includes=['tsl9-v4160-reset-contract'],
        dependencies=[], expected=(5,121496), proof=dict(body_bytes=230,body_instructions=66,header_bytes=4,raw_operand_mutation_rejections=35)),
    'resident-copy': dict(folder='tsl9-resident-copy-reference',scope='resident-copy-reference-2026-10-21',
        sources=['src/reference_copy.c','tests/test_reference_copy.c'],
        includes=['tsl9-boot2580-command-adapter','tsl9-boot2580-uid-helper','tsl9-contract-model'],
        dependencies=[],expected=(5,772),proof=dict(helper_bytes=58,helper_instructions=18,raw_operand_mutation_rejections=23)),
}


def need(value, message):
    if not value:
        raise RuntimeError(message)


def digest(path):
    with path.open('rb') as stream:
        h=hashlib.sha256()
        for block in iter(lambda:stream.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()


def run(argv, *, cwd=None, env=None, log=None):
    result=subprocess.run([str(x) for x in argv],cwd=cwd,env=env,capture_output=True,
                          text=True,encoding='utf8',errors='replace',timeout=180)
    if log:
        log.write_text(result.stdout+result.stderr,encoding='utf8')
    need(result.returncode==0,'Command failed; inspect '+str(log or argv[0]))
    return result.stdout


def contained(path):
    path=path.resolve()
    need(path.is_relative_to(ROOT.resolve()),'Input must stay within the checkout')
    return path


def first(candidates):
    for relative in candidates:
        path=contained(ROOT/relative)
        if path.is_file():
            return path
    raise RuntimeError('Required local artifact missing: '+str(candidates[0]))


def original_by_hash(expected):
    for relative in ('firmware-downloads/legacy-options-2026-10-20/BINs',
                     'exports/TSL-firmware-options-22-BINs-2026-10-20/BINs'):
        directory=contained(ROOT/relative)
        for path in sorted(directory.glob('*.bin')):
            if digest(path)==expected:
                return path
    raise RuntimeError('Required original BIN missing; SHA-256 '+expected)


@functools.lru_cache(maxsize=1)
def windows_environment():
    environment=dict(os.environ)
    existing=shutil.which('cl.exe')
    if existing:
        return environment,Path(existing)
    installer=Path(os.environ.get('ProgramFiles(x86)','C:/Program Files (x86)'))/'Microsoft Visual Studio/Installer/vswhere.exe'
    need(installer.is_file(),'Install Visual Studio C++ Build Tools or set CC/CXX to a working compiler')
    installation=run([installer,'-latest','-products','*','-requires','Microsoft.VisualStudio.Component.VC.Tools.x86.x64','-property','installationPath']).strip()
    need(installation,'No installed MSVC C++ toolchain')
    batch=Path(installation)/'Common7/Tools/VsDevCmd.bat'
    need(batch.is_file() and not any(c in str(batch) for c in '"%\r\n'),'Valid Visual Studio command environment required')
    # Captured environment stays in memory; never print or serialize its values.
    # cmd.exe parses /c quoting itself; list2cmdline on the inner command would
    # insert backslash-escaped quotes, which cmd does not treat like C argv.
    commandline=subprocess.list2cmdline([os.environ.get('COMSPEC','cmd.exe')])
    commandline+=' /u /d /s /c ""'+str(batch)+'" -arch=x64 -host_arch=x64 >nul && set"'
    result=subprocess.run(commandline,
                          capture_output=True,timeout=60)
    need(result.returncode==0,'Visual Studio command environment failed (exit '+str(result.returncode)+')')
    output=result.stdout.decode('utf-16-le')
    environment={k.upper():v for k,v in environment.items()}
    for line in output.splitlines():
        if '=' in line and not line.startswith('='):
            key,value=line.split('=',1);environment[key.upper()]=value
    compiler=shutil.which('cl.exe',path=environment.get('PATH'))
    need(compiler,'MSVC environment did not expose cl.exe')
    return environment,Path(compiler)


def compiler_for(language):
    override=os.environ.get('CXX' if language=='cpp' else 'CC')
    if override:
        value=shutil.which(override) or (str(Path(override).resolve()) if Path(override).is_file() else None)
        need(value,'CC/CXX must name one installed compiler executable')
        compiler=Path(value);environment=dict(os.environ)
    elif os.name=='nt':
        environment,compiler=windows_environment()
    else:
        names=('c++','clang++','g++') if language=='cpp' else ('cc','clang','gcc')
        found=next((shutil.which(n) for n in names if shutil.which(n)),None)
        need(found,'Install a C11/C++17 compiler (GCC, Clang or MSVC)')
        compiler=Path(found);environment=dict(os.environ)
    return compiler.resolve(),environment,compiler.name.lower() in ('cl','cl.exe')


def source_proof(spec, model, build):
    mapping=json.loads((model/'source-map.json').read_text(encoding='utf8'))
    scope=spec['scope'];proof_dir=first(['analysis/'+scope+'/source/final-audit.json',
                                      'apk-analysis/tsl9-'+scope+'/source/final-audit.json']).parent
    # The older resident scope name already starts tsl9- only in the workspace.
    seal=proof_dir/'final-audit.json'
    need(digest(seal)==mapping['source_seal_sha256'],'Exact sealed source identity required')
    sealed=json.loads(seal.read_text(encoding='utf8'))
    need(sealed.get('passed') and sealed.get('sealed'),'Completed source seal required')
    inputs={seal:digest(seal),model/'source-map.json':digest(model/'source-map.json')}
    for item in sealed['members']:
        path=(proof_dir/item['path']).resolve()
        need(path.is_relative_to(proof_dir.resolve()),'Contained proof member')
        need(path.stat().st_size==item['bytes'] and digest(path)==item['sha256'],'Source proof member changed')
        inputs[path]=item['sha256']
    argv=[sys.executable,'-B',str(proof_dir/'inspect-source.py'),'--check','--source-root',str(proof_dir)]
    if 'carrier_sha256' in mapping:
        carrier=first(['analysis/'+scope+'/reference-carrier/'+CARRIER,
                       'apk-analysis/tsl9-wch-resident-candidate-2026-10-21/carrier-dec2023/'+CARRIER])
        need(digest(carrier)==mapping['carrier_sha256'],'Exact candidate carrier required')
        inputs[carrier]=mapping['carrier_sha256'];argv+=['--carrier',str(carrier)]
    if 'tail_sha256' in mapping:
        tail=first(['analysis/'+scope+'/reference-carrier/'+TAIL,
                    'apk-analysis/tsl9-wch-resident-candidate-2026-10-21/carrier-dec2023/'+TAIL])
        need(digest(tail)==mapping['tail_sha256'],'Exact captured tail required');inputs[tail]=mapping['tail_sha256']
    runtime_hash=mapping.get('runtime_sha256') or mapping.get('bridge_firmware_sha256')
    if runtime_hash:
        firmware=original_by_hash(runtime_hash)
        need(digest(firmware)==runtime_hash,'Exact Runtime identity required');inputs[firmware]=runtime_hash
        if 'carrier_sha256' not in mapping:
            argv+=['--firmware',str(firmware)]
    for key in ('dependency_inputs','reset_inputs','bridge_inputs'):
        for name,value in mapping.get(key,{}).items():
            path=contained(ROOT/name.replace('\\','/'));need(digest(path)==value,'Declared dependency changed: '+name);inputs[path]=value
    output=run(argv,cwd=ROOT,log=build/'source-proof.log')
    result=json.loads(output.strip())
    need(result.get('passed') and all(result.get(k)==v for k,v in spec['proof'].items()),'Complete selected raw source proof required')
    return inputs,result


def verify_model(name, language, tests_only):
    spec=SPECS[name];model=ROOT/'experiments'/spec['folder']
    build=model/'build'/('portable-'+uuid.uuid4().hex+'-'+language);build.mkdir(parents=True)
    sources=[model/n for n in spec['sources']]+[ROOT/'experiments'/n for n in spec['dependencies']]
    includes=[model/'src']+[ROOT/'experiments'/n/'src' for n in spec['includes']]
    owned=set(p for p in sources if p.is_relative_to(model))
    for relative in ('source-map.json','README.md','readme.en.md','readme.zh-TW.md','verify.sh','tests/run-tests.sh'):
        if (model/relative).is_file():owned.add(model/relative)
    inputs={p:digest(p) for p in sources if p not in owned}
    for directory in includes:
        for path in directory.glob('*.h'):
            if path.is_relative_to(model):owned.add(path)
            else:inputs[path]=digest(path)
    proof=None
    if not tests_only:
        proof_inputs,proof=source_proof(spec,model,build);inputs.update(proof_inputs)
    inputs[Path(__file__).resolve()]=digest(Path(__file__).resolve())
    inputs[ROOT/'verify.sh']=digest(ROOT/'verify.sh')
    pins={p.relative_to(model).as_posix():digest(p) for p in owned}
    compiler,environment,msvc=compiler_for(language)
    executable=build/('host-tests.exe' if os.name=='nt' else 'host-tests')
    if msvc:
        flags=['/nologo','/W4','/WX','/Od','/TP' if language=='cpp' else '/TC',
               '/std:c++17' if language=='cpp' else '/std:c11','/Fo'+str(build)+os.sep]
        flags+=['/I'+str(p) for p in includes]
        command=[compiler,*flags,*sources,'/Fe'+str(executable),'/link','/INCREMENTAL:NO']
    else:
        flags=['-x','c++' if language=='cpp' else 'c','-std=c++17' if language=='cpp' else '-std=c11',
               '-O0','-Wall','-Wextra','-Werror','-Wno-misleading-indentation']
        flags += [x for p in includes for x in ('-I',str(p))]
        command=[compiler,*flags,*sources,'-o',executable]
    compiler_before=digest(compiler)
    run(command,cwd=build,env=environment,log=build/'compiler.log')
    raw=run([executable],cwd=build,env=environment,log=build/'test-output.json')
    result=json.loads(raw.strip())
    need(result.get('passed') and (result.get('groups'),result.get('checks'))==spec['expected'],'Complete selected test suite required')
    need(all(digest(model/n)==value for n,value in pins.items()),'Model changed during verification')
    need(all(digest(p)==value for p,value in inputs.items()),'Input changed during verification')
    need(digest(compiler)==compiler_before,'Compiler changed during verification')
    receipt=dict(schema='TSL9-portable-host-verification-v1',passed=True,model=name,mode=language,tests=result,
                 source_sha256=pins,input_sha256={str(p):h for p,h in inputs.items()},original_source=proof,
                 source_proof_checked=not tests_only,executable=str(executable),executable_sha256=digest(executable),
                 compiler=str(compiler),compiler_sha256=compiler_before,compile_flags=flags,
                 platform=dict(system=platform.system(),machine=platform.machine()),
                 original_executed=False,ISA_emulation=False,network=False,hardware=False,native_BIN=False,
                 native_RV32_gate_checked=False,original_ABI_proved=False,OTA_ready=False)
    path=build/'verification.json';path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return dict(passed=True,model=name,mode=language,tests=result,receipt=str(path),source_proof_checked=not tests_only)


def main():
    need(sys.version_info>=(3,10),'Python 3.10+ is required')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model',choices=['all',*SPECS],default='all')
    parser.add_argument('--language',choices=['c','cpp','both'],default='both')
    parser.add_argument('--tests-only',action='store_true',help='Explicitly skip raw proof; receipt is labelled accordingly')
    parser.add_argument('--list',action='store_true')
    args=parser.parse_args()
    if args.list:
        print(json.dumps({'models':list(SPECS),'scope':'selected raw proofs and host tests; historical native/ELF suites require separate migration'}));return
    names=list(SPECS) if args.model=='all' else [args.model]
    languages=['c','cpp'] if args.language=='both' else [args.language]
    results=[]
    for name in names:
        for language in languages:
            print('Verifying '+name+' / '+language,file=sys.stderr,flush=True)
            value=verify_model(name,language,args.tests_only);results.append(value)
            print('VERIFICATION_RESULT '+json.dumps(value),flush=True)
    print(json.dumps({'passed':True,'results':results,'original_executed':False,'hardware':False,'OTA_ready':False}))


if __name__=='__main__':
    try:main()
    except (RuntimeError,OSError,subprocess.SubprocessError,json.JSONDecodeError) as error:
        print('Verification failed: '+str(error),file=sys.stderr);sys.exit(1)
