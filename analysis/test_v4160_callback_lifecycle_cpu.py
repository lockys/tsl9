"""Original callback install and post-free continuations, offline only.

Unknown providers stop at entry. Explicit return hooks below are hypotheses,
not executions or inferred implementations of clear/install/free/event services.
"""
from hashlib import sha256
from itertools import product
from test_v4160_callback_dispatch_cpu import Callbacks,dispatch,setup,KEY
from test_v4160_register_gate_cpu import (initialize as init_callbacks,rows,
    register,arguments,FREE,START,REPEAT,TABLE,TASK,GP)
from test_v4160_feature_outer_cpu import registers,APP_HASH
from test_v4160_zero_id_queue_cpu import IMAGE,BASE,RETURN,MASK,check

INIT,CANCEL = 0x907a,0x90b0
CLEAR,INSTALL,EVENT,NEXT = 0x30000f00,0x30000f04,0x30000f08,0x30000f0c
S_REGS = (8,9,*range(18,28))


class Lifecycle(Callbacks):
    CODE_RANGES = Callbacks.CODE_RANGES+((INIT,0x9124),)


def initialize(c):
    init_callbacks(c)
    c.regions.extend(((0x40048,bytearray(CLEAR.to_bytes(4,'little')),False),
                      (0x40080,bytearray(INSTALL.to_bytes(4,'little')),True),
                      (0x4005c,bytearray(EVENT.to_bytes(4,'little')),True),
                      (TASK+1,bytearray([0xff]),True)))
    # Mutable pointer cells model explicitly declared return-hook effects only.
    c.regions[:] = [(a,b,True if a in (0x40058,0x4022c) else w) for a,b,w in c.regions]


def segment(c,start,stops,expected,label):
    c.events,c.trace_active = [],True
    c.writes.clear()
    stop = c.run(start,stops)
    c.trace_active = False
    check(c.events == expected,label+' accesses')
    check(c.writes == [(a,n,v) for op,a,n,v in expected if op == 'w'],label+' stores')
    check(not c.calls,label+' no provider execution')
    return stop


def clobber_callers(c,result=MASK):
    for r in (1,5,6,7,*range(10,18),*range(28,32)):
        c.put(r,0xcafe0000+r*0x101)
    c.put(10,result)


def install(c,reply=0x123456a5,clear_table=True,target=INSTALL):
    before = c.reg[:]
    sp,resume = before[2],before[1]
    old = c.mem(TABLE,180)
    expected = [('w',sp-8,4,before[8]),('r',0x40048,4,CLEAR),('w',sp-4,4,resume)]
    check(segment(c,INIT,{CLEAR},expected,'install clear boundary') == CLEAR and
          c.reg[10:13] == [TABLE,0,180] and
          (c.reg[1],c.reg[2],c.reg[8]) == (0x9096,sp-16,0x40000),
          'install clear arguments/frame')
    check(c.mem(TABLE,180) == old,'APP has no clear stores')
    # First return premise: preserve S0=40000, SP/GP and saved frame. The
    # table may either be cleared or unchanged; APP checks neither outcome.
    if clear_table: c.mem(TABLE,180,0)
    c.mem(0x40080,4,target)
    clobber_callers(c,0xdeadbeef)
    check(segment(c,0x9096,{target},[('r',0x40080,4,target)],'install second boundary') == target and
          (c.reg[10],c.reg[1],c.reg[2]) == (0x901a,0x90a4,sp-16), 'install callback argument')
    check(c.mem(TABLE,180) == (0 if clear_table else old),'declared clear effect only')
    # Second return no longer needs live S0; deliberately corrupt it. Keep
    # SP/GP and saved memory intact; the original epilogue restores caller S0.
    clobber_callers(c,reply)
    c.put(8,0xbad0bad0)
    expected = [('r',sp-4,4,resume),('r',sp-8,4,before[8]),('w',TASK,1,reply & 255)]
    check(segment(c,0x90a4,{resume},expected,'install return') == resume and
          (c.reg[1],c.reg[2],c.reg[10]) == (resume,sp,reply), 'install return value/frame')
    check(all(c.reg[r] == before[r] for r in (3,4,*S_REGS)) and
          c.mem(TASK,1) == reply & 255 and c.mem(TASK+1,1) == 255,
          'install preservation/task canary')


def cancel_free(c,index,task_after,event_target=EVENT,key_after=0x76543210):
    before = c.reg[:]
    sp,resume = before[2],before[1]
    data = c.mem(TABLE,180).to_bytes(180,'little')
    payload = int.from_bytes(data[index*12+8:index*12+12],'little')
    check(payload != 0,'cancel nonzero payload fixture')
    expected = [('w',sp-8,4,before[8]),('w',sp-12,4,before[9]),('w',sp-4,4,resume)]
    expected += [('r',TABLE+12*i+4,4,int.from_bytes(data[12*i+4:12*i+8],'little')) for i in range(index+1)]
    expected += [('r',TABLE+12*index+8,4,payload),('r',0x40068,4,FREE)]
    check(segment(c,CANCEL,{FREE},expected,'cancel free boundary') == FREE and
          (c.reg[10],c.reg[1],c.reg[2],c.reg[8],c.reg[9]) ==
          (payload,0x90e0,sp-16,index,TABLE),'cancel live free frame')
    check(c.mem(TABLE,180).to_bytes(180,'little') == data,'cancel no table writes before free')
    # Declared hook effects: replace task/key/payload and event pointer. No
    # free code runs. S0(index), S1(table), SP/GP/frame must still be preserved.
    row = TABLE+12*index
    c.mem(TASK,1,task_after)
    c.mem(row+4,4,key_after)
    c.mem(row+8,4,0x01234567)
    c.mem(0x4005c,4,event_target)
    clobber_callers(c)
    expected = [('r',sp-8,4,before[8]),('r',sp-4,4,resume),('r',TASK,1,task_after),
                ('w',row+4,4,0),('w',row+8,4,0),('r',0x4005c,4,event_target),
                ('r',sp-12,4,before[9])]
    check(segment(c,0x90e0,{event_target},expected,'cancel after free') == event_target and
          (c.reg[1],c.reg[2],c.reg[10],c.reg[11]) == (resume,sp,task_after,1 << index),
          'cancel event tail arguments')
    model = bytearray(data)
    model[index*12+4:index*12+12] = bytes(8)
    check(c.mem(TABLE,180).to_bytes(180,'little') == model and
          all(c.reg[r] == before[r] for r in (3,4,*S_REGS)) and c.mem(TASK+1,1) == 255,
          'cancel post-free table/frame')


def update_free(c,index,task_after,target,key_after):
    before = c.reg[:]
    sp,resume = before[2],before[1]
    flag,duration,payload = before[11:14]
    data = c.mem(TABLE,180).to_bytes(180,'little')
    check(register(c) == ('free',index),'update free boundary')
    # Preserve live S0(flag),S1(index),S2(table),S3(duration),S4(new payload),
    # SP/GP/frame. Change task/key/old payload and selected downstream cell.
    row = TABLE+12*index
    slot = 0x40058 if flag == 0 else 0x4022c
    c.mem(TASK,1,task_after)
    c.mem(row+4,4,key_after)
    c.mem(row+8,4,0x01234567)
    c.mem(slot,4,target)
    clobber_callers(c)
    expected = [('r',TASK,1,task_after),('w',row,1,flag & 255),('w',row+8,4,payload)]
    if flag:
        expected += [('r',sp-8,4,before[8]),('r',sp-4,4,resume),
                     ('r',sp-12,4,before[9]),('r',sp-16,4,before[18]),
                     ('r',sp-20,4,before[19]),('r',sp-24,4,before[20])]
    expected.append(('r',slot,4,target))
    check(segment(c,0x91b6,{target},expected,'update after free') == target and
          c.reg[10:13] == [task_after,1 << index,((duration*1000) & MASK)//625],
          'update service arguments')
    if flag:
        check((c.reg[1],c.reg[2]) == (resume,sp) and
              all(c.reg[r] == before[r] for r in S_REGS),'update repeat restored frame')
    else:
        check((c.reg[1],c.reg[2],c.reg[8],c.reg[9],c.reg[18],c.reg[19],c.reg[20]) ==
              (0x9230,sp-32,flag,index,TABLE,duration,payload),'update timer live frame')
    model = bytearray(data)
    model[12*index] = flag & 255
    model[12*index+4:12*index+8] = key_after.to_bytes(4,'little')
    model[12*index+8:12*index+12] = payload.to_bytes(4,'little')
    check(c.mem(TABLE,180).to_bytes(180,'little') == model and c.mem(TASK+1,1) == 255,
          'update retains hook key and replaces payload')


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == APP_HASH,'firmware identity')
    c = Lifecycle(image)
    initialize(c)
    installs = 0
    for reply,cleared,target in product((*range(256),0x123456a5,0x80000000,MASK),(False,True),(INSTALL,NEXT)):
        registers(c)
        c.reg[3] = GP
        rows(c,task=0xcc)
        install(c,reply,cleared,target)
        installs += 1
    cancels = 0
    for index,task,payload,target in product(range(15),range(256),(1,0xdeadbeef,MASK),(EVENT,NEXT)):
        rows(c,[(index,KEY,payload)])
        arguments(c)
        cancel_free(c,index,task,target,key_after=0 if task & 1 else MASK)
        cancels += 1
    updates = 0
    for index,flag,duration,payload,task,changed in product(range(15),(0,1,255,256,MASK),
            (0,1,10000,0x40000000,MASK),(0,0xdeadbeef),(0,255),(False,True)):
        rows(c,[(index,KEY,MASK)])
        arguments(c,flag=flag,duration=duration,payload=payload)
        update_free(c,index,task,NEXT if changed else (START if flag == 0 else REPEAT),
                    0 if changed else 0x76543210)
        updates += 1
    # Initialization's declared zero-fill premise, followed by an actual empty
    # table consumer: explicit input event, not provider-generated delivery.
    registers(c)
    c.reg[3] = GP
    rows(c)
    install(c,reply=MASK,clear_table=True)
    for i in range(15):
        setup(c,(1 << i) | 0x8000)
        check(dispatch(c) == (i,0),'declared-clear table to actual consumer')
    mutations = 0
    for addr,old,new,which,message in (
        (0x9086,'1306400b','1306300b','init','install clear arguments/frame'),
        (0x909e,'130505f8','130525f8','init','install callback argument'),
        (0x9102,'23a40400','23a60400','cancel','cancel after free accesses'),
        (0x91c8,'23808700','23800700','update','update after free accesses')):
        off = addr-BASE
        check(image[off:off+len(bytes.fromhex(old))] == bytes.fromhex(old),'lifecycle mutation pin')
        mutant = bytearray(image)
        mutant[off:off+len(bytes.fromhex(old))] = bytes.fromhex(new)
        d = Lifecycle(mutant)
        initialize(d)
        rows(d,[(0,KEY,1)])
        arguments(d,flag=1)
        try:
            if which == 'init': install(d)
            elif which == 'cancel': cancel_free(d,0,255)
            else: update_free(d,0,255,NEXT,0)
        except RuntimeError as error:
            check(str(error) == message,'unexpected lifecycle mutation failure: '+str(error))
            mutations += 1
        else: raise RuntimeError('lifecycle mutation escaped')
    print('PASS: %d original 907a install cases; table cleared AND unchanged return hypotheses; full A0/low8 task' % installs)
    print('PASS: %d cancel/free-return cases; %d update/free-return cases; 15 declared-clear/consumer chains; %d mutations' % (cancels,updates,mutations))
    print('PASS: exact post-return accesses/stores/live frames; changed task/key/slot hooks explicit; provider code NOT executed')


if __name__ == '__main__':
    verify(IMAGE.read_bytes())
