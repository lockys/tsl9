"""Original D1B2 assembly of the 19-byte TX source, offline fixtures only.

All provider entries stop before execution. Optional destination writes and
normal returns are explicit premises, not observations of installed services.
"""
from hashlib import sha256
from itertools import product
from test_v4160_mode1_dispatch_cpu import Mode1,execute as dispatch
from test_v4160_feature_outer_cpu import registers,APP_HASH,MODE,ROW
from test_v4160_zero_id_queue_cpu import IMAGE,BASE,RETURN,MASK,check

ENTRY,GETTER,CLEAR,OTHER = 0xd1b2,0xd1a8,0xd272,0x12ad0
DATA,GP,STAGE = 0x2000bf48,0x20004000,0x200040ec
COPY,FILL = 0x30002000,0x30002020
SAVED = (8,9,18,19,20,21,22,23,24,25,26,27)


class Source19(Mode1):
    CODE_RANGES = Mode1.CODE_RANGES+((GETTER,0xd288),(0x133a6,0x133b4))


def initialize(c):
    c.regions[:] = [(a,bytearray(COPY.to_bytes(4,'little')),True) if a == 0x4004c else (a,b,w)
                   for a,b,w in c.regions]
    c.regions.extend(((DATA-1,bytearray(21),True),(GP+232,bytearray(12),True),
                      (0x40048,bytearray(FILL.to_bytes(4,'little')),True)))


def fixture(c,ready=0,stage=0,sub=16,low=0):
    registers(c)
    c.reg[3] = GP
    c.mem(DATA-1,21,int.from_bytes(bytes([0xe1])+bytes((low+19*i)&255 for i in range(19))+bytes([0xe2]),'little'))
    c.mem(DATA,1,ready)
    c.mem(GP+232,12,int.from_bytes(bytes(range(0xd0,0xdc)),'little'))
    c.mem(STAGE,1,stage)
    row = bytearray((low+7*i)&255 for i in range(12))
    row[:2],row[3] = (1029).to_bytes(2,'little'),sub
    c.mem(ROW,12,int.from_bytes(row,'little'))
    c.mem(0x4004c,4,COPY)
    return bytes(row)


def run_segment(c,start,stops,events,label,budget=1000):
    old = [bytes(b) for a,b,w in c.regions]
    model = [bytearray(b) for b in old]
    for op,address,n,value in events:
        if op != 'w': continue
        hits = [i for i,(a,b,w) in enumerate(c.regions) if a <= address and address+n <= a+len(b)]
        check(len(hits) == 1,label+' expected mapped write')
        i = hits[0]
        off = address-c.regions[i][0]
        model[i][off:off+n] = value.to_bytes(n,'little')
    c.events,c.trace_active = [],True
    c.writes.clear()
    stop = c.run(start,stops,budget)
    c.trace_active = False
    check(c.events == events,label+' ordered accesses')
    check([bytes(b) for a,b,w in c.regions] == [bytes(b) for b in model],label+' memory footprint')
    check(not c.calls,label+' provider executed')
    return stop


def assemble(c):
    before = c.reg[:]
    p,sp,resume = before[10],before[2],before[1]
    ready,stage,sub = c.mem(DATA,1),c.mem(STAGE,1),c.mem(p+3,1)
    target = c.mem(0x4004c,4)
    expected = [('r',DATA,1,ready)]
    kind,endpoint = ('ready',OTHER) if ready else ('return',resume)
    if not ready:
        expected += [('r',STAGE,1,stage)]
        if stage:
            expected += [('w',sp-8,4,before[8]),('w',sp-4,4,resume)]
        if stage in (0,1,2): expected += [('r',p+3,1,sub)]
        if stage in (0,1,2) and sub == 16+stage:
            kind,endpoint = 'copy',target
            if stage == 1: expected += [('r',sp-8,4,before[8])]
            expected += [('w',STAGE,1,stage+1)]
            if stage == 1: expected += [('r',sp-4,4,resume)]
            expected += [('r',0x4004c,4,target)]
        else:
            expected += [('w',STAGE,1,0)]
            if stage: expected += [('r',sp-4,4,resume),('r',sp-8,4,before[8])]
    check(run_segment(c,ENTRY,{target,OTHER,resume},expected,'source19') == endpoint,
          'source19 endpoint')
    if kind == 'copy':
        args = ([DATA+1,p+8,3],[DATA+4,p+4,7],[DATA+11,p+4,7])[stage]
        check(c.reg[10:13] == args,'source19 copy arguments')
        check((c.reg[1],c.reg[2],c.reg[8]) ==
              ((0xd250,sp-16,1) if stage == 2 else (resume,sp,before[8])),
              'source19 copy live frame')
    else:
        check(c.reg[10] == (1 if ready else p),'source19 untouched/ready A0')
        check((c.reg[1],c.reg[2],c.reg[8]) == (resume,sp,before[8]),'source19 return frame')
    check(all(c.reg[r] == before[r] for r in (3,4,*SAVED) if r != 8),
          'source19 preserved context')
    return kind,stage,before


def finish_third(c,before,reply=MASK,s0=1):
    # Hypothesis: normal return preserves frame, GP/SP and all S registers;
    # s0 override is a separate negative-contract probe, not an ABI guarantee.
    for r in (1,5,6,7,*range(10,18),*range(28,32)):
        c.put(r,0xcafe0000+r*0x101)
    c.put(10,reply)
    c.put(8,s0)
    sp,resume = before[2],before[1]
    expected = [('w',DATA,1,s0&255),('r',sp-4,4,resume),('r',sp-8,4,before[8])]
    check(run_segment(c,0xd250,{resume},expected,'source19 completion') == resume and
          c.reg[10] == reply and all(c.reg[r] == before[r] for r in (1,2,3,4,*SAVED)),
          'source19 completion result')


def clear(c):
    before = c.reg[:]
    target = c.mem(0x40048,4)
    check(run_segment(c,CLEAR,{target},[('r',0x40048,4,target)],'source19 clear') == target and
          c.reg[10:13] == [DATA,0,19] and
          all(c.reg[r] == before[r] for r in range(32) if r not in (6,10,11,12,15)),
          'source19 clear contract')


def request_tx(c):
    # The actual caller fragment captures COPY, calls D1A8, and forwards its
    # pointer. Earlier TX frame construction was verified separately.
    c.put(8,0x40000)  # explicit live context established by the earlier TX prefix
    before = c.reg[:]
    target = c.mem(0x4004c,4)
    check(run_segment(c,0x133a6,{target},[('r',0x4004c,4,target)],'source19 TX request') == target and
          c.reg[10:13] == [before[2]+60,DATA,19] and
          (c.reg[1],c.reg[2],c.reg[8]) == (0x133b4,before[2],target),
          'source19 TX source contract')


def chain(c,low,effects=True,clear_first=False,reply=MASK):
    fixture(c,low=low)
    if clear_first:
        clear(c)
        # Explicit fill effect, not execution of the slot48 provider.
        c.mem(DATA,19,0)
    original = c.mem(DATA,19).to_bytes(19,'little')
    model = bytearray(original)
    for stage in range(3):
        registers(c)
        c.reg[3] = GP
        row = bytearray((low+stage*61+7*i)&255 for i in range(12))
        row[:2],row[3] = (1029).to_bytes(2,'little'),16+stage
        c.mem(ROW,12,int.from_bytes(row,'little'))
        c.mem(0x4004c,4,COPY+stage*4)
        if stage&1: c.mem(ROW+2,1,0)  # length byte is not a handler guard
        kind,seen,last_caller = assemble(c)
        check((kind,seen) == ('copy',stage),'source19 staged path')
        before = c.reg[:]
        dest,source,n = before[10:13]
        if effects:
            # Synthetic effect restricted to exactly the requested destination.
            data = c.mem(source,n).to_bytes(n,'little')
            c.mem(dest,n,int.from_bytes(data,'little'))
            model[dest-DATA:dest-DATA+n] = data
        if stage == 2:
            # assemble() stores the pre-entry caller frame in its third result.
            finish_third(c,last_caller,reply)
            model[0] = 1
        else:
            check(c.mem(DATA,1) == 0,'source19 premature ready flag')
        check(c.mem(DATA,19).to_bytes(19,'little') == model,'source19 staged data')
        # No stage0/1 post-call APP instructions: providers tail-return directly.
        if stage < 2:
            check(c.reg[1] == RETURN,'source19 tail caller return address')
    check(model[18] == original[18] and c.mem(STAGE,1) == 3,'source19 final byte/stage')
    registers(c)
    c.reg[3] = GP
    request_tx(c)
    check(c.mem(DATA,19).to_bytes(19,'little') == model,'source19 TX request does not read/write source')
    return bytes(model)


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == APP_HASH,'APP identity')
    c = Source19(image)
    initialize(c)
    matrix = 0
    for stage,sub in product(range(256),repeat=2):
        fixture(c,stage=stage,sub=sub)
        assemble(c)
        matrix += 1
    ready_cases = 0
    for ready,stage,sub in product(range(1,256),(0,1,2,255),(0,16,17,18)):
        fixture(c,ready,stage,sub)
        assemble(c)
        ready_cases += 1
    chains = 0
    for low,effects,zero,reply in product(range(256),(False,True),(False,True),(0,MASK)):
        chain(c,low,effects,zero,reply)
        chains += 1
    routes = 0
    for stage,sub,ready in product((0,1,2,255),(16,17,18),(0,1)):
        fixture(c,ready,stage,sub)
        c.mem(MODE,1,1)
        check(dispatch(c,1029,sub) == 'tail','source19 actual mode1 tail')
        assemble(c)
        routes += 1
    # Even a provider that performs no destination writes can lead to ready=1.
    # Corrupting live S0 changes the marker, while the saved caller S0 restores.
    for s0 in (0,1,2,255,256,257,0x80000001,MASK):
        fixture(c,stage=2,sub=18)
        kind,stage,before = assemble(c)
        check(kind == 'copy','source19 third-copy probe')
        finish_third(c,before,s0=s0)
        check(c.mem(DATA,1) == s0&255,'source19 marker depends on live S0')
    # Clear19 itself only delegates: neither stage reset nor zero stores occur.
    for stage,ready in product(range(256),(0,1,255)):
        fixture(c,ready,stage)
        clear(c)
        check(c.mem(STAGE,1) == stage and c.mem(DATA,1) == ready,'source19 clear does not reset stage')
    fixture(c,ready=1,stage=3)
    clear(c)
    c.mem(DATA,19,0)  # explicit successful fill premise
    registers(c)
    c.reg[3] = GP
    check(assemble(c)[:2] == ('return',3) and c.mem(STAGE,1) == 0,
          'source19 post-clear first record only resets stale stage')
    check(assemble(c)[:2] == ('copy',0),'source19 post-clear retry')
    # Freeze the third copy before any return: stage advances, ready does not.
    fixture(c,stage=2,sub=18)
    assemble(c)
    check(c.mem(STAGE,1) == 3 and c.mem(DATA,1) == 0,'source19 stopped third copy is incomplete')
    reset_check(image)
    mutations = mutation_checks(image)
    print('PASS: %d stage/sub-byte cases; %d nonzero-ready short-circuits' % (matrix,ready_cases))
    print('PASS: %d conditional three-fragment/TX-source chains; %d real mode1 tails; 768 clear boundaries; 8 S0 contract probes' % (chains,routes))
    print('PASS: exact events/frame/memory; untouched byte18; %d specified mutations; providers/hardware NOT executed' % mutations)


def reset_check(image):
    begin,end = 0x20004080,0x2000c958
    c = Source19(image)
    c.CODE_RANGES = ((0x186de,0x186f8),)
    # Single synthetic BSS span avoids alias/overlap with normal handler regions.
    c.regions[:] = [(BASE,bytearray(image),False),(begin-4,bytearray([0xa5])*(end-begin+8),True)]
    c.reg[3] = GP
    events = [('w',a,4,0) for a in range(begin,end,4)]
    check(run_segment(c,0x186de,{0x186f8},events,'source19 reset BSS',30000) == 0x186f8 and
          c.mem(DATA,19) == 0 and c.mem(STAGE,1) == 0 and
          c.mem(begin-4,4) == 0xa5a5a5a5 and c.mem(end,4) == 0xa5a5a5a5,
          'source19 reset range/canaries')
    # GP was a fixture for loop execution; independently decode reset's GP pair.
    off = 0x186aa-BASE
    check(image[off:off+8] == bytes.fromhex('97c1fe1f93816195'),'source19 reset GP pin')
    check((0x186aa+0x1ffec000-1706)&MASK == GP,'source19 reset GP operand')
    print('PASS: original reset loop 8758 zero-word stores; 19-byte source and stage inside BSS; CSR boundary not entered')


def mutation_checks(image):
    cases = (
        (0xd1de,'0d46','1146',0,16,'assemble','source19 copy arguments'),
        (0xd21c,'130545d3','130555d3',1,17,'assemble','source19 copy arguments'),
        (0xd254,'238c87ce','a38c87ce',2,18,'finish','source19 completion ordered accesses'),
        (0xd27a,'4d46','4946',0,16,'clear','source19 clear contract'),
        (0x133ae,'4d46','4946',0,16,'request','source19 TX source contract'),
    )
    for address,old,new,stage,sub,kind,message in cases:
        off = address-BASE
        a,b = bytes.fromhex(old),bytes.fromhex(new)
        check(image[off:off+len(a)] == a,'source19 mutation pin')
        mutant = bytearray(image)
        mutant[off:off+len(a)] = b
        c = Source19(mutant)
        initialize(c)
        fixture(c,stage=stage,sub=sub)
        try:
            if kind == 'assemble': assemble(c)
            elif kind == 'finish': finish_third(c,assemble(c)[2])
            elif kind == 'clear': clear(c)
            else: request_tx(c)
        except RuntimeError as error:
            check(str(error) == message,'unexpected source19 mutation failure: '+str(error))
        else: raise RuntimeError('source19 mutation escaped')
    return len(cases)


if __name__ == '__main__': verify(IMAGE.read_bytes())
