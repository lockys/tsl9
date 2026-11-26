"""Complete record producer and conditional relation to literal0 consumer.

Static bytes/operands/CFG and host width/interval algebra only. No target
ISA, allocator, list, arena, callback, provider or MMIO execution/model.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_builtin_record_handlers_static as previous

init,post,ROOT,MASK=previous.init,previous.post,previous.ROOT,previous.MASK
check=init.check
OUT=Path(__file__).with_name('v4160-record-producer-static.json')
DETAILS=((0x43414,'29d76ad5a42d8e18963f91612f71693c26830228176b6efa20d7e017173262fd'),
         (0x434a0,'ead8c94e325f34c8ebbe837ba926b2d170ca2e4433d79e34c73a8ff42011aeed'))
SAVED=((2,9,36,50),(8,1,44,46),(10,8,40,48),(12,18,32,52),(14,19,28,54),
       (16,20,24,56),(18,21,20,58),(20,22,16,60),(22,23,12,62),(24,24,8,64))


def specs(pc,M,Pslot):
    rows=[];G=0x20003000
    def e(o,op,**f):rows.append((o,dict(op=op,**f)))
    def load(o,rd,base,off):e(o,'load',rd=rd,rs1=base,imm=off,width=4)
    def store(o,src,base,off,width=4,**extra):e(o,'store',rs2=src,rs1=base,imm=off,width=width,**extra)
    e(0,'addi',rd=2,rs1=2,imm=-48);e(4,'lui',rd=15,imm=0x40024000)
    for save,reg,off,restore in SAVED:store(save,reg,2,off);load(restore,reg,2,off)
    load(26,9,15,524);store(30,0,15,524);e(34,'fence.i');e(38,'bnez',rs1=10,target=pc+70)
    store(40,9,15,524);e(44,'li',rd=10,imm=2);e(66,'addi',rd=2,rs1=2,imm=48);e(68,'jr',rs1=1)
    e(70,'lui',rd=15,imm=G);load(74,15,15,M+68-G)
    for off,rd,src in ((78,21,14),(80,20,13),(82,23,12),(84,22,11),(86,19,10)):e(off,'mv',rd=rd,rs2=src)
    e(88,'call_indirect',rd=1,rs1=15);e(90,'lui',rd=15,imm=G);load(94,14,15,Pslot-G)
    e(98,'mv',rd=18,rs2=15);e(100,'li',rd=8,imm=0);e(102,'li',rd=13,imm=12);e(104,'li',rd=15,imm=16)
    e(106,'mul',rd=24,rs1=8,rs2=13);e(110,'add',rd=12,rs1=14,rs2=24);load(114,12,12,0)
    e(116,'bnez',rs1=12,target=pc+250);e(118,'lui',rd=11,imm=0x10000)
    e(120,'addi',rd=11,rs1=11,imm=-256);e(124,'li',rd=10,imm=16)
    # +126/+130 is an independently resolved AUIPC/JALR core call pair.
    e(134,'bnez',rs1=10,target=pc+164);e(136,'lui',rd=15,imm=G);load(140,15,15,M+132-G)
    e(144,'beqz',rs1=15,target=pc+152);e(146,'li',rd=11,imm=0);e(148,'li',rd=10,imm=4)
    e(150,'call_indirect',rd=1,rs1=15);e(152,'lui',rd=15,imm=0x40024000)
    store(156,9,15,524);e(160,'li',rd=10,imm=11);e(162,'jump',target=pc+46)
    e(164,'lui',rd=15,imm=G);load(168,14,15,M+76-G);e(172,'bnez',rs1=14,target=pc+242)
    store(174,10,15,M+76-G);store(178,0,10,0,1);load(182,15,18,Pslot-G)
    e(186,'li',rd=14,imm=1);e(188,'sll',rd=14,rs1=14,rs2=8)
    store(192,0,10,12);store(196,23,10,8);store(200,14,10,2,2,mnemonic='qk.c.sh');store(202,21,10,4)
    e(206,'add',rd=15,rs1=15,rs2=24);store(208,19,15,0);store(212,22,15,4);store(216,21,15,8)
    e(220,'beq',rs1=20,rs2=0,target=pc+228);store(224,8,20,0,1)
    e(228,'lui',rd=15,imm=0x40024000);store(232,9,15,524);e(236,'li',rd=10,imm=0);e(238,'jump',target=pc+46)
    e(240,'mv',rd=14,rs2=15);load(242,15,14,12);e(244,'bnez',rs1=15,target=pc+240)
    store(246,10,14,12);e(248,'jump',target=pc+178)
    e(250,'addi',rd=8,rs1=8,imm=1);e(252,'bne',rs1=8,rs2=15,target=pc+106)
    e(256,'lui',rd=15,imm=0x40024000);store(260,9,15,524);e(264,'li',rd=10,imm=8);e(266,'jump',target=pc+46)
    return {pc+o:f for o,f in rows}


def body(raw,pc,M,Pslot,digest):
    n=previous.decode(raw,pc);expected=specs(pc,M,Pslot)
    check(set(n)==set(expected)|{pc+126,pc+130},'producer complete instruction boundaries')
    for p,f in expected.items():init.g(n,p,'producer instruction '+hex(p-pc),**f)
    init.pair(n,pc+126,1,0x20000040,'producer allocation target pair')
    edges,cycles=init.timer.cfg(n,pc);ei={int(p,16):[int(q,16) for q in qs] for p,qs in edges.items()}
    check(cycles==[[hex(pc+o) for o in (240,242,244)],[hex(pc+o) for o in (106,110,114,116,250,252)]],
          'producer complete SCC census')
    restore={pc+o for o in (40,156,232,260)}
    check(pc+68 not in post.reachable(ei,pc,restore),'producer control restore cut set before RET')
    check(not any(d.get('rd')==10 for p,d in n.items() if pc+46<=p<=pc+68),'producer epilogue preserves status A0')
    writes=sorted({d['rd'] for d in n.values() if d.get('rd',0)})
    check(writes==[1,2,8,9,10,11,12,13,14,15,18,19,20,21,22,23,24],'producer GPR writes')
    stores=[p for p,d in n.items() if d['op']=='store']
    check(len(stores)==26 and sum(d['op']=='store' and d['rs1']==2 for d in n.values())==10,'producer complete store counts')
    check(len(n)==97 and len(raw)==268 and sha256(raw).hexdigest()==digest,'producer complete body identity')
    # Both possible link stores precede the shared node/record initialization.
    check(pc+178 not in post.reachable(ei,pc,{pc+174,pc+246}),'producer node-link stores dominate node initialization')
    return {'start':hex(pc),'end_exclusive':hex(pc+268),'bytes':268,'sha256':digest,
        'instructions':list(n.values()),'conditional_normal_return_CFG':edges,'cyclic_SCCs':cycles,
        'encoded_GPR_writes':writes,'store_PCs':[hex(p) for p in stores],
        'saved_frame_bytes':48,'saved_register_words':[{'register':r,'SP_offset':off} for _,r,off,_ in SAVED],
        'normal_status_paths':{'2':'entry callback word A0==0 after control-word prologue',
            '8':'16 sequential callback-word reads from initial P snapshot observed nonzero; not an atomic arena snapshot',
            '11':'allocation reply zero after optional fallback call',
            '0':'node linked/initialized, record writes, optional index store and control-word restore complete'},
        'pre_call':{'pc':hex(pc+88),'target_source':hex(M+68),'local_null_guard':False,
            'A0_A4':'entry callback, argument, node_input8, optional index pointer, metadata_word',
            'scalar_A0_reply_used':False,'ambient_registers_remain_observable':True},
        'allocation_call':{'pair_start':hex(pc+126),'transfer':hex(pc+130),'target':'0x20000040',
            'A0':16,'A1':65280,'A2':0,'A3':12,'A4':'initial arena snapshot P','A5':16,
            'reply':'Q, nonzero needed; actual extent/ownership unproved'},
        'fallback_call':{'pc':hex(pc+150),'target_source':hex(M+132),'null_guard':True,
            'A0':4,'A1':0,'other_registers':'then-live values after allocation core',
            'scalar_reply_used':False,'allocation_retry_after_normal_return':False},
        'arena_selection':{'pointer_source':hex(Pslot),'callback_word_only_tested':True,
            'index_domain_with_context':[0,15],'entry_width':12,'initial_snapshot':'P',
            'write_snapshot':'fresh Pprime reloaded after allocation','destination_empty_rechecked':False},
        'node_link':{'head_slot':hex(M+76),'head_store_pc':hex(pc+174),'tail_next_store_pc':hex(pc+246),
            'next_field_offset':12,'cycle_guard_or_bound':False,'link_before_node_fields':True},
        'node_field_stores':[{'pc':hex(pc+off),'offset':field,'bytes':width,'value':v}
            for off,field,width,v in ((178,0,1,0),(192,12,4,0),(196,8,4,'saved entry A2'),
                (200,2,2,'low16(1<<index)'),(202,4,4,'saved entry A4'))],
        'node_byte1_directly_initialized':False,
        'record_stores':[{'pc':hex(pc+off),'offset':field,'value':v}
            for off,field,v in ((208,0,'saved entry A0'),(212,4,'saved entry A1'),(216,8,'saved entry A4'))],
        'optional_index_store':{'pc':hex(pc+224),'destination':'then-live S4, saved entry A3 with context',
            'width':1,'value':'low8(index)','null_guard':True},
        'publication_is_atomic_or_success_means_event_delivery':False}


def derive(app,carriers,header):
    old=previous.derive(app,carriers,header);profiles=[]
    for i,(data,prior,(pc,digest)) in enumerate(zip(carriers,old['profiles'],DETAILS)):
        C=init.DETAILS[i][5];M=C-80;Pslot=C+64
        check(prior['arena_pointer_slot']==hex(Pslot),'producer-to-consumer arena storage slot')
        p=body(init.binding.take(data,pc,268),pc,M,Pslot,digest)
        profiles.append({'label':prior['label'],'producer':p,'metadata_base':hex(M),'arena_pointer_slot':hex(Pslot),
            'consumer_kind0_entry':prior['literal_handlers'][0]['start'],
            'conditional_matching_record':'producer writes Pprime+12*i; kind0 g=0 reads Plive+12*k; same record only if i=k and bases/context agree',
            'metadata_word_relation':'saved entry A4 is stored as node+4 and record+8; kind0 freshly tests group0 record+8',
            'producer_fills_only_first_group':True,'other_group_producers_identified_here':False,
            'possible_composed_allocation_failure':{'core_input_request':16,'core_rounded_request':16,'core_tag':65280,
                'core_fallback_if_search_reaches_sentinel_and_word_nonzero':{'A0':1,'A1':0x0010ff00,'A2':0},
                'core_normal_failure_forces_A0_zero':True,'producer_fallback_is_fresh_read':True,
                'producer_fallback_if_fresh_read_nonzero':{'A0':4,'A1':0},
                'two_calls_or_same_target_unconditionally_proved':False},
            'actual_provider_binding_proved':False})
    check(sum(len(p['producer']['instructions']) for p in profiles)==194,'producer instruction total')
    check(sum(len(p['producer']['store_PCs']) for p in profiles)==52,'producer store total')
    return {'schema':'TSL9-record-producer-static-v1','profile':init.timer.PROFILE,
        'scope':'2 complete producer bodies; prior record consumer/registration provenance revalidated; no target execution',
        'profiles':profiles,
        'node_and_arena_different_roles':'Q is a separate16-byte allocation; records use reloaded arena pointer, not Q',
        'generic_semantics_not_inferred':['entry A2/A4 timing units','actual timer delivery','atomic registration or exclusive critical section'],
        'premises':['matching original/candidate code and supported encoding semantics; valid frame/code/accesses',
            'opaque calls return normally preserving required SP/S registers/saved inputs/control word',
            'Q is valid16-byte allocation and list/arena/global/frame/output ranges do not adversely alias',
            'initial P, later Pprime and consumer Plive equality require separate preservation evidence',
            'list traversal reaches null and outside writers/interrupts do not invalidate required relationships'],
        'unresolved':['producer callers and actual entry parameters','linked-node consumers and other record groups',
            'pre-call/fallback provider installation and effects','payload ownership, list reentry and event delivery'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    fields=((0,1),(2,2),(4,4),(8,4),(12,4))
    touched={j for off,width in fields for j in range(off,off+width)}
    check(touched==set(range(16))-{1},'16-byte node direct field coverage')
    for i in range(16):
        check(1<=1<<i<=0x8000 and ((1<<i)&65535)==1<<i,'node event mask width')
        check(12*i+12<=192 and 12*i==12*(16*0+i),'first-group producer/consumer offset')
    for size in range(65536):
        if size>=16:check((size-16>8)==(size>24),'request16 split threshold algebra')
    check(((16+3)&65535)&0xfffc==16 and (0xff00|(16<<16))==0x10ff00,'core request/tag algebra')
    for flag in (0,1,2,0x80000000,MASK):check(bool(flag)==(flag!=0),'full-word consumer flag predicate')
    cases=((38,'05e1','05c1'),(104,'c147','a147'),(114,'1042','5042'),
      (124,'4145','5145'),(140,'83a70722','83a72722'),(160,'2d45','2945'),
      (174,'23a4a71e','23a6a71e'),(200,'3aa1','3aa3'),(202,'23225501','23227501'),
      (208,'23a03701','23a43701'),(216,'23a45701','23a65701'),(246,'48c7','48c3'))
    pc,digest=DETAILS[0];C=init.DETAILS[0][5]
    for off,old,new in cases:
        raw=bytearray(init.binding.take(carriers[0],pc,268))
        check(raw[off:off+len(bytes.fromhex(old))]==bytes.fromhex(old),'producer mutation source '+hex(off))
        raw[off:off+len(bytes.fromhex(new))]=bytes.fromhex(new)
        try:body(raw,pc,C-80,C+64,digest)
        except RuntimeError as error:check(str(error)=='producer instruction '+hex(off),'unexpected producer mutation guard '+str(error))
        else:raise RuntimeError('producer mutation escaped')
    print('PASS: 16 node-mask/group cases; 65520 split-gap identities; node byte1 exclusion; 12 specified raw mutations')


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true',help='Create ledger exclusively');o=p.parse_args()
    app,header=init.binding.APP.read_bytes(),init.core.outer.HEADER.read_bytes()
    check(len(app)==76800 and sha256(app).hexdigest()==init.binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK header identity')
    carriers=[]
    for label,folder,tail,size,digest in init.binding.PROFILES:
        raw=(ROOT/'analysis/wch-resident-candidate-2026-10-21'/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(raw)==size and sha256(raw).hexdigest()==digest,'candidate identity '+label);carriers.append(raw)
    sources,vectors=init.timer.source_contract();ledger=derive(app,carriers,header)
    ledger['sources'],ledger['official_Xwchc_vectors']=sources,vectors
    tests(carriers);output=(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'record producer exact ledger replay')
    print('PASS: 2 complete producers, 536 bytes/194 instructions/52 stores; node/arena distinction; link-before-initialization')
    print('PASS: exact ledger replay; status/consumer edges conditional; provider/ownership/delivery UNPROVED; NO target execution')


if __name__=='__main__':main()
