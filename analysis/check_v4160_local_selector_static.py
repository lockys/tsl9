"""Complete local selector and nested word-pair shift leaf, offline only.

Original operands/CFG and host finite-width algebra/ranking facts; no target
ISA, callback, RAM/frame, MMIO, resident or device execution/emulation.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_ram_callback_closure_static as previous

init,sparse,check=previous.init,previous.sparse,previous.check
OUT=Path(__file__).with_name('v4160-local-selector-static.json')
MASK=0xffffffff
DETAILS=((0x41736,0x6dec2,-1610,-1644,'e20608a420fad0d2bcadc9188c56c5f655764288c31e5322ba361faa14c885ed'),
 (0x41776,0x6e0b2,-1114,-1148,'4f6f58637e6f16ca3efa2844d7e3840b7eac68ccc04c58352bf6beca5ee1978e'))
LEAF_HASH='1eb4d7b36ea3c0fd97d6c5e13c51cd41901375aea68054d52fa1f0572a047a92'
SAVED=((1,44),(8,40),(9,36),(18,32),(19,28),(20,24),(21,20),(22,16),(23,12))


def decode(raw,pc):
    n={};off=0
    while off<len(raw):
        h=int.from_bytes(raw[off:off+2],'little');size=4 if h&3==3 else 2;check(off+size<=len(raw),'selector whole instruction')
        chunk=raw[off:off+size];w=int.from_bytes(chunk,'little');p=pc+off
        if size==4 and w&0xfe00707f in (0x02007033,0x00005033):
            d=dict(pc=p,size=4,bytes=chunk.hex(),op='remu' if w&0xfe00707f==0x02007033 else 'srl',
                rd=w>>7&31,rs1=w>>15&31,rs2=w>>20&31)
        elif size==4 and w&0xfe00707f==0x40005013:
            d=dict(pc=p,size=4,bytes=chunk.hex(),op='srai',rd=w>>7&31,rs1=w>>15&31,imm=w>>20&31)
        else:d=previous.decode(chunk,p)[p]
        n[p]=d;off+=size
    return n


def specs(role,pc,lows=None):
    s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def addi(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def load(o,r,b,v,w=4):e(o,'load',rd=r,rs1=b,imm=v,width=w)
    def store(o,r,b,v,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    def binary(o,op,r,a,b):e(o,op,rd=r,rs1=a,rs2=b)
    def move(o,r,a):e(o,'mv',rd=r,rs2=a)
    if role=='selector':
        addi(0,2,2,-48);store(2,9,2,36)
        for j,(r,o) in enumerate((SAVED[0],SAVED[1])+SAVED[3:]):store(4+2*j,r,2,o)
        load(20,15,10,53,1);load(24,8,10,311,1);move(28,9,10);binary(30,'add',8,8,15)
        e(32,'andi',rd=8,rs1=8,imm=255);addi(36,15,0,36);e(40,'bgeu',rs1=15,rs2=8,target=pc+52)
        addi(44,8,8,-37);e(48,'andi',rd=8,rs1=8,imm=255);load(52,20,9,312);load(56,21,9,316)
        store(60,8,9,311,1);move(64,12,8);move(66,10,20);move(68,11,21)
        e(70,'auipc',rd=1,imm=0xe006d000);e(74,'jalr',rd=1,rs1=1,imm=lows[0]);e(78,'andi',rd=10,rs1=10,imm=1)
        e(80,'bnez',rs1=10,target=pc+124);load(82,22,9,301,1);e(86,'li',rd=18,imm=0);e(88,'li',rd=19,imm=0)
        binary(90,'remu',22,8,22);addi(94,23,0,37);move(98,12,18);move(100,10,20);move(102,11,21)
        e(104,'auipc',rd=1,imm=0xe006d000);e(108,'jalr',rd=1,rs1=1,imm=lows[1]);e(112,'andi',rd=10,rs1=10,imm=1)
        e(114,'beqz',rs1=10,target=pc+158);e(116,'bne',rs1=19,rs2=22,target=pc+150)
        e(120,'andi',rd=8,rs1=18,imm=255);store(124,8,9,310,1)
        for j,(r,o) in enumerate(SAVED):load(128+2*j,r,2,o)
        addi(146,2,2,48);e(148,'jr',rs1=1);addi(150,19,19,1);e(152,'slli',rd=19,rs1=19,imm=24)
        e(154,'srai',rd=19,rs1=19,imm=24);addi(158,18,18,1);e(160,'bne',rs1=18,rs2=23,target=pc+98);e(164,'jump',target=pc+124)
    elif role=='leaf':
        e(0,'beqz',rs1=12,target=pc+28);addi(2,15,0,32);binary(6,'sub',15,15,12)
        e(8,'bge',rs1=0,rs2=15,target=pc+30);binary(12,'srl',10,10,12);binary(16,'sll',15,11,15)
        binary(20,'srl',12,11,12);binary(24,'or',10,10,15);move(26,11,12);e(28,'jr',rs1=1)
        addi(30,10,12,-32);e(34,'li',rd=12,imm=0);binary(36,'srl',10,11,10);move(40,11,12);e(42,'jump',target=pc+28)
    else:raise RuntimeError('unknown selector role')
    return s


def body(raw,role,pc,digest,lows=None):
    if role=='selector':
        check(int.from_bytes(raw[90:94],'little')&0xfe00707f==0x02007033,'selector exact REMU encoding')
        check(int.from_bytes(raw[154:158],'little')&0xfe00707f==0x40005013,'selector exact SRAI encoding')
    else:check(all(int.from_bytes(raw[o:o+4],'little')&0xfe00707f==0x00005033 for o in (12,20,36)),'leaf exact logical SRL encodings')
    n=decode(raw,pc);s=specs(role,pc,lows);check(set(n)==set(s),'selector complete boundaries '+role)
    for p,f in s.items():init.g(n,p,'selector '+role+' operand '+hex(p-pc),**f)
    size,count=(166,61) if role=='selector' else (44,15)
    check((len(raw),len(n),sha256(raw).hexdigest())==(size,count,digest),'selector complete identity '+role)
    edges={};calls=[]
    for p,d in n.items():
        if d['op']=='jr':qs=[]
        elif d['op']=='jump':qs=[d['target']]
        elif d['op'] in ('bgeu','bge','bnez','beqz','bne'):qs=[p+d['size'],d['target']]
        else:qs=[p+d['size']]
        check(all(q in n for q in qs),'selector no local CFG cut '+role);edges[p]=qs
        if d['op']=='jalr':calls.append({'pc':hex(p),'link':hex(p+4),'target':hex((p-4+n[p-4]['imm']+d['imm'])&0xfffffffe)})
    seen=set()
    def visit(p):
        if p in seen:return
        seen.add(p)
        for q in edges[p]:visit(q)
    visit(pc);check(seen==set(n),'selector all nodes locally reachable '+role)
    return {'start':hex(pc),'end_exclusive':hex(pc+size),'bytes':size,'sha256':digest,'instructions':list(n.values()),
        'CFG':{hex(k):[hex(q) for q in qs] for k,qs in edges.items()},'calls':calls,'complete_function':True}


def derive(app,carriers,header,coverage):
    parent=previous.derive(app,carriers,header,coverage);profiles=[]
    for i,(data,d) in enumerate(zip(carriers,DETAILS)):
        source,leafpc,lo1,lo2,h=d;p=parent['profiles'][i]
        shift=int(p['mapped_start'],16)-int(p['flash_start'],16);runtime=source+shift
        check(runtime==0x200014c6,'mapped selector entry')
        selector=body(init.binding.take(data,source,166),'selector',runtime,h,(lo1,lo2))
        body(init.binding.take(data,source,166),'selector',source,h,(lo1,lo2))
        leaf=body(init.binding.take(data,leafpc,44),'leaf',leafpc,LEAF_HASH)
        check([x['target'] for x in selector['calls']]==[hex(leafpc)]*2,'both nested calls target complete leaf')
        ln={x['pc']:x for x in leaf['instructions']};defs={x['rd'] for x in ln.values() if 'rd' in x}
        check(defs=={10,11,12,15} and not leaf['calls'] and not any(x['op'] in ('load','store') for x in ln.values()),'leaf only A0/A1/A2/A5 definitions, no memory/calls')
        lgraph={int(k,16):[int(q,16) for q in qs] for k,qs in leaf['CFG'].items()}
        check(all(len(c)==1 and c[0] not in lgraph[c[0]] for c in previous.previous.previous.previous.components(lgraph)),'nested leaf acyclic')
        sn={x['pc']:x for x in selector['instructions']};sg={int(k,16):[int(q,16) for q in qs] for k,qs in selector['CFG'].items()}
        cycles=[c for c in previous.previous.previous.previous.components(sg) if len(c)>1 or c[0] in sg[c[0]]]
        expected={v for v in sn if runtime+98<=v<runtime+120 or runtime+150<=v<runtime+164}
        check(len(cycles)==1 and len(cycles[0])==13 and set(cycles[0])==expected,'selector exact 13-node scan SCC')
        check({(x['rs2'],x['imm']) for x in sn.values() if x['op']=='store' and x['rs1']==2}==set(SAVED),'nine exact frame stores')
        check({(x['rd'],x['imm']) for x in sn.values() if x['op']=='load' and x['rs1']==2}==set(SAVED),'nine exact frame restores')
        check([(x['rs1'],x['rs2'],x['imm'],x['width']) for x in sn.values() if x['op']=='store' and x['rs1']!=2]==[(9,8,311,1),(9,8,310,1)],'only two direct object-byte stores')
        # Ranking operand facts, not target execution: i starts0, only i++
        # within SCC; limit37 preserved by the no-call/no-S-register leaf.
        check([(x['pc'],x['op'],x.get('imm')) for x in sn.values() if x.get('rd')==18]==
            [(runtime+86,'li',0),(runtime+134,'load',32),(runtime+158,'addi',1)],'scan index definitions and restore')
        check(sn[runtime+94]['imm']==37 and 23 not in defs and 18 not in defs,'limit/index preserved by nested leaf')
        callers=[c for c in p['calls'] if c['target']==hex(runtime)];check(len(callers)==2,'two complete callback direct selector callers')
        full=previous.decode(init.binding.take(data,int(p['flash_start'],16),978),int(p['mapped_start'],16))
        for c in callers:init.g(full,int(c['pc'],16)-2,'callback explicit selector A0=S0',op='mv',rd=10,rs2=8)
        profiles.append({'label':p['label'],'flash_selector':hex(source),'selector':selector,'shift_leaf':leaf,
            'callback_callers':callers,'leaf_defined_registers':sorted(defs),'scan_SCC_nodes':[hex(v) for v in cycles[0]],
            'conditional_scan_bound':37,'conditional_total_probe_bound':38,
            'bound_premises':'verified leaf identity/mapping, fault-free calls and valid frame/object accesses, no adverse aliases/interrupt/reentry/writer/code changes',
            'actual_installed_binding_or_runtime_completion_proved':False})
    return {'schema':'TSL9-local-selector-static-v1','profile':parent['profile'],'profiles':profiles,
        'scope':'2 complete selectors332B/122instructions +2 identical complete nested leaves88B/30instructions',
        'entry_contract':'c=low8(fresh U8[object+311]+fresh U8[object+53]); ifc>36 subtract37 once; snapshot words312/316; SB c->byte311; probe pair atc',
        'shift_leaf_contract':'for count0..255: n0 leaves pair;1..31 logical pair right shift;32..255 A1=0,A0=oldA1>>((n-32)&31); counts>=64 are not general64-bit shift',
        'fallback_contract':'if initial probe lowbit0, fresh d=U8[object+301]; targetOrdinal=REMU(c,d), with d0 ->c under RV32M; scan indices0..36, selecting matching set-bit ordinal if found, else retainc',
        'ordinal_contract':'ordinal increments only after nonmatching set-bit; explicit signExtend8 update retained, but at most37 increments under verified scan bound',
        'output_contract':'byte310 receives selectedindex or retainedc; A0 is last probe result AND1, not a proved success flag; stack restores nine fields; ordinary RET',
        'preservation_contract':'nested leaf only defines A0/A1/A2/A5, with no memory/call/frame; selector restores RA/S0..S7 if saved words survive; direct nonstack writes only bytes311/310',
        'premises':['actual installed candidate, completed preserved first-copy selector and leaf code; valid conditional ISA/object/frame accesses',
            'object and stack aliasing or outside writers can invalidate saved words/data; no adverse interrupts/reentry or code modification assumed',
            'byte bounds, divisor meaning, bitset validity and selected-index constraints remain unproved; candidate can exceed36 and63',
            'bounded selector scan does not prove the larger caller callback terminates or identify other providers'],
        'remaining':['second selector417dc/4181c and bit-reversal transforms','other callback helpers, config gates/copy/actual provider binding',
            'object/global writers and practical field bounds','whole-system progress and frame/payload lifetime'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    for a in range(256):
        for b in range(256):
            c=(a+b)&255;c=c if c<=36 else c-37
            check(0<=c<=218,'candidate domain after low8 and one subtract')
            if a<=36 and b<=36:check(c==(a+b)%37,'conditional modulo37 domain')
    check(74-37==37 and 74%37==0,'one subtraction is not unrestricted modulo37')
    for c in range(219):
        for d in range(256):
            remainder=c%d if d else c
            check(0<=remainder<=218 and (d!=0 or remainder==c),'unsigned remainder byte domain including divisorzero')
    values=(0,1,0x80000000,0xffffffff,0x01234567,0x89abcdef)
    for lo in values:
        for hi in values:
            pair=(hi<<32)|lo
            for n in range(256):
                result=pair if n==0 else pair>>n if n<32 else hi>>((n-32)&31)
                if n<64:check(result==pair>>n,'leaf pair right shift within0..63')
                else:check(result==hi>>(n&31),'large byte count uses RV32 low5 shift')
    check((1>>((64-32)&31))==1 and ((1<<32)>>64)==0,'count64 counterexample to unbounded64-shift')
    check(all(0<=i<37 and i+1<=37 for i in range(37)) and 37<128,'finite index ranking and ordinal signed8 bound')
    changes={'selector':((0,4),(20,1<<20),(32,1<<20),(40,1<<12),(44,1<<20),(60,1<<20),(74,1<<20),
        (90,1<<12),(108,1<<20),(116,1<<12),(124,1<<20),(128,4),(154,1<<30),(160,1<<12)),
        'leaf':((0,4),(8,1<<12),(12,1<<30),(16,1<<20),(20,1<<15),(36,1<<20))}
    count=0
    for data,(source,leafpc,lo1,lo2,h) in zip(carriers,DETAILS):
        for role,pc,size,digest,lows in (('selector',source,166,h,(lo1,lo2)),('leaf',leafpc,44,LEAF_HASH,None)):
            raw=init.binding.take(data,pc,size)
            for off,flip in changes[role]:
                b=bytearray(raw);width=decode(raw,pc)[pc+off]['size'];b[off:off+width]=(int.from_bytes(b[off:off+width],'little')^flip).to_bytes(width,'little')
                try:body(b,role,pc,digest,lows)
                except RuntimeError as e:check(str(e) in ('selector '+role+' operand '+hex(off),'selector exact REMU encoding','selector exact SRAI encoding','leaf exact logical SRL encodings'),'specific selector mutation guard '+str(e))
                else:raise RuntimeError('selector mutation escaped')
                count+=1
    check(count==40,'selector mutation census')
    print('PASS: 65536 byte-sum cases; 56064 remainder cases; 9216 host pair/count identities; 40 specified mutations rejected')


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
    else:check(OUT.read_bytes()==output,'local selector exact ledger replay')
    print('PASS: complete420B/152instructions; callback caller join; 13-node scan SCC; exact pure-leaf clobbers; conditional37/38 probe bounds')
    print('PASS: exact ledger; NO target execution; actual binding/field bounds/frame lifetime/larger callback termination UNPROVED')


if __name__=='__main__':main()
