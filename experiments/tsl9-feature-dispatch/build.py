#!/usr/bin/env python3
"""Compile IR and partially link real C objects; no execution or firmware BIN."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
S = json.loads((HERE/'spec.json').read_bytes())


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def encoded(value):
    return (json.dumps(value,indent=2,sort_keys=True,ensure_ascii=True)+'\n').encode()


def portable(value,llvm):
    pairs = [(llvm.parent/'lib/clang/18','$'+'{CLANG_RESOURCE}'),(llvm,'$'+'{LLVM_BIN}'),(ROOT,'$'+'{PROJECT_ROOT}')]
    if isinstance(value,str):
        for p,t in pairs:
            for form in (str(p),p.as_posix()):
                value = value.replace(form,t)
        return value
    if isinstance(value,list):
        return [portable(x,llvm) for x in value]
    if isinstance(value,dict):
        return {portable(k,llvm):portable(v,llvm) for k,v in value.items()}
    return value


def parent(mode):
    return ROOT/'experiments/tsl9-channel-route/build/graph-v1'/mode/'UNRESOLVED-CHANNEL-GRAPH.o'


def obj(unit,mode):
    return ROOT/S['curation_root']/unit['name']/mode/'curated/unit.o'


def inputs(llvm,mode):
    paths = [HERE/n for n in ('spec.json','build.py','component.ld','joined.ld','describe.py')]
    paths += [ROOT/S[k] for k in ('firmware','reader','original_reader','curation_checker','parent_checker')]
    paths += [parent(mode),parent(mode).parent/'measurement.json',parent(mode).parent/'verification-v2.json',
              ROOT/S['curation_root']/'verification.json',ROOT/S['previous_curation_root']/'verification.json',
              ROOT/'src/source-manifest.json',llvm.parent/'lib/clang/18/include/stdint.h']
    for u in S['units']:
        paths += [ROOT/u['curated_unit'],ROOT/u['origin_unit'],obj(u,mode),
                  obj(u,mode).parent/'unit.d',obj(u,mode).parent/'compile.log']
    paths += [llvm/n for n in S['tools']]
    return {str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(set(paths))}


def recipes(llvm,folder,mode):
    C = runpy.run_path(str(ROOT/S['curation_checker']))
    out = []
    for u in S['units']:
        out.append(('IR-'+u['name'],[str(llvm/'clang.exe')]+C['flags'](u,mode)+[
            '-S','-emit-llvm',str(ROOT/u['curated_unit']),'-o',str(folder/(u['name']+'.ll'))]))
    objects = [str(obj(u,mode)) for u in S['units']]
    out += [
        ('component-link',[str(llvm/'ld.lld.exe'),'-r','--no-relax','-T',str(HERE/'component.ld')]+objects+
         ['-o',str(folder/'UNRESOLVED-ORIGINAL-ADDRESS-DISPATCH.o')]),
        ('component-read',[str(llvm/'llvm-objdump.exe'),'-dr','-t','-h',str(folder/'UNRESOLVED-ORIGINAL-ADDRESS-DISPATCH.o')]),
        ('joined-link',[str(llvm/'ld.lld.exe'),'-r','--no-relax','-T',str(HERE/'joined.ld'),str(parent(mode))]+objects+
         ['-o',str(folder/'UNRESOLVED-FEATURE-GRAPH.o')]),
        ('joined-read',[str(llvm/'llvm-objdump.exe'),'-dr','-t','-h',str(folder/'UNRESOLVED-FEATURE-GRAPH.o')])]
    return out


def build(llvm,output):
    need(not output.exists() and output.is_relative_to(HERE/'build'),'Create-only local output')
    for k in ('firmware','reader','original_reader','curation_checker','parent_checker'):
        need(sha(ROOT/S[k]) == S[k+'_sha256'],'Pinned '+k)
    for n,pin in S['tools'].items():
        need(sha(llvm/n) == pin,'Pinned local tool '+n)
    need(sha(llvm.parent/'lib/clang/18/include/stdint.h') == S['stdint_sha256'],'Pinned compiler header')
    need(sha(ROOT/S['curation_root']/'verification.json') == S['curation_receipt_sha256'],'Actual96-comparison source receipt')
    for mode in ('c','cpp'):
        need(sha(parent(mode)) == S['parent_object_sha256'],'Actual genuine3166B parent')
        for u in S['units']:
            need(sha(obj(u,mode)) == u['native_object_sha256'][mode],'Actual curated source object')
        folder = output/mode
        folder.mkdir(parents=True)
        before = inputs(llvm,mode)
        commands = []
        for label,argv in recipes(llvm,folder,mode):
            p = subprocess.run(argv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            (folder/(label+'.log')).write_bytes(p.stdout)
            commands.append(dict(label=label,argv=argv,exit=p.returncode,log_sha256=hashlib.sha256(p.stdout).hexdigest()))
            need(p.returncode == 0,'Actual command failed '+label+'; retained log')
        need(before == inputs(llvm,mode),'Actual inputs unchanged during production')
        report = dict(schema='TSL9-feature-dispatch-build-v1',mode=mode,inputs=before,commands=commands,
                      artifacts={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(folder.iterdir()) if p.is_file()},
                      target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,
                      network=False,firmware_BIN_generated=False,firmware_ready=False)
        (folder/'measurement.json').write_bytes(encoded(portable(report,llvm)))
    print(json.dumps(dict(built=True,modes=['c','cpp'],commands_per_language=7,firmware_ready=False)))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tool-dir',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a = p.parse_args()
    build(a.tool_dir.resolve(),a.output.resolve())
