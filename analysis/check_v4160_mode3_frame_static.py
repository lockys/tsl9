"""Complete mode3 callee structure and conditional frame preservation, offline.

No target instructions, signed division, frame, polling or MMIO are run.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_config_precallees_static as previous
import check_v4160_service_provider_link_static as service
import check_v4160_ram_callback_loop_static as graphs

init,sparse,check=previous.init,previous.sparse,previous.check
OUT=Path(__file__).with_name('v4160-mode3-frame-static.json')
PC=0x1929a
END=0x196c4
HASH='0b79dfccf11a0f49b7d234d0efdd318c2d564ff95e4d8711c12aee0fb963a236'
CALLS=(0x19382,0x1938a,0x1949a,0x194a0,0x195d6,0x195dc)
SAVED=((1,76),(8,72),(9,68),(18,64),(19,60),(20,56),(21,52),(22,48),
 (23,44),(24,40),(25,36),(26,32),(27,28))


def decode(raw,pc):
    n={};off=0
    while off<len(raw):
        h=int.from_bytes(raw[off:off+2],'little');size=4 if h&3==3 else 2
        check(off+size<=len(raw),'mode3 whole instruction');chunk=raw[off:off+size];w=int.from_bytes(chunk,'little');p=pc+off
        if size==4 and w&0xfe00707f==0x02004033:
            d=dict(pc=p,size=4,bytes=chunk.hex(),op='div',rd=w>>7&31,rs1=w>>15&31,rs2=w>>20&31)
        elif size==2 and h&0xfc03==0x8401:
            r=8+(h>>7&7);d=dict(pc=p,size=2,bytes=chunk.hex(),op='srai',rd=r,rs1=r,imm=h>>2&31)
        else:d=previous.decode(chunk,p)[p]
        n[p]=d;off+=size
    return n


def cfg(n):
    edges={}
    for p,d in n.items():
        op=d['op']
        if op=='jr':check(d['rs1']==1,'mode3 RET register');q=[]
        elif op=='jump':q=[d['target']]
        elif op in ('beq','bne','beqz','bnez','bge','blt','bgeu','bltu'):q=[p+d['size'],d['target']]
        else:q=[p+d['size']]
        check(all(v in n for v in q),'mode3 CFG no cuts');edges[p]=q
    return edges


def reaching(n,edges,pc,reg,reader_defs):
    """Backward may-reaching-definition census, no register-value execution."""
    pred={p:[] for p in n}
    for p,qs in edges.items():
        for q in qs:pred[q].append(p)
    pending=list(pred[pc]);seen=set();origins=set()
    while pending:
        p=pending.pop()
        if p in seen:continue
        seen.add(p);d=n[p]
        if d.get('rd')==reg or p in CALLS and reg in reader_defs:origins.add(p)
        elif p==PC:origins.add('entry')
        else:pending.extend(pred[p])
    if pc==PC:origins.add('entry')
    return origins


BRANCHES=((0x19346,'bge',14,0,0x1933e),(0x19390,'beq',10,15,0x19388),
 (0x193a8,'blt',15,0,0x193a0),(0x193b4,'bge',14,0,0x193ac),
 (0x193ce,'bge',18,14,0x193d6),(0x193d2,'blt',14,19,0x19406),
 (0x193dc,'beq',26,0,0x19406),(0x193e8,'bge',0,14,0x19402),
 (0x19462,'bge',14,0,0x19456),(0x194a4,'beq',10,18,0x194a0),
 (0x194c4,'blt',15,0,0x194bc),(0x194d4,'bge',14,0,0x194cc),
 (0x19524,'bge',0,14,0x196bc),(0x1959e,'bge',14,0,0x19592),
 (0x195e0,'beq',10,19,0x195dc),(0x19600,'blt',15,0,0x195f8),
 (0x19610,'bge',14,0,0x19608),(0x1967e,'bge',0,18,0x196c0))
JUMPS=((0x19400,0x19316),(0x19404,0x193ee),(0x196be,0x1952a),(0x196c2,0x19684))
ROOTS=((0x192de,15),(0x192f6,25),(0x19406,15),(0x19452,13),(0x194a8,15),
 (0x194b8,14),(0x194c8,13),(0x19530,14),(0x1958e,13),(0x195e4,15),
 (0x195f4,14),(0x19604,13),(0x196a4,14))
DIVS=((0x192cc,22,8,22),(0x1930a,18,8,18),(0x1930e,19,8,19),(0x19312,20,8,20),
 (0x193e4,15,15,20),(0x193f2,15,15,24),(0x194ec,18,8,18),(0x19502,8,8,15),
 (0x19518,13,13,12),(0x19520,15,15,13),(0x1952c,15,15,14),(0x19646,18,18,15),
 (0x1965c,9,9,14),(0x19672,8,8,14),(0x1967a,15,15,8),(0x196a0,15,15,14))
SRAIS=((0x19344,14),(0x193a6,15),(0x193b2,14),(0x19460,14),(0x194c2,15),
 (0x194d2,14),(0x1959c,14),(0x195fe,15),(0x1960e,14))
STORES=(
 (0x192a0,2,8,72,4),(0x192a4,2,18,64,4),(0x192a6,2,19,60,4),(0x192a8,2,20,56,4),
 (0x192aa,2,21,52,4),(0x192ba,2,22,48,4),(0x192d0,2,9,68,4),(0x192d2,2,23,44,4),
 (0x192d4,2,24,40,4),(0x192d6,2,25,36,4),(0x192d8,2,26,32,4),(0x192da,2,27,28,4),
 (0x192dc,2,1,76,4),(0x192ee,15,14,73,1),(0x19300,15,14,73,1),
 (0x1931e,25,14,79,1),(0x1932a,25,14,76,2),(0x1933a,25,14,76,2),
 (0x19356,25,14,79,1),(0x19362,25,14,79,1),(0x1936e,25,14,76,2),
 (0x1937e,25,14,76,2),(0x19388,2,15,12,4),(0x1939c,25,15,76,2),(0x193fc,25,15,54,2),
 (0x19414,15,14,73,1),(0x19420,15,14,73,1),(0x1942c,15,14,79,1),(0x19438,15,14,79,1),
 (0x19442,15,14,76,2),(0x1944e,15,14,76,2),(0x19472,13,14,79,1),(0x1947e,13,14,79,1),
 (0x1948a,15,14,32,2),(0x19496,15,14,32,2),(0x194b4,15,14,76,2),
 (0x19540,14,15,54,2),(0x1954e,14,15,73,1),(0x1955c,14,15,73,1),(0x19568,14,15,79,1),
 (0x19574,14,15,79,1),(0x1957e,14,15,76,2),(0x1958a,14,15,76,2),
 (0x195ae,13,14,79,1),(0x195ba,13,14,79,1),(0x195c6,15,14,32,2),
 (0x195d2,15,14,32,2),(0x195f0,15,14,76,2),(0x19620,13,14,79,1),(0x196b4,14,15,54,2))


def body(raw,reader_defs):
    n=decode(raw,PC)
    # Independent operand guards for every store/control edge/frame field and
    # address origin. Uninterpreted arithmetic is retained by whole-byte identity.
    for p,b,r,v,w in STORES:init.g(n,p,'mode3 store operand '+hex(p),op='store',rs1=b,rs2=r,imm=v,width=w)
    check([p for p,d in n.items() if d['op']=='store']==[x[0] for x in STORES],'mode3 complete store census')
    for p,op,a,b,t in BRANCHES:init.g(n,p,'mode3 branch operand '+hex(p),op=op,rs1=a,rs2=b,target=t)
    for p,t in JUMPS:init.g(n,p,'mode3 jump operand '+hex(p),op='jump',target=t)
    check({p for p,d in n.items() if d['op'] in ('beq','bne','beqz','bnez','bge','blt','bgeu','bltu','jump')}==
        {x[0] for x in BRANCHES+JUMPS},'mode3 full branch census')
    for p in CALLS:init.g(n,p,'mode3 call operand '+hex(p),op='jal',rd=1,target=0x191c6)
    check([p for p,d in n.items() if d['op'] in ('jal','jalr','call_indirect')]==list(CALLS),'mode3 complete call census')
    for p,r in ROOTS:init.g(n,p,'mode3 origin operand '+hex(p),op='lui',rd=r,imm=0x40022000)
    for p,r,a,b in DIVS:init.g(n,p,'mode3 DIV operand '+hex(p),op='div',rd=r,rs1=a,rs2=b)
    check([p for p,d in n.items() if d['op']=='div']==[x[0] for x in DIVS],'mode3 signed DIV census')
    for p,r in SRAIS:init.g(n,p,'mode3 SRAI operand '+hex(p),op='srai',rd=r,rs1=r,imm=16)
    check([p for p,d in n.items() if d['op']=='srai']==[x[0] for x in SRAIS],'mode3 sign extension census')
    special={PC:dict(op='addi',rd=2,rs1=2,imm=-80),
        0x1929c:dict(op='addi',rd=15,rs1=3,imm=108),0x192a2:dict(op='load',rd=8,rs1=15,imm=0,width=4),
        0x192e6:dict(op='mv',rd=9,rs2=10),0x192e8:dict(op='li',rd=26,imm=4),
        0x193d6:dict(op='addi',rd=26,rs1=26,imm=-1),0x193d8:dict(op='andi',rd=26,rs1=26,imm=255),
        0x1945a:dict(op='addi',rd=15,rs1=13,imm=44),0x19596:dict(op='addi',rd=15,rs1=13,imm=44),
        0x19556:dict(op='or',rd=15,rs1=15,rs2=9),0x196b8:dict(op='addi',rd=2,rs1=2,imm=80),
        0x196ba:dict(op='jr',rs1=1)}
    for p,f in special.items():init.g(n,p,'mode3 special operand '+hex(p),**f)
    for j,(r,off) in enumerate(SAVED):init.g(n,0x19686+2*j,'mode3 restore operand '+hex(r),op='load',rd=r,rs1=2,imm=off,width=4)
    init.g(n,0x1938e,'mode3 scratch reload',op='load',rd=15,rs1=2,imm=12,width=4)
    check({(d['rs2'],d['imm'],d['width']) for d in n.values() if d['op']=='store' and d['rs1']==2}==
        {(r,o,4) for r,o in SAVED}|{(15,12,4)},'mode3 frame store set')
    check({(d['rd'],d['imm'],d['width']) for d in n.values() if d['op']=='load' and d['rs1']==2}==
        {(r,o,4) for r,o in SAVED}|{(15,12,4)},'mode3 frame load set')
    check([p for p,d in n.items() if d.get('rd')==2]==[PC,0x196b8],'mode3 only SP definitions')
    check(not any(d.get('rd')==3 for d in n.values()),'mode3 GP never defined')
    # Standard unsigned-load funct3 pins are separate from width-only decoding.
    for d in n.values():
        if d['op']=='load' and d['size']==4:
            w=int(d['bytes'][6:8]+d['bytes'][4:6]+d['bytes'][2:4]+d['bytes'][0:2],16)
            check((w>>12&7)=={1:4,2:5,4:2}[d['width']],'mode3 unsigned load encoding')
    e=cfg(n);seen=set();pending=[PC]
    while pending:
        p=pending.pop()
        if p in seen:continue
        seen.add(p);pending.extend(e[p])
    check(seen==set(n) and [p for p,qs in e.items() if not qs]==[0x196ba],'mode3 whole local reachability/sole RET')
    cycles=[c for c in graphs.components(e) if len(c)>1 or c[0] in e[c[0]]]
    check([(c[0],len(c),c[-1]) for c in cycles]==[(0x19316,71,0x19404),(0x19456,5,0x19462),
        (0x194a0,2,0x194a4),(0x194bc,4,0x194c4),(0x194cc,4,0x194d4),
        (0x19592,5,0x1959e),(0x195dc,2,0x195e0),(0x195f8,4,0x19600),(0x19608,4,0x19610)],'mode3 exact nine SCCs')
    check(set(reader_defs)=={10,11,12,13,14,15},'mode3 exact reused reader definitions')
    # Backward reaching definitions resolve every memory base across branches,
    # loops and reader call clobbers. This is a graph proof, not a CPU run.
    roots={p for p,r in ROOTS};memory=[]
    for p,d in n.items():
        if d['op'] not in ('load','store'):continue
        origins=reaching(n,e,p,d['rs1'],reader_defs);check(len(origins)==1,'mode3 unique memory origin '+hex(p));origin=next(iter(origins))
        if d['rs1']==2:
            check(origin==PC and 0<=d['imm'] and d['imm']+d['width']<=80,'mode3 stack origin/extent')
            address='entrySP'+str(d['imm']-80)
        elif p==0x192a2:
            check(origin==0x1929c and d['op']=='load','mode3 GP-relative read only');address='entryGP+108'
        else:
            base=0x40022000
            if origin in (0x1945a,0x19596):
                source=0x19452 if origin==0x1945a else 0x1958e
                check(reaching(n,e,origin,13,reader_defs)=={source},'mode3 derived base reaching definition');base+=44
            else:check(origin in roots and n[origin]['rd']==d['rs1'],'mode3 constant memory root '+hex(p))
            address=base+d['imm'];check((address,d['width']) in {(0x40022036,2),(0x40022049,1),(0x4002204c,2),(0x4002204e,1),(0x4002204f,1)},'mode3 exact MMIO address/width')
        memory.append({'pc':hex(p),'op':d['op'],'width':d['width'],'base_register':d['rs1'],'unique_reaching_definition':hex(origin),'address':hex(address) if isinstance(address,int) else address})
    check(len(memory)==119 and sum(x['op']=='store' and x['address'].startswith('0x') for x in memory)==36,'mode3 complete memory/store classification')
    # Every restore is dominated by its matching save; no alternate frame release.
    def reaches(start,target,avoid):
        visited=set();todo=[start]
        while todo:
            p=todo.pop()
            if p==avoid or p in visited:continue
            if p==target:return True
            visited.add(p);todo.extend(e[p])
        return False
    for j,(reg,off) in enumerate(SAVED):
        save=next(p for p,d in n.items() if d['op']=='store' and d['rs1']==2 and d['rs2']==reg and d['imm']==off)
        check(not reaches(PC,0x19686+2*j,save),'mode3 save dominates restore')
        restore=0x19686+2*j
        check(not reaches(PC,0x196ba,restore) and reaching(n,e,0x196ba,reg,reader_defs)=={restore},'mode3 restore dominates RET and is final definition')
    check(reaching(n,e,0x196ba,3,reader_defs)=={'entry'},'mode3 GP preserved through return')
    check([p for p,d in n.items() if d.get('rd')==26]==[0x192e8,0x193d6,0x193d8,0x1969c],'mode3 counter definition census')
    check(not reaches(PC,0x19316,0x192e8),'mode3 counter initialization dominates outer entry')
    for gate in (0x193d6,0x193d8,0x193dc):check(not reaches(0x19316,0x19400,gate),'mode3 every outer retry crosses decrement/zero guard')
    check(reaching(n,e,0x19556,9,reader_defs)=={0x192e6},'mode3 mode argument reaches OR')
    check(reaching(n,e,0x192e6,10,reader_defs)=={'entry'},'mode3 entry A0 reaches saved mode')
    check(len(raw)==1066 and len(n)==329 and sha256(raw).hexdigest()==HASH,'mode3 exact whole body identity')
    return {'start':hex(PC),'end_exclusive':hex(END),'bytes':len(raw),'sha256':HASH,'instructions':list(n.values()),
        'conditional_normal_return_CFG':{hex(p):[hex(q) for q in qs] for p,qs in e.items()},
        'calls':[{'pc':hex(p),'target':'0x191c6','link':hex(p+4)} for p in CALLS],
        'cyclic_SCCs':[[hex(p) for p in c] for c in cycles],'memory_accesses_with_origin_proofs':memory,
        'saved_fields':[{'register':r,'child_SP_offset':o} for r,o in SAVED],
        'signed_DIV_PCs':[hex(p) for p,r,a,b in DIVS],
        'complete_function_bytes_CFG_and_memory_classification':True,'complete_arithmetic_or_hardware_semantics':False}


def derive(app,carriers,header,coverage):
    parent=previous.derive(app,carriers,header,coverage)
    reader=service.body(app[0x191c6-0x8000:0x19220-0x8000],'reader',0x191c6,service.APP_HASHES[1])
    rn={d['pc']:d for d in reader['instructions']}
    reader_defs=sorted({d['rd'] for d in rn.values() if d.get('rd',0)})
    check(not reader['calls'] and not any(d['op']=='store' for d in rn.values()),'mode3 reused reader no calls/stores')
    b=body(app[PC-0x8000:END-0x8000],reader_defs)
    mode=previous.previous.body(app[0x197b8-0x8000:0x197be-0x8000],'mode_tail')
    check(parent['remaining_constructor_site']=={'pc':'0x19ba8','target':'0x197b8'} and
        mode['external_tails']==[{'pc':'0x197ba','target':'0x1929a','link_written':False}],'mode3 last constructor call/tail joins')
    return {'schema':'TSL9-mode3-frame-static-v1','profile':parent['profile'],'APP_sha256':sha256(app).hexdigest(),
        'scope':'complete1066B/329instruction mode callee structure;50stores/119memoryaccesses; reused90B reader and6B mode3 wrapper, not counted as newcode',
        'mode_callee':b,'reused_reader':{'start':reader['start'],'bytes':90,'sha256':reader['sha256'],'encoded_GPR_definitions':reader_defs},
        'mode3_join':'constructor19ba8 JAL197b8 setsRA19bac; LI A0=3 thenJALX0 1929a preserveslink; completecallee ordinaryRET returns19bac ifsavedRA/contextvalid',
        'input_source':'fresh U32[entryGP+108] once at192a2; interpreted by16signedDIV instructions; actualvalue, arithmeticunits/results/divisorconditions unproved',
        'memory_contract':'13savedRA/S0..S11 wordstores and1scratchwordstore, allinside80B childframe;36MMIOstores only byte40022049/4002204f andhalfword4002204c/40022036; noGP/variableinput-pointer store',
        'memory_proof':'all119memorybases have unique backward-reaching definitions acrossfullCFG andsixcallclobbers;13LUI roots fixed40022000,2derivedA5roots add44; otherdataread is entryGP+108',
        'derived_base_detail':'1945a/19596 A5=4002202c; laterSH[A5+32] is4002204c evenafterA3becomesmaskconstant',
        'frame_contract':'entrySP=C; savewords C-52..C-1 andscratch C-68..C-65; disjointcallerconfig C..C+15 andcallerRA C+28..C+31; RA/S0..S11 restoredbeforeSP+=80/RET; GPnotdefined',
        'mode_argument':'entryA0 reachesS1 unchanged; S1 stillreachesOR19556 afterfreshbyte-read; mode3 makesORoperand3, not proof of finalhardwarefield or coherentRMW',
        'outer_retry_bound':'S10initialized4; everyretry19400->19316 crossesdecrement,AND255,andzeroexitguard; only3retryedges/4passes possible ifinnerpolls/readercallsprogress andnointerference; doesnotboundinnerwaits',
        'polling_contract':'ninecyclicSCCs incl71nodeouterregion; repeatedfreshbit15 polls andreaderreply-equalitywaits have no localtimeout; readerhasfourretryloops ofitsown; noeventualreturn/time guarantee',
        'combined_config_preservation':'withfirst12callsitecontracts andmode3matchingcode/validframe/MMIO/noalias/noexternalinterference, all13pre-provider sites preserveconstructorconfig16B andrequiredRA/SP/S/GP onnormalreturn; byte12zero canreachpost-callconstruction and40074call',
        'provider_boundary':'fresh40074target andoptionalhook maystillchangeframe/input/config; preservedzeroatAPPcall doesnotproveposthookgates/copy/output orinstalledprovideridentity',
        'premises':['exactAPP/candidate/inputsourceidentities andconditionalISA inclsignedDIV/C.SRAI interpretation; actualcode/reader contentpreserved',
            'allinstruction/data/MMIOaccesses complete normally; callee/reader loops mustfinish forreturnstatement; nofaultortrap guarantee inferred',
            'childsavedwords/callerframe/code physically distinct fromMMIOsideeffects; noDMA/interrupt/reentry/externalwriter/GPRinterference',
            'savedfieldformat/restore instructions prove localusage only, not externalpointerretention or objectlifetime',
            'signedDIV recordedwithsignedoperands only; noPython/C quotient emulates target, no fullcalibration arithmetic orphysicalsuccess claim'],
        'remaining':['actual providerbinding/slotwriters andoptionalhook/registrationeffects','sourceU32[GP+108] writers/relations and signedarithmeticcontract',
            'MMIOphysicaleffects/progress, externalwriters andframe/payloadlifetime','otherarithmetichelperdomains'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(app):
    # Frame offsets and bit interpretation are integer sets/equalities only.
    writes=set(range(-68,-64))|set(range(-52,0));caller=set(range(16))|set(range(28,32))
    check(len(writes)==56 and not writes&caller,'mode3 child/caller disjoint offset sets')
    for h in range(65536):
        signed=h if h<32768 else h-65536
        check((signed<0)==bool(h&0x8000),'mode3 signed-halfword predicate')
    check([((4-k)&255) for k in range(1,5)]==[3,2,1,0],'mode3 fourpass ranking constants')
    raw=app[PC-0x8000:END-0x8000];nodes=decode(raw,PC);count=0
    points=[x[0] for x in STORES+BRANCHES+JUMPS+ROOTS+DIVS+SRAIS]+list(CALLS)+[0x19686+2*j for j in range(13)]+[PC,0x192e6,0x192e8,0x193d6,0x193d8,0x1945a,0x19596,0x196b8,0x196ba]
    check(len(points)==len(set(points)),'mode3 mutation points unique')
    for p in points:
        d=nodes[p];at=p-PC;w=d['size'];b=bytearray(raw);flip=1<<20 if w==4 else 4
        b[at:at+w]=(int.from_bytes(b[at:at+w],'little')^flip).to_bytes(w,'little')
        try:body(b,{10,11,12,13,14,15})
        except RuntimeError as e:check(str(e).startswith(('mode3 store operand ','mode3 branch operand ','mode3 jump operand ',
            'mode3 origin operand ','mode3 DIV operand ','mode3 SRAI operand ','mode3 call operand ',
            'mode3 restore operand ','mode3 special operand ')),'specific mode3 mutation guard '+str(e))
        else:raise RuntimeError('mode3 operand mutation escaped')
        count+=1
    check(count==138,'mode3 mutation census')
    # Regression vector distinguishes DIV from DIVU, without evaluating either.
    signed_word=0x03644b33
    ds=decode(signed_word.to_bytes(4,'little'),0)[0]
    du=decode((signed_word^(1<<12)).to_bytes(4,'little'),0)[0]
    check((ds['op'],ds['rd'],ds['rs1'],ds['rs2'])==('div',22,8,22) and du['op']=='divu','signed/unsigned DIV decode separation')
    print('PASS:65536 sign-bit identities; frame-offset/4pass ranking algebra;138 specified operand mutations rejected; DIV/DIVU decode separation')


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
    else:check(OUT.read_bytes()==output,'mode3 exact ledger replay')
    print('PASS:whole1066B/329node CFG;50stores/119memory-origin proofs;6readerjoins/9SCCs/13framefields; exact ledger')
    print('PASS:NO target execution; signedarithmetic/MMIOprogress/optionalhook/installedprovider/lifetime UNPROVED')


if __name__=='__main__':main()
