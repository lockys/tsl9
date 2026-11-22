"""Post-admission TX comparison on original and saved linked spans (same CLI as loop_exit)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_v4160_linked_tx_loop_exit import image, loop, need, tail
import tx_header_decoder as header


def execute(code, candidate, bank, n, cmd):
    base = 0x2000b18c + 1062 * bank
    src, sp, gp = 0x20009000, 0x2000ff80, 0x20004000
    r = [0xdeadbeef] * 32
    r[0], r[2], r[3], r[8], r[9], r[12], r[19] = 0, sp, gp, n, src, bank, cmd
    payload = bytes((i * 37 + (i >> 8) + bank + cmd) & 255 for i in range(n))
    initial = {src+i:v for i,v in enumerate(payload)}
    for start,size in [(base,1062),(sp+12,20),(0x40050,4),(gp+148+4*bank,1)]:
        initial.update((start+i,(165+i)&255) for i in range(size))
    r,mem,events = header.run(code,r,initial)
    d = base + 6
    seed = ((cmd & 255) + (n >> 8) + (n & 255)) & 255
    need((r[15],r[11],r[14]) == (d,0,seed), 'header register result')
    need(events == [('write',d,2,0x7f55),('write',d+4,1,n&255),('write',d+3,1,n>>8),('write',d+2,1,cmd&255)], 'header order')
    for i,v in enumerate(payload):
        action,r,mem,events = loop.step(code,r,mem,candidate)
        need((action,events)==('copy',[('read',src+i,v),('write',d+5+i,v)]), 'copy trace')
    action,r,mem,events = loop.step(code,r,mem,candidate)
    checksum = (seed + sum(payload)) & 255
    need((action,events,r[11],r[14])==('exit',[],n,checksum), 'loop exit')
    result = tail.run(code,r,mem,candidate)
    expected = initial.copy()
    frame = (n+6).to_bytes(2,'little') + bytes([0,0,0x55,0x7f,cmd&255,n>>8,n&255]) + payload + bytes([checksum])
    expected.update((base+2+i,v) for i,v in enumerate(frame))
    need(result[2]==expected,'final memory')
    return result


def main():
    orig = image(sys.argv[1],'0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
    for profile,path in zip(('C','C++'),sys.argv[2:],strict=True):
        code = image(path,'ef9d3be753f02d5802a2c2feda99aa94b9b3c3acc2b55d32f8f480719d658a54')
        for bank in (0,1):
            for n in (0,1,255,256,257,1023,1024,1039):
                for cmd in (0,255,0x123456a7):
                    need(execute(orig,False,bank,n,cmd)==execute(code,True,bank,n,cmd),'tail state')
        print(f'PASS {profile}: 48 decoded header -> loop -> tail cases, both banks')


if __name__=='__main__': main()
