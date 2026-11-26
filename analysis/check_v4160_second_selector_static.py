"""Complete second selector: pinned reversal expansions, CFG and leaf joins.

Original operands plus host permutation/algebra/ranking facts only. No target
ISA, callback, RAM/frame, resident, MMIO or device execution/emulation.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_local_selector_static as previous

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-second-selector-static.json')
DETAILS=((0x417dc,0xe006c000,1872,1836,'2690bd6dd6452573835de2af9c1799cd1adfcd73aa68f937703ccd91498b39c9'),
 (0x4181c,0xe006d000,-1728,-1764,'109d36e174f53e18be4a41283ea4e677405fcefc1cad75e4700609d0458b865d'))
SAVED=previous.SAVED+((24,8),)


def specs(pc,upper,low1,low2):
    s={}
    def e(o,op,**f):check(pc+o not in s,'second selector duplicate expected instruction');s[pc+o]=dict(op=op,**f)
    def imm(o,op,r,a,v):e(o,op,rd=r,rs1=a,imm=v)
    def binary(o,op,r,a,b):e(o,op,rd=r,rs1=a,rs2=b)
    def move(o,r,a):e(o,'mv',rd=r,rs2=a)
    def load(o,r,b,v,w=4):e(o,'load',rd=r,rs1=b,imm=v,width=w)
    def store(o,r,b,v,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    def low_reverse(base,x,out,tmp,last):
        # Original 70B/24-instruction low-byte expansion; first two finish in
        # out, third finishes in x. This register schedule is intentional.
        for o,op,r,a,v in ((0,'srai',out,x,7),(4,'srai',tmp,x,5),(8,'andi',tmp,tmp,2),(10,'andi',out,out,1),
            (14,'srai',tmp,x,3),(18,'andi',tmp,tmp,4),(22,'srai',tmp,x,1),(26,'andi',tmp,tmp,8),
            (30,'slli',tmp,x,1),(34,'andi',tmp,tmp,16),(38,'slli',tmp,x,3),(42,'andi',tmp,tmp,32),
            (48,'slli',tmp,x,5),(52,'srli',11,x,8),(56,'andi',tmp,tmp,64),(60,'slli',x,x,7),(64,'andi',x,x,255)):
            imm(base+o,op,r,a,v)
        for o in (12,20,28,36,46,62):binary(base+o,'or',out,out,tmp)
        binary(base+68,'or',*last)
    def high_reverse(base,out,tmp,first,lo):
        # The first high-byte expansion schedules shifts in the other order.
        a,b=((out,5),(tmp,3)) if first else ((tmp,3),(out,5))
        imm(base,'srai',a[0],11,a[1]);imm(base+4,'srai',b[0],11,b[1])
        for o,op,r,a,v in ((8,'andi',tmp,tmp,4),(10,'andi',out,out,2),(14,'srai',tmp,11,7),
            (20,'srai',tmp,11,1),(24,'andi',tmp,tmp,8),(28,'slli',tmp,11,1),(32,'andi',tmp,tmp,16),
            (36,'slli',tmp,11,3),(40,'andi',tmp,tmp,32),(46,'slli',tmp,11,5),(50,'andi',tmp,tmp,64),
            (54,'slli',11,11,7),(58,'andi',11,11,255),(64,'slli',out,out,8)):
            imm(base+o,op,r,a,v)
        for o in (12,18,26,34,44,56):binary(base+o,'or',out,out,tmp)
        binary(base+62,'or',out,out,11)
        if first:e(base+66,'li',rd=12,imm=17);binary(base+68,'or',lo,lo,out)
        else:binary(base+66,'or',lo,lo,out)
    load(0,15,10,152);load(4,12,10,64,2);imm(8,'addi',2,2,-48);imm(10,'srli',13,15,16)
    binary(14,'xor',13,13,15);imm(16,'slli',13,13,16);imm(18,'srli',13,13,16);binary(20,'xor',12,12,13)
    low_reverse(22,12,14,15,(14,14,12));high_reverse(92,15,12,True,14)
    binary(162,'mul',14,14,12);store(166,8,2,40);move(168,8,10);store(170,9,2,36)
    store(172,20,2,24);store(174,21,2,20);load(176,20,8,312);load(180,21,8,316)
    store(184,22,2,16);store(186,1,2,44);binary(188,'add',14,14,13);imm(190,'slli',14,14,16);imm(192,'srli',14,14,16)
    low_reverse(194,14,15,10,(15,15,14));high_reverse(264,14,10,False,15)
    binary(332,'mul',15,15,12)
    for o,r,v in ((336,18,32),(338,19,28),(340,23,12),(342,24,8)):store(o,r,2,v)
    binary(344,'add',15,15,13);imm(346,'slli',15,15,16);imm(348,'srli',15,15,16)
    low_reverse(350,15,14,10,(15,15,14));high_reverse(420,14,10,False,15)
    binary(488,'mul',15,15,12);imm(492,'addi',12,0,37);move(496,10,20);move(498,11,21)
    binary(500,'add',15,15,13);binary(502,'xor',13,13,15);imm(504,'slli',9,13,16);imm(508,'srli',9,9,16)
    binary(510,'remu',12,9,12);imm(514,'andi',22,12,255);e(518,'auipc',rd=1,imm=upper);e(522,'jalr',rd=1,rs1=1,imm=low1)
    imm(526,'andi',10,10,1);e(528,'bnez',rs1=10,target=pc+586);load(530,15,8,301,1)
    e(534,'li',rd=18,imm=0);e(536,'li',rd=19,imm=0);binary(538,'mul',9,15,9);imm(542,'addi',24,0,37);imm(546,'srli',9,9,16)
    move(548,12,18);move(550,10,20);move(552,11,21);e(554,'auipc',rd=1,imm=upper);e(558,'jalr',rd=1,rs1=1,imm=low2)
    imm(562,'andi',10,10,1);imm(564,'andi',23,18,255);e(568,'beqz',rs1=10,target=pc+580)
    e(570,'beq',rs1=9,rs2=19,target=pc+614);imm(574,'addi',19,19,1);imm(576,'andi',19,19,255)
    imm(580,'addi',18,18,1);e(582,'bne',rs1=18,rs2=24,target=pc+548);store(586,22,8,310,1)
    for j,(r,o) in enumerate(SAVED):load(590+2*j,r,2,o)
    imm(610,'addi',2,2,48);e(612,'jr',rs1=1);move(614,22,23);e(616,'jump',target=pc+586)
    return s


def body(raw,pc,upper,lo1,lo2,digest):
    check(int.from_bytes(raw[510:514],'little')&0xfe00707f==0x02007033,'second selector exact REMU encoding')
    check(int.from_bytes(raw[4:8],'little')&0x707f==0x5003,'second selector unsigned halfword encoding')
    n=decode(raw,pc);expected=specs(pc,upper,lo1,lo2);check(set(n)==set(expected),'second selector complete boundaries')
    for p,f in expected.items():init.g(n,p,'second selector operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(618,222,digest),'second selector whole identity')
    edges={};calls=[]
    for p,d in n.items():
        if d['op']=='jr':qs=[]
        elif d['op']=='jump':qs=[d['target']]
        elif d['op'] in ('beqz','bnez','beq','bne'):qs=[p+d['size'],d['target']]
        else:qs=[p+d['size']]
        check(all(q in n for q in qs),'second selector no local cuts');edges[p]=qs
        if d['op']=='jalr':calls.append({'pc':hex(p),'link':hex(p+4),'target':hex((p-4+n[p-4]['imm']+d['imm'])&0xfffffffe)})
    seen=set()
    def visit(p):
        if p in seen:return
        seen.add(p)
        for q in edges[p]:visit(q)
    visit(pc);check(seen==set(n),'second selector all nodes locally reachable including out-of-line exit')
    return {'start':hex(pc),'end_exclusive':hex(pc+618),'bytes':618,'sha256':digest,'instructions':list(n.values()),
        'CFG':{hex(k):[hex(q) for q in qs] for k,qs in edges.items()},'calls':calls,'complete_function':True}


def derive(app,carriers,header,coverage):
    parent=previous.derive(app,carriers,header,coverage);profiles=[]
    for i,(data,d) in enumerate(zip(carriers,DETAILS)):
        source,upper,lo1,lo2,h=d;p=parent['profiles'][i]
        shift=int(p['selector']['start'],16)-int(p['flash_selector'],16);runtime=source+shift
        check(runtime==0x2000156c,'second selector mapped entry')
        b=body(init.binding.take(data,source,618),runtime,upper,lo1,lo2,h)
        body(init.binding.take(data,source,618),source,upper,lo1,lo2,h)
        leaf=p['shift_leaf'];check([c['target'] for c in b['calls']]==[leaf['start']]*2,'second selector two calls join exact verified pure leaf')
        check(p['leaf_defined_registers']==[10,11,12,15],'leaf preserves selector index/limit/data S registers')
        ns={x['pc']:x for x in b['instructions']};edges={int(k,16):[int(q,16) for q in qs] for k,qs in b['CFG'].items()}
        cycles=[c for c in previous.previous.previous.previous.previous.components(edges) if len(c)>1 or c[0] in edges[c[0]]]
        expected={runtime+o for o in (548,550,552,554,558,562,564,568,570,574,576,580,582)}
        check(len(cycles)==1 and set(cycles[0])==expected,'second selector exact 13-node scan SCC')
        check(runtime+614 not in cycles[0] and edges[runtime+614]==[runtime+616] and edges[runtime+616]==[runtime+586],'out-of-line selected-index exit included, outside SCC')
        check({(x['rs2'],x['imm']) for x in ns.values() if x['op']=='store' and x['rs1']==2}==set(SAVED),'second selector ten frame saves')
        check({(x['rd'],x['imm']) for x in ns.values() if x['op']=='load' and x['rs1']==2}==set(SAVED),'second selector ten frame restores')
        check([(x['rs1'],x['rs2'],x['imm'],x['width']) for x in ns.values() if x['op']=='store' and x['rs1']!=2]==[(8,22,310,1)],'only direct nonstack byte310 store')
        check([(x['pc'],x['op'],x.get('imm')) for x in ns.values() if x.get('rd')==18]==
            [(runtime+534,'li',0),(runtime+580,'addi',1),(runtime+596,'load',32)],'index initial0 / only SCC increment / outside restore')
        check(ns[runtime+542]['imm']==37 and 18 not in p['leaf_defined_registers'] and 24 not in p['leaf_defined_registers'],'index/limit37 preserved by leaf')
        callpc=(0x41146,0x41186)[i];caller=decode(init.binding.take(data,callpc,4),callpc+shift)
        init.g(caller,callpc+shift,'callback second selector argument',op='mv',rd=10,rs2=8)
        init.g(caller,callpc+shift+2,'callback second selector call',op='jal',rd=1,target=runtime)
        profiles.append({'label':p['label'],'flash_start':hex(source),'selector':b,'reused_leaf_sha256':leaf['sha256'],
            'leaf_target':leaf['start'],'callback_call':{'pc':hex(callpc+shift+2),'A0':'then-live S0'},
            'scan_SCC_nodes':[hex(v) for v in cycles[0]],'conditional_scan_bound':37,'conditional_total_probe_bound':38,
            'bound_premises':'matching code/mapping/leaf; valid object/frame accesses; no saved-word alias corruption or external interference/reentry',
            'actual_installed_binding_runtime_execution_or_success_proved':False})
    return {'schema':'TSL9-second-selector-static-v1','profile':parent['profile'],'profiles':profiles,
        'scope':'2 complete second selectors1236B/444instructions; prior identical leaf reused, not counted as new code',
        'transform_contract':{'F':'low16(single U32[object+152] snapshot XOR(snapshot>>16))',
            'x':'fresh U16[object+64] XOR F','B':'reverse bits within each byte, preserving byte positions',
            'rounds':'x1=low16(17*B(x)+F); x2=low16(17*B(x1)+F); x3=low16(17*B(x2)+F); seed=x3 XOR F',
            'third_truncation':'actual third low16 happens after XOR; equivalent because only low16 is retained',
            'candidate':'seed %37; always0..36; all probe counts within verified 64bit-shift domain'},
        'probe_contract':'snapshot words312/316 intoS4/S5; probe candidate through verified leaf; testA0&1; ifzero fallback',
        'fallback_contract':'fresh d=U8[object+301]; rank=(d*seed)>>16, rank0..254; scan indices0..36 and set-bit ordinal, selecting matching rank else retaining original candidate',
        'output_contract':'only object store byte310, candidate always0..36 but set-bit/success property unproved; A0 is last probe AND1, not fixed success flag',
        'preservation_contract':'48-byte frame saves/restores RA/S0..S8 (10 fields); nested leaf has no memory/calls and only A0/A1/A2/A5 definitions',
        'premises':['actual installed candidate and completed preserved first-copy mapping; conditional ISA/code/data/frame accesses valid',
            'separate source loads are not coherent snapshots; object/global writers, aliases, faults, interrupts and reentry remain external premises',
            'frame format matching does not establish saved-word lifetime; helper-code identity must hold for rank/index preservation',
            'bounded selector scan does not prove caller callback/system termination or actual path reachability'],
        'remaining':['arithmetic helper6df1a/6e10a and other callees','complete config gates/copy and installed provider binding',
            'object/global producers and practical field relationships','hardware effects, callback progress and frame/payload lifetime'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def reverse_formula(x):
    def byte(v):return ((v>>7)&1)|((v>>5)&2)|((v>>3)&4)|((v>>1)&8)|((v<<1)&16)|((v<<3)&32)|((v<<5)&64)|((v<<7)&255)
    return byte(x&255)|(byte(x>>8)<<8)


def tests(carriers):
    table=[int(f'{x:08b}'[::-1],2) for x in range(256)]
    for x in range(65536):
        rev=reverse_formula(x);check(rev==table[x&255]|(table[x>>8]<<8) and reverse_formula(rev)==x,'byte-position preserving reversal oracle')
        for d in (0,1,255):
            rank=(d*x)>>16;check(0<=rank<=254 and (d!=0 or rank==0),'rank product bound including d0')
        check(0<=x%37<=36,'candidate constant divisor domain')
    check(reverse_formula(1)==0x0080 and reverse_formula(1)!=0x8000,'bytewise is not whole16 reversal')
    for f in (0,1,0x55aa,65535):
        for counter in (0,1,0x7fff,0x8000,65535):
            x=counter^f
            for _ in range(2):
                wide=17*reverse_formula(x)+f;check(0<=wide<=1179630,'round intermediate fitsU32');x=wide&65535
            wide=17*reverse_formula(x)+f;check((wide^f)&65535==((wide&65535)^f),'last low16/XOR equivalence')
    changes=((4,1<<14),(22,1<<20),(90,4),(92,1<<20),(194,1<<20),(264,1<<20),(350,1<<20),(420,1<<20),
        (488,1<<20),(502,4),(510,1<<12),(522,1<<20),(538,1<<15),(546,4),(558,1<<20),
        (570,1<<12),(586,1<<20),(590,4),(614,4),(612,4))
    count=0
    for data,(source,upper,lo1,lo2,h) in zip(carriers,DETAILS):
        raw=init.binding.take(data,source,618)
        for off,flip in changes:
            b=bytearray(raw);width=decode(raw,source)[source+off]['size'];b[off:off+width]=(int.from_bytes(b[off:off+width],'little')^flip).to_bytes(width,'little')
            try:body(b,source,upper,lo1,lo2,h)
            except RuntimeError as e:check(str(e) in ('second selector operand '+hex(off),'second selector exact REMU encoding','second selector unsigned halfword encoding'),'specific second-selector mutation guard '+str(e))
            else:raise RuntimeError('second-selector mutation escaped')
            count+=1
    check(count==40,'second selector mutation census')
    print('PASS: 65536 reversal/domain cases; 196608 rank cases; round algebra; 40 specified operand mutations rejected')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');o=parser.parse_args()
    app=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(app)==76800 and sha256(app).hexdigest()==init.binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK header identity')
    carriers=[]
    for label,folder,tail,size,digest in init.binding.PROFILES:
        raw=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(raw)==size and sha256(raw).hexdigest()==digest,'candidate identity '+label);carriers.append(raw)
    raw_hex=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
    coverage=sparse.derive(app,carriers,header,raw_hex,sparse.parser())
    ledger=derive(app,carriers,header,coverage);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract()
    tests(carriers);output=(json.dumps(ledger,indent=1,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'second selector exact ledger replay')
    print('PASS: each second selector618B/222instructions; full operands/CFG, ten frame fields, sole object-byte store, exact13-node SCC and reused leaf joins')
    print('PASS: exact ledger; NO target execution; actual binding/rank validity/frame lifetime/larger callback termination UNPROVED')


if __name__=='__main__':main()
