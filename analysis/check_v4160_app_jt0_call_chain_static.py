"""Original APP reset -> resident handoff -> main -> fresh JT0 loop.

Complete local operands, conditional graphs and bounded host algebra only.
No target ISA/CSR, boot/copy state, scheduler, callee or MMIO execution/model.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_dispatch_origin_mask_static as previous
from check_v4160_builtin_record_handlers_static import decode as base_decode

init,sparse,ROOT,MASK=previous.init,previous.sparse,previous.ROOT,previous.MASK
check=init.check
OUT=Path(__file__).with_name('v4160-app-jt0-call-chain-static.json')
DETAILS=(('reset',0x186aa,138,37,2,'9507502c874a03e2c64a28b186a1f56aba9e85c9989dbf0cc053dabc4045bb4d'),
 ('main',0x9008,18,8,1,'87dd87b4471d5281a6185185b66e454ac79136553f837e3c9a3c2abdfb85ead5'),
 ('init_sequence',0x9250,64,19,1,'9c9a241ad1ffb34eab4267c3368c9b5cbd459e1d9f111621eb4716087f8cf60b'),
 ('loop',0x8180,42,15,5,'c440bafcc9fdbe370d24fbcd3bd0c67e8162ceaa776a64ea6f34f1d509b6f72f'),
 ('flag_service',0x17002,62,21,5,'dd6b0fa91982cf653657b71e2d2bfaf2d6349ccc12f2b31561483e40572b0c69'))
INIT_CALLS=((4,0x18834),(8,0x9a42),(12,0x1973c),(16,0x9f4c),(20,0x131c2),(24,0x8e88),
 (26,0x9b4e),(30,0x9958),(32,0x9f12),(36,0x12d92),(40,0x14c8a),(44,0x154a6),(48,0x17040),(52,0x173a2))


def take(app,pc,size):
    check(0x8000<=pc and pc+size<=0x8000+len(app),'APP source range')
    return app[pc-0x8000:pc-0x8000+size]


def decode(raw,pc):
    n={};off=0
    while off<len(raw):
        h=int.from_bytes(raw[off:off+2],'little');size=2 if h&3!=3 else 4
        check(off+size<=len(raw),'APP chain complete instruction')
        chunk=raw[off:off+size];w=int.from_bytes(chunk,'little');p=pc+off
        if size==4 and w&127==0x73:
            d=dict(pc=p,bytes=chunk.hex(),size=4,op='csr',rd=w>>7&31,rs1=w>>15&31,funct3=w>>12&7,csr=w>>20)
        elif size==4 and w&0x707f==0x6013:
            d=dict(pc=p,bytes=chunk.hex(),size=4,op='ori',rd=w>>7&31,rs1=w>>15&31,imm=init.sx(w>>20,12))
        else:d=base_decode(chunk,p)[p]
        n[p]=d;off+=size
    return n


def expected(role,pc):
    s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def load(o,r,b,v=0,w=4):e(o,'load',rd=r,rs1=b,imm=v,width=w)
    def store(o,r,b,v=0,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    def addi(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    def call(o,t):e(o,'jal',rd=1,target=t)
    def constant(o,r,upper,low):e(o,'auipc',rd=r,imm=upper);addi(o+4,r,r,low)
    if role=='reset':
        constant(0,3,0x1ffec000,-1706);constant(8,2,0x1fff8000,-1714);constant(16,10,0x2000,1190)
        addi(24,11,3,0);addi(28,12,3,128);e(32,'bgeu',rs1=11,rs2=12,target=pc+52)
        load(36,5,10);store(40,5,11);addi(44,10,10,4);addi(46,11,11,4)
        e(48,'bltu',rs1=11,rs2=12,target=pc+36);addi(52,10,3,128)
        constant(56,11,0x1fff4000,630);e(64,'bgeu',rs1=10,rs2=11,target=pc+78)
        store(68,0,10);addi(72,10,10,4);e(74,'bltu',rs1=10,rs2=11,target=pc+68)
        li(78,5,31);e(80,'csr',rd=0,rs1=5,funct3=1,csr=0xbc0)
        li(84,5,3);e(86,'csr',rd=0,rs1=5,funct3=1,csr=0x804)
        e(90,'lui',rd=5,imm=0x2000);addi(94,5,5,-1912);e(98,'csr',rd=0,rs1=5,funct3=2,csr=0x300)
        constant(102,5,0xffff0000,-1752);e(110,'ori',rd=5,rs1=5,imm=3)
        e(114,'csr',rd=0,rs1=5,funct3=1,csr=0x305);call(118,0x1874a)
        constant(122,5,0xffff1000,-1820);e(130,'csr',rd=0,rs1=5,funct3=1,csr=0x341)
        e(134,'jal',rd=0,target=0x40000)
    elif role=='main':
        addi(0,2,2,-16);store(2,1,2,12);call(4,0x9250);call(6,0x8180)
        load(10,1,2,12);li(12,10,0);addi(14,2,2,16);e(16,'jr',rs1=1)
    elif role=='init_sequence':
        addi(0,2,2,-16);store(2,1,2,12)
        for o,t in INIT_CALLS:call(o,t)
        load(56,1,2,12);addi(58,2,2,16);e(60,'jal',rd=0,target=0x17bf6)
    elif role=='loop':
        addi(0,2,2,-16);store(2,8,2,8);e(4,'lui',rd=8,imm=0xb000);store(6,9,2,4)
        store(8,18,2);store(10,1,2,12);e(12,'lui',rd=18,imm=0x20000000)
        e(16,'lui',rd=9,imm=0x40003000);addi(20,8,8,-1366);load(24,15,18)
        e(28,'call_indirect',rd=1,rs1=15);call(30,0x17002);call(34,0x12c58)
        store(38,8,9);e(40,'jump',target=pc+24)
    elif role=='flag_service':
        addi(0,2,2,-16);load(2,15,3,360,1);store(6,1,2,12)
        for off,mask,value,tail in ((8,1,1,30),(34,2,2,56)):
            e(off,'andi',rd=14,rs1=15,imm=mask);e(off+4,'beqz',rs1=14,target=pc+tail)
            e(off+6,'andi',rd=15,rs1=15,imm=-1-mask);li(off+8,10,value)
            store(off+10,15,3,360,1);call(off+14,0x16b0a);store(off+18,0,3,360+value,1)
        load(30,15,3,360,1);load(56,1,2,12);addi(58,2,2,16);e(60,'jr',rs1=1)
    else:raise RuntimeError('unknown APP chain role')
    return s


def body(raw,role,pc,digest,count,store_count):
    n=decode(raw,pc);s=expected(role,pc)
    check(set(n)==set(s),'APP chain complete boundaries '+role)
    for p,f in s.items():init.g(n,p,'APP chain '+role+' instruction '+hex(p-pc),**f)
    edges={};external=[];calls=[]
    for p,d in n.items():
        if d['op']=='jr':qs=[]
        elif d['op']=='jump' or (d['op']=='jal' and d['rd']==0):qs=[d['target']]
        elif d['op'] in ('beqz','bnez','beq','bne','bltu','bgeu'):qs=[p+d['size'],d['target']]
        else:qs=[p+d['size']]
        for q in qs:
            if q not in n:
                check((role,p,q) in (('reset',0x18730,0x40000),('init_sequence',0x928c,0x17bf6)),
                      'APP chain explicit external edge')
                external.append({'pc':hex(p),'target':hex(q),'link_written':False})
        edges[p]=qs
        if d['op']=='call_indirect' or (d['op']=='jal' and d['rd']==1):
            calls.append({'pc':hex(p),'target':hex(d['target']) if 'target' in d else 'fresh raw A5 & ~1',
                'link':hex(p+d['size']),'normal_return_proved':False})
    seen=set();back=[];active=set()
    def visit(p):
        if p not in n or p in seen:return
        seen.add(p);active.add(p)
        for q in edges[p]:
            if q in active:back.append([hex(p),hex(q)])
            else:visit(q)
        active.remove(p)
    visit(pc);check(seen==set(n),'APP chain full CFG reachability '+role)
    stores=[d for d in n.values() if d['op']=='store']
    check(len(n)==count and len(stores)==store_count and sha256(raw).hexdigest()==digest,'APP chain complete identity '+role)
    if role=='loop':
        check(back==[['0x81a8','0x8198']] and not any(d['op']=='jr' for d in n.values()),'APP loop no local RET and exact backedge')
        check(not any(d.get('rd')==10 for d in n.values()),'APP loop no explicit A0 setup or scalar result test')
    return {'start':hex(pc),'end_exclusive':hex(pc+len(raw)),'bytes':len(raw),'sha256':digest,
        'instructions':list(n.values()),'stores':stores,'calls':calls,'external_tail_edges':external,
        'conditional_normal_return_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},'DFS_back_edges':back,
        'encoded_GPR_writes':sorted({d['rd'] for d in n.values() if d.get('rd',0)})}


def derive(app,carriers,header,coverage):
    old=previous.derive(app,carriers,header,coverage)
    bodies={role:body(take(app,pc,size),role,pc,digest,count,stores) for role,pc,size,count,stores,digest in DETAILS}
    entry=decode(take(app,0x8000,4),0x8000);init.g(entry,0x8000,'APP image entry jump',op='jal',rd=0,target=0x186aa)
    reset=bodies['reset']['instructions'];n={x['pc']:x for x in reset}
    values={}
    for name,p,r in (('GP',0x186aa,3),('SP',0x186b2,2),('initialized_data_source',0x186ba,10),
                     ('zero_end',0x186e2,11),('vector_base_before_OR3',0x18710,5),('MEPC_operand',0x18724,5)):
        values[name]=(p+n[p]['imm']+n[p+4]['imm'])&MASK
    check(values=={'GP':0x20004000,'SP':0x20010000,'initialized_data_source':0x1ab60,
        'zero_end':0x2000c958,'vector_base_before_OR3':0x8038,'MEPC_operand':0x9008},'APP reset constant operands')
    data_source=take(app,values['initialized_data_source'],128)
    copy_range=(values['GP'],values['GP']+128);zero_range=(values['GP']+128,values['zero_end'])
    check(all(0x20000004<=a<b<=MASK for a,b in (copy_range,zero_range)),'APP listed init destinations disjoint from JT0')
    loop=bodies['loop'];check(loop['calls'][0]['pc']=='0x819c','APP fresh JT0 call position')
    joins=[]
    for p in old['profiles']:
        check(p['initializer']['JT_words'][0]=={'pc':hex(int(p['initializer']['start'],16)+16),
            'address':'0x20000000','value':'0x200007d0'},'APP/candidate initial JT0 slot join')
        check(p['dispatcher_join']['entry']=='0x200007d0' and p['startup']['MRET_external_exit'],
              'APP/candidate dispatcher and external MRET join')
        joins.append({'label':p['label'],'resident_startup':p['startup']['start'],
            'resident_MRET_pc':p['startup']['MRET_external_exit'],'initial_JT0_writer':p['initializer']['JT_words'][0],
            'candidate_dispatcher':'0x200007d0','APP_JT0_load_pc':'0x8198','APP_JT0_call_pc':'0x819c',
            'APP_continuation_after_dispatch':'0x819e','installed_binding_or_MEPC_retention_proved':False})
    check(sum(b['bytes'] for b in bodies.values())==324 and sum(len(b['instructions']) for b in bodies.values())==100,
          'APP chain body byte/instruction census')
    check(sum(len(b['stores']) for b in bodies.values())==14,'APP chain store census')
    return {'schema':'TSL9-APP-JT0-call-chain-static-v1','profile':init.timer.PROFILE,
        'scope':'5 complete original APP bodies324B/100instructions plus4B image-entry transfer; candidate joins revalidated',
        'APP_entry_transfer':list(entry.values()),'bodies':bodies,'reset_constant_operands':{k:hex(v) for k,v in values.items()},
        'reset_data_source':{'start':'0x1ab60','end_exclusive':'0x1abe0','bytes':128,'sha256':sha256(data_source).hexdigest()},
        'reset_destination_intervals':{'initialized_data':[hex(x) for x in copy_range],'zero':[hex(x) for x in zero_range]},
        'reset_CSR_operands':{'bc0_write_value':'0x1f','804_write_value':'0x3','mstatus_set_bits':'0x1888',
            'mtvec_write_operand':'0x803b','mepc_write_operand':'0x9008','physical_CSR_effects_or_return_proved':False},
        'candidate_joins':joins,
        'loop_contract':{'first_load':'U32[then-live S2]; nominal S2=20000000 only with preservation',
            'target':'fresh raw pointer & ~1; no local null guard','scalar_reply_tested':False,
            'explicit_arguments_setup':False,'next_reads_same_word_value_proved':False,
            'normal_order':['fresh load8198','indirect call819c','direct17002','direct12c58','SW S0 to then-live S1','back8198'],
            'nominal_store_address':'0x40003000','nominal_store_value':'0xaaaa','physical_MMIO_effect_proved':False,
            'ordinary_local_return_path':False,'local_loop_edges_reach_main_suffix_or_config':False},
        'init_sequence':'14 calls without local argument setup/reply tests; restore RA/SP then tail17bf6; completion unproved',
        'flag_service':'fresh U8[GP+360] bit0 then fresh bit1; clear each bit before16b0a(1/2), clear GP+361/362 after normal return',
        'writer_scope':'listed direct reset copy/zero destinations and local stores only; no transitive JT0 retention proof',
        'premises':['original bytes and supported ISA; valid code/stack/data accesses',
            'needed GP/S/SP/frame preservation and normal callee/tail return where described',
            'candidate resident actually installed, initialized, code/JT0/MEPC retained for conditional roundtrip',
            'no adverse alias, reentry, unknown writer/interrupt/reset or unproved MMIO effects'],
        'remaining_boundaries':['1874a hardware initializer effects','17bf6 tail and14 init callees',
            'actual JT0/MEPC/context retention and installed provider','16b0a and12c58 descendants/ownership'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(app):
    by_role={d[0]:d for d in DETAILS}
    cases=(('reset',126,1<<20),('reset',130,1<<20),('reset',134,1<<21),('reset',114,1<<20),
           ('main',6,1<<21),('init_sequence',60,1<<21),('loop',12,1<<12),('loop',24,1<<20),
           ('loop',28,0x80),('loop',38,4),('loop',40,4),('flag_service',2,1<<20),
           ('flag_service',14,4),('flag_service',30,1<<20),('flag_service',44,1<<20))
    for role,off,flip in cases:
        _,pc,size,count,stores,digest=by_role[role];raw=bytearray(take(app,pc,size));n=decode(raw,pc);width=n[pc+off]['size']
        raw[off:off+width]=(int.from_bytes(raw[off:off+width],'little')^flip).to_bytes(width,'little')
        try:body(raw,role,pc,digest,count,stores)
        except RuntimeError as e:check(str(e)=='APP chain '+role+' instruction '+hex(off),'unexpected APP chain mutation guard '+str(e))
        else:raise RuntimeError('APP chain mutation escaped')
    for first in range(256):
        for second in range(256):
            check((first&~1)&255==first&254 and (second&~2)&255==second&253,'independent flag byte clear')
    for value in range(65536):check((value&~1)==((value|1)&~1),'JALR lowbit normalization')
    check(0xb000-1366==0xaaaa and 0x20004000+360==0x20004168,'nominal loop store/GP flag addresses')
    check((0x20004000+128-0x20004000)//4==32 and (0x2000c958-0x20004080)//4==8758,'reset interval word algebra')
    print('PASS: 65536 independent flag-read pairs; 65536 pointer low-bit cases; 15 specified raw mutations')


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true',help='Create ledger exclusively');o=p.parse_args()
    app=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(app)==76800 and sha256(app).hexdigest()==init.binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK header identity')
    carriers=[]
    for label,folder,tail,size,digest in init.binding.PROFILES:
        raw=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(raw)==size and sha256(raw).hexdigest()==digest,'candidate identity '+label);carriers.append(raw)
    hex_sources=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
    coverage=sparse.derive(app,carriers,header,hex_sources,sparse.parser())
    sources,vectors=init.timer.source_contract();ledger=derive(app,carriers,header,coverage)
    ledger['sources'],ledger['official_Xwchc_vectors']=sources,vectors
    tests(app);output=(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'APP JT0 chain exact ledger replay')
    print('PASS: 5 complete APP bodies324B/100instructions/14stores plus image-entry4B; CSR operands and dual candidate joins')
    print('PASS: exact ledger replay; boot/CSR/context/JT0 retention/installed binding UNPROVED; NO target execution')


if __name__=='__main__':main()
