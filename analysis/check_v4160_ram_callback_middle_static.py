"""Callback middle operands, arithmetic fixups and fresh-target wait SCC.

Host graph/bit algebra and original bytes only. No target ISA, callback,
resident, RAM/frame, MMIO, copy or device execution/emulation.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_ram_callback_exits_static as previous

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-ram-callback-middle-static.json')
MASK=0xffffffff
PARTS=(('middle',408,162,50),('difference_fixup',854,10,3),('wait',570,40,12),('wait_fixup',864,6,3))
HASHES=(
 ('e7d8007f510e5de8fac83edab90ecae06d120a7ea35598a74b17b667a5128718',
  '51b8fc10aed712a9ba900d59386a239782e8c66360feb9ff4c25bbb1af57c08c',
  'e61758034b99b4726af07ccaebf95796d7e3c28b366c51cb53887ac091d28acf',
  'b4dcb2dce06f8caedf373dde7e86e8a6c82c27ffdda4d9471df11beb05e73c18'),
 ('f6eeb3242e4cf13c5bf43c870d4a57af7cddcc6f982b65c7d4724e2281a27e77',
  '51b8fc10aed712a9ba900d59386a239782e8c66360feb9ff4c25bbb1af57c08c',
  '5b0a85597ca71126f7fd6244009a0bc25b018d1a9bb9ae9deda5b3eac7a5bf3e',
  'b4dcb2dce06f8caedf373dde7e86e8a6c82c27ffdda4d9471df11beb05e73c18'))


def specs(role,entry,service,helper_low):
    s={};pc=entry+next(o for r,o,size,n in PARTS if r==role)
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def load(o,r,b,v,w=4,**f):e(o,'load',rd=r,rs1=b,imm=v,width=w,**f)
    def store(o,r,b,v,w=4,**f):e(o,'store',rs2=r,rs1=b,imm=v,width=w,**f)
    def qload(o,r,b,v):load(o,r,b,v,2,mnemonic='qk.c.lhu')
    def qstore(o,r,b,v):store(o,r,b,v,2,mnemonic='qk.c.sh')
    def addi(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def binary(o,op,r,a,b):e(o,op,rd=r,rs1=a,rs2=b)
    def move(o,r,a):e(o,'mv',rd=r,rs2=a)
    if role=='middle':
        qload(0,10,9,8);load(2,15,8,134,2);e(6,'lui',rd=13,imm=999424);addi(10,12,13,575)
        binary(14,'mul',15,15,10);addi(18,13,13,576);load(22,14,8,144);store(26,0,8,54,1);load(30,21,9,4)
        binary(34,'add',15,15,12);binary(36,'divu',15,15,13);e(40,'bltu',rs1=14,rs2=15,target=entry+854)
        binary(44,'sub',15,14,15);load(48,13,8,140);store(52,15,8,136);e(56,'li',rd=22,imm=0)
        binary(58,'add',15,13,14);move(62,18,15);e(64,'bltu',rs1=15,rs2=13,target=pc+72)
        e(68,'bltu',rs1=15,rs2=21,target=pc+76);binary(72,'sub',18,15,21);qload(76,15,8,32)
        store(78,18,8,144);e(82,'beqz',rs1=15,target=entry+570);load(84,13,8,64,2);qload(88,14,8,36)
        e(90,'lui',rd=12,imm=999424);qstore(94,13,8,36);binary(96,'sub',14,13,14)
        binary(100,'mul',15,15,14);qload(104,14,8,34);addi(106,12,12,576);e(110,'li',rd=13,imm=0);e(112,'li',rd=11,imm=0)
        binary(114,'add',15,15,14);e(116,'slli',rd=15,rs1=15,imm=16);e(118,'srli',rd=15,rs1=15,imm=16)
        binary(120,'mul',10,15,10);qstore(124,15,8,34);e(126,'auipc',rd=1,imm=0xe006d000)
        e(130,'jalr',rd=1,rs1=1,imm=helper_low);e(134,'beqz',rs1=10,target=entry+570)
        binary(136,'add',10,10,18);binary(138,'sltu',18,10,18);binary(142,'add',18,18,11);move(144,15,10)
        e(146,'bne',rs1=22,rs2=18,target=pc+154);e(150,'bltu',rs1=10,rs2=21,target=pc+158)
        binary(154,'sub',15,10,21);store(158,15,8,144)
    elif role=='difference_fixup':
        binary(0,'add',13,14,21);binary(4,'sub',15,13,15);e(8,'jump',target=entry+456)
    elif role=='wait':
        load(0,15,20,service);e(4,'call_indirect',rd=1,rs1=15);move(6,18,10)
        load(8,15,20,service);e(12,'call_indirect',rd=1,rs1=15);e(14,'beq',rs1=10,rs2=18,target=pc+8)
        load(18,15,20,service);load(22,18,8,136);e(26,'call_indirect',rd=1,rs1=15)
        e(28,'bltu',rs1=18,rs2=10,target=entry+864);binary(32,'sub',10,18,10);e(36,'beq',rs1=10,rs2=0,target=entry+898)
    elif role=='wait_fixup':
        load(0,15,9,4);binary(2,'add',18,18,15);e(4,'jump',target=entry+602)
    else:raise RuntimeError('unknown callback middle role')
    return s


def window(raw,role,entry,service,helper_low,digest):
    _,off,size,count=next(d for d in PARTS if d[0]==role)
    if role=='middle':check(all(int.from_bytes(raw[o:o+4],'little')&0x707f==0x5003 for o in (2,84)),'middle unsigned halfword encodings')
    n=decode(raw,entry+off);s=specs(role,entry,service,helper_low);check(set(n)==set(s),'middle whole window boundaries '+role)
    for p,f in s.items():init.g(n,p,'middle '+role+' operand '+hex(p-entry-off),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(size,count,digest),'middle whole window identity '+role)
    edges={};calls=[]
    for p,d in n.items():
        if d['op']=='jump':qs=[d['target']]
        elif d['op'] in ('bltu','beqz','bne','beq'):qs=[p+d['size'],d['target']]
        else:qs=[p+d['size']]
        edges[p]=qs
        if d['op'] in ('jalr','call_indirect'):
            target=hex((p-4+n[p-4]['imm']+d['imm'])&0xfffffffe) if d['op']=='jalr' else 'fresh U32[then-live S4+service_delta] & ~1'
            calls.append({'pc':hex(p),'link':hex(p+d['size']),'target':target,'normal_return_and_preservation_proved':False})
    return {'start':hex(entry+off),'end_exclusive':hex(entry+off+size),'bytes':size,'sha256':digest,
        'instructions':list(n.values()),'conditional_CFG':{hex(k):[hex(q) for q in qs] for k,qs in edges.items()},
        'calls':calls,'complete_function':False}


def derive(app,carriers,header,coverage):
    parent=previous.derive(app,carriers,header,coverage);profiles=[]
    for i,(data,p) in enumerate(zip(carriers,parent['profiles'])):
        source=int(p['flash_entry'],16);entry=int(p['mapped_entry'],16);service=(480,560)[i];low=(-76,420)[i];bodies={}
        for j,(role,off,size,count) in enumerate(PARTS):
            raw=init.binding.take(data,source+off,size);bodies[role]=window(raw,role,entry,service,low,HASHES[i][j])
            window(raw,role,source,service,low,HASHES[i][j])
        check(bodies['middle']['calls'][0]['target']==('0x6df1a','0x6e10a')[i],'middle mapped word-pair helper')
        edges={int(k,16):[int(q,16) for q in qs] for k,qs in p['combined_CFG'].items()}
        for b in bodies.values():
            for k,qs in b['conditional_CFG'].items():check(int(k,16) not in edges,'new middle window overlap');edges[int(k,16)]=[int(q,16) for q in qs]
        check({q for qs in edges.values() for q in qs if q not in edges}=={entry+610},'single remaining middle cut')
        seen=set()
        def visit(v):
            if v not in edges or v in seen:return
            seen.add(v)
            for q in edges[v]:visit(q)
        visit(entry);check(len(edges)==242 and seen==set(edges),'previous independent tail now locally entry-reachable')
        check(edges[entry+606]==[entry+610,entry+898],'wait zero difference connects final-tail entry')
        cycles=[c for c in previous.previous.components(edges) if len(c)>1 or c[0] in edges[c[0]]]
        waitnodes=[entry+578,entry+582,entry+584]
        check(len(cycles)==2 and sorted(map(len,cycles))==[3,41] and waitnodes in cycles,'one new exact three-node wait SCC plus prior update SCC')
        check([int(x,16) for x in p['cyclic_SCC_nodes']] in cycles,'prior update SCC unchanged')
        profiles.append({'label':p['label'],'flash_entry':hex(source),'mapped_entry':hex(entry),'bodies':bodies,
            'combined_CFG':{hex(k):[hex(q) for q in qs] for k,qs in edges.items()},
            'cyclic_SCC_nodes':[[hex(v) for v in c] for c in cycles],'only_continuation_cut':hex(entry+610),
            'entry_root_reachable_nodes':len(seen),'previous_final_tail_root_now_locally_reachable':hex(entry+898),
            'actual_runtime_reachability_termination_preservation_or_installed_binding_proved':False})
    check(sum(b['bytes'] for p in profiles for b in p['bodies'].values())==436,'middle new byte census')
    check(sum(len(b['instructions']) for p in profiles for b in p['bodies'].values())==136,'middle new instruction census')
    return {'schema':'TSL9-RAM-callback-middle-static-v1','profile':parent['profile'],'profiles':profiles,
        'scope':'8 new bounded pieces436B/136instructions; selected combined1452B/484instructions, not complete callback',
        'middle_arithmetic':['fresh factorb=U16[S1+8],a=U16[S0+134]; Q=low32(a*b+999999) unsigned_div1000000',
            'fresh V=U32[S0+144]; clear byte54; fresh W=U32[S1+4]; field136=low32(V-Q) ifV>=Q else low32(V+W-Q)',
            'fresh B=U32[S0+140] with earlierV formsC=low32(B+V); S2=low32(C-W) ifC<B orC>=W elseC; S6=0',
            'fresh R=U16[S0+32] before SW S2->[S0+144]; Rzero skips optional helper block',
            'fresh c=U16[S0+64],oldc=U16[S0+36],oldp=U16[S0+34]; SH c->field36; p=low16(R*low32(c-oldc)+oldp)',
            'A0=p*b (fitsU32); SH p->field34; A1=0,A2=1000000,A3=0; linked helper, semantics/return ABI unproved'],
        'post_helper_contract':['test only returnedA0 forzero; returnedA1 is not part of this guard',
            'ifnonzero: lo=low32(A0+then-live S2); carry=unsigned(lo<oldS2); hi=low32(A1+carry)',
            'storelow32(lo-S5) ifhi!=then-live S6 orlo>=then-live S5 else lo tofield144; not general64bit modulo proof'],
        'wait_contract':['fresh target seed call; copy replyA0 toS2; three-node SCC reloads target/calls/comparesA0 with then-live S2',
            'equal ->repeat; different ->reload target and snapshot field136 intoS2 BEFORE post-wait call; dynamic call count unproved',
            'unsignedS2<reply ->fresh wrap read addS2 once, then join after comparison; A0=low32(S2-reply)',
            'A0zero ->previous final-tail entry; otherwise only remaining cut; normal returns and live values conditional'],
        'premises':['matching installed candidate/mappings and valid conditional Xwchc ISA/object/frame/code accesses',
            'fresh reads can differ; unknown helpers may change registers/data/targets/frame or not return; preserve required S0/S1/S2/S4/S5/S6 and saved words explicitly',
            'word-pair arguments/carry-like pattern do not establish division64 ABI, mathematical modulo, monotonic replies or loop progress',
            'encoded local reachability/SCCs do not prove actual path reachability, callback execution or termination'],
        'remaining':['cut41222/41262 and remaining middle instructions including MULHU','full callback closure and all callees',
            'config gates/copy/registration order/other writers','installed provider, object fields and frame/payload lifetime'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    for op,r,b,off,w in (('lhu',10,9,8,0x248a),('lhu',15,8,32,0x301e),('lhu',14,8,36,0x305a),
        ('lhu',14,8,34,0x303a),('sh',13,8,36,0xb056),('sh',15,8,34,0xb03e)):
        check(init.timer.encode(op,r,b,off)==w,'critical middle QK field encodings')
    for current in range(65536):
        for old in (0,1,65535):
            r,oldp=65535,12345
            a=(r*((current-old)&MASK)+oldp)&65535;b=(r*(current-old)+oldp)%65536
            check(a==b and a*65535<=MASK,'low16 field update algebra / final product bound')
    check(((1-7)&MASK)==0xfffffffa and ((1<<32)+1)%7==5,'carry-like correction is not unrestricted modulo64')
    changes=(((0,4),(2,1<<14),(26,1<<20),(36,1<<15),(40,1<<12),(52,1<<20),(76,4),(94,4),
        (116,4),(124,4),(130,1<<20),(134,4),(138,1<<15),(146,1<<12)),
        ((0,1<<15),(8,4)),((0,1<<20),(6,4),(14,1<<12),(22,1<<20),(28,1<<12),(36,1<<12)),((0,4),(4,4)))
    count=0
    for i,(data,d) in enumerate(zip(carriers,previous.previous.prefix.DETAILS)):
        source=d[0]
        for j,(role,off,size,n) in enumerate(PARTS):
            raw=init.binding.take(data,source+off,size)
            for at,flip in changes[j]:
                b=bytearray(raw);width=decode(raw,source+off)[source+off+at]['size'];b[at:at+width]=(int.from_bytes(b[at:at+width],'little')^flip).to_bytes(width,'little')
                try:window(b,role,source,(480,560)[i],(-76,420)[i],HASHES[i][j])
                except RuntimeError as e:check(str(e) in ('middle '+role+' operand '+hex(at),'middle unsigned halfword encodings'),'specific middle mutation guard '+str(e))
                else:raise RuntimeError('middle mutation escaped')
                count+=1
    check(count==48,'middle mutation census')
    print('PASS: exact QK fields; 196608 host low16 algebra cases; modulo counterexample; 48 specified mutations rejected')


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
    else:check(OUT.read_bytes()==output,'callback middle exact ledger replay')
    print('PASS: new436B/136instructions; combined1452B/484instructions; final-tail local join; exact3/41-node SCCs and one remaining cut')
    print('PASS: exact ledger; NO target execution; actual reachability/helper ABI/loop termination/installed binding UNPROVED')


if __name__=='__main__':main()
