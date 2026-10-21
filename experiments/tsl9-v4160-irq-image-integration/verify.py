"""Portable model entry point for the independent source-image verifier."""
from pathlib import Path
import runpy
ROOT=Path(__file__).resolve().parents[2]
for target in (ROOT/'apk-analysis/tsl9-v4160-irq-image-integration-2026-10-21/integration/verify_image.py',
               ROOT/'analysis/v4160-irq-image-integration-2026-10-21/integration/verify_image.py'):
    if target.is_file():
        runpy.run_path(str(target),run_name='__main__')
        break
else:
    raise SystemExit('Missing published/local source-image verifier')
