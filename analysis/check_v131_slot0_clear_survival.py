"""Observe slot writes in the existing optional-role trace. Args: APP, V1.31, rasm2.
Counts only the interpreter's ordinary CPU stores. No continuity to dispatch is assumed.
"""
from pathlib import Path
import runpy
import sys

source = Path(__file__).with_name('check_v131_outer_count_rf.py').resolve()
slot = 0x200034e0
runs = []


def observe(frame, event, arg):
    code = frame.f_code
    if code.co_filename != str(source):
        return
    if event == 'call' and code.co_name == 'trace':
        runs.append([])
    if event == 'call' and code.co_name == 'put':
        d = frame.f_locals
        if d['p'] < slot + 4 and slot < d['p'] + d['w']:
            runs[-1].append((frame.f_back.f_locals.get('at'), d['p'], d['w'], d['z']))
    if event == 'return' and code.co_name == 'trace':
        d = frame.f_locals
        if runs[-1] != [(0x55bd8, slot, 4, 0)]:
            raise ValueError(('unexpected overlapping writes', runs[-1]))
        if bytes(d['mem'][slot+i] for i in range(4)) != bytes(4):
            raise ValueError('final slot not zero')
        runs[-1].append(d['pc'])


if __name__ == '__main__':
    old = sys.getprofile()
    try:
        sys.setprofile(observe)
        runpy.run_path(str(source))
    finally:
        sys.setprofile(old)
    stops = [r[-1] for r in runs]
    if sorted(stops) != sorted([0x6632e]*32 + [0x4db3e]*8 + [0x20000040]*24):
        raise ValueError('unexpected stop distribution')
    print('PASS: one 4-byte clear, no later overlapping stores in each of 64 traces; 32 bounded waits, 8 zero-count paths, 24 allocation entries; no dispatch observed')
