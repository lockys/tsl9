"""Original 9fc8 gate and 9124 callback registration/update, offline fixtures.
Free and tail providers stop before execution. Optional 40058 normal return is
explicit, preserves memory/SP/GP, and deliberately clobbers restored S0-S4.
"""
from hashlib import sha256
from itertools import product,combinations
from test_v4160_schedule_171de_cpu import (Schedule,initialize as init_schedule,
    fixture as schedule_fixture,execute as schedule,guard,GP,CONFIG,FLAG,FIRST as START)
from test_v4160_feature_outer_cpu import registers,APP_HASH
from test_v4160_zero_id_queue_cpu import IMAGE,BASE,RETURN,MASK,check

GATE,GETTER,REGISTER,KEY = 0x9fc8,0x8202,0x9124,0x9f7a
READY,TABLE,TASK = 0x2000bee1,0x2000be08,GP+166
FREE,IMMEDIATE,REPEAT = 0x30000d00,0x30000d04,0x30000d08
S_REGS = (8,9,18,19,20)


class Registration(Schedule):
    CODE_RANGES = Schedule.CODE_RANGES+((GATE,0xa00c),(GETTER,0x820c),(REGISTER,0x9250))


def initialize(c):
    init_schedule(c)
    c.regions.extend(((TABLE,bytearray(180),True),(TASK,bytearray([0xa5]),True),
                      (FLAG+1,bytearray([0xff]),True),
                      (0x40068,bytearray(FREE.to_bytes(4,'little')),False),
                      (0x40050,bytearray(IMMEDIATE.to_bytes(4,'little')),False),
                      (0x4022c,bytearray(REPEAT.to_bytes(4,'little')),False)))


def gate_fixture(c,flags=16,ready=1,k=0,old=0xcc):
    registers(c)
    c.reg[3] = GP
    for address,value in ((CONFIG+8,flags),(READY,ready),(GP+354,k),(FLAG,old)):
        c.mem(address,1,value)


def gate(c):
    before = c.reg[:]
    sp,resume = before[2],before[1]
    flags,ready,k = (c.mem(address,1) for address in (CONFIG+8,READY,GP+354))
    expected = [('w',FLAG,1,0),('r',GP+84,4,CONFIG),('r',CONFIG+8,1,flags)]
    used = bool(flags & 16)
    accepted = bool(used and ready and not k)
    if used:
        expected.extend((('w',sp-4,4,resume),('r',READY,1,ready)))
        if ready:
            expected.append(('r',GP+354,1,k))
        expected.append(('r',sp-4,4,resume))
    c.events,c.trace_active = [],True
    c.writes.clear()
    stop = c.run(GATE,{GETTER,REGISTER,resume})
    if used:
        check(stop == GETTER and (c.reg[1],c.reg[2],c.reg[10]) ==
              (0x9fe2,sp-16,before[10]), 'registration gate getter entry')
        regs,mark = c.reg[:],len(c.writes)
        check(c.run(GETTER,{0x9fe2}) == 0x9fe2 and c.reg[10] == ready and
              all(c.reg[i] == regs[i] for i in range(32) if i != 10) and len(c.writes) == mark,
              'registration gate actual getter')
        stop = c.run(0x9fe2,{REGISTER,resume})
    c.trace_active = False
    check(stop == (REGISTER if accepted else resume), 'registration gate endpoint')
    check(c.events == expected, 'registration gate exact accesses')
    check(c.writes == [(a,n,v) for op,a,n,v in expected if op == 'w'], 'registration gate stores')
    check((c.reg[1],c.reg[2]) == (resume,sp), 'registration gate restored frame')
    args = [KEY,0,10000,0] if accepted else [ready if used else before[10],*before[11:14]]
    check(c.reg[10:14] == args, 'registration gate arguments')
    check(all(c.reg[i] == before[i] for i in range(32) if i not in (1,2,10,11,12,13,15)) and
          c.mem(FLAG,1) == 0 and c.mem(FLAG+1,1) == 255 and not c.calls, 'registration gate preservation/canary')
    return accepted


def rows(c,changes=(),task=0xa5):
    data = bytearray()
    for index in range(15):
        data += (0xaabb0000+index).to_bytes(4,'little')
        data += (0x51000000+index).to_bytes(4,'little')+bytes(4)
    for index,key,payload in changes:
        data[index*12+4:index*12+12] = key.to_bytes(4,'little')+payload.to_bytes(4,'little')
    c.mem(TABLE,180,int.from_bytes(data,'little'))
    c.mem(TASK,1,task)


def register(c,reply=None):
    before = c.reg[:]
    sp,resume = before[2],before[1]
    key,flag,duration,payload = before[10:14]
    saved = {reg:before[reg] for reg in S_REGS}
    offsets = {8:8,9:12,18:16,19:20,20:24}
    data = c.mem(TABLE,180).to_bytes(180,'little')
    keys = [int.from_bytes(data[i*12+4:i*12+8],'little') for i in range(15)]
    task = c.mem(TASK,1)
    expected = [('w',sp-16,4,before[18]),('w',sp-4,4,resume),('w',sp-8,4,before[8]),
                ('w',sp-12,4,before[9]),('w',sp-20,4,before[19]),('w',sp-24,4,before[20])]
    model = bytearray(data)
    empty = next((i for i,k in enumerate(keys) if not k),None)
    quick = duration == 0 and empty is not None
    def scan(limit):
        expected.extend(('r',TABLE+i*12+4,4,keys[i]) for i in range(limit))
    def restore(reg): expected.append(('r',sp-offsets[reg],4,saved[reg]))
    def write(address,size,value):
        expected.append(('w',address,size,value & ((1 << (size*8))-1)))
        model[address-TABLE:address-TABLE+size] = (value & ((1 << (size*8))-1)).to_bytes(size,'little')
    if duration == 0:
        scan(15 if empty is None else empty+1)
    existing = False
    if quick:
        index,kind,endpoint = empty,'immediate',IMMEDIATE
        for reg in (8,): restore(reg)
        expected.append(('r',sp-4,4,resume))
        for reg in (9,19,20): restore(reg)
        row = TABLE+index*12
        write(row+4,4,key)
        write(row,1,0)
        write(row+8,4,payload)
        restore(18)
        expected.extend((('r',0x40050,4,IMMEDIATE),('r',TASK,1,task)))
        scaled = 0
    else:
        match = next((i for i,k in enumerate(keys) if k == key),None)
        scan(15 if match is None else match+1)
        if match is not None:
            index,existing = match,True
            old = int.from_bytes(data[index*12+8:index*12+12],'little')
            expected.append(('r',TABLE+12*index+8,4,old))
        else:
            scan(15 if empty is None else empty+1)
            index,old = empty,0
        if index is None:
            kind,endpoint,scaled = 'full',resume,None
            expected.append(('r',sp-4,4,resume))
            for reg in S_REGS: restore(reg)
        elif old:
            kind,endpoint,scaled = 'free',FREE,None
            expected.append(('r',0x40068,4,FREE))
        else:
            row = TABLE+index*12
            if existing:
                expected.append(('r',TASK,1,task))
            else:
                write(row+4,4,key)
            write(row,1,flag)
            write(row+8,4,payload)
            if not existing:
                expected.append(('r',TASK,1,task))
            scaled = ((duration*1000)&MASK)//625
            kind,endpoint = ('call',START) if flag == 0 else ('repeat',REPEAT)
            if flag:
                restore(8)
                expected.append(('r',sp-4,4,resume))
                for reg in (9,18,19,20): restore(reg)
                expected.append(('r',0x4022c,4,REPEAT))
            else:
                expected.append(('r',0x40058,4,START))
    c.events,c.trace_active = [],True
    c.writes.clear()
    stop = c.run(REGISTER,{FREE,START,REPEAT,IMMEDIATE,resume})
    check(stop == endpoint, 'registration endpoint')
    if kind == 'free':
        check((c.reg[1],c.reg[2],c.reg[8],c.reg[9],c.reg[18],c.reg[19],c.reg[20],c.reg[10]) ==
              (0x91b6,sp-32,flag,index,TABLE,duration,payload,old), 'registration pre-free contract')
    elif kind == 'full':
        check((c.reg[1],c.reg[2],c.reg[10]) == (resume,sp,1) and
              all(c.reg[reg] == saved[reg] for reg in S_REGS), 'registration full-table return')
    else:
        check(c.reg[10:13] == [task,1 << index,scaled], 'registration service arguments')
        if kind == 'call':
            check((c.reg[1],c.reg[2],c.reg[8],c.reg[9],c.reg[18],c.reg[19],c.reg[20]) ==
                  (0x9230,sp-32,flag,index if existing else 15,TABLE,duration,payload), 'registration live frame')
            if reply is not None:
                # Explicit normal return: preserve SP/GP, table and saved frame.
                # S0-S4 are not needed after return and are deliberately clobbered.
                for reg in (1,5,6,7,*range(10,18),*range(28,32),*S_REGS):
                    c.put(reg,0xcafe0000+reg*0x101)
                c.put(10,reply)
                check(c.run(0x9230,{resume}) == resume and c.reg[10] == int(reply == 0) and
                      (c.reg[1],c.reg[2]) == (resume,sp) and all(c.reg[r] == saved[r] for r in S_REGS),
                      'registration normal-return result')
                expected.append(('r',sp-4,4,resume))
                for reg in S_REGS: restore(reg)
        else:
            check((c.reg[1],c.reg[2]) == (resume,sp) and all(c.reg[r] == saved[r] for r in S_REGS),
                  'registration restored tail frame')
    c.trace_active = False
    check(c.events == expected, 'registration exact accesses')
    check(c.writes == [(a,n,v) for op,a,n,v in expected if op == 'w'], 'registration exact stores')
    check(c.mem(TABLE,180).to_bytes(180,'little') == model and not c.calls, 'registration table/canary/no provider')
    return kind,index


def arguments(c,key=KEY,flag=0,duration=10000,payload=0):
    registers(c)
    c.reg[3],c.reg[10:14] = GP,[key,flag,duration,payload]


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == APP_HASH, 'APP identity')
    c = Registration(image)
    initialize(c)
    for flags,ready,k in product(range(256),range(256),(0,1,255)):
        gate_fixture(c,flags,ready,k)
        gate(c)
    for k,ready,flags in product(range(256),(0,1,255),(0,16)):
        gate_fixture(c,flags,ready,k)
        gate(c)
    for old in range(256):
        gate_fixture(c,flags=0,old=old)
        gate(c)
    durations = (0,1,624,625,626,4294967,4294968,0x80000000,MASK)
    counts = dict.fromkeys(('immediate','full','free','call','repeat'),0)
    for index,existing,duration,flag,task,key,old in product(range(15),(False,True),durations,(0,1,256,MASK),(0,1,255),(0,KEY,MASK),(0,0x29000000)):
        arguments(c,key,flag,duration,0x28000000)
        rows(c,((index,key if existing else 0,old),),task)
        counts[register(c)[0]] += 1
    for index,task,flag,existing in product(range(15),range(256),(0,1,256),(False,True)):
        arguments(c,flag=flag)
        rows(c,((index,KEY if existing else 0,0),),task)
        register(c)
    for duration,flag,task,key in product(durations,(0,1,256,MASK),(0,1,255),(0,KEY,MASK)):
        arguments(c,key,flag,duration)
        rows(c,task=task)
        check(register(c)[0] == 'full', 'registration full fixture')
    for (first,last),key,duration in product(combinations(range(15),2),(0,KEY,MASK),(0,10000)):
        arguments(c,key,duration=duration)
        rows(c,((first,0,0x29000000),(last,key,0)))
        register(c)
        arguments(c,key,duration=duration)
        rows(c,((first,key,0),(last,key,0)))
        register(c)
    for index,reply,existing in product(range(15),(0,1,MASK),(False,True)):
        arguments(c)
        rows(c,((index,KEY if existing else 0,0),))
        check(register(c,reply)[0] == 'call', 'normal-return fixture')
    for address,before,after,which in (
        (GATE,'2386010a','a386010a','gate'),
        (0x919a,'bd46','b946','scan'),
        (0x91d0,'9307803e','9307903e','scale'),
        (0x9230,'13351500','13352500','reply'),
    ):
        mutant = bytearray(image)
        offset = address-BASE
        check(mutant[offset:offset+len(bytes.fromhex(before))] == bytes.fromhex(before), 'registration mutation pin')
        mutant[offset:offset+len(bytes.fromhex(after))] = bytes.fromhex(after)
        probe = Registration(mutant)
        initialize(probe)
        if which == 'gate':
            gate_fixture(probe,flags=0)
        else:
            arguments(probe,duration=625)
            rows(probe,((14 if which == 'scan' else 0,KEY,0),))
        try:
            gate(probe) if which == 'gate' else register(probe,1 if which == 'reply' else None)
        except RuntimeError as exc:
            wanted = {'gate':'registration gate exact accesses','scan':'registration endpoint',
                      'scale':'registration service arguments','reply':'registration normal-return result'}[which]
            check(str(exc) == wanted, 'unexpected registration mutation failure: '+str(exc))
        else:
            raise RuntimeError('registration mutation undetected')
    print(f'PASS: 196608 gate byte cases; 1536 K probes; 256 unconditional clears; {sum(counts.values())} table cases {counts}; '
          '23040 task/flag cases; 324 full tables; 1260 priority/duplicate cases; 90 declared normal returns; 4 mutations')


def composition(image):
    c = Registration(image)
    initialize(c)
    counts = dict.fromkeys(('return','free','call','full'),0)
    for flags,ready,k,layout,reply in product((0,16),(0,1),(0,1),('empty','match','payload','full'),(None,0,1,MASK)):
        gate_fixture(c,flags,ready,k)
        changes = ((7,0,0),) if layout == 'empty' else ((7,KEY,0),) if layout == 'match' else ((7,KEY,0x29000000),) if layout == 'payload' else ()
        rows(c,changes)
        if not gate(c):
            counts['return'] += 1
        else:
            path,_ = register(c,reply)
            check(path in ('call','full','free'), '9fc8 reachable registration subset')
            counts[path] += 1
    completed = 0
    for value,layout,reply in product((6,7,0x101,0x10012),('empty','full'),(None,0,1,MASK)):
        schedule_fixture(c,enabled=0,flags8=16)
        c.mem(READY,1,1)
        c.mem(GP+354,1,0)
        c.reg[10] = value
        saved = tuple(c.reg[r] for r in S_REGS)
        rows(c,((7,0,0),) if layout == 'empty' else ())
        check(guard(c) and schedule(c)[0] == 'return', 'original b6f4 early-return schedule')
        stop = c.run(0xb70e,{GATE,RETURN})
        if value <= 11:
            check(stop == GATE and gate(c), 'b6f4 actual 9fc8 call')
            path,_ = register(c,reply)
            if path == 'call' and reply is None:
                continue
            final_a0 = 1 if path == 'full' else int(reply == 0)
            check(c.run(0xb71e,{RETURN}) == RETURN, 'b6f4 post-registration return')
        else:
            check(stop == RETURN, 'high alias skips 9fc8')
            final_a0 = 0
        check(c.reg[1] == RETURN and c.reg[2] == 0x21000800 and
              tuple(c.reg[r] for r in S_REGS) == saved and c.reg[10] == final_a0 and c.mem(0x2000bf0c,1) == value & 255,
              'b6f4 final caller/byte store')
        completed += 1
    print(f'PASS: {sum(counts.values())} original 9fc8-to-9124 chains {counts}; '
          f'{completed} b6f4 full returns; free/tail providers NOT executed; 40058 return premise explicit')


if __name__ == '__main__':
    image = IMAGE.read_bytes()
    verify(image)
    composition(image)
