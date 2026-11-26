"""Offline ID9 initialization, active vector selectors and dispatch boundaries.

Original operands/CFG, finite path certificates and fixed-address geometry.
No target ISA, mutable register/RAM model, callback or provider execution.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_id8_initialization_static as previous

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
paths,role,registration=previous.paths,previous.role,previous.registration
leaves=previous.leaves
OUT=Path(__file__).with_name('v4160-id9-vector-dispatch-static.json')
PARTS=('initializer','vectors','select_A','select_B','callback','consumer','next_outer')
STARTS=((0x50412,0x50368,0x503d2,0x503f2,0x4f516,0x4f54c,0x6dd5e),
        (0x504ac,0x50402,0x5046c,0x5048c,0x4f5ae,0x4f5e4,0x6df4e))
SIZES=(42,106,32,32,54,88,16)
COUNTS=(14,29,10,10,22,36,4)
HASHES=(('287c9cce470c87b00c1e5239e613dd6af9af5337e942e1dd8a64d5b1784f4e7d','1e39e8316be08510605cc9a8e506e739ac47cee308cc41fe5dac595afb506a49',
 '7c38423c7f9c13bb389775fdaf3fa494e2da2bb958ab6660c985083b32689632','bc0e2538f118b75d5481f91f319c4c1ca252dc1060dbaec01bfc7e9c1707cbb3',
 '68e82fb900672f8e6a24e8248adc75d91aa170e25231fd906716422437dd579c','54f5259923df0e6dfc957627d7bddfc5482b61d75d49a004be73207daffee09f','c590e62070c97931212c604761073af35687bf2433306e3d03f08d43aed3f367'),
 ('a25fc648d997886d06a8388307d13b69aa4c7ceaa151c338842d860832b30bc1','4dd63df9ba6da08fb247681ecdbf336aed354a68d3c167f434b3722c8c21f6a6',
 'ff1f76e3a4d287e66b460f442a120fe963aa46aa1d336b07f839d51e3640adcd','5b3e1218cf8b8d4b7c54d798e655fd2d31e58d0adb4c99241381dd0815275962',
 'ce512a6591a9c3da8340ab835dd491e7802affbe23298993b120f8c16c565e8a','87bba253156c3bdb684390005d6b55f90b51c0f4dad0ed839df9fc9de63f8ff1','79895c37a8aae125f39e152a0b1d14d2c30ff27c0314d9e780c0246a64dc70d8'))
POINTERS=((0x5091a,0x50668,0x4f39e,0x517a0,0x5134e,0x515ee),
          (0x509ba,0x50708,0x4f436,0x51840,0x513ee,0x5168e))


def specs(part,index):
    pc=STARTS[index][PARTS.index(part)];delta=80*index;s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def lui(o,r,v=0x20003000):e(o,'lui',rd=r,imm=v)
    def ai(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    def st(o,r,b,v,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    def ld(o,r,b,v,w=4):e(o,'load',rd=r,rs1=b,imm=v,width=w)
    def bz(o,r,t):e(o,'beqz',rs1=r,target=pc+t)
    def bne(o,a,b,t):e(o,'bne',rs1=a,rs2=b,target=pc+t)
    def ret(o):e(o,'jr',rs1=1)
    if part=='initializer':
        ai(0,2,2,-32);st(2,1,2,28);st(4,10,2,12);e(6,'jal',rd=1,target=STARTS[index][1]);ld(10,10,2,12)
        lui(12,15);li(16,11,6);st(18,10,15,943+delta,1);e(22,'jal',rd=1,target=0x4d9ec+152*index)
        ld(26,1,2,28);lui(28,10,0x4f000);ai(32,10,10,1302+152*index);ai(36,2,2,32);e(38,'jal',rd=0,target=0x4efe2+152*index)
    elif part=='vectors':
        lui(0,15);st(4,0,15,924+delta);lui(8,15);st(12,0,15,908+delta);lui(16,14,0x51000);lui(20,15)
        ai(24,14,14,-1766+160*index);st(28,0,15,904+delta);lui(32,15);st(36,14,15,928+delta)
        lui(40,14,0x50000);ai(44,15,15,928+delta);ai(48,14,14,1640+160*index);st(52,14,15,4)
        lui(54,14,0x4f000);ai(58,14,14,926+152*index);st(62,14,15,8)
        lui(64,14,0x52000 if index else 0x51000);lui(68,15);ai(72,14,14,-1984 if index else 1952);st(76,14,15,912+delta)
        lui(80,14,0x51000);ai(84,15,15,912+delta);ai(88,14,14,846+160*index);st(92,14,15,4)
        lui(94,14,0x51000);ai(98,14,14,1518+160*index);st(102,14,15,8);ret(104)
    elif part in ('select_A','select_B'):
        a=part=='select_A';lui(0,15);ld(4,15,15,944+delta,1);e(8,'andi',rd=15,rs1=15,imm=8 if a else 4)
        bz(10,15,20);lui(12,15);ai(16,15,15,(928 if a else 912)+delta);lui(20,14);st(24,15,14,(908 if a else 904)+delta)
        li(28,10,0);ret(30)
    elif part=='callback':
        ai(0,2,2,-32);st(2,8,2,24);st(4,1,2,28);e(6,'mv',rd=8,rs2=10);st(8,11,2,12)
        e(10,'auipc',rd=1,imm=0x1ffb1000);e(14,'jalr',rd=1,rs1=1,imm=1396-152*index)
        ld(18,15,10,52);bz(20,15,46);ld(22,15,15,0,2);ld(24,11,2,12);bne(26,15,8,46);li(30,15,1);bne(32,11,15,46)
        ld(36,8,2,24);ld(38,1,2,28);ai(40,2,2,32);e(42,'jal',rd=0,target=0x4f43c+152*index)
        ld(46,1,2,28);ld(48,8,2,24);ai(50,2,2,32);ret(52)
    elif part=='consumer':
        ai(0,2,2,-16);st(2,1,2,12);st(4,8,2,8);st(6,9,2,4);e(8,'jal',rd=1,target=0x4f2ae+152*index)
        bz(12,10,78);ld(14,8,10,52);e(16,'mv',rd=9,rs2=10);bz(18,8,78);ld(20,15,8,2,1);bz(22,15,68)
        lui(24,15);ld(28,15,15,908+delta);bz(32,15,42);ld(34,15,15,4);bz(36,15,42);e(38,'mv',rd=10,rs2=8)
        e(40,'call_indirect',rd=1,rs1=15);ld(42,14,8,3,1);ai(44,15,0,47);bne(48,14,15,78)
        ld(52,8,2,8);ld(54,10,9,2,2);ld(56,1,2,12);ld(58,9,2,4);li(60,11,0);ai(62,2,2,16)
        e(64,'jal',rd=0,target=0x4f4b8+152*index);lui(68,15);ld(72,15,15,904+delta);e(76,'jump',target=pc+32)
        ld(78,1,2,12);ld(80,8,2,8);ld(82,9,2,4);ai(84,2,2,16);ret(86)
    else:
        entry,old=role.specs('entry',index);check(pc==entry+72,'id9 outer start');s={p:f for p,f in old.items() if pc<=p<pc+16}
    return pc,s


def body(raw,part,index):
    k=PARTS.index(part);pc,s=specs(part,index);n=decode(raw,pc)
    check(set(n)==set(s),'id9 '+part+' boundaries')
    for p,f in s.items():init.g(n,p,'id9 '+part+' operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[k],HASHES[index][k]),'id9 '+part+' identity')
    edges={};calls=[];tails=[]
    for p,d in n.items():
        op=d['op'];q=[p+d['size']]
        if op=='jr':check(d['rs1']==1,'id9 ordinary RET');q=[]
        elif op in ('beqz','bne'):q.append(d['target'])
        elif op=='jump':q=[d['target']]
        elif op in ('jal','jalr','call_indirect'):
            if op=='call_indirect':target='fresh U32[active_vector+4]'
            elif op=='jal':target=hex(d['target'])
            else:
                a=n[p-4];check(a['op']=='auipc' and a['rd']==d['rs1'],'id9 adjacent provider pair');target=hex((p-4+a['imm']+d['imm'])&0xfffffffe)
            row={'pc':hex(p),'target':target,'rd':d['rd']}
            if d['rd']==0:tails.append(row);q=[]
            else:
                calls.append(row)
                if part=='next_outer' and p==pc+12:q=[]
        check(all(v in n for v in q),'id9 '+part+' closed local CFG');edges[p]=q
    seen=set();active=set()
    def visit(p):
        check(p not in active,'id9 '+part+' acyclic CFG')
        if p in seen:return
        active.add(p);seen.add(p)
        for q in edges[p]:visit(q)
        active.remove(p)
    visit(pc);check(seen==set(n),'id9 '+part+' all nodes locally reachable')
    stores=[d for d in n.values() if d['op']=='store'];defs=sorted({d['rd'] for d in n.values() if d.get('rd',0)})
    check(len(stores)==(3,9,1,1,3,3,0)[k],'id9 '+part+' store census')
    if part in ('callback','consumer'):check(all(d['rs1']==2 for d in stores),'id9 runtime body only frame stores locally')
    if part=='vectors':check(defs==[14,15] and not calls and not tails and not any(d['op']=='load' for d in n.values()),'id9 pure vectors leaf')
    if part in ('select_A','select_B'):check(defs==[10,14,15] and not calls and not tails,'id9 selector leaf GPR census')
    if part=='initializer':check([(d['rs2'],d['imm']) for d in stores if d['rs1']==2]==[(1,28),(10,12)],'id9 saved input/RA frame')
    return {'start':hex(pc),'bytes':len(raw),'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),'encoded_GPR_definitions':defs,
        'store_count':len(stores),'calls':calls,'tails':tails,'conditional_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},
        'complete_function':part!='next_outer','calls_are_return_premises':True}


def certificates(b,part):
    pc=int(b['start'],16);edges={int(p,16):[int(q,16) for q in qs] for p,qs in b['conditional_CFG'].items()};cases={}
    def path(name,choices):cases[name]=paths.chain(edges,pc,{pc+p:pc+q for p,q in choices.items()})
    if part in ('select_A','select_B'):
        path('bit_clear',{10:20});path('bit_set',{10:12})
    elif part=='callback':
        path('record_null',{20:46});path('ID_mismatch',{20:22,26:46});path('event_not1',{20:22,26:30,32:46});path('match_tail',{20:22,26:30,32:36})
    elif part=='consumer':
        path('lookup_null',{12:78});path('record_null',{12:14,18:78})
        for group,target in (('A',24),('B',68)):
            for state in ('vector_null','function_null','call'):
                for post in ('RET','type47_tail'):
                    choices={12:14,18:20,22:target,32:42 if state=='vector_null' else 34,36:42 if state=='function_null' else 38,48:78 if post=='RET' else 52}
                    path(group+'_'+state+'_'+post,choices)
    for name,trace in cases.items():
        last=int(trace[-1],16);check(not edges[last],'id9 certificate ends RET/tail '+name)
    return cases


def bit_domain():
    rows=[]
    for b in range(256):
        rows.append({'fresh_flags':b,'activate_A':bool(b&8),'activate_B':bool(b&4)})
    check(sum(r['activate_A'] for r in rows)==128 and sum(r['activate_B'] for r in rows)==128,'id9 bit-selector domains')
    check(sum(r['activate_A'] and r['activate_B'] for r in rows)==64,'id9 bit selectors independent')
    return rows


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[]
    for i,(data,pr) in enumerate(zip(carriers,parent['profiles'])):
        g=0x20003000+80*i;d=role.DETAILS[i];ctx=0x20003000+d['ctx'];F=ctx+80;pc=STARTS[i][0];entry=d['entry']
        windows={p:body(init.binding.take(data,STARTS[i][k],SIZES[k]),p,i) for k,p in enumerate(PARTS)}
        check(pr['cut_before_fourth_outer_initializer']['target']==hex(pc) and pr['cut_before_fourth_outer_initializer']['A0']==9,'id9 inherited input ID9')
        selector=previous.previous.body(init.binding.take(data,0x4d9ec+152*i,44),'selector',i)
        cbreg=leaves.body(init.binding.take(data,0x4efe2+152*i,42),'callback_register',i)
        vn={x['pc']:x for x in windows['vectors']['instructions']};vpc=STARTS[i][1]
        pairs=((16,24),(40,48),(54,58),(64,72),(80,88),(94,98))
        pointers=[vn[vpc+a]['imm']+vn[vpc+b]['imm'] for a,b in pairs]
        check(tuple(pointers)==POINTERS[i],'id9 six vector pointers, independent profile identities')
        protected=[(ctx+1,1),(ctx+2,1),(ctx+3,1),(ctx+40,4),(paths.layout.T,4*212),(F+21,1),(F+36,4),(F+48,4),(F+68,4),
            (g+784,4),(g+792,4),(g+852,4),(g+940,1),(g+941,1),(g+944,1),(g+948,1),(g+949,1),(g+856,48)]
        rows=[(4,924),(12,908),(28,904),(36,928),(52,932),(62,936),(76,912),(92,916),(102,920)]
        for o,v in rows:
            check(vn[vpc+o]['op']=='store' and vn[vpc+o]['width']==4,'id9 vector store link')
            for a,z in protected:check(paths.origin.separated(g+v,4,a,z),'id9 vector stores exclude protected state')
        check(g+856+48==g+904 and g+936+4==g+940,'id9 vectors adjacent to old callback table and ID7 byte')
        pn={x['pc']:x for x in windows['initializer']['instructions']}
        check(pn[pc+10]['rd']==10 and pn[pc+18]['rs2']==10 and pn[pc+16]['imm']==6,'id9 reload input then ID9/selector6')
        check(pn[pc+22]['target']==int(selector['start'],16) and pn[pc+38]['target']==int(cbreg['start'],16),'id9 two reused leaf joins')
        check(pn[pc+28]['imm']+pn[pc+32]['imm']==STARTS[i][4],'id9 initializer publishes guarded callback body pointer')
        record=g+800+24;check(record+3<=g+848 and paths.origin.separated(record,3,g+812,3) and paths.origin.separated(record,3,g+800,3),'id9 record2 distinct from record0/1')
        for a,z in protected:check(paths.origin.separated(record,3,a,z),'id9 record2 excludes protected state')
        for k in range(12):
            for a,z in protected[:17]:check(paths.origin.separated(g+856+4*k,4,a,z),'id9 callback insertion excludes source/task state')
        callback=windows['callback'];consumer=windows['consumer'];cp=STARTS[i][4];wp=STARTS[i][5]
        check(callback['calls']==[{'pc':hex(cp+14),'target':'0x20000a94','rd':1}],'id9 callback provider target')
        check(consumer['calls'][0]['target']==hex(0x4f2ae+152*i) and consumer['calls'][1]['target']=='fresh U32[active_vector+4]','id9 lookup and indirect dispatch targets')
        cn={x['pc']:x for x in callback['instructions']};wn={x['pc']:x for x in consumer['instructions']}
        check(cn[cp+18]['rs1']==10 and cn[cp+20]['rs1']==15,'id9 callback tests record only after unguarded context dereference')
        check(wn[wp+12]['rs1']==10 and wn[wp+18]['rs1']==8,'id9 consumer guards lookup and record nulls')
        check([wn[wp+o]['imm'] for o in (20,42,54)]==[2,3,2] and wn[wp+54]['width']==2,'id9 exact narrow field geometry')
        paths_by_part={p:certificates(windows[p],p) for p in ('select_A','select_B','callback','consumer')}
        check(sum(len(x) for x in paths_by_part.values())==22,'id9 path certificate census per profile')
        on={x['pc']:x for x in windows['next_outer']['instructions']};outer=role.body(init.binding.take(data,entry,112),'entry',i);en={x['pc']:x for x in outer['instructions']}
        check(en[entry+68]['target']==pc and entry+72==STARTS[i][6],'id9 normal tail RET returns to next outer window')
        reg=registration.body(init.binding.take(data,d['reg'],48),i);check(11 not in reg['encoded_GPR_definitions'],'id9 next registration preserves A1')
        check(on[entry+80]['target']==d['reg'] and on[entry+84]['target']==d['outer_init'][4],'id9 next registration and fifth initializer')
        handler=0x6d000+d['outer_lows'][4];check(on[entry+72]['imm']+on[entry+76]['imm']==handler,'id9 fifth handler formation')
        entry10=paths.layout.T+40;check(10<14 and entry10+4<=paths.layout.T+14*4,'id9 table entry10 extent')
        for a,z in protected[:4]:check(paths.origin.separated(entry10,4,a,z),'id9 entry10 excludes metadata')
        profiles.append({'label':pr['label'],'bodies':windows,'path_certificates':paths_by_part,'inherited_entry':pr['cut_before_fourth_outer_initializer'],
            'reused_selector_sha256':selector['sha256'],'reused_callback_register_sha256':cbreg['sha256'],
            'vector_setup':{'zero_words':[hex(g+924),hex(g+908),hex(g+904)],'A':{'base':hex(g+928),'pointers':[hex(p) for p in pointers[:3]],'active_word':hex(g+908)},
                'B':{'base':hex(g+912),'pointers':[hex(p) for p in pointers[3:]],'active_word':hex(g+904)},'initializer_does_not_call_activation_selectors':True,
                'actual_pointer_lifetime_or_activation_order_proved':False},
            'ID9_publication':{'saved_input_SP_offset':-20,'saved_RA_SP_offset':-4,'byte_address':hex(g+943),'value':9,'selector':6,
                'record2_halfword':{'address':hex(record),'value':6},'record2_byte':{'address':hex(record+2),'value':9},'callback_pointer':hex(STARTS[i][4]),
                'registration_success_not_required_for_return':True,'tail_reply_A0':'0 if inserted,19 if full','tail_reply_A1':'0 if inserted,slot11 last observed nonzero word if full','tail_reply_A2':12},
            'activation_contract':{'fresh_flags_byte':hex(g+944),'A_mask':8,'B_mask':4,'mask_clear':'write0 to active word','mask_set':'write corresponding fixed vector base to active word',
                'reply_A0':0,'separate_fresh_reads_not_a_coherent_pair':True,'flags_source_and_selector_call_order_proved':False},
            'registered_callback_contract':{'entry':callback['start'],'cut_before_provider':{'pc':hex(cp+14),'target':'0x20000a94'},
                'context_premise':'returned C must allow U32[C+52] even when C is zero; no local C-null guard precedes this dereference',
                'conditional_tail':'if R=U32[C+52] nonzero, U16[R] equals saved full entry A0, and saved entry A1==1, restore frame and tail4f43c/4f4d4',
                'other_paths':'restore frame and ordinaryRET, local A0 remains provider reply C','provider_preservation_premise':'saved S0/input/SP/frame/RA, code and valid source objects retained',
                'tail_target':callback['tails'][0]['target'],'tail_entry_A0':'provider reply C, not recordR','tail_entry_A1':1,'tail_expanded_here':False},
            'vector_consumer_contract':{'entry':consumer['start'],'lookup_target':hex(0x4f2ae+152*i),'lookup_body_not_expanded':True,
                'guards':'null C or null U32[C+52] -> ordinaryRET; otherwiseR=U32[C+52]',
                'choose':'freshU8[R+2]!=0 selects activeA; zero selects activeB; this record byte differs from activation flags byte',
                'dispatch':'if fresh active pointerV and freshU32[V+4] nonzero, call that pointer withA0=R; otherwise skipcall',
                'candidate_dispatch_targets_if_retained':{'A':hex(pointers[1]),'B':hex(pointers[4])},
                'post_call':'read freshU8[R+3]; if47 restoreframe then tail withA0=U16[C+2],A1=0; otherwiseordinaryRET',
                'post_tail':consumer['tails'][0]['target'],'post_tail_expanded_here':False,
                'premises':'valid C/R/V/function/context/stack objects and required S0/S1/SP/frame/RA/GP/code preserved across lookup/indirect call; activation/provider freshness and actual binding unknown'},
            'conditional_next_registration':{'pc':hex(entry+80),'handler':hex(handler),'fresh_count_premise':10,'fresh_capacity_premise':'>=14','fresh_table_premise':hex(paths.layout.T),
                'entry10_address':hex(entry10),'new_count':11,'reply_A0':10,'reply_A2':11,'A1':'callback-register result preserved'},
            'cut_before_fifth_outer_initializer':{'pc':hex(entry+84),'target':hex(d['outer_init'][4]),'A0':10,'A2':11,'A1':'0 if inserted,slot11 last observed nonzero word if full'},
            'actual_installed_binding_proved':False,'target_callback_executed':False})
    return {'schema':'TSL9-ID9-vector-dispatch-static-v1','profile':parent['profile'],'APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'flag_domain':bit_domain(),
        'scope':'per candidate42B initializer/106B vectors/two32B activation leaves/54B registeredcallback/88B consumer/16B outer join;740B/250 new operand guards and44 finite CFG path certificates; selector/callback-registration reused',
        'boundary':'ID9 pure-RAM initializer closes under valid nonalias frames/code/table; insertionfailure still returns. Runtimecallback stops at RAMprovider; vectorconsumer stops at lookup/indirect/post-tail contracts, actual activation and reachability not assumed',
        'remaining':['fifth initializer6c300/6c4ec and source of activation flags/call order','callback provider20000a94, lookup4f2ae/4f346 and tails4f43c/4f4d4,4f4b8/4f550','actual vector target callees, provider bindings and object/frame lifetimes'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    mutations=certs=0
    for i,data in enumerate(carriers):
        for k,part in enumerate(PARTS):
            pc=STARTS[i][k];raw=init.binding.take(data,pc,SIZES[k]);b=body(raw,part,i)
            if part in ('select_A','select_B','callback','consumer'):certs+=len(certificates(b,part))
            for p,d in decode(raw,pc).items():
                at=p-pc;z=d['size'];buf=bytearray(raw)
                buf[at:at+z]=(int.from_bytes(buf[at:at+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
                try:body(buf,part,i)
                except RuntimeError as e:check(str(e).startswith('id9 '+part+' operand '),'id9 specified mutation guard '+str(e))
                else:raise RuntimeError('id9 mutation escaped')
                mutations+=1
    check(mutations==250 and certs==44 and sum(SIZES)*2==740,'id9 instruction/path/byte census');bit_domain()
    print('PASS:250 operand mutations rejected;740 original bytes;44 finite CFG path certificates;256 activation-flag cases')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');o=parser.parse_args()
    image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK header identity')
    carriers=[]
    for label,folder,tail,z,digest in init.binding.PROFILES:
        raw=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(raw)==z and sha256(raw).hexdigest()==digest,'candidate identity '+label);carriers.append(raw)
    raw_hex=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
    coverage=sparse.derive(image,carriers,header,raw_hex,sparse.parser())
    ledger=derive(image,carriers,header,coverage);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract()
    tests(carriers);output=(json.dumps(ledger,indent=1,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'id9 exact ledger replay')
    print('PASS:ID9 vector/record2 publication;conditional ID10/count11 return;callback and indirect-dispatch boundaries;exact ledger')
    print('PASS:NO target execution/emulation;actual activation/provider/callback reachability and lifetimes UNPROVED')


if __name__=='__main__':main()
