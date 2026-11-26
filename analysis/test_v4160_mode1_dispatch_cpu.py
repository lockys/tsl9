"""Original mode1 tree and first call/tail contracts, synthetic records only.
Stop before every callee and before the local 2047 state handler at 152f4.
"""
import argparse
from pathlib import Path
from test_v4160_feature_outer_cpu import (Outer, Trace, registers, ENTRY, GETTER,
    MODE, TABLE, ROW, APP_HASH, SP, SAVED_S0)
from test_v4160_zero_id_queue_cpu import IMAGE, BASE, RETURN, MASK, check
from hashlib import sha256

STATE_HANDLER, COPY = 0x152f4, 0x82a8
RANGES = ((GETTER, 0x82a8), (ENTRY, STATE_HANDLER))
PLAIN_TAIL = {
    130:0xd288,259:0xdac8,280:0xcf96,297:0x10440,325:0xd632,
    505:0xdbcc,524:0xb390,568:0xabc4,579:0xb2fe,599:0x10288,
    602:0xd104,605:0xd332,659:0xb1b6,694:0xb14a,737:0xda74,
    755:0xb402,799:0xd14a,801:0xb372,819:0xd378,825:0xf0d0,
    826:0xd47c,880:0xa054,921:0xb036,923:0xb05c,925:0xd64a,
    950:0x10044,984:0x10096,994:0xc3d4,995:0x100d6,1022:0xd69c,
    1025:0x13bd2,1029:0xd1b2,1267:0x185d8,
}
COPY_CALL = {258:(0,0x15072),627:(2,0x14e70),947:(8,0x151c0),
             1001:(13,0x15238),1013:(15,0x14ff6),1657:(18,0x152c4)}
COPY_TAIL = {306:1,658:3,692:4,978:11,991:12}
DIRECT_CALL = {553:(0xcec0,0x150c4),585:(0xc8a2,0x150e2),
               820:(0x1083c,0x15190),963:(0xc472,0x14f94),1656:(0xff56,0x15050)}
CONDITIONAL = (818,850,962,1021,1250,1251)
KNOWN = set(PLAIN_TAIL)|set(COPY_CALL)|set(COPY_TAIL)|set(DIRECT_CALL)|set(CONDITIONAL)|{614,741,2047}
STOPS = set(PLAIN_TAIL.values())|{COPY,STATE_HANDLER,0x10100,0xd3f6,0xb730}|{t for t,_ in DIRECT_CALL.values()}


class Mode1(Outer):
    CODE_RANGES = RANGES


def contract(ident, byte3, before):
    pointer, resume = before[10], before[1]
    kind, target, args, link = 'return', resume, [TABLE+4, before[11], before[12]], resume
    if ident in PLAIN_TAIL:
        kind, target, args[0] = 'tail', PLAIN_TAIL[ident], pointer
    elif ident in (614,741):
        kind, target, args[:2] = 'tail', 0x10100, [pointer, int(ident == 614)]
    elif ident in COPY_CALL:
        index, link = COPY_CALL[ident]
        kind, target, args = 'call', COPY, [0,index,pointer]
    elif ident in COPY_TAIL:
        kind, target, args = 'tail', COPY, [0,COPY_TAIL[ident],pointer]
    elif ident in DIRECT_CALL:
        target, link = DIRECT_CALL[ident]
        kind, args[0] = 'call', pointer
        if ident == 820:
            args[:2] = [0x1069e,pointer]
    elif ident == 818:
        if byte3 & 3 == 1:
            kind, target, args, link = 'call', COPY, [0,5,pointer], 0x1516a
        else:
            kind, target, args[0] = 'tail', 0xd3f6, pointer
    elif ident == 850:
        if byte3 & 3 < 2:
            kind, target, args = 'tail', COPY, [0,6+(byte3 & 3),pointer]
    elif ident == 962:
        if byte3 & 3 < 2:
            kind, target, args, link = 'call', COPY, [0,9+(byte3 & 3),pointer], 0x15208
        else:
            kind, target, args[0], link = 'call', 0xb730, pointer, 0x151f2
    elif ident in (1021,1250,1251):
        if byte3 & 7 == (0 if ident == 1021 else 5):
            kind, target, args = 'tail', COPY, [0,{1021:14,1250:16,1251:17}[ident],pointer]
    elif ident == 2047:
        kind, target, link = 'state', STATE_HANDLER, 0x14d3a
    return kind, target, args, link


def execute(c, ident, byte3):
    before = c.reg[:]
    pointer, caller_sp, saved_s0 = before[10], before[2], before[8]
    kind, endpoint, args, link = contract(ident, byte3, before)
    expected = [('w',caller_sp-8,4,saved_s0),('w',caller_sp-4,4,before[1]),
                ('r',MODE,1,1),('r',TABLE+4,4,(0x14d5e-TABLE)&MASK),('r',pointer,2,ident)]
    if ident in CONDITIONAL:
        expected.append(('r',pointer+3,1,byte3))
    if kind in ('return','tail'):
        restores = [(caller_sp-4,before[1]),(caller_sp-8,saved_s0)] if kind == 'return' else [(caller_sp-8,saved_s0),(caller_sp-4,before[1])]
        expected.extend(('r',a,4,v) for a,v in restores)
    c.events, c.trace_active = [], True
    c.writes.clear()
    stop = c.run(ENTRY, STOPS|{before[1]})
    c.trace_active = False
    check(stop == endpoint, 'mode1 endpoint')
    check(c.events == expected, 'mode1 ordered data accesses')
    check(c.writes == [(caller_sp-8,4,saved_s0),(caller_sp-4,4,before[1])], 'mode1 write footprint')
    check(c.reg[10:13] == args, 'mode1 call/tail arguments')
    check(c.reg[1] == link, 'mode1 call/tail link')
    live_frame = kind in ('call','state')
    check((c.reg[2],c.reg[8]) == ((caller_sp-16,pointer) if live_frame else (caller_sp,saved_s0)), 'mode1 frame state')
    check(all(c.reg[i] == before[i] for i in range(32) if i not in (1,2,8,10,11,12,14,15)), 'mode1 other registers preserved')
    check(not c.calls, 'provider unexpectedly executed')
    return kind


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == APP_HASH, 'APP identity')
    check(len(KNOWN) == 58, 'mode1 reference census')
    c = Mode1(image)
    c.mem(MODE,1,1)
    c.mem(ROW+3,1,0)
    observed = set()
    for ident in range(65536):
        registers(c)
        c.mem(ROW,2,ident)
        kind = execute(c,ident,0)
        if kind != 'return' or any(a == ROW+3 for op,a,n,v in c.events if op == 'r'):
            observed.add(ident)
    check(observed == KNOWN, 'observed mode1 census')
    for ident in CONDITIONAL:
        for byte3 in range(256):
            registers(c)
            c.mem(ROW,2,ident)
            c.mem(ROW+3,1,byte3)
            execute(c,ident,byte3)
    for ident in KNOWN:
        for length,tag in ((0,0),(8,2),(255,255)):
            registers(c)
            c.mem(ROW,2,ident)
            c.mem(ROW+2,1,length)
            c.mem(ROW+3,1,5)
            c.mem(ROW+11,1,tag)
            execute(c,ident,5)
    for address,before,after,ident,byte3,message in (
        (0x14d62,'13073033','13072033',819,0,'mode1 endpoint'),
        (0x1506c,'8145','8545',258,0,'mode1 call/tail arguments'),
        (0x14f34,'8d8b','9d8b',850,4,'mode1 endpoint'),
    ):
        mutant = bytearray(image)
        offset = address-BASE
        check(mutant[offset:offset+len(bytes.fromhex(before))] == bytes.fromhex(before), 'mode1 mutation pin')
        mutant[offset:offset+len(bytes.fromhex(after))] = bytes.fromhex(after)
        probe = Mode1(mutant)
        registers(probe)
        probe.mem(MODE,1,1)
        probe.mem(ROW,2,ident)
        probe.mem(ROW+3,1,byte3)
        try:
            execute(probe,ident,byte3)
        except RuntimeError as exc:
            check(str(exc) == message, 'unexpected mode1 mutation failure: '+str(exc))
        else:
            raise RuntimeError('mode1 mutation undetected')
    print('PASS: 65536 full-ID cases; 58 recognized IDs; 1536 conditional-byte cases; '
          '174 length/tag probes; 3 mutations; callees/2047 state body NOT executed')


def composition(image,carrier):
    from test_v4160_consumer_classify_cpu import (Classification,classify,snapshot,
        CARRIER_HASH,BODY_HASH,CONTROL,CONTROL_INITIAL,OTHER,S_REGS,S_VALUES)
    from test_v4160_queue_filter_cpu import TABLE as FILTER_TABLE,table_bytes,execute_filter
    from test_v4160_consumer_detach_cpu import fixture,CALLBACK,FRAME_SP,INITIAL_SP
    from test_v4160_tx_entry_cpu import CONFIG
    check(len(carrier) == 191078 and sha256(carrier).hexdigest() == CARRIER_HASH, 'copy candidate identity')
    body = carrier[0x5a2:0x5dc]
    check(sha256(body).hexdigest() == BODY_HASH and carrier[0x4c:0x50] == (0x20000332).to_bytes(4,'little'), 'copy candidate body/slot')
    class Chained(Trace,Classification):
        CODE_RANGES = Classification.CODE_RANGES+RANGES
    counts = dict.fromkeys(('return','tail','call','state'),0)
    for ident in sorted(KNOWN|{0x123,0xffff}):
        for byte3 in (0,1,5):
            row = bytearray(snapshot(ident=ident))
            row[3] = byte3
            data = fixture([])
            data[17*12:17*12+12] = row
            c = Chained(image,body,data,0)
            c.regions.extend(((MODE,bytearray([1,0xff]),True),
                              (FILTER_TABLE,table_bytes(((0xfffe,1,0),(0xfffe,1,0))),True)))
            c.mem(CONFIG+4,1,0)
            check(c.advance() == CALLBACK, 'mode1 composed detach')
            execute_filter(c)
            check(c.reg[10] == 0 and classify(c,row,1) == OTHER and c.probe_calls == 1, 'mode1 composed classification')
            check(c.reg[10] == FRAME_SP+8 and c.reg[1] == 0x12d90 and c.reg[2] == FRAME_SP, 'mode1 composed handoff')
            kind = execute(c,ident,byte3)
            counts[kind] += 1
            if kind == 'return':
                c.scan_start = 0x12d90
                check(c.advance() == RETURN and c.reg[2] == INITIAL_SP and
                      [c.reg[r] for r in S_REGS] == list(S_VALUES), 'mode1 unmatched consumer completion')
            data[17*12:17*12+2] = bytes(2)
            check(c.queue() == data and c.mem(FRAME_SP+8,12) == int.from_bytes(row,'little') and
                  c.csr == 0x88 and c.mem(CONTROL,4) == CONTROL_INITIAL, 'mode1 composed memory/control preserved')
    print('PASS: '+str(sum(counts.values()))+' detached-consumer/mode1 chains; '
          +str(counts)+'; candidate-only copy; first-boundary stops')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--standalone-only',action='store_true')
    parser.add_argument('--carrier',type=Path,default=Path(__file__).resolve().parent/'wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin')
    args = parser.parse_args()
    image = IMAGE.read_bytes()
    verify(image)
    if not args.standalone_only:
        composition(image,args.carrier.read_bytes())
