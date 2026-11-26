"""Original ID2047 state handler, both tables and actual cd4e byte getter.
All data/CSR/copy fixtures are offline; no physical device operations.
"""
import argparse
from hashlib import sha256
from itertools import product
from pathlib import Path
from test_v4160_feature_outer_cpu import Outer, Trace, registers, ENTRY, GETTER, MODE, TABLE, ROW, APP_HASH
from test_v4160_zero_id_queue_cpu import IMAGE, BASE, RETURN, MASK, check

GP, GLOBAL, BYTE_GETTER, BYTE_SOURCE = 0x20004000, 0x20004158, 0xcd4e, 0x2000bf27
STATE_TABLE = 0x1a6d4
TARGETS = (0x15364,0x1536c,0x15370,0x15394,0x153b4,0x153b4,0x153b4,0x153b0)
RANGES = ((GETTER,0x82a8),(ENTRY,0x153ba),(BYTE_GETTER,0xcd58))
CANARY = bytes(range(0xa0,0xb0))


class StateTrace(Trace):
    def mem(self,address,size,value=None):
        result = super().mem(address,size,value)
        if getattr(self,'trace_active',False) and STATE_TABLE <= address < STATE_TABLE+32:
            self.events.append(('r' if value is None else 'w',address,size,
                                result if value is None else value & ((1 << (size*8))-1)))
        return result


class StateCPU(StateTrace,Outer):
    CODE_RANGES = RANGES


def initialize(c):
    c.regions.extend(((GLOBAL,bytearray(CANARY),True),(BYTE_SOURCE,bytearray([0,0xff]),True)))


def state_fixture(c,h,j,k,getter):
    c.mem(GLOBAL,16,int.from_bytes(CANARY,'little'))
    for offset,value in ((348,h),(352,j),(354,k)):
        c.mem(GP+offset,1,value)
    c.mem(BYTE_SOURCE,1,getter)


def record(c,sub,b4=0,b5=0,b8=0,pointer=ROW):
    data = bytearray([0xff,7,8,sub,b4,b5,0xa4,0xa5,b8,0xa7,0xa8,2])
    c.mem(pointer,12,int.from_bytes(data,'little'))
    return data


def prepare(c,sub,b4=0,b5=0,b8=0,h=0,j=0,k=0,getter=0):
    registers(c)
    c.reg[3] = GP
    c.mem(MODE,1,1)
    state_fixture(c,h,j,k,getter)
    record(c,sub,b4,b5,b8)


def execute(c,sub,b4,b5,b8):
    before = c.reg[:]
    pointer,caller_sp,saved_s0,resume = before[10],before[2],before[8],before[1]
    original_global = c.mem(GLOBAL,16).to_bytes(16,'little')
    original_record = c.mem(pointer,12)
    getter = c.mem(BYTE_SOURCE,1)
    h,j,k = (original_global[offset-344] for offset in (348,352,354))
    expected = [('w',caller_sp-8,4,saved_s0),('w',caller_sp-4,4,resume),
                ('r',MODE,1,1),('r',TABLE+4,4,(0x14d5e-TABLE)&MASK),
                ('r',pointer,2,2047),('r',pointer+3,1,sub)]
    def read(address,value): expected.append(('r',address,1,value))
    def write(offset,value): expected.append(('w',GP+offset,1,value))
    called = False
    if sub == 1:
        read(pointer+8,b8)
        write(348,int((b8 & 7) < 4))
        read(pointer+4,b4)
        write(355,(b4 >> 3) & 1)
    elif sub == 2:
        read(pointer+8,b8)
        write(353,int(b8 & 24 == 8))
    elif sub == 3:
        read(pointer+4,b4)
        write(356,int(b4 & 112 == 16))
        read(pointer+5,b5)
        selector = (b5 >> 2) & 7
        expected.append(('r',STATE_TABLE+selector*4,4,(TARGETS[selector]-STATE_TABLE)&MASK))
        if selector in (0,1,4,5,6,7):
            result = (7,8,None,None,0,0,0,9)[selector]
        else:
            read(GP+354,k)
            if k:
                if selector == 2:
                    called = True
                    read(BYTE_SOURCE,getter)
                    result = 10 if getter else 5
                else:
                    result = 6
            else:
                read(GP+348,h)
                if not h:
                    read(GP+352,j)
                result = (1 if h or j else 3) if selector == 2 else (2 if h or j else 4)
        write(357,result)
    expected.extend((('r',caller_sp-4,4,resume),('r',caller_sp-8,4,saved_s0)))
    c.events,c.trace_active = [],True
    c.writes.clear()
    stop = c.run(ENTRY,{BYTE_GETTER,resume})
    if called:
        check(stop == BYTE_GETTER and (c.reg[10],c.reg[1],c.reg[2],c.reg[8]) ==
              (TABLE+4,0x1537a,caller_sp-16,pointer), 'state getter call boundary')
        check(c.events == expected[:len(c.events)] and
              not any(op == 'w' and address == GP+357 for op,address,n,v in c.events), 'state getter pre-call effects')
        getter_regs,getter_writes = c.reg[:],len(c.writes)
        check(c.run(BYTE_GETTER,{0x1537a}) == 0x1537a, 'state getter return')
        check(c.reg[10] == getter and all(c.reg[i] == getter_regs[i] for i in range(32) if i != 10) and
              len(c.writes) == getter_writes, 'state getter result/preservation')
        stop = c.run(0x1537a,{resume})
    check(stop == resume, 'state final return')
    c.trace_active = False
    check(c.events == expected, 'state ordered data accesses')
    check(c.writes == [(a,n,v) for op,a,n,v in expected if op == 'w'], 'state exact stores')
    check((c.reg[1],c.reg[2],c.reg[8],c.reg[10]) ==
          (resume,caller_sp,saved_s0,getter if called else TABLE+4), 'state caller/A0 restoration')
    check(all(c.reg[i] == before[i] for i in range(32) if i not in (1,2,8,10,14,15)), 'state other registers preserved')
    expected_global = bytearray(original_global)
    for op,address,size,value in expected:
        if op == 'w' and GLOBAL <= address < GLOBAL+16:
            expected_global[address-GLOBAL] = value
    check(c.mem(GLOBAL,16).to_bytes(16,'little') == expected_global and c.mem(pointer,12) == original_record,
          'state full globals/canary/record')
    check(c.mem(BYTE_SOURCE,2) == getter | 0xff00 and c.mem(MODE,2) == 0xff01 and not c.calls,
          'state sources preserved/no opaque provider')
    return called


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == APP_HASH, 'APP identity')
    check(tuple((STATE_TABLE+int.from_bytes(image[STATE_TABLE-BASE+i*4:STATE_TABLE-BASE+i*4+4],'little'))&MASK
                for i in range(8)) == TARGETS, 'state relative table')
    c = StateCPU(image)
    initialize(c)
    for sub in range(256):
        prepare(c,sub)
        execute(c,sub,0,0,0)
    for b4,b8 in product(range(256),repeat=2):
        prepare(c,1,b4=b4,b8=b8)
        execute(c,1,b4,0,b8)
    for b8 in range(256):
        prepare(c,2,b8=b8)
        execute(c,2,0,0,b8)
    for b4,b5 in product(range(256),repeat=2):
        prepare(c,3,b4=b4,b5=b5)
        execute(c,3,b4,b5,0)
    for h,j,k,selector,getter in product((0,1,255),(0,1,255),(0,1,255),range(8),(0,1,255)):
        prepare(c,3,b4=16,b5=selector*4,h=h,j=j,k=k,getter=getter)
        execute(c,3,16,selector*4,0)
    for k,getter in product(range(256),repeat=2):
        prepare(c,3,b5=8,k=k,getter=getter)
        execute(c,3,0,8,0)
    for b8,j,k,getter,selector in product((0,4),(0,255),(0,255),(0,1,255),(2,3)):
        prepare(c,1,b4=8,b8=b8,j=j,k=k,getter=getter)
        execute(c,1,8,0,b8)
        check(c.mem(GP+348,1) == int(b8 == 0), 'state sequential H update')
        for sub,args in ((2,(0,0,8)),(3,(16,selector*4,0))):
            registers(c)
            c.reg[3] = GP
            record(c,sub,*args)
            execute(c,sub,*args)
    for address,before,after,args,message in (
        (0x15310,'93b74700','93b73700',dict(sub=1,b8=3),'state ordered data accesses'),
        (STATE_TABLE,'90acffff','98acffff',dict(sub=3),'state ordered data accesses'),
        (0xcd52,'0345951d','0345a51d',dict(sub=3,b5=8,k=1),'state getter result/preservation'),
    ):
        mutant = bytearray(image)
        offset = address-BASE
        check(mutant[offset:offset+len(bytes.fromhex(before))] == bytes.fromhex(before), 'state mutation pin')
        mutant[offset:offset+len(bytes.fromhex(after))] = bytes.fromhex(after)
        probe = StateCPU(mutant)
        initialize(probe)
        prepare(probe,**args)
        try:
            execute(probe,args['sub'],args.get('b4',0),args.get('b5',0),args.get('b8',0))
        except RuntimeError as exc:
            check(str(exc) == message, 'unexpected state mutation failure: '+str(exc))
        else:
            raise RuntimeError('state mutation undetected')
    print('PASS: 256 subcommands; 65536 sub1 byte pairs; 256 sub2 bytes; 65536 sub3 field pairs; '
          '648 state probes; 65536 K/getter pairs; 48 sequential triples; 3 mutations; actual cd4e getter')


def composition(image,carrier):
    from test_v4160_consumer_classify_cpu import (Classification,classify,snapshot,
        CARRIER_HASH,BODY_HASH,CONTROL,CONTROL_INITIAL,OTHER,S_REGS,S_VALUES)
    from test_v4160_queue_filter_cpu import TABLE as FILTER_TABLE,table_bytes,execute_filter
    from test_v4160_consumer_detach_cpu import fixture,CALLBACK,FRAME_SP,INITIAL_SP
    from test_v4160_tx_entry_cpu import CONFIG
    check(len(carrier) == 191078 and sha256(carrier).hexdigest() == CARRIER_HASH, 'copy candidate identity')
    body = carrier[0x5a2:0x5dc]
    check(sha256(body).hexdigest() == BODY_HASH and carrier[0x4c:0x50] == (0x20000332).to_bytes(4,'little'), 'copy candidate body/slot')
    class Chained(StateTrace,Classification):
        CODE_RANGES = Classification.CODE_RANGES+RANGES
    cases = getters = 0
    for sub,selector,h,j,k,getter,field in product((0,1,2,3,255),range(8),(0,255),(0,255),(0,255),(0,1,255),range(4)):
        b4,b8 = (0,8,16,112)[field],(0,3,4,7)[field]
        b5 = selector*4
        row = bytearray(snapshot(ident=2047,length=8))
        row[3],row[4],row[5],row[8] = sub,b4,b5,b8
        data = fixture([])
        data[17*12:17*12+12] = row
        c = Chained(image,body,data,0)
        c.regions.extend(((MODE,bytearray([1,0xff]),True),
                          (FILTER_TABLE,table_bytes(((0xfffe,1,0),(0xfffe,1,0))),True)))
        initialize(c)
        state_fixture(c,h,j,k,getter)
        c.mem(CONFIG+4,1,0)
        check(c.advance() == CALLBACK, 'state composed detach')
        execute_filter(c)
        check(c.reg[10] == 0 and classify(c,row,1) == OTHER, 'state composed classification')
        check(c.reg[10] == FRAME_SP+8 and c.reg[1] == 0x12d90 and c.reg[2] == FRAME_SP, 'state composed handoff')
        getters += int(execute(c,sub,b4,b5,b8))
        c.scan_start = 0x12d90
        check(c.advance() == RETURN and c.reg[2] == INITIAL_SP and
              [c.reg[r] for r in S_REGS] == list(S_VALUES), 'state consumer completion')
        data[17*12:17*12+2] = bytes(2)
        check(c.queue() == data and c.mem(FRAME_SP+8,12) == int.from_bytes(row,'little') and
              c.csr == 0x88 and c.mem(CONTROL,4) == CONTROL_INITIAL, 'state composed memory/control preserved')
        cases += 1
    print(f'PASS: {cases} original consumer/state/scan completions; {getters} actual getter calls; candidate-only upstream copy/probe premise')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--standalone-only',action='store_true')
    parser.add_argument('--carrier',type=Path,default=Path(__file__).resolve().parent/'wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin')
    args = parser.parse_args()
    image = IMAGE.read_bytes()
    verify(image)
    if not args.standalone_only:
        composition(image,args.carrier.read_bytes())
