"""Candidate outer event dispatcher: complete operands and conditional CFG.

Host bytes/bitfields only; no target ISA, scheduler, provider, list or MMIO
execution/emulation. Fresh read identities and opaque calls remain separate.
"""
import argparse
import json
import re
from hashlib import sha256
from pathlib import Path
import check_v4160_linked_node_consumer_static as previous

init,ROOT,MASK=previous.init,previous.ROOT,previous.MASK
check=init.check
ENTRY=0x200007d0
OUT=Path(__file__).with_name('v4160-event-dispatch-static.json')
DETAILS=((0x40a40,0x20002610,0x63dd0,'bd63b35b352cf367a879d5d7c282905295538eaa7b18b16d294765447cbe0a40'),
         (0x40a80,0x2000265c,0x63eba,'ad64465c017cf16b6e1b0c5d6dbb27567cfce78ef64d96171cd52f69f5d478e1'))


def specs(M,B,F,direct):
    G=0x20003000;rows={}
    def e(o,op,**f):rows[ENTRY+o]=dict(op=op,**f)
    def lui(o,r):e(o,'lui',rd=r,imm=G)
    def addi(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def load(o,r,b,v=0,w=4,**f):e(o,'load',rd=r,rs1=b,imm=v,width=w,**f)
    def store(o,r,b,v=0,w=4,**f):e(o,'store',rs2=r,rs1=b,imm=v,width=w,**f)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    def branch(o,op,a,b,t):e(o,op,rs1=a,rs2=b,target=ENTRY+t)
    def bz(o,op,r,t):e(o,op,rs1=r,target=ENTRY+t)
    def jump(o,t):e(o,'jump',target=ENTRY+t)
    def binary(o,op,r,a,b):e(o,op,rd=r,rs1=a,rs2=b)
    def shift(o,r,a,n):e(o,'slli',rd=r,rs1=a,imm=n)
    def call(o):e(o,'call_indirect',rd=1,rs1=15)
    def qload(o,r,b,v,w,name):load(o,r,b,v,w,mnemonic='qk.c.'+name)
    addi(0,2,2,-32);store(2,9,2,20);lui(4,9);store(8,8,2,24);store(10,18,2,16)
    addi(12,15,9,B-G)
    for o,r,v in ((16,1,28),(18,19,12),(20,20,8),(22,21,4)):store(o,r,2,v)
    qload(24,15,15,12,1,'lbu');lui(26,18);addi(30,9,9,B-G);addi(34,8,18,M+44-G)
    bz(38,'bnez',15,74);lui(40,15);addi(44,15,15,F-G);qload(48,14,15,5,1,'lbu')
    e(50,'andi',rd=14,rs1=14,imm=1);bz(52,'beqz',14,74);qload(54,14,15,7,1,'lbu')
    li(56,13,6);branch(58,'bne',13,14,240);store(62,0,15,5,1)
    e(66,'jal',rd=1,target=direct);load(70,15,8,12);call(72);load(74,15,8,8)
    bz(76,'beqz',15,80);call(78);lui(80,8);lui(84,19);addi(88,15,8,M-G)
    load(92,14,19,M+72-G);qload(96,12,15,1,1,'lbu');addi(98,20,8,M-G)
    load(102,15,8,M-G,1);shift(106,13,15,1);binary(110,'add',13,13,14)
    qload(112,13,13,0,2,'lhu');bz(114,'beqz',13,260);load(116,15,8,M-G,1)
    branch(120,'bltu',15,12,276);store(124,0,8,M-G,1);lui(128,8)
    addi(132,15,8,F-G);qload(136,15,15,9,1,'lbu');addi(138,8,8,F-G)
    branch(142,'bne',15,0,400);lui(146,15);load(150,15,15,M+68-G)
    bz(154,'beqz',15,382);load(156,15,9,4);store(158,15,20,16)
    e(162,'jal',rd=1,target=previous.ENTRY);lui(164,15);load(168,15,15,M+120-G)
    bz(172,'beqz',15,382);qload(174,15,8,7,1,'lbu');li(176,14,4)
    branch(178,'bltu',14,15,382);lui(182,15);addi(186,15,15,F+76-G)
    qload(190,15,15,12,1,'lbu');e(192,'andi',rd=15,rs1=15,imm=4)
    bz(194,'bnez',15,382);lui(196,15);load(200,15,15,B-824-G,1)
    e(204,'andi',rd=15,rs1=15,imm=255);bz(208,'bnez',15,382)
    load(210,13,20,1,1);load(214,12,19,M+72-G);branch(218,'blt',15,13,424)
    for o,r,v in ((222,8,24),(224,1,28),(226,9,20),(228,18,16),(230,19,12),(232,20,8),(234,21,4)):load(o,r,2,v)
    addi(236,2,2,32);e(238,'jump',target=0x2000061a)
    qload(240,14,15,7,1,'lbu');li(242,13,7);branch(244,'bne',13,14,74)
    store(248,0,15,5,1);e(252,'jal',rd=1,target=direct);load(256,15,8,16);jump(258,72)
    addi(260,15,15,1);e(262,'andi',rd=15,rs1=15,imm=255);store(266,15,8,M-G,1)
    branch(270,'bltu',15,12,102);jump(274,116)
    shift(276,15,15,1);binary(278,'add',14,14,15);qload(280,11,14,0,2,'lhu')
    store(282,0,14,0,2);load(286,10,8,M-G,1);lui(290,15);load(294,15,15,M+40-G)
    shift(298,14,10,2);lui(302,21);binary(306,'add',15,15,14);load(308,15,15)
    store(310,0,21,M+64-G,2);call(314);load(316,15,21,M+64-G,2)
    load(320,14,8,M-G,1);e(324,'xori',rd=15,rs1=15,imm=-1)
    binary(328,'and',10,10,15);shift(330,15,14,1);load(334,14,19,M+72-G)
    binary(338,'add',14,14,15);qload(340,15,14,0,2,'lhu');binary(342,'or',10,10,15)
    store(344,10,14,0,2,mnemonic='qk.c.sh');load(346,15,8,M-G,1)
    bz(350,'beqz',15,358);addi(352,15,15,1);store(354,15,8,M-G,1)
    load(358,15,18,M+44-G);bz(362,'beqz',15,370);call(364);store(366,0,18,M+44-G)
    load(370,14,8,M-G,1);load(374,15,20,1,1);branch(378,'bgeu',14,15,124)
    for o,r,v in ((382,1,28),(384,8,24),(386,9,20),(388,18,16),(390,19,12),(392,20,8),(394,21,4)):load(o,r,2,v)
    addi(396,2,2,32);e(398,'jr',rs1=1);qload(400,15,8,7,1,'lbu')
    e(402,'andi',rd=15,rs1=15,imm=255);branch(406,'bne',15,0,146)
    store(410,0,8,9,1)
    # +414/+418 AUIPC/JALR is pinned independently with runtime PC.
    jump(422,146);shift(424,14,15,1);binary(428,'add',14,14,12)
    qload(430,14,14,0,2,'lhu');bz(432,'bnez',14,382);addi(434,15,15,1);jump(436,218)
    return rows


def body(raw,M,B,F,direct,pair_target,digest):
    n=previous.previous.previous.decode(raw,ENTRY);expected=specs(M,B,F,direct)
    check(set(n)==set(expected)|{ENTRY+414,ENTRY+418},'dispatcher complete boundaries')
    for pc,f in expected.items():init.g(n,pc,'dispatcher instruction '+hex(pc-ENTRY),**f)
    init.pair(n,ENTRY+414,1,pair_target,'dispatcher opaque runtime target pair')
    edges={};back=[];seen=set();active=set()
    for pc,d in n.items():
        if d['op']=='jr':qs=[]
        elif d['op']=='jump':qs=[d['target']]
        elif d['op'] in ('beq','bne','blt','bltu','bgeu','beqz','bnez'):qs=[pc+d['size'],d['target']]
        else:qs=[pc+d['size']]
        check(all(q in n or (pc==ENTRY+238 and q==0x2000061a) for q in qs),'dispatcher bounded edge')
        edges[pc]=qs
    def visit(pc):
        if pc not in n:return
        if pc in active:return
        if pc in seen:return
        seen.add(pc);active.add(pc)
        for q in edges[pc]:
            if q in active:back.append([hex(pc),hex(q)])
            else:visit(q)
        active.remove(pc)
    visit(ENTRY);check(seen==set(n),'dispatcher full CFG reachability')
    stores=[d for d in n.values() if d['op']=='store']
    writes=sorted({d['rd'] for d in n.values() if d.get('rd',0)})
    check(len(stores)==18 and sum(d['rs1']==2 for d in stores)==7,'dispatcher store census')
    check(len(n)==150 and len(raw)==438 and sha256(raw).hexdigest()==digest,'dispatcher complete identity')
    check(writes==[1,2,8,9,10,11,12,13,14,15,18,19,20,21],'dispatcher GPR writes')
    return {'runtime_start':hex(ENTRY),'runtime_end_exclusive':hex(ENTRY+438),'bytes':438,'sha256':digest,
        'instructions':list(n.values()),'stores':stores,'encoded_GPR_writes':writes,'frame_bytes':32,
        'conditional_normal_return_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},
        'DFS_back_edges':back,'tail_target':'0x2000061a','opaque_direct_target':hex(direct),
        'opaque_pair_target':hex(pair_target),'handler_call':{'pc':hex(ENTRY+314),'link':hex(ENTRY+316),
            'A0':'fresh U8[M] after event-halfword clear','A1':'fresh U16[P0+2*i1] before clear',
            'target':'U32[fresh U32[M+40]+4*A0]','local_null_guard':False},
        'consumer_call':{'pc':hex(ENTRY+162),'target':hex(previous.ENTRY),
            'provider_gate':'fresh U32[M+68] !=0','normal_return':hex(ENTRY+164),
            'same_invocation_event_delivery_proved':False},
        'whole_dispatch_control_save_clear_FENCEI':False,'universal_termination_proved':False,
        'reply':'not normalized: then-live A0 or opaque tail result, not fixed status'}


def derive(app,carriers,header):
    prior=previous.derive(app,carriers,header);post=previous.post.derive(app,carriers,header);profiles=[]
    check(re.search(rb'^#define\s+TMOS_SystemProcess\s+[^\r\n]*BLE_LIB_RAM_JT\(\s*0\s*\)',header,re.M) is not None,'SDK RAM JT0 alias')
    for i,(data,old,(src,direct,pair_target,digest)) in enumerate(zip(carriers,prior['profiles'],DETAILS)):
        M=int(old['metadata_base'],16);B=M+152;F=M+888
        reg=post['profiles'][i]
        check(reg['table_slot']==hex(M+40) and reg['event_table_slot']==hex(M+72) and
              reg['count_byte']==hex(M+1),'dispatcher post-config table/count storage join')
        mapping=init.binding.profile(data,old['label']);copy=mapping['first_copy'];start=int(copy['destination'],16)
        check(start<=ENTRY and ENTRY+438<=int(mapping['first_copy_end_exclusive'],16),'dispatcher mapped extent')
        check(int(copy['source'],16)+ENTRY-start==src,'dispatcher first-copy provenance')
        b=body(init.binding.take(data,src,438),M,B,F,direct,pair_target,digest)
        check(int(old['consumer']['runtime_start'],16)==previous.ENTRY and old['list_head_slot']==hex(M+76),'linked consumer join')
        profiles.append({'label':old['label'],'flash_source':hex(src),'body':b,'metadata_base':hex(M),
            'cursor_slot':hex(M),'count_slot':hex(M+1),'handler_table_pointer_slot':hex(M+40),
            'one_shot_hook_slot':hex(M+44),'return_mask_slot':hex(M+64),'pending_pointer_slot':hex(M+72),
            'post_config_literals':reg['registered_literals'],
            'other_bases':{'B':hex(B),'F':hex(F)},'actual_installed_binding_proved':False})
    return {'schema':'TSL9-event-dispatch-static-v1','profile':init.timer.PROFILE,
        'scope':'2 complete mapped438-byte candidate dispatchers; all150 operands/profile; no scheduler execution',
        'profiles':profiles,'scan':'P0/count0 captured before scan; U8 cursor read then pending load BEFORE bounds check; zero entries advance U8 cursor',
        'delivery':'fresh pending snapshot A1; clear selected halfword; fresh cursor A0/table pointer/handler; clear return mask; unguarded indirect call',
        'writeback':'low16(fresh pending[P1+2*i_after] | (full handler_reply & ~fresh U16[M+64]))',
        'read_identities':'i_probe/i_bound/i_task/i_after/i_increment/i_final and P0/P1 are independent unless preservation proved',
        'cursor_update':'fresh cursor0 stays0; nonzero is incremented then SB low8; optional hook then fresh cursor/count bounds comparison',
        'joins':['post-config writes same M+40/M+72 slots; literal0 at task n only under table/count preservation',
            'literal0 gets absolute task n as A0, not task minus registration start; its group offset is not automatically0',
            'maintenance gate M+68, hint write from fresh [B+4], direct linked consumer, then opaque additional gates'],
        'remaining_boundaries':['RAM JT0 startup pointer source and installed binding','actual IDs/groups, reentrancy and ownership',
            'return-mask writers/semantics','opaque hooks, maintenance callees, tail and MMIO effects'],
        'premises':['supported ISA and first-copy bytes remain applicable; code/frame/data accesses valid',
            'opaque callees return normally with needed S/SP/frame preservation',
            'no adverse alias, unaccounted external writer, interrupt or reentrancy effects',
            'fresh snapshots equated only with separate preservation evidence; scan termination is not unconditional'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    # Host bitfield identities; no scheduler or mutable event-memory model.
    for x in range(65536):
        for mask in (0,1,0x8000,0xffff):
            for pending in (0,0x5555):
                check(((x&(~mask&MASK))|pending)&0xffff==((x&0xffff)&(mask^0xffff))|pending,'return merge low16')
    for x in range(256):check(((x+1)&255)==(x+1)%256,'U8 cursor wrap')
    check(((3&~1)|1)==3,'pending reassertion survives return mask')
    check(255+1==256 and ((255+1)&255)==0,'nonzero cursor may wrap to0')
    M=init.DETAILS[0][5]-80;src,direct,pair_target,digest=DETAILS[0]
    for off,flip in ((92,1<<20),(112,0x20),(120,0x1000),(162,4),(280,0x20),(282,1<<20),
                     (286,1<<20),(294,1<<20),(310,1<<20),(314,0x80),(316,1<<20),
                     (320,1<<20),(328,0x40),(334,1<<20),(344,4),(350,0x80),(354,1<<20)):
        raw=bytearray(init.binding.take(carriers[0],src,438));n=previous.previous.previous.decode(raw,ENTRY);width=n[ENTRY+off]['size']
        raw[off:off+width]=(int.from_bytes(raw[off:off+width],'little')^flip).to_bytes(width,'little')
        try:body(raw,M,M+152,M+888,direct,pair_target,digest)
        except RuntimeError as e:check(str(e)=='dispatcher instruction '+hex(off),'unexpected dispatcher mutation guard '+str(e))
        else:raise RuntimeError('dispatcher mutation escaped')
    print('PASS: 524288 merge identities; 256 cursor cases; 17 specified raw mutations')


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true',help='Create ledger exclusively');o=p.parse_args()
    app=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(app)==76800 and sha256(app).hexdigest()==init.binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK header identity')
    carriers=[]
    for label,folder,tail,size,digest in init.binding.PROFILES:
        data=(ROOT/'analysis/wch-resident-candidate-2026-10-21'/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(data)==size and sha256(data).hexdigest()==digest,'candidate identity '+label);carriers.append(data)
    sources,vectors=init.timer.source_contract();ledger=derive(app,carriers,header)
    ledger['sources'],ledger['official_Xwchc_vectors']=sources,vectors
    tests(carriers);output=(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'event dispatcher exact ledger replay')
    print('PASS: 2 complete bodies, 876 bytes/300 instructions/36 stores; runtime targets and linked-consumer join')
    print('PASS: exact ledger replay; snapshot/clear/call/merge edges conditional; installed binding/ownership/delivery UNPROVED; NO target execution')


if __name__=='__main__':main()
