"""Config-specific arithmetic path closure and reuse of verified copy leaf.

Only original bytes/CFG and closed-form host algebra. No instruction runner,
register machine, target ISA, RAM, callback, MMIO, FENCE.I or device emulation.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_config_gates_static as previous
import check_v4160_event_payload_chain_static as payload

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-config-arithmetic-static.json')
BASES=(0x6df1a,0x6e10a)
HASHES=('fa6f59ae203928d3a374374ed27afdaafa0853df94a9a7951f92cdfa2c7c1868',
 'd6f207480c5ba1e976090946008d93aaa3ab2335ba91924302b2eb77de4b2a1d')
TABLE=bytes.fromhex('00010202030303030404040404040404')
SELECTED={8:12,12:16,18:22,26:858,56:58,110:130,158:180}


def specs(pc):
    s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def mv(o,r,b):e(o,'mv',rd=r,rs2=b)
    def binary(o,op,r,a,b):e(o,op,rd=r,rs1=a,rs2=b)
    def imm(o,op,r,b,v):e(o,op,rd=r,rs1=b,imm=v)
    def branch(o,op,a,b,t):e(o,op,rs1=a,rs2=b,target=pc+t)
    mv(0,15,13);mv(2,17,12);mv(4,6,10);mv(6,16,11)
    branch(8,'bne',13,0,350);branch(12,'bgeu',11,12,188)
    e(16,'lui',rd=14,imm=65536);branch(18,'bltu',12,14,456)
    e(22,'lui',rd=15,imm=16777216);branch(26,'bltu',12,15,858)
    imm(30,'srli',13,12,24);e(34,'li',rd=15,imm=24)
    e(36,'auipc',rd=14,imm=4096);imm(40,'addi',14,14,-1506)
    binary(44,'add',14,14,13);e(46,'load',rd=14,rs1=14,imm=0,width=1,mnemonic='qk.c.lbu')
    binary(48,'add',15,15,14);imm(50,'addi',14,0,32);binary(54,'sub',14,14,15)
    e(56,'beqz',rs1=14,target=pc+78)
    binary(58,'sll',16,11,14);binary(62,'srl',15,10,15);binary(66,'sll',17,12,14)
    binary(70,'or',16,15,16);binary(74,'sll',6,10,14);imm(78,'srli',12,17,16)
    binary(82,'divu',10,16,12);imm(86,'slli',13,17,16);imm(90,'srli',13,13,16)
    imm(92,'srli',15,6,16);binary(96,'remu',14,16,12);binary(100,'mul',11,13,10)
    imm(104,'slli',14,14,16);binary(106,'or',16,14,15);branch(110,'bgeu',16,11,130)
    binary(114,'add',16,16,17);imm(116,'addi',15,10,-1);branch(120,'bltu',16,17,128)
    branch(124,'bltu',16,11,902);mv(128,10,15);binary(130,'sub',16,16,11)
    binary(134,'divu',14,16,12);imm(138,'slli',6,6,16);imm(140,'srli',6,6,16)
    binary(144,'remu',16,16,12);binary(148,'mul',13,13,14);imm(152,'slli',16,16,16)
    binary(154,'or',16,16,6);branch(158,'bgeu',16,13,180)
    binary(162,'add',16,16,17);imm(164,'addi',15,14,-1);branch(168,'bltu',16,17,178)
    imm(172,'addi',14,14,-2);branch(174,'bltu',16,13,180);mv(178,14,15)
    imm(180,'slli',10,10,16);binary(182,'or',10,10,14);e(184,'li',rd=11,imm=0);e(186,'jr',rs1=1)
    imm(858,'srli',13,12,16);e(862,'li',rd=15,imm=16);e(864,'jump',target=pc+36)
    return s


def body(data,index):
    pc=BASES[index];pieces=[];n={}
    for (off,size),digest in zip(((0,188),(858,8)),HASHES):
        raw=init.binding.take(data,pc+off,size);part=decode(raw,pc+off);n.update(part)
        pieces.append({'start':hex(pc+off),'bytes':size,'sha256':sha256(raw).hexdigest(),'expected_sha256':digest})
    expected=specs(pc);check(set(n)==set(expected),'config arithmetic complete fragment boundaries')
    for p,f in expected.items():init.g(n,p,'config arithmetic operand '+hex(p-pc),**f)
    check(all(x['sha256']==x['expected_sha256'] for x in pieces) and len(n)==62,'config arithmetic fragment identity')
    check(not any(x['op'] in ('store','jal','jalr','call_indirect') for x in n.values()),'config arithmetic no local calls/stores')
    table=init.binding.take(data,pc+0xa42,16)
    check(table==TABLE and pc+36+4096-1506==pc+0xa42,'config arithmetic lookup16 source')
    edges={};cuts=[]
    for p,d in n.items():
        op=d['op']
        if op=='jr':q=[]
        elif op=='jump':q=[d['target']]
        elif op in ('bne','bgeu','bltu','beqz'):q=[p+d['size'],d['target']]
        else:q=[p+d['size']]
        edges[p]=q
        cuts.extend((p,v) for v in q if v not in n)
    check([(p-pc,q-pc) for p,q in cuts]==[(8,350),(12,188),(18,456),(124,902)],'config arithmetic general-fragment cuts')
    # These branch choices are proved from the domain algebra, not selected by a target runner.
    specialized={p:([pc+SELECTED[p-pc]] if p-pc in SELECTED else q) for p,q in edges.items()}
    reachable=set();pending=[pc]
    while pending:
        p=pending.pop()
        if p in reachable:continue
        check(p in n,'config arithmetic specialized no cuts');reachable.add(p);pending.extend(specialized[p])
    check(len(reachable)==49,'config arithmetic specialized49 nodes')
    check({p-pc for p in reachable if not specialized[p]}=={186},'config arithmetic specialized sole RET')
    # Single selected successor for every nonterminal; whole reachable set is one finite chain.
    check(all(len(specialized[p])==1 for p in reachable if p!=pc+186),'config arithmetic selected single chain')
    incoming={p:0 for p in reachable}
    for p in reachable:
        for q in specialized[p]:incoming[q]+=1
    check(incoming[pc]==0 and all(incoming[p]==1 for p in reachable if p!=pc),'config arithmetic selected chain no cycle')
    writes=sorted({n[p]['rd'] for p in reachable if n[p].get('rd',0)})
    check(writes==[6,10,11,12,13,14,15,16,17],'config arithmetic specialized GPR definitions')
    check([p-pc for p in reachable if n[p]['op']=='load']==[46],'config arithmetic only lookup load')
    return {'entry':hex(pc),'pieces':pieces,'instructions':list(n.values()),
        'general_fragment_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},
        'general_fragment_cuts':[[hex(p),hex(q)] for p,q in cuts],
        'specialized_branch_successors':{hex(pc+p):hex(pc+q) for p,q in SELECTED.items()},
        'specialized_reachable_nodes':sorted(hex(p) for p in reachable),'specialized_instructions':49,
        'specialized_CFG_closed_acyclic':True,'encoded_GPR_definitions_on_specialized_path':writes,
        'lookup':{'start':hex(pc+0xa42),'bytes':table.hex(),'index':15,'loaded_value':4},
        'complete_general_function':False,'complete_config_domain_path':True}


def algebra_tests():
    # Closed-form normalization and two quotient digits. This is deliberately
    # independent of bytes/PCs/register files and does not run target instructions.
    divisor=1000000;norm=12;normalized=divisor<<norm
    check(divisor>>16==15 and TABLE[15]==4 and 16+4==20 and 32-20==norm,'normalization constants')
    check(normalized==0xf4240000 and normalized>>16==62500 and normalized&65535==0,'normalized divisor digits')
    for h in range(65536):
        x=1400*h
        check(0<=x<=91749000<2**32,'config numerator bound')
        high=x>>20;low=(x<<12)&0xffffffff
        first=high//62500;rem=high%62500
        check(high<=87 and first==0,'first quotient digit zero')
        merged=(rem<<16)|(low>>16)
        check(merged==x>>4 and merged>=0,'first correction product zero and merge identity')
        second=merged//62500;tail=((merged%62500)<<16)|((low<<16&0xffffffff)>>16)
        check(0<=tail<2**32 and tail>=0,'second correction product zero and unsigned bound')
        quotient=(first<<16)|second
        check(quotient==x//divisor==(7*h)//5000 and 0<=quotient<=91,'config exact quotient')
        check((quotient&255)==quotient,'config output byte truncation loses no bits')
    check((1400*31250)//1000000==43,'default quotient43')
    print('PASS: all65536 config halfwords; normalization/digit identities; corrections skipped; exact floor(7*h/5000), range0..91, default43')


def derive(app,carriers,header,coverage):
    parent=previous.derive(app,carriers,header,coverage);profiles=[]
    for i,data in enumerate(carriers):
        b=body(data,i);config=parent['profiles'][i]['config'];pc,size,*_=previous.DETAILS[i]
        check(config['arithmetic_call_arguments']=={'A0':'1400 * fresh U16[copied_config+8]','A1':0,'A2':1000000,'A3':0},'config exact arithmetic argument join')
        check(config['calls'][2]['target']==b['entry'],'config exact arithmetic target join')
        mapping=init.binding.profile(data,init.binding.PROFILES[i][0]);m=mapping['first_copy']
        src=int(m['source'],16)+0x20000332-int(m['destination'],16)
        check(src==(0x405a2,0x405e2)[i] and 0x20000332+58<=int(mapping['first_copy_end_exclusive'],16),'config mapped complete copy source')
        c=payload.body(init.binding.take(data,src,58),'copy',0x20000332,58,18,3,init.binding.COPY_HASH)
        check(c['encoded_GPR_writes']==[13,14,15,16] and not c['calls'],'config reused copy GPR/call contract')
        check(config['copy_call_arguments']['A2']==16 and config['calls'][1]['target']==c['start'],'config exact copy join')
        profiles.append({'label':init.binding.PROFILES[i][0],'arithmetic':b,'config_call':config['calls'][2],
            'copy_reused':{'source':hex(src),'target':c['start'],'bytes':58,'sha256':c['sha256'],
                'defined_GPRs':c['encoded_GPR_writes'],'new_code_bytes_counted':0},
            'installed_binding_proved':False})
    return {'schema':'TSL9-config-arithmetic-static-v1','profile':parent['profile'],'profiles':profiles,
        'scope':'2 arithmetic fragments392B/124instructions plus2 fixed16-byte lookup prefixes; specialized49-instruction path per candidate; existing copy leaf reused',
        'domain':'config call only: A0=1400*h for fresh U16 h0..65535, A1=0,A2=1000000,A3=0; actual call additionally requires config/base+23 branch and earlier gates',
        'proof':'normalization index15 loads4; shift12 gives divisor0xf4240000, high digit62500/low digit0; first quotient digit0, both correction products0; second digit=floor((x>>4)/62500)=floor(x/1000000)',
        'result':'on completed specialized path A0=floor(7*h/5000) in0..91,A1=0; config low8 store keeps quotient unchanged; if default h remains31250 and branch executes, output43',
        'arithmetic_preservation':'specialized49-node path has no stores/calls/frame; only data read is pinned lookup byte; RA/SP/S0 and all other GPRs outside explicit definition census locally unchanged',
        'copy_connection':'existing verified58B/18instruction leaf: only GPRsA3/A4/A5/A6 defined; original A0/A1/A2,RA/SP/S0 unchanged locally; forward byte loop increments index0..15 for nonnull config source and fixed nonnull destination',
        'copy_retention':'no local store of source/destination pointer registers; byte stores transfer source values, which can themselves contain pointer bytes; no claim against external/MMIO retention or physical aliases',
        'copy_effects':'before null/count guards readU32[4002420c],write0there,FENCE.I; after data loop write saved word there; forward source/destination overlap may feed back, not a snapshot or memmove guarantee',
        'config_publication':'under matching preserved leaf code, valid noninterfering accesses and normal return, fresh publication reload joins completed forward16byte destination; equality to entry source requires no interfering source/destination alias/writers',
        'premises':['candidate identities/conditional ISA, original lookup bytes and actual code mapping preserved',
            'normal instruction/data/MMIO/FENCE.I completion; no asynchronous GPR or code/table changes',
            'copy effective byte writes/MMIO effects must not corrupt live caller frame/code/fields required later; no frame lifetime inferred from GPR preservation',
            'config h is fresh loaded copied-config halfword; no unconditional link to entry C, coherent snapshot or actual installed provider'],
        'remaining':['full general arithmetic helper and other callback argument domains','APP full config construction and installed provider provenance',
            'optional hook/registration effects, external writers, pointer retention and frame/object lifetime'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    algebra_tests();count=0
    offsets=(0,6,8,12,16,18,22,26,36,40,44,46,48,54,56,58,62,66,74,78,82,90,92,96,100,106,110,130,134,138,144,148,154,158,180,182,184,186,858,862,864)
    for i,data in enumerate(carriers):
        pc=BASES[i];n=body(data,i)['instructions'];lookup={x['pc']:x for x in n}
        for off in offsets:
            d=lookup[pc+off];at=pc+off-0x40000;raw=bytearray(data);width=d['size'];flip=1<<20 if width==4 else 4
            raw[at:at+width]=(int.from_bytes(raw[at:at+width],'little')^flip).to_bytes(width,'little')
            try:body(raw,i)
            except RuntimeError as e:check(str(e).startswith('config arithmetic operand '),'specific arithmetic mutation guard '+str(e))
            else:raise RuntimeError('arithmetic operand mutation escaped')
            count+=1
        raw=bytearray(data);raw[pc+0xa42+15-0x40000]^=1
        try:body(raw,i)
        except RuntimeError as e:check(str(e)=='config arithmetic lookup16 source','specific table mutation guard')
        else:raise RuntimeError('arithmetic table mutation escaped')
        count+=1
    check(count==84,'arithmetic mutation census')
    print('PASS: 82 operand mutations and2 lookup mutations rejected; reused complete copy leaf verified')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');o=parser.parse_args()
    app=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(app)==76800 and sha256(app).hexdigest()==init.binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK header identity')
    carriers=[]
    for label,folder,tail,size,digest in init.binding.PROFILES:
        raw=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(raw)==size and sha256(raw).hexdigest()==digest,'candidate identity '+label);carriers.append(raw)
    raw_hex=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
    coverage=sparse.derive(app,carriers,header,raw_hex,sparse.parser())
    ledger=derive(app,carriers,header,coverage);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract()
    tests(carriers);output=(json.dumps(ledger,indent=1,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'config arithmetic exact ledger replay')
    print('PASS: two config-domain49-node closed acyclic paths; exact operands/CFG/lookup/caller/copy joins and ledger')
    print('PASS: NO target execution; general helper/installed binding/MMIO effects/lifetime UNPROVED')


if __name__=='__main__':main()
