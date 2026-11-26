"""Complete post-config resident body: operands, conditional CFG and host algebra.

All seven nested calls are opaque normal-return edges. No target ISA, heap,
provider or MMIO executes/emulates. Reloaded values retain distinct identities.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_fallback_initialization_static as init

ROOT,LIB,MASK=init.ROOT,init.LIB,init.MASK
OUT=Path(__file__).with_name('v4160-post-config-static.json')
TEMPLATE=bytes.fromhex(
 'b737002023a4071e37350020b7370020411123a807225146b737002081451305851c'
 '06c623a0071e22c426c23734002097d0fb1fe780e0821305c419130680028145'
 '97d0fb1fe780c081eff0cfd7b737002083c717201304c419854513d527008d8b3e95'
 '8d473305f5029947b734002039051375f50f28a03305f5021305052497c0fb1f'
 'e780204823a6a4222dcd3020994781453306f6021306062497c0fb1fe780207c'
 '83a7c4223820b7340020938707240a0723a2f41cba97373700202322f71e'
 'eff0afe939291c3083a6441c373604001397270036971306462a10c313871700'
 '1377f70f0a073736040036971306663210c313873700890793f7f70f8a0718b0'
 'b69790c3b2402244924441018280')
DETAILS=(
 (0x43b3e,0x43104,0x4329a,0x44022,0x432a4,0x43326,
  '3093ac8a6c0596e6c6b2afaa1f4480c76b6dfb7e39f6df5d3e121d4007c456d6'),
 (0x43bca,0x43190,0x43326,0x440b6,0x43330,0x433b2,
  '970669cbefbaf5eac23456590dd1b4d5769bddddf02f0f8e25c72f872251cf24'))
check,sx=init.check,init.sx


def decode(raw,start):
    nodes,off={},0
    while off<len(raw):
        h=int.from_bytes(raw[off:off+2],'little');size=2 if h&3!=3 else 4
        check(off+size<=len(raw),'post-config partial instruction')
        chunk,pc=raw[off:off+size],start+off;w=int.from_bytes(chunk,'little')
        d=dict(pc=pc,bytes=chunk.hex(),size=size)
        if size==4 and w&0xfe00707f==0x02000033:
            d.update(op='mul',rd=w>>7&31,rs1=w>>15&31,rs2=w>>20&31)
        elif size==4 and w&0xfe00707f==0x5013:
            d.update(op='srli',rd=w>>7&31,rs1=w>>15&31,imm=w>>20&31)
        elif size==4 and w&0x707f==0x7013:
            d.update(op='andi',rd=w>>7&31,rs1=w>>15&31,imm=sx(w>>20,12))
        elif size==2 and h&3==1 and h>>13==4 and h>>10&3==2:
            r=8+(h>>7&7);d.update(op='andi',rd=r,rs1=r,imm=sx((h>>2&31)|(h>>7&32),6))
        else:d=init.decode(chunk,pc)[pc]
        nodes[pc]=d;off+=size
    return nodes


def specs(pc,b,detail):
    _,heap,late,read,lit0,lit1,_=detail;g=0x20003000;dest=b+80
    rows=[
      (0,'lui',dict(rd=15,imm=g)),(4,'store',dict(rs2=0,rs1=15,imm=b+76-g,width=4)),
      (8,'lui',dict(rd=10,imm=g)),(12,'lui',dict(rd=15,imm=g)),
      (16,'addi',dict(rd=2,rs1=2,imm=-16)),(18,'store',dict(rs2=0,rs1=15,imm=dest+68-g,width=4)),
      (22,'li',dict(rd=12,imm=20)),(24,'lui',dict(rd=15,imm=g)),(28,'li',dict(rd=11,imm=0)),
      (30,'addi',dict(rd=10,rs1=10,imm=b+44-g)),(34,'store',dict(rs2=1,rs1=2,imm=12,width=4)),
      (36,'store',dict(rs2=0,rs1=15,imm=b+68-g,width=4)),
      (40,'store',dict(rs2=8,rs1=2,imm=8,width=4)),(42,'store',dict(rs2=9,rs1=2,imm=4,width=4)),
      (44,'lui',dict(rd=8,imm=g)),(56,'addi',dict(rd=10,rs1=8,imm=b-g)),
      (60,'addi',dict(rd=12,rs1=0,imm=40)),(64,'li',dict(rd=11,imm=0)),
      (74,'jal',dict(rd=1,target=heap)),(78,'lui',dict(rd=15,imm=g)),
      (82,'load',dict(rd=15,rs1=15,imm=dest+21-g,width=1)),
      (86,'addi',dict(rd=8,rs1=8,imm=b-g)),(90,'li',dict(rd=11,imm=1)),
      (92,'srli',dict(rd=10,rs1=15,imm=2)),(96,'andi',dict(rd=15,rs1=15,imm=3)),
      (98,'add',dict(rd=10,rs1=10,rs2=15)),(100,'li',dict(rd=15,imm=3)),
      (102,'mul',dict(rd=10,rs1=10,rs2=15)),(106,'li',dict(rd=15,imm=6)),
      (108,'lui',dict(rd=9,imm=g)),(112,'addi',dict(rd=10,rs1=10,imm=14)),
      (114,'andi',dict(rd=10,rs1=10,imm=255)),
      (118,'store',dict(rs2=10,rs1=8,imm=2,width=1,mnemonic='qk.c.sb')),
      (120,'mul',dict(rd=10,rs1=10,rs2=15)),(124,'addi',dict(rd=10,rs1=10,imm=576)),
      (136,'store',dict(rs2=10,rs1=9,imm=dest+64-g,width=4)),
      (140,'beqz',dict(rs1=10,target=pc+262)),
      (142,'load',dict(rd=12,rs1=8,imm=2,width=1,mnemonic='qk.c.lbu')),
      (144,'li',dict(rd=15,imm=6)),(146,'li',dict(rd=11,imm=0)),
      (148,'mul',dict(rd=12,rs1=12,rs2=15)),(152,'addi',dict(rd=12,rs1=12,imm=576)),
      (164,'load',dict(rd=15,rs1=9,imm=dest+64-g,width=4)),
      (168,'load',dict(rd=14,rs1=8,imm=2,width=1,mnemonic='qk.c.lbu')),
      (170,'lui',dict(rd=9,imm=g)),(174,'addi',dict(rd=15,rs1=15,imm=576)),
      (178,'slli',dict(rd=14,rs1=14,imm=2)),(180,'store',dict(rs2=15,rs1=9,imm=b+40-g,width=4)),
      (184,'add',dict(rd=15,rs1=15,rs2=14)),(186,'lui',dict(rd=14,imm=g)),
      (190,'store',dict(rs2=15,rs1=14,imm=b+72-g,width=4)),
      (194,'jal',dict(rd=1,target=late)),(198,'jal',dict(rd=1,target=read)),
      (200,'load',dict(rd=15,rs1=8,imm=1,width=1,mnemonic='qk.c.lbu')),
      (202,'load',dict(rd=13,rs1=9,imm=b+40-g,width=4)),
      (206,'lui',dict(rd=12,imm=0x43000)),(210,'slli',dict(rd=14,rs1=15,imm=2)),
      (214,'add',dict(rd=14,rs1=14,rs2=13)),(216,'addi',dict(rd=12,rs1=12,imm=lit0-0x43000)),
      (220,'store',dict(rs2=12,rs1=14,imm=0,width=4)),
      (222,'addi',dict(rd=14,rs1=15,imm=1)),(226,'andi',dict(rd=14,rs1=14,imm=255)),
      (230,'slli',dict(rd=14,rs1=14,imm=2)),(232,'lui',dict(rd=12,imm=0x43000)),
      (236,'add',dict(rd=14,rs1=14,rs2=13)),(238,'addi',dict(rd=12,rs1=12,imm=lit1-0x43000)),
      (242,'store',dict(rs2=12,rs1=14,imm=0,width=4)),
      (244,'addi',dict(rd=14,rs1=15,imm=3)),(248,'addi',dict(rd=15,rs1=15,imm=2)),
      (250,'andi',dict(rd=15,rs1=15,imm=255)),(254,'slli',dict(rd=15,rs1=15,imm=2)),
      (256,'store',dict(rs2=14,rs1=8,imm=1,width=1,mnemonic='qk.c.sb')),
      (258,'add',dict(rd=15,rs1=15,rs2=13)),(260,'store',dict(rs2=12,rs1=15,imm=0,width=4)),
      (262,'load',dict(rd=1,rs1=2,imm=12,width=4)),(264,'load',dict(rd=8,rs1=2,imm=8,width=4)),
      (266,'load',dict(rd=9,rs1=2,imm=4,width=4)),(268,'addi',dict(rd=2,rs1=2,imm=16)),(270,'jr',dict(rs1=1))]
    return {pc+o:dict(op=op,**f) for o,op,f in rows}


def reachable(edges,start,blocked=()):
    seen,work=set(),[start]
    while work:
        p=work.pop()
        if p in seen or p in blocked:continue
        seen.add(p);work.extend(edges[p])
    return seen


def derive(app,carriers,header):
    parents=init.derive(app,carriers,header);profiles=[]
    for data,parent,detail in zip(carriers,parents['profiles'],DETAILS):
        pc,heap,late,read,lit0,lit1,digest=detail;dest=int(parent['config']['destination'],16);b=dest-80
        check(int(parent['config']['target'],16)-320==pc,'config-to-post callee target')
        raw=init.binding.take(data,pc,272);n=decode(raw,pc);expected=specs(pc,b,detail)
        pairs=(48,66,128,156)
        check(set(n)==set(expected)|{pc+o+d for o in pairs for d in (0,4)},'post-config instruction boundaries')
        for p,f in expected.items():init.g(n,p,'post instruction '+hex(p-pc),**f)
        for off,target in ((48,0x2000039c),(66,0x2000039c),(128,0x20000040),(156,0x2000039c)):
            init.pair(n,pc+off,1,target,'post call '+hex(off))
        spans=tuple((o,4) for o in (4,18,30,36,56,82,86,136,164,180,190,202,216,238))+tuple((o,8) for o in pairs)+((198,2),)
        check(init.core.outer.normalized(raw,spans)==init.core.outer.normalized(TEMPLATE,spans),'complete post-config template')
        edges,cycles=init.timer.cfg(n,pc);ei={int(p,16):[int(q,16) for q in qs] for p,qs in edges.items()}
        check(not cycles,'post-config conditional CFG acyclic')
        check(pc+140 not in reachable(ei,pc,{pc+136}),'post allocation store dominates null branch')
        check(reachable(ei,pc+262)=={pc+i for i in (262,264,266,268,270)},'post null allocation epilogue only')
        check(not any(d.get('rd')==10 for p,d in n.items() if p>=pc+200),'post suffix preserves last helper A0')
        writes=sorted({d['rd'] for d in n.values() if d.get('rd',0)})
        check(writes==[1,2,8,9,10,11,12,13,14,15],'post encoded GPR write set')
        fixed=((4,b+76,4),(18,dest+68,4),(36,b+68,4),(118,b+2,1),(136,dest+64,4),
               (180,b+40,4),(190,b+72,4),(256,b+1,1))
        fallback=int(parent['fallback_slot'],16)
        requests=((b+44,20),(b,40))
        for _,address,size in fixed:
            check(address+size<=fallback or fallback+4<=address,'fixed post stores exclude fallback')
        for address,size in requests:
            check(address+size<=fallback or fallback+4<=address,'fixed post fill requests exclude fallback')
        stores=[p for p,d in n.items() if d['op']=='store']
        check(set(stores)=={pc+o for o,_,_ in fixed}|{pc+o for o in (34,40,42,220,242,260)},'complete local store census')
        calls=[{'role':role,'window_start':hex(pc+off),
                'transfer_pc':hex(pc+off+(4 if off in pairs else 0)),
                'link':hex(pc+off+(8 if off in pairs else n[pc+off]['size'])),
                'target':hex(target),'normal_return_effects_proved':False}
            for role,off,target in (('fill20',48,0x2000039c),('fill40',66,0x2000039c),('heap-init',74,heap),
                ('allocate',128,0x20000040),('fill-reply',156,0x2000039c),('late-init',194,late),('late-read',198,read))]
        profiles.append({'label':parent['label'],'target':hex(pc),'bytes':272,'sha256':sha256(raw).hexdigest(),
            'expected_sha256':digest,'instructions':list(n.values()),'conditional_normal_return_CFG':edges,'cyclic_SCCs':cycles,
            'calls':calls,'encoded_GPR_writes':writes,'local_store_count':len(stores),
            'fixed_stores_with_live_base_premise':[{'pc':hex(pc+o),'address':hex(a),'bytes':w} for o,a,w in fixed],
            'fixed_zero_fill_requests':[{'address':hex(a),'bytes':w} for a,w in requests],
            'dynamic_stores':{'stack_relative_PCs':[hex(pc+i) for i in (34,40,42)],
                'table_PCs':[hex(pc+i) for i in (220,242,260)]},
            'input_byte':hex(dest+21),'capacity_byte':hex(b+2),'count_byte':hex(b+1),
            'allocation_reply_slot':hex(dest+64),'table_slot':hex(b+40),'event_table_slot':hex(b+72),
            'snapshot_read_PCs':{'N1':hex(pc+142),'P_prime':hex(pc+164),'N2':hex(pc+168),'n':hex(pc+200),'T_prime':hex(pc+202)},
            'registered_literals':[hex(lit0),hex(lit1),hex(lit1)],
            'fixed_ranges_exclude_fallback':True,'whole_function_excludes_fallback_writes_proved':False,
            'callee_context_code_frame_and_data_stability_proved':False,'installed_binding_proved':False})
    return {'schema':'TSL9-post-config-static-v1','profile':init.timer.PROFILE,
        'standard_integer_interpretation':'conditional RV32I/M/C semantics; physical support unproved',
        'scope':'Complete local operands/store census and conditional CFG, opaque calls; no target state execution',
        'installed_binding_proved':False,'physical_ISA_profile_proved':False,'profiles':profiles,
        'N0':'(14 + 3*((U8[c] >> 2) + (U8[c] & 3))) & 255',
        'allocation_arguments':{'A0':'576 + 6*N0','A1':1},'N0_range':[14,212],'allocation_request_range':[660,1848],
        'allocation_core_rounded_requests_all_choose_large_head':True,
        'nonnull_fill_arguments':{'A0':'returned P','A1':0,'A2':'576 + 6*fresh_U8_capacity_N1'},
        'post_fill_table_base':'T=(fresh_P_prime + 576)&0xffffffff',
        'post_fill_event_base':'(T + 4*fresh_U8_capacity_N2)&0xffffffff',
        'snapshots_N0_N1_N2_equivalent_proved':False,'snapshots_P_Pprime_equivalent_proved':False,
        'snapshots_T_Tprime_equivalent_proved':False,
        'registration_order':['U32[(Tprime+4*n)&0xffffffff]=literal0',
            'U32[(Tprime+4*((n+1)&255))&0xffffffff]=literal1',
            'U8[count_byte]=(n+3)&255','U32[(Tprime+4*((n+2)&255))&0xffffffff]=literal1'],
        'local_registration_capacity_guard_present':False,'final_count_requires_table_nonalias':True,
        'null_allocation_normal_return_A0':0,'nonnull_normal_return_A0':'last late-read helper reply, not forced zero',
        'outer_config_passes_inner_reply_to_APP':False}


def tests(app,carriers,header):
    capacities=set()
    for c in range(256):
        v=(14+3*((c>>2)+(c&3)))&255;request=576+6*v;r=((request+3)&65535)&0xfffc
        check(14<=v<=212 and v==14+3*((c>>2)+(c&3)) and 660<=request<=1848 and r>52,
              'capacity/request/core-head byte-domain algebra');capacities.add(v)
    check(capacities==set(range(14,213,3)),'67 exact capacity values')
    for cap in range(256):check(576<=576+6*cap<=2106,'fresh capacity fill range')
    for n in range(256):
        ids=[(n+i)&255 for i in range(3)];check(len(set(ids))==3,'registration indices distinct')
        for base in (0,0x20004000,0xfffffff0,0xffffffff):
            byte_sets=[{(base+4*i+j)&MASK for j in range(4)} for i in ids]
            check(all(byte_sets[i].isdisjoint(byte_sets[j]) for i in range(3) for j in range(i)),
                  'registration modulo table words disjoint')
    cases=(
      (82,'83c71720','83c72720'),(114,'1375f50f','1375f507'),
      (118,'28a0','08a0'),(136,'23a6a422','23a4a422'),
      (140,'2dcd','2ded'),(142,'3020','1020'),
      (164,'83a7c422','83a74422'),(202,'83a6441c','83a6c41c'),
      (250,'93f7f70f','93f7f707'),(256,'18b0','18a0'))
    for off,oldhex,newhex in cases:
        cs=[bytearray(c) for c in carriers];p=DETAILS[0][0]+off-LIB
        old,new=bytes.fromhex(oldhex),bytes.fromhex(newhex)
        check(cs[0][p:p+len(old)]==old,'post-config mutation pin');cs[0][p:p+len(new)]=new
        try:derive(app,cs,header)
        except RuntimeError as error:check(str(error)=='post instruction '+hex(off),'unexpected post mutation guard: '+str(error))
        else:raise RuntimeError('post-config mutation escaped')
    print('PASS: 256 capacity/request/core-head cases; 256 fresh-capacity ranges; 1024 modulo table cases; 10 specified raw mutations')


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
    for v in ledger['profiles']:check(v['sha256']==v['expected_sha256'],'complete post-config body identity')
    tests(app,cs,header);output=(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'post-config ledger exact replay')
    print('PASS: 2 complete bodies, 544 bytes/174 instructions; 28 local stores; 14 opaque call edges; conditional CFG')
    print('PASS: ledger exact replay; installed/nested effects/pointer stability UNPROVED; NO ISA/provider/heap/MMIO execution')


if __name__=='__main__':main()
