"""Original TX bytes38..43 through config-copy and transport lookup boundaries.
All data/fill/40060 returns are explicit offline hypotheses; no provider runs.
"""
from hashlib import sha256
from itertools import product
from test_v4160_tx_record_cpu import (RecordCPU,initialize as init_record,prepare,
    select,pack23,GP,RECORD,segment,TRANSPORT,LOOKUP)
from test_v4160_tx13346_prefix_cpu import clobber
from test_v4160_feature_outer_cpu import MODE,APP_HASH,registers
from test_v4160_schedule_171de_cpu import CONFIG,TASK
from test_v4160_zero_id_queue_cpu import IMAGE,BASE,MASK,RETURN,check

TIME,RAW,READY = 0x171ba,0x30001200,0x821e
DEFS = {
 'bool':(0xa968,0xa976,0x2000bed1,1,'bool'),
 'half':(0xd314,0xd322,0x2000bf5c,2,'bool'),
 'byte':(0xd3e8,0xd3f6,0x2000bf5f,1,'bool'),
 'repeat':(0x181c4,0x181ce,0x2000c925,1,'raw'),
 'threshold':(0xb5b4,0xb5c6,0x2000beef,1,'ge2'),
 'six':(0xc35a,0xc364,0x2000bf12,1,'raw'),
 'seven':(0xcd44,0xcd4e,0x2000bf26,1,'raw'),
 'enabled':(0x8440,0x8446,GP+364,1,'raw'),
 'one':(0xf6b0,0xf6ba,0x2000bf9d,1,'raw'),
 'two':(0xf714,0xf71e,0x2000bfa2,1,'raw'),
 'three':(0xf6e2,0xf6ec,0x2000bf9f,1,'raw'),
 'four':(0xf746,0xf750,0x2000bfa4,1,'raw'),
 'five':(0x8202,0x820c,0x2000bee1,1,'raw'),
 'six39':(0xf992,0xf998,GP+277,1,'raw'),
 'mode':(0x829e,0x82a8,MODE,1,'raw')}
NAMES = tuple(n for n in DEFS if n != 'mode')
S_REGS = (8,9,*range(18,28))


class Fields(RecordCPU):
    CODE_RANGES = RecordCPU.CODE_RANGES+((0x13434,0x13598),(READY,0x8248),(TIME,0x171de))+tuple(
        (v[0],v[1]) for v in DEFS.values())


def initialize(c):
    init_record(c)
    c.regions[:] = [(a,b,True if a == GP+84 else w) for a,b,w in c.regions]
    c.regions.extend(((0x2000bf5c,bytearray(4),True),(0x2000c925,bytearray([0,255]),True),
        (0x2000beef,bytearray([0,255]),True),(0x2000bf12,bytearray([0,255]),True),
        (0x2000bf26,bytearray([0]),True),(0x2000bf9c,bytearray([255]*10),True),
        (GP+192,bytearray(4),True),(0x40060,bytearray(RAW.to_bytes(4,'little')),False)))


def seed(c,values=None,cfg4=0,states=(0,0,0),mode=1,flag=0):
    values = {} if values is None else values
    c.mem(GP+84,4,CONFIG)
    for n in NAMES:
        _,_,a,size,_ = DEFS[n]
        c.mem(a,size,values.get(n,0))
    for a,v in ((GP+278,0),(GP+196,0),(GP+279,0),(GP+357,0),
                (CONFIG+4,cfg4),(MODE,mode),(GP+356,flag),(TASK,17)):
        c.mem(a,1,v)
    for i,v in enumerate(states): c.mem(GP+193+i,1,v)


def begin(c,index=0,**kwargs):
    prepare(c,index=index,active=1)
    seed(c,**kwargs)
    select(c)
    pack23(c)


def source(c,name,resume):
    entry,_,address,size,kind = DEFS[name]
    before = c.reg[:]
    raw = c.mem(address,size)
    result = int(bool(raw)) if kind == 'bool' else int(raw >= 2) if kind == 'ge2' else raw
    check(segment(c,entry,{resume},[('r',address,size,raw)],'field getter') == resume and
          c.reg[10] == result and all(c.reg[r] == before[r] for r in range(32) if r != 10),
          'field getter result/preservation')
    return result


def readiness(c,index,resume):
    before = c.reg[:]
    check(before[10] == index,'readiness argument')
    ptr = c.mem(GP+84,4)
    flags = c.mem(ptr+4,1)
    expected = [('r',GP+84,4,ptr),('r',ptr+4,1,flags)]
    value = 0
    if not flags & 8:
        raw = c.mem(GP+193+index,1)
        expected.append(('r',GP+193+index,1,raw))
        value = int(raw < 3)
    check(segment(c,READY,{resume},expected,'field readiness') == resume and c.reg[10] == value and
          all(c.reg[r] == before[r] for r in range(32) if r not in (10,14,15)),
          'field readiness result/preservation')
    return value


def fields(c,repeat_second=None,stack_hooks=(),fresh_flags=None):
    s = c.reg[2]
    hooks = dict(stack_hooks)
    for stage,(name,resume,next_name,shift,mask) in enumerate((
        ('half',0x13434,'byte',1,MASK),('byte',0x13444,'repeat',2,MASK),
        ('repeat',0x13454,'repeat',3,8),('repeat',0x13466,'threshold',3,16),
        ('threshold',0x13478,'six',5,MASK),('six',0x13488,'seven',6,MASK),
        ('seven',0x13498,'enabled',7,MASK))):
        if stage == 3 and repeat_second is not None: c.mem(DEFS['repeat'][2],1,repeat_second)
        value = source(c,name,resume)
        if (38,stage) in hooks: c.mem(s+38,1,hooks[(38,stage)])
        old = c.mem(s+38,1)
        full = old | (((value << shift)&MASK)&mask)
        expected = [('r',s+38,1,old),('w',s+38,1,full&255)]
        target = DEFS[next_name][0]
        check(segment(c,resume,{target},expected,'byte38 assembly') == target and
              c.reg[10] == full and c.mem(s+38,1) == full&255,'byte38 full/low result')
    value = source(c,'enabled',0x134a8)
    check(segment(c,0x134a8,{DEFS['one'][0]},[('w',s+39,1,value)],'byte39 initial') == DEFS['one'][0],
          'byte39 initial endpoint')
    for stage,(name,resume,next_name,shift) in enumerate((
        ('one',0x134b0,'two',1),('two',0x134c0,'three',2),('three',0x134d0,'four',3),
        ('four',0x134e0,'five',4),('five',0x134f0,'six39',5),('six39',0x13500,None,6))):
        value = source(c,name,resume)
        if (39,stage) in hooks: c.mem(s+39,1,hooks[(39,stage)])
        old = c.mem(s+39,1)
        full = old | ((value << shift)&MASK)
        target = READY if next_name is None else DEFS[next_name][0]
        expected = [('r',s+39,1,old),('w',s+39,1,full&255)]
        check(segment(c,resume,{target},expected,'byte39 assembly') == target and
              c.reg[10] == (0 if next_name is None else full),'byte39 full result')
    ready = readiness(c,0,0x13512)
    if fresh_flags is not None: c.mem(CONFIG+4,1,fresh_flags)  # Explicit fixture mutation.
    expected = []
    bit = 0
    if not ready:
        ptr = c.mem(GP+84,4)
        flags = c.mem(ptr+4,1)
        expected += [('r',GP+84,4,ptr),('r',ptr+4,1,flags)]
        bit = ((flags >> 3)^1)&1
    old = c.mem(s+39,1)
    expected += [('r',s+39,1,old),('w',s+39,1,old | (bit << 7))]
    check(segment(c,0x13512,{TIME},expected,'byte39 final bit') == TIME and
          (c.reg[1],c.reg[2]) == (0x13536,s),'byte39 time entry')
    return c.mem(s+38,1),c.mem(s+39,1)


def clock(c,raw):
    before = c.reg[:]
    sp,resume = before[2],before[1]
    task = c.mem(TASK,1)
    expected = [('r',0x40060,4,RAW),('w',sp-4,4,resume),('r',TASK,1,task)]
    check(segment(c,TIME,{RAW},expected,'field clock entry') == RAW and
          (c.reg[1],c.reg[2],c.reg[10],c.reg[11]) == (0x171cc,sp-16,task,1) and
          c.reg[12:14] == before[12:14],'field clock boundary')
    clobber(c,raw)  # Declared scalar normal return, memory/S/GP/SP/frame preserved.
    value = (((raw*10)&MASK)>>4)+50
    check(segment(c,0x171cc,{resume},[('r',sp-4,4,resume)],'field clock finish') == resume and
          (c.reg[1],c.reg[2],c.reg[10]) == (resume,sp,value) and
          all(c.reg[r] == before[r] for r in (3,4,*S_REGS)),'field clock arithmetic/frame')
    return value


def tail(c,raw=0):
    s = c.reg[2]
    value = clock(c,raw)
    check(segment(c,0x13536,{DEFS['mode'][0]},[('w',s+40,2,value&0xffff)],'field halfword') == DEFS['mode'][0],
          'field mode entry')
    mode = source(c,'mode',0x1353e)
    flag = c.mem(GP+356,1)
    out = ((mode&31) | (flag << 7))&255
    check(segment(c,0x1353e,{READY},[('r',GP+356,1,flag),('w',s+42,1,out)],'field byte42') == READY and
          c.reg[10] == 0,'field byte42/readiness entry')
    results = []
    for i,resume in enumerate((0x13552,0x1355c,0x1356e)):
        result = readiness(c,i,resume)
        results.append(result)
        if i == 0:
            expected = [('w',s+43,1,result)]
        else:
            old = c.mem(s+43,1)
            expected = [('r',s+43,1,old)]
            if i == 2:
                ptr = c.mem(GP+84,4)
                expected.append(('r',GP+84,4,ptr))
            expected.append(('w',s+43,1,old | (result << i)))
        if i == 2:
            target = c.mem(0x4004c,4)
            expected.append(('r',0x4004c,4,target))
        else: target = READY
        check(segment(c,resume,{target},expected,'field byte43') == target,'field byte43 endpoint')
        if i < 2: check(c.reg[10] == i+1,'field readiness next argument')
    check(c.mem(s+40,2) == value&0xffff and c.mem(s+42,1) == out and
          c.mem(s+43,1) == sum(v << i for i,v in enumerate(results)),'fields40..43 result')
    check((c.reg[1],c.reg[2],c.reg[10:13]) == (0x13586,s,[s+44,ptr,16]),'field first config copy')


def copies(c,index,fresh=False):
    s = c.reg[2]
    model = bytearray(c.mem(s,144).to_bytes(144,'little'))
    d0,d1 = bytes(range(0xa0,0xb0)),bytes(range(0xb0,0xc0))
    c.mem(s+44,16,int.from_bytes(d0,'little'))
    model[44:60] = d0
    p2 = CONFIG+0x100 if fresh else CONFIG
    t2 = 0x30001300 if fresh else c.mem(0x4004c,4)
    c.mem(GP+84,4,p2)
    c.mem(0x4004c,4,t2)
    clobber(c,MASK)
    expected = [('r',GP+84,4,p2),('r',0x4004c,4,t2)]
    check(segment(c,0x13586,{t2},expected,'field second config copy') == t2 and
          (c.reg[1],c.reg[2],c.reg[10:13]) == (0x13598,s,[s+79,p2+96,16]),'field second config arguments')
    c.mem(s+79,16,int.from_bytes(d1,'little'))
    model[79:95] = d1
    if fresh: c.mem(RECORD+4*index+2,2,0x4321)
    clobber(c,MASK)
    h = c.mem(RECORD+4*index+2,2)
    check(segment(c,0x13598,{TRANSPORT},[('r',RECORD+4*index+2,2,h)],'field transport entry') == TRANSPORT and
          (c.reg[1],c.reg[2],c.reg[10:14]) == (0x135ac,s,[h,160,s+20,76]),'field transport arguments')
    check(c.mem(s,144).to_bytes(144,'little') == model,'field full config-copy frame')
    c.mem(GP+150,2,h)
    expected = [('w',s-8,4,0x40000),('w',s-12,4,RECORD+4*index),('w',s-16,4,index),
                ('w',s-20,4,0xfffe),('w',s-4,4,0x135ac),('r',GP+150,2,h),('r',0x4013c,4,LOOKUP)]
    check(segment(c,TRANSPORT,{LOOKUP},expected,'field transport lookup') == LOOKUP and
          (c.reg[1],c.reg[2],c.reg[10],c.reg[11]) == (0x8a90,s-32,h,GP+128),
          'field transport lookup contract')


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == APP_HASH,'firmware identity')
    c = Fields(image)
    initialize(c)
    packed = 0
    for name,value,base,index in product(NAMES,range(256),(0,255),(0,1)):
        v = dict.fromkeys(NAMES,base)
        v[name] = value
        begin(c,index,values=v)
        b38,b39 = fields(c)
        r = v['repeat']
        expected38 = (int(bool(v['bool'])) | (int(bool(v['half']))<<1) | (int(bool(v['byte']))<<2) |
                      ((r<<3)&8) | ((r<<3)&16) | (int(v['threshold']>=2)<<5) |
                      (v['six']<<6) | (v['seven']<<7))&255
        expected39 = v['enabled']
        for i,n in enumerate(('one','two','three','four','five','six39'),1): expected39 |= v[n] << i
        check((b38,b39) == (expected38,expected39&255),'independent packed bytes')
        packed += 1
    for value in range(65536):
        registers(c)
        c.mem(DEFS['half'][2],2,value)
        check(source(c,'half',RETURN) == int(value != 0),'full halfword boolean')
    repeats = 0
    for first,second,index in product((0,1,2,255),(0,1,2,255),(0,1)):
        begin(c,index,values={'repeat':first})
        a,_ = fields(c,repeat_second=second)
        check(a == ((first<<3)&8) | ((second<<3)&16),'two actual repeat reads')
        repeats += 1
    hooks = 0
    for offset,stage,value in product((38,39),(0,3,5),(0,1,128,255)):
        begin(c)
        fields(c,stack_hooks=(((offset,stage),value),))
        hooks += 1
    readiness_cases = 0
    for cfg4,which,value in product((0,8,255),range(3),(0,1,2,3,255)):
        states = [0,0,0]
        states[which] = value
        begin(c,cfg4=cfg4,states=states)
        fields(c)
        tail(c)
        readiness_cases += 1
    for before,after in product((0,8),repeat=2):
        begin(c,cfg4=before,states=(255,0,0))
        fields(c,fresh_flags=after)
    clock_cases = 0
    for task,raw in product(range(256),(0,1,16,0x19999999,0x1999999a,0x80000000,MASK)):
        registers(c)
        c.reg[3] = GP
        c.mem(TASK,1,task)
        clock(c,raw)
        clock_cases += 1
    tails = 0
    for index,mode,flag,raw,fresh in product((0,1),(0,1,31,32,255),(0,1,2,3,255),
                              (0,0x19999999,0x1999999a,MASK),(False,True)):
        begin(c,index,mode=mode,flag=flag)
        fields(c)
        tail(c,raw)
        copies(c,index,fresh)
        tails += 1
    mutations = 0
    for addr,old,new,which,message in (
        (0x1346c,'4189','2189','repeat','byte38 assembly accesses'),
        (0xb5bc,'13352500','13351500','threshold','field getter result/preservation'),
        (0x171d8,'13052503','13053503','clock','field clock arithmetic/frame'),
        (0x1358e,'93850506','93851506','copy','field second config arguments')):
        off = addr-BASE
        check(image[off:off+len(bytes.fromhex(old))] == bytes.fromhex(old),'field mutation pin')
        mutant = bytearray(image)
        mutant[off:off+len(bytes.fromhex(old))] = bytes.fromhex(new)
        d = Fields(mutant)
        initialize(d)
        begin(d,values={'repeat':2,'threshold':1})
        try:
            fields(d)
            if which in ('clock','copy'):
                tail(d)
                if which == 'copy': copies(d,0)
        except RuntimeError as error:
            check(str(error) == message,'unexpected field mutation failure: '+str(error))
            mutations += 1
        else: raise RuntimeError('field mutation escaped')
    print('PASS: %d original byte38/39 chains; 65536 halfword booleans; %d repeated-read pairs; %d stack hooks' % (packed,repeats,hooks))
    print('PASS: %d readiness cases/4 fresh-flag pairs; %d declared clock returns; %d active-record-to-lookup chains; %d mutations' % (readiness_cases,clock_cases,tails,mutations))
    print('PASS: original getters/fields40..43 and fresh config/slot/handle loads; provider and transport posting bodies NOT executed')


if __name__ == '__main__':
    verify(IMAGE.read_bytes())
