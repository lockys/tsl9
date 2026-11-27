"""Offline small constructor consumer/caller/lookup and mapped RAM tail.

Original operands, graph, interval and bit-domain certificates only. No target
ISA, RAM/register machine, allocator/provider/copy/polling/FENCE.I execution.
"""
import argparse
import json
from collections import deque
from hashlib import sha256
from pathlib import Path
import check_v4160_list_common_body_static as previous

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
outer=previous.previous
OUT=Path(__file__).with_name('v4160-constructor-consumer-tail-static.json')
PARTS=('consumer','caller','lookup','ramtail')
STARTS=((0x6a2a8,0x679a2,0x5784a,0x200026ba),(0x6a3c0,0x67ae0,0x5798a,0x20002706))
SOURCES=((0x6a2a8,0x679a2,0x5784a,0x4292a),(0x6a3c0,0x67ae0,0x5798a,0x429b6))
SIZES=(222,44,24,250)
COUNTS=(80,19,9,93)
HASHES=(('92d99dfec5889ecb843ef31bc46869ff3e40806e0295cf241743689e4d8b518a','0f5dd80cb852a21e7e32ea836d97656596c5513b831393a7a5b9696bdd6d7744','b140a78d46168c0712c865a6898aaecd7d4fd0c2fd6bcb306149223a45063973','67120c2b2b0a0bb0ebfeb9d2310dda3e54cb6f67f6d0e62319839ce279eeda47'),
 ('e2d6ac5be18a919e37413b52c13d067a799a1e87b852f0b64ac8dc380ee0bab2','deed694c78f325c1a89c000908e99ffbdb550cbf8c4bb64a8418040a25e89eac','c33bd4712fa72e9a97153d15575654202cdcdc9b49cefe6f387c3a9d3e9c9aa8','2f1bdd416541a994d2a877e352d4100ebed85aa6e6fcba609d0342420c28e2d9'))


def specs(part,index):
    pc=STARTS[index][PARTS.index(part)];s={};d=80*index
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def ai(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def lui(o,r,v=0x20003000):e(o,'lui',rd=r,imm=v)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    def ld(o,r,b,v,w=4):e(o,'load',rd=r,rs1=b,imm=v,width=w)
    def st(o,r,b,v,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    def mv(o,r,b):e(o,'mv',rd=r,rs2=b)
    def imm(o,op,r,b,v):e(o,op,rd=r,rs1=b,imm=v)
    def alu(o,op,r,a,b):e(o,op,rd=r,rs1=a,rs2=b)
    def bz(o,r,t):e(o,'beqz',rs1=r,target=pc+t)
    def bnz(o,r,t):e(o,'bnez',rs1=r,target=pc+t)
    def br(o,op,a,b,t):e(o,op,rs1=a,rs2=b,target=pc+t)
    def j(o,t):e(o,'jump',target=pc+t)
    def call(o,t):e(o,'jal',rd=1,target=t)
    def ret(o):e(o,'jr',rs1=1)
    if part=='consumer':
        ai(0,2,2,-32)
        for o,r,v in ((2,8,24),(4,9,20),(6,19,12),(8,20,8),(10,21,4),(12,22,0),(14,1,28),(16,18,16)):st(o,r,2,v)
        for o,r,v in ((18,19,11),(20,22,12),(22,21,13),(24,20,14)):mv(o,r,v)
        lui(26,9);call(30,0x5784a+320*index);ai(34,15,9,952+d);ld(38,8,15,128);bz(42,10,218);ai(44,9,9,952+d);ld(48,15,9,132);mv(52,18,10);bnz(54,15,60)
        call(56,0x60856+234*index);bnz(60,8,110);ld(62,15,9,132);e(66,'call_indirect',rd=1,rs1=15);mv(68,8,10);li(70,10,3);bz(72,8,180)
        ld(74,15,8,77,1);imm(78,'andi',15,15,1);bz(80,15,200);ld(82,15,9,2,1);li(84,10,18);bz(86,15,180);lui(88,11);li(92,12,6);ai(94,11,11,1190+d)
        ai(98,10,8,78);e(102,'auipc',rd=1,imm=0x1ff96000);e(106,'jalr',rd=1,rs1=1,imm=36-280*index)
        ld(110,15,8,28);imm(112,'andi',14,15,2);bz(116,14,152);imm(118,'andi',14,15,14);li(122,13,8);br(124,'bne',14,13,212)
        ld(128,10,8,125,1);imm(132,'andi',15,15,-15);st(134,15,8,28);st(136,0,8,124,1);ai(140,15,0,255);br(144,'beq',10,15,152);call(148,0x43a14+140*index)
        li(152,15,-1);st(154,15,8,125,1);st(158,22,8,132,2);st(162,21,8,134,2);st(166,20,8,131,1);st(170,19,18,334,1);call(174,0x63578+234*index);li(178,10,0)
        for o,r,v in ((180,1,28),(182,8,24),(184,9,20),(186,18,16),(188,19,12),(190,20,8),(192,21,4),(194,22,0)):ld(o,r,2,v)
        ai(196,2,2,32);ret(198);lui(200,11);li(204,12,6);ai(206,11,11,1184+d);j(210,98);call(212,0x5f96c+234*index);j(216,152);li(218,10,2);j(220,180)
    elif part=='caller':
        ai(0,2,2,-32);st(2,1,2,28);st(4,8,2,24);mv(6,8,10);call(8,STARTS[index][0]);st(12,10,2,12,1);lui(14,10,0x2000);st(16,8,2,13,1)
        ai(18,12,2,12);imm(20,'srli',8,8,8);ai(22,10,10,92);li(26,11,3);st(28,8,2,14,1);call(30,0x6a70c+484*index);ld(34,1,2,28);ld(36,8,2,24);ld(38,10,2,12,1);ai(40,2,2,32);ret(42)
    elif part=='lookup':
        lui(0,15);ld(4,15,15,1108+d);bnz(8,15,14);mv(10,10,15);ret(12);ld(14,14,15,8,2);br(16,'beq',14,10,10);ld(20,15,15,0);j(22,8)
    else:
        ai(0,2,2,-16);st(2,8,2,8);st(4,1,2,12);lui(6,8);st(10,9,2,4);ld(12,14,8,1340+d);bnz(16,10,126);mv(18,15,11);ld(20,13,14,100);bnz(22,13,20)
        lui(24,9);ai(28,9,9,1300+d);mv(32,10,15);mv(34,11,12);st(36,0,9,2,1);e(40,'auipc',rd=1,imm=0xe0061000);e(44,'jalr',rd=1,rs1=1,imm=1068+158*index)
        lui(48,15);ld(52,15,15,1288+d);lui(56,13,0x800000);ld(60,14,15,0);alu(62,'or',14,14,13);st(64,14,15,0);ld(66,14,15,44);imm(68,'andi',14,14,-4);st(70,14,15,44)
        ld(72,15,8,1340+d);st(76,0,9,5,1);st(80,0,9,1,1);li(84,14,2);st(86,14,15,0);ld(88,13,8,1340+d);lui(92,15);ai(96,15,15,1300+d)
        ld(100,14,15,2,1);imm(102,'andi',14,14,1);bnz(104,14,116);ld(106,14,15,3,1);imm(108,'andi',14,14,1);bnz(110,14,116);ld(112,14,13,100);bnz(114,14,100)
        ld(116,1,2,12);ld(118,8,2,8);ld(120,9,2,4);ai(122,2,2,16);ret(124);li(126,15,3);br(128,'bne',10,15,158)
        lui(132,15);ld(136,15,15,1288+d);lui(140,13,0x800000);ld(144,14,15,0);alu(146,'or',14,14,13);st(148,14,15,0);ld(150,14,15,44);imm(152,'andi',14,14,-4);st(154,14,15,44);j(156,88)
        li(158,15,1);br(160,'bne',10,15,88);ld(164,13,14,12);lui(166,15,0xffffe000);ai(168,15,15,-1);alu(170,'and',15,15,13);st(172,15,14,12);e(174,'fence.i')
        ld(178,15,8,1340+d);lui(182,14,0x2000);ai(184,12,0,-128);st(188,14,15,8);lui(190,14);ai(194,14,14,1300+d);st(198,12,14,4,1);lui(200,14);ld(204,12,14,1288+d)
        ld(208,14,12,0);imm(210,'srli',14,14,12);imm(212,'andi',14,14,3);bnz(214,14,226);ai(216,14,0,406);st(220,14,15,100);st(222,13,15,12);j(224,88)
        ld(226,14,12,0);li(228,12,2);imm(230,'srli',14,14,12);imm(232,'andi',14,14,3);br(234,'bne',14,12,244);ai(238,14,0,1086);j(242,220);ai(244,14,0,446);j(248,220)
    return s


def body(raw,part,index):
    k=PARTS.index(part);pc=STARTS[index][k]
    if part=='ramtail':check(raw[174:178]==bytes.fromhex('0f100000'),'small ramtail fencebytes')
    n=decode(raw,pc);s=specs(part,index);check(set(n)==set(s),'small '+part+' boundaries')
    for p,f in s.items():init.g(n,p,'small '+part+' operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[k],HASHES[index][k]),'small '+part+' identity')
    edges={};calls=[]
    for p,v in n.items():
        op=v['op'];q=[p+v['size']]
        if op=='jr':check(v['rs1']==1,'small RET RA');q=[]
        elif op in ('beqz','bnez','beq','bne'):q.append(v['target'])
        elif op=='jump':q=[v['target']]
        elif op in ('jal','jalr','call_indirect'):
            if op=='jal':target=hex(v['target'])
            elif op=='call_indirect':target='freshU32[B132]'
            else:
                a=n[p-4];check(a['op']=='auipc' and a['rd']==v['rs1'],'small adjacentPCpair');target=hex((p-4+a['imm']+v['imm'])&0xfffffffe)
            check(v['rd']==1,'small calllinkRA');calls.append({'pc':p,'target':target})
        check(all(x in n for x in q),'small closed '+part+' CFG');edges[p]=q
    groups=previous.sccs(edges);cycles=[[x-pc for x in g] for g in groups if len(g)>1 or g[0] in edges[g[0]]]
    expected=[] if k<2 else [[8,14,16,20,22]] if k==2 else [[20,22],list(range(100,116,2))]
    check(cycles==expected,'small exact '+part+' cyclicSCCs')
    seen=set();pending=[pc]
    while pending:
        p=pending.pop()
        if p in seen:continue
        seen.add(p);pending.extend(edges[p])
    check(seen==set(n),'small fullsyntacticreachability '+part)
    stores=[{'pc':p,'base':v['rs1'],'offset':v['imm'],'source':v['rs2'],'bytes':v['width']} for p,v in n.items() if v['op']=='store']
    check((len(stores),len(calls))==((15,7),(5,2),(0,0),(16,1))[k],'small stores/calls census '+part)
    return {'start':pc,'end_exclusive':pc+SIZES[k],'source':SOURCES[index][k],'bytes':SIZES[k],'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),
      'local_CFG':edges,'cyclic_SCC_offsets':cycles,'calls':calls,'stores':stores,'complete_local_body':True,'local_CFG_acyclic':k<2,'finite_return_proved':False}


def certificates(b,part):
    pc=b['start'];e=b['local_CFG'];ends={p for p,qs in e.items() if not qs}
    def path(a,z):
        q=deque([(a,[a])]);seen=set()
        while q:
            p,s=q.popleft()
            if p==z:return s
            if p in seen:continue
            seen.add(p);q.extend((v,s+[v]) for v in e[p])
        return None
    def finish(p):
        xs=[x for q in sorted(ends) if (x:=path(p,q)) is not None];check(bool(xs),'small edge exitwalk');return min(xs,key=len)
    witnesses=[]
    for p,qs in e.items():
        for q in qs:
            s=path(pc,p)+[q]+finish(q)[1:];check(all(z in e[a] for a,z in zip(s,s[1:])),'small validedgewalk');witnesses.append([a-pc for a in s])
    points=({'consumer':[30,56,66,106,128,148,174,212,218,70,84],'caller':[30],'lookup':[10,14,20],'ramtail':[44,126,164,174,216,238,244]}[part])
    walks={hex(o):[a-pc for a in path(pc,pc+o)+finish(pc+o)[1:]] for o in points}
    return {'selected_syntactic_walks':walks,'all_edge_witness_count':len(witnesses),'all_edge_witness_sha256':sha256(json.dumps(witnesses,separators=(',',':')).encode()).hexdigest(),
      'scope':'syntactic CFG only; consumerinfeasibleblock separatelyproved; lookup/tail polling exits andcallee returns notguaranteed'}


def infeasible(b):
    pc=b['start'];e=b['local_CFG'];n={v['pc']:v for v in b['instructions']};pred={p:set() for p in e}
    for p,qs in e.items():
        for q in qs:pred[q].add(p)
    check(pred[pc+128]=={pc+124},'small onlyincoming cancellationblock')
    check([p-pc for p,v in n.items() if 110<=p-pc<=124 and v.get('rd')==15]==[110],'small sameA5snapshot acrossmaskgates')
    impossible=[]
    for low in range(16):
        if low&2 and low&14==8:impossible.append(low)
    check(not impossible,'small incompatible maskpredicates all16 lowbits')
    pruned={p:list(q) for p,q in e.items()};pruned[pc+124].remove(pc+128)
    seen=set();pending=[pc]
    while pending:
        p=pending.pop()
        if p in seen:continue
        seen.add(p);pending.extend(pruned[p])
    excluded=sorted(p-pc for p in set(e)-seen);check(excluded==[128,132,134,136,140,144,148],'small exact entryinfeasible encodednodes')
    return {'low4_cases':16,'satisfying_patterns':[],'predicate':'(sameU32snapshot&2)!=0 AND(sameU32snapshot&14)==8',
      'pruned_edge':[124,128],'encoded_nodes_excluded_from_entry':excluded,'excluded_effects':['N28maskclear','N124zero','43a14/43aa0call'],
      'encoded_CFG_retained':True,'scope':'ordinarydecodedGPRsemantics/fromthisfunctionentry only; externalmidfunctionentry/faults/codepatches notexcluded'}


def domains():
    check(all(not(x&2 and x&14==8) for x in range(16)),'small impossible16cases')
    for x in range(65536):
        check((x&255)|((x>>8)<<8)==x,'small callerlow16payloadbyte split')
    return {'mask_low4_cases':16,'infeasiblemask_solutions':0,'caller_low16_cases':65536,'local_status_values':[0,2,3,18],
      'status_meaning_or_actualsuccess_proved':False,'packet_extent_or_input_domain_proved':False}


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[]
    for i,(data,pr) in enumerate(zip(carriers,parent['profiles'])):
        bodies={part:body(init.binding.take(data,SOURCES[i][k],SIZES[k]),part,i) for k,part in enumerate(PARTS)};B=0x200033b8+80*i
        certs={part:certificates(b,part) for part,b in bodies.items()};imp=infeasible(bodies['consumer']);mapping=init.binding.profile(data,pr['label']);first={k:int(v,16) for k,v in mapping['first_copy'].items()}
        pc=STARTS[i][3];src=SOURCES[i][3];check(first['destination']<=pc and pc+250<=int(mapping['first_copy_end_exclusive'],16) and first['source']+pc-first['destination']==src,'small fullRAMtail affine startupsource')
        check(pr['body']['tail_cuts'][0]['target']==pc and bodies['ramtail']['calls'][0]['target']==hex(0x63b0e+234*i),'small common->RAMtail->flash exactjoin')
        ctor=outer.body(init.binding.take(data,outer.STARTS[i][0],148),'outer128',i);publisher=outer.body(init.binding.take(data,outer.STARTS[i][3],68),'publish128',i)
        cn={v['pc']:v for v in bodies['consumer']['instructions']};cp=STARTS[i][0]
        check([v['target'] for v in bodies['consumer']['calls']]==[hex(STARTS[i][2]),publisher['start'],'freshU32[B132]','0x20000332',hex(0x43a14+140*i),hex(0x63578+234*i),hex(0x5f96c+234*i)],'small exactconsumer calleejoins')
        check(bodies['caller']['calls'][0]['target']==hex(cp) and bodies['caller']['calls'][1]['target']==hex(0x6a70c+484*i),'small caller joinedwithnonuniformservice delta')
        check(all(v['offset']+v['bytes']<=77 or v['offset']>77 for v in ctor['stores'] if v['base_register']==8),'small constructor excludes77 explicitwrites')
        profiles.append({'label':pr['label'],'B':hex(B),'bodies':bodies,'CFG_certificates':certs,'consumer_infeasible_branch':imp,
          'reused_constructor':{k:ctor[k] for k in ('start','bytes','sha256')},'reused_publisher':{k:publisher[k] for k in ('start','bytes','sha256')},
          'consumer_contract':{'frame_bytes':32,'saved':['RA','S0','S1','S2','S3','S4','S5','S6'],'lookup_call':'firstcallee receivesoriginalA0; remainingentryA1..A4savedbeforecall',
            'old_outer':'freshU32[B128] sampledafterlookup butBEFORE lookupnulltest/optionalpublisher; S0snapshot usedafterpublisher withoutreloadingouterword',
            'lookup_null':'return2, afteralreadyreadingouterword','initial_function_zero':'callpublisher,which maycallfullsetup beforepublishing B132; allreturns/preservation required',
            'constructor_call':'ifoldsnapshot0, freshlyreloadB132 thenJALR withoutfreshnullguard; ifoldnonzero skipconstructor andnewobjectcopyblock',
            'conditional_constructor_target':ctor['start'],'constructor_entry_A0':'lookupreply ifpublisher skipped, otherwisepublisherreply; knownconstructor resetsits ownallocationrequestargs',
            'constructor_null':'return3; no rollback/slotclear locally','new_object':'freshU8[N77]bit0clear ->sourceB232; set ->freshU8[B2]==0 return18, otherwise sourceB238',
            'copy_request':{'target':'0x20000332','args':['N78','B232 orB238',6],'requires_destination_through':84,'physicalcopy/retention_proved':False},
            'conditional_N77_zero':'ifmatchingzero-fill232,validnonaliasN/frame/globals/table,nointerference andconstructorpreservation, ctor excludes77writes -> N77=0 onreturn. Actualfill/providerbinding remainsunproved',
            'word28_branch':'onefreshU32[N28];bit1clear goescommonwrites;bit1set necessarilycalls5f96c/5fa56 thencommonwrites; encodedcancelblock infeasiblefromentry',
            'common_writes':{'N125':255,'N132_half':'low16(entryA2)','N134_half':'low16(entryA3)','N131_byte':'low8(entryA4)','lookup_record334_byte':'low8(entryA1)'},
            'last_service':{'target':hex(0x63578+234*i),'A0':'locallyinherited predecessor/calleevalue, notexplicitN','reply':'discarded; localA0=0 afterrequirednormalreturn'},
            'minimum_fixed_extents':{'N':136,'lookup_record':335},'final_stores_preserved_across_lastcallee_proved':False,'actual_installedbinding_or_lifetime_proved':False},
          'lookup_contract':{'head_slot':hex(B+156),'node_next_word':0,'node_key_unsigned_halfword':8,'comparison':'fullentryA0 vsU16[node8], no entrymask',
            'local_writes':'GPR A0/A4/A5 only; no stores/frame/calls','return':'firstmatchednode or0 atnull; pointervalidity/acyclicity/chainbound unproved',
            'minimum_node_extent':10,'high16_nonzero_key':'no U16match; nullresult requiresactual traversal termination'},
          'caller_contract':{'frame_bytes':32,'saved':['RA','S0'],'payload_before_second_service':['SP12=low8consumerreply','SP13=low8entryA0','SP14=bits8..15entryA0'],
            'second_request':{'target':hex(0x6a70c+484*i),'args':[0x205c,3,'SP12'],'packet_meaning_or_pointer_nonretention_proved':False},
            'return':'freshU8[SP12] aftersecondcallee; equalspriorstatusbyte onlyifcallee/framepreservation coversit','after_return_stack_pointer_escape_proved':False},
          'RAM_source_mapping':{'candidate_first_copy':mapping['first_copy'],'first_copy_end_exclusive':mapping['first_copy_end_exclusive'],'RAM_entry':hex(pc),'flash_source':hex(src),'fullbytes':250,
            'proof':'replayed startupoperands/helper contract pluscompleteinterval containment; no actualstartupcopy/installedRAM assertion'},
          'ramtail_contract':{'frame_bytes':16,'saved':['RA','S0','S1'],'C':hex(0x20003514+80*i),'initial_H0':'freshU32['+hex(0x2000353c+80*i)+'] beforeentrymodebranch; noHnullguard',
            'common_entry':'previouscommonbody suppliesA0=0,A1=ORflags,A2=freshN17',
            'mode0':'captureentryA1 inA5; pollH0[100] untilzero; C2=0; flashcallee(A0=entryA1,A1=entryA2,A2=entryA2 stilllocally)',
            'flash_callee':hex(0x63b0e+234*i),'postcall_mode0':'freshR from'+hex(0x20003508+80*i)+';R0OR00800000,R44AND-4;freshH1,C5=0,C1=0,H1[0]=2',
            'mode3':'no nestedcall; R0bit23set/R44low2clear thenfinalpoll','mode1':'H0[12]clearbit13,FENCE.I encodingonly; freshH1[8]=8192,C4=128; twofreshR0bits12..13 reads choose406(first0),1086(second2),or446;H1[100]=duration,H1[12]=savedoriginalH0[12]',
            'other_nonzero_modes':'no specialeffects/call, enterfinalpoll; localA0retainsentrymode',
            'finalpoll':'freshH2 globalpointer loadedonce at+58; eachloop readsfreshC2bit0 thenC3bit0 thenH2[100]; exitifC2bit0orC3bit0orH2word0, otherwisebackedge',
            'snapshots':'H0,H1,H2 maydiffer; noglobalpointer reloadinsidepolls; no localfinitebound/backoff/progress proof',
            'return':'mode0 calleeA0 afterfinitepoll/requiredreturn; othermodes locallyentryA0; notfixedsuccess',
            'minimum_fixed_extents':{'H':104,'R':48,'C':6},'FENCE_I_executed':False,'MMIO_or_physicalbehavior_proved':False,'retention_and_actualbinding_proved':False},
          'target_execution_or_emulation':False})
    return {'schema':'TSL9-constructor-consumer-tail-static-v1','profile':parent['profile'],'APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'integer_domains':domains(),
      'scope':'fullconsumer222B/80i,caller44B/19i,lookup24B/9i,mappedRAMtail250B/93i eachprofile;1080neworiginalbytes/402guards;priorconstructor/publisher/common/startup proofs reused',
      'boundary':'conditionalstatic body/graph/arg/mapping contracts; actualconstructorinvocation, poll/helperreturns, installedbinding andlifetime unproved',
      'remaining':['larger B152consumer69a22/69b3a','callback55480/5555e plus13-entry tables/versiondifferences','helpers63578/63662,5f96c/5fa56,63b0e/63bf8,6a70c/6a8f0','lookuphead/nodewriters/pollprogress/actualprovider/retention'],
      'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    mutations=walks=edges=0
    for i,data in enumerate(carriers):
        for k,part in enumerate(PARTS):
            raw=init.binding.take(data,SOURCES[i][k],SIZES[k]);b=body(raw,part,i);cert=certificates(b,part);walks+=len(cert['selected_syntactic_walks']);edges+=cert['all_edge_witness_count']
            if part=='consumer':infeasible(b)
            for p,v in decode(raw,STARTS[i][k]).items():
                at=p-STARTS[i][k];z=v['size'];buf=bytearray(raw);buf[at:at+z]=(int.from_bytes(buf[at:at+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
                try:body(buf,part,i)
                except RuntimeError as ex:check(str(ex).startswith('small '+part+' operand ') or part=='ramtail' and at==174 and str(ex)=='small ramtail fencebytes','small specifiedmutation '+str(ex))
                else:raise RuntimeError('small mutationescaped')
                mutations+=1
    check(mutations==402,'small mutationcensus');domains()
    print('PASS:402 operand/encoding mutations rejected;1080 new originalbytes;'+str(walks)+' selectedCFG walks;'+str(edges)+' edge witnesses;16 maskcases/65536 payloadcases')


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');o=p.parse_args()
    image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes();check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK identity')
    carriers=[]
    for label,folder,tail,z,digest in init.binding.PROFILES:
        data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidate identity '+label);carriers.append(data)
    raw_hex=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,raw_hex,sparse.parser());ledger=derive(image,carriers,header,coverage)
    ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers);output=(json.dumps(ledger,indent=1,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'small exactledger replay')
    print('PASS:consumer/caller/lookup/constructor/publisher joins;infeasibleentry branch;common->mappedRAMtail->flash;exact ledger')
    print('PASS:NO target execution/emulation;poll/helperreturn/installedbinding/pointerretention UNPROVED')


if __name__=='__main__':main()
