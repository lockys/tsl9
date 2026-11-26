"""Original 901a -> table callback -> 9f7a, explicit offline event inputs.

No event delivery, timer, allocation, free, or copy provider is executed.
Unknown callback keys stop at their entry. Payload words are opaque scalars.
"""
from hashlib import sha256
from itertools import product
from test_v4160_register_gate_cpu import (Registration,initialize,gate_fixture,gate,
    register,rows,KEY,READY,TABLE,GP,CONFIG,FLAG)
from test_v4160_feature_outer_cpu import registers,APP_HASH
from test_v4160_zero_id_queue_cpu import IMAGE,BASE,RETURN,MASK,check

DISPATCH,AFTER = 0x901a,0x905a
OPAQUE = 0x30000e00


class Callbacks(Registration):
    CODE_RANGES = Registration.CODE_RANGES+((KEY,0x9fb2),(DISPATCH,0x907a))


def callback(c):
    before = c.reg[:]
    sp,resume = before[2],before[1]
    flags,ready,k = (c.mem(a,1) for a in (CONFIG+8,READY,GP+354))
    used = bool(flags & 16)
    expected = [('r',GP+84,4,CONFIG),('r',CONFIG+8,1,flags)]
    if used:
        expected += [('w',sp-4,4,resume),('r',READY,1,ready)]
        if ready: expected.append(('r',GP+354,1,k))
        expected.append(('r',sp-4,4,resume))
    value = ((k ^ 1) & 1) if used and ready else 0
    expected.append(('w',FLAG,1,value))
    c.events,c.trace_active = [],True
    c.writes.clear()
    check(c.run(KEY,{resume}) == resume, 'callback endpoint')
    c.trace_active = False
    check(c.events == expected, 'callback exact accesses')
    check(c.writes == [(a,n,v) for op,a,n,v in expected if op == 'w'], 'callback stores')
    check(c.mem(FLAG,1) == value and c.mem(FLAG+1,1) == 255, 'callback flag/canary')
    check(c.reg[10] == (ready if used else before[10]), 'callback A0')
    check(all(c.reg[i] == before[i] for i in range(32) if i not in (10,15)) and
          not c.calls, 'callback registers/provider isolation')
    return value,expected


def dispatch(c,complete=False):
    before = c.reg[:]
    sp,resume,mask = before[2],before[1],before[11]
    data = c.mem(TABLE,180).to_bytes(180,'little')
    model = bytearray(data)
    selected = next((i for i in range(15) if mask & (1 << i)),None)
    expected = [('w',sp-8,4,before[8]),('w',sp-4,4,resume),('w',sp-12,4,before[9])]
    key,payload = 0,0
    if selected is not None:
        row = selected*12
        key = int.from_bytes(data[row+4:row+8],'little')
        expected.append(('r',TABLE+row+4,4,key))
        if key:
            flag,payload = data[row],int.from_bytes(data[row+8:row+12],'little')
            expected += [('r',TABLE+row,1,flag),('r',TABLE+row+8,4,payload)]
            if not flag:
                expected += [('w',TABLE+row+4,4,0),('w',TABLE+row+8,4,0)]
                model[row+4:row+12] = bytes(8)
    c.events,c.trace_active = [],True
    c.writes.clear()
    target = (key & ~1) if key else resume
    stop = c.run(DISPATCH,{target,resume})
    c.trace_active = False
    if key:
        check(stop == target and c.reg[10] == payload and c.reg[1] == AFTER and
              c.reg[2] == sp-16 and c.reg[8] == selected and c.reg[9] == mask,
              'dispatch callback entry')
        check(all(c.reg[i] == before[i] for i in range(32) if i not in (1,2,8,9,10,12,13,14,15)),
              'dispatch callback entry preservation')
    check(c.mem(TABLE,180).to_bytes(180,'little') == model, 'dispatch table at call')
    if key and complete:
        check(target == KEY, 'only original callback may complete')
        # Execute the actual indirect target, with the actual dispatcher frame.
        check(c.events == expected, 'dispatch prefix accesses')
        prefix_writes = c.writes[:]
        _,cb_events = callback(c)
        expected += cb_events
        c.writes[:] = prefix_writes+c.writes
        c.events,c.trace_active = expected[:],True
        stop = c.run(AFTER,{resume})
        c.trace_active = False
    if not key or complete:
        expected += [('r',sp-4,4,resume),('r',sp-8,4,before[8]),('r',sp-12,4,before[9])]
        result = ((mask ^ (1 << selected)) & 0xffff) if selected is not None else 0
        check(stop == resume and c.reg[10] == result, 'dispatch returned mask')
        check(all(c.reg[i] == before[i] for i in (1,2,8,9,18,19,20,21,22,23,24,25,26,27)),
              'dispatch restored frame')
    check(c.events == expected, 'dispatch exact accesses')
    check(c.writes == [(a,n,v) for op,a,n,v in expected if op == 'w'], 'dispatch exact stores')
    check(c.mem(TABLE,180).to_bytes(180,'little') == model and not c.calls,
          'dispatch final table/provider isolation')
    return selected,key


def setup(c,mask):
    registers(c)
    c.reg[3],c.reg[11] = GP,mask


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == APP_HASH, 'firmware identity')
    c = Callbacks(image)
    initialize(c)
    # Validate the newly supported instructions at their original addresses,
    # including sign extension and RV32's five-bit shift count masking.
    for value,shift in product((0,1,0x7fffffff,0x80000000,MASK),(0,1,14,31,32,63)):
        c.reg[11],c.reg[8] = value,shift
        c.run(0x9026,{0x902a})
        signed = value if value < 0x80000000 else value-(1 << 32)
        check(c.reg[15] == (signed // (1 << (shift & 31))) & MASK, 'original SRA semantics')
    for a,b in product((0,1,0x80000000,MASK),repeat=2):
        c.reg[10],c.reg[9] = a,b
        c.run(0x9060,{0x9062})
        check(c.reg[10] == a ^ b, 'original C.XOR semantics')
    total = 0
    for flags,ready,k in product(range(256),(0,1,255),range(256)):
        gate_fixture(c,flags,ready,k)
        callback(c)
        total += 1
    full_bytes = 0
    for ready,k in product(range(256),range(256)):
        gate_fixture(c,16,ready,k)
        callback(c)
        full_bytes += 1
    for old,incoming in product(range(256),(0,1,0x80000000,MASK)):
        gate_fixture(c,16,255,254,old)
        c.reg[10] = incoming
        callback(c)
    # Registration uses full K!=0; callback uses only K parity.
    differences = 0
    for k in range(256):
        gate_fixture(c,16,255,k)
        accepted = gate(c)
        gate_fixture(c,16,255,k)
        value,_ = callback(c)
        check(accepted == (k == 0) and value == (1-(k & 1)), 'K gate/parity distinction')
        differences += int(bool(value) != accepted)
    # Exhaust every 16-bit event mask; empty keys consume the lowest bit only.
    rows(c,[(i,0,0x80000000+i) for i in range(15)])
    for mask in range(65536):
        setup(c,mask)
        dispatch(c)
    # Opaque keys are reached but never run; nonzero payload is never dereferenced.
    boundaries = 0
    for i,flag,payload in product(range(15),(0,1,2,255),(0,1,0xdeadbeef,MASK)):
        rows(c,[(i,OPAQUE | (i & 1),payload)])
        c.mem(TABLE+12*i,1,flag)
        setup(c,(0x80000000 | (0xffff & ~((1 << i)-1))))
        check(dispatch(c)[0] == i, 'opaque selected index')
        boundaries += 1
    chains = 0
    for i,flag,flags,ready,k,payload in product(range(15),(0,255),(0,16),(0,255),
                                               (0,1,2,254,255),(0,0xdeadbeef)):
        rows(c,[(i,KEY,payload)])
        c.mem(TABLE+12*i,1,flag)
        gate_fixture(c,flags,ready,k)
        c.reg[11] = (1 << i) | 0x8000
        dispatch(c,complete=True)
        chains += 1
    # Explicit event injection follows registration: no provider execution or
    # claim that 40058 delivered it. The table entry and indirect call are real.
    registrations = 0
    for i in range(15):
        rows(c,[(i,0,0)])
        gate_fixture(c)
        check(gate(c), 'registration chain gate')
        check(register(c,reply=0)[0] == 'call', 'registration chain normal return')
        setup(c,1 << i)
        dispatch(c,complete=True)
        registrations += 1
    mutations = 0
    for address,old,new,mode,message in (
        (0x9fa2,'93c71700','93c70700','callback','callback exact accesses'),
        (0x9faa,'2386f10a','a386f10a','callback','callback exact accesses'),
        (0x9024,'3d47','3947','scan','dispatch exact accesses'),
        (0x9050,'23a20700','23a00700','dispatch','dispatch table at call')):
        off = address-BASE
        check(image[off:off+len(bytes.fromhex(old))] == bytes.fromhex(old), 'mutation pin')
        mutant = bytearray(image)
        mutant[off:off+len(bytes.fromhex(old))] = bytes.fromhex(new)
        d = Callbacks(mutant)
        initialize(d)
        gate_fixture(d,16,255,0)
        try:
            if mode == 'callback': callback(d)
            else:
                rows(d,[(14 if mode == 'scan' else 0,0 if mode == 'scan' else OPAQUE,0)])
                setup(d,1 << (14 if mode == 'scan' else 0))
                dispatch(d)
        except RuntimeError as error:
            check(str(error) == message, 'unexpected mutation failure: '+str(error))
            mutations += 1
        else: raise RuntimeError('mutation escaped')
    print('PASS: %d callback config/ready/K cases; %d full ready/K bytes; 1024 overwrite/input cases; %d nonzero-even K gate differences' % (total,full_bytes,differences))
    print('PASS: 46 original SRA/C.XOR vectors; 65536 event masks; %d opaque callback boundaries; %d actual 901a-to-9f7a chains; %d registration/injected-event chains; %d mutations' % (boundaries,chains,registrations,mutations))
    print('PASS: exact access/store order and restored frames; nonzero payload stays opaque; event/timer/free providers NOT executed')


if __name__ == '__main__':
    verify(IMAGE.read_bytes())
