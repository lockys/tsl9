"""Complete original a2ee branch boundaries; conditional A204 return explicit.

No unknown callee/provider code executes. Full-table registration chains return
naturally; inputs outside the known event caller's 0..15 domain are direct probes.
"""
from hashlib import sha256
from itertools import product
from test_v4160_task_event_cpu import (TaskEvent,initialize as init_event,segment,
    prepare as prepare_event,entry as event_entry,post_schedule,finish,schedule,
    HANDLER,GP,CONFIG,MODE,S_REGS)
from test_v4160_register_gate_cpu import rows,register,REGISTER
from test_v4160_feature_outer_cpu import registers,APP_HASH
from test_v4160_zero_id_queue_cpu import IMAGE,BASE,MASK,check

LOCAL,ALT,KEY = 0xa204,0x10816,0x9f74
PENDING,COUNTER,READY = GP+175,GP+176,GP+195


class Action(TaskEvent):
    CODE_RANGES = TaskEvent.CODE_RANGES+((0xa316,0xa372),(0x821e,0x8248))


def initialize(c):
    init_event(c)
    c.regions.extend(((GP+192,bytearray([0xa0,0xa1,0xa2,0]),True),
                      (COUNTER,bytearray([0,255]),True)))


def state(c,cfg3=0,cfg4=0,cfg5=1,ready=0,counter=0xcc):
    for a,v in ((CONFIG+3,cfg3),(CONFIG+4,cfg4),(CONFIG+5,cfg5),(READY,ready),
                (COUNTER,counter),(PENDING,0xdd),(GP+174,0x5a)):
        c.mem(a,1,v)


def fixture(c,value=1,mode=1,**kwargs):
    registers(c)
    c.reg[3],c.reg[10] = GP,value
    c.mem(MODE,1,mode)
    state(c,**kwargs)


def execute(c,local_reply=None,hook=()):
    before = c.reg[:]
    sp,resume,value = before[2],before[1],before[10]
    mode,cfg5 = c.mem(MODE,1),c.mem(CONFIG+5,1)
    expected = [('w',sp-8,4,before[8]),('w',sp-4,4,resume),('w',sp-12,4,before[9]),
                ('r',MODE,1,mode)]
    if mode != 1:
        expected += [('r',sp-8,4,before[8]),('r',sp-4,4,resume),('r',sp-12,4,before[9])]
        stop = segment(c,HANDLER,{LOCAL,ALT,REGISTER,resume,0xa312},expected,'action non-mode1')
        check(stop == ALT and c.reg[10] == value and (c.reg[1],c.reg[2]) == (resume,sp),
              'action alternate tail')
        check(all(c.reg[r] == before[r] for r in (3,4,*S_REGS)),'action alternate preservation')
        return 'alt'
    v = (cfg5 & 3)+1
    expected += [('r',GP+84,4,CONFIG),('r',CONFIG+5,1,cfg5)]
    stop = segment(c,HANDLER,{LOCAL,ALT,REGISTER,resume,0xa312},expected,'action prefix')
    check(stop == (LOCAL if v & 1 else 0xa312) and
          (c.reg[1],c.reg[2],c.reg[8],c.reg[9],c.reg[10]) ==
          (0xa312 if v & 1 else 0xa306,sp-16,value,v,value if v & 1 else v),
          'action local/prefix boundary')
    if v & 1:
        if local_reply is None: return 'local'
        # Declared local A204 normal return. Preserve live S0/S1/SP/GP/frame;
        # config/ready/counter mutations, if present, are explicit hook effects.
        c.trace_active = False
        for a,x in hook:
            check(a in (CONFIG+3,CONFIG+4,READY,COUNTER,PENDING),'action hook address')
            c.mem(a,1,x)
        for r in (1,5,6,7,*range(10,18),*range(28,32)):
            c.put(r,0xcafe0000+r*0x101)
        c.put(10,local_reply)
    cfg3,cfg4,ready,counter,pending = (c.mem(a,1) for a in
        (CONFIG+3,CONFIG+4,READY,COUNTER,PENDING))
    expected = []
    tail = False
    result = local_reply if v == 1 else 4
    if v & 2:
        expected += [('r',GP+84,4,CONFIG),('r',CONFIG+4,1,cfg4)]
        if not cfg4 & 8: expected.append(('r',READY,1,ready))
        result = int(not cfg4 & 8 and ready < 3)
        if result and value:
            expected += [('r',GP+84,4,CONFIG),('r',CONFIG+3,1,cfg3)]
            tail = cfg3 & 15 != 15
    if tail:
        expected += [('r',COUNTER,1,counter),('r',sp-8,4,before[8]),
                     ('w',COUNTER,1,(counter+1)&3),('r',sp-4,4,resume),
                     ('r',sp-12,4,before[9]),('w',PENDING,1,1)]
    else:
        expected += [('r',sp-4,4,resume),('r',sp-8,4,before[8]),('r',sp-12,4,before[9])]
    stop = segment(c,0xa312,{LOCAL,ALT,REGISTER,resume},expected,'action continuation')
    check(stop == (REGISTER if tail else resume),'action continuation endpoint')
    check((c.reg[1],c.reg[2]) == (resume,sp) and
          all(c.reg[r] == before[r] for r in (3,4,*S_REGS)),'action restored frame')
    if tail:
        check(c.reg[10:14] == [KEY,0,(value*1000)&MASK,0],'action registration arguments')
    else: check(c.reg[10] == result,'action return A0')
    check(c.mem(COUNTER,1) == ((counter+1)&3 if tail else counter) and
          c.mem(PENDING,1) == (1 if tail else pending) and
          c.mem(COUNTER+1,1) == 255 and c.mem(GP+174,1) == 0x5a and
          c.mem(GP+192,3) == 0xa2a1a0,'action state/canaries')
    return 'register' if tail else 'return'


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == APP_HASH,'firmware identity')
    c = Action(image)
    initialize(c)
    modes = 0
    for mode,value in product(range(256),(0,1,15,0x80000000,MASK)):
        fixture(c,value,mode)
        execute(c)
        modes += 1
    configs = 0
    for cfg5,value,ready,cfg4,cfg3 in product(range(256),(0,1,MASK),(0,2,3,255),(0,8),(0,15)):
        fixture(c,value,cfg5=cfg5,ready=ready,cfg4=cfg4,cfg3=cfg3)
        execute(c)
        configs += 1
    for cfg4,ready in product(range(256),repeat=2):
        fixture(c,cfg4=cfg4,ready=ready)
        execute(c)
    for cfg3,value in product(range(256),(0,1,MASK)):
        fixture(c,value,cfg3=cfg3)
        execute(c)
    for counter,value in product(range(256),(1,15,0x80000000,MASK)):
        fixture(c,value,counter=counter)
        check(execute(c) == 'register','counter registration path')
    hypotheses = 0
    for cfg5,reply,cfg4,ready,value,cfg3 in product((0,2),(0,1,0xdeadbeef,MASK),
                                                 (0,8),(0,3,255),(0,1,MASK),(0,15)):
        fixture(c,value,cfg5=cfg5,cfg4=cfg4,ready=ready,cfg3=cfg3)
        execute(c,local_reply=reply)
        hypotheses += 1
    hooks = 0
    for reply,counter in product((0,MASK),(0,3,255)):
        fixture(c,15,cfg5=2,cfg4=8,ready=255,cfg3=15)
        check(execute(c,local_reply=reply,hook=((CONFIG+4,0),(READY,0),(CONFIG+3,0),
              (COUNTER,counter),(PENDING,12))) == 'register','fresh local-return controls')
        hooks += 1
    # Direct word probes include nonzero values whose *1000 wraps to zero.
    # The known event caller supplies only config8-low4 (possibly capped at3).
    values = (*range(1,16),0x1000000,0x20000000,0x80000000,MASK)
    chains = dict.fromkeys(('immediate','call','free','full'),0)
    for index,value,layout in product(range(15),values,('new','existing','old','full')):
        changes = [] if layout == 'full' else [(index,0 if layout == 'new' else KEY,
                                               1 if layout == 'old' else 0)]
        rows(c,changes)
        fixture(c,value)
        check(execute(c) == 'register','original registration chain')
        kind,_ = register(c)
        want = 'full' if layout == 'full' else 'free' if layout == 'old' else (
            'immediate' if layout == 'new' and not (value*1000)&MASK else 'call')
        check(kind == want,'registration chain endpoint')
        chains[kind] += 1
        check(c.mem(PENDING,1) == 1 and c.mem(COUNTER,1) == 1,'state committed before registration outcome')
    # Actual caller -> disabled scheduler -> post-config -> A2EE -> full-table
    # registration return -> caller epilogue. No opaque return hypothesis.
    event_chains = 0
    for cfg3,value in product((0,14,15),range(1,16)):
        rows(c)
        prepare_event(c,0x80000003,enabled=0,config3=cfg3,config8=value)
        state(c,cfg3=cfg3)
        kind,before = event_entry(c)
        check(kind == 'schedule' and schedule(c,sample=None)[0] == 'return','event schedule early return')
        post_schedule(c,before)
        outcome = execute(c)
        if outcome == 'register': check(register(c) == ('full',None),'event full table natural return')
        else: check(outcome == 'return','event action natural return')
        finish(c,before,1,0x17300)
        event_chains += 1
    mutations = 0
    for addr,old,new,which,message in (
        (0x8240,'93b73700','93b72700','ready','action continuation accesses'),
        (0xa340,'8d8b','9d8b','counter','action continuation accesses'),
        (0xa34e,'a387f10a','a387010a','pending','action continuation accesses'),
        (0xa35a,'1305e5c1','130505c2','key','action registration arguments')):
        off = addr-BASE
        check(image[off:off+len(bytes.fromhex(old))] == bytes.fromhex(old),'action mutation pin')
        mutant = bytearray(image)
        mutant[off:off+len(bytes.fromhex(old))] = bytes.fromhex(new)
        d = Action(mutant)
        initialize(d)
        fixture(d,ready=2 if which == 'ready' else 0,counter=3)
        try: execute(d)
        except RuntimeError as error:
            check(str(error) == message,'unexpected action mutation failure: '+str(error))
            mutations += 1
        else: raise RuntimeError('action mutation escaped')
    print('PASS: %d full-mode/value cases; %d config5 branches; 65536 readiness-byte pairs; 768 config3/value cases; 1024 counter/word cases' % (modes,configs))
    print('PASS: %d declared A204 returns; %d fresh-control hooks; original A2EE-to-9124 chains %s; %d full event/caller natural returns; %d mutations' % (hypotheses,hooks,chains,event_chains,mutations))
    print('PASS: exact stores/read order/frame; wrapped-zero duration and pre-failure state retained; unknown callees/providers NOT executed')


if __name__ == '__main__':
    verify(IMAGE.read_bytes())
