#!/usr/bin/env python3
"""Only link two existing formal objects; never compile or execute target code."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('project-root','llvm-bin','dispatch-root','peripheral-root','build-root'):
        p.add_argument('--'+name,required=True,type=Path)
    a = p.parse_args()
    spec = importlib.util.spec_from_file_location('peripheral_dispatch_component_checker',HERE/'check.py')
    c = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(c)
    root,llvm,out = a.project_root.resolve(),a.llvm_bin.resolve(),a.build_root.resolve()
    c.need(root/c.MODEL == HERE, 'Exact portable owned experiment')
    c.need(out.is_relative_to(HERE/'build') and out != HERE/'build' and not out.exists(), 'Create-only fresh output directory')
    c.metadata(root)
    before = c.inputs(root,llvm)
    sources = {}
    for mode in ('c','cpp'):
        left,right = a.dispatch_root.resolve()/mode,a.peripheral_root.resolve()/mode
        sources[mode] = (left,right)
        c.upstream(root,llvm,left,right,mode)
    out.mkdir(parents=True)
    receipts = []
    for mode in ('c','cpp'):
        folder = out/mode
        folder.mkdir()
        left,right = sources[mode]
        commands = []
        for label,argv in c.recipes(llvm,folder,left,right):
            run = subprocess.run([str(x) for x in argv],cwd=root,capture_output=True,timeout=120)
            log = folder/(label+'.log')
            log.write_bytes(run.stdout+run.stderr)
            commands.append(dict(label=label,argv=c.portable([str(x) for x in argv],root,llvm),exit=run.returncode,log_sha256=c.sha(log)))
            c.need(run.returncode == 0, 'Retained '+label+' failure; no retry or recipe change')
        c.need(before == c.inputs(root,llvm), 'All source/tool/resource inputs stable through link')
        value = dict(schema=c.BUILD_SCHEMA,mode=mode,inputs=before,dispatch_folder=c.portable(str(left),root,llvm),
                     peripheral_folder=c.portable(str(right),root,llvm),commands=commands,
                     artifacts={p.name:c.sha(p) for p in sorted(folder.iterdir()) if p.is_file()})
        c.write_new(folder/'link-receipt.json',value)
        reviewed = c.inspect(root,llvm,folder)
        c.write_new(folder/'verification.json',reviewed)
        c.replay(root,llvm,folder/'verification.json')
        receipts.append(dict(mode=mode,path=c.portable(str(folder/'verification.json'),root,llvm),sha256=c.sha(folder/'verification.json')))
    print(json.dumps(dict(passed=True,receipts=receipts,new_compilation=False,firmware_ready=False)))


if __name__ == '__main__':
    main()
