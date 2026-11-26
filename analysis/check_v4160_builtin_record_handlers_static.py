"""Registered resident record handlers: bytes, CFG and width algebra only.

No target ISA, handler/event scheduler, record arena, queue, allocator,
callback or provider executes or is emulated.
"""
import argparse
import json
import re
from hashlib import sha256
from pathlib import Path
import check_v4160_callback_reply_lifetime_static as previous

init,post,ROOT,MASK=previous.init,previous.post,previous.ROOT,previous.MASK
check,sx=init.check,init.sx
OUT=Path(__file__).with_name('v4160-builtin-record-handlers-static.json')
DIGESTS=(
 ('089d8b189f02f55d102f1dff78ed529c0466ed9b61a01159f8501835bf7d3f8a',
  '4bbf8181a2860d9178a85965cf08dbe0964ffe2bff674f906965efdb2def911c'),
 ('e7837a4729174d7691c7098e7feec36aa60651a6a8888a7e31ebf16588ce44f1',
  'fb4383055ffeee8c01e8f3867bb8391a4c39f881a6396f75920dba3a63a14220'))


def decode(raw,pc):
    nodes,off={},0
    while off<len(raw):
        h=int.from_bytes(raw[off:off+2],'little');size=2 if h&3!=3 else 4
        check(off+size<=len(raw),'record handler partial instruction')
        chunk,p=raw[off:off+size],pc+off;w=int.from_bytes(chunk,'little');d=dict(pc=p,bytes=chunk.hex(),size=size)
        if size==4 and w&0xfe00707f==0x40005033:
            d.update(op='sra',rd=w>>7&31,rs1=w>>15&31,rs2=w>>20&31)
        elif size==4 and w&0x707f==0x5063:
            v=(w>>31)<<12|(w>>7&1)<<11|(w>>25&63)<<5|(w>>8&15)<<1
            d.update(op='bge',rs1=w>>15&31,rs2=w>>20&31,target=p+sx(v,13))
        elif size==2 and h&0xfc03==0x8401:
            r=8+(h>>7&7);d.update(op='srai',rd=r,rs1=r,imm=h>>2&31)
        elif size==2 and h&0xfc63==0x8c21:
            r=8+(h>>7&7);d.update(op='xor',rd=r,rs1=r,rs2=8+(h>>2&7))
        else:d=previous.closure.decode(chunk,p)[p]
        nodes[p]=d;off+=size
    return nodes


def specs(pc,kind,pool_offset,free_target):
    rows=[]
    def e(o,op,**f):rows.append((o,dict(op=op,**f)))
    def load(o,rd,base,imm=0):e(o,'load',rd=rd,rs1=base,imm=imm,width=4)
    def store(o,rs2,base,imm=0):e(o,'store',rs2=rs2,rs1=base,imm=imm,width=4)
    if kind==0:
        e(0,'beqz',rs1=11,target=pc+126);e(2,'addi',rd=2,rs1=2,imm=-48)
        for off,reg,sp in ((4,8,40),(6,1,44),(8,9,36),(10,18,32),(12,19,28)):store(off,reg,2,sp)
        e(14,'li',rd=8,imm=0);e(16,'li',rd=14,imm=16)
        e(18,'sra',rd=15,rs1=11,rs2=8);e(22,'andi',rd=15,rs1=15,imm=1)
        e(24,'beqz',rs1=15,target=pc+116);e(26,'slli',rd=10,rs1=10,imm=4)
        e(28,'li',rd=14,imm=12);e(30,'add',rd=10,rs1=10,rs2=8);e(32,'mul',rd=10,rs1=10,rs2=14)
        e(36,'lui',rd=15,imm=0x20003000);load(40,18,15,pool_offset)
        e(44,'li',rd=9,imm=1);e(46,'sll',rd=9,rs1=9,rs2=8)
        e(50,'slli',rd=9,rs1=9,imm=16);e(52,'srli',rd=9,rs1=9,imm=16)
        e(54,'mv',rd=19,rs2=15);e(56,'add',rd=18,rs1=18,rs2=10);load(58,14,18)
        e(62,'beqz',rs1=14,target=pc+74);load(64,10,18,4);store(68,11,2,12)
        e(70,'call_indirect',rd=1,rs1=14);load(72,11,2,12)
        e(74,'li',rd=14,imm=12);e(76,'mul',rd=8,rs1=8,rs2=14);load(80,15,19,pool_offset)
        e(84,'add',rd=8,rs1=8,rs2=15);load(86,15,8,8);e(88,'bnez',rs1=15,target=pc+98)
        store(90,0,18);store(94,0,18,4)
        load(98,1,2,44);load(100,8,2,40);e(102,'xor',rd=11,rs1=11,rs2=9)
        load(104,18,2,32);load(106,9,2,36);load(108,19,2,28)
        e(110,'mv',rd=10,rs2=11);e(112,'addi',rd=2,rs1=2,imm=48);e(114,'jr',rs1=1)
        e(116,'addi',rd=8,rs1=8,imm=1);e(118,'bne',rs1=8,rs2=14,target=pc+18)
        e(122,'li',rd=9,imm=0);e(124,'jump',target=pc+98);e(126,'mv',rd=10,rs2=11);e(128,'jr',rs1=1)
    else:
        e(0,'addi',rd=2,rs1=2,imm=-16);e(2,'slli',rd=14,rs1=11,imm=16)
        for off,reg,sp in ((6,8,8),(8,1,12),(10,9,4),(12,18,0)):store(off,reg,2,sp)
        e(14,'srai',rd=14,rs1=14,imm=16);e(16,'mv',rd=8,rs2=11)
        e(18,'bge',rs1=14,rs2=0,target=pc+52)
        # +22/+26 AUIPC/JALR pair is guarded numerically outside this table.
        e(30,'beqz',rs1=10,target=pc+34);e(32,'jal',rd=1,target=free_target)
        e(34,'lui',rd=15,imm=0x8000);e(36,'xor',rd=8,rs1=8,rs2=15);e(38,'mv',rd=10,rs2=8)
        for off,reg,sp in ((40,1,12),(42,8,8),(44,9,4),(46,18,0)):load(off,reg,2,sp)
        e(48,'addi',rd=2,rs1=2,imm=16);e(50,'jr',rs1=1)
        e(52,'beqz',rs1=11,target=pc+38);e(54,'mv',rd=15,rs2=10);e(56,'li',rd=14,imm=0)
        e(58,'li',rd=12,imm=16);e(60,'sra',rd=13,rs1=8,rs2=14);e(64,'andi',rd=13,rs1=13,imm=1)
        e(66,'beqz',rs1=13,target=pc+120);e(68,'slli',rd=15,rs1=15,imm=4)
        e(70,'add',rd=15,rs1=15,rs2=14);e(72,'li',rd=13,imm=12);e(74,'mul',rd=15,rs1=15,rs2=13)
        e(78,'lui',rd=13,imm=0x20003000);load(82,18,13,pool_offset)
        e(86,'li',rd=9,imm=1);e(88,'sll',rd=9,rs1=9,rs2=14)
        e(92,'slli',rd=9,rs1=9,imm=16);e(94,'srli',rd=9,rs1=9,imm=16)
        e(96,'add',rd=18,rs1=18,rs2=15);load(98,15,18);load(102,10,18,4)
        e(106,'call_indirect',rd=1,rs1=15);store(108,0,18);store(112,0,18,4)
        e(116,'xor',rd=8,rs1=8,rs2=9);e(118,'jump',target=pc+38)
        e(120,'addi',rd=14,rs1=14,imm=1);e(122,'bne',rs1=14,rs2=12,target=pc+60)
        e(126,'li',rd=9,imm=0);e(128,'jump',target=pc+116)
    return {pc+o:f for o,f in rows}


def body(raw,pc,kind,pool_offset,free_target,digest):
    n=decode(raw,pc);expected=specs(pc,kind,pool_offset,free_target)
    extra={pc+22,pc+26} if kind else set()
    check(set(n)==set(expected)|extra,'handler complete instruction boundaries')
    for p,f in expected.items():init.g(n,p,'handler'+str(kind)+' instruction '+hex(p-pc),**f)
    if kind:init.pair(n,pc+22,1,0x2000028c,'handler1 receive pair target')
    # Only topology is relabeled; original signed BGE operands remain guarded.
    topology={p:dict(d,op='bne') if d['op']=='bge' else d for p,d in n.items()}
    edges,cycles=init.timer.cfg(topology,pc)
    loop=(18,22,24,116,118) if kind==0 else (60,64,66,120,122)
    check(cycles==[[hex(pc+o) for o in loop]],'handler scan SCC')
    writes=sorted({d['rd'] for d in n.values() if d.get('rd',0)})
    want=[1,2,8,9,10,11,14,15,18,19] if kind==0 else [1,2,8,9,10,12,13,14,15,18]
    check(writes==want,'handler encoded GPR writes')
    stores=[p for p,d in n.items() if d['op']=='store']
    want_stores=(4,6,8,10,12,68,90,94) if kind==0 else (6,8,10,12,108,112)
    check(stores==[pc+o for o in want_stores],'handler complete store census')
    call_off=70 if kind==0 else 106
    check(not any(d.get('rs1')==10 or d.get('rs2')==10 for p,d in n.items() if p>pc+call_off),
          'handler callback scalar A0 reply has no local consumer')
    check(len(raw)==130 and len(n)==(53 if kind==0 else 51) and sha256(raw).hexdigest()==digest,
          'handler complete body identity')
    return {'kind':kind,'start':hex(pc),'end_exclusive':hex(pc+130),'bytes':130,'sha256':digest,
        'instructions':list(n.values()),'conditional_normal_return_CFG':edges,'cyclic_SCCs':cycles,
        'encoded_GPR_writes':writes,'store_PCs':[hex(p) for p in stores],
        'record_callback':{'pc':hex(pc+call_off),'pointer_source':'selected record+0','A0':'fresh U32[selected record+4]',
            'effective_target':'fresh callback word with JALR bit0 cleared','ambient_registers_remain_observable':True,
            'A1':'full entry event word E','A2':'ambient' if kind==0 else 16,
            'null_guard_before_call':kind==0,'scalar_A0_reply_used':False},
        'frame_bytes':48 if kind==0 else 16,'creates_frame_for_zero_input':kind==1,
        'clear_word_offsets':[0,4],'clears_record_plus8':False,
        'clear_condition':'fresh U32[Pprime+12*k+8] == 0 after optional call' if kind==0 else 'normal return from record callback',
        'clear_base':'then-live S2; equals original selected record only with preservation',
        'normal_return':'preserved full E XOR low16(1<<k), or full E if no selected low bit; kind1 bit15 path XOR8000',
        'unconditional_context_or_termination_proved':False}


def derive(app,carriers,header):
    old=previous.derive(app,carriers,header);profiles=[];api={}
    for name,jt in ((b'tmos_msg_deallocate',13),(b'tmos_msg_receive',14)):
        match=re.search(rb'^#define\s+'+name+rb'\s+[^\r\n]*BLE_LIB_JT\(\s*(\d+)\s*\)',header,re.M)
        check(match is not None and int(match[1])==jt,'handler SDK alias '+name.decode())
        api[name.decode()]={'JT':jt,'slot':hex(0x40034+4*jt)}
    for i,(data,prior) in enumerate(zip(carriers,old['profiles'])):
        d=post.DETAILS[i];p0,p1=d[4:6];C=init.DETAILS[i][5];Pslot=C+64
        free_target=init.binding.word(data,0x40068)
        check(free_target==(0x431ba if i==0 else 0x43246),'handler free slot alias')
        check(init.binding.word(data,0x4006c)==0x2000028c,'handler receive slot alias')
        mapping=init.binding.profile(data,prior['label']);copy=mapping['first_copy']
        receive_target=0x2000028c;load_start=int(copy['destination'],16)
        check(load_start<=receive_target and receive_target+16<=int(mapping['first_copy_end_exclusive'],16),
              'receive prefix inside complete first-copy mapping')
        receive_source=int(copy['source'],16)+receive_target-load_start
        receive_prefix=init.binding.take(data,receive_source,16)
        b0=body(init.binding.take(data,p0,130),p0,0,Pslot-0x20003000,free_target,DIGESTS[i][0])
        b1=body(init.binding.take(data,p1,130),p1,1,Pslot-0x20003000,free_target,DIGESTS[i][1])
        profiles.append({'label':prior['label'],'literal_handlers':[b0,b1],
            'post_config_registration_values':[hex(p0),hex(p1),hex(p1)],
            'registration_executes_handlers':False,'actual_outer_dispatch_and_arguments_proved':False,
            'arena_pointer_slot':hex(Pslot),'outer_handler_table_pointer_slot':hex(C-80+40),
            'arena_pointer_storage_slot_differs_from_outer_table_pointer_storage_slot':True,
            'actual_pointer_values_disjoint_proved':False,
            'record_address_with_context':'(fresh P + 12*((full entry A0<<4)+selected bit k)) mod2^32',
            'kind0_flag_read_address_with_context':'(fresh Pprime + 12*k +8) mod2^32; no group term',
            'selected_record_and_flag_test_same_record_unconditionally':False,
            'local_group_capacity_or_record_pointer_guard':False,
            'kind1_bit15_priority':{'test':'signed32((full E<<16) mod2^32) <0 after SRAI16; exactly original bit15',
                'receive_target':'0x2000028c','receive_flash_source':hex(receive_source),
                'receive_prefix16_sha256':sha256(receive_prefix).hexdigest(),
                'A0_before_receive':'full entry group A0; ambient arguments remain observable',
                'free_target':hex(free_target),'free_argument':'nonnull receive reply A0',
                'free_scalar_reply_checked':False,'clears_bit15_even_on_zero_receive_reply_with_context':True,
                'queue_provider_and_free_effects_proved_here':False}})
    check(sum(len(b['instructions']) for p in profiles for b in p['literal_handlers'])==208,'four handler instruction total')
    check(sum(len(b['store_PCs']) for p in profiles for b in p['literal_handlers'])==28,'four handler store total')
    return {'schema':'TSL9-builtin-record-handlers-static-v1','profile':init.timer.PROFILE,
        'scope':'4 complete candidate literal handlers; original registration/data provenance revalidated; no scheduler execution',
        'SDK_aliases':api,'profiles':profiles,
        'bitmap_scan':'first set bit among bits0..15 only; high16 bits retained in XOR reply with required context',
        'kind1_priority':'bit15 branch precedes scan; ordinary hits then limited0..14',
        'normal_invocation_max_selected_bits':1,'opaque_calls_normal_return_edges_assumed':True,
        'arena_geometry_if_matching_stable_post_config':'576-byte record prefix =3 groups *16 records *12 bytes',
        'this_proves_group_input_or_runtime_task_ID_bounds':False,
        'ownership':'clearing two record words is not freeing the arena or proving callback payload ownership',
        'premises':['matching candidate code and supported ISA semantics; valid frame/code/record accesses',
            'opaque callees return normally and preserve required SP/S registers/saved event words',
            'arena pointer, frame, code, records and global slots do not adversely alias; external writers separately constrained'],
        'unresolved':['actual installed provider and outer handler dispatch/delivery',
            'record producers, payload lifetime, reentry/concurrent writers','receive/free and arbitrary record callback effects'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    # Host bitfield and modular address identities, without scheduler/records.
    for low in range(65536):
        bit=(low&-low) if low else 0
        check((low^bit)==(low&(low-1)) if low else bit==0,'lowest-bit XOR identity')
        for high in (0,0x80000000,0xffff0000):
            E=high|low;v=(E<<16)&MASK
            check(bool(v&0x80000000)==bool(low&0x8000),'bit15 sign-test identity')
            check(((E^bit)>>16)==(E>>16),'high16 retained by low-bit XOR')
        if low&0x8000:check(((low^0x8000)&0x7fff)==(low&0x7fff),'bit15 priority preserves lower bits')
    for group in range(3):
        for k in range(16):
            off=12*(16*group+k);check(0<=off and off+12<=576,'nominal3-group prefix geometry')
            check((off==12*k)==(group==0),'group term absent from kind0 flag base')
    cases=((0,0,'bdcd','bde5'),(0,40,'03a9c722','03a98722'),
      (0,62,'11c7','11e7'),(0,64,'03254900','03258900'),
      (0,86,'1c44','5c44'),(0,90,'23200900','23240900'),
      (0,102,'a58d','a18d'),(1,14,'4187','4587'),
      (1,30,'11c1','11e1'),(1,98,'83270900','83274900'),
      (1,108,'23200900','23240900'),(1,116,'258c','218c'))
    for kind,off,old,new in cases:
        pc=post.DETAILS[0][4+kind];raw=bytearray(init.binding.take(carriers[0],pc,130))
        check(raw[off:off+len(bytes.fromhex(old))]==bytes.fromhex(old),'handler mutation source '+str(kind)+hex(off))
        raw[off:off+len(bytes.fromhex(new))]=bytes.fromhex(new)
        try:body(raw,pc,kind,init.DETAILS[0][5]+64-0x20003000,0x431ba,DIGESTS[0][kind])
        except RuntimeError as error:check(str(error)=='handler'+str(kind)+' instruction '+hex(off),'unexpected handler mutation guard '+str(error))
        else:raise RuntimeError('handler mutation escaped')
    print('PASS: 65536 lowest-bit masks; 196608 sign/high-bit cases; 48 group/record identities; 12 specified raw mutations')


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true',help='Create ledger exclusively');o=p.parse_args()
    app,header=init.binding.APP.read_bytes(),init.core.outer.HEADER.read_bytes()
    check(len(app)==76800 and sha256(app).hexdigest()==init.binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK header identity')
    carriers=[]
    for label,folder,tail,size,digest in init.binding.PROFILES:
        raw=(ROOT/'analysis/wch-resident-candidate-2026-10-21'/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(raw)==size and sha256(raw).hexdigest()==digest,'candidate identity '+label);carriers.append(raw)
    sources,vectors=init.timer.source_contract();ledger=derive(app,carriers,header)
    ledger['sources'],ledger['official_Xwchc_vectors']=sources,vectors
    tests(carriers);output=(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'record handlers exact ledger replay')
    print('PASS: 4 complete handlers, 520 bytes/208 instructions/28 stores; pool/table distinction; conditional callback cleanup')
    print('PASS: exact ledger replay; slot aliases and bit15 priority; actual dispatch/ownership UNPROVED; NO target execution')


if __name__=='__main__':main()
