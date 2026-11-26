"""Offline special task events and published record callback contracts.

Strict original bytes/operands/CFG and integer domains only. No target ISA,
mutable RAM/register machine, message, enumerator, provider or MMIO model.
"""
import argparse
import json
import re
from hashlib import sha256
from pathlib import Path
import check_v4160_id11_outer_tail_static as previous

init,sparse,check=previous.init,previous.sparse,previous.check
paths,role=previous.paths,previous.role
OUT=Path(__file__).with_name('v4160-special-event-callback-static.json')


def decode(raw,pc):
    nodes={};off=0
    while off<len(raw):
        h=int.from_bytes(raw[off:off+2],'little');z=2 if h&3!=3 else 4;chunk=raw[off:off+z];w=int.from_bytes(chunk,'little')
        check(len(chunk)==z,'special complete instruction')
        if z==2 and h&0xf863==0x8020:
            d=dict(pc=pc+off,bytes=chunk.hex(),size=2,op='load',rd=8+(h>>2&7),rs1=2,imm=((h>>8&7)<<1)|((h>>7&1)<<4),width=2,mnemonic='qk.c.lhusp')
        elif z==4 and w&0x707f==3:
            imm=w>>20;imm-=4096 if imm&2048 else 0
            d=dict(pc=pc+off,bytes=chunk.hex(),size=4,op='load',rd=w>>7&31,rs1=w>>15&31,imm=imm,width=1,signed=True,mnemonic='lb')
        else:d=previous.decode(chunk,pc+off)[pc+off]
        nodes[pc+off]=d;off+=z
    return nodes


def extra_encoding_source():
    sources,_=init.timer.source_contract();td=(init.timer.REF/'RISCVInstrInfoXwch.td').read_text(encoding='utf-8')
    for x in ('def QK_C_LHUSP : QKStackInst<0b01, (outs GPRC:$rd_rs2),','let Inst{10-8} = imm{3-1};','let Inst{7} = imm{4};'):
        check(x in td,'special cached LLVM LHUSP fields')
    lines=(init.timer.REF/'xwchc-valid.s').read_text(encoding='utf-8').splitlines();vectors=[]
    for i,line in enumerate(lines):
        m=re.fullmatch(r'# CHECK-ASM-AND-OBJ: qk\.c\.lhusp s0, (\d+)\(sp\)',line)
        if not m:continue
        e=re.fullmatch(r'# CHECK-ASM: encoding: \[0x([0-9a-f]{2}),0x([0-9a-f]{2})\]',lines[i+1]);check(e is not None,'special official LHUSP vector')
        raw=bytes(int(v,16) for v in e.groups());n=decode(raw,0)[0]
        check((n['rd'],n['rs1'],n['imm'],n['width'])==(8,2,int(m[1]),2),'special official LHUSP decode')
        vectors.append({'bytes':raw.hex(),'offset':int(m[1]),'source_line':i+1})
    check(len(vectors)==6,'special six LHUSP official vectors')
    for r in range(8,16):
        for imm in range(0,32,2):
            h=0x8020|((r-8)<<2)|((imm>>1&7)<<8)|((imm>>4&1)<<7);n=decode(h.to_bytes(2,'little'),0)[0]
            check((n['rd'],n['imm'],n['rs1'],n['width'])==(r,imm,2,2),'special128 LHUSP field combinations')
    return {'sources':sources,'LHUSP_vectors':vectors,'field_cases':128,'actual_callback_load':'3087 -> LHU A2,14(SP)',
        'signed_LB':'RV32 opcode0000011/funct3=000; raw payload byte3 sign-extended to A1, not LBU'}


PARTS=('handler','message','callback','invalidate')
STARTS=((0x6d26c,0x6d214,0x4cff6,0x4cfd0),(0x6d458,0x6d400,0x4d08e,0x4d068))
SIZES=(568,88,114,38)
COUNTS=(188,29,45,15)
HASHES=(('7022782334be49e92221c39f5e5440eae225df2f4761ed5f587f5cba53d693ca','ad6485e67f0650ff2a6a6b2e5e7bdce1813107486b1aaf7ed5ee7ebb49b1a72d',
 '1625865da8d265019041523338709515da17901c5eb32070025cda40b8ae18cd','188efab2e4a1eae80b909ca292108ffbe411b5a74ef6674b2695c0c15122d0e6'),
 ('ff274b24639a1f8a958a33535da6314e6d41ef273bfeaa5ed8ef65d3bc7bf851','f294c787cfea26a538c41b49236719b5a233527cb9ada01f62cf7820f2c249a7',
 '267e58e9663a65cef2fda717bf2f9a8b39e0cd7c2e2f816f1008d4922f38a2ce','188efab2e4a1eae80b909ca292108ffbe411b5a74ef6674b2695c0c15122d0e6'))


def specs(part,index):
    pc=STARTS[index][PARTS.index(part)];d=80*index;s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def lui(o,r,v=0x20003000):e(o,'lui',rd=r,imm=v)
    def ai(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    def ld(o,r,b,v,w=4,**f):e(o,'load',rd=r,rs1=b,imm=v,width=w,**f)
    def st(o,r,b,v,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    def mv(o,r,b):e(o,'mv',rd=r,rs2=b)
    def br(o,op,a,b,t):e(o,op,rs1=a,rs2=b,target=pc+t)
    def bz(o,r,t):e(o,'beqz',rs1=r,target=pc+t)
    def bnz(o,r,t):e(o,'bnez',rs1=r,target=pc+t)
    def j(o,t):e(o,'jump',target=pc+t)
    def call(o,t):e(o,'jal',rd=1,target=t)
    def ret(o,r=1):e(o,'jr',rs1=r)
    def pair(o,low):e(o,'auipc',rd=1,imm=0x1ff93000);e(o+4,'jalr',rd=1,rs1=1,imm=low-492*index)
    def imm(o,op,r,b,v):e(o,op,rd=r,rs1=b,imm=v)
    def binary(o,op,r,a,b):e(o,op,rd=r,rs1=a,rs2=b)
    if part=='handler':
        ai(0,2,2,-32);imm(2,'slli',15,11,16);st(6,9,2,20);st(8,1,2,28);st(10,8,2,24);imm(12,'srai',15,15,16);mv(14,9,11)
        br(16,'bge',15,0,218);lui(20,15);ld(24,10,15,1525+d,1);pair(28,4);mv(36,8,10);bz(38,10,60)
        lui(40,15);ld(44,15,15,1451+d,1);bnz(48,15,74);call(50,STARTS[index][1]);mv(54,10,8);call(56,0x431ba+140*index)
        lui(60,10,0x8000);binary(62,'xor',10,10,9);ld(64,1,2,28);ld(66,8,2,24);ld(68,9,2,20);ai(70,2,2,32);ret(72)
        ld(74,15,10,0,1);ai(76,14,0,208);br(80,'bne',15,14,170);ld(84,15,10,2,1);bnz(86,15,94);call(88,STARTS[index][1]);j(92,108)
        li(94,14,5);br(96,'bne',15,14,124);ld(100,14,10,12,1);li(102,15,8);br(104,'bne',15,14,50)
        lui(108,15);ld(112,10,15,1554+d,1);mv(116,11,8);call(118,0x43208+140*index);j(122,60)
        li(124,14,8);br(126,'beq',15,14,88);li(130,13,6);br(132,'bne',15,13,140);ld(136,15,10,7,1);j(138,104)
        li(140,14,7);br(142,'bne',15,14,50);ld(146,10,10,4,2);pair(148,1940);bz(156,10,54)
        ld(158,14,10,12,1);li(160,15,8);mv(162,10,8);br(164,'bne',14,15,50);j(168,108)
        ai(170,14,0,162);br(174,'beq',15,14,50);ai(178,14,0,145);br(182,'bne',15,14,88)
        ld(186,14,10,1,1);li(188,15,14);br(190,'bne',14,15,88);ld(194,14,10,4,2);lui(196,15,0x1000);ai(198,15,15,1029)
        br(202,'bne',14,15,88);ld(206,14,10,8);ld(208,15,14,2,1);ld(210,10,14,1,1);imm(212,'slli',15,15,8);binary(214,'or',10,10,15);j(216,148)
        imm(218,'slli',15,11,17);br(222,'bge',15,0,258);lui(226,12);ai(230,12,12,-12+d);li(234,11,4);li(236,10,4)
        call(238,0x4435c+148*index);lui(242,15);ld(246,10,15,-272+d,1);call(250,0x44310+148*index);lui(254,10,0x4000);j(256,62)
        imm(258,'andi',15,11,1);bz(262,15,418);lui(264,15);ld(268,15,15,1448+d,1);bz(272,15,368)
        call(274,0x4f128+152*index);lui(278,15);ld(282,15,15,513+d,1);imm(286,'andi',15,15,3);br(288,'bltu',10,15,374)
        li(292,15,3);st(294,15,2,4,1);lui(296,15);ld(300,15,15,1449+d,1);ai(304,11,2,4);st(306,15,2,12,1)
        lui(308,15);ld(312,15,15,1544+d,1);st(316,15,2,13,1);lui(318,15);ld(322,10,15,1525+d,1);call(326,0x482f4+152*index);bz(330,10,368)
        lui(332,15);ld(336,10,15,1484+d);imm(340,'andi',10,10,-16);imm(342,'ori',10,10,6);st(346,10,15,1484+d)
        lui(350,15);ld(354,15,15,-16+d);bz(358,15,368);ld(360,15,15,0);bz(362,15,368);li(364,11,0);e(366,'call_indirect',rd=1,rs1=15)
        imm(368,'xori',10,9,1);j(372,64);lui(374,15);ld(378,15,15,1450+d,1);lui(382,11);li(386,12,6);st(388,15,2,4,1)
        lui(390,15);ld(394,15,15,1488+d,1);ai(398,11,11,1456+d);ai(402,10,2,6);st(406,15,2,5,1);pair(408,-210);j(416,296)
        imm(418,'andi',15,11,2);bz(422,15,490);lui(424,15);ld(428,15,15,1452+d,1);imm(432,'andi',15,15,1);bz(434,15,484)
        lui(436,15);ld(440,10,15,1525+d,1);call(444,0x485e0+152*index);bz(448,10,484)
        lui(450,15);ld(454,10,15,1484+d);imm(458,'andi',10,10,-241);st(462,10,15,1484+d);lui(466,15);ld(470,15,15,-16+d)
        bz(474,15,484);ld(476,15,15,0);bz(478,15,484);li(480,11,0);e(482,'call_indirect',rd=1,rs1=15);imm(484,'xori',10,9,2);j(488,64)
        imm(490,'andi',15,11,4);li(494,10,0);br(496,'beq',15,0,64);lui(500,15);ld(504,15,15,1555+d,1);bz(508,15,562)
        lui(510,15);ld(514,10,15,1525+d,1);call(518,0x4861c+152*index);bz(522,10,562)
        lui(524,14);ld(528,10,14,1484+d);lui(532,15,0xfffff000);ai(534,15,15,255);binary(538,'and',10,10,15);lui(540,15)
        ld(544,15,15,-16+d);st(548,10,14,1484+d);bz(552,15,562);ld(554,15,15,0);bz(556,15,562);li(558,11,0)
        e(560,'call_indirect',rd=1,rs1=15);imm(562,'xori',10,9,4);j(566,64)
    elif part=='message':
        ld(0,14,10,0,1);ai(2,13,0,145);br(6,'beq',14,13,20);ai(10,15,0,208);br(14,'beq',14,15,82);ret(18)
        ld(20,13,10,1,1);li(22,14,14);br(24,'bne',13,14,86);ld(28,13,10,4,2);lui(30,14,0x1000);ai(32,14,14,1029);br(36,'bne',13,14,86)
        ld(40,14,10,8);ai(42,15,0,127);ld(46,11,14,3,1,signed=True);br(50,'beq',11,15,86)
        lui(54,15);ld(58,15,15,-16+d);bz(62,15,86);ld(64,6,15,4);br(68,'beq',6,0,86);ld(72,15,14,2,1);ld(74,10,14,1,1)
        imm(76,'slli',15,15,8);binary(78,'or',10,10,15);ret(80,6);e(82,'jal',rd=0,target=0x6cf34+492*index);ret(86)
    elif part=='callback':
        ai(0,2,2,-32);st(2,18,2,16);st(4,1,2,28);st(6,8,2,24);st(8,9,2,20);li(10,15,1);mv(12,18,10);br(14,'bne',11,15,82)
        mv(18,10,18);call(20,0x4b61e+152*index);bnz(24,10,108);lui(26,9,0x10000);lui(28,12,0x6f000);ai(32,11,9,-1)
        ai(36,14,2,14);li(40,13,2);ai(42,12,12,-1424+496*index);li(46,10,1);call(48,0x4bf06+152*index);mv(52,8,10);ai(54,9,9,-1)
        bz(56,8,96);ld(58,11,8,12);mv(60,10,18);call(62,STARTS[index][3]);ld(66,12,2,14,2);mv(68,10,8);li(70,13,0);mv(72,11,9)
        call(74,0x4c35e+152*index);mv(78,8,10);j(80,56);li(82,15,2);br(84,'bne',11,15,96);li(88,11,1);call(90,0x4f072+152*index);bz(94,10,18)
        for o,r,v in ((96,1,28),(98,8,24),(100,9,20),(102,18,16)):ld(o,r,2,v)
        ai(104,2,2,32);ret(106);call(108,0x4b5d2+152*index);j(112,26)
    else:
        lui(0,15,0x10000);ai(2,15,15,-1);br(4,'bne',10,15,14);mv(8,10,11);e(10,'jal',rd=0,target=0x4b33c+152*index)
        ai(14,2,2,-16);st(16,1,2,12);call(18,0x4b2e4+152*index);bz(22,10,32);li(24,15,-1);st(26,15,10,0,2);st(28,0,10,2,1)
        ld(32,1,2,12);ai(34,2,2,16);ret(36)
    return pc,s


def body(raw,part,index):
    k=PARTS.index(part);pc,s=specs(part,index);n=decode(raw,pc)
    check(set(n)==set(s),'special '+part+' boundaries')
    for p,f in s.items():init.g(n,p,'special '+part+' operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[k],HASHES[index][k]),'special '+part+' identity')
    edges={};calls=[];tails=[]
    for p,d in n.items():
        op=d['op'];q=[p+d['size']]
        if op=='jr':
            q=[]
            if d['rs1']!=1:check(part=='message' and d['rs1']==6,'special indirect tail register');tails.append({'pc':hex(p),'target':'fresh U32[hook_object+4]','rd':0})
        elif op in ('beq','bne','bge','beqz','bnez','bltu'):q.append(d['target'])
        elif op=='jump':q=[d['target']]
        elif op in ('jal','jalr','call_indirect'):
            if op=='call_indirect':t='fresh U32[hook_object+0]'
            elif op=='jal':t=hex(d['target'])
            else:
                a=n[p-4];check(a['op']=='auipc' and a['rd']==d['rs1'],'special PC pair adjacency');t=hex((p-4+a['imm']+d['imm'])&0xfffffffe)
            row={'pc':hex(p),'target':t,'rd':d['rd']}
            if d['rd']==0:tails.append(row);q=[]
            else:calls.append(row)
        check(all(v in n for v in q),'special '+part+' CFG edges closed');edges[p]=q
    seen={pc};todo=[pc]
    while todo:
        for q in edges[todo.pop()]:
            if q not in seen:seen.add(q);todo.append(q)
    check(seen==set(n),'special '+part+' all nodes locally reachable')
    if part!='callback':
        done=set();active=set()
        def visit(p):
            check(p not in active,'special '+part+' no local cycle')
            if p in done:return
            active.add(p)
            for q in edges[p]:visit(q)
            active.remove(p);done.add(p)
        visit(pc)
    stores=[x for x in n.values() if x['op']=='store'];check(len(stores)==(11,0,4,3)[k],'special '+part+' store census')
    check((len(calls),len(tails))==((16,0),(0,2),(6,0),(1,1))[k],'special '+part+' call census')
    if part=='handler':check([(x['rs2'],x['imm']) for x in stores if x['rs1']==2]==[(9,20),(1,28),(8,24),(15,4),(15,12),(15,13),(15,4),(15,5)],'special handler frame/scratch stores exact')
    if part=='callback':
        check(all(x['rs1']==2 for x in stores),'special callback no nonframe local store')
        check([(p-pc,q-pc) for p,qs in edges.items() for q in qs if q<p]==[(80,56),(94,18),(112,26)],'special callback exact backedges, only80->56 can form cycle')
        check([p-pc for p,x in n.items() if x.get('rd')==9]==[26,54,100],'special FFFF constant has only setup and epilogue restore, no per-iteration decrement')
    return {'start':hex(pc),'bytes':len(raw),'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),'store_count':len(stores),'calls':calls,'tails':tails,
        'conditional_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},'complete_function':True,'calls_are_return_premises':True}


def event_domains():
    counts={str(b):0 for b in (32768,16384,1,2,4,0)}
    for low in range(65536):
        bit=next((v for v in (32768,16384,1,2,4) if low&v),0);counts[str(bit)]+=1
        for upper in (0,1,32768,65535):
            mask=upper<<16|low
            check(bool((mask<<16&0xffffffff)&0x80000000)==bool(low&32768),'special bit15 signed-low16 identity')
            check(bool((mask<<17&0xffffffff)&0x80000000)==bool(low&16384),'special bit14 sign identity')
            if bit:check((mask^bit)>>16==upper,'special consumed-bit XOR preserves upper16')
    check(counts=={'32768':32768,'16384':16384,'1':8192,'2':4096,'4':2048,'0':2048},'special event priority census')
    signed=[b-256 if b&128 else b for b in range(256)]
    check(min(signed)==-128 and max(signed)==127 and [b for b,v in enumerate(signed) if v==127]==[127],'special signed byte sentinel domain')
    return {'low16_priority_counts':counts,'priority_bits':[32768,16384,1,2,4],'upper16_vectors':[0,1,32768,65535],
        'reply':'entry_full32mask XOR selected bit; if none of five selected bits,0','signed_payload_byte3_range':[-128,127]}


def selected_paths(b,part):
    pc=int(b['start'],16);e={int(p,16):[int(q,16) for q in qs] for p,qs in b['conditional_CFG'].items()}
    if part=='handler':
        cases={'message_null':{16:20,38:60},'bit14':{16:218,222:226},'bit0_disabled':{16:218,222:258,262:264,272:368},
            'bit1_disabled':{16:218,222:258,262:418,422:424,434:484},'bit2_disabled':{16:218,222:258,262:418,422:490,496:500,508:562},
            'no_known_bits':{16:218,222:258,262:418,422:490,496:64}}
    elif part=='callback':cases={'other_mode':{14:82,84:96},'mode2_nonzero_reply':{14:82,84:88,94:96},'initial_enumerator_null':{14:18,24:26,56:96}}
    elif part=='invalidate':cases={'all_selector_tail':{4:8},'lookup_null':{4:14,22:32},'lookup_nonnull':{4:14,22:24}}
    else:cases={'other_type':{6:10,14:18},'type208_tail':{6:10,14:82},'type145_header_mismatch':{6:20,24:86}}
    return {name:paths.chain(e,pc,{pc+p:pc+q for p,q in c.items()}) for name,c in cases.items()}


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[]
    for i,(data,pr) in enumerate(zip(carriers,parent['profiles'])):
        g=0x20003000+80*i;hp,mp,cp,ip=STARTS[i]
        windows={p:body(init.binding.take(data,STARTS[i][k],SIZES[k]),p,i) for k,p in enumerate(PARTS)}
        check(int(pr['final_gate']['extra_task_conditions']['handler'],16)==hp and int(pr['ID11']['callback_pointer'],16)==cp,'special prior published targets match guarded bodies')
        hn={x['pc']:x for x in windows['handler']['instructions']};cn={x['pc']:x for x in windows['callback']['instructions']};mn={x['pc']:x for x in windows['message']['instructions']}
        check(hn[hp+14]['rs2']==11 and hn[hp+14]['rd']==9,'special saves full eventmask inS1')
        check([x['target'] for x in windows['handler']['calls'] if x['pc'] in (hex(hp+32),hex(hp+152),hex(hp+412))]==['0x2000028c','0x20000a94','0x20000332'],'special RAM receive/lookup/copy targets')
        check(cn[cp+36]['imm']==14 and cn[cp+66]['rs1']==2 and cn[cp+66]['width']==2,'special SP14 output/LHUSP link')
        rom=0x6f000+cn[cp+42]['imm'];check(rom==0x6ea70+496*i and rom>0x40000+len(data),'special enumerator ROM outside supplied candidate bytes')
        check(rom in [int(v,16) for v in pr['profile_layout']['stored_ROM_pointers']],'special ROM search pattern matches prior stored external ROM pointer')
        pool=previous.body(init.binding.take(data,previous.STARTS[i][3],30),'pool',i)
        check(windows['invalidate']['tails'][0]['target']==pool['start'],'special FFFF selector reuses reserved-margin clear')
        check(mn[mp+46].get('signed') is True and mn[mp+46]['width']==1 and mn[mp+50]['rs1']==11,'special signed payload byte comparison remains signed')
        certs={p:selected_paths(b,p) for p,b in windows.items()};check(sum(len(v) for v in certs.values())==15,'special selected-path census per profile')
        partial=[(x['pc']-hp,x['imm'],x['width']) for x in hn.values() if x['op']=='store' and x['rs1']==2 and x['imm']<20]
        check(partial==[(294,4,1),(306,12,1),(316,13,1),(388,4,1),(406,5,1)],'special scratch partial initialization exact local stores')
        check(hn[hp+402]['imm']==6 and hn[hp+386]['imm']==6 and hn[hp+304]['imm']==4,'special optionalcopySP6len6 and borrowedSP4 request')
        state=g+1484;hook=g-16
        check([(x['pc']-hp,x['imm']) for x in hn.values() if x['op']=='store' and x['rs1']!=2]==[(346,1484+80*i),(462,1484+80*i),(548,1484+80*i)],'special only three fixed nonframe state stores')
        ctx=0x20003000+role.DETAILS[i]['ctx'];F=ctx+80
        for a,z in ((ctx+1,1),(ctx+2,1),(ctx+40,4),(paths.layout.T,4*212),(F+21,1),(F+36,4),(F+48,4),(F+68,4)):
            check(paths.origin.separated(state,4,a,z),'special state word excludes task/source slots')
        profiles.append({'label':pr['label'],'bodies':windows,'selected_CFG_paths':certs,
            'source_links':{'optional_task_handler':hex(hp),'published_callback':hex(cp),'handler_special_ID_byte':hex(g+1525),'actual_scheduling_or_callback_invocation_proved':False},
            'handler_contract':{'frame_bytes':32,'saved':['RA','S0','S1'],'priority':[32768,16384,1,2,4],
                'message_event':{'receive_target':'0x2000028c','A0':hex(g+1525)+' freshU8','null_reply':'entryfullmask XOR8000',
                    'nonnull':'S0=message; freshflag1451 gates dispatcher; type208/145 and subtype/raw field branches decide messagehelper/free/delivery calls',
                    'free_target':hex(0x431ba+140*i),'delivery_target':hex(0x43208+140*i),'delivery_args':['freshU8['+hex(g+1554)+']','original message S0'],
                    'ownership_limit':'helper/free/delivery called on distinct paths; actual ownership transfer, consumption/retention, and message valid extent not proved'},
                'bit14_calls':[hex(0x4435c+148*i),hex(0x44310+148*i)],'state_word':hex(state),
                'low_event_state_updates':{'bit0':'(freshword&fffffff0)|6','bit1':'freshword&ffffff0f','bit2':'freshword&fffff0ff'},
                'optional_callbacks':{'hook_word':hex(hook),'function_word_offset':0,'both_pointers_guarded':True,'A0':'updated stateword','A1':0,'ABI_and_retention_unknown':True},
                'borrowed_request_SP4':{'request_target':hex(0x482f4+152*i),'common_written_bytes':[12,13],'tag3_path_written_bytes':[4,12,13],
                    'copy_path_written_bytes':'4,5 and conditional copy6to6..11, plus12,13','tag3_path_SP5_to11_locally_uninitialized':True,
                    'callee_input':'A0=freshtaskbyte,A1=SP4; no local length defining whole10byte read; callee extent/consumption/retention unknown'},
                'reply':'selectedbit XOR originalfull32eventmask after required calls return; no recognized bits returns0',
                'preservation':'all callees/indirect callbacks preserve live S0/S1/SP/frame/RA/GP and valid code/message/context state as required'},
            'message_helper_contract':{'entry':hex(mp),'frame_bytes':0,'type208_tail':hex(0x6cf34+492*i),
                'type145_requirements':'byte1=14,LHU4=1405; payload=U32[message+8] valid; signedLBpayload3!=127; hook andU32[hook+4] nonzero',
                'indirect_tail_args':{'A0':'U8[payload+1]|(U8[payload+2]<<8)','A1':'signextended signedbyte payload+3, -128..127'},
                'tail_target':'fresh U32[hook_object+4]','payload_pointer_local_null_guard':False,'unmatched_returns':'ordinaryRET with no forced scalar status'},
            'record_callback_contract':{'frame_bytes':32,'saved':['RA','S0','S1','S2'],'entry_selector_in':'S2 full32',
                'mode1':'4b61e/4b6b6; nonzero reply additionally4b5d2/4b66a; then enumerator',
                'mode2':'4f072/4f10a(entryA0,1); reply0 joins mode1 check, nonzero returns','other_mode':'RET without helper calls',
                'enumerator':{'target':hex(0x4bf06+152*i),'args':[1,65535,hex(rom),2,'SP+14'],'ROM_pattern_bytes_available':False,'SP14_output_initialized_by_local_body':False},
                'loop':'while returned node!=0: invalidate(entryselector,U32[node+12]); LHU SP14; nexthelper(node,ffff,LHUSP14,0)',
                'next_helper':hex(0x4c35e+152*i),'FFFF_is_filter_not_counter':True,'finite_iteration_bound_proved':False,
                'required_contracts':'enumerator/nexthelper output initialization, node/payload extents, actual next-node progress/acyclicity, S0-S2/SP/frame/RA/GP preservation; borrowed SP14 consumption/retention still unknown'},
            'invalidate_contract':{'entry':hex(ip),'selector_ffff':'tail margin-clear withA0=entryA1; reuses prior count/end-pointer premises',
                'other_selectors':'lookup4b2e4/4b37c; ifnonnullR thenSHffff@R0,SB0@R2; returnactualR, noforcedstatus',
                'lookup_target':hex(0x4b2e4+152*i),'dynamic_writes_require_valid_nonalias_record_extent':True},
            'actual_installed_bindings_proved':False,'target_provider_or_callback_executed':False})
    return {'schema':'TSL9-special-event-callback-static-v1','profile':parent['profile'],'APP_sha256':sha256(image).hexdigest(),'profiles':profiles,
        'event_domains':event_domains(),'extra_encoding':extra_encoding_source(),
        'scope':'per candidate full568B/188i handler,88B/29i messagehelper,114B/45i callback,38B/15i invalidatehelper;1616B/554operand guards;30 selectedCFG paths;LHUSP/LBdecode and domain checks',
        'boundary':'complete local CFG/operands and no-call gates; message/provider/indirect paths conditional. Callback enumerator has no proved iteration bound and outside-image ROM pattern; no claim of actual event/packet execution',
        'remaining':['receive/lookup/free/delivery providers and messagehelper type208 tail','request482f4/4838c scratch extent and retained pointer contract','enumerator/nexthelper/node progress, missingROMpattern, indirect ABI and payload/frame lifetime'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    mutations=certs=0
    for i,data in enumerate(carriers):
        for k,part in enumerate(PARTS):
            pc=STARTS[i][k];raw=init.binding.take(data,pc,SIZES[k]);b=body(raw,part,i);certs+=len(selected_paths(b,part))
            for p,d in decode(raw,pc).items():
                at=p-pc;z=d['size'];buf=bytearray(raw)
                buf[at:at+z]=(int.from_bytes(buf[at:at+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
                try:body(buf,part,i)
                except RuntimeError as e:check(str(e).startswith('special '+part+' operand '),'special specified mutation guard '+str(e))
                else:raise RuntimeError('special mutation escaped')
                mutations+=1
    check(mutations==554 and certs==30 and sum(SIZES)*2==1616,'special instruction/path/byte census');event_domains();extra_encoding_source()
    print('PASS:554 operand mutations rejected;1616 original bytes;30 CFG path certificates;65536 event priorities;6 LLVM LHUSP vectors/128 fields')


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
    else:check(OUT.read_bytes()==output,'special exact ledger replay')
    print('PASS:published handler/callback joins;eventmask/partialscratch/signedpayload and enumeration contracts;exact ledger')
    print('PASS:NO target execution/emulation;actual provider/ownership/enumeration progress/borrowed-buffer lifetime UNPROVED')


if __name__=='__main__':main()
