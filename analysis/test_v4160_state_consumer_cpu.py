"""Original cd6a state consumer plus actual 81ee getter/a658 setter.
Stop before b6f4 and fe6a; globals and records are offline bytearray fixtures.
"""
import argparse
from hashlib import sha256
from itertools import product
from pathlib import Path
from test_v4160_state2047_cpu import (StateCPU,initialize as initialize_state,
    prepare as prepare_state,execute as execute_state,GP,GLOBAL)
from test_v4160_feature_outer_cpu import registers,APP_HASH,ROW
from test_v4160_zero_id_queue_cpu import IMAGE,BASE,RETURN,MASK,check

ENTRY,GETTER,SETTER,CALLEE,TAIL = 0xcd6a,0x81ee,0xa658,0xb6f4,0xfe6a
LOCAL,ACTIVE,SOURCE,CELLS,L,R = 0x2000bed0,0x2000bed0,0x2000bed5,0x2000bf2a,0x2000bf2b,0x2000bf2c
SELECTED = {1,2,3,4,6,9,10}


class Gate(StateCPU):
    CODE_RANGES = StateCPU.CODE_RANGES+((ENTRY,0xce88),(GETTER,0x81f8),(SETTER,0xa664))


def initialize(c):
    initialize_state(c)
    c.regions.extend(((LOCAL,bytearray(range(0xb0,0xb8)),True),
                      (CELLS,bytearray(range(0xc0,0xc6)),True)))


def fixture(c,value,category,source,initial_l=0xcc,initial_r=0xdd,active=0xee):
    registers(c)
    c.reg[3],c.reg[10:12] = GP,[value,category]
    c.mem(LOCAL,8,int.from_bytes(bytes(range(0xb0,0xb8)),'little'))
    c.mem(CELLS,6,int.from_bytes(bytes(range(0xc0,0xc6)),'little'))
    for address,byte in ((SOURCE,source),(L,initial_l),(R,initial_r),(ACTIVE,active)):
        c.mem(address,1,byte)


def action(status,category,value,source):
    """Algebraic branch oracle independent of instruction stepping."""
    if status in SELECTED:
        current = 0
        if category == 0:
            current = {1:6,2:2}.get(source,0)
        elif category == 1:
            current = (4 if value else 0) if source == 1 else (0 if value else 8) if source == 2 else (4 if value else 8)
        elif category == 2:
            current = (4 if value else 6) if source == 1 else (2 if value else 8) if source == 2 else (4 if value else 8)
        return ('tail' if current in (4,8) else 'return'),current,None
    if category == 0:
        return ('call',6 if source == 1 else 7,0) if source in (1,2) else ('return',None,None)
    if category == 1:
        if source == 1 and not value or source == 2 and value:
            return 'return',None,None
    elif category == 2:
        if source in (1,2):
            return 'call',6 if source == 1 else 7,0
    else:
        return 'return',None,None
    return 'call',7 if value else 6,value if value else 1


def execute(c):
    before = c.reg[:]
    sp,saved_s0,resume,value,category = before[2],before[8],before[1],before[10],before[11]
    status,source = c.mem(GP+357,1),c.mem(SOURCE,1)
    snapshots = {base:c.mem(base,size).to_bytes(size,'little') for base,size in ((GLOBAL,16),(LOCAL,8),(CELLS,6))}
    kind,current,live_s0 = action(status,category,value,source)
    expected = [('w',sp-8,4,saved_s0),('w',sp-20,4,category),('w',sp-4,4,resume),
                ('r',SOURCE,1,source),('r',GP+357,1,status),('r',sp-20,4,category)]
    if status in SELECTED:
        expected.append(('w',L,1,0))
        if current:
            expected.append(('w',L,1,current))
        expected.append(('r',L,1,current))
        if current:
            expected.append(('w',R,1,4))
        if kind == 'tail':
            expected.append(('w',ACTIVE,1,1))
    if kind != 'call':
        restores = ((sp-8,saved_s0),(sp-4,resume)) if kind == 'tail' else ((sp-4,resume),(sp-8,saved_s0))
        expected.extend(('r',a,4,v) for a,v in restores)
    c.events,c.trace_active = [],True
    c.writes.clear()
    stop = c.run(ENTRY,{GETTER,SETTER,CALLEE,TAIL,resume})
    check(stop == GETTER and c.reg[1] == 0xcd78 and c.reg[2] == sp-32 and c.reg[8] == value and c.reg[10] == value,
          'consumer getter entry')
    getter_regs,write_count = c.reg[:],len(c.writes)
    check(c.run(GETTER,{0xcd78}) == 0xcd78 and c.reg[10] == source and
          all(c.reg[i] == getter_regs[i] for i in range(32) if i != 10) and len(c.writes) == write_count,
          'consumer actual getter')
    stop = c.run(0xcd78,{SETTER,CALLEE,TAIL,resume})
    if kind == 'tail':
        pre_a0 = 8 if category == 2 and source == 2 and not value else source
        check(stop == SETTER and (c.reg[1],c.reg[2],c.reg[8],c.reg[10],c.reg[11]) ==
              (0xcddc,sp-32,value,pre_a0,category), 'consumer setter entry')
        setter_regs = c.reg[:]
        check(c.run(SETTER,{0xcddc}) == 0xcddc and
              all(c.reg[i] == setter_regs[i] for i in range(32) if i not in (14,15)), 'consumer actual setter')
        stop = c.run(0xcddc,{TAIL,resume})
    c.trace_active = False
    check(stop == (CALLEE if kind == 'call' else TAIL if kind == 'tail' else resume), 'consumer endpoint')
    check(c.events == expected, 'consumer ordered data accesses')
    check(c.writes == [(a,n,v) for op,a,n,v in expected if op == 'w'], 'consumer exact stores')
    if kind == 'call':
        check((c.reg[1],c.reg[2],c.reg[8],c.reg[10],c.reg[11]) ==
              (0xce6e,sp-32,live_s0,current,category), 'consumer first-callee contract')
    else:
        check((c.reg[1],c.reg[2],c.reg[8],c.reg[10],c.reg[11]) ==
              (resume,sp,saved_s0,1 if kind == 'tail' else source,category), 'consumer restored caller/tail')
    check(all(c.reg[i] == before[i] for i in range(32) if i not in (1,2,8,10,14,15)), 'consumer preserved other registers')
    for base,original in snapshots.items():
        model = bytearray(original)
        for op,address,size,byte in expected:
            if op == 'w' and base <= address < base+len(model):
                model[address-base:address-base+size] = byte.to_bytes(size,'little')
        check(c.mem(base,len(model)).to_bytes(len(model),'little') == model, 'consumer global/canary')
    check(not c.calls, 'opaque provider executed')
    return kind


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == APP_HASH, 'APP identity')
    c = Gate(image)
    initialize(c)
    categories = (0,1,2,3,255,0x10000,MASK)
    for status,category,value,source in product(range(256),categories,(0,1,MASK),(0,1,2,3,255)):
        fixture(c,value,category,source)
        c.mem(GP+357,1,status)
        execute(c)
    for category,source,value,status in product(range(256),range(256),(0,1,MASK),(0,1)):
        fixture(c,value,category,source)
        c.mem(GP+357,1,status)
        execute(c)
    for initial_l,category,source,value in product(range(256),(0,1,2),(1,2,3),(0,1)):
        fixture(c,value,category,source,initial_l=initial_l,initial_r=initial_l ^ 255,active=initial_l)
        c.mem(GP+357,1,1)
        execute(c)
    for address,before,after,status,category,value,source,message in (
        (0xcd84,'9307e065','9307f065',0,3,0,0,'consumer ordered data accesses'),
        (0xcdaa,'a3820718','23820718',1,3,0,0,'consumer ordered data accesses'),
        (0x81f2,'034575ce','034585ce',0,3,0,0,'consumer actual getter'),
    ):
        mutant = bytearray(image)
        offset = address-BASE
        check(mutant[offset:offset+len(bytes.fromhex(before))] == bytes.fromhex(before), 'consumer mutation pin')
        mutant[offset:offset+len(bytes.fromhex(after))] = bytes.fromhex(after)
        probe = Gate(mutant)
        initialize(probe)
        fixture(probe,value,category,source)
        probe.mem(GP+357,1,status)
        try:
            execute(probe)
        except RuntimeError as exc:
            check(str(exc) == message, 'unexpected consumer mutation failure: '+str(exc))
        else:
            raise RuntimeError('consumer mutation undetected')
    print('PASS: 26880 state/category/input/getter cases; 393216 full category/getter pairs; '
          '4608 old-cell probes; 3 mutations; original getter/setter; b6f4/fe6a NOT executed')


def composition(image):
    c = Gate(image)
    initialize(c)
    counts = dict.fromkeys(('return','call','tail'),0)
    cases = 0
    for selector,h,j,k,state_source,category,value,source in product(range(8),(0,1),(0,1),(0,1),(0,1,255),(0,1,2,255),(0,1),(0,1,2,255)):
        prepare_state(c,3,b4=16,b5=selector*4,h=h,j=j,k=k,getter=state_source)
        execute_state(c,3,16,selector*4,0)
        status = c.mem(GP+357,1)
        fixture(c,value,category,source)
        check(c.mem(GP+357,1) == status, 'producer status retained')
        counts[execute(c)] += 1
        cases += 1
    print(f'PASS: {cases} original ID2047 producer-to-state-consumer chains; {counts}; shared globals; no SDK required')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--standalone-only',action='store_true')
    args = parser.parse_args()
    image = IMAGE.read_bytes()
    verify(image)
    if not args.standalone_only:
        composition(image)
