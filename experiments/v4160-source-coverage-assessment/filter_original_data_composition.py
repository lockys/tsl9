"""Conditionally combine original source windows, filter descriptors and stores.

Assumes providers filled the 112-byte local buffer with zeros and copied the
original 94/106-byte window into its prefix, normal returns and ordinary
word-backed synthetic registers. No provider, physical MMIO, interrupts,
aliasing, traps or continuous CPU execution is modeled.
"""
import hashlib,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent

def module(name,filename):
    spec=importlib.util.spec_from_file_location(name,HERE/filename)
    result=importlib.util.module_from_spec(spec); spec.loader.exec_module(result); return result
src=module('original_data','transfer_data_witness.py')
compose=module('register_composition','filter_register_composition.py')
loop=compose.machine.projection.route.A.audit.loop


def main():
    image=loop.calls.case.dispatch.IMAGE.read_bytes(); compose.machine.projection.route.flow.flow(image)
    for address,length,digest in src.SLICES:
        window=src.slice_data(image,address,length,digest)
        buffer=window+bytes(112-length)
        # Independently build expected 14 pairs of packed words from the input.
        expected=[]
        for i in range(14):
            words=[(int.from_bytes(buffer[8*i+2*j:8*i+2*j+2],'little')<<5)&65535 for j in range(4)]
            expected.extend(((words[3]<<16)|words[1],(words[2]<<16)|words[0]))
        for sp in (0x20001000,0xfffffe00,0x1000,0x7fffff00):
            mem={(sp+32+i)&0xffffffff:b for i,b in enumerate(buffer)}; fields=[]
            for i in range(14):
                result=loop.step(image,mem,sp,(sp+32+8*i)&0xffffffff,i,1,1)
                if result[3:5]!=((sp+40+8*i)&0xffffffff,i+1): raise ValueError('loop state mismatch')
                fields.append(tuple(mem[(sp+12+2*j)&0xffffffff]|mem[(sp+13+2*j)&0xffffffff]<<8 for j in range(4)))
            initial={a:0 for a in (compose.CTL,compose.ACTIVE,compose.SCALE,compose.MODE,compose.FIFO)}
            regs,data,events=compose.run(image,initial,fields)
            actual=[data[0x40006640+4*i] for i in range(28)]
            if actual!=expected or len(events)!=126 or regs[compose.ACTIVE]!=0x3fff: raise ValueError('data composition mismatch')
        packed=b''.join(word.to_bytes(4,'little') for word in expected)
        expected_hash={94:'0f71877f232f85e1b8a482a1ee81d2669cba15a1d38438b1b460fb3037e45f51',106:'2edd87ad198e7a47c86348ae7d060a464770af0ac539b56f98c8fdbc58f1120e'}[length]
        if hashlib.sha256(packed).hexdigest()!=expected_hash: raise ValueError('packed fixture mismatch')
        print(f'PASS: original {length}-byte slice at {address:#x}, four synthetic SPs, 28 packed words sha256={expected_hash}')
    print('Conditional zero-fill/copy provider and ordinary-memory assumptions only; no hardware execution.')
if __name__=='__main__': main()
