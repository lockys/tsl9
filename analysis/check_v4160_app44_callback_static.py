"""Complete config+44 APP callback, poll/result leaves and caller reply edge.

Only raw bytes, decoded operands, CFGs and host width/interval algebra are
checked. No target ISA, buffer, callback, polling or MMIO is run/emulated.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_config_buffer_source_static as source

cb,init,ROOT,MASK = source.cb,source.init,source.ROOT,source.MASK
check=init.check
OUT=Path(__file__).with_name('v4160-app44-callback-static.json')
ENTRY,SIZE,DIGEST=0x197f0,364,'ee7d9a35ebc31a363cc5f6efca0ce21d341099694f34aa90185be94995d826a4'
POLL,RESULT=0x18a8e,0x18a66
POLL_SHA='54df366a01082d8608026cdcc1facff8db6e5c1447bb3b66237bd2ad55888349'
RESULT_SHA='3742627de5a8d8a288a2a2a446c3a88b6056a8892352d99777783ea3467b5504'
SAVED=((1,124,0x197fa,0x19920),(9,116,0x197fc,0x19928),(8,120,0x197fe,0x1994e),
 (18,112,0x19800,0x1992a),(19,108,0x19802,0x19932),(20,104,0x19804,0x19934),
 (21,100,0x19806,0x1993c),(22,96,0x19808,0x1993e),(23,92,0x1980a,0x19946),
 (24,88,0x1980c,0x19950),(25,84,0x1980e,0x19952),(26,80,0x19810,0x19954),(27,76,0x19812,0x19956))
# Explicit register-carried snapshot rows: load PC/base/offset, holding GPR,
# restore PC/base/offset, projected physical address (conditional context).
REG_SNAP=((0x1981c,15,24,27,0x198ee,15,24,0x40021018),
 (0x19820,15,4,26,0x198f2,15,4,0x40021004),
 (0x1982c,9,4,25,0x198f6,8,1028,0x40012404),
 (0x19830,9,8,24,0x198fa,8,1032,0x40012408),
 (0x19834,9,44,23,0x198fe,8,1068,0x4001242c),
 (0x19838,9,48,22,0x19902,8,1072,0x40012430),
 (0x1983c,9,52,21,0x19906,8,1076,0x40012434),
 (0x19840,9,12,20,0x1990a,8,1036,0x4001240c),
 (0x19844,9,16,19,0x19910,8,1040,0x40012410),
 (0x19848,9,20,18,0x19914,8,1044,0x40012414))
# Stack-carried snapshots use A5, disjoint from the separately saved GPR frame.
STACK_SNAP=((0x1984c,24,0x19854,4,0x1990e,0x19918),
 (0x19856,28,0x1985c,8,0x1991c,0x19922),
 (0x1985e,32,0x19860,12,0x19926,0x1992c),
 (0x19862,36,0x19864,16,0x19930,0x19936),
 (0x19866,40,0x19868,20,0x1993a,0x19940),
 (0x1986a,56,0x1986c,24,0x19944,0x1994a))
CALLS=((0x19814,0x8520),(0x1986e,0x19124),(0x19874,0x1908c),(0x1987a,0x188e2),
 (0x19896,0x1892e),(0x1989e,0x18986),(0x198a6,0x18a98),(0x198ac,0x18a6e),
 (0x198b8,0x189ae),(0x198c0,0x18996),(0x198ca,POLL),(0x198dc,RESULT),(0x198e6,0x188e2))


def decode(raw,pc):
    nodes,off={},0
    while off<len(raw):
        h=int.from_bytes(raw[off:off+2],'little');size=2 if h&3!=3 else 4
        check(off+size<=len(raw),'APP44 partial instruction')
        chunk,p=raw[off:off+size],pc+off;w=int.from_bytes(chunk,'little')
        if size==4 and w&0xfe00707f==0x3033:
            d=dict(pc=p,size=size,bytes=chunk.hex(),op='sltu',rd=w>>7&31,rs1=w>>15&31,rs2=w>>20&31)
        else:d=cb.decode(chunk,p)[p]
        nodes[p]=d;off+=size
    return nodes


def body_record(raw,pc,n):
    edges,cycles=init.timer.cfg(n,pc)
    return {'start':hex(pc),'end_exclusive':hex(pc+len(raw)),'bytes':len(raw),
        'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),
        'conditional_normal_return_CFG':edges,'cyclic_SCCs':cycles,
        'encoded_GPR_writes':sorted({d['rd'] for d in n.values() if d.get('rd',0)}),
        'store_PCs':[hex(p) for p,d in n.items() if d['op']=='store']}


def callback_contract(raw):
    n=decode(raw,ENTRY);expected={}
    def e(pc,op,**fields):
        check(pc not in expected,'APP44 duplicate independent specification')
        expected[pc]=dict(op=op,**fields)
    def load(pc,rd,base,off):e(pc,'load',rd=rd,rs1=base,imm=off,width=4)
    def store(pc,rs2,base,off,width=4):e(pc,'store',rs2=rs2,rs1=base,imm=off,width=width)
    e(ENTRY,'addi',rd=2,rs1=2,imm=-128)
    e(0x197f2,'addi',rd=12,rs1=0,imm=32);e(0x197f6,'li',rd=11,imm=0)
    e(0x197f8,'addi',rd=10,rs1=2,imm=32)
    for reg,off,save,restore in SAVED:store(save,reg,2,off);load(restore,reg,2,off)
    for pc,target in CALLS:e(pc,'jal',rd=1,target=target)
    e(0x19818,'lui',rd=15,imm=0x40021000);e(0x19824,'lui',rd=15,imm=0x40012000)
    e(0x19828,'addi',rd=9,rs1=15,imm=1024);e(0x19858,'lui',rd=8,imm=0x40012000)
    e(0x198ea,'lui',rd=15,imm=0x40021000)
    for lp,lb,lo,reg,sp,sb,so,_ in REG_SNAP:load(lp,reg,lb,lo);store(sp,reg,sb,so)
    for lp,off,save,stackoff,reload,restore in STACK_SNAP:
        load(lp,15,9,off);store(save,15,2,stackoff);load(reload,15,2,stackoff)
        store(restore,15,8,1024+off)
    for pc in (0x1984e,0x1989a,0x198a2,0x198bc):e(pc,'li',rd=11,imm=1)
    e(0x19850,'addi',rd=10,rs1=0,imm=512);e(0x19872,'lui',rd=10,imm=0xc000)
    for pc in (0x19878,0x19888,0x1989c,0x198a4,0x198b6,0x198be):e(pc,'mv',rd=10,rs2=9)
    e(0x1987e,'lui',rd=14,imm=0xe0000);store(0x19882,14,2,44)
    e(0x19884,'addi',rd=11,rs1=2,imm=32);e(0x19886,'li',rd=14,imm=1);store(0x1988a,14,2,52,1)
    for pc,off in ((0x1988e,32),(0x19890,36),(0x19892,40),(0x19894,48)):store(pc,0,2,off)
    e(0x198aa,'li',rd=10,imm=1)
    for pc,reg,value in ((0x198b0,13,7),(0x198b2,12,1),(0x198b4,11,16),(0x198c8,11,2)):
        e(pc,'li',rd=reg,imm=value)
    e(0x198c4,'mv',rd=15,rs2=9);e(0x198c6,'mv',rd=10,rs2=15)
    e(0x198ce,'lui',rd=15,imm=0x40012000);e(0x198d2,'addi',rd=15,rs1=15,imm=1024)
    e(0x198d6,'beqz',rs1=10,target=0x198c6)
    for pc in (0x198d8,0x198e2):e(pc,'addi',rd=10,rs1=8,imm=1024)
    store(0x198e0,10,2,28);load(0x1991e,14,2,28);e(0x19948,'mv',rd=10,rs2=14)
    e(0x19958,'addi',rd=2,rs1=2,imm=128);e(0x1995a,'jr',rs1=1)
    check(set(n)==set(expected),'APP44 complete independent instruction boundaries')
    for pc,f in expected.items():init.g(n,pc,'APP44 instruction '+hex(pc),**f)
    r=body_record(raw,ENTRY,n)
    check(r['cyclic_SCCs']==[[hex(p) for p in (0x198c6,0x198c8,0x198ca,0x198ce,0x198d2,0x198d6)]],'APP44 poll SCC')
    check(r['encoded_GPR_writes']==[1,2,8,9,10,11,12,13,14,15,18,19,20,21,22,23,24,25,26,27],'APP44 GPR writes')
    stores={pc:d for pc,d in n.items() if d['op']=='store'}
    check(len(stores)==42 and sum(d['rs1']==2 for d in stores.values())==26,'APP44 store census')
    check(all(0<=d['imm'] and d['imm']+d['width']<=128 for d in stores.values() if d['rs1']==2),'APP44 encoded stack store extent')
    # No other local definition can replace the fresh saved result after reload.
    check(not any(d.get('rd')==14 for pc,d in n.items() if 0x1991e<pc<0x19948),'APP44 result A4 path')
    check(not any(d.get('rd')==10 for pc,d in n.items() if pc>0x19948),'APP44 final A0 path')
    check(not any(d['op']=='store' and d['rs1']==2 and set(range(d['imm'],d['imm']+d['width']))&set(range(28,32))
                  for pc,d in n.items() if pc>0x198e0),'APP44 no later local stack-result overwrite')
    check(len(n)==130 and len(raw)==SIZE and sha256(raw).hexdigest()==DIGEST,'APP44 complete body identity')
    r.update(frame_bytes=128,clear_request={'call':'0x19814','target':'0x8520','A0':'then-live SP+32','A1':0,'A2':32,'actual_extent_unproved':True},
        direct_calls=[{'pc':hex(pc),'target':hex(t),'normal_return_assumed':True,'body_expanded_here':t in (POLL,RESULT)} for pc,t in CALLS],
        saved_GPR_slots=[{'register':reg,'SP_offset':off,'save_pc':hex(s),'restore_pc':hex(t)} for reg,off,s,t in SAVED],
        frame_regions={'saved_GPR_words':[76,127],'configuration_request':[32,63],
            'six_MMIO_snapshot_words':[4,27],'result_word':[28,31]},
        normal_reply='fresh U32[then-live SP+28] via A4 to A0; equals earlier result-leaf reply only with saved-word/SP/context preservation',
        unconditional_config_field_preservation_proved=False)
    return r


def leaves_contract(app):
    records=[]
    for pc,size,digest in ((POLL,10,POLL_SHA),(RESULT,8,RESULT_SHA)):
        raw=app[pc-0x8000:pc-0x8000+size];records.append(leaf_contract(raw,pc,digest))
    return records


def leaf_contract(raw,pc,digest):
    n=decode(raw,pc)
    if pc==POLL:
        specs={0:dict(op='load',rd=10,rs1=10,imm=0,width=4),2:dict(op='and',rd=10,rs1=10,rs2=11),
               4:dict(op='sltu',rd=10,rs1=0,rs2=10),8:dict(op='jr',rs1=1)}
    else:
        check(pc==RESULT,'explicit result leaf')
        specs={0:dict(op='load',rd=10,rs1=10,imm=76,width=4),2:dict(op='slli',rd=10,rs1=10,imm=16),
               4:dict(op='srli',rd=10,rs1=10,imm=16),6:dict(op='jr',rs1=1)}
    check(set(n)=={pc+off for off in specs},'APP44 leaf full instruction boundaries')
    for off,f in specs.items():init.g(n,pc+off,'APP44 leaf instruction '+hex(pc+off),**f)
    r=body_record(raw,pc,n)
    check(not r['store_PCs'] and not r['cyclic_SCCs'] and r['encoded_GPR_writes']==[10],'APP44 leaves only A0 written')
    check(sha256(raw).hexdigest()==digest,'APP44 leaf complete identity')
    r['conditional_reply']= '(fresh U32[entry A0] & entry A1) != 0, normalized to 0/1' if pc==POLL else 'fresh U32[entry A0+76] & 0xffff'
    return r


def derive(app,carriers,header):
    previous=source.derive(app,carriers,header)
    main=callback_contract(app[ENTRY-0x8000:ENTRY-0x8000+SIZE]);leaves=leaves_contract(app)
    snapshots=[]
    for lp,lb,lo,reg,sp,sb,so,address in REG_SNAP:
        nominal_loadbase=0x40021000 if lb==15 else 0x40012400
        nominal_storebase=0x40021000 if sb==15 else 0x40012000
        check(nominal_loadbase+lo==nominal_storebase+so==address,'snapshot projected address equality')
        snapshots.append({'source_pc':hex(lp),'destination_pc':hex(sp),'projected_address':hex(address),
            'storage':'GPR '+str(reg),'source_and_destination_actual_values_equivalent_proved':False})
    for lp,off,sp,stackoff,reload,restore in STACK_SNAP:
        check(0x40012400+off==0x40012000+1024+off,'stack snapshot projected address equality')
        snapshots.append({'source_pc':hex(lp),'save_pc':hex(sp),'reload_pc':hex(reload),'destination_pc':hex(restore),
            'projected_address':hex(0x40012400+off),'storage':'SP+'+str(stackoff),
            'source_and_destination_actual_values_equivalent_proved':False})
    replies=[]
    for data,detail,prior in zip(carriers,init.DETAILS,previous['profiles']):
        pc=detail[2];raw=init.binding.take(data,pc,228);n=decode(raw,pc)
        for off,fields in ((182,dict(op='load',rd=15,rs1=15,imm=44,width=4)),
          (184,dict(op='beqz',rs1=15,target=pc+196)),(186,dict(op='call_indirect',rd=1,rs1=15)),
          (188,dict(op='lui',rd=15,imm=0x20003000)),(192,dict(op='store',rs1=15,rs2=10,imm=detail[9],width=2))):
            init.g(n,pc+off,'APP44 caller instruction '+hex(off),**fields)
        replies.append({'label':prior['label'],'call_pc':hex(pc+186),'callback_field':hex(detail[5]+44),
            'store_pc':hex(pc+192),'store_address':hex(0x20003000+detail[9]),'width':2,
            'same_as_config_length_or_count':False,'actual_result_value_known':False})
    check(len(snapshots)==16 and len({p['projected_address'] for p in snapshots})==16,'16 distinct snapshot pairs')
    check(sum(r['bytes'] for r in [main]+leaves)==382 and sum(len(r['instructions']) for r in [main]+leaves)==138,'APP44 complete body totals')
    return {'schema':'TSL9-APP-config44-callback-static-v1','profile':init.timer.PROFILE,
        'scope':'Complete APP config+44 callback and two directly called read-only leaves; other 11 call sites remain opaque',
        'callback':main,'expanded_leaves':leaves,'conditional_MMIO_snapshot_restore_pairs':snapshots,
        'resident_reply_stores':replies,'APP_callback_binding_source':'builder19a92/19a96 -> value197f0 stored at SP+60, C+44 if C=SP+16',
        'poll':{'call':'0x198ca','mask':2,'initial_base':'then-live S1','subsequent_base':'encoded constant40012400',
            'continuation_test':'reply == 0','local_timeout':False,'physical_completion_semantics_known':False},
        'result':{'call':'0x198dc','argument':'then-live S0+1024','nominal_read_address':'0x4001244c',
            'actual_read_width':4,'normalized_reply_bits':16,'save':'0x198e0 then-live SP+28',
            'intervening_opaque_call':'0x198e6 -> 188e2','reload':'0x1991e then-live SP+28',
            'final_move':'0x19948 A0=A4','conditional_reply_range':[0,65535],
            'actual_reply_range_without_preservation_proved':False},
        'preservation_premises':['matching code and supported ISA semantics; valid nonaliasing frame/accesses',
            'opaque callees return normally and preserve required SP, S0/S1, saved snapshot GPRs and stack words',
            'no interfering writers/interrupts/MMIO effects invalidate saved-word or pointer relationships',
            'poll observes nonzero eventually; source/config/cache writes by other callees separately constrained'],
        'local_write_projection':'26 stack stores and 16 MMIO restore stores under required base preservation',
        'direct_RAM_config_write_identified':False,'all_callee_effects_or_field_preservation_proved':False,
        'unresolved':['8520 clear and peripheral helper effects','real MMIO values/semantics and termination',
            'whole closure config/cache/frame preservation','installed provider/physical profile and pointer lifetime'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(app):
    for value in range(65536):
        for high in (0,0x12340000,0xffff0000):
            word=high|value;check(((word<<16)&MASK)>>16==word&65535,'RV32 low-half extraction')
        check(int(0<(value&2))==((value>>1)&1),'poll normalized bit1 reply')
    # Frame region identities; no target buffer or memory state is allocated.
    regions=(set(range(4,28)),set(range(28,32)),set(range(32,64)),set(range(76,128)))
    check(all(not a&b for i,a in enumerate(regions) for b in regions[i+1:]),'stack region disjointness')
    cases=((ENTRY,0x197f0,'1971','1961'),(ENTRY,0x19854,'3ec2','3ec4'),
      (ENTRY,0x19882,'3ad6','3ad4'),(ENTRY,0x198c8,'8945','9145'),
      (ENTRY,0x198d6,'65d9','65f9'),(ENTRY,0x198e0,'2ace','2acc'),
      (ENTRY,0x198f6,'23229441','23249441'),(ENTRY,0x1991e,'7247','6247'),
      (ENTRY,0x19948,'3a85','3e85'),(POLL,POLL+4,'3335a000','3335b000'),
      (RESULT,RESULT,'6845','2845'),(RESULT,RESULT+4,'4181','4581'))
    for entry,pc,old,new in cases:
        size=SIZE if entry==ENTRY else (10 if entry==POLL else 8)
        raw=bytearray(app[entry-0x8000:entry-0x8000+size]);off=pc-entry
        check(raw[off:off+len(bytes.fromhex(old))]==bytes.fromhex(old),'APP44 mutation source '+hex(pc))
        raw[off:off+len(bytes.fromhex(new))]=bytes.fromhex(new)
        try:
            if entry==ENTRY:callback_contract(raw)
            else:leaf_contract(raw,entry,POLL_SHA if entry==POLL else RESULT_SHA)
        except RuntimeError as error:
            check(str(error)==('APP44 instruction ' if entry==ENTRY else 'APP44 leaf instruction ')+hex(pc),'unexpected APP44 mutation guard '+str(error))
        else:raise RuntimeError('specified APP44 mutation escaped')
    print('PASS: 196608 word extraction cases; 65536 poll-bit cases; 4 disjoint stack regions; 12 specified raw mutations')


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
    tests(app);output=(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'APP44 exact ledger replay')
    print('PASS: 3 complete APP bodies, 382 bytes/138 instructions; 42 store sites; 16 projected snapshot/restore pairs')
    print('PASS: exact ledger replay; low16 reply conditional on saved-word/context integrity; 11 opaque call sites; NO target execution')


if __name__=='__main__':main()
