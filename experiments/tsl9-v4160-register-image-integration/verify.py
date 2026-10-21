"""Fresh offline compiler/linker plus explicit ABI scheduling; never RV32 execution."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[2]
relative='v4160-register-image-integration-2026-10-22/implementation/verify_image.py'
target=next(p for p in (root/'analysis'/relative,root/'apk-analysis'/('tsl9-'+relative)) if p.is_file())
runpy.run_path(str(target),run_name='__main__')
