"""Original A204 local state machine and 10816 registration tail, offline.

40038 may receive an explicit scalar return preserving memory/SP/GP/S registers.
D05C always stops at entry. No provider code or device operations execute.
"""
from hashlib import sha256
from itertools import product
from test_v4160_a2ee_action_cpu import (Action,initialize as init_action,
    execute as action,fixture as action_fixture,LOCAL,ALT,KEY as ACTION_KEY,
    GP,CONFIG,MODE,S_REGS,segment)
from test_v4160_register_gate_cpu import rows,register,REGISTER,READY as GET_READY
from test_v4160_schedule_171de_cpu import FLAG,SAMPLE
from test_v4160_feature_outer_cpu import registers,APP_HASH
from test_v4160_zero_id_queue_cpu import IMAGE,BASE,MASK,check

LIGHT,LATCH,DIRECTION,PENDING = GP+178,GP+179,GP+180,GP+174
COMMAND,ALT_FLAG,ALT_KEY,DIRECT = 0x2000bf0c,0x2000bfb8,0x1061c,0xd05c


class LocalState(Action):
    CODE_RANGES = Action.CODE_RANGES+((LOCAL,0xa2ee),(0xb6ea,0xb6f4),(ALT,0x1083c))


def initialize(c):
    init_action(c)
    c.regions.extend(((LIGHT,bytearray([0,0,0,255]),True),
                      (ALT_FLAG,bytearray([0,255]),True)))


def state(c,flag=0,ready=1,latch=0,light=0,direction=0,pending=0,cfg4=0,cfg9=0):
    for a,v in ((FLAG,flag),(GET_READY,ready),(LATCH,latch),(LIGHT,light),
                (DIRECTION,direction),(PENDING,pending),(CONFIG+4,cfg4),(CONFIG+9,cfg9),
                (COMMAND,0xcc),(ALT_FLAG,0xdd)):
        c.mem(a,1,v)


def fixture(c,value=1,**kwargs):
    registers(c)
    c.reg[3],c.reg[10] = GP,value
    state(c,**kwargs)


def local(c,sample=None):
    before = c.reg[:]
    sp,resume,value = before[2],before[1],before[10]
    flag,ready,latch,light,direction,pending,cfg4,cfg9 = (c.mem(a,1) for a in
        (FLAG,GET_READY,LATCH,LIGHT,DIRECTION,PENDING,CONFIG+4,CONFIG+9))
    model = {LIGHT:light,LATCH:latch,DIRECTION:direction,COMMAND:c.mem(COMMAND,1)}
    expected = [('w',sp-4,4,resume),('r',FLAG,1,flag)]
    sampled,direct,common = False,False,False
    result = value
    def write(a,v):
        model[a] = v & 255
        expected.append(('w',a,1,v & 255))
    if flag:
        if value:
            expected.append(('r',GET_READY,1,ready))
            result,direct = ready,bool(ready)
    else:
        expected.append(('r',LATCH,1,latch))
        if value and not latch:
            write(LATCH,value)
            expected += [('r',GP+84,4,CONFIG),('r',CONFIG+4,1,cfg4)]
            selection = cfg4 >> 6
            if selection == 2:
                expected.append(('r',DIRECTION,1,direction))
                direction = int(not direction)
            else: direction = selection
            write(DIRECTION,direction)
            expected.append(('r',CONFIG+9,1,cfg9))
            choice = cfg9 & 3
            if choice in (0,1): write(LIGHT,choice)
            elif choice == 3:
                sampled = True
                expected.append(('r',0x40038,4,SAMPLE))
            common = True
        elif not value and latch:
            write(LATCH,latch-1)
            if latch == 1:
                expected.append(('r',LIGHT,1,light))
                write(LIGHT,int(not light))
                common = True
    # First run stops at the opaque sample. All preceding state changes are
    # checked even when no return hypothesis is supplied.
    prefix = expected[:]
    if sampled:
        check(segment(c,LOCAL,{SAMPLE,DIRECT,resume},prefix,'local sample prefix') == SAMPLE and
              (c.reg[1],c.reg[2],c.reg[10]) == (0xa2a0,sp-16,value),'local sample boundary')
        check(all(c.mem(a,1) == v for a,v in model.items()),'local pre-sample state')
        if sample is None: return 'sample'
        for r in (1,5,6,7,*range(10,18),*range(28,32)):
            c.put(r,0xcafe0000+r*0x101)
        c.put(10,sample)
        expected = []
        result = sample & 1
        write(LIGHT,result)
    if direct:
        expected.append(('r',sp-4,4,resume))
    elif common:
        expected.append(('r',DIRECTION,1,model[DIRECTION]))
        d = model[DIRECTION]
        command = None
        if not d:
            expected.append(('r',PENDING,1,pending))
            if not pending:
                expected.append(('r',LIGHT,1,model[LIGHT]))
                command = 3 if model[LIGHT] else 1
        else:
            expected.append(('r',LIGHT,1,model[LIGHT]))
            command = (10 if model[LIGHT] else 12) if d == 3 else (11 if model[LIGHT] else 9)
        expected.append(('r',sp-4,4,resume))
        if command is not None:
            result = command
            write(COMMAND,command)  # Actual B6EA leaf, not a modelled callee.
    else:
        expected.append(('r',sp-4,4,resume))
    stop = segment(c,0xa2a0 if sampled else LOCAL,{DIRECT,resume},expected,'local completion')
    check(stop == (DIRECT if direct else resume),'local completion endpoint')
    if direct: check(c.reg[10:13] == [3,1,0],'local direct tail arguments')
    else: check(c.reg[10] == result,'local returned A0')
    check((c.reg[1],c.reg[2]) == (resume,sp) and
          all(c.reg[r] == before[r] for r in (3,4,*S_REGS)),'local restored frame')
    check(all(c.mem(a,1) == v for a,v in model.items()) and
          c.mem(GP+181,1) == 255 and c.mem(COMMAND+1,1) == 255,
          'local final state/canaries')
    return 'direct' if direct else 'return'


def alternate(c):
    before = c.reg[:]
    value = before[10] or 1
    expected = [('w',ALT_FLAG,1,1)]
    check(segment(c,ALT,{REGISTER},expected,'alternate') == REGISTER and
          c.reg[10:14] == [ALT_KEY,0,(value*1000)&MASK,0], 'alternate registration arguments')
    check(all(c.reg[r] == before[r] for r in range(32) if r not in (10,11,12,13,14,15)) and
          c.mem(ALT_FLAG,1) == 1 and c.mem(ALT_FLAG+1,1) == 255,'alternate frame/canary')


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == APP_HASH,'firmware identity')
    c = LocalState(image)
    initialize(c)
    for cfg4,cfg9 in product(range(256),repeat=2):
        fixture(c,cfg4=cfg4,cfg9=cfg9,light=255,direction=255)
        local(c)
    gates = 0
    for flag,value,ready in product(range(256),(0,1,256,MASK),(0,1,255)):
        fixture(c,value,flag=flag,ready=ready)
        local(c)
        gates += 1
    for latch,value in product(range(256),(0,1,256,MASK)):
        fixture(c,value,latch=latch,light=255)
        local(c)
    releases = 0
    for direction,light,pending in product((0,1,3,255),range(256),(0,1,255)):
        fixture(c,0,latch=1,light=light,direction=direction,pending=pending)
        local(c)
        releases += 1
    samples = 0
    for cfg4,direction,pending,raw in product(range(256),(0,1,255),(0,1,255),(0,1,2,MASK)):
        fixture(c,cfg4=cfg4,cfg9=3,direction=direction,pending=pending)
        local(c,sample=raw)
        samples += 1
    for ready in range(256):
        fixture(c,flag=255,ready=ready)
        local(c)
    alternate_chains = dict.fromkeys(('immediate','call','free','full'),0)
    for value,index,layout in product((0,1,15,256,0x20000000,0x80000000,MASK),range(15),('new','existing','old','full')):
        rows(c,[] if layout == 'full' else [(index,0 if layout == 'new' else ALT_KEY,1 if layout == 'old' else 0)])
        fixture(c,value)
        c.mem(MODE,1,2)
        check(action(c) == 'alt','actual A2EE alternate tail')
        alternate(c)
        kind,_ = register(c)
        alternate_chains[kind] += 1
        check(c.mem(ALT_FLAG,1) == 1,'alternate flag survives registration result')
    # Actual A2EE -> A204 returns -> A2EE epilogue, no fabricated A204 return.
    parents = 0
    for v,cfg4,value,latch,flag,ready in product((1,3),(8,72,136,200),(0,1,15),(0,1),(0,1),(0,1)):
        action_fixture(c,value,cfg5=v-1,cfg4=cfg4)
        state(c,flag=flag,ready=ready,latch=latch,cfg4=cfg4,cfg9=2)
        before = c.reg[:]
        check(action(c) == 'local','actual A204 caller entry')
        outcome = local(c)
        if outcome == 'return':
            answer = c.reg[10] if v == 1 else 0  # config4 bit3 blocks readiness.
            sp,resume = before[2],before[1]
            expected = [] if v == 1 else [('r',GP+84,4,CONFIG),('r',CONFIG+4,1,cfg4)]
            expected += [('r',sp-4,4,resume),('r',sp-8,4,before[8]),('r',sp-12,4,before[9])]
            check(segment(c,0xa312,{resume},expected,'parent actual return') == resume and
                  c.reg[10] == answer and all(c.reg[r] == before[r] for r in (1,2,3,4,*S_REGS)),
                  'actual parent frame/A0')
            parents += 1
    mutations = 0
    for addr,old,new,which,message in (
        (0xa230,'a389a10a','a389010a','latch','local completion accesses'),
        (0xa2a0,'0589','0d89','sample','local completion accesses'),
        (0x10818,'0545','0945','alternate','alternate registration arguments'),
        (0x10834,'1305c5de','1305e5de','alternate','alternate registration arguments')):
        off = addr-BASE
        check(image[off:off+len(bytes.fromhex(old))] == bytes.fromhex(old),'local mutation pin')
        mutant = bytearray(image)
        mutant[off:off+len(bytes.fromhex(old))] = bytes.fromhex(new)
        d = LocalState(mutant)
        initialize(d)
        fixture(d,0 if which == 'alternate' else 1,cfg9=3 if which == 'sample' else 0)
        try:
            if which == 'alternate': alternate(d)
            else: local(d,sample=2 if which == 'sample' else None)
        except RuntimeError as error:
            check(str(error) == message,'unexpected local mutation failure: '+str(error))
            mutations += 1
        else: raise RuntimeError('local mutation escaped')
    print('PASS: 65536 config4/config9 pairs; %d flag/input/ready gates; 1024 latch/input cases; %d retained-state releases; %d declared sample returns; 256 ready bytes' % (gates,releases,samples))
    print('PASS: A2EE-to-10816-to-9124 chains %s; %d original A2EE/A204 parent returns; %d mutations' % (alternate_chains,parents,mutations))
    print('PASS: exact accesses/stores/frame; input low-byte latch and zero normalization; D05C and sample target NOT executed')


if __name__ == '__main__':
    verify(IMAGE.read_bytes())
