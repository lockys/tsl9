"""Compare real linked spans, using the local bounded TX instruction decoders.
Usage: python check_v4160_linked_tx_loop_exit.py original.bin c-spans.bin cpp-spans.bin
Only ordinary, disjoint synthetic RAM; start at loop gate, stop at tail jump.
"""
import hashlib
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiments/v4160-10408-aggregate-audit'))
from tx_copy_finish_composition import loop, tail


def need(ok, msg):
    if not ok:
        raise ValueError(msg)


def image(path, digest):
    data = Path(path).read_bytes()
    need(hashlib.sha256(data).hexdigest() == digest, 'input identity')
    return data[0xa56:0xb6e]


def trace(code, candidate, bank, n):
    src, sp, gp = 0x20009000, 0x2000ff80, 0x20004000
    desc = 0x2000b18c + bank*1062
    dest = desc+11
    seed = (0x5d + n//256 + bank) & 255
    payload = bytes((j*37 + (j>>8) + n + bank) & 255 for j in range(n))
    r = [0]*32
    r[2:4] = [sp,gp]; r[8:10] = [n,src]; r[12:16] = [bank,0x2000b18c,seed,desc+6]
    mem = {src+j:v for j,v in enumerate(payload)}
    for lo,size in [(desc,1062),(sp+12,20),(0x40050,4),(gp+148+4*bank,1)]:
        mem.update((lo+j,(j+0xa5)&255) for j in range(size))
    initial = mem.copy()
    for j,v in enumerate(payload):
        action,r,mem,events = loop.step(code,r,mem,candidate)
        need(action=='copy' and events==[('read',src+j,v),('write',dest+j,v)], 'copy trace')
    action,r,mem,events = loop.step(code,r,mem,candidate)
    checksum = (seed+sum(payload)) & 255
    expected = initial.copy(); expected.update((dest+j,v) for j,v in enumerate(payload))
    need(action=='exit' and not events and r[11]==n and r[14]==checksum and mem==expected, 'loop exit')
    end = tail.run(code,r,mem,candidate)
    expected[dest+n] = checksum
    for j,v in enumerate((n+6).to_bytes(2,'little') + bytes(2)):
        expected[desc+2+j] = v
    need(end[2]==expected and end[3][0]==('write',dest+n,1,checksum), 'tail stores')
    return r,mem,end


def main():
    orig, c, cpp = sys.argv[1:]
    orig=image(orig,'0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
    for mode,path in [('C',c),('C++',cpp)]:
        code=image(path,'ef9d3be753f02d5802a2c2feda99aa94b9b3c3acc2b55d32f8f480719d658a54')
        lengths=(0,1,2,7,8,15,16,254,255,256,257,511,512,1023,1024,1038,1039)
        for bank in (0,1):
            for n in lengths:
                need(trace(orig,False,bank,n)==trace(code,True,bank,n),'machine state')
        mutant=bytearray(code); i=0x8b20-0x8a56
        need(mutant[i:i+2]==bytes.fromhex('8505'),'increment site')
        mutant[i:i+2]=bytes.fromhex('2a97')  # valid add a4,a4,a0 instead of advancing cursor
        try: trace(mutant,True,0,2)
        except ValueError as exc: need(str(exc)=='copy trace','wrong mutant failure')
        else: raise ValueError('missed cursor control')
        print(f'PASS {mode}: 34 loop exits and tails; {2*sum(lengths)} copied bytes; cursor mutant detected')


if __name__=='__main__': main()
