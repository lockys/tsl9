"""Offline last outer initializer, reserved pool margin and final tail gate.

Original operands/CFG and integer/interval certificates; no target execution,
register/RAM state model, allocator, fill, copy, NV, callback or MMIO model.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_id10_nv_initialization_static as previous

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
paths,role,registration=previous.paths,previous.role,previous.registration
resources=previous.previous.previous
leaves=previous.previous.leaves
OUT=Path(__file__).with_name('v4160-id11-outer-tail-static.json')
PARTS=('initializer','factory','defaults','pool','outer_return','gate','special_ID')
STARTS=((0x4d172,0x493f2,0x4b35e,0x4b33c,0x6dd7e,0x6d572,0x4600e),
        (0x4d20a,0x4948a,0x4b3f6,0x4b3d4,0x6df6e,0x6d75e,0x460a6))
SIZES=(62,252,248,30,8,272,10)
COUNTS=(19,72,72,11,3,84,3)
HASHES=(('66605688b14f5ad32ce2045e36961f0558a1f6368630ed347f5bbacae737fc8b','c9485cde6f5c67c1535f48050373b46047c21bc0ac883324144db1b6b4bbd32e',
 '23e76814de096c94fef6c170849a8f6e4606c939523ad8b46b726ec974f42d96','521190163d50f92c9a16c029d77efb81e23c508217173a0b008092d61b4794ea',
 'd22e032f5a3fdaad1fb7c10a5c23bc377ff3fa9cded04ce27a6788ecd106a476','d88be82481a97e65c8f66deb95e52cf8e362f22dd7f4dbd5849cf2cde554a294','6825731612539241d0ebd07d48e7692bd9156377c88b0a9a624aff16c756f5a2'),
 ('66438832248b0c647a27877215f6c36e0fdd912c96edae912964e1d3e0bd5e29','89ab5e8af1c2ea63347f6175786812d1a20e3c773fc838a0799d5184a56a788d',
 '5dc1984b781f856ead2e1b29e361334f8a32b57715e2b111a4005a5d98cbcda1','73f5ed62bc1663f16e47472b5a08f9f4c1877f4fe30a321c2cfe7424e7e8c97c',
 '2c252bc93eb4f5a56df9e5dfc990c4ec9bf31ec40867a1ccd4c160715cc306bf','b0d3a8128f9bba8fd20aaf192a4da6e5b4cf49294772f9baa1b026eec3592485','89e3aa66b7e7ca3ecc6e28eb5829da6ee873d5c10839b59db5bfc245f62a78a7'))


def specs(part,index):
    pc=STARTS[index][PARTS.index(part)];d=80*index;obj=76*index;rom=496*index;s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def lui(o,r,v=0x20003000):e(o,'lui',rd=r,imm=v)
    def ai(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    def ld(o,r,b,v,w=4):e(o,'load',rd=r,rs1=b,imm=v,width=w)
    def st(o,r,b,v,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    def call(o,t):e(o,'jal',rd=1,target=t)
    def ret(o):e(o,'jr',rs1=1)
    def pair(o,upper,low):e(o,'auipc',rd=1,imm=upper);e(o+4,'jalr',rd=1,rs1=1,imm=low)
    if part=='initializer':
        ai(0,2,2,-16);st(2,1,2,12);st(4,8,2,8);e(6,'mv',rd=8,rs2=10);call(8,STARTS[index][1]);call(12,STARTS[index][2])
        lui(16,15);st(20,8,15,-289+d,1);lui(24,15);ld(28,10,15,-128+d);call(32,STARTS[index][3])
        lui(36,15);st(40,8,15,-274+d,1);ld(44,8,2,8);ld(46,1,2,12);lui(48,10,0x4d000);ai(52,10,10,-10+152*index)
        ai(56,2,2,16);e(58,'jal',rd=0,target=0x4efe2+152*index)
    elif part=='factory':
        lui(0,15);ai(4,2,2,-16);st(6,0,15,-164+d);lui(10,15);st(14,8,2,8);st(16,0,15,-166+d,1);li(20,8,2)
        for o,r,v,w in ((22,8,-305,1),(30,0,-169,1),(38,8,-308,1),(46,0,-172,2),(54,8,-292,1)):
            lui(o,15);st(o+4,r,15,v+d,w)
        lui(62,10);lui(66,15);li(70,14,8);st(72,0,15,-160+d,1);li(76,12,6);lui(78,15);li(82,11,0)
        ai(84,10,10,-156+d);st(88,1,2,12);st(90,14,15,-291+d,1);pair(94,0x1ffb7000,-180-152*index)
        lui(102,15);st(106,8,15,-302+d,1);lui(110,14,0xa00000);lui(114,15);ai(118,15,15,-300+d);ai(122,14,14,80)
        st(126,14,15,0);lui(128,14,0x3e80000);st(132,14,15,4);lui(134,15);st(138,8,15,-306+d,1)
        li(142,14,1);lui(144,15);st(148,14,15,-307+d,1);lui(152,15);st(156,8,15,-290+d,1)
        lui(160,10);lui(164,15);st(168,0,15,-150+d,1);li(172,12,24);lui(174,15);li(178,11,0);ai(180,10,10,12+d)
        st(184,8,15,-304+d,1);pair(188,0x1ffb7000,-274-152*index);lui(196,15);st(200,8,15,-303+d,1);lui(204,15);st(208,0,15,-167+d,1)
        lui(212,14,0x49000);lui(216,15);ai(220,15,15,-400+obj);ai(224,14,14,342+152*index);st(228,14,15,0)
        ld(230,1,2,12);ld(232,8,2,8);lui(234,14,0x49000);ai(238,14,14,624+152*index);st(242,14,15,4);st(244,0,15,8);ai(248,2,2,16);ret(250)
    elif part=='defaults':
        lui(0,12);ai(4,12,12,-273+d);ai(8,15,0,32);st(12,15,12,0,1);lui(14,14);li(18,15,-1)
        st(20,15,14,-274+d,1);lui(24,14);st(28,15,14,-288+d,1);lui(32,14);st(36,15,14,-289+d,1);li(40,11,1)
        for o,v,w,r in ((42,-276,2,11),(50,-134,2,0),(58,-124,4,0),(66,-108,4,0),(74,-120,4,0)):
            lui(o,15);st(o+4,r,15,v+d,w)
        lui(82,13);lui(86,15,0x6f000);ai(90,13,13,-284+d);ai(94,15,15,-1408+rom);st(98,15,13,4)
        lui(100,15);st(104,0,15,-132+d,1);lui(108,15);ai(112,15,15,-388+obj);li(116,14,2)
        st(118,14,13,0,1);st(120,14,15,0,1);st(122,14,15,16,1);st(124,14,15,32,1);st(128,14,15,48,1)
        lui(132,14,0x6f000);ai(136,14,14,-1424+rom);st(140,13,15,12);st(142,14,15,52)
        lui(144,13,0x6f000);li(148,14,3);st(150,14,15,56,1);ai(154,13,13,-1428+rom);lui(158,14)
        st(162,13,15,20);ld(164,14,14,-128+d);lui(168,10,0x6f000);lui(172,13,0x6f000)
        ai(176,10,10,-1392+rom);ai(180,13,13,-1376+rom);st(184,10,15,4);st(186,11,15,8,1);st(188,0,15,10,2)
        st(192,11,15,24,1);st(194,0,15,26,2);st(198,12,15,28);st(200,13,15,36);st(202,0,15,40,1);st(206,0,15,42,2)
        st(210,0,15,44);st(214,0,15,58,2);st(218,14,15,60);lui(220,15);lui(224,14,0x4b000)
        ai(228,15,15,-324+obj);ai(232,14,14,1280+152*index);st(236,0,15,0);st(240,14,15,4);st(242,0,15,8);ret(246)
    elif part=='pool':
        lui(0,15);ld(4,14,15,949+d,1);li(8,13,-1);li(10,15,0);e(12,'bltu',rs1=15,rs2=14,target=pc+18);ret(16)
        st(18,13,10,0,2);st(20,0,10,2,1);ai(24,15,15,1);ai(26,10,10,4);e(28,'jump',target=pc+12)
    elif part=='outer_return':
        ld(0,1,2,12);ai(2,2,2,16);e(4,'jal',rd=0,target=STARTS[index][5])
    elif part=='special_ID':lui(0,15);st(4,10,15,942+d,1);ret(8)
    else:
        lui(0,15);ld(4,15,15,513+d,1);e(8,'andi',rd=15,rs1=15,imm=3);e(10,'bnez',rs1=15,target=pc+30)
        li(12,10,24);ret(14);li(16,10,24);ld(18,1,2,12);ld(20,8,2,8);ld(22,9,2,4);ld(24,18,2,0);ai(26,2,2,16);ret(28)
        ai(30,2,2,-16);st(32,9,2,4);lui(34,9);st(38,8,2,8);ld(40,8,9,1525+d,1);st(44,1,2,12);st(46,18,2,0)
        ai(48,15,0,255);e(52,'bne',rs1=8,rs2=15,target=pc+16);lui(56,10,0x6d000);ai(60,10,10,620+492*index)
        call(64,role.DETAILS[index]['reg']);st(68,10,9,1525+d,1);e(72,'beq',rs1=10,rs2=8,target=pc+16)
        lui(76,15);st(80,0,15,-16+d);lui(84,15);li(88,14,4);st(90,0,15,1484+d);lui(94,15);st(98,14,15,1524+d,1)
        lui(102,9);call(106,STARTS[index][6]);li(110,12,16);li(112,11,0);ai(114,10,9,1492+d)
        pair(118,0x1ff93000,-588-492*index);lui(126,8);li(130,12,16);li(132,11,0);ai(134,10,8,1508+d)
        pair(138,0x1ff93000,-608-492*index)
        for o,v,r in ((146,1450,0),(154,1488,0),(164,1449,14)):
            lui(o,15)
            if o==154:li(158,14,7);st(160,0,15,v+d,1)
            else:st(o+4,r,15,v+d,1)
        lui(172,18);lui(176,15);ai(180,12,9,1492+d);li(184,11,16);li(186,10,2);st(188,0,15,1544+d,1);st(192,0,18,-12+d)
        call(196,0x440c2+148*index);ai(200,12,8,1508+d);li(204,11,16);li(206,10,3);call(208,0x440c2+148*index)
        lui(212,10);li(216,12,16);ai(218,11,9,1492+d);ai(222,10,10,1528+d);pair(226,0x1ff93000,-802-492*index)
        lui(234,10);li(238,12,16);ai(240,11,8,1508+d);ai(244,10,10,1464+d);pair(248,0x1ff93000,-824-492*index)
        ai(256,12,18,-12+d);li(260,11,4);li(262,10,4);call(264,0x440c2+148*index);li(268,10,0);e(270,'jump',target=pc+18)
    return pc,s


def body(raw,part,index):
    k=PARTS.index(part);pc,s=specs(part,index);n=decode(raw,pc)
    check(set(n)==set(s),'id11 '+part+' boundaries')
    for p,f in s.items():init.g(n,p,'id11 '+part+' operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[k],HASHES[index][k]),'id11 '+part+' identity')
    edges={};calls=[];tails=[]
    for p,d in n.items():
        op=d['op'];q=[p+d['size']]
        if op=='jr':check(d['rs1']==1,'id11 ordinary RET');q=[]
        elif op in ('beqz','bnez','beq','bne','bltu'):q.append(d['target'])
        elif op=='jump':q=[d['target']]
        elif op in ('jal','jalr'):
            if op=='jal':t=d['target']
            else:
                a=n[p-4];check(a['op']=='auipc' and a['rd']==d['rs1'],'id11 adjacent PC pair');t=(p-4+a['imm']+d['imm'])&0xfffffffe
            row={'pc':hex(p),'target':hex(t),'rd':d['rd']}
            if d['rd']==0:tails.append(row);q=[]
            else:calls.append(row)
        check(all(v in n for v in q),'id11 '+part+' closed local CFG');edges[p]=q
    seen={pc};todo=[pc]
    while todo:
        for q in edges[todo.pop()]:
            if q not in seen:seen.add(q);todo.append(q)
    check(seen==set(n),'id11 '+part+' all nodes locally reachable')
    stores=[x for x in n.values() if x['op']=='store'];defs=sorted({x['rd'] for x in n.values() if x.get('rd',0)})
    check(len(stores)==(4,24,35,2,0,13,1)[k],'id11 '+part+' store census')
    check((len(calls),len(tails))==((3,1),(2,0),(0,0),(0,0),(0,1),(9,0),(0,0))[k],'id11 '+part+' call census')
    if part in ('defaults','pool','special_ID'):check(not set(defs)&{1,2,3,4,8,9,18,19,20,21,22,23,24,25,26,27},'id11 leaf preserves RA/SP/GP/S locally')
    if part=='pool':check([p-pc for p,d in n.items() if d['op']=='jr']==[16],'id11 pool sole in-loop RET, excludes next LI0/RET function')
    return {'start':hex(pc),'bytes':len(raw),'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),'encoded_GPR_definitions':defs,
        'store_count':len(stores),'calls':calls,'tails':tails,'conditional_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},
        'complete_function':part!='outer_return','calls_are_return_premises':True}


def fixed_rows(part,index):
    base=0x20003000;d=80*index;obj=76*index
    if part=='factory':
        a=[(o,base+v+d,z) for o,v,z in ((6,-164,4),(16,-166,1),(26,-305,1),(34,-169,1),(42,-308,1),(50,-172,2),(58,-292,1),(72,-160,1),(90,-291,1),
            (106,-302,1),(126,-300,4),(132,-296,4),(138,-306,1),(148,-307,1),(156,-290,1),(168,-150,1),(184,-304,1),(200,-303,1),(208,-167,1))]
        return a+[(o,base-400+obj+v,4) for o,v in ((228,0),(242,4),(244,8))]
    if part=='defaults':
        a=[(o,base+v+d,z) for o,v,z in ((12,-273,1),(20,-274,1),(28,-288,1),(36,-289,1),(46,-276,2),(54,-134,2),(62,-124,4),(70,-108,4),(78,-120,4),(98,-280,4),(104,-132,1),(118,-284,1))]
        a.extend((o,base-388+obj+v,z) for o,v,z in ((120,0,1),(122,16,1),(124,32,1),(128,48,1),(140,12,4),(142,52,4),(150,56,1),(162,20,4),
            (184,4,4),(186,8,1),(188,10,2),(192,24,1),(194,26,2),(198,28,4),(200,36,4),(202,40,1),(206,42,2),(210,44,4),(214,58,2),(218,60,4)))
        return a+[(o,base-324+obj+v,4) for o,v in ((236,0),(240,4),(242,8))]
    return []


def domains():
    rows=[]
    for n in range(256):
        start=190*n+6;end=start+4*n;request=194*n+6
        check(end==request and all(start+4*j+3<=request for j in range(n)),'id11 reserved4N margin extents')
        check(n<=255 and 4*n<=1020,'id11 loaded U8 loop bound')
        rows.append({'fresh_count':n,'margin_start':start,'margin_bytes':4*n,'request_end':request,'writes_per_record_bytes':3,'unwritten_byte_per_record':3})
    return rows


def gate_paths(gate):
    pc=int(gate['start'],16);e={int(p,16):[int(q,16) for q in qs] for p,qs in gate['conditional_CFG'].items()}
    choices={'low2_zero':{10:12},'cached_ID_notFF':{10:30,52:16},'registration_rejected':{10:30,52:56,72:16},'admitted':{10:30,52:56,72:76}}
    return {name:paths.chain(e,pc,{pc+p:pc+q for p,q in c.items()}) for name,c in choices.items()}


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[]
    for i,(data,pr) in enumerate(zip(carriers,parent['profiles'])):
        base=0x20003000;g=base+80*i;d=role.DETAILS[i];ctx=base+d['ctx'];F=ctx+80;pc,fp,dp,pp,ep,gp,ip=STARTS[i]
        windows={p:body(init.binding.take(data,STARTS[i][k],SIZES[k]),p,i) for k,p in enumerate(PARTS)}
        check(pr['cut_before_sixth_outer_initializer']['A0']==11 and pr['cut_before_sixth_outer_initializer']['target']==hex(pc),'id11 inherited entryID11')
        cbreg=leaves.body(init.binding.take(data,0x4efe2+152*i,42),'callback_register',i)
        protected=[(ctx+1,1),(ctx+2,1),(ctx+3,1),(ctx+40,4),(paths.layout.T,4*212),(F+21,1),(F+36,4),(F+48,4),(F+68,4),(g-128,4),(g+948,1),(g+949,1),(g+1525,1)]
        intervals={}
        for part in ('factory','defaults'):
            b=windows[part];start=int(b['start'],16);n={x['pc']:x for x in b['instructions']};rows=fixed_rows(part,i)
            check({start+o for o,a,z in rows}=={p for p,x in n.items() if x['op']=='store' and x['rs1']!=2},'id11 '+part+' exact nonframe interval census')
            for o,a,z in rows:
                check(n[start+o]['width']==z,'id11 fixed interval width')
                for v,w in protected:check(paths.origin.separated(a,z,v,w),'id11 defaults exclude task/source/end-pointer/cache slots')
            intervals[part]=[{'pc':hex(start+o),'address':hex(a),'bytes':z} for o,a,z in rows]
        for a,z in ((g-156,6),(g+12,24)):
            for v,w in protected:check(paths.origin.separated(a,z,v,w),'id11 factory fill extents exclude protected slots')
        check([x['target'] for x in windows['factory']['calls']]==['0x2000039c']*2,'id11 factory two fill targets')
        pn={x['pc']:x for x in windows['initializer']['instructions']};cn={x['pc']:x for x in windows['pool']['instructions']};dn={x['pc']:x for x in windows['defaults']['instructions']}
        check(pn[pc+6]['rd']==8 and pn[pc+6]['rs2']==10 and pn[pc+20]['rs2']==8 and pn[pc+40]['rs2']==8,'id11 two IDbyte stores use saved S0 input')
        check(pn[pc+28]['imm']==-128+80*i and cn[pp+4]['imm']==949+80*i,'id11 margin pointer and low2 source')
        source=resources.body(init.binding.take(data,resources.STARTS[i][2],266),'resources',i);sn={x['pc']:x for x in source['instructions']};sp=int(source['start'],16)
        init.g(sn,sp+180,'id11 earlier resource end-pointer slot',op='store',rs1=19,rs2=15,imm=0,width=4)
        init.g(sn,sp+70,'id11 earlier end-pointer base',op='addi',rd=19,rs1=14,imm=-128+80*i)
        check(sn[sp+114]['imm']==9 and cn[pp+4]['imm']+base==g+949,'id11 earlier and current count byte join')
        check(dn[dp+164]['imm']==-128+80*i,'id11 defaults captures same fresh end pointer')
        check(8 not in windows['defaults']['encoded_GPR_definitions'] and 8 not in windows['pool']['encoded_GPR_definitions'],'id11 local leaves preserve saved ID S0')
        check(pn[pc+48]['imm']+pn[pc+52]['imm']==0x4cff6+152*i and pn[pc+58]['target']==int(cbreg['start'],16),'id11 callback pointer/tail')
        gn={x['pc']:x for x in windows['gate']['instructions']};outer=role.body(init.binding.take(data,d['entry'],112),'entry',i);on={x['pc']:x for x in outer['instructions']}
        check(on[d['entry']+100]['target']==pc and ep==d['entry']+104 and windows['outer_return']['tails'][0]['target']==hex(gp),'id11 final call to outer released frame/gate join')
        check(gn[gp+4]['imm']+base==F+21 and gn[gp+40]['imm']+base==g+1525,'id11 final gate source byte/cache geometry')
        reg=registration.body(init.binding.take(data,d['reg'],48),i);check(11 not in reg['encoded_GPR_definitions'],'id11 special registration preserves A1')
        check(gn[gp+56]['imm']+gn[gp+60]['imm']==0x6d26c+492*i and gn[gp+64]['target']==d['reg'],'id11 optional13thtask handler/register')
        check(12<14 and paths.layout.T+52<=paths.layout.T+56,'id11 optional entry12 capacity extent')
        check([x['target'] for x in windows['gate']['calls']]==[hex(d['reg']),hex(ip),'0x2000039c','0x2000039c',hex(0x440c2+148*i),hex(0x440c2+148*i),'0x20000332','0x20000332',hex(0x440c2+148*i)],'id11 gate exact call list')
        check(not any(x.get('rd')==10 for p,x in gn.items() if gp+68<=p<gp+106),'id11 admitted ID carried to setter before any A0 definition')
        pairs=[(g+1492,g+1528,16),(g+1508,g+1464,16)]
        for a,b,z in pairs:check(paths.origin.separated(a,z,b,z),'id11 copy source/destination separated')
        cases=gate_paths(windows['gate']);check(len(cases)==4,'id11 final gate four path census')
        check(hex(gp+30) not in cases['low2_zero'] and all(hex(gp+64) not in cases[k] for k in ('low2_zero','cached_ID_notFF')),'id11 skip cases exclude registration')
        ROM=[0x6f000+v+496*i for v in (-1408,-1424,-1428,-1392,-1376)]
        check(all(v>0x40000+len(data) for v in ROM),'id11 stored ROM pointers outside supplied candidate bytes')
        profiles.append({'label':pr['label'],'bodies':windows,'inherited_entry':pr['cut_before_sixth_outer_initializer'],'fixed_intervals':intervals,
            'ID11':{'entry_saved_in':'S0 full32','local_frame_bytes':16,'nested_factory_frame_bytes':16,'IDbytes':[hex(g-289),hex(g-274)],'values':[11,11],
                'required_preservation':'factory fill providers preserve its live S0=2 and frames; factory restores caller S0=ID11; defaults/pool have no local S0 definitions',
                'callback_pointer':hex(0x4cff6+152*i),'callback_registration_reply':'0 if inserted,19 if full; both return to outer','callback_invoked':False},
            'pool_margin':{'end_pointer_word':hex(g-128),'count_byte':hex(g+949),'generic_count_range':[0,255],'retained_low2_range':[0,3],
                'earlier_source_body':source['start'],'earlier_source_sha256':source['sha256'],'start_formula':'P+190*N+6','end_formula':'P+194*N+6',
                'loop':'N records stride4: SHffff@0,SB0@2; byte+3 untouched; fullword index increments without truncation; N read once before loop',
                'reply_A0':'entry_pointer+4*N modulo2^32, not forced0','zero_count':'no input pointer dereference, so pointer0 does not by itself prevent this leaf RET',
                'layout_premises':'earlier allocated extent>=194*N+6; same retained N and end pointer at all required phases; valid nonwrapping physical nonalias block and provider/metadata/frame preservation; current stores cover exactly3 of each4 reserved bytes',
                'actual_end_pointer/count_retention_proved':False},
            'profile_layout':{'most_scalar_RAM_delta':80,'three_RAM_object_base_delta':76,'ROM_pointer_delta':496,'stored_ROM_pointers':[hex(v) for v in ROM],
                'stored_ROM_contents_available':False,'pointer_stores_do_not_dereference_external_ROM':True},
            'outer_return':{'frame_bytes_released':16,'incoming_initializer_reply_not_tested':True,'tail_gate':hex(gp)},
            'final_gate':{'fresh_source':hex(F+21),'mask':3,'cached_ID_byte':hex(g+1525),'paths':cases,
                'return24_cases':['freshlow2==0: noframe','freshlow2!=0 and cachedID!=ff: restore16Bframe','freshlow2!=0,cachedIDff and taskregistrationreplyff: restore16Bframe'],
                'actual_gate_values_proved':False,'extra_task_conditions':{'freshlow2':'nonzero','fresh_cached_ID':255,'fresh_count':12,'fresh_capacity':'>=14','fresh_table':hex(paths.layout.T),
                    'handler':hex(0x6d26c+492*i),'entry12':hex(paths.layout.T+48),'reply_ID':12,'new_count':13,'registration_reply_byte_stored_before_test':True},
                'special_ID_setter':{'target':hex(ip),'destination':hex(g+942),'value_when_fresh_count12':12,'overwrites_earlier_FF':True},
                'success_calls':{'fill16':[hex(g+1492),hex(g+1508)],'NV_reads':[[2,16,hex(g+1492)],[3,16,hex(g+1508)],[4,4,hex(g-12)]],
                    'copy16':[{'source':hex(a),'destination':hex(b),'bytes':z} for a,b,z in pairs]},
                'successful_path_reply_A0':0,'A1_A2_after_last_service':'opaque, not forced afterNV read','service_reply_values_tested':False,
                'premises':'all fill/copy/NV return, preserve S0/S1/S2/SP/frame/RA/GP/code and required source/table state; correct extents/units, physical nonalias and no interfering writers; actual outputs remain unknown'},
            'actual_installed_binding_proved':False,'actual_NV_or_callback_execution':False})
    return {'schema':'TSL9-ID11-outer-tail-static-v1','profile':parent['profile'],'APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'margin_domains':domains(),
        'scope':'per candidate62B lastinitializer/252B factory/248B defaults/30B poolclear/8B outerepilogue/272B finalgate/10B IDsetter;1764B/528 operand guards;poolreservedmargin andfour finalgate paths perprofile',
        'boundary':'six outer initializers now have original local-byte contracts; full-chain progress/installed providers remain conditional. Final gate returns24 on three classes, or conditionally admits ID12/count13 then returns0 after NV/copy services',
        'remaining':['actual bindings/provider outputs and frame/source/payload lifetimes across the full chain','special handler6d26c/6d458 and callback4cff6/4d08e consumers','RAM/ROM source gaps and all flag/count/cache writers; actual application return chain'],
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
                except RuntimeError as e:check(str(e).startswith('id11 '+part+' operand '),'id11 specified mutation guard '+str(e))
                else:raise RuntimeError('id11 mutation escaped')
                mutations+=1
    check(mutations==528 and sum(SIZES)*2==1764,'id11 mutation/byte census');domains()
    check(sum((v&3)==0 for v in range(256))==64,'id11 fresh low2 zero domain')
    print('PASS:528 operand mutations rejected;1764 original bytes;256 reserved-margin domains;8 final-gate CFG path certificates')


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
    else:check(OUT.read_bytes()==output,'id11 exact ledger replay')
    print('PASS:ID11 saved publication and4N reserved-margin link;final24/conditional0 replies and optionalID12/count13;exact ledger')
    print('PASS:NO target execution/emulation;actual provider outputs/full-chain progress/object lifetimes UNPROVED')


if __name__=='__main__':main()
