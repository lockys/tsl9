#!/usr/bin/env python3
"""Portable entry to fresh offline source integration or actual receipt replay."""
from pathlib import Path
import runpy,sys
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[2]
relative='v4160-tx-image-integration-2026-10-22/implementation/verify_image.py'
entry=next(p for p in(root/'analysis'/relative,root/'apk-analysis'/('tsl9-'+relative)) if p.is_file())
runpy.run_path(str(entry),run_name='__main__')
