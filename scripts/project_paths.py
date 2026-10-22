#!/usr/bin/env python3
"""Resolve local paths without storing a developer's account or machine layout."""
import argparse
import os
from pathlib import Path
import shutil
import sys


def project_root():
    return Path(__file__).resolve().parent.parent


def configured_path(name):
    value = os.environ.get(name)
    return Path(value).expanduser().resolve() if value else None


def executable_name(name):
    return name + ('.exe' if os.name == 'nt' else '')


def llvm_bin():
    explicit = configured_path('TSL9_LLVM_BIN')
    if explicit:
        candidates = [explicit]
    else:
        ndk = configured_path('ANDROID_NDK_HOME') or configured_path('ANDROID_NDK_ROOT')
        candidates = sorted((ndk/'toolchains/llvm/prebuilt').glob('*/bin')) if ndk else []
        if not ndk:
            clang = shutil.which('clang')
            candidates = [Path(clang).resolve().parent] if clang else []
    required = [executable_name(n) for n in ('clang','ld.lld','llvm-objdump')]
    valid = [p.resolve() for p in candidates if all((p/n).is_file() for n in required)]
    if len(valid) != 1:
        raise ValueError('Set TSL9_LLVM_BIN to one existing LLVM bin directory containing clang, ld.lld and llvm-objdump; no tools are downloaded.')
    return valid[0]


def radare2():
    explicit = configured_path('TSL9_R2')
    found = explicit or (Path(shutil.which('r2')) if shutil.which('r2') else None)
    if not found or not found.is_file():
        raise ValueError('Set TSL9_R2 to an existing r2 executable or add r2 to PATH.')
    return found.resolve()


def analysis_workspace():
    result = configured_path('TSL9_ANALYSIS_WORKSPACE')
    if not result or not result.is_dir():
        raise ValueError('This historical review requires TSL9_ANALYSIS_WORKSPACE pointing to the retained analysis workspace.')
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--select',required=True,choices=['project-root','llvm-bin','radare2','analysis-workspace','python'])
    a = p.parse_args()
    actions = {'project-root':project_root,'llvm-bin':llvm_bin,'radare2':radare2,
               'analysis-workspace':analysis_workspace,'python':lambda:Path(sys.executable).resolve()}
    print(actions[a.select]())


if __name__=='__main__':
    main()
