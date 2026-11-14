"""Bounded 0x13d88 event tail to scheduler path composition.

Execution is reconstituted at boundaries, not a continuous CPU; successful
reads, stable independent table/stack data and returning benign providers are
assumed. The clock provider and scheduler providers are synthetic stubs.
"""
import hashlib
import importlib.util
import random
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
tail=load('tail',HERE.parent/'v4160-event-13d48-entry'/'tail.py')
d=load('dp',HERE/'delay_precedence.py'); free=load('free',HERE/'free_scan.py'); common=load('common',HERE/'common.py'); exitmod=load('exit',HERE/'resident_exit.py')


def main():
    image=tail.BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=tail.SHA: raise ValueError('firmware identity mismatch')
    rng=random.Random(416008); counts={'direct':0,'match':0,'insert':0,'full':0}
    for n in range(12000):
        # Four caller outcomes: nonzero result => 100; zero result and
        # delta 0/34 => 35; delta 35 => direct non-scheduler branch.
        caller=n%4; result=1 if caller==0 else 0; delta=(0,0,34,35)[caller]
        previous=rng.getrandbits(32); clock=(previous+delta)&0xffffffff
        pc,args,_,_,_,_,_=tail.run(image,result,clock,previous,0x20001000,0x20002000,0x12345678)
        if caller==3:
            if (pc,args)!=(0x13346,(0,)): raise ValueError('direct caller mismatch')
            counts['direct']+=1; continue
        expected_delay=100 if caller==0 else 35
        if (pc,args)!=(0x9124,(0x13346,0,expected_delay,0)): raise ValueError('caller arguments mismatch')
        shape=(n//4)%3; callback,mode,delay,arg=args
        if shape==0: words=[0xabcdef01]*15; idx=rng.randrange(15); words[idx]=callback
        elif shape==1: words=[0xabcdef01]*15; idx=rng.randrange(15); words[idx]=0
        else: words=[0xabcdef01]*15; idx=15
        if d.branch(image,delay)!=0x9188: raise ValueError('nonzero delay branch')
        if d.setup.run(image,*args)!=(callback,mode,0x2000be08,delay,arg,0x2000be08): raise ValueError('setup mismatch')
        mpc,match_idx,_,_=d.m.scan(image,words,callback)
        if shape==0:
            if (mpc,match_idx)!=(0x91a2,idx): raise ValueError('match route mismatch')
            task=rng.randrange(256); a0,a1,_=d.upd.run(image,idx,0,mode,arg,task,0x1000)
            counts['match']+=1
        else:
            if (mpc,match_idx)!=(0x9206,15): raise ValueError('miss route mismatch')
            fpc,free_idx,_,a0,_=free.scan(image,words)
            if shape==2:
                if (fpc,free_idx,a0)!=(0x9234,15,1): raise ValueError('full route mismatch')
                counts['full']+=1; continue
            if (fpc,free_idx)!=(0x920e,idx): raise ValueError('insert route mismatch')
            task=rng.randrange(256)
            _,a0,a1,_,_=d.z.v.run(image,idx,callback,mode,delay,arg,task)
            counts['insert']+=1
        dest,mask,scaled,base=common.run(image,a1,delay,mode)
        if (dest,mask,scaled,base)!=(0x922c,1<<idx,160 if delay==100 else 56,0x40000) or a0!=task: raise ValueError('scheduler arithmetic mismatch')
        kind,_,out,_,_,_=exitmod.run(image,mode,task,0x1000,[1,2,3,4,5,6],0x2000,0)
        if kind!='return' or out!=1: raise ValueError('resident exit mismatch')
    if counts!={'direct':3000,'match':3000,'insert':3000,'full':3000}: raise ValueError(f'coverage mismatch: {counts}')
    print(f'PASS: 12000 composed event-tail cases: {counts}')
    print('PASS: original tail supplies delay 35 or 100; bounded common scaling yields 56 or 160')
    print('Reachability, provider effects, concurrent memory and physical hardware not established.')

if __name__=='__main__': main()
