"""Complete heap bootstrap/walker/reset contracts, strictly static and algebraic.

No linked-list/heap memory model or ISA/provider/MMIO execution. The nominal
geometry is arithmetic on APP operand values, conditional on stable inputs.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_post_config_static as post

init,ROOT,LIB,MASK=post.init,post.ROOT,post.LIB,post.MASK
OUT=Path(__file__).with_name('v4160-heap-bootstrap-static.json')
DETAILS=(
 (0x430e0,0x43104,0x4329a,
  '8f1f4e0425a68707da3ab94395611ae4190c0c42917bd52688d01d893d8bb035',
  '08fabd9e35085e531dc922755f25e9bbc0b59436321f0e379a98382cafc8bc9f',
  '20b6e8c0db1202a821074e9d59f332d7f232de9d0f830fc7a28a5a310b3ddec6'),
 (0x4316c,0x43190,0x43326,
  'cd3672ac77f49ab93fd3ef6fb79b745701f4a95973976e65b9f8a03d91760f6b',
  '284aeff7f1aeda778c7d5d781d881b2e61dd1b5bc3cde69448e3e93906d98154',
  '17fbeb7a0e85fa837644f95ad788d07d604ce2004353b56869dec4e771ee6e55'))
check=init.check


def decode(raw,start):
    nodes,off={},0
    while off<len(raw):
        h=int.from_bytes(raw[off:off+2],'little');size=2 if h&3!=3 else 4
        check(off+size<=len(raw),'heap bootstrap partial instruction')
        chunk,pc=raw[off:off+size],start+off
        w=int.from_bytes(chunk,'little')
        if size==4 and w&0xfe00707f==0x33:
            d=dict(pc=pc,bytes=chunk.hex(),size=size,op='add',rd=w>>7&31,rs1=w>>15&31,rs2=w>>20&31)
        elif size==2 and h&3==1 and h>>13==4 and h>>10&3==3 and not h&0x1000 and h>>5&3==0:
            r=8+(h>>7&7);d=dict(pc=pc,bytes=chunk.hex(),size=size,op='sub',rd=r,rs1=r,rs2=8+(h>>2&7))
        else:d=post.decode(chunk,pc)[pc]
        nodes[pc]=d;off+=size
    return nodes


def guard_body(nodes,start,rows,role):
    check(set(nodes)=={start+o for o,_,_ in rows},role+' instruction boundaries')
    for off,op,f in rows:init.g(nodes,start+off,role+' instruction '+hex(off),op=op,**f)


def walker_spec(pc,meta):
    g=0x20003000
    return [(0,'lui',dict(rd=15,imm=g)),(4,'lui',dict(rd=14,imm=g)),
      (8,'load',dict(rd=15,rs1=15,imm=meta-8-g,width=4)),
      (12,'load',dict(rd=14,rs1=14,imm=meta-16-g,width=4)),(16,'li',dict(rd=10,imm=0)),
      (18,'bne',dict(rs1=14,rs2=15,target=pc+24)),(22,'jr',dict(rs1=1)),
      (24,'load',dict(rd=13,rs1=15,imm=6,width=2,mnemonic='qk.c.lhu')),
      (26,'bnez',dict(rs1=13,target=pc+32)),
      (28,'load',dict(rd=13,rs1=15,imm=4,width=2,mnemonic='qk.c.lhu')),
      (30,'add',dict(rd=10,rs1=10,rs2=13)),(32,'load',dict(rd=15,rs1=15,imm=0,width=4)),
      (34,'jump',dict(target=pc+18))]


def bootstrap_spec(pc,walker,config,meta):
    g=0x20003000
    return [(0,'lui',dict(rd=15,imm=g)),(4,'load',dict(rd=11,rs1=15,imm=config-g,width=4)),
      (8,'lui',dict(rd=14,imm=g)),(12,'addi',dict(rd=15,rs1=15,imm=config-g)),
      (16,'addi',dict(rd=12,rs1=11,imm=544)),(20,'store',dict(rs2=12,rs1=14,imm=meta-8-g,width=4)),
      (24,'load',dict(rd=14,rs1=15,imm=4,width=2,mnemonic='qk.c.lhu')),
      (26,'addi',dict(rd=15,rs1=11,imm=-8)),(30,'lui',dict(rd=13,imm=g)),
      (34,'addi',dict(rd=2,rs1=2,imm=-16)),(36,'add',dict(rd=15,rs1=15,rs2=14)),
      (38,'lui',dict(rd=10,imm=0x1000)),(40,'store',dict(rs2=15,rs1=13,imm=meta-16-g,width=4)),
      (44,'store',dict(rs2=1,rs1=2,imm=12,width=4)),(46,'addi',dict(rd=10,rs1=10,imm=7)),
      (48,'srli',dict(rd=13,rs1=14,imm=3)),(52,'bgeu',dict(rs1=10,rs2=14,target=pc+60)),
      (56,'addi',dict(rd=13,rs1=0,imm=512)),(60,'add',dict(rd=14,rs1=12,rs2=13)),
      (64,'lui',dict(rd=10,imm=g)),(68,'store',dict(rs2=14,rs1=10,imm=meta-12-g,width=4)),
      (72,'store',dict(rs2=14,rs1=11,imm=544,width=4)),(76,'addi',dict(rd=13,rs1=13,imm=-8)),
      (78,'store',dict(rs2=13,rs1=12,imm=4,width=2,mnemonic='qk.c.sh')),
      (80,'store',dict(rs2=0,rs1=12,imm=6,width=2)),(84,'store',dict(rs2=15,rs1=14,imm=0,width=4)),
      (86,'sub',dict(rd=15,rs1=15,rs2=14)),(88,'addi',dict(rd=15,rs1=15,imm=-8)),
      (90,'store',dict(rs2=15,rs1=14,imm=4,width=2,mnemonic='qk.c.sh')),
      (92,'store',dict(rs2=0,rs1=14,imm=6,width=2)),(96,'jal',dict(rd=1,target=walker)),
      (98,'load',dict(rd=1,rs1=2,imm=12,width=4)),(100,'lui',dict(rd=15,imm=g)),
      (104,'store',dict(rs2=10,rs1=15,imm=meta+6-g,width=2)),
      (108,'addi',dict(rd=2,rs1=2,imm=16)),(110,'jr',dict(rs1=1))]


def geometry(H,L):
    """Address/width formulas only, no memory objects or instruction stepping."""
    check(type(H) is int and 0<=H<=MASK and type(L) is int and 0<=L<=65535,'geometry operand domains')
    s=(L>>3) if L<=0x1007 else 512
    a=(H+544)&MASK;e=(H+L-8)&MASK;b=(a+s)&MASK
    return dict(H=H,L=L,split_distance=s,small_head=a,large_head=b,sentinel=e,
                small_size=(s-8)&65535,large_size=(e-b-8)&65535)


def app_operands(app):
    start=0x19a3a;raw=app[start-0x8000:start-0x8000+16];n=decode(raw,start)
    init.g(n,start,'APP heap upper operand',op='auipc',rd=15,imm=0x1ffea000)
    init.g(n,start+4,'APP heap-address operand',op='addi',rd=15,rs1=15,imm=1874)
    init.g(n,start+8,'APP heap-address stack store',op='store',rs2=15,rs1=2,imm=16,width=4)
    init.g(n,start+10,'APP heap-length operand',op='lui',rd=15,imm=0x7000)
    init.g(n,start+12,'APP heap-length stack store',op='store',rs2=15,rs1=2,imm=20,width=2)
    H=(start+n[start]['imm']+n[start+4]['imm'])&MASK;L=n[start+10]['imm']&65535
    check(H==0x2000418c and L==0x7000,'APP nominal heap operand values')
    return {'start':hex(start),'bytes':16,'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),
            'H':hex(H),'L':hex(L),'config_stores_SP_offsets':[16,20],
            'later_live_config_values_proved':False},geometry(H,L)


def derive(app,carriers,header):
    parent=post.derive(app,carriers,header);ap,nominal=app_operands(app);profiles=[]
    for data,previous,detail in zip(carriers,parent['profiles'],DETAILS):
        walker,heap,reset,wh,hh,rh=detail
        calls={c['role']:int(c['target'],16) for c in previous['calls']}
        check(calls['heap-init']==heap and calls['late-init']==reset,'post-config nested targets')
        meta=int(previous['count_byte'],16)-1;config=meta+80
        wn=decode(init.binding.take(data,walker,36),walker)
        hn=decode(init.binding.take(data,heap,112),heap)
        rn=decode(init.binding.take(data,reset,10),reset)
        guard_body(wn,walker,walker_spec(walker,meta),'walker')
        guard_body(hn,heap,bootstrap_spec(heap,walker,config,meta),'bootstrap')
        guard_body(rn,reset,[(0,'lui',dict(rd=15,imm=0x20003000)),
            (4,'store',dict(rs2=0,rs1=15,imm=meta-4-0x20003000,width=4)),(8,'jr',dict(rs1=1))],'reset')
        we,wc=init.timer.cfg(wn,walker);he,hc=init.timer.cfg(hn,heap);re,rc=init.timer.cfg(rn,reset)
        check(len(wc)==1 and set(wc[0])=={hex(walker+i) for i in (18,24,26,28,30,32,34)},'walker complete SCC')
        check(not hc and not rc,'bootstrap/reset local CFG acyclic')
        check(not any(d['op']=='store' for d in wn.values()),'walker has no stores')
        sets=[sorted({d['rd'] for d in n.values() if d.get('rd',0)}) for n in (wn,hn,rn)]
        check(sets==[[10,13,14,15],[1,2,10,11,12,13,14,15],[15]],'heap local GPR writes')
        check([p-heap for p,d in hn.items() if d['op']=='store']==[20,40,44,68,72,78,80,84,90,92,104],
              'bootstrap complete ordered store census')
        fallback=config+52
        fixed=[(meta-16,4),(meta-8,4),(meta-12,4),(meta+6,2),(meta-4,4)]
        check(all(a+w<=fallback or fallback+4<=a for a,w in fixed),'heap fixed globals exclude fallback')
        bodies=[]
        for role,pc,size,digest,n,edges,cycles,writes in (
            ('walker',walker,36,wh,wn,we,wc,sets[0]),('bootstrap',heap,112,hh,hn,he,hc,sets[1]),
            ('reset',reset,10,rh,rn,re,rc,sets[2])):
            raw=init.binding.take(data,pc,size)
            bodies.append({'role':role,'start':hex(pc),'bytes':size,'sha256':sha256(raw).hexdigest(),
                'expected_sha256':digest,'instructions':list(n.values()),'conditional_normal_return_CFG':edges,
                'cyclic_SCCs':cycles,'encoded_GPR_writes':writes})
        profiles.append({'label':previous['label'],'bodies':bodies,'config_base':hex(config),
            'slots':{k:hex(v) for k,v in dict(small_head=meta-8,large_head=meta-12,sentinel=meta-16,
                accounting=meta+6,late_reset=meta-4,fallback=fallback).items()},
            'bootstrap_store_order':['small-head=A','sentinel=E','save RA at SP+12',
                'large-head=B','U32[A]=B','U16[A+4]=low16(S-8)','U16[A+6]=0',
                'U32[B]=E','U16[B+4]=low16(E-B-8)','U16[B+6]=0','U16[account]=low16(walker_A0)'],
            'walker_call':{'pc':hex(heap+96),'target':hex(walker),'link':hex(heap+98),
                'complete_local_body_verified':True,'universal_termination_proved':False},
            'walker_entry_global_snapshots_reloaded_each_iteration':False,
            'reset_preserves_A0_by_encoded_nonwrite':True,'fixed_globals_exclude_fallback':True,
            'all_heap_stack_or_pointer_writes_exclude_fallback_proved':False,
            'code_frame_header_global_stability_proved':False,'installed_binding_proved':False})
    return {'schema':'TSL9-heap-bootstrap-static-v1','profile':init.timer.PROFILE,
        'standard_integer_interpretation':'conditional RV32I/C; physical support unproved',
        'scope':'Complete static operands/CFG/store order plus address algebra; no linked-list or ISA execution',
        'APP_operand_witness':ap,'profiles':profiles,
        'geometry_formulas':{'H':'fresh U32[config]','L':'fresh U16[config+4]',
            'A':'(H+544)&0xffffffff','E':'(H+L-8)&0xffffffff',
            'S':'L>>3 if L<=0x1007 else 512; equivalently min(L>>3,512)',
            'B':'(A+S)&0xffffffff','small_size':'(S-8)&0xffff','large_size':'(E-B-8)&0xffff'},
        'local_geometry_admission_checks_present':False,
        'walker':'A0=0; snapshot head/end once; if cur==end return; add U16[cur+4] iff U16[cur+6]==0; next=U32[cur]',
        'walker_accumulator_width':32,'account_store_width':16,'sentinel_next_read_on_equal_path':False,
        'nominal_geometry':{k:hex(v) if k in ('H','L','small_head','large_head','sentinel') else v for k,v in nominal.items()},
        'nominal_two_node_sum_with_stable_nonalias_headers':nominal['small_size']+nominal['large_size'],
        'nominal_two_node_memory_state_constructed_or_traversed':False,
        'installed_binding_proved':False,'full_boot_or_heap_ownership_proved':False}


def tests(app,carriers,header):
    for length in range(65536):
        s=(length>>3) if length<=4103 else 512
        check(s==min(length>>3,512),'split-distance U16 algebra')
        if length>=639:
            check(s-8>=0 and length-560-s>=0 and (s-8)+(length-560-s)==length-568,'nonnegative size-sum algebra')
    for h in (0,0x2000418c,0xfffffff0,0xffffffff):
        for length in (0,7,63,639,4103,4104,0x7000,65535):
            v=geometry(h,length)
            check(v['large_head']==(h+544+v['split_distance'])&MASK and
                  v['large_size']==(length-560-v['split_distance'])&65535,'wrapped geometry identities')
    v=geometry(0x2000418c,0x7000)
    check((v['small_head'],v['large_head'],v['sentinel'],v['small_size'],v['large_size'])==
          (0x200043ac,0x200045ac,0x2000b184,504,27600),'nominal APP geometry witness')
    cases=(
      ('carrier',0x430e0+18,'6313f700','6303f700','walker instruction 0x12'),
      ('carrier',0x430e0+24,'f623','d623','walker instruction 0x18'),
      ('carrier',0x430e0+32,'9c43','dc43','walker instruction 0x20'),
      ('carrier',0x43104+46,'1d05','1905','bootstrap instruction 0x2e'),
      ('carrier',0x43104+56,'93060020','93064020','bootstrap instruction 0x38'),
      ('carrier',0x43104+78,'56a2','76a2','bootstrap instruction 0x4e'),
      ('carrier',0x43104+92,'23130700','23120700','bootstrap instruction 0x5c'),
      ('carrier',0x43104+104,'2391a71a','2392a71a','bootstrap instruction 0x68'),
      ('carrier',0x4329a+4,'23ac0718','23ae0718','reset instruction 0x4'),
      ('app',0x19a3a+4,'93872775','93876775','APP heap-address operand'))
    for kind,pc,oldhex,newhex,error in cases:
        a,cs=bytearray(app),[bytearray(c) for c in carriers]
        data,off=(a,pc-0x8000) if kind=='app' else (cs[0],pc-LIB)
        old,new=bytes.fromhex(oldhex),bytes.fromhex(newhex)
        check(data[off:off+len(old)]==old,'heap bootstrap mutation pin');data[off:off+len(new)]=new
        try:derive(a,cs,header)
        except RuntimeError as e:check(str(e)==error,'unexpected heap mutation guard: '+str(e))
        else:raise RuntimeError('heap bootstrap mutation escaped')
    print('PASS: 65536 split distances; 64897 nonnegative size identities; 32 wrapped geometry cases; APP witness; 10 specified raw mutations')


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true',help='Create ledger exclusively');o=p.parse_args()
    app,header=init.binding.APP.read_bytes(),init.core.outer.HEADER.read_bytes()
    check(len(app)==76800 and sha256(app).hexdigest()==init.binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK header identity')
    cs=[]
    for label,folder,tail,n,digest in init.binding.PROFILES:
        b=(ROOT/'analysis/wch-resident-candidate-2026-10-21'/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(b)==n and sha256(b).hexdigest()==digest,'candidate identity '+label);cs.append(b)
    sources,vectors=init.timer.source_contract();ledger=derive(app,cs,header)
    ledger['sources'],ledger['official_Xwchc_vectors']=sources,vectors
    for p in ledger['profiles']:
        for b in p['bodies']:check(b['sha256']==b['expected_sha256'],'complete heap helper body identity')
    tests(app,cs,header);output=(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'heap bootstrap ledger exact replay')
    print('PASS: 6 complete candidate bodies, 316 bytes/104 instructions; 24 local stores; linked walker call; APP16 operand pin')
    print('PASS: ledger exact replay; installed/geometry validity/termination UNPROVED; NO ISA/provider/heap/MMIO execution')


if __name__=='__main__':main()
