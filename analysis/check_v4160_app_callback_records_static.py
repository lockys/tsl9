"""APP 15-record cancel/register services and two complete callbacks.

Original bytes, conditional operands/CFG and host integer equations only.
No target ISA, callback table, provider, timer, payload or MMIO execution/model.
"""
import argparse
import json
import re
from hashlib import sha256
from pathlib import Path
import check_v4160_init_tail_hardware_static as previous

init,sparse,ROOT,MASK=previous.init,previous.sparse,previous.ROOT,previous.MASK
check=init.check
OUT=Path(__file__).with_name('v4160-app-callback-records-static.json')
DETAILS=(('cancel',0x90b0,116,45,5,'6ae3c32faae25ccd27fea46de4a04b6246489daafb5f1fa0d9ede512e65f2b31'),
 ('register',0x9124,300,115,14,'45dd01a76fedc4bd8d01fdb7ff005f410166a68f171d52420d19da2cbba2e992'),
 ('retry_callback',0x176a0,88,30,3,'8411c1a832677e340569a880397508fbe62ff7016d7d17b52856dfe3b856cd6d'),
 ('packet_callback',0x178f8,80,29,4,'ee37bb82ebc75f0273397af864811a63fc953c51f06cc26d57a76156e2e78077'))


def decode(raw,pc):
    n={};off=0
    while off<len(raw):
        h=int.from_bytes(raw[off:off+2],'little');size=2 if h&3!=3 else 4
        check(off+size<=len(raw),'APP record complete instruction')
        chunk=raw[off:off+size];w=int.from_bytes(chunk,'little');p=pc+off
        if size==4 and w&0xfe00707f==0x02005033:
            d=dict(pc=p,size=4,bytes=chunk.hex(),op='divu',rd=w>>7&31,rs1=w>>15&31,rs2=w>>20&31)
        elif size==4 and w&0x707f==0x3013:
            d=dict(pc=p,size=4,bytes=chunk.hex(),op='sltiu',rd=w>>7&31,rs1=w>>15&31,imm=init.sx(w>>20,12))
        else:d=previous.previous.decode(chunk,p)[p]
        n[p]=d;off+=size
    return n


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
    def indirect(o):e(o,'call_indirect',rd=1,rs1=15)
    def call(o,t):e(o,'jal',rd=1,target=t)
    def constant(o,r,upper,low):e(o,'auipc',rd=r,imm=upper);addi(o+4,r,r,low)
    def restore(rows):
        for o,r,v in rows:load(o,r,2,v)
    if role=='cancel':
        addi(0,2,2,-16);constant(2,15,0x20003000,-682)
        for o,r,v in ((10,8,8),(12,9,4),(14,1,12)):store(o,r,2,v)
        li(16,8,0);mv(18,9,15);li(20,14,15);load(22,13,15,4);branch(24,'bne',13,10,96)
        li(28,15,12);binary(30,'mul',15,8,15);binary(34,'add',15,15,9);load(36,10,15,8)
        bz(38,'beqz',10,48);lui(40,15,0x40000);load(44,15,15,104);indirect(46)
        li(48,15,12);binary(50,'mul',15,8,15);li(54,11,1);binary(56,'sll',11,11,8)
        restore(((60,8,8),(62,1,12)));imm(64,'slli',11,11,16);load(66,10,3,166,1)
        imm(70,'srli',11,11,16);binary(72,'add',9,9,15);lui(74,15,0x40000)
        store(78,0,9,4);store(82,0,9,8);load(86,6,15,92);load(90,9,2,4);addi(92,2,2,16);e(94,'jr',rs1=6)
        addi(96,8,8,1);addi(98,15,15,12);branch(100,'bne',8,14,22)
        restore(((104,1,12),(106,8,8),(108,9,4)));li(110,10,1);addi(112,2,2,16);e(114,'jr',rs1=1)
    elif role=='register':
        addi(0,2,2,-32)
        for o,r,v in ((2,18,16),(4,1,28),(6,8,24),(8,9,20),(10,19,12),(12,20,8)):store(o,r,2,v)
        constant(14,18,0x20003000,-810);bz(22,'bnez',12,100);mv(24,15,18);li(26,14,0);li(28,16,15)
        load(30,17,15,4);branch(34,'bne',17,0,92);li(38,15,12);binary(40,'mul',15,14,15)
        restore(((44,8,24),(48,1,28),(50,9,20),(52,19,12),(54,20,8)));li(46,11,1)
        binary(56,'sll',11,11,14);imm(60,'slli',11,11,16);imm(62,'srli',11,11,16)
        binary(64,'add',15,15,18);store(66,10,15,4);store(68,0,15,0,1);store(72,13,15,8)
        lui(74,15,0x40000);load(78,18,2,16);load(80,6,15,80);load(84,10,3,166,1)
        addi(88,2,2,32);e(90,'jr',rs1=6);addi(92,14,14,1);addi(94,15,15,12);branch(96,'bne',14,16,30)
        constant(100,15,0x20003000,-896)
        for o,r,a in ((108,20,13),(110,19,12),(112,8,11),(114,14,15)):mv(o,r,a)
        li(116,9,0);li(118,13,15);load(120,12,14,4);branch(122,'bne',12,10,218)
        li(126,15,12);binary(128,'mul',15,9,15);binary(132,'add',15,15,18);load(134,10,15,8)
        bz(136,'beqz',10,146);lui(138,15,0x40000);load(142,15,15,104);indirect(144)
        li(146,15,12);binary(148,'mul',15,9,15);li(152,11,1);load(154,10,3,166,1)
        binary(158,'sll',11,11,9);binary(162,'add',15,15,18);store(164,8,15,0,1);store(168,20,15,8)
        addi(172,15,0,1000);binary(176,'mul',12,19,15);imm(180,'slli',11,11,16)
        addi(182,15,0,625);imm(186,'srli',11,11,16);binary(188,'divu',12,12,15)
        lui(192,15,0x40000);bz(196,'beqz',8,264)
        restore(((198,8,24),(200,1,28),(202,9,20),(204,18,16),(206,19,12),(208,20,8)))
        load(210,6,15,556);addi(214,2,2,32);e(216,'jr',rs1=6)
        addi(218,9,9,1);addi(220,14,14,12);branch(222,'bne',9,13,120)
        li(226,14,0);li(228,13,15);load(230,12,15,4);bz(232,'bnez',12,288)
        li(234,15,12);binary(236,'mul',15,14,15);li(240,11,1);binary(242,'sll',11,11,14)
        binary(246,'add',15,15,18);store(248,10,15,4);store(250,8,15,0,1);store(254,20,15,8)
        load(258,10,3,166,1);jump(262,172);load(264,15,15,88);indirect(266)
        imm(268,'sltiu',10,10,1)
        restore(((272,1,28),(274,8,24),(276,9,20),(278,18,16),(280,19,12),(282,20,8)))
        addi(284,2,2,32);e(286,'jr',rs1=1);addi(288,14,14,1);addi(290,15,15,12)
        branch(292,'bne',14,13,230);li(296,10,1);jump(298,272)
    elif role=='retry_callback':
        lui(0,15,0x6000);addi(2,2,2,-32);addi(4,15,15,693);lui(8,10,0xb000);store(10,15,2,12,2)
        li(14,14,2);constant(16,15,0,-74);addi(24,13,2,12);li(26,12,15);li(28,11,21)
        addi(30,10,10,1378);store(34,1,2,28);call(36,0x1753a);bz(40,'bnez',10,82)
        load(42,15,3,377,1);addi(46,15,15,1);imm(48,'andi',15,15,255);store(52,15,3,377,1)
        li(56,14,4);branch(58,'bltu',14,15,82);li(62,13,0);addi(64,12,0,500)
        li(68,11,0);constant(70,10,0,-70);call(78,0x9124);load(82,1,2,28);addi(84,2,2,32);e(86,'jr',rs1=1)
    elif role=='packet_callback':
        lui(0,15,0x40000);load(4,15,15,72);addi(6,2,2,-32);store(8,1,2,28)
        addi(10,10,2,8);li(12,12,7);li(14,11,0);indirect(16);load(18,15,2,8)
        lui(20,14,0xff001000);addi(24,14,14,-1024);imm(28,'andi',15,15,1023)
        binary(32,'or',15,15,14);store(34,15,2,8);load(36,15,2,12,2);lui(40,14,0xffffe000)
        addi(42,10,2,8);binary(44,'and',15,15,14);lui(46,14,0x2000);addi(48,14,14,-256)
        binary(52,'or',15,15,14);store(54,15,2,12,2);load(58,15,2,14,1)
        imm(62,'ori',15,15,-128);store(66,15,2,14,1);call(70,0x1787c)
        load(74,1,2,28);addi(76,2,2,32);e(78,'jr',rs1=1)
    else:raise RuntimeError('unknown APP record role')
    return s


def body(raw,role,pc,size,count,store_count,digest):
    n=decode(raw,pc);expected=specs(role,pc)
    check(set(n)==set(expected),'APP record complete boundaries '+role)
    for p,f in expected.items():init.g(n,p,'APP record '+role+' instruction '+hex(p-pc),**f)
    edges={};calls=[];tails=[]
    for p,d in n.items():
        if d['op']=='jr':
            qs=[]
            if d['rs1']!=1:
                check(d['rs1']==6 and (role,p) in (('cancel',0x910e),('register',0x917e),('register',0x91fc)),
                      'APP record indirect tail exit')
                tails.append({'pc':hex(p),'register':'T1','link_written':False,'target':'fresh slot word & ~1'})
        elif d['op']=='jump':qs=[d['target']]
        elif d['op'] in ('beq','bne','beqz','bnez','bltu','bgeu'):qs=[p+d['size'],d['target']]
        else:qs=[p+d['size']]
        check(all(q in n for q in qs),'APP record bounded graph')
        edges[p]=qs
        if d['op']=='call_indirect' or d['op']=='jal':calls.append({'pc':hex(p),'link':hex(p+d['size']),
            'target':hex(d['target']) if 'target' in d else 'fresh raw A5 & ~1','normal_return_proved':False})
    seen=set();active=set();back=[]
    def visit(p):
        if p in seen:return
        seen.add(p);active.add(p)
        for q in edges[p]:
            if q in active:back.append([hex(p),hex(q)])
            else:visit(q)
        active.remove(p)
    visit(pc);check(seen==set(n),'APP record full CFG reachability '+role)
    stores=[d for d in n.values() if d['op']=='store']
    check(len(raw)==size and len(n)==count and len(stores)==store_count and sha256(raw).hexdigest()==digest,'APP record complete identity '+role)
    check(len(back)=={'cancel':1,'register':3,'retry_callback':0,'packet_callback':0}[role],'APP record loop census')
    return {'start':hex(pc),'end_exclusive':hex(pc+size),'bytes':size,'sha256':digest,'instructions':list(n.values()),
        'stores':stores,'calls':calls,'indirect_tail_exits':tails,'DFS_back_edges':back,
        'conditional_normal_return_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},
        'encoded_GPR_writes':sorted({d['rd'] for d in n.values() if d.get('rd',0)})}


def delay_ticks(value):return ((value*1000)&MASK)//625


def derive(app,carriers,header,coverage):
    parent=previous.derive(app,carriers,header,coverage)
    bodies={r:body(previous.previous.take(app,p,size),r,p,size,n,stores,h) for r,p,size,n,stores,h in DETAILS}
    bases=[]
    for role,offset,reg in (('cancel',2,15),('register',14,18),('register',100,15)):
        n={d['pc']:d for d in bodies[role]['instructions']};p=int(bodies[role]['start'],16)+offset
        bases.append((p+n[p]['imm']+n[p+4]['imm'])&MASK)
    check(bases==[0x2000be08]*3,'APP 15-record table base identity')
    check(parent['late_constants']['cancel_callback']==bodies['packet_callback']['start'] and
          parent['late_constants']['deferred_callback']==bodies['retry_callback']['start'],'init-tail callback literal joins')
    check(any(c['target']=='0x90b0' for c in parent['bodies']['late_init']['calls']) and
          any(c['target']=='0x9124' for c in parent['bodies']['tail_return']['calls']),'late-init cancel/register call joins')
    aliases={}
    for name,index in ((b'tmos_set_event',7),(b'tmos_start_task',9),(b'tmos_stop_task',10),
                       (b'tmos_msg_deallocate',13),(b'tmos_start_reload_task',126)):
        check(re.search(rb'^\s*#define\s+'+name+rb'\s+[^\r\n]*BLE_LIB_JT\(\s*'+str(index).encode()+rb'\s*\)',header,re.M) is not None,
              'APP record SDK alias '+name.decode())
        aliases[name.decode()]={'slot':hex(0x40034+4*index),'candidate_targets':[hex(init.binding.word(d,0x40034+4*index)&~1) for d in carriers],
            'installed_binding_proved':False}
    check(sum(b['bytes'] for b in bodies.values())==584 and sum(len(b['instructions']) for b in bodies.values())==219 and
          sum(len(b['stores']) for b in bodies.values())==26,'APP record body census')
    return {'schema':'TSL9-APP-callback-records-static-v1','profile':init.timer.PROFILE,
        'scope':'4 complete APP bodies584B/219instructions/26stores; init-tail/provider aliases revalidated',
        'bodies':bodies,'SDK_aliases':aliases,
        'table':{'base':'0x2000be08','end_exclusive':'0x2000bebc','records':15,'stride':12,
            'fields':{'0':'mode byte; other3bytes not initialized by these field stores','4':'full callback/key word, zero used as free','8':'saved entry A3 word, optionally passed to deallocate'},
            'resident16_record_arena_same_object_proved':False},
        'cancel_contract':{'lookup':'first full U32[R+4]==entry A0; no local null callback guard',
            'miss_reply':1,'hit_order':['read R+8','if nonzero call fresh40068(A0=old word), reply not tested',
                'fresh task U8[GP+166], form low16(1<<i)','clear R+4 then R+8, R+0 retained','restore frame; tail fresh4005c(task,mask)'],
            'hit_reply':'raw provider tail reply; no wrapper normalization','local_wrapper_rollback_on_provider_failure':False},
        'register_contract':{'entry_A2_zero':'scan first free R+4; on hit write callback, mode0, entry A3 then tail fresh40050(task,mask); no scalar conversion; if full falls into general path',
            'general_existing':'first matching full callback; optional fresh40068(old R+8) before updating mode low8(entry A1) then R+8=entry A3; callback word unchanged',
            'general_new':'after no match rescan first free; write callback then mode byte then R+8; if none reply1',
            'task':'fresh U8[GP+166]; not the init-tail GP+379 task byte','event':'low16(1<<index), index0..14 under scan/context premises',
            'duration':'uint32(entry A2*1000) unsigned-div625; multiplication wraps before division',
            'full_entry_A1_nonzero':'restore frame then tail fresh4022c(task,mask,duration); raw reply',
            'full_entry_A1_zero':'call fresh40058(task,mask,duration); return1 iff full scalar reply==0, else0',
            'mode_byte_zero_implies_oneshot_path':False,'writes_precede_provider_result':True,'atomic_publication_or_rollback_proved':False},
        'concrete_init_request':{'caller':'0x17bb0','entry_args':['0x176a0',0,100,0],
            'if_record_matched_or_free_slot_selected':'fresh40058(fresh U8[GP+166],onehot,160); wrapper A0=int(provider A0==0); no time units or success proof',
            'outer_tail_uses_reply':False},
        'retry_callback':{'transmission_call':{'pc':'0x176c4','target':'0x1753a','args':['0xb562',21,15,'SP+12',2,'0x17666'],
            'stack_payload':'SH62b5 atSP+12; initialized2bytes b5,62','retention_or_callback_delivery_proved':False},
            'retry_predicate':'only scalar reply0: u=(fresh U8[GP+377]+1)&255, store u; requeue iff u<=4',
            'qualifying_old_byte_values':[0,1,2,3,255],
            'requeue_args':['0x176a0',0,500,0],'conditional_requeue_ticks':800,
            'unconditional_max4_retries_proved':False,'uniform_scalar_return_proved':False},
        'packet_callback':{'fill_request':'fresh40048(SP+8,0,7); no local null guard',
            'fresh_post_fill_fields':['SW((U32[SP+8]&3ff)|ff000c00)','SH((U16[SP+12]&e000)|1f00)','SB(U8[SP+14]|80)'],
            'delivery_call':'1787c(SP+8), 7-byte local payload span; scalar not tested',
            'payload_pointer_retention_proved':False,'zero_fill_completed_unconditionally_proved':False},
        'premises':['supported ISA/RV32M, original code and valid stack/table/payload accesses',
            'callee normal return and needed GP/S/SP/frame preservation; table/frame/data nonalias',
            'no unaccounted writer/reentry/IRQ/MMIO effects; fresh loads remain distinct',
            'provider API name/candidate target is not installed identity, success or ownership evidence'],
        'remaining_boundaries':['176f8 event consumer and callbacks17666','1753a/1787c payload ownership/copy/retention',
            'actual GP+166/GP+379 task IDs and provider words','other callers/writers and record lifetime'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(app):
    for value in range(65536):
        check(delay_ticks(value)==value*1000//625,'bounded duration equation')
        packed=(value&0xe000)|0x1f00
        check(packed&255==0 and packed&0x1f00==0x1f00 and packed&0xe000==value&0xe000,'packet halfword field partition')
    check(delay_ticks(100)==160 and delay_ticks(500)==800,'concrete duration requests')
    check(delay_ticks(4294968)==1 and 4294968*1000//625!=1,'duration multiply wraps before DIVU')
    check([b for b in range(256) if ((b+1)&255)<=4]==[0,1,2,3,255],'retry byte wrap predicate')
    check(256!=0 and 256&255==0,'full mode branch differs from stored byte')
    for index in range(15):check(1<<index==((1<<index)&65535) and 12*index+12<=180,'15-record index/mask bounds')
    for reply in (0,1,255,256,0x80000000,MASK):check(int(reply<1)==int(reply==0),'SLTIU reply inversion')
    by_role={d[0]:d for d in DETAILS}
    cases=(('cancel',36,4),('cancel',78,1<<20),('cancel',86,1<<20),('cancel',94,0x80),
           ('register',22,0x80),('register',66,4),('register',164,1<<20),('register',176,1<<20),
           ('register',188,1<<20),('register',210,1<<20),('register',268,1<<20),
           ('retry_callback',10,1<<20),('retry_callback',48,1<<20),('retry_callback',58,0x1000),
           ('packet_callback',28,1<<20),('packet_callback',54,1<<20),('packet_callback',62,1<<20))
    for role,off,flip in cases:
        _,pc,size,count,stores,digest=by_role[role];raw=bytearray(previous.previous.take(app,pc,size));n=decode(raw,pc);width=n[pc+off]['size']
        raw[off:off+width]=(int.from_bytes(raw[off:off+width],'little')^flip).to_bytes(width,'little')
        try:body(raw,role,pc,size,count,stores,digest)
        except RuntimeError as e:check(str(e)=='APP record '+role+' instruction '+hex(off),'unexpected APP record mutation guard '+str(e))
        else:raise RuntimeError('APP record mutation escaped')
    print('PASS: 65536 duration/halfword cases; 256 retry bytes; overflow/full-mode/reply boundaries; 17 specified raw mutations')


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true',help='Create ledger exclusively');o=p.parse_args()
    app=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(app)==76800 and sha256(app).hexdigest()==init.binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK header identity')
    carriers=[]
    for label,folder,tail,size,digest in init.binding.PROFILES:
        raw=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(raw)==size and sha256(raw).hexdigest()==digest,'candidate identity '+label);carriers.append(raw)
    sources_hex=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
    coverage=sparse.derive(app,carriers,header,sources_hex,sparse.parser())
    sources,vectors=init.timer.source_contract();ledger=derive(app,carriers,header,coverage)
    ledger['sources'],ledger['official_Xwchc_vectors']=sources,vectors
    tests(app);output=(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'APP callback records exact ledger replay')
    print('PASS: 4 complete APP bodies584B/219instructions/26stores; cancel/register/provider/retry and stack-payload boundaries')
    print('PASS: exact ledger replay; record/payload ownership/provider status/retention/installed binding UNPROVED; NO target execution')


if __name__=='__main__':main()
