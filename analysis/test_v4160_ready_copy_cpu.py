"""Original ready19 -> 12AD0 -> software copy -> 128FE boundary.

Synthetic memory only. Original local APP copy runs; opaque downstream bodies
stop before execution. Normal downstream returns are explicit hypotheses.
"""
from hashlib import sha256
from test_v4160_source19_cpu import (Source19,initialize,fixture,assemble,
    run_segment,GP,DATA,SAVED,dispatch)
from test_v4160_feature_outer_cpu import registers,APP_HASH,MODE
from test_v4160_zero_id_queue_cpu import IMAGE,BASE,RETURN,MASK,check

ENTRY,LOCAL_COPY,NEXT,ZERO = 0x12ad0,0x19bf0,0x128fe,0x1299e
SOURCES = {1:(0x19d08,94,0x12b00),2:(0x19d68,106,0x12b1e)}
ARENA = 0x24000000


class ReadyCopy(Source19):
    CODE_RANGES = Source19.CODE_RANGES+((ENTRY,0x12b24),(LOCAL_COPY,0x19ca6))

    def mem(self,address,size,value=None):
        result = super().mem(address,size,value)
        # Parent trace excludes APP bytes; explicitly include this literal span.
        if getattr(self,'trace_active',False) and 0x19d08 <= address < 0x19dd2:
            self.events.append(('r' if value is None else 'w',address,size,
                                result if value is None else value & ((1 << (size*8))-1)))
        return result

    def run(self,start,stops,budget=1000):
        # Shared CPU lacks RV32 XOR. Decode only this exact original entry word;
        # all remaining original instructions use the unchanged shared decoder.
        if start == LOCAL_COPY and start not in stops:
            check(self.mem(start,4) == 0x00a5c7b3,'local-copy XOR entry pin')
            self.put(15,self.reg[11]^self.reg[10])
            start,budget = start+4,budget-1
        return super().run(start,stops,budget)


def oracle(c,dest,source,count):
    """Live-memory transaction oracle: byte prefix, 36-byte batches, word tail.

    Batch source+32 is read after the first destination word store. This ordering
    matters for overlap; neither bytes slicing nor host memmove is the oracle.
    Scope: valid nonwrapping pointers and count <=110 in mapped fixtures.
    """
    banks = [(a,bytearray(b)) for a,b,w in c.regions]
    events = []
    def access(kind,address,n,value=None):
        hits = [(a,b) for a,b in banks if a <= address and address+n <= a+len(b)]
        check(len(hits) == 1,'copy oracle mapped transaction')
        a,b = hits[0]
        off = address-a
        if kind == 'r': value = int.from_bytes(b[off:off+n],'little')
        else: b[off:off+n] = value.to_bytes(n,'little')
        events.append((kind,address,n,value))
        return value
    p,s,end = dest,source,dest+count
    def unit(n):
        nonlocal p,s
        value = access('r',s,n)
        access('w',p,n,value)
        p,s = p+n,s+n
    if (dest^source)&3 or count <= 3:
        while p < end: unit(1)
        return events
    while p&3: unit(1)
    aligned = end&~3
    while p < aligned-32:
        values = [access('r',s+4*i,4) for i in range(8)]
        access('w',p,4,values[0])
        last = access('r',s+32,4)
        for i in range(1,8): access('w',p+4*i,4,values[i])
        access('w',p+32,4,last)
        p,s = p+36,s+36
    while p < aligned: unit(4)
    while p < end: unit(1)
    return events


def copy(c,dest,source,count,resume):
    c.reg[10:13],c.reg[1] = [dest,source,count],resume
    before = c.reg[:]
    events = oracle(c,dest,source,count)
    check(run_segment(c,LOCAL_COPY,{resume},events,'local software copy') == resume and
          all(c.reg[r] == before[r] for r in range(32)
              if r not in (5,6,7,*range(11,18),*range(28,32))),
          'local-copy preserved registers')
    # Exact coverage includes widths and order above, plus no source overread.
    reads = {a+i for op,a,n,v in events if op == 'r' for i in range(n)}
    writes = {a+i for op,a,n,v in events if op == 'w' for i in range(n)}
    check(reads == set(range(source,source+count)) and writes == set(range(dest,dest+count)),
          'local-copy read/write extent')
    return events


def route(c,selector,finish=False,reply=MASK):
    check(selector in SOURCES,'ready copy selector precondition')
    before = c.reg[:]
    sp,resume = before[2],before[1]
    frame = sp-128
    c.put(10,selector)
    check(run_segment(c,ENTRY,{LOCAL_COPY,NEXT,ZERO,resume},
          [('w',sp-4,4,resume)],'ready selector') == LOCAL_COPY,'ready selector endpoint')
    source,n,link = SOURCES[selector]
    check((c.reg[1],c.reg[2],c.reg[10:13]) == (link,frame,[frame+4,source,n]),
          'ready local-copy arguments')
    # No source fixture: these bytes are the pinned, captured APP literal.
    literal = c.mem(source,n).to_bytes(n,'little')
    events = copy(c,frame+4,source,n,link)
    check(c.mem(frame+4,n).to_bytes(n,'little') == literal,'ready captured literal bytes')
    check(run_segment(c,link,{NEXT},[],'ready downstream entry') == NEXT and
          (c.reg[1],c.reg[2],c.reg[10:12]) == (0x12b0a,frame,[frame+4,n]),
          'ready downstream arguments')
    if finish:
        # Explicit NEXT normal return: all memory/frame, S registers, GP/SP
        # preserved, A/T clobbered. Its body is never executed.
        for r in (1,5,6,7,*range(10,18),*range(28,32)):
            c.put(r,0xcafe0000+r*0x101)
        c.put(10,reply)
        check(run_segment(c,0x12b0a,{resume},[('r',sp-4,4,resume)],'ready caller return') == resume and
              c.reg[10] == reply and all(c.reg[r] == before[r] for r in (1,2,3,4,*SAVED)),
              'ready caller restored result')
    return events


def invalid_or_zero(c,selector):
    before = c.reg[:]
    c.put(10,selector)
    sp,resume = before[2],before[1]
    events = [('w',sp-4,4,resume)]
    if selector: events += [('r',sp-4,4,resume)]
    endpoint = resume if selector else ZERO
    check(run_segment(c,ENTRY,{ZERO,LOCAL_COPY,NEXT,resume},events,'ready other selector') == endpoint,
          'ready other endpoint')
    check((c.reg[1],c.reg[2],c.reg[10]) ==
          ((resume,sp,selector) if selector else (0x12aec,sp-128,0)),
          'ready other frame/result')


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == APP_HASH,'APP identity')
    c = ReadyCopy(image)
    initialize(c)
    c.regions.append((ARENA,bytearray(512),True))
    def prepare():
        fixture(c)
        c.mem(ARENA,512,int.from_bytes(bytes((i*29+7)&255 for i in range(512)),'little'))
    copies = 0
    for n in range(111):
        for dm in range(4):
            for sm in range(4):
                prepare()
                copy(c,ARENA+32+dm,ARENA+256+sm,n,RETURN)
                copies += 1
    overlaps = 0
    for n in (0,3,4,35,36,37,72,94,106):
        for delta in (-8,-4,0,4,8,32):
            prepare()
            first = c.mem(ARENA+96,4)
            copy(c,ARENA+96+delta,ARENA+96,n,RETURN)
            if delta == 32 and n >= 36:
                check(c.mem(ARENA+96+delta+32,4) == first,
                      'local-copy late ninth load sees overwritten source word')
            overlaps += 1
    routes = 0
    for selector in (1,2):
        for residue in range(4):
            for reply in (0,1,MASK):
                fixture(c)
                c.reg[2] += residue
                route(c,selector,True,reply)
                routes += 1
    for selector in (*range(256),256,257,258,0x80000001,MASK):
        if selector in SOURCES: continue
        fixture(c)
        invalid_or_zero(c,selector)
    chains = 0
    for ready in range(1,256):
        fixture(c,ready=ready,stage=255,sub=0)
        check(assemble(c)[0] == 'ready','actual ready19 tail')
        route(c,1,True,ready)
        chains += 1
    for ready in (1,255):
        fixture(c,ready=ready)
        c.mem(MODE,1,1)
        check(dispatch(c,1029,16) == 'tail' and assemble(c)[0] == 'ready','actual dispatch/ready chain')
        route(c,1,True,ready)
    mutants = mutations(image)
    print('PASS: %d count/alignment local-copy cases; %d live-overlap cases; exact ordered reads/stores and preservation' % (copies,overlaps))
    print('PASS: %d selector1/2 caller copies; 259 other selectors; %d ready-byte chains; 2 actual mode1 chains' % (routes,chains))
    print('PASS: captured94/106 literal to stack to128fe; conditional normal return; %d specified mutations; downstream/provider/hardware NOT executed' % mutants)


def mutations(image):
    cases = (
        (0x12af6,'1306e005','1306f005',1,'ready local-copy arguments'),
        (0x12b00,'9305e005','9305f005',1,'ready downstream arguments'),
        (0x19c68,'03a8c5ff','03a885ff',1,'local software copy ordered accesses'),
        (0x19c88,'93874702','93870702',1,'local software copy ordered accesses'),
    )
    for address,old,new,selector,message in cases:
        off = address-BASE
        a,b = bytes.fromhex(old),bytes.fromhex(new)
        check(image[off:off+len(a)] == a,'ready mutation pin')
        mutant = bytearray(image)
        mutant[off:off+len(a)] = b
        c = ReadyCopy(mutant)
        initialize(c)
        fixture(c)
        try: route(c,selector)
        except RuntimeError as error:
            check(str(error) == message,'unexpected ready mutation failure: '+str(error))
        else: raise RuntimeError('ready-copy mutation escaped')
    return len(cases)


if __name__ == '__main__': verify(IMAGE.read_bytes())
