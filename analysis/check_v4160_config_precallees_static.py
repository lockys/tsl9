"""Close first12 config pre-call sites: original operands/CFG/frame algebra.

No target ISA, MMIO, polling, frame memory, callbacks or device execution.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_app_config_source_static as previous
import check_v4160_irq_setup_stack_sources_static as setup

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-config-precallees-static.json')
DETAILS=(('bit100',0x19076,22,8,'6bdc2c041299cdf45177294a82b8c6039bb2332c20f22e15e93981a5a0bb7d09'),
 ('mode_byte',0x1909e,40,13,'10726315dbdb4f66cad955b3095852bb4f9c990586821bc4c7ea72d4f84041fe'),
 ('bit1',0x190c6,20,8,'86f9e16277d4d276e11ce58da974aa04e9db414e5526379740bdd14c39aee7f0'),
 ('or20',0x190da,12,5,'289f57afbd8428e8e89a74d466f203b15b843072b64a45063eb03d1ce41056f3'),
 ('bit8000',0x190e6,32,14,'245a28b52b86294610b5bc51245ba42db99ce037336098ef9833d2df719f1703'),
 ('set10',0x1919c,18,5,'b065beab1b39128063791265f2675a49d1f7fd2abbf78a40e0f50974b8df7091'),
 ('clear10',0x191ae,24,9,'0fa80cfcbe9194ed6a7372aac524a678c9f0cea068ab45360d3d8d01d7caa686'),
 ('pair18',0x19220,40,14,'2cc3844eb6861cf9182265f00dbd64e1532483cdcb7ede4b71d71b3bc6efe74e'),
 ('pair08',0x19248,42,15,'24c7f8d386442b699d2a1dc541fd5b4b476ff8e3caf0044c2033510e3a3d0578'),
 ('poll20',0x19272,16,5,'59fbe6b77b6d0481b5d8c4d6ddae179ce5534ccff2f269a17fa651c009af704b'))
DEFS={'bit100':[14,15],'mode_byte':[14,15],'bit1':[14,15],'or20':[10,14,15],
 'bit8000':[13,14,15],'set10':[14,15],'clear10':[14,15],
 'pair18':[1,2,10,14,15],'pair08':[1,2,10,14,15],'poll20':[14,15]}


def specs(role,pc):
    s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def lui(o,r,v):e(o,'lui',rd=r,imm=v)
    def load(o,r,b,v,w=4):e(o,'load',rd=r,rs1=b,imm=v,width=w)
    def store(o,r,b,v,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    def imm(o,op,r,b,v):e(o,op,rd=r,rs1=b,imm=v)
    def binary(o,op,r,a,b):e(o,op,rd=r,rs1=a,rs2=b)
    def bz(o,r,t):e(o,'beqz',rs1=r,target=pc+t)
    def ret(o):e(o,'jr',rs1=1)
    if role in ('bit100','bit1'):
        base,off,mask=(0x40007000,0,256) if role=='bit100' else (0x40021000,36,1)
        lui(0,14,base);load(4,15,14,off);bz(6,10,16)
        imm(8,'ori',15,15,mask);store(12,15,14,off);ret(14)
        imm(16,'andi',15,15,-1-mask);e(20 if role=='bit100' else 18,'jump',target=pc+12)
    elif role=='mode_byte':
        lui(0,15,0x40021000);store(4,0,15,32,1);store(8,0,15,32,1)
        e(12,'li',rd=14,imm=1);e(14,'beq',rs1=10,rs2=14,target=pc+26)
        e(18,'li',rd=14,imm=4);e(20,'beq',rs1=10,rs2=14,target=pc+32)
        ret(24);store(26,10,15,32,1);ret(30);e(32,'li',rd=14,imm=5);store(34,14,15,32,1);ret(38)
    elif role=='or20':
        lui(0,14,0x40021000);load(4,15,14,32);binary(6,'or',10,10,15);store(8,10,14,32);ret(10)
    elif role=='bit8000':
        bz(0,10,16);lui(2,14,0x40021000);load(6,15,14,32);lui(8,13,0x8000)
        binary(10,'or',15,15,13);store(12,15,14,32);ret(14)
        lui(16,13,0x40021000);load(20,15,13,32);lui(22,14,0xffff8000)
        imm(24,'addi',14,14,-1);binary(26,'and',15,15,14);store(28,15,13,32);ret(30)
    elif role=='set10':
        lui(0,15,0x40003000);load(4,14,15,-2044,2);imm(8,'ori',14,14,16);store(12,14,15,-2044,2);ret(16)
    elif role=='clear10':
        lui(0,14,0x40003000);load(4,15,14,-2044,2);imm(8,'slli',15,15,16);imm(10,'srli',15,15,16)
        imm(12,'andi',15,15,-17);imm(14,'slli',15,15,16);imm(16,'srli',15,15,16);store(18,15,14,-2044,2);ret(22)
    elif role in ('pair18','pair08'):
        imm(0,'addi',2,2,-32);store(2,1,2,28);store(4,10,2,12);e(6,'jal',rd=1,target=0x1919c)
        load(10,10,2,12);lui(12,15,0x40003000);load(16,1,2,28);imm(18,'srli',14,10,16)
        if role=='pair08':imm(22,'andi',14,14,15)
        k=0 if role=='pair18' else 2
        imm(22+k,'slli',10,10,16);store(24+k,14,15,-2024 if not k else -2040,2)
        imm(28+k,'srli',10,10,16);store(30+k,10,15,-2020 if not k else -2036,2)
        imm(34+k,'addi',2,2,32);e(36+k,'jal',rd=0,target=0x191ae)
    elif role=='poll20':
        lui(0,14,0x40003000);load(4,15,14,-2044,2);imm(8,'andi',15,15,32);bz(12,15,4);ret(14)
    else:raise RuntimeError('unknown config pre-callee role')
    return s


def body(raw,role):
    _,pc,size,count,digest=next(d for d in DETAILS if d[0]==role)
    if role in ('set10','clear10','poll20'):
        check(int.from_bytes(raw[4:8],'little')&0x707f==0x5003,'pre-callee unsigned halfword encoding')
    n=decode(raw,pc);s=specs(role,pc);check(set(n)==set(s),'pre-callee complete boundaries '+role)
    for p,f in s.items():init.g(n,p,'pre-callee '+role+' operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(size,count,digest),'pre-callee complete identity '+role)
    defs=sorted({d['rd'] for d in n.values() if d.get('rd',0)})
    check(defs==DEFS[role],'pre-callee GPR census '+role)
    edges={};calls=[];tails=[]
    for p,d in n.items():
        op=d['op']
        if op=='jr':check(d['rs1']==1,'pre-callee ordinary return');q=[]
        elif op=='jal' and d['rd']==0:q=[];tails.append({'pc':hex(p),'target':hex(d['target']),'link_written':False})
        elif op=='jump':q=[d['target']]
        elif op in ('beqz','beq'):q=[p+d['size'],d['target']]
        else:q=[p+d['size']]
        check(all(v in n for v in q),'pre-callee CFG no cuts '+role);edges[p]=q
        if op=='jal' and d['rd']==1:calls.append({'pc':hex(p),'target':hex(d['target']),'link':hex(p+d['size'])})
    seen=set();active=set();back=[]
    def visit(p):
        if p in seen:return
        seen.add(p);active.add(p)
        for q in edges[p]:
            if q in active:back.append((p,q))
            else:visit(q)
        active.remove(p)
    visit(pc);check(seen==set(n),'pre-callee all local nodes reachable '+role)
    check(back==([(pc+12,pc+4)] if role=='poll20' else []),'pre-callee exact loop census '+role)
    paired=role in ('pair18','pair08')
    check(len(calls)==len(tails)==int(paired),'pre-callee complete nested call/tail census '+role)
    stores=[d for d in n.values() if d['op']=='store']
    if paired:
        check({(d['rs2'],d['imm'],d['width']) for d in stores if d['rs1']==2}=={(1,28,4),(10,12,4)},'pre-callee child frame stores')
        check({(d['rd'],d['imm'],d['width']) for d in n.values() if d['op']=='load' and d['rs1']==2}=={(1,28,4),(10,12,4)},'pre-callee child frame reloads')
        check(calls[0]['target']=='0x1919c' and tails[0]['target']=='0x191ae','pre-callee set/clear joins')
    else:check(not any(d.get('rs1')==2 for d in stores),'pre-callee leaf no stack stores')
    return {'role':role,'start':hex(pc),'end_exclusive':hex(pc+size),'bytes':size,'sha256':digest,
        'instructions':list(n.values()),'conditional_normal_return_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},
        'calls':calls,'external_tails':tails,'stores':stores,'encoded_GPR_definitions':defs,
        'local_back_edges':[[hex(p),hex(q)] for p,q in back],'complete_function':True}


def derive(app,carriers,header,coverage):
    parent=previous.derive(app,carriers,header,coverage)
    bodies={r:body(app[p-0x8000:p-0x8000+size],r) for r,p,size,count,digest in DETAILS}
    d=next(d for d in setup.DETAILS if d[0]=='clock1c');r,p,size,count,stores,digest=d
    reused=setup.body(app[p-0x8000:p-0x8000+size],r,p,size,count,stores,digest)
    entries={int(b['start'],16) for b in bodies.values()}|{int(reused['start'],16)}
    sites=parent['pre_calls'];check(len(sites)==13 and all(int(s['target'],16) in entries for s in sites[:12]),'pre-callee first12 exact constructor joins')
    check(sites[12]['target']=='0x197b8' and parent['bodies']['mode_tail']['external_tails'][0]['target']=='0x1929a','pre-callee remaining13th target')
    check(sum(b['bytes'] for b in bodies.values())==266 and sum(len(b['instructions']) for b in bodies.values())==96,'pre-callee new scope census')
    check(reused['encoded_GPR_writes']==[10,14,15] and not reused['calls'],'pre-callee reused19142 preservation')
    mmio={
        '19142':{'address':'0x4002101c','width':4,'caller_effect':'fresh word OR0x18000000'},
        '19076':{'address':'0x40007000','width':4,'caller_effect':'fresh word OR0x100'},
        '190c6':{'address':'0x40021024','width':4,'caller_effect':'fresh word OR1'},
        '1909e':{'address':'0x40021020','width':1,'caller_effect':'two ordered zero byte stores; A0=0 selects no thirdstore'},
        '190da':{'address':'0x40021020','width':4,'caller_effect':'fresh word OR512'},
        '190e6':{'address':'0x40021020','width':4,'caller_effect':'fresh word OR0x8000'},
        '1919c':{'address':'0x40002804','width':2,'effect':'fresh unsigned halfword OR0x10'},
        '191ae':{'address':'0x40002804','width':2,'effect':'fresh unsigned halfword AND0xffef'},
        '19272':{'address':'0x40002804','width':2,'effect':'repeated fresh unsigned reads until bit0x20 nonzero; no stores/timeout'},
        '19248':{'addresses':['0x40002808','0x4000280c'],'width':2,'caller_values':[0,1]},
        '19220':{'addresses':['0x40002818','0x4000281c'],'width':2,'caller_values':[0,0]}}
    # Pin MMIO effective-address operands independently of semantic prose.
    for role,offset,base,reg,imm,width in (
        ('bit100',12,0x40007000,14,0,4),('mode_byte',4,0x40021000,15,32,1),
        ('bit1',12,0x40021000,14,36,4),('or20',8,0x40021000,14,32,4),
        ('bit8000',12,0x40021000,14,32,4),('set10',12,0x40003000,15,-2044,2),
        ('clear10',18,0x40003000,14,-2044,2),('pair18',24,0x40003000,15,-2024,2),
        ('pair18',30,0x40003000,15,-2020,2),('pair08',26,0x40003000,15,-2040,2),
        ('pair08',32,0x40003000,15,-2036,2)):
        b=bodies[role];n={x['pc']:x for x in b['instructions']};init.g(n,int(b['start'],16)+offset,'pre-callee MMIO operand',op='store',rs1=reg,imm=imm,width=width)
        check(base+imm in (0x40007000,0x40021020,0x40021024,0x40002804,0x40002808,0x4000280c,0x40002818,0x4000281c),'pre-callee MMIO address algebra')
    return {'schema':'TSL9-config-precallees-static-v1','profile':parent['profile'],'APP_sha256':sha256(app).hexdigest(),
        'scope':'10 complete new bodies266B/96instructions plus reused19142 body30B/12instructions;12of13 pre-provider call sites covered under normal return',
        'bodies':bodies,'reused_19142':{'start':reused['start'],'bytes':30,'sha256':reused['sha256'],'new_code_bytes_counted':0},
        'covered_constructor_sites':sites[:12],'remaining_constructor_site':sites[12],
        'MMIO_encoded_contracts':mmio,
        'closed_call_graph':'only pair08/pair18 call1919c thenrestoreRA/SP andtail191ae; both leaves locally ordinary RET; all other covered helpers have no calls/tails',
        'GPR_contract':'covered9unique direct callees and2nested leaves do not defineGP/S registers; leafSP/RA unchanged; pair wrappers saveRA, use32B childframe, restoreRA/SP beforetail',
        'frame_contract':'relative constructorSP child stores only -20..-17 and -4..-1; disjoint constructorconfig offsets0..15 and constructorRA28..31; no other direct RAM stores in covered bodies',
        'preservation_boundary':'if first12calls complete with valid nonaliasing MMIO/code/stack accesses, preserved code and no external interference, constructorSP/config16B/RA/S/GP survive to197b8 call; no inference past1929a',
        'polling_contract':'19272 has one3-node SCC and no timeout/counter; each of4calls may read forever; every result is fresh, no hardware readiness/time or eventual return proved',
        'conditional_poll_A0s':[1,1,1,0],
        'poll_A0_proof':'190e6 preservesA0=1; poll leafdefinesA4/A5only; pair08(1) returnslow16(1)=1 throughA0-preservingclear10; pair18(0) returns0; externalinterference excluded',
        'config_byte12':'initialzero still available immediately before197b8 only under statedconditions; lastmode3tail1929a and lateroptionalhook still may modifyframe/config',
        'remaining':['1929a fullmode3 behavior and itscallees','actual installedprovider and slotwriters','MMIO sideeffects/physicalaliases/asynchronouswrites and frame/payload lifetime','general arithmetic domains'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(app):
    # Integer-offset/bitfield identities only; no RAM or peripheral state model.
    child=set(range(-20,-16))|set(range(-4,0));config=set(range(16));saved=set(range(28,32))
    check(not child&config and not child&saved and len(child)==8,'child writes vs constructor frame intervals')
    for h in range(65536):
        check(((h&-17)<<16&0xffffffff)>>16==h&0xffef,'clear10 halfword mask oracle')
        check((h|16)&16==16 and (h&0xffef)&16==0,'set/clear individual masks')
        check(bool(h&32)==bool((h>>5)&1),'poll ready predicate oracle')
    for x in (0,1,0xffff,0x10000,0xffffffff):
        check((((x>>16)&15),x&65535)==((x>>16)&15,x%65536),'pair08 split oracle')
    count=0
    for role,pc,size,n,h in DETAILS:
        raw=app[pc-0x8000:pc-0x8000+size]
        for p,d in decode(raw,pc).items():
            b=bytearray(raw);at=p-pc;w=d['size'];flip=1<<20 if w==4 else 4
            b[at:at+w]=(int.from_bytes(b[at:at+w],'little')^flip).to_bytes(w,'little')
            try:body(b,role)
            except RuntimeError as e:check(str(e).startswith('pre-callee '+role+' operand '),'specific pre-callee mutation guard '+str(e))
            else:raise RuntimeError('pre-callee mutation escaped')
            count+=1
        if role in ('set10','clear10','poll20'):
            b=bytearray(raw);b[5]^=64
            try:body(b,role)
            except RuntimeError as e:check(str(e)=='pre-callee unsigned halfword encoding','specific pre-callee unsigned guard')
            else:raise RuntimeError('pre-callee unsigned mutation escaped')
            count+=1
    check(count==99,'pre-callee mutation census')
    print('PASS:65536 halfword mask/poll cases; child-frame offset disjointness;96operand and3unsigned-load mutations rejected')


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
    tests(app);output=(json.dumps(ledger,indent=1,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'pre-callee exact ledger replay')
    print('PASS:10new complete bodies266B/96instructions; reused19142; first12callsite joins/CFG/SCC/tails/frame/MMIO/GPR census; exact ledger')
    print('PASS:NO target execution; polling termination/last1929a/MMIO effects/installedprovider/lifetime UNPROVED')


if __name__=='__main__':main()
