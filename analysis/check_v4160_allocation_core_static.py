"""Two complete reference allocation cores: static operands/CFG and host algebra.

Opaque fallback has a conditional normal-return CFG edge only. No ISA, heap,
loader, provider, linked list or MMIO is executed/emulated by this checker.
"""
import argparse
import json
from hashlib import sha256
from itertools import product
from pathlib import Path
import check_v4160_message_marker_static as message

timer,outer,binding = message.timer,message.outer,message.binding
ROOT,LIB,MASK = message.ROOT,message.LIB,message.MASK
ENTRY,LENGTH = 0x20000040,208
OUT = Path(__file__).with_name('v4160-allocation-core-static.json')
TEMPLATE = bytes.fromhex(
 '411122c4b747024006c603a4c72023a607200f10000011c199e5b747024023a68720'
 '014545a093073500c207c183f19bc207c183130740036366f7023737002003254719'
 '373700208326c7186391a602373700200327072269d3c207dd8d0545029765bf'
 '3737002003250719e1bf7a2131ef5a21636cf704b73600203306f74021489386c619'
 '6375c8028328050003d86600138687001d8f2a9661175aa22320160123130600'
 '10c15ea1130788fffaa26ea1ee222105b387f540fea2b747024023a68720b2402244'
 '410182800841bdbf')
DETAILS = (
 (0x402b0,0x20003194,0x20003190,0x2000318c,0x20003220,0x2000319c,
  'e74bee633acbf171c951df2720f2aeb66758fc597a8aa8efc0271bc686d2c42b'),
 (0x402f0,0x200031e4,0x200031e0,0x200031dc,0x20003270,0x200031ec,
  'd386953a4afde83699523eed2fd8fcb8c4c1ffb405641600c77dffcbe13a0163'))
check,sx = timer.check,timer.sx


def decode(raw):
    nodes,off = {},0
    while off<len(raw):
        h=int.from_bytes(raw[off:off+2],'little'); size=2 if h&3!=3 else 4
        check(off+size<=len(raw),'core partial instruction')
        pc,chunk=ENTRY+off,raw[off:off+size]; w=int.from_bytes(chunk,'little')
        d={'pc':pc,'bytes':chunk.hex(),'size':size}
        if size==4 and w&0xfe00707f==0x40000033:
            d.update(op='sub',rd=w>>7&31,rs1=w>>15&31,rs2=w>>20&31)
        elif size==2 and h&3==1 and h>>13==4:
            r=8+(h>>7&7)
            if h>>10&3==2: d.update(op='andi',rd=r,rs1=r,imm=sx((h>>2&31)|(h>>7&32),6))
            elif h>>10&3==3 and not h&0x1000 and h>>5&3==0:
                d.update(op='sub',rd=r,rs1=r,rs2=8+(h>>2&7))
        if 'op' not in d: d=message.decode(chunk,pc)[pc]
        nodes[pc]=d; off+=size
    return nodes


def specs(detail):
    _,small,large,sentinel,fallback,account,_=detail
    rows=[
      (0,'addi',dict(rd=2,rs1=2,imm=-16)),(2,'store',dict(rs2=8,rs1=2,imm=8,width=4)),
      (4,'lui',dict(rd=15,imm=0x40024000)),(8,'store',dict(rs2=1,rs1=2,imm=12,width=4)),
      (10,'load',dict(rd=8,rs1=15,imm=524,width=4)),(14,'store',dict(rs2=0,rs1=15,imm=524,width=4)),
      (18,'fence.i',{}),(22,'beqz',dict(rs1=10,target=ENTRY+26)),
      (24,'bnez',dict(rs1=11,target=ENTRY+38)),(26,'lui',dict(rd=15,imm=0x40024000)),
      (30,'store',dict(rs2=8,rs1=15,imm=524,width=4)),(34,'li',dict(rd=10,imm=0)),
      (36,'jump',dict(target=ENTRY+196)),(38,'addi',dict(rd=15,rs1=10,imm=3)),
      (42,'slli',dict(rd=15,rs1=15,imm=16)),(44,'srli',dict(rd=15,rs1=15,imm=16)),
      (46,'andi',dict(rd=15,rs1=15,imm=-4)),(48,'slli',dict(rd=15,rs1=15,imm=16)),
      (50,'srli',dict(rd=15,rs1=15,imm=16)),(52,'addi',dict(rd=14,rs1=0,imm=52)),
      (56,'bltu',dict(rs1=14,rs2=15,target=ENTRY+100)),(60,'lui',dict(rd=14,imm=0x20003000)),
      (64,'load',dict(rd=10,rs1=14,imm=small-0x20003000,width=4)),
      (68,'lui',dict(rd=14,imm=0x20003000)),(72,'load',dict(rd=13,rs1=14,imm=sentinel-0x20003000,width=4)),
      (76,'bne',dict(rs1=13,rs2=10,target=ENTRY+110)),(80,'lui',dict(rd=14,imm=0x20003000)),
      (84,'load',dict(rd=14,rs1=14,imm=fallback-0x20003000,width=4)),
      (88,'beqz',dict(rs1=14,target=ENTRY+26)),(90,'slli',dict(rd=15,rs1=15,imm=16)),
      (92,'or',dict(rd=11,rs1=11,rs2=15)),(94,'li',dict(rd=10,imm=1)),
      (96,'call_indirect',dict(rd=1,rs1=14)),(98,'jump',dict(target=ENTRY+26)),
      (100,'lui',dict(rd=14,imm=0x20003000)),(104,'load',dict(rd=10,rs1=14,imm=large-0x20003000,width=4)),
      (108,'jump',dict(target=ENTRY+68)),
      (110,'load',dict(rd=14,rs1=10,imm=6,width=2,mnemonic='qk.c.lhu')),
      (112,'bnez',dict(rs1=14,target=ENTRY+204)),
      (114,'load',dict(rd=14,rs1=10,imm=4,width=2,mnemonic='qk.c.lhu')),
      (116,'bltu',dict(rs1=14,rs2=15,target=ENTRY+204)),(120,'lui',dict(rd=13,imm=0x20003000)),
      (124,'sub',dict(rd=12,rs1=14,rs2=15)),(128,'li',dict(rd=16,imm=8)),
      (130,'addi',dict(rd=13,rs1=13,imm=account-0x20003000)),
      (134,'bgeu',dict(rs1=16,rs2=12,target=ENTRY+176)),
      (138,'load',dict(rd=17,rs1=10,imm=0,width=4)),(142,'load',dict(rd=16,rs1=13,imm=6,width=2)),
      (146,'addi',dict(rd=12,rs1=15,imm=8)),(150,'sub',dict(rd=14,rs1=14,rs2=15)),
      (152,'add',dict(rd=12,rs1=12,rs2=10)),(154,'addi',dict(rd=14,rs1=14,imm=-8)),
      (156,'store',dict(rs2=14,rs1=12,imm=4,width=2,mnemonic='qk.c.sh')),
      (158,'store',dict(rs2=17,rs1=12,imm=0,width=4)),(162,'store',dict(rs2=0,rs1=12,imm=6,width=2)),
      (166,'store',dict(rs2=12,rs1=10,imm=0,width=4)),
      (168,'store',dict(rs2=15,rs1=10,imm=4,width=2,mnemonic='qk.c.sh')),
      (170,'addi',dict(rd=14,rs1=16,imm=-8)),
      (174,'store',dict(rs2=14,rs1=13,imm=6,width=2,mnemonic='qk.c.sh')),
      (176,'store',dict(rs2=11,rs1=10,imm=6,width=2,mnemonic='qk.c.sh')),
      (178,'load',dict(rd=11,rs1=13,imm=6,width=2,mnemonic='qk.c.lhu')),
      (180,'addi',dict(rd=10,rs1=10,imm=8)),(182,'sub',dict(rd=15,rs1=11,rs2=15)),
      (186,'store',dict(rs2=15,rs1=13,imm=6,width=2,mnemonic='qk.c.sh')),
      (188,'lui',dict(rd=15,imm=0x40024000)),(192,'store',dict(rs2=8,rs1=15,imm=524,width=4)),
      (196,'load',dict(rd=1,rs1=2,imm=12,width=4)),(198,'load',dict(rd=8,rs1=2,imm=8,width=4)),
      (200,'addi',dict(rd=2,rs1=2,imm=16)),(202,'jr',dict(rs1=1)),
      (204,'load',dict(rd=10,rs1=10,imm=0,width=4)),(206,'jump',dict(target=ENTRY+76))]
    return {ENTRY+off:dict(op=op,**f) for off,op,f in rows}


def reachable(edges,start,blocked=()):
    seen,work=set(),[start]
    while work:
        p=work.pop()
        if p in seen or p in blocked: continue
        seen.add(p);work.extend(edges[p])
    return seen


def derive(app,carriers,header):
    parent=message.derive(app,carriers,header)
    profiles=[]
    for data,meta,detail in zip(carriers,parent['profiles'],DETAILS):
        src,small,large,sentinel,fallback,account,digest=detail
        check((int(meta['core_call']['target'],16),int(meta['core_call']['conditional_source'],16))==(ENTRY,src),'message-to-core source mapping')
        mapping=binding.profile(data,meta['label'])
        first={k:int(v,16) for k,v in mapping['first_copy'].items()}
        check(first['destination']<=ENTRY and ENTRY+LENGTH<=int(mapping['first_copy_end_exclusive'],16) and
              first['source']+ENTRY-first['destination']==src,'complete core first-copy source mapping')
        raw=binding.take(data,src,LENGTH); nodes=decode(raw); expected=specs(detail)
        check(nodes.keys()==expected.keys(),'core instruction boundaries')
        for pc,fields in expected.items(): message.guard(nodes,pc,'core instruction '+hex(pc-ENTRY),**fields)
        spans=tuple((p,4) for p in (64,72,84,104,130))
        check(outer.normalized(raw,spans)==outer.normalized(TEMPLATE,spans),'core complete body template')
        # Opaque call receives only an ASSUMED normal-return continuation edge.
        topology={p:dict(d,op='bne') if d['op']=='bltu' else d for p,d in nodes.items()}
        edges,cycles=timer.cfg(topology,ENTRY)
        ei={int(p,16):[int(q,16) for q in qs] for p,qs in edges.items()}
        check(len(cycles)==1 and set(cycles[0])=={hex(ENTRY+n) for n in (76,110,112,114,116,204,206)},'core search SCC')
        check(ENTRY+202 not in reachable(ei,ENTRY,{ENTRY+30,ENTRY+192}),'core control-restore cut set')
        check(ENTRY+202 not in reachable(ei,ENTRY,{ENTRY+196}) and
              ENTRY+202 not in reachable(ei,ENTRY,{ENTRY+198}),'core frame-restore dominance')
        writes=sorted({d['rd'] for d in nodes.values() if d.get('rd',0)})
        check(writes==[1,2,8,10,11,12,13,14,15,16,17],'core encoded GPR writes')
        check(not any(d.get(k)==12 for p,d in nodes.items() if p<ENTRY+110 for k in ('rd','rs1','rs2')),
              'core prefix ambient A2 untouched')
        a2writes=[p for p,d in nodes.items() if d.get('rd')==12]
        check(a2writes and min(a2writes)==ENTRY+124 and ENTRY+96 not in reachable(ei,ENTRY+124),
              'core A2 first definition is fit-path only')
        profiles.append({'label':meta['label'],'runtime_target':hex(ENTRY),'load_image_source':hex(src),
            'bytes':LENGTH,'sha256':sha256(raw).hexdigest(),'expected_sha256':digest,
            'slots':{k:hex(v) for k,v in dict(small_head=small,large_head=large,sentinel=sentinel,fallback=fallback,account_base=account).items()},
            'instructions':list(nodes.values()),'conditional_normal_return_CFG':edges,'cyclic_SCCs':cycles,
            'opaque_normal_return_edge':[hex(ENTRY+96),hex(ENTRY+98)],'opaque_callee_effects_proved':False,
            'encoded_GPR_writes':writes,'encoded_GPR_not_written':[i for i in range(1,32) if i not in writes],
            'control_restore_cut_set':[hex(ENTRY+30),hex(ENTRY+192)],'frame_restore_dominates_encoded_ret':True,
            'fallback':{'call_pc':hex(ENTRY+96),'target':'fresh U32[fallback slot], JALR clears bit0',
                'link':hex(ENTRY+98),'A0':1,'A1':'full_input_A1 | (rounded_R << 16)',
                'A2':'ambient caller value, untouched by encoded prefix',
                'normal_reply_A0_discarded':True,'normal_continuation_A0':0,'list_retry_after_call':False},
            'first_A2_write_pc':hex(ENTRY+124),'entire_core_A2_untouched':False,
            'finite_termination_proved':False,'installed_binding_proved':False,
            'saved_frame_control_and_code_integrity_proved':False})
    return {'schema':'TSL9-allocation-core-static-v1','profile':timer.PROFILE,
        'scope':'Complete static operands/conditional CFG/write sets and host algebra; no ISA/heap/provider/MMIO execution',
        'installed_binding_proved':False,'physical_ISA_profile_proved':False,
        'rounded_R':'((full_input_A0 + 3) & 0xffff) & 0xfffc',
        'early_reject':'full_input_A0 == 0 OR full_input_A1 == 0, AFTER control prelude',
        'small_head_condition':'R <= 52','fit':'U16[cur+6] == 0 AND U16[cur+4] >= R',
        'split_condition':'U16[cur+4] - R > 8',
        'no_split_stored_size':'original U16[cur+4], unchanged',
        'split_new_header':'(cur + R + 8) & 0xffffffff','split_new_size':'original_U16_size - R - 8',
        'tag_written':'low16(full_input_A1), may be zero even if full_input_A1 is nonzero',
        'success_return':'(cur + 8) & 0xffffffff, may wrap to zero',
        'account_formula_nonalias':'(old_U16 - R - (8 if split else 0)) & 0xffff',
        'account_formula_requires_stable_nonalias_reads':True,
        'account_subtracts_stored_block_size_on_no_split':False,
        'no_counter_increment_in_encoded_core':True,
        'conditional_APP_descriptor_request12_composition':{
            'core_input_size':20,'rounded_R':20,'input_tag':'0xf00c','table':'small',
            'core_return_P':'(cur+8)&0xffffffff','message_return_D':'(cur+16)&0xffffffff',
            'allocator_marker_D_minus2':'(cur+14)&0xffffffff','APP_marker_D_plus2':'(cur+18)&0xffffffff',
            'split_condition':'original_U16_size > 28','no_split_size_range':[20,28],
            'account_subtraction_split':28,'account_subtraction_no_split':20},
        'profiles':profiles}


def tests(app,carriers,header):
    small,large,wrapped=0,0,[]
    for length in range(65536):
        r=((length+3)&65535)&0xfffc
        check(r==((length+3)//4*4)&65535 and r%4==0,'core rounding algebra')
        if length:
            if r<=52:small+=1
            else:large+=1
        if length and not r:wrapped.append(length)
    check((small,large,wrapped)==(55,65480,[65533,65534,65535]),'core U16 table domains and zero rounding')
    for gap in range(65536):
        split=gap>8
        check(split==(not 8>=gap),'core unsigned split boundary')
        if split:check(0<gap-8<=65527,'core split remainder range')
    for value,r,split in product(range(65536),(0,4,20,52,56,65532),(False,True)):
        sequential=(((value-8)&65535) if split else value)-r
        check(sequential&65535==(value-r-(8 if split else 0))&65535,'core modulo accounting algebra')
    check((20,24,False,(100-20)&65535,24)==(20,24,24-20>8,80,24),'core no-split accounting witness')
    check(0x10000!=0 and (0x10000&65535)==0,'core full-tag guard does not imply nonzero stored flag')
    cases=(
      (46,'f19b','e19b'),(94,'0545','0945'),(96,'0297','8297'),
      (34,'0145','0545'),(110,'7a21','5a21'),(128,'2148','3148'),
      (156,'5aa2','7aa2'),(158,'23201601','23221601'),
      (176,'6ea1','4ea1'),(182,'b387f540','b387e540'))
    for off,before,after in cases:
        changed=[bytearray(c) for c in carriers];p=DETAILS[0][0]+off-LIB
        old,new=bytes.fromhex(before),bytes.fromhex(after)
        check(changed[0][p:p+len(old)]==old,'core mutation pin')
        changed[0][p:p+len(new)]=new
        try:derive(app,changed,header)
        except RuntimeError as error:check(str(error)=='core instruction '+hex(off),'unexpected core mutation guard: '+str(error))
        else:raise RuntimeError('core mutation escaped')
    print('PASS: 65536 rounding cases (55 small/65480 large/1 zero input); 65536 split gaps; 786432 U16 accounting cases; 10 specified raw mutations')


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true',help='Create ledger exclusively')
    options=p.parse_args();app,header=binding.APP.read_bytes(),outer.HEADER.read_bytes()
    check(len(app)==76800 and sha256(app).hexdigest()==binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==outer.HEADER_HASH,'SDK header identity')
    carriers=[]
    for label,folder,tail,n,digest in binding.PROFILES:
        raw=(ROOT/'analysis/wch-resident-candidate-2026-10-21'/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(raw)==n and sha256(raw).hexdigest()==digest,'candidate identity '+label);carriers.append(raw)
    sources,vectors=timer.source_contract();ledger=derive(app,carriers,header)
    ledger['sources'],ledger['official_Xwchc_vectors']=sources,vectors
    for v in ledger['profiles']:check(v['sha256']==v['expected_sha256'],'core complete body identity')
    tests(app,carriers,header);output=(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n').encode('utf-8')
    if options.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'core ledger exact replay')
    print('PASS: 2 complete cores, 416 bytes/144 instructions; conditional CFG/SCC; fallback-zero return; encoded restore cut set')
    print('PASS: ledger exact replay; installed/fallback/context integrity UNPROVED; NO ISA/provider/heap/MMIO execution')


if __name__=='__main__':main()
