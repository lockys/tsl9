"""Original 135e6/13d48 and bit1 caller, offline shared-state fixtures.

Full callback tables return naturally. Raw clock receives only an explicit scalar
return; TX and all provider bodies stop at entry. Event delivery is not inferred.
"""
from hashlib import sha256
from itertools import product
from test_v4160_task_event_cpu import (TaskEvent,initialize as init_event,segment,
    entry as event_entry,finish,GP,S_REGS)
from test_v4160_register_gate_cpu import rows,register,REGISTER
from test_v4160_timer_callback_cpu import timer,scale,RAW,TIMER
from test_v4160_feature_outer_cpu import registers,APP_HASH
from test_v4160_zero_id_queue_cpu import IMAGE,BASE,MASK,check

PREP,HANDLER,TX,MARKER,RECORD,STAMP = 0x135e6,0x13d48,0x13346,0x1333c,0x2000c794,GP+344


class Bit1(TaskEvent):
    CODE_RANGES = TaskEvent.CODE_RANGES+((PREP,0x13660),(HANDLER,0x13dd4),(TIMER,0x81ca))


def initialize(c):
    init_event(c)
    c.regions.extend(((RECORD,bytearray([0xcc]*10+[255]),True),
                      (0x4007c,bytearray(RAW.to_bytes(4,'little')),False)))


def records(c,values):
    h0,m0,a0,h1,m1,a1 = values
    for off,size,x in ((2,2,h0),(5,1,m0),(4,1,a0),(6,2,h1),(9,1,m1),(8,1,a1)):
        c.mem(RECORD+off,size,x)


def fixture(c,values=(0,0,0,0,0,0),stamp=0):
    registers(c)
    c.reg[3] = GP
    c.mem(RECORD,1,0xcc)
    c.mem(STAMP,4,stamp)
    records(c,values)
    rows(c)  # Explicitly full, with no MARKER/TX key: registration returns1.


def preprocess(c,complete=False):
    before = c.reg[:]
    sp,resume = before[2],before[1]
    expected,found = [],False
    for offset in (0,4):
        h,m,a = (c.mem(RECORD+offset+n,s) for n,s in ((2,2),(5,1),(4,1)))
        expected.append(('r',RECORD+offset+2,2,h))
        if h != 0xfffe:
            expected.append(('r',RECORD+offset+5,1,m))
            if m:
                expected.append(('r',RECORD+offset+4,1,a))
                if a:
                    found = True
                    break
    if found: expected += [('w',sp-4,4,resume),('w',RECORD,1,1)]
    stop = segment(c,PREP,{REGISTER,resume},expected,'preprocess')
    check(stop == (REGISTER if found else resume),'preprocess endpoint')
    if found:
        check((c.reg[1],c.reg[2],c.reg[10:14]) == (0x13656,sp-16,[MARKER,0,300,0]),
              'preprocess registration contract')
        if not complete: return 'register'
        check(register(c) == ('full',None),'preprocess full-table return')
        check(segment(c,0x13656,{resume},[('r',sp-4,4,resume)],'preprocess finish') == resume and
              c.reg[10] == 1,'preprocess ignores registration failure')
    else: check(c.reg[10] == 0,'preprocess zero return')
    check((c.reg[1],c.reg[2]) == (resume,sp) and
          all(c.reg[r] == before[r] for r in (3,4,*S_REGS)) and c.mem(RECORD+10,1) == 255,
          'preprocess preserved caller')
    return 'one' if found else 'zero'


def handler(c,raw=None,after=None,complete_registration=False):
    before = c.reg[:]
    sp,resume = before[2],before[1]
    check(segment(c,HANDLER,{PREP},[('w',sp-4,4,resume)],'bit1 entry') == PREP and
          (c.reg[1],c.reg[2]) == (0x13d50,sp-16),'bit1 prep call frame')
    outcome = preprocess(c,complete=True)
    result = int(outcome == 'one')
    if after is not None: records(c,after)  # Explicit between-call state hook.
    h0,m0,h1,m1 = (c.mem(RECORD+o,s) for o,s in ((2,2),(5,1),(6,2),(9,1)))
    expected = [('r',RECORD+2,2,h0)]
    block = False
    if h0 != 0xfffe: expected.append(('r',RECORD+5,1,m0))
    if h0 == 0xfffe or m0:
        expected.append(('r',RECORD+6,2,h1))
        if h1 != 0xfffe: expected.append(('r',RECORD+9,1,m1))
        block = h1 == 0xfffe or bool(m1)
    if block: expected.append(('r',sp-4,4,resume))
    elif result: expected.append(('r',sp-4,4,resume))
    target = resume if block else REGISTER if result else TIMER
    check(segment(c,0x13d50,{TIMER,REGISTER,TX,resume},expected,'bit1 fresh state') == target,
          'bit1 fresh endpoint')
    if block:
        check(c.reg[10] == result and (c.reg[1],c.reg[2]) == (resume,sp),'bit1 blocked return')
        return 'return'
    duration = 100 if result else None
    if not result:
        check((c.reg[1],c.reg[2],c.reg[10]) == (0x13da6,sp-16,0),'bit1 clock entry')
        if raw is None: return 'clock'
        stamp = c.mem(STAMP,4)
        timer(c,raw)  # Explicit raw scalar normal-return premise, no body run.
        now = scale(raw)
        elapsed = (now-stamp)&MASK
        expected = [('r',STAMP,4,stamp),('r',sp-4,4,resume)]
        if elapsed <= 34:
            target,duration = REGISTER,35
        else:
            expected.append(('w',STAMP,4,now))
            target = TX
        check(segment(c,0x13da6,{REGISTER,TX,resume},expected,'bit1 elapsed') == target,
              'bit1 elapsed endpoint')
        check(c.mem(STAMP,4) == (stamp if elapsed <= 34 else now),'bit1 timestamp update')
    check((c.reg[1],c.reg[2]) == (resume,sp) and
          all(c.reg[r] == before[r] for r in (3,4,*S_REGS)),'bit1 restored tail frame')
    if target == TX:
        check(c.reg[10] == 0,'bit1 TX argument')
        return 'tx'
    check(c.reg[10:14] == [TX,0,duration,0],'bit1 scheduled TX arguments')
    if complete_registration:
        check(register(c) == ('full',None),'bit1 natural registration failure')
        return 'return'
    return 'schedule100' if result else 'schedule35'


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == APP_HASH,'firmware identity')
    c = Bit1(image)
    initialize(c)
    for field,h in product((0,1),range(65536)):
        values = (h,255,255,0xfffe,0,0) if field == 0 else (0xfffe,0,0,h,255,255)
        fixture(c,values)
        preprocess(c)
    byte_cases = 0
    for field,m,a in product((0,1),range(256),(0,1,255)):
        values = (0,m,a,0xfffe,0,0) if field == 0 else (0xfffe,0,0,0,m,a)
        fixture(c,values)
        preprocess(c,complete=True)
        byte_cases += 1
    routes = dict.fromkeys(('return','clock','schedule100'),0)
    for values in product((0,0xfffe,0xffff),(0,1,255),(0,1,255),
                          (0,0xfffe,0xffff),(0,1,255),(0,1,255)):
        fixture(c,values)
        routes[handler(c)] += 1
    hooks = 0
    for initial,after in product(((0,0,0,0,0,0),(0,1,1,0,0,0),(0xfffe,0,0,0xfffe,0,0)),
            ((0,0,0,0,0,0),(0,1,0,0xfffe,0,0),(0xfffe,0,0,0,1,0),(0,0,0,0,1,1))):
        fixture(c,initial)
        handler(c,after=after)
        hooks += 1
    clocks = 0
    outcomes = dict.fromkeys(('schedule35','tx'),0)
    for raw,elapsed in product((0,1,16,0x1999999a,0x80000000,MASK),
                               (*range(256),0x7fffffff,0x80000000,MASK)):
        fixture(c,stamp=(scale(raw)-elapsed)&MASK)
        outcome = handler(c,raw=raw)
        check(outcome == ('schedule35' if elapsed <= 34 else 'tx'),'elapsed unsigned threshold')
        outcomes[outcome] += 1
        clocks += 1
    events = 0
    for mask in (*range(2,65536,4),0x80000002,0xfffffffe):
        fixture(c,(0xfffe,0,0,0xfffe,0,0))
        c.reg[11] = mask
        kind,before = event_entry(c)
        check(kind == 'bit1' and handler(c) == 'return','actual bit1 natural callee return')
        finish(c,before,2,0x1731a)
        events += 1
    for values in ((0,1,1,0,0,0),(0,0,0,0,1,1)):
        fixture(c,values)
        c.reg[11] = 0x80000002
        _,before = event_entry(c)
        check(handler(c,complete_registration=True) == 'return','full-table bit1 natural return')
        check(c.mem(RECORD,1) == 1,'preprocess flag survives failed registration')
        finish(c,before,2,0x1731a)
        events += 1
    mutations = 0
    for addr,old,new,which,message in (
        (0x135f0,'7917','7d17','sentinel','preprocess accesses'),
        (0x1364e,'2305f714','23050714','flag','preprocess accesses'),
        (0x13dac,'13072002','13073002','threshold','bit1 elapsed accesses'),
        (0x13d8c,'13064006','13065006','delay','bit1 scheduled TX arguments')):
        off = addr-BASE
        check(image[off:off+len(bytes.fromhex(old))] == bytes.fromhex(old),'bit1 mutation pin')
        mutant = bytearray(image)
        mutant[off:off+len(bytes.fromhex(old))] = bytes.fromhex(new)
        d = Bit1(mutant)
        initialize(d)
        fixture(d,(0xfffe,1,1,0,0,0) if which == 'sentinel' else
                  (0,1,1,0,0,0) if which in ('flag','delay') else (0,0,0,0,0,0),stamp=(-35)&MASK)
        try:
            if which in ('sentinel','flag'): preprocess(d)
            else: handler(d,raw=0)
        except RuntimeError as error:
            check(str(error) == message,'unexpected bit1 mutation failure: '+str(error))
            mutations += 1
        else: raise RuntimeError('bit1 mutation escaped')
    print('PASS: 131072 halfword sentinel probes; %d mode/action bytes; 729 original branch combinations %s; %d fresh-state hooks' % (byte_cases,routes,hooks))
    print('PASS: %d declared-clock elapsed cases %s; %d actual bit1 event/callee returns; %d mutations' % (clocks,outcomes,events,mutations))
    print('PASS: exact read/store/frame and pre-failure flag; clock premise explicit; TX/provider bodies NOT executed')


if __name__ == '__main__':
    verify(IMAGE.read_bytes())
