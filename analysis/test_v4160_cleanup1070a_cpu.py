"""Original 1070A no-match closure; no provider or MMIO execution.

Fill effects/returns are explicit. 9AF0's zero flag stops before its MMIO arm;
callback-table hits stop before payload reads/free/event services.
"""
from hashlib import sha256
from itertools import product
from test_v4160_filter_callers_cpu import (Callers,initialize_work,prepare as caller_fixture,
    zero_loop,mmio_return,SINGLE,SWITCH,LOOP,TAIL,ALT,MMIO)
from test_v4160_source19_cpu import run_segment,GP,SAVED,FILL
from test_v4160_feature_outer_cpu import APP_HASH
from test_v4160_zero_id_queue_cpu import IMAGE,BASE,RETURN,MASK,check

CLEAN,CANCEL,MATCH,HW = 0x1070a,0x90b0,0x90cc,0x9af6
TABLE,FIRST,SECOND,FLAG = 0x2000be08,GP+300,0x2000bfb8,GP+168
KEYS = (0x1061c,0x9b36,0x107c0)


class Cleanup(Callers):
    # Deliberately omit 9AF6..9B00, which contains the MMIO store.
    CODE_RANGES = Callers.CODE_RANGES+((CLEAN,0x1074c),(0x10032,0x10044),
        (0x1061c,0x10630),(CANCEL,0x9124),(0x9af0,HW),(0x9b00,0x9b02))


def initialize(c):
    initialize_work(c)
    c.regions.extend(((TABLE-4,bytearray(188),True),(FIRST-1,bytearray(5),True),
                      (SECOND-1,bytearray(14),True),(FLAG,bytearray(2),True)))


def prepare(c,value=0,kind=0,seed=0,flag=1):
    caller_fixture(c,value,seed)
    rows = bytearray((seed+17*i)&255 for i in range(180))
    for i in range(15):
        key = (0 if kind == 0 else 0x70000000+0x100*seed+4*i if kind == 1 else
               KEYS[i%3]|1 if kind == 2 else KEYS[i%3]^0x80000000)
        rows[12*i+4:12*i+8] = key.to_bytes(4,'little')
        rows[12*i+8:12*i+12] = (0xdead0000+i).to_bytes(4,'little')
    c.mem(TABLE-4,188,int.from_bytes(bytes([0xc1])*4+rows+bytes([0xc2])*4,'little'))
    c.mem(FIRST-1,5,int.from_bytes(bytes([0xd1,0xa1,0xa2,0xa3,0xd2]),'little'))
    c.mem(SECOND-1,14,int.from_bytes(bytes([0xe1])+bytes(range(0xb0,0xbc))+bytes([0xe2]),'little'))
    c.mem(FLAG,2,flag|0xee00)
    c.mem(0x40048,4,FILL)


def fill_return(c,reply):
    for r in (1,5,6,7,*range(10,18),*range(28,32)):
        c.put(r,0xcafe0000+r*0x101)
    c.put(10,reply)


def lookup(c,key):
    before = c.reg[:]
    p,resume = before[2],before[1]
    keys = [c.mem(TABLE+12*i+4,4) for i in range(15)]
    index = next((i for i,k in enumerate(keys) if k == key),None)
    expected = [('w',p-8,4,before[8]),('w',p-12,4,before[9]),('w',p-4,4,resume)]
    expected += [('r',TABLE+12*i+4,4,keys[i]) for i in range(15 if index is None else index+1)]
    if index is None:
        expected += [('r',p-4,4,resume),('r',p-8,4,before[8]),('r',p-12,4,before[9])]
    check(c.reg[10] == key,'cleanup lookup input key')
    stop = run_segment(c,CANCEL,{MATCH,resume},expected,'cleanup lookup')
    if index is not None:
        check(stop == MATCH and (c.reg[1],c.reg[2],c.reg[8],c.reg[9],c.reg[10]) ==
              (resume,p-16,index,TABLE,key),'cleanup lookup hit boundary')
        return 'hit',index
    check(stop == resume and c.reg[10] == 1 and
          all(c.reg[r] == before[r] for r in (1,2,3,4,*SAVED)),
          'cleanup lookup miss result')
    return 'miss',None


def cleanup(c,effects=(False,False),replies=(0,MASK),fresh=False):
    before = c.reg[:]
    p,resume = before[2],before[1]
    table = c.mem(TABLE-4,188).to_bytes(188,'little')
    keys = [c.mem(TABLE+12*i+4,4) for i in range(15)]
    check(not set(KEYS)&set(keys),'cleanup requires all three keys absent')
    expected = [('w',p-4,4,resume),('r',0x40048,4,FILL)]
    check(run_segment(c,CLEAN,{FILL},expected,'cleanup first fill') == FILL and
          (c.reg[1],c.reg[2],c.reg[10:13]) == (0x10712,p-16,[FIRST,0,3]),
          'cleanup first fill arguments')
    if effects[0]: c.mem(FIRST,3,0)  # explicit destination-only effect
    fill_return(c,replies[0])
    target = FILL+4 if fresh else FILL
    c.mem(0x40048,4,target)
    check(run_segment(c,0x10712,{CANCEL},[('w',SECOND,1,0)],'cleanup first key') == CANCEL and
          (c.reg[1],c.reg[2],c.reg[10]) == (0x10718,p-16,KEYS[0]),
          'cleanup first cancel context')
    check(lookup(c,KEYS[0]) == ('miss',None),'cleanup first cancel miss')
    check(run_segment(c,0x10718,{target},[('r',0x40048,4,target)],'cleanup second fill') == target and
          (c.reg[1],c.reg[2],c.reg[10:13]) == (0x1072c,p-16,[SECOND,0,12]),
          'cleanup second fill arguments')
    if effects[1]: c.mem(SECOND,12,0)
    fill_return(c,replies[1])
    flag = c.mem(FLAG,1)
    stop = run_segment(c,0x1072c,{CANCEL,HW},[('r',FLAG,1,flag)],'cleanup flag')
    check(stop == (CANCEL if flag else HW),'cleanup flag endpoint')
    if not flag:
        check((c.reg[1],c.reg[2],c.reg[10]) == (0x10730,p-16,replies[1]),
              'cleanup zero flag boundary')
        check(c.mem(TABLE-4,188).to_bytes(188,'little') == table,'cleanup stopped table')
        return 'mmio-boundary'
    check((c.reg[1],c.reg[2],c.reg[10]) == (0x1073c,p-16,KEYS[1]),
          'cleanup second cancel context')
    check(lookup(c,KEYS[1]) == ('miss',None),'cleanup second cancel miss')
    check(run_segment(c,0x1073c,{CANCEL},[('r',p-4,4,resume)],'cleanup final tail') == CANCEL and
          (c.reg[1],c.reg[2],c.reg[10]) == (resume,p,KEYS[2]),
          'cleanup final cancel context')
    check(lookup(c,KEYS[2]) == ('miss',None),'cleanup final cancel miss')
    check(c.reg[10] == 1 and all(c.reg[r] == before[r] for r in (1,2,3,4,*SAVED)),
          'cleanup restored return1')
    check(c.mem(TABLE-4,188).to_bytes(188,'little') == table,'cleanup table unchanged across all three')
    first = bytes(3) if effects[0] else bytes([0xa1,0xa2,0xa3])
    second = bytes(12) if effects[1] else bytes([0])+bytes(range(0xb1,0xbc))
    check(c.mem(FIRST-1,5).to_bytes(5,'little') == bytes([0xd1])+first+bytes([0xd2]) and
          c.mem(SECOND-1,14).to_bytes(14,'little') == bytes([0xe1])+second+bytes([0xe2]) and
          c.mem(FLAG+1,1) == 0xee,'cleanup bounded effects/canaries')
    return 'return1'


def wrapper_chain(c,entry,value,effects,fresh=False):
    before = c.reg[:]
    p,resume = before[2],before[1]
    size,link = (64,0x12a78) if entry == SINGLE else (32,0x12aaa)
    f = p-size
    check(run_segment(c,entry,{CLEAN},[('w',f+12,4,value),('w',p-4,4,resume)],'cleanup wrapper') == CLEAN and
          (c.reg[1],c.reg[2]) == (link,f),'cleanup wrapper entry frame')
    check(cleanup(c,effects,fresh=fresh) == 'return1','cleanup actual wrapper return')
    check(c.mem(f+12,4) == value,'cleanup saved selector unchanged')
    expected = [('r',f+12,4,value)]
    if entry == SWITCH:
        expected += [('r',p-4,4,resume)]
        target = TAIL if value else LOOP
        check(run_segment(c,link,{TAIL,LOOP},expected,'cleanup wrapper tail') == target and
              (c.reg[1],c.reg[2],c.reg[10]) == (resume,p,value),
              'cleanup wrapper tail context')
        if not value: zero_loop(c,dirty=True)
    else:
        if not value:
            expected += [('w',f+40,4,0),('w',f+40,1,1),('w',f+28,4,0),
                         ('w',f+32,4,0),('w',f+36,4,0),('w',f+44,4,1)]
        target = ALT if value else MMIO
        check(run_segment(c,link,{ALT,MMIO},expected,'cleanup wrapper single') == target and
              (c.reg[1],c.reg[2],c.reg[10]) ==
              ((0x12a9e,f,value) if value else (0x12a94,f,f+28)),
              'cleanup wrapper single context')
        if not value:
            mmio_return(c)  # static A0 preservation premise only, no MMIO body
            check(run_segment(c,0x12a94,{resume},[('r',p-4,4,resume)],'cleanup single return') == resume and
                  c.reg[10] == p-36 and all(c.reg[r] == before[r] for r in (1,2,3,4,*SAVED)),
                  'cleanup single returned pointer')


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == APP_HASH,'APP identity')
    c = Cleanup(image)
    initialize(c)
    direct = 0
    for kind,e0,e1,reply,flag,fresh in product(range(4),(False,True),(False,True),
            ((0,MASK),(MASK,0),(0x1234,0x5678)),(1,128,255),(False,True)):
        prepare(c,0x100,kind,kind,flag)
        check(cleanup(c,(e0,e1),reply,fresh) == 'return1','cleanup direct no-match')
        direct += 1
    flags = 0
    for flag in range(256):
        prepare(c,0x76543210,flag=flag)
        before = c.reg[:]
        stop = run_segment(c,0x9af0,{RETURN,HW},[('r',FLAG,1,flag)],'9af0 guarded branch')
        check(stop == (RETURN if flag else HW) and c.reg[15] == flag and
              all(c.reg[r] == before[r] for r in range(32) if r != 15),
              '9af0 guarded result')
        flags += 1
    for e0,e1 in product((False,True),repeat=2):
        prepare(c,flag=0)
        check(cleanup(c,(e0,e1)) == 'mmio-boundary','cleanup stops before MMIO')
    hits = 0
    for key,index,payload in product(KEYS,range(15),(0,MASK)):
        prepare(c,kind=1)
        c.mem(TABLE+12*index,1,0)
        c.mem(TABLE+12*index+4,4,key)
        c.mem(TABLE+12*index+8,4,payload)
        c.put(10,key)
        check(lookup(c,key) == ('hit',index),'cleanup hit control')
        hits += 1
    chains = 0
    values = (*range(256),256,257,0x80000001,MASK)
    for entry,value,e0,e1 in product((SINGLE,SWITCH),values,(False,True),(False,True)):
        prepare(c,value,value%4,value&255,value%255+1)
        wrapper_chain(c,entry,value,(e0,e1),bool(value&1))
        chains += 1
    mutants = mutations(image)
    print('PASS: %d complete1070a no-match cases; 3 real15-row scans/case; return1; two explicit fill effects/returns' % direct)
    print('PASS: %d guarded flag bytes; 4 full zero-flag prefixes stopped before MMIO; %d table-hit boundaries stopped before payload/free/event' % (flags,hits))
    print('PASS: %d actual-wrapper chains preserve saved selector; %d specified mutations; provider/MMIO bodies NOT executed' % (chains,mutants))


def mutations(image):
    cases = (
        (0x1003a,'0d46','1146','cleanup first fill arguments'),
        (0x1071e,'3146','3546','cleanup second fill arguments'),
        (0x10742,'13052508','13054508','cleanup final cancel context'),
        (0x911e,'0545','0145','cleanup lookup miss result'),
        (0x10746,'4101','2101','cleanup final cancel context'),
        (0x9af4,'91e7','91c7','cleanup flag endpoint'))
    for pc,old,new,message in cases:
        off = pc-BASE
        a,b = bytes.fromhex(old),bytes.fromhex(new)
        check(image[off:off+len(a)] == a,'cleanup mutation pin')
        m = bytearray(image)
        m[off:off+len(a)] = b
        d = Cleanup(m)
        initialize(d)
        prepare(d)
        try: cleanup(d)
        except RuntimeError as error:
            check(str(error) == message,'unexpected cleanup mutation failure: '+str(error))
        else: raise RuntimeError('cleanup mutation escaped')
    return len(cases)


if __name__ == '__main__': verify(IMAGE.read_bytes())
