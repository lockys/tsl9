"""Pinned, local reference candidates; neither establishes installed identity."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PROFILES={
    'v131':dict(path='analysis/wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin',
        size=191078,sha256='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22',
        cfg=(0x4b456,0x4b2e4,0x200033b5,0x4354a,0x2000319d,0x200031e4)),
    'v140':dict(path='analysis/wch-resident-candidate-2026-10-21/carrier/REFERENCE-CANDIDATE-ONLY-00040000-0006EC56.bin',
        size=191574,sha256='b02cf8ec6829425a558887bd6bc10d28ae1f0e2e9e1850333f0bab6088e9e941',
        cfg=(0x4b4ee,0x4b37c,0x20003405,0x435d6,0x200031ed,0x20003234))}
