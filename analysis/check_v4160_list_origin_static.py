"""Offline callback writer and list-node creator contracts.

Literal operands/CFG, order and integer/interval certificates only; no target ISA
execution/emulation, register/RAM/list/allocator/fill/provider model.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_request_output_static as previous

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-list-origin-static.json')
PARTS=('installer','creator')
STARTS=((0x55bde,0x5397c),(0x55d1e,0x53a2a))
SIZES=(84,194)
COUNTS=(26,69)
HASHES=(('9ef85054159cc95da5f7e8607cd18f34cc5ba3688a53ab863cb7e76f7e4d1ad7','01e3c45726419fafc78e79a70e764f3813ff117ee2bb89e70b87ca88af522828'),
 ('9f99120d6b47f4e836af410233c8ef64eb9e8170217129db0a128351b9921456','88579abfac39454ad267a315830a80ac069d55342a1e352d94fd5654d28ccf45'))


def specs(part,index):
    pc=STARTS[index][PARTS.index(part)];s={};d=80*index
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def lui(o,r,v=0x20003000):e(o,'lui',rd=r,imm=v)
    def ai(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    def ld(o,r,b,v,w=4):e(o,'load',rd=r,rs1=b,imm=v,width=w)
    def st(o,r,b,v,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    def mv(o,r,b):e(o,'mv',rd=r,rs2=b)
    def call(o,t):e(o,'jal',rd=1,target=t)
    def bz(o,r,t):e(o,'beqz',rs1=r,target=pc+t)
    def bnz(o,r,t):e(o,'bnez',rs1=r,target=pc+t)
    def br(o,op,a,b,t):e(o,op,rs1=a,rs2=b,target=pc+t)
    def j(o,t):e(o,'jump',target=pc+t)
    def ret(o):e(o,'jr',rs1=1)
    if part=='installer':
        lui(0,15);ld(4,15,15,415+d,1);ai(8,2,2,-16);st(10,1,2,12);bnz(12,15,30)
        lui(14,10,0x53000);ai(18,10,10,1324+174*index);call(22,0x43c4e+140*index);call(26,0x5362e+174*index)
        lui(30,15);lui(34,14,0x54000);ai(38,15,15,952+d);ai(42,14,14,-1668+174*index);st(46,14,15,104)
        lui(48,14,0x55000);ai(52,14,14,288+202*index);st(56,14,15,108);lui(58,14,0x56000);ai(62,14,14,-1880+312*index);st(66,14,15,112)
        ld(68,1,2,12);lui(70,14,0x55000);ai(74,14,14,204+202*index);st(78,14,15,116);ai(80,2,2,16);ret(82)
    else:
        ai(0,2,2,-16);st(2,9,2,4);lui(4,9);st(8,1,2,12);st(10,8,2,8);st(12,18,2,0);ai(14,15,9,952+d)
        ld(18,14,15,62,1);ld(22,15,15,63,1);br(26,'bltu',14,15,46);li(30,8,0);mv(32,10,8)
        for o,r,v in ((34,1,12),(36,8,8),(38,9,4),(40,18,0)):ld(o,r,2,v)
        ai(42,2,2,16);ret(44);mv(46,18,10);ai(48,11,0,577);ai(52,10,0,192);e(56,'auipc',rd=1,imm=0x1ffac000);e(60,'jalr',rd=1,rs1=1,imm=1676-174*index)
        mv(64,8,10);bz(66,10,30);ai(68,12,0,192);li(72,11,0);ai(74,9,9,952+d);e(78,'auipc',rd=1,imm=0x1ffad000);e(82,'jalr',rd=1,rs1=1,imm=-1582-174*index)
        br(86,'bne',18,0,94);li(90,15,-16);st(92,15,8,8,1);ld(94,15,9,92);bnz(96,15,176)
        st(98,8,9,88);st(100,8,9,92);st(102,8,9,96);st(104,0,8,0);li(108,15,1);st(110,15,9,62,1)
        li(114,15,1);st(116,15,8,9,1);ai(118,15,0,-112);st(122,15,8,11,1);lui(124,15);ai(128,15,15,1300+d)
        ld(132,14,15,32);ld(134,15,15,36);st(136,14,8,76);st(138,15,8,80);li(140,15,-1);st(142,15,8,22,1);st(144,15,8,125,1)
        ld(148,15,9,74,1);st(152,15,8,180,1);lui(156,15);ld(160,10,15,512+d,1);st(164,10,8,104,1);call(168,0x63966+234*index);st(172,10,8,21,1);j(174,32)
        ld(176,15,9,96);st(178,8,15,0);st(180,8,9,96);st(182,0,8,0);ld(186,15,9,62,1);ai(190,15,15,1);j(192,110)
    return s


def body(raw,part,index):
    k=PARTS.index(part);pc=STARTS[index][k];s=specs(part,index);n=decode(raw,pc)
    check(set(n)==set(s),'origin '+part+' boundaries')
    for p,f in s.items():init.g(n,p,'origin '+part+' operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[k],HASHES[index][k]),'origin '+part+' identity')
    edges={};calls=[]
    for p,d in n.items():
        op=d['op'];q=[p+d['size']]
        if op=='jr':check(d['rs1']==1,'origin RET RA');q=[]
        elif op in ('bnez','beqz','bne','bltu'):q.append(d['target'])
        elif op=='jump':q=[d['target']]
        elif op in ('jal','jalr'):
            if op=='jal':target=d['target']
            else:
                a=n[p-4];check(a['op']=='auipc' and a['rd']==d['rs1'],'origin adjacent PC pair');target=(p-4+a['imm']+d['imm'])&0xfffffffe
            check(d['rd']==1,'origin calllink');calls.append({'pc':hex(p),'target':hex(target)})
        check(all(v in n for v in q),'origin closed '+part+' CFG');edges[p]=q
    done=set();active=set()
    def visit(p):
        check(p not in active,'origin acyclic '+part)
        if p in done:return
        active.add(p)
        for q in edges[p]:visit(q)
        active.remove(p);done.add(p)
    visit(pc);check(done==set(n),'origin all '+part+' nodes locally reachable')
    stores=[(p-pc,v) for p,v in n.items() if v['op']=='store'];check((len(calls),len(stores))==((2,5),(3,22))[k],'origin '+part+' call/store census')
    if part=='installer':check([(o,v['imm']) for o,v in stores if v['rs1']!=2]==[(46,104),(56,108),(66,112),(78,116)],'origin exact four callback writes')
    else:check([o for o,v in stores if v['rs1']==9 and v['imm']==92]==[100],'origin only local head write onfirstnode')
    return {'start':hex(pc),'end_exclusive':hex(pc+SIZES[k]),'bytes':SIZES[k],'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),
            'calls':calls,'store_count':len(stores),'conditional_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},'complete_local_body':True,'local_CFG_acyclic':True}


def certificates(b,part):
    pc=int(b['start'],16);edges={int(p,16):[int(q,16) for q in qs] for p,qs in b['conditional_CFG'].items()}
    if part=='installer':cases={'flag_nonzero_skipsetup':{12:30},'flag0_callssetup':{12:14}}
    else:cases={'count_gate_reject':{26:30},'allocation_null':{26:46,66:30},
        'mode0_headnull':{26:46,66:68,86:90,96:98},'mode_nonzero_headnull':{26:46,66:68,86:94,96:98},
        'mode0_append':{26:46,66:68,86:90,96:176},'mode_nonzero_append':{26:46,66:68,86:94,96:176}}
    paths={name:previous.previous.previous.previous.previous.previous.paths.chain(edges,pc,{pc+p:pc+q for p,q in c.items()}) for name,c in cases.items()}
    for name,path in paths.items():
        offsets=[int(p,16)-pc for p in path]
        if part=='installer':check(all(v in offsets for v in (46,56,66,78)),'origin both installerpaths writeallcallbacks')
        elif name.startswith('mode'):
            publication=100 if name.endswith('headnull') else 178
            check(offsets.index(publication)<offsets.index(116)<offsets.index(172),'origin publication precedes defaults andRoutput')
            check((92 in offsets)==name.startswith('mode0_'),'origin key f0 onlymode0')
    return paths


def domains():
    admitted=0
    for count in range(256):
        for cap in range(256):
            if count<cap:
                admitted+=1;check(count<=254 and count+1<=cap<=255,'origin preserved count increment no wrap')
    check(admitted==32640,'origin capacity bytepair domain')
    increments=[(v+1)&255 for v in range(256)];check(increments[255]==0,'origin fresh count wrap remainspossible without preservation')
    check(192>=108 and all(o+w<=192 for o,w in ((0,4),(8,1),(9,1),(11,1),(21,1),(22,1),(76,4),(80,4),(104,1),(125,1),(180,1))),'origin requested node extent covers validated stores andcore108')
    return {'capacity_byte_pairs':65536,'admitted':admitted,'rejected':65536-admitted,'cap0_admitted':0,
            'stable_count_relation':'if same count survives allocator/fill then admittedcount+1<=cap<=255; no wrap inthatcase',
            'fresh_count_relation':'append reloads count after providers; fresh255 increments tolow8zero unless invariants/preservation exclude it',
            'requested_allocation_bytes':192,'prior_core_required_local_extent':108,'allocation_extent_actually_proved':False}


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[]
    for i,(data,pr) in enumerate(zip(carriers,parent['profiles'])):
        windows={part:body(init.binding.take(data,STARTS[i][k],SIZES[k]),part,i) for k,part in enumerate(PARTS)};paths={part:certificates(b,part) for part,b in windows.items()}
        B=0x200033b8+80*i;ip=STARTS[i][0];cn={v['pc']:v for v in windows['creator']['instructions']};ins={v['pc']:v for v in windows['installer']['instructions']};cp=STARTS[i][1]
        callback_values={}
        for upper,low,store in ((34,42,46),(48,52,56),(58,62,66),(70,74,78)):
            callback_values[str(ins[ip+store]['imm'])]=hex((ins[ip+upper]['imm']+ins[ip+low]['imm'])&0xffffffff)
        check(callback_values['104']==windows['creator']['start'],'origin installedcreator literal matchesfullbody')
        check(pr['lookup']['head_slot']==hex(B+92),'origin creatorhead joins publishedlookup')
        core=previous.previous;cs=core.specs(i);corepc=core.STARTS[i]
        check(cs[corepc+162]['imm']==104 and cs[corepc+164]['imm']==1 and cs[corepc+166]['op']=='call_indirect','origin corecallbackslot andargument1 join')
        check(cs[corepc+178]=={'op':'store','rs2':15,'rs1':10,'imm':8,'width':1},'origin later core key store site')
        check([v['target'] for v in windows['creator']['calls']]==['0x20000040','0x2000039c',pr['bodies']['unsigned_map']['start']],'origin allocator/fill/R exacttargets')
        r=pr['interval_certificates']['unsigned_map'];default_rows=[]
        for code in range(256):
            value=previous.interval_value(r,code);default_rows.append({'sourcebyte':code,'logical_R_reply':value,'node21byte':value&255})
        check(sorted({v['logical_R_reply'] for v in default_rows})==[-18,-10,-5,-3,0,1,2,3,4,5,6,7],'origin exact defaultRbyte domain')
        profiles.append({'label':pr['label'],'bodies':windows,'selected_CFG_paths':paths,
            'installer':{'flag_byte':hex(0x2000319f+80*i),'frame_bytes':16,'saved':['RA'],'zero_flag_optional_calls':[
                {'target':hex(0x43c4e+140*i),'A0':hex(0x5352c+174*i)},
                {'target':hex(0x5362e+174*i),'A0':'inherited firstcall reply; not locally reset'}],
                'nonnull_flag':'skips bothsetupcalls','B':hex(B),'callback_word_values':callback_values,
                'local_order':'all optionalcalls precede four callback stores; no furthercall beforeRET',
                'return':'no fixedsuccessstatus; flag nonzero retainsentryA0 locally, flag0 returnsinherited secondsetupA0',
                'binding_limit':'candidate writer proves value andpoststore order if it runs/returns normally andslots preserved; actual invocation, ordering againstcore andotherwriters unproved'},
            'creator':{'frame_bytes':16,'saved':['RA','S0','S1','S2'],'admission':'freshU8[B62] < freshU8[B63], otherwise return0 withoutallocator',
                'allocation':{'target':'0x20000040','args':[192,0x241],'null':'return0','nonnull':'N savedS0; requirevalid192byte extent/nonalias andcallee preservation'},
                'fill':{'target':'0x2000039c','args':['N',0,192],'output_zeroing_or_retention_proved':False,'reply':'ignored; originalN remainsS0 underpreservation'},
                'key8':'entryA0fullzero ->SBf0toN8; otherentryvalues skiplocalkey8write; zero onlyif actualfilloutputcontract supplies it',
                'first_node':{'guard':'freshU32[B92]==0','write_order':['B88=N','B92=N','B96=N','N.next0=0','B62=1'],
                    'prior_invariant_checked':False},
                'append':{'guard':'freshheadnonzero','write_order':['loadoldtail=U32[B96] withoutnullguard','U32[oldtail0]=N','B96=N','N.next0=0','freshcount=U8[B62]','B62=low8(freshcount+1)'],
                    'head_and_B88_locally_written':False,'tail_validity_or_acyclicity_proved':False},
                'defaults_after_publication':{'N9':1,'N11':'90hex','N76':'freshU32['+hex(0x20003534+80*i)+']','N80':'freshU32['+hex(0x20003538+80*i)+']',
                    'N22_N125':'ff','N180':'freshU8[B74]','N104':'freshU8['+hex(0x20003200+80*i)+']','N21':'R(thefreshN104sourcebyte) low8'},
                'default_R_cases':default_rows,'return':'originalallocatorN, or0 forcountgate/allocationnull; no local free/rollback'},
            'chain_join':{'lookup':'B92head, node0next, node8bytekey match previousfull lookupbody',
                'core_callback':'B104 ->creator if thissettervalue survives untilcorecall; callbackentryA0=1 skipscreatorf0keywrite',
                'key1_order':'creator publishesnode anddefaults first; then corecallbacknonnullpath storesoriginalcoreA0low8@N8; priorpublishedchain supplies1',
                'object_extent':'192 request iscompatiblewithcorelocal108byte extent only ifallocator output valid/retained; existinglookupnodes mayhaveothercreators',
                'global_invariants':'head/count/tail coherence, disjoint freshN, stablecount, validtail, actual chainbound/acyclicity andretainedlifetime notproved'},
            'actual_installed_binding_proved':False,'target_execution_or_emulation':False})
    return {'schema':'TSL9-list-origin-static-v1','profile':parent['profile'],'APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'integer_domains':domains(),
            'scope':'two full84B/26i installers and194B/69i creators;556 originalbytes/190operandguards;16selectedCFGpaths;65536capacitypairs and512defaultRcases',
            'boundary':'validated candidate callback/list writer paths only, not allwriters or actual runtimebinding; optionalsetup, allocator/fill, list coherence andlifetime remain conditional',
            'remaining':['installeractualcallers andoptional43c4e/5362e setup','initialcount/cap/head/tail andotherwriters/removal','actualallocator/fill providers andretention','othercallbacks, enumerators/missingROMpattern'],
            'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    mutations=paths=0
    for i,data in enumerate(carriers):
        for k,part in enumerate(PARTS):
            pc=STARTS[i][k];raw=init.binding.take(data,pc,SIZES[k]);b=body(raw,part,i);paths+=len(certificates(b,part))
            for p,d in decode(raw,pc).items():
                at=p-pc;z=d['size'];buf=bytearray(raw);buf[at:at+z]=(int.from_bytes(buf[at:at+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
                try:body(buf,part,i)
                except RuntimeError as e:check(str(e).startswith('origin '+part+' operand '),'origin specified mutation '+str(e))
                else:raise RuntimeError('origin mutation escaped')
                mutations+=1
    check((mutations,paths)==(190,16),'origin mutation/path census');domains()
    print('PASS:190 operand mutations rejected;556 original bytes;16 CFG certificates;65536 capacity pairs;512 default R cases')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');o=parser.parse_args()
    image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK identity')
    carriers=[]
    for label,folder,tail,z,digest in init.binding.PROFILES:
        data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidate identity '+label);carriers.append(data)
    raw_hex=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
    coverage=sparse.derive(image,carriers,header,raw_hex,sparse.parser());ledger=derive(image,carriers,header,coverage);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers)
    output=(json.dumps(ledger,indent=1,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'origin exact ledger replay')
    print('PASS:callbackwriter-to-creator/core andhead-to-lookup joins;192byte request/publication/key/default ordering;exact ledger')
    print('PASS:NO target execution/emulation;actualbinding/list invariants/allocator/fill/retention UNPROVED')


if __name__=='__main__':main()
