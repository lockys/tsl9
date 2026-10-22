#!/usr/bin/env python3
"""Compiler-only entry; never execute the MMIO adapter."""
from pathlib import Path
import runpy
import sys
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[2]
case='v4160-resident-native-2026-10-22/implementation/probe.py'
runner=next(p for p in(root/'analysis'/case,root/'apk-analysis'/('tsl9-'+case)) if p.is_file())
if '--project-root' not in sys.argv:sys.argv.extend(['--project-root',str(root)])
runpy.run_path(str(runner),run_name='__main__')
