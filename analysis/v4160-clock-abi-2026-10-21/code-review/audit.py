#!/usr/bin/env python3
"""Independent compiled hosted checks of normal-return register residues."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import uuid

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
MODEL=ROOT/'experiments/tsl9-v4160-clock-registers'
HELPER=ROOT/'scripts/portable_verify.py'
OLD_FIXTURE=ROOT/'apk-analysis/tsl9-v4160-native-clock-2026-10-21/code-review'
OLD_MODEL=ROOT/'experiments/tsl9-v4160-native-clock'
SEALS=(
    ('apk-analysis/tsl9-v4160-system-clock-query-2026-10-21/source/final-audit.json','ebf0521f52c5142d1dc7969aaca17bb1c7567065165eba4c88fd4523e30b6a51'),
    ('apk-analysis/tsl9-v4160-native-clock-2026-10-21/code-review/final-audit.json','ed38147f37a9420b27124cf591a45ff45b54d58861a4d5d733ff11e8288f9dc7'),
    ('apk-analysis/tsl9-v4160-clock-abi-2026-10-21/caller-review/final-audit.json','46cbea5e11efd4c7eb383502e86c7d545bfd7c4f918caba26c9b84cf64477208'),
)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def need(okay,message):
    if not okay:raise RuntimeError(message)

def source_evidence():
    paths=[]
    for relative,digest in SEALS:
        p=ROOT/relative;need(sha(p)==digest,'Immutable previous source/review seal');seal=json.loads(p.read_text())
        need(seal['passed'],'Prior sealed evidence passed');paths.append(p)
        for member in seal['members']:
            q=p.parent/member['path'];need(q.stat().st_size==member['bytes'] and sha(q)==member['sha256'],'Prior sealed member');paths.append(q)
    original=ROOT/'exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
    need(original.stat().st_size==76800 and sha(original)=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','Exact source runtime')
    return paths+[original]

def variants(query,fields):
    fallback='base=(residue_a3&UINT32_C(0x80000000))!=0u\n                    ?UINT32_C(4000000):UINT32_C(8000000);'
    results={
        'original':(query,fields),
        'wrong-default-a3':(query.replace('residue_a3=4u;','residue_a3=0u;').replace('residue_a3=8u;','residue_a3=0u;'),fields),
        'wrong-internal-a3':(query.replace('residue_a3=17u;','residue_a3=18u;'),fields),
        'wrong-external-a3':(query.replace('residue_a3=UINT32_C(0x40021000);','residue_a3=UINT32_C(0x40021004);'),fields),
        'wrong-fallback-a3':(query.replace(fallback,fallback+'\n                residue_a3=fallback_sample<<13;'),fields),
        'unconditional-a2':(query.replace('const uint32_t rcc=UINT32_C(0x40021004);','(void)CA_EXTERNAL_MASK();\n    const uint32_t rcc=UINT32_C(0x40021004);'),fields),
        'masked-query-a4':(query.replace('CA_QUERY_OUTPUTS(residue_a3,(uint32_t)shift,result);','CA_QUERY_OUTPUTS(residue_a3,(uint32_t)(shift&31u),result);'),fields),
        'swapped-field-outputs':(query,fields.replace('CA_FIELD_OUTPUTS(factor,product);','CA_FIELD_OUTPUTS(product,factor);')),
        'truncated-field-a5':(query,fields.replace('CA_FIELD_OUTPUTS(factor,product);','CA_FIELD_OUTPUTS(factor,(uint16_t)product);')),
    }
    need(len(set(results.values()))==9,'Eight distinct source mutations actually applied')
    return results

def run(mode):
    originals=source_evidence()
    spec=importlib.util.spec_from_file_location('clock_register_review_tools',HELPER)
    tool=importlib.util.module_from_spec(spec);spec.loader.exec_module(tool)
    compiler,environment,msvc=tool.compiler_for(mode)
    build=HERE/'build'/('independent-'+uuid.uuid4().hex+'-'+mode);build.mkdir(parents=True)
    products=sorted((MODEL/'src').glob('*.[ch]'));need(len(products)==4,'Frozen four product source/header files')
    paths=products+[HELPER,HERE/'audit.py',HERE/'test_independent.c',HERE/'register_test_io.h',
        OLD_FIXTURE/'test_independent.c',OLD_FIXTURE/'test_io.h',OLD_MODEL/'src/native_clock.h']+originals
    pins={p:sha(p) for p in paths};compiler_sha=sha(Path(compiler));results=[]
    query=(MODEL/'src/clock_query.c').read_text(encoding='utf-8');fields=(MODEL/'src/clock_fields.c').read_text(encoding='utf-8')
    for name,(q,f) in variants(query,fields).items():
        folder=build/name;folder.mkdir()
        (folder/'clock_query.c').write_text(q,encoding='utf-8');(folder/'clock_fields.c').write_text(f,encoding='utf-8')
        for header in ('clock_io.h','clock_registers.h'):(folder/header).write_bytes((MODEL/'src'/header).read_bytes())
        exe=folder/('test.exe' if os.name=='nt' else 'test');includes=[folder,HERE,OLD_MODEL/'src']
        sources=[folder/'clock_query.c',folder/'clock_fields.c',HERE/'test_independent.c']
        if msvc:
            flags=['/nologo','/W4','/WX','/Od','/TP' if mode=='cpp' else '/TC','/std:c++17' if mode=='cpp' else '/std:c11','/DTSL9_CLOCK_REGISTER_HOST_TEST=1','/Fo'+str(folder)+os.sep]+['/I'+str(p) for p in includes]
            command=[compiler,*flags,*sources,'/Fe'+str(exe),'/link','/INCREMENTAL:NO']
        else:
            flags=['-x','c++' if mode=='cpp' else 'c','-std=c++17' if mode=='cpp' else '-std=c11','-O0','-Wall','-Wextra','-Werror','-DTSL9_CLOCK_REGISTER_HOST_TEST=1']+[value for p in includes for value in ('-I',str(p))]
            command=[compiler,*flags,*sources,'-o',exe]
        tool.run(command,cwd=folder,env=environment,log=folder/'compiler.log')
        need(exe.is_file(),'Actual hosted executable compiled')
        process=subprocess.run([str(exe)],cwd=folder,env=environment,capture_output=True,text=True,timeout=30)
        (folder/'stdout.txt').write_text(process.stdout,encoding='utf-8');(folder/'stderr.txt').write_text(process.stderr,encoding='utf-8')
        if name=='original':
            need(process.returncode==0,'Reconstruction passes independent memory/register suite')
            tests=json.loads(process.stdout)
            need(tests['passed'] and tests['groups']==4 and tests['cases']==5345 and tests['checks']>214811,'Complete independent scope plus new register assertions')
        else:
            need(process.returncode==17 and process.stderr.startswith('REVIEW_FAIL '),'Compiled source mutant rejected by actual runtime assertion')
            tests=dict(rejected=True,failure=process.stderr.strip())
        results.append(dict(variant=name,compiled=True,exit_code=process.returncode,tests=tests,
            source_sha256={p.name:sha(p) for p in sources[:2]+[folder/'clock_io.h',folder/'clock_registers.h']},
            executable_sha256=sha(exe),compile_flags=flags,compiler_log_sha256=sha(folder/'compiler.log')))
    need(all(sha(p)==h for p,h in pins.items()),'All actual compilation and evidence inputs unchanged')
    need(sha(Path(compiler))==compiler_sha,'Compiler unchanged')
    receipt=dict(schema='TSL9-clock-register-residues-independent-host-review-v1',passed=True,mode=mode,
        source_sha256={str(p.relative_to(ROOT)):h for p,h in pins.items()},compiler=str(compiler),compiler_sha256=compiler_sha,
        variants=results,original_source_bytes=214,original_source_instructions=69,original_raw_mutations_rejected=50,
        caller_a3_obligation_checked=True,original_executed=False,ISA_emulation=False,physical_IO=False,
        actual_native_register_commitments_proved=False,original_ABI_proved=False,OTA_ready=False)
    p=build/'verification.json';p.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    return dict(passed=True,mode=mode,tests=results[0]['tests'],compiled_negatives=8,receipt=str(p.relative_to(ROOT)),sha256=sha(p))

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--language',choices=['c','cpp','both'],default='both');args=parser.parse_args();results=[]
    for mode in (['c','cpp'] if args.language=='both' else [args.language]):
        result=run(mode);results.append(result);print('CLOCK_REGISTERS_REVIEW_RESULT '+json.dumps(result),flush=True)
    print(json.dumps(dict(passed=True,results=results,OTA_ready=False)))

if __name__=='__main__':main()
