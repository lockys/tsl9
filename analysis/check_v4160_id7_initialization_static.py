"""Offline full ID7 initializer/callees, selector-tail and ID8 boundary.

Raw operand/CFG guards and explicit fixed-address interval algebra only.
No target ISA, memory/register machine, fill, callback or hardware model.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_id6_leaf_return_static as previous

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
paths,role,registration=previous.paths,previous.role,previous.registration
OUT=Path(__file__).with_name('v4160-id7-initialization-static.json')
PARTS=('initializer','defaults','vectors_A','vectors_B','state','selector','next_outer')
STARTS=((0x46570,0x45220,0x48c56,0x47eac,0x6d682,0x4d9ec,0x6dd3e),
        (0x46608,0x452b4,0x48cee,0x47f44,0x6d86e,0x4da84,0x6df2e))
SIZES=((68,352,144,126,126,44,16),(68,356,144,126,126,44,16))
COUNTS=((22,102,40,35,36,16,4),(22,103,40,35,36,16,4))
HASHES=(('dd244a7b90422fb3ad617001e5d604e37086364872a2fb449c9c5b8b0337eb05','1a2d61c374c68d9715df5fb9cc0e80c859d8c9fcbb28f8831b512ccbae9d1074',
 '4108ae4cae2ed674031034bba003db68be03abfdfeaafb5faa5e40de2e5937b2','f13de9921d70a73b502a6ffcc8af043f488536c0404129a8472ceb475bebecce',
 'ae518ce18a121c3e721f3ae9915774b41b5b6ebd05593fdf665559cf1f9b64ba','7c9bb40255be706907b9c7e06ed306161ddf93b5330007d017cc082ecb23197e','d39539ffed238b71ea6cf137ab1f6e4076edab9f3b64aad2072308a39e444189'),
 ('4e1f1c2e225802a260a73ca585e544f43f1f709bbd0914a0c03f6283cb43ffcd','0471e0cbdb7e13bb0c028fe12bd5c311073235239de8716da9a2c2acaf52e7b6',
 '9a12140bec25313df75e35d131e16b0ebf4e142157d9d094ef06e83f3fa87095','80c3e2f142ff17c40dccbd9eddc7f1a389b274f37e0daedda4c0defefa72ebf2',
 'd6bff23731732f97294021d9101792a8ddadca71c63d09d175e944b42a3688ac','4015d92d91425223cec14d8da7f7624ca851f9d2f2fbfc694ea9eea914c70383','0d9a9156e9c85bbd88235af7b18c9e0a3d0015dd6d2af184b133cba02284cefc'))


def default_stores(index):
    # (instruction offset, source GPR, field offset in fixed defaults object).
    early=[(80,13,34),(92,14,2),(94,13,36),(112,14,4),(114,13,38),
        (124,14,10),(126,14,12),(128,14,18),(130,14,20),(132,14,22),(134,14,24),(136,14,40)]
    middle=[(142,11,6),(144,11,8),(146,12,14),(148,12,16),(150,10,26),(152,0,28),(156,0,30),(160,0,32),(164,13,42)]
    if index==0:middle=[(138,16,44)]+middle
    else:middle=[(o-4,r,f) for o,r,f in middle]+[(162,16,44)]
    later=[(166,0,46),(174,0,48),(178,14,68),(182,14,70),(186,14,94),(190,14,96),(194,14,98),(198,14,100),
        (202,16 if index==0 else 17,50),(210,13,52),(212,13,54),(214,0,56),(218,0,58),(222,0,60),(226,0,62),(230,0,64),
        (234,13,66),(238,0,72),(242,0,74),(246,13,76),(250,12,78),(254,12,80),(258,10,82),(262,0,84),(266,0,86),
        (270,0,88),(274,12,90),(278,12,92),(282,10,102),(286,0,104),(290,0,106),(294,0,108),(298,11,110),(302,11,112),
        (306,0,114),(310,14,116),(316,14,122),(322,0,118),(326,0,120),(330,13,124),(334,0,126),(338,0,128),(342,0,130),
        (346,14 if index==0 else 16,132)]
    if index:later.append((350,14,134))
    return sorted(early+middle+later)


def specs(part,index):
    pc=STARTS[index][PARTS.index(part)];delta=80*index;s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def lui(o,r,v=0x20003000):e(o,'lui',rd=r,imm=v)
    def ai(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    def st(o,r,b,v,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    def ld(o,r,b,v):e(o,'load',rd=r,rs1=b,imm=v,width=4)
    def ret(o):e(o,'jr',rs1=1)
    if part=='initializer':
        ai(0,2,2,-32);st(2,1,2,28);st(4,10,2,12)
        for o,t in zip((6,10,14,18),STARTS[index][1:5]):e(o,'jal',rd=1,target=t)
        lui(22,15);ai(26,15,15,584+delta);ai(30,14,0,-256);st(34,14,15,2,2);st(36,0,15,4,1)
        lui(40,15);ld(44,10,2,12);ai(46,14,15,940+delta);li(50,13,-1);st(52,13,14,2,1)
        ld(54,1,2,28);st(56,10,15,940+delta,1);li(60,11,5);ai(62,2,2,32);e(64,'jal',rd=0,target=STARTS[index][5])
    elif part=='defaults':
        for o,v,w in ((0,-207,1),(8,-208,1),(16,-232,4),(24,-228,4),(32,-224,4),(40,-220,4),(48,-236,4),(56,-240,4),(64,616,2)):
            lui(o,15);st(o+4,0,15,v+delta,w)
        ai(72,13,0,900);ai(76,15,15,616+delta);lui(82,13,0xffffc000);ai(84,14,0,180);ai(88,13,13,-1152)
        lui(96,14,0x4000);li(98,13,7);ai(100,12,0,80);ai(104,11,0,160);ai(108,10,0,2000)
        li(116,14,16);li(118,13,1);ai(120,16,0,-127);ai(170,16 if index==0 else 17,0,127)
        ai(206,14,0,460);li(314,14,20);li(320,14,-1)
        for o,r,f in default_stores(index):st(o,r,15,f,2)
        ret(350 if index==0 else 354)
    elif part=='vectors_A':
        lui(0,15);li(4,14,-1);st(6,14,15,-195+delta,1);lui(10,15);li(14,14,-2);st(16,14,15,-196+delta,1)
        for o,v,w in ((20,780,1),(28,-194,1),(36,-192,2),(44,-184,4),(52,-176,4),(60,-180,4)):
            lui(o,15);st(o+4,0,15,v+delta,w)
        lui(68,14,0x49000);lui(72,15);ai(76,15,15,-8+delta);ai(80,14,14,-330+152*index);st(84,14,15,0)
        for o,v,f in ((86,1220,4),(96,112,8),(106,-20,12),(116,28,16)):
            lui(o,14,0x48000);ai(o+4,14,14,v+152*index);st(o+8,14,15,f)
        lui(126,15,0x48000);lui(130,14);ai(134,15,15,410+152*index);st(138,15,14,-188+delta);ret(142)
    elif part=='vectors_B':
        lui(0,15);li(4,14,-1);st(6,0,15,-206+delta,1);lui(10,15);st(14,14,15,947+delta,1)
        lui(18,15);st(22,0,15,-200+delta);lui(26,14,0x47000);lui(30,15);ai(34,14,14,1456+152*index)
        st(38,0,15,-204+delta);lui(42,15);st(46,14,15,752+delta);lui(50,14,0x47000);ai(54,15,15,752+delta)
        ai(58,14,14,1512+152*index);st(62,14,15,4)
        for o,v,f in ((64,1780,8),(74,2032,12),(84,-680,16)):
            upper,low=(0x48000,-1912) if index and o==74 else (0x47000,v+152*index)
            lui(o,14,upper);ai(o+4,14,14,low);st(o+8,14,15,f)
        lui(94,14,0x47000);lui(98,15);ai(102,14,14,-538+152*index);st(106,14,15,772+delta)
        lui(110,14,0x47000);ai(114,15,15,772+delta);ai(118,14,14,-1026+152*index);st(122,14,15,4);ret(124)
    elif part=='state':
        lui(0,15);li(4,14,-1);ai(6,15,15,940+delta);st(10,14,15,5,1);st(12,14,15,6,1)
        lui(14,15);li(18,13,1);st(20,0,15,1524+delta,1);lui(24,15);st(28,13,15,1448+delta,1)
        lui(32,15);li(36,13,6);st(38,0,15,-12+delta);lui(42,15);st(46,13,15,1480+delta,2)
        lui(50,15,0x1000);ai(52,15,15,-896);lui(56,13);st(60,15,13,1490+delta,2)
        for o,r,v in ((64,0,1454),(72,0,1451),(80,14,1554)):lui(o,15);st(o+4,r,15,v+delta,1)
        lui(88,10);li(92,15,7);lui(94,14);st(98,15,14,1453+delta,1);li(102,12,6);lui(104,14);li(108,11,0)
        ai(110,10,10,1456+delta);st(114,15,14,1462+delta,1)
        e(118,'auipc',rd=6,imm=0x1ff93000);e(122,'jalr',rd=0,rs1=6,imm=-860-492*index)
    elif part=='selector':
        ai(0,15,11,-4);e(4,'slli',rd=13,rs1=15,imm=16);e(8,'srli',rd=13,rs1=13,imm=16);li(10,14,3)
        e(12,'bltu',rs1=14,rs2=13,target=pc+40);li(16,14,12);e(18,'mul',rd=15,rs1=15,rs2=14)
        lui(22,14);ai(26,14,14,800+delta);e(30,'add',rd=15,rs1=15,rs2=14)
        st(32,10,15,2,1);st(34,11,15,0,2);li(36,10,0);ret(38);li(40,10,2);ret(42)
    else:
        entry,old=role.specs('entry',index);check(pc==entry+40,'id7 outer start');s={p:f for p,f in old.items() if pc<=p<pc+16}
    return pc,s


def body(raw,part,index):
    k=PARTS.index(part);pc,s=specs(part,index);n=decode(raw,pc)
    check(set(n)==set(s),'id7 '+part+' boundaries')
    for p,f in s.items():init.g(n,p,'id7 '+part+' operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[index][k],COUNTS[index][k],HASHES[index][k]),'id7 '+part+' identity')
    edges={};calls=[];tails=[]
    for p,d in n.items():
        op=d['op'];q=[p+d['size']]
        if op=='jr':check(d['rs1']==1,'id7 ordinary RET');q=[]
        elif op=='bltu':q.append(d['target'])
        elif op in ('jal','jalr'):
            target=d['target'] if op=='jal' else (p-4+n[p-4]['imm']+d['imm'])&0xfffffffe
            row={'pc':hex(p),'target':hex(target),'rd':d['rd']}
            if d['rd']==0:tails.append(row);q=[]
            elif part=='next_outer' and p==pc+12:calls.append(row);q=[]
            else:calls.append(row)
        check(all(v in n for v in q),'id7 '+part+' closed local edges');edges[p]=q
    seen=set();active=set()
    def visit(p):
        check(p not in active,'id7 '+part+' acyclic CFG')
        if p in seen:return
        active.add(p);seen.add(p)
        for q in edges[p]:visit(q)
        active.remove(p)
    visit(pc);check(seen==set(n),'id7 '+part+' all nodes locally reachable')
    defs=sorted({d['rd'] for d in n.values() if d.get('rd',0)})
    stores=[d for d in n.values() if d['op']=='store']
    check(len(stores)==(6,75+index,14,11,12,2,0)[k],'id7 '+part+' store census')
    if part in ('defaults','vectors_A','vectors_B','state','selector'):
        check(not set(defs)&{1,2,3,4,8,9,18,19,20,21,22,23,24,25,26,27},'id7 callee no RA/SP/GP/TP/S definitions')
        check(not any(d['op']=='load' for d in n.values()),'id7 callee no source loads')
        check(not calls,'id7 callee no linked/nested calls')
        check(len(tails)==int(part=='state'),'id7 callee only state fill tail')
    if part=='initializer':
        check([(d['rs2'],d['imm']) for d in stores if d['rs1']==2]==[(1,28),(10,12)],'id7 saved RA and input ID frame')
        check(len(calls)==4 and len(tails)==1,'id7 initializer four calls and selector tail')
    return {'start':hex(pc),'bytes':len(raw),'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),'encoded_GPR_definitions':defs,
        'store_count':len(stores),'calls':calls,'tails':tails,'conditional_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},
        'complete_function':part!='next_outer','call_fallthrough_is_return_premise':True}


def fixed_intervals(part,index):
    """Explicit address expressions tied to guarded constant-base operands."""
    g=0x20003000+80*index
    if part=='defaults':
        rows=[(o+4,g+v,w) for o,v,w in ((0,-207,1),(8,-208,1),(16,-232,4),(24,-228,4),(32,-224,4),(40,-220,4),(48,-236,4),(56,-240,4),(64,616,2))]
        return rows+[(o,g+616+f,2) for o,r,f in default_stores(index)]
    if part=='vectors_A':return [(o,g+v,w) for o,v,w in ((6,-195,1),(16,-196,1),(24,780,1),(32,-194,1),(40,-192,2),(48,-184,4),(56,-176,4),(64,-180,4),(84,-8,4),(94,-4,4),(104,0,4),(114,4,4),(124,8,4),(138,-188,4))]
    if part=='vectors_B':return [(o,g+v,w) for o,v,w in ((6,-206,1),(14,947,1),(22,-200,4),(38,-204,4),(46,752,4),(62,756,4),(72,760,4),(82,764,4),(92,768,4),(106,772,4),(122,776,4))]
    if part=='state':return [(o,g+v,w) for o,v,w in ((10,945,1),(12,946,1),(20,1524,1),(28,1448,1),(38,-12,4),(46,1480,2),(60,1490,2),(68,1454,1),(76,1451,1),(84,1554,1),(98,1453,1),(114,1462,1))]
    if part=='initializer':return [(34,g+586,2),(36,g+588,1),(52,g+942,1),(56,g+940,1)]
    if part=='selector':return [(32,g+814,1),(34,g+812,2)] # caller A1=5, A0=7
    return []


def selector_domain():
    accepted=[v for v in range(65536) if ((v-4)&65535)<=3]
    check(accepted==[4,5,6,7],'id7 selector full U16 domain')
    check((5-4)*12==12 and ((5-4)&65535)==1,'id7 selector caller index1')
    # Upper16 terms vanish in the guard but not in the address expression.
    check(12*65536%2**32!=0,'id7 selector guard does not truncate address index')
    return {'U16_accepted_selectors':accepted,'U16_rejected_count':65532,'caller_selector':5,'caller_record_index':1,
        'generic_guard':'((A1-4) mod65536)<=3','generic_address':'(base+12*((A1-4) mod2^32)) mod2^32',
        'generic_guard_alone_proves_48B_extent':False,'generic_upper16_requires_extra_constraint':True}


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[]
    for i,(data,pr) in enumerate(zip(carriers,parent['profiles'])):
        d=role.DETAILS[i];pc=STARTS[i][0];g=0x20003000+80*i;ctx=0x20003000+d['ctx'];F=ctx+80
        windows={p:body(init.binding.take(data,STARTS[i][k],SIZES[i][k]),p,i) for k,p in enumerate(PARTS)}
        check(pr['cut_before_second_outer_initializer']['target']==hex(pc) and pr['cut_before_second_outer_initializer']['A0']==7,'id7 inherited input ID7')
        protected=[(ctx+1,1),(ctx+2,1),(ctx+3,1),(ctx+40,4),(paths.layout.T,4*212),(F+21,1),(F+36,4),(F+48,4),(F+68,4),
            (g+784,4),(g+792,4),(g+852,4),(g+948,1),(g+949,1),(g+856,48)]
        all_writes=[]
        for part in PARTS[:-1]:
            w=windows[part];nodes={x['pc']:x for x in w['instructions']};start=int(w['start'],16);rows=fixed_intervals(part,i)
            check({start+o for o,a,z in rows}=={p for p,x in nodes.items() if x['op']=='store' and x['rs1']!=2},'id7 '+part+' all nonframe stores have fixed intervals in caller domain')
            for o,a,z in rows:
                check(nodes[start+o]['width']==z,'id7 interval store width')
                for b,n in protected:check(paths.origin.separated(a,z,b,n),'id7 fixed write excludes protected state')
                all_writes.append({'part':part,'pc':hex(start+o),'address':hex(a),'bytes':z})
        fill=(g+1456,6)
        for b,z in protected:check(paths.origin.separated(fill[0],fill[1],b,z),'id7 six-byte fill excludes protected state')
        sn={x['pc']:x for x in windows['state']['instructions']};spc=STARTS[i][4]
        check(windows['state']['tails'][0]['target']=='0x2000039c','id7 state tail RAM fill target')
        init.g(sn,spc+108,'id7 state fill byte0',op='li',rd=11,imm=0)
        init.g(sn,spc+102,'id7 state fill6',op='li',rd=12,imm=6)
        check(sn[spc+88]['imm']+sn[spc+110]['imm']==fill[0],'id7 state fixed fill destination')
        tail=windows['selector'];tpc=STARTS[i][5];tn={x['pc']:x for x in tail['instructions']}
        te={int(p,16):[int(q,16) for q in qs] for p,qs in tail['conditional_CFG'].items()}
        routes={key:paths.chain(te,tpc,{tpc+12:tpc+off}) for key,off in (('accepted',16),('rejected',40))}
        check(len(routes['accepted'])==14 and len(routes['rejected'])==7,'id7 selector path certificates')
        check(11 not in tail['encoded_GPR_definitions'],'id7 selector preserves A1=5')
        pn={x['pc']:x for x in windows['initializer']['instructions']}
        check(pn[pc+44]['rd']==10 and pn[pc+56]['rs2']==10,'id7 reload saved input ID7')
        check(-32+12==-20 and -32+28==-4,'id7 frame projection')
        check(pn[pc+60]['imm']==5 and pn[pc+64]['target']==tpc,'id7 final caller selector5')
        record=g+800+12
        check(record==g+812 and record+3<=g+800+48,'id7 selected record1 extent')
        check(not paths.origin.separated(record,3,g+800,48),'id7 explicit modification of prior48B records')
        on={x['pc']:x for x in windows['next_outer']['instructions']};entry=d['entry']
        old=role.body(init.binding.take(data,entry,112),'entry',i);en={x['pc']:x for x in old['instructions']}
        check(en[entry+36]['target']==pc and entry+40==STARTS[i][6],'id7 return to next outer window')
        check(on[entry+48]['target']==d['reg'] and on[entry+52]['target']==d['outer_init'][2],'id7 next registration and cut targets')
        handler=0x4b000+d['outer_lows'][2];check(on[entry+40]['imm']+on[entry+44]['imm']==handler,'id7 next handler formation')
        reg=registration.body(init.binding.take(data,d['reg'],48),i);check(11 not in reg['encoded_GPR_definitions'],'id7 next registration preserves A1')
        entry8=paths.layout.T+32;check(8<14 and entry8+4<=paths.layout.T+14*4,'id7 entry8 extent')
        for b,z in protected[:4]+[(record,3)]:check(paths.origin.separated(entry8,4,b,z),'id7 next table write excludes live slots')
        profiles.append({'label':pr['label'],'bodies':windows,'inherited_entry':pr['cut_before_second_outer_initializer'],
            'fixed_writes':all_writes,'fixed_write_count':len(all_writes),'protected_intervals':[{'address':hex(a),'bytes':z} for a,z in protected],
            'frames_relative_initializer_entry_SP':{'local_SP':-32,'saved_ID7':-20,'saved_RA':-4,'SP_before_selector_tail':0},
            'callee_contracts':{'defaults':'straight-line stores; no loads/calls/frame; defines A0=2000 so caller must reload saved ID',
                'vectors_A':'straight-line defaults and six code-pointer stores, never invokes them','vectors_B':'straight-line defaults and seven code-pointer stores, never invokes them',
                'state':'fixed stores then unlinked tail fill; no RA/SP/GP/S definitions',
                'fill_boundary':{'pc':hex(spc+122),'target':'0x2000039c','A0':hex(fill[0]),'A1':0,'A2':6,'conditional_return_to':hex(pc+22)},
                'required_fill_contract':'normal return through carried RA to initializer+22; SP/frame/GP/S and required code/state retained; valid nonalias write extent and no external interference. Actual installed implementation remains unknown'},
            'profile_default_difference':{'object':hex(g+616),'last_field132':65535 if i==0 else 65409,'field134_present':bool(i),'field134_value':65535 if i else None},
            'conditional_local_publication':[{'address':hex(g+586),'bytes':2,'value':65280},{'address':hex(g+588),'bytes':1,'value':0},
                {'address':hex(g+942),'bytes':1,'value':255},{'address':hex(g+940),'bytes':1,'value':7}],
            'selector_contract':{'paths':routes,'input_A0':7,'input_A1':5,'record_index':1,'record_base':hex(record),
                'ordered_writes':[{'address':hex(record+2),'bytes':1,'value':7},{'address':hex(record),'bytes':2,'value':5}],
                'ordinary_RET_reply_A0':0,'ordinary_RET_reply_A1':5,'return_to_outer':hex(entry+40),'parent_has_no_ordinary_RET':True,
                'prior_record_block_modified':True,'remaining_record_bytes_not_proved_unchanged_against_external_writers':True},
            'conditional_next_registration':{'pc':hex(entry+48),'target':hex(d['reg']),'handler':hex(handler),'fresh_count_premise':8,'fresh_capacity_premise':'>=14','fresh_table_premise':hex(paths.layout.T),
                'entry8_address':hex(entry8),'new_count':9,'reply_A0':8,'reply_A1':5,'reply_A2':9},
            'cut_before_third_outer_initializer':{'pc':hex(entry+52),'target':hex(d['outer_init'][2]),'A0':8,'A1':5,'A2':9},
            'completion_premises':'valid original code and RAM/frame accesses, physical nonalias, matching provider return/preservation contract at state fill, and no interfering writers. Four direct-call bodies now guarded; actual fill and hardware are not executed/proved',
            'actual_installed_binding_proved':False,'actual_callback_or_provider_execution':False})
    return {'schema':'TSL9-ID7-initialization-static-v1','profile':parent['profile'],'APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'selector_domain':selector_domain(),
        'scope':'full two-profile68B initializer, all four direct callees,44B selector tail and16B outer join;1756B/511 operand-guarded instructions; V140 defaults independently guarded, not treated as relocation',
        'boundary':'all local initialization paths and saved-ID publication closed conditional on sole6-byte fill return/preservation; selector5 writes record1, returns0/A1=5; fresh metadata8/c>=14/T admits nextID8/count9, stop before4a7d6/4a86e',
        'remaining':['actual state-fill provider and physical/frame preservation','third initializer4a7d6/4a86e and callback-pointer consumers','all writers/publication ordering/record lifetime and hardware progress'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    count=0
    for i,data in enumerate(carriers):
        for k,part in enumerate(PARTS):
            pc=STARTS[i][k];raw=init.binding.take(data,pc,SIZES[i][k])
            for p,d in decode(raw,pc).items():
                at=p-pc;z=d['size'];buf=bytearray(raw)
                buf[at:at+z]=(int.from_bytes(buf[at:at+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
                try:body(buf,part,i)
                except RuntimeError as e:check(str(e).startswith('id7 '+part+' operand '),'id7 specified mutation guard '+str(e))
                else:raise RuntimeError('id7 mutation escaped')
                count+=1
    check(count==511,'id7 mutation census');selector_domain()
    check(sum(sum(x) for x in SIZES)==1756,'id7 full source byte census')
    print('PASS:511 operand mutations rejected;65536 selector-domain cases;two complete initializer/callee/tail CFGs;1756 original bytes')


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
    else:check(OUT.read_bytes()==output,'id7 exact ledger replay')
    print('PASS:ID7 frame/source and fixed-write exclusions;record1 update;conditional ID8/count9 return join;exact ledger')
    print('PASS:NO target execution/emulation;actual fill/provider binding and callback lifetime UNPROVED')


if __name__=='__main__':main()
