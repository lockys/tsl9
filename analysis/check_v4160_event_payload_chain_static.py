"""Complete event consumer, payload submission/enqueue/completion and copy leaf.

Bytes, operands, conditional graphs and host bitfields only. No target ISA,
event queue, copy state, provider, payload, callback or MMIO execution/model.
"""
import argparse
import json
import re
from hashlib import sha256
from pathlib import Path
import check_v4160_app_callback_records_static as previous

init,sparse,ROOT,MASK=previous.init,previous.sparse,previous.ROOT,previous.MASK
check=init.check
OUT=Path(__file__).with_name('v4160-event-payload-chain-static.json')
DETAILS=(('submit',0x1753a,174,59,9,'35b5fa1a5d028d10cb4b5bae27f3b458192eac49ac58a1aedac44cc7a3eb39f9'),
 ('complete',0x17666,58,22,3,'f1cbcf44c139aae19dc96b5c5b7ef6f40f3b6820265947a29987167fdfdffd8a'),
 ('consume',0x176f8,388,135,13,'1bd864d85cd82d9253370ea168691d98e1929d40ba4f6d64a6fa42320c278592'),
 ('enqueue',0x1787c,124,43,5,'d6bf7526927fd47af6e6ae487b36a176eb7dc85a2ee33e275971b2dd589d6990'))
COPY=0x20000332


def decode(raw,pc):
    n={};off=0
    while off<len(raw):
        h=int.from_bytes(raw[off:off+2],'little');size=2 if h&3!=3 else 4
        check(off+size<=len(raw),'payload complete instruction')
        chunk=raw[off:off+size];w=int.from_bytes(chunk,'little');p=pc+off;key=w&0xfe00707f
        if size==4 and key in (0x6033,0x02006033):
            d=dict(pc=p,size=4,bytes=chunk.hex(),op='or' if key==0x6033 else 'rem',rd=w>>7&31,rs1=w>>15&31,rs2=w>>20&31)
        else:d=previous.decode(chunk,p)[p]
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
    def bz(o,op,r,t):e(o,op,rs1=r,target=pc+t)
    def branch(o,op,a,b,t):e(o,op,rs1=a,rs2=b,target=pc+t)
    def jump(o,t):e(o,'jump',target=pc+t)
    def call(o,t):e(o,'jal',rd=1,target=t)
    def indirect(o,r=15):e(o,'call_indirect',rd=1,rs1=r)
    def upper(o,r,v=0x1fff5000):e(o,'auipc',rd=r,imm=v)
    def constant(o,r,v,low):upper(o,r,v);addi(o+4,r,r,low)
    def restore(rows):
        for o,r,v in rows:load(o,r,2,v)
    if role=='submit':
        mv(0,17,12);upper(2,12);load(6,12,12,621,1);bz(10,'bnez',12,170)
        load(12,16,3,366,1);addi(16,16,16,1);imm(18,'andi',16,16,15);mv(22,12,14)
        store(24,16,3,366,1);imm(28,'slli',14,10,8);imm(32,'slli',16,16,4)
        imm(34,'srli',10,10,8);binary(36,'or',16,17,16);binary(40,'or',10,10,14)
        upper(42,14);store(46,10,14,582,2);upper(50,14);store(54,16,14,576,1)
        addi(58,2,2,-16);addi(60,14,0,50);store(64,9,2,4);mv(66,9,11);mv(68,11,13)
        upper(70,13);store(74,14,13,552,1);addi(78,14,12,3);store(82,8,2,8)
        upper(84,13);store(88,14,13,539,1);lui(92,8,0x40000);upper(96,14);store(100,15,14,522)
        load(104,15,8,76);store(106,1,2,12);constant(108,10,0x1fff5000,519);indirect(116)
        load(118,15,8,512);mv(122,10,9);indirect(124);load(126,15,8,88)
        addi(128,12,0,320);li(132,11,2);upper(134,10);load(138,10,10,480,1);indirect(142)
        load(144,15,8,80);li(146,11,1);upper(148,10);load(152,10,10,466,1);indirect(156)
        restore(((158,1,12),(160,8,8),(162,9,4)));li(164,10,0);addi(166,2,2,16);e(168,'jr',rs1=1)
        li(170,10,1);e(172,'jr',rs1=1)
    elif role=='complete':
        lui(0,15,0x40000);load(4,15,15,88);addi(6,2,2,-16);store(8,8,2,8);store(10,1,2,12)
        mv(12,8,10);li(14,12,2);li(16,11,1);load(18,10,3,379,1);indirect(22)
        bz(24,'bnez',8,50);load(26,15,3,378,1);bz(30,'bnez',15,50)
        constant(32,10,0,26);call(40,0x90b0);li(44,15,1);store(46,15,3,378,1)
        restore(((50,1,12),(52,8,8)));addi(54,2,2,16);e(56,'jr',rs1=1)
    elif role=='consume':
        addi(0,2,2,-48)
        for o,r,v in ((2,8,40),(4,1,44),(6,9,36),(8,18,32),(10,19,28)):store(o,r,2,v)
        imm(12,'andi',15,11,1);mv(16,8,11);bz(18,'beqz',15,126)
        upper(20,15);load(24,15,15,418,1);constant(28,9,0x1fff5000,408);bz(36,'beqz',15,108)
        load(38,15,9,0,1);li(42,13,7);lui(44,10,0xb000);binary(46,'mul',13,13,15)
        li(50,14,7);constant(52,15,0,-198);li(60,12,0);li(62,11,21);addi(64,10,10,1378)
        addi(68,13,13,3);binary(70,'add',13,13,9);call(72,0x1753a);bz(76,'bnez',10,108)
        load(78,15,9,0,1);addi(82,15,15,1);imm(84,'andi',15,15,15);upper(86,14);store(90,15,14,350,1)
        load(94,15,9,2,1);addi(98,15,15,-1);upper(100,14);store(104,15,14,338,1);imm(108,'xori',10,8,1)
        restore(((112,1,44),(114,8,40),(116,9,36),(118,18,32),(120,19,28)))
        addi(122,2,2,48);e(124,'jr',rs1=1)
        imm(126,'andi',15,11,2);mv(130,9,10);li(132,10,0);bz(134,'beqz',15,112)
        load(136,15,3,376,1);li(140,11,7);binary(142,'mul',15,15,11);addi(146,18,3,104)
        load(150,11,18);lui(154,19,0x40000);load(158,14,19,76);li(162,12,7);addi(164,10,2,8)
        binary(166,'add',11,11,15);indirect(168,14);load(170,15,3,376,1);bz(174,'beqz',15,204)
        load(176,15,2,9,1);imm(180,'andi',15,15,252);bz(184,'bnez',15,204)
        store(186,0,3,376,1);load(190,15,19,76);load(194,11,18);li(198,12,7);addi(200,10,2,8);indirect(202)
        load(204,15,2,9,1);imm(208,'andi',15,15,2);bz(210,'beqz',15,234)
        load(212,14,2,8);li(214,13,1);imm(216,'srli',15,14,10);imm(220,'andi',15,15,63)
        branch(224,'beq',15,13,246);li(228,13,2);branch(230,'beq',15,13,314)
        addi(234,10,2,8);call(236,0xc776);imm(240,'xori',10,8,2);jump(244,112)
        load(246,15,2,14,1);imm(250,'andi',15,15,124);bz(254,'beqz',15,234)
        load(256,15,3,369,1);imm(260,'xori',15,15,1);store(264,15,3,369,1);bz(268,'beqz',15,286)
        load(270,15,2,12,2);lui(274,14,0x2000);addi(276,14,14,-256);binary(280,'or',15,15,14);store(282,15,2,12,2)
        load(286,15,2,12);lui(288,14,0x40000);load(292,14,14,88);imm(294,'srli',15,15,18)
        imm(296,'andi',15,15,31);addi(298,12,0,160);binary(302,'mul',12,15,12);li(306,11,2)
        mv(308,10,9);indirect(310,14);jump(312,234)
        load(314,15,3,370,1);imm(318,'slli',12,15,2);constant(322,13,0x3000,686)
        binary(330,'add',13,13,12);load(332,13,13);lui(334,12,0x10000);addi(336,12,12,-1)
        binary(338,'and',11,13,12);binary(342,'and',14,14,12);imm(344,'slli',11,11,16)
        binary(346,'or',14,14,11);store(348,14,2,8);addi(350,15,15,1);li(352,14,7)
        binary(354,'rem',15,15,14);imm(358,'srli',13,13,16);store(360,13,2,12,1)
        addi(364,12,0,800);store(368,15,3,370,1);load(372,15,2,12);lui(374,14,0x40000)
        load(378,14,14,88);imm(380,'srli',15,15,18);imm(382,'andi',15,15,31);addi(384,15,15,1);jump(386,302)
    elif role=='enqueue':
        addi(0,2,2,-16);store(2,9,2,4);store(4,1,2,12);upper(6,9);load(10,9,9,44,1);store(14,8,2,8)
        upper(16,14);load(20,14,14,34,1);li(24,15,15);branch(26,'bltu',15,14,96)
        constant(30,8,0x1fff5000,18);mv(38,11,10);load(40,10,8,1,1);li(44,15,7)
        lui(46,14,0x40000);binary(50,'mul',15,15,10);load(54,14,14,76);li(56,12,7)
        addi(58,15,15,3);binary(60,'add',10,8,15);indirect(64,14)
        load(66,15,8,1,1);addi(70,15,15,1);imm(72,'andi',15,15,15);upper(74,14);store(78,15,14,-25,1)
        load(82,15,8,2,1);addi(86,15,15,1);upper(88,14);store(92,15,14,-38,1);bz(96,'bnez',9,114)
        restore(((98,8,8),(100,1,12),(102,9,4)));addi(104,10,0,255);addi(108,2,2,16)
        e(110,'jal',rd=0,target=0x17666);restore(((114,1,12),(116,8,8),(118,9,4)));addi(120,2,2,16);e(122,'jr',rs1=1)
    elif role=='copy':
        lui(0,15,0x40024000);load(4,14,15,524);store(8,0,15,524);e(12,'fence.i')
        bz(16,'beqz',10,24);bz(18,'beqz',11,24);li(20,15,0);bz(22,'bnez',12,34)
        lui(24,15,0x40024000);store(28,14,15,524);e(32,'jr',rs1=1)
        binary(34,'add',13,11,15);load(38,16,13,0,1);binary(42,'add',13,10,15)
        addi(46,15,15,1);store(48,16,13,0,1);branch(52,'bne',12,15,34);jump(56,24)
    else:raise RuntimeError('unknown payload role')
    return s


def body(raw,role,pc,size,count,store_count,digest):
    n=decode(raw,pc);expected=specs(role,pc)
    check(set(n)==set(expected),'payload complete boundaries '+role)
    for p,f in expected.items():init.g(n,p,'payload '+role+' instruction '+hex(p-pc),**f)
    edges={};calls=[];tails=[]
    for p,d in n.items():
        if d['op']=='jr':check(d['rs1']==1,'payload RA return operand');qs=[]
        elif d['op']=='jump' or (d['op']=='jal' and d['rd']==0):qs=[d['target']]
        elif d['op'] in ('beq','bne','beqz','bnez','bltu','bgeu'):qs=[p+d['size'],d['target']]
        else:qs=[p+d['size']]
        for q in qs:
            if q not in n:
                check((role,p,q)==('enqueue',0x178ea,0x17666),'payload explicit external tail')
                tails.append({'pc':hex(p),'target':hex(q),'link_written':False,'A0':255})
        edges[p]=qs
        if d['op']=='call_indirect' or (d['op']=='jal' and d['rd']==1):calls.append({'pc':hex(p),'link':hex(p+d['size']),
            'target':hex(d['target']) if 'target' in d else 'then-live raw '+str(d['rs1'])+' & ~1','normal_return_proved':False})
    seen=set();active=set();back=[]
    def visit(p):
        if p not in n or p in seen:return
        seen.add(p);active.add(p)
        for q in edges[p]:
            if q in active:back.append([hex(p),hex(q)])
            else:visit(q)
        active.remove(p)
    visit(pc);check(seen==set(n),'payload full CFG reachability '+role)
    stores=[d for d in n.values() if d['op']=='store'];writes=sorted({d['rd'] for d in n.values() if d.get('rd',0)})
    check(len(raw)==size and len(n)==count and len(stores)==store_count and sha256(raw).hexdigest()==digest,'payload complete identity '+role)
    if role=='copy':
        check(back==[[hex(pc+52),hex(pc+34)]] and not calls and writes==[13,14,15,16],'copy leaf cycle/call/GPR census')
    else:check(not back,'payload APP local acyclic graph '+role)
    return {'start':hex(pc),'end_exclusive':hex(pc+size),'bytes':size,'sha256':digest,'instructions':list(n.values()),
        'stores':stores,'calls':calls,'external_tail_edges':tails,'DFS_back_edges':back,'encoded_GPR_writes':writes,
        'conditional_normal_return_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()}}


def derive(app,carriers,header,coverage):
    parent=previous.derive(app,carriers,header,coverage)
    bodies={r:body(previous.previous.previous.take(app,p,size),r,p,size,n,stores,h) for r,p,size,n,stores,h in DETAILS}
    copies=[]
    for data,desc in zip(carriers,init.binding.PROFILES):
        m=init.binding.profile(data,desc[0]);c=m['first_copy'];src=int(c['source'],16)+COPY-int(c['destination'],16)
        check(int(c['destination'],16)<=COPY and COPY+58<=int(m['first_copy_end_exclusive'],16),'copy full first-copy extent')
        check(init.binding.word(data,0x4004c)&~1==COPY,'copy slot4004c alias')
        copies.append(dict(body(init.binding.take(data,src,58),'copy',COPY,58,18,3,init.binding.COPY_HASH),label=desc[0],flash_source=hex(src)))
    check(parent['bodies']['retry_callback']['calls'][0]['target']==bodies['submit']['start'] and
          parent['bodies']['packet_callback']['calls'][-1]['target']==bodies['enqueue']['start'],'previous stack-payload call joins')
    aliases={}
    for name,index in ((b'tmos_memcpy',6),(b'RF_SetChannel',115)):
        check(re.search(rb'^\s*#define\s+'+name+rb'\s+[^\r\n]*BLE_LIB_JT\(\s*'+str(index).encode()+rb'\s*\)',header,re.M) is not None,
              'payload SDK alias '+name.decode())
        aliases[name.decode()]={'slot':hex(0x40034+4*index),'candidate_targets':[hex(init.binding.word(d,0x40034+4*index)&~1) for d in carriers],
            'installed_binding_proved':False}
    n={d['pc']:d for d in bodies['submit']['instructions']};absolute={}
    for name,p in (('gate_length',0x1753c),('opcode',0x17564),('kind_seq',0x1756c),('control',0x17580),
                   ('length_store',0x1758e),('callback_word',0x1759a),('payload',0x175a6),('timer_task',0x175c0),('event_task',0x175ce)):
        absolute[name]=hex((p+n[p]['imm']+n[p+4]['imm'])&MASK)
    check(absolute=={'gate_length':'0x2000c7a9','opcode':'0x2000c7aa','kind_seq':'0x2000c7ac','control':'0x2000c7a8',
        'length_store':'0x2000c7a9','callback_word':'0x2000c7a4','payload':'0x2000c7ad','timer_task':'0x2000c7a0','event_task':'0x2000c7a0'},
        'submission absolute fields')
    consumer={d['pc']:d for d in bodies['consume']['instructions']}
    table=(0x1783a+consumer[0x1783a]['imm']+consumer[0x1783e]['imm'])&MASK
    check(table==0x1aae8,'consumer literal-table base')
    raw_table=previous.previous.previous.take(app,table,28)
    all_bodies=list(bodies.values())+copies
    check(sum(b['bytes'] for b in all_bodies)==860 and sum(len(b['instructions']) for b in all_bodies)==295 and
          sum(len(b['stores']) for b in all_bodies)==36,'payload body census')
    return {'schema':'TSL9-event-payload-chain-static-v1','profile':init.timer.PROFILE,
        'scope':'4 complete APP bodies744B/259instructions/30stores +2 complete mapped copy leaves116B/36instructions/6stores',
        'bodies':bodies,'reference_copy_profiles':copies,'SDK_aliases':aliases,'submission_fields':absolute,
        'submit_contract':{'entry_args':['H','channel','kind','source','length','callback'],
            'gate':'fresh U8[2000c7a9]!=0 returns1 without local stores/calls/frame; same address later stores low8(length+3)',
            'publication_order':['seq=(fresh U8[GP+366]+1)&15; store seq','SH low16((H>>8)|(H<<8))',
                'SB low8(kind|(seq<<4))','SB50 control','SB low8(length+3)','SW entry callback to2000c7a4',
                'fresh4004c(2000c7ad,entry source,full entry length)','fresh40200(A0=saved channel)',
                'fresh40058(fresh task,2,320)','fresh40050(another fresh task,1)','normal accepted path returns0 regardless scalar replies'],
            'source_pointer_direct_field_store':False,'callback_pointer_direct_field_store':True,
            'copy_completed_or_actual_delivery_proved':False,'gate_is_unconditional_lock_or_length_bound':False,
            'general_H_is_unconditional_U16_byteswap':False,'kind_low4_guard':False},
        'copy_contract':{'entry_args':['destination','source','full length'],'guard':'control save/write0/FENCE.I before null guards; dest0/source0/length0 return without byte copy',
            'nonzero_case':'i starts0; fresh U8[source+i] read then SB to destination+i; i++ until i==length; restore control; RET',
            'encoded_preservation':'A0/A1/A2/GP/S/SP/RA not written; no nested call or source-pointer field store',
            'conditional_bridge':'if actual slot matches reference, code/accesses/MMIO valid and ranges nonadversely alias, original stack bytes are copied before helper returns; no copy state simulated',
            'later_unknown_calls_preserve_destination_proved':False,'physical_MMIO_effects_proved':False},
        'queue_contract':{'base':'0x2000c8ac','fields':['read index +0','write index +1','count +2','payload +3+7*i'],
            'nominal_layout':'3+16*7=115 bytes, from earlier init fill request; not an unconditional extent proof',
            'enqueue':'first count saved S1, second fresh count<=15 permits copy toB+3+7*full U8[B+1]; no initial index mask/guard',
            'after_copy':'fresh write index ->(i+1)&15; fresh count ->low8(c+1); no scalar reply test',
            'completion_tail':'first saved count0 ->restore frame;17666(255), even if second count rejected copy',
            'payload_source_direct_field_store':False,'copy_or_index_validity_proved':False},
        'consume_contract':{'event_input':'full entry E=A1; entry A0 task preserved for bit1 scheduling',
            'priority_reply':'bit0 first ->E XOR1; else bit1 ->E XOR2; neither ->0',
            'bit0':'count!=0 then1753a(b562,21,0,B+3+7*full fresh readindex,7,17666); only scalar0 updates fresh readindex/count; reply bit0 cleared regardless',
            'bit1_copy':'fresh4004c(SP+8,fresh U32[GP+104]+7*fresh U8[GP+376],7); optional mode reset and second fresh copy',
            'special1':'GP+369 XOR1; if new byte nonzero OR1f00 into SP+12 halfword; schedule(saved full task,2,160*((fresh U32[SP+12]>>18)&31))',
            'special2':'unmasked U8[GP+370] indexes literal table before (i+1) signed REM7; schedule(saved full task,2,800*(1+((fresh U32[SP+12]>>18)&31)))',
            'stack_delivery':'C776(SP+8) after scheduling; ownership/retention unresolved',
            'nominal_copy7_span_excludes_stack_byte15':True,'neither_delay_formula_uses_stack_byte15':True},
        'completion_contract':{'first_action':'fresh40058(fresh U8[GP+379],1,2), scalar not tested',
            'conditional_cancel':'if saved full entry A0==0 and fresh U8[GP+378]==0:90b0(176a0), then SB1 toGP+378 regardless cancel reply',
            'queue_tail255_skips_cancel_flag_update':True,'callback_invocation_from_saved_pointer_proved':False},
        'literal_table':{'start':hex(table),'captured_nominal_bytes':28,'sha256':sha256(raw_table).hexdigest(),
            'words':[hex(int.from_bytes(raw_table[i:i+4],'little')) for i in range(0,28,4)],
            'initial_index_less7_guard':False,'read_precedes_remainder_update':True},
        'premises':['supported ISA/RV32M and code bytes; valid stack/global/table/MMIO accesses',
            'opaque callees return normally and preserve needed GP/S/SP/frame; no adverse alias/interrupt/writer/reentry',
            'fresh counts/indices/task/provider words stay distinct unless preservation separately proved',
            'reference copy binding and physical side effects remain conditional; sparse boot gap/installed identity not closed'],
        'remaining_boundaries':['C776 stack payload retention and parsing','saved callback word consumers and transport task',
            'actual40200/4004c/40058/40050 bindings and global field writers','queue/index/record ownership and reentry'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(app,carriers):
    counts=[0,0,0]
    for E in range(65536):
        role=0 if E&1 else 1 if E&2 else 2;counts[role]+=1
        reply=E^1 if role==0 else E^2 if role==1 else 0
        check((role!=0 or not reply&1) and (role!=1 or not reply&2),'priority reply bit algebra')
        H=E;check((((H>>8)|(H<<8))&65535)==((H&255)<<8)|(H>>8),'bounded opcode byte swap')
    check(counts==[32768,16384,16384],'event priority partition')
    check((((0x10000>>8)|(0x10000<<8))&65535)==0x100,'full H is not unconditional low16 byte swap')
    for byte in range(256):
        check(0<=((byte+1)&15)<=15 and 0<=((byte+1)%7)<=6,'index update bitfields')
        check(((byte+1)&255)==(byte+1)%256,'queue count byte wrap')
    for upper in range(256):
        for low in range(256):
            word=(upper<<24)|(low<<16)|0x55aa
            check(((word>>18)&31)==((low>>2)&31),'delay field excludes stack byte15')
    check(((253+3)&255)==0 and (7+3)&255==10,'length gate wraps, concrete seven-byte length')
    by_role={d[0]:d for d in DETAILS}
    cases=(('submit',6,1<<20),('submit',88,1<<20),('submit',100,1<<20),('submit',116,0x80),
           ('complete',24,0x80),('consume',18,0x80),('consume',38,1<<20),('consume',104,1<<20),
           ('consume',168,0x80),('consume',310,0x80),('consume',332,4),('consume',354,1<<20),
           ('enqueue',10,1<<20),('enqueue',26,0x1000),('enqueue',64,0x80),('enqueue',110,1<<21))
    for role,off,flip in cases:
        _,pc,size,count,stores,digest=by_role[role];raw=bytearray(previous.previous.previous.take(app,pc,size));n=decode(raw,pc);w=n[pc+off]['size']
        raw[off:off+w]=(int.from_bytes(raw[off:off+w],'little')^flip).to_bytes(w,'little')
        try:body(raw,role,pc,size,count,stores,digest)
        except RuntimeError as e:check(str(e)=='payload '+role+' instruction '+hex(off),'unexpected payload mutation guard '+str(e))
        else:raise RuntimeError('payload mutation escaped')
    mapping=init.binding.profile(carriers[0],'V1.31');src=int(mapping['first_copy']['source'],16)+COPY-int(mapping['first_copy']['destination'],16)
    for off,flip in ((16,0x80),(38,1<<20),(48,1<<20)):
        raw=bytearray(init.binding.take(carriers[0],src,58));n=decode(raw,COPY);w=n[COPY+off]['size']
        raw[off:off+w]=(int.from_bytes(raw[off:off+w],'little')^flip).to_bytes(w,'little')
        try:body(raw,'copy',COPY,58,18,3,init.binding.COPY_HASH)
        except RuntimeError as e:check(str(e)=='payload copy instruction '+hex(off),'unexpected copy mutation guard '+str(e))
        else:raise RuntimeError('copy mutation escaped')
    print('PASS: 65536 event/opcode cases; 65536 delay-field cases; 256 byte indices; 19 specified raw mutations')


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
    tests(app,carriers);output=(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'event payload chain exact ledger replay')
    print('PASS: 6 complete bodies860B/295instructions/36stores; queue/consumer/submission/completion and conditional reference copy joins')
    print('PASS: exact ledger replay; actual copy/delivery/retention/installed binding UNPROVED; NO target execution')


if __name__=='__main__':main()
