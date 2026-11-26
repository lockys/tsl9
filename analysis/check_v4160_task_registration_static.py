"""Complete candidate task registration and conditional hook-write exclusion.

Original operands/CFG plus host integer/interval algebra. No target ISA,
registration table, mutable memory, callback, provider or device execution.
"""
import argparse
import json
import re
from hashlib import sha256
from pathlib import Path
import check_v4160_optional_hook_origin_static as previous
import check_v4160_app_config_source_static as app_source
import check_v4160_post_config_static as post

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-task-registration-static.json')
MASK=0xffffffff
DETAILS=((0x43c4e,412,452,'be96828519d6ea00886e75e0bc515e41b4c44f1731cb5b7dcf1db6a0fdcf12e1'),
 (0x43cda,492,532,'f3ba68eb31ec8f03ec9ac9125f190aa0e903953b96b8dda2673b457e0a98d2bd'))


def specs(pc,index):
    _,ctx,table,_=DETAILS[index]
    return {
        pc:dict(op='lui',rd=14,imm=0x20003000),
        pc+4:dict(op='addi',rd=14,rs1=14,imm=ctx),
        pc+8:dict(op='load',rd=15,rs1=14,imm=1,width=1,mnemonic='qk.c.lbu'),
        pc+10:dict(op='load',rd=13,rs1=14,imm=2,width=1,mnemonic='qk.c.lbu'),
        pc+12:dict(op='bgeu',rs1=15,rs2=13,target=pc+42),
        pc+16:dict(op='lui',rd=13,imm=0x20003000),
        pc+20:dict(op='load',rd=13,rs1=13,imm=table,width=4),
        pc+24:dict(op='addi',rd=12,rs1=15,imm=1),
        pc+28:dict(op='store',rs2=12,rs1=14,imm=1,width=1,mnemonic='qk.c.sb'),
        pc+30:dict(op='slli',rd=14,rs1=15,imm=2),
        pc+34:dict(op='add',rd=14,rs1=14,rs2=13),
        pc+36:dict(op='store',rs2=10,rs1=14,imm=0,width=4),
        pc+38:dict(op='mv',rd=10,rs2=15),pc+40:dict(op='jr',rs1=1),
        pc+42:dict(op='addi',rd=15,rs1=0,imm=255),pc+46:dict(op='jump',target=pc+38)}


def body(raw,index):
    pc,ctx,table,digest=DETAILS[index];n=decode(raw,pc);s=specs(pc,index)
    check(set(n)==set(s),'registration complete boundaries')
    for p,f in s.items():init.g(n,p,'registration operand '+hex(p-pc),**f)
    edges={}
    for p,d in n.items():
        if d['op']=='jr':q=[]
        elif d['op']=='jump':q=[d['target']]
        elif d['op']=='bgeu':q=[p+d['size'],d['target']]
        else:q=[p+d['size']]
        check(all(v in n for v in q),'registration CFG no cuts');edges[p]=q
    seen=set();active=set()
    def visit(p):
        check(p not in active,'registration no local cycle')
        if p in seen:return
        seen.add(p);active.add(p)
        for q in edges[p]:visit(q)
        active.remove(p)
    visit(pc);check(seen==set(n),'registration all nodes locally reachable')
    check([p for p,d in n.items() if d['op']=='store']==[pc+28,pc+36],'registration exact two-store census')
    check(sorted({d['rd'] for d in n.values() if d.get('rd',0)})==[10,12,13,14,15],'registration exact GPR definitions')
    check(not any(d['op'] in ('jal','jalr','call_indirect','fence.i','csr') for d in n.values()),'registration leaf no calls/privileged operations')
    check([p for p,q in edges.items() if not q]==[pc+40],'registration sole RET')
    # Rejection jumps directly to the shared reply/RET and skips both stores.
    check(edges[pc+12]==[pc+16,pc+42] and edges[pc+42]==[pc+46] and edges[pc+46]==[pc+38] and edges[pc+38]==[pc+40],'registration rejection edges')
    check((len(raw),len(n),sha256(raw).hexdigest())==(48,16,digest),'registration whole identity')
    return {'start':hex(pc),'end_exclusive':hex(pc+48),'bytes':48,'sha256':digest,'instructions':list(n.values()),
        'conditional_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},
        'context_base':hex(0x20003000+ctx),'count_byte':hex(0x20003000+ctx+1),
        'capacity_byte':hex(0x20003000+ctx+2),'table_pointer_word':hex(0x20003000+table),
        'encoded_GPR_definitions':[10,12,13,14,15],'no_local_frame_or_nested_calls':True,'complete_function':True}


def derive(app,carriers,header,coverage):
    parent=previous.derive(app,carriers,header,coverage)
    wrapper=app_source.body(app[0x19b16-0x8000:0x19b56-0x8000],'wrapper')
    wn={d['pc']:d for d in wrapper['instructions']}
    init.g(wn,0x19b1e,'registration APP slot load',op='load',rd=15,rs1=9,imm=128,width=4)
    init.g(wn,0x19b26,'registration APP callback high',op='auipc',rd=10,imm=0)
    init.g(wn,0x19b2a,'registration APP callback low',op='addi',rd=10,rs1=10,imm=-458)
    check(0x19b26-458==0x1995c and wrapper['calls'][0]['pc']=='0x19b2e','registration APP callback/call projection')
    check(wn[0x19b34]['op']=='store' and wn[0x19b34]['width']==1 and
        wrapper['calls'][1]['pc']=='0x19b38' and wrapper['calls'][1]['target']=='0x19b56','registration reply byte/constructor join')
    check(wrapper['external_tails'][0]['pc']=='0x19b54','registration APP tail join')
    m=re.search(rb'^\s*#define\s+TMOS_ProcessEventRegister\s+[^\r\n]*BLE_LIB_JT\(\s*19\s*\)',header,re.M)
    check(m is not None and 0x40034+19*4==0x40080,'registration fixed SDK alias JT19')
    post_profiles=post.derive(app,carriers,header)['profiles'];profiles=[]
    for i,(data,detail,pp,prior) in enumerate(zip(carriers,DETAILS,post_profiles,parent['profiles'])):
        pc,ctx,table,h=detail;b=body(init.binding.take(data,pc,48),i)
        check(init.binding.word(data,0x40080)==pc,'registration candidate40080 word')
        hook=int(prior['hook_word'],16);context=int(b['context_base'],16)
        check(hook==context+128 and int(b['table_pointer_word'],16)==context+40,'registration context/table/hook geometry')
        check(previous.separated(int(b['count_byte'],16),1,hook,4),'registration direct count store excludes hook')
        check(pp['table_slot']==b['table_pointer_word'] and pp['capacity_byte']==b['capacity_byte'] and pp['count_byte']==b['count_byte'],'registration post-init table/capacity/count source joins')
        pn={d['pc']:d for d in pp['instructions']};postpc=int(pp['target'],16)
        init.g(pn,postpc+174,'registration post-init table offset',op='addi',rd=15,rs1=15,imm=576)
        init.g(pn,postpc+180,'registration post-init table pointer store',op='store',rs2=15,rs1=9,imm=context+40-0x20003000,width=4)
        profiles.append({'label':init.binding.PROFILES[i][0],'candidate40080':hex(pc),'leaf':b,
            'hook_word':hex(hook),'direct_count_store_disjoint_from_hook':True,
            'post_init_source':{'body_start':pp['target'],'body_sha256':pp['sha256'],
                'table_pointer_store_PC':hex(postpc+180),'table_formula':'T=(fresh P_prime+576) mod2^32',
                'count_byte':pp['count_byte'],'capacity_byte':pp['capacity_byte'],
                'dynamic_table_stores':pp['dynamic_stores']['table_PCs']},
            'unconditional_dynamic_word_exclusion_or_installed_binding_proved':False})
    return {'schema':'TSL9-task-registration-static-v1','profile':parent['profile'],'APP_sha256':sha256(app).hexdigest(),
        'scope':'two complete candidate leaves96B/32instructions; prior64B APPwrapper/post-init/full-source evidence reused',
        'SDK_alias':'fixed header JT19 TMOS_ProcessEventRegister; candidate identity only','profiles':profiles,
        'input_snapshots':'n=freshU8[context+1], c=freshU8[context+2]; separate loads, not coherent snapshot; T=freshU32[context+40] read only after n<c',
        'reject':'if n>=c, setA5=255 thenA0=A5 andRET; no local stores or table load on this path',
        'admit':'if n<c, n0..254; firstSB(n+1) tocontext+1, thenSW entryA0 toD=(T+4*n)mod2^32, thenA0=n andRET; code pointer stored, never invoked here',
        'reply_range':'admission reply0..254, rejection255; n+1<=255 so index/count arithmetic itself does not wrap; valid accesses/code and noexternal interference required',
        'validation_limit':'no local table-null/alignment/extent/provenance or callback-null guard; index<c alone does not establish D/hook disjointness',
        'alias_limit':'later dynamicSW may overlap earliercountbyte, hookword, frame or otherlive data ifT aliases them; finalmemorycount=n+1 requiresnonalias/nointerference, although localreply remains carriedn under validcode/GPRconditions',
        'conditional_exclusion':'if admitted, T=P+576 withoutwrap, R>=576+4*c, nonwrapping block[P,P+R) disjointhookword, and requiredphysicalnonalias/noexternalinterference: dynamic4Bstore liesinsideblock andcannotdirectlytouchhook',
        'post_init_connection':'existingrequestR0=576+6*N0; sufficientlayout premise is c=N0, P_prime=P, tableword preserved and validblockofatleastR0 disjointhook; sourcefreshsnapshots/ownership/equality are not proved here',
        'APP_call':'19b2e fresh40080 withA0=1995c; matchingcandidate localreply low8 storedthroughthen-liveGP+388; no localreplytest beforeconstructor19b38',
        'APP_rejection_flow':'255 reply also storedasbyte thenconstructorcalled; afterconstructorfreshU8[then-liveS0] replacesA0 before40058tail; forwarding255 there requiresbyte/contextpreservation, not fixed byregistrationreply alone',
        'GPR_preservation':'leafdefinesonlyA0/A2/A3/A4/A5; SP/RA/GP/S unchangedlocally; dynamicstoremustnotcorruptcallerframe/code orphysicalaliases forcallerpreservation',
        'remaining':['proveactualtableextent/ownership andP/P_prime/capacitysnapshotequality','post-initdynamicstores/callees andotherhookwriters',
            'actualinstalled40080/400a4/40074bindings','MMIOprogress/asynchronouswriters andframe/payloadlifetime'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    admitted=rejected=0
    for n in range(256):
        for c in range(256):
            if n<c:
                admitted+=1;check(n<=254 and n+1<=255 and 4*n+4<=4*c,'registration admitted byte/index/extent domain')
                check(576+4*n+4<=576+4*c<=576+6*c,'registration request-vs-table extent inequality')
            else:rejected+=1;check(not n<c and n>=c,'registration unsigned reject complement')
    check((admitted,rejected)==(32640,32896),'registration exhaustive snapshot-pair census')
    # Modulo address sets, no table contents, writes or target state.
    for h in (0,4,0x2000321c,0x2000326c,MASK-3):
        hook={(h+j)&MASK for j in range(4)}
        for delta in range(-8,9):
            d=(h+delta)&MASK;word={(d+j)&MASK for j in range(4)}
            overlap=bool(word&hook);check(overlap==(-3<=delta<=3),'registration possible partial-word overlap geometry')
            if not h&3 and not d&3:check(overlap==(d==h),'registration aligned word overlap special case')
    count=0
    for i,(data,detail) in enumerate(zip(carriers,DETAILS)):
        pc=detail[0];raw=init.binding.take(data,pc,48)
        for p,d in decode(raw,pc).items():
            b=bytearray(raw);at=p-pc;w=d['size'];flip=1<<20 if w==4 else 4
            b[at:at+w]=(int.from_bytes(b[at:at+w],'little')^flip).to_bytes(w,'little')
            try:body(b,i)
            except RuntimeError as e:check(str(e).startswith('registration operand '),'specific registration mutation guard '+str(e))
            else:raise RuntimeError('registration mutation escaped')
            count+=1
        b=bytearray(raw);b[12:16]=(int.from_bytes(b[12:16],'little')^(1<<13)).to_bytes(4,'little')
        try:body(b,i)
        except RuntimeError as e:check(str(e).startswith('registration operand '),'registration signedness mutation guard')
        else:raise RuntimeError('registration branch signedness escaped')
        count+=1
    check(count==34,'registration mutation census')
    print('PASS:65536 n/c pairs (32640admit/32896reject); index/request/partial-overlap algebra;34 operand/signedness mutations rejected')


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
    else:check(OUT.read_bytes()==output,'registration exact ledger replay')
    print('PASS:two complete48B/16instruction leaves; fulloperands/CFG/stores/GPR/40080caller/post-initsource joins; exact ledger')
    print('PASS:NO target execution; actualtableextent/aliasexclusion/installedprovider/lifetime UNPROVED')


if __name__=='__main__':main()
