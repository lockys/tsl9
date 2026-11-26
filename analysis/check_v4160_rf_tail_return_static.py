"""RF A0=13 return cases and the next tail-call cut, strictly offline.

Decode/operand/CFG/store/frame contracts and bit/interval identities only.
No target execution, emulation, mutable MMIO model or callback invocation.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_radio_config_chain_static as previous
import check_v4160_timer_start_setup_static as paths

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-rf-tail-return-static.json')
ROLES=('rf','reset','tail')
SIZES=(198,130,232)
COUNTS=(72,48,79)
DETAILS=(
 ((0x63eda,0x63e58,0x641b0),0,(0x6645c,0x67198,0x662da,0x6636e),
 ('e6d7c29e07d6e998b779415f5f951411d3ce419a3b34b209c1e084be28382dff',
  '78c0d7c677f9c05545b1f0df5ff9c4ad3ccf8745c81dc7da8e50f85cc30570e7',
  '7fc45d07fe76aea16bd8cf6c22b480e65790b42c28c3952dc16e81603d5a5f03')),
 ((0x63fc4,0x63f42,0x6429a),80,(0x6659a,0x672d6,0x66418,0x664ac),
 ('1557d799119cb7d1ad9b7644e0d7b5d33e35b7e211ced043918632c9576a001c',
  'd829879280bba9f7ef5915cc4292bd5afdd4fe9aab9270f49cd71d5a8eb16fb6',
  '301b39915f60afe97df27bfe26df6db47ff01cc7524708f6c55616b9c52a5242')))
RF_SAVED=((18,0),(1,12),(8,8),(9,4))
TAIL_SAVED=((8,24),(1,28),(9,20),(18,16),(19,12),(20,8),(21,4))


def specs(role,index):
    addresses,delta,later,_=DETAILS[index];pc=addresses[ROLES.index(role)];s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def lui(o,r,v):e(o,'lui',rd=r,imm=v)
    def imm(o,op,r,b,v):e(o,op,rd=r,rs1=b,imm=v)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    def load(o,r,b,v,w=4,**f):e(o,'load',rd=r,rs1=b,imm=v,width=w,**f)
    def store(o,r,b,v,w=4,**f):e(o,'store',rs2=r,rs1=b,imm=v,width=w,**f)
    def binary(o,op,r,a,b):e(o,op,rd=r,rs1=a,rs2=b)
    def branch(o,op,a,b,t):e(o,op,rs1=a,rs2=b,target=pc+t)
    def bz(o,op,r,t):e(o,op,rs1=r,target=pc+t)
    def byte(o,r,b,v):load(o,r,b,v,1,mnemonic='qk.c.lbu')
    if role=='rf':
        imm(0,'addi',2,2,-16);store(2,18,2,0);lui(4,15,0x40024000)
        for o,r,v in ((8,1,12),(10,8,8),(12,9,4)):store(o,r,2,v)
        load(14,18,15,524);store(18,0,15,524);e(22,'fence.i');lui(26,15,0x20003000)
        load(30,15,15,1340+delta);load(34,15,15,0);imm(36,'andi',15,15,3);bz(38,'beqz',15,124)
        lui(40,8,0x20003000);imm(44,'addi',15,8,1300+delta);byte(48,15,15,7);li(50,14,3)
        e(52,'mv',rd=9,rs2=10);imm(54,'addi',8,8,1300+delta);branch(58,'bne',14,15,78)
        lui(62,15,0x20003000);load(66,15,15,1360+delta);li(70,12,0);li(72,11,0);li(74,10,17)
        e(76,'call_indirect',rd=1,rs1=15);li(78,14,6);branch(80,'bne',9,14,144)
        byte(84,15,8,9);bz(86,'beqz',15,98);byte(88,15,8,8);branch(90,'bne',15,9,98);store(94,0,8,9,1)
        byte(98,15,8,7);li(100,14,8);branch(102,'bne',14,15,112);imm(106,'addi',15,0,264)
        store(110,15,8,8,2,mnemonic='qk.c.sh');lui(112,15,0x20003000);store(116,0,15,-260+delta,1)
        e(120,'jal',rd=1,target=addresses[1]);load(124,1,2,12);load(126,8,2,8);lui(128,15,0x40024000)
        store(132,18,15,524);load(136,9,2,4);load(138,18,2,0);imm(140,'addi',2,2,16);e(142,'jr',rs1=1)
        li(144,15,7);branch(146,'bne',9,15,164);byte(150,15,8,9);bz(152,'beqz',15,98)
        byte(154,14,8,8);li(156,15,3);branch(158,'bne',14,15,98);e(162,'jump',target=pc+94)
        byte(164,13,8,7);branch(166,'beq',14,13,184);byte(170,14,8,7);branch(172,'beq',15,14,184)
        byte(176,15,8,7);li(178,14,8);branch(180,'bne',14,15,112);byte(184,15,8,9);bz(186,'bnez',15,112)
        byte(188,15,8,7);store(190,15,8,8,1,mnemonic='qk.c.sb');li(192,15,1)
        store(194,15,8,9,1,mnemonic='qk.c.sb');e(196,'jump',target=pc+112)
    elif role=='reset':
        lui(0,14,0x20003000);load(4,15,14,1340+delta);load(8,13,15,80);imm(10,'andi',13,13,-8)
        store(12,13,15,80);load(14,13,15,0);imm(16,'ori',13,13,8);store(20,13,15,0)
        load(22,15,15,0);imm(24,'srli',15,15,3);imm(26,'andi',15,15,1);bz(28,'beqz',15,38)
        for o in (30,32,34,36):e(o,'nop')
        lui(38,15,0x20003000);load(42,13,15,1288+delta);load(46,15,13,0);imm(48,'andi',15,15,-385)
        imm(52,'ori',15,15,128);store(56,15,13,0);lui(58,15,0x20003000);load(62,12,15,1424+delta)
        lui(66,13,0xffce0000);imm(70,'addi',13,13,-1);load(72,15,12,8);binary(74,'and',15,15,13)
        store(76,15,12,8);load(78,15,14,1340+delta);store(82,0,15,80);lui(86,15,0x20003000)
        load(90,15,15,1292+delta);bz(94,'beqz',15,116);load(96,13,15,4);load(98,12,15,8);load(100,14,13,0)
        binary(102,'or',14,14,12);store(104,14,13,0);load(106,13,15,16);load(108,15,15,20);load(110,14,13,0)
        binary(112,'or',15,15,14);store(114,15,13,0);lui(116,15,0x20003000);imm(120,'addi',15,15,1300+delta)
        store(124,0,15,7,1);e(128,'jr',rs1=1)
    else:
        s=dict(previous.specs('tail_prefix',index)[1])
        lui(76,21,0x20003000);load(80,15,21,1288+delta);lui(84,13,0xffffd000);imm(86,'addi',13,13,-1)
        load(88,14,15,0);lui(90,19,0x20003000);lui(94,18,0x20003000);binary(98,'and',14,14,13)
        lui(100,13,4096);binary(102,'or',14,14,13);store(104,14,15,0);load(106,14,15,0)
        lui(108,13,0x330000);imm(112,'andi',14,14,-385);store(116,14,15,0);load(118,14,15,0)
        imm(120,'andi',14,14,-385);imm(124,'ori',14,14,256);store(128,14,15,0);load(130,14,19,1424+delta)
        load(134,15,14,8);binary(136,'or',15,15,13);store(138,15,14,8);load(140,15,18,1340+delta)
        imm(144,'addi',14,0,93);store(148,14,15,80)
        for o,t in zip((150,154,158,162),later):e(o,'jal',rd=1,target=t)
        load(166,14,21,1288+delta);load(170,15,14,0);imm(172,'andi',15,15,-385);imm(176,'ori',15,15,128)
        store(180,15,14,0);load(182,13,19,1424+delta);lui(186,14,0xffce0000);imm(190,'addi',14,14,-1)
        load(192,15,13,8);binary(194,'and',15,15,14);store(196,15,13,8);load(198,15,18,1340+delta)
        store(202,0,15,80);store(206,0,8,7,1);store(210,20,9,524)
        for o,r,v in ((214,1,28),(216,8,24),(218,9,20),(220,18,16),(222,19,12),(224,20,8),(226,21,4)):load(o,r,2,v)
        imm(228,'addi',2,2,32);e(230,'jr',rs1=1)
    return pc,s


def body(raw,role,index):
    pc,s=specs(role,index);n=decode(raw,pc);j=ROLES.index(role)
    check(set(n)==set(s),'RF '+role+' boundaries')
    for p,f in s.items():init.g(n,p,'RF '+role+' operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[j],COUNTS[j],DETAILS[index][-1][j]),'RF '+role+' full identity')
    edges={};calls=[]
    for p,d in n.items():
        op=d['op']
        if op=='jr':check(d['rs1']==1,'RF ordinary RET');q=[]
        elif op in ('beq','bne','beqz','bnez'):q=[p+d['size'],d['target']]
        elif op=='jump':q=[d['target']]
        else:q=[p+d['size']]
        check(all(v in n for v in q),'RF complete local CFG');edges[p]=q
        if op in ('jal','call_indirect'):calls.append({'pc':hex(p),'op':op,'target':hex(d['target']) if 'target' in d else 'fresh A5','link':hex(p+d['size'])})
    check(not any(len(c)>1 or c[0] in edges[c[0]] for c in previous.graphs.components(edges)),'RF acyclic normal-return CFG')
    stores=[d for d in n.values() if d['op']=='store'];loads=[d for d in n.values() if d['op']=='load']
    check((len(stores),len(loads),len(calls))=={'rf':(11,19,2),'reset':(8,16,0),'tail':(18,23,5)}[role],'RF full memory/call census')
    saved=RF_SAVED if role=='rf' else TAIL_SAVED if role=='tail' else ()
    check([(d['rs2'],d['imm']) for d in stores if d['rs1']==2]==list(saved),'RF own exact frame saves')
    check(sorted((d['rd'],d['imm']) for d in loads if d['rs1']==2)==sorted(saved),'RF own exact frame restores')
    sp=[(p-pc,d['imm']) for p,d in n.items() if d.get('rd')==2]
    check(sp=={'rf':[(0,-16),(140,16)],'reset':[],'tail':[(0,-32),(228,32)]}[role],'RF balanced local frame')
    if role=='reset':check({d['rd'] for d in n.values() if d.get('rd',0)}=={12,13,14,15},'RF reset preserves all S/RA/SP/GP')
    check(all(d.get('rd')!=3 for d in n.values()),'RF no GP definitions')
    return {'role':role,'start':hex(pc),'bytes':len(raw),'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),
        'normal_return_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},'calls':calls,
        'store_count':len(stores),'load_count':len(loads),'local_RET':hex(pc+{'rf':142,'reset':128,'tail':230}[role]),
        'complete_local_body':True,'callee_normal_return_edges_are_conditional':role!='reset'}


def edge_map(b):return {int(p,16):[int(q,16) for q in qs] for p,qs in b['normal_return_CFG'].items()}


def selected(b,choices,start=None,cut=None):
    pc=int(b['start'],16)
    return paths.chain(edge_map(b),pc if start is None else pc+start,{pc+p:pc+q for p,q in choices.items()},None if cut is None else pc+cut)


def preservation(delta,writes):
    # All fixed RAM publications on the selected A0=13 / initial-state1 cases.
    objectbase=0x200033b8+delta;ctx=0x2000319c+delta
    protected=[(objectbase,296),(ctx+1,1),(ctx+2,1),(ctx+3,1),(ctx+40,4),
        (paths.layout.T,4*212),(paths.layout.A+8,16),(0x200040a6,1),(0x20004184,1)]
    slots=[0x2000353c+delta,0x20003508+delta,0x20003590+delta,0x20003504+delta,0x2000350c+delta]
    for p,w in writes:
        for q,z in protected+[(x,4) for x in slots]:check(paths.origin.separated(p,w,q,z),'RF fixed writes preserve upstream fields/pointer slots')
    return [{'address':hex(p),'bytes':w} for p,w in writes]


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[]
    for i,(data,pr,detail) in enumerate(zip(carriers,parent['profiles'],DETAILS)):
        (rf,reset,tail),delta,later,_=detail
        bodies={r:body(init.binding.take(data,pc,z),r,i) for r,pc,z in zip(ROLES,detail[0],SIZES)}
        check(pr['cut_before_RF_call']=={'pc':hex(tail+72),'target':hex(rf),'A0':13},'RF upstream cut joins actual direct call')
        check(pr['conditional_state_at_tail_reads']==1 and pr['conditional_context_gate']==5 and pr['conditional_count']==6,'RF upstream conditional state join')
        quick=selected(bodies['rf'],{38:124})
        slow=selected(bodies['rf'],{38:40,58:78,80:144,146:164,166:170,172:176,180:112})
        check(hex(rf+76) not in quick+slow,'RF state1 excludes indirect callback')
        check(hex(rf+120) not in quick and hex(rf+120) in slow,'RF distinct reset admission')
        rf_n={d['pc']:d for d in bodies['rf']['instructions']}
        for path in (quick,slow):
            taken=[rf_n[int(p,16)] for p in path]
            check([d['imm'] for d in taken if d['op']=='store' and d['rs1']==8]==[],'RF state1 A0=13 excludes fields8/9 writes')
            check([d['pc']-rf for d in taken if d.get('rd')==18]==[14,138],'RF snapshot S2 unchanged until matching restore')
            check([d['pc']-rf for d in taken if d.get('rd') in (20,21,19)]==[],'RF closed path preserves tail S3/S4/S5')
            check(not any(d.get('rd')==10 for d in taken),'RF selected return preserves A0=13')
        reset_paths=[selected(bodies['reset'],{28:q,94:116}) for q in (30,38)]
        check(all(hex(reset+104) not in path and hex(reset+114) not in path for path in reset_paths),'RF parent-zero descriptor avoids pointer writes')
        reset_n={d['pc']:d for d in bodies['reset']['instructions']}
        reset_stores=[[reset_n[int(p,16)]['pc']-reset for p in path if reset_n[int(p,16)]['op']=='store'] for path in reset_paths]
        check(reset_stores==[[12,20,56,76,82,124]]*2,'RF reset exactly five MMIO and one state stores')
        tail_cut=selected(bodies['tail'],{28:32,34:38,54:58},cut=150)
        normal_tail=selected(bodies['tail'],{28:32,34:38,54:58})
        early=[selected(bodies['tail'],cs) for cs in ({28:214},{28:32,34:214},{28:32,34:38,54:214})]
        check(all(hex(tail+58) not in p and hex(tail+210) not in p for p in early),'RF all early exits skip snapshot read and restore')
        tn={d['pc']:d for d in bodies['tail']['instructions']}
        check([p-tail for p,d in tn.items() if d.get('rd')==20]==[58,224],'RF tail S4 only snapshot definition and epilogue restore')
        check([tn[int(p,16)]['pc']-tail for p in tail_cut if tn[int(p,16)]['op']=='store' and tn[int(p,16)]['rs1']!=2]==[62,104,116,128,138,148],'RF tail selected pre-next-call MMIO stores')
        writes=preservation(delta,[(0x20002efc+delta,1),(0x2000351b+delta,1)])
        profiles.append({'label':pr['label'],'bodies':bodies,'quick_RF_path':quick,'nonzero_low2_RF_path':slow,
            'reset_two_readback_bit3_paths':reset_paths,'reset_selected_store_offsets':reset_stores,
            'RF_argument':13,'RF_initial_state':1,'RF_low2_mask_domain':[0,1,2,3],
            'conditional_RF_return_state':{'low2_zero':1,'low2_nonzero':0},
            'conditional_slow_fixed_RAM_stores':writes,'quick_additional_fixed_RAM_stores':[],
            'indirect_callback_proved_unreachable_only_in_selected_cases':True,
            'descriptor_zero_slot':hex(0x2000350c+delta),'descriptor_pointer_writes_excluded':True,
            'tail_path_to_next_call_cut':tail_cut,'cut_before_next_call':{'pc':hex(tail+150),'target':hex(later[0])},
            'tail_remaining_calls':[hex(p) for p in later],
            'tail_structural_normal_return_path':normal_tail,'tail_three_early_return_paths':early,
            'tail_control_snapshot_restoration_store':hex(tail+210),'tail_state_zero_store':hex(tail+206),
            'conditional_context_gate':5,'conditional_count':6,'actual_installed_binding_proved':False})
    return {'schema':'TSL9-RF-tail-return-static-v1','profile':parent['profile'],'APP_sha256':sha256(image).hexdigest(),
        'scope':'per candidate full RF198B/72 instructions, reset130B/48 instructions and tail232B/79 instructions; full local operands and CFG; selected RF path closed and tail bounded before second linked call; no new C bytes',
        'profiles':profiles,
        'RF_contract':'fresh read4002420c into S2, CPU SW0/FENCE.I, fresh low2 at published40024200. Low2=0 skips reset; nonzero with state1 and A0=13 skips callback17 and fields8/9 writes, clears flagbyte, invokes local reset. Both cases CPU store S2 snapshot before restoring S2/16B frame and RET. Actual MMIO value after write not inferred',
        'reset_contract':'no frame/calls/S/RA/SP/GP definitions; five ordered MMIO stores then statebyte0 if descriptor slot stays parent-published0. Unknown fresh readback bit3 selects skip or four NOPs, no loop. Nonzero descriptor path contains two pointer-based OR stores and is not assumed harmless',
        'distinct_snapshots':'outer tail snapshot in S4 and nested RF snapshot in S2 are separate fresh reads. Nested snapshot not assumed zero or equal outer S4 after outer SW0; CPU store-source restoration is not hardware completion evidence',
        'fresh_RMW_masks':{'reset_and_tail_clear_mask':'0xffcdffff = (0xffce0000-1) mod2^32','complement':'0x00320000','tail_pre_call_OR_mask':'0x00330000','inverse_pair_claimed':False},
        'bounded_preservation':'selected cases use only own frames/MMIO plus fixed flagbyte/statebyte writes; interval exclusions preserve upstream B296/context count/capacity/gate/table/task/node and pointer/descriptor slots under inherited mapping/nonalias/normal-completion/no-adverse-MMIO/FENCE.I/asynchronous-interference premises. Both RF cases join unconditional tail code up to next call; 32B tail frame remains active and outer S4 snapshot still held',
        'tail_return_obligations':'full local tail paths identified. Main path CPU writes state0 and outer S4 snapshot then restores seven saved words/SP32 and RET only IF all four remaining calls normally return with same SP, S0..S5, own saved frame words and required global pointer mappings intact, plus valid accesses/no adverse interference. These callees/obligations are NOT proved by this checkpoint',
        'early_exit_contract':'three local early-exit paths branch to common epilogue before any control snapshot read/clear; they do not CPU-write S4 to control. This does not establish reachability under selected initial-state1/matching-pointer premise',
        'remaining':['6645c/6659a and three later linked callees','actual tail/initializer return and hardware control effects','actual installed provider and later object/frame lifetimes'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    operands=canonical=0
    for i,(data,detail) in enumerate(zip(carriers,DETAILS)):
        for role,pc,size in zip(ROLES,detail[0],SIZES):
            raw=init.binding.take(data,pc,size);n=decode(raw,pc)
            for p,d in n.items():
                at=p-pc;w=d['size'];buf=bytearray(raw);special=d['op'] in ('nop','fence.i')
                flip=(4 if d['op']=='nop' else 128) if special else (1<<20 if w==4 else 4)
                buf[at:at+w]=(int.from_bytes(buf[at:at+w],'little')^flip).to_bytes(w,'little')
                try:body(buf,role,i)
                except RuntimeError as e:
                    check(str(e)=='unsupported static leaf encoding '+hex(p) if special else str(e).startswith('RF '+role+' operand '),'RF specified mutation guard '+str(e))
                else:raise RuntimeError('RF mutation escaped')
                if special:canonical+=1
                else:operands+=1
    check((operands,canonical)==(386,12),'RF mutation census')
    check((0xffce0000-1)&0xffffffff==0xffcdffff and (~0xffcdffff)&0xffffffff==0x320000,'RF mask complement distinct from OR mask')
    check(0x330000&0xffcdffff==0x10000,'RF OR/AND masks not inverse')
    for word in range(256):
        check((word&3) in (0,1,2,3),'RF low2 domain')
        check((word>>3)&1 in (0,1),'RF readback bit3 domain')
    check(13!=6 and 13!=7 and all(1!=v for v in (3,6,7,8)),'RF selected branch comparisons')
    print('PASS:386 operand mutations and12 noncanonical NOP/FENCE.I encodings rejected; mask/domain/branch identities')


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
    else:check(OUT.read_bytes()==output,'RF tail exact ledger replay')
    print('PASS:full RF/reset/tail operands/CFG/frames; conditional A0=13,state1 two RF returns and next-call cut; exact ledger')
    print('PASS:NO target execution; remaining tail callees/actual installed provider/hardware outcomes UNPROVED')


if __name__=='__main__':main()
