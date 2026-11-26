"""Tagged dispatch and its complete local transfer wrappers, bytes/CFG only.

No target ISA, provider, copy, frame state or MMIO execution/emulation.
Host arithmetic checks do not establish hardware success or input stability.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_record_dispatch_static as previous
import check_v4160_app44_closure_static as closure

init,sparse,check,take=previous.init,previous.sparse,previous.check,previous.take
decode=previous.previous.previous.decode
OUT=Path(__file__).with_name('v4160-tagged-dispatch-static.json')
DETAILS=(('tagged',0x16b7c,246,86,10,'f7711c4ac4195be6dd04aa57f8e2069e6c3275ae1f5377fd84c4d151d81adf47'),
 ('send',0x168de,96,36,7,'b78dcba7bd78bb506751aa59cae9981168dbe41bc97b8900e9eb7106f60d935f'),
 ('update',0x1693e,86,32,7,'2ca1290ceca255bcbf9776107820b20f8b1fed06cb2f7eed3ada3c4b397b7e5b'),
 ('query',0x16994,72,26,5,'0949ef0357f5c7543bc480b214103d78880ccba36a0551e0cb8cfb1edab2d538'),
 ('transfer',0x16896,72,25,1,'654d0f600794c1548c617d0f476ca4f0fa5aaf780f49be7c328b3df69e8878dc'))


def specs(role,pc):
    s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def load(o,r,b,v=0,w=4):e(o,'load',rd=r,rs1=b,imm=v,width=w)
    def store(o,r,b,v=0,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    def addi(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    def lui(o,r,v):e(o,'lui',rd=r,imm=v)
    def mv(o,r,a):e(o,'mv',rd=r,rs2=a)
    def binary(o,op,r,a,b):e(o,op,rd=r,rs1=a,rs2=b)
    def imm(o,op,r,a,v):e(o,op,rd=r,rs1=a,imm=v)
    def branch(o,op,a,b,t):e(o,op,rs1=a,rs2=b,target=pc+t)
    def bz(o,op,r,t):e(o,op,rs1=r,target=pc+t)
    def jump(o,t):e(o,'jump',target=pc+t)
    def call(o,t):e(o,'jal',rd=1,target=t)
    if role=='tagged':
        load(0,15,10,11,1);li(4,14,1);addi(6,15,15,-1);imm(8,'andi',15,15,255);branch(12,'bltu',14,15,240)
        addi(16,15,3,84);load(20,15,15);load(22,14,15,4,1);li(26,15,4);imm(28,'andi',14,14,8);bz(30,'bnez',14,242)
        addi(32,2,2,-64)
        for off,r,slot in ((34,1,60),(36,8,56),(38,9,52),(40,18,48),(42,19,44)):store(off,r,2,slot)
        load(44,9,10,2,1);li(48,14,8);branch(50,'bltu',14,9,214)
        lui(54,15,0x4000);addi(56,15,15,48);mv(60,8,10);store(62,15,2,12,2)
        li(66,12,11);addi(68,15,0,80);li(72,11,0);addi(74,10,2,18);store(78,15,2,14,1);call(82,0x8520)
        load(86,15,8,0,2);store(90,9,2,20,1);mv(94,12,9);imm(96,'srli',14,15,3);imm(100,'slli',15,15,5)
        store(102,15,2,17,1);store(106,14,2,16,1);lui(110,15,0x40000);load(114,15,15,76)
        addi(116,11,8,3);addi(120,10,2,21);e(124,'call_indirect',rd=1,rs1=15)
        li(126,9,0);li(128,19,3);addi(130,15,2,12);binary(132,'add',15,15,9);load(134,18,15,0,1)
        load(138,10,8,11,1);mv(142,11,18);call(144,0x16994);imm(148,'andi',10,10,8);bz(150,'bnez',10,230)
        load(152,13,8,2,1);load(156,10,8,11,1);addi(160,11,18,1);addi(164,13,13,5)
        imm(166,'andi',13,13,255);addi(170,12,2,16);imm(172,'andi',11,11,255);call(176,0x168de)
        load(180,10,8,11,1);li(184,13,8);li(186,12,8);mv(188,11,18);call(190,0x1693e)
        load(194,10,8,11,1);mv(198,11,18);call(200,0x16994);imm(204,'andi',10,10,112)
        binary(208,'sltu',15,0,10);imm(212,'slli',15,15,2)
        for off,r,slot in ((214,1,60),(216,8,56),(218,9,52),(220,18,48),(222,19,44)):load(off,r,2,slot)
        mv(224,10,15);addi(226,2,2,64);e(228,'jr',rs1=1)
        addi(230,9,9,1);branch(232,'bne',9,19,130);li(236,15,4);jump(238,214)
        li(240,15,4);mv(242,10,15);e(244,'jr',rs1=1)
    elif role=='send':
        addi(0,2,2,-32);store(2,8,2,24);store(4,9,2,20);store(6,1,2,28)
        imm(8,'andi',15,10,1);mv(12,8,12);mv(14,9,13);bz(16,'beqz',15,28)
        lui(18,15,0x40011000);li(22,14,16);store(24,14,15,-2028)
        imm(28,'andi',10,10,2);bz(30,'beqz',10,42);lui(32,15,0x40011000);li(36,14,1);store(38,14,15,-2028)
        li(42,10,2);store(44,11,2,12);call(46,0x16896);load(50,11,2,12)
        binary(52,'add',9,9,8);mv(54,10,11);call(56,0x16896);branch(60,'bne',8,9,84)
        load(64,1,2,28);load(66,8,2,24);lui(68,15,0x40011000);li(72,14,17);store(74,14,15,-2032)
        load(78,9,2,20);addi(80,2,2,32);e(82,'jr',rs1=1)
        load(84,10,8,0,1);addi(88,8,8,1);call(90,0x16896);jump(94,60)
    elif role in ('query','update'):
        addi(0,2,2,-32);store(2,1,2,28);imm(4,'andi',15,10,1);bz(8,'beqz',15,20)
        lui(10,15,0x40011000);li(14,14,16);store(16,14,15,-2028)
        imm(20,'andi',10,10,2);bz(22,'beqz',10,34);lui(24,15,0x40011000);li(28,14,1);store(30,14,15,-2028)
        li(34,10,3 if role=='query' else 5)
        if role=='query':
            store(36,11,2,12);call(38,0x16896);load(42,11,2,12);mv(44,10,11);call(46,0x16896)
            li(50,10,0);call(52,0x16896);load(56,1,2,28);lui(58,15,0x40011000);li(62,14,17)
            store(64,14,15,-2032);addi(68,2,2,32);e(70,'jr',rs1=1)
        else:
            store(36,13,2,12);store(38,12,2,8);store(40,11,2,4);call(42,0x16896)
            load(46,11,2,4);mv(48,10,11);call(50,0x16896);load(54,12,2,8);mv(56,10,12);call(58,0x16896)
            load(62,13,2,12);mv(64,10,13);call(66,0x16896);load(70,1,2,28);lui(72,15,0x40011000);li(76,14,17)
            store(78,14,15,-2032);addi(82,2,2,32);e(84,'jr',rs1=1)
    elif role=='transfer':
        addi(0,15,0,255);lui(4,13,0x40013000);load(8,14,13,8,2);imm(12,'andi',14,14,2);bz(14,'beqz',14,50)
        imm(16,'slli',10,10,16);imm(18,'srli',10,10,16);store(20,10,13,12,2)
        addi(24,15,0,255);lui(28,13,0x40013000);load(32,14,13,8,2);imm(36,'andi',14,14,1);bz(38,'beqz',14,62)
        load(40,10,13,12,2);imm(44,'andi',10,10,255);e(48,'jr',rs1=1)
        addi(50,15,15,-1);imm(52,'andi',15,15,255);bz(56,'bnez',15,8);li(58,10,0);e(60,'jr',rs1=1)
        addi(62,15,15,-1);imm(64,'andi',15,15,255);bz(68,'bnez',15,32);jump(70,58)
    else:raise RuntimeError('unknown tagged role')
    return s


def body(raw,role,pc,size,count,store_count,digest):
    n=decode(raw,pc);expected=specs(role,pc)
    check(set(n)==set(expected),'tagged complete boundaries '+role)
    for p,f in expected.items():init.g(n,p,'tagged '+role+' instruction '+hex(p-pc),**f)
    edges={};calls=[]
    for p,d in n.items():
        if d['op']=='jr':check(d['rs1']==1,'tagged return register');qs=[]
        elif d['op']=='jump':qs=[d['target']]
        elif d['op'] in ('beqz','bnez','bltu','bne'):qs=[p+d['size'],d['target']]
        else:qs=[p+d['size']]
        check(all(q in n for q in qs),'tagged complete local successors '+role);edges[p]=qs
        if d['op']=='call_indirect' or d['op']=='jal':
            check(d['rd']==1,'tagged linked calls');calls.append({'pc':hex(p),'target':hex(d['target']) if 'target' in d else 'fresh4004c & ~1',
                'link':hex(p+d['size']),'normal_return_proved':False})
    seen=set();active=set();back=[]
    def visit(p):
        if p in seen:return
        seen.add(p);active.add(p)
        for q in edges[p]:
            if q in active:back.append((p-pc,q-pc))
            else:visit(q)
        active.remove(p)
    visit(pc)
    expected_back={'tagged':[(232,130)],'send':[(94,60)],'transfer':[(56,8),(68,32)]}.get(role,[])
    check(seen==set(n) and sorted(back)==expected_back,'tagged full reachability and exact backedges '+role)
    stores=[d for d in n.values() if d['op']=='store'];writes=sorted({d['rd'] for d in n.values() if d.get('rd',0)})
    check((len(raw),len(n),len(stores),sha256(raw).hexdigest())==(size,count,store_count,digest),'tagged complete identity '+role)
    if role=='transfer':check(not calls and writes==[10,13,14,15],'transfer no A1/S/frame/context writes')
    if role in ('query','update'):check(not any(r in writes for r in range(8,10)) and not any(r in writes for r in range(18,28)), 'query/update no S writes')
    return {'start':hex(pc),'end_exclusive':hex(pc+size),'bytes':size,'sha256':digest,'instructions':list(n.values()),
        'stores':stores,'calls':calls,'encoded_GPR_writes':writes,'backedges_relative':back,
        'conditional_normal_return_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()}}


def length_footprint(fresh):
    count=(fresh+5)&255;end=16+count
    return {'fresh_length':fresh,'send_count':count,'read_interval_relative_tagged_SP':[16,end],
        'past_initialized_prefix_interval':([29,end] if end>29 else None),
        'saved_register_intersections':{name:[max(16,start),min(end,start+4)] for name,start in
            (('S3',44),('S2',48),('S1',52),('S0',56),('RA',60)) if end>start},
        'past_tagged_frame_interval':([64,end] if end>64 else None)}


def derive(app,carriers,header,coverage):
    parent=previous.derive(app,carriers,header,coverage)
    bodies={r:body(take(app,p,size),r,p,size,n,stores,h) for r,p,size,n,stores,h in DETAILS}
    check(sum(b['bytes'] for b in bodies.values())==572 and sum(len(b['instructions']) for b in bodies.values())==205
          and sum(len(b['stores']) for b in bodies.values())==30,'tagged body census')
    fill_detail=next(d for d in closure.DETAILS if d[0]==0x8520)
    fill=closure.body(take(app,0x8520,168),fill_detail)
    check(any(c['target']=='0x16b7c' for c in parent['bodies']['dispatch']['calls']),'record dispatcher to tagged body join')
    n={d['pc']:d for d in bodies['tagged']['instructions']}
    check([c['target'] for c in bodies['tagged']['calls']]==['0x8520','fresh4004c & ~1','0x16994','0x168de','0x1693e','0x16994'],'tagged full call set')
    for role in ('send','query','update'):check(all(c['target']=='0x16896' for c in bodies[role]['calls']),'wrapper to complete transfer join '+role)
    # Complete raw operands tie the host footprint formulas to actual frame offsets.
    check(n[0x16b9c]['imm']==-64 and n[0x16bae]['target']==0x16c52 and n[0x16bac]['imm']==8,'frame and first length bound')
    check(n[0x16bbe]['imm']==11 and n[0x16bc6]['imm']==18 and n[0x16bc4]['imm']==0,'local fill11 call arguments')
    check(n[0x16bf4]['imm']==21 and n[0x16bda]['rs2']==9,'first length passed to copy')
    check(n[0x16c14]['imm']==2 and n[0x16c20]['imm']==5 and n[0x16c22]['imm']==255 and n[0x16c26]['imm']==16,'fresh length send footprint')
    early=[d for p,d in n.items() if p<0x16bc4]
    check(not any(d.get('rs1')==11 or d.get('rs2')==11 or d.get('rd')==11 for d in early),'ambient A1 unread before first explicit overwrite')
    check(n[0x16bc4]['rd']==11 and n[0x16bc4]['imm']==0,'first explicit ambient A1 replacement')
    check(all(d['rs1']==2 for d in bodies['tagged']['stores']),'tagged own stores frame-only')
    send={d['pc']:d for d in bodies['send']['instructions']}
    check(send[0x16912]['rs1']==9 and send[0x16912]['rs2']==8 and send[0x16936]['imm']==1,'send end pointer and unit increment')
    selectors=(n[0x16bb2]['imm']+n[0x16bb4]['imm']).to_bytes(2,'little')+bytes([n[0x16bc0]['imm']])
    check(selectors.hex()=='304050','tagged selector literals')
    direct_targets={0x8520,0x16896,0x168de,0x1693e,0x16994}
    check(all(int(c['target'],16) in direct_targets for b in bodies.values() for c in b['calls'] if c['target'].startswith('0x')),'direct software call closure')
    return {'schema':'TSL9-tagged-dispatch-static-v1','profile':init.timer.PROFILE,'scope':'5 complete APP bodies572B/205instructions/30stores plus reused fill168B/55instructions/19stores',
        'bodies':bodies,'revalidated_fill':fill,'conditional_direct_software_targets_closed':True,
        'entry_guards':{'tag':'fresh U8[O+11] in1,2 else4 without frame/config/length reads',
            'config':'fresh U8[U32[GP+84]+4]&8 ->4 without frame/length read',
            'first_length':'save64B frame then fresh L0=U8[O+2]; L0>8 ->epilogue4; no packing/fill/copy',
            'ambient_A1':'not read before LI A1,0 at16bc4; rejected paths may leave ambient A1 unchanged'},
        'packing':{'frame':'tagged new SP=S; saved RA60/S056/S152/S248/S344; selectors S+12..14=30,40,50; S+15 not written',
            'fill':'8520(S+18,0,11): computed tail target856a, descending stores S+28..18, no provider/callee or frame; full fill revalidated',
            'header':'S+20=L0; S+17=low8(ID<<5); S+16=low8(ID>>3), fresh U16[O] after fill',
            'copy':'fresh4004c(S+21,O+3,L0) forL0=0..8; no scalar test; actual effects/retention unknown',
            'initialized_prefix':'with actual reference-copy/fill/context/nonalias: S+16..28 initialized; S+15 hole is outside send start'},
        'selector_loop':{'counter':'after copy S1=0,S3=3; fresh selector byte S+12+S1; query(fresh tag,selector)',
            'busy':'query reply&8 ->increment S1; compare3; try indices0,1,2 orreturn4',
            'selected':'send(fresh tag,low8(selector+1),S+16,low8(fresh U8[O+2]+5)); update(fresh tag,selector,8,8); query(fresh tag,selector)',
            'result':'return4 iff final query reply&0x70 nonzero, else0; send/update replies not used',
            'bounds_conditional_on':'valid frames/context/code, ordinary access completion, nonadverse MMIO/frame alias/interrupt/writer; normal copy return required before counter init'},
        'fresh_length_footprints': [length_footprint(x) for x in range(256)],
        'length_preservation':'entry L0<=8 does not constrain later fresh L1 without object preservation; N=low8(L1+5), may be0..255',
        'stable_length_bridge':'if L1=L0 and0<=L0<=8, N=5+L0 and read S+16..20+L0; copy range21..20+L0 inside fill18..28 and disjoint saved44..63',
        'wrapper_contracts':{'query':'transfer inputs[3,entry A1,0]; returns third reply; locally saves entry A1 at ownSP+12',
            'send':'transfer inputs[2,entry A1,fresh bytes at buffer0..N-1]; source pointer in S0, end in S1; saves caller S0/S1 to own frame; no early abort based on transfer replies',
            'update':'transfer inputs[5,entry A1,entry A2,entry A3]; locally saves arguments at ownSP+4,+8,+12; returns fourth reply',
            'IO':'if tagbit0 write16 to40010814; iftagbit1 write1 there; before ordinary return write17 to40010810',
            'pointer_scope':'send saves outer S0 (O) in nested frame; original object pointer is not globally erased; other ambient registers not scrubbed'},
        'transfer_contract':{'first_phase':'up to255 fresh U16[40013008] bit1 polls; all clear ->0 and no DATA store/read',
            'ready':'SH low16(input A0) to4001300c; up to255 fresh status bit0 polls; allclear ->0 without DATA read',
            'completed_numeric':'LHU4001300c &255; same0 return possible as timeout; no successful physical transfer/ACK claim',
            'context':'no frame, callees or S/SP/GP/RA/A1 writes; encoded GPR writes A0,A3,A4,A5 only'},
        'lifetime_boundaries':['resident copy can observe O+3 and S+21, actual preservation/retention unknown',
            'source O retained in S0/nested saved-S0 frame, not a proof of global lifetime/ownership',
            'first length and later length/tag loads are independent; provider/IRQ/aliases can invalidate stable-length formulas',
            'no direct entry-A1 use in accepted tagged prefix does not prove pointer erasure or no prior escaping alias'],
        'remaining_boundaries':['actual copy binding and preservation/retention','object+2/+11 writers and reachable fresh length changes',
            'physical MMIO semantics and concurrent writers','broader object/stack lifetime'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(app):
    for tag in range(256):check((((tag-1)&255)<=1)==(tag in (1,2)),'byte tag guard')
    for cfg in range(256):
        for length in range(256):check((not cfg&8 and length<=8)==(cfg&8==0 and length in range(9)),'config/entry length partition')
    for ID in range(65536):
        hi=(ID>>3)&255;lo=(ID<<5)&255
        check(((hi<<3)|(lo>>5))==ID&2047,'packed ID only low11 bits')
    for L0 in range(9):
        for L1 in range(256):
            f=length_footprint(L1);N=f['send_count']
            check(0<=N<=255 and bool(f['past_initialized_prefix_interval'])==(N>=14),'fresh length beyond initialized prefix')
            check(bool(f['past_tagged_frame_interval'])==(N>=49),'fresh length beyond tagged frame')
            check(bool(f['saved_register_intersections'])==(N>=29),'fresh length reaches saved registers')
            if L1==L0:check(N==L0+5 and 16+N==21+L0 and not f['past_initialized_prefix_interval'],'stable length source span')
    check(length_footprint(251)['send_count']==0 and length_footprint(250)['send_count']==255,'fresh length wrap endpoints')
    for status in range(256):check((4 if status&112 else 0)==int(bool(status&112))*4,'final status mapping')
    for counter in range(1,256):check(((counter-1)&255)==counter-1,'transfer counter range1..255')
    check(255-255==0 and (0x8550+4*(15-11)+10)&~1==0x856a,'bounded transfer/fill11 arithmetic')
    for k in range(3):
        for L in range(9):check((k+1)*3+(2+L+5)+4+3==17+L+3*k,'stable length transfer call census')
    roles={r:(p,size,count,stores,h) for r,p,size,count,stores,h in DETAILS}
    cases=(('tagged',8,1<<20),('tagged',48,4),('tagged',72,4),('tagged',90,1<<20),
        ('tagged',116,1<<20),('tagged',124,0x80),('tagged',152,1<<20),('tagged',166,1<<20),
        ('tagged',204,1<<20),('tagged',232,0x1000),('send',52,0x80),('send',84,1<<20),
        ('query',50,4),('update',62,0x80),('transfer',0,1<<20),('transfer',20,1<<20),('transfer',44,1<<20),('transfer',68,0x80))
    for role,off,flip in cases:
        pc,size,count,stores,digest=roles[role];raw=bytearray(take(app,pc,size));w=decode(raw,pc)[pc+off]['size']
        raw[off:off+w]=(int.from_bytes(raw[off:off+w],'little')^flip).to_bytes(w,'little')
        try:body(raw,role,pc,size,count,stores,digest)
        except RuntimeError as e:check(str(e)=='tagged '+role+' instruction '+hex(off),'unexpected tagged mutation guard '+str(e))
        else:raise RuntimeError('tagged mutation escaped')
    print('PASS: 65536 config/length + 65536 ID cases; 2304 independent length pairs; 256 tag/status cases each; 27 call-count cases; 18 specified raw mutations')


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true',help='Create ledger exclusively');o=p.parse_args()
    app=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(app)==76800 and sha256(app).hexdigest()==init.binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK header identity')
    carriers=[]
    for label,folder,tail,size,digest in init.binding.PROFILES:
        raw=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(raw)==size and sha256(raw).hexdigest()==digest,'candidate identity '+label);carriers.append(raw)
    raw_hex=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
    coverage=sparse.derive(app,carriers,header,raw_hex,sparse.parser())
    sources,vectors=init.timer.source_contract();ledger=derive(app,carriers,header,coverage)
    ledger['sources'],ledger['official_Xwchc_vectors']=sources,vectors
    tests(app);output=(json.dumps(ledger,indent=1,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'tagged dispatch exact ledger replay')
    print('PASS: 5 complete APP bodies572B/205instructions/30stores; full fill168B revalidated; direct software callees resolved in bytes')
    print('PASS: exact ledger bytes; NO target execution; copy preservation/retention, fresh length stability and physical transfer success UNPROVED')


if __name__=='__main__':main()
