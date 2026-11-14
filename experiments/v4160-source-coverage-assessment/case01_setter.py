"""Connect cases 0/1 to the bounded original setter; second callee is stubbed.

Boundary reconstruction only. Successful reads, normal return and no
asynchronous changes are assumed; 0x12ad0 is not executed.
"""
import hashlib
import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module

calls=load('calls',HERE/'case01_calls.py')
setter=load('setter',ROOT/'experiments/v4160-dispatch-148b4-model/state_setter.py')


def main():
    image=setter.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=setter.SHA: raise ValueError('APP identity mismatch')
    count=0
    for index in (0,1):
        mode=(0,3)[index]
        for first in range(65536):
            for handle,second,reads,writes in (
                (first,first,[setter.FIRST],[(0x2000c799,mode)]),
                (first^1,first^1,[setter.FIRST,setter.SECOND],[(0x2000c79d,mode)]),
                (first^1,first,[setter.FIRST,setter.SECOND],[]),
                (first|0x10000,first,[setter.FIRST,setter.SECOND],[]),
            ):
                first_call,second_call,exit_pc=calls.run(image,index,handle)
                target,a0,a1,_=first_call
                if (target,a0,a1)!=(0x13ba6,handle,mode): raise ValueError('call mismatch')
                if setter.run(image,a0,a1,first,second)!=(reads,writes,(0x12345678,0x20001000,handle,mode)): raise ValueError('setter mismatch')
                if second_call!=(0x12ad0,(0,2)[index],0x1453c) or exit_pc!=0x14098: raise ValueError('tail mismatch')
                count+=1
    print(f'PASS: {count} case/setter boundary combinations; first-match precedence and full-width handles')
    print('Case 0 writes 0 and case 1 writes 3 to the matching state byte; unmatched writes nothing.')
    print('Second callee 0x12ad0 is stubbed; no epilogue, asynchronous or hardware claim.')

if __name__=='__main__': main()
