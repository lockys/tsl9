#!/usr/bin/env python3
"""Portable entry to the scoped native compiler/static verifier."""
from pathlib import Path
import runpy
import sys

sys.dont_write_bytecode = True
root = Path(__file__).resolve().parents[2]
if '--project-root' in sys.argv:
    root = Path(sys.argv[sys.argv.index('--project-root') + 1]).resolve()
else:
    sys.argv += ['--project-root', str(root)]
runner = next(p for p in (
    root / 'analysis/v4160-callback-registers-2026-10-22/implementation/verify_native.py',
    root / 'apk-analysis/tsl9-v4160-callback-registers-2026-10-22/implementation/verify_native.py'
) if p.is_file())
runpy.run_path(str(runner), run_name='__main__')
