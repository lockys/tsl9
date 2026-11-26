"""Original TX-stack transport framing and two-record loop, offline only.
Lookup/POST/clock/copy/fill returns are explicit hypotheses; no provider runs.
"""
from hashlib import sha256
from itertools import product
from test_v4160_tx_fields_cpu import (Fields,initialize as init_fields,begin,fields,
    tail,copies,seed,GP,RECORD,S_REGS,segment,CONFIG)
from test_v4160_tx_record_cpu import (prepare,select,pack23,zero_record,FIRST,CLEAR,
    LOOKUP)
from test_v4160_tx13346_prefix_cpu import (build,clobber,SAVED,OFFSETS)
from test_v4160_bit1_handler_cpu import fixture,handler,event_entry,finish,scale
from test_v4160_register_gate_cpu import IMMEDIATE as POST
from test_v4160_feature_outer_cpu import APP_HASH
from test_v4160_zero_id_queue_cpu import IMAGE,BASE,MASK,check

BUFFER,STRIDE = 0x2000b18c,1062


class Loop(Fields):
    CODE_RANGES = Fields.CODE_RANGES+((0x8a90,0x8b6e),)


def initialize(c):
    init_fields(c)
    c.regions.append((BUFFER,bytearray([0xcc])*(STRIDE*2),True))


def run(c,start,stops,expected,label):
    c.events,c.trace_active = [],True
    c.writes.clear()
    stop = c.run(start,stops,budget=30000)
    c.trace_active = False
    check(c.events == expected,label+' accesses')
    check(c.writes == [(a,n,v) for op,a,n,v in expected if op == 'w'],label+' stores')
    check(not c.calls,label+' no provider execution')
    return stop


def start(c,index=0,active=True,via_event=False):
    outer = None
    if via_event:
        check(index == 0,'event initial index')
        fixture(c,(0x123,0,int(active),0xfffe,0,0),stamp=(-35)&MASK)
        c.reg[11] = 0x80000002
        kind,outer = event_entry(c)
        check(kind == 'bit1' and handler(c,raw=0) == 'tx','actual event-to-TX tail')
        build(c,bytes(range(8)),bytes(range(14)),bytes(range(0x80,0x93)))
        s = c.reg[2]
        c.mem(s+60,19,int.from_bytes(bytes(range(0x80,0x93)),'little'))
        clobber(c,MASK)
        seed(c,mode=31,flag=1)
        select(c)
    elif active:
        begin(c,index,mode=31,flag=1)
    else:
        prepare(c,index,active=0)
        select(c)
    s = c.reg[2]
    if active:
        if via_event: pack23(c)
        fields(c)
        tail(c,MASK)
        copies(c,index)
    else: zero_record(c,index)
    check(c.reg[1] == 0x8a90 and c.reg[2] == s-32,'initial lookup context')
    return s,outer


def transport(c,replies=(1,0),secondary=0xfffe,fresh_second=None,tasks=(7,11)):
    before = c.reg[:]
    s = before[2]+32
    handle,length,source,command = before[18],before[8],before[9],before[19]
    check((length,source,command) == (76,s+20,160) and before[1] == 0x8a90,
          'transport chained lookup fixture')
    saved = {r:c.mem(s-o,4) for r,o in ((1,4),(8,8),(9,12),(18,16),(19,20))}
    payload = c.mem(source,76).to_bytes(76,'little')
    old_frame = c.mem(s,144)
    before_buffer = c.mem(BUFFER,STRIDE*2).to_bytes(STRIDE*2,'little')
    model = bytearray(before_buffer)
    c.mem(GP+154,2,secondary)
    for bank,task in enumerate(tasks): c.mem(GP+148+4*bank,1,task)
    clobber(c,replies[0])  # Declared lookup normal return, S/GP/SP/memory preserved.
    if fresh_second is not None: c.mem(GP+154,2,fresh_second)
    live_second = c.mem(GP+154,2)
    bank = 0 if replies[0] == 1 else None
    final_reply = replies[0]
    prefix = []
    if bank is None:
        prefix.append(('r',GP+154,2,live_second))
        if live_second == handle and handle != 0xfffe:
            prefix.append(('r',0x4013c,4,LOOKUP))
            check(run(c,0x8a90,{LOOKUP,POST,saved[1]},prefix,'transport second lookup') == LOOKUP and
                  (c.reg[1],c.reg[2],c.reg[10],c.reg[11]) ==
                  (0x8ab6,s-32,handle,GP+128),'transport second lookup contract')
            clobber(c,replies[1])
            pc,prefix,final_reply = 0x8ab6,[],replies[1]
            if replies[1] == 1: bank = 1
        else: pc = 0x8a90
    else: pc = 0x8a90
    if bank is None:
        expected = prefix+[('r',s-o,4,saved[r]) for r,o in ((1,4),(8,8),(9,12),(18,16),(19,20))]
        check(run(c,pc,{POST,saved[1]},expected,'transport rejected') == saved[1] and
              c.reg[10] == final_reply,'transport rejected A0')
    else:
        b = BUFFER+STRIDE*bank
        checksum = (160+76+sum(payload))&255
        expected = prefix+[('w',b+6,2,0x7f55),('w',b+10,1,76),('w',b+9,1,0),('w',b+8,1,160)]
        for i,value in enumerate(payload): expected += [('r',source+i,1,value),('w',b+11+i,1,value)]
        expected += [('w',b+87,1,checksum),('r',s-4,4,saved[1]),('r',s-12,4,saved[9]),
                     ('r',s-16,4,saved[18]),('r',s-20,4,saved[19]),
                     ('w',b+2,2,82),('w',b+4,2,0),('r',s-8,4,saved[8]),
                     ('r',0x40050,4,POST),('r',GP+148+4*bank,1,tasks[bank])]
        check(run(c,pc,{POST,saved[1]},expected,'transport admitted') == POST and
              c.reg[10:13] == [tasks[bank],1,GP+148+4*bank],'transport POST contract')
        off = bank*STRIDE
        model[off+2:off+6] = bytes([82,0,0,0])
        model[off+6:off+11] = bytes([0x55,0x7f,160,0,76])
        model[off+11:off+87] = payload
        model[off+87] = checksum
    check((c.reg[1],c.reg[2]) == (saved[1],s) and
          all(c.reg[r] == saved[r] for r in (8,9,18,19)) and
          all(c.reg[r] == before[r] for r in (3,4,*range(20,28))),
          'transport restored TX frame')
    check(c.mem(s,144) == old_frame and c.mem(BUFFER,STRIDE*2).to_bytes(STRIDE*2,'little') == model,
          'transport whole payload/buffer')
    return 'return' if bank is None else 'post',bank


def post_return(c,reply):
    check(c.pc == POST and c.reg[1] == 0x135ac,'declared POST return entry')
    # Explicit tail-service return: preserve TX live S/GP/SP/frame and memory.
    clobber(c,reply)


def advance(c):
    s,index,answer = c.reg[2],c.reg[18],c.reg[10]
    resume = c.mem(s+140,4)
    expected = []
    target = resume
    if index == 0:
        h,m,a = (c.mem(RECORD+4+o,n) for o,n in ((2,2),(5,1),(4,1)))
        expected.append(('r',RECORD+6,2,h))
        if h != 0xfffe:
            expected.append(('r',RECORD+9,1,m))
            if not m:
                expected += [('r',RECORD+8,1,a),('w',s+23,1,1)]
                target = FIRST if a else CLEAR
    if target == resume:
        expected += [('r',s+OFFSETS[r],4,c.mem(s+OFFSETS[r],4)) for r in (1,*SAVED)]
    before = c.reg[:]
    check(run(c,0x135ac,{FIRST,CLEAR,resume},expected,'TX next record') == target,'TX next endpoint')
    if target == resume:
        check((c.reg[1],c.reg[2],c.reg[10]) == (resume,s+144,answer) and
              all(c.reg[r] == c.mem(s+OFFSETS[r],4) for r in SAVED) and
              all(c.reg[r] == before[r] for r in (3,4,*range(24,28))), 'TX final frame/A0')
        return 'return'
    check((c.reg[2],c.reg[8],c.reg[9],c.reg[18],c.reg[19]) == (s,0x40000,4,1,0xfffe),
          'TX second record live state')
    return 'active' if target == FIRST else 'clear'


def second(c,kind):
    if kind == 'active':
        seed(c,values={'one':255},mode=1,flag=0)
        pack23(c)
        fields(c)
        tail(c,0)
        copies(c,1)
    else:
        old_fields = c.mem(c.reg[2]+40,4)
        zero_record(c,1)
        check(c.mem(c.reg[2]+32+40,4) == old_fields,'second clear retains fields40..43')


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == APP_HASH,'firmware identity')
    c = Loop(image)
    initialize(c)
    counts = dict.fromkeys(('return','bank0','bank1'),0)
    for first,second_reply,matched,index in product((*range(256),256,257,0x80000001,MASK),
                                                   (0,1,2,MASK),(False,True),(0,1)):
        start(c,index)
        h = c.reg[18]
        kind,bank = transport(c,(first,second_reply),secondary=h if matched else h^1)
        counts['return' if bank is None else 'bank'+str(bank)] += 1
        if kind == 'post': post_return(c,MASK)
        check(advance(c) == 'return','standalone next skip/final return')
    tasks = 0
    for task,bank in product(range(256),(0,1)):
        start(c)
        h = c.reg[18]
        check(transport(c,(1,0) if bank == 0 else (0,1),secondary=h,
                        tasks=(task,task))[1] == bank,'all task bytes POST')
        tasks += 1
    fresh = 0
    for reply in (0,2,256,MASK):
        start(c)
        h = c.reg[18]
        check(transport(c,(reply,1),secondary=h^1,fresh_second=h)[1] == 1,'fresh secondary handle')
        fresh += 1
    next_cases = 0
    for h,m,a,admit,post_value in product((0,0xfffe,0xffff),(0,1,255),(0,1,255),(False,True),(0,1,MASK)):
        s,_ = start(c)
        kind,_ = transport(c,(int(admit),0))
        if kind == 'post': post_return(c,post_value)
        c.mem(RECORD+6,2,h)
        c.mem(RECORD+9,1,m)
        c.mem(RECORD+8,1,a)
        c.mem(s+23,1,0xa5)
        outcome = advance(c)
        check(outcome == ('return' if h == 0xfffe or m else 'active' if a else 'clear'),
              'fresh next record predicate')
        if outcome == 'return': check(c.mem(s+23,1) == 0xa5,'skipped record retains byte23')
        next_cases += 1
    chains = 0
    carried = 0
    for via_event,first_active,next_kind,admit0,admit1,post_value in product((False,True),(False,True),
            ('active','clear','skip'),(False,True),(False,True),(0,MASK)):
        s,outer = start(c,active=first_active,via_event=via_event)
        kind,_ = transport(c,(int(admit0),0))
        if kind == 'post': post_return(c,post_value)
        first_buffer = c.mem(BUFFER,STRIDE)
        c.mem(RECORD+6,2,0xfffe if next_kind == 'skip' else 0x456)
        c.mem(RECORD+9,1,0)
        c.mem(RECORD+8,1,int(next_kind == 'active'))
        outcome = advance(c)
        if next_kind != 'skip':
            check(outcome == next_kind,'two-record second entry')
            second(c,outcome)
            h = c.reg[18]
            kind,bank = transport(c,(0,1 if admit1 else 2),secondary=h)
            check(bank == (1 if admit1 else None),'second record secondary admission')
            check(c.mem(BUFFER,STRIDE) == first_buffer,'second bank leaves first frame intact')
            if first_active and next_kind == 'clear':
                check(c.mem(s+40,4) == 0x079f0031,'actual cross-record fields40..43 carry-over')
                carried += 1
            if kind == 'post': post_return(c,post_value)
            check(advance(c) == 'return','two-record final return')
        else: check(outcome == 'return','two-record skip return')
        if outer is not None: finish(c,outer,2,0x1731a)
        chains += 1
    mutations = 0
    for addr,old,new,which,message in (
        (0x8a90,'8547','8947','admission','transport admitted accesses'),
        (0x8ae0,'134757f5','134767f5','marker','transport admitted accesses'),
        (0x8b62,'a302a800','a303a800','store','transport admitted accesses'),
        (0x135c6,'0549','0149','loop','TX next record accesses')):
        off = addr-BASE
        check(image[off:off+len(bytes.fromhex(old))] == bytes.fromhex(old),'transport-loop mutation pin')
        mutant = bytearray(image)
        mutant[off:off+len(bytes.fromhex(old))] = bytes.fromhex(new)
        d = Loop(mutant)
        initialize(d)
        start(d)
        try:
            if which == 'loop':
                transport(d,(0,0))
                advance(d)
            else: transport(d,(1,0))
        except RuntimeError as error:
            check(str(error) == message,'unexpected transport-loop mutation failure: '+str(error))
            mutations += 1
        else: raise RuntimeError('transport-loop mutation escaped')
    print('PASS: chained admission cases %s; %d task bytes/banks; %d fresh secondary probes; %d next-record live-state cases' % (counts,tasks,fresh,next_cases))
    print('PASS: %d complete two-record/event chains; %d observed fields40..43 carry-over cases; %d mutations' % (chains,carried,mutations))
    print('PASS: original 76-byte stack payload/frame/checksum; lookup and POST returns explicit; no provider/posting/device execution')


if __name__ == '__main__':
    verify(IMAGE.read_bytes())
