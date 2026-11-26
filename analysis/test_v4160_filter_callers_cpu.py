"""Other original 18BA2 callers and saved-selector gates, offline only.

1070A/16C72/16DAC and MMIO 18BA2 stop before execution. Normal returns
are explicit premises; 18BA2's A0/S preservation follows the pinned static body.
"""
from hashlib import sha256
from itertools import product
import check_v4160_18ba2_static as contract
from test_v4160_work112_cpu import Work112,initialize_work
from test_v4160_source19_cpu import fixture,run_segment,GP,SAVED
from test_v4160_feature_outer_cpu import registers,APP_HASH
from test_v4160_zero_id_queue_cpu import IMAGE,BASE,RETURN,MASK,check,sx

LOOP,SINGLE,SWITCH,HELPER,MMIO,ALT,TAIL = 0x129c4,0x12a6e,0x12aa0,0x1070a,0x18ba2,0x16c72,0x16dac
SAVES = {8:56,9:52,18:48,19:44,1:60}


class Callers(Work112):
    CODE_RANGES = Work112.CODE_RANGES+((LOOP,0x12a08),(SINGLE,0x12abe))


def prepare(c,value=0,seed=0):
    fixture(c)
    c.reg[10] = value
    p = c.reg[2]
    data = bytes((0x91+seed+29*i)&255 for i in range(128))
    c.mem(p-96,128,int.from_bytes(data,'little'))


def opaque_return(c,reply):
    # Explicit 1070A/16C72 return: preserve S/GP/SP and memory, clobber A/T.
    for r in (1,5,6,7,*range(10,18),*range(28,32)):
        c.put(r,0xcafe0000+r*0x101)
    c.put(10,reply)


def mmio_return(c):
    # No body execution. Unknown A1..A6 values; static body preserves all other
    # GPRs on normal completion. Stores are not modeled as device RAM writes.
    for r in range(11,17): c.put(r,0xaced0000+r*0x101)


def zero_loop(c,dirty=False):
    before = c.reg[:]
    p,resume = before[2],before[1]
    f = p-64
    prefix = [('w',f+SAVES[r],4,before[r]) for r in (8,9,18,19,1)]
    records = []
    for index in range(14):
        expected = prefix if index == 0 else []
        expected += [('w',f+20,4,0),('w',f+22,1,index),('w',f+24,4,0),
                     ('w',f+23,1,1),('w',f+12,4,0),('w',f+16,4,0),('w',f+28,4,1)]
        start = LOOP if index == 0 else 0x129f6
        check(run_segment(c,start,{MMIO,resume},expected,'zero14 record') == MMIO,
              'zero14 endpoint')
        data = bytes(10)+bytes([index,1])+bytes(4)+(1).to_bytes(4,'little')
        check((c.reg[1],c.reg[2],c.reg[8],c.reg[9],c.reg[18],c.reg[19],c.reg[10]) ==
              (0x129f6,f,index+1,14,1,1,f+12) and c.mem(f+12,20).to_bytes(20,'little') == data,
              'zero14 context/record')
        row = contract.formula(data)
        check(row['index'] == index and row['scale_bit'] == 'clear' and row['mode_bit'] == 'set' and
              row['fifo_bit'] == 'clear' and row['late_enable_bit_set'],'zero14 static branch contract')
        records.append(data)
        if dirty and index < 13:
            c.mem(f+12,20,int.from_bytes(bytes([0xa5])*20,'little'))
        mmio_return(c)
    expected = [('r',f+SAVES[r],4,before[r]) for r in (1,8,9,18,19)]
    check(run_segment(c,0x129f6,{MMIO,resume},expected,'zero14 return') == resume and
          c.reg[10] == p-52 and all(c.reg[r] == before[r] for r in (1,2,3,4,*SAVED)),
          'zero14 restored caller/pointer')
    return records


def gate(c,entry,value,helper_reply=MASK,reload=None,complete=True):
    c.put(10,value)
    before = c.reg[:]
    p,resume = before[2],before[1]
    size,link = (64,0x12a78) if entry == SINGLE else (32,0x12aaa)
    f = p-size
    expected = [('w',f+12,4,value),('w',p-4,4,resume)]
    check(run_segment(c,entry,{HELPER},expected,'saved selector entry') == HELPER and
          (c.reg[1],c.reg[2],c.reg[10]) == (link,f,value),'saved selector helper context')
    opaque_return(c,helper_reply)
    selected = value if reload is None else reload
    if reload is not None:
        # Explicit saved-word edit after helper entry; not an observed side effect.
        c.mem(f+12,4,reload)
    expected = [('r',f+12,4,selected)]
    if entry == SWITCH:
        expected += [('r',p-4,4,resume)]
        target = TAIL if selected else LOOP
        check(run_segment(c,link,{LOOP,TAIL},expected,'selector tail') == target and
              (c.reg[1],c.reg[2],c.reg[10]) == (resume,p,selected) and
              all(c.reg[r] == before[r] for r in (3,4,*SAVED)),
              'selector tail restored context')
        if not selected and complete: zero_loop(c,dirty=True)
        return 'tail' if selected else 'loop'
    if not selected:
        expected += [('w',f+40,4,0),('w',f+40,1,1),('w',f+28,4,0),
                     ('w',f+32,4,0),('w',f+36,4,0),('w',f+44,4,1)]
        target = MMIO
    else: target = ALT
    check(run_segment(c,link,{MMIO,ALT},expected,'single selector') == target and
          (c.reg[1],c.reg[2],c.reg[10]) ==
          ((0x12a94,f,f+28) if not selected else (0x12a9e,f,selected)),
          'single selector endpoint/context')
    if not selected:
        data = bytes(12)+(1).to_bytes(4,'little')+(1).to_bytes(4,'little')
        row = contract.formula(data)
        check(c.mem(f+28,20).to_bytes(20,'little') == data and row['index'] == 0 and
              row['scale_bit'] == 'set' and row['mode_bit'] == 'clear' and row['fifo_bit'] == 'clear' and
              row['late_enable_bit_set'] and row['data_words'] == ['0x0','0x0'],
              'single scale1 record contract')
        result = f+28
        mmio_return(c)
        start = 0x12a94
    else:
        if not complete: return 'alternate'
        result = 0x12345678 ^ selected
        opaque_return(c,result)
        start = 0x12a9e
    check(run_segment(c,start,{resume},[('r',p-4,4,resume)],'single caller return') == resume and
          c.reg[10] == result and all(c.reg[r] == before[r] for r in (1,2,3,4,*SAVED)),
          'single restored caller/result')
    return 'alternate' if selected else 'single'


def direct_candidates(data,target,base=BASE):
    """Halfword-aligned raw encodings only; not a CFG/all-caller census."""
    result = []
    for off in range(0,len(data)-1,2):
        p = base+off
        h = int.from_bytes(data[off:off+2],'little')
        if h&3 == 1 and h>>13 in (1,5):
            imm = (h>>12&1)<<11 | (h>>11&1)<<4 | (h>>9&3)<<8 | (h>>8&1)<<10 | (h>>7&1)<<6 | (h>>6&1)<<7 | (h>>3&7)<<1 | (h>>2&1)<<5
            if p+sx(imm,12) == target: result.append((p,2,1 if h>>13 == 1 else 0))
        if off+4 <= len(data):
            w = int.from_bytes(data[off:off+4],'little')
            if w&127 != 0x6f: continue
            imm = (w>>31)<<20 | (w>>12&255)<<12 | (w>>20&1)<<11 | (w>>21&1023)<<1
            if p+sx(imm,21) == target: result.append((p,4,w>>7&31))
    return result


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == APP_HASH,'APP identity')
    static = contract.derive(image)
    check(static['GPR_writes'] == [11,12,13,14,15,16] and static['path_count'] == 36,
          'pinned static MMIO preservation')
    check(direct_candidates(image,MMIO) == [(0x12986,4,1),(0x129f2,4,1),(0x12a90,4,1)],
          'raw direct candidate inventory')
    # Scanner controls cover link and no-link encodings at the final halfword too.
    for raw,width,rd in (('6f000000',4,0),('ef000000',4,1),('01a0',2,0),('0120',2,1)):
        check(direct_candidates(bytes.fromhex(raw),0x1000,0x1000) == [(0x1000,width,rd)],
              'synthetic direct-encoding scanner')
    for pc,width,rd,target in ((0x81ce,2,1,0x81b0),(0x18c90,2,0,0x18c18),
                               (0x12aa6,4,1,HELPER),(0x12ab2,4,0,LOOP)):
        raw = image[pc-BASE:pc-BASE+width]
        check(direct_candidates(raw,target,pc) == [(pc,width,rd)],'captured negative-displacement scanner')
    c = Callers(image)
    initialize_work(c)
    loops = 0
    for seed,residue in product(range(256),range(4)):
        prepare(c,seed=seed)
        c.reg[2] += residue
        zero_loop(c,dirty=True)
        loops += 1
    regular = 0
    values = (*range(256),256,257,0x80000001,MASK)
    for entry,value,reply in product((SINGLE,SWITCH),values,(0,1,MASK)):
        prepare(c,value,value&255)
        gate(c,entry,value,reply)
        regular += 1
    rereads = 0
    for entry,old,new,reply in product((SINGLE,SWITCH),(0,1,2,255,256,257,0x80000001,MASK),values,(0,1,MASK)):
        prepare(c,old,old&255)
        gate(c,entry,old,reply,new)
        rereads += 1
    count = mutations(image)
    print('PASS: 3 raw direct-transfer candidates; 8 scanner controls; %d complete zero14 loops; static18ba2 contract applied without execution' % loops)
    print('PASS: %d original saved-selector cases; %d explicit saved-word rereads; exact single scale1 record and restored tail frames' % (regular,rereads))
    print('PASS: %d specified mutations; conditional pointer returns; 1070a/16c72/16dac and MMIO body NOT executed' % count)


def mutations(image):
    cases = (
        (0x129d6,'b944','bd44','loop','zero14 context/record'),
        (0x129e8,'a30b3101','230b3101','loop','zero14 record ordered accesses'),
        (0x12a80,'2304f102','a304f102','single','single selector ordered accesses'),
        (0x12aaa,'3245','4245','switch','selector tail ordered accesses'),
    )
    for address,old,new,kind,message in cases:
        a,b = bytes.fromhex(old),bytes.fromhex(new)
        off = address-BASE
        check(image[off:off+len(a)] == a,'other callers mutation pin')
        mutant = bytearray(image)
        mutant[off:off+len(b)] = b
        c = Callers(mutant)
        initialize_work(c)
        prepare(c,256)
        try:
            if kind == 'loop': zero_loop(c)
            elif kind == 'single': gate(c,SINGLE,0)
            else: gate(c,SWITCH,256)
        except RuntimeError as error:
            check(str(error) == message,'unexpected other-callers mutation failure: '+str(error))
        else: raise RuntimeError('other-callers mutation escaped')
    return len(cases)


if __name__ == '__main__': verify(IMAGE.read_bytes())
