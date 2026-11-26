"""Stack-to-global payload/state path and actual saved-callback consumer.

Complete original APP operands/CFGs and host bitfields only; no target ISA,
copy state, RF/provider, callback, stack/object or MMIO execution/emulation.
"""
import argparse
import json
import re
from hashlib import sha256
from pathlib import Path
import check_v4160_event_payload_chain_static as previous
from check_v4160_app_jt0_call_chain_static import take

init,sparse,ROOT,MASK=previous.init,previous.sparse,previous.ROOT,previous.MASK
check=init.check
OUT=Path(__file__).with_name('v4160-payload-consumers-static.json')
DETAILS=(('state',0xc6a8,206,75,5,'183f54a7320d68b1733a292cddda5a4d08fe197fb91de67dcbec4123ce522947'),
 ('handoff',0xc776,34,13,1,'2589e0bc3b3faa584824a9b1c6a28a4995e8386f8d226acde09007a720cd114f'),
 ('finish',0x173ee,84,29,5,'cd8a5a0901d99319d3661a7b0872caad618b0bdcfb524a399ab567ea2d11805c'),
 ('retry',0x17442,52,16,1,'9c7f4452739ef9007097805174f93d3ce685bf07bd56e763bf3424e84b1e2446'),
 ('task',0x17476,120,43,3,'9e896a2abfa642e40f3b7c0d90355760e9e8d78f9159f85190826be0ef9de2a9'),
 ('status',0x174ee,76,22,0,'8d1fe26ede0b1c74b6c550872c3a3db09c6ce90f8b129501d4d6e50156c974d0'),
 ('constructor',0x175e8,126,44,9,'f4a0f1fe856e488853f27ae937fdca1e9e0240a4b705e79b77265675c3513c5e'))


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
    def tail(o,t):e(o,'jal',rd=0,target=t)
    def indirect(o):e(o,'call_indirect',rd=1,rs1=15)
    def upper(o,r,v=0x1fff5000):e(o,'auipc',rd=r,imm=v)
    def constant(o,r,v,low):upper(o,r,v);addi(o+4,r,r,low)
    def restore(rows):
        for o,r,v in rows:load(o,r,2,v)
    if role=='state':
        addi(0,14,3,220);load(4,15,14);imm(6,'srli',15,15,9);imm(8,'andi',15,15,1);bz(10,'beqz',15,204)
        load(12,15,14);li(14,13,0);imm(16,'srli',15,15,10);imm(18,'andi',15,15,63);bz(22,'beqz',15,60)
        load(24,15,14);imm(26,'srli',13,15,16);load(30,15,14,4);imm(32,'andi',15,15,255)
        imm(36,'slli',15,15,16);binary(38,'or',15,15,13);imm(40,'srli',13,15,8);store(44,15,10,4,1)
        imm(48,'srli',15,15,16);store(50,13,10,5,1);store(54,15,10,6,1);li(58,13,1)
        load(60,15,14,4);imm(62,'srli',15,15,8);imm(64,'andi',15,15,31);bz(66,'beqz',15,202)
        load(68,15,14,4);li(70,13,10);imm(72,'srli',15,15,8);imm(74,'andi',15,15,31)
        branch(76,'bltu',13,15,172);load(80,13,14,4);li(82,12,10);load(84,15,10,7,1)
        imm(88,'srli',13,13,8);imm(90,'andi',13,13,31);binary(92,'mul',13,13,12)
        imm(96,'andi',15,15,127);binary(100,'add',15,15,13);imm(102,'andi',15,15,255)
        addi(106,12,0,100);mv(110,13,15);branch(112,'bgeu',12,15,120);addi(116,13,0,100)
        imm(120,'andi',15,13,255);load(124,13,10,7,1);imm(128,'andi',15,15,127)
        imm(132,'andi',13,13,-128);binary(136,'or',15,15,13);store(138,15,10,7,1)
        load(142,15,10,2,1);bz(146,'beqz',15,204);load(148,15,14,4);imm(150,'srli',15,15,13)
        imm(152,'andi',14,15,3);load(156,15,10,8,1);imm(160,'andi',15,15,-4)
        binary(162,'or',15,15,14);store(164,15,10,8,1);tail(168,0x12a08)
        load(172,13,14,4);li(174,12,20);li(176,15,0);imm(178,'srli',13,13,8);imm(180,'andi',13,13,31)
        branch(182,'bltu',12,13,124);load(186,15,14,4);li(188,13,10);imm(190,'srli',15,15,8)
        imm(192,'andi',15,15,31);addi(194,15,15,-10);binary(196,'mul',15,15,13);jump(200,102)
        bz(202,'bnez',13,142);e(204,'jr',rs1=1)
    elif role=='handoff':
        lui(0,15,0x40000);load(4,15,15,76);addi(6,2,2,-16);store(8,1,2,12);mv(10,11,10)
        li(12,12,7);addi(14,10,3,220);indirect(18);load(20,1,2,12)
        constant(22,10,0x20000000,-1276);addi(30,2,2,16);e(32,'jump',target=0xc6a8)
    elif role=='finish':
        lui(0,15,0x40000);load(4,15,15,92);addi(6,2,2,-16);store(8,8,2,8);store(10,1,2,12)
        mv(12,8,10);li(14,11,2);upper(16,10);load(20,10,10,930,1);indirect(24)
        upper(26,15);store(30,0,15,928,1);upper(34,15);store(38,0,15,921,1)
        constant(42,15,0x1fff5000,904);load(50,6,15,4);branch(54,'beq',6,0,76)
        mv(58,10,8);restore(((60,8,8),(62,1,12)));upper(64,15);store(68,0,15,886)
        addi(72,2,2,16);e(74,'jr',rs1=6);restore(((76,1,12),(78,8,8)));addi(80,2,2,16);e(82,'jr',rs1=1)
    elif role=='retry':
        upper(0,15);load(4,15,15,870,1);addi(8,15,15,-1);imm(10,'andi',15,15,255)
        upper(14,14);store(18,15,14,856,1);bz(22,'bnez',15,30);li(24,10,1);tail(26,0x173ee)
        lui(30,15,0x40000);load(34,6,15,88);li(38,12,2);li(40,11,1)
        upper(42,10);load(46,10,10,820,1);e(50,'jr',rs1=6)
    elif role=='task':
        addi(0,2,2,-16);imm(2,'slli',15,11,16)
        for o,r,v in ((6,8,8),(8,1,12),(10,9,4)):store(o,r,2,v)
        imm(12,'srai',15,15,16);mv(14,8,11);branch(16,'bge',15,0,48)
        lui(20,9,0x40000);load(24,15,9,108);indirect(26);bz(28,'beqz',10,34)
        load(30,15,9,104);indirect(32);lui(34,10,0x8000);binary(36,'xor',10,10,8)
        restore(((38,1,12),(40,8,8),(42,9,4)));addi(44,2,2,16);e(46,'jr',rs1=1)
        imm(48,'andi',15,11,1);bz(52,'beqz',15,100);lui(54,9,0x40000)
        load(58,15,9,464);indirect(62);load(64,15,9,460);addi(68,13,0,255);addi(72,12,0,255)
        upper(76,11);load(80,11,11,743,1);constant(84,10,0x1fff5000,736);indirect(92)
        imm(94,'xori',10,8,1);jump(98,38);imm(100,'andi',15,11,2);li(104,10,0);bz(106,'beqz',15,38)
        li(108,10,1);call(110,0x173ee);imm(114,'xori',10,8,2);jump(118,38)
    elif role=='status':
        li(0,15,2);branch(2,'beq',10,15,26);branch(6,'bltu',10,15,74)
        addi(10,10,10,-17);imm(12,'andi',10,10,255);li(16,15,1);branch(18,'bltu',15,10,74);tail(22,0x17442)
        bz(26,'bnez',11,22);load(28,15,12,1,1);branch(32,'bne',15,10,22)
        load(36,14,12,2,1);upper(40,15);load(44,15,15,660,1);branch(48,'bne',14,15,22)
        load(52,14,12,3,1);upper(56,15);load(60,15,15,645,1);branch(64,'bne',14,15,22)
        li(68,10,0);tail(70,0x173ee);e(74,'jr',rs1=1)
    elif role=='constructor':
        addi(0,2,2,-48);store(2,8,2,40);lui(4,8,0x40000);load(8,15,8,72);store(10,9,2,36)
        constant(12,9,0x1fff5000,428);store(20,1,2,44);addi(22,12,0,268);li(26,11,0);mv(28,10,9);indirect(30)
        load(32,15,8,128);constant(36,10,0,-406);indirect(44);store(46,10,9,0,1)
        load(50,15,8,72);mv(52,10,2);addi(54,12,0,32);li(58,11,0);indirect(60)
        lui(62,15,0x8e89c000);addi(66,15,15,-298);store(70,15,2,8)
        lui(72,15,0x555000);addi(76,15,15,1365);store(80,15,2,12)
        lui(82,15,0x2000);addi(84,15,15,1281);store(88,15,2,0,2)
        constant(92,15,0,-342);store(100,15,2,16);li(102,15,4);store(104,15,2,25,1)
        load(108,15,8,452);mv(112,10,2);indirect(114)
        restore(((116,1,44),(118,8,40),(120,9,36)));addi(122,2,2,48);e(124,'jr',rs1=1)
    else:raise RuntimeError('unknown payload-consumer role')
    return s


def body(raw,role,pc,size,count,store_count,digest):
    n=previous.decode(raw,pc);expected=specs(role,pc)
    check(set(n)==set(expected),'consumer complete boundaries '+role)
    for p,f in expected.items():init.g(n,p,'consumer '+role+' instruction '+hex(p-pc),**f)
    edges={};calls=[];exits=[]
    external={('state',0xc750):0x12a08,('handoff',0xc796):0xc6a8,('retry',0x1745c):0x173ee,
              ('status',0x17504):0x17442,('status',0x17534):0x173ee}
    for p,d in n.items():
        if d['op']=='jr':
            qs=[]
            if d['rs1']!=1:
                check(d['rs1']==6 and (role,p) in (('finish',0x17438),('retry',0x17474)),'consumer indirect tail register')
                exits.append({'pc':hex(p),'kind':'indirect tail','target':'captured T1 & ~1','link_written':False})
        elif d['op']=='jump' or (d['op']=='jal' and d['rd']==0):qs=[d['target']]
        elif d['op'] in ('beq','bne','beqz','bnez','bge','bltu','bgeu'):qs=[p+d['size'],d['target']]
        else:qs=[p+d['size']]
        for q in qs:
            if q not in n:
                check(external.get((role,p))==q,'consumer explicit external tail')
                exits.append({'pc':hex(p),'kind':'direct tail','target':hex(q),'link_written':False})
        edges[p]=qs
        if d['op']=='call_indirect' or (d['op']=='jal' and d['rd']==1):calls.append({'pc':hex(p),'link':hex(p+d['size']),
            'target':hex(d['target']) if 'target' in d else 'fresh A5 & ~1','normal_return_proved':False})
    seen=set();active=set();back=[]
    def visit(p):
        if p not in n or p in seen:return
        seen.add(p);active.add(p)
        for q in edges[p]:
            if q in active:back.append([p,q])
            else:visit(q)
        active.remove(p)
    visit(pc);check(seen==set(n) and not back,'consumer complete local acyclic CFG '+role)
    stores=[d for d in n.values() if d['op']=='store'];writes=sorted({d['rd'] for d in n.values() if d.get('rd',0)})
    check(len(raw)==size and len(n)==count and len(stores)==store_count and sha256(raw).hexdigest()==digest,'consumer complete identity '+role)
    if role=='state':check(not calls and writes==[12,13,14,15] and all(d['rs1']==10 and d['width']==1 for d in stores),
                           'state byte-only output/no pointer/context stores')
    return {'start':hex(pc),'end_exclusive':hex(pc+size),'bytes':size,'sha256':digest,'instructions':list(n.values()),
        'stores':stores,'calls':calls,'terminal_external_edges':exits,'encoded_GPR_writes':writes,
        'conditional_normal_return_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()}}


def derive(app,carriers,header,coverage):
    parent=previous.derive(app,carriers,header,coverage)
    bodies={r:body(take(app,p,size),r,p,size,n,stores,h) for r,p,size,n,stores,h in DETAILS}
    check(any(c['target']==bodies['handoff']['start'] for c in parent['bodies']['consume']['calls']),'event-consumer stack handoff join')
    hand={d['pc']:d for d in bodies['handoff']['instructions']};stateptr=(0xc78c+hand[0xc78c]['imm']+hand[0xc790]['imm'])&MASK
    check(stateptr==0x2000c290,'handoff stable object literal')
    finish={d['pc']:d for d in bodies['finish']['instructions']};addresses={}
    for key,p in (('stop_task_byte',0x173fe),('control_clear',0x17408),('length_clear',0x17410),('callback_base',0x17418),('callback_clear',0x1742e)):
        addresses[key]=hex((p+finish[p]['imm']+finish[p+4]['imm'])&MASK)
    check(addresses=={'stop_task_byte':'0x2000c7a0','control_clear':'0x2000c7a8','length_clear':'0x2000c7a9',
        'callback_base':'0x2000c7a0','callback_clear':'0x2000c7a4'},'callback consumer absolute field identities')
    check(parent['submission_fields']['callback_word']==addresses['callback_clear'] and
          parent['submission_fields']['gate_length']==addresses['length_clear'],'submission writer to callback consumer join')
    ctor={d['pc']:d for d in bodies['constructor']['instructions']}
    constants={name:hex((p+ctor[p]['imm']+ctor[p+4]['imm'])&MASK) for name,p in
        (('state_base',0x175f4),('registered_task',0x1760c),('status_callback',0x17644))}
    check(constants=={'state_base':'0x2000c7a0','registered_task':'0x17476','status_callback':'0x174ee'},'constructor task/status source constants')
    aliases={}
    for name,index in ((b'RF_Config',100),(b'RF_Tx',102),(b'RF_Shut',103)):
        check(re.search(rb'^\s*#define\s+'+name+rb'\s+[^\r\n]*BLE_LIB_JT\(\s*'+str(index).encode()+rb'\s*\)',header,re.M) is not None,
              'consumer SDK alias '+name.decode())
        aliases[name.decode()]={'slot':hex(0x40034+4*index),'candidate_targets':[hex(init.binding.word(d,0x40034+4*index)&~1) for d in carriers],
            'installed_binding_proved':False}
    check(sum(b['bytes'] for b in bodies.values())==698 and sum(len(b['instructions']) for b in bodies.values())==242 and
          sum(len(b['stores']) for b in bodies.values())==24,'consumer body census')
    return {'schema':'TSL9-payload-consumers-static-v1','profile':init.timer.PROFILE,
        'scope':'7 complete APP bodies698B/242instructions/24stores; previous copy/submission/event chain revalidated',
        'bodies':bodies,'SDK_aliases':aliases,'finish_addresses':addresses,'constructor_constants':constants,
        'stack_handoff':{'copy_request':'fresh4004c(then-live GP+220,entry source,7), scalar not tested',
            'tail':'restore frame; explicit A0=2000c290; tail C6a8; no direct source-pointer field store, but ambient A1 may retain original source across this and later tails',
            'reference_copy_bridge':'if actual copy matches reference and accesses/context/nonalias hold, source bytes copied before helper returns; later destination preservation still conditional',
            'nominal_packet_base':'0x200040dc','output_object':'0x2000c290','actual_copy_or_input_pointer_retention_proved':False},
        'state_contract':{'input':'A0=output object O; packet P=then-live GP+220; no nested calls or frame',
            'gate':'fresh U32[P] bit9 must be1; next fresh bits10..15 nonzero enable byte stores O+4..6',
            'composite':'fresh U32[P]>>16 OR ((fresh U32[P+4]&ff)<<16), sequential low3bytes to O+4..6',
            'numeric_field':'multiple distinct fresh (U32[P+4]>>8)&31 reads; compare10/20, byte truncate before min100, fresh O+7 highbit preservation',
            'stable_snapshot_summary':'only with equal packet fields: n1..10 adds10*n to old low7, n11..20 sets10*(n-10), n>20 sets0; n0 follows earlier changed flag',
            'send_gate':'after bit9 gate and O+4..6 store path or O+7 update path: fresh U8[O+2]!=0 then fresh P+4 bits13..14 ->low2 of fresh O+8, tail12a08(O); earlier byte stores not rolled back if gate0',
            'nominal_copy7_excludes_packet_byte7':True,'word_Pplus4_read_requires_byte7_valid':True,
            'selected_fields_do_not_depend_on_packet_bytes6_or7':True,'downstream_output_object_retention_proved':False},
        'finish_contract':{'entry':'full entry value saved S0; fresh4005c(fresh U8[2000c7a0],2), scalar not tested',
            'order':['clear2000c7a8','clear2000c7a9','capture fresh U32[2000c7a4] into T1','if nonzero A0=saved entry, restorecontext,clear2000c7a4,tail capturedT1'],
            'null_callback_reply':'then-live A0, potentially stop reply; no normalization',
            'callback_reply_or_success_tested':False,'capture_and_clear_atomic_proved':False,
            'post_callback_local_cleanup':False,'payload_header_directly_cleared':False},
        'retry_contract':{'equation':'u=(fresh U8[2000c7a8]-1)&255; SB before branch',
            'u_zero':'tail173ee(A0=1)','u_nonzero':'tail fresh40058(fresh task,1,2)',
            'old_zero_wraps_to255':True,'unconditional_retry_bound_proved':False},
        'task_contract':{'priority_reply':'low16 bit15 first->full E XOR8000; elsebit0->E XOR1; elsebit1->E XOR2; neither->0',
            'bit15':'fresh4006c(entry task), if reply nonzero fresh40068(reply), scalars not otherwise tested',
            'bit0':'fresh401d0() then fresh401cc(2000c7aa,fresh U8[2000c7a9],255,255); replies not tested',
            'bit1':'173ee(A0=1), callback result then overwritten by E XOR2'},
        'status_contract':{'full_status2':'A1 must0; ordered fresh bytes A2+1==2,A2+2==freshc7aa,A2+3==freshc7ab ->tail173ee(0); mismatches tail17442',
            'status_less2':'RET','other_status':'if low8(status-17)<=1 tail17442 else RET with transformed A0',
            'packet_null_or_extent_guard':False,'provider_really_invokes_this_callback_proved':False},
        'constructor_contract':{'requests':['fresh40048(2000c7a0,0,268)','fresh40080(A0=17476), low8 reply stored2000c7a0',
            'fresh40048(SP,0,32)','local stack fields; fresh401c4(A0=SP)'],
            'local_fields':['SW8e89bed6 atSP+8','SW00555555 atSP+12','SH2501 atSP+0','SW174ee atSP+16','SB4 atSP+25'],
            'scalar_results_tested':False,'config_stack_pointer_copy_or_retention_proved':False},
        'premises':['original bytes/conditional ISA and valid packet/object/stack/MMIO access',
            'normal callees and needed GP/S/SP/RA/frame preservation; no adverse alias or unaccounted writer/IRQ/reentry',
            'fresh packet/header/length/callback/count values equated only with separate evidence',
            'API/candidate words are not installed identity or physical RF execution/delivery evidence'],
        'remaining_boundaries':['12a08 output-object retention and later consumption','RF_Config stack config retention/callback delivery',
            'RF/provider effects and global field writers','actual task IDs, saved callback lifetime and reentrancy'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(app):
    partition=[0,0,0,0]
    for E in range(65536):
        k=0 if E&0x8000 else 1 if E&1 else 2 if E&2 else 3;partition[k]+=1
        reply=E^(0x8000 if k==0 else 1 if k==1 else 2) if k<3 else 0
        check(k==3 or not reply&(0x8000 if k==0 else 1 if k==1 else 2),'transport task reply bit')
    check(partition==[32768,16384,8192,8192],'transport task priority partition')
    for old in range(256):check(((old-1)&255)==(old-1)%256,'retry decrement byte wrap')
    check(((0-1)&255)==255 and [x for x in range(256) if ((x-1)&255)==0]==[1],'only old1 selects zero-retry tail')
    for status in range(65536):
        if status!=2 and status>=2:check((((status-17)&255)<=1)==((status&255) in (17,18)),'full status lowbyte classifier')
    check(((273-17)&255)==0,'wide status17 lowbyte example')
    for n in range(1,32):
        for old in range(256):
            low=min(((old&127)+10*n)&255,100) if n<=10 else 10*(n-10) if n<=20 else 0
            out=(old&128)|(low&127)
            check(out&128==old&128 and out&127<=100,'stable-field output byte partition')
    check(min((0+10*26)&255,100)==4,'raw truncate before cap with independent fresh field')
    by_role={d[0]:d for d in DETAILS}
    cases=(('handoff',14,1<<20),('handoff',26,1<<20),('state',10,0x80),('state',44,1<<20),
           ('state',102,1<<20),('state',138,1<<20),('state',168,1<<21),
           ('finish',20,1<<20),('finish',50,0x80),('finish',68,1<<20),('finish',74,0x80),
           ('retry',8,4),('task',16,0x1000),('task',80,1<<20),
           ('status',28,1<<20),('status',64,0x1000),('constructor',100,4),('constructor',114,0x80))
    for role,off,flip in cases:
        _,pc,size,count,stores,digest=by_role[role];raw=bytearray(take(app,pc,size));n=previous.decode(raw,pc);w=n[pc+off]['size']
        raw[off:off+w]=(int.from_bytes(raw[off:off+w],'little')^flip).to_bytes(w,'little')
        try:body(raw,role,pc,size,count,stores,digest)
        except RuntimeError as e:check(str(e)=='consumer '+role+' instruction '+hex(off),'unexpected consumer mutation guard '+str(e))
        else:raise RuntimeError('consumer mutation escaped')
    print('PASS: 65536 priority cases + 65536 status cases; 256 retry bytes; 7936 stable-field cases; 18 specified raw mutations')


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
    else:check(OUT.read_bytes()==output,'payload consumers exact ledger replay')
    print('PASS: 7 complete APP bodies698B/242instructions/24stores; stack-to-global and saved-callback capture/clear/tail joins')
    print('PASS: exact ledger replay; copy/callback/config retention/physical RF/installed binding UNPROVED; NO target execution')


if __name__=='__main__':main()
