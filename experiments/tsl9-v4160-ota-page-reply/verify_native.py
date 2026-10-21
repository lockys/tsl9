#!/usr/bin/env python3
"""Portable source-only entry for the independently scoped native verifier."""
import runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[2]
for rel in ('analysis/v4160-ota-page-reply-2026-10-22/implementation/verify_native.py','apk-analysis/tsl9-v4160-ota-page-reply-2026-10-22/implementation/verify_native.py'):
 p=root/rel
 if p.is_file():runpy.run_path(str(p),run_name='__main__');break
else:raise SystemExit('Missing published native verifier')
