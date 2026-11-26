"""Complete original record dispatch/leaf/peripheral operand and footprint checks.

Offline byte decoding, conditional CFGs and host interval/bitfield arithmetic.
Never executes/emulates target ISA, copy, stack memory, callbacks or MMIO.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_payload_consumers_static as previous

init,sparse,check=previous.init,previous.sparse,previous.check
take=previous.take
OUT=Path(__file__).with_name('v4160-record-dispatch-static.json')
DETAILS=(('dispatch',0x12a08,102,35,5,'334494853a765e550af99f0e8dd95523efaf7cbb86d392e0340a5d5f004940c9'),
 ('probe',0x81aa,6,2,0,'887c2bfb847a7e013acebac38c8be3f2bed06fd44305080ad6fc7ca3593e8fc3'),
 ('gate',0x821e,42,15,0,'4af30f18b196e304a5b6d30bb167ee2a02c567c4ffcf4e36bb4f72e6204bcdcd'),
 ('peripheral',0x18ca4,212,72,8,'f2e7e2a7bc63053c45f5951e801c84bd0b83dc603168267e54bde8aa4bd86960'))


def specs(role,pc):
    s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def load(o,r,b,v=0,w=4):e(o,'load',rd=r,rs1=b,imm=v,width=w)
    def store(o,r,b,v=0,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    def addi(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    def mv(o,r,a):e(o,'mv',rd=r,rs2=a)
    def binary(o,op,r,a,b):e(o,op,rd=r,rs1=a,rs2=b)
    def imm(o,op,r,a,v):e(o,op,rd=r,rs1=a,imm=v)
    def branch(o,op,a,b,t):e(o,op,rs1=a,rs2=b,target=pc+t)
    def bz(o,op,r,t):e(o,op,rs1=r,target=pc+t)
    def jump(o,t):e(o,'jump',target=pc+t)
    def call(o,t):e(o,'jal',rd=1,target=t)
    if role=='dispatch':
        addi(0,2,2,-48);store(2,8,2,40);store(4,1,2,44);mv(6,8,10);call(8,0x81aa)
        bz(12,'bnez',10,24);load(14,14,8,0,2);li(18,15,1);branch(20,'bne',14,15,86)
        li(24,10,0);call(26,0x821e);bz(30,'beqz',10,86);load(32,15,8,11,1);bz(36,'bnez',15,94)
        load(38,15,8,0,2);load(42,12,8,2,1);store(46,0,2,20,2);store(50,15,2,12)
        store(52,12,2,22,1);e(56,'lui',rd=15,imm=0x40000);load(60,15,15,76)
        addi(62,11,8,3);addi(66,10,2,23);e(70,'call_indirect',rd=1,rs1=15)
        e(72,'lui',rd=10,imm=0x40006000);addi(76,11,2,12);addi(78,10,10,1024);call(82,0x18ca4)
        load(86,1,2,44);load(88,8,2,40);addi(90,2,2,48);e(92,'jr',rs1=1)
        mv(94,10,8);call(96,0x16b7c);jump(100,86)
    elif role=='probe':load(0,10,3,167,1);e(4,'jr',rs1=1)
    elif role=='gate':
        addi(0,15,3,84);load(4,15,15);load(6,14,15,4,1);li(10,15,0);imm(12,'andi',14,14,8)
        bz(14,'bnez',14,38);li(16,14,2);li(18,15,0);branch(20,'bltu',14,10,38)
        addi(24,15,3,192);binary(28,'add',15,15,10);load(30,15,15,1,1);imm(34,'sltiu',15,15,3)
        mv(38,10,15);e(40,'jr',rs1=1)
    elif role=='peripheral':
        load(0,15,10,8);imm(2,'slli',14,15,5);branch(6,'blt',14,0,186)
        load(10,15,10,8);imm(12,'slli',14,15,4);branch(16,'blt',14,0,190)
        load(20,15,10,8);li(22,13,4);imm(24,'slli',14,15,3);branch(28,'bge',14,0,182)
        li(32,13,2);imm(34,'slli',15,13,4);binary(38,'add',15,15,10)
        load(40,14,15,384);imm(44,'andi',14,14,1);store(46,14,15,384)
        load(50,12,11,8,1);load(54,10,11,9,1);bz(58,'bnez',12,194)
        load(60,14,11);load(62,12,15,384);imm(66,'slli',14,14,21)
        binary(68,'or',14,14,10);binary(70,'or',14,14,12);store(72,14,15,384)
        load(76,14,11,10,1);imm(80,'andi',14,14,15);store(82,14,11,10,1)
        load(86,12,15,388);imm(90,'andi',12,12,-16);store(92,12,15,388)
        load(96,12,15,388);binary(100,'or',14,14,12);store(102,14,15,388)
        for off,first,second,third,fourth,out in ((106,12,11,13,14,392),(138,16,15,17,18,396)):
            load(off,12,11,first,1);load(off+4,14,11,second,1);imm(off+8,'slli',12,12,8)
            binary(off+10,'or',12,12,14);load(off+12,14,11,third,1);imm(off+16,'slli',14,14,16)
            binary(off+18,'or',12,12,14);load(off+20,14,11,fourth,1);imm(off+24,'slli',14,14,24)
            binary(off+26,'or',14,14,12);store(off+28,14,15,out)
        load(170,14,15,384);imm(174,'ori',14,14,1);store(178,14,15,384)
        mv(182,10,13);e(184,'jr',rs1=1);li(186,13,0);jump(188,34);li(190,13,1);jump(192,34)
        load(194,14,11,4);load(196,16,15,384);imm(200,'slli',14,14,3)
        binary(202,'or',14,14,10);binary(204,'or',14,14,12);binary(206,'or',14,14,16);jump(210,72)
    else:raise RuntimeError('unknown record role')
    return s


def body(raw,role,pc,size,count,store_count,digest):
    n=previous.previous.decode(raw,pc);expected=specs(role,pc)
    check(set(n)==set(expected),'record complete boundaries '+role)
    for p,f in expected.items():init.g(n,p,'record '+role+' instruction '+hex(p-pc),**f)
    edges={};calls=[]
    for p,d in n.items():
        if d['op']=='jr':check(d['rs1']==1,'record return register');qs=[]
        elif d['op']=='jump':qs=[d['target']]
        elif d['op'] in ('beqz','bnez','bne','bltu','blt','bge'):qs=[p+d['size'],d['target']]
        else:qs=[p+d['size']]
        check(all(q in n for q in qs),'record complete local successors '+role)
        edges[p]=qs
        if d['op']=='call_indirect' or d['op']=='jal':
            check(role=='dispatch' and d['rd']==1,'record only linked dispatch calls')
            calls.append({'pc':hex(p),'target':hex(d['target']) if 'target' in d else 'fresh4004c & ~1',
                          'link':hex(p+d['size']),'normal_return_proved':False})
    seen=set();active=set()
    def visit(p):
        check(p not in active,'record local cycle '+role)
        if p in seen:return
        seen.add(p);active.add(p)
        for q in edges[p]:visit(q)
        active.remove(p)
    visit(pc);check(seen==set(n),'record all nodes reachable '+role)
    stores=[d for d in n.values() if d['op']=='store'];writes=sorted({d['rd'] for d in n.values() if d.get('rd',0)})
    check((len(raw),len(n),len(stores),sha256(raw).hexdigest())==(size,count,store_count,digest),'record complete identity '+role)
    if role=='probe':check(writes==[10] and not stores and not calls,'probe only A0 write')
    if role=='gate':check(writes==[10,14,15] and not stores and not calls,'gate register writes')
    if role=='peripheral':
        check(writes==[10,12,13,14,15,16] and not calls,'peripheral no A1/frame/context register writes')
        check([(d['rs1'],d['imm'],d['width']) for d in stores]==[(15,384,4),(15,384,4),(11,10,1),
            (15,388,4),(15,388,4),(15,392,4),(15,396,4),(15,384,4)],'peripheral complete store footprint')
        check(all(d['rs2'] in (12,14) for d in stores),'peripheral no direct A1 pointer-value store')
    return {'start':hex(pc),'end_exclusive':hex(pc+size),'bytes':size,'sha256':digest,'instructions':list(n.values()),
        'stores':stores,'calls':calls,'encoded_GPR_writes':writes,'conditional_normal_return_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()}}


def footprint(n):
    copied=set(range(23,23+n))
    return {'length':n,'copy_interval_relative_new_SP':[23,23+n],
        'saved_S0_overlap':sorted(copied&set(range(40,44))),
        'saved_RA_overlap':sorted(copied&set(range(44,48))),
        'outside_frame_interval':([48,23+n] if n>=26 else None),
        'outside_frame_byte_count':max(0,n-25),
        'handler_payload_not_filled_by_this_copy':sorted(set(range(23,31))-copied)}


def derive(app,carriers,header,coverage):
    parent=previous.derive(app,carriers,header,coverage)
    bodies={r:body(take(app,p,size),r,p,size,n,stores,h) for r,p,size,n,stores,h in DETAILS}
    state=parent['bodies']['state']
    check(any(e.get('target')=='0x12a08' for e in state['terminal_external_edges']),'state to full dispatch join')
    n={d['pc']:d for d in bodies['dispatch']['instructions']};g={d['pc']:d for d in bodies['gate']['instructions']}
    check([c['target'] for c in bodies['dispatch']['calls']]==['0x81aa','0x821e','fresh4004c & ~1','0x18ca4','0x16b7c'],
          'dispatch full callees')
    check(n[0x12a46]['rd']==11 and n[0x12a46]['rs1']==8 and n[0x12a54]['rd']==11 and n[0x12a54]['rs1']==2,
          'two explicit A1 replacement sites')
    check([d['pc'] for d in n.values() if d.get('rd')==11]==[0x12a46,0x12a54],'ambient A1 survives local gates and tagged path')
    check(g[0x8236]['imm']+g[0x823c]['imm']==193,'gate state byte base')
    direct=[c for c in bodies['dispatch']['calls'] if c['target']=='0x18ca4'][0]
    check(direct['link']=='0x12a5e','peripheral joins full epilogue')
    check(n[0x12a50]['imm']+n[0x12a56]['imm']==0x40006400,'peripheral fixed base')
    fixed=set(range(12,16))|set(range(20,23))
    check(sorted(set(range(12,23))-fixed)==[16,17,18,19],'record fixed-store gap')
    intervals=[footprint(n) for n in range(256)]
    return {'schema':'TSL9-record-dispatch-static-v1','profile':init.timer.PROFILE,'scope':'4 complete APP bodies362B/124instructions/13stores',
        'bodies':bodies,'object_from_prior_handoff':parent['stack_handoff']['output_object'],
        'probe':'fresh U8[GP+167]; only A0 overwritten; frame stores before probe can alias state unless excluded',
        'gate':'read U32[GP+84], then byte at pointer+4; bit3 set ->0; else full unsigned input<=2 then fresh U8[GP+193+index]<3',
        'dispatch_contract':{'probe_zero':'fresh U16[O] must1; nonzero probe bypasses this ID condition',
            'gate_call':'821e(0), zero reply ->epilogue; tag sampled fresh U8[O+11] only after gate',
            'tag_nonzero':'16b7c(A0=O); A1 remains ambient entry word through these local bodies, identity conditional on earlier provider',
            'tag_zero_fixed_record':'new SP=entry SP-48; saveS0+40/RA+44, U32 ID+12, U16 zero+20, U8 length+22; gap16..19 not directly initialized',
            'copy_request':'fresh4004c(new SP+23,O+3,original sampled U8[O+2]); no independent length bound; copy side effects unknown',
            'peripheral_request':'18ca4(A0=40006400,A1=new SP+12), exact explicit A1 replacement after copy',
            'normal_return':'restore RA/S0/SP only; untagged A1 remains record pointer in selected peripheral body; no local A0 normalization'},
        'length_footprints_under_reference_copy':intervals,
        'length_boundaries':{'first_saved_S0_overlap':18,'first_saved_RA_overlap':22,'first_outside_frame':26,
            'first_all_8_handler_payload_bytes_copied':8,'all_are_conditional_intervals_not_executed':True},
        'peripheral_contract':{'selection':'fresh word T+8 per test; bit26 of first selects0, else bit27 of second selects1, else bit28 of third selects2, else return4 with no P read/store',
            'selected':'P=entry A1; B=T+384+16*bank; return bank (0 is a normal selected value)',
            'ordered_stores':['U32[B]=fresh U32[B]&1','U32[B]=(fresh ID<<shift)|sampledR|sampledF_if_nonzero|fresh U32[B]',
                'U8[P+10]=fresh U8[P+10]&15','U32[B+4]=fresh U32[B+4]&fffffff0',
                'U32[B+4]=fresh U32[B+4]|sampled_nibble','U32[B+8]=bytes P+11..14 read12,11,13,14',
                'U32[B+12]=bytes P+15..18 read16,15,17,18','U32[B]=fresh U32[B]|1'],
            'ID_branch':'sample F=U8[P+8], R=U8[P+9]; F0->U32[P]<<21; Fnonzero->U32[P+4]<<3 with full F OR; all RV32',
            'A1_unchanged_no_callees_no_direct_pointer_value_store':True,'register_containment_not_lifetime_proof':True},
        'conditional_untagged_bridge':{'record':'P=new SP+12; fixed F/R zero if copy/provider/aliases preserve them; alternate ID gap then not read',
            'length':'P+10 byte later masked15; payload8 read independently of nibble or length',
            'short_copy':'length<8 leaves some SP+23..30 unfilled by this copy; not proof of zero/unmapped/invalid bytes',
            'long_copy':'length>=18 can overwrite saved S0; >=22 saved RA; >=26 beyond frame; no safety/completeness claim for these paths',
            'ambient':'earlier original stack source may reach tagged callee in A1; untagged path replaces A1 with O+3 then local record; other ambient words and provider retention unproved'},
        'premises':['conditional ISA, valid nonwrapping stack/object/GP/config/MMIO accesses and appropriate alignment',
            'selected copy actual binding/normal return/context preservation/no adverse alias or writer/IRQ/reentry must be proved separately',
            'MMIO fresh reads not collapsed to stable state; numeric stores are not physical RF/peripheral semantics',
            'direct pointer-field store absence does not prove ownership, erasure, no escaping aliases, or no data numerically equal to addresses'],
        'remaining_boundaries':['16b7c tagged continuation with ambient inputs','copy-provider pointer retention and actual installed binding',
            'object+2/+11 writers and reachable lengths','physical MMIO side effects and stack record lifetime'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(app):
    for cfg in range(256):
        for state in range(256):
            result=int(not cfg&8 and state<3)
            check(result==int(cfg&8==0)*int(state in (0,1,2)),'gate byte partition')
    # Host interval algebra only: no stack/copy state or target execution.
    for n in range(256):
        f=footprint(n)
        check(bool(f['saved_S0_overlap'])==(n>=18) and bool(f['saved_RA_overlap'])==(n>=22), 'saved context interval thresholds')
        check(bool(f['outside_frame_interval'])==(n>=26) and f['outside_frame_byte_count']==max(0,n-25),'frame bound interval threshold')
        check(len(f['handler_payload_not_filled_by_this_copy'])==max(8-n,0),'fixed payload read/copy interval difference')
    # Every possible independent selector bit triple, not a stable register snapshot.
    for bits in range(8):
        b=[bits>>i&1 for i in range(3)]
        bank=next((i for i,v in enumerate(b) if v),4)
        check(bank==(0 if b[0] else 1 if b[1] else 2 if b[2] else 4),'fresh selector priority')
    for old in range(256):check(old&15==old%16,'record nibble is masking not capping')
    for byte in range(256):
        for shift in (0,8,16,24):check(((byte<<shift)>>shift)&255==byte,'payload byte placement')
    roles={r:(p,size,count,stores,h) for r,p,size,count,stores,h in DETAILS}
    cases=(('dispatch',14,1<<20),('dispatch',36,0x80),('dispatch',42,1<<20),('dispatch',46,1<<20),
        ('dispatch',62,1<<20),('dispatch',70,0x80),('dispatch',76,4),('dispatch',82,1<<21),
        ('probe',0,1<<20),('gate',6,1<<20),('gate',20,0x1000),('gate',34,1<<20),
        ('peripheral',6,0x1000),('peripheral',46,1<<20),('peripheral',76,1<<20),
        ('peripheral',82,1<<20),('peripheral',106,1<<20),('peripheral',174,1<<20))
    for role,off,flip in cases:
        pc,size,count,stores,digest=roles[role];raw=bytearray(take(app,pc,size));d=previous.previous.decode(raw,pc)[pc+off];w=d['size']
        raw[off:off+w]=(int.from_bytes(raw[off:off+w],'little')^flip).to_bytes(w,'little')
        try:body(raw,role,pc,size,count,stores,digest)
        except RuntimeError as e:check(str(e)=='record '+role+' instruction '+hex(off),'unexpected record mutation guard '+str(e))
        else:raise RuntimeError('record mutation escaped')
    print('PASS: 65536 gate cases; 256 length footprints; 8 independent selector triples; 256 nibble and 1024 byte-placement cases; 18 specified raw mutations')


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
    tests(app);output=(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'record dispatch exact ledger replay')
    print('PASS: 4 complete APP bodies362B/124instructions/13stores; state/dispatch/gates/peripheral argument and return joins')
    print('PASS: exact ledger bytes; no target execution; copy/ambient-pointer retention/installed binding/physical MMIO UNPROVED')


if __name__=='__main__':main()
