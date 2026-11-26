"""Complete APP hardware leaf and initialization tail/return helpers.

Static operands/CFGs and host bitfield algebra only. No target ISA, MMIO,
CSR, boot/copy state, provider, timer or callback execution/emulation.
"""
import argparse
import json
import re
from hashlib import sha256
from pathlib import Path
import check_v4160_app_jt0_call_chain_static as previous

init,sparse,ROOT,MASK=previous.init,previous.sparse,previous.ROOT,previous.MASK
check=init.check
OUT=Path(__file__).with_name('v4160-init-tail-hardware-static.json')
DETAILS=(('hardware',0x1874a,234,93,21,'e0debe8b77025cfb56144045a0aa7524b7a2cd2ad0bd3daa2d880408ad9758f5'),
 ('late_init',0x17bf6,88,30,3,'2610037e76c76f2f6d393773b5ab1251f86c3cb2201ab972da78778ab8a1a3df'),
 ('tail_return',0x17b92,50,17,2,'9f5b6868f32f0296af6e11a1089470c89e95cbeeb98db464f0ed114cc152ed3c'),
 ('select_or_schedule',0x1798a,114,44,4,'0969013e78bab8c5a4124628d5a3c7bf3a5d017f5fabed9be493fdcc1e3b065e'))


def specs(role,pc):
    s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def load(o,r,b,v=0,w=4):e(o,'load',rd=r,rs1=b,imm=v,width=w)
    def store(o,r,b,v=0,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    def lui(o,r,v):e(o,'lui',rd=r,imm=v)
    def addi(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    def binary(o,op,r,a,b):e(o,op,rd=r,rs1=a,rs2=b)
    def imm(o,op,r,a,v):e(o,op,rd=r,rs1=a,imm=v)
    def branch(o,op,a,b,t):e(o,op,rs1=a,rs2=b,target=pc+t)
    def bz(o,op,a,t):e(o,op,rs1=a,target=pc+t)
    def call(o,t):e(o,'jal',rd=1,target=t)
    def indirect(o):e(o,'call_indirect',rd=1,rs1=15)
    def constant(o,r,upper,low):e(o,'auipc',rd=r,imm=upper);addi(o+4,r,r,low)
    if role=='hardware':
        B=0x40021000;lui(0,15,B);load(4,14,15);lui(6,13,0xf8ff0000);addi(10,2,2,-16)
        imm(12,'ori',14,14,1);store(16,14,15);load(18,14,15,4);lui(20,12,0x20000)
        binary(24,'and',14,14,13);store(26,14,15,4)
        for o,upper,target in ((28,0xfef70000,0),(40,0xfffc0000,0),(52,0xff810000,4)):
            load(o,14,15,target);lui(o+2,13,upper);addi(o+6,13,13,-1)
            binary(o+8,'and',14,14,13);store(o+10,14,15,target)
        lui(64,14,0x9f0000);store(68,14,15,8);store(70,0,2,8);store(72,0,2,12)
        load(74,14,15);lui(76,13,0x10000);binary(78,'or',14,14,13);store(80,14,15)
        lui(82,13,B);lui(86,14,0x1000);load(88,15,13);binary(90,'and',15,15,12)
        store(92,15,2,12);load(94,15,2,8);addi(96,15,15,1);store(98,15,2,8)
        load(100,15,2,12);bz(102,'bnez',15,110);load(104,15,2,8);branch(106,'bne',15,14,88)
        lui(110,15,B);load(114,15,15);imm(116,'slli',14,15,14);branch(120,'bge',14,0,230)
        li(124,15,1);store(126,15,2,12);load(128,14,2,12);li(130,15,1)
        branch(132,'bne',14,15,226);lui(136,15,B);load(140,14,15,4)
        lui(142,13,0xffc10000);addi(146,13,13,-1);store(148,14,15,4)
        load(150,14,15,4);store(152,14,15,4);load(154,14,15,4);imm(156,'ori',14,14,1024)
        store(160,14,15,4);load(162,14,15,4);binary(164,'and',14,14,13);store(166,14,15,4)
        load(168,14,15,4);lui(170,13,0x290000);binary(174,'or',14,14,13);store(176,14,15,4)
        load(178,14,15);lui(180,13,0x1000000);binary(184,'or',14,14,13);store(186,14,15)
        load(188,14,15);imm(190,'slli',13,14,6);branch(194,'bge',13,0,188)
        load(198,14,15,4);lui(200,13,B);imm(204,'andi',14,14,-4);store(206,14,15,4)
        load(208,14,15,4);imm(210,'ori',14,14,2);store(214,14,15,4);li(216,14,8)
        load(218,15,13,4);imm(220,'andi',15,15,12);branch(222,'bne',15,14,218)
        addi(226,2,2,16);e(228,'jr',rs1=1);store(230,0,2,12);e(232,'jump',target=pc+128)
    elif role=='late_init':
        addi(0,2,2,-16);store(2,8,2,8);lui(4,8,0x40000);load(8,15,8,72);store(10,1,2,12)
        li(12,12,3);li(14,11,0);addi(16,10,3,376);indirect(20);load(22,15,8,72)
        addi(24,12,0,115);li(28,11,0);constant(30,10,0x1fff5000,-872);indirect(38)
        load(40,15,8,128);constant(44,10,0,-1322);indirect(52);store(54,10,3,379,1)
        constant(58,10,0,-824);call(66,0x90b0);li(70,11,0);li(72,10,1);call(74,0x1798a)
        load(78,8,2,8);load(80,1,2,12);addi(82,2,2,16);e(84,'jal',rd=0,target=0x17b92)
    elif role=='tail_return':
        load(0,15,3,378,1);bz(4,'bnez',15,44);addi(6,2,2,-16);li(8,13,0)
        addi(10,12,0,100);li(14,11,0);constant(16,10,0,-1282);store(24,1,2,12)
        store(26,0,3,377,1);call(30,0x9124);load(34,1,2,12);load(36,10,3,378,1)
        addi(40,2,2,16);e(42,'jr',rs1=1);load(44,10,3,378,1);e(48,'jr',rs1=1)
    elif role=='select_or_schedule':
        addi(0,15,0,35);branch(4,'bltu',15,11,112);addi(8,2,2,-32);store(10,1,2,28)
        bz(12,'bnez',10,90);li(14,15,7);binary(16,'mul',11,11,15);addi(20,15,3,100)
        load(24,14,15);lui(26,15,0x40000);load(30,15,15,76);li(32,12,7);addi(34,10,2,8)
        binary(36,'add',11,11,14);indirect(38);load(40,15,2,8);imm(42,'srli',15,15,10)
        imm(44,'andi',15,15,63);imm(48,'andi',14,15,1);bz(52,'beqz',14,64)
        load(54,14,2,12);imm(56,'srli',14,14,23);imm(58,'andi',14,14,1);store(60,14,3,367,1)
        imm(64,'andi',15,15,2);bz(66,'beqz',15,78);load(68,15,2,12)
        imm(70,'srli',15,15,23);imm(72,'andi',15,15,1);store(74,15,3,368,1)
        addi(78,10,2,8);call(80,0x1787c);load(84,1,2,28);addi(86,2,2,32);e(88,'jr',rs1=1)
        store(90,11,3,376,1);lui(94,15,0x40000);load(98,15,15,88);li(100,12,2);li(102,11,2)
        load(104,10,3,379,1);indirect(108);e(110,'jump',target=pc+84);e(112,'jr',rs1=1)
    else:raise RuntimeError('unknown init-tail role')
    return s


def body(raw,role,pc,digest,count,store_count):
    n=previous.decode(raw,pc);expected=specs(role,pc)
    check(set(n)==set(expected),'init-tail complete boundaries '+role)
    for p,f in expected.items():init.g(n,p,'init-tail '+role+' instruction '+hex(p-pc),**f)
    edges={};calls=[];external=[]
    for p,d in n.items():
        if d['op']=='jr':qs=[]
        elif d['op']=='jump' or (d['op']=='jal' and d['rd']==0):qs=[d['target']]
        elif d['op'] in ('beq','bne','beqz','bnez','bge','bltu','bgeu'):qs=[p+d['size'],d['target']]
        else:qs=[p+d['size']]
        for q in qs:
            if q not in n:
                check((role,p,q)==('late_init',0x17c4a,0x17b92),'init-tail explicit external edge')
                external.append({'pc':hex(p),'target':hex(q),'link_written':False})
        edges[p]=qs
        if d['op']=='call_indirect' or (d['op']=='jal' and d['rd']==1):
            calls.append({'pc':hex(p),'link':hex(p+d['size']),'target':hex(d['target']) if 'target' in d else 'fresh raw A5 & ~1',
                'normal_return_proved':False})
    seen=set();active=set();back=[]
    def visit(p):
        if p not in n or p in seen:return
        seen.add(p);active.add(p)
        for q in edges[p]:
            if q in active:back.append([hex(p),hex(q)])
            else:visit(q)
        active.remove(p)
    visit(pc);check(seen==set(n),'init-tail full CFG reachability '+role)
    stores=[d for d in n.values() if d['op']=='store'];loads=[d for d in n.values() if d['op']=='load']
    writes=sorted({d['rd'] for d in n.values() if d.get('rd',0)})
    check(len(raw)==next(d[2] for d in DETAILS if d[0]==role) and len(n)==count and len(stores)==store_count and
          sha256(raw).hexdigest()==digest,'init-tail complete identity '+role)
    if role=='hardware':
        check(writes==[2,12,13,14,15] and not calls and not any(d['op']=='csr' for d in n.values()),'hardware leaf GPR/call/CSR census')
        check(len(loads)==22 and sum(d['rs1']==2 for d in stores)==6 and sum(d['rs1']==2 for d in loads)==4,'hardware stack/MMIO census')
        check(all(d['rs1']==2 or (d['rs1'] in (13,15) and d['imm'] in (0,4,8) and d['width']==4)
                  for d in stores+loads),'hardware memory operand classes')
        check(sorted(back)==sorted([['0x187b4','0x187a2'],['0x1880c','0x18806'],['0x18828','0x18824']]),
              'hardware three polling backedges')
    else:check(not back,'init-tail local acyclic CFG '+role)
    return {'start':hex(pc),'end_exclusive':hex(pc+len(raw)),'bytes':len(raw),'sha256':digest,
        'instructions':list(n.values()),'stores':stores,'loads':loads,'calls':calls,'external_tail_edges':external,
        'conditional_normal_return_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},
        'DFS_back_edges':back,'encoded_GPR_writes':writes}


def derive(app,carriers,header,coverage):
    parent=previous.derive(app,carriers,header,coverage)
    bodies={role:body(previous.take(app,pc,size),role,pc,digest,count,stores) for role,pc,size,count,stores,digest in DETAILS}
    check(parent['bodies']['reset']['calls']==[{'pc':'0x18720','target':'0x1874a','link':'0x18724','normal_return_proved':False}],
          'reset-to-hardware call join')
    check(parent['bodies']['init_sequence']['external_tail_edges']==[{'pc':'0x928c','target':'0x17bf6','link_written':False}],
          'init-sequence-to-late-init tail join')
    check(bodies['late_init']['external_tail_edges'][0]['target']==bodies['tail_return']['start'],'late-init-to-return tail join')
    aliases={}
    for name,index in ((b'tmos_memset',5),(b'TMOS_ProcessEventRegister',19),(b'tmos_start_task',9)):
        check(re.search(rb'^\s*#define\s+'+name+rb'\s+[^\r\n]*BLE_LIB_JT\(\s*'+str(index).encode()+rb'\s*\)',header,re.M) is not None,
              'late-init SDK alias '+name.decode())
        aliases[name.decode()]={'JT':index,'slot':hex(0x40034+4*index),
            'candidate_targets':[hex(init.binding.word(data,0x40034+4*index)&~1) for data in carriers],'installed_binding_proved':False}
    late={d['pc']:d for d in bodies['late_init']['instructions']}
    constants={}
    for key,p in (('second_fill_destination',0x17c14),('registered_callback',0x17c22),('cancel_callback',0x17c30)):
        constants[key]=hex((p+late[p]['imm']+late[p+4]['imm'])&MASK)
    ret={d['pc']:d for d in bodies['tail_return']['instructions']}
    constants['deferred_callback']=hex((0x17ba2+ret[0x17ba2]['imm']+ret[0x17ba6]['imm'])&MASK)
    check(constants=={'second_fill_destination':'0x2000c8ac','registered_callback':'0x176f8',
        'cancel_callback':'0x178f8','deferred_callback':'0x176a0'},'late-init callback/data constants')
    check(not any(d.get('rd')==10 for d in parent['bodies']['loop']['instructions'] if d['pc']<=0x819c),
          'first-JT0 prefix keeps returned A0')
    check(sum(b['bytes'] for b in bodies.values())==486 and sum(len(b['instructions']) for b in bodies.values())==184 and
          sum(len(b['stores']) for b in bodies.values())==30,'init-tail byte/instruction/store census')
    return {'schema':'TSL9-init-tail-hardware-static-v1','profile':init.timer.PROFILE,
        'scope':'4 complete original APP bodies486B/184instructions/30stores; previous reset/init/JT0 chain revalidated',
        'bodies':bodies,'SDK_aliases':aliases,'late_constants':constants,
        'hardware_contract':{'frame_bytes':16,'scratch_words':'SP+8 counter, SP+12 status; RA not saved or written',
            'MMIO_operand_base':'0x40021000','MMIO_word_offsets':[0,4,8],'MMIO_load_sites':18,'MMIO_store_sites':15,
            'initial_poll':'fresh reg0&20000; counter++ from0; break if stored status!=0 or counter==4096; stable/noalias stack premise',
            'reclassification':'fresh reg0 bit17 -> scratch1/0, fresh scratch read controls setup; not old poll status',
            'unbounded_polls':['fresh reg0 bit25 must become1','fresh reg4 &12 must equal8'],
            'unconditional_return_or_hardware_success_proved':False,'normal_return_A0':'entry A0 preserved',
            'encoded_GP_S_RA_CSR_writes':False,'direct_JT0_store_with_valid_disjoint_stack':False,
            'physical_MMIO_or_asynchronous_effects_proved':False},
        'late_contract':{'first_fill':'fresh slot40048: (then-live GP+376,0,3)',
            'second_fill':'fresh slot40048: (2000c8ac,0,115)',
            'register':'fresh slot40080: A0=176f8; low8 reply -> then-live GP+379; no invalid-ID guard',
            'cancel':'90b0(178f8), opaque','select_call':'1798a(A0=1,A1=0) -> concrete schedule branch',
            'schedule_request':'SB0 at GP+376; fresh slot40058(fresh U8[GP+379],2,2); no time units or success proof',
            'timer_scalar_reply_tested_before_tail':False,'first_two_slot_words_same_unconditionally':False},
        'return_contract':{'predicate':'fresh U8[GP+378] nonzero skips local frame/call, but return rereads byte',
            'zero_path':'clear GP+377; 9124(176a0,0,100,0), opaque; fresh U8[GP+378] -> A0',
            'reply':'both normal paths fresh U8[then-live GP+378], not predicate snapshot or provider reply',
            'conditional_RA_chain':'9250 restores900e ->17bf6 restores900e ->17b92 returns900e; frame/GP/normal-callee premises required'},
        'first_JT0_A0_join':'if initialization returns normally through these bodies, A0 at first819c is last fresh U8[GP+378],0..255; no claim for later iterations',
        'alternate_select_branch':'A1>35 returns without frame; else entry A0=0 requests7-byte copy toSP+8 then selected bit updates GP+367/368 and1787c(SP+8); opaque effects',
        'retention_scope':'concrete hardware leaf has no GP/S/RA/CSR writes; late helpers keep opaque provider/callee/alias boundaries; no transitive JT0/MEPC retention proof',
        'premises':['supported ISA/code bytes and valid stack/MMIO/data access; hardware polls exit where continuation asserted',
            'needed GP/S/SP/RA/frame and data preservation across unknown callees; no adverse alias/writer/IRQ/reentry',
            'fresh byte/slot/MMIO reads remain distinct; nominal addresses require live base preservation',
            'actual resident binding, sparse-source gap, CSR/MRET effects and ownership remain unproved'],
        'remaining_boundaries':['90b0/9124 and registered callbacks176f8/178f8/176a0','actual provider word/ID lifetime',
            'other13 init calls and nested effects','hardware poll exits/physicalMMIO, JT0/MEPC retention and ownership'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(app):
    for high in range(65536):
        word=(high<<16)|0xa55a
        for shift,bit in ((14,17),(6,25)):
            check(bool(((word<<shift)&MASK)&0x80000000)==bool(word&(1<<bit)),'signed shift polling bit identity')
    for count in range(1,4097):check((count!=4096)==(count<4096),'bounded first-poll counter equality')
    for word in range(256):check(((word&12)==8)==((word>>2&3)==2),'reg4 two-bit poll predicate')
    by_role={d[0]:d for d in DETAILS}
    cases=(('hardware',88,4),('hardware',106,0x1000),('hardware',116,1<<20),('hardware',120,0x1000),
           ('hardware',148,4),('hardware',190,1<<20),('hardware',194,0x1000),('hardware',222,0x1000),
           ('hardware',230,4),('late_init',8,4),('late_init',24,1<<20),('late_init',54,1<<20),
           ('late_init',84,1<<21),('tail_return',36,1<<20),('tail_return',44,1<<20),
           ('select_or_schedule',104,1<<20),('select_or_schedule',108,0x80))
    for role,off,flip in cases:
        _,pc,size,count,stores,digest=by_role[role];raw=bytearray(previous.take(app,pc,size));n=previous.decode(raw,pc);width=n[pc+off]['size']
        raw[off:off+width]=(int.from_bytes(raw[off:off+width],'little')^flip).to_bytes(width,'little')
        try:body(raw,role,pc,digest,count,stores)
        except RuntimeError as e:check(str(e)=='init-tail '+role+' instruction '+hex(off),'unexpected init-tail mutation guard '+str(e))
        else:raise RuntimeError('init-tail mutation escaped')
    print('PASS: 131072 signed-bit identities; 4096 counter cases; 256 poll predicates; 17 specified raw mutations')


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
    else:check(OUT.read_bytes()==output,'init-tail/hardware exact ledger replay')
    print('PASS: 4 complete APP bodies486B/184instructions/30stores; poll/return/schedule and first-JT0 A0 joins')
    print('PASS: exact ledger replay; hardware termination/provider status/retention/installed binding UNPROVED; NO target execution')


if __name__=='__main__':main()
