"""401a0 role entry, conditional registration and early gate writer, static.

Original operands/CFGs and bounded field/frame algebra only; no target ISA,
register machine, callback, provider, RAM/frame, fill or MMIO runner.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_timer_start_setup_static as previous
import check_v4160_loaded_hook_sources_static as loaded

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-first-role-gate-static.json')
DETAILS=(
 dict(entry=0x6dd16,primary=0x61b1c,gate=0x55bde,initialize=0x5362e,reg=0x43c4e,ctx=412,base=952,
  handler=0x5352c,setters=(0x55bd4,0x55c48),fill_low=-692,primary_lows=(-1894,-1570,564),gate_lows=(-1668,288,-1880,204),
  outer_lows=(-1038,1460,-2040,692,-948,432),outer_init=(0x4da70,0x46570,0x4a7d6,0x50412,0x6c300,0x4d172),tail=0x6d572,
  hashes=('28f55e63884b9c5def170e1371fb51bd594ec4ece3a8494c67564e868b9d430f','ed21d79f478408a77e4d50d6bff6a7122aad846e9889b8b6dcaad31d5b43b242',
   '9ef85054159cc95da5f7e8607cd18f34cc5ba3688a53ab863cb7e76f7e4d1ad7','d9161c509371f2ef33c33a70810b8ad946caf4fb8109187753bbeb610ba8425c',
   '110abd1425093f24b05eedc3c79e2d2d4203d39f62cd173623dab603c6bb8b1e','ad86c49b580b43e67a9912b9db7cfcf3227b323b00c06ddf5f680186d20bd26d')),
 dict(entry=0x6df06,primary=0x61c06,gate=0x55d1e,initialize=0x536dc,reg=0x43cda,ctx=492,base=1032,
  handler=0x535da,setters=(0x55d14,0x55d88),fill_low=-866,primary_lows=(-1660,-1336,798),gate_lows=(-1494,490,-1568,406),
  outer_lows=(-886,1612,-1888,846,-456,584),outer_init=(0x4db08,0x46608,0x4a86e,0x504ac,0x6c4ec,0x4d20a),tail=0x6d75e,
  hashes=('e431dfe5dd168d6a0876d8a26df7f4180be6a5dfa0a1000cf7602c00d6ae99e7','63c24ba47085e5d747402a9138c9e5257bc408c847e4141bc645df7f87eab093',
   '9f99120d6b47f4e836af410233c8ef64eb9e8170217129db0a128351b9921456','b30defc16c708406db5627076a1d096a583e1d579d87c5a8390fb3fc0c7fc33c',
   'aa3b49eb0981c313d210f2faef5e196bc09d23a89a62c76d8c05cdb174a0c3e6','7b09271385520acd1da75a181cd6b2607f099db4b0a1cc7a4a24ef279c81e781')))
ROLES=('entry','primary','gate','initialize','setter0','setter1')
SIZES=(112,62,84,62,10,10)
COUNTS=(30,18,26,20,3,3)


def specs(role,index):
    d=DETAILS[index];pc=d['setters'][int(role[-1])] if role.startswith('setter') else d[role];s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def lui(o,r,v):e(o,'lui',rd=r,imm=v)
    def addi(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def load(o,r,b,v):e(o,'load',rd=r,rs1=b,imm=v,width=4)
    def store(o,r,b,v,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    def call(o,t):e(o,'jal',rd=1,target=t)
    if role=='entry':
        addi(0,2,2,-16);store(2,1,2,12);call(4,d['primary'])
        for j,upper in enumerate((0x4e000,0x46000,0x4b000,0x50000,0x6d000,0x4d000)):
            o=8+16*j;lui(o,10,upper);addi(o+4,10,10,d['outer_lows'][j]);call(o+8,d['reg']);call(o+12,d['outer_init'][j])
        load(104,1,2,12);addi(106,2,2,16);e(108,'jal',rd=0,target=d['tail'])
    elif role=='primary':
        a,b,c=d['primary_lows'];addi(0,2,2,-16);store(2,1,2,12);call(4,d['gate'])
        lui(8,15,0x20003000);lui(12,14,0x61000);addi(16,15,15,d['base']);addi(20,14,14,a);store(24,14,15,184)
        lui(28,14,0x61000);addi(32,14,14,b);store(36,14,15,188);load(40,1,2,12)
        lui(42,15,0x61000);lui(46,14,0x20003000);addi(50,15,15,c);store(54,15,14,d['base']+324)
        addi(58,2,2,16);e(60,'jr',rs1=1)
    elif role=='gate':
        lui(0,15,0x20003000);e(4,'load',rd=15,rs1=15,imm=d['ctx']+3,width=1)
        addi(8,2,2,-16);store(10,1,2,12);e(12,'bnez',rs1=15,target=pc+30)
        lui(14,10,0x53000);addi(18,10,10,d['handler']-0x53000);call(22,d['reg']);call(26,d['initialize'])
        lui(30,15,0x20003000);lui(34,14,0x54000);addi(38,15,15,d['base']);addi(42,14,14,d['gate_lows'][0]);store(46,14,15,104)
        for o,upper,low,field in ((48,0x55000,d['gate_lows'][1],108),(58,0x56000,d['gate_lows'][2],112),(70,0x55000,d['gate_lows'][3],116)):
            lui(o,14,upper);addi(o+4,14,14,low);store(o+8,14,15,field)
        load(68,1,2,12);addi(80,2,2,16);e(82,'jr',rs1=1)
    elif role=='initialize':
        addi(0,2,2,-16);store(2,9,2,4);lui(4,9,0x20003000);lui(8,15,0x20003000)
        addi(12,12,0,296);e(16,'li',rd=11,imm=0);store(18,8,2,8);e(20,'mv',rd=8,rs2=10)
        addi(22,10,9,d['base']);store(26,1,2,12);store(28,0,15,d['base']+300);store(32,18,2,0)
        e(34,'auipc',rd=1,imm=0x1ffad000);e(38,'jalr',rd=1,rs1=1,imm=d['fill_low'])
        e(42,'li',rd=10,imm=0);call(44,d['setters'][0]);e(48,'li',rd=10,imm=0);call(50,d['setters'][1])
        lui(54,15,0x20003000);store(58,8,15,d['ctx']+3,1)
    else:
        lui(0,15,0x20003000);store(4,10,15,d['base']+296+8*int(role[-1]));e(8,'jr',rs1=1)
    return pc,s


def body(raw,role,index):
    pc,s=specs(role,index);n=decode(raw,pc);j=ROLES.index(role)
    check(set(n)==set(s),'role '+role+' boundaries')
    for p,f in s.items():init.g(n,p,'role '+role+' operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[j],COUNTS[j],DETAILS[index]['hashes'][j]),'role '+role+' identity')
    e={};cuts=[];calls=[]
    for p,d in n.items():
        if d['op']=='jr':q=[]
        elif d['op']=='jal' and d['rd']==0:q=[d['target']]
        elif d['op']=='bnez':q=[p+d['size'],d['target']]
        else:q=[p+d['size']]
        for v in q:
            if v not in n:
                check((role=='entry' and p==pc+108) or (role=='initialize' and v==pc+62),'role explicit cuts only')
                cuts.append({'pc':hex(p),'target':hex(v)})
        e[p]=q
        if d['op'] in ('jal','jalr') and d['rd']==1:calls.append({'pc':hex(p),'target':hex(d['target']) if 'target' in d else '0x2000039c','link':hex(p+d['size'])})
    seen=set();active=set()
    def visit(p):
        check(p not in active,'role local CFG acyclic')
        if p in seen or p not in n:return
        active.add(p);seen.add(p)
        for v in e[p]:visit(v)
        active.remove(p)
    visit(pc);check(seen==set(n),'role all local nodes reachable')
    if role=='initialize':init.pair(n,pc+34,1,0x2000039c,'role initializer fill pair')
    expected_calls={'entry':13,'primary':1,'gate':2,'initialize':3,'setter0':0,'setter1':0}
    check(len(calls)==expected_calls[role],'role exact call census')
    stores=[d for d in n.values() if d['op']=='store']
    check(len(stores)==dict(entry=1,primary=4,gate=5,initialize=6,setter0=1,setter1=1)[role],'role exact store census')
    return {'role':role,'start':hex(pc),'bytes':len(raw),'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),
        'normal_return_CFG':{hex(p):[hex(q) for q in qs] for p,qs in e.items()},'external_cuts':cuts,'calls':calls,
        'complete_function':role!='initialize','transitive_callee_closure_proved':False}


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[]
    # Prior complete setup window pins the actual 401a0 load/call operands.
    check(all(p['second_task']['reply']==4 and p['second_task']['new_count']==5 for p in parent['profiles']),'role prior second-task reply/count join')
    for i,(data,prior,d) in enumerate(zip(carriers,parent['profiles'],DETAILS)):
        bodies={role:body(init.binding.take(data,specs(role,i)[0],size),role,i) for role,size in zip(ROLES,SIZES)}
        check(init.binding.word(data,0x401a0)==d['entry'],'role candidate401a0 slot')
        # The primary publisher was already independently verified in the old chain.
        primary=loaded.body(init.binding.take(data,d['primary'],62),'publish_primary',d['primary'],
            (d['gate'],d['base'],*d['primary_lows'],d['base']+324),d['hashes'][1])
        reg=previous.registration.body(init.binding.take(data,d['reg'],48),i)
        fill=previous.source.fill_contract(init.binding.take(data,(0x4060c,0x4064c)[i],46))
        check(fill['encoded_GPR_writes']==[10,14,15] and reg['no_local_frame_or_nested_calls'],'role fill/registration preserved S/GP/SP/RA contracts')
        ctx=0x20003000+d['ctx'];base=0x20003000+d['base'];tableword=previous.layout.T+20
        check(prior['second_task']['new_count']==5 and int(reg['context_base'],16)==ctx,'role count5/shared context join')
        check(5<14 and tableword==0x20004808 and tableword+4<=previous.layout.T+56,'role next registration footprint')
        gp=d['gate']
        ei={int(p,16):[int(q,16) for q in qs] for p,qs in bodies['gate']['normal_return_CFG'].items()}
        skip=previous.chain(ei,gp,{gp+12:gp+30})
        zero=previous.chain(ei,gp,{gp+12:gp+14},gp+26)
        check(hex(gp+22) not in skip and hex(gp+22) in zero,'role optional registration selected gate paths')
        # Publisher words are data installs, reached only after required calls return.
        gate_words=[{'address':hex(base+off),'value':hex(upper+low)} for off,upper,low in zip((104,108,112,116),(0x54000,0x55000,0x56000,0x55000),d['gate_lows'])]
        primary_words=[{'address':hex(base+184),'value':hex(0x61000+d['primary_lows'][0])},
            {'address':hex(base+188),'value':hex(0x61000+d['primary_lows'][1])},
            {'address':hex(base+324),'value':hex(0x61000+d['primary_lows'][2])}]
        protected=[(ctx+1,1),(ctx+2,1),(ctx+40,4),(previous.layout.T,4*14),(0x20004184,1),(0x200040a6,1),(previous.layout.A+8,16)]
        zero_writes=[(base,296),(base+296,12),(ctx+3,1),(ctx+1,1),(tableword,4)]
        for p,w in zero_writes[:3]:
            for q,z in protected:check(previous.origin.separated(p,w,q,z),'role initializer prefix writes exclude live fields')
        for row in gate_words+primary_words:
            for q,z in protected+[(ctx+3,1)]:check(previous.origin.separated(int(row['address'],16),4,q,z),'role publisher words exclude live metadata')
        check(all(base<=int(row['address'],16) and int(row['address'],16)+4<=base+296 for row in gate_words+primary_words[:2]),'role six later publisher slots are inside earlier clear')
        outer=[]
        for j,upper in enumerate((0x4e000,0x46000,0x4b000,0x50000,0x6d000,0x4d000)):
            outer.append({'registration_PC':hex(d['entry']+16+16*j),'handler':hex(upper+d['outer_lows'][j]),'next_initializer':hex(d['outer_init'][j]),'actual_ID_proved':False})
        profiles.append({'label':prior['label'],'bodies':bodies,'gate_byte':hex(ctx+3),'count_byte':hex(ctx+1),
            'gate_zero_selected_prefix':zero,'gate_nonzero_selected_path':skip,'gate_publisher_words':gate_words,'primary_publisher_words':primary_words,
            'zero_case':{'additional_fresh_gate_premise':0,'registration_reply':5,'count_after_registration':6,'entry5_address':hex(tableword),
                'entry5_handler':hex(d['handler']),'initializer_entry':hex(d['initialize']),'initializer_incoming_A0':5,
                'fill_start':hex(base),'fill_bytes':296,'fill_end_exclusive':hex(base+296),'zero_word_stores':[hex(base+296+k) for k in (0,4,8)],
                'gate_write_PC':hex(d['initialize']+58),'gate_after_prefix':5,'S0_after_prefix':5,'prefix_end_exclusive':hex(d['initialize']+62),
                'A0_A1_A2_after_prefix':[0,0,296],'initializer_returns_to_gate_proved':False},
            'nonzero_case':{'additional_fresh_gate_premise':'1..255','extra_gate_registration':False,
                'after_primary_incoming_A0_A1_A2':[4,0,5],'first_outer_registration_reply':5,'count_after_first_outer':6,
                'entry5_address':hex(tableword),'entry5_handler':outer[0]['handler'],
                'cut_before_initializer':outer[0]['next_initializer'],'initializer_incoming_A0_A1_A2':[5,0,6]},
            'remaining_outer_calls':outer,'outer_tail':hex(d['tail']),'primary_reused_sha256':primary['sha256'],'actual_installed_binding_proved':False})
    return {'schema':'TSL9-first-role-gate-static-v1','profile':parent['profile'],'APP_sha256':sha256(image).hexdigest(),
        'scope':'six windows per candidate340B/100instructions; full entry112B, reused primary62B, full gate84B, bounded initializer62B, two10B setters; no new C reconstruction bytes',
        'profiles':profiles,'incoming_arguments':'conditional401a0 entry(4,0,5); neither branch treats4 as fixedtaskID: handler word is formed before eachregistration andfreshcount determinesreply',
        'gate_value_boundary':'fresh U8[ctx+3] is distinct fromcountctx+1 andcapacityctx+2; previous contextclear is a sourcewitness only, no universalwriter census establishes whichbranchactuallyoccurs',
        'zero_branch':'matchingregistration withn5/c>=14/Towned stores5352c/535da intoentry5, incrementscount6, returns5. Initializer prefix saves5 inS0, clears296B, zeros3trailingwords usingtwoleafsetters, writeslow8(S0)=5 back togate; stopswithfourframesstillactive',
        'nonzero_branch':'skip twoinnercalls; gateandprimary publish7codepointerwords andreturn preservingincomingA0/A1/A2 underframes/nointerferencepremises. Firstouterregistration storesitsownhandler atentry5,returns5/count6; stopsbeforefirstouterinitializer',
        'publication_order':'initializerzero fillcoverssixlatergate/primarypublisherwordslots; thosepublishersareafterinitializerreturn, not evidenceofearliercallbackinvocation. No same-path claimthatthosewordstoresalreadyhappenedatzeroprefixcut',
        'frame_projection':'relative401a0entrySP=S: outerRA atS-4,primaryRA atS-20,gateRA atS-36; initializerSP=S-64,localsS2/S1/S0/RAatS-64/-60/-56/-52. Fill/setters are leaf/no frame; zero cut has no restore yet',
        'outer_boundary':'entry has13linkedcalls thenrestoreRA/SP andtail6d572/6d75e, no ordinaryRET or forcedsuccesscode. Sixregistrationindices cannot be fixed until interveninginitializer effects areclosed',
        'premises':'all previous conditional source/metadata/slotconditions, matching401a0andregistration/fill/helpercode; additionalfreshgatevaluepercase; validnonwrappingnonaliasstack/globals/table/timerpayload; preservedcode/contextandnoadverseMMIO/FENCE.I/IRQ/DMA/reentry/externalwriters; requiredlocalcallsreturnnormally',
        'remaining':['rest of5362e/536dc aftergatewrite andreturn/preservation','4da70/4db08 andotherouterinitializers/tail','actualfreshgate/installedproviderprovenance, physicaleffects andlaterlifetimes'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    count=0
    for i,data in enumerate(carriers):
        for role,size in zip(ROLES,SIZES):
            pc=specs(role,i)[0];raw=init.binding.take(data,pc,size)
            for p,d in decode(raw,pc).items():
                at=p-pc;w=d['size'];buf=bytearray(raw);buf[at:at+w]=(int.from_bytes(buf[at:at+w],'little')^(1<<20 if w==4 else 4)).to_bytes(w,'little')
                try:body(buf,role,i)
                except RuntimeError as e:check(str(e).startswith('role '+role+' operand '),'role mutation guard '+str(e))
                else:raise RuntimeError('role mutation escaped')
                count+=1
    check(count==200,'role mutation census')
    for gate in range(256):check((gate==0)==(gate not in range(1,256)),'role exhaustive byte classification')
    for row in previous.layout.facts():check(5<row['N0'] and previous.layout.T+24<=previous.layout.T+4*row['N0'],'role entry5 boundall256 capacities')
    saved=[set(range(-4,0)),set(range(-20,-16)),set(range(-36,-32)),set(range(-64,-48))]
    check(sum(map(len,saved))==len(set().union(*saved))==28,'role fourframe savedwords disjoint')
    for i,d in enumerate(DETAILS):check(d['initialize']+34+0x1ffad000+d['fill_low']==0x2000039c,'role mapped fill target algebra')
    print('PASS:200 role/gate/prefix/setter operand mutations rejected;256 gateclasses/256 capacitycases;fourframe offsets')


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
    else:check(OUT.read_bytes()==output,'first role gate exact ledger replay')
    print('PASS:401a0 entry/gate/registration/fill/setter joins;conditionalreply5/count6 andgatewrite5;two boundedbranchcuts;exactledger')
    print('PASS:NO target execution;actualgate/installedprovider/remaininginitializers/physicaleffects/lifetime UNPROVED')


if __name__=='__main__':main()
