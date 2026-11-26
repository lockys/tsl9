"""Offline ID10 allocation/NV initialization and conditional ID11 boundary.

Original operands/CFG, LLVM encoding vectors and integer/interval checks.
No target ISA, mutable RAM/register model, NV, allocator or fill execution.
"""
import argparse
import json
import re
from hashlib import sha256
from pathlib import Path
import check_v4160_id9_vector_dispatch_static as previous

init,sparse,check=previous.init,previous.sparse,previous.check
paths,role,registration=previous.paths,previous.role,previous.registration
OUT=Path(__file__).with_name('v4160-id10-nv-initialization-static.json')


def decode(raw,pc):
    nodes={};off=0
    while off<len(raw):
        h=int.from_bytes(raw[off:off+2],'little');z=2 if h&3!=3 else 4;chunk=raw[off:off+z]
        check(len(chunk)==z,'id10 complete instruction')
        if z==2 and h&0xf863==0x8040:
            d=dict(pc=pc+off,size=2,bytes=chunk.hex(),op='store',rs1=2,rs2=8+(h>>2&7),imm=h>>7&15,width=1,mnemonic='qk.c.sbsp')
        else:d=previous.decode(chunk,pc+off)[pc+off]
        nodes[pc+off]=d;off+=z
    return nodes


def stack_encoding_source():
    sources,_=init.timer.source_contract();td=(init.timer.REF/'RISCVInstrInfoXwch.td').read_text(encoding='utf-8')
    for fragment in ('let Inst{15-11} = 0b10000;','let Inst{6-5} = funct2;','let Inst{4-2} = rd_rs2;',
        'let Inst{1-0} = 0b00;','def QK_C_SBSP : QKStackInst<0b10, (outs),','let Inst{10-7} = imm;'):
        check(fragment in td,'id10 cached LLVM SBSP field evidence')
    lines=(init.timer.REF/'xwchc-valid.s').read_text(encoding='utf-8').splitlines();vectors=[]
    for i,line in enumerate(lines):
        m=re.fullmatch(r'# CHECK-ASM-AND-OBJ: qk\.c\.sbsp s0, (\d+)\(sp\)',line)
        if not m:continue
        x=re.fullmatch(r'# CHECK-ASM: encoding: \[0x([0-9a-f]{2}),0x([0-9a-f]{2})\]',lines[i+1]);check(x is not None,'id10 official SBSP vector')
        raw=bytes(int(v,16) for v in x.groups());n=decode(raw,0)[0]
        check((n['op'],n['rs1'],n['rs2'],n['imm'],n['width'])==('store',2,8,int(m[1]),1),'id10 official SBSP decode')
        vectors.append({'word':raw.hex(),'register':8,'offset':int(m[1]),'source_line':i+1})
    check(len(vectors)==6,'id10 six official SBSP vectors')
    for r in range(8,16):
        for imm in range(16):
            word=0x8040|((r-8)<<2)|(imm<<7);d=decode(word.to_bytes(2,'little'),0)[0]
            check((d['rs2'],d['imm'],d['rs1'],d['width'])==(r,imm,2,1),'id10 128 SBSP field combinations')
    return {'sources_reused':sources,'official_SBSP_vectors':vectors,'field_combinations':128,'actual_saved_byte':'dc87 -> SB A5,15(SP), not a halfword or floating store'}


PARTS=('initializer','allocate','load','save','next_outer')
STARTS=((0x6c300,0x6b928,0x6b286,0x6b25e,0x6dd6e),(0x6c4ec,0x6bb0c,0x6b46a,0x6b442,0x6df5e))
SIZES=(28,470,178,40,16)
COUNTS=(10,138,60,15,4)
HASHES=(('07bd8139f587c11ff1557335dbf0f2fa06c43602b083702e200a448d16b62bff','37f7c6ac4278fad29e51ea71ee422ede88c167df8698b623424df1e9ea24e52b',
 '07a59d322dbfbe6c912823f8d6af31d59a81da56f06cbb855cc53d32982c3d8a','7771120ca54f6787dc9faa7a9ccdfd526fd582b88faa56c3ed18df25dd12f380','5315f2f12237cd46da6ea85a8aa7c4e5e49be5424f183ef971a353bbbaee5f2b'),
 ('2308cd171eed6430f343434c7ad6edfa68984ef57e27fbb86fea2df1cb963f62','57da42cb66e20360178b3e4ac613822657d908144f6d44762aada426920010a4',
 'a77049b6c989bf680fd2a72f596ee8be82b268015bd2df08f1ad0fc8de542e4f','72fd10439c3021321c8ee57a682cf38e60a9c92c3bbcff4b760542b9c2028ff4','ba276bae712fef0ce31d1a31f6f5185a7696e9662fdec2e7286d83ec60cdf6f0'))


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
    def bz(o,r,t):e(o,'beqz',rs1=r,target=pc+t)
    def ret(o):e(o,'jr',rs1=1)
    def call(o,t):e(o,'jal',rd=1,target=t)
    def pair(o,upper,low):e(o,'auipc',rd=1,imm=upper);e(o+4,'jalr',rd=1,rs1=1,imm=low)
    if part=='initializer':
        ai(0,2,2,-32);st(2,1,2,28);st(4,10,2,12);call(6,STARTS[index][1]);ld(10,10,2,12);ld(12,1,2,28)
        lui(14,15);st(18,10,15,-62+delta,1);ai(22,2,2,32);e(24,'jal',rd=0,target=STARTS[index][2])
    elif part=='allocate':
        ai(0,2,2,-32);st(2,19,2,12);lui(4,15);li(8,14,-1);lui(10,19);st(14,8,2,24);st(16,9,2,20)
        st(18,18,2,16);st(20,1,2,28);st(22,20,2,8);st(24,14,15,-62+delta,1);ai(28,15,19,492+delta)
        ld(32,10,15,14,1);lui(34,18);lui(38,8);ai(42,9,18,-68+delta);ai(46,11,0,66);e(50,'slli',rd=10,rs1=10,imm=4)
        st(52,0,8,-63+delta,1);st(56,0,9,0);pair(60,0x1ff94000,1756-484*index);st(68,10,9,0);ai(70,8,8,-63+delta)
        bz(74,10,114);ai(76,19,19,492+delta);ld(80,15,19,14,1);ai(84,18,18,-68+delta);li(88,9,0);st(90,15,8,0,1)
        ld(92,15,8,0,1);branch(94,'bltu',9,15,392);ld(98,14,19,8);lui(102,15);branch(106,'beq',14,0,460);st(110,0,15,1443+delta,1)
        ld(114,14,8,0,1);lui(116,15);li(120,8,1);st(122,14,15,-70+delta,1);lui(126,15);st(130,0,15,-36+delta)
        lui(134,15);st(138,8,15,-266+delta,1);lui(142,10);lui(146,15);st(150,0,15,-51+delta,1);li(154,12,16)
        lui(156,15);li(160,11,0);ai(162,10,10,380+delta);st(166,0,15,-49+delta,1)
        pair(170,0x1ff94000 if index else 0x1ff95000,2022 if index else -1590)
        lui(178,15);ai(182,9,0,119);st(186,0,15,-52+delta,1);lui(190,15);st(194,9,15,-50+delta,1)
        lui(198,15);st(202,0,15,-48+delta);lui(206,15);st(210,8,15,-269+delta,1);lui(214,15);st(218,0,15,-60+delta,1)
        lui(222,10);lui(226,15);st(230,0,15,-59+delta,1);li(234,12,16);lui(236,15);li(240,11,0)
        ai(242,10,10,364+delta);st(246,0,15,-57+delta,1);pair(250,0x1ff94000 if index else 0x1ff95000,1942 if index else -1670)
        lui(258,15);st(262,9,15,-58+delta,1);lui(266,15);st(270,0,15,-56+delta);lui(274,15);st(278,0,15,-61+delta,1)
        li(282,14,5);lui(284,15);st(288,14,15,-271+delta,1);lui(292,15);li(296,14,16);st(298,14,15,-267+delta,1)
        lui(302,15);st(306,0,15,-44+delta,1);li(310,14,2);lui(312,15);st(316,14,15,-270+delta,1)
        for o,v,w,r in ((320,-28,4,0),(328,-32,4,0),(336,-71,1,0),(344,-64,1,0),(352,-272,1,8),(360,-265,1,8),(368,-268,1,8)):
            lui(o,15);st(o+4,r,15,v+delta,w)
        for o,r,v in ((376,1,28),(378,8,24),(380,9,20),(382,18,16),(384,19,12),(386,20,8)):ld(o,r,2,v)
        ai(388,2,2,32);ret(390)
        ld(392,10,18,0);e(396,'slli',rd=20,rs1=9,imm=4);li(400,12,6);ai(402,11,0,255);binary(406,'add',10,10,20)
        pair(408,0x1ff94000 if index else 0x1ff95000,1784 if index else -1828)
        ld(416,10,18,0);li(420,12,6);ai(422,11,0,255);binary(426,'add',10,10,20);ai(428,10,10,6)
        pair(430,0x1ff94000 if index else 0x1ff95000,1762 if index else -1850)
        ld(438,15,18,0);ai(442,9,9,1);e(444,'andi',rd=9,rs1=9,imm=255);binary(448,'add',15,15,20)
        st(450,0,15,12,2);st(454,0,15,14,1);e(458,'jump',target=pc+92);ai(460,14,0,-128);st(464,14,15,1443+delta,1);e(468,'jump',target=pc+114)
    elif part=='load':
        ai(0,2,2,-32)
        for o,r,v in ((2,8,24),(4,19,12),(6,20,8),(8,21,4),(10,1,28),(12,9,20),(14,18,16)):st(o,r,2,v)
        li(16,8,0);lui(18,19);lui(22,20);li(26,21,6);ld(28,15,19,-63+delta,1);branch(32,'bltu',8,15,88)
        call(36,0x6af88+484*index);lui(40,15);ld(44,15,15,-71+delta,1);bz(48,15,54);call(50,0x6b16e+484*index)
        lui(54,15);ld(58,15,15,-72+delta,1);bz(62,15,68);call(64,0x6b1d4+484*index)
        for o,r,v in ((68,8,24),(70,1,28),(72,9,20),(74,18,16),(76,19,12),(78,20,8),(80,21,4)):ld(o,r,2,v)
        ai(82,2,2,32);e(84,'jal',rd=0,target=STARTS[index][3]);binary(88,'mul',10,8,21);ai(92,18,20,-68+delta)
        ld(96,12,18,0);e(100,'slli',rd=9,rs1=8,imm=4);li(104,11,16);binary(106,'add',12,12,9);ai(108,10,10,512)
        call(112,0x440c2+148*index);bz(116,10,170);ld(118,10,18,0);li(122,12,6);ai(124,11,0,255);binary(128,'add',10,10,9)
        pair(130,0x1ff95000,148-484*index);ld(138,10,18,0);li(142,12,6);ai(144,11,0,255);binary(148,'add',10,10,9);ai(150,10,10,6)
        pair(152,0x1ff95000,126-484*index);ld(160,15,18,0);binary(164,'add',9,9,15);st(166,0,9,12,2)
        ai(170,8,8,1);e(172,'andi',rd=8,rs1=8,imm=255);e(176,'jump',target=pc+28)
    elif part=='save':
        ai(0,2,2,-32);st(2,1,2,28);call(4,0x6af88+484*index);li(8,14,1);li(10,15,10);branch(12,'bgeu',14,10,18)
        li(16,15,2);ai(18,12,2,15);li(22,11,1);ai(24,10,0,66);st(28,15,2,15,1);call(30,0x494ee+152*index)
        ld(34,1,2,28);ai(36,2,2,32);ret(38)
    else:
        entry,old=role.specs('entry',index);check(pc==entry+88,'id10 outer start');s={p:f for p,f in old.items() if pc<=p<pc+16}
    return pc,s


def body(raw,part,index):
    k=PARTS.index(part);pc,s=specs(part,index);n=decode(raw,pc)
    check(set(n)==set(s),'id10 '+part+' boundaries')
    for p,f in s.items():init.g(n,p,'id10 '+part+' operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[k],HASHES[index][k]),'id10 '+part+' identity')
    edges={};calls=[];tails=[]
    for p,d in n.items():
        op=d['op'];q=[p+d['size']]
        if op=='jr':check(d['rs1']==1,'id10 ordinary RET');q=[]
        elif op in ('beqz','bltu','beq','bgeu'):q.append(d['target'])
        elif op=='jump':q=[d['target']]
        elif op in ('jal','jalr'):
            if op=='jal':t=d['target']
            else:
                a=n[p-4];check(a['op']=='auipc' and a['rd']==d['rs1'],'id10 adjacent PC pair');t=(p-4+a['imm']+d['imm'])&0xfffffffe
            r={'pc':hex(p),'target':hex(t),'rd':d['rd']}
            if d['rd']==0:tails.append(r);q=[]
            else:
                calls.append(r)
                if part=='next_outer' and p==pc+12:q=[]
        check(all(v in n for v in q),'id10 '+part+' closed local edges');edges[p]=q
    seen={pc};todo=[pc]
    while todo:
        for q in edges[todo.pop()]:
            if q not in seen:seen.add(q);todo.append(q)
    check(seen==set(n),'id10 '+part+' all nodes locally reachable')
    stores=[d for d in n.values() if d['op']=='store'];check(len(stores)==(3,41,8,2,0)[k],'id10 '+part+' store census')
    check((len(calls),len(tails))==((1,1),(5,0),(6,1),(2,0),(2,0))[k],'id10 '+part+' call census')
    if part=='allocate':
        check([(d['rs2'],d['imm']) for d in stores if d['rs1']==2]==[(19,12),(8,24),(9,20),(18,16),(1,28),(20,8)],'id10 allocation frame')
        check([(p-pc,q-pc) for p,qs in edges.items() for q in qs if q<p]==[(458,92),(468,114)],'id10 allocation backedges')
    if part=='load':
        check([(d['rs2'],d['imm']) for d in stores if d['rs1']==2]==[(8,24),(19,12),(20,8),(21,4),(1,28),(9,20),(18,16)],'id10 loader frame')
        check([(p-pc,q-pc) for p,qs in edges.items() for q in qs if q<p]==[(176,28)],'id10 loader loop backedge')
    if part=='save':check([(d['rs2'],d['imm'],d['width']) for d in stores]==[(1,28,4),(15,15,1)],'id10 writer only savedRA and single-byte stack source')
    return {'start':hex(pc),'bytes':len(raw),'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),'store_count':len(stores),
        'calls':calls,'tails':tails,'conditional_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},
        'complete_function':part!='next_outer','calls_are_return_premises':True}


def interval_rows(index):
    g=0x20003000+80*index
    slots=((24,-62,1),(52,-63,1),(56,-68,4),(68,-68,4),(90,-63,1),(110,1443,1),(122,-70,1),(130,-36,4),
        (138,-266,1),(150,-51,1),(166,-49,1),(186,-52,1),(194,-50,1),(202,-48,4),(210,-269,1),(218,-60,1),
        (230,-59,1),(246,-57,1),(262,-58,1),(270,-56,4),(278,-61,1),(288,-271,1),(298,-267,1),(306,-44,1),
        (316,-270,1),(324,-28,4),(332,-32,4),(340,-71,1),(348,-64,1),(356,-272,1),(364,-265,1),(372,-268,1),(464,1443,1))
    return [(o,g+v,z) for o,v,z in slots]


def arithmetic():
    pairs=0
    for index in range(256):
        for fresh in range(256):
            if index<fresh:
                check(index<255 and (index+1)&255==index+1 and index+1>index,'id10 loop cannot wrap on admitted step')
            pairs+=1
    rows=[{'config_count':n,'request_bytes':16*n,'maximum_iterations_under_valid_callee_preservation':255} for n in range(256)]
    check(rows[-1]['request_bytes']==4080 and pairs==65536,'id10 count/index arithmetic domain')
    check(512+6*254==2036 and 15<32 and 15+1<=28,'id10 NV address and stack-byte extent')
    return rows


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[]
    for i,(data,pr) in enumerate(zip(carriers,parent['profiles'])):
        d=role.DETAILS[i];g=0x20003000+80*i;ctx=0x20003000+d['ctx'];F=ctx+80;pc,ap,lp,wp,op=STARTS[i]
        windows={p:body(init.binding.take(data,STARTS[i][k],SIZES[k]),p,i) for k,p in enumerate(PARTS)}
        check(pr['cut_before_fifth_outer_initializer']['A0']==10 and pr['cut_before_fifth_outer_initializer']['target']==hex(pc),'id10 inherited entryID10')
        an={x['pc']:x for x in windows['allocate']['instructions']};pn={x['pc']:x for x in windows['initializer']['instructions']};ln={x['pc']:x for x in windows['load']['instructions']};wn={x['pc']:x for x in windows['save']['instructions']}
        check(an[ap+10]['imm']+an[ap+28]['imm']==F and an[ap+32]['imm']==14,'id10 allocation source F14')
        check(pn[pc+10]['rd']==10 and pn[pc+18]['rs2']==10 and an[ap+24]['rs2']==14,'id10 saved ID overwrites priorFF rather than callee reply')
        check(an[ap+8]['imm']==-1 and pn[pc+18]['imm']==an[ap+24]['imm'],'id10 transient FF/current ID same byte')
        protected=[(ctx+1,1),(ctx+2,1),(ctx+3,1),(ctx+40,4),(paths.layout.T,4*212),(F+8,4),(F+14,1),(F+21,1),(F+36,4),(F+48,4),(F+68,4),(g+856,48),(g+948,1),(g+949,1)]
        rows=interval_rows(i)
        check({ap+o for o,a,z in rows}=={p for p,x in an.items() if x['op']=='store' and x['rs1']!=2 and p not in (ap+450,ap+454)},'id10 all fixed allocation stores covered')
        for o,a,z in rows:
            check(an[ap+o]['width']==z,'id10 fixed store widths')
            for b,w in protected:check(paths.origin.separated(a,z,b,w),'id10 fixed store excludes live task/source fields')
        for dest in (g+380,g+364):
            for b,w in protected:check(paths.origin.separated(dest,16,b,w),'id10 common fill16 excludes live fields')
        check([x['target'] for x in windows['allocate']['calls']]==['0x20000040']+['0x2000039c']*4,'id10 allocation/fill call identities')
        ae={int(p,16):[int(q,16) for q in qs] for p,qs in windows['allocate']['conditional_CFG'].items()}
        null=paths.chain(ae,ap,{ap+74:ap+114})
        check(hex(ap+174) in null and hex(ap+254) in null and hex(ap+98) not in null,'id10 allocation-null still takes two common fills, skips F8 flag')
        prefix=paths.chain(ae,ap,{},cut=ap+64);check(prefix[-1]==hex(ap+64),'id10 unconditional allocator cut')
        check(ln[lp+112]['target']==0x440c2+148*i and windows['load']['tails'][0]['target']==hex(wp),'id10 NVread and save-wrapper joins')
        check(wn[wp+30]['target']==0x494ee+152*i and wn[wp+18]['imm']==15 and wn[wp+28]['width']==1,'id10 NVwrite1 borrowed SP15 source')
        se={int(p,16):[int(q,16) for q in qs] for p,qs in windows['save']['conditional_CFG'].items()}
        save_paths={name:paths.chain(se,wp,{wp+12:wp+off}) for name,off in (('count_reply_le1_byte10',18),('count_reply_gt1_byte2',16))}
        check(len(save_paths)==2 and wn[wp+12]['rs1']==14 and wn[wp+12]['rs2']==10,'id10 writer unsigned status split')
        le={int(p,16):[int(q,16) for q in qs] for p,qs in windows['load']['conditional_CFG'].items()}
        zero_paths={}
        for a in (False,True):
            for b in (False,True):
                zero_paths[str(int(a))+str(int(b))]=paths.chain(le,lp,{lp+32:lp+36,lp+48:lp+(50 if a else 54),lp+62:lp+(64 if b else 68)})
        check(all(hex(lp+36) in path and hex(lp+84) in path for path in zero_paths.values()),'id10 zero record count still status+save-tail')
        on={x['pc']:x for x in windows['next_outer']['instructions']};entry=d['entry'];outer=role.body(init.binding.take(data,entry,112),'entry',i);en={x['pc']:x for x in outer['instructions']}
        check(en[entry+84]['target']==pc and op==entry+88,'id10 full return address join')
        check(on[entry+96]['target']==d['reg'] and on[entry+100]['target']==d['outer_init'][5],'id10 sixth registration/initializer join')
        reg=registration.body(init.binding.take(data,d['reg'],48),i);check(11 not in reg['encoded_GPR_definitions'],'id10 next registration leaves opaque A1 unchanged')
        handler=0x4d000+d['outer_lows'][5];check(on[entry+88]['imm']+on[entry+92]['imm']==handler,'id10 sixth handler pointer')
        check(11<14 and paths.layout.T+48<=paths.layout.T+56,'id10 taskentry11 capacity')
        profiles.append({'label':pr['label'],'bodies':windows,'inherited_entry':pr['cut_before_fifth_outer_initializer'],
            'ID10':{'saved_input_entry_SP_offset':-20,'saved_RA_entry_SP_offset':-4,'transient_IDbyte_FF':hex(g-62),'post_return_IDbyte':10,'callee_A0_not_used_as_ID':True},
            'fixed_allocation_writes':[{'pc':hex(ap+o),'address':hex(a),'bytes':z} for o,a,z in rows],
            'allocation_contract':{'source_byte':hex(F+14),'request':'16*freshU8[F+14],0..4080','tag':66,'pool_word':hex(g-68),'count_byte':hex(g-63),
                'cut_before_allocator':{'pc':hex(ap+64),'target':'0x20000040'},'prefix_path':prefix,'allocation_always_called_even_source0':True,
                'null_guard':True,'null_path':null,'null_case':'count stays0 only under required memory preservation; skips record loop and F8 flag update, still calls two common fill16 sites',
                'success_case':'fresh second U8[F+14] stored ascount; each admitted slot16*i gets fillFF6 at0/6, SH0at12, SB0at14; byte15 not locally initialized',
                'fresh_config_counts_equal_proved':False,'loop_maximum':255,'loop_bound_does_not_require_constant_count':'index255 cannot be less than anyfreshU8count, so no admitted wrap, assuming body calls return and preserve index/live GPRs',
                'F8_flag':{'address':hex(g+1443),'success_F8_zero':128,'success_F8_nonzero':0,'allocation_null_path_updates_this_flag':False},
                'common_fill16':[hex(g+380),hex(g+364)],'actual_heap/payload/provider_preservation_proved':False},
            'load_contract':{'count_byte':hex(g-63),'pool_word':hex(g-68),'NV_read_target':hex(0x440c2+148*i),
                'NV_read_args':'(512+6*i,16,fresh_pool+16*i), i0..254 on admitted steps; units/provider output/retention remain unknown',
                'nonzero_read_reply_fallback':'fillFF6 atslot0/6;SH0at12; does not locally resetbytes14/15, so a failing/partial provider may leave them unknown',
                'loop_maximum':255,'fresh_count_can_change_without_invalidating_counter_bound':True,'zero_record_paths':zero_paths,
                'post_scan_status_call':hex(0x6af88+484*i),'optional_calls':[{'flag':hex(g-71),'target':hex(0x6b16e+484*i)},{'flag':hex(g-72),'target':hex(0x6b1d4+484*i)}],
                'flags_fresh_after_status_call':'setup clearsflag-71 but doesnot clearflag-72; intervening status/provider/asynchronous writes may change either',
                'tail_to_save':hex(wp),'zero_count_is_not_provider_free':True},
            'save_contract':{'frame_bytes':32,'status_target':hex(0x6af88+484*i),'paths':save_paths,'selected_byte':'unsigned statusreply<=1 ->10, else2',
                'SBSP_PC':hex(wp+28),'SBSP_source_GPR':15,'stack_initialized_bytes':[15],'NV_write_target':hex(0x494ee+152*i),'NV_write_args':'(66,1,SP+15)',
                'buffer_valid_only_during_frame':'1 byte within frame, distinct from savedRA28..31; actual synchronous consumption/retention contract not proved',
                'reply':'actual writer A0; A1/A2 not forced after provider; not a fixed boolean/status'},
            'conditional_next_registration':{'pc':hex(entry+96),'handler':hex(handler),'fresh_count_premise':11,'fresh_capacity_premise':'>=14','fresh_table_premise':hex(paths.layout.T),
                'entry11_address':hex(paths.layout.T+44),'new_count':12,'reply_A0':11,'reply_A2':12,'A1':'opaque writer/callee reply register, preserved by task-registration',
                'premises':'all allocator/fill/NV/status/optional services return and preserve required frames/live metadata/code and valid nonalias payload extents; no external interference'},
            'cut_before_sixth_outer_initializer':{'pc':hex(entry+100),'target':hex(d['outer_init'][5]),'A0':11,'A2':12,'A1':'opaque, not fixed1'},
            'actual_installed_binding_proved':False,'actual_NV_service_executed':False})
    return {'schema':'TSL9-ID10-NV-initialization-static-v1','profile':parent['profile'],'APP_sha256':sha256(image).hexdigest(),'profiles':profiles,
        'count_domain':arithmetic(),'stack_encoding':stack_encoding_source(),
        'scope':'per candidate28B wrapper/470B allocate/178B loader/40B save/16B outer join;1464B/454 new operand guards; cached LLVM SBSP sixvectors/128fieldcases;65536 index/fresh-count pairs',
        'boundary':'full local wrappers/CFG/dataflow guarded; allocator/fill/NV/status/optional bodies remain contracts. Conditional final return admits nextID11/count12; zero counts do not skip all external services',
        'remaining':['sixth initializer4d172/4d20a and outer final tail','status6af88/6b16c and optional services, NVread440c2/44156/NVwrite494ee/49586 contracts','actual providers, config/flag writers, payload and borrowed buffer lifetime'],
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
                except RuntimeError as e:check(str(e).startswith('id10 '+part+' operand '),'id10 specified mutation guard '+str(e))
                else:raise RuntimeError('id10 mutation escaped')
                mutations+=1
    check(mutations==454 and sum(SIZES)*2==1464,'id10 instruction/byte census');arithmetic();stack_encoding_source()
    print('PASS:454 operand mutations rejected;1464 original bytes;65536 index/count pairs;6 LLVM SBSP vectors and128 field cases')


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
    else:check(OUT.read_bytes()==output,'id10 exact ledger replay')
    print('PASS:ID10 frame/publication;allocation and NV scan/save contracts;conditional ID11/count12;exact ledger')
    print('PASS:NO target execution/emulation;actual providers/NV outcomes/payload and borrowed-buffer lifetime UNPROVED')


if __name__=='__main__':main()
