"""Offline original-operand and finite CFG certificates for two list callbacks.

No target ISA, callbacks, provider, MMIO, scheduler, register machine or mutable
RAM/object model is executed. Arithmetic checks use bounded integer identities.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_list_setup_handler_static as previous

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-list-direct-callbacks-static.json')
PARTS=('bit0','bit1')
STARTS=((0x558a8,0x550cc),(0x559e0,0x55196))
HASHES=(('9216c986b163fd691e4682719c527d34f935d73234126d8f15e922cc0d87dd67','491b7de0e29c5715080af568586caa361a85244a7ad0db1f7c50fb89361a0869'),
 ('b0c450a8b1e264d26154d1ebcfff940f6d59a84572e68c49279a914e53336497','71fceb63357b4fca57142005c31ea4649b9a45d1b65dc1a6b5df89f4ecf973a7'))


def offset(o,index,part='bit0'):
    return o+(8 if index and part=='bit0' and o>=204 else 0)


def specs(part,index):
    pc=STARTS[index][PARTS.index(part)];s={};d=80*index
    def addr(o):return pc+offset(o,index,part)
    def e(o,op,**f):s[addr(o)]=dict(op=op,**f)
    def ai(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def lui(o,r,v=0x20003000):e(o,'lui',rd=r,imm=v)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    def ld(o,r,b,v,w=4):e(o,'load',rd=r,rs1=b,imm=v,width=w)
    def st(o,r,b,v,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    def mv(o,r,b):e(o,'mv',rd=r,rs2=b)
    def alu(o,op,r,a,b):e(o,op,rd=r,rs1=a,rs2=b)
    def imm(o,op,r,b,v):e(o,op,rd=r,rs1=b,imm=v)
    def br(o,op,a,b,t):e(o,op,rs1=a,rs2=b,target=addr(t))
    def bz(o,r,t):e(o,'beqz',rs1=r,target=addr(t))
    def bnz(o,r,t):e(o,'bnez',rs1=r,target=addr(t))
    def j(o,t):e(o,'jump',target=addr(t))
    def call(o,t,rd=1):e(o,'jal',rd=rd,target=t)
    def indirect(o):e(o,'call_indirect',rd=1,rs1=12)
    def ret(o):e(o,'jr',rs1=1)
    if part=='bit1':
        lui(0,15);ai(4,2,2,-16);ai(6,15,15,952+d);st(10,8,2,8);ld(12,8,15,100);st(14,1,2,12);li(16,14,1);ld(18,13,8,12,1)
        br(20,'bne',13,14,52);ld(24,15,15,124,1);li(28,14,4);br(30,'bne',14,15,40);mv(34,10,8);call(36,0x53d98+178*index)
        mv(40,10,8);ld(42,8,2,8);ld(44,1,2,12);ai(46,2,2,16);call(48,0x54c08+202*index,0)
        ld(52,1,2,12);ld(54,8,2,8);ai(56,2,2,16);ret(58)
        return s
    ai(0,2,2,-16);st(2,9,2,4);lui(4,9);ai(8,15,9,952+d);st(12,8,2,8);ld(14,8,15,88);st(16,1,2,12);st(18,18,2,0)
    br(20,'beq',8,0,618);ld(24,14,8,12,1);li(26,15,1);br(28,'bne',14,15,618);lui(32,15);ai(36,15,15,1300+d)
    ld(40,14,15,7,1);li(42,13,5);br(44,'beq',13,14,64);ld(48,14,15,7,1);li(50,13,3);br(52,'beq',13,14,64)
    ld(56,15,15,7,1);li(58,14,11);br(60,'bne',14,15,88)
    ld(64,8,2,8);lui(66,15);ld(70,1,2,12);ld(72,9,2,4);ld(74,18,2,0);ld(76,10,15,415+d,1);li(80,11,1);ai(82,2,2,16);call(84,0x4354a+140*index,0)
    ld(88,13,8,32,2);ai(90,14,0,1600);ld(94,15,9,952+d,1);alu(98,'div',14,14,13);ai(102,18,9,952+d);ai(106,15,15,1);imm(108,'andi',15,15,255)
    st(112,8,18,100);st(116,15,9,952+d,1);br(120,'blt',15,14,132);call(124,0x43edc+140*index);st(128,0,9,952+d,1)
    ld(132,14,8,14,1);li(134,15,7);br(136,'bne',14,15,204);ld(140,15,8,105,1);bz(144,15,198);ld(146,13,8,112,2);br(150,'bltu',13,15,192)
    ld(154,11,8,8,1);ai(156,15,0,67);st(160,15,8,23,1);ai(162,10,0,67);imm(166,'andi',13,13,255);li(170,12,0);call(172,0x6a7cc+484*index)
    mv(176,10,8);ld(178,8,2,8);ld(180,1,2,12);ld(182,9,2,4);ld(184,18,2,0);ai(186,2,2,16);call(188,0x55330+202*index,0)
    ai(192,13,13,1);st(194,13,8,112,2)
    if not index:li(198,15,5);st(200,15,8,98,1)
    else:
        # V1.40 replaces the six-byte constant store with a fourteen-byte call.
        ai(198,11,0,35);li(202,10,1)
        s[pc+204]=dict(op='jal',rd=1,target=0x43ef6)
        s[pc+208]=dict(op='store',rs2=10,rs1=8,imm=98,width=1)
    li(204,15,1);st(206,15,18,124,1);ld(210,14,8,24,1);li(212,15,3);br(214,'bne',14,15,376)
    call(218,0x433a8+140*index);imm(222,'andi',10,10,3);bnz(224,10,244)
    ai(226,15,0,39);st(230,15,8,10,1);ai(232,15,0,37);st(236,15,8,25,1);ai(238,15,0,38);j(242,266)
    li(244,15,1);br(246,'bne',10,15,364);ai(250,15,0,38);st(254,15,8,10,1);ai(256,15,0,37);st(260,15,8,25,1);ai(262,15,0,39);st(266,15,8,26,1)
    ld(268,14,8,14,1);lui(270,15);ld(274,9,15,415+d,1);li(278,15,1);br(280,'bne',14,15,498)
    ld(284,12,8,32,2);li(286,11,1);mv(288,10,9);call(290,0x43728+140*index)
    ld(294,15,8,53,1);imm(298,'andi',15,15,2);bz(300,15,512);ld(302,15,8,60,1);bz(306,15,512);ld(308,11,8,48);bz(310,11,512);ld(312,15,11,10,1);bz(314,15,512)
    li(316,15,2);st(318,15,8,52,1);li(322,12,6);ai(324,11,11,12);ai(326,10,8,54);e(330,'auipc',rd=1,imm=0x1ffab000);e(334,'jalr',rd=1,rs1=1,imm=-1728-320*index)
    ld(338,14,8,124,1);li(342,15,2);br(344,'bltu',15,14,520)
    mv(348,10,8);ld(350,8,2,8);ld(352,1,2,12);ld(354,9,2,4);ld(356,18,2,0);ai(358,2,2,16);call(360,0x54c08+202*index,0)
    ai(364,15,0,37);st(368,15,8,10,1);ai(370,15,0,39);j(374,236)
    li(376,13,2);ld(378,15,8,15,1);br(380,'bne',14,13,424);imm(384,'andi',14,15,1);bz(388,14,412);ai(390,14,0,37);st(394,14,8,10,1)
    imm(396,'andi',15,15,2);bz(398,15,418);ai(400,15,0,38);st(404,15,8,25,1);st(406,0,8,26,1);j(410,268)
    ai(412,15,0,38);st(416,15,8,10,1);ai(418,15,0,39);j(422,404)
    bz(424,15,460);imm(426,'andi',14,15,1);bz(430,14,444);ai(432,15,0,37);st(436,15,8,10,1);st(438,0,8,25,1);j(442,406)
    imm(444,'andi',15,15,2);bz(446,15,454);ai(448,15,0,38);j(452,436);ai(454,15,0,39);j(458,436)
    ld(460,15,8,25,1);ai(462,14,0,36);br(466,'bltu',14,15,476);ai(470,15,0,37);j(474,490);ai(476,15,15,1);imm(478,'andi',15,15,255);ai(482,14,0,39);br(486,'bltu',14,15,470)
    st(490,15,8,25,1);ld(492,15,8,25,1);st(494,15,8,10,1);j(496,406)
    li(498,11,14);li(500,10,1);call(502,0x43e6a+140*index);ld(506,12,8,32,2);alu(508,'add',12,12,10);j(510,286)
    li(512,15,1);st(514,15,8,52,1);j(518,338)
    ld(520,14,8,172);lui(524,15);ld(528,12,15,480+d);ld(532,15,14,10,1);bz(534,15,630);ld(536,15,14,9,1);ld(538,14,14,5,1);lui(540,13);ai(544,11,13,564+d)
    alu(548,'mul',15,15,14);ld(552,14,11,8,2);ai(554,9,13,564+d);ld(558,11,11,4);alu(560,'mul',15,15,14);ai(564,14,0,800);ai(568,15,15,400);alu(572,'divu',15,15,14)
    ld(576,14,8,148);alu(580,'add',14,14,15);mv(582,18,14);br(584,'bltu',14,15,592);br(588,'bltu',14,11,596);alu(592,'sub',18,14,11);indirect(596)
    alu(598,'sub',15,18,10);br(602,'bgeu',18,10,610);ld(606,14,9,4);alu(608,'add',15,15,14);ld(610,14,8,118,2);br(614,'bgeu',15,14,348)
    ld(618,1,2,12);ld(620,8,2,8);ld(622,9,2,4);ld(624,18,2,0);ai(626,2,2,16);ret(628)
    ld(630,9,8,152);indirect(634);br(636,'bltu',9,10,654);ld(640,15,8,118,2);alu(644,'sub',10,9,10);br(648,'bgeu',10,15,348);j(652,618)
    lui(654,15);ld(658,15,15,568+d);alu(662,'add',9,9,15);j(664,640)
    return s


def body(raw,part,index):
    k=PARTS.index(part);pc=STARTS[index][k];n=decode(raw,pc);s=specs(part,index)
    check(set(n)==set(s),'direct '+part+' boundaries')
    for p,f in s.items():init.g(n,p,'direct '+part+' operand '+hex(p-pc),**f)
    size,count=(666+8*index,229+2*index) if part=='bit0' else (60,23)
    check((len(raw),len(n),sha256(raw).hexdigest())==(size,count,HASHES[index][k]),'direct '+part+' identity')
    edges={};calls=[];tails=[]
    for p,v in n.items():
        op=v['op'];q=[p+v['size']]
        if op=='jr':check(v['rs1']==1,'direct return RA');q=[]
        elif op in ('beq','bne','blt','bltu','bgeu','beqz','bnez'):q.append(v['target'])
        elif op=='jump':q=[v['target']]
        elif op in ('jal','jalr','call_indirect'):
            if op=='jal':target=hex(v['target'])
            elif op=='call_indirect':target='freshU32['+hex(0x200031e0+80*index)+']'
            else:
                a=n[p-4];check(a['op']=='auipc' and a['rd']==v['rs1'],'direct adjacent PC pair');target=hex((p-4+a['imm']+v['imm'])&0xfffffffe)
            row={'pc':hex(p),'target':target}
            if v['rd']==0:tails.append(row);q=[]
            else:check(v['rd']==1,'direct link RA');calls.append(row)
        check(all(x in n for x in q),'direct closed '+part+' CFG');edges[p]=q
    seen=set();active=set();pathcounts={}
    def visit(p):
        check(p not in active,'direct '+part+' acyclic CFG')
        if p in seen:return pathcounts[p]
        active.add(p);count=sum(visit(q) for q in edges[p]) if edges[p] else 1
        active.remove(p);seen.add(p);pathcounts[p]=count;return count
    local_paths=visit(pc);check(seen==set(n),'direct all '+part+' nodes reachable')
    stores=[{'pc':hex(p),'base_register':v['rs1'],'source_register':v['rs2'],'offset':v['imm'],'bytes':v['width']} for p,v in n.items() if v['op']=='store']
    check((len(calls),len(tails))==((8+index,3) if part=='bit0' else (1,1)),'direct call/tail census')
    if part=='bit1':check(len(stores)==2 and all(v['base_register']==2 for v in stores),'direct bit1 frame stores only')
    return {'start':hex(pc),'end_exclusive':hex(pc+size),'bytes':size,'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),
      'conditional_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},'calls':calls,'tail_cuts':tails,'stores':stores,
      'syntactic_local_CFG_paths':local_paths,'complete_local_body':True,'local_CFG_acyclic':True,'path_feasibility_or_callee_return_proved':False}


def certificates(b,part,index):
    pc=int(b['start'],16);edges={int(p,16):[int(q,16) for q in qs] for p,qs in b['conditional_CFG'].items()}
    def walk(choices):
        out=[];p=pc
        while True:
            check(p not in out,'direct path acyclic');out.append(p);q=edges[p]
            if not q:break
            p=choices.get(p,q[0]);check(p in q,'direct valid selected edge')
        return out
    if part=='bit1':cases={'N12_not1':{20:52},'B124_not4_tail':{20:24,30:40},'B124_4_call_tail':{20:24,30:34}}
    else:
        gate={20:24,28:32,44:48,52:56,60:88,120:132,136:204,214:376,380:424,424:460,466:470,280:284,300:512,344:348}
        cases={'N_null':{20:618},'N12_not1':{20:24,28:618},'global5_tail':{20:24,28:32,44:64},
          'global3_tail':{20:24,28:32,44:48,52:64},'global11_tail':{20:24,28:32,44:48,52:56,60:64},
          'basic_tail':gate,'reset_B0':{**gate,120:124},'counter_underlimit':{**gate,136:140,144:146,150:192},
          'counter0':{**gate,136:140,144:198},'counter_atlimit_tail':{**gate,136:140,144:146,150:154},
          'selector_reply0':{**gate,214:218,224:226},'selector_reply1':{**gate,214:218,224:244,246:250},
          'selector_reply2or3':{**gate,214:218,224:244,246:364},
          'copy6_tail':{**gate,300:302,306:308,310:312,314:316},
          'nested_clock_nonzero':{**gate,344:520,534:536,584:588,588:596,602:610,614:618},
          'nested_clock_zero':{**gate,344:520,534:630,636:640,648:652},
          'nested_clock_zero_wrap':{**gate,344:520,534:630,636:654,648:348},
          'advance_wrap':{**gate,466:476,486:470},'delay_reply':{**gate,280:498}}
    selected={}
    for name,c in cases.items():
        choices={pc+offset(a,index,part):pc+offset(z,index,part) for a,z in c.items()}
        selected[name]=[p-pc for p in walk(choices)]
    # Every encoded edge has a syntactic entry-to-exit witness; no input solver.
    def prefix(goal):
        pending=[(pc,[pc])];seen=set()
        while pending:
            p,path=pending.pop()
            if p==goal:return path
            if p in seen:continue
            seen.add(p);pending.extend((q,path+[q]) for q in edges[p])
        raise RuntimeError('direct unreachable edge')
    witnesses=[]
    for p,qs in edges.items():
        for q in qs:
            path=prefix(p)+[q];r=q
            while edges[r]:r=edges[r][0];check(r not in path,'direct edgewitness acyclic');path.append(r)
            witnesses.append([v-pc for v in path])
    return {'selected_paths':selected,'all_edge_witness_count':len(witnesses),'all_edge_witness_sha256':sha256(json.dumps(witnesses,separators=(',',':')).encode()).hexdigest(),
      'scope':'syntactic local CFG witnesses only; branch feasibility, provider behavior and normalreturn remain conditional'}


def domains():
    # Positive U16 denominator only. The DIV-zero edge is explicitly left open.
    qcounts={}
    for d in range(1,65536):
        q=1600//d;qcounts[q]=qcounts.get(q,0)+1;check(0<=q<=1600,'direct positive divisor quotient')
    check(sum(qcounts.values())==65535 and qcounts[0]==63935,'direct positive divisor census')
    increments=[(v+1)&255 for v in range(256)];check(sorted(increments)==list(range(256)),'direct B0 increment including wrap')
    transitions=[]
    for x in range(256):
        v=37 if x<=36 else (x+1)&255;v=37 if v>39 else v
        transitions.append(v)
        check((v==0 if x==255 else 37<=v<=39),'direct byte25 transition including ff ->0')
    check(transitions[255]==0 and transitions[37:40]==[38,39,37],'direct cycle and ff discontinuity')
    max_product=255*255*65535
    check(max_product==4261413375 and max_product+400<2**32,'direct two byte onehalfword product no wrap')
    check((max_product+400)//800==5326767,'direct rounded duration maximum')
    return {'positive_U16_divisors':65535,'positive_division_quotient_range':[0,1600],'denominators_giving_quotient0':63935,
      'divisor0':'not locally guarded; no positive-divisor conclusion or runtimecondition asserted forzero',
      'B0_increment_domain':increments,'node25_transition_by_original_byte':transitions,'transition_ff':'ff increments tolow8zero andpasses<=39, so result0 not37',
      'duration_numerator_maximum':max_product+400,'duration_quotient_maximum':5326767,
      'duration_formula':'floor((U8[O9]*U8[O5]*U16[C8]+400)/800); no32bit overflow for these widths',
      'remaining_modular_arithmetic':'later wordaddition/subtractions wrap32; single modulus correction is encoded, not a global clock-range invariant'}


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[]
    for i,(data,pr) in enumerate(zip(carriers,parent['profiles'])):
        bodies={part:body(init.binding.take(data,STARTS[i][k],(666+8*i,60)[k]),part,i) for k,part in enumerate(PARTS)}
        certs={part:certificates(b,part,i) for part,b in bodies.items()};B=0x200033b8+80*i;C=0x20003234+80*i
        for part,bit in (('bit0','bit0'),('bit1','bit1')):check(pr['direct_callbacks'][bit]['conditional_installer_value']==bodies[part]['start'],'direct actual literal/body join')
        n={v['pc']:v for v in bodies['bit0']['instructions']};p=STARTS[i][0];o=lambda x:p+offset(x,i)
        check(bodies['bit0']['calls'][4+i]['target']=='0x20000332','direct copy original pair toRAM')
        check(n[o(112)]['imm']==100 and n[o(14)]['imm']==88,'direct original N B88 toB100 publication')
        stores=bodies['bit0']['stores'];check(all(v['base_register'] in (2,8,9,18) for v in stores),'direct classified store bases')
        check(all(v['offset'] not in (128,148) for v in stores if v['base_register'] in (8,18)),'direct no syntactic B128/B148 write in thesebodies')
        profiles.append({'label':pr['label'],'B':hex(B),'C':hex(C),'bodies':bodies,'CFG_certificates':certs,
          'provenance':{'handler':pr['handler']['start'],'candidate_installer_callback_values':{'B112':bodies['bit0']['start'],'B116':bodies['bit1']['start']},
            'binding':'conditional static literal-to-handler-slot-to-callee chain; actual invocation and slot preservation unproved'},
          'bit1_contract':{'N':'freshU32[B100]','dereference':'U8[N12] occurs without local N nullguard; valid readable N ofatleast13bytes required',
            'N12_not1':'restoreSP/S0/RA andreturn locally inheritedentryA0; not a fixedstatus',
            'N12_1':'if freshU8[B124]==4 call'+hex(0x53d98+178*i)+'(originalN); thenrestore andtail'+hex(0x54c08+202*i)+'(originalN)',
            'persistent_local_stores':0,'callee_reply':'optional callreply replaced byoriginalN fortail; finaltailreply/effects unknown'},
          'bit0_contract':{'N':'freshU32[B88]; nullguard before U8[N12]; N12!=1 returns withno nestedcalls',
            'minimum_direct_N_extent':176,'frame_bytes':16,'saved':['RA','S0','S1','S2'],
            'gates':'three separate freshU8['+hex(0x2000351b+80*i)+'] reads test5,then3,then11; no stablebyte assumption',
            'gated_tail':{'target':hex(0x4354a+140*i),'args':['freshU8['+hex(0x2000319f+80*i)+']',1],'restores_frame_beforetail':True},
            'publication_order':['readU16[N32]','readU8[B0]','signedDIV1600/denominator','incrementlow8 ofsavedB0byte','U32[B100]=originalN','U8[B0]=increment','if increment>=DIVreply call'+hex(0x43edc+140*i)+' thenB0=0'],
            'counter7':'if freshN14==7: nonzeroN105 andU16[N112]>=N105 ->N23=67; call'+hex(0x6a7cc+484*i)+'(67,U8[N8],0,low8(N112));tail'+hex(0x55330+202*i)+'(N). Otherwise incrementN112 onlywhen it wasbelow nonzeroN105, then writeN98',
            'profile_difference_N98':('constant5' if not i else 'low8reply of'+hex(0x43ef6)+'(1,35), requiring S0/S2/frame preservation'),
            'ongoing':'B124=1; selectN10/N25/N26 bytes37/38/39 orzero fromN24,N15, optional low2reply of'+hex(0x433a8+140*i)+'; node25 ff->0 edge is retained',
            'scheduling_call':{'target':hex(0x43728+140*i),'args':['freshgatebyte',1,'freshU16[N32] plus optionalreplyof'+hex(0x43e6a+140*i)+'(1,14)'],'no_positive_delay_or_return_guarantee':True},
            'copy_request':{'guards':['freshN53 bit1','freshN60 nonzero','freshU32[N48]=P nonnull','freshU8[P10] nonzero'],'write_before_call':'N52=2','target':'0x20000332','args':['N54','P12',6],
              'fallback':'failedguard storesN52=1','extent':'P readable throughbyte17 required forrequestedcopy; N54..59 destination; candidate reference copy not proof ofactualprovider or borrowedpointer retention'},
            'aftercopy':'freshU8[N124]<=2 tails'+hex(0x54c08+202*i)+'(N);otherwise loadO=U32[N172] anddereferenceU8[O10] withoutnullguard',
            'clock_service':{'pointer_source':hex(0x200031e0+80*i),'locally_null_guarded':False,'callsites':[hex(o(596)),hex(o(634))],'argument_note':'loadedA2 isfunction; no freshA0 setup immediatelybeforeeitherindirectcall; not a proved zeroargument ABI',
              'O10_nonzero':'duration=(U8[O9]*U8[O5]*U16[C8]+400)//800;T=wrap32(N148+duration);S2=T; ifT<duration orT>=U32[C4],S2=wrap32(T-U32[C4]); callloadedservice; compute wrap32(S2-reply),addfreshC4 ifS2<reply; compareunsignedwithfreshU16[N118]',
              'O10_zero':'S1=U32[N152];callloadedservice;ifS1<reply,S1=wrap32(S1+freshU32[C4]);comparewrap32(S1-reply)>=freshU16[N118]',
              'comparison':'true tails'+hex(0x54c08+202*i)+'(N);false returns locally; outerO validextent11 required; clock normalization/monotonicity/provider identity unproved'},
            'local_effect_limits':'stores reachframe,B0,B100,B124 andoriginalN fields; no local listnext/head/tail/free mutation. Object nonaliasing required to concludeotherglobal slotsunchanged'},
          'cross_event_lifetime':{'join':'bit0 publishesN toB100 before its first postgate nestedcall; later bit1 freshlyreadsB100',
            'unproved':['event order/actualscheduler','N retainedafterbit0 callees/tails','B100 preserved orreplaced byotherwriters','N minimumextent andnonaliasframe/globals','nestedcallees preserveS0/S1/S2/SP/frame/RA','actualcopy/clockprovider andretention','outerB128/B148 objectwriters']},
          'target_execution_or_emulation':False,'actual_installed_binding_proved':False})
    return {'schema':'TSL9-list-direct-callbacks-static-v1','profile':parent['profile'],'APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'integer_domains':domains(),
      'scope':'completebit0 666B/229i and674B/231i;completebit1 60B/23i each;1460neworiginalbytes/506operandguards;priorinstaller/setup/handlerproofs reused',
      'boundary':'candidate localbodies only; localCFG acyclic doesnotprove termination/return of callees/tails, eventreachability, pointerretention oractualbinding',
      'remaining':['tail54c08/54cd2,55330/553fa andoptional53d98/53e4a semantics','clockandcopyprovider actualbinding/retention','outerB128/B148 writers','setup latecall preservation/otherevents/listwriters'],
      'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    mutations=selected=witnesses=0
    for i,data in enumerate(carriers):
        for k,part in enumerate(PARTS):
            pc=STARTS[i][k];raw=init.binding.take(data,pc,(666+8*i,60)[k]);b=body(raw,part,i);cert=certificates(b,part,i);selected+=len(cert['selected_paths']);witnesses+=cert['all_edge_witness_count']
            for p,v in decode(raw,pc).items():
                at=p-pc;z=v['size'];buf=bytearray(raw);buf[at:at+z]=(int.from_bytes(buf[at:at+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
                try:body(buf,part,i)
                except RuntimeError as e:check(str(e).startswith('direct '+part+' operand '),'direct specifiedmutation '+str(e))
                else:raise RuntimeError('direct mutation escaped')
                mutations+=1
    check(mutations==506,'direct mutationcensus');domains()
    print('PASS:506 operand mutations rejected;1460 new originalbytes;'+str(selected)+' selectedCFG paths;'+str(witnesses)+' edge witnesses;positive65535divisors/byte domains')


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');o=p.parse_args()
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
    else:check(OUT.read_bytes()==output,'direct exactledger replay')
    print('PASS:handler/installer-to-directcallbacks;B88->B100->bit1 lifetime boundary;V140 extra service;exact ledger')
    print('PASS:NO target execution/emulation;actualproviders/eventorder/retention/setup-latepreservation UNPROVED')


if __name__=='__main__':main()
