"""Original 171de arithmetic and fresh provider/task loads, synthetic fixtures.
Sample and first schedule targets only receive explicitly declared normal returns.
Second schedule tail and 9fc8 always stop before execution; no device operations.
"""
from hashlib import sha256
from itertools import product
from test_v4160_downstream_gates_cpu import (Downstream,initialize as init_downstream,
    guard,GP,CONFIG,GUARD,FOLLOW)
from test_v4160_feature_outer_cpu import registers,APP_HASH
from test_v4160_zero_id_queue_cpu import IMAGE,BASE,RETURN,MASK,check

ENTRY,ENABLE_GET,EXTRA_GET,FLAG_GET = 0x171de,0x8440,0xabf2,0x9fc2
SAMPLE,FIRST,SECOND = 0x30000c00,0x30000c04,0x30000c08
SLOT,ENABLE,TASK,EXTRA,FLAG = 0x40058,GP+364,GP+365,0x2000bee0,GP+172


class Schedule(Downstream):
    CODE_RANGES = Downstream.CODE_RANGES+((ENTRY,0x172b6),(ENABLE_GET,0x8446),
                                        (EXTRA_GET,0xabfc),(FLAG_GET,0x9fc8))

    def mem(self,address,size,value=None):
        result = super().mem(address,size,value)
        if getattr(self,'trace_active',False) and value is None and address == CONFIG+3 and self.read_pair is not None:
            result = next(self.read_pair)
            check(self.events[-1][:3] == ('r',address,size), 'scripted read trace position')
            self.events[-1] = ('r',address,size,result)
        return result


def initialize(c):
    init_downstream(c)
    c.regions.extend(((0x40038,bytearray(SAMPLE.to_bytes(4,'little')),False),
                      (SLOT,bytearray(FIRST.to_bytes(4,'little')),True),
                      (GP+360,bytearray(range(0xa0,0xa8)),True),
                      (EXTRA,bytearray([0,0xff]),True),(FLAG,bytearray([0]),True),
                      (0x2000bf0c,bytearray([0,0xff]),True)))
    c.read_pair = None


def fixture(c,mode=1,jitter=1,enabled=1,extra=0,flags8=0,flag=0,task=17):
    registers(c)
    c.reg[3] = GP
    c.mem(CONFIG,10,int.from_bytes(bytes(range(10)),'little'))
    for address,value in ((CONFIG+3,mode),(CONFIG+4,jitter),(CONFIG+8,flags8),
                          (ENABLE,enabled),(EXTRA,extra),(FLAG,flag),(TASK,task)):
        c.mem(address,1,value)
    c.mem(SLOT,4,FIRST)


def clobber(c,value):
    for reg in (1,5,6,7,*range(10,18),*range(28,32)):
        c.put(reg,0xcafe0000+reg*0x101)
    c.put(10,value)


def execute(c,sample=0,complete_first=False,next_task=None,next_target=SECOND,reply=MASK,pair=None):
    before = c.reg[:]
    sp,s0,s1,resume = before[2],before[8],before[9],before[1]
    enabled,extra,flags8,flag,task,jitter,config3 = (c.mem(address,1) for address in
        (ENABLE,EXTRA,CONFIG+8,FLAG,TASK,CONFIG+4,CONFIG+3))
    modes = (config3,config3) if pair is None else pair
    expected = [('w',sp-4,4,resume),('w',sp-8,4,s0),('w',sp-12,4,s1),('r',ENABLE,1,enabled)]
    getters = [(ENABLE_GET,before[10],0x171ea,enabled,s0,s1)]
    early,incoming = not enabled,enabled
    if enabled:
        expected.extend((('r',GP+84,4,CONFIG),('r',CONFIG+3,1,modes[0])))
        if modes[0] & 15 == 15:
            expected.append(('r',EXTRA,1,extra))
            getters.append((EXTRA_GET,incoming,0x1726e,extra,s0,GP+84))
            incoming = extra
            if extra:
                expected.extend((('r',GP+84,4,CONFIG),('r',CONFIG+8,1,flags8)))
                if not flags8 & 16:
                    early = True
                else:
                    expected.append(('r',FLAG,1,flag))
                    getters.append((FLAG_GET,incoming,0x1727e,flag,s0,GP+84))
                    incoming,early = flag,not flag
        if not early:
            expected.extend((('r',GP+84,4,CONFIG),('r',CONFIG+3,1,modes[1]),('r',0x40038,4,SAMPLE)))
    if early:
        expected.extend((('r',sp-4,4,resume),('r',sp-8,4,s0),('r',sp-12,4,s1)))
    c.events,c.trace_active = [],True
    c.writes.clear()
    c.read_pair = None if pair is None else iter(pair)
    pc,seen = ENTRY,[]
    for _ in range(4):
        stop = c.run(pc,{ENABLE_GET,EXTRA_GET,FLAG_GET,SAMPLE,FIRST,SECOND,resume})
        if stop not in (ENABLE_GET,EXTRA_GET,FLAG_GET):
            break
        check(len(seen) < len(getters), 'unexpected schedule getter')
        target,arg,continuation,result,live_s0,live_s1 = getters[len(seen)]
        check((stop,c.reg[10],c.reg[1],c.reg[2],c.reg[8],c.reg[9]) ==
              (target,arg,continuation,sp-16,live_s0,live_s1), 'schedule getter boundary')
        regs,mark = c.reg[:],len(c.writes)
        check(c.run(target,{continuation}) == continuation and c.reg[10] == result and
              all(c.reg[i] == regs[i] for i in range(32) if i != 10) and len(c.writes) == mark,
              'schedule actual getter')
        seen.append(target)
        pc = continuation
    else:
        raise RuntimeError('schedule getter budget')
    check(seen == [row[0] for row in getters], 'schedule getter count')
    if early:
        check(stop == resume and (c.reg[1],c.reg[2],c.reg[8],c.reg[9],c.reg[10]) ==
              (resume,sp,s0,s1,incoming), 'schedule early return')
        outcome,d = 'return',None
    else:
        mode = modes[1] & 15
        mode = 1 if mode == 15 else mode
        check(stop == SAMPLE and (c.reg[1],c.reg[2],c.reg[8],c.reg[9],c.reg[10]) ==
              (0x17216,sp-16,mode,GP+84,incoming) and c.reg[11:13] == before[11:13],
              'schedule sample boundary')
        if sample is None:
            outcome,d = 'sample',None
        else:
            # Normal-return hypothesis for 40038: S0/S1/SP/GP and memory preserved.
            clobber(c,sample)
            stop = c.run(0x17216,{FIRST,SECOND,resume})
            base,modulus = (2000,1001) if mode <= 1 else (3000,2001) if mode == 2 else (5000*(mode-2),5001)
            delay = base+(sample % modulus if jitter & 1 else 0)
            d = 8*delay//5  # Independent reduction: original code uses *1000 /625.
            check(delay <= 65000, 'schedule delay domain')
            expected.extend((('r',GP+84,4,CONFIG),('r',CONFIG+4,1,jitter),
                             ('r',SLOT,4,FIRST),('r',TASK,1,task)))
            check(stop == FIRST and (c.reg[10],c.reg[11],c.reg[12],c.reg[1],c.reg[2],c.reg[8],c.reg[9]) ==
                  (task,1,d,0x17252,sp-16,delay*1000,0x40000), 'schedule first-call contract')
            outcome = 'first'
            if complete_first:
                # First 40058 return may clobber S0, which is immediately reloaded.
                # Preserve S1/SP/GP/frame; explicitly change only slot/task memory.
                clobber(c,reply)
                c.put(8,0xdeadbeef)
                task_after = task if next_task is None else next_task
                c.trace_active = False
                for address,size,value in ((SLOT,4,next_target),(TASK,1,task_after)):
                    c.mem(address,size,value)
                    c.events.append(('hook',address,size,value))
                    expected.append(('hook',address,size,value))
                c.trace_active = True
                stop = c.run(0x17252,{FIRST,SECOND,resume})
                expected.extend((('r',sp-8,4,s0),('r',SLOT,4,next_target),('r',sp-4,4,resume),
                                 ('r',sp-12,4,s1),('r',TASK,1,task_after)))
                check(stop == next_target and (c.reg[1],c.reg[2],c.reg[8],c.reg[9],c.reg[10],c.reg[11],c.reg[12]) ==
                      (resume,sp,s0,s1,task_after,2,80), 'schedule fresh tail contract')
                outcome = 'tail'
    c.trace_active = False
    c.read_pair = None
    check(c.events == expected, 'schedule exact accesses')
    check(c.writes == [(a,n,v) for op,a,n,v in expected if op in ('w','hook')], 'schedule exact native/hook stores')
    check(all(c.reg[i] == before[i] for i in (0,3,4,*range(18,28))) and not c.calls,
          'schedule declared preservation/no provider')
    return outcome,d


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == APP_HASH, 'APP identity')
    c = Schedule(image)
    initialize(c)
    for enabled,mode,extra,flags8,flag in product(range(256),(0,1,2,3,14,15),(0,1,255),(0,16,255),(0,1,255)):
        fixture(c,mode,enabled=enabled,extra=extra,flags8=flags8,flag=flag)
        execute(c,1000)
    values = set()
    residue_cases = 0
    for mode in range(16):
        modulus = 1001 if mode in (0,1,15) else 2001 if mode == 2 else 5001
        for sample in range(modulus):
            fixture(c,mode)
            path,d = execute(c,sample)
            check(path == 'first', 'residue scheduling path')
            values.add(d)
            residue_cases += 1
    check(residue_cases == 65016 and len(values) == 63001, 'exhaustive schedule output domain')
    for mode,jitter in product(range(256),repeat=2):
        fixture(c,mode,jitter=jitter)
        execute(c,MASK)
    for mode,flags,sample in product(range(16),(0,1),(0,1,1000,1001,2000,2001,5000,5001,0x80000000,MASK)):
        fixture(c,mode,jitter=flags)
        execute(c,sample)
    for first,second in product(range(16),repeat=2):
        fixture(c,0xa0|first)
        execute(c,1234,pair=(0xa0|first,0xb0|second))
    for task,after in product(range(256),repeat=2):
        fixture(c,3,task=task)
        execute(c,42,True,next_task=after)
    for mode,reply,next_target in product(range(16),(0,1,MASK),(FIRST,SECOND)):
        fixture(c,mode)
        execute(c,MASK,True,next_task=255,next_target=next_target,reply=reply)
    for mode in range(16):
        fixture(c,mode)
        check(execute(c,None)[0] == 'sample', 'sample pre-provider stop')
    for address,before,after,mode,sample,complete in (
        (0x1721c,'9307903e','9307803e',1,1000,False),
        (0x17248,'13061027','13060027',0,1,False),
        (0x1725c,'03c5d116','03c5c116',3,42,True),
    ):
        mutant = bytearray(image)
        offset = address-BASE
        check(mutant[offset:offset+len(bytes.fromhex(before))] == bytes.fromhex(before), 'schedule mutation pin')
        mutant[offset:offset+len(bytes.fromhex(after))] = bytes.fromhex(after)
        probe = Schedule(mutant)
        initialize(probe)
        fixture(probe,mode)
        try:
            execute(probe,sample,complete,next_task=42)
        except RuntimeError as exc:
            check(str(exc) == ('schedule fresh tail contract' if complete else 'schedule first-call contract'),
                  'unexpected schedule mutation failure: '+str(exc))
        else:
            raise RuntimeError('schedule mutation undetected')
    print('PASS: 41472 guard probes; 65016 original remainder cases / 63001 unique outputs; '
          '65536 config-byte pairs; 320 word boundaries; 256 fresh-read pairs; 65536 task reload pairs; '
          '96 reply/slot probes; 16 sample stops; 3 mutations; opaque targets NOT executed')


def composition(image):
    c = Schedule(image)
    initialize(c)
    counts = dict.fromkeys(('return','first','tail'),0)
    for value,enabled,mode,jitter,complete in product((6,7,0x101,0x10012),(0,1),(0,1,2,14,15),(0,1),(False,True)):
        fixture(c,mode,jitter=jitter,enabled=enabled)
        c.reg[10] = value
        saved = (c.reg[8],c.reg[9])
        check(guard(c), 'original b6f4 accepted input')
        path,_ = execute(c,MASK,complete,next_task=255)
        counts[path] += 1
        if path == 'return':
            # Follow actual 171de return into b6f4; stop before 9fc8 if selected.
            stop = c.run(0xb70e,{0x9fc8,RETURN})
            selected = value <= 11 or value == 18
            check(stop == (0x9fc8 if selected else RETURN), 'b6f4 full-width post-call selection')
            if not selected:
                check(c.reg[2] == 0x21000800 and c.reg[1] == RETURN and (c.reg[8],c.reg[9]) == saved and
                      c.reg[10] == 0 and c.mem(0x2000bf0c,1) == value & 255 and c.mem(0x2000bf0d,1) == 255,
                      'b6f4 direct completion')
    print(f'PASS: {sum(counts.values())} actual b6f4-to-171de chains; {counts}; 9fc8/second target stopped')


if __name__ == '__main__':
    image = IMAGE.read_bytes()
    verify(image)
    composition(image)
