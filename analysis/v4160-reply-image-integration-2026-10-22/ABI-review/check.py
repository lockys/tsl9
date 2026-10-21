#!/usr/bin/env python3
"""Metadata-only default. Never read firmware, compiled objects or tools."""
import argparse,json,runpy
from pathlib import Path
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path);p.parse_args();api=runpy.run_path(str(Path(__file__).with_name('review.py')));print(json.dumps(api['metadata']()))
if __name__=='__main__':main()
