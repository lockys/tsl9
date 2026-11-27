"""Offline query jump table, request consumer and conditional slot cleanup.

Original operands/closed CFG and integer identities only. No target execution,
emulation, RAM/register machine, provider, allocator, RF, NV or MMIO model.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_special_request_static as previous

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-request-consumers-static.json')
PARTS=('query','fallback','cleanup')
STARTS=((0x6bc2e,0x48070,0x47fc8),(0x6be12,0x48108,0x48060))
SIZES=(340,298,36)
COUNTS=(111,109,13)
HASHES=(('25f3f8c1811692c1efccf1608e92a89e8573ce61136bac99e5a4222c57ae756e','e3410befc80c9d068023882b21e711d7bed140d617d2f16d3fc8fba49f9405c8','dc353407955d24806a0d73ff8c73bb7f2ad0ba862ec5dbf53c4b86b2f4ce9567'),
 ('ceb0f0f635c5505059fde7dc83b908fdae951b6800194b2d1898764ff15d4a7f','6e9c99cf61581ff351e25600a64ae6e5cba3b03158c5d3580987bcc9181edda0','f840cadb4dc189b798d05d2e5cbde566b3f2de123d31abca6bbe99bfd81d8793'))
TABLE_HASHES=('33599e90d51ba2bf44a1dbdaae77b3953bc9c07fe8b6bdd202d3be5fc85f3799','1d207e71b34f6bd3e01de62532033b3663315e741b356a55bacbb6b20e525444')
TABLE_OFFSETS=(40,52,64,74,84,116,128,138,150,160,170,180,190,202,212,222,322,232,242,252,262,282,322,322,322,322,322,322,322,322,290,272,322,300,312)


def specs(part,index):
    pc=STARTS[index][PARTS.index(part)];d=80*index;s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def lui(o,r,v=0x20003000):e(o,'lui',rd=r,imm=v)
    def ai(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    def ld(o,r,b,v,w=4):e(o,'load',rd=r,rs1=b,imm=v,width=w)
    def st(o,r,b,v,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    def mv(o,r,b):e(o,'mv',rd=r,rs2=b)
    def imm(o,op,r,b,v):e(o,op,rd=r,rs1=b,imm=v)
    def br(o,op,a,b,t):e(o,op,rs1=a,rs2=b,target=pc+t)
    def bz(o,r,t):e(o,'beqz',rs1=r,target=pc+t)
    def j(o,t):e(o,'jump',target=pc+t)
    def call(o,t):e(o,'jal',rd=1,target=t)
    def ret(o):e(o,'jr',rs1=1)
    if part=='query':
        ai(0,15,10,-1024);ai(4,2,2,-16);imm(6,'slli',15,15,16);st(8,8,2,8);st(10,1,2,12);imm(12,'srli',15,15,16)
        ai(14,14,0,34);mv(18,8,11);br(20,'bltu',14,15,322);lui(24,14,0x6e000+4096*index);imm(28,'slli',15,15,2)
        ai(30,14,14,1728-3600*index);e(34,'add',rd=15,rs1=15,rs2=14);ld(36,15,15,0);e(38,'jr',rs1=15)
        lui(40,15);ld(44,15,15,-266+d,1);st(48,15,8,0,1);j(50,104)
        lui(52,15);ld(56,15,15,-52+d,1);imm(60,'srai',15,15,2);j(62,124)
        for o,src in ((64,-51),(74,-49)):
            lui(o,15);ld(o+4,15,15,src+d,1);j(o+8,48)
        lui(84,11);li(88,12,16);ai(90,11,11,380+d);mv(94,10,8);e(96,'auipc',rd=1,imm=0x1ff94000);e(100,'jalr',rd=1,rs1=1,imm=1700-484*index)
        li(104,15,0);ld(106,1,2,12);ld(108,8,2,8);mv(110,10,15);ai(112,2,2,16);ret(114)
        lui(116,15);ld(120,15,15,-52+d,1);imm(124,'andi',15,15,1);j(126,48)
        lui(128,15);ld(132,15,15,-50+d,1);j(136,48);lui(138,15);ld(142,15,15,-48+d);st(146,15,8,0);j(148,104)
        for o,src,target in ((150,-269,48),(160,-60,60),(170,-59,48),(180,-57,48)):
            lui(o,15);ld(o+4,15,15,src+d,1);j(o+8,target)
        lui(190,11);li(194,12,16);ai(196,11,11,364+d);j(200,94)
        for o,src,target,width in ((202,-60,124,1),(212,-58,48,1),(222,-56,146,4),(232,-61,48,1),(242,-271,48,1),(252,-267,48,1),(262,-71,48,1),(272,-72,48,1)):
            lui(o,15);ld(o+4,15,15,src+d,width);j(o+8,target)
        call(282,0x6af88+484*index);st(286,10,8,0,1);j(288,104);lui(290,15);ld(294,15,15,-268+d,1);j(298,48)
        lui(300,15);ld(304,15,15,-52+d,1);imm(308,'srai',15,15,3);j(310,124);lui(312,15);ld(316,15,15,-60+d,1);j(320,308)
        ai(322,14,0,65+index);li(326,15,2);br(328,'bltu',14,10,106);call(332,0x45f9c+152*index);st(336,10,8,0,2);j(338,104)
    elif part=='fallback':
        ai(0,2,2,-144);st(2,8,2,136);lui(4,8);ld(8,15,8,-236+d)
        for o,r,v in ((12,1,140),(14,9,132),(16,18,128),(18,19,124),(20,20,120),(22,21,116),(24,22,112),(26,23,108),(28,24,104)):st(o,r,2,v)
        li(30,10,1);br(32,'beq',15,0,274);ai(36,11,2,95);ai(40,10,0,1055);call(44,STARTS[index][0]);ai(48,11,2,95);ai(52,10,0,1055);call(56,STARTS[index][0])
        lui(60,15);ai(64,15,15,584+d);ld(68,15,15,2,1);ld(70,14,2,95,1);e(74,'sltu',rd=15,rs1=0,rs2=15);bz(78,14,82);ai(80,15,15,2)
        ld(82,14,8,-236+d);st(86,15,2,76);ld(88,10,14,3,1);ai(90,11,14,4);call(94,0x45612+152*index)
        ld(98,14,8,-236+d);st(102,10,2,72);li(104,10,3);ld(106,11,14,2,1);st(108,11,2,68);call(110,0x45f9c+152*index)
        st(114,10,2,64);li(116,10,4);call(118,0x45f9c+152*index);ld(122,8,8,-236+d);st(126,10,2,60);li(128,10,25);ld(130,14,8,10,1);ld(132,24,8,11,1);st(136,14,2,56);call(138,0x45f9c+152*index);mv(142,9,10)
        for o,param,reg in ((144,26,18),(152,28,19),(160,27,20),(168,29,21),(176,30,22)):
            li(o,10,param);call(o+2,0x45f9c+152*index);mv(o+6,reg,10)
        ai(184,10,0,64);call(188,0x45f9c+152*index);mv(192,23,10);ai(194,10,0,65);call(198,0x45f9c+152*index)
        imm(202,'slli',9,9,24)
        for o,r,v in ((204,16,72),(206,15,76),(208,14,56),(210,13,60),(212,12,64),(214,11,68)):ld(o,r,2,v)
        imm(216,'andi',10,10,255)
        for o,r in ((220,23),(224,22),(228,21),(232,20),(236,19),(240,18)):imm(o,'andi',r,r,255)
        imm(244,'srai',9,9,24)
        for o,r,v in ((246,10,32),(248,23,28),(250,22,24),(252,21,20),(254,20,16),(256,19,12),(258,18,8),(260,9,4),(262,24,0)):st(o,r,2,v)
        ai(264,17,8,4);li(268,10,1);call(270,0x533ce+174*index)
        for o,r,v in ((274,1,140),(276,8,136),(278,9,132),(280,18,128),(282,19,124),(284,20,120),(286,21,116),(288,22,112),(290,23,108),(292,24,104)):ld(o,r,2,v)
        ai(294,2,2,144);ret(296)
    else:
        ai(0,2,2,-16);st(2,8,2,8);lui(4,8);ld(8,10,8,-236+d);st(12,1,2,12);bz(14,10,28)
        e(16,'auipc',rd=1,imm=0x1ffb8000);e(20,'jalr',rd=1,rs1=1,imm=312-152*index);st(24,0,8,-236+d);ld(28,1,2,12);ld(30,8,2,8);ai(32,2,2,16);ret(34)
    return s


def table(raw,index):
    pc=STARTS[index][0];words=[int.from_bytes(raw[o:o+4],'little') for o in range(0,len(raw),4)]
    check(len(raw)==140 and len(words)==35,'consumers table size')
    for i,(v,off) in enumerate(zip(words,TABLE_OFFSETS)):check(v==pc+off,'consumers table entry '+str(i))
    check(sha256(raw).hexdigest()==TABLE_HASHES[index],'consumers table identity')
    return {'start':hex(0x6e6c0+496*index),'bytes':140,'sha256':sha256(raw).hexdigest(),'targets':[hex(v) for v in words],
            'index_expression':'low16(entryA0-1024); table only ifindex<=34','query1055_index':31,'query1055_target':hex(pc+272)}


def body(raw,part,index,t):
    k=PARTS.index(part);pc=STARTS[index][k];n=decode(raw,pc);s=specs(part,index)
    check(set(n)==set(s),'consumers '+part+' boundaries')
    for p,f in s.items():init.g(n,p,'consumers '+part+' operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[k],HASHES[index][k]),'consumers '+part+' identity')
    edges={};calls=[]
    for p,d in n.items():
        op=d['op'];q=[p+d['size']]
        if op=='jr':
            if d['rs1']==1:q=[]
            else:check(part=='query' and p==pc+38 and d['rs1']==15,'consumers only tableJR');q=list(dict.fromkeys(int(v,16) for v in t['targets']))
        elif op in ('beq','beqz','bltu'):q.append(d['target'])
        elif op=='jump':q=[d['target']]
        elif op in ('jal','jalr'):
            if op=='jal':target=d['target']
            else:
                a=n[p-4];check(a['op']=='auipc' and a['rd']==d['rs1'],'consumers pairedPC');target=(p-4+a['imm']+d['imm'])&0xfffffffe
            check(d['rd']==1,'consumers call link');calls.append({'pc':hex(p),'target':hex(target)})
        check(all(v in n for v in q),'consumers closed '+part+' CFG');edges[p]=q
    seen=set();active=set()
    def visit(p):
        check(p not in active,'consumers acyclic '+part)
        if p in seen:return
        active.add(p)
        for q in edges[p]:visit(q)
        active.remove(p);seen.add(p)
    visit(pc);check(seen==set(n),'consumers all '+part+' nodes reachable')
    stores=[d for d in n.values() if d['op']=='store'];check((len(calls),len(stores))==((3,6),(14,25),(1,3))[k],'consumers '+part+' call/store census')
    if part=='fallback':check(all(v['rs1']==2 for v in stores),'consumers fallback only explicit frame stores')
    return {'start':hex(pc),'end_exclusive':hex(pc+SIZES[k]),'bytes':SIZES[k],'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),
            'calls':calls,'store_count':len(stores),'conditional_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},'complete_local_body':True,'local_CFG_acyclic':True}


def certificates(b,part,t):
    pc=int(b['start'],16);e={int(p,16):[int(q,16) for q in qs] for p,qs in b['conditional_CFG'].items()}
    if part=='query':
        cases={'index'+str(i):{20:24,38:int(v,16)-pc,328:106} for i,v in enumerate(t['targets'])}
        cases.update({'small_ID_param':{20:322,328:332},'large_ID_invalid':{20:322,328:106}})
    elif part=='fallback':cases={'slot_null':{32:274},'slot_present_output0':{32:36,78:82},'slot_present_output_nonzero':{32:36,78:80}}
    else:cases={'slot_null':{14:28},'slot_present':{14:16}}
    return {name:previous.previous.paths.chain(e,pc,{pc+p:pc+q for p,q in c.items()}) for name,c in cases.items()}


def domains():
    admitted=[i for i in range(65536) if ((i-1024)&65535)<=34]
    check(admitted==list(range(1024,1059)),'consumers exact low16 query admission')
    for upper in (0,1,32768,65535):check((((upper<<16)|1055)-1024)&65535==31,'consumers1055 upper16 aliases')
    signed=[b-256 if b&128 else b for b in range(256)]
    check(all((((b<<24)^0x80000000)-0x80000000)>>24==v for b,v in enumerate(signed)),'consumers signed query25 lowbyte')
    flags=[int(a!=0)+2*int(b!=0) for a in range(256) for b in range(256)]
    check({v:flags.count(v) for v in range(4)}=={0:1,1:255,2:255,3:65025},'consumers boolrole/output packing')
    return {'admitted_low16_IDs':[1024,1058],'low16_cases':65536,'query1055_index':31,'upper16_alias_vectors':[0,1,32768,65535],
            'query25_lowbyte_signed_range':[-128,127],'flag_pack_counts':{str(v):flags.count(v) for v in range(4)},
            'byte11_extent':'P+11 is within requested12byte allocation only under valid allocator output/nonalias assumptions'}


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[]
    for i,(data,pr) in enumerate(zip(carriers,parent['profiles'])):
        rawtable=init.binding.take(data,0x6e6c0+496*i,140);t=table(rawtable,i)
        windows={part:body(init.binding.take(data,STARTS[i][k],SIZES[k]),part,i,t) for k,part in enumerate(PARTS)}
        certs={part:certificates(b,part,t) for part,b in windows.items()};check(sum(len(v) for v in certs.values())==42,'consumers42 certificates/profile')
        g=0x20003000+80*i;qp=STARTS[i][0];qn={d['pc']:d for d in windows['query']['instructions']};fp=STARTS[i][1];fn={d['pc']:d for d in windows['fallback']['instructions']}
        check(pr['query_and_return']['query1055']==hex(qp) and pr['query_and_return']['fallback']['target']==hex(fp) and pr['query_and_return']['fallback']['nonnull_reply_extra_call']==hex(STARTS[i][2]),'consumers joins published request calls')
        check(qn[qp+24]['imm']+qn[qp+30]['imm']==int(t['start'],16),'consumers table base from exact instructions')
        p1055=certs['query']['index31'];check(all(hex(qp+o) in p1055 for o in (272,276,280,48,104,110,114)),'consumers1055 byte store and return0 chain')
        check(not any(c['pc'] in p1055 for c in windows['query']['calls']),'consumers1055 no provider call')
        check(windows['cleanup']['calls'][0]['target']=='0x20000110','consumers cleanup actual paired target')
        check([fn[fp+o]['imm'] for o in (36,48)]==[95,95] and [fn[fp+o]['target'] for o in (44,56)]==[qp,qp],'consumers two fresh1055 calls shareSP95')
        profiles.append({'label':pr['label'],'bodies':windows,'query_table':t,'selected_CFG_paths':certs,
            'query1055':{'source':hex(g-72),'operation':'freshU8[source] -> U8[entryA1], thenA0=0; no provider call on this path','output_extent_bytes':1,
                'requirements':'valid writable output and readable source; normal nonalias frame/source/code/table, valid SP/RA; installed provider identity not proved',
                'origin_unknown':'writers and actual runtime byte value not established'},
            'query_other_cases':{'index_dispatch':'35 table words validated from supplied candidate bytes; aliases based onlow16, not full original ID range',
                'small_ID_limit':65+i,'small_fallback':'outside table and unsigned entryA0<='+str(65+i)+' ->45f9c(entryA0),storelow16 reply atoutput,return0',
                'large_fallback':'outside table and unsigned entryA0>'+str(65+i)+' ->return2 without output store',
                'other_table_outputs':'byte/word local sources, bit selections, two copy16 cases via20000332 and one6af88 call; those callees remain conditional'},
            'fallback':{'frame_bytes':144,'saved':['RA','S0','S1','S2','S3','S4','S5','S6','S7','S8'],'slot':hex(g-236),'null_slot_return':1,
                'query1055_calls':'two consecutive local queries(1055,SP95); second fresh source byte supplies later SP95 read; no equality across calls assumed',
                'packed_A5':'bool(freshU8['+hex(g+586)+']) + 2*bool(second query1055 output)',
                'object_snapshots':'P0=freshslot before45612; P1=freshslot after45612; P2=freshslot afterquery4. Equality/validity across callees not assumed',
                'prepare_call':{'target':hex(0x45612+152*i),'args':['U8[P0+3]','P0+4'],'result':'full A0 saved for finalA6'},
                'query_order':[3,4,25,26,28,27,29,30,64,65],
                'final_call':{'target':hex(0x533ce+174*i),'register_args':['1','U8[P1+2]','query3 fullreply','query4 fullreply','U8[P2+10]','packedflags','45612 fullreply','P2+4'],
                    'stack_word_offsets':[0,4,8,12,16,20,24,28,32],
                    'stack_values':['U8[P2+11]','signedlow8(query25)','U8(query26)','U8(query28)','U8(query27)','U8(query29)','U8(query30)','U8(query64)','U8(query65)'],
                    'prototype_or_retention_proved':False},
                'return':'nonnull-slot path returns actual finalcallA0; epilogue does not replace it. Requires callee/frame preservation',
                'local_persistent_writes':False,'requirements':'all fresh object pointers valid and source extents at least12; query/prepare/finalcallee side effects, A7 borrowed pointer retention and stack argument consumption unproved'},
            'cleanup':{'frame_bytes':16,'saved':['RA','S0'],'slot':hex(g-236),'null_slot':'skip provider and store; ordinaryRET withA0=0',
                'nonnull_slot':'pass loadedP to20000110; after required return,store0tofixedslot; returnactualproviderA0',
                'ordering':'slot clear occurs after provider return and clears current slot unconditionally; no recheck against loadedP',
                'limits':'20000110 deallocation/retention/success not proved; no claim of actual free, leak, unique ownership or lifecycle completion'},
            'request_link':'fallback reply is saved by requestS0; nonzero reply calls cleanup but request ignores its A0; zero reply leaves slot uncleared by this local path',
            'actual_installed_bindings_proved':False,'target_execution_or_emulation':False})
    return {'schema':'TSL9-request-consumers-static-v1','profile':parent['profile'],'APP_sha256':sha256(image).hexdigest(),'profiles':profiles,
            'integer_domains':domains(),'scope':'two complete340Bquery/298Bfallback/36Bcleanup bodies;1348instructionbytes/466instructions;280tablebytes/70entries;84selectedCFGpaths',
            'boundary':'query1055 concrete local output source andreturn0; others conditional static candidate contracts only; provider behavior, source writers, borrowed pointer retention and actual installation unproved',
            'remaining':['45612 and533ce request callee read/retain contracts','source20002fb8/20003008 writers and actual values','query45f9c and other output providers','enumerator4bf06/4c35e and missingROMpattern'],
            'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    mutations=entries=paths=0
    for i,data in enumerate(carriers):
        rawtable=init.binding.take(data,0x6e6c0+496*i,140);t=table(rawtable,i)
        for k,part in enumerate(PARTS):
            pc=STARTS[i][k];raw=init.binding.take(data,pc,SIZES[k]);b=body(raw,part,i,t);paths+=len(certificates(b,part,t))
            for p,d in decode(raw,pc).items():
                at=p-pc;z=d['size'];buf=bytearray(raw);buf[at:at+z]=(int.from_bytes(buf[at:at+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
                try:body(buf,part,i,t)
                except RuntimeError as e:check(str(e).startswith('consumers '+part+' operand '),'consumers specified instruction mutation '+str(e))
                else:raise RuntimeError('consumers instruction mutation escaped')
                mutations+=1
        for at in range(0,140,4):
            buf=bytearray(rawtable);buf[at]^=2
            try:table(buf,i)
            except RuntimeError as e:check(str(e)=='consumers table entry '+str(at//4),'consumers specified table mutation')
            else:raise RuntimeError('consumers table mutation escaped')
            entries+=1
    check((mutations,entries,paths)==(466,70,84),'consumers mutation/path census');domains()
    print('PASS:466 operand and70 table-entry mutations rejected;1348 original instruction bytes+280 table bytes;84 CFG certificates;65536 ID cases/65536 flag pairs')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');o=parser.parse_args()
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
    else:check(OUT.read_bytes()==output,'consumers exact ledger replay')
    print('PASS:query1055 local byte output/return0;fallback argument and actual reply joins;cleanup ordering;exact ledger')
    print('PASS:NO target execution/emulation;provider/retention/source writers/object validity UNPROVED')


if __name__=='__main__':main()
