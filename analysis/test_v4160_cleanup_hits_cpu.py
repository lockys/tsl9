"""Original 90B0 hit paths composed with 1070A, offline fixtures only.

Free/event/fill bodies NEVER execute. Explicit returns preserve live S context,
GP/SP and saved frames. Table edits are declared synthetic hooks, not services.
"""
from hashlib import sha256
from itertools import product
from test_v4160_cleanup1070a_cpu import (Cleanup,initialize as initialize_cleanup,
    prepare as prepare_cleanup,fill_return,CLEAN,CANCEL,HW,TABLE,FIRST,SECOND,FLAG,KEYS)
from test_v4160_filter_callers_cpu import SINGLE,SWITCH,LOOP,TAIL,ALT,MMIO
from test_v4160_source19_cpu import run_segment,GP,SAVED,FILL
from test_v4160_feature_outer_cpu import APP_HASH
from test_v4160_zero_id_queue_cpu import IMAGE,BASE,RETURN,MASK,check

FREE,EVENT,TASK,SHIFT = 0x30003000,0x30003020,GP+166,0x90e8


class Hits(Cleanup):
    def run(self,start,stops,budget=1000):
        stop = super().run(start,stops|{SHIFT},budget)
        if stop != SHIFT or SHIFT in stops: return stop
        # Shared CPU lacks this RV32 variable SLL. Pin one exact original word;
        # remaining original instructions use the unchanged shared decoder.
        check(self.mem(SHIFT,4) == 0x008595b3,'cancel SLL word pin')
        self.put(11,self.reg[11] << (self.reg[8]&31))
        return super().run(SHIFT+4,stops,budget-1)


def initialize(c):
    initialize_cleanup(c)
    c.regions.extend(((TASK,bytearray([0,0xef]),True),
                      (0x40068,bytearray(FREE.to_bytes(4,'little')),True),
                      (0x4005c,bytearray(EVENT.to_bytes(4,'little')),True)))


def prepare(c,states=(0,0,0),offset=0,value=0,task=0):
    prepare_cleanup(c,value,kind=1,seed=offset,flag=1)
    c.mem(TASK,1,task)
    c.mem(0x40068,4,FREE)
    c.mem(0x4005c,4,EVENT)
    for k,state in enumerate(states):
        if state:
            row = TABLE+12*((offset+5*k)%15)
            c.mem(row+4,4,KEYS[k])
            c.mem(row+8,4,0 if state == 1 else 0xdead0000+k)


def scan(c):
    before = c.reg[:]
    p,resume,key = before[2],before[1],before[10]
    keys = [c.mem(TABLE+12*i+4,4) for i in range(15)]
    index = next((i for i,k in enumerate(keys) if k == key),None)
    expected = [('w',p-8,4,before[8]),('w',p-12,4,before[9]),('w',p-4,4,resume)]
    expected += [('r',TABLE+12*i+4,4,keys[i]) for i in range(15 if index is None else index+1)]
    if index is None:
        expected += [('r',p-4,4,resume),('r',p-8,4,before[8]),('r',p-12,4,before[9])]
        target,payload,kind = resume,None,'miss'
    else:
        payload = c.mem(TABLE+12*index+8,4)
        expected += [('r',TABLE+12*index+8,4,payload)]
        kind,target = ('free',c.mem(0x40068,4)) if payload else ('zero',0x90e0)
        if payload: expected += [('r',0x40068,4,target)]
    stops = {target,FREE,EVENT,FILL,0x90e0,c.mem(0x40068,4),c.mem(0x4005c,4)}
    check(run_segment(c,CANCEL,stops,expected,'matched cancel scan') == target,
          'matched cancel scan endpoint')
    if index is None:
        check(c.reg[10] == 1 and all(c.reg[r] == before[r] for r in (1,2,3,4,*SAVED)),
              'matched cancel miss result')
    else:
        check((c.reg[1],c.reg[2],c.reg[8],c.reg[9],c.reg[10]) ==
              (0x90e0 if payload else resume,p-16,index,TABLE,payload),
              'matched cancel payload boundary')
    return {'before':before,'index':index,'kind':kind,'payload':payload}


def event_tail(c,state):
    before,index = state['before'],state['index']
    p,resume = before[2],before[1]
    task,target = c.mem(TASK,1),c.mem(0x4005c,4)
    row = TABLE+12*index
    expected = [('r',p-8,4,before[8]),('r',p-4,4,resume),('r',TASK,1,task),
                ('w',row+4,4,0),('w',row+8,4,0),('r',0x4005c,4,target),
                ('r',p-12,4,before[9])]
    check(run_segment(c,0x90e0,{target,FILL,FREE,EVENT},expected,'matched cancel event') == target and
          (c.reg[1],c.reg[2],c.reg[10],c.reg[11]) == (resume,p,task,1 << index) and
          all(c.reg[r] == before[r] for r in (3,4,*SAVED)),
          'matched cancel event context')
    return task,1 << index,target


def cancel(c,event_reply=MASK,free_hook=None,event_hook=None):
    state = scan(c)
    if state['kind'] == 'miss': return state
    if state['kind'] == 'free':
        if free_hook: free_hook(c,state)
        fill_return(c,0x76543210)  # explicit free normal return; preserve live S0/S1/frame
    state['event'] = event_tail(c,state)
    if event_hook: event_hook(c,state)
    fill_return(c,event_reply)  # event tail normal return with caller S/frame preserved
    before = state['before']
    check(c.reg[10] == event_reply and all(c.reg[r] == before[r] for r in (2,3,4,*SAVED)),
          'matched cancel event-return premise')
    # RA is caller-saved in the return fixture; the encoded resume PC is explicit.
    state['reply'] = event_reply
    return state


def cleanup(c,event_reply=MASK,fill_effect=False,hooks=None):
    before = c.reg[:]
    p,resume = before[2],before[1]
    hooks = hooks or {}
    expected = [('w',p-4,4,resume),('r',0x40048,4,FILL)]
    check(run_segment(c,CLEAN,{FILL},expected,'hit cleanup fill1') == FILL and
          (c.reg[1],c.reg[2],c.reg[10:13]) == (0x10712,p-16,[FIRST,0,3]),'hit cleanup fill1 context')
    if fill_effect: c.mem(FIRST,3,0)
    fill_return(c,MASK)
    check(run_segment(c,0x10712,{CANCEL},[('w',SECOND,1,0)],'hit cleanup key1') == CANCEL and
          c.reg[10] == KEYS[0] and (c.reg[1],c.reg[2]) == (0x10718,p-16),'hit cleanup key1 context')
    records = []
    def one(i):
        rec = cancel(c,event_reply if i == 2 else 0xa0000000+i,
                     hooks.get(('free',i)),hooks.get(('event',i)))
        records.append(rec)
    one(0)
    check(run_segment(c,0x10718,{FILL},[('r',0x40048,4,FILL)],'hit cleanup fill2') == FILL and
          (c.reg[1],c.reg[2],c.reg[10:13]) == (0x1072c,p-16,[SECOND,0,12]),'hit cleanup fill2 context')
    if fill_effect: c.mem(SECOND,12,0)
    fill_return(c,0x87654321)
    check(run_segment(c,0x1072c,{CANCEL,HW},[('r',FLAG,1,1)],'hit cleanup key2') == CANCEL and
          c.reg[10] == KEYS[1] and (c.reg[1],c.reg[2]) == (0x1073c,p-16),'hit cleanup key2 context')
    one(1)
    check(run_segment(c,0x1073c,{CANCEL},[('r',p-4,4,resume)],'hit cleanup final tail') == CANCEL and
          c.reg[10] == KEYS[2] and (c.reg[1],c.reg[2]) == (resume,p),'hit cleanup final tail context')
    one(2)
    result = 1 if records[2]['kind'] == 'miss' else event_reply
    check(c.reg[10] == result and all(c.reg[r] == before[r] for r in (2,3,4,*SAVED)),
          'hit cleanup result/context')
    return records


def wrapper(c,entry,value,reply):
    before = c.reg[:]
    p,resume = before[2],before[1]
    size,link = (64,0x12a78) if entry == SINGLE else (32,0x12aaa)
    f = p-size
    check(run_segment(c,entry,{CLEAN},[('w',f+12,4,value),('w',p-4,4,resume)],'hit wrapper entry') == CLEAN,
          'hit wrapper entry endpoint')
    cleanup(c,reply)
    check(c.mem(f+12,4) == value,'hit wrapper selector preserved')
    expected = [('r',f+12,4,value)]
    if entry == SWITCH:
        expected += [('r',p-4,4,resume)]
        target = TAIL if value else LOOP
        context = (resume,p,value)
    else:
        if not value:
            expected += [('w',f+40,4,0),('w',f+40,1,1),('w',f+28,4,0),
                         ('w',f+32,4,0),('w',f+36,4,0),('w',f+44,4,1)]
        target = ALT if value else MMIO
        context = (0x12a9e,f,value) if value else (0x12a94,f,f+28)
    check(run_segment(c,link,{target},expected,'hit wrapper reload') == target and
          (c.reg[1],c.reg[2],c.reg[10]) == context,'hit wrapper reload context')


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == APP_HASH,'APP identity')
    c = Hits(image)
    initialize(c)
    direct = 0
    for index,payload,reply,fresh in product(range(15),(0,1,0x80000000,MASK),(0,1,MASK),(False,True)):
        prepare(c)
        c.put(10,KEYS[0])
        row = TABLE+12*index
        c.mem(row+4,4,KEYS[0]); c.mem(row+8,4,payload)
        def change(d,state):
            d.mem(TASK,1,255)
            d.mem(0x4005c,4,EVENT+4)
            # Original code must clear these fresh values without re-reading them.
            d.mem(row+4,4,KEYS[1]); d.mem(row+8,4,0x12345678)
        rec = cancel(c,reply,change if fresh else None)
        check(rec['index'] == index and c.mem(row+4,8) == 0,'matched first row cleared')
        direct += 1
    tasks = 0
    for task,index,payload in product(range(256),(0,14),(0,MASK)):
        prepare(c,task=task)
        c.put(10,KEYS[0])
        c.mem(TABLE+12*index+4,4,KEYS[0]); c.mem(TABLE+12*index+8,4,payload)
        def fresh_task(d,state): d.mem(TASK,1,(task+1)&255)
        rec = cancel(c,free_hook=fresh_task)
        check(rec['event'][:2] == (((task+1)&255 if payload else task),1 << index),
              'fresh task byte after free')
        tasks += 1
    chains = 0
    for offset,states,reply,effect in product(range(15),product(range(3),repeat=3),(0,MASK),(False,True)):
        prepare(c,states,offset,task=offset)
        recs = cleanup(c,reply,effect)
        check([r['kind'] for r in recs] == [({0:'miss',1:'zero',2:'free'}[s]) for s in states],
              'three-key live hit/miss outcomes')
        chains += 1
    # First match only: a duplicate of the first key survives the one lookup.
    prepare(c)
    for index in (1,2):
        c.mem(TABLE+12*index+4,4,KEYS[0]); c.mem(TABLE+12*index+8,4,0)
    recs = cleanup(c)
    check(recs[0]['index'] == 1 and c.mem(TABLE+28,4) == KEYS[0],'duplicate key later row retained')
    # Explicit event edits add later keys; later lookups use the current table.
    prepare(c,(1,0,0),offset=2)
    def add_second(d,state):
        d.mem(TABLE+12*7+4,4,KEYS[1]); d.mem(TABLE+12*7+8,4,1)
    def add_third(d,state):
        d.mem(TABLE+12*12+4,4,KEYS[2]); d.mem(TABLE+12*12+8,4,0)
    recs = cleanup(c,hooks={('event',0):add_second,('event',1):add_third})
    check([r['kind'] for r in recs] == ['zero','free','zero'] and
          [r['index'] for r in recs] == [2,7,12],'future key insertion reread')
    prepare(c,(1,0,1),offset=2)
    def remove_third(d,state): d.mem(TABLE+12*12+4,8,0)
    recs = cleanup(c,0,hooks={('event',0):remove_third})
    check(recs[2]['kind'] == 'miss' and c.reg[10] == 1,'future deletion changes final result')
    wrappers = 0
    for entry,value,states,reply in product((SINGLE,SWITCH),(0,1,256,257,MASK),product(range(3),repeat=3),(0,MASK)):
        prepare(c,states,2,value)
        wrapper(c,entry,value,reply)
        wrappers += 1
    negatives = 0
    for reg,delta in ((8,1),(9,12)):
        prepare(c,(2,0,0),2)
        c.put(10,KEYS[0])
        state = scan(c)
        fill_return(c,0)
        c.put(reg,c.reg[reg]+delta)
        try: event_tail(c,state)
        except RuntimeError as error:
            check(str(error) == 'matched cancel event ordered accesses','unexpected live-context failure')
            negatives += 1
        else: raise RuntimeError('live-context corruption escaped')
    mutants = mutations(image)
    print('PASS: %d matched-row/free/event cases; %d task-byte probes; two live S0/S1 preservation controls' % (direct,tasks))
    print('PASS: %d three-key cleanup chains; %d wrapper reload chains; first duplicate only; explicit later-key insertion/deletion' % (chains,wrappers))
    print('PASS: %d specified mutations; free/event/fill returns explicit; provider/MMIO bodies NOT executed' % mutants)


def mutations(image):
    cases = (
        (0x90d4,'8847','c847','matched cancel scan ordered accesses'),
        (0x90fe,'23a20400','23a40400','matched cancel event ordered accesses'),
        (0x90f2,'03c5610a','03c5710a','matched cancel event ordered accesses'),
        (0x9106,'03a3c705','03a38704','matched cancel event ordered accesses'))
    for pc,old,new,message in cases:
        a,b = bytes.fromhex(old),bytes.fromhex(new)
        off = pc-BASE
        check(image[off:off+len(a)] == a,'matched cancel mutation pin')
        m = bytearray(image)
        m[off:off+len(a)] = b
        d = Hits(m)
        initialize(d)
        prepare(d,(1,0,0),2)
        d.put(10,KEYS[0])
        try: cancel(d)
        except RuntimeError as error:
            check(str(error) == message,'unexpected matched mutation failure: '+str(error))
        else: raise RuntimeError('matched cancel mutation escaped')
    return len(cases)


if __name__ == '__main__': verify(IMAGE.read_bytes())
