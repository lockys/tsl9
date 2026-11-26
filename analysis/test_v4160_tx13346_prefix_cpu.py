"""Original 13346 prefix and local wrappers, offline provider boundaries.

Synthetic destination writes/returns are explicit hypotheses, never provider
executions or reads of real ROM/RAM sources. Active-record TX paths stay bounded.
"""
from hashlib import sha256
from itertools import product
from test_v4160_bit1_handler_cpu import (Bit1,initialize as init_bit1,fixture,
    handler,event_entry,TX,RECORD,STAMP,scale,GP,S_REGS,segment)
from test_v4160_feature_outer_cpu import registers,APP_HASH
from test_v4160_zero_id_queue_cpu import IMAGE,BASE,MASK,check

COPY,FILL = 0x30001100,0x30001120
GETTER,LOCAL_DATA = 0xd1a8,0x2000bf48
SAVED = (8,9,18,19,20,21,22,23)
OFFSETS = {1:140,8:136,9:132,18:128,19:124,20:120,21:116,22:112,23:108}


class Prefix(Bit1):
    CODE_RANGES = Bit1.CODE_RANGES+((TX,0x133f0),(0x135ac,0x135ca),
        (0x9e84,0x9ea6),(0x92ba,0x92f2),(GETTER,0xd1b2))


def initialize(c):
    init_bit1(c)
    c.regions[:] = [(a,bytearray(COPY.to_bytes(4,'little')),True) if a == 0x4004c else (a,b,w)
                   for a,b,w in c.regions]
    c.regions.append((0x40048,bytearray(FILL.to_bytes(4,'little')),False))


def clobber(c,reply):
    for r in (1,5,6,7,*range(10,18),*range(28,32)):
        c.put(r,0xcafe0000+r*0x101)
    c.put(10,reply)


def build(c,sid,uid,local_data,zero_fill=True,fresh=False,finish=False,reply=MASK):
    check((len(sid),len(uid),len(local_data)) == (8,14,19),'synthetic data lengths')
    before = c.reg[:]
    sp,resume = before[2],before[1]
    s = sp-144
    model = bytearray(c.mem(s,144).to_bytes(144,'little'))
    t = [COPY+4*i if fresh else COPY for i in range(5)]
    c.mem(0x4004c,4,t[0])
    def apply(events):
        for op,a,n,v in events:
            if op == 'w' and s <= a and a+n <= s+144:
                model[a-s:a-s+n] = v.to_bytes(n,'little')
    def execute(start,stops,events,label):
        stop = segment(c,start,stops,events,label)
        apply(events)
        return stop
    def effect(address,data):
        # Explicit hook destination bytes, not a source read or copy body.
        c.mem(address,len(data),int.from_bytes(data,'little'))
        if s <= address and address+len(data) <= s+144:
            model[address-s:address-s+len(data)] = data
    expected = [('w',s+OFFSETS[r],4,before[r]) for r in (1,8,18,19,20,21,22,23,9)]
    expected += [('r',0x4004c,4,t[0]),('w',s-4,4,0x13362)]
    check(execute(TX,{t[0]},expected,'TX first source') == t[0] and
          (c.reg[1],c.reg[2],c.reg[8],c.reg[10:13]) ==
          (0x9e9c,s-32,0x40000,[s-32,0x08077b00,8]),'TX first source contract')
    effect(s-32,sid)
    clobber(c,reply)
    a,b = int.from_bytes(sid[:4],'little'),int.from_bytes(sid[4:],'little')
    expected = [('r',s-4,4,0x13362),('r',s-32,4,a),('r',s-28,4,b),
                ('r',0x40048,4,FILL),('w',s+12,2,a&0xffff),('w',s+16,2,b&0xffff),
                ('w',s+14,2,a>>16),('w',s+18,2,b>>16)]
    check(execute(0x9e9c,{FILL},expected,'TX fill boundary') == FILL and
          (c.reg[1],c.reg[2],c.reg[10:13]) == (0x13382,s,[s+20,0,76]),'TX fill contract')
    if zero_fill: effect(s+20,bytes(76))
    c.mem(0x4004c,4,t[1])
    clobber(c,reply)
    expected = [('r',s+12,1,sid[0]),('w',s+20,1,0),('w',s+21,1,sid[0]),
                ('r',s+13,1,sid[1]),('w',s+22,1,sid[1]),
                ('w',s-12,4,before[9]),('r',0x4004c,4,t[1]),
                ('w',s-8,4,0x40000),('w',s-16,4,before[18]),('w',s-4,4,0x133a6)]
    check(execute(0x13382,{t[1]},expected,'TX UID first') == t[1] and
          (c.reg[1],c.reg[2],c.reg[8],c.reg[9],c.reg[18],c.reg[10:13]) ==
          (0x92d8,s-16,0x1ffff000,0x40000,s+24,[s+24,0x1ffff7ec,8]),'TX UID first contract')
    effect(s+24,uid[:8])
    c.mem(0x4004c,4,t[2])
    clobber(c,reply)
    expected = [('r',s-8,4,0x40000),('r',0x4004c,4,t[2]),('r',s-4,4,0x133a6),
                ('r',s-12,4,before[9]),('r',s-16,4,before[18])]
    check(execute(0x92d8,{t[2]},expected,'TX UID second') == t[2] and
          (c.reg[1],c.reg[2],c.reg[8],c.reg[9],c.reg[18],c.reg[10:13]) ==
          (0x133a6,s,0x40000,before[9],before[18],[s+32,0x1ffff7e8,6]),'TX UID second contract')
    effect(s+32,uid[8:])
    c.mem(0x4004c,4,t[3])
    clobber(c,reply)
    check(execute(0x133a6,{GETTER},[('r',0x4004c,4,t[3])],'TX local getter entry') == GETTER and
          c.reg[8] == t[3] and (c.reg[1],c.reg[2]) == (0x133ac,s),'TX captured copy pointer')
    # Change slot AFTER S0 captured it: the upcoming third copy keeps t[3].
    c.mem(0x4004c,4,t[4])
    regs = c.reg[:]
    check(execute(GETTER,{0x133ac},[],'TX actual local getter') == 0x133ac and
          c.reg[10] == LOCAL_DATA and all(c.reg[r] == regs[r] for r in range(32) if r != 10),
          'TX local source getter result')
    check(execute(0x133ac,{t[3]},[],'TX local copy boundary') == t[3] and
          (c.reg[1],c.reg[2],c.reg[10:13]) == (0x133b4,s,[s+60,LOCAL_DATA,19]),
          'TX local copy contract')
    check(c.mem(s,144).to_bytes(144,'little') == model,'TX prefix complete frame')
    if not finish: return 'local-copy'
    effect(s+60,local_data)
    clobber(c,reply)
    expected = []
    for index in range(2):
        h,m = c.mem(RECORD+4*index+2,2),c.mem(RECORD+4*index+5,1)
        check(h == 0xfffe or m != 0,'TX skipped-record fixture')
        expected.append(('r',RECORD+4*index+2,2,h))
        if h != 0xfffe: expected.append(('r',RECORD+4*index+5,1,m))
    expected += [('r',s+OFFSETS[r],4,before[r]) for r in (1,*SAVED)]
    check(execute(0x133b4,{resume},expected,'TX skipped-record return') == resume and
          c.reg[10] == reply and all(c.reg[r] == before[r] for r in (1,2,3,4,*S_REGS)),
          'TX skipped-record restored frame/A0')
    check(c.mem(s,144).to_bytes(144,'little') == model,'TX completed frame footprint')
    return 'return'


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == APP_HASH,'firmware identity')
    c = Prefix(image)
    initialize(c)
    uid,local_data = bytes(range(14)),bytes(range(0x80,0x93))
    builds = 0
    for low,high,zero,fresh,reply in product(range(256),(0,0x1234,0xffff),(False,True),
                                          (False,True),(0,MASK)):
        fixture(c,(0xfffe,0,0,0xfffe,0,0))
        sid = (low | ((low ^ 0xa5) << 8) | (high << 16)).to_bytes(4,'little')+bytes([0x55,0xaa,0x12,0x34])
        build(c,sid,uid,local_data,zero,fresh,True,reply)
        builds += 1
    skip_pairs = 0
    for h0,m0,h1,m1 in product((0,0xfffe,0xffff),(0,1,255),repeat=2):
        if (h0 != 0xfffe and not m0) or (h1 != 0xfffe and not m1): continue
        fixture(c,(h0,m0,255,h1,m1,255))
        build(c,bytes(8),uid,local_data,finish=True)
        skip_pairs += 1
    chains = 0
    for raw,elapsed,fresh in product((0,16,MASK),(35,36,0x80000000,MASK),(False,True)):
        fixture(c,stamp=(scale(raw)-elapsed)&MASK)
        c.reg[11] = 0x80000002
        check(event_entry(c)[0] == 'bit1','actual bit1 caller entry')
        check(handler(c,raw=raw) == 'tx','actual bit1 TX tail')
        check(build(c,bytes(range(8)),uid,local_data,fresh=fresh) == 'local-copy','actual TX prefix boundary')
        chains += 1
    mutations = 0
    for addr,old,new,which,message in (
        (0x13370,'1306c004','1306d004','fill','TX fill contract'),
        (0x92ec,'1946','1d46','uid','TX UID second contract'),
        (0x133ae,'4d46','4946','local','TX local copy contract'),
        (0xd1ac,'130505da','130525da','getter','TX local source getter result')):
        off = addr-BASE
        check(image[off:off+len(bytes.fromhex(old))] == bytes.fromhex(old),'TX prefix mutation pin')
        mutant = bytearray(image)
        mutant[off:off+len(bytes.fromhex(old))] = bytes.fromhex(new)
        d = Prefix(mutant)
        initialize(d)
        fixture(d,(0xfffe,0,0,0xfffe,0,0))
        try: build(d,bytes(range(8)),uid,local_data)
        except RuntimeError as error:
            check(str(error) == message,'unexpected TX prefix mutation failure: '+str(error))
            mutations += 1
        else: raise RuntimeError('TX prefix mutation escaped')
    print('PASS: %d original TX prefix/skipped-record returns; %d skip predicates; %d bit1-to-TX local-copy boundaries; %d mutations' % (builds,skip_pairs,chains,mutations))
    print('PASS: exact frame/halfword/copy arguments; slot rereads AND captured target; fill and data-return premises explicit')
    print('PASS: ROM/RAM sources not read; provider bodies, transport and device operations NOT executed')


if __name__ == '__main__':
    verify(IMAGE.read_bytes())
