"""Compose data-selected delay caller with bounded scheduler projections.

Synthetic independent segment state; successful reads, stable table, benign
returning providers and no memory aliasing. No continuous CPU or hardware.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load(name):
    spec=importlib.util.spec_from_file_location(name,HERE/(name+'.py')); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
entry=load('data_delay_entry'); caller=load('data_delay_caller'); zero=load('zero_delay_scan'); insert=load('zero_delay_insert'); setup=load('setup'); match=load('match_scan'); upd=load('match_update'); free=load('free_scan'); common=load('common'); ex=load('resident_exit'); full=load('full_exit'); branch=load('delay_precedence')


def main():
    image=caller.v.BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=caller.v.SHA: raise ValueError('firmware identity mismatch')
    count=0; seen=set()
    for byte in range(256):
        for shape in ('match','empty','both','full'):
            for clock in (0,0xffffffff,0xfffffff0,0x12345678):
                initial_sp=0x20002000; saved_ra=0x12345678
                typ,_,body_sp,_,_=entry.run(image,0,0,initial_sp,saved_ra)
                if typ!='body': raise ValueError('gate mismatch')
                args,restored_sp,ra,_=caller.run(image,byte,clock,0x20000000,0x20001234,body_sp,saved_ra)
                callback,mode,delay,argument=args
                if (restored_sp,ra,callback,mode,argument)!=(initial_sp,saved_ra,0xb254,0,0): raise ValueError('caller boundary mismatch')
                expected_delay=(0,60000,300000,600000)[byte>>6]
                if delay!=expected_delay: raise ValueError('delay mismatch')
                words=[0xabcdef01]*15
                if shape in ('match','both'): words[3]=callback
                if shape in ('empty','both'): words[7]=0
                route=None
                if branch.branch(image,delay)==0x913c:
                    pc,idx,_,_=zero.scan(image,words)
                    if pc==0x914a: route='zero'; expected_idx=7
                if route is None:
                    if setup.run(image,callback,mode,delay,argument)!=(callback,0,0x2000be08,delay,0,0x2000be08): raise ValueError('setup mismatch')
                    pc,idx,_,_=match.scan(image,words,callback)
                    if pc==0x91a2: route='match'; expected_idx=3
                    else:
                        pc,idx,_,a0,_=free.scan(image,words)
                        if pc==0x920e: route='insert'; expected_idx=7
                        else: route='full'; expected_idx=15
                if idx!=expected_idx: raise ValueError('index mismatch')
                if route=='zero':
                    a0,a1,target,_,_,_=insert.run(image,idx,callback,argument,9,0x1000,0x20003000,[0]*6)
                    if (a0,a1,target)!=(9,1<<idx,0x1000) or delay!=0: raise ValueError('zero insert mismatch')
                elif route=='match':
                    a0,a1,_=upd.run(image,idx,0,mode,argument,9,0x1000)
                elif route=='insert':
                    _,a0,a1,_,_=caller.v.run(image,idx,callback,mode,delay,argument,9)
                else:
                    value,_,_,_,_=full.run(image,0x20003000,[0]*6,a0)
                    if value!=1: raise ValueError('full exit mismatch')
                if route in ('match','insert'):
                    dest,mask,scaled,_=common.run(image,a1,delay,mode)
                    if (dest,mask,scaled,a0)!=(0x922c,1<<idx,(delay*8)//5,9): raise ValueError('common mismatch')
                    if ex.run(image,mode,9,0x20003000,[0]*6,0x1000,0)[0:3]!=('return',0,1): raise ValueError('resident mismatch')
                seen.add((byte>>6,shape,route)); count+=1
    if count!=4096 or len(seen)!=16: raise ValueError(f'coverage mismatch {count} {len(seen)}')
    print('PASS: 4096 caller-to-scheduler compositions; all byte values, four table shapes and four clocks')
    print('PASS: selected delays 0/60000/300000/600000; nonzero scaled values 96000/480000/960000')
    print('Bounded segments only; providers benign by assumption, no hardware or reachability claim.')

if __name__=='__main__': main()
