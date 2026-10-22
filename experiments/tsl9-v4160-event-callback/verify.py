#!/usr/bin/env python3
"""Portable HOST default, explicit native diagnostic, or readonly replay."""
import argparse,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(add_help=False);p.add_argument('--kind',choices=['host','native'],default='host');a,rest=p.parse_known_args()
if '--project-root' not in rest:rest=['--project-root',str(root),*rest]
if a.kind=='host':entry=Path(__file__).with_name('verify_host.py')
else:
    rel='v4160-event-callback-2026-10-22/implementation/verify_native.py';entry=next(p for p in(root/'analysis'/rel,root/'apk-analysis'/('tsl9-'+rel)) if p.is_file())
sys.argv=[str(entry),*rest];runpy.run_path(str(entry),run_name='__main__')
