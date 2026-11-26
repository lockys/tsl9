"""Complete candidate 40058, nominal empty-list case and APP setup join.

Static operands/CFGs and integer/interval identities only. No target ISA,
register machine, timer/list/heap, callbacks, MMIO or service execution.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_registration_return_chain_static as previous
import check_v4160_allocation_core_static as core
import check_v4160_initial_table_extent_static as layout
import check_v4160_config_buffer_source_static as source
import check_v4160_task_registration_static as registration
import check_v4160_optional_hook_origin_static as origin
import check_v4160_post_config_static as post

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-timer-start-setup-static.json')
DETAILS=((0x43728,412,480,564,488,544,-1268,0x1ffbd000,-2026,
 '8904d50d1266850605a200c20d7a9053aa94304a7340e4f0d072dfaf12aed5bc',
 '3dbc188eb9ab2d30be1a30431a4e29a19fa7bbc0b21326dc7accd6d73913e1e8'),
 (0x437b4,492,560,644,568,624,-1408,0x1ffbc000,1930,
 '334dfdb9f90b5f7cc9f5bf0712c5928045c652e58b752a22f4b3d0595c5056d4',
 'fd479d64abd9a70599e2a32ecc5b0f66fda66c4345890568f90959997842c6b6'))
APP_WINDOWS=(('task',0x907a,54,19,'901ef49b5e03e522d166f5ea11ae041f799b6733971e69ad6fc8fb252c6923f8'),
 ('setup',0x8eb0,8,3,'0267bf47e923181dba78a67d13ff5c3af69c11233593d4f2cf06b8bea899b0fd'))
SAVED=((1,44),(8,40),(9,36),(18,32),(19,28),(20,24),(21,20),(22,16),(23,12))


def specs(role,index=0):
    pc,ctx,service,copied,head,fallback,low,upper,alow,*_=DETAILS[index]
    if role=='lookup':pc=0x20000314
    elif role in ('task','setup'):pc=next(w[1] for w in APP_WINDOWS if w[0]==role)
    s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def imm(o,op,r,b,v):e(o,op,rd=r,rs1=b,imm=v)
    def load(o,r,b,v,w=4,**extra):e(o,'load',rd=r,rs1=b,imm=v,width=w,**extra)
    def store(o,r,b,v,w=4,**extra):e(o,'store',rs2=r,rs1=b,imm=v,width=w,**extra)
    def lui(o,r,v):e(o,'lui',rd=r,imm=v)
    def mv(o,r,b):e(o,'mv',rd=r,rs2=b)
    def binary(o,op,r,a,b):e(o,op,rd=r,rs1=a,rs2=b)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    def branch(o,op,a,b,t):e(o,op,rs1=a,rs2=b,target=pc+t)
    def bz(o,op,r,t):e(o,op,rs1=r,target=pc+t)
    def jump(o,t):e(o,'jump',target=pc+t)
    if role=='service':
        imm(0,'addi',2,2,-48)
        for off,r,v in ((2,9,36),(4,20,24),(10,1,44),(12,8,40),(14,18,32),(16,19,28),(18,21,20),(20,22,16),(22,23,12)):store(off,r,2,v)
        lui(6,9,0x40024000);load(24,20,9,524);store(28,0,9,524);e(32,'fence.i')
        lui(36,15,0x20003000);load(40,15,15,ctx+1,1);branch(44,'bgeu',10,15,60)
        lui(48,15,0x20003000);load(52,23,15,service);branch(56,'bne',23,0,70)
        lui(60,15,0x40024000);store(64,20,15,524);jump(68,138)
        lui(70,18,0x20003000);imm(74,'addi',18,18,copied);mv(78,21,11)
        load(80,22,18,4);load(84,11,18,8,2);lui(88,15,0xfe364000);imm(92,'addi',15,15,-896)
        binary(96,'add',22,22,15);binary(98,'mul',15,11,12);mv(102,8,10);mv(104,19,12);li(106,13,0)
        binary(108,'mulhu',11,11,12);imm(112,'addi',10,15,800);binary(116,'sltu',15,10,15)
        imm(120,'addi',12,0,1600);binary(124,'add',11,11,15);e(126,'jal',rd=1,target=previous.previous.arithmetic.BASES[index])
        branch(130,'bgeu',22,10,162);store(134,20,9,524);li(138,10,0)
        for j,(r,v) in enumerate(SAVED):load(140+2*j,r,2,v)
        imm(158,'addi',2,2,48);e(160,'jr',rs1=1)
        e(162,'call_indirect',rd=1,rs1=23);load(164,11,18,8,2);mv(168,9,10)
        imm(170,'addi',12,0,1600);binary(174,'mul',15,11,19);li(178,13,0)
        binary(180,'mulhu',11,11,19);imm(184,'addi',10,15,800);binary(188,'sltu',15,10,15)
        binary(192,'add',11,11,15);e(194,'jal',rd=1,target=previous.previous.arithmetic.BASES[index])
        binary(198,'add',15,10,9);mv(202,9,15);load(204,14,18,4)
        branch(208,'bltu',15,10,216);branch(212,'bltu',15,14,220);binary(216,'sub',9,15,14)
        mv(220,11,21);mv(222,10,8);e(224,'auipc',rd=1,imm=0x1ffbd000);e(228,'jalr',rd=1,rs1=1,imm=low)
        bz(232,'beqz',10,248);store(234,9,10,8);lui(236,15,0x40024000);store(240,20,15,524);li(244,10,1);jump(246,140)
        imm(248,'ori',11,8,-256);imm(252,'slli',11,11,16);imm(254,'srli',11,11,16);li(256,10,16)
        e(258,'auipc',rd=1,imm=upper);e(262,'jalr',rd=1,rs1=1,imm=alow);bz(266,'bnez',10,286)
        lui(268,15,0x20003000);load(272,15,15,fallback);bz(276,'beqz',15,60)
        mv(278,11,8);li(280,10,4);e(282,'call_indirect',rd=1,rs1=15);jump(284,60)
        lui(286,14,0x20003000);load(290,15,14,head);bz(294,'bnez',15,324);store(296,10,14,head)
        li(300,15,1);store(302,0,10,12);store(306,9,10,8);store(308,21,10,2,2)
        store(312,8,10,0,1,mnemonic='qk.c.sb');store(314,15,10,1,1,mnemonic='qk.c.sb');store(316,0,10,4)
        jump(320,236);mv(322,15,14);load(324,14,15,12);bz(326,'bnez',14,322);store(328,10,15,12);jump(330,300)
    elif role=='lookup':
        lui(0,15,0x20003000);load(4,15,15,head);bz(8,'bnez',15,14);mv(10,10,15);e(12,'jr',rs1=1)
        load(14,14,15,2,2,mnemonic='qk.c.lhu');branch(16,'bne',14,11,26)
        load(20,14,15,0,1,mnemonic='qk.c.lbu');branch(22,'beq',14,10,10);load(26,15,15,12);jump(28,8)
    elif role=='task':
        imm(0,'addi',2,2,-16);store(2,8,2,8);lui(4,8,0x40000);load(8,15,8,72);store(10,1,2,12)
        imm(12,'addi',12,0,180);li(16,11,0);e(18,'auipc',rd=10,imm=0x20003000);imm(22,'addi',10,10,-644)
        e(26,'call_indirect',rd=1,rs1=15);load(28,15,8,128);e(32,'auipc',rd=10,imm=0)
        imm(36,'addi',10,10,-128);e(40,'call_indirect',rd=1,rs1=15);load(42,1,2,12);load(44,8,2,8)
        store(46,10,3,166,1);imm(50,'addi',2,2,16);e(52,'jr',rs1=1)
    elif role=='setup':
        e(0,'jal',rd=1,target=0x907a);load(2,15,8,416);e(6,'call_indirect',rd=1,rs1=15)
    return pc,s


def edges(n):
    out={}
    for p,d in n.items():
        op=d['op']
        q=[] if op=='jr' else [d['target']] if op=='jump' else [p+d['size'],d['target']] if op in ('bgeu','bne','bnez','beqz','bltu','beq') else [p+d['size']]
        check(all(v in n for v in q),'timer CFG no cuts');out[p]=q
    return out


def body(raw,role,index=0):
    pc,s=specs(role,index);n=decode(raw,pc)
    check(set(n)==set(s),'timer '+role+' boundaries')
    for p,f in s.items():init.g(n,p,'timer '+role+' operand '+hex(p-pc),**f)
    if role=='service':size,count,digest=332,113,DETAILS[index][-2]
    elif role=='lookup':size,count,digest=30,11,DETAILS[index][-1]
    else:_,_,size,count,digest=next(w for w in APP_WINDOWS if w[0]==role)
    check((len(raw),len(n),sha256(raw).hexdigest())==(size,count,digest),'timer '+role+' complete identity')
    if role=='setup':
        e={p:[p+d['size']] for p,d in n.items()};cycle=[]
    else:
        e=edges(n);cycle=[c for c in previous.previous.mode.graphs.components(e) if len(c)>1 or c[0] in e[c[0]]]
        if role=='service':check(cycle==[[pc+322,pc+324,pc+326]],'timer sole append SCC')
        elif role=='lookup':check(len(cycle)==1 and set(cycle[0])=={pc+o for o in (8,14,16,20,22,26,28)},'timer lookup SCC')
        else:check(not cycle,'timer task no cycle')
    if role=='service':
        init.pair(n,pc+224,1,0x20000314,'timer lookup pair');init.pair(n,pc+258,1,0x20000040,'timer allocator pair')
        check([p-pc for p,d in n.items() if d['op'] in ('jal','jalr','call_indirect')]==[126,162,194,228,262,282],'timer complete six-call census')
        check([p-pc for p,d in n.items() if d['op']=='store']==[2,4,10,12,14,16,18,20,22,28,64,134,234,240,296,302,306,308,312,314,316,328],'timer exact22 store census')
        check({(d['rs2'],d['imm']) for d in n.values() if d['op']=='store' and d['rs1']==2}==set(SAVED),'timer exact saved words')
    if role=='lookup':
        check(not any(d['op']=='store' or d['op'] in ('jal','jalr','call_indirect') for d in n.values()),'timer lookup no stores/calls')
        check(sorted({d['rd'] for d in n.values() if d.get('rd',0)})==[10,14,15],'timer lookup GPR definitions')
    return {'role':role,'start':hex(pc),'bytes':size,'sha256':digest,'instructions':list(n.values()),
        'normal_return_CFG':{hex(p):[hex(q) for q in qs] for p,qs in e.items()},
        'cyclic_SCCs':[[hex(p) for p in c] for c in cycle],'complete_function':role!='setup'}


def chain(e,start,choices,cut=None):
    e={p:list(qs) for p,qs in e.items()}
    for p,q in choices.items():check(q in e[p],'timer selected branch membership');e[p]=[q]
    if cut is not None:e[cut]=[]
    seen=[];p=start
    while True:
        check(p not in seen,'timer selected chain acyclic');seen.append(p)
        if not e[p]:return [hex(p) for p in seen]
        check(len(e[p])==1,'timer selected single successor');p=e[p][0]


def small_case(raw,index):
    n=core.decode(raw);s=core.specs(core.DETAILS[index]);check(set(n)==set(s),'timer small core boundaries')
    for p,f in s.items():init.g(n,p,'timer small core operand '+hex(p-core.ENTRY),**f)
    check(sha256(raw).hexdigest()==core.DETAILS[index][-1],'timer small core identity')
    path=chain(edges(n),core.ENTRY,{core.ENTRY+p:core.ENTRY+q for p,q in {22:24,24:38,56:60,76:110,112:114,116:120,134:138}.items()})
    check(hex(core.ENTRY+96) not in path and hex(core.ENTRY+204) not in path,'timer small core no fallback/search')
    return {'path':path,'payload':hex(layout.A+8),'request':16,'tag':'0xff03','remainder_header':hex(layout.A+24),
        'remainder_size':480,'account_delta':-24,'fresh_small_header_is_additional_premise':True}


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[]
    app_windows={r:body(image[pc-0x8000:pc-0x8000+size],r) for r,pc,size,_,_ in APP_WINDOWS}
    check(parent['wrapper_tail']['conditional_arguments']=={'A0':3,'A1':8192,'A2':192000},'timer original caller argument join')
    setup_prefix=origin.window(image[0x8e88-0x8000:0x8eb0-0x8000],'setup')
    check(setup_prefix['normal_return_prefix_cut']=='0x8eb0','timer tail return link to setup')
    check(0x908c+0x20003000-644==0x2000be08 and 0x909a-128==0x901a,'timer APP second task operands')
    for i,(data,pr) in enumerate(zip(carriers,parent['profiles'])):
        pc,ctx,service,copied,head,*_=DETAILS[i];ctx+=0x20003000
        check(init.binding.word(data,0x40058)==pc and pr['candidate40058_word']==hex(pc),'timer matching slot join')
        b=body(init.binding.take(data,pc,332),'service',i);n={d['pc']:d for d in b['instructions']};e=edges(n)
        mapping=init.binding.profile(data,pr['label'])['first_copy'];src=int(mapping['source'],16)+0x20000314-int(mapping['destination'],16)
        lookup=body(init.binding.take(data,src,30),'lookup',i)
        alloc=small_case(init.binding.take(data,core.DETAILS[i][0],208),i)
        arithmetic=previous.arithmetic(init.binding.take(data,previous.previous.arithmetic.BASES[i],914),previous.previous.arithmetic.BASES[i])
        check(arithmetic['complete_CFG_and_preservation'],'timer two arithmetic calls preserve needed S/frame')
        fill=source.fill_contract(init.binding.take(data,(0x4060c,0x4064c)[i],46))
        reg=registration.body(init.binding.take(data,registration.DETAILS[i][0],48),i)
        check(fill['encoded_GPR_writes']==[10,14,15] and 11 not in reg['encoded_GPR_definitions'],'timer second-task A1 zero preservation')
        rn={d['pc']:d for d in reg['instructions']}
        init.g(rn,registration.DETAILS[i][0]+24,'timer second-task final A2 definition',op='addi',rd=12,rs1=15,imm=1)
        check([p for p,d in rn.items() if d.get('rd')==12]==[registration.DETAILS[i][0]+24],'timer second-task A2 equals admitted n+1')
        check(init.binding.word(data,0x40048)==0x2000039c and init.binding.word(data,0x40080)==int(reg['start'],16),'timer second task matching fill/registration slots')
        choices={44:48,56:70}
        reject=chain(e,pc,{pc+p:pc+q for p,q in choices.items()}|{pc+130:pc+134})
        accepted=[]
        for adjust in ({208:216},{208:212,212:216},{208:212,212:220}):
            selected=choices|{130:162,232:248,266:286,294:296}|adjust
            accepted.append(chain(e,pc,{pc+p:pc+q for p,q in selected.items()}))
        check(all(hex(pc+282) not in p and hex(pc+324) not in p for p in accepted),'timer nominal success avoids fallback and append')
        headaddr=0x20003000+head;postpc=post.DETAILS[i][0]
        postproof=post.derive(image,carriers,header)['profiles'][i];pn={d['pc']:d for d in postproof['instructions']}
        init.g(pn,postpc+4,'timer earlier head-zero source',op='store',rs1=15,rs2=0,imm=head,width=4)
        # This witness is NOT a universal preservation proof from post to fresh entry.
        node=layout.A+8;remainder=layout.A+24
        stores=[(layout.A,8),(remainder,8),(node,16),(headaddr,4),(ctx+6,2)]
        taskaddr=0x20004000+166;tableword=layout.T+16
        protected=[(0x20004184,1),(ctx+1,1),(ctx+2,1),(ctx+40,4),(0x20003000+copied,16),
            (0x20003000+service,4),(layout.B,8),(layout.T+12,8),(0x2000be08,180)]
        for p,w in stores:
            for q,z in protected:check(origin.separated(p,w,q,z),'timer small allocation/node stores exclude live ranges')
        check(node+16==remainder and remainder+8+480==layout.B and layout.A+8+504==layout.B,'timer small split geometry')
        check(4<14 and tableword==0x20004804 and tableword+4<=layout.T+4*14,'timer second registration extent')
        for p,w in ((0x2000be08,180),(tableword,4),(taskaddr,1),(ctx+1,1)):
            for q,z in ((node,16),(headaddr,4),(0x20004184,1),(layout.T+12,4)):
                check(origin.separated(p,w,q,z),'timer second task writes preserve new node/first task')
        profiles.append({'label':pr['label'],'service':b,'lookup':lookup,'lookup_candidate_source':hex(src),
            'small_allocation_case':alloc,'threshold_reject_path':reject,'nominal_new_node_paths':accepted,
            'head_word':hex(headaddr),'earlier_post_head_zero_PC':hex(postpc+4),
            'new_node_fields':{'address':hex(node),'byte0':3,'byte1':1,'halfword2':8192,'word4':0,'word8':'deadline','word12':0},
            'conditional_service_reply_if_rejected':0,'conditional_service_reply_if_new_node':1,
            'second_task':{'fill_bytes':180,'fill_start':'0x2000be08','fill_end_exclusive':'0x2000bebc','fill_sha256':fill['sha256'],
                'registration_sha256':reg['sha256'],'entry4_address':hex(tableword),'entry4_value':'0x901a','reply':4,'new_count':5,'saved_byte_address':hex(taskaddr)},
            'actual_installed_binding_proved':False})
    return {'schema':'TSL9-timer-start-setup-static-v1','profile':parent['profile'],'APP_sha256':sha256(image).hexdigest(),
        'scope':'two complete332B/113instruction40058 services and two30B/11instruction lookup leaves; complete54B/19instruction APP second-task function plus8B bounded setup window; existing full core/helper/fill/registration reused',
        'profiles':profiles,'APP_windows':app_windows,
        'new_fresh_premises':'in addition to previous chain: at40058 entry listhead=0, smallhead=A=200043ac with next=B200045ac,size504,tag0, sentinel=E2000b184 and matching allocator/global headers; head remains0 throughlookup/append reads. Earlier post clear/bootstrap are source witnesses, NOT proof that all intervening writers preserve these values',
        'admission':'task3<count4 and fresh service191c6 nonzero. First helper receives 64-bit h*192000+800, divisor1600. Its opaque A0=D0 is compared unsigned with fresh(word4-30000000)mod32; nominal limitfe363c7f. Reject0 or continue ifD0<=limit; numerical quotient not proved',
        'deadline':'after matching reader replyR and second helper opaqueD1, sum=(R+D1)mod32. Ifcarry (sum<D1) OR sum>=freshword4, deadline=(sum-word4)mod32; otherwise sum. Only one subtraction, not general modulo',
        'success':'head0 makeslookupreturn0; request16 tagff03 small-fit splits504 into16 plus8-byteheader plus480. Returnnode200043b4; head=node; sixnode fields initialized; return1 with saved4002420c snapshot restored locally',
        'general_body_boundary':'lookup/append traversal may cycle; existing-node and allocationfailure/fallback paths decoded but not transitively closed here; nominal head0/smallfit excludes them',
        'return_to_setup':'tail retained wrapper callerRA8eb0 if earlier setup frames/context preserved; service48B frame restoresRA/S0..S7/SP thenRET; setup8eb0 calls907a without checking timerreply',
        'second_registration':'matching fill clears180B then matching40080 receives901a, n4<c>=14 returns4,stores901a atT+16, count5. APP stores lowbyte4 atGP+166 andreturns8eb2; no inferred success from controlflow alone',
        'cut_before':'8eb6 indirect call usingfresh[then-liveS0+416]; nominal401a0 only ifS0=40000 preserved. No new argument setup: A0=4, A1=0 retained through matchingfill/registration, A2=5 from admitted registration n+1. No call execution or outcome claim',
        'premises':'previous alternative-path conditions and additionalfresh nominal list/smallheader facts, matching slots/code/mappedRAMhelpers; valid nonwrapping nonalias stack/heap/globals, no adverse MMIO/FENCE.I/IRQ/DMA/reentry/externalwrites; required reader/helper/core/fill calls complete normally',
        'remaining':['actual fresh head/smallblock preservation and installed provider provenance','401a0 and later setup calls','general arithmetic quotient, other list paths/progress, physical effects and later lifetime'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(image,carriers):
    count=0
    for i,data in enumerate(carriers):
        mapping=init.binding.profile(data,init.binding.PROFILES[i][0])['first_copy'];src=int(mapping['source'],16)+0x20000314-int(mapping['destination'],16)
        for role,pc,raw in (('service',DETAILS[i][0],init.binding.take(data,DETAILS[i][0],332)),('lookup',0x20000314,init.binding.take(data,src,30))):
            for p,d in decode(raw,pc).items():
                at=p-pc;w=d['size'];buf=bytearray(raw)
                if d['op']=='fence.i':buf[at]^=128
                else:buf[at:at+w]=(int.from_bytes(buf[at:at+w],'little')^(1<<20 if w==4 else 4)).to_bytes(w,'little')
                try:body(buf,role,i)
                except RuntimeError as e:
                    expected=str(e)=='unsupported static leaf encoding '+hex(p) if d['op']=='fence.i' else str(e).startswith('timer '+role+' operand ')
                    check(expected,'timer mutation guard '+str(e))
                else:raise RuntimeError('timer mutation escaped')
                count+=1
        raw=init.binding.take(data,core.DETAILS[i][0],208);n=core.decode(raw)
        for off in (38,46,56,110,114,116,124,134,146,156,166,168,176,180,192):
            d=n[core.ENTRY+off];w=d['size'];buf=bytearray(raw);buf[off:off+w]=(int.from_bytes(buf[off:off+w],'little')^(1<<20 if w==4 else 4)).to_bytes(w,'little')
            try:small_case(buf,i)
            except RuntimeError as e:check(str(e).startswith('timer small core operand '),'timer core mutation guard '+str(e))
            else:raise RuntimeError('timer core mutation escaped')
            count+=1
    for role,pc,size,_,_ in APP_WINDOWS:
        raw=image[pc-0x8000:pc-0x8000+size]
        for p,d in decode(raw,pc).items():
            at=p-pc;w=d['size'];buf=bytearray(raw);buf[at:at+w]=(int.from_bytes(buf[at:at+w],'little')^(1<<20 if w==4 else 4)).to_bytes(w,'little')
            try:body(buf,role)
            except RuntimeError as e:check(str(e).startswith('timer '+role+' operand '),'timer APP mutation guard '+str(e))
            else:raise RuntimeError('timer APP mutation escaped')
            count+=1
    check(count==300,'timer mutation census')
    for h in range(65536):
        x=h*192000;low=x&0xffffffff;carry=int(((low+800)&0xffffffff)<low)
        check((((x>>32)+carry)<<32)|((low+800)&0xffffffff)==x+800,'timer 64-bit multiply/add carry identity')
    check(((3|-256)&65535)==0xff03 and (0xffffffff-30000000)&0xffffffff==0xfe363c7f,'timer tag and limit constants')
    for cap in layout.facts():check(layout.T+20<=layout.T+4*cap['N0'],'timer entry4 within all256 tables')
    print('PASS:298 operand mutations plus2 noncanonical FENCE.I encodings rejected;65536 wide-product/carry identities;256 table bounds;small-split algebra')


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
    tests(image,carriers);output=(json.dumps(ledger,indent=1,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'timer start setup exact ledger replay')
    print('PASS:complete40058/lookup bodies;conditional empty-list/small-fit or threshold-reject returns;second registration reply4/count5 to8eb6 cut;exact ledger')
    print('PASS:NO target execution; actualslots/freshhead/smallheader/generalquotient/401a0/physicaleffects UNPROVED')


if __name__=='__main__':main()
