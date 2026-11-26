"""Full config I/O helper: static bytes/CFG/operands and host-width algebra.

All callback/allocation/fill/free calls are opaque boundaries. No target ISA,
provider, heap, output-buffer or MMIO execution/model is constructed.
"""
import argparse
import json
from hashlib import sha256
from itertools import product
from pathlib import Path
import check_v4160_post_config_static as post

init,ROOT,LIB,MASK=post.init,post.ROOT,post.LIB,post.MASK
OUT=Path(__file__).with_name('v4160-config-io-static.json')
DETAILS=((0x44022,'72f70ec3ff48430f0b198f914b6bd949fed111707b324a237e5af2f2f3b2ef11'),
         (0x440b6,'4a44bc23e78c7c0b93549c29695e2f889a28e57d8e8f33570300a6f1453fe126'))
check,sx=init.check,init.sx


def decode(raw,start):
    nodes,off={},0
    while off<len(raw):
        h=int.from_bytes(raw[off:off+2],'little');size=2 if h&3!=3 else 4
        check(off+size<=len(raw),'config-io partial instruction')
        chunk,pc=raw[off:off+size],start+off;w=int.from_bytes(chunk,'little')
        if size==4 and w&0x707f==0x4063:
            v=(w>>31)<<12|(w>>7&1)<<11|(w>>25&63)<<5|(w>>8&15)<<1
            d=dict(pc=pc,bytes=chunk.hex(),size=size,op='blt',rs1=w>>15&31,rs2=w>>20&31,target=pc+sx(v,13))
        elif size==2 and h&3==0 and h>>13==0:
            imm=(h>>11&3)<<4|(h>>7&15)<<6|(h>>6&1)<<2|(h>>5&1)<<3
            check(imm!=0,'reserved C.ADDI4SPN zero immediate')
            d=dict(pc=pc,bytes=chunk.hex(),size=size,op='addi',rd=8+(h>>2&7),rs1=2,imm=imm)
        else:d=post.decode(chunk,pc)[pc]
        nodes[pc]=d;off+=size
    return nodes


def specs(pc,config,meta):
    g=0x20003000
    rows=[
      (0,'addi',dict(rd=2,rs1=2,imm=-32)),(2,'store',dict(rs2=8,rs1=2,imm=24,width=4)),
      (4,'lui',dict(rd=8,imm=g)),(8,'addi',dict(rd=15,rs1=8,imm=config-g)),
      (12,'load',dict(rd=10,rs1=15,imm=8,width=4)),(14,'store',dict(rs2=1,rs1=2,imm=28,width=4)),
      (16,'store',dict(rs2=9,rs1=2,imm=20,width=4)),(18,'store',dict(rs2=18,rs1=2,imm=16,width=4)),
      (20,'bnez',dict(rs1=10,target=pc+36)),(22,'li',dict(rd=10,imm=1)),
      (24,'load',dict(rd=1,rs1=2,imm=28,width=4)),(26,'load',dict(rd=8,rs1=2,imm=24,width=4)),
      (28,'load',dict(rd=9,rs1=2,imm=20,width=4)),(30,'load',dict(rd=18,rs1=2,imm=16,width=4)),
      (32,'addi',dict(rd=2,rs1=2,imm=32)),(34,'jr',dict(rs1=1)),
      (36,'addi',dict(rd=8,rs1=8,imm=config-g)),(40,'load',dict(rd=15,rs1=8,imm=56,width=4)),
      (42,'beqz',dict(rs1=15,target=pc+22)),(44,'load',dict(rd=14,rs1=8,imm=60,width=4)),
      (46,'beqz',dict(rs1=14,target=pc+22)),(48,'addi',dict(rd=12,rs1=2,imm=12)),
      (50,'li',dict(rd=11,imm=1)),(52,'call_indirect',dict(rd=1,rs1=15)),
      (54,'load',dict(rd=14,rs1=8,imm=8,width=4)),(56,'load',dict(rd=15,rs1=2,imm=12,width=4)),
      (58,'beq',dict(rs1=14,rs2=15,target=pc+22)),
      (62,'load',dict(rd=10,rs1=8,imm=12,width=2,mnemonic='qk.c.lhu')),
      (64,'addi',dict(rd=11,rs1=0,imm=78)),(68,'lui',dict(rd=9,imm=g)),
      (80,'addi',dict(rd=14,rs1=9,imm=meta-g)),(84,'store',dict(rs2=10,rs1=14,imm=32,width=4)),
      (86,'addi',dict(rd=9,rs1=9,imm=meta-g)),(90,'beqz',dict(rs1=10,target=pc+22)),
      (92,'load',dict(rd=12,rs1=8,imm=12,width=2,mnemonic='qk.c.lhu')),
      (94,'addi',dict(rd=11,rs1=0,imm=255)),(98,'li',dict(rd=18,imm=0)),
      (108,'load',dict(rd=15,rs1=8,imm=14,width=1,mnemonic='qk.c.lbu')),
      (110,'load',dict(rd=12,rs1=9,imm=32,width=4)),(112,'blt',dict(rs1=18,rs2=15,target=pc+138)),
      (116,'mv',dict(rd=10,rs2=12)),(126,'li',dict(rd=10,imm=0)),
      (128,'store',dict(rs2=0,rs1=9,imm=32,width=4)),(132,'store',dict(rs2=0,rs1=9,imm=36,width=4)),
      (136,'jump',dict(target=pc+24)),
      (138,'load',dict(rd=11,rs1=8,imm=12,width=2,mnemonic='qk.c.lhu')),
      (140,'load',dict(rd=10,rs1=8,imm=8,width=4)),(142,'load',dict(rd=14,rs1=8,imm=60,width=4)),
      (144,'mul',dict(rd=15,rs1=11,rs2=18)),(148,'srli',dict(rd=11,rs1=11,imm=2)),
      (150,'addi',dict(rd=18,rs1=18,imm=1)),(152,'add',dict(rd=10,rs1=10,rs2=15)),
      (154,'store',dict(rs2=10,rs1=12,imm=0,width=4)),(156,'call_indirect',dict(rd=1,rs1=14)),
      (158,'jump',dict(target=pc+108))]
    return {pc+o:dict(op=op,**f) for o,op,f in rows}


def derive(app,carriers,header):
    parent=post.derive(app,carriers,header);profiles=[]
    for data,previous,(pc,digest) in zip(carriers,parent['profiles'],DETAILS):
        check(next(c['target'] for c in previous['calls'] if c['role']=='late-read')==hex(pc),'post-to-config-io target')
        meta=int(previous['count_byte'],16)-1;config=meta+80
        raw=init.binding.take(data,pc,160);n=decode(raw,pc);expected=specs(pc,config,meta);pairs=(72,100,118)
        check(set(n)==set(expected)|{pc+o+d for o in pairs for d in (0,4)},'config-io complete instruction boundaries')
        for p,f in expected.items():init.g(n,p,'io instruction '+hex(p-pc),**f)
        for off,target in ((72,0x20000040),(100,0x2000039c),(118,0x20000110)):
            init.pair(n,pc+off,1,target,'io direct call '+hex(off))
        # BLT topology uses two conditional successors; its signed operands are
        # independently guarded above. Calls have ASSUMED normal-return edges.
        topology={p:dict(d,op='bne') if d['op']=='blt' else d for p,d in n.items()}
        edges,cycles=init.timer.cfg(topology,pc);ei={int(p,16):[int(q,16) for q in qs] for p,qs in edges.items()}
        check(len(cycles)==1 and set(cycles[0])=={hex(pc+o) for o in (108,110,112,138,140,142,144,148,150,152,154,156,158)},
              'config-io loop SCC')
        stores={p:d for p,d in n.items() if d['op']=='store'}
        check(set(stores)=={pc+o for o in (2,14,16,18,84,128,132,154)},'io complete local store census')
        stack_stores=[(d['imm'],d['width']) for d in stores.values() if d['rs1']==2]
        check(sorted(stack_stores)==[(16,4),(20,4),(24,4),(28,4)] and
              all(set(range(a,a+w)).isdisjoint(range(12,16)) for a,w in stack_stores),'io no local output-word initialization')
        check(pc+90 not in post.reachable(ei,pc,{pc+84}),'io allocation reply store dominates null test')
        preds={p for p,qs in ei.items() if pc+24 in qs}
        check(preds=={pc+22,pc+136} and not any(d.get('rd')==10 for p,d in n.items() if pc+128<=p<=pc+136),
              'io normal encoded return values')
        writes=sorted({d['rd'] for d in n.values() if d.get('rd',0)})
        check(writes==[1,2,8,9,10,11,12,14,15,18],'io encoded GPR write set')
        profiles.append({'label':previous['label'],'target':hex(pc),'bytes':160,'sha256':sha256(raw).hexdigest(),
            'expected_sha256':digest,'instructions':list(n.values()),'conditional_normal_return_CFG':edges,'cyclic_SCCs':cycles,
            'encoded_GPR_writes':writes,'local_store_PCs':[hex(p) for p in stores],
            'config_base':hex(config),'metadata_base':hex(meta),'cache_pointer_slot':hex(meta+32),'neighbor_clear_slot':hex(meta+36),
            'initial_callback':{'transfer_pc':hex(pc+52),'link':hex(pc+54),'target_source':hex(config+56),
                'A0':'initial U32[config+8]','A1':1,'A2':'SP_after_frame+12',
                'local_output_word_initialized':False,'output_or_reply_contract_proved':False,'scalar_A0_reply_checked':False},
            'direct_calls':[{'window_start':hex(pc+o),'transfer_pc':hex(pc+o+4),'link':hex(pc+o+8),'target':hex(t)}
                for o,t in ((72,0x20000040),(100,0x2000039c),(118,0x20000110))],
            'per_iteration_callback':{'transfer_pc':hex(pc+156),'link':hex(pc+158),'target_source':hex(config+60),
                'target_fresh_each_iteration':True,'repeated_null_guard':False,
                'A0':'(fresh_U32[config+8] + fresh_U16[config+12] * old_S2) & 0xffffffff',
                'A1':'fresh_U16[config+12] >> 2','A2':'fresh U32[cache_pointer_slot]',
                'pre_call_store':'U32[A2] = A0, before callback','S2_increment_before_callback':True,
                'scalar_A0_reply_checked':False},
            'cleanup_order':['free(last reloaded cache pointer)','A0=0','cache pointer slot=0','neighbor slot=0','frame restores/RET'],
            'frame_context_output_pointer_stability_proved':False,'installed_binding_proved':False})
    return {'schema':'TSL9-config-io-static-v1','profile':init.timer.PROFILE,
        'standard_integer_interpretation':'conditional RV32I/M/C including signed BLT; physical support unproved',
        'scope':'Complete static operands/store census/conditional CFG and width algebra only; opaque calls',
        'profiles':profiles,'installed_binding_proved':False,
        'gate_fields':[8,56,60],'gate_uses_full_U32_values':True,
        'nominal_base_premises':['live S0 == config base at each projected read','live S1 == metadata base at each projected access',
            'initial and then-live SP agree when relating callback output to readback'],
        'readback_compare':'fresh U32[live_S0+8] == U32[then_live_SP+12], not callback A0',
        'allocation_arguments':{'A0':'fresh U16[config+12] = L0','A1':78},
        'allocation_reply_stored_before_null_test':True,
        'nonnull_fill_arguments':{'A0':'allocation reply P','A1':255,'A2':'fresh U16[config+12] = L1'},
        'L0_L1_iteration_lengths_equivalent_proved':False,'P_and_reloaded_cache_pointers_equivalent_proved':False,
        'loop_test':'signed32(S2) < zero_extended_U8[config+14]',
        'conditional_max_iterations':255,
        'bound_premises':['S2 is zero after fill','normal callbacks preserve S2','code/control/required context and reads remain valid'],
        'bound_requires_count_byte_stable':False,'universal_termination_proved':False,
        'return_one_paths':['config+8/+56/+60 gate absent','equal readback word','null allocation reply'],
        'return_zero_path':'normal cleanup after loop, independent of callback/free scalar replies',
        'normal_return_proves_NV_effect_or_release':False,
        'parent_post_reply_domain_with_premises':[0,1],'outer_config_still_overwrites_reply_with_zero':True}


def signed(v):return v if v<0x80000000 else v-0x100000000


def tests(app,carriers,header):
    gates=sum(all(x!=0 for x in a) for a in product((0,1,0x80000000,MASK),repeat=3))
    check(gates==27,'64 full-word gate shapes')
    for i,n in product(range(256),repeat=2):
        check((signed(i)<n)==(i<n),'nonnegative signed loop condition')
        if i<n:check(i<=254 and i+1<=255 and 255-(i+1)<255-i,'conditional loop variant')
    for i,n in product((0x7fffffff,0x80000000,0xfffffffe,MASK),range(256)):
        check((signed(i)<n)==bool(i&0x80000000),'signed callback-clobber controls')
    for length in range(65536):check((length>>2)*4<=length<(length>>2)*4+4,'U16 count floor algebra')
    for base,length,i in product((0,0x08077c00,0xfffffff0,MASK),(0,1,3,4,65535),(0,254)):
        check((base+(length*i&MASK))&MASK==(base+length*i)&MASK,'modulo address algebra')
    cases=(
      (12,'8847','c847'),(40,'1c5c','1c58'),(48,'7000','5000'),(56,'b247','a247'),
      (62,'4a24','0a24'),(84,'08d3','48d3'),(110,'9050','d050'),(112,'634df900','636df900'),
      (138,'4e24','0e24'),(142,'585c','185c'),(150,'0509','0909'),(132,'23a20402','23a00402'))
    for off,oldhex,newhex in cases:
        cs=[bytearray(c) for c in carriers];p=DETAILS[0][0]+off-LIB;old,new=bytes.fromhex(oldhex),bytes.fromhex(newhex)
        check(cs[0][p:p+len(old)]==old,'config-io mutation pin');cs[0][p:p+len(new)]=new
        try:derive(app,cs,header)
        except RuntimeError as error:check(str(error)=='io instruction '+hex(off),'unexpected io mutation guard: '+str(error))
        else:raise RuntimeError('config-io mutation escaped')
    print('PASS: 64 gate shapes; 65536 loop variants; 1024 signed controls; 65536 U16 counts; 40 address cases; 12 specified raw mutations')


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
    for v in ledger['profiles']:check(v['sha256']==v['expected_sha256'],'complete config-io body identity')
    tests(app,cs,header);output=(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'config-io ledger exact replay')
    print('PASS: 2 complete bodies, 320 bytes/122 instructions; 16 local stores; 10 opaque call sites; stack/cache distinctions')
    print('PASS: ledger exact replay; installed/callback output/context integrity UNPROVED; NO ISA/provider/heap/MMIO execution')


if __name__=='__main__':main()
