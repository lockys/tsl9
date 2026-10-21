"""Project-local portable entry for the actual source-image compiler/replay."""
import argparse,runpy,sys
from pathlib import Path
p=argparse.ArgumentParser(add_help=False);p.add_argument('--project-root',type=Path,default=Path(__file__).resolve().parents[2]);a,rest=p.parse_known_args();root=a.project_root.resolve();slug='v4160-flash-image-integration-2026-10-22'
entry=next(p for p in (root/'analysis'/slug/'implementation/verify_image.py',root/'apk-analysis'/('tsl9-'+slug)/'implementation/verify_image.py') if p.is_file());sys.argv=[str(entry),'--project-root',str(root),*rest];runpy.run_path(str(entry),run_name='__main__')
