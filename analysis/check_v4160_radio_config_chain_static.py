"""64298 config callees and bounded tail entry, strictly static.

Original bytes/CFG/control-memory operands, def/store censuses and interval
identities only. No target ISA, MMIO/RMW, callback or device execution/model.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_role_initializer_fields_static as previous
import check_v4160_ram_callback_loop_static as graphs

init,sparse,check=previous.init,previous.sparse,previous.check
OUT=Path(__file__).with_name('v4160-radio-config-chain-static.json')
ROLES=('parent','registers','bulk','pulse','bits','tail_prefix')
SIZES=(118,60,372,54,90,76)
COUNTS=(34,23,140,20,31,25)
DETAILS=(
 ((0x64298,0x6430e,0x660ce,0x66098,0x638ea,0x641b0),0,0x63eda,
 ('9f9a81049c85e8a55640027311b107b0b6cfaf82c3dd402ebb3375745fa782d8','8e0872ead0eb26ac696d9c302036701812d9788330404cc2bbe8878dcbe669d8',
  '5c7fcd667d7ec34a7d12c7cf19225ddd31929b3e3469a2b11134cedf8253f3cf','fdb8664d445076f9beebdd2144956d37181d274760cc52e995e20571d2cddcfb',
  'adcf72e0cd136e982c91dc040dad0436b7e218c4c55add25675ebb32c6c14db2','b664ce8f31185b7ed650450b701049b1b250968d3281ff1b124010f1f0a551bd')),
 ((0x64382,0x643f8,0x6620c,0x661d6,0x639d4,0x6429a),80,0x63fc4,
 ('d61830401117594542b26a88915a4bae1ffc86a8f15b43d1ca59aff4e05b5f69','2733a007bf488a6fcbbe0e7ce861e3b47c7a3297913368f347048c1cebf14458',
  '11cbf7ee528a4a215d17142265545a0714d4084e964dd3ca89897bd31452f37e','bda3d3bf068a75d0b07a8da43215f5a6ee3c4eca7a784bac20605d65627645aa',
  '76dd5efd6d4317a3f18206cb5949078a82ce468b25c97dff77a709d70af4a95b','52b79741f34dd6e5de4e0cbc33b8e8d523c7b6064d4011d063d48f4134e47300')))
BULK_STORES=((2,2,12,1),(24,15,40,14),(42,15,72,14),(60,15,72,14),(76,15,72,14),(90,15,72,14),(104,15,72,14),
 (118,15,76,14),(130,15,76,14),(142,15,76,11),(148,15,76,14),(158,15,76,14),(178,15,80,16),(196,15,84,16),
 (206,15,84,12),(212,15,84,12),(222,15,60,10),(236,15,60,11),(250,15,60,12),(258,15,44,12),(264,15,44,13),
 (276,15,44,13),(294,15,44,13),(300,15,48,13),(308,15,48,13),(316,15,48,13),(326,15,48,14),(336,15,48,14),
 (354,15,56,14),(362,15,56,17))
BULK_LOADS=((12,15,15,1424),(26,14,15,72),(44,14,15,72),(62,14,15,72),(78,14,15,72),(92,14,15,72),
 (106,14,15,76),(120,14,15,76),(132,11,15,76),(144,14,15,76),(150,14,15,76),(160,16,15,80),
 (182,16,15,84),(200,12,15,84),(208,12,15,84),(214,10,15,60),(224,11,15,60),(238,12,15,60),
 (252,12,15,44),(260,12,15,44),(266,13,15,44),(278,13,15,44),(296,13,15,48),(302,13,15,48),
 (310,13,15,48),(318,14,15,48),(328,14,15,48),(338,14,15,56),(356,14,15,56),(366,1,2,12))


def decode(raw,pc):
    n={};off=0
    while off<len(raw):
        h=int.from_bytes(raw[off:off+2],'little');size=4 if h&3==3 else 2;chunk=raw[off:off+size]
        check(len(chunk)==size,'radio complete instruction')
        if h==1 and size==2:d=dict(pc=pc+off,bytes=chunk.hex(),size=2,op='nop')
        else:d=previous.decode(chunk,pc+off)[pc+off]
        n[pc+off]=d;off+=size
    return n


def specs(role,index):
    addresses,delta,rf,_=DETAILS[index];pc=addresses[ROLES.index(role)];s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def lui(o,r,v):e(o,'lui',rd=r,imm=v)
    def imm(o,op,r,b,v):e(o,op,rd=r,rs1=b,imm=v)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    def load(o,r,b,v,w=4,**f):e(o,'load',rd=r,rs1=b,imm=v,width=w,**f)
    def store(o,r,b,v,w=4,**f):e(o,'store',rs2=r,rs1=b,imm=v,width=w,**f)
    def binary(o,op,r,a,b):e(o,op,rd=r,rs1=a,rs2=b)
    if role=='parent':
        lui(0,15,0x20003000);store(4,0,15,1296+delta,1);lui(8,15,0x20003000);store(12,0,15,1292+delta)
        lui(16,15,0x40024000);imm(20,'addi',13,15,768);lui(24,14,0x20003000);store(28,13,14,1284+delta)
        imm(32,'addi',13,15,512);lui(36,14,0x20003000);store(40,13,14,1340+delta);lui(44,13,0x40025000)
        lui(48,14,0x20003000);store(52,13,14,1424+delta);imm(56,'addi',15,15,256);lui(60,14,0x20003000)
        imm(64,'addi',2,2,-16);store(66,15,14,1288+delta);lui(70,15,0x20003000);store(74,1,2,12)
        imm(76,'addi',15,15,1300+delta);li(80,14,1);store(82,14,15,7,1,mnemonic='qk.c.sb')
        lui(84,14,0x20003000);load(88,14,14,492+delta);store(92,14,15,36);imm(94,'addi',14,14,272);store(98,14,15,32)
        for off,target in ((100,addresses[1]),(102,addresses[2]),(106,addresses[4])):e(off,'jal',rd=1,target=target)
        load(110,1,2,12);imm(112,'addi',2,2,16);e(114,'jal',rd=0,target=addresses[5])
    elif role=='registers':
        lui(0,15,0x20003000);load(4,15,15,1340+delta);imm(8,'addi',14,0,140);imm(12,'addi',13,0,108)
        for off,r,v in ((16,14,20),(18,13,28),(20,14,36),(26,12,44),(28,14,52),(30,12,60),(32,14,68),(42,13,76),(44,14,116),(50,14,8),(56,14,12)):store(off,r,15,v)
        imm(22,'addi',12,0,60);lui(34,14,0x20003000);load(38,14,14,1336+delta);lui(46,14,0x10000)
        imm(48,'addi',14,14,-1);lui(52,14,0xf000);imm(54,'addi',14,14,15);e(58,'jr',rs1=1)
    elif role=='bulk':
        imm(0,'addi',2,2,-16);e(4,'jal',rd=1,target=addresses[3]);lui(8,15,0x20003000)
        for o,base,offset,r in BULK_STORES:store(o,r,base,offset)
        for o,r,base,offset in BULK_LOADS:load(o,r,base,offset+(delta if o==12 else 0))
        imm(368,'addi',2,2,16);e(370,'jr',rs1=1)
    elif role=='pulse':
        lui(0,15,0x20003000);load(4,13,15,1424+delta);lui(8,14,4096);imm(10,'addi',14,14,257);store(14,14,13,12)
        li(16,14,20);e(18,'nop');imm(20,'addi',14,14,-1);e(22,'bnez',rs1=14,target=pc+18)
        load(24,14,15,1424+delta);store(28,0,14,12);li(32,14,20);e(34,'nop');imm(36,'addi',14,14,-1)
        e(38,'bnez',rs1=14,target=pc+34);load(40,14,15,1424+delta);lui(44,15,4096);imm(46,'addi',15,15,257);store(50,15,14,12);e(52,'jr',rs1=1)
    elif role=='bits':
        lui(0,15,0x20003000);load(4,15,15,1288+delta);lui(8,13,0x800000);lui(12,12,0x80011000)
        load(16,14,15,0);imm(18,'addi',12,12,-312);binary(22,'or',14,14,13);store(24,14,15,0)
        load(26,14,15,0);lui(28,13,0x10000000);binary(32,'or',14,14,13);store(34,14,15,0)
        imm(36,'addi',14,0,464);store(40,14,15,52);lui(42,14,0x20003000);load(46,14,14,512+delta,1)
        imm(50,'slli',13,14,25);binary(54,'or',13,13,12);store(56,13,15,44);load(58,13,15,44)
        lui(60,12,0x82000000);imm(64,'andi',14,14,63);imm(68,'addi',12,12,-1);imm(70,'slli',14,14,25)
        binary(72,'and',13,13,12);binary(74,'or',14,14,13);store(76,14,15,44);lui(78,14,0x90000)
        imm(82,'addi',14,14,131);store(86,14,15,32);e(88,'jr',rs1=1)
    else:
        imm(0,'addi',2,2,-32);store(2,8,2,24);lui(4,8,0x20003000);imm(8,'addi',8,8,1300+delta)
        load(12,14,8,7,1,mnemonic='qk.c.lbu')
        for o,r,v in ((14,1,28),(16,9,20),(18,18,16),(20,19,12),(22,20,8),(24,21,4)):store(o,r,2,v)
        li(26,15,4);e(28,'beq',rs1=15,rs2=14,target=pc+214);load(32,14,8,7,1,mnemonic='qk.c.lbu')
        e(34,'beq',rs1=15,rs2=14,target=pc+214);lui(38,15,0x20003000);load(42,14,15,1284+delta)
        lui(46,9,0x40024000);imm(50,'addi',15,9,768);e(54,'bne',rs1=14,rs2=15,target=pc+214)
        load(58,20,9,524);store(62,0,9,524);e(66,'fence.i');li(70,10,13);e(72,'jal',rd=1,target=rf)
    return pc,s


def body(raw,role,index):
    pc,s=specs(role,index);n=decode(raw,pc);j=ROLES.index(role)
    if role!='bulk':check(set(n)==set(s),'radio '+role+' boundaries')
    else:check(set(s)<=set(n),'radio bulk guarded memory/control boundaries')
    for p,f in s.items():init.g(n,p,'radio '+role+' operand '+hex(p-pc),**f)
    if role=='bulk':
        check([p-pc for p,d in n.items() if d['op']=='store']==[x[0] for x in BULK_STORES],'radio bulk full store census')
        check([p-pc for p,d in n.items() if d['op']=='load']==[x[0] for x in BULK_LOADS],'radio bulk full load census')
        check([p-pc for p,d in n.items() if d.get('rd')==15]==[8,12],'radio bulk A5 has sole stable pointer definition')
        check(sorted({d['rd'] for d in n.values() if d.get('rd',0)})==[1,2,6,10,11,12,13,14,15,16,17,28,29],'radio bulk GPR census excludes S/GP')
    check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[j],COUNTS[j],DETAILS[index][-1][j]),'radio '+role+' full identity')
    edges={};external=[];calls=[]
    for p,d in n.items():
        op=d['op']
        if op=='jr':check(d['rs1']==1,'radio ordinary RET');q=[]
        elif op=='jal' and d['rd']==0:q=[d['target']]
        elif op in ('bnez','beq','bne'):q=[p+d['size'],d['target']]
        else:q=[p+d['size']]
        for v in q:
            if v not in n:
                check(role=='parent' and p==pc+114 or role=='tail_prefix' and v in (pc+214,pc+76),'radio explicit exit only')
                external.append([hex(p),hex(v)])
        edges[p]=[v for v in q if v in n]
        if op=='jal' and d['rd']==1:calls.append({'pc':hex(p),'target':hex(d['target']),'link':hex(p+d['size'])})
    cycles=[c for c in graphs.components(edges) if len(c)>1 or c[0] in edges[c[0]]]
    check(cycles==([[pc+18,pc+20,pc+22],[pc+34,pc+36,pc+38]] if role=='pulse' else []),'radio exact cycle census')
    check(len(calls)==dict(parent=3,registers=0,bulk=1,pulse=0,bits=0,tail_prefix=1)[role],'radio exact call census')
    if role in ('registers','pulse','bits'):
        check(not any(d.get('rd') in (1,2,3,8,9,*range(18,28)) for d in n.values()),'radio leaf RA/SP/GP/S preserved')
    if role in ('parent','bulk'):
        frames=[d for d in n.values() if d['op']=='store' and d['rs1']==2]
        check(len(frames)==1 and frames[0]['rs2']==1 and frames[0]['imm']==12,'radio sole RA frame save')
    return {'role':role,'start':hex(pc),'bytes':len(raw),'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),
        'normal_return_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},'external_exits':external,'calls':calls,
        'cycles':[[hex(p) for p in c] for c in cycles],'independent_operand_guard_count':len(s),
        'bulk_scope':'full byte identity/GPR/CFG/memory-control operands; individual RMW arithmetic formulas not claimed' if role=='bulk' else None,
        'complete_function_or_tail_body':role!='tail_prefix'}


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[]
    for i,(data,pr,detail) in enumerate(zip(carriers,parent['profiles'],DETAILS)):
        addresses,delta,rf,_=detail
        bodies={role:body(init.binding.take(data,pc,size),role,i) for role,pc,size in zip(ROLES,addresses,SIZES)}
        check(pr['cut_before_first_late_call']['target']==hex(addresses[0]),'radio initializer caller join')
        g=0x20003000;state=g+1300+delta
        ram=[(g+1296+delta,1,'0'),(g+1292+delta,4,'0'),(g+1284+delta,4,'0x40024300'),
            (g+1340+delta,4,'0x40024200'),(g+1424+delta,4,'0x40025000'),(g+1288+delta,4,'0x40024100'),
            (state+7,1,'1'),(state+36,4,'fresh X=U32[F+0]'),(state+32,4,'(X+272)mod2^32')]
        objectbase=int(pr['object_base'],16);ctxgate=int(pr['context_gate_byte'],16);ctx=ctxgate-3
        protected=[(objectbase,296),(ctx+1,1),(ctx+2,1),(ctxgate,1),(ctx+40,4),
            (previous.previous.previous.layout.T,4*212),(previous.previous.previous.layout.A+8,16),(0x200040a6,1),(0x20004184,1)]
        for p,width,value in ram:
            for q,z in protected:check(previous.previous.previous.origin.separated(p,width,q,z),'radio fixed RAM excludes live role/table/task/node fields')
        # Memory-base provenance from fixed loads and absence of later base defs.
        mmio=[]
        for role,base in (('registers',0x40024200),('bulk',0x40025000),('pulse',0x40025000),('bits',0x40024100)):
            for d in bodies[role]['instructions']:
                if d['op']=='store' and d['rs1']!=2:mmio.append({'role':role,'pc':hex(d['pc']),'address':hex(base+d['imm']),'bytes':d['width']})
        check(len(mmio)==49 and all(d['bytes']==4 for d in mmio),'radio exact49 conditional MMIO word stores')
        check({int(d['address'],16) for d in mmio if d['role']=='bulk'}=={0x40025000+x for x in (40,44,48,56,60,72,76,80,84)},'radio bulk address set')
        tp=addresses[5];tb=bodies['tail_prefix'];ei={int(p,16):[int(q,16) for q in qs] for p,qs in tb['normal_return_CFG'].items()}
        selected=previous.previous.previous.chain(ei,tp,{tp+28:tp+32,tp+34:tp+38,tp+54:tp+58},tp+72)
        profiles.append({'label':pr['label'],'bodies':bodies,'RAM_publications':[{'address':hex(p),'bytes':w,'value':v} for p,w,v in ram],
            'conditional_MMIO_stores':mmio,'state_byte':hex(state+7),'conditional_state_at_tail_reads':1,
            'pointer_slot_premises':{hex(g+1340+delta):'0x40024200',hex(g+1424+delta):'0x40025000',hex(g+1288+delta):'0x40024100',hex(g+1284+delta):'0x40024300'},
            'bounded_tail_path_before_RF_call':selected,'cut_before_RF_call':{'pc':hex(tp+72),'target':hex(rf),'A0':13},
            'tail_entry_parent_frame_released':True,'tail_prefix_frame_active_bytes':32,'MMIO_control_at_cut':'saved word inS4; CPU SW0 andFENCE.I identified, restoration not yet proved',
            'conditional_context_gate':5,'conditional_count':6,'actual_installed_binding_proved':False})
    return {'schema':'TSL9-radio-config-chain-static-v1','profile':parent['profile'],'APP_sha256':sha256(image).hexdigest(),
        'scope':'per candidate five complete bodies694B/248instructions plus bounded76B/25instruction tail prefix; bulk arithmetic retained by fullhash whilememory/control/definition contracts checked; no new C bytes',
        'profiles':profiles,
        'binding_boundary':'publishedpointerwords andfreshX arestatic CPUdata effects. Freshdereferences must retain publishedMMIObases; X isnotcalled ordereferenced bythisclosedprefix. X=heapH onlyifactualfreshsourcepreserved; storingvalues doesnot provehardware/retention effects',
        'pulse_contract':'threefreshbase loads, SW1101/0/1101 tobase+12 inthatorder; two loops eachLI20,NOP,ADDI-1,BNEZ,20iterations undernoGPRinterference/normalinstructions. Nohardware-ready polling/timeunit inferred',
        'registers_contract':'eleven orderedwordstores to40024200 offsets20,28,36,44,52,60,68,76,116,8,12; offset116 valuefreshX, lastvalue0000f00f isdirectwrite, notrestorationofpreviousMMIOsnapshot',
        'bulk_contract':'onecalltopulse; all29nonframewordstores throughsinglefreshbase40025000; orderedfreshreads/RMWretained, no coherent snapshot/finalhardwarestateformula claimed',
        'bits_contract':'sixorderedwordstores to40024100 offsets0,0,52,44,44,32; onefreshU8[F+20] sourcebyte used, notwritten; noframe/nestedcalls',
        'preservation_to_cut':'parentRAMpublications excludeupstreamB/count/capacity/gate/table/task/node; closedhelpers onlyownRAframe/MMIOstores. Undervalidnonaliasframes/mapping andnoadverseMMIO/FENCE.I/IRQ/DMA/reentry/externalwrites, statebyte1 survivesintobothfresh tailreads, skipsstate4 exits, pointer40024300testpasses',
        'return_boundary':'parentrestores16Bframe andtailstransferRAfrominitializer; tailprefixbuilds32Bframe, reads/saves4002420c thenCPUclearsitandFENCE.I. Stopbefore63eda/63fc4 callwithA0=13; noRFcallback/remainingtail/initializerreturn orcontrolrestore claim',
        'premises':'all previous gatezero/prefix/field conditions; actualcodeandMMIOpointermappingmatchcandidates; validdata/frameaccesses, preservedsavedwordsandrequirednormalcompletion; noadversephysicalalias/MMIO/asynchronous interference. CPUstore addresses are not hardware outcome or object lifetime proofs',
        'remaining':['63eda/63fc4 andlater641b0/6429a calls/controlrestore','remaininginitializercallees/tail andouterregistrations','actualfreshpointers/installedproviders, MMIOphysicaleffects andlaterlifetimes'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    operand=canonical=0
    for i,(data,detail) in enumerate(zip(carriers,DETAILS)):
        for role,pc,size in zip(ROLES,detail[0],SIZES):
            raw=init.binding.take(data,pc,size);n=decode(raw,pc);guarded=specs(role,i)[1]
            for p in guarded:
                d=n[p];at=p-pc;w=d['size'];buf=bytearray(raw)
                special=d['op'] in ('nop','fence.i');flip=(4 if d['op']=='nop' else 128) if special else (1<<20 if w==4 else 4)
                buf[at:at+w]=(int.from_bytes(buf[at:at+w],'little')^flip).to_bytes(w,'little')
                try:body(buf,role,i)
                except RuntimeError as e:
                    check(str(e)=='unsupported static leaf encoding '+hex(p) if special else str(e).startswith('radio '+role+' operand '),'radio specified mutation guard '+str(e))
                else:raise RuntimeError('radio mutation escaped')
                if special:canonical+=1
                else:operand+=1
    check((operand,canonical)==(390,6),'radio mutation census')
    for value in (0,1,0x2000418c,0xffffff00,0xffffffff):check((value+272)&0xffffffff==(value+272)%2**32,'radio data-pointer addition wrap identity')
    check([20-i for i in range(21)]==list(range(20,-1,-1)) and all(20-i>0 for i in range(20)),'radio finite20 countdown ranking')
    check(4096+257==0x1101 and 0xf000+15==0xf00f,'radio scalar constants')
    print('PASS:390 memory/control/operand mutations and6 noncanonical NOP/FENCE.I encodings rejected;20-step ranking/pointer-wrap identities')


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
    else:check(OUT.read_bytes()==output,'radio config chain exact ledger replay')
    print('PASS:fivecompleteconfigbodies/pointerpublications/49MMIOstorelocations;conditionalstate1totailprefixRFcallcut;exactledger')
    print('PASS:NO target execution;RFcall/remainingtail/controlrestore/actualhardware/installedbinding/lifetime UNPROVED')


if __name__=='__main__':main()
