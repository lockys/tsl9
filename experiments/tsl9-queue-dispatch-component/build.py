#!/usr/bin/env python3
"""One offline adapter compilation and genuine partial link per language."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent


def checker():
    spec = importlib.util.spec_from_file_location('dispatch_checker', HERE/'check.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', required=True, type=Path)
    p.add_argument('--llvm-bin', required=True, type=Path)
    p.add_argument('--queue-root', required=True, type=Path)
    p.add_argument('--filter-root', required=True, type=Path)
    p.add_argument('--build-root', required=True, type=Path)
    a = p.parse_args()
    c = checker()
    root, llvm, out = a.project_root.resolve(), a.llvm_bin.resolve(), a.build_root.resolve()
    c.need(HERE == root/c.MODEL, 'Owned canonical or portable project root')
    c.need(out.is_relative_to(HERE/'build') and out != HERE/'build' and not out.exists(), 'Fresh owned output only')
    frozen = c.inputs(root, llvm)
    folders = {}
    for mode in ('c', 'cpp'):
        q, f = a.queue_root.resolve()/mode, a.filter_root.resolve()/mode
        c.upstream(root, llvm, q, f, mode)
        folders[mode] = (q, f)
    out.mkdir(parents=True)
    records = []
    for mode in ('c', 'cpp'):
        q, f = folders[mode]
        folder = out/mode
        folder.mkdir()
        commands = []
        for label, argv in c.recipes(root, llvm, folder, mode, q, f):
            run = subprocess.run([str(x) for x in argv], cwd=root, capture_output=True, timeout=120)
            log = folder/(label+'.log')
            log.write_bytes(run.stdout+run.stderr)
            commands.append(dict(label=label, argv=c.portable([str(x) for x in argv], root, llvm),
                                 exit=run.returncode, log_sha256=c.sha(log)))
            c.need(run.returncode == 0, 'Retained '+label+' failure; no retry or profile change')
        c.need(frozen == c.inputs(root, llvm), 'Stable authored, upstream, compiler and resource inputs')
        record = dict(schema=c.BUILD_SCHEMA, mode=mode, inputs=frozen,
                      queue_folder=c.portable(str(q), root, llvm), filter_folder=c.portable(str(f), root, llvm),
                      commands=commands, artifacts={x.name:c.sha(x) for x in sorted(folder.iterdir()) if x.is_file()})
        c.write_new(folder/'compile-receipt.json', record)
        checked = c.inspect(root, llvm, folder)
        c.write_new(folder/'verification.json', checked)
        c.replay(root, llvm, folder/'verification.json')
        records.append(dict(mode=mode, path=c.portable(str(folder/'verification.json'), root, llvm),
                            sha256=c.sha(folder/'verification.json'), result=checked['result']))
    print(json.dumps(dict(passed=True, receipts=records, firmware_ready=False)))


if __name__ == '__main__':
    main()
