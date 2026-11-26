"""Specific RX ->queue ->consumer ->ID1657 cache ingress, static contracts.

Complete original bodies/operands/CFGs and host predicates/intervals only.
No target ISA, CSR, copy/RAM/stack state, provider or MMIO execution/emulation.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_cached_record_origin_static as previous

init,sparse,check,take,decode=previous.init,previous.sparse,previous.check,previous.take,previous.decode
OUT=Path(__file__).with_name('v4160-rx-cache-ingress-static.json')
DETAILS=(('consumer',0x12c58,314,107,14,'89905d7666bbe8295d09c752f1fcd34246847ea86c6428b539406450f8980c0f'),
 ('filter',0x82d2,188,69,13,'7a49eb89a2c698b0a9d4a97083329c2a12e200c1f27fbdadec16784a6edb0e30'),
 ('producer',0x12bc8,92,32,6,'d3d9af9bcec8af13dfd424d3bfb2bd79f8fc3fd61308cb6ec0d7c18b1b78b13b'),
 ('rx',0x16a7c,142,52,8,'d823c819bbe92c3b7ee17c92411825549084d08dc32c36378d8e60d4915f40e2'))


def specs(role,pc):
    s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def load(o,r,b,v=0,w=4):e(o,'load',rd=r,rs1=b,imm=v,width=w)
    def store(o,r,b,v=0,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    def addi(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    def lui(o,r,v):e(o,'lui',rd=r,imm=v)
    def mv(o,r,a):e(o,'mv',rd=r,rs2=a)
    def binary(o,op,r,a,b):e(o,op,rd=r,rs1=a,rs2=b)
    def imm(o,op,r,a,v):e(o,op,rd=r,rs1=a,imm=v)
    def branch(o,op,a,b,t):e(o,op,rs1=a,rs2=b,target=pc+t)
    def bz(o,op,r,t):e(o,op,rs1=r,target=pc+t)
    def jump(o,t):e(o,'jump',target=pc+t)
    def call(o,t):e(o,'jal',rd=1,target=t)
    def indirect(o):e(o,'call_indirect',rd=1,rs1=15)
    if role=='consumer':
        addi(0,2,2,-80)
        for off,r,slot in ((2,9,68),(4,18,64),(6,19,60),(8,20,56),(10,21,52),(12,22,48),(14,23,44),(16,1,76),(18,8,72)):store(off,r,2,slot)
        li(20,9,0);e(22,'auipc',rd=21,imm=0x1fff9000);addi(26,21,21,970);li(30,22,12)
        addi(32,18,0,136);lui(36,19,0x40000);li(40,20,1);addi(42,23,3,84)
        binary(46,'mul',8,9,22);binary(50,'add',8,8,21);load(52,15,8,0,2)
        imm(56,'slli',15,15,16);imm(58,'srli',15,15,16);bz(60,'beqz',15,150)
        e(62,'csr',rd=0,rs1=18,funct3=3,csr=0x800);load(66,15,19,76);li(70,12,12);mv(72,11,8)
        addi(74,10,2,8);indirect(76);store(78,0,8,0,2);e(82,'csr',rd=0,rs1=18,funct3=2,csr=0x800)
        addi(86,10,2,8);call(88,0x82d2);bz(92,'bnez',10,150);load(94,15,2,8,2);branch(98,'bne',15,20,288)
        load(102,14,2,10,1);li(106,15,4);branch(108,'bne',14,15,150)
        load(112,14,2,11,1);addi(116,15,0,181);branch(120,'bne',14,15,150)
        load(124,14,2,12,1);addi(128,15,0,98);branch(132,'bne',14,15,150)
        load(136,15,2,13,1);bz(140,'beqz',15,182);addi(142,14,0,90);branch(146,'beq',15,14,244)
        addi(150,9,9,1);addi(152,15,0,32);branch(156,'bne',9,15,46)
        for off,r,slot in ((160,1,76),(162,8,72),(164,9,68),(166,18,64),(168,19,60),(170,20,56),(172,21,52),(174,22,48),(176,23,44)):load(off,r,2,slot)
        addi(178,2,2,80);e(180,'jr',rs1=1)
        call(182,0x820c);load(186,10,2,14,1);call(190,0x9454);li(194,10,0);call(196,0x9b36)
        load(200,10,2,19,1);li(204,12,2);addi(206,11,2,20);store(208,0,2,20,2);call(212,0x12abe)
        load(216,14,2,19,1);store(220,20,2,20,2);li(224,15,2);li(226,10,1);branch(228,'beq',14,15,234)
        li(232,10,2);li(234,12,2);addi(236,11,2,20);call(238,0x12abe);jump(242,150)
        load(244,14,2,14,1);addi(248,15,0,85);branch(252,'bne',14,15,150)
        load(256,15,19,76);addi(260,10,2,20);li(262,12,12);addi(264,11,2,8);indirect(266)
        addi(268,15,0,86);addi(272,10,2,20);store(274,15,2,26,1);store(278,0,2,31,1);call(282,0x12a08);jump(286,150)
        load(288,15,23);load(292,15,15,4,1);imm(296,'andi',15,15,8);bz(298,'bnez',15,150)
        call(300,0x81aa);bz(304,'beqz',10,150);addi(306,10,2,8);call(308,0x14d2e);jump(312,150)
    elif role=='filter':
        addi(0,2,2,-64);store(2,19,2,44);lui(4,19,0x10000)
        for off,r,slot in ((6,9,52),(8,18,48),(10,20,40),(12,21,36),(14,22,32),(16,23,28),(18,24,24),(20,25,20),(22,1,60),(24,8,56)):store(off,r,2,slot)
        mv(26,9,10);li(28,18,0);li(30,20,0);e(32,'auipc',rd=21,imm=0x20004000);addi(36,21,21,1186)
        addi(40,19,19,-2);li(42,22,2);li(44,23,8);addi(46,24,10,3);lui(50,25,0x40000)
        imm(54,'slli',8,18,2);binary(58,'add',8,8,21);load(60,15,8,2,2);branch(64,'beq',19,15,152)
        load(68,15,8,5,1);branch(72,'bne',22,15,152);load(76,15,8,4,1);imm(80,'andi',15,15,255);bz(84,'beqz',15,152)
        load(86,12,9,2,1);mv(90,20,15);branch(92,'bltu',23,12,152)
        load(96,13,9,0,2);load(100,15,9,11,1);mv(104,11,24);store(106,13,2,5,1)
        imm(110,'slli',14,15,4);imm(114,'srli',15,13,8);binary(118,'or',15,15,14);store(120,15,2,4,1)
        load(124,15,25,76);addi(128,10,2,6);indirect(132)
        load(134,13,9,2,1);load(138,10,8,2,2);addi(142,12,2,4);addi(144,13,13,2);addi(146,11,0,192);call(150,0x8a56)
        branch(152,'beq',18,0,184);load(156,1,2,60);load(158,8,2,56);mv(160,10,20)
        for off,r,slot in ((162,9,52),(164,18,48),(166,19,44),(168,20,40),(170,21,36),(172,22,32),(174,23,28),(176,24,24),(178,25,20)):load(off,r,2,slot)
        addi(180,2,2,64);e(182,'jr',rs1=1);li(184,18,1);jump(186,54)
    elif role=='producer':
        addi(0,2,2,-16);store(2,1,2,12);store(4,8,2,8);store(6,9,2,4);li(8,15,0)
        e(10,'auipc',rd=17,imm=0x1fff9000);addi(14,17,17,1126);li(18,28,12);addi(20,6,0,32)
        binary(24,'mul',14,15,28);binary(28,'add',8,17,14);load(32,16,8,0,2);imm(36,'slli',16,16,16);imm(38,'srli',16,16,16)
        branch(42,'bne',16,0,84);store(46,10,8,0,2);store(50,12,8,2,1);lui(54,15,0x40000);load(58,15,15,76)
        addi(60,14,14,3);mv(62,9,13);binary(64,'add',10,17,14);indirect(68);store(70,9,8,11,1)
        load(74,1,2,12);load(76,8,2,8);load(78,9,2,4);addi(80,2,2,16);e(82,'jr',rs1=1)
        addi(84,15,15,1);branch(86,'bne',15,6,24);jump(90,74)
    elif role=='rx':
        addi(0,2,2,-48);store(2,9,2,36);lui(4,15,0x40011000);store(8,1,2,44);store(10,8,2,40);store(12,18,2,32)
        li(14,14,1);mv(16,9,10);addi(18,15,15,-2048);branch(22,'bne',10,14,28);li(26,14,16);store(28,14,15,20)
        li(30,10,3);store(32,11,2,12);call(34,0x16896);load(38,11,2,12);li(40,8,0);li(42,18,13);mv(44,10,11);call(46,0x16896)
        li(50,10,0);call(52,0x16896);addi(56,15,2,16);binary(58,'add',15,15,8);store(60,10,15,0,1);addi(64,8,8,1);branch(66,'bne',8,18,50)
        lui(70,15,0x40011000);li(74,14,17);store(76,14,15,-2032)
        load(80,15,2,17,1);imm(84,'andi',14,15,24);bz(88,'bnez',14,130);load(90,12,2,20,1);li(94,13,7)
        imm(96,'andi',12,12,15);addi(98,14,12,-1);imm(102,'andi',14,14,255);branch(106,'bltu',13,14,130)
        load(110,10,2,16,1);imm(114,'srli',15,15,5);mv(116,13,9);imm(118,'slli',10,10,3);addi(120,11,2,21);binary(124,'or',10,10,15);call(126,0x12bc8)
        load(130,1,2,44);load(132,8,2,40);load(134,9,2,36);load(136,18,2,32);addi(138,2,2,48);e(140,'jr',rs1=1)
    else:raise RuntimeError('unknown ingress role')
    return s


def body(raw,role,pc,size,count,store_count,digest):
    n=decode(raw,pc);expected=specs(role,pc);check(set(n)==set(expected),'ingress complete boundaries '+role)
    for p,f in expected.items():init.g(n,p,'ingress '+role+' instruction '+hex(p-pc),**f)
    edges={};calls=[]
    for p,d in n.items():
        if d['op']=='jr':check(d['rs1']==1,'ingress return register');qs=[]
        elif d['op']=='jump':qs=[d['target']]
        elif d['op'] in ('beq','bne','beqz','bnez','bltu'):qs=[p+d['size'],d['target']]
        else:qs=[p+d['size']]
        check(all(q in n for q in qs),'ingress complete local CFG '+role);edges[p]=qs
        if d['op']=='call_indirect' or d['op']=='jal':
            check(d['rd']==1,'ingress linked callees');calls.append({'pc':hex(p),'target':hex(d['target']) if 'target' in d else 'fresh A5 & ~1','link':hex(p+d['size']),'normal_return_proved':False})
    seen=set();active=set();back=[]
    def visit(p):
        if p in seen:return
        seen.add(p);active.add(p)
        for q in edges[p]:
            if q in active:back.append((p-pc,q-pc))
            else:visit(q)
        active.remove(p)
    visit(pc);wanted={'consumer':[(156,46)],'filter':[(186,54)],'producer':[(86,24)],'rx':[(66,50)]}[role]
    check(seen==set(n) and back==wanted,'ingress full reachability and exact cycle '+role)
    # Graph dominators retain calls as conditional normal-return edges only.
    dom={p:({p} if p==pc else set(n)) for p in n};pred={p:set() for p in n}
    for p,qs in edges.items():
        for q in qs:pred[q].add(p)
    changed=True
    while changed:
        changed=False
        for p in n:
            if p==pc:continue
            ds={p}|set.intersection(*(dom[q] for q in pred[p]))
            if ds!=dom[p]:dom[p]=ds;changed=True
    if role=='filter':
        check(all(pc+90 in dom[pc+q] for q in (132,150)),'filter nonzero flag assignment dominates optional calls')
        check([p-pc for p,d in n.items() if d.get('rd')==20]==[30,90,168],'filter only flag init/assignment/after-result restore')
    stores=[d for d in n.values() if d['op']=='store']
    check((len(raw),len(n),len(stores),sha256(raw).hexdigest())==(size,count,store_count,digest),'ingress full identity '+role)
    return {'start':hex(pc),'end_exclusive':hex(pc+size),'bytes':size,'sha256':digest,'instructions':list(n.values()),'stores':stores,
        'calls':calls,'backedges_relative':back,'conditional_normal_return_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},
        'optional_filter_calls_dominated_by_flag_assignment':role=='filter'}


def derive(app,carriers,header,coverage):
    parent=previous.derive(app,carriers,header,coverage)
    bodies={r:body(take(app,p,size),r,p,size,n,stores,h) for r,p,size,n,stores,h in DETAILS}
    check(sum(b['bytes'] for b in bodies.values())==736 and sum(len(b['instructions']) for b in bodies.values())==260
          and sum(len(b['stores']) for b in bodies.values())==41,'ingress full body census')
    n={r:{d['pc']:d for d in b['instructions']} for r,b in bodies.items()}
    qb=(0x12bd2+n['producer'][0x12bd2]['imm']+n['producer'][0x12bd6]['imm'])&0xffffffff
    cb=(0x12c6e+n['consumer'][0x12c6e]['imm']+n['consumer'][0x12c72]['imm'])&0xffffffff
    check(qb==cb==0x2000c038 and qb+32*12==0x2000c1b8,'producer/consumer same bounded queue before cache table')
    check(n['rx'][0x16afa]['target']==0x12bc8 and n['consumer'][0x12d8c]['target']==0x14d2e,'RX queue and consumer mode joins')
    check(parent['mode1_join']['selected_ID']==1657 and parent['cache_layout']['object']=='0x2000c290','existing selected cache writer join')
    filterbase=(0x82f2+n['filter'][0x82f2]['imm']+n['filter'][0x82f6]['imm'])&0xffffffff
    check(filterbase==0x2000c794,'two overlapping-stride filter descriptor bases')
    check(n['producer'][0x12bfa]['rs2']==12 and n['producer'][0x12c0e]['imm']==11 and n['producer'][0x12c0e]['rs2']==9,'producer byte length then post-copy tag')
    return {'schema':'TSL9-RX-cache-ingress-static-v1','profile':init.timer.PROFILE,'scope':'4 complete APP bodies736B/260instructions/41stores',
        'bodies':bodies,'queue':{'base':hex(qb),'end_exclusive':hex(qb+384),'rows':32,'row_bytes':12},
        'rx_contract':{'capture':'48-byte frame; 16896(3),16896(saved entry A1),13 times16896(0); low bytes stored atSP+16..28',
            'guards':'b1=U8[SP+17], b1&18hex must0; L=U8[SP+20]&15, 1<=L<=8',
            'queue_call':'12bc8(ID=(U8[SP+16]<<3)|(b1>>5),source=SP+21,length=L,tag=saved full entry A0)',
            'ID_domain':[0,2047],'ID1657_header_examples':['cf20','cf21','cf22','cf23','cf24','cf25','cf26','cf27'],
            'payload_source_limit':'SP+21..28 maximum, inside captured13 bytes; entry tag not locally restricted to1/2',
            'physical_receive_success_or_actual_bytes_proved':False},
        'producer_contract':{'selection':'first fresh U16[row]==0 among0..31; full queue no copy or queue stores',
            'order':['SH low16(entryID) row+0','SB low8(entrylength) row+2','fresh4004c(row+3,entrysource,full entrylength)',
                     'after normal return SB low8(savedtag S1) at then-live S0+11'],
            'general_input_ID_or_length_guard':False,'atomic_publication_or_interrupt_safety_proved':False,
            'short_payload_tail':'RX length1..8 copies prefix row+3..10; remaining payload bytes not filled by that copy',
            'zero_ID':'under specific RX length1..8/reference-copy/disjoint-context premises, ID0 stays an empty marker despite payload/tag stores; unknown provider effects excluded only conditionally'},
        'consumer_contract':{'scan':'80-byte frame; fresh nonzero queueID ->requestcopy12(SP+8,row,12), then clear onlyrowID, thenfilter82d2(SP+8)',
            'CSR':'encoded CSR800 clear then set using S2=88hex, not a claim of physical synchronization or old-state restoration',
            'snapshot':'SP+8 ID,SP+10 length,SP+11..18 payload,SP+19 tag; whole12-byte snapshot request independent of length',
            'ID1657_route':'filter scalar0; fresh snapshotID!=1; config+4 bit3 clear; real81aa reads freshGP+167 nonzero ->14d2e(SP+8)',
            'ID1_only':'length4/signatureb562/opcode tests and responsecopy patch/tag0 are not gates onID1657',
            'further_ID_sample':'mode1 tree reads snapshotID again; must still be1657 to reach row18 case'},
        'filter_contract':{'descriptor_base':hex(filterbase),'two_indices':[0,1],'stride':4,
            'candidate':'fresh U16[base+4*i+2]!=fffe, freshU8[base+4*i+5]==2, freshU8[base+4*i+4]!=0',
            'order':'read length, setS4=nonzero candidateflag, THEN iflength>8 skip optional calls; S4 never reset between candidates',
            'optional':'length<=8 ->copy at8356, then8a56 at8368; fresh length reread for latter plus2',
            'return':'A0=S4 before restoring oldS4; under required callee S4/context preservation, zero return implies no qualifying candidate and no optional call',
            'inactive_candidates':'zero return possible for any snapshotlength, since length may never be read',
            'generic_zero_filter_is_length_guard':False,'unknown_optional_provider_effects_excluded_unconditionally':False},
        'conditional_specific_RX_cache_bridge':{'premises':['RX/header guards accepted and queue has empty slot',
            'actual copy matches reference; accesses and needed registers/frames preserved; no adverse aliases/other writers/IRQ changes',
            'consumer snapshots same item; filter returns0 with required context preservation; config/probe gates pass; mode1 and resampledID1657'],
            'cached_fields':'length1..8 and tag=low8(RXentryA0); tag1/2 only if entry value established1/2 separately',
            'pointer_flow':'RXframe+21 ->queue payload; queue12 ->consumerSP+8 P; P12 ->cachedO; immediate C6a8(P), later C776->C6a8(O)',
            'all_ingress_paths_bounded_by8':False,'actual_reception_or_provider_binding_proved':False},
        'other_ingress_boundary':'known12c24->18d78->12bc8 is a separate unexpanded source here; do not transfer RX1..8/tag constraints to it',
        'remaining_boundaries':['12c24/18d78 other ingress field/length construction','actual copy provider identity/preservation/retention',
            'other writers and item publication/snapshot lifetime','physical MMIO/CSR and interrupt semantics'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(app):
    accepted=0;ids=[0]*2048;witness=[]
    for b0 in range(256):
        for b1 in range(256):
            if b1&24:continue
            ident=(b0<<3)|(b1>>5);ids[ident]+=1;accepted+=1
            if ident==1657:witness.append(bytes((b0,b1)).hex())
    check(accepted==16384 and set(ids)=={8} and witness==['cf'+format(x,'02x') for x in range(32,40)],'all RX ID header encodings')
    flags_lengths=0
    for flags in range(256):
        for lengthbyte in range(256):
            length=lengthbyte&15
            accept=not flags&24 and ((length-1)&255)<=7
            check(accept==(flags&24==0 and 1<=length<=8),'RX guard partition')
            flags_lengths+=accept
    check(flags_lengths==8192,'RX accepted flag/length pairs')
    for length in range(256):
        for pattern in range(4):
            eligible=[bool(pattern&1),bool(pattern&2)]
            flag=9 if eligible[1] else 7 if eligible[0] else 0
            optional_calls=sum(eligible)*2 if length<=8 else 0
            check(bool(flag)==any(eligible),'filter flag independent of length bound')
            if length>8:check(optional_calls==0,'long filter input can skip calls yet remain nonzero')
            if not any(eligible):check(flag==optional_calls==0,'inactive rules permit zero for any length')
    for index in range(32):
        for length in range(1,9):
            start=0x2000c038+12*index
            check(start+3+length<=start+11 and start+12<=0x2000c1b8,'RX payload fits row before tag')
            check(21+length<=29,'RX payload within13 captured bytes')
    roles={r:(p,size,count,stores,h) for r,p,size,count,stores,h in DETAILS}
    cases=(('consumer',70,4),('consumer',78,1<<20),('consumer',82,1<<12),('consumer',98,0x1000),
        ('consumer',292,1<<20),('consumer',306,4),('filter',90,0x80),('filter',92,0x1000),
        ('filter',160,0x80),('filter',184,4),('producer',50,1<<20),('producer',70,1<<20),
        ('producer',20,1<<20),('rx',84,1<<20),('rx',96,4),('rx',106,0x1000),('rx',116,0x80),('rx',126,1<<21))
    for role,off,flip in cases:
        pc,size,count,stores,digest=roles[role];raw=bytearray(take(app,pc,size));w=decode(raw,pc)[pc+off]['size']
        raw[off:off+w]=(int.from_bytes(raw[off:off+w],'little')^flip).to_bytes(w,'little')
        try:body(raw,role,pc,size,count,stores,digest)
        except RuntimeError as e:check(str(e)=='ingress '+role+' instruction '+hex(off),'unexpected ingress mutation guard '+str(e))
        else:raise RuntimeError('ingress mutation escaped')
    print('PASS: 65536 headers (16384 accepted/8 perID); 65536 flag-length pairs (8192 accepted); 1024 filter predicates; 256 row/source spans; 18 specified raw mutations')


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true',help='Create ledger exclusively');o=p.parse_args()
    app=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(app)==76800 and sha256(app).hexdigest()==init.binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK header identity')
    carriers=[]
    for label,folder,tail,size,digest in init.binding.PROFILES:
        raw=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(raw)==size and sha256(raw).hexdigest()==digest,'candidate identity '+label);carriers.append(raw)
    raw_hex=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
    coverage=sparse.derive(app,carriers,header,raw_hex,sparse.parser())
    sources,vectors=init.timer.source_contract();ledger=derive(app,carriers,header,coverage)
    ledger['sources'],ledger['official_Xwchc_vectors']=sources,vectors
    tests(app);output=(json.dumps(ledger,indent=1,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'RX cache ingress exact ledger replay')
    print('PASS: 4 complete APP bodies736B/260instructions/41stores; RX->queue->consumer->selected ID1657 cache joins')
    print('PASS: exact ledger bytes; NO target execution; other ingress, actual provider, snapshot lifetime and physical CSR/MMIO UNPROVED')


if __name__=='__main__':main()
