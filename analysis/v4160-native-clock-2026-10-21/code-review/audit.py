#!/usr/bin/env python3
"""Compile only our readable clock C and independent fake-memory harness."""
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
MODEL=ROOT/'experiments/tsl9-v4160-native-clock'
HELPER=ROOT/'scripts/portable_verify.py'
SOURCE=ROOT/'apk-analysis/tsl9-v4160-system-clock-query-2026-10-21/source'
SEAL_SHA256='ebf0521f52c5142d1dc7969aaca17bb1c7567065165eba4c88fd4523e30b6a51'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def need(okay,message):
    if not okay:raise RuntimeError(message)

def source_evidence():
    p=SOURCE/'final-audit.json';need(sha(p)==SEAL_SHA256,'Prior original source seal')
    seal=json.loads(p.read_text())
    need(seal['passed'] and seal['source_bytes']==214 and seal['source_instructions']==69
         and seal['raw_operand_mutations_rejected']==50,'Exact original source scope')
    files=[p]
    for member in seal['members']:
        q=SOURCE/member['path'];need(q.stat().st_size==member['bytes'] and sha(q)==member['sha256'],'Prior sealed source member');files.append(q)
    original=ROOT/'exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
    need(original.stat().st_size==76800 and sha(original)=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','Original runtime identity')
    files.append(original);return files

def variants(original):
    frozen=original.replace('write32(current_gp() + 108u, frequency);','const uint32_t fixed_gp = current_gp();\n    write32(fixed_gp + 108u, frequency);')
    start=frozen.index('void tsl9_rebuild_clock_query_18834(void)')
    end=frozen.index('void tsl9_rebuild_clock_fields_1973c(void)')
    section=frozen[start:end].replace('current_gp() + 64u + index','fixed_gp + 64u + index').replace('current_gp() + 108u','fixed_gp + 108u')
    frozen=frozen[:start]+section+frozen[end:]
    result={
        'original':original,
        'cached-pll-source':original.replace('const uint32_t source_sample = read32(rcc);','const uint32_t source_sample = multiplier_sample;'),
        'cached-scalar':original.replace('const uint32_t live_frequency = read32(current_gp() + 108u);','const uint32_t live_frequency = frequency;'),
        'frozen-gp':frozen,
        'clamped-shift':original.replace('live_frequency >> (shift & 31u)','live_frequency >> (shift > 31u ? 31u : shift)'),
        'untruncated-quotient':original.replace('const uint32_t quotient = (frequency / UINT32_C(8000000)) & 255u;','const uint32_t quotient = frequency / UINT32_C(8000000);'),
    }
    need(len(set(result.values()))==6,'All five source mutations change actual C distinctly')
    return result

def run(mode):
    original_files=source_evidence()
    spec=importlib.util.spec_from_file_location('native_clock_review_tools',HELPER)
    tool=importlib.util.module_from_spec(spec);spec.loader.exec_module(tool)
    compiler,environment,msvc=tool.compiler_for(mode)
    build=HERE/'build'/('independent-'+uuid.uuid4().hex+'-'+mode);build.mkdir(parents=True)
    source=MODEL/'src/native_clock.c'
    paths=[source,MODEL/'src/native_clock.h',HELPER,HERE/'audit.py',HERE/'test_io.h',HERE/'test_independent.c']+original_files
    inputs={p:sha(p) for p in paths};compiler_sha=sha(Path(compiler));results=[]
    for name,contents in variants(source.read_text(encoding='utf-8')).items():
        folder=build/name;folder.mkdir();candidate=folder/'native_clock.c';candidate.write_text(contents,encoding='utf-8')
        exe=folder/('test.exe' if os.name=='nt' else 'test');includes=[MODEL/'src',HERE]
        if msvc:
            flags=['/nologo','/W4','/WX','/Od','/TP' if mode=='cpp' else '/TC','/std:c++17' if mode=='cpp' else '/std:c11','/DTSL9_CLOCK_HOST_TEST=1','/Fo'+str(folder)+os.sep]+['/I'+str(p) for p in includes]
            command=[compiler,*flags,candidate,HERE/'test_independent.c','/Fe'+str(exe),'/link','/INCREMENTAL:NO']
        else:
            flags=['-x','c++' if mode=='cpp' else 'c','-std=c++17' if mode=='cpp' else '-std=c11','-O0','-Wall','-Wextra','-Werror','-DTSL9_CLOCK_HOST_TEST=1']+[item for p in includes for item in ('-I',str(p))]
            command=[compiler,*flags,candidate,HERE/'test_independent.c','-o',exe]
        tool.run(command,cwd=folder,env=environment,log=folder/'compiler.log')
        need(exe.is_file(),'Actual native-host executable compiled')
        process=subprocess.run([str(exe)],cwd=folder,env=environment,capture_output=True,text=True,timeout=30)
        (folder/'stdout.txt').write_text(process.stdout,encoding='utf-8');(folder/'stderr.txt').write_text(process.stderr,encoding='utf-8')
        if name=='original':
            need(process.returncode==0,'Original reconstructed C passes independent tests')
            tests=json.loads(process.stdout)
            need(tests['passed'] and tests['groups']==4 and tests['cases']==5345 and tests['checks']>100000,'Complete original independent test scope')
        else:
            need(process.returncode==17 and process.stderr.startswith('REVIEW_FAIL '),'Compiled mutant rejected by actual runtime assertion')
            tests={'rejected':True,'failure':process.stderr.strip()}
        results.append(dict(variant=name,compiled=True,exit_code=process.returncode,tests=tests,
            source_sha256=sha(candidate),executable_sha256=sha(exe),compile_flags=flags,
            compiler_log_sha256=sha(folder/'compiler.log')))
    need(all(sha(p)==expected for p,expected in inputs.items()),'All compiled/source-proof inputs immutable during run')
    need(sha(Path(compiler))==compiler_sha,'Compiler unchanged during run')
    receipt=dict(schema='TSL9-native-clock-independent-host-review-v1',passed=True,mode=mode,
        source_sha256={str(p.relative_to(ROOT)):h for p,h in inputs.items()},compiler=str(compiler),compiler_sha256=compiler_sha,
        variants=results,original_source_bytes=214,original_source_instructions=69,original_raw_mutations_rejected=50,
        original_executed=False,ISA_emulation=False,physical_IO=False,original_ABI_proved=False,OTA_ready=False)
    out=build/'verification.json';out.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    return dict(mode=mode,passed=True,tests=results[0]['tests'],compiled_negatives=5,
        receipt=str(out.relative_to(ROOT)),sha256=sha(out))

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--language',choices=['c','cpp','both'],default='both');args=parser.parse_args()
    results=[]
    for mode in (['c','cpp'] if args.language=='both' else [args.language]):
        item=run(mode);results.append(item);print('NATIVE_CLOCK_REVIEW_RESULT '+json.dumps(item),flush=True)
    print(json.dumps(dict(passed=True,results=results,OTA_ready=False)))

if __name__=='__main__':main()
