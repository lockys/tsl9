"""Post-RF leaves, unbounded MMIO wait, and large magic-entry preservation.

Static decoding/CFG/operand/store/frame contracts only. Numeric DIV/packing
results and hardware state are not modeled; no target is executed/emulated.
"""
import argparse
import json
from collections import Counter,deque
from hashlib import sha256
from pathlib import Path
import check_v4160_rf_tail_return_static as previous

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-post-rf-leaves-static.json')
ROLES=('large','enable','wait','final')
SIZES=(3388,18,148,56)
COUNTS=(1032,6,60,24)
DETAILS=(
 ((0x6645c,0x67198,0x662da,0x6636e),0,0x20002df2,
 ('7d48a5568c5e2a17a5bb1261e79183cafe44b9463b3beb6426213066be999b89','9bb8f59add21978de5aaf58cff0dc95794fcdd818ab50faf1ff180b2ba60588d',
  'af38386d56649406f3a87b3c80a7673e38ffd67a9d11f85296b952826e784698','8ab97770ea65f4cf16bea8ea7b35db57a3cdd2508407a6e2e5f236f156b3665b')),
 ((0x6659a,0x672d6,0x66418,0x664ac),80,0x20002e3e,
 ('bd2030c3d651a18010efe907dfd050fd3ba0af6bea56521e11bc293a4b245e00','ceabac004c0b1a1d3cab4b8488161b77918b918e80f76d016ca662a7e58534a5',
  'a9f9f86eb20c480766d9b9763b8d869d09f4d077fa9fd136acd2be10bcde3c26','994190d61318ce7f41f7925ea5dc3a1476fb045e05e805a6f322e8cac3c87d4e')))
LARGE_SAVED=((8,72),(9,68),(19,60),(1,76),(18,64),(20,56),(21,52),(22,48),(23,44),(24,40),(25,36),(26,32),(27,28))
LARGE_OPS={'addi':33,'and':82,'andi':132,'auipc':3,'beq':1,'div':99,'jal':1,'jalr':3,'jr':1,'li':41,'load':159,'lui':26,'mul':74,'or':108,'ori':15,'slli':102,'srli':3,'store':145,'sub':4}


def specs(role,index):
    addresses,delta,service,_=DETAILS[index];pc=addresses[ROLES.index(role)];s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def lui(o,r,v):e(o,'lui',rd=r,imm=v)
    def imm(o,op,r,b,v):e(o,op,rd=r,rs1=b,imm=v)
    def load(o,r,b,v,w=4,**f):e(o,'load',rd=r,rs1=b,imm=v,width=w,**f)
    def store(o,r,b,v,w=4,**f):e(o,'store',rs2=r,rs1=b,imm=v,width=w,**f)
    def binary(o,op,r,a,b):e(o,op,rd=r,rs1=a,rs2=b)
    def bz(o,r,t):e(o,'beqz',rs1=r,target=pc+t)
    if role=='enable':
        lui(0,15,0x20003000);load(4,14,15,1424+delta);load(8,15,14,4);imm(10,'ori',15,15,256);store(14,15,14,4);e(16,'jr',rs1=1)
    elif role=='wait':
        lui(0,14,0x20003000);load(4,15,14,1424+delta);lui(8,12,0xffff0000);imm(10,'addi',12,12,-1)
        load(12,13,15,80);binary(14,'and',13,13,12);store(16,13,15,80);load(18,13,15,8);lui(20,12,0x200000)
        binary(24,'or',13,13,12);store(26,13,15,8);load(28,13,15,12);imm(30,'ori',13,13,16);store(34,13,15,12)
        load(36,13,15,12);imm(38,'andi',13,13,-17);store(40,13,15,12)
        for o in (42,44,46,48,98,100,102,104):e(o,'nop')
        load(50,13,14,1424+delta);lui(54,12,4096);load(56,15,13,12);imm(58,'ori',15,15,16);store(62,15,13,12)
        load(64,15,13,4);binary(66,'or',15,15,12);store(68,15,13,4);lui(70,15,0x20003000);load(74,12,15,1340+delta)
        imm(78,'addi',15,0,80);store(82,15,12,100);load(84,15,12,100);bz(86,15,98);load(88,15,13,156)
        imm(92,'srli',15,15,8);imm(94,'andi',15,15,1);bz(96,15,84);load(106,15,14,1424+delta)
        lui(110,12,65536);load(112,14,15,156);load(116,13,15,80);binary(118,'or',13,13,12);store(120,13,15,80)
        imm(122,'andi',13,14,31);load(126,14,15,80);imm(128,'andi',14,14,-32);binary(130,'or',14,14,13);store(132,14,15,80)
        load(134,14,15,8);lui(136,13,0xffe00000);imm(140,'addi',13,13,-1);binary(142,'and',14,14,13);store(144,14,15,8);e(146,'jr',rs1=1)
    elif role=='final':
        lui(0,15,0x20003000);load(4,15,15,1424+delta);lui(8,14,0xffff0000);imm(10,'addi',14,14,-1);load(12,13,15,88)
        lui(14,12,65536);binary(16,'and',13,13,14);store(18,13,15,88);load(20,13,15,8);binary(22,'or',13,13,12)
        store(24,13,15,8);load(26,13,15,12);imm(28,'andi',13,13,-257);store(32,13,15,12);load(34,13,15,4)
        binary(36,'and',14,14,13);store(38,14,15,4);load(40,13,15,12);imm(42,'ori',13,13,256);store(46,13,15,12)
        load(48,14,15,4);binary(50,'or',14,14,12);store(52,14,15,4);e(54,'jr',rs1=1)
    else:
        imm(0,'addi',2,2,-80);store(2,8,2,72);lui(4,8,0x20003000);load(8,15,8,1424+delta)
        for o,(r,v) in zip(range(12,36,2),LARGE_SAVED[1:]):store(o,r,2,v)
        load(36,14,15,4);lui(38,13,0xfffff000);imm(40,'addi',13,13,-1);imm(42,'andi',14,14,-257);store(46,14,15,4)
        load(48,14,15,40);lui(50,11,0x20003000);imm(54,'addi',11,11,-89+delta);binary(58,'and',14,14,13);store(60,14,15,40)
        load(62,14,15,44);lui(64,13,0x20000);lui(68,9,0x20003000);imm(72,'andi',14,14,-17);store(74,14,15,44)
        load(76,14,15,8);imm(78,'addi',9,9,-90+delta);lui(82,19,0x20003000);binary(86,'or',14,14,13);store(88,14,15,8)
        load(90,14,15,4);lui(92,13,0x20003000);imm(96,'ori',14,14,16);store(100,14,15,4);load(102,12,13,1416+delta)
        lui(106,14,0x12345000);imm(110,'addi',14,14,1656);store(114,11,2,12);e(116,'beq',rs1=12,rs2=14,target=pc+3380)
        for au,upper,low in zip((156,222,298),((0x1ff9d000,)*3 if index==0 else (0x1ff9d000,0x1ff9c000,0x1ff9c000)),((-1798,-1864,-1940) if index==0 else (-2040,1990,1914))):
            e(au,'auipc',rd=1,imm=upper);e(au+4,'jalr',rd=1,rs1=1,imm=low)
        load(164,15,8,1424+delta);load(230,15,8,1424+delta)
        load(310,15,14,144);imm(314,'andi',15,15,63);load(322,15,14,148);imm(330,'srli',15,15,10);imm(332,'andi',15,15,127)
        load(340,15,19,1428+delta,1);load(344,13,9,0,1,mnemonic='qk.c.lbu');store(348,15,2,8);load(350,14,2,8);load(352,15,8,1424+delta)
        for o,(r,v) in zip(range(3350,3376,2),((1,76),(8,72),(9,68),(18,64),(19,60),(20,56),(21,52),(22,48),(23,44),(24,40),(25,36),(26,32),(27,28))):load(o,r,2,v)
        imm(3376,'addi',2,2,80);e(3378,'jr',rs1=1);store(3380,0,13,1416+delta);e(3384,'jal',rd=0,target=pc+340)
    return pc,s


def edges(n):
    e={}
    for p,d in n.items():
        op=d['op']
        if op=='jr':check(d['rs1']==1,'post RF ordinary RET');q=[]
        elif op in ('beq','beqz'):q=[p+d['size'],d['target']]
        elif op=='jal':check(d['rd']==0,'post RF explicit tail jump');q=[d['target']]
        else:q=[p+d['size']]
        check(all(v in n for v in q),'post RF full local CFG');e[p]=q
    return e


def reachable(e,start):
    seen=set();todo=[start]
    while todo:
        p=todo.pop()
        if p in seen:continue
        seen.add(p);todo.extend(e[p])
    return seen


def acyclic(e):
    ind={p:0 for p in e}
    for qs in e.values():
        for q in qs:ind[q]+=1
    todo=deque(p for p,d in ind.items() if d==0);count=0
    while todo:
        p=todo.popleft();count+=1
        for q in e[p]:
            ind[q]-=1
            if ind[q]==0:todo.append(q)
    return count==len(e)


def inspect(raw,role,index):
    pc,s=specs(role,index);n=decode(raw,pc)
    check(set(s)<=set(n) if role=='large' else set(n)==set(s),'post RF '+role+' boundaries')
    for p,f in s.items():init.g(n,p,'post RF '+role+' operand '+hex(p-pc),**f)
    j=ROLES.index(role);check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[j],COUNTS[j],DETAILS[index][-1][j]),'post RF '+role+' full identity')
    e=edges(n);check(reachable(e,pc)==set(n),'post RF all local nodes reachable')
    stores=[d for d in n.values() if d['op']=='store'];loads=[d for d in n.values() if d['op']=='load']
    check((len(stores),len(loads))=={'large':(145,159),'enable':(1,2),'wait':(10,16),'final':(6,7)}[role],'post RF exact memory census')
    if role!='wait':check(acyclic(e),'post RF acyclic local CFG')
    else:
        cycles=[c for c in previous.previous.graphs.components(e) if len(c)>1 or c[0] in e[c[0]]]
        check(cycles==[[pc+x for x in (84,86,88,92,94,96)]],'post RF unique six-node wait SCC')
    if role!='large':
        check({d['rd'] for d in n.values() if d.get('rd',0)}==({14,15} if role=='enable' else {12,13,14,15}),'post RF leaf precise definitions')
        check(all(d['width']==4 for d in stores),'post RF only word MMIO stores')
    else:
        check(Counter(d['op'] for d in n.values())==LARGE_OPS,'post RF large opcode census')
        check([p-pc for p,d in n.items() if d.get('rd')==2]==[0,3376],'post RF large only balanced SP definitions')
        check(not any(d.get('rd')==3 for d in n.values()),'post RF large GP untouched')
        check([p-pc for p,d in n.items() if d.get('rd')==15]==[8,164,230,310,314,322,330,332,340,352],'post RF large all pointer definitions')
        check(not any(d.get('rd')==8 for p,d in n.items() if pc+4<p<pc+352),'post RF S0 fixed through last base load')
        frames=[(d['pc']-pc,d['rs2'],d['imm'],d['width']) for d in stores if d['rs1']==2]
        check(frames==[(o,r,v,4) for o,(r,v) in zip((2,*range(12,36,2)),LARGE_SAVED)]+[(114,11,12,4),(348,15,8,4)],'post RF exact saved/scratch store census')
        common=[d for d in stores if pc+340<=d['pc']<pc+3380 and d['rs1']!=2]
        check(len(common)==109 and all(d['rs1']==15 and d['width']==4 for d in common),'post RF common all109 word stores use stable A5')
        check({d['imm'] for d in common}=={4,40,44,56,*range(160,209,4)},'post RF common exact MMIO offset set')
    return n,e


def render_small(raw,role,index):
    n,e=inspect(raw,role,index);pc=next(iter(n))
    return {'start':hex(pc),'bytes':len(raw),'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),
        'normal_return_CFG':{hex(p):[hex(q) for q in qs] for p,qs in e.items()},'complete_function':True}


def large_contract(data,index):
    pc=DETAILS[index][0][0];delta=DETAILS[index][1];raw=init.binding.take(data,pc,3388);n,e=inspect(raw,'large',index)
    selected=previous.paths.chain(e,pc,{pc+116:pc+3380});selected_set={int(p,16) for p in selected}
    calls=[]
    for off in (156,222,298):
        au=n[pc+off];call=n[pc+off+4];target=(au['pc']+au['imm']+call['imm'])&0xfffffffe
        check(target==DETAILS[index][2] and pc+off not in selected_set,'post RF magic excludes three mapped service calls')
        calls.append({'AUIPC':hex(pc+off),'JALR':hex(pc+off+4),'target':hex(target),'link':hex(pc+off+8)})
    picked=[n[p] for p in map(lambda x:int(x,16),selected)]
    nonframe=[d for d in picked if d['op']=='store' and d['rs1']!=2]
    ram=[d for d in nonframe if d['pc']==pc+3380];mmio=[d for d in nonframe if d['pc']!=pc+3380]
    check(len(ram)==1 and len(mmio)==114,'post RF magic one RAM word and114 MMIO stores')
    check(all(d['rs1']==15 and d['width']==4 for d in mmio),'post RF magic all MMIO writes through stable published bases')
    check([d['pc']-pc for d in picked if d['op']=='store' and d['rs1']==2]==[2,*range(12,36,2),114,348],'post RF magic frame stores exact')
    # All saved words [28,80) exclude scratch words [8,12), [12,16).
    for _,v in LARGE_SAVED:
        for scratch in (8,12):check(previous.paths.origin.separated(v,4,scratch,4),'post RF saved frame excludes scratch')
    magic=0x20003588+delta
    previous.preservation(delta,[(magic,4)])
    structural={'pc':hex(pc),'bytes':3388,'sha256':sha256(raw).hexdigest(),'instruction_count':len(n),'load_count':159,'store_count':145,
        'opcode_census':dict(sorted(Counter(d['op'] for d in n.values()).items())),
        'control_edges':[{'pc':hex(p),'op':n[p]['op'],'successors':[hex(q) for q in e[p]]} for p in n if n[p]['op'] in ('beq','jal','jalr','jr')],
        'calls':calls,'guarded_instructions':[n[p] for p in specs('large',index)[1]],
        'all_store_operands':[[d['pc']-pc,d['rs1'],d['imm'],d['rs2'],d['width']] for d in n.values() if d['op']=='store'],
        'whole_CFG_digest':sha256(json.dumps({str(p-pc):[q-pc for q in qs] for p,qs in e.items()},sort_keys=True).encode()).hexdigest(),
        'all_nodes_reachable':True,'acyclic_local_CFG':True,
        'semantic_scope':'whole bytes/decode/CFG/GPR/store/frame contract; independently guarded prefix, pointers, control and epilogue; common DIV/packing numeric formulas not reconstructed'}
    return {'body':structural,'additional_fresh_magic_premise':{'address':hex(magic),'value':'0x12345678'},
        'selected_magic_path':selected,'magic_consumption_store':hex(pc+3380),'magic_join':hex(pc+340),
        'conditional_selected_MMIO_store_count':114,'sole_selected_fixed_RAM_store':{'address':hex(magic),'bytes':4,'value':0},
        'common_last_base_load':hex(pc+352),'conditional_base_value':'0x40025000','common_MMIO_store_count':109,
        'frame_bytes':80,'saved_RA_and_all12_S_registers':True,'conditional_normal_return':True,'A0_return_value':'opaque',
        'unmatched_magic_boundary':{'cut_before_AUIPC':hex(pc+156),'service':hex(DETAILS[index][2])}}


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[]
    for i,(data,pr,detail) in enumerate(zip(carriers,parent['profiles'],DETAILS)):
        addresses,delta,_,_=detail
        check(pr['cut_before_next_call']['target']==hex(addresses[0]) and pr['tail_remaining_calls']==[hex(p) for p in addresses],'post RF upstream target join')
        small={r:render_small(init.binding.take(data,p,z),r,i) for r,p,z in zip(ROLES[1:],addresses[1:],SIZES[1:])}
        large=large_contract(data,i);wp=addresses[2];wn={d['pc']:d for d in small['wait']['instructions']};we=previous.edge_map(small['wait'])
        paths={key:previous.paths.chain(we,wp,{wp+86:q,wp+96:t}) for key,q,t in
            (('R_zero',wp+98,wp+98),('R_nonzero_Q_bit8_one',wp+88,wp+98))}
        check(hex(wp+88) not in paths['R_zero'] and hex(wp+88) in paths['R_nonzero_Q_bit8_one'],'post RF wait short circuit')
        loop_nodes={wp+x for x in (84,86,88,92,94,96)}
        check(not any(wn[p]['op']=='store' or wn[p].get('rd') in (12,13,14) for p in loop_nodes),'post RF wait no stores/base reload/countdown')
        stable={wp+84:[wp+86],wp+86:[wp+88],wp+88:[wp+92],wp+92:[wp+94],wp+94:[wp+96],wp+96:[wp+84]}
        check(not acyclic(stable),'post RF continuing nonzero/unset-bit CFG cycle exists')
        profiles.append({'label':pr['label'],'large':large,'leaves':small,'wait_two_exit_paths':paths,
            'wait_SCC_offsets':[84,86,88,92,94,96],'wait_no_timeout':True,
            'wait_load_snapshots':{'Q_loads':[hex(wp+x) for x in (4,50,106)],'R_load':hex(wp+74),'exit_then_new_Q_status_load':hex(wp+112)},
            'wait_loop_bases_not_reloaded':True,'leaves_total_MMIO_store_sites':17,
            'conditional_outer_tail_return':'additional fresh magic==12345678, matching pointer mappings, normal accesses/instructions, preserved nonalias frames and no adverse hardware/asynchronous interference; wait additionally eventually satisfies R+100==0 OR Q1+156 bit8==1. Then four callees preserve needed S/frame; outer tail stores state0/S4 snapshot and RET. No actual reachability/event guarantee',
            'conditional_context_gate':5,'conditional_count':6,'actual_installed_binding_proved':False})
    return {'schema':'TSL9-post-RF-leaves-static-v1','profile':parent['profile'],'APP_sha256':sha256(image).hexdigest(),'profiles':profiles,
        'scope':'per candidate full3388B large structural contract and three complete222B/90instruction leaves; no new C bytes',
        'large_magic_boundary':'magic branch consumes one fresh matching word and rejoins common arithmetic, not direct epilogue. Selected path excludes all three mapped services. Common99 signed DIV and packing values remain opaque; fixed store destinations/frame/GPR contract independent of numeric payload validity',
        'wait_contract':'three independently fresh Q0/Q1/Q2 loads and one R0 load require mapping premises. Each iteration reads R0+100 first; zero exits without reading Q1 status; otherwise fresh Q1+156 bit8=1 exits. No counter/timeout. All iterations R nonzero and bit8 zero admit an infinite path. Eight NOPs do not prove bounded waiting',
        'readback_boundary':'initial CPU store80(decimal) to R0+100 does not prove hardware countdown or eventual zero. Q2+156 read after loop is independent of earlier Q1 sample; fresh RMW pairs are not coherent snapshots or inverse hardware restoration',
        'preservation':'selected large only own80B frame, one consumed magic word,114 conditional MMIO stores; all three leaves only MMIO stores and A2..A5 definitions. Valid nonalias frames/global/mappings and no adverse MMIO/FENCE.I/IRQ/DMA/reentry/external writers remain premises; A0 opaque after large',
        'remaining':['unmatched magic path mapped service20002df2/20002e3e and later calls','magic writers/actual reachable branch and wait completion','remaining initializer callees/tail and actual installed providers/lifetimes'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    operands=nops=0
    for i,(data,detail) in enumerate(zip(carriers,DETAILS)):
        for role,pc,size in zip(ROLES,detail[0],SIZES):
            raw=init.binding.take(data,pc,size);n=decode(raw,pc)
            for p in specs(role,i)[1]:
                d=n[p];at=p-pc;w=d['size'];buf=bytearray(raw);isnop=d['op']=='nop'
                buf[at:at+w]=(int.from_bytes(buf[at:at+w],'little')^(4 if isnop or w==2 else 1<<20)).to_bytes(w,'little')
                try:inspect(buf,role,i)
                except RuntimeError as e:
                    check(str(e)=='unsupported static leaf encoding '+hex(p) if isnop else str(e).startswith('post RF '+role+' operand '),'post RF mutation required guard '+str(e))
                else:raise RuntimeError('post RF mutation escaped')
                if isnop:nops+=1
                else:operands+=1
    check((operands,nops)==(324,16),'post RF mutation census '+str((operands,nops)))
    check((0xffff0000-1)&0xffffffff==0xfffeffff and (0xffe00000-1)&0xffffffff==0xffdfffff,'post RF decrement masks')
    check(0x12345000+1656==0x12345678,'post RF magic constant')
    print('PASS:324 operand mutations and16 noncanonical NOP encodings rejected; explicit continuing-cycle witness and mask identities')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');o=parser.parse_args()
    image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK header identity')
    carriers=[]
    for label,folder,tail,size,digest in init.binding.PROFILES:
        raw=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(raw)==size and sha256(raw).hexdigest()==digest,'candidate identity '+label);carriers.append(raw)
    raw_hex=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
    coverage=sparse.derive(image,carriers,header,raw_hex,sparse.parser())
    ledger=derive(image,carriers,header,coverage);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract()
    tests(carriers);output=(json.dumps(ledger,indent=1,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'post RF exact ledger replay')
    print('PASS:large full structural/magic-path frame preservation; three leaves and unbounded MMIO wait; exact ledger')
    print('PASS:NO target execution; actual magic/event reachability, nonmagic services and installed binding UNPROVED')


if __name__=='__main__':main()
