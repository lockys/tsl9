"""Mapped linked-node consumer and flash event helper: static evidence only.

Complete bytes/operands/CFG and host modular arithmetic; no target ISA,
clock, node list, event buffer, allocator, provider or MMIO execution/model.
"""
import argparse
import json
import re
from hashlib import sha256
from pathlib import Path
import check_v4160_record_producer_static as previous

init,post,ROOT,MASK=previous.init,previous.post,previous.ROOT,previous.MASK
check=init.check
ENTRY=0x200004fa
OUT=Path(__file__).with_name('v4160-linked-node-consumer-static.json')
DETAILS=((0x4076a,0x4354a,'ba161fdee5b8033b76abc008a1f3c12c3187cd7394cc1ef567b91a94d9e0c06c',
          '4ef50e4708a6b1c5ac912c80d17a95724f66d5a0cf7644327399725e928c16bd'),
         (0x407aa,0x435d6,'d07007de1936346526ca0606cae4d7827ba41e93d0b848430a8ad021f60ab476',
          'ae751e4200fdbceed6610772cc6775a0863ee0a1d92169ff554ad6cda2802f3a'))
SAVED=((2,9,36,206),(8,8,40,204),(14,1,44,202),(16,18,32,208),(18,19,28,210),
       (20,20,24,212),(22,21,20,214),(24,22,16,216),(26,23,12,218),(28,24,8,220))
CYCLE=tuple(int(x,16) for x in
 '42 44 46 48 4c 50 54 56 58 5a 5c 60 62 66 68 6a 6e 72 76 78 7a 7e 82 86 88 8a 8e 92 94 96 98 9a 9e a0 a2 a6 aa ae b0 b2 b4 e2 e6 ea ec f0 f2 f6 f8 fc 100 104 108 10c 10e 110 112 116 118'.split())


def consumer_specs(M,C):
    pc=ENTRY;G=0x20003000;rows=[]
    def e(o,op,**f):rows.append((o,dict(op=op,**f)))
    def load(o,rd,base,off,width=4,**extra):e(o,'load',rd=rd,rs1=base,imm=off,width=width,**extra)
    def store(o,src,base,off):e(o,'store',rs2=src,rs1=base,imm=off,width=4)
    e(0,'addi',rd=2,rs1=2,imm=-48);e(4,'lui',rd=9,imm=G);load(10,8,9,M+76-G)
    for save,reg,off,restore in SAVED:store(save,reg,2,off);load(restore,reg,2,off)
    e(30,'beqz',rs1=8,target=pc+202)
    for off,reg in ((32,20),(36,18),(40,19),(46,21)):e(off,'lui',rd=reg,imm=G)
    e(44,'li',rd=23,imm=0);e(50,'lui',rd=22,imm=0x1c9c000)
    for off,reg,value in ((54,20,C-G),(58,18,M-G),(62,19,C+72-G)):e(off,'addi',rd=reg,rs1=reg,imm=value)
    load(66,15,8,2,2,mnemonic='qk.c.lhu');e(68,'bnez',rs1=15,target=pc+98)
    load(70,15,8,12);e(72,'bne',rs1=23,rs2=0,target=pc+92);store(76,15,9,M+76-G)
    load(80,24,8,12);e(84,'mv',rd=10,rs2=8);e(86,'jal',rd=1,target=0x20000110)
    e(88,'mv',rd=8,rs2=24);e(90,'jump',target=pc+180);store(92,15,23,12);e(96,'jump',target=pc+80)
    load(98,15,21,M+68-G);e(102,'call_indirect',rd=1,rs1=15);load(104,15,8,8)
    e(106,'sub',rd=14,rs1=10,rs2=15);e(110,'bgeu',rs1=10,rs2=15,target=pc+122)
    load(114,14,19,4);e(118,'sub',rd=14,rs1=14,rs2=15);e(120,'add',rd=14,rs1=14,rs2=10)
    e(122,'addi',rd=13,rs1=22,imm=895);e(126,'bltu',rs1=13,rs2=14,target=pc+242)
    store(130,0,18,16);load(134,11,8,2,2,mnemonic='qk.c.lhu');load(136,10,8,0,1,mnemonic='qk.c.lbu')
    # +138/+142 is a pair interpreted at the mapped RAM PC, not load-image PC.
    load(146,15,8,4);load(148,14,8,12);e(150,'beqz',rs1=15,target=pc+226)
    load(152,11,8,8);load(154,12,19,4);e(158,'add',rd=15,rs1=15,rs2=11)
    e(160,'mv',rd=13,rs2=15);e(162,'bltu',rs1=15,rs2=11,target=pc+170)
    e(166,'bltu',rs1=15,rs2=12,target=pc+174);e(170,'sub',rd=13,rs1=15,rs2=12);store(174,13,8,8)
    e(176,'mv',rd=23,rs2=8);e(178,'mv',rd=8,rs2=14);e(180,'bnez',rs1=8,target=pc+66)
    e(182,'lui',rd=15,imm=G);e(186,'addi',rd=15,rs1=15,imm=M-G);load(190,14,15,16)
    e(192,'li',rd=13,imm=1);e(194,'bgeu',rs1=13,rs2=14,target=pc+282)
    e(198,'addi',rd=14,rs1=14,imm=-1);store(200,14,15,16)
    e(222,'addi',rd=2,rs1=2,imm=48);e(224,'jr',rs1=1)
    e(226,'bne',rs1=23,rs2=0,target=pc+236);store(230,14,9,M+76-G);e(234,'jump',target=pc+80)
    store(236,14,23,12);e(240,'jump',target=pc+80)
    load(242,14,20,40);e(246,'beqz',rs1=14,target=pc+268)
    e(248,'bltu',rs1=15,rs2=10,target=pc+274);e(252,'sub',rd=10,rs1=15,rs2=10)
    load(256,15,18,16);e(260,'bgeu',rs1=10,rs2=15,target=pc+268);store(264,10,18,16)
    e(268,'mv',rd=23,rs2=8);load(270,8,8,12);e(272,'jump',target=pc+180)
    load(274,14,19,4);e(278,'add',rd=15,rs1=15,rs2=14);e(280,'jump',target=pc+252)
    store(282,0,15,16);e(286,'jump',target=pc+202)
    return {pc+o:f for o,f in rows}


def consumer_body(raw,M,C,event_target,digest):
    n=previous.previous.decode(raw,ENTRY);expected=consumer_specs(M,C)
    check(set(n)==set(expected)|{ENTRY+138,ENTRY+142},'consumer complete instruction boundaries')
    for p,f in expected.items():init.g(n,p,'consumer instruction '+hex(p-ENTRY),**f)
    init.pair(n,ENTRY+138,1,event_target,'consumer mapped event target pair')
    topology={p:dict(d,op='bne') if d['op']=='bltu' else d for p,d in n.items()}
    edges,cycles=init.timer.cfg(topology,ENTRY)
    check(cycles==[[hex(ENTRY+o) for o in CYCLE]] and len(CYCLE)==59,'consumer full walk SCC')
    writes=sorted({d['rd'] for d in n.values() if d.get('rd',0)})
    check(writes==[1,2,8,9,10,11,12,13,14,15,18,19,20,21,22,23,24],'consumer GPR writes')
    stores=[d for d in n.values() if d['op']=='store']
    check(len(stores)==19 and sum(d['rs1']==2 for d in stores)==10,'consumer store census')
    check(not any(d.get('rd')==10 for p,d in n.items() if p<=ENTRY+30),'empty-head preserves ambient entry A0')
    check(not any(d.get('rd')==10 for p,d in n.items() if ENTRY+180<=p<=ENTRY+224),'consumer final hint/epilogue preserves then-live A0')
    check(len(n)==103 and len(raw)==288 and sha256(raw).hexdigest()==digest,'consumer full body identity')
    return {'runtime_start':hex(ENTRY),'runtime_end_exclusive':hex(ENTRY+288),'bytes':288,'sha256':digest,
        'instructions':list(n.values()),'conditional_normal_return_CFG':edges,'cyclic_SCCs':cycles,
        'encoded_GPR_writes':writes,'stores':stores,'frame_bytes':48,
        'clock_call':{'pc':hex(ENTRY+102),'target_source':hex(M+68),'local_null_guard':False,
            'explicit_argument_setup':False,'ambient_registers_observable':True},
        'event_call':{'pair_start':hex(ENTRY+138),'pc':hex(ENTRY+142),'target':hex(event_target),
            'A0':'fresh U8[current node+0]','A1':'fresh U16[current node+2]',
            'scalar_reply_controls_retain_remove':False,'ambient_A0_visible_to_later_callees_possible':True},
        'release_call':{'pc':hex(ENTRY+86),'target':'0x20000110','A0':'then-live current node S0',
            'SDK_message_deallocate_wrapper':False,'scalar_reply_tested':False},
        'unlink':{'head_stores':[hex(ENTRY+76),hex(ENTRY+230)],
            'predecessor_next_stores':[hex(ENTRY+92),hex(ENTRY+236)],
            'next_snapshot_used_for_link':'first node+12 read on selected branch',
            'next_snapshot_used_after_release':'fresh U32[current node+12] at+80 saved in S8 before release',
            'two_next_values_same_unconditionally':False,'link_updated_before_release':True},
        'return':'not normalized: empty-head keeps entry A0; other paths retain then-live A0 from calls/arithmetic',
        'empty_head_skips_hint_normalization':True,'whole_walk_MMIO_control_prologue':False}


def event_body(raw,pc,M,digest):
    n=previous.previous.decode(raw,pc);G=0x20003000
    specs={0:dict(op='lui',rd=15,imm=0x40024000),4:dict(op='load',rd=13,rs1=15,imm=524,width=4),
      8:dict(op='store',rs1=15,rs2=0,imm=524,width=4),12:dict(op='fence.i'),
      16:dict(op='lui',rd=14,imm=G),20:dict(op='load',rd=14,rs1=14,imm=M+1-G,width=1),
      24:dict(op='bgeu',rs1=10,rs2=14,target=pc+56),28:dict(op='lui',rd=12,imm=G),
      32:dict(op='slli',rd=14,rs1=10,imm=1),36:dict(op='load',rd=10,rs1=12,imm=M+72-G,width=4),
      40:dict(op='add',rd=10,rs1=10,rs2=14),42:dict(op='load',rd=14,rs1=10,imm=0,width=2,mnemonic='qk.c.lhu'),
      44:dict(op='or',rd=11,rs1=11,rs2=14),46:dict(op='store',rs1=10,rs2=11,imm=0,width=2,mnemonic='qk.c.sh'),
      48:dict(op='store',rs1=15,rs2=13,imm=524,width=4),52:dict(op='li',rd=10,imm=0),54:dict(op='jr',rs1=1),
      56:dict(op='store',rs1=15,rs2=13,imm=524,width=4),60:dict(op='li',rd=10,imm=3),62:dict(op='jr',rs1=1)}
    check(set(n)=={pc+o for o in specs},'event helper complete instruction boundaries')
    for off,f in specs.items():init.g(n,pc+off,'event helper instruction '+hex(off),**f)
    edges,cycles=init.timer.cfg(n,pc)
    check(not cycles and len(n)==20 and len(raw)==64 and sha256(raw).hexdigest()==digest,'event full body identity and CFG')
    writes=sorted({d['rd'] for d in n.values() if d.get('rd',0)})
    check(writes==[10,11,12,13,14,15],'event GPR writes')
    return {'start':hex(pc),'end_exclusive':hex(pc+64),'bytes':64,'sha256':digest,'instructions':list(n.values()),
        'conditional_normal_return_CFG':edges,'encoded_GPR_writes':writes,
        'stores':[d for d in n.values() if d['op']=='store'],
        'accepted':'full task A0 < fresh U8[M+1]; OR into U16[fresh event_base +2*task], low16 stored; reply0',
        'rejected':'full task A0 >= count; no event pointer read/write; reply3',
        'control_word':'read/save/write0/FENCE.I before guard; restore on both normal paths',
        'null_event_base_guard':False,'invokes_APP_record_callback':False}


def derive(app,carriers,header):
    old=previous.derive(app,carriers,header);profiles=[]
    match=re.search(rb'^#define\s+tmos_set_event\s+[^\r\n]*BLE_LIB_JT\(\s*(\d+)\s*\)',header,re.M)
    check(match is not None and int(match[1])==7,'event helper SDK JT7 alias')
    release=init.core.message.release
    for i,(data,prior,(src,event_pc,digest,event_digest)) in enumerate(zip(carriers,old['profiles'],DETAILS)):
        C=init.DETAILS[i][5];M=C-80;mapping=init.binding.profile(data,prior['label']);copy=mapping['first_copy']
        check(prior['producer']['node_link']['head_slot']==hex(M+76),'producer-to-consumer head storage slot')
        start=int(copy['destination'],16);end=int(mapping['first_copy_end_exclusive'],16)
        check(start<=ENTRY and ENTRY+288<=end and int(copy['source'],16)+ENTRY-start==src,'consumer complete first-copy source mapping')
        raw=init.binding.take(data,src,288);consumer=consumer_body(raw,M,C,event_pc,digest)
        check(init.binding.word(data,0x40050)&~1==event_pc,'event slot40050 alias')
        event=event_body(init.binding.take(data,event_pc,64),event_pc,M,event_digest)
        free_src=release.DETAILS[i][0]
        check(int(copy['source'],16)+0x20000110-start==free_src and
              sha256(init.binding.take(data,free_src,212)).hexdigest()==release.DETAILS[i][-1],'consumer private release provenance')
        # Demonstrate why using load-image PC for PC-relative transfers is wrong.
        wrong=previous.previous.decode(raw,src)
        check(wrong[src+86]['target']!=0x20000110,'consumer runtime/load-image call distinction')
        profiles.append({'label':prior['label'],'consumer':dict(consumer,flash_source=hex(src)),
            'event_helper':event,'metadata_base':hex(M),'config_base':hex(C),
            'list_head_slot':hex(M+76),'hint_slot':hex(M+16),'future_hint_gate':hex(C+40),
            'wrap_word':hex(M+156),'private_release':{'target':'0x20000110','flash_source':hex(free_src),
                'bytes':212,'sha256':release.DETAILS[i][-1],'actual_release_or_ownership_proved':False},
            'producer_join':{'producer':prior['producer']['start'],'initial_node0':0,
                'initial_node2':'low16(1<<index)','initial_node4':'producer entry A4','initial_node8':'producer entry A2',
                'initial_fields_still_live_at_consumer_proved':False},
            'cancellation_join':'matched-node mask+2 can be cleared by stop-task path; zero mask branch here unlinks/releases without event call for that node'})
    check(sum(len(p['consumer']['instructions'])+len(p['event_helper']['instructions']) for p in profiles)==246,'node consumer/helper instruction total')
    check(sum(len(p['consumer']['stores'])+len(p['event_helper']['stores']) for p in profiles)==46,'node consumer/helper store total')
    return {'schema':'TSL9-linked-node-consumer-static-v1','profile':init.timer.PROFILE,
        'scope':'2 complete mapped288B consumers +2 complete flash64B event helpers; no list/time/event execution',
        'profiles':profiles,
        'mask_zero_path':'read next; unlink head/predecessor; fresh reread next into S8; private release; advance to S8; predecessor unchanged',
        'eligibility_equation':'E1=fresh node+8 after clock reply N; D=(N-E1) mod32 if N>=E1 else (fresh W0-E1+N) mod32',
        'event_path_predicate':'D <= 29999999, inclusive; scalar event-helper reply not checked',
        'event_then_lifetime':'fresh node+4==0 unlinks/releases; otherwise fresh E2 and W2 form one update to node+8',
        'repeat_equation':'u=(fresh repeat + fresh E2) mod32; new E=(u-fresh W2) mod32 if u<E2 or u>=W2 else u',
        'repeat_is_generic_modulo_or_catchup_loop':False,
        'future_hint':'only if fresh U32[config+40]!=0: remaining=(E1-N) mod32, or (E1+fresh W1-N) mod32 when E1<N; store only if remaining<fresh hint',
        'final_hint':'after nonempty traversal ends, fresh h>1 becomes h-1, h<=1 becomes0; initially empty head skips it',
        'physical_time_unit_or_earliest_hint_proved':False,
        'premises':['first-copy RAM bytes and supported ISA semantics match; code/frame/list/event accesses valid',
            'clock/release callees return normally preserving required SP/S registers/frame',
            'list/global/frame/event ranges do not adversely alias; no unaccounted interrupt/writer/MMIO effects',
            'list walk reaches null; fresh node/deadline/period/next snapshots only equated with separate preservation evidence'],
        'remaining_boundaries':['actual clock provider/installed binding and time units','node/record mutation, cancellation and ownership',
            'outer event dispatch and APP callback invocation','whole-walk atomicity and universal termination'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    # Host equations only: no list, target registers, event memory or clock state.
    for n in range(256):
        for e in range(256):
            d=n-e if n>=e else 256-e+n
            check(d==(n-e)%256,'bounded wrap-distance identity')
            u=e+n;once=u-256 if u>=256 else u
            check(once==(e+n)%256,'bounded one-subtract repeat identity')
    for word in range(65536):
        for mask in (0,1,0x8000,0xffff):check((word|mask)|mask==word|mask,'event OR idempotence')
    check(0x1c9c000+895==29999999 and 29999999<30000000,'inclusive event threshold')
    check(100-30==70 and 70!=100%30,'one subtract is not generic modulo')
    for count in range(256):
        for task in range(256):check((task<count)==(not task>=count),'full U8 task/count partition')
    cases=(('consumer',66,0x20),('consumer',86,4),('consumer',102,0x80),('consumer',122,1<<20),
           ('consumer',136,0x1000),('consumer',146,0x40),('consumer',148,0x40),('consumer',174,0x40),
           ('consumer',256,1<<22),('consumer',264,1<<9),('event',24,0x1000),('event',46,4))
    M=init.DETAILS[0][5]-80;src,event_pc,digest,event_digest=DETAILS[0]
    for role,off,flip in cases:
        pc,size=(ENTRY,288) if role=='consumer' else (event_pc,64)
        raw=bytearray(init.binding.take(carriers[0],src if role=='consumer' else event_pc,size))
        nodes=previous.previous.decode(raw,pc);node=nodes[pc+off];width=node['size']
        raw[off:off+width]=(int.from_bytes(raw[off:off+width],'little')^flip).to_bytes(width,'little')
        wanted=('consumer instruction ' if role=='consumer' else 'event helper instruction ')+hex(off)
        try:
            if role=='consumer':consumer_body(raw,M,M+80,event_pc,digest)
            else:event_body(raw,event_pc,M,event_digest)
        except RuntimeError as error:check(str(error)==wanted,'unexpected node-consumer mutation guard '+str(error))
        else:raise RuntimeError('node-consumer mutation escaped')
    print('PASS: 65536 wrap-distance cases; 65536 bounded-repeat cases; 262144 OR cases; 65536 task/count pairs; 12 specified raw mutations')


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
    else:check(OUT.read_bytes()==output,'linked-node consumer exact ledger replay')
    print('PASS: 4 complete bodies, 704 bytes/246 instructions/46 stores; runtime mappings and event/release targets')
    print('PASS: exact ledger replay; repeat/unlink/hint edges conditional; binding/clock/ownership/delivery UNPROVED; NO target execution')


if __name__=='__main__':main()
