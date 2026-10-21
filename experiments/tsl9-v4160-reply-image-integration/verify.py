#!/usr/bin/env python3
"""Fresh offline source compilation plus two explicit ABI ordering stages."""
from pathlib import Path
import runpy,sys
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[2]
relative='v4160-reply-image-integration-2026-10-22/implementation/verify_image.py'
target=next(p for p in (root/'analysis'/relative,root/'apk-analysis'/('tsl9-'+relative)) if p.is_file())
runpy.run_path(str(target),run_name='__main__')
