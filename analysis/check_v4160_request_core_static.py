"""Offline complete request core, conditional output writes and loop bound.

Literal operand/CFG and integer/interval proofs only. No target ISA execution,
emulation, mutable register/RAM machine, providers, allocator or hardware model.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_request_tail_static as previous

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-request-core-static.json')
STARTS=(0x68bb4,0x68cf2)
HASHES=('39d5e08577b70b923670de9394caa111f311d58b72c464424b21f4fa1a161a21','ce68665d1e54292fb206978657907d3451471b9c8bd0bfc0c5d3a7464cb496fe')


def specs(index):
    pc=STARTS[index];s={};d=80*index
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def ai(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    def lui(o,r,v=0x20003000):e(o,'lui',rd=r,imm=v)
    def ld(o,r,b,v,w=4,**f):e(o,'load',rd=r,rs1=b,imm=v,width=w,**f)
    def st(o,r,b,v,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    def mv(o,r,b):e(o,'mv',rd=r,rs2=b)
    def imm(o,op,r,b,v):e(o,op,rd=r,rs1=b,imm=v)
    def br(o,op,a,b,t):e(o,op,rs1=a,rs2=b,target=pc+t)
    def bz(o,r,t):e(o,'beqz',rs1=r,target=pc+t)
    def bnz(o,r,t):e(o,'bnez',rs1=r,target=pc+t)
    def j(o,t):e(o,'jump',target=pc+t)
    def call(o,t):e(o,'jal',rd=1,target=t)
    ai(0,2,2,-80);st(2,9,2,68);lui(4,9);ai(8,6,9,952+d);ld(12,6,6,88)
    for o,r,v in ((16,18,64),(18,19,60),(20,24,40),(22,25,36),(24,26,32),(26,1,76),(28,8,72),(30,20,56),(32,21,52),(34,22,48),(36,23,44),(38,27,28)):st(o,r,2,v)
    ld(40,24,2,84,1,signed=True);ld(44,19,2,88,1);ld(48,18,2,96,1);ld(52,25,2,108,1);ld(56,26,2,112,1);ai(60,9,9,952+d)
    br(64,'beq',6,0,114);ld(68,6,6,84);imm(72,'slli',8,6,5);br(76,'bge',8,0,114);li(80,6,12)
    for o,r,v in ((82,1,76),(84,8,72),(86,9,68),(88,18,64),(90,19,60),(92,20,56),(94,21,52),(96,22,48),(98,23,44),(100,24,40),(102,25,36),(104,26,32),(106,27,28)):ld(o,r,2,v)
    mv(108,10,6);ai(110,2,2,80);e(112,'jr',rs1=1);li(114,28,3);li(116,6,18);br(118,'bltu',28,15,82)
    imm(122,'andi',27,11,16);br(126,'beq',27,0,278);li(130,28,1);br(132,'bne',19,28,82)
    st(136,14,2,12);mv(138,22,17);st(140,16,2,8);st(142,15,2,4);mv(144,23,13);mv(146,21,12);mv(148,8,11);st(150,10,2,0)
    call(152,0x55108+202*index);mv(156,20,10);ld(158,14,2,12);bnz(160,10,180);ld(162,15,9,104);li(164,10,1);e(166,'call_indirect',rd=1,rs1=15)
    mv(168,20,10);li(170,6,7);bz(172,10,82);ld(174,15,2,0);ld(176,14,2,12);st(178,15,10,8,1)
    ai(180,11,0,32);br(184,'bne',23,11,218);li(188,11,3);br(190,'bne',18,11,350);ld(194,10,20,28,2);ai(198,11,0,249)
    ai(202,6,0,69);br(206,'bltu',11,10,82);ld(210,10,20,30,2);br(214,'bltu',11,10,82)
    imm(218,'andi',11,8,255);st(222,11,20,96,1);br(226,'beq',27,0,668);imm(230,'andi',8,8,15);li(232,10,5);br(234,'bne',8,10,366)
    ai(238,10,0,-127);st(242,10,20,14,1);li(246,6,17);br(248,'bltu',23,21,82);li(252,10,31);li(254,6,17);br(256,'bgeu',10,21,82)
    lui(260,10,0x4000);br(262,'bltu',10,23,82);e(266,'add',rd=12,rs1=23,rs2=21);imm(270,'srli',12,12,1);st(272,12,20,32,2);j(276,384)
    imm(278,'andi',29,11,3);li(282,6,18);br(284,'beq',29,28,82);imm(288,'andi',29,11,8);br(292,'bne',29,0,82);br(296,'bne',19,28,332)
    ld(300,6,9,60,1);imm(304,'andi',6,6,4);br(308,'beq',6,0,80);br(312,'beq',18,19,136);li(316,6,2);br(318,'bne',18,6,136)
    ld(322,6,9,60,1);imm(326,'andi',6,6,2);j(330,344);br(332,'bne',18,28,316);ld(336,6,9,60,1);imm(340,'andi',6,6,4);br(344,'bne',6,0,136);j(348,80)
    li(350,11,1);br(352,'bne',18,11,218);ld(356,10,20,28,2);ai(360,11,0,749);j(364,202)
    li(366,10,13);br(368,'bne',8,10,648);li(372,13,1);st(374,13,20,14,1);li(378,13,2);st(380,13,20,32,2)
    st(384,14,20,15,1);br(388,'bne',14,0,742);li(392,14,1);st(394,14,20,24,1);imm(398,'andi',11,11,32);bnz(402,11,410);ld(404,15,2,4);st(406,15,20,53,1)
    li(410,12,6);li(412,11,0);mv(414,10,22);e(416,'auipc',rd=1,imm=0x1ff97000);e(420,'jalr',rd=1,rs1=1,imm=1896-318*index);br(424,'bne',10,0,776)
    ld(428,15,2,8);li(430,14,1);st(432,14,20,60,1);st(436,15,20,61,1);li(440,12,6);mv(442,11,22);ai(444,10,20,62)
    e(448,'auipc',rd=1,imm=0x1ff97000);e(452,'jalr',rd=1,rs1=1,imm=1470-318*index)
    ld(456,14,2,80,1);st(460,14,20,13,1);ai(464,14,0,127);br(468,'bne',24,14,782);lui(472,14);ld(476,14,14,512+d,1);ld(480,15,2,116);st(482,14,15,0,1)
    ld(484,10,20,21,1,signed=True);call(488,0x639ca+234*index);st(492,10,20,104,1);call(496,0x63966+234*index);ld(500,15,2,116);st(502,10,20,21,1);li(506,14,3);st(508,10,15,0,1)
    br(510,'bne',19,14,800);br(514,'beq',25,0,540);imm(518,'andi',13,25,1);bz(522,13,536);ld(524,14,9,60,1);imm(528,'andi',14,14,8);bnz(530,14,536);br(532,'beq',25,19,80);st(536,13,20,106,1)
    li(540,14,2);st(542,14,20,100,1);ld(546,14,2,92,1);st(550,14,20,101,1);ld(554,14,20,96,1);imm(558,'andi',14,14,16);bnz(560,14,614)
    ai(562,14,18,-1);imm(566,'andi',14,14,255);li(570,13,2);li(572,6,18);br(574,'bltu',13,14,82);li(578,13,3);br(580,'bne',18,13,810)
    br(584,'beq',26,0,610);imm(588,'andi',12,26,1);bz(592,12,606);ld(594,13,9,60,1);imm(598,'andi',13,13,8);bnz(600,13,606);br(602,'beq',26,18,80);st(606,12,20,107,1);st(610,14,20,99,1)
    ld(614,14,2,100,1);lui(618,13,0x08000000);li(622,6,0);st(624,14,20,97,1);ld(628,14,2,104,1);st(632,14,20,103,1);ld(636,14,20,84);e(640,'or',rd=14,rs1=14,rs2=13);st(642,14,20,84);j(646,82)
    li(648,10,2);br(650,'bne',8,10,658);li(654,10,6);j(656,242);br(658,'beq',8,0,242);st(662,0,20,14,1);j(666,246)
    li(668,10,7);st(670,10,20,14,1);imm(674,'andi',16,11,1);imm(678,'andi',10,11,4);br(682,'beq',16,0,704);li(686,16,4);bz(688,10,692);li(690,16,1);st(692,16,20,95,1);li(696,10,1);st(698,10,20,94,1);j(702,246)
    imm(704,'andi',16,11,2);br(708,'beq',16,0,726);li(712,16,2);bz(714,10,718);li(716,16,5);st(718,16,20,95,1);li(722,10,2);j(724,698);li(726,16,3);bz(728,10,732);li(730,16,6);st(732,16,20,95,1);st(736,0,20,94,1);j(740,246)
    st(742,0,20,24,1);li(746,13,0);li(748,10,3);e(750,'sra',rd=12,rs1=14,rs2=13);imm(754,'andi',12,12,1);bz(756,12,768);ld(758,12,20,24,1);ai(762,12,12,1);st(764,12,20,24,1);ai(768,13,13,1);br(770,'bne',13,10,750);j(774,398)
    st(776,0,20,60,1);j(780,456);li(782,14,6);br(784,'blt',14,24,794);st(788,24,20,21,1);j(792,484);st(794,14,20,21,1);j(798,484);st(800,0,20,106,1);st(804,0,20,100,1);j(808,546);st(810,0,20,107,1);j(814,610)
    return s


def body(raw,index):
    pc=STARTS[index];s=specs(index);n=decode(raw,pc)
    check(set(n)==set(s),'core boundaries')
    for p,f in s.items():init.g(n,p,'core operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(816,271,HASHES[index]),'core identity')
    edges={};calls=[]
    for p,d in n.items():
        op=d['op'];q=[p+d['size']]
        if op=='jr':check(d['rs1']==1,'core returnRA');q=[]
        elif op in ('beq','bne','beqz','bnez','bge','bltu','bgeu','blt'):q.append(d['target'])
        elif op=='jump':q=[d['target']]
        elif op in ('jal','jalr','call_indirect'):
            if op=='jal':t=hex(d['target'])
            elif op=='call_indirect':t='freshU32[contextB+104]'
            else:
                a=n[p-4];check(a['op']=='auipc' and a['rd']==d['rs1'],'core PC pair');t=hex((p-4+a['imm']+d['imm'])&0xfffffffe)
            check(d['rd']==1,'core call link');calls.append({'pc':hex(p),'target':t})
        check(all(v in n for v in q),'core closedCFG');edges[p]=q
    reachable={pc};todo=[pc]
    while todo:
        for q in edges[todo.pop()]:
            if q not in reachable:reachable.add(q);todo.append(q)
    check(reachable==set(n),'core all nodes locally reachable')
    dag={p:[q for q in qs if (p,q)!=(pc+770,pc+750)] for p,qs in edges.items()};seen=set();active=set()
    def visit(p):
        check(p not in active,'core no cycle except single bitcount backedge')
        if p in seen:return
        active.add(p)
        for q in dag[p]:visit(q)
        active.remove(p);seen.add(p)
    visit(pc)
    stores=[d for d in n.values() if d['op']=='store'];check(len(stores)==56 and len(calls)==6,'core store/call census')
    outputs=[p-pc for p,d in n.items() if d['op']=='store' and d['rs1']==15];check(outputs==[482,508] and all(n[pc+o]['imm']==0 and n[pc+o]['width']==1 for o in outputs),'core exact two output byte-store sites')
    check([(p-pc,d['imm']) for p,d in n.items() if d['op']=='load' and d['rd']==15 and d['rs1']==2 and d['imm']==116]==[(480,116),(500,116)],'core output pointer loaded from tenth incoming stackword')
    check([p-pc for p,d in n.items() if d.get('rd')==13 and 742<=p-pc<=770]==[746,768],'core loop counter onlyinit/increment')
    check([p-pc for p,d in n.items() if d.get('rd')==10 and 742<=p-pc<=770]==[748],'core loop bound register3 unchanged')
    check(all(d['rs2']!=22 for d in stores if d['rs1']!=2),'core no explicit nonframe store of borrowedA7 inS6')
    # Compiler-style reaching definitions, not register-value execution.
    # Every call is conservatively an arbitrary T1 definition.
    reaching={p:set() for p in n};reaching[pc].add(-1);changed=True
    while changed:
        changed=False
        for p,d in n.items():
            outgoing={p} if d.get('rd')==6 or d['op'] in ('jal','jalr','call_indirect') else reaching[p]
            for q in edges[p]:
                before=len(reaching[q]);reaching[q].update(outgoing)
                changed|=len(reaching[q])!=before
    defs=sorted(reaching[pc+108]);check(defs==[pc+o for o in (80,116,170,202,246,254,282,572,622)],'core complete return T1 reaching definitions')
    check(all(n[p]['op'] in ('li','addi') and n[p].get('rs1',0)==0 for p in defs),'core return definitions are literal status constants')
    statuses=sorted({n[p]['imm'] for p in defs});check(statuses==[0,7,12,17,18,69],'core all local return status domain')
    without_output={pc};todo=[pc]
    while todo:
        for q in edges[todo.pop()]:
            if q!=pc+508 and q not in without_output:without_output.add(q);todo.append(q)
    check(pc+622 not in without_output,'core final output508 dominates local success0 definition')
    return {'start':hex(pc),'end_exclusive':hex(pc+816),'bytes':816,'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),'calls':calls,'store_count':56,
            'conditional_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},'complete_local_body':True,'only_cycle_backedge':[hex(pc+770),hex(pc+750)],'output_store_offsets':outputs,
            'return_definitions':{'T1_literal_definition_offsets':[p-pc for p in defs],'status_domain':statuses,'calls_conservatively_clobber_T1':True,'output508_dominates_success0_definition':True}}


def certificates(b):
    pc=int(b['start'],16);e={int(p,16):[int(q,16) for q in qs] for p,qs in b['conditional_CFG'].items()}
    typed={64:114,118:122,126:130,132:136};got={**typed,160:180}
    common={**got,184:218,226:230,234:366,368:372,388:392,402:404,424:776,468:472,510:800,560:614}
    untyped={64:114,118:122,126:278,284:288,292:296}
    via3={**untyped,296:300,308:312,312:136,160:180,184:218,226:668,682:686,688:692,248:252,256:260,262:266,388:392,402:404,424:776,468:472,510:514}
    via1={**untyped,296:332,332:316,318:136,160:180,184:218,226:668,682:704,708:726,728:732,248:252,256:260,262:266,388:392,402:404,424:776,468:472,510:800,560:562,574:82}
    cases={
        'early12_busy':{64:68,76:80},'early18_packedA5':{64:114,118:82},'early18_typed_role':{64:114,118:122,126:130,132:82},
        'early7_allocation_null':{**typed,160:162,172:82},'early69_bound':{**got,184:188,190:194,206:82},
        'early17_interval':{**got,184:218,226:230,234:238,248:82},'early18_lowbits':{**untyped,284:82},
        'early12_capability':{**untyped,296:300,308:80},
        'success0_sentinel':common,'success0_signed_input':{**common,468:782,784:788},
        'late12_query64':{**via3,514:518,522:524,530:532,532:80},
        'late18_query27':via1,
        'late12_query65':{**via3,514:540,560:562,574:578,580:584,584:588,592:594,600:602,602:80}}
    result={}
    for name,c in cases.items():
        path=previous.previous.previous.previous.paths.chain(e,pc,{pc+p:pc+q for p,q in c.items()})
        writes=[int(p,16)-pc for p in path if int(p,16)-pc in (482,508)]
        check(bool(writes)==(name.startswith('late') or name.startswith('success')),'core output phase '+name)
        calls=[v['target'] for v in b['calls'] if v['pc'] in path]
        expected=0 if name.startswith('success') else int(''.join(v for v in name.split('_')[0] if v.isdigit()))
        ns={v['pc']:v for v in b['instructions']};defs=[int(p,16) for p in path if ns[int(p,16)].get('rd')==6]
        check(ns[defs[-1]]['imm']==expected and ns[defs[-1]]['op'] in ('li','addi'),'core selected literalstatus '+name)
        check(all(v['pc'] not in path[path.index(hex(defs[-1]))+1:] for v in b['calls']),'core selected no call after finalstatus definition')
        result[name]={'path':path,'local_output_store_offsets':writes,'call_targets':calls,'local_status_at_return':expected,'actual_reachability_and_callee_returns_are_premises':True}
    check(len(result)==13,'core13 selected paths/profile');return result


def domains():
    for b in range(256):
        s=b-256 if b&128 else b
        if s!=127:check(-128<=min(s,6)<=6,'core signed input cap keepsnegative values')
    pack=[v for v in range(256) if v<=3];check(pack==[0,1,2,3],'core fullA5 unsigned limit')
    roles=[v for v in range(256) if ((v-1)&255)<=2];check(roles==[1,2,3],'core latequery27 accepted byte domain')
    bitmap=[1 if v==0 else sum((v>>k)&1 for k in (0,1,2)) for v in range(256)]
    check({v:bitmap.count(v) for v in range(4)}=={0:31,1:97,2:96,3:32},'core zero specialcase vs low3 popcount')
    check(list(range(3))==[0,1,2] and all((i+1!=3)==(i<2) for i in range(3)),'core exact three-step loop bound')
    for lo,hi in ((32,32),(32,16384),(16384,16384),(1024,2048)):
        check(32<=lo<=hi<=16384 and lo+hi<=32768 and lo<=(lo+hi)//2<=hi,'core valid unsigned interval arithmetic')
    for bit in (0,1,25,26,27,31):check(bool(((1<<bit)<<5&0xffffffff)&0x80000000)==(bit==26),'core entrybusy bit26 identity')
    return {'signed_input_domain_cases':256,'sentinel':127,'nonsentinel_cap':'min(signedlow8,6), negatives preserved','late_query27_accepts':[1,2,3],
            'bitmap_counts':{str(v):bitmap.count(v) for v in range(4)},'bitmap0_result':1,'nonzero_bitmap_result':'popcount(low3), includes0 for nonzero high-bit-only values',
            'bitcount_iterations':3,'busy_bit':26,'success_object_flag_OR':'08000000hex bit27','interval':'32<=unsignedquery3<=unsignedquery4<=16384; SH midpoint floor((lo+hi)/2)',
            'output_address_relation':'coreSP=adapterSP-80; U32[coreSP+116]=U32[adapterSP+36]=adapterSP+61 under caller-frame preservation'}


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[]
    for i,(data,pr) in enumerate(zip(carriers,parent['profiles'])):
        pc=STARTS[i];b=body(init.binding.take(data,pc,816),i);n={v['pc']:v for v in b['instructions']};certs=certificates(b);B=0x200033b8+80*i
        check(pr['adapter']['core_target']==b['start'],'core joins published adaptercall')
        check(n[pc+8]['imm']+0x20003000==B and n[pc+60]['imm']+0x20003000==B,'core fixed contextbase')
        check([v['target'] for v in b['calls']]==[hex(0x55108+202*i),'freshU32[contextB+104]','0x200004bc','0x20000332',hex(0x639ca+234*i),hex(0x63966+234*i)],'core actual callee target sequence')
        profiles.append({'label':pr['label'],'body':b,'selected_CFG_paths':certs,'frame_bytes':80,'saved':['RA','S0','S1','S2','S3','S4','S5','S6','S7','S8','S9','S10','S11'],
            'context':{'B':hex(B),'busy_object_slot':hex(B+88),'busy_test':'nonnullobject andword[object+84]bit26 ->return12','capability_byte':hex(B+60),'unguarded_callback_slot':hex(B+104)},
            'entry_contract':{'registers':['originalA0','mappedtagA1','query3fullA2','query4fullA3','byteP2+10 A4','packedflagsA5','preparereplyA6','borrowedP2+4 A7'],
                'stack_reads':{'80':'unsignedbyte argument0','84':'signedbyte query25','88':'unsignedbyte query26','92':'unsignedbyte query28','96':'unsignedbyte query27','100':'unsignedbyte query29','104':'unsignedbyte query30','108':'unsignedbyte query64','112':'unsignedbyte query65','116':'fullpointer toadapterSP61'},
                'A5_gate':'full unsignedA5>3 returns18','typed_gate':'entryA1bit4 set requires query26byte=1,else18','untyped_gates':'bit4clear: low2!=3,bit3clear; query26/query27 andfreshcontextcapabilities select12 orcontinue; see exactCFG'},
            'object_acquisition':{'direct_target':hex(0x55108+202*i),'nonnull':'S4=object result','null':'callfreshU32[B+104](1) without localcallback nullguard; nullreplyreturns7',
                'new_object_store':'only callbacknonnull branch stores low8 originalA0 atobject+8','required_extent':'dynamic object stores/reads through offset107; validwritable at least108bytes pluscallee needs unproved',
                'distinct_from_request_allocation':'S4 from lookup/callback is not proved equal to earlier12byte request allocation used as borrowedA7 source'},
            'pre_output_changes':{'stored_tag':'U8[object+96]=low8 originaltag','range_return17':'unsignedquery3>query4 OR query3<=31 OR query4>16384; some objectwrites already occurred',
                'bound_return69':'when query4=32 andquery27=3, LHUobject28/30<=249 required; query27=1 uses749; otherquery27 skipsboundcheck',
                'mode_fields':'typed lowtag5 ->byte14=81hex andSH midpoint@32; typed13 ->byte14=1,SH2@32; typed2/0/other use6/2/0; untyped usesbyte14=7 andfields94/95',
                'bitmap':'object15=entryA4; zero ->object24=1; nonzero ->3iteration lowbitcount intoobject24; source/alias/concurrency conditions remain'},
            'borrowed_A7':{'saved_register':'S6','first_provider':{'target':'0x200004bc','args':['borrowedA7',0,6],'reply_gate':'zero ->setobject60=1,object61=low8preparereply,copy6toobject62; nonzero ->object60=0'},
                'copy':{'target':'0x20000332','args':['object+62','borrowedA7',6]},'local_pointer_storage':'oldS6 saved inframe before assignment; no explicit nonframe store of borrowedA7; providers receive it, retention/consumption/success unknown'},
            'output_contract':{'pointer':'freshU32[coreSP116] eachwrite, no localnullguard','two_local_sites':[hex(pc+482),hex(pc+508)],
                'sentinel127':'firststorefreshU8['+hex(0x20003200+80*i)+'] tooutput, thencommonhelpers',
                'nonsentinel':'objectbyte21=min(signedquery25byte,6), preservingnegative values, thencommonhelpers',
                'common':'639ca/63ab4(signedLBobject21) ->SBreplylow8toobject104; 63966/63a50(currentA0andotherliveargs) ->SBreplylow8toobject21 andoutput',
                'last_value':'low8 secondhelperreply under validcallee/frame/output extent, not necessarily corestatus',
                'early_returns':'selected12/18/7/69/17 paths have no localoutputstore; no universal output initialization',
                'late_returns':'selected12/18 afteroutputstores exist; output mayalreadybe initialized onerror',
                'adapter_consequence':'adapterstillrequests2byte notification(statuslow8,SP61) after anynormalcorereturn; earlierunwrittenSP61 premise remains onpreoutput paths'},
            'late_state_and_returns':{'query64_65_capability_checks':'canreturn12 afteroutputwrites','query27_gate':'if freshobject96bit4clear thenquery27must1..3,else18 afteroutput',
                'success':'SBTlow8query29@object97,query30@103;wordobject84 |=08000000; T1=0; shared epilogue returnsT1',
                'all_local_status_constants':[0,7,12,17,18,69],'rollback_proved':False,'returns_do_not_undo_previous_writes':True},
            'actual_installed_binding_proved':False,'target_execution_or_emulation':False})
    return {'schema':'TSL9-request-core-static-v1','profile':parent['profile'],'APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'integer_domains':domains(),
            'scope':'two full816B/271i cores;1632originalbytes/542operand guards;26selectedCFGpaths andone bounded3iterationlocalcycle/profile',
            'boundary':'complete local CFG/operands; selected paths are conditional certificates, not actual reachability. Provider returns/ABI/object extent/outputpointer/source validity/retention unproved',
            'remaining':['55108/551d2 acquisition andunguardedcallback installedbinding','200004bc/20000332 borrowed6byte consumption/retention','639ca/63ab4 and63966/63a50 output semantics','context/source writers, callback enumerators andmissingROMpattern'],
            'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    mutations=paths=0
    for i,data in enumerate(carriers):
        pc=STARTS[i];raw=init.binding.take(data,pc,816);b=body(raw,i);paths+=len(certificates(b))
        for p,d in decode(raw,pc).items():
            at=p-pc;z=d['size'];buf=bytearray(raw);buf[at:at+z]=(int.from_bytes(buf[at:at+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
            try:body(buf,i)
            except RuntimeError as e:check(str(e).startswith('core operand '),'core specified mutation '+str(e))
            else:raise RuntimeError('core mutation escaped')
            mutations+=1
    check((mutations,paths)==(542,26),'core mutation/path census');domains()
    print('PASS:542 operand mutations rejected;1632 original bytes;26 CFG path certificates;single3iterationcycle;256 signed/bitmap domain cases')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');o=parser.parse_args()
    image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK identity')
    carriers=[]
    for label,folder,tail,z,digest in init.binding.PROFILES:
        data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidate identity '+label);carriers.append(data)
    raw_hex=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
    coverage=sparse.derive(image,carriers,header,raw_hex,sparse.parser());ledger=derive(image,carriers,header,coverage);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers)
    output=(json.dumps(ledger,indent=1,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'core exact ledger replay')
    print('PASS:adapterSP61 output stores;early/late error partition;borrowedA7 anddynamic object contracts;exact ledger')
    print('PASS:NO target execution/emulation;provider/output initialization/retention/actualbinding UNPROVED')


if __name__=='__main__':main()
