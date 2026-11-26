"""Complete first-role initializer fields/selector and bounded late-call join.

Only original operands/CFG and closed field/range identities. No target ISA,
register machine, initializer, callback, mutable object, MMIO or device runner.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_first_role_gate_static as previous

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-role-initializer-fields-static.json')
DETAILS=((0x43e24,574,305,(0x64298,0x57ac4,0x63704),0x5e758,
 '8bb20f81018416194e2b8739b4917789870c2bc74168b281d044f008fcc03a24','411a51dc3699acd615c4acc9014bd9eb950e605db32be01ad88b1fcb24827c76'),
 (0x43eb0,654,320,(0x64382,0x57c04,0x637ee),0x5e842,
 '7e9bb137afc77b7c1a4b6b5cef3fbc0d3c3122dcf426fe0946957535414ec251','904be4acee55f023aa7428b7dbc079c2f3c90af66050c60b299b79a70f169f6c'))
THRESHOLDS=(20,30,50,75,100,150,250)


def specs(role,index):
    d=previous.DETAILS[index];selector,half,version,calls,tail,*_=DETAILS[index]
    pc=d['initialize'] if role=='initializer' else selector
    s=dict(previous.specs('initialize',index)[1]) if role=='initializer' else {}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def imm(o,op,r,b,v):e(o,op,rd=r,rs1=b,imm=v)
    def lui(o,r,v):e(o,'lui',rd=r,imm=v)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    def load(o,r,b,v,w=4,**extra):e(o,'load',rd=r,rs1=b,imm=v,width=w,**extra)
    def store(o,r,b,v,w=4,**extra):e(o,'store',rs2=r,rs1=b,imm=v,width=w,**extra)
    def sh(o,r,b,v):store(o,r,b,v,2,mnemonic='qk.c.sh')
    def binary(o,op,r,a,b):e(o,op,rd=r,rs1=a,rs2=b)
    if role=='selector':
        lui(0,15,0x20003000);load(4,15,15,half,2)
        for o,limit,out in ((8,20,7),(16,30,6),(24,50,5),(34,75,4),(44,100,3),(54,150,2)):
            if limit<=31:li(o,14,limit)
            else:imm(o,'addi',14,0,limit)
            li(o+(2 if limit<=31 else 4),10,out)
            e(o+(4 if limit<=31 else 6),'bgeu',rs1=14,rs2=15,target=pc+68)
        imm(64,'sltiu',10,15,251);e(68,'jr',rs1=1)
        return pc,s
    lui(62,15,0x07d70000);imm(66,'addi',8,9,d['base']);imm(70,'addi',15,15,13);store(72,15,8,20)
    lui(74,15,0x0d0db000);imm(78,'addi',15,15,version);store(82,15,8,24)
    lui(84,15,0x07d7b000);imm(88,'addi',15,15,version);store(92,15,8,28)
    lui(94,15,0xffffb000);imm(96,'addi',15,15,version);li(100,14,31);sh(102,15,8,32);store(104,14,8,224)
    li(108,15,0);load(110,14,8,208);store(114,15,8,228);lui(118,15,0x072d8000);imm(122,'addi',15,15,-1537)
    binary(126,'or',14,14,15);load(128,15,8,212);lui(132,13,0x2000);imm(134,'addi',13,13,-1122)
    lui(138,18,0x20003000);binary(142,'or',15,15,13);imm(144,'addi',18,18,d['ctx']+80)
    store(148,15,8,212);store(152,15,8,220);load(156,15,18,14,1);store(160,14,8,208);store(164,14,8,216)
    store(168,15,8,193,1);store(172,15,8,201,1);lui(176,15,0xffffe000);imm(178,'addi',15,15,-1)
    store(180,15,8,262,2);store(184,15,8,264,2);li(188,15,31);store(190,15,8,266,1)
    lui(194,15,4096);imm(196,'addi',15,15,-241);sh(200,15,8,58);sh(202,15,8,60);store(204,0,8,57,1)
    e(208,'jal',rd=1,target=selector);imm(212,'addi',15,0,460);store(216,15,8,126,2);li(220,15,1);store(222,15,8,63,1)
    load(226,15,18,4,2);load(230,14,18,16,2);store(234,10,8,3,1,mnemonic='qk.c.sb');imm(236,'srli',15,15,10)
    store(238,15,8,137,1);li(242,15,3);store(244,15,8,66,2);lui(248,15,0x06071000);imm(252,'addi',15,15,1088)
    store(256,15,8,72);store(258,0,8,68);imm(262,'addi',13,0,251);imm(266,'addi',15,9,d['base'])
    e(270,'bgeu',rs1=13,rs2=14,target=pc+278);imm(274,'addi',14,0,251);imm(278,'slli',11,14,16)
    sh(282,14,15,42);sh(284,14,15,46);load(286,14,15,60,1);imm(290,'srli',11,11,16);imm(292,'addi',12,11,14)
    imm(296,'andi',14,14,4);e(298,'beqz',rs1=14,target=pc+414);imm(300,'addi',14,11,138);imm(304,'slli',14,14,3)
    load(306,13,15,61,1);imm(310,'slli',14,14,16);imm(312,'srli',14,14,16);sh(314,14,15,44)
    imm(316,'andi',13,13,4);e(318,'beqz',rs1=13,target=pc+420);imm(320,'addi',13,11,138);imm(324,'slli',13,13,3)
    imm(326,'slli',13,13,16);imm(328,'srli',13,13,16);sh(330,13,15,48);li(332,10,27);imm(334,'addi',9,9,d['base'])
    e(338,'mv',rd=13,rs2=11);e(340,'bgeu',rs1=11,rs2=10,target=pc+346);li(344,13,27);sh(346,13,9,34)
    imm(348,'addi',11,0,328);e(352,'mv',rd=13,rs2=14);e(354,'bgeu',rs1=14,rs2=11,target=pc+362)
    imm(358,'addi',13,0,328);imm(362,'addi',14,0,460);store(366,14,15,64,2);lui(370,14,0x160000)
    imm(374,'slli',12,12,3);imm(376,'addi',14,14,-1792);sh(380,13,15,36);sh(382,12,15,38);sh(384,13,15,40);store(386,14,15,52)
    for o,t in zip((388,392,396),calls):e(o,'jal',rd=1,target=t)
    for o,r,v in ((400,8,8),(402,1,12),(404,9,4),(406,18,0)):load(o,r,2,v)
    imm(408,'addi',2,2,16);e(410,'jal',rd=0,target=tail)
    imm(414,'slli',14,12,3);e(418,'jump',target=pc+306);imm(420,'slli',13,12,3);e(424,'jump',target=pc+326)
    return pc,s


def body(raw,role,index):
    pc,s=specs(role,index);n=decode(raw,pc)
    check(set(n)==set(s),'fields '+role+' boundaries')
    for p,f in s.items():init.g(n,p,'fields '+role+' operand '+hex(p-pc),**f)
    size,count,digest=(426,138,DETAILS[index][-2]) if role=='initializer' else (70,22,DETAILS[index][-1])
    check((len(raw),len(n),sha256(raw).hexdigest())==(size,count,digest),'fields '+role+' identity')
    # Pin standard unsigned load encodings as well as the conditional Xwchc forms.
    offsets=(156,226,230,286,306) if role=='initializer' else (4,)
    for off in offsets:
        d=n[pc+off];w=int.from_bytes(raw[off:off+4],'little')
        check((w>>12&7)=={1:4,2:5}[d['width']],'fields unsigned source load')
    edges={};cuts=[];calls=[]
    for p,d in n.items():
        if d['op']=='jr':q=[]
        elif d['op']=='jump' or d['op']=='jal' and d['rd']==0:q=[d['target']]
        elif d['op'] in ('bgeu','beqz'):q=[p+d['size'],d['target']]
        else:q=[p+d['size']]
        for v in q:
            if v not in n:check(role=='initializer' and p==pc+410,'fields sole explicit tail');cuts.append([hex(p),hex(v)])
        edges[p]=q
        if d['op'] in ('jal','jalr') and d['rd']==1:calls.append({'pc':hex(p),'target':hex(d['target']) if 'target' in d else '0x2000039c','link':hex(p+d['size'])})
    visited=set();active=set()
    def visit(p):
        check(p not in active,'fields local CFG acyclic')
        if p in visited or p not in n:return
        visited.add(p);active.add(p)
        for q in edges[p]:visit(q)
        active.remove(p)
    visit(pc);check(visited==set(n),'fields all local nodes reachable')
    stores=[d for d in n.values() if d['op']=='store']
    if role=='selector':
        check(not stores and not calls,'fields selector leaf no stores/calls')
        check(sorted({d['rd'] for d in n.values() if d.get('rd',0)})==[10,14,15],'fields selector GPR preservation')
    else:
        check(len(calls)==7 and len(cuts)==1 and len(stores)==41 and not any(d['op']=='jr' for d in n.values()),'fields initializer seven calls/41stores and tail no RET')
        check([p-pc for p,d in n.items() if d.get('rd')==2]==[0,408],'fields initializer SP definition census')
    return {'role':role,'start':hex(pc),'end_exclusive':hex(pc+size),'bytes':size,'sha256':digest,'instructions':list(n.values()),
        'normal_return_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},'tail_cuts':cuts,'calls':calls,'store_count':len(stores),
        'complete_function_or_tail_body':True,'transitive_late_calls_closed':False}


def selected_prefix(b,pc,h):
    k=min(h,251)
    ei={int(p,16):[int(q,16) for q in qs] for p,qs in b['normal_return_CFG'].items()}
    choices={pc+270:pc+(278 if h<=251 else 274),pc+298:pc+300,pc+318:pc+320,pc+340:pc+(346 if k>=27 else 344),pc+354:pc+362}
    return previous.previous.chain(ei,pc,choices,pc+388)


def selector_algebra(h):return sum(h<=limit for limit in THRESHOLDS)


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[]
    for i,(data,prior,d) in enumerate(zip(carriers,parent['profiles'],previous.DETAILS)):
        pc=d['initialize'];b=body(init.binding.take(data,pc,426),'initializer',i)
        selector=body(init.binding.take(data,DETAILS[i][0],70),'selector',i)
        check(prior['zero_case']['prefix_end_exclusive']==hex(pc+62),'fields original prefix join')
        base=0x20003000+d['base'];state=0x20003000+d['ctx']+80;gate=0x20003000+d['ctx']+3
        check(0x20003000+DETAILS[i][1]==state+82,'fields selector reads copied config halfword+10')
        check(previous.previous.origin.separated(base,296,state,96) and previous.previous.origin.separated(base+3,1,gate,1),'fields object/source/context gate distinct')
        n={row['pc']:row for row in b['instructions']};accesses=[]
        for p,row in n.items():
            if row['op']!='store':continue
            off=p-pc;r=row['rs1'];width=row['width'];imm=row['imm']
            if r==2:address='initializerSP+'+str(imm)
            elif off==28:address=base+300
            elif off==58:address=gate
            elif r==8 and off>=62 or r==15 and off>=266 or r==9 and off>=334:address=base+imm
            else:raise RuntimeError('fields unclassified store '+hex(p))
            if isinstance(address,int) and off>=62:check(base<=address and address+width<=base+296,'fields suffix object store extent')
            accesses.append({'pc':hex(p),'bytes':width,'address':hex(address) if isinstance(address,int) else address})
        protected=[(0x20003000+d['ctx']+1,1),(0x20003000+d['ctx']+2,1),(gate,1),
            (previous.previous.layout.T,4*212),(previous.previous.layout.A+8,16),(0x200040a6,1),(0x20004184,1)]
        for p,width in ((base,296),(base+296,12)):
            for q,z in protected:check(previous.previous.origin.separated(p,width,q,z),'fields object/direct globals exclude live table/task/node/gate')
        # The only call between the first-role prefix and late-call cut is this
        # selector leaf; all its stores/clobbers were exhaustively classified.
        calls_before=[c['target'] for c in b['calls'] if pc+62<=int(c['pc'],16)<pc+388]
        check(calls_before==[selector['start']],'fields suffix single closed selector call before cut')
        paths=[selected_prefix(b,pc,k) for k in (0,27,252)]
        check(all(hex(pc+414) not in p and hex(pc+420) not in p and hex(pc+358) not in p for p in paths),'fields own0f0f flags avoid fallback stride branches')
        profiles.append({'label':prior['label'],'initializer':b,'selector':selector,'classified_direct_stores':accesses,
            'object_base':hex(base),'context_gate_byte':hex(gate),'object_selector_byte':hex(base+3),'selector_input_halfword':hex(state+82),
            'conditional_selector_h1000_output':0,'conditional_ctx_gate_at_cut':5,'conditional_count_at_cut':6,
            'fresh_source_reads':{'record_count_byte':hex(state+14),'word4_low_halfword':hex(state+4),'size_halfword':hex(state+16)},
            'selected_prefix_examples':paths,'cut_before_first_late_call':b['calls'][4],
            'conditional_first_late_arguments':{'A0':27,'A1':328,'A2':'8*(k+14)','A3':'8*(k+138)'},
            'late_call_targets':[hex(t) for t in DETAILS[i][3]],'unclosed_tail':hex(DETAILS[i][4]),'actual_installed_binding_proved':False})
    return {'schema':'TSL9-role-initializer-fields-static-v1','profile':parent['profile'],'APP_sha256':sha256(image).hexdigest(),
        'scope':'two complete426B/138instruction initializer bodies and two70B/22instruction selector leaves; prior62B prefixes reused; no new C reconstruction bytes',
        'profiles':profiles,'selector_formula':'for fresh U16 h:7 ifh<=20,6 if<=30,5 if<=50,4 if<=75,3 if<=100,2 if<=150,1 if<=250,else0; leafno store/frame/call, only A0/A4/A5 defined',
        'separate_bytes':'ctx+3 remains previous registrationID5 under preservation; objectB+3 is selectorreply. They are distinct addresses. If prior copiedconfig+10 remains1000, selector0 is storedtoB+3, not toctx+3',
        'constant_fields':'B+20 word07d7000d; B+24 word0d0db000+version305/320; B+28 word07d7b000+version; B+32 halfwordlow16(ffffb000+version); B+224 word31,B+228 word0; B+262/+264 halfworddfff; B+266 byte31; B+58/+60 halfword0f0f; B+57 byte0; B+126 halfword460; B+63 byte1; B+66 halfword3; B+72 word06071440; B+68 word0; B+64 halfword460; B+52 word1440000',
        'zero_and_sample_fields':'previous296Bclear plus no intervening writes makesinitialB+208/+212 words0; OR creates072d79ff atB+208/+216 and1b9e atB+212/+220; single freshsourcebyte state+14 copiedtoB+193/+201; freshU16state+4 shiftedright10 storedasbyteB+137 (0..63)',
        'size_algebra':'k=min(fresh U16[state+16],251); B+42/+46=k, B+44/+48=8*(k+138), B+34=max(k,27), B+36/+40=8*(k+138), B+38=8*(k+14). Allhalfwordvaluesfitwithoutwrap',
        'flag_branch_reason':'local SH0f0f atB+60 also fixesB+61=0f, andselectorhasnostores. Both subsequent &4 tests therefore nonzero under physicalnonalias/nointerference, selecting138 ratherthan14 offset. 8*(k+138)>=1104>328 skipslater328clamp',
        'return_boundary':'last two post-tail code blocks remain locally reachable alternatives in fullCFG. At+400..+408 restoreS0/RA/S1/S2/SP thenJALX0tail; no ordinaryRET orforcedsuccesscode. Three latecalls andtail unclosed, soinitializerreturntopublisher notproved',
        'premises':'previous gatezero/registration/prefix conditions; matching preserved selector code/data/ISA, valid object296B/sourcehalfwords/nonalias frames/globals/table/timerpayload; no adverse priorMMIO/FENCE.I orIRQ/DMA/reentry/unknownwriters; requiredreadscomplete normally. Code constants and B fields do not establish physical units',
        'remaining':['64298/64382,57ac4/57c04,63704/637ee callees and5e758/5e842tail','latergate/primarypublication andouterregistrationIDs','actualfreshsources/installedproviders, physicaleffects andobjectlifetimes'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    count=0
    for i,data in enumerate(carriers):
        for role,pc,size in (('initializer',previous.DETAILS[i]['initialize'],426),('selector',DETAILS[i][0],70)):
            raw=init.binding.take(data,pc,size)
            for p,d in decode(raw,pc).items():
                at=p-pc;w=d['size'];buf=bytearray(raw);buf[at:at+w]=(int.from_bytes(buf[at:at+w],'little')^(1<<20 if w==4 else 4)).to_bytes(w,'little')
                try:body(buf,role,i)
                except RuntimeError as e:check(str(e).startswith('fields '+role+' operand '),'fields mutation guard '+str(e))
                else:raise RuntimeError('fields mutation escaped')
                count+=1
    check(count==320,'fields mutation census')
    bins=[0]*8
    for h in range(65536):
        answer=selector_algebra(h);bins[answer]+=1
        piece=7 if h<=20 else 6 if h<=30 else 5 if h<=50 else 4 if h<=75 else 3 if h<=100 else 2 if h<=150 else 1 if h<=250 else 0
        check(answer==piece,'fields selector exhaustive threshold identity')
        k=min(h,251);short=8*(k+14);long=8*(k+138)
        check(0<=k<=251 and 112<=short<=2120 and 1104<=long<=3112 and long>328 and long-short==992,'fields size bounds and difference')
        check((k<<16&0xffffffff)>>16==k and ((long<<16)&0xffffffff)>>16==long,'fields halfword narrowing loses no bits')
    check(bins==[65285,100,50,25,25,20,10,21] and selector_algebra(1000)==0,'fields exact selector histogram')
    for byte in range(256):check(((0x0f0f>>8)&4)!=0 and (0x0f0f&4)!=0 and byte==byte&255,'fields local flag bytes and sampled byte domain')
    print('PASS:320 initializer/selector operand mutations rejected;65536 threshold/size cases;exactselectorhistogram/halfwordbounds')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');o=parser.parse_args()
    image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK header identity')
    carriers=[]
    for label,folder,tail,size,digest in init.binding.PROFILES:
        raw=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(raw)==size and sha256(raw).hexdigest()==digest,'candidate identity '+label);carriers.append(raw)
    raw_hex=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
    coverage=sparse.derive(image,carriers,header,raw_hex,sparse.parser())
    ledger=derive(image,carriers,header,coverage);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract()
    tests(carriers);output=(json.dumps(ledger,indent=1,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'role initializer fields exact ledger replay')
    print('PASS:completeinitializer/selector CFGs andallstoreclassification;conditionalctxgate5 vsB+3selector0;field/sizejoinsto firstlatecall;exactledger')
    print('PASS:NO target execution;three latecallees/tail/actualfreshsources/installedbinding/physicaleffects UNPROVED')


if __name__=='__main__':main()
