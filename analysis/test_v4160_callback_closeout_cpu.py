"""Original D05C stores and 9F74 / 1061C callbacks, offline only.

Actual dispatcher and cancellation are executed; free/event providers stop at
entry. Explicit event inputs do not establish real scheduler delivery.
"""
from hashlib import sha256
from itertools import product
from test_v4160_a204_local_cpu import (LocalState,initialize as init_local,local,
    fixture as local_fixture,DIRECT,ALT_FLAG,ALT_KEY,GP,S_REGS,segment)
from test_v4160_callback_dispatch_cpu import dispatch,setup
from test_v4160_register_gate_cpu import rows,register,arguments,FREE,TABLE,TASK
from test_v4160_feature_outer_cpu import registers,APP_HASH
from test_v4160_zero_id_queue_cpu import IMAGE,BASE,MASK,check

PACKET,CLEAR,CANCEL,AFTER,EVENT = 0x2000bf38,0x9f74,0x90b0,0x905a,0x30001000
PENDING = GP+175


class Closeout(LocalState):
    CODE_RANGES = LocalState.CODE_RANGES+((DIRECT,0xd07c),(CLEAR,0x9f7a),
                                         (ALT_KEY,0x10630),(CANCEL,0x9124))


def initialize(c):
    init_local(c)
    c.regions.extend(((PACKET,bytearray([0xcc]*4+[255]),True),
                      (0x4005c,bytearray(EVENT.to_bytes(4,'little')),False)))


def packet(c):
    before = c.reg[:]
    a,b,n = before[10:13]
    data = [1,a & 255,(-n) & 255,b & 255]
    expected = [('w',PACKET+i,1,v) for i,v in enumerate(data)]
    check(segment(c,DIRECT,{before[1]},expected,'packet leaf') == before[1] and
          c.reg[12] == (-n)&MASK and (c.reg[14],c.reg[15]) == (1,PACKET),
          'packet leaf result')
    check(all(c.reg[r] == before[r] for r in range(32) if r not in (12,14,15)) and
          c.mem(PACKET,4) == int.from_bytes(bytes(data),'little') and
          c.mem(PACKET+4,1) == 255,'packet preservation/canary')


def clear(c):
    before = c.reg[:]
    neighbors = (c.mem(GP+174,1),c.mem(GP+176,1))
    check(segment(c,CLEAR,{before[1]},[('w',PENDING,1,0)],'clear callback') == before[1] and
          c.reg == before and c.mem(PENDING,1) == 0 and
          (c.mem(GP+174,1),c.mem(GP+176,1)) == neighbors,'clear callback preservation')


def self_entry(c):
    before = c.reg[:]
    check(segment(c,ALT_KEY,{CANCEL},[('w',ALT_FLAG,1,0)],'self callback') == CANCEL and
          c.reg[10] == ALT_KEY and
          all(c.reg[r] == before[r] for r in range(32) if r not in (10,15)) and
          c.mem(ALT_FLAG,1) == 0 and c.mem(ALT_FLAG+1,1) == 255,'self callback key/frame')


def cancel(c):
    before = c.reg[:]
    sp,resume,key = before[2],before[1],before[10]
    data = c.mem(TABLE,180).to_bytes(180,'little')
    keys = [int.from_bytes(data[12*i+4:12*i+8],'little') for i in range(15)]
    index = next((i for i,k in enumerate(keys) if k == key),None)
    expected = [('w',sp-8,4,before[8]),('w',sp-12,4,before[9]),('w',sp-4,4,resume)]
    expected += [('r',TABLE+12*i+4,4,keys[i]) for i in range(15 if index is None else index+1)]
    model = bytearray(data)
    if index is None:
        kind,target = 'miss',resume
        expected += [('r',sp-4,4,resume),('r',sp-8,4,before[8]),('r',sp-12,4,before[9])]
    else:
        row = TABLE+12*index
        payload = int.from_bytes(data[12*index+8:12*index+12],'little')
        expected.append(('r',row+8,4,payload))
        if payload:
            kind,target = 'free',FREE
            expected.append(('r',0x40068,4,FREE))
        else:
            kind,target = 'event',EVENT
            task = c.mem(TASK,1)
            expected += [('r',sp-8,4,before[8]),('r',sp-4,4,resume),('r',TASK,1,task),
                         ('w',row+4,4,0),('w',row+8,4,0),('r',0x4005c,4,EVENT),
                         ('r',sp-12,4,before[9])]
            model[12*index+4:12*index+12] = bytes(8)
    check(segment(c,CANCEL,{FREE,EVENT,resume},expected,'self cancellation') == target,
          'self cancellation endpoint')
    check(c.mem(TABLE,180).to_bytes(180,'little') == model,'self cancellation table')
    if kind == 'free':
        check((c.reg[1],c.reg[2],c.reg[8],c.reg[9],c.reg[10]) ==
              (0x90e0,sp-16,index,TABLE,payload),'self cancellation free frame')
    else:
        check((c.reg[1],c.reg[2],c.reg[8],c.reg[9]) ==
              (resume,sp,before[8],before[9]),'self cancellation restored frame')
        check((c.reg[10],c.reg[11]) ==
              ((1,before[11]) if kind == 'miss' else (task,1 << index)),
              'self cancellation returned arguments')
    return kind,index


def finish(c,before,index):
    sp,resume = before[2],before[1]
    expected = [('r',sp-4,4,resume),('r',sp-8,4,before[8]),('r',sp-12,4,before[9])]
    check(segment(c,AFTER,{resume},expected,'callback dispatcher finish') == resume and
          c.reg[10] == ((before[11] ^ (1 << index)) & 0xffff) and
          all(c.reg[r] == before[r] for r in (1,2,3,4,*S_REGS)),
          'callback dispatcher restored result')


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == APP_HASH,'firmware identity')
    c = Closeout(image)
    initialize(c)
    for a,b in product(range(256),repeat=2):
        registers(c)
        c.reg[10:13] = [0xab000000+a,0xcd000000+b,0xfffffff1]
        packet(c)
    negations = 0
    for low,high in product(range(256),(0,0x80000000,0xffffff00)):
        registers(c)
        c.reg[10:13] = [MASK,0x80000000,high | low]
        packet(c)
        negations += 1
    direct_chains = 0
    for flag,value,ready in product((1,255),(0,1,256,MASK),range(256)):
        local_fixture(c,value,flag=flag,ready=ready)
        kind = local(c)
        if kind == 'direct':
            packet(c)
            check(c.reg[10] == 3 and c.mem(PACKET,4) == 0x01000301,'actual A204 packet return')
            direct_chains += 1
    for old,payload in product(range(256),(0,0xdeadbeef,MASK)):
        registers(c)
        c.reg[3],c.reg[10] = GP,payload
        c.mem(PENDING,1,old)
        clear(c)
    clear_chains = 0
    for index,flag,payload,raw_key in product(range(15),(0,1,255),(0,1,MASK),(CLEAR,CLEAR|1)):
        rows(c,[(index,raw_key,payload)])
        c.mem(TABLE+12*index,1,flag)
        setup(c,(1 << index) | 0x8000)
        c.mem(PENDING,1,255)
        before = c.reg[:]
        check(dispatch(c) == (index,raw_key),'clear dispatched entry')
        clear(c)
        finish(c,before,index)
        clear_chains += 1
    counts = dict.fromkeys(('miss','event','free'),0)
    odd_misses = 0
    for index,raw_key,flag,payload,duplicate,other_payload in product(range(15),
            (ALT_KEY,ALT_KEY|1),(0,1,255),(0,1,MASK),range(-1,15),(0,MASK)):
        if duplicate == index: continue
        changes = [(index,raw_key,payload)]
        if duplicate >= 0: changes.append((duplicate,ALT_KEY,other_payload))
        rows(c,changes)
        c.mem(TABLE+12*index,1,flag)
        setup(c,(1 << index) | 0x8000)
        c.mem(ALT_FLAG,1,255)
        before = c.reg[:]
        check(dispatch(c) == (index,raw_key),'self dispatched entry')
        self_entry(c)
        kind,chosen = cancel(c)
        counts[kind] += 1
        if duplicate < 0:
            want = 'miss' if not flag or raw_key & 1 else ('free' if payload else 'event')
            check(kind == want,'one-shot/retained/odd-key distinction')
            if raw_key & 1 and flag:
                check(c.mem(TABLE+12*index+4,4) == raw_key,'odd raw key retained after miss')
                odd_misses += 1
        if kind == 'miss': finish(c,before,index)
        check(c.mem(ALT_FLAG,1) == 0,'self callback clears flag before opaque boundary')
    # Explicit post-registration event injection, using existing normal-return
    # premise for 40058 only. No actual delivery or provider body is inferred.
    registrations = 0
    for key,index in product((CLEAR,ALT_KEY),range(15)):
        rows(c,[(index,0,0)])
        arguments(c,key=key,duration=1000)
        check(register(c,reply=0) == ('call',index),'cleanup registration fixture')
        setup(c,1 << index)
        before = c.reg[:]
        dispatch(c)
        if key == CLEAR: clear(c)
        else:
            self_entry(c)
            check(cancel(c) == ('miss',None),'registered one-shot self cancellation miss')
        finish(c,before,index)
        registrations += 1
    mutations = 0
    for addr,old,new,which,message in (
        (0xd066,'3306c040','3306c000','negate','packet leaf accesses'),
        (0x9f74,'a387010a','a387a10a','clear','clear callback accesses'),
        (0x10620,'238e0798','238ef798','self','self callback accesses'),
        (0x10628,'130585ff','1305a5ff','key','self callback key/frame')):
        off = addr-BASE
        check(image[off:off+len(bytes.fromhex(old))] == bytes.fromhex(old),'cleanup mutation pin')
        mutant = bytearray(image)
        mutant[off:off+len(bytes.fromhex(old))] = bytes.fromhex(new)
        d = Closeout(mutant)
        initialize(d)
        registers(d)
        d.reg[3],d.reg[10],d.reg[12] = GP,1,1
        try:
            if which == 'negate': packet(d)
            elif which == 'clear': clear(d)
            else: self_entry(d)
        except RuntimeError as error:
            check(str(error) == message,'unexpected cleanup mutation failure: '+str(error))
            mutations += 1
        else: raise RuntimeError('cleanup mutation escaped')
    print('PASS: 65536 packet byte pairs; %d full-word negations; %d actual A204/D05C returns; 768 pending-clear cases' % (negations,direct_chains))
    print('PASS: %d clear callback/dispatcher chains; self-cancel/duplicate chains %s; %d retained odd-key misses; %d registration/injected-event returns; %d mutations' % (clear_chains,counts,odd_misses,registrations,mutations))
    print('PASS: exact stores/frame/key equality; nonzero one-shot payload not freed on no-duplicate path; free/event providers NOT executed')


if __name__ == '__main__':
    verify(IMAGE.read_bytes())
