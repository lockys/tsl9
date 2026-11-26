"""Original callback update operands and conditional CFG/SCC, offline only.

No target ISA, RAM/frame, copy, callback, MMIO, resident or device execution.
Host computations below concern graph structure and finite-width algebra.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_service_provider_link_static as previous

prefix=previous.previous
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-ram-callback-loop-static.json')
MASK=0xffffffff
PARTS=(('completion',108,28,9),('threshold',164,38,11),('iteration',202,34,11),
       ('update',236,80,25),('wrap',316,8,4),('fixups',376,14,6))
HASHES=(
 ('1b5d556f73ab236d57c53cd9ec3e0975c21fbbcf3b0f3ee4df02958741ad4d29',
  '00949dd869cdce4df750e08288f00452b0849e06d4d0272e3c974a185103146b',
  '411a8f0bf1cf91da5c54c8f58bfa78b67a0255f08fc19f69b11e4ea395face4d',
  '12622416bd71250525d7d218da638569d2533d05c725a6028cba77af76b64583',
  '8eef5ac727dd2c02fdbbd242aa3dcd77bc8a7855ce66102cd287ed4e95efdce5',
  '5f37073aadb3f0807e0431393b49a185b2f61895821910a7d5e084c42b23d063'),
 ('1b5d556f73ab236d57c53cd9ec3e0975c21fbbcf3b0f3ee4df02958741ad4d29',
  '00949dd869cdce4df750e08288f00452b0849e06d4d0272e3c974a185103146b',
  '92bf32824f92901fda558ec2aefffa19a3e23d5f22b2b63a07e3a348484a2a2d',
  'e5eefc41b7449deb31a390827931a623325e174cdd848b6814c610539e652c62',
  '8eef5ac727dd2c02fdbbd242aa3dcd77bc8a7855ce66102cd287ed4e95efdce5',
  '5f37073aadb3f0807e0431393b49a185b2f61895821910a7d5e084c42b23d063'))


def specs(role,entry,service_delta,helper_low):
    s={};off=next(o for r,o,size,n in PARTS if r==role);pc=entry+off
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def load(o,r,b,v,w=4,**f):e(o,'load',rd=r,rs1=b,imm=v,width=w,**f)
    def store(o,r,b,v,w=4,**f):e(o,'store',rs2=r,rs1=b,imm=v,width=w,**f)
    def addi(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def binary(o,op,r,a,b):e(o,op,rd=r,rs1=a,rs2=b)
    def move(o,r,a):e(o,'mv',rd=r,rs2=a)
    if role=='completion':
        load(0,15,8,64,2);store(4,0,8,31,1);addi(8,15,15,1);store(10,15,8,64,2);load(14,15,8,320,1)
        e(18,'bne',rs1=15,rs2=0,target=entry+390);move(22,10,8);e(24,'jal',rd=1,target=entry+1910);e(26,'jump',target=entry+394)
    elif role=='threshold':
        load(0,15,8,62,2,mnemonic='qk.c.lhu');load(2,14,9,8,2,mnemonic='qk.c.lhu')
        e(4,'slli',rd=15,rs1=15,imm=3);binary(6,'mul',15,15,14);addi(10,14,0,800);addi(14,15,15,400)
        binary(18,'divu',15,15,14);e(22,'bltu',rs1=15,rs2=10,target=entry+324)
        e(26,'lui',rd=21,imm=999424);addi(30,22,21,575);addi(34,21,21,576)
    elif role=='iteration':
        load(0,15,8,64,2);addi(4,15,15,1);store(6,15,8,64,2);load(10,15,8,320,1)
        e(14,'bnez',rs1=15,target=pc+20);move(16,10,8);e(18,'jal',rd=1,target=entry+1910);move(20,10,8)
        e(22,'auipc',rd=1,imm=0xe0056000);e(26,'jalr',rd=1,rs1=1,imm=helper_low)
        e(30,'bne',rs1=10,rs2=0,target=entry+834)
    elif role=='update':
        load(0,13,8,144);load(4,15,8,140);load(8,14,9,4);binary(10,'add',15,15,13);move(12,10,15)
        e(14,'bltu',rs1=15,rs2=13,target=pc+22);e(18,'bltu',rs1=15,rs2=14,target=pc+26);binary(22,'sub',10,15,14)
        load(26,15,8,31,1,mnemonic='qk.c.lbu');load(28,18,8,134,2);store(32,10,8,144)
        addi(36,15,15,1);store(38,15,8,31,1,mnemonic='qk.c.sb');load(40,15,9,8,2,mnemonic='qk.c.lhu')
        binary(42,'mul',18,18,15);binary(46,'add',18,18,22);binary(48,'divu',18,18,21)
        e(52,'bltu',rs1=10,rs2=18,target=entry+376);binary(56,'sub',18,10,18);load(60,15,20,service_delta)
        e(64,'call_indirect',rd=1,rs1=15);e(66,'bltu',rs1=18,rs2=10,target=entry+384)
        binary(70,'sub',10,18,10);e(74,'blt',rs1=10,rs2=0,target=entry+202);e(78,'jump',target=entry+108)
    elif role=='wrap':
        load(0,15,9,4);binary(2,'sub',15,15,14);binary(4,'add',10,10,15);e(6,'jump',target=entry+164)
    elif role=='fixups':
        binary(0,'sub',18,14,18);binary(4,'add',18,18,10);e(6,'jump',target=entry+296)
        load(8,15,9,4);binary(10,'add',18,18,15);e(12,'jump',target=entry+306)
    else:raise RuntimeError('unknown callback loop role')
    return s


def window(raw,role,entry,service,helper_low,digest):
    _,off,size,count=next(d for d in PARTS if d[0]==role)
    if role in ('completion','iteration','update'):
        at=28 if role=='update' else 0
        check(int.from_bytes(raw[at:at+4],'little')&0x707f==0x5003,'loop unsigned halfword encoding')
    n=decode(raw,entry+off);s=specs(role,entry,service,helper_low)
    check(set(n)==set(s),'loop whole window boundaries '+role)
    for p,f in s.items():init.g(n,p,'loop '+role+' operand '+hex(p-entry-off),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(size,count,digest),'loop whole window identity '+role)
    edges={};calls=[]
    for p,d in n.items():
        if d['op']=='jump':qs=[d['target']]
        elif d['op'] in ('bne','bnez','bltu','blt'):qs=[p+d['size'],d['target']]
        else:qs=[p+d['size']]
        edges[p]=qs
        if d['op'] in ('jal','jalr','call_indirect'):
            target=hex(d['target']) if d['op']=='jal' else hex((p-4+0xe0056000+helper_low)&0xfffffffe) if d['op']=='jalr' else 'fresh U32[then-live S4+service_delta] & ~1'
            calls.append({'pc':hex(p),'link':hex(p+d['size']),'target':target,'normal_return_and_preservation_proved':False})
    return {'start':hex(entry+off),'end_exclusive':hex(entry+off+size),'bytes':size,'sha256':digest,'instructions':list(n.values()),
        'conditional_normal_return_CFG':{hex(k):[hex(q) for q in qs] for k,qs in edges.items()},'calls':calls,'complete_function':False}


def components(edges):
    indices={};low={};stack=[];on=set();result=[]
    def visit(v):
        indices[v]=low[v]=len(indices);stack.append(v);on.add(v)
        for w in edges[v]:
            if w not in edges:continue
            if w not in indices:visit(w);low[v]=min(low[v],low[w])
            elif w in on:low[v]=min(low[v],indices[w])
        if low[v]==indices[v]:
            group=[]
            while True:
                w=stack.pop();on.remove(w);group.append(w)
                if w==v:break
            result.append(sorted(group))
    for v in edges:
        if v not in indices:visit(v)
    return sorted(result,key=lambda x:x[0])


def derive(app,carriers,header,coverage):
    service_link=previous.derive(app,carriers,header,coverage)
    parent=prefix.derive(app,carriers,header,coverage);profiles=[]
    for i,(data,d) in enumerate(zip(carriers,prefix.DETAILS)):
        source,obj,factor,service,_=d;p=parent['profiles'][i];entry=int(p['mapped_entry'],16);helper_low=(-1214,-894)[i]
        bodies={}
        for j,(role,off,size,count) in enumerate(PARTS):
            raw=init.binding.take(data,source+off,size);bodies[role]=window(raw,role,entry,service,helper_low,HASHES[i][j])
            window(raw,role,source,service,helper_low,HASHES[i][j])
        allbodies=list(p['bodies'].values())+list(bodies.values())
        nodes={x['pc']:x for b in allbodies for x in b['instructions']}
        edges={int(k,16):[int(q,16) for q in qs] for b in allbodies for k,qs in b['conditional_normal_return_CFG'].items()}
        cuts={q for qs in edges.values() for q in qs if q not in nodes}
        check(cuts=={entry+324,entry+390,entry+394,entry+834},'four loop external cuts')
        seen=set()
        def visit(v):
            if v not in nodes or v in seen:return
            seen.add(v)
            for q in edges[v]:visit(q)
        visit(entry);check(seen==set(nodes) and len(nodes)==110,'combined prefix loop reachability/census')
        scc=components(edges);cycles=[c for c in scc if len(c)>1 or c[0] in edges[c[0]]]
        expected={v for v in nodes if entry+202<=v<entry+314 or entry+376<=v<entry+390}
        check(len(cycles)==1 and len(cycles[0])==41 and set(cycles[0])==expected,'one exact 41-node local update SCC')
        check(edges[entry+310]==[entry+314,entry+202] and edges[entry+314]==[entry+108],'loop signed backedge vs completion exit')
        check(bodies['iteration']['calls'][-1]['target']==('0x56972','0x56ab2')[i],'mapped status helper target')
        check(bodies['completion']['calls'][0]['target']=='0x200014c6','mapped optional local call target')
        check(service_link['profiles'][i]['nominal_service_pointer_word']==p['nominal_service_pointer_word'],'conditional service publication source reused')
        profiles.append({'label':p['label'],'flash_entry':hex(source),'mapped_entry':hex(entry),'bodies':bodies,
            'reused_prefix_body_hashes':{k:b['sha256'] for k,b in p['bodies'].items()},
            'combined_CFG':{hex(k):[hex(q) for q in qs] for k,qs in edges.items()},
            'cyclic_SCC_nodes':[hex(v) for v in cycles[0]],'continuation_cuts':[hex(v) for v in sorted(cuts)],
            'nominal_service_pointer_word':p['nominal_service_pointer_word'],'nominal_wrap_word':p['nominal_wrap_word'],
            'loop_termination_actual_iteration_or_installed_binding_proved':False})
    check(sum(b['bytes'] for p in profiles for b in p['bodies'].values())==404,'loop new byte census')
    check(sum(len(b['instructions']) for p in profiles for b in p['bodies'].values())==132,'loop new instruction census')
    return {'schema':'TSL9-RAM-callback-loop-static-v1','profile':parent['profile'],'profiles':profiles,
        'scope':'12 new bounded pieces404B/132instructions; combined with prior272B/88instructions ->selected676B/220instructions',
        'threshold_contract':'((8*U16[then-live S0+62]*U16[then-live S1+8]+400) modulo2^32) unsigned_div800; unsigned threshold<A0 leaves selected graph',
        'iteration_contract':['fresh U16[object+64] increment stored modulo65536; fresh U8[object+320] gates optional call withA0=S0',
            'setA0=S0, direct helper formed by AUIPC/JALR; nonzero return leaves selected graph',
            'fresh A=U32[object+144],B=U32[object+140],W=U32[then-live S1+4]; C=(A+B) modulo2^32; T=(C-W) modulo2^32 if C<A or C>=W, else T=C',
            'fresh byte[object+31] and U16[object+134]; storeT to[object+144]; increment byte31 modulo256; fresh factorU16[then-live S1+8]',
            'S2=(low32(product)+then-live S6) modulo2^32 unsigned_div then-live S5; interpreting S6/S5 as999999/1000000 requires preservation across callees',
            'conditional correction, fresh service target and call; conditional fresh wrap read; A0=S2-return modulo2^32; signedA0<0 back to iteration, else completion'],
        'completion_contract':'increment halfword64 modulo65536; clear byte31; fresh byte320 selects local-call/other continuation; call effects unknown',
        'not_general_modulo_proof':True,'encoded_local_cycle_is_not_observed_execution_or_termination':True,
        'premises':['installed identity, completed first-copy code, valid conditional Xwchc ISA and object/stack accesses',
            'S0/S1/S2/S4/S5/S6, saved frame/words and relevant values preserved as required across unknown callees; aliases/other writers/reentry can invalidate joins',
            'fresh object/global loads can differ across visits and calls; nominal addresses depend on live register bases',
            'field bounds, object type, loop iteration count, helper semantics and any hardware behavior remain unproved'],
        'remaining':['four new continuation cuts including local callees/epilogue','full config gates and copy semantics from prior service link',
            'actual object fields/provider writes/registration order','whole callback exit, frame lifetime and installed binding'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    check(init.timer.encode('lhu',15,8,62)==0x3c7e and init.timer.encode('lhu',14,9,8)==0x249a,'critical threshold QK encodings')
    check(init.timer.encode('lbu',15,8,31)==0x3c7c and init.timer.encode('sb',15,8,31)==0xbc7c,'critical byte31 QK encodings')
    for a in range(65536):
        check(((a+1)&65535)==(0 if a==65535 else a+1),'halfword increment truncation')
        product=a*65535;wide=8*product+400;q=(wide&MASK)//800
        check(0<=q<=5368709,'second threshold quotient bound')
        if product<=536870861:check(q==wide//800,'unwrapped second threshold safe domain')
    for a in range(256):check(((a+1)&255)==(0 if a==255 else a+1),'byte increment truncation')
    wide=8*16384*32768+400;check((wide&MASK)//800==0 and wide//800==5368709,'wrapped threshold counterexample')
    wide=8*65535*65535+400;check((wide&MASK)//800==5367398 and wide//800==42948362,'overflow need not imply zero threshold')
    check((100+100-7)==193 and (100+100)%7==4,'one subtract is not arbitrary modulo')
    check((((0xfffffff0+0x30)&MASK)-256)&MASK==0xffffff20 and (0xfffffff0+0x30)%256==32,'carry correction not arbitrary modulo')
    changes=(((0,1<<20),(4,1<<20),(10,1<<20),(18,1<<12),(24,4)),
        ((0,4),(2,4),(4,4),(10,1<<20),(18,1<<15),(22,1<<12)),
        ((0,1<<20),(6,1<<20),(14,4),(22,1<<12),(30,1<<12)),
        ((4,1<<20),(14,1<<12),(26,4),(32,1<<20),(40,4),(48,1<<20),(74,1<<12)),
        ((0,4),(6,4)),((0,1<<15),(6,4),(12,4)))
    count=0
    for i,(data,d) in enumerate(zip(carriers,prefix.DETAILS)):
        source,obj,factor,service,_=d
        for j,(role,off,size,n) in enumerate(PARTS):
            raw=init.binding.take(data,source+off,size)
            for at,flip in changes[j]:
                b=bytearray(raw);width=decode(raw,source+off)[source+off+at]['size'];b[at:at+width]=(int.from_bytes(b[at:at+width],'little')^flip).to_bytes(width,'little')
                try:window(b,role,source,service,(-1214,-894)[i],HASHES[i][j])
                except RuntimeError as e:check(str(e) in ('loop '+role+' operand '+hex(at),'loop unsigned halfword encoding'),'specific loop mutation guard '+str(e))
                else:raise RuntimeError('loop mutation escaped')
                count+=1
    check(count==56,'loop mutation census')
    print('PASS: exact QK encodings; 65536 halfword/max-factor cases +256 byte cases; arithmetic counterexamples; 56 specified mutations rejected')


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
    else:check(OUT.read_bytes()==output,'callback loop exact ledger replay')
    print('PASS: new404B/132instructions; combined676B/220instructions; one exact41-node SCC/profile and four explicit continuation cuts')
    print('PASS: exact ledger; NO target execution; actual loop termination/provider preservation/installed binding UNPROVED')


if __name__=='__main__':main()
