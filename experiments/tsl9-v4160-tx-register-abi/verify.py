#!/usr/bin/env python3
import runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[2]
script=next(p for p in(root/'analysis/v4160-tx-register-abi-2026-10-22/implementation/verify_native.py',root/'apk-analysis/tsl9-v4160-tx-register-abi-2026-10-22/implementation/verify_native.py') if p.is_file())
if '--project-root' not in sys.argv:sys.argv.extend(['--project-root',str(root)])
runpy.run_path(str(script),run_name='__main__')
