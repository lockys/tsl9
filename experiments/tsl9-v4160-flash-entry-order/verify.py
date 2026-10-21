"""Default entry point: synthetic HOST verification, never RV32 execution."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).resolve().with_name('verify_host.py')),run_name='__main__')
