#!/usr/bin/env python3
"""Portable entry to the single formal source-wiring producer/replay CLI."""
from pathlib import Path
import runpy
import sys
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[2]
target=next(p for p in (root/'analysis/v4160-ota-source-wiring-2026-10-22/implementation/verify_image.py',root/'apk-analysis/tsl9-v4160-ota-source-wiring-2026-10-22/implementation/verify_image.py') if p.is_file())
runpy.run_path(str(target),run_name='__main__')
