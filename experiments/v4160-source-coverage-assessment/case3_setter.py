"""Compose case 3 with bounded 0x13ba6 leaf and its subsequent jump.

This is boundary reconstruction, not continuous execution.  Memory accesses
succeed, the leaf returns, and no concurrent writes or traps occur.
"""
import hashlib
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

case = load('case', HERE / 'table_case_entry.py')
setter = load('setter', ROOT / 'experiments/v4160-dispatch-148b4-model/state_setter.py')


def jump(code):
    if code != bytes.fromhex('89ba'): raise ValueError('unexpected continuation')
    h = int.from_bytes(code,'little')
    if h & 3 != 1 or h >> 13 != 5: raise ValueError('not C.J')
    imm = ((h>>12&1)<<11)|((h>>11&1)<<4)|((h>>9&3)<<8)|((h>>8&1)<<10)|((h>>7&1)<<6)|((h>>6&1)<<7)|((h>>3&7)<<1)|((h>>2&1)<<5)
    return 0x14746 + (imm - 4096 if imm & 2048 else imm)


def main():
    image = setter.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=setter.SHA: raise ValueError('APP identity mismatch')
    pc = 0x1473e
    raw = image[pc-0x8000:pc-0x8000+8]
    continuation = image[0x14746-0x8000:0x14748-0x8000]
    if jump(continuation)!=0x14098: raise ValueError('jump destination mismatch')
    for first in range(65536):
        for handle,second,reads,writes in (
            (first,first,[setter.FIRST],[(0x2000c799,4)]),
            (first^1,first^1,[setter.FIRST,setter.SECOND],[(0x2000c79d,4)]),
            (first^1,first,[setter.FIRST,setter.SECOND],[]),
            (first|0x10000,first,[setter.FIRST,setter.SECOND],[]),
        ):
            target,a0,a1,ra = case.entry(pc,raw,handle)
            if (target,a0,a1,ra)!=(0x13ba6,handle,4,0x14746): raise ValueError('call boundary mismatch')
            got = setter.run(image,a0,a1,first,second)
            if got != (reads,writes,(0x12345678,0x20001000,handle,4)): raise ValueError('leaf mismatch')
    for i in range(2):
        bad=bytearray(continuation); bad[i]^=1
        try: jump(bytes(bad))
        except ValueError: continue
        raise ValueError('jump mutation accepted')
    print('PASS: 262144 case-3/leaf combinations, two continuation mutations')
    print('First matching record receives byte 4; no match writes nothing; continuation reaches 0x14098.')
    print('Synthetic boundary composition only: no asynchronous effects, epilogue or hardware execution.')

if __name__=='__main__': main()
