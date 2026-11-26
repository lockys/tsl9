"""Original timer scaling, callback removal and fe6a post-time paths.
Only the raw timer target may receive an explicit scalar normal return.
Free/event targets always stop before execution; no physical device operations.
"""
from hashlib import sha256
from itertools import product,combinations
from test_v4160_downstream_gates_cpu import (Downstream,initialize as init_downstream,
    setup,feature,GP,CONFIG,STATE,TIMER,CALLBACK)
from test_v4160_feature_outer_cpu import registers,APP_HASH
from test_v4160_zero_id_queue_cpu import IMAGE,BASE,RETURN,MASK,check

RAW,FREE,EVENT = 0x30000b00,0x30000b04,0x30000b08
TABLE,TASK = 0x2000be08,GP+166
FIRST,SECOND = 0xfb1e,0xfb5e


class Services(Downstream):
    CODE_RANGES = Downstream.CODE_RANGES+((TIMER,0x81ca),(CALLBACK,0x9124))


def initialize(c):
    init_downstream(c)
    c.regions.extend(((0x4007c,bytearray(RAW.to_bytes(4,'little')),False),
                      (0x40068,bytearray(FREE.to_bytes(4,'little')),False),
                      (0x4005c,bytearray(EVENT.to_bytes(4,'little')),False),
                      (TABLE,bytearray(180),True),(TASK,bytearray([0]),True)))


def table(c,entries=(),task=0xa5):
    data = bytearray()
    for index in range(15):
        data += (0xaabb0000+index).to_bytes(4,'little')
        data += (0x51000000+index).to_bytes(4,'little')+bytes(4)
    for index,key,payload in entries:
        data[index*12+4:index*12+12] = key.to_bytes(4,'little')+payload.to_bytes(4,'little')
    c.mem(TABLE,180,int.from_bytes(data,'little'))
    c.mem(TASK,1,task)


def scale(raw):
    return ((raw*10) & MASK)//16


def timer(c,raw):
    before = c.reg[:]
    sp,resume = before[2],before[1]
    c.events,c.trace_active = [],True
    c.writes.clear()
    check(c.run(TIMER,{RAW,resume}) == RAW and (c.reg[10],c.reg[1],c.reg[2]) ==
          (before[10],0x81bc,sp-16), 'raw timer call boundary')
    check(c.events == [('r',0x4007c,4,RAW),('w',sp-4,4,resume)], 'raw timer pre-call effects')
    # Explicit normal-return hypothesis: preserve SP/S/GP and all memory.
    # Caller-saved registers are deliberately clobbered, including RA.
    for reg in (1,5,6,7,*range(10,18),*range(28,32)):
        c.put(reg,0xcafe0000+reg*0x101)
    c.put(10,raw)
    check(c.run(0x81bc,{resume}) == resume, 'timer wrapper return')
    c.trace_active = False
    check(c.events == [('r',0x4007c,4,RAW),('w',sp-4,4,resume),('r',sp-4,4,resume)], 'timer exact accesses')
    check(c.writes == [(sp-4,4,resume)], 'timer exact stores')
    check((c.reg[1],c.reg[2],c.reg[10]) == (resume,sp,scale(raw)), 'timer wrapped scaling')
    check(all(c.reg[i] == before[i] for i in (0,3,4,8,9,*range(18,28))) and not c.calls,
          'timer declared preservation/no provider')


def cancel(c):
    before = c.reg[:]
    sp,s0,s1,resume,key = before[2],before[8],before[9],before[1],before[10]
    data = c.mem(TABLE,180).to_bytes(180,'little')
    task = c.mem(TASK,1)
    index = next((i for i in range(15) if int.from_bytes(data[i*12+4:i*12+8],'little') == key),None)
    expected = [('w',sp-8,4,s0),('w',sp-12,4,s1),('w',sp-4,4,resume)]
    for i in range(15 if index is None else index+1):
        expected.append(('r',TABLE+12*i+4,4,int.from_bytes(data[i*12+4:i*12+8],'little')))
    model = bytearray(data)
    if index is None:
        kind,endpoint = 'miss',resume
        expected.extend((('r',sp-4,4,resume),('r',sp-8,4,s0),('r',sp-12,4,s1)))
    else:
        row = TABLE+12*index
        payload = int.from_bytes(data[index*12+8:index*12+12],'little')
        expected.append(('r',row+8,4,payload))
        if payload:
            kind,endpoint = 'free',FREE
            expected.append(('r',0x40068,4,FREE))
        else:
            kind,endpoint = 'event',EVENT
            expected.extend((('r',sp-8,4,s0),('r',sp-4,4,resume),('r',TASK,1,task),
                             ('w',row+4,4,0),('w',row+8,4,0),('r',0x4005c,4,EVENT),('r',sp-12,4,s1)))
            model[index*12+4:index*12+12] = bytes(8)
    c.events,c.trace_active = [],True
    c.writes.clear()
    check(c.run(CALLBACK,{FREE,EVENT,resume}) == endpoint, 'callback removal endpoint')
    c.trace_active = False
    check(c.events == expected, 'callback exact accesses')
    check(c.writes == [(a,n,v) for op,a,n,v in expected if op == 'w'], 'callback exact stores')
    check(c.mem(TABLE,180).to_bytes(180,'little') == model, 'callback table/canary')
    if kind == 'free':
        check((c.reg[1],c.reg[2],c.reg[8],c.reg[9],c.reg[10]) ==
              (0x90e0,sp-16,index,TABLE,payload), 'callback pre-free contract')
    else:
        check((c.reg[1],c.reg[2],c.reg[8],c.reg[9],c.reg[10],c.reg[11]) ==
              (resume,sp,s0,s1,1 if kind == 'miss' else task,before[11] if kind == 'miss' else 1 << index),
              'callback restored return/event contract')
    check(all(c.reg[i] == before[i] for i in range(32) if i not in (1,2,6,8,9,10,11,13,14,15)) and not c.calls,
          'callback unused registers/no provider')
    return kind,index


def finish_callbacks(c,resume,activation,caller):
    counts = 0
    for key,continuation in ((FIRST,0xfece if activation else 0xff2e),(SECOND,0xfeda if activation else 0xff3a)):
        check(c.reg[10] == key and c.reg[1] == continuation, 'feature callback key/link')
        kind,_ = cancel(c)
        counts += 1
        if kind != 'miss':
            return kind,counts
        c.events,c.trace_active = [],True
        c.writes.clear()
        stop = c.run(continuation,{CALLBACK,resume})
        c.trace_active = False
        if key == FIRST:
            check(stop == CALLBACK and not c.events and not c.writes, 'feature second callback reached despite first miss')
        else:
            check(stop == resume, 'feature callback completion return')
            sp,s0,s1 = caller
            expected = [('w',GP+288,1,2 if activation else 1),
                        ('w',GP+(291 if activation else 292),1,0),
                        ('r',sp-4,4,resume),('r',sp-8,4,s0),('r',sp-12,4,s1)]
            check(c.events == expected and c.writes == [(a,n,v) for op,a,n,v in expected if op == 'w'],
                  'feature post-callback stores/epilogue')
    return 'return',counts


def continuation(c,raw=None):
    before = c.reg[:]
    sp,s0,s1,resume,value = before[2],before[8],before[9],before[1],before[10]
    initial = c.mem(STATE,20).to_bytes(20,'little')
    flags,pending = c.mem(CONFIG+9,1),c.mem(GP+291,1)
    stamp = c.mem(GP+296,4)
    path = feature(c)
    model = bytearray(initial)
    if path == 'return':
        if not value and c.mem(GP+292,1) == 0:
            model[292-284] = 0
        check(c.mem(STATE,20).to_bytes(20,'little') == model, 'feature early-return state')
        return 'early',0
    if path == 'timer':
        check(raw is not None, 'raw fixture required')
        phase = c.reg[1]
        timer(c,raw)
        now = scale(raw)
        c.events,c.trace_active = [],True
        c.writes.clear()
        stop = c.run(phase,{CALLBACK,resume})
        c.trace_active = False
        if phase == 0xff00:
            elapsed = (now-stamp) & MASK
            expected = [('r',GP+296,4,stamp)]
            if elapsed > 1499:
                expected.append(('w',GP+292,1,0))
                model[292-284] = 0
            expected.extend((('r',sp-4,4,resume),('r',sp-8,4,s0),('r',sp-12,4,s1)))
            check(stop == resume and c.events == expected and c.reg[10] == elapsed, 'feature elapsed boundary')
            check((c.reg[1],c.reg[2],c.reg[8],c.reg[9]) == (resume,sp,s0,s1), 'feature elapsed frame')
            check(c.mem(STATE,20).to_bytes(20,'little') == model, 'feature elapsed state/canary')
            return 'elapsed',0
        check(phase == 0xfea8 and stop == CALLBACK, 'feature activation callback boundary')
        flag = 1 if pending else (flags >> 2) & 3
        expected = [('w',GP+296,4,now),('r',GP+291,1,pending)]
        if not pending:
            expected.extend((('r',GP+84,4,CONFIG),('r',CONFIG+9,1,flags)))
        expected.append(('w',GP+292,1,flag))
        check(c.events == expected, 'feature activation write/read order')
        model[296-284:300-284] = now.to_bytes(4,'little')
        model[292-284] = flag
        activation = True
    else:
        activation = False
    kind,calls = finish_callbacks(c,resume,activation,(sp,s0,s1))
    if kind == 'return':
        if activation:
            model[288-284],model[291-284] = 2,0
        else:
            model[288-284],model[292-284] = 1,0
        check((c.reg[1],c.reg[2],c.reg[8],c.reg[9],c.reg[10]) == (resume,sp,s0,s1,1), 'feature completed caller')
    check(c.mem(STATE,20).to_bytes(20,'little') == model, 'feature callback state/canary')
    return kind,calls


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == APP_HASH, 'APP identity')
    c = Services(image)
    initialize(c)
    for raw in range(65536):
        registers(c)
        c.reg[3] = GP
        timer(c,raw)
    edges = (MASK,0x19999999,0x1999999a,0x80000000)+tuple(1 << i for i in range(32))
    for raw in edges:
        registers(c)
        c.reg[3] = GP
        timer(c,raw)
    for index,task,key in product(range(15),range(256),(0,FIRST,MASK)):
        registers(c)
        c.reg[3],c.reg[10] = GP,key
        table(c,((index,key,0),),task)
        check(cancel(c) == ('event',index), 'callback selected index')
    for index,key,payload in product(range(15),(0,FIRST,MASK),(1,0x29000000,MASK)):
        registers(c)
        c.reg[3],c.reg[10] = GP,key
        table(c,((index,key,payload),))
        check(cancel(c) == ('free',index), 'callback free index')
    for task,key in product(range(256),(0,FIRST,MASK)):
        registers(c)
        c.reg[3],c.reg[10] = GP,key
        table(c,task=task)
        check(cancel(c) == ('miss',None), 'callback no match')
    for (first,second),key in product(combinations(range(15),2),(0,FIRST,MASK)):
        registers(c)
        c.reg[3],c.reg[10] = GP,key
        table(c,((first,key,0),(second,key,0)))
        check(cancel(c) == ('event',first), 'callback duplicate first')
        registers(c)
        c.reg[3],c.reg[10] = GP,key
        check(cancel(c) == ('event',first if key == 0 else second), 'callback duplicate repeated')
    for address,before,after,which in (
        (0x81bc,'a947','a547','timer'),
        (0x90c4,'3d47','3947','scan'),
        (0x90e6,'8545','8945','mask'),
    ):
        mutant = bytearray(image)
        offset = address-BASE
        check(mutant[offset:offset+len(bytes.fromhex(before))] == bytes.fromhex(before), 'service mutation pin')
        mutant[offset:offset+len(bytes.fromhex(after))] = bytes.fromhex(after)
        probe = Services(mutant)
        initialize(probe)
        registers(probe)
        probe.reg[3],probe.reg[10] = GP,FIRST
        table(probe,((14 if which == 'scan' else 0,FIRST,0),))
        try:
            timer(probe,16) if which == 'timer' else cancel(probe)
        except RuntimeError as exc:
            wanted = 'timer wrapped scaling' if which == 'timer' else 'callback removal endpoint' if which == 'scan' else 'callback restored return/event contract'
            check(str(exc) == wanted, 'unexpected service mutation failure: '+str(exc))
        else:
            raise RuntimeError('service mutation undetected')
    print(f'PASS: 65536 timer inputs + {len(edges)} wrap/basis probes; 11520 callback removals; '
          '135 pre-free stops; 768 misses; 315 duplicate/repeated pairs; 3 mutations; free/event NOT executed')


def composition(image):
    c = Services(image)
    initialize(c)
    activation = elapsed = deletion = pending_calls = 0
    raw_values = (0,16,MASK,0x1999999a)
    for flags,pending,raw,kind,value in product((4,8,12,255),range(256),raw_values,(1,7),(1,MASK)):
        setup(c,value,flags=flags,kind=kind,active=0)
        c.mem(GP+291,1,pending)
        table(c)
        check(continuation(c,raw) == ('return',2), 'complete activation with absent keys')
        activation += 1
    for raw,delta,active in product(raw_values,range(2048),(1,255)):
        setup(c,1,kind=0,active=active,stage=0,event=0)
        c.mem(GP+296,4,(scale(raw)-delta)&MASK)
        table(c)
        check(continuation(c,raw) == ('elapsed',0), 'elapsed delta sweep')
        elapsed += 1
    for raw,delta in product(raw_values,(MASK,0x80000000,0xfffffff0)):
        setup(c,1,kind=0,active=1,stage=0,event=0)
        c.mem(GP+296,4,(scale(raw)-delta)&MASK)
        table(c)
        continuation(c,raw)
        elapsed += 1
    for flags,stage in product((4,8,12,255),range(256)):
        setup(c,0,flags=flags,active=2,stage=stage)
        table(c)
        check(continuation(c) == ('return',2), 'deactivation despite absent keys')
        deletion += 1
    for activate,index,payload,key in product((False,True),(0,7,14),(0,0x29000000),(FIRST,SECOND)):
        setup(c,1 if activate else 0,kind=1,active=0 if activate else 2)
        table(c,((index,key,payload),))
        result,calls = continuation(c,16 if activate else None)
        check(result == ('free' if payload else 'event') and calls == (1 if key == FIRST else 2), 'feature pending removal boundary')
        pending_calls += 1
    print(f'PASS: {activation} full activations; {elapsed} unsigned elapsed checks; {deletion} deactivations; '
          f'{pending_calls} pending free/event boundaries; actual callback scans; explicit raw-timer return only')


if __name__ == '__main__':
    image = IMAGE.read_bytes()
    verify(image)
    composition(image)
