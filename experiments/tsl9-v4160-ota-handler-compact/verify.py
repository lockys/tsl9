#!/usr/bin/env python3
"""Portable default synthetic HOST entry. Native compilation is a separate CLI."""
from pathlib import Path
import runpy
import sys
sys.dont_write_bytecode = True
runpy.run_path(str(Path(__file__).with_name('verify_host.py')), run_name='__main__')
