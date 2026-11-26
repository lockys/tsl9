"""Offline ID8 initializer, low2-count resource tail and ID9 return boundary.

Strict original operands/CFG plus closed-form integer/interval certificates.
No target ISA, RAM/register machine, allocator, fill or callback execution.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_id7_initialization_static as previous

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
paths,role,registration=previous.paths,previous.role,previous.registration
leaves=previous.previous
origin=leaves.previous
OUT=Path(__file__).with_name('v4160-id8-initialization-static.json')
PARTS=('initializer','clear','resources','hook_A','hook_B','next_outer')
STARTS=((0x4a7d6,0x445d4,0x4d068,0x4a1f6,0x44694,0x6dd4e),
        (0x4a86e,0x44668,0x4d100,0x4a28e,0x44728,0x6df3e))
SIZES=(50,18,266,10,10,16)
COUNTS=(16,5,89,3,3,4)
HASHES=(('b14c1ddd0b086972b5386eb4112a6927f54e9ec36f4017c4ca5a17c4659b702f','fd4cc09ba5622999635c34e60942d4b7a61a81e1cd6c14472bd15883d22d4b4b',
 '617dffb012fcb90099d8e7cb62811ab320dc967317023d94953777e8c50b3798','159d82cf512659cd7f405b2b2ed03781b50d82b79b9cbd9f5796044ca6a931c5',
 '4cb8d2c5c8b853588e39663a672d5cbc98b1f4906fafe74d768d7eaeddf4bf53','1357dd30e5e516dd0bad41de8b5b3b07dc1e17b96996c699097ad52392548e8d'),
 ('92506d5a20805a93f9958d30ffb66d65abaf1fa9ac48acf3ee9054049863167b','13dd6ad6f5980b420b319672e1718768ed6685ac08e9376955751a802584c2fb',
 '9aec0b7794f59c0dfbc53d0c33b6f04824ec8c840f09929ead7df27921ed6a38','1ce8866decbd97843d6de439820d265e35f3dd487e346b6fef448cfd92a1be50',
 'a70c95baccd365a980f16d30dbd94329cbec959c879a66e0942dde7730a09645','3e19fa491f9f3e0d999fc60c33090acac5da5c73e7cba9e6d974dc3b4a66227b'))


def specs(part,index):
    pc=STARTS[index][PARTS.index(part)];delta=80*index;s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def lui(o,r,v=0x20003000):e(o,'lui',rd=r,imm=v)
    def ai(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    def ld(o,r,b,v,w=4):e(o,'load',rd=r,rs1=b,imm=v,width=w)
    def st(o,r,b,v,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    def binary(o,op,r,a,b):e(o,op,rd=r,rs1=a,rs2=b)
    def branch(o,op,a,b,t):e(o,op,rs1=a,rs2=b,target=pc+t)
    def ret(o):e(o,'jr',rs1=1)
    def pair(o,low):e(o,'auipc',rd=1,imm=0x1ffb3000);e(o+4,'jalr',rd=1,rs1=1,imm=low-152*index)
    if part=='initializer':
        ai(0,2,2,-32);st(2,1,2,28);st(4,10,2,12);e(6,'jal',rd=1,target=STARTS[index][1]);ld(10,10,2,12)
        lui(12,15);st(16,0,15,-148+delta);lui(20,15);st(24,0,15,-144+delta);li(28,11,4)
        lui(30,15);st(34,10,15,941+delta,1);e(38,'jal',rd=1,target=0x4d9ec+152*index)
        ld(42,1,2,28);ai(44,2,2,32);e(46,'jal',rd=0,target=STARTS[index][2])
    elif part in ('clear','hook_A','hook_B'):
        lui(0,15)
        if part=='clear':st(4,0,15,-252+delta);lui(8,15);st(12,0,15,-256+delta);ret(16)
        else:st(4,10,15,(-144 if part=='hook_A' else -252)+delta);ret(8)
    elif part=='resources':
        ai(0,2,2,-32);st(2,9,2,20);lui(4,9);ai(8,9,9,940+delta);st(12,8,2,24);ld(14,10,9,9,1)
        lui(16,8);ai(20,8,8,-116+delta);lui(24,15);lui(28,14);st(32,1,2,28);st(34,18,2,16);st(36,19,2,12)
        st(38,0,8,0);st(42,0,15,-112+delta);st(46,0,14,-128+delta);e(50,'beqz',rs1=10,target=pc+184)
        ai(52,18,15,-112+delta);ai(56,15,0,194);binary(60,'mul',10,10,15);lui(64,11,0x4000);ai(66,11,11,1793)
        ai(70,19,14,-128+delta);ai(74,10,10,6);e(76,'slli',rd=10,rs1=10,imm=16);e(78,'srli',rd=10,rs1=10,imm=16)
        pair(80,-120);ld(88,12,9,9,1);ai(90,15,0,194);li(94,11,0);binary(96,'mul',12,12,15);st(100,10,8,0)
        ai(102,12,12,6);pair(104,716);ld(112,15,8,0);ld(114,14,9,9,1);li(116,11,0);ai(118,13,15,184);li(122,10,-1)
        branch(124,'bltu',11,14,236);ai(128,13,0,184);binary(132,'mul',13,14,13);li(136,12,0);li(138,11,-1)
        ai(140,14,14,1);binary(142,'add',15,15,13);st(144,15,18,0);e(148,'mv',rd=13,rs2=15)
        st(150,11,13,0,2);st(152,11,13,3,1);st(154,11,13,2,1);st(156,0,13,4,1)
        ai(160,12,12,1);ai(162,13,13,6);branch(164,'bltu',12,14,150);li(168,13,-2);st(170,13,15,0,2)
        li(172,13,6);binary(174,'mul',14,14,13);binary(178,'add',15,15,14);st(180,15,19,0)
        for o,low,target in ((184,-1724,STARTS[index][3]),(196,-1286,STARTS[index][4]),(208,-1882,0x4efe2+152*index)):
            lui(o,10,0x4c000);ai(o+4,10,10,low+152*index);e(o+8,'jal',rd=1,target=target)
        for o,r,v in ((220,1,28),(222,8,24),(224,9,20),(226,18,16),(228,19,12)):ld(o,r,2,v)
        li(230,10,0);ai(232,2,2,32);ret(234)
        st(236,10,13,-184,2);ai(240,12,13,-180);st(244,0,12,0,2);st(248,0,12,8)
        ai(252,12,12,12);branch(254,'bne',12,13,244);ai(258,11,11,1);ai(260,13,13,184);e(264,'jump',target=pc+124)
    else:
        entry,old=role.specs('entry',index);check(pc==entry+56,'id8 next outer start');s={p:f for p,f in old.items() if pc<=p<pc+16}
    return pc,s


def body(raw,part,index):
    k=PARTS.index(part);pc,s=specs(part,index);n=decode(raw,pc)
    check(set(n)==set(s),'id8 '+part+' boundaries')
    for p,f in s.items():init.g(n,p,'id8 '+part+' operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[k],HASHES[index][k]),'id8 '+part+' identity')
    edges={};calls=[];tails=[]
    for p,d in n.items():
        op=d['op'];q=[p+d['size']]
        if op=='jr':check(d['rs1']==1,'id8 ordinary RET');q=[]
        elif op in ('beqz','bltu','bne'):q.append(d['target'])
        elif op=='jump':q=[d['target']]
        elif op in ('jal','jalr'):
            if op=='jal':target=d['target']
            else:
                a=n[p-4];check(a['op']=='auipc' and a['rd']==d['rs1'],'id8 adjacent provider pair')
                target=(p-4+a['imm']+d['imm'])&0xfffffffe
            row={'pc':hex(p),'target':hex(target),'rd':d['rd']}
            if d['rd']==0:tails.append(row);q=[]
            else:
                calls.append(row)
                if part=='next_outer' and p==pc+12:q=[]
        check(all(v in n for v in q),'id8 '+part+' local CFG closed');edges[p]=q
    seen={pc};todo=[pc]
    while todo:
        for q in edges[todo.pop()]:
            if q not in seen:seen.add(q);todo.append(q)
    check(seen==set(n),'id8 '+part+' all nodes locally reachable')
    defs=sorted({d['rd'] for d in n.values() if d.get('rd',0)})
    stores=[d for d in n.values() if d['op']=='store'];check(len(stores)==(5,2,19,1,1,0)[k],'id8 '+part+' store census')
    if part in ('clear','hook_A','hook_B'):
        check(defs==[15] and not calls and not tails,'id8 pure leaf GPR/call census')
        check(not any(d['op']=='load' for d in n.values()),'id8 pure leaf no source loads')
    if part=='initializer':
        check([(d['rs2'],d['imm']) for d in stores if d['rs1']==2]==[(1,28),(10,12)],'id8 input frame exact')
        check(len(calls)==2 and len(tails)==1,'id8 initializer two calls and tail')
    if part=='resources':
        check([(d['rs2'],d['imm']) for d in stores if d['rs1']==2]==[(9,20),(8,24),(1,28),(18,16),(19,12)],'id8 resource frame exact')
        check([(d['rd'],d['imm']) for d in n.values() if d['op']=='load' and d['rs1']==2]==[(1,28),(8,24),(9,20),(18,16),(19,12)],'id8 resource restores exact')
        check(len(calls)==5 and not tails,'id8 resource five calls/RET')
        check([(p-pc,q-pc) for p,qs in edges.items() for q in qs if q<p]==[(164,150),(254,244),(264,124)],'id8 exact local backedge census')
        check(not any(d['op'] in ('beqz','bltu','bne') for p,d in n.items() if pc+84<p<pc+124),'id8 no local allocator null guard')
    return {'start':hex(pc),'bytes':len(raw),'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),'encoded_GPR_definitions':defs,
        'store_count':len(stores),'calls':calls,'tails':tails,'conditional_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},
        'complete_function':part!='next_outer','call_fallthrough_is_return_premise':True}


def arithmetic():
    rows=[]
    for n in range(256):
        request=194*n+6;used=184*n+6*(n+1)
        check(request<=65535 and (request&65535)==request,'id8 U8 request low16 no truncation')
        check(used==190*n+6 and used+4*n==request,'id8 equal-count layout bound')
        check(180//12==15 and all(4+12*j+8+4<=184 for j in range(15)),'id8 inner15 record extents')
        check(0<n+1<=256 and 6*(n+1)<=1536,'id8 post-record queue bound')
        rows.append({'fresh_count':n,'request_bytes':request,'equal_count_layout_bytes':used,'unused_request_bytes':4*n,
            'outer_iterations':n,'inner_iterations_per_record':15,'queue_iterations':n+1})
    check(rows[2]['request_bytes']==394 and rows[2]['equal_count_layout_bytes']==386,'id8 APP low2 case')
    return rows


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[]
    for i,(data,pr) in enumerate(zip(carriers,parent['profiles'])):
        g=0x20003000+80*i;d=role.DETAILS[i];ctx=0x20003000+d['ctx'];F=ctx+80;pc=STARTS[i][0];rpc=STARTS[i][2]
        windows={p:body(init.binding.take(data,STARTS[i][k],SIZES[k]),p,i) for k,p in enumerate(PARTS)}
        check(pr['cut_before_third_outer_initializer']=={'pc':hex(d['entry']+52),'target':hex(pc),'A0':8,'A1':5,'A2':9},'id8 inherited exact inputs')
        selector=previous.body(init.binding.take(data,0x4d9ec+152*i,44),'selector',i)
        callback=leaves.body(init.binding.take(data,0x4efe2+152*i,42),'callback_register',i)
        source=origin.body(init.binding.take(data,origin.STARTS[i][1],160),'resources',i)
        sn={x['pc']:x for x in source['instructions']};spc=int(source['start'],16)
        init.g(sn,spc+16,'id8 original low2 source',op='andi',rd=15,rs1=10,imm=3)
        init.g(sn,spc+26,'id8 original low2 destination',op='store',rs1=8,rs2=15,imm=9,width=1)
        check(sn[spc+12]['imm']+sn[spc+20]['imm']+9==g+949,'id8 low2 source address join')
        rn={x['pc']:x for x in windows['resources']['instructions']};pn={x['pc']:x for x in windows['initializer']['instructions']}
        check([rn[rpc+o]['imm'] for o in (14,88,114)]==[9,9,9] and rn[rpc+4]['imm']+rn[rpc+8]['imm']+9==g+949,'id8 three fresh loads same low2 slot')
        check(any(int(x['address'],16)==g+949 and x['bytes']==1 for x in pr['protected_intervals']),'id8 prior ID7 fixed stores exclude low2 source')
        protected=[(ctx+1,1),(ctx+2,1),(ctx+3,1),(ctx+40,4),(paths.layout.T,4*212),(F+21,1),(F+36,4),(F+48,4),(F+68,4),(g+948,1),(g+949,1)]
        fixed=[('clear',4,g-252,4),('clear',12,g-256,4),('initializer',16,g-148,4),('initializer',24,g-144,4),('initializer',34,g+941,1),
            ('resources',38,g-116,4),('resources',42,g-112,4),('resources',46,g-128,4),('resources',100,g-116,4),
            ('resources',144,g-112,4),('resources',180,g-128,4),('hook_A',4,g-144,4),('hook_B',4,g-252,4),('selector',32,g+802,1),('selector',34,g+800,2)]
        for part,o,a,z in fixed:
            start=int(selector['start'],16) if part=='selector' else STARTS[i][PARTS.index(part)]
            nodes={x['pc']:x for x in (selector if part=='selector' else windows[part])['instructions']}
            check(nodes[start+o]['op']=='store' and nodes[start+o]['width']==z,'id8 fixed store link')
            for b,w in protected:check(paths.origin.separated(a,z,b,w),'id8 fixed store excludes protected state')
        for k in range(12):
            for b,z in protected:check(paths.origin.separated(g+856+4*k,4,b,z),'id8 callback store excludes task/source fields')
        check(pn[pc+28]['imm']==4 and pn[pc+34]['rs2']==10 and pn[pc+10]['rd']==10,'id8 saved ID8 then selector4')
        check(pn[pc+38]['target']==int(selector['start'],16) and pn[pc+46]['target']==rpc and pn[pc+46]['rd']==0,'id8 selector return/tail joins')
        check(pn[pc+44]['imm']==32 and rn[rpc]['imm']==-32,'id8 frame released then reused, not still-live saved ID slot')
        re={int(p,16):[int(q,16) for q in qs] for p,qs in windows['resources']['conditional_CFG'].items()}
        zero=paths.chain(re,rpc,{rpc+50:rpc+184})
        check(zero[-1]==hex(rpc+234) and not {hex(rpc+o) for o in (80,84,104,108,124,150,244)}&set(zero),'id8 zero-count route excludes providers and payload loops')
        check([x['target'] for x in windows['resources']['calls']]==['0x20000040','0x2000039c',hex(STARTS[i][3]),hex(STARTS[i][4]),callback['start']],'id8 exact call inventory')
        pointers=[0x4c000+low+152*i for low in (-1724,-1286,-1882)]
        check([rn[rpc+o]['imm']+rn[rpc+o+4]['imm'] for o in (184,196,208)]==pointers,'id8 three callback source pointers')
        check(rn[rpc+230]['op']=='li' and rn[rpc+230]['imm']==0,'id8 final reply independent of registration success')
        on={x['pc']:x for x in windows['next_outer']['instructions']};entry=d['entry'];outer=role.body(init.binding.take(data,entry,112),'entry',i)
        en={x['pc']:x for x in outer['instructions']}
        check(en[entry+52]['target']==pc and entry+56==STARTS[i][5],'id8 resource RA returns to next outer window')
        reg=registration.body(init.binding.take(data,d['reg'],48),i);check(11 not in reg['encoded_GPR_definitions'],'id8 next registration preserves callback leaf A1')
        check(on[entry+64]['target']==d['reg'] and on[entry+68]['target']==d['outer_init'][3],'id8 next registration and fourth initializer targets')
        handler=0x50000+d['outer_lows'][3];check(on[entry+56]['imm']+on[entry+60]['imm']==handler,'id8 next handler overrides returned0')
        entry9=paths.layout.T+36;check(9<14 and entry9+4<=paths.layout.T+14*4,'id8 entry9 admitted extent')
        for b,z in protected[:4]:check(paths.origin.separated(entry9,4,b,z),'id8 entry9 excludes metadata')
        profiles.append({'label':pr['label'],'bodies':windows,'reused_selector_sha256':selector['sha256'],'reused_callback_register_sha256':callback['sha256'],
            'inherited_entry':pr['cut_before_third_outer_initializer'],'source_low2':{'address':hex(g+949),'original_F21_address':hex(F+21),'original_write_PC':hex(spc+26),
                'formula':'b&3; different from adjacent q=(b&3)+(b>>2)','retained_domain':[0,3],'fresh_domain_without_retention':[0,255],
                'APP_source_case':'if source b14 and all required low2-slot/provider/state retention premises hold, N2/request394/layout386; actual installed setting not proved'},
            'fixed_writes':[{'part':part,'pc_offset':o,'address':hex(a),'bytes':z} for part,o,a,z in fixed],
            'saved_ID_publication':{'frame_bytes':32,'saved_ID_entry_SP_offset':-20,'saved_RA_entry_SP_offset':-4,'ID_byte':hex(g+941),'ID_value':8,
                'selector':4,'record0_halfword':{'address':hex(g+800),'value':4},'record0_IDbyte':{'address':hex(g+802),'value':8},'prior48B_record_block_modified':True},
            'resource_frame':{'bytes':32,'saves':['RA','S0','S1','S2','S3'],'restores_before_RET':True,'reuses_released_initializer_frame':True},
            'zero_count_case':{'additional_premise':'entry fresh byteN=0; code/frame/fixed/table accesses valid and nonalias; no interfering writers',
                'path':zero,'no_allocator_fill_or_payload_loop':True,'cleared_words':[hex(g-116),hex(g-112),hex(g-128)],'three_callback_publication_calls_still_run':True},
            'nonzero_count_case':{'cut_before_allocator':{'pc':hex(rpc+84),'target':'0x20000040','A0':'194*N1+6','A1':'0x4701'},'request_range':[200,49476],
                'fill_length':'194*N2+6 whereN2=freshU8; range6..49476','loop_count':'N3=freshU8 after fill,0..255','fresh_N1_N2_N3_equality_proved':False,'allocator_null_guard':False,
                'record_stride':184,'record_header_halfword':65535,'inner_iterations':15,'inner_halfwords':'record+4+12*j=0, j0..14','inner_words':'record+12+12*j=0, j0..14',
                'queue_count':'N3+1,1..256','queue_stride':6,'queue_writes':'halfword+0=ffff, byte+3=ff, byte+2=ff, byte+4=0; first entry halfword overwrittenfffe',
                'middle_pointer_store':hex(g-112),'middle_pointer':'P+184*N3','end_pointer_store':hex(g-128),'end_pointer':'P+190*N3+6',
                'equal_count_layout':'if N1=N2=N3=N, used190*N+6 <= requested194*N+6, margin4*N; valid nonnull nonalias payload extent, arithmetic/access and provider preservation remain required'},
            'callback_publication':{'hook_A':{'address':hex(g-144),'pointer':hex(pointers[0])},'hook_B':{'address':hex(g-252),'pointer':hex(pointers[1])},
                'callback_table':hex(g+856),'third_pointer':hex(pointers[2]),'callback_register_body':callback['start'],'callbacks_invoked':False,
                'tail_final_A0':0,'registration_reply_ignored':True,'tail_final_A1':'0 on insertion; slot11 last observed nonzero word if full','tail_final_A2':12},
            'conditional_next_registration':{'pc':hex(entry+64),'handler':hex(handler),'fresh_count_premise':9,'fresh_capacity_premise':'>=14','fresh_table_premise':hex(paths.layout.T),
                'entry9_address':hex(entry9),'new_count':10,'reply_A0':9,'reply_A2':10,'A1':'preserved callback-register result',
                'return_premise':'tail ordinaryRET with valid nonalias frame/code/table; nonzero entry additionally requires allocator/fill success, extents and required count/state preservation'},
            'cut_before_fourth_outer_initializer':{'pc':hex(entry+68),'target':hex(d['outer_init'][3]),'A0':9,'A2':10,'A1':'0 on insertion; slot11 last observed nonzero word if full'},
            'actual_installed_binding_proved':False,'actual_payload_lifetime_proved':False})
    return {'schema':'TSL9-ID8-initialization-static-v1','profile':parent['profile'],'APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'arithmetic_domain':arithmetic(),
        'scope':'per candidate full50B initializer/18B clear/266B resource tail/two10B setters/16B outer join:740B/240 new guarded instructions; existing44B selector and42B callback-register reused',
        'boundary':'freshN0 closes pure-RAM return and publications conditional on valid nonalias frame/code/table; freshNnonzero stops at allocator, with full local CFG and conditional equal-count layout certificate. Fresh metadata9/c>=14/T joins nextID9/count10',
        'remaining':['actual allocator/fill bindings, success, payload/frame preservation and fresh-count retention','fourth initializer50412/504ac and three newly stored callback consumers','all writers/lifetimes/asynchronous ordering and hardware progress'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    mutations=0
    for i,data in enumerate(carriers):
        for k,part in enumerate(PARTS):
            pc=STARTS[i][k];raw=init.binding.take(data,pc,SIZES[k])
            for p,d in decode(raw,pc).items():
                at=p-pc;z=d['size'];buf=bytearray(raw)
                buf[at:at+z]=(int.from_bytes(buf[at:at+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
                try:body(buf,part,i)
                except RuntimeError as e:check(str(e).startswith('id8 '+part+' operand '),'id8 specified mutation guard '+str(e))
                else:raise RuntimeError('id8 mutation escaped')
                mutations+=1
    check(mutations==240 and sum(SIZES)*2==740,'id8 instruction/byte census');arithmetic()
    check({b&3 for b in range(256)}==set(range(4)) and (14&3)==2,'id8 retained low2 domain')
    print('PASS:240 operand mutations rejected;740 original bytes;256 fresh-count layout domains;low2 source0..3;zero-count CFG excludes providers')


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
    else:check(OUT.read_bytes()==output,'id8 exact ledger replay')
    print('PASS:ID8 saved source/record0 publication;two hook stores and callback-table insertion attempt;conditional ID9/count10 return join;exact ledger')
    print('PASS:NO target execution/emulation;actual providers/count retention/payload lifetime UNPROVED')


if __name__=='__main__':main()
