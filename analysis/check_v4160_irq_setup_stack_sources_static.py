"""Controller/config setup and candidate prior writes to extended-ID stack slot.

Original operands/CFGs plus conditional host address/bitfield algebra only.
No target ISA/CSR/MMIO, interrupt, provider, stack or RAM execution/model.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_peripheral_rx_ingress_static as previous
import check_v4160_app_jt0_call_chain_static as boot

init,sparse,check,take,decode=previous.init,previous.sparse,previous.check,previous.take,previous.decode
OUT=Path(__file__).with_name('v4160-irq-setup-stack-sources-static.json')
DETAILS=(('controller',0x9a42,144,46,10,'3d86f7124c682f02bbcc3b85162bfc37ebebbcd2631bbc3f5b2dfacf5e4c36c4'),
 ('pins',0x9a24,30,12,5,'756314467323266876b3aee48b6f979d57f4b754b42578d3ef313637d40487bf'),
 ('config',0x12d92,194,62,6,'779ae31d8a5baba95433a098c3b28f2853da1f94a70a5fc27e07aea369ee1565'),
 ('clock18',0x19124,30,12,2,'ca3d4aef350f5c783ee6eeae7d25ba85b74055551058135024d07edf1804e864'),
 ('clock1c',0x19142,30,12,2,'e74e208ea699962ecf8c71269627881ab8edfd64787710b410c6c74a3607d6d5'),
 ('reset0c',0x19160,30,12,2,'a5541a42d8ec2844fcd1d2df5492c90e2b140ce22ae79b02f50e330277c31b60'),
 ('reset10',0x1917e,30,12,2,'bec2619b2d742c8bfa1b82087f6cea1ed8a133adb89b25258a487ef2e2d2648e'))


def specs(role,pc):
    s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def load(o,r,b,v=0,w=4):e(o,'load',rd=r,rs1=b,imm=v,width=w)
    def store(o,r,b,v=0,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    def addi(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    def lui(o,r,v):e(o,'lui',rd=r,imm=v)
    def mv(o,r,a):e(o,'mv',rd=r,rs2=a)
    def imm(o,op,r,a,v):e(o,op,rd=r,rs1=a,imm=v)
    def branch(o,op,a,b,t):e(o,op,rs1=a,rs2=b,target=pc+t)
    def call(o,t):e(o,'jal',rd=1,target=t)
    if role=='controller':
        addi(0,2,2,-16);store(2,18,2);store(4,1,2,12);store(6,8,2,8);store(8,9,2,4);addi(10,18,0,136)
        e(14,'csr',rd=0,rs1=18,funct3=3,csr=0x800);lui(18,9,0x2020000);addi(22,10,9,6);li(26,11,1);call(28,0x19142)
        lui(32,8,0x1000);addi(34,10,8,29);li(38,11,1);call(40,0x19124)
        addi(44,10,9,6);li(48,11,1);call(50,0x1917e);addi(54,10,9,6);li(58,11,0);call(60,0x1917e)
        addi(64,10,8,29);li(68,11,1);call(70,0x19160);li(74,11,0);addi(76,10,8,29);call(80,0x19160)
        lui(84,15,0xe000e000);store(88,0,15,1069,1);lui(92,14,0x2000);store(94,14,15,260)
        addi(98,14,0,32);store(102,14,15,1060,1);li(106,14,16);store(108,14,15,260)
        addi(112,14,0,48);store(116,14,15,1063,1);addi(120,14,0,128);store(124,14,15,260)
        e(128,'csr',rd=0,rs1=18,funct3=2,csr=0x800)
        load(132,1,2,12);load(134,8,2,8);load(136,9,2,4);load(138,18,2);addi(140,2,2,16);e(142,'jr',rs1=1)
    elif role=='pins':
        addi(0,2,2,-32);store(2,11,2,4,2);li(6,15,3);addi(8,11,2,4);store(10,1,2,28)
        store(12,0,2,6,2);store(16,15,2,8);store(18,12,2,12);call(20,0x18f88);load(24,1,2,28);addi(26,2,2,32);e(28,'jr',rs1=1)
    elif role=='config':
        addi(0,2,2,-48);store(2,8,2,40);lui(4,8,0x40000);load(8,15,8,72);store(10,1,2,44)
        addi(12,12,0,384);li(16,11,0);e(18,'auipc',rd=10,imm=0x1fff9000);addi(22,10,10,660);e(26,'call_indirect',rd=1,rs1=15)
        load(28,15,8,72);addi(30,12,0,228);li(34,11,0);e(36,'auipc',rd=10,imm=0x1fff9000);addi(40,10,10,1026);e(44,'call_indirect',rd=1,rs1=15)
        lui(46,8,0x40011000);li(50,12,24);lui(52,11,0x1000);addi(54,10,8,-2048);call(58,0x9a24)
        lui(62,11,0x1000);addi(64,12,0,72);addi(68,11,11,-2048);addi(72,10,8,-2048);call(76,0x9a24)
        addi(80,12,0,32);li(84,11,0);mv(86,10,2);call(88,0x8520);li(92,15,1);store(94,15,2,12)
        addi(96,15,0,1029);store(100,15,2,4,2);addi(104,15,3,108);load(108,14,15)
        lui(110,15,0x7271000);addi(114,15,15,-512);branch(118,'beq',14,15,186)
        lui(122,15,0x8954000);addi(126,15,15,1024);branch(130,'beq',14,15,190)
        lui(134,15,0x5b8e000);addi(138,15,15,-2048);branch(142,'bne',14,15,152)
        li(146,15,8);store(148,15,2,0,2);lui(152,8,0x40006000);mv(156,11,2);addi(158,10,8,1024);call(162,0x18ab0)
        load(166,15,8,1044);load(170,1,2,44);imm(172,'ori',15,15,2);store(176,15,8,1044)
        load(180,8,2,40);addi(182,2,2,48);e(184,'jr',rs1=1);li(186,15,10);e(188,'jump',target=pc+148)
        li(190,15,12);e(192,'jump',target=pc+148)
    elif role in ('clock18','clock1c','reset0c','reset10'):
        off={'clock18':24,'clock1c':28,'reset0c':12,'reset10':16}[role]
        e(0,'beqz',rs1=11,target=pc+14);lui(2,14,0x40021000);load(6,15,14,off)
        e(8,'or',rd=10,rs1=10,rs2=15);store(10,10,14,off);e(12,'jr',rs1=1)
        lui(14,15,0x40021000);load(18,14,15,off);imm(20,'xori',10,10,-1)
        e(24,'and',rd=10,rs1=10,rs2=14);store(26,10,15,off);e(28,'jr',rs1=1)
    else:raise RuntimeError('unknown IRQ setup role')
    return s


def body(raw,role,pc,size,count,store_count,digest):
    n=decode(raw,pc);expected=specs(role,pc);check(set(n)==set(expected),'setup complete boundaries '+role)
    for p,f in expected.items():init.g(n,p,'setup '+role+' instruction '+hex(p-pc),**f)
    edges={};calls=[]
    for p,d in n.items():
        if d['op']=='jr':check(d['rs1']==1,'setup ordinary return register');qs=[]
        elif d['op']=='jump':qs=[d['target']]
        elif d['op'] in ('beqz','beq','bne'):qs=[p+d['size'],d['target']]
        else:qs=[p+d['size']]
        check(all(q in n for q in qs),'setup whole local CFG '+role);edges[p]=qs
        if d['op'] in ('jal','call_indirect'):
            check(d['rd']==1,'setup linked calls');calls.append({'pc':hex(p),'target':hex(d['target']) if 'target' in d else 'fresh A5 & ~1','link':hex(p+d['size']),'normal_return_proved':False})
    seen=set();active=set()
    def visit(p):
        check(p not in active,'setup local acyclic graph '+role)
        if p in seen:return
        seen.add(p);active.add(p)
        for q in edges[p]:visit(q)
        active.remove(p)
    visit(pc);check(seen==set(n),'setup full local reachability '+role)
    stores=[d for d in n.values() if d['op']=='store'];writes=sorted({d['rd'] for d in n.values() if d.get('rd',0)})
    check((len(raw),len(n),len(stores),sha256(raw).hexdigest())==(size,count,store_count,digest),'setup complete identity '+role)
    if role not in ('controller','pins','config'):check(writes==[10,14,15] and not calls,'setup helpers no S/GP/SP/RA writes')
    return {'start':hex(pc),'end_exclusive':hex(pc+size),'bytes':size,'sha256':digest,'instructions':list(n.values()),
        'stores':stores,'calls':calls,'encoded_GPR_writes':writes,'conditional_normal_return_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()}}


def derive(app,carriers,header,coverage):
    parent=previous.derive(app,carriers,header,coverage)
    bodies={r:body(take(app,p,size),r,p,size,n,stores,h) for r,p,size,n,stores,h in DETAILS}
    check(sum(b['bytes'] for b in bodies.values())==488 and sum(len(b['instructions']) for b in bodies.values())==168
          and sum(len(b['stores']) for b in bodies.values())==29,'setup seven body census')
    n={r:{d['pc']:d for d in b['instructions']} for r,b in bodies.items()}
    c=n['controller'];cfg=n['config'];pins=n['pins']
    check([x['target'] for x in bodies['controller']['calls']]==['0x19142','0x19124','0x1917e','0x1917e','0x19160','0x19160'],'controller closed leaf call set')
    controller_base=c[0x9a96]['imm'];word=controller_base+c[0x9aae]['imm'];priority=controller_base+c[0x9aa8]['imm']
    check((controller_base,word,priority,c[0x9aac]['imm'])==(0xe000e000,0xe000e104,0xe000e424,16),'nominal index36 address/value join')
    vector_index=parent['raw_vector_reference']['word_index_relative_base'];check(vector_index==36 and priority-(controller_base+0x400)==32+4==vector_index,'vector/priority/bank-mask numeric index join')
    check(c[0x9a4c]['imm']==136 and c[0x9a50]['csr']==c[0x9ac2]['csr']==0x800,'CSR800 live mask source')
    check([x['target'] for x in bodies['config']['calls']]==['fresh A5 & ~1','fresh A5 & ~1','0x9a24','0x9a24','0x8520','0x18ab0'],'full config software calls')
    check(pins[0x9a38]['target']==0x18f88 and cfg[0x12e34]['target']==0x18ab0,'two unexpanded configuration drivers')
    check(cfg[0x12e2a]['imm']+cfg[0x12e38]['imm']==0x40006414 and parent['entry_contract']['active'].startswith('entrySP-32'), 'same ingress peripheral base plus14hex control')
    # Byte guards from whole prior consumer identify exactly the saved ENTRY S3.
    rx=previous.previous
    detail=next(d for d in rx.DETAILS if d[0]=='consumer');r,p,size,count,stores,digest=detail
    consumer=rx.body(take(app,p,size),r,p,size,count,stores,digest)
    cn={d['pc']:d for d in consumer['instructions']}
    check(cn[0x12c58]['imm']==-80 and cn[0x12c5e]['rs2']==19 and cn[0x12c5e]['imm']==60,'consumer saved-entry S3 offset')
    check(pins[0x9a24]['imm']==-32 and pins[0x9a36]['imm']==12 and pins[0x9a36]['rs2']==12,'pin wrapper prior mode word')
    check(cfg[0x12d92]['imm']==-48 and cfg[0x12de2]['imm']==32 and cfg[0x12de6]['imm']==0,'config scratch zero request')
    reset_detail=boot.DETAILS[0];_,rp,rs,rn,rc,rh=reset_detail;reset=boot.body(take(app,rp,rs),'reset',rp,rh,rn,rc)
    bn={d['pc']:d for d in reset['instructions']}
    nominal_sp=(0x186b2+bn[0x186b2]['imm']+bn[0x186b6]['imm'])&0xffffffff
    zero_end=(0x186e2+bn[0x186e2]['imm']+bn[0x186e6]['imm'])&0xffffffff
    check((nominal_sp,zero_end,nominal_sp-20)==(0x20010000,0x2000c958,0x2000ffec),'nominal stack word outside reset zero range')
    csr_sources=[{'pc':hex(p),'csr':hex(bn[p]['csr']),'funct3':bn[p]['funct3'],'source_register':bn[p]['rs1']}
                 for p in (0x186fa,0x18700,0x1870c,0x1871c,0x1872c)]
    check(bn[0x186f8]['imm']==31 and bn[0x186fe]['imm']==3,'reset custom CSR source literals')
    return {'schema':'TSL9-IRQ-setup-stack-sources-static-v1','profile':init.timer.PROFILE,
        'scope':'7 complete APP bodies488B/168instructions/29stores; includes revalidation of two previously expanded RMW leaves',
        'bodies':bodies,'reused_consumer_body_sha256':digest,'reset_CSR_operand_sources':csr_sources,
        'raw_vector_join':parent['raw_vector_reference'],
        'controller_numeric_stores':[
            {'index':45,'priority_address':'0xe000e42d','priority_byte':0,'word_address':'0xe000e104','word_value':'0x2000'},
            {'index':36,'priority_address':'0xe000e424','priority_byte':32,'word_address':'0xe000e104','word_value':'0x10'},
            {'index':39,'priority_address':'0xe000e427','priority_byte':48,'word_address':'0xe000e104','word_value':'0x80'}],
        'controller_contract':{'CSR':'CSR800 clear then set mask88hex; no old word saved or hardware-global-disable meaning assumed',
            'leaf_context':'six direct calls into four complete fresh RMW leaves; onlyA0/A4/A5 writes, noS2/stack stores with required nonalias context',
            'helper_args':['19142(02020006,1)','19124(101d,1)','1917e(02020006,1)','1917e(02020006,0)','19160(101d,1)','19160(101d,0)'],
            'helper_words':['4002101c','40021018','40021010','40021010','4002100c','4002100c'],
            'separate_reads':'each helper reads fresh word, nonzero mode ORmask, zero mode ANDcomplement; not a restored prior hardware state',
            'index_semantics':'priorityoffset and bankbit arithmetic match36; actual controller semantics/routing/context preservation/delivery unproved'},
        'peripheral_config_contract':{'prefix':'fresh fill requests384B queue then228B cache; normal return/requiredS0/frame preservation conditional',
            'pin_requests':['9a24(40010800,1000,18hex)','9a24(40010800,0800,48hex)'],
            'pins_record':'32B nested frame; config atSP+4: SHentryA1,SH0,SW3,SWentryA2; saveRA+28;18f88(A0,SP+4), retention/side effects unknown',
            'local_config':'48B frameI;8520(I,0,32),SW1atI+12,SH0405atI+4; fresh U32[GP+108] selectsSH atI+0',
            'clock_cases':{'96000000':8,'120000000':10,'144000000':12,'other':'no direct SHI+0; zero only with successful fill and preservation'},
            'driver':'18ab0(40006400,I), scalar reply not tested; then fresh40006414 OR2 stored back, with requiredS0/context',
            'actual_setup_success_or_stack_config_retention_proved':False},
        'extended_ID_slot':{'definition':'actual IRQentry SP=E; H=E-32; R=H+12=E-20; extended reader has no direct R0..3 store',
            'producer_saved_words_relative_E':[-44,-40,-36],'producer_saves_overlap_ID_word':False,
            'candidate_prior_writes':[
                {'source':'completed consumer with same entrySP=E','pc':'0x12c5e','equation':'(E-80)+60=E-20','value':'ENTRY S3, before consumer sets its ownS3=40000; actual value/lastwriter unknown'},
                {'source':'completed9a24 wrapper with entrySP=E','pc':'0x9a36','equation':'(E-32)+12=E-20','value':'entryA2 word; this init requests18hex then48hex, subject to18f88/frame preservation'},
                {'source':'completed12d92 config with entrySP=E','equation':'(E-48)+28=E-20','value':'zero from successful local fill32 only if laterdriver/otherwriters preserveI+28'},
                {'source':'prior standard IRQ at same actualSP=E','pc':'0x18d90','equation':'R=E-20','value':'standard IDword; laterextended does not itself replace it'}],
            'candidate_identity_only':'address overlap under SAME actualSP, completed priorcall/required preservation and no intervening writer; not a last-writer/runtime/context proof',
            'reset_example':{'nominal_E':hex(nominal_sp),'R0':hex(nominal_sp-20),'reset_zero_end':hex(zero_end),'R0_in_reset_zero_interval':False},
            'hardware_push_switch_clear_or_prior_RAM_content_proved':False},
        'premises':['matching original bytes/conditional ISA, normal required calls and valid nonwrapping accesses',
            'MMIO addresses do not adversely alias frames/config; no unaccounted IRQ/reentry/other writer',
            'CSRbc0=31/804=3/resetvector operands do not identify actual hardware frame or later retention',
            'sameSP witness equations do not assert actual interrupt timing or runtime memory content'],
        'remaining_boundaries':['actual hardware/IRQ frame and linkage of restore entry8448','drivers18f88/18ab0 config writes/retention',
            'resident fill/copy binding and actual last writer of E-20','concurrency/CSR/MMIO semantics and lifetime'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(app):
    for old in range(256):
        check(((old&~0x88)|0x88)==old|0x88,'CSR mask algebra is set not prior-state restore')
    for index,bit,priority_offset in ((45,13,1069),(36,4,1060),(39,7,1063)):
        check(32+bit==index and priority_offset-0x400==index,'controller common numeric index')
    for i in range(512):
        E=0x2000d000+16*i;slot=E-20
        check((E-80)+60==slot and (E-32)+12==slot and (E-48)+28==slot,'three prior-stack writer equalities')
        for offset in (-44,-40,-36):check(offset+4<=-20 or -16<=offset,'producer saved words disjoint from IDslot')
    probes=(0,1,95999999,96000000,96000001,119999999,120000000,120000001,143999999,144000000,144000001,0xffffffff)
    selected={x:{96000000:8,120000000:10,144000000:12}.get(x,0) for x in probes}
    check(sorted(v for v in selected.values() if v)==[8,10,12],'clock boundary partition with conditional successful zero-fill')
    roles={r:(p,size,count,stores,h) for r,p,size,count,stores,h in DETAILS}
    cases=(('controller',10,1<<20),('controller',14,1<<12),('controller',98,1<<20),('controller',102,1<<7),
        ('controller',106,4),('controller',128,1<<12),('pins',18,4),('pins',20,1<<21),
        ('config',64,1<<20),('config',80,1<<20),('config',100,1<<20),('config',118,0x1000),
        ('config',166,1<<20),('config',172,1<<20),('clock18',10,4),('clock1c',6,4),('reset0c',20,1<<20),('reset10',26,4))
    for role,off,flip in cases:
        pc,size,count,stores,digest=roles[role];raw=bytearray(take(app,pc,size));w=decode(raw,pc)[pc+off]['size']
        raw[off:off+w]=(int.from_bytes(raw[off:off+w],'little')^flip).to_bytes(w,'little')
        try:body(raw,role,pc,size,count,stores,digest)
        except RuntimeError as e:check(str(e)=='setup '+role+' instruction '+hex(off),'unexpected setup mutation guard '+str(e))
        else:raise RuntimeError('setup mutation escaped')
    print('PASS: 256 CSR algebra cases; 3 controller index joins; 512 same-SP address witnesses; 12 clock boundary probes; 18 specified raw mutations')


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
    else:check(OUT.read_bytes()==output,'IRQ setup stack source exact ledger replay')
    print('PASS: 7 complete APP bodies488B/168instructions/29stores; nominal index36 setup and conditional extended-ID prior-write joins')
    print('PASS: exact ledger bytes; NO target execution; actual IRQframe/context, lastwriter and provider/driver retention UNPROVED')


if __name__=='__main__':main()
