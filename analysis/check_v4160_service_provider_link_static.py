"""Conditional APP reader/config-copy/service-slot link; bytes and CFG only.

No target ISA, MMIO, callback, resident, copy, RAM/frame or device execution.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_ram_callback_prefix_static as previous

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-service-provider-link-static.json')
APP_HASHES=('d7b011c49b40ad7e6cf8dc8865c4817187ea3e201bacd24c99872c74b61ed08a',
 '7a866d6e294594b1a618d9cedfffc67a28a08122e72fb22d89bffe5383a2a482')
DETAILS=((0x43f46,0x43f8c,564,480,924,'b1afb0f40c42b491d134c5f765e7ea10b5f98721210829d574b1ac47f24cb802'),
 (0x43fd2,0x44020,644,560,776,'bab2b2c9af5c7902e1fcc24fe84a41d7dd800df09e0961e859f659bb4ead548e'))


def specs(role,pc,params=None):
    s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def lui(o,r,v):e(o,'lui',rd=r,imm=v)
    def addi(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def load(o,r,b,v,w=4):e(o,'load',rd=r,rs1=b,imm=v,width=w)
    def store(o,r,b,v):e(o,'store',rs2=r,rs1=b,imm=v,width=4)
    if role=='APP_call':
        e(0,'auipc',rd=15,imm=0xfffff000);addi(4,15,15,1548);store(8,15,2,0)
        lui(10,15,0x40000);load(14,15,15,116);e(16,'mv',rd=10,rs2=2);e(18,'call_indirect',rd=1,rs1=15)
    elif role=='publication':
        copied,slot,low=params;lui(0,10,0x20003000);e(4,'li',rd=12,imm=16);addi(6,10,10,copied)
        e(10,'auipc',rd=1,imm=0x1ffbc000);e(14,'jalr',rd=1,rs1=1,imm=low)
        lui(18,15,0x20003000);load(22,13,15,copied);lui(26,14,0x20003000);store(30,13,14,slot)
    elif role=='reader':
        lui(0,12,0x40003000);load(4,13,12,-2024,2);load(8,14,12,-2024,2)
        e(12,'slli',rd=14,rs1=14,imm=16);e(14,'srli',rd=14,rs1=14,imm=16);e(16,'bne',rs1=14,rs2=13,target=pc+4)
        lui(20,12,0x40003000);load(24,13,12,-2020,2);load(28,15,12,-2020,2)
        e(32,'slli',rd=15,rs1=15,imm=16);e(34,'srli',rd=15,rs1=15,imm=16);e(36,'bne',rs1=15,rs2=13,target=pc+24)
        lui(40,11,0x40003000);load(44,12,11,-2024,2);load(48,10,11,-2024,2)
        e(52,'slli',rd=10,rs1=10,imm=16);e(54,'srli',rd=10,rs1=10,imm=16);e(56,'bne',rs1=10,rs2=12,target=pc+44)
        e(60,'beq',rs1=14,rs2=10,target=pc+84);lui(64,13,0x40003000)
        load(68,14,13,-2020,2);load(72,15,13,-2020,2);e(76,'slli',rd=15,rs1=15,imm=16)
        e(78,'srli',rd=15,rs1=15,imm=16);e(80,'bne',rs1=15,rs2=14,target=pc+68)
        e(84,'slli',rd=10,rs1=10,imm=16);e(86,'or',rd=10,rs1=10,rs2=15);e(88,'jr',rs1=1)
    else:raise RuntimeError('unknown service link role')
    return s


def body(raw,role,pc,digest,params=None):
    if role=='reader':
        check(all(int.from_bytes(raw[o:o+4],'little')&0x707f==0x5003 for o in (4,8,24,28,44,48,68,72)),
            'service reader unsigned halfword encodings')
    n=decode(raw,pc);s=specs(role,pc,params);check(set(n)==set(s),'service link whole boundaries '+role)
    for p,f in s.items():init.g(n,p,'service link '+role+' operand '+hex(p-pc),**f)
    size,count={'APP_call':(20,7),'reader':(90,28),'publication':(34,9)}[role]
    check((len(raw),len(n),sha256(raw).hexdigest())==(size,count,digest),'service link whole identity '+role)
    edges={};calls=[];cuts=[]
    for p,d in n.items():
        if d['op']=='jr':qs=[]
        elif d['op'] in ('bne','beq'):qs=[p+d['size'],d['target']]
        else:qs=[p+d['size']]
        for q in qs:
            if q not in n:check(role!='reader' and q==pc+size,'service link explicit prefix cut');cuts.append(hex(q))
        edges[p]=qs
        if d['op'] in ('call_indirect','jalr'):calls.append({'pc':hex(p),'link':hex(p+d['size']),
            'target':'fresh U32[40074] & ~1' if role=='APP_call' else hex((pc+10+0x1ffbc000+params[2])&0xfffffffe),
            'normal_return_and_preservation_proved':False})
    seen=set()
    def visit(p):
        if p not in n or p in seen:return
        seen.add(p)
        for q in edges[p]:visit(q)
    visit(pc);check(seen==set(n),'service link local reachability '+role)
    return {'start':hex(pc),'end_exclusive':hex(pc+size),'bytes':size,'sha256':digest,'instructions':list(n.values()),
        'conditional_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},'calls':calls,'cuts':cuts,
        'complete_function':role=='reader'}


def derive(app,carriers,header,coverage):
    parent=previous.derive(app,carriers,header,coverage)
    caller=body(app[0x19bba-0x8000:0x19bce-0x8000],'APP_call',0x19bba,APP_HASHES[0])
    reader=body(app[0x191c6-0x8000:0x19220-0x8000],'reader',0x191c6,APP_HASHES[1])
    check((0x19bba+0xfffff000+1548)&0xffffffff==0x191c6,'APP stack config first word forms reader pointer')
    rn={x['pc']:x for x in reader['instructions']}
    check(not reader['calls'] and not any(x['op']=='store' for x in rn.values()),'reader no local calls/stores')
    loops=[(p,d['target']) for p,d in rn.items() if d['op']=='bne']
    check(loops==[(0x191d6,0x191ca),(0x191ea,0x191de),(0x191fe,0x191f2),(0x19216,0x1920a)],'four exact retry edges')
    profiles=[]
    for i,(data,d) in enumerate(zip(carriers,DETAILS)):
        entry,pc,copied,slot,low,h=d;p=parent['profiles'][i]
        word=int.from_bytes(init.binding.take(data,0x40074,4),'little');check(word==entry,'candidate40074 config entry word')
        b=body(init.binding.take(data,pc,34),'publication',pc,h,(copied,slot,low))
        check(b['calls'][0]['target']=='0x20000332','candidate copy helper target')
        check(hex(0x20003000+slot)==p['nominal_service_pointer_word'],'publication joins nominal callback service word')
        profiles.append({'label':p['label'],'candidate_40074_word':hex(word),'publication':b,
            'copied_config_first_word':hex(0x20003000+copied),'nominal_service_pointer_word':hex(0x20003000+slot),
            'first_copy_mapping_shift':p['mapping_shift'],'copy_helper_target':'0x20000332',
            'fragment_reached_copy_completed_first_word_preserved_and_installed_identity_proved':False})
    return {'schema':'TSL9-service-provider-link-static-v1','profile':parent['profile'],'APP_call':caller,'APP_reader':reader,'profiles':profiles,
        'scope':'APP bounded call prefix20B/7instructions +complete APP reader90B/28instructions +2 bounded candidate publications68B/18instructions',
        'conditional_link':['APP caller forms191c6, SW to[SP+0], passes A0=SP to fresh[40074] target without local null guard',
            'candidate40074 points to config function entry; its earlier gates/optional callback and full CFG not covered here',
            'publication fragment requests helper20000332 with A0=copied_config,A1=then-live config pointer,A2=16',
            'after normal helper return, fresh LW copied_config[0] -> SW service_slot; source need not equal original APP stack word',
            'only if identity/mapping/gates/argument retention/copy-word semantics and preservation all hold can callback service slot equal191c6'],
        'reader_contract':{'nominal_high_halfword_operand':'0x40002818','nominal_low_halfword_operand':'0x4000281c',
            'pairs':'fresh H1 reads until equal; fresh L1 reads until equal; fresh H2 reads until equal; H1==H2 skips L2 retry pair, otherwise fresh L2 reads until equal',
            'ordinary_return_A0':'(H2<<16)|L1 if H1==H2; else(H2<<16)|L2',
            'final_high_recheck_after_L2':False,'retry_bound_or_termination_proved':False,
            'monotonic_coherent_atomic_counter_or_MMIO_semantics_proved':False,'local_stack_allocation_calls_or_stores':False},
        'retry_backedges':[{'branch':hex(p),'target':hex(q)} for p,q in loops],
        'premises':['actual installed resident equals candidate and required mappings/code/data/register/frame accesses valid',
            'bounded config fragment may never be reached; upstream callback/gates and source A1 not proved by the fragment',
            'helper target identity alone is not proof of copy behavior, return, allocation or pointer retention; fresh copied word may differ',
            'APP stack first word/source config and published service word may be modified; callback unknown-callee preservation conditions still apply',
            'reader halfword operands identify access addresses only; hardware values, side effects, stability and progress not observed'],
        'remaining':['complete config gates and copy-provider semantics','three callback continuations and larger update loop',
            'actual source registration/order/writers and field bounds','installed provider identity, MMIO behavior and object/frame lifetime'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(app,carriers):
    for high in range(65536):
        for low in (0,65535):
            packed=(high<<16)|low
            check(packed>>16==high and packed&65535==low and 0<=packed<=0xffffffff,'reader return bit packing')
    changes={'APP_call':((0,1<<12),(4,1<<20),(8,4),(14,4),(16,4),(18,0x80)),
        'reader':((4,1<<14),(16,1<<12),(36,1<<12),(56,1<<12),(60,1<<12),(80,1<<12),(84,4),(86,4))}
    count=0
    cases=[(app[0x19bba-0x8000:0x19bce-0x8000],'APP_call',0x19bba,APP_HASHES[0],None),
        (app[0x191c6-0x8000:0x19220-0x8000],'reader',0x191c6,APP_HASHES[1],None)]
    for data,d in zip(carriers,DETAILS):
        entry,pc,copied,slot,low,h=d;cases.append((init.binding.take(data,pc,34),'publication',pc,h,(copied,slot,low)))
    for raw,role,pc,h,args in cases:
        cs=changes.get(role,((4,4),(6,1<<20),(10,1<<12),(14,1<<20),(22,1<<20),(30,1<<20)))
        for off,flip in cs:
            b=bytearray(raw);n=decode(raw,pc)[pc+off]['size'];b[off:off+n]=(int.from_bytes(b[off:off+n],'little')^flip).to_bytes(n,'little')
            try:body(b,role,pc,h,args)
            except RuntimeError as e:check(str(e) in ('service link '+role+' operand '+hex(off),'service reader unsigned halfword encodings'),'specific service mutation guard '+str(e))
            else:raise RuntimeError('service link mutation escaped')
            count+=1
    check(count==26,'service link mutation census')
    print('PASS: 131072 host bit-packing cases; four exact retry edges; 26 specified operand mutations rejected')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');o=parser.parse_args()
    app=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(app)==76800 and sha256(app).hexdigest()==init.binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK header identity')
    carriers=[]
    for label,folder,tail,size,digest in init.binding.PROFILES:
        raw=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(raw)==size and sha256(raw).hexdigest()==digest,'candidate identity '+label);carriers.append(raw)
    raw_hex=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
    coverage=sparse.derive(app,carriers,header,raw_hex,sparse.parser())
    ledger=derive(app,carriers,header,coverage);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract()
    tests(app,carriers);output=(json.dumps(ledger,indent=1,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'service provider link exact ledger replay')
    print('PASS: 178B/53instructions; APP stack pointer source, candidate copy/publication and full reader body joined conditionally')
    print('PASS: exact ledger; NO target execution; installed binding/copy preservation/MMIO semantics/termination UNPROVED')


if __name__=='__main__':main()
