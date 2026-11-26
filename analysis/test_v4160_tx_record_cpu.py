"""Original TX record selection, byte23 getters, zero-field path to 8a56.

Provider writes/returns and between-block mutations are explicit fixtures.
No provider body, actual source memory, transport posting or device is executed.
"""
from hashlib import sha256
from itertools import product
from test_v4160_tx13346_prefix_cpu import (Prefix,initialize as init_prefix,build,
    clobber,FILL,GP,RECORD,S_REGS,segment)
from test_v4160_bit1_handler_cpu import fixture
from test_v4160_feature_outer_cpu import APP_HASH
from test_v4160_zero_id_queue_cpu import IMAGE,BASE,MASK,check

FIRST,SECOND,THIRD,BOOL,NEXT = 0xfa2a,0xb1b0,0xfa36,0xa968,0xd314
CLEAR,TRANSPORT,LOOKUP = 0x135ca,0x8a56,0x30000200
X,Y,Z,G,B = GP+278,GP+196,GP+279,GP+357,0x2000bed1


class RecordCPU(Prefix):
    CODE_RANGES = Prefix.CODE_RANGES+((0x133f0,0x13434),(0x13598,0x135ac),
        (CLEAR,0x135e6),(FIRST,0xfa30),(SECOND,0xb1b6),(THIRD,0xfa3c),
        (BOOL,0xa976),(TRANSPORT,0x8a90))


def initialize(c):
    init_prefix(c)
    c.regions[:] = [(a,b,True if a == 0x40048 else w) for a,b,w in c.regions]
    c.regions.extend(((GP+276,bytearray([0xcc]*4),True),(Y,bytearray([0,255]),True),
                      (GP+128,bytearray([0xcc]*32),True),
                      (0x4013c,bytearray(LOOKUP.to_bytes(4,'little')),False)))


def prepare(c,index=0,active=1,handle=0x123,outer_fill=True):
    values = (handle,0,active,0xfffe,0,0) if index == 0 else (0xfffe,0,0,handle,0,active)
    fixture(c,values)
    c.mem(0x40048,4,FILL)
    build(c,bytes(range(8)),bytes(range(14)),bytes(range(0x80,0x93)),zero_fill=outer_fill)
    s = c.reg[2]
    # Explicit normal return of the final 19-byte copy, preserving S/GP/SP/frame.
    c.mem(s+60,19,int.from_bytes(bytes(range(0x80,0x93)),'little'))
    clobber(c,MASK)
    return s


def select(c):
    s = c.reg[2]
    expected = []
    chosen = None
    for i in range(2):
        h,m,a = (c.mem(RECORD+4*i+o,n) for o,n in ((2,2),(5,1),(4,1)))
        expected.append(('r',RECORD+4*i+2,2,h))
        if h == 0xfffe: continue
        expected.append(('r',RECORD+4*i+5,1,m))
        if m: continue
        expected += [('r',RECORD+4*i+4,1,a),('w',s+23,1,1)]
        chosen = i
        break
    check(chosen is not None,'selected record fixture')
    target = FIRST if a else CLEAR
    check(segment(c,0x133b4,{FIRST,CLEAR},expected,'record selection') == target and
          c.reg[2] == s and (c.reg[8],c.reg[9],c.reg[18],c.reg[19],c.reg[20],c.reg[21],
                            c.reg[22],c.reg[23]) ==
          (0x40000,chosen*4,chosen,0xfffe,GP+84,RECORD,1,RECORD),
          'record selection live state')
    if a: check(c.reg[1] == 0x133f4,'record first getter link')
    return chosen,target


def getter(c,entry,resume,address,boolean=False):
    before = c.reg[:]
    value = c.mem(address,1)
    check(segment(c,entry,{resume},[('r',address,1,value)],'record getter') == resume and
          c.reg[10] == (int(bool(value)) if boolean else value) and
          all(c.reg[r] == before[r] for r in range(32) if r != 10),'record getter result/preservation')
    return c.reg[10]


def pack23(c,stack_hooks=(),fresh_g=None):
    s = c.reg[2]
    hook = dict(stack_hooks)
    for stage,entry,resume,address,shift,pc,target in (
        (1,FIRST,0x133f4,X,1,0x133f4,SECOND),
        (2,SECOND,0x13404,Y,2,0x13404,THIRD),
        (3,THIRD,0x13414,Z,3,0x13414,BOOL)):
        value = getter(c,entry,resume,address)
        if stage in hook: c.mem(s+23,1,hook[stage])  # Declared external fixture change.
        if stage == 3 and fresh_g is not None: c.mem(G,1,fresh_g)
        old = c.mem(s+23,1)
        expected = [('r',s+23,1,old)]
        extra = 0
        if stage == 3:
            g = c.mem(G,1)
            expected.append(('r',G,1,g))
            extra = g << 4
        result = (old | (value << shift) | extra)&255
        expected.append(('w',s+23,1,result))
        check(segment(c,pc,{target},expected,'record byte23') == target and
              (c.reg[2],c.reg[10],c.mem(s+23,1)) ==
              (s,((old | (value << shift))&MASK) if stage != 3 else (value << 3)&MASK,result),
              'record byte23 result')
    value = getter(c,BOOL,0x1342c,B,boolean=True)
    check(segment(c,0x1342c,{NEXT},[('w',s+38,1,value)],'record byte38 start') == NEXT and
          (c.reg[1],c.reg[2]) == (0x13434,s),'record next getter boundary')
    return c.mem(s+23,1)


def zero_record(c,index,zero_effect=True,fresh_slot=False,new_handle=None,lookup=True):
    s = c.reg[2]
    model = bytearray(c.mem(s,144).to_bytes(144,'little'))
    def apply(events):
        for op,a,n,v in events:
            if op == 'w' and s <= a and a+n <= s+144: model[a-s:a-s+n] = v.to_bytes(n,'little')
    first = c.mem(0x40048,4)
    expected = [('w',s+38,2,0),('r',0x40048,4,first)]
    check(segment(c,CLEAR,{first},expected,'record clear first') == first and
          (c.reg[1],c.reg[2],c.reg[10:13]) == (0x135d8,s,[s+44,0,16]),'record first clear contract')
    apply(expected)
    if zero_effect:
        c.mem(s+44,16,0)
        model[44:60] = bytes(16)
    second = first+4 if fresh_slot else first
    c.mem(0x40048,4,second)
    clobber(c,MASK)
    expected = [('r',0x40048,4,second)]
    check(segment(c,0x135d8,{second},expected,'record clear second') == second and
          (c.reg[1],c.reg[2],c.reg[10:13]) == (0x135e4,s,[s+79,0,16]),'record second clear contract')
    if zero_effect:
        c.mem(s+79,16,0)
        model[79:95] = bytes(16)
    if new_handle is not None: c.mem(RECORD+4*index+2,2,new_handle)
    clobber(c,MASK)
    h = c.mem(RECORD+4*index+2,2)
    expected = [('r',RECORD+4*index+2,2,h)]
    check(segment(c,0x135e4,{TRANSPORT},expected,'record transport call') == TRANSPORT and
          (c.reg[1],c.reg[2],c.reg[9],c.reg[10:14]) ==
          (0x135ac,s,RECORD+4*index,[h,160,s+20,76]),'record transport arguments')
    check(c.mem(s,144).to_bytes(144,'little') == model,'record clear frame footprint')
    if not lookup: return
    check(h != 0xfffe,'transport lookup fixture')
    c.mem(GP+150,2,h)
    c.mem(GP+154,2,0xfffe)
    expected = [('w',s-8,4,0x40000),('w',s-12,4,RECORD+4*index),
                ('w',s-16,4,index),('w',s-20,4,0xfffe),('w',s-4,4,0x135ac),
                ('r',GP+150,2,h),('r',0x4013c,4,LOOKUP)]
    check(segment(c,TRANSPORT,{LOOKUP},expected,'record transport lookup') == LOOKUP and
          (c.reg[1],c.reg[2],c.reg[8],c.reg[9],c.reg[18],c.reg[19],c.reg[10],c.reg[11]) ==
          (0x8a90,s-32,76,s+20,h,160,h,GP+128),'record transport lookup contract')
    check(c.mem(s,144).to_bytes(144,'little') == model,'record payload stays in caller frame')


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == APP_HASH,'firmware identity')
    c = RecordCPU(image)
    initialize(c)
    packed = 0
    for field,value,base,index in product(range(4),range(256),(0,255),(0,1)):
        s = prepare(c,index=index,active=255)
        values = [base]*4
        values[field] = value
        for a,v in zip((X,Y,Z,G),values): c.mem(a,1,v)
        c.mem(B,1,value)
        check(select(c) == (index,FIRST),'active record selection')
        result = pack23(c)
        x,y,z,g = values
        check(result == (1 | (x << 1) | (y << 2) | (z << 3) | (g << 4))&255,
              'independent byte23 formula')
        packed += 1
    hooks = 0
    for stage,value,index in product((1,2,3),(0,1,0x80,255),(0,1)):
        prepare(c,index=index)
        for a in (X,Y,Z,G): c.mem(a,1,0)
        c.mem(B,1,255)
        select(c)
        check(pack23(c,stack_hooks=((stage,value),),fresh_g=1) == value | 16,'live stack/G probe')
        hooks += 1
    clears = 0
    for index,h,outer,zero,fresh,changed in product((0,1),(0,1,0xfffd,0xffff),
                                                  (False,True),(False,True),(False,True),(False,True)):
        prepare(c,index,active=0,handle=h,outer_fill=outer)
        check(select(c) == (index,CLEAR),'zero record selection')
        zero_record(c,index,zero,fresh,0x1234 if changed else None)
        clears += 1
    # Handle is re-read after both clear calls, without rechecking eligibility.
    for index in (0,1):
        prepare(c,index,active=0)
        select(c)
        zero_record(c,index,new_handle=0xfffe,lookup=False)
    mutations = 0
    for addr,old,new,which,message in (
        (0x133f8,'0605','0a05','shift','record byte23 accesses'),
        (0xfa2a,'03c56111','03c57111','getter','record getter accesses'),
        (0x135d2,'4146','4546','clear','record first clear contract'),
        (0x1359e,'9306c004','9306d004','length','record transport arguments')):
        off = addr-BASE
        check(image[off:off+len(bytes.fromhex(old))] == bytes.fromhex(old),'record mutation pin')
        mutant = bytearray(image)
        mutant[off:off+len(bytes.fromhex(old))] = bytes.fromhex(new)
        d = RecordCPU(mutant)
        initialize(d)
        prepare(d,active=0 if which in ('clear','length') else 1)
        for a,v in ((X,1),(Y,0),(Z,0),(G,0),(B,0)): d.mem(a,1,v)
        select(d)
        try:
            if which in ('clear','length'): zero_record(d,0)
            else: pack23(d)
        except RuntimeError as error:
            check(str(error) == message,'unexpected record mutation failure: '+str(error))
            mutations += 1
        else: raise RuntimeError('record mutation escaped')
    print('PASS: %d actual getter/byte23 chains; %d explicit live stack/G hooks; actual A968 boolean and byte38 first store' % (packed,hooks))
    print('PASS: %d zero-record-to-8a56/lookup chains; 2 fresh FFFE handle boundaries; %d mutations' % (clears,mutations))
    print('PASS: exact frame/store/argument order; source/fill return premises explicit; remaining getters and provider bodies NOT executed')


if __name__ == '__main__':
    verify(IMAGE.read_bytes())
