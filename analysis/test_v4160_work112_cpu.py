"""Original 128FE work buffer and 14 calls, with explicit provider premises.

18BA2 is an MMIO routine and is NEVER executed. Every call stops at its entry;
normal return and destination effects are hypotheses in synthetic memory only.
"""
from hashlib import sha256
from itertools import product
from test_v4160_ready_copy_cpu import (ReadyCopy,initialize,fixture,route,
    invalid_or_zero,copy as local_copy,LOCAL_COPY,GP,SAVED,run_segment)
from test_v4160_feature_outer_cpu import registers,APP_HASH
from test_v4160_source19_cpu import COPY,FILL
from test_v4160_zero_id_queue_cpu import IMAGE,BASE,RETURN,MASK,check

ENTRY,ZERO,MMIO,SOURCE = 0x128fe,0x1299e,0x18ba2,0x25000000
OFFSETS = {8:168,9:164,1:172,18:160,19:156,20:152}


class Work112(ReadyCopy):
    CODE_RANGES = ReadyCopy.CODE_RANGES+((ENTRY,0x129c4),)

    def mem(self,address,size,value=None):
        result = super().mem(address,size,value)
        # The selector-zero literal is immediately before the prior two spans.
        if getattr(self,'trace_active',False) and 0x19ca8 <= address < 0x19d08:
            self.events.append(('r' if value is None else 'w',address,size,
                                result if value is None else value & ((1 << (size*8))-1)))
        return result


def initialize_work(c):
    initialize(c)
    c.regions.append((SOURCE,bytearray(128),True))


def prepare(c,length=112,seed=0):
    fixture(c)
    c.reg[10:12] = [SOURCE,length]
    data = bytes((seed+31*i)&255 for i in range(128))
    c.mem(SOURCE,128,int.from_bytes(data,'little'))
    c.mem(c.reg[2]-176,176,int.from_bytes(bytes((0x91+seed+17*i)&255 for i in range(176)),'little'))


def clobber(c,reply):
    for r in (1,5,6,7,*range(10,18),*range(28,32)):
        c.put(r,0xcafe0000+r*0x101)
    c.put(10,reply)


def prefix(c,zero_fill=True,copy_effect=True,fresh=False):
    before = c.reg[:]
    p,length,sp = before[10],before[11],before[2]
    f = sp-176
    model = bytearray(c.mem(f+32,112).to_bytes(112,'little'))
    expected = [('r',0x40048,4,FILL)]
    expected += [('w',f+OFFSETS[r],4,before[r]) for r in (8,9,1,18,19,20)]
    check(run_segment(c,ENTRY,{FILL},expected,'work112 fill entry') == FILL and
          (c.reg[1],c.reg[2],c.reg[8],c.reg[9],c.reg[10:13]) ==
          (0x12920,f,length,p,[f+32,0,112]),'work112 fill arguments')
    if zero_fill:
        c.mem(f+32,112,0)
        model[:] = bytes(112)
    target = COPY+4 if fresh else COPY
    c.mem(0x4004c,4,target)
    clobber(c,MASK)  # explicit fill return, preserving all S/GP/SP/frame/memory
    n = min(length,112)
    check(run_segment(c,0x12920,{target},[('r',0x4004c,4,target)],'work112 copy entry') == target and
          (c.reg[1],c.reg[2],c.reg[8],c.reg[9],c.reg[10:13]) ==
          (0x1293c,f,length,p,[f+32,p,n]),'work112 copy arguments')
    if copy_effect:
        # Exact synthetic destination effect only; provider code does not run.
        data = c.mem(p,n).to_bytes(n,'little') if n else b''
        if n: c.mem(f+32,n,int.from_bytes(data,'little'))
        model[:n] = data
    clobber(c,0x12345678)  # explicit copy normal return with same preservation
    return before,f,model


def expected_iteration(f,index,model):
    words = [int.from_bytes(model[index*8+2*j:index*8+2*j+2],'little') for j in range(4)]
    shifted = [w<<5 for w in words]
    expected = [('r',f+32+8*index+2*j,2,v) for j,v in enumerate(words)]
    expected += [('w',f+20,4,0),('w',f+22,1,index),('w',f+24,4,0),('w',f+23,1,1)]
    expected += [('w',f+12+2*j,2,v&0xffff) for j,v in enumerate(shifted)]
    expected += [('w',f+28,4,1)]
    payload = b''.join((v&0xffff).to_bytes(2,'little') for v in shifted)
    payload += bytes([0,0,index,1])+bytes(4)+(1).to_bytes(4,'little')
    return expected,shifted,payload


def loop(c,before,f,model,reply=MASK,live=False):
    records = []
    for index in range(14):
        expected,shifted,payload = expected_iteration(f,index,model)
        start = 0x1293c if index == 0 else 0x1298a
        check(run_segment(c,start,{MMIO,before[1]},expected,'work112 iteration') == MMIO,
              'work112 iteration endpoint')
        check((c.reg[1],c.reg[2],c.reg[8],c.reg[9],c.reg[18],c.reg[19],c.reg[20],c.reg[10]) ==
              (0x1298a,f,f+32+8*(index+1),index+1,14,1,1,f+12) and
              c.reg[12:16] == shifted,'work112 iteration context')
        check(c.mem(f+12,20).to_bytes(20,'little') == payload and
              c.mem(f+32,112).to_bytes(112,'little') == model,'work112 record/workspace')
        records.append(payload)
        if live and index < 13:
            # Explicit between-call edits: no claim about actual MMIO side effects.
            c.mem(f+12,20,int.from_bytes(bytes([0xa5])*20,'little'))
            if index == 0:
                data = bytes.fromhex('ffff0008ff070080')
                c.mem(f+40,8,int.from_bytes(data,'little'))
                model[8:16] = data
        clobber(c,reply if index == 13 else 0x11110000+index)
    events = [('r',f+OFFSETS[r],4,before[r]) for r in (1,8,9,18,19,20)]
    check(run_segment(c,0x1298a,{MMIO,before[1]},events,'work112 final return') == before[1] and
          c.reg[10] == reply and all(c.reg[r] == before[r] for r in (1,2,3,4,*SAVED)),
          'work112 restored result')
    check(c.mem(f+32,112).to_bytes(112,'little') == model,'work112 final workspace')
    return records


def work(c,zero_fill=True,copy_effect=True,fresh=False,reply=MASK,live=False):
    before,f,model = prefix(c,zero_fill,copy_effect,fresh)
    return loop(c,before,f,model,reply,live)


def zero_entry(c):
    before = c.reg[:]
    f = before[2]-112
    check(run_segment(c,ZERO,{LOCAL_COPY},[('w',f+108,4,before[1])],'zero96 entry') == LOCAL_COPY and
          (c.reg[1],c.reg[2],c.reg[10:13]) == (0x129b4,f,[f,0x19ca8,96]),'zero96 copy arguments')
    data = c.mem(0x19ca8,96).to_bytes(96,'little')
    local_copy(c,f,0x19ca8,96,0x129b4)
    check(c.mem(f,96).to_bytes(96,'little') == data,'zero96 captured literal')
    check(run_segment(c,0x129b4,{ENTRY},[],'zero96 work entry') == ENTRY and
          (c.reg[1],c.reg[2],c.reg[10:12]) == (0x129be,f,[f,96]),'zero96 work arguments')
    return before,f


def caller_chain(c,selector,reply,zero_fill=True,copy_effect=True,live=False):
    fixture(c)
    inner = c.reg[2]-128-(112 if selector == 0 else 0)-176
    seed = bytes((0xd3+selector+13*i)&255 for i in range(176))
    c.mem(inner,176,int.from_bytes(seed,'little'))
    original = c.reg[:]
    if selector:
        route(c,selector)
        records = work(c,zero_fill,copy_effect,True,reply,live)
        start = 0x12b0a
    else:
        invalid_or_zero(c,0)
        before,f = zero_entry(c)
        records = work(c,zero_fill,copy_effect,True,reply,live)
        check(run_segment(c,0x129be,{before[1]},[('r',f+108,4,before[1])],'zero96 return') == before[1] and
              (c.reg[1],c.reg[2]) == (before[1],before[2]),'zero96 restored caller')
        start = 0x12aec
    sp,resume = original[2],original[1]
    check(run_segment(c,start,{resume},[('r',sp-4,4,resume)],'outer work112 return') == resume and
          c.reg[10] == reply and all(c.reg[r] == original[r] for r in (1,2,3,4,*SAVED)),
          'outer work112 restored result')
    return records


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == APP_HASH,'APP identity')
    c = Work112(image)
    initialize_work(c)
    cases = 0
    lengths = (*range(256),256,257,0x80000001,MASK)
    for n,zero,copied in product(lengths,(False,True),(False,True)):
        prepare(c,n,n&255)
        work(c,zero,copied,True,n)
        cases += 1
    shifts = 0
    for value in (0,1,0x7ff,0x800,0x801,0x1234,0x7fff,0x8000,0xffff):
        prepare(c)
        c.mem(SOURCE,112,int.from_bytes(value.to_bytes(2,'little')*56,'little'))
        records = work(c)
        check(all(r[:8] == ((value<<5)&0xffff).to_bytes(2,'little')*4 for r in records),
              'work112 halfword shift/truncation')
        shifts += 1
    live_cases = 0
    for n in (0,1,7,8,94,96,106,112,256):
        prepare(c,n)
        work(c,False,True,True,1,True)
        live_cases += 1
    chains = 0
    for selector,zero,copied,reply in product(range(3),(False,True),(False,True),(0,MASK)):
        caller_chain(c,selector,reply,zero,copied,True)
        chains += 1
    # Negative preservation probe: altering live S1 ends after the first call.
    prepare(c)
    before,f,model = prefix(c)
    expected,shifted,payload = expected_iteration(f,0,model)
    check(run_segment(c,0x1293c,{MMIO},expected,'work112 negative context') == MMIO,
          'work112 first call context')
    clobber(c,0xdeadbeef)
    c.put(9,14)
    events = [('r',f+OFFSETS[r],4,before[r]) for r in (1,8,9,18,19,20)]
    check(run_segment(c,0x1298a,{MMIO,before[1]},events,'work112 changed counter') == before[1] and
          c.reg[10] == 0xdeadbeef,'work112 loop count needs saved live S1')
    mutants = mutations(image)
    print('PASS: %d full-word length/fill/copy cases, 14 records each; %d shift/truncation cases; %d live-workspace cases' % (cases,shifts,live_cases))
    print('PASS: %d selector0/1/2 complete local chains; original96/94/106 literals; exact frames/records; negative S1 preservation probe' % chains)
    print('PASS: %d specified mutations; provider writes/returns explicit; 18ba2 MMIO body and hardware NOT executed' % mutants)


def mutations(image):
    cases = (
        (0x1290a,'13060007','13061007',112,'work','work112 fill arguments'),
        (0x12924,'13060007','1306f006',MASK,'work','work112 copy arguments'),
        (0x1295e,'1606','1206',112,'work','work112 iteration ordered accesses'),
        (0x12944,'3949','3549',112,'work','work112 iteration context'),
        (0x129a0,'13060006','1306f005',112,'zero','zero96 copy arguments'),
    )
    for address,old,new,n,kind,message in cases:
        off = address-BASE
        a,b = bytes.fromhex(old),bytes.fromhex(new)
        check(image[off:off+len(a)] == a,'work112 mutation pin')
        mutant = bytearray(image)
        mutant[off:off+len(a)] = b
        c = Work112(mutant)
        initialize_work(c)
        prepare(c,n)
        try:
            if kind == 'zero': zero_entry(c)
            else: work(c)
        except RuntimeError as error:
            check(str(error) == message,'unexpected work112 mutation failure: '+str(error))
        else: raise RuntimeError('work112 mutation escaped')
    return len(cases)


if __name__ == '__main__': verify(IMAGE.read_bytes())
