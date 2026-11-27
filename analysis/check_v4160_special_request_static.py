"""Original request operands, conditional CFG and borrowed-buffer boundaries.

Offline byte decoding and integer/interval certificates only; no target ISA,
register/RAM machine, allocator, copy, scheduler, callback or MMIO execution.
"""
import argparse
import json
import re
from hashlib import sha256
from pathlib import Path
import check_v4160_special_event_callback_static as previous

init,sparse,check=previous.init,previous.sparse,previous.check
OUT=Path(__file__).with_name('v4160-special-request-static.json')
STARTS=(0x482f4,0x4838c)
HASHES=('daf496c4ba5d1321c7b01c5887776ccac81745e9e3c54a674f61f50a7394c7f4',
        '39c1fb1ce4f568f611342c21fd0fe7c9a0ac595af975be5eb9adacfdba0555c1')


def decode(raw,pc):
    nodes={};off=0
    while off<len(raw):
        h=int.from_bytes(raw[off:off+2],'little');z=2 if h&3!=3 else 4;chunk=raw[off:off+z]
        check(len(chunk)==z,'request complete instruction')
        if z==2 and h&0xf863==0x8000:
            d=dict(pc=pc+off,bytes=chunk.hex(),size=2,op='load',rd=8+(h>>2&7),rs1=2,imm=h>>7&15,width=1,mnemonic='qk.c.lbusp')
        else:d=previous.decode(chunk,pc+off)[pc+off]
        nodes[pc+off]=d;off+=z
    return nodes


def encoding_source():
    sources,_=init.timer.source_contract();td=(init.timer.REF/'RISCVInstrInfoXwch.td').read_text(encoding='utf-8')
    for s in ('def QK_C_LBUSP : QKStackInst<0b00, (outs GPRC:$rd_rs2),','let Inst{10-7} = imm;',
              'let Inst{15-11} = 0b10000;','let Inst{4-2} = rd_rs2;'):
        check(s in td,'request cached LLVM LBUSP source')
    lines=(init.timer.REF/'xwchc-valid.s').read_text(encoding='utf-8').splitlines();vectors=[]
    for i,line in enumerate(lines):
        m=re.fullmatch(r'# CHECK-ASM-AND-OBJ: qk\.c\.lbusp s0, (\d+)\(sp\)',line)
        if not m:continue
        e=re.fullmatch(r'# CHECK-ASM: encoding: \[0x([0-9a-f]{2}),0x([0-9a-f]{2})\]',lines[i+1]);check(e is not None,'request official LBUSP vector')
        raw=bytes(int(v,16) for v in e.groups());d=decode(raw,0)[0]
        check((d['rd'],d['rs1'],d['imm'],d['width'])==(8,2,int(m[1]),1),'request official LBUSP decode')
        vectors.append({'bytes':raw.hex(),'offset':int(m[1]),'source_line':i+1})
    check(len(vectors)==6,'request six LBUSP vectors')
    for r in range(8,16):
        for imm in range(16):
            h=0x8000|((r-8)<<2)|(imm<<7);d=decode(h.to_bytes(2,'little'),0)[0]
            check((d['rd'],d['rs1'],d['imm'],d['width'])==(r,2,imm,1),'request128 LBUSP field combinations')
    return {'sources':sources,'vectors':vectors,'field_cases':128,'actual_encoding':'9c83 = LBU A5,7(SP); unsigned byte'}


def specs(index):
    pc=STARTS[index];d=80*index;s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def lui(o,r,v=0x20003000):e(o,'lui',rd=r,imm=v)
    def ai(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    def ld(o,r,b,v,w=4):e(o,'load',rd=r,rs1=b,imm=v,width=w)
    def st(o,r,b,v,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    def mv(o,r,b):e(o,'mv',rd=r,rs2=b)
    def bz(o,r,t):e(o,'beqz',rs1=r,target=pc+t)
    def bnz(o,r,t):e(o,'bnez',rs1=r,target=pc+t)
    def br(o,op,a,b,t):e(o,op,rs1=a,rs2=b,target=pc+t)
    def j(o,t):e(o,'jump',target=pc+t)
    def call(o,t):e(o,'jal',rd=1,target=t)
    def imm(o,op,r,b,v):e(o,op,rd=r,rs1=b,imm=v)
    def pair(o,low):e(o,'auipc',rd=1,imm=0x1ffb8000);e(o+4,'jalr',rd=1,rs1=1,imm=low-152*index)
    ai(0,2,2,-48);st(2,18,2,32);lui(4,18);ld(8,15,18,-236+d)
    for o,r,v in ((12,8,40),(14,1,44),(16,9,36),(18,19,28),(20,20,24),(22,21,20)):st(o,r,2,v)
    li(24,8,17);bnz(26,15,202);lui(28,9);ai(32,15,9,940+d);ld(36,15,15,4,1);li(38,8,18)
    imm(40,'andi',15,15,5);bz(42,15,202);lui(44,15);mv(48,20,11);lui(50,11,0x4000);st(52,10,15,-195+d,1)
    mv(56,19,10);ai(58,11,11,1815);li(62,10,12);pair(64,-756);st(72,10,18,-236+d);li(76,8,19);bz(78,10,202)
    st(80,19,10,0,1);st(84,0,10,1,1);li(88,12,10);mv(90,11,20);ai(92,10,10,2);pair(94,-32)
    ld(102,15,18,-236+d);li(106,13,4);ld(108,14,15,2,1);br(110,'bltu',13,14,256);bnz(114,14,222)
    li(116,14,19);st(118,14,15,2,1);ld(120,14,15,2,1);imm(122,'ori',14,14,16);st(126,14,15,2,1)
    ai(128,11,2,7);ai(132,10,0,1055);call(136,0x6bc2e+484*index);ld(140,15,2,7,1);bnz(142,15,346)
    lui(144,15);ld(148,14,15,586+d,1);li(152,15,3);br(154,'bne',14,15,346)
    call(158,0x456ea+152*index);ai(162,11,2,8);call(164,0x4fd72+152*index);ai(168,10,2,8);call(170,0x45d3a+152*index)
    li(174,10,17);call(176,0x45f9c+152*index);li(180,8,0);bz(182,10,202);ai(184,12,0,1600)
    e(188,'mul',rd=12,rs1=10,rs2=12);ld(192,10,9,940+d,1);li(196,11,4);call(198,0x43728+140*index)
    mv(202,10,8)
    for o,r,v in ((204,1,44),(206,8,40),(208,9,36),(210,18,32),(212,19,28),(214,20,24),(216,21,20)):ld(o,r,2,v)
    ai(218,2,2,48);e(220,'jr',rs1=1)
    li(222,13,1);br(224,'bne',14,13,232);li(228,14,29);j(230,118)
    li(232,13,2);br(234,'bne',14,13,242);li(238,14,18);j(240,118)
    li(242,13,3);br(244,'bne',14,13,252);li(248,14,16);j(250,118);li(252,14,21);j(254,118)
    li(256,13,5);mv(258,21,18);br(260,'beq',14,13,286);li(264,13,6);br(266,'bne',14,13,276)
    li(270,14,2);st(272,14,15,2,1);j(274,286);li(276,12,7);br(278,'bne',14,12,314);st(282,0,15,2,1)
    li(286,10,25);call(288,0x45f9c+152*index);ai(292,15,0,127);br(296,'beq',10,15,128)
    ld(300,14,21,-236+d);ld(304,15,14,2,1);imm(306,'ori',15,15,64);st(310,15,14,2,1);j(312,128)
    li(314,12,8);br(316,'bne',14,12,324);li(320,14,1);j(322,272);li(324,12,9);br(326,'bne',14,12,334)
    st(330,13,15,2,1);j(332,286);li(334,13,10);li(336,8,1);br(338,'bne',14,13,202);li(342,14,4);j(344,272)
    call(346,0x48070+152*index);mv(350,8,10);bz(352,10,202);call(354,0x47fc8+152*index);j(358,202)
    return s


def body(raw,index):
    pc=STARTS[index];s=specs(index);n=decode(raw,pc)
    check(set(n)==set(s),'request boundaries')
    for p,f in s.items():init.g(n,p,'request operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(360,132,HASHES[index]),'request identity')
    edges={};calls=[]
    for p,d in n.items():
        op=d['op'];q=[p+d['size']]
        if op=='jr':check(d['rs1']==1,'request return register');q=[]
        elif op in ('beq','bne','beqz','bnez','bltu'):q.append(d['target'])
        elif op=='jump':q=[d['target']]
        elif op in ('jal','jalr'):
            if op=='jal':t=d['target']
            else:
                a=n[p-4];check(a['op']=='auipc' and a['rd']==d['rs1'],'request paired PC target');t=(p-4+a['imm']+d['imm'])&0xfffffffe
            check(d['rd']==1,'request link call');calls.append({'pc':hex(p),'target':hex(t)})
        check(all(v in n for v in q),'request closed CFG');edges[p]=q
    seen=set();active=set()
    def visit(p):
        check(p not in active,'request acyclic local CFG')
        if p in seen:return
        active.add(p)
        for q in edges[p]:visit(q)
        active.remove(p);seen.add(p)
    visit(pc);check(seen==set(n),'request all instructions locally reachable')
    stores=[(p-pc,d['rs1'],d['rs2'],d['imm'],d['width']) for p,d in n.items() if d['op']=='store']
    check(len(calls)==11 and len(stores)==17,'request call/store census')
    check([v for v in stores if v[1]==2]==[(2,2,18,32,4),(12,2,8,40,4),(14,2,1,44,4),(16,2,9,36,4),(18,2,19,28,4),(20,2,20,24,4),(22,2,21,20,4)],'request frame stores')
    check(all(v[2]!=20 for v in stores if v[1]!=2),'request no explicit nonframe store of source pointer S4')
    check([p-pc for p,d in n.items() if d['op']=='load' and d['rs1']==20]==[],'request no direct local load through borrowed source S4')
    return {'start':hex(pc),'end_exclusive':hex(pc+360),'bytes':360,'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),
            'conditional_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},'calls':calls,'store_operands':stores,'complete_local_body':True,'local_CFG_acyclic':True}


def tag_choices(tag):
    c={110:256 if tag>4 else 114}
    if tag<=4:
        c[114]=116 if tag==0 else 222
        if tag:
            c[224]=228 if tag==1 else 232
            if tag>1:
                c[234]=238 if tag==2 else 242
                if tag>2:c[244]=248 if tag==3 else 252
    else:
        c[260]=286 if tag==5 else 264
        if tag!=5:
            c[266]=270 if tag==6 else 276
            if tag!=6:
                c[278]=282 if tag==7 else 314
                if tag!=7:
                    c[316]=320 if tag==8 else 324
                    if tag!=8:
                        c[326]=330 if tag==9 else 334
                        if tag!=9:c[338]=342 if tag==10 else 202
        if tag<=10:c[296]=128
    return c


def certificates(b):
    pc=int(b['start'],16);e={int(p,16):[int(q,16) for q in qs] for p,qs in b['conditional_CFG'].items()}
    cases={'busy':{26:202},'disabled':{26:28,42:202},'allocation_null':{26:28,42:44,78:202}}
    for tag in range(12):
        c={26:28,42:44,78:80,142:346,352:202,**tag_choices(tag)}
        cases['tag'+str(tag)+'_fallback_null']=c
    for label,extra in (
        ('role3_query0',{142:144,154:158,182:202}),
        ('role3_timer',{142:144,154:158,182:184}),
        ('fallback_nonzero',{142:346,352:354}),
        ('role_other',{142:144,154:346,352:202}),
        ('tag5_query25_not127',{296:300,142:346,352:202})):
        cases[label]={26:28,42:44,78:80,**tag_choices(5 if label.startswith('tag5') else 3),**extra}
    return {label:previous.paths.chain(e,pc,{pc+p:pc+q for p,q in c.items()}) for label,c in cases.items()}


def domains():
    rows=[]
    # Integer relation derived from the literal tag compare/store operands,
    # not a target register/RAM execution model. Provider effects are excluded.
    s=specs(0);pc=STARTS[0]
    low=tuple(s[pc+v]['imm'] for v in (116,228,238,248,252))
    high={5:s[pc+256]['imm'],6:s[pc+270]['imm'],7:0,8:s[pc+320]['imm'],9:s[pc+264]['imm'],10:s[pc+342]['imm']}
    for tag in range(256):
        mapped=low[tag]|16 if tag<=4 else high.get(tag)
        rows.append({'tag':tag,'mapped_byte_under_stable_valid_storage':mapped,'query25':5<=tag<=10,'invalid_tag_return1':tag>10})
    check([r['mapped_byte_under_stable_valid_storage'] for r in rows[:11]]==[19,29,18,16,21,5,2,0,1,6,4],'request literal tag-domain map')
    check(sum(r['invalid_tag_return1'] for r in rows)==245,'request invalid tag domain count')
    flags=[v for v in range(256) if v&5];check(len(flags)==192,'request flag admission192')
    source=list(range(4,14));tag3={4,12,13};unknown=sorted(set(source)-tag3)
    check(unknown==list(range(5,12)),'request caller seven unwritten bytes')
    translation=[{'caller_offset':v,'copy_destination_offset':2+v-4,'locally_written_on_tag3_path':v in tag3} for v in source]
    check([r['copy_destination_offset'] for r in translation if not r['locally_written_on_tag3_path']]==list(range(3,10)),'request copied P3..9 provenance gap')
    return {'tags':rows,'flag_ands5_nonzero_count':192,'tag3_source_translation':translation,
            'copy_extent_relation':'entryA1..entryA1+9 -> allocatedP+2..P+11; actual reads/writes require provider contract',
            'arithmetic':'timerA2=(query17reply*1600) mod2^32; reply width/domain and timer effect unknown'}


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[]
    for i,(data,pr) in enumerate(zip(carriers,parent['profiles'])):
        b=body(init.binding.take(data,STARTS[i],360),i);pc=STARTS[i];n={d['pc']:d for d in b['instructions']};g=0x20003000+80*i
        check(pr['handler_contract']['borrowed_request_SP4']['request_target']==hex(pc),'request prior handler call joins body')
        check([c['target'] for c in b['calls'][:2]]==['0x20000040','0x20000332'],'request allocator/copy PC-relative targets')
        h=pr['bodies']['handler'];hp=int(h['start'],16);hn={d['pc']:d for d in h['instructions']}
        check(hn[hp+304]['imm']==4 and hn[hp+326]['target']==pc,'request caller SP4 direct link')
        check((n[pc+62]['imm'],n[pc+88]['imm'],n[pc+92]['imm'])==(12,10,2),'request allocate12 copy10 atP2')
        check((n[pc+48]['rd'],n[pc+48]['rs2'],n[pc+90]['rs2'])==(20,11,20),'request borrowed source saved inS4 then passed tocopy')
        cert=certificates(b);check(len(cert)==20,'request20 selected CFG certificates/profile')
        tag9=[int(p,16) for p in cert['tag9_fallback_null']];at264=tag9.index(pc+264);at330=tag9.index(pc+330)
        check(at264<at330 and all(n[p].get('rd')!=13 for p in tag9[at264+1:at330]),'request tag9 stores retained A3=6, not earlier5')
        profiles.append({'label':pr['label'],'body':b,'selected_CFG_paths':cert,
            'entry':'A0=task value, A1=borrowed source; special handler uses A0=freshU8task and A1=callerSP+4',
            'frame':{'bytes':48,'saved':['RA','S0','S1','S2','S3','S4','S5'],'borrowed_entryA1_saved_in':'S4','local_source_pointer_retention':'no explicit nonframe store ofS4; copy provider receives it, so non-retention remains unproved'},
            'gates':{'pointer_slot':hex(g-236),'nonnull_slot_return':17,'flag_byte':hex(g+944),'flag_and5_zero_return':18,'allocation_null_return':19},
            'allocation_copy':{'task_byte_store_before_allocation':hex(g-195),'allocator':'0x20000040','allocation_args':[12,0x4717],
                'slot_write':'raw allocator reply stored before null guard','object_prefix':['P0=entrytask low8','P1=0'],
                'copy_target':'0x20000332','copy_args':['allocatedP+2','entry borrowed source',10],
                'tag_source':'fresh U32[pointer_slot] -> U8[P+2]; no new null guard aftercopy',
                'required':'allocator valid12byte extent, nonalias storage, copy10 output/consumption/retention, callee preservation and stable or valid fresh slot; pointer equality with allocatedP not automatic'},
            'tag_paths':{'tags0_to4':'write mapped byte then fresh byte OR16','tags5_to10':'map and query25(25); reply!=127 -> freshslot byte2 OR64; reply127 skips OR64',
                'tags11_to255':'return1 after allocation/publication/copy, no local free','query25_reply_width':'full register compared with127; no local LBU truncation'},
            'query_and_return':{'query1055':hex(0x6bc2e+484*i),'args':[1055,'requestSP+7'],'local_SP7_initialization':False,
                'read_after_return':'LBUSP A5,7(SP); nonzero -> fallback','role_byte':hex(g+586),'zero_output_and_role3':'calls456ea,4fd72(A1=SP8),45d3a(A0=SP8),45f9c(17); thenS0=0',
                'timer_if_query17_nonzero':{'target':hex(0x43728+140*i),'args':['freshU8['+hex(g+940)+']',4,'query17reply*1600 modulo2^32']},
                'fallback':{'target':hex(0x48070+152*i),'S0':'actual full reply','nonnull_reply_extra_call':hex(0x47fc8+152*i),'extra_reply_ignored_by_local_epilogue':True},
                'return':'A0=S0; local gates17/18/19, invalidtag1, role3path0 or fallback actual reply; requires liveS0/frame preservation'},
            'scratch_lifetime':'requestSP7 andSP8 pointers escape to callees without local initialization/extent/retention proof; distinct from callerSP4 source under ordinary nonwrapping stack layout',
            'persistent_pointer_lifetime':'slot may retain allocation across return, including invalidtag; no local clear/free in this body; subsequent consumers not covered',
            'actual_installed_provider_proved':False,'target_execution_or_emulation':False})
    return {'schema':'TSL9-special-request-static-v1','profile':parent['profile'],'APP_sha256':sha256(image).hexdigest(),'profiles':profiles,
            'source_encoding':encoding_source(),'integer_domains':domains(),'scope':'two complete360B/132i request bodies;720originalbytes;264operand guards;40selectedCFGpaths',
            'boundary':'static candidate contract only; all calls are return/preservation premises. Borrowed10byte copy extent established as call arguments, actual provider behavior and installed binding unproved',
            'remaining':['copy/allocator installed providers and pointer retention','query1055 and role3 callees output extents','fallback48070/47fc8 consumption and published-slot lifetime','callback enumerators, missing ROM pattern and node progress'],
            'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    count=paths=0
    for i,data in enumerate(carriers):
        pc=STARTS[i];raw=init.binding.take(data,pc,360);b=body(raw,i);paths+=len(certificates(b))
        for p,d in decode(raw,pc).items():
            at=p-pc;z=d['size'];buf=bytearray(raw);buf[at:at+z]=(int.from_bytes(buf[at:at+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
            try:body(buf,i)
            except RuntimeError as e:check(str(e).startswith('request operand '),'request specified mutation guard '+str(e))
            else:raise RuntimeError('request mutation escaped')
            count+=1
    check(count==264 and paths==40,'request mutation/path census');encoding_source();domains()
    print('PASS:264 operand mutations rejected;720 original bytes;40 CFG path certificates;256 tag/flag domains;6 LLVM LBUSP vectors/128 fields')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');o=parser.parse_args()
    image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK identity')
    carriers=[]
    for label,folder,tail,z,digest in init.binding.PROFILES:
        data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(data)==z and sha256(data).hexdigest()==digest,'candidate identity '+label);carriers.append(data)
    raw_hex=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
    coverage=sparse.derive(image,carriers,header,raw_hex,sparse.parser());ledger=derive(image,carriers,header,coverage)
    ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers)
    output=(json.dumps(ledger,indent=1,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'request exact ledger replay')
    print('PASS:published SP4 caller/copy10 relation, local return gates and borrowed outputs;exact ledger')
    print('PASS:NO target execution/emulation;actual provider/retention/output extent/slot lifetime UNPROVED')


if __name__=='__main__':main()
