"""Cross-check retained 0x19bf0 instruction inventory against original image.

Byte identity and direct-target decoding only; this is not CPU execution.
"""
import hashlib
import importlib.util
import json
import re
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
spec=importlib.util.spec_from_file_location('continuation',HERE/'callee_12ad0_continuation.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
START,END=0x19bf0,0x19ca6
EVIDENCE=ROOT/'analysis/record-copy-windows-2026-10-25/evidence.json'


def cb(pc,code):
    h=int.from_bytes(code,'little')
    if len(code)!=2 or h&3!=1 or h>>13 not in (6,7): raise ValueError('not compressed branch')
    imm=((h>>12&1)<<8)|((h>>10&3)<<3)|((h>>5&3)<<6)|((h>>3&3)<<1)|((h>>2&1)<<5)
    return pc+(imm-512 if imm&256 else imm)


def validate(image,operations):
    if len(operations)!=54: raise ValueError('instruction count mismatch')
    pc=START; targets=0
    for op in operations:
        raw=bytes.fromhex(op['bytes']); n=op['size']
        if op['addr']!=pc or n not in (2,4) or len(raw)!=n: raise ValueError('noncontiguous inventory')
        if image[pc-0x8000:pc-0x8000+n]!=raw: raise ValueError(f'byte mismatch at {pc:#x}')
        text=op['opcode']; m=re.search(r'0x[0-9a-f]+$',text)
        if m:
            name=text.split()[0]; target=int(m.group(),16)
            if name=='j': actual=mod.entry.calls.cj(pc,raw)
            elif name in ('beqz','bnez'): actual=cb(pc,raw)
            elif name in ('bltu','bleu'): actual=mod.entry.branch(pc,raw)
            else: raise ValueError(f'unexpected transfer {text}')
            if actual!=target: raise ValueError(f'wrong target at {pc:#x}')
            targets+=1
        pc+=n
    if pc!=END or targets!=10: raise ValueError(f'range or target count mismatch {pc:#x} {targets}')
    return targets


def main():
    image=mod.entry.calls.case.dispatch.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=mod.entry.calls.case.dispatch.SHA: raise ValueError('APP identity mismatch')
    evidence=json.loads(EVIDENCE.read_text(encoding='utf-8'))
    funcs=[x for x in evidence['functions'] if x['start']==START and x['end']==END]
    if len(funcs)!=1: raise ValueError('function inventory mismatch')
    ops=funcs[0]['operations']; count=validate(image,ops)
    for pc in range(START,END):
        bad=bytearray(image); bad[pc-0x8000]^=1
        try: validate(bad,ops)
        except ValueError: continue
        raise ValueError(f'accepted byte mutation {pc:#x}')
    for i,op in enumerate(ops):
        m=re.search(r'0x[0-9a-f]+$',op['opcode'])
        if not m: continue
        bad=[dict(x) for x in ops]
        bad[i]['opcode']=op['opcode'][:m.start()]+hex(int(m.group(),16)+2)
        try: validate(image,bad)
        except ValueError: continue
        raise ValueError('accepted mutated target')
    bad=[dict(x) for x in ops]; bad[0]['addr']+=2
    try: validate(image,bad)
    except ValueError: pass
    else: raise ValueError('accepted noncontiguous inventory')
    print(f'PASS: 182 original bytes, 54 contiguous instructions, {count} decoded direct targets and target mutations, 182 byte mutations')
    print('Static evidence only; no instruction execution, copy semantics, overlap or hardware claim.')

if __name__=='__main__': main()
