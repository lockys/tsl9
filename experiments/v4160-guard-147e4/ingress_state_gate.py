"""Decode the local ingress state gate and unsigned counter guard.

Only entry at 0x89f6 and successful halfword reads are modeled.  No claim of
packet reachability, atomicity, trap behavior or execution on hardware.
"""
import hashlib
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('entry', HERE.parent/'v4160-dispatch-148b4-model'/'entry_provenance.py')
entry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(entry)
MASK = 0xffffffff
EXPECTED = bytes.fromhex('631a970303d6a1081307f0406365c704')

def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits-1)) else value

def run(code, gp, a4, s9, loaded, initial_a2=0):
    if len(code) != 16 or any(not 0 <= x <= MASK for x in (gp,a4,s9,initial_a2)) or not 0 <= loaded <= 0xffff:
        raise ValueError('invalid input')
    registers = [0]*32
    registers[2] = 0x13579bdf  # Preserve a nonzero SP to expose an altered rs1.
    registers[3],registers[12],registers[14],registers[25] = gp,initial_a2,a4,s9
    reads = []
    trace = []
    pc = 0x89f6
    for _ in range(4):
        if pc in (0x8a2a,0x8a06,0x8a4c):
            return pc,reads,registers[12],registers[14],trace
        offset = pc - 0x89f6
        if offset < 0 or offset+4 > len(code) or pc & 1:
            raise ValueError('outside local block')
        word = int.from_bytes(code[offset:offset+4],'little')
        trace.append(pc)
        op, rd, f3, rs1, rs2 = word&127, (word>>7)&31, (word>>12)&7, (word>>15)&31, (word>>20)&31
        if op == 0x63 and f3 in (1,6):
            immediate = ((word>>31&1)<<12)|((word>>7&1)<<11)|((word>>25&63)<<5)|((word>>8&15)<<1)
            take = registers[rs1] != registers[rs2] if f3 == 1 else registers[rs1] < registers[rs2]
            pc = (pc + signed(immediate,13)) & MASK if take else pc+4
        elif op == 3 and f3 == 5:
            address = (registers[rs1]+signed(word>>20,12)) & MASK
            if address != (gp+138)&MASK: raise ValueError('unexpected load address')
            reads.append(address)
            registers[rd] = loaded
            pc += 4
        elif op == 0x13 and f3 == 0:
            registers[rd] = (registers[rs1]+signed(word>>20,12)) & MASK
            pc += 4
        else:
            raise ValueError('unsupported instruction')
        registers[0] = 0
    if pc in (0x8a2a,0x8a06,0x8a4c):
        return pc,reads,registers[12],registers[14],trace
    raise ValueError('state gate did not finish')

def check(code,gp,a4,s9,loaded):
    got = run(code,gp,a4,s9,loaded)
    if a4 != s9:
        expected = (0x8a2a,[],0,a4,[0x89f6])
    else:
        expected = (0x8a4c if loaded>1039 else 0x8a06,[(gp+138)&MASK],loaded,1039,[0x89f6,0x89fa,0x89fe,0x8a02])
    if got != expected: raise ValueError(f'state gate mismatch: {got!r} != {expected!r}')

def main():
    image=entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=entry.SHA: raise ValueError('firmware identity mismatch')
    code=image[0x89f6-0x8000:0x8a06-0x8000]
    if code!=EXPECTED: raise ValueError('original bytes mismatch')
    for loaded in range(65536): check(code,0x20004000,5,5,loaded)
    for gp in (0,0xffffff76,MASK):
        for a4,s9 in ((0,1),(MASK,0),(0,MASK),(MASK,MASK),(5,5)):
            for loaded in (0,1,1038,1039,1040,65535): check(code,gp,a4,s9,loaded)
    cases=((0x20004000,5,5,0),(0x20004000,5,6,0),(0xffffffff,5,5,1039),(0xffffffff,5,5,1040),(0,0,0,65535))
    for i in range(len(code)):
        mutant=bytearray(code); mutant[i]^=1
        try:
            for args in cases: check(mutant,*args)
        except ValueError: continue
        raise ValueError(f'undetected byte mutation {i}')
    print('PASS: 65536 counter values, 90 boundary cases and 16 byte mutations')
    print('Conditional local entry and successful halfword read only; not hardware or packet reachability.')

if __name__=='__main__': main()
