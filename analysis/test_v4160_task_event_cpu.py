"""Original 172b6 task event, natural a2ee return, and 9fb2 -> 17320.

Offline synthetic state/events only. Unknown sample/event/local callees stop at
entry; only the separately labelled bit1 normal-return probe uses a hypothesis.
"""
from hashlib import sha256
from itertools import product
from test_v4160_callback_dispatch_cpu import Callbacks,callback
from test_v4160_register_gate_cpu import initialize as init_callbacks,gate_fixture,IMMEDIATE
from test_v4160_schedule_171de_cpu import (execute as schedule,ENTRY as SCHEDULE,
    ENABLE,EXTRA,FLAG,TASK,GP,CONFIG)
from test_v4160_feature_outer_cpu import registers,APP_HASH,MODE
from test_v4160_zero_id_queue_cpu import IMAGE,BASE,MASK,check

EVENT,HANDLER,BIT1,PENDING,KICK = 0x172b6,0xa2ee,0x13d48,GP+174,0x17320
S_REGS = (8,9,*range(18,28))


class TaskEvent(Callbacks):
    CODE_RANGES = Callbacks.CODE_RANGES+((EVENT,0x17344),(0x9fb2,0x9fc2),
                                        (HANDLER,0xa316),(0xa372,0xa37c),(0x81de,0x81ee))


def initialize(c):
    init_callbacks(c)
    c.regions.append((PENDING,bytearray([0,255]),True))


def segment(c,start,stops,expected,label):
    c.events,c.trace_active = [],True
    c.writes.clear()
    stop = c.run(start,stops)
    c.trace_active = False
    check(c.events == expected,label+' accesses')
    check(c.writes == [(a,n,v) for op,a,n,v in expected if op == 'w'],label+' stores')
    check(not c.calls,label+' no provider execution')
    return stop


def prepare(c,mask=1,enabled=0,config3=15,config8=15,mode=1,extra=1,flag=0):
    registers(c)
    c.reg[3],c.reg[11] = GP,mask
    for a,v in ((ENABLE,enabled),(CONFIG+3,config3),(CONFIG+8,config8),
                (CONFIG+5,3),(MODE,mode),(EXTRA,extra),(TASK,17)):
        c.mem(a,1,v)
    if flag is not None: c.mem(FLAG,1,flag)


def entry(c):
    before = c.reg[:]
    sp,resume,mask = before[2],before[1],before[11]
    expected = [('w',sp-12,4,before[9]),('w',sp-4,4,resume),('w',sp-8,4,before[8])]
    kind = 'schedule' if mask & 1 else 'bit1' if mask & 2 else 'none'
    target = SCHEDULE if kind == 'schedule' else BIT1 if kind == 'bit1' else resume
    if kind == 'none':
        expected += [('r',sp-4,4,resume),('r',sp-8,4,before[8]),('r',sp-12,4,before[9])]
    check(segment(c,EVENT,{SCHEDULE,BIT1,resume},expected,'task entry') == target,'task entry endpoint')
    if kind == 'none':
        check(c.reg[10] == 0 and all(c.reg[i] == before[i] for i in (1,2,3,4,*S_REGS)),
              'task empty return')
    else:
        check((c.reg[1],c.reg[2],c.reg[8],c.reg[9],c.reg[10]) ==
              (0x172ca if kind == 'schedule' else 0x1731a,sp-16,before[8],mask,
               before[10] if kind == 'schedule' else 0),'task callee entry')
    return kind,before


def finish(c,before,bit,start):
    sp,resume,mask = before[2],before[1],before[11]
    expected = [('r',sp-4,4,resume),('r',sp-8,4,before[8]),('r',sp-12,4,before[9])]
    check(segment(c,start,{resume},expected,'task finish') == resume and
          c.reg[10] == mask ^ bit,'task full-word remaining mask')
    check(all(c.reg[r] == before[r] for r in (1,2,3,4,*S_REGS)),'task restored frame')


def post_schedule(c,before,natural=False):
    sp,resume,mask = before[2],before[1],before[11]
    config3,config8,mode = (c.mem(a,1) for a in (CONFIG+3,CONFIG+8,MODE))
    value = config8 & 15
    expected = [('r',GP+84,4,CONFIG),('r',CONFIG+8,1,config8),('r',CONFIG+3,1,config3)]
    if config3 & 15 == 15:
        expected.append(('r',MODE,1,mode))
        if mode == 1: value = min(value,3)
    check(segment(c,0x172ca,{HANDLER},expected,'task post-schedule') == HANDLER and
          (c.reg[10],c.reg[1],c.reg[2],c.reg[8],c.reg[9]) ==
          (value,0x17300,sp-16,value,mask),'task handler argument/clamp')
    if natural:
        # Actual mode1/config5-low2=3 -> V=4 path: no invented callee return.
        config5 = c.mem(CONFIG+5,1)
        check(mode == 1 and config5 & 3 == 3,'natural handler fixture')
        inner_sp = sp-16
        expected = [('w',inner_sp-8,4,value),('w',inner_sp-4,4,0x17300),
                    ('w',inner_sp-12,4,mask),('r',MODE,1,mode),
                    ('r',GP+84,4,CONFIG),('r',CONFIG+5,1,config5),
                    ('r',inner_sp-4,4,0x17300),('r',inner_sp-8,4,value),
                    ('r',inner_sp-12,4,mask)]
        check(segment(c,HANDLER,{0x17300},expected,'task natural handler') == 0x17300 and
              (c.reg[10],c.reg[2],c.reg[8],c.reg[9]) == (4,sp-16,value,mask),
              'task natural handler return')
        finish(c,before,1,0x17300)
    return value


def event(c,natural=False):
    kind,before = entry(c)
    if kind != 'schedule': return kind
    outcome,_ = schedule(c,sample=None)
    if outcome == 'sample': return 'sample'
    check(outcome == 'return','task bounded schedule outcome')
    post_schedule(c,before,natural)
    return 'natural' if natural else 'handler'


def kick(c,pending_entry=True):
    before = c.reg[:]
    sp,resume = before[2],before[1]
    pending,enabled,task = (c.mem(a,1) for a in (PENDING,ENABLE,TASK))
    expected = [('r',PENDING,1,pending)] if pending_entry else []
    active = not pending_entry or bool(pending)
    if pending_entry and pending: expected.append(('w',PENDING,1,0))
    if active:
        expected += [('w',sp-4,4,resume),('r',ENABLE,1,enabled),('r',sp-4,4,resume)]
        if enabled: expected += [('r',0x40050,4,IMMEDIATE),('r',TASK,1,task)]
    target = IMMEDIATE if active and enabled else resume
    check(segment(c,0x9fb2 if pending_entry else KICK,{target},expected,'task kick') == target,
          'task kick endpoint')
    check((c.reg[1],c.reg[2]) == (resume,sp) and
          all(c.reg[r] == before[r] for r in range(32) if r not in (6,10,11,15)) and
          c.reg[6] == (IMMEDIATE if active and enabled else before[6]),
          'task kick preserved registers')
    check(c.reg[10] == (task if enabled else 0) if active else c.reg[10] == before[10],
          'task kick A0')
    check(c.reg[11] == (1 if active and enabled else before[11]) and
          c.mem(PENDING,1) == (0 if pending_entry else pending) and c.mem(PENDING+1,1) == 255,
          'task kick flag/arguments/canary')
    return active and bool(enabled)


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == APP_HASH,'firmware identity')
    c = TaskEvent(image)
    initialize(c)
    counts = dict.fromkeys(('schedule','bit1','none'),0)
    for mask in range(65536):
        prepare(c,mask)
        kind,_ = entry(c)
        counts[kind] += 1
    check(counts == {'schedule':32768,'bit1':16384,'none':16384},'task priority distribution')
    clamps = 0
    for cfg3,cfg8,mode in product(range(256),(0,3,4,15,16,255),(0,1,2,255)):
        prepare(c,0x80008003,config3=cfg3,config8=cfg8,mode=mode)
        check(event(c,natural=mode == 1) == ('natural' if mode == 1 else 'handler'),'task clamp route')
        clamps += 1
    for cfg8,mode in product(range(256),range(256)):
        # Direct original post-call block with the frame from actual entry and
        # actual disabled 171de; covers full mode byte and config8 matrix.
        prepare(c,0xffff0001,config8=cfg8,mode=mode)
        check(event(c) == 'handler','task full mode/config8 route')
    gates = dict.fromkeys(('sample','handler'),0)
    for enabled,extra,flags,flag in product((0,1,255),(0,1,255),range(256),(0,1,255)):
        prepare(c,1,enabled=enabled,extra=extra,config8=flags,flag=flag)
        outcome = event(c)
        gates[outcome] += 1
    chains = 0
    for flags,ready,k in product((0,16),(0,1,255),range(256)):
        gate_fixture(c,flags,ready,k)
        value,_ = callback(c)
        # Explicit sequential event input, no claim that the callback emitted it.
        prepare(c,1,enabled=1,config8=16,flag=None)
        result = event(c,natural=not value)
        check(result == ('sample' if value else 'natural'),'callback flag to task gate')
        chains += 1
    bit1_returns = 0
    for mask in (2,6,0x80000002,0xfffffffe):
        prepare(c,mask)
        kind,before = entry(c)
        check(kind == 'bit1','bit1 return fixture')
        # Explicit local-callee normal return: preserve live S1/SP/GP/frame;
        # clobber caller-saved state and S0, which the outer epilogue reloads.
        for r in (1,5,6,7,8,*range(10,18),*range(28,32)):
            c.put(r,0xcafe0000+r*0x101)
        finish(c,before,2,0x1731a)
        bit1_returns += 1
    kicks = 0
    for pending,enabled in product(range(256),repeat=2):
        prepare(c,enabled=enabled)
        c.mem(PENDING,1,pending)
        kick(c)
        kicks += 1
    for enabled,task in product(range(256),repeat=2):
        prepare(c,enabled=enabled)
        c.mem(TASK,1,task)
        c.mem(PENDING,1,255)
        kick(c,pending_entry=False)
    mutations = 0
    for addr,old,new,which,message in (
        (0x172be,'93f71500','93f74500','priority','task entry endpoint'),
        (0x172f4,'8d47','8947','clamp','task handler argument/clamp'),
        (0x17300,'13c51400','13c52400','return','task full-word remaining mask'),
        (0x9fb8,'2387010a','a387010a','kick','task kick accesses')):
        off = addr-BASE
        check(image[off:off+len(bytes.fromhex(old))] == bytes.fromhex(old),'task mutation pin')
        mutant = bytearray(image)
        mutant[off:off+len(bytes.fromhex(old))] = bytes.fromhex(new)
        d = TaskEvent(mutant)
        initialize(d)
        prepare(d,3 if which == 'priority' else 1)
        d.mem(PENDING,1,255)
        try:
            if which == 'kick': kick(d)
            else: event(d,natural=True)
        except RuntimeError as error:
            check(str(error) == message,'unexpected task mutation failure: '+str(error))
            mutations += 1
        else: raise RuntimeError('task mutation escaped')
    print('PASS: 65536 event masks %s; %d config/clamp cases; 65536 full mode/config8 pairs; %d original gate chains %s' % (counts,clamps,sum(gates.values()),gates))
    print('PASS: %d callback/separate-event state chains; %d explicit bit1 returns; %d pending/enable pairs; 65536 direct enable/task pairs; %d mutations' % (chains,bit1_returns,kicks,mutations))
    print('PASS: mode1/config5-low2=3 handler returns by original instructions; exact accesses/stores/frame; providers NOT executed')


if __name__ == '__main__':
    verify(IMAGE.read_bytes())
