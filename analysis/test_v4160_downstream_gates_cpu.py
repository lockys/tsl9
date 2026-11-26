"""Original b6f4 first-call guard and fe6a until first opaque timer/callback.
Includes actual 828c/a9de/81ee getters; no device operations or synthetic returns.
"""
from hashlib import sha256
from itertools import product
from test_v4160_state_consumer_cpu import (Gate,initialize as init_gate,fixture as gate_fixture,
    execute as execute_gate,GP,SOURCE)
from test_v4160_feature_outer_cpu import registers,APP_HASH
from test_v4160_zero_id_queue_cpu import IMAGE,BASE,RETURN,MASK,check

GUARD,FOLLOW,FEATURE,TIMER,CALLBACK = 0xb6f4,0x171de,0xfe6a,0x81b0,0x90b0
READY_GETTER,TYPE_GETTER,EVENT_GETTER = 0x828c,0xa9de,0x81ee
READY,TYPE,CONFIG,STATE = 0x2000bfb4,0x2000bedc,0x23000000,GP+284


class Downstream(Gate):
    CODE_RANGES = Gate.CODE_RANGES+((GUARD,0xb730),(FEATURE,0xff44),
                                  (READY_GETTER,0x829e),(TYPE_GETTER,0xa9e8))


def initialize(c):
    init_gate(c)
    c.regions.extend(((GP+84,bytearray(CONFIG.to_bytes(4,'little')),False),
                      (CONFIG,bytearray(range(10)),True),(STATE,bytearray(range(20)),True),
                      (READY,bytearray([0]),True),(TYPE,bytearray([0,0xff]),True)))


def feature_fixture(c,flags,ready,kind,active,stage,event):
    c.mem(CONFIG,10,int.from_bytes(bytes(range(10)),'little'))
    c.mem(CONFIG+9,1,flags)
    c.mem(STATE,20,int.from_bytes(bytes(range(0xa0,0xb4)),'little'))
    for address,value in ((READY,ready),(TYPE,kind),(GP+292,active),(GP+288,stage),(SOURCE,event)):
        c.mem(address,1,value)


def feature(c):
    before = c.reg[:]
    sp,s0,s1,resume,value = before[2],before[8],before[9],before[1],before[10]
    flags,ready,kind,active,stage,event = (c.mem(address,1) for address in
        (CONFIG+9,READY,TYPE,GP+292,GP+288,SOURCE))
    state = c.mem(STATE,20).to_bytes(20,'little')
    expected = [('r',GP+84,4,CONFIG),('r',CONFIG+9,1,flags)]
    calls = []
    endpoint,a0,link = resume,value,resume
    framed = bool(flags & 12)
    if framed:
        expected.extend((('w',sp-8,4,s0),('w',sp-12,4,s1),('w',sp-4,4,resume),('r',READY,1,ready)))
        calls.append((READY_GETTER,value,0xfe8a,int(ready >= 4)))
        a0 = int(ready >= 4)
        if ready >= 4:
            if not value:
                expected.append(('r',GP+292,1,active))
                if active == 2:
                    endpoint,a0,link = CALLBACK,0xfb1e,0xff2e
                elif active:
                    expected.append(('w',GP+292,1,0))
            else:
                expected.extend((('r',TYPE,1,kind),('r',GP+292,1,active)))
                calls.append((TYPE_GETTER,1,0xfe92,kind))
                a0 = kind
                if kind in (1,7):
                    if not active:
                        endpoint,link = TIMER,0xfea8
                elif active:
                    expected.append(('r',GP+288,1,stage))
                    if not stage:
                        expected.append(('r',SOURCE,1,event))
                        calls.append((EVENT_GETTER,kind,0xfefa,event))
                        a0 = event
                        if not event:
                            endpoint,link = TIMER,0xff00
        if endpoint == resume:
            expected.extend((('r',sp-4,4,resume),('r',sp-8,4,s0),('r',sp-12,4,s1)))
    c.events,c.trace_active = [],True
    c.writes.clear()
    pc,seen = FEATURE,[]
    for _ in range(4):
        stop = c.run(pc,{READY_GETTER,TYPE_GETTER,EVENT_GETTER,TIMER,CALLBACK,resume})
        if stop not in (READY_GETTER,TYPE_GETTER,EVENT_GETTER):
            break
        index = len(seen)
        check(index < len(calls), 'unexpected downstream getter')
        target,incoming,continuation,result = calls[index]
        check(stop == target and (c.reg[10],c.reg[1],c.reg[2],c.reg[8],c.reg[9]) ==
              (incoming,continuation,sp-16,GP+84,value), 'downstream getter boundary')
        getter_regs,mark = c.reg[:],len(c.writes)
        check(c.run(target,{continuation}) == continuation and c.reg[10] == result and
              all(c.reg[i] == getter_regs[i] for i in range(32) if i != 10) and len(c.writes) == mark,
              'downstream getter result/preservation')
        seen.append(target)
        pc = continuation
    else:
        raise RuntimeError('downstream getter budget')
    c.trace_active = False
    check(stop == endpoint, 'downstream endpoint')
    check(seen == [target for target,_,_,_ in calls], 'downstream getter call count')
    check(c.events == expected, 'downstream exact data accesses')
    check(c.writes == [(a,n,v) for op,a,n,v in expected if op == 'w'], 'downstream exact stores')
    if endpoint == resume:
        check((c.reg[1],c.reg[2],c.reg[8],c.reg[9],c.reg[10]) ==
              (resume,sp,s0,s1,a0), 'downstream restored caller/A0')
    else:
        check((c.reg[1],c.reg[2],c.reg[8],c.reg[9],c.reg[10]) ==
              (link,sp-16,GP+84,value,a0), 'downstream opaque-call contract')
    check(all(c.reg[i] == before[i] for i in range(32) if i not in (1,2,8,9,10,14,15)),
          'downstream unused registers')
    model = bytearray(state)
    for op,address,size,byte in expected:
        if op == 'w' and STATE <= address < STATE+20:
            model[address-STATE] = byte
    check(c.mem(STATE,20).to_bytes(20,'little') == model and c.mem(TYPE+1,1) == 255 and not c.calls,
          'downstream state/canary/no provider')
    return 'return' if endpoint == resume else 'timer' if endpoint == TIMER else 'callback'


def guard(c):
    before = c.reg[:]
    value,sp,s0,resume = before[10],before[2],before[8],before[1]
    accepted = 1 <= (value & 255) <= 18
    expected = [('w',sp-8,4,s0),('w',sp-4,4,resume)] if accepted else []
    c.events,c.trace_active = [],True
    c.writes.clear()
    stop = c.run(GUARD,{FOLLOW,resume})
    c.trace_active = False
    check(stop == (FOLLOW if accepted else resume), 'guard endpoint')
    check(c.events == expected and c.writes == [(a,n,v) for _,a,n,v in expected], 'guard footprint')
    check((c.reg[1],c.reg[2],c.reg[8],c.reg[10]) ==
          ((0xb70e,sp-16,value,value) if accepted else (resume,sp,s0,value)), 'guard full-width call contract')
    check(all(c.reg[i] == before[i] for i in range(32) if i not in (1,2,8,14,15)) and not c.calls,
          'guard preserved registers/no provider')
    return accepted


def setup(c,value,flags=4,ready=4,kind=1,active=0,stage=0,event=0):
    registers(c)
    c.reg[3],c.reg[10] = GP,value
    feature_fixture(c,flags,ready,kind,active,stage,event)


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == APP_HASH, 'APP identity')
    c = Downstream(image)
    initialize(c)
    for prefix,low in product((0,0x100,0x10000,0x80000000,0xffffff00),range(256)):
        registers(c)
        c.reg[3],c.reg[10] = GP,prefix | low
        guard(c)
    for flags,ready,value in product(range(256),range(256),(0,1)):
        setup(c,value,flags=flags,ready=ready)
        feature(c)
    for kind,active,value in product(range(256),range(256),(0,1)):
        setup(c,value,kind=kind,active=active)
        feature(c)
    for stage,event in product(range(256),repeat=2):
        setup(c,1,kind=0,active=1,stage=stage,event=event)
        feature(c)
    for value,flags,ready,kind,active,stage,event in product((0x10000,MASK),(4,8,12,255),(3,4,255),(0,1,7,255),(0,1,2,255),(0,255),(0,255)):
        setup(c,value,flags,ready,kind,active,stage,event)
        feature(c)
    for address,before,after,which in (
        (0xfe74,'318b','218b','feature'),
        (0x8294,'13354500','13355500','getter'),
        (0xb6f8,'93f7f70f','93f7f707','guard'),
    ):
        mutant = bytearray(image)
        offset = address-BASE
        check(mutant[offset:offset+len(bytes.fromhex(before))] == bytes.fromhex(before), 'downstream mutation pin')
        mutant[offset:offset+len(bytes.fromhex(after))] = bytes.fromhex(after)
        probe = Downstream(mutant)
        initialize(probe)
        setup(probe,129 if which == 'guard' else 1)
        try:
            guard(probe) if which == 'guard' else feature(probe)
        except RuntimeError as exc:
            wanted = 'guard endpoint' if which == 'guard' else 'downstream getter result/preservation' if which == 'getter' else 'downstream endpoint'
            check(str(exc) == wanted, 'unexpected downstream mutation failure: '+str(exc))
        else:
            raise RuntimeError('downstream mutation undetected')
    print('PASS: 1280 guard aliases; 131072 config/readiness cases; 131072 type/active cases; '
          '65536 stage/event pairs; 1536 full-width probes; 3 mutations; actual getters; opaque callees NOT executed')


def composition(image):
    c = Downstream(image)
    initialize(c)
    outcomes = dict.fromkeys(('gate_return','guard_call','feature_return','feature_timer','feature_callback'),0)
    profiles = ((0,4,1,0,0),(4,3,1,0,0),(4,4,1,0,0),
                (4,4,7,1,0),(4,4,0,1,1),(4,4,0,1,0))
    for status,category,value,source,profile in product((0,1,5,7,10,255),(0,1,2,255),(0,1),(0,1,2,255),profiles):
        gate_fixture(c,value,category,source)
        feature_fixture(c,*profile,source)
        c.mem(GP+357,1,status)
        original_source = c.mem(SOURCE,1)
        path = execute_gate(c)
        check(c.mem(SOURCE,1) == original_source, 'shared getter source')
        if path == 'call':
            check(guard(c), 'actual gate always supplies 6/7')
            outcomes['guard_call'] += 1
        elif path == 'tail':
            outcomes['feature_'+feature(c)] += 1
        else:
            outcomes['gate_return'] += 1
    print(f'PASS: {sum(outcomes.values())} actual cd6a-to-downstream control-flow chains; {outcomes}; no SDK or callee return hypotheses')


if __name__ == '__main__':
    image = IMAGE.read_bytes()
    verify(image)
    composition(image)
