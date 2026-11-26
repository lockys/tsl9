"""Range helpers, callback-fed word source and full retry tail, offline.

Original operand/CFG/frame proofs and integer/byte identities only.
No target/register-machine, callback, RNG, MMIO or device execution/model.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_initializer_post_radio_static as previous
import check_v4160_service_provider_link_static as provider
import check_v4160_ram_callback_loop_static as graphs
import check_v4160_post_rf_leaves_static as structure
import check_v4160_rf_tail_return_static as rf

init,sparse,check=previous.init,previous.sparse,previous.check
paths=previous.paths
OUT=Path(__file__).with_name('v4160-range-retry-static.json')
ROLES=('signed_range','unsigned_range','source','tail')
SIZES=(36,32,108,276)
COUNTS=(16,14,37,94)
DETAILS=(
 ((0x43e8e,0x43eb2,0x433a8,0x53868),0,
 ('0643ceb944dae1fc1096e0e5405c8efc070bb2196555a88bd3c1c8884423adec','2ab53c63f413f54475e31c5a93f67de93eef181f5aac3d4f2b243f53a43273a8',
  '06f924f8b9fd9d66163ccbcc8e4a586c183799a96f7e2c1911ce0328384184c8','c16dc5e380f5e6d0a20c4b6bec980915498d4114bdde27b82d6495db46d1f929')),
 ((0x43f1a,0x43f3e,0x43434,0x53916),80,
 ('0643ceb944dae1fc1096e0e5405c8efc070bb2196555a88bd3c1c8884423adec','2ab53c63f413f54475e31c5a93f67de93eef181f5aac3d4f2b243f53a43273a8',
  'b45be9b226d49d8f11dd49f3f6422054f676beb64edfea75f9e32f3db7667db0','b4c0a556e3f0962653521f6c3d69bde030cc0e24103404357ca135b2678999a9')))


def decode(raw,pc):
    n={};off=0
    while off<len(raw):
        h=int.from_bytes(raw[off:off+2],'little');z=4 if h&3==3 else 2;chunk=raw[off:off+z]
        check(len(chunk)==z,'range retry complete instruction');w=int.from_bytes(chunk,'little');p=pc+off
        if z==4 and w&0xfe00707f==0x02002033:
            d=dict(pc=p,bytes=chunk.hex(),size=4,op='mulhsu',rd=w>>7&31,rs1=w>>15&31,rs2=w>>20&31)
        elif z==4 and w&0x707f==0x1003:
            imm=w>>20;imm=imm-4096 if imm&2048 else imm
            d=dict(pc=p,bytes=chunk.hex(),size=4,op='load',rd=w>>7&31,rs1=w>>15&31,imm=imm,width=2,signed=True,mnemonic='lh')
        else:d=previous.decode(chunk,p)[p]
        n[p]=d;off+=z
    return n


def specs(role,index):
    addresses,delta,_=DETAILS[index];pc=addresses[ROLES.index(role)];s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def lui(o,r,v):e(o,'lui',rd=r,imm=v)
    def imm(o,op,r,b,v):e(o,op,rd=r,rs1=b,imm=v)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    def load(o,r,b,v,w=4,**f):e(o,'load',rd=r,rs1=b,imm=v,width=w,**f)
    def store(o,r,b,v,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    def binary(o,op,r,a,b):e(o,op,rd=r,rs1=a,rs2=b)
    def mv(o,r,b):e(o,'mv',rd=r,rs2=b)
    def branch(o,op,a,b,t):e(o,op,rs1=a,rs2=b,target=pc+t)
    def bz(o,op,r,t):e(o,op,rs1=r,target=pc+t)
    def call(o,t):e(o,'jal',rd=1,target=t)
    if role.endswith('_range'):
        imm(0,'addi',2,2,-32);store(2,8,2,24);store(4,1,2,28);mv(6,8,10);store(8,11,2,12)
        call(10,addresses[2]);load(14,11,2,12);load(16,1,2,28);binary(18,'sub',11,11,8)
        binary(20,'mulhsu' if role=='signed_range' else 'mulhu',10,11,10);binary(24,'add',10,10,8);load(26,8,2,24)
        if role=='signed_range':imm(28,'slli',10,10,16);imm(30,'srli',10,10,16);imm(32,'addi',2,2,32);e(34,'jr',rs1=1)
        else:imm(28,'addi',2,2,32);e(30,'jr',rs1=1)
    elif role=='source':
        imm(0,'addi',2,2,-16);store(2,9,2,4);lui(4,15,0x40024000);store(8,1,2,12);store(10,8,2,8)
        load(12,9,15,524);store(16,0,15,524);e(20,'fence.i');lui(24,15,0x20003000);load(28,15,15,528+delta)
        lui(32,8,0x20003000);imm(36,'addi',8,8,-312+delta);bz(40,'beqz',15,52);e(42,'call_indirect',rd=1,rs1=15)
        load(44,15,8,0);binary(46,'add',10,10,15);store(48,10,8,0);e(50,'jump',target=pc+62)
        lui(52,15,0x20003000);load(56,15,15,480+delta);bz(60,'bnez',15,42);load(62,15,8,0)
        lui(64,14,0x34000);imm(68,'addi',14,14,1021);binary(72,'mul',15,15,14);lui(76,14,0x26a000)
        imm(80,'addi',14,14,-317);load(84,1,2,12);binary(86,'add',15,15,14);store(88,15,8,0)
        lui(90,15,0x40024000);store(94,9,15,524);load(98,10,8,0);load(100,8,2,8);load(102,9,2,4)
        imm(104,'addi',2,2,16);e(106,'jr',rs1=1)
    else:
        s=dict(previous.specs('next_prefix',index)[1]);mv(50,8,10);li(52,11,-1);li(54,10,0);call(56,addresses[1])
        mv(60,15,8);imm(62,'addi',9,9,-1);li(64,18,-1);binary(66,'and',14,15,9);binary(70,'or',13,10,14)
        bz(74,'beqz',13,254);branch(76,'bne',10,18,84);branch(80,'beq',14,9,254)
        lui(84,8,0x20003000);imm(88,'addi',14,8,952+delta);store(92,15,14,248,1);imm(96,'srli',15,15,8)
        imm(98,'ori',15,15,-64);lui(102,19,0x4000);lui(104,9,0x10000);store(106,10,14,244);store(110,15,14,249,1)
        imm(114,'addi',8,8,952+delta);imm(118,'addi',19,19,-1);imm(120,'addi',9,9,-1)
        mv(122,11,19);li(124,10,0);call(126,addresses[0]);mv(130,18,10);li(132,11,-1);li(134,10,0);call(136,addresses[1])
        binary(140,'or',15,10,18);bz(144,'beqz',15,122);li(146,15,-1);branch(148,'bne',10,15,156);branch(152,'beq',18,19,122)
        imm(156,'srli',15,10,16);store(160,15,8,252,1);imm(164,'srli',15,10,24);store(168,15,8,253,1)
        load(172,15,8,232,2,signed=True,mnemonic='lh');store(176,10,8,250,2);store(180,18,8,254,1)
        imm(184,'slli',10,10,16);imm(186,'srli',18,18,8);imm(190,'andi',18,18,63);imm(194,'srai',10,10,16)
        store(196,18,8,255,1);binary(200,'and',10,10,9);binary(202,'and',15,15,9);branch(204,'bne',10,15,240)
        load(208,14,8,252,2,signed=True,mnemonic='lh');load(212,15,8,234,2,signed=True,mnemonic='lh')
        binary(216,'and',14,14,9);binary(218,'and',15,15,9);branch(220,'bne',14,15,240)
        load(224,14,8,254,2,signed=True,mnemonic='lh');load(228,15,8,236,2,signed=True,mnemonic='lh')
        binary(232,'and',14,14,9);binary(234,'and',15,15,9);branch(236,'beq',14,15,122)
        for o,r,v in ((240,1,28),(242,8,24),(244,9,20),(246,18,16),(248,19,12)):load(o,r,2,v)
        imm(250,'addi',2,2,32);e(252,'jr',rs1=1);mv(254,11,9);li(256,10,0);call(258,addresses[0]);mv(262,8,10)
        li(264,11,-1);li(266,10,0);call(268,addresses[1]);mv(272,15,8);e(274,'jump',target=pc+66)
    return pc,s


def edges(n):
    e={}
    for p,d in n.items():
        op=d['op']
        if op=='jr':check(d['rs1']==1,'range ordinary RET');q=[]
        elif op=='jump':q=[d['target']]
        elif op in ('beq','bne','beqz','bnez'):q=[p+d['size'],d['target']]
        else:q=[p+d['size']]
        check(all(v in n for v in q),'range full local CFG');e[p]=q
    return e


def cycles(e):
    return [c for c in graphs.components(e) if len(c)>1 or c[0] in e[c[0]]]


def body(raw,role,index):
    pc,s=specs(role,index);n=decode(raw,pc);j=ROLES.index(role)
    check(set(n)==set(s),'range '+role+' boundaries')
    for p,f in s.items():init.g(n,p,'range '+role+' operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[j],COUNTS[j],DETAILS[index][-1][j]),'range '+role+' identity')
    e=edges(n);check(structure.reachable(e,pc)==set(n),'range all local nodes reachable')
    stores=[d for d in n.values() if d['op']=='store'];loads=[d for d in n.values() if d['op']=='load']
    calls=[{'pc':hex(p),'target':hex(d['target']) if 'target' in d else ('0x20000332' if d['op']=='jalr' else 'fresh A5'),'link':hex(p+d['size'])} for p,d in n.items() if d['op'] in ('jal','jalr','call_indirect')]
    check((len(stores),len(loads),len(calls))=={'signed_range':(3,3,1),'unsigned_range':(3,3,1),'source':(7,9,1),'tail':(13,10,7)}[role],'range exact memory/call census')
    cyc=cycles(e);check([len(c) for c in cyc]==([14,37] if role=='tail' else []),'range exact local SCC sizes')
    check(not any(d.get('rd')==3 for d in n.values()),'range no local GP definition')
    frames={'signed_range':(32,32,((8,24),(1,28),(11,12))), 'unsigned_range':(32,28,((8,24),(1,28),(11,12))),
        'source':(16,104,((9,4),(1,12),(8,8))), 'tail':(32,250,((1,28),(8,24),(9,20),(18,16),(19,12)))}
    size,restore,saved=frames[role]
    check([(d['rs2'],d['imm']) for d in stores if d['rs1']==2]==list(saved),'range exact own frame saves')
    check([p-pc for p,d in n.items() if d.get('rd')==2]==([8,restore] if role=='tail' else [0,restore]),'range SP definition census')
    return {'role':role,'start':hex(pc),'bytes':len(raw),'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),
        'normal_return_CFG':{hex(p):[hex(q) for q in qs] for p,qs in e.items()},'cycles':[[hex(p) for p in c] for c in cyc],
        'calls':calls,'own_frame_bytes':size,'complete_function':True}


def pair_bytes(x,y):return y.to_bytes(4,'little')+x.to_bytes(2,'little')


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[]
    reader=provider.body(image[0x191c6-0x8000:0x19220-0x8000],'reader',0x191c6,provider.APP_HASHES[1])
    for i,(data,pr,detail) in enumerate(zip(carriers,parent['profiles'],DETAILS)):
        addresses,delta,_=detail;small,wide,src,tail=addresses;B=int(pr['B'],16);state=0x20002ec8+delta
        bodies={r:body(init.binding.take(data,p,z),r,i) for r,p,z in zip(ROLES,addresses,SIZES)}
        check(pr['cut_before_next_call']=={'pc':hex(tail+46),'target':hex(small),'A0':0,'A1':16383},'range previous call-cut join')
        sn={d['pc']:d for d in bodies['source']['instructions']};se=edges(sn)
        source_paths={name:paths.chain(se,src,{src+p:src+q for p,q in choices.items()}) for name,choices in (
            ('primary_nonzero',{40:42,60:42}),('primary_zero_fallback_nonzero',{40:52,60:42}),('both_zero',{40:52,60:62}))}
        check(hex(src+42) not in source_paths['both_zero'],'range no-hook case skips callback')
        mapping=init.binding.profile(data,pr['label']);check(next(r['target'] for r in mapping['slots'] if r['slot']=='0x40038')==hex(src),'range candidate word-source identity')
        rf.preservation(delta,[(state,4)])
        tn={d['pc']:d for d in bodies['tail']['instructions']};te=edges(tn);reduced={p:list(q) for p,q in te.items()}
        reduced[tail+76]=[tail+84];reduced[tail+148]=[tail+156]
        reach=structure.reachable(reduced,tail);rcycles=cycles({p:[q for q in qs if q in reach] for p,qs in reduced.items() if p in reach})
        check(len(reach)==92 and tail+80 not in reach and tail+152 not in reach,'range all-ones guards unreachable in caller domain')
        check([len(c) for c in rcycles]==[12,36],'range pruned exact retry SCC sizes')
        check(rcycles[0]==[tail+x for x in (66,70,74,254,256,258,262,264,266,268,272,274)],'range pruned first retry exact nodes')
        object_stores=[]
        for p,d in tn.items():
            if d['op']!='store' or d['rs1']==2:continue
            check((p-tail in (92,106,110) and d['rs1']==14) or (p-tail in (160,168,176,180,196) and d['rs1']==8),'range direct store fixed B provenance')
            address=B+d['imm'];check(B+244<=address<address+d['width']<=B+256,'range candidate and seed direct extents')
            object_stores.append({'pc':hex(p),'address':hex(address),'bytes':d['width']})
        protected=[(B+232,6),(B+193,1),(B+201,1)]
        for d in object_stores:
            for q,z in protected:check(paths.origin.separated(int(d['address'],16),d['bytes'],q,z),'range direct stores preserve old tuple/sampled bytes')
        check([p-tail for p,d in tn.items() if d.get('rd')==10 and p>=tail+200]==[200,256,266],'range return block last A0 definition is low16 mask')
        # Last two A0 definitions are in a separate retry block, not RET suffix.
        ret_path=paths.chain(te,tail+240,{})
        check(ret_path==[hex(tail+x) for x in (240,242,244,246,248,250,252)] and not any(tn[int(p,16)].get('rd')==10 for p in ret_path),'range RET suffix preserves masked A0')
        profiles.append({'label':pr['label'],'bodies':bodies,'word_source_state':hex(state),
            'source_primary_slot':hex(0x20003210+delta),'source_fallback_slot':hex(0x200031e0+delta),'source_three_paths':source_paths,
            'callback_obligations':'if selected nonzero callback, normal return with same SP, source S0(state base)/S1(snapshot), all other live caller S registers (notably tail S2/S3), required GP and saved frame words intact; also preserve caller-required object/global state. This is not inferred from ABI name',
            'matching_APP_reader_case':'only if primary=0 and fresh fallback=191c6 (or actual selected target matches that code), existing reader proves local S/frame nonwrites; paired-halfword retries still require eventual completion',
            'range_call_domains':{'small':[0,16383],'wide':[0,4294967295]},'conditional_outputs':{'X':[0,16382],'Y':[0,4294967294]},
            'range_pruned_reachable_nodes':len(reach),'range_pruned_retry_SCCs':[[hex(p) for p in c] for c in rcycles],
            'classified_direct_object_stores':object_stores,'old_six_bytes':hex(B+232),'seed_word':hex(B+244),'seed_halfword_bytes':hex(B+248),
            'candidate_six_bytes':hex(B+250),'ordinary_RET':hex(tail+252),'ordinary_A0_return':'Y & 0xffff; may be zero',
            'conditional_context_gate':5,'conditional_count':6,'actual_installed_binding_proved':False})
    return {'schema':'TSL9-range-retry-static-v1','profile':parent['profile'],'APP_sha256':sha256(image).hexdigest(),'profiles':profiles,
        'APP_fallback_reader':reader,
        'scope':'per candidate full36B signed/32B unsigned/108B word-source/276B retry-tail:452B/161 instructions, all operands guarded; strict new LH/MULHSU decoding; no new C bytes',
        'source_formula':'under required normal completion/state retention: no-hook path fresh state s ->(214013*s+2531011)mod2^32; callback path first stores(callback_reply+fresh_post_callback_state)mod2^32 then applies same arithmetic. Final A0 is fresh state read after CPU control snapshot writeback; no random/uniform/atomic/progress guarantee',
        'range_formula':'D=(upper-lower)mod32. Small uses signed(D)*unsigned(R) high32, adds lower mod32 then low16. Wide uses unsigned high32 and adds lower mod32. Only caller domains (0,3fff)/(0,ffffffff) establish stated ranges; arbitrary reversed/overflowing bounds not normalized',
        'caller_bounds':'for any returned unsigned R: X=floor(16383*R/2^32) in0..16382; Y=floor((2^32-1)*R/2^32)=0 if R0 else R-1 in0..fffffffe. All-ones guards unreachable; zero-pair retry remains not excluded by these bounds alone',
        'retry_contract':'first stage retries until sampled pair(X,Y) is not both zero, then writes seed Y atB244 and little-endian(X ORc000) atB248. Second stage resamples until nonzero pair whose bytes LE32(Y)||LE16(X) differ from oldB232..237; stores candidateB250..255 before comparisons. No requirement that candidate differs from seed. No attempt count or source fairness/completion proof',
        'return_contract':'after any halfword mismatch and required helper/frame/state preservation, restore RA/S0/S1/S2/S3 and SP32, RET with A0=Y low16. Nonzero six-byte candidate may legally return A0=0; this is not a Boolean status',
        'LH_contract':'five standard signed LH loads are followed by ANDffff; signed extension is canceled for three16bit equality comparisons. Destination halfwords are assembled by prior stores under required no-interference assumptions',
        'preservation':'direct source RAM writes only one fixed word outside B/context/table/task/node; direct tail object writesB244..255 exclude old six bytes and sampled B193/B201. Unknown callbacks must additionally satisfy explicit caller object/frame/mapping preservation; CPU MMIO store sources do not prove hardware effects',
        'remaining':['actual primary/fallback binding and callback/source state retention','retry termination and actual caller data/ordering','gate/primary publication after ordinary return and actual installed providers/lifetimes'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    operands=fences=0
    for i,(data,detail) in enumerate(zip(carriers,DETAILS)):
        for role,pc,z in zip(ROLES,detail[0],SIZES):
            raw=init.binding.take(data,pc,z)
            for p,d in decode(raw,pc).items():
                off=p-pc;w=d['size'];buf=bytearray(raw);fence=d['op']=='fence.i'
                buf[off:off+w]=(int.from_bytes(buf[off:off+w],'little')^(128 if fence else 4 if w==2 else 1<<20)).to_bytes(w,'little')
                try:body(buf,role,i)
                except RuntimeError as e:check(str(e)=='unsupported static leaf encoding '+hex(p) if fence else str(e).startswith('range '+role+' operand '),'range specified mutation guard '+str(e))
                else:raise RuntimeError('range mutation escaped')
                if fence:fences+=1
                else:operands+=1
    check((operands,fences)==(320,2),'range mutation census '+str((operands,fences)))
    for high in range(65536):
        for low in (0,65535):
            r=(high<<16)|low;x=(16383*r)>>32;y=(0xffffffff*r)>>32
            check(0<=x<=16382 and y==(0 if r==0 else r-1) and y<=0xfffffffe,'range caller multiplication bounds')
        signed=high-65536 if high&32768 else high
        check(signed&65535==high,'range LH then low16 identity')
    for x in range(16383):check((x&255)|(((x>>8)|0xc0)&255)<<8==x|0xc000,'range seed flag-byte identity')
    for y in (0,1,65535,65536,0x80000000,0xfffffffe):
        for x in (0,1,16382):
            packed=pair_bytes(x,y);check(int.from_bytes(packed[:4],'little')==y and int.from_bytes(packed[4:],'little')==x,'range candidate byte/block identity')
    check(pair_bytes(1,0)!=bytes(6) and (1|0)!=0 and 0&65535==0,'range legal nonzero candidate can return zero')
    check(0x34000+1021==214013 and 0x26a000-317==2531011,'range source constants')
    # Positive opcode fixtures distinguish signed LH/MULHSU from LHU/MULHU.
    lh=decode(bytes.fromhex('8317840e'),0)[0];check(lh['signed'] and lh['imm']==232,'range strict LH fixture')
    lhu=decode((int.from_bytes(bytes.fromhex('8317840e'),'little')|(4<<12)).to_bytes(4,'little'),0)[0]
    check(lhu['width']==2 and not lhu.get('signed',False),'range strict LH/LHU distinction')
    check(decode(bytes.fromhex('33a5a502'),0)[0]['op']=='mulhsu' and decode(bytes.fromhex('33b5a502'),0)[0]['op']=='mulhu','range strict multiply variant fixtures')
    print('PASS:320 operand mutations and2 noncanonical FENCE.I encodings rejected;131072 range inputs/65536 LH identities/seed packing/zero-return example')


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
    tests(carriers);output=(json.dumps(ledger,indent=1,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'range retry exact ledger replay')
    print('PASS:full range/source/retry-tail operands/CFG/frames; domain-pruned guards, candidate compares and low16 ordinary return; exact ledger')
    print('PASS:NO target execution; callback identity/retention, retry termination and actual initializer return UNPROVED')


if __name__=='__main__':main()
