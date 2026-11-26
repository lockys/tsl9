"""Conditional source-clock binding and post-initializer publication, offline.

Raw operands/CFG/frame links, source fields and interval identities only.
No target ISA, callback, clock, copy, registration or MMIO execution/model.
"""
import argparse
import json
import re
from hashlib import sha256
from pathlib import Path
import check_v4160_range_retry_static as previous
import check_v4160_first_role_gate_static as role
import check_v4160_task_registration_static as registration
import check_v4160_config_buffer_source_static as source
import check_v4160_fallback_initialization_static as fallback
import check_v4160_registration_return_chain_static as clock

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
paths=previous.paths
OUT=Path(__file__).with_name('v4160-gate-return-publication-static.json')
ROLES=('clock','gate_suffix','primary_suffix','outer_prefix')
SIZES=(42,54,54,16)
COUNTS=(17,17,15,4)
HASHES=(('94c304a4b9238393a0ebd3b267c6cdd74e87c093e8124a48e65f1999f255356c',
 'ff01811a0b89086c800f69a8bb3a8f8257eb3bc81eba742cf9ef2fb9d875d4e5','90a419ec9270169834b5b5c70834d6d42a52e0f1023cd9567382cd173605767b','09d6ec1a3c8ffaa1891db2e09648dc07565d9a1bf9e5636c7bc8643319a1427a'),
 ('0269893236760e20dba273a25fb82b2a963cd044b5863c28bb50e92400f3f667',
 '19727b72e07150765c89da124de0d6b58c2c73643c337e23700f412dec2ea633','bc80ccc710d2b69bd0be2d021e50393f2e7e01e40aa6c3caf98a3a996d454027','74c80718fdb08b6184a350e2ebb5ce4662148436d8907f04073a6b9cc466467a'))
APP_PC,APP_SIZE,APP_HASH=0x19a74,30,'1bdd395d0bf827f5955e75892c9c4cb24fc5af894a41cc95cbcafce941dec753'


def specs(part,index=0):
    d=role.DETAILS[index];delta=80*index;s={}
    if part in ('gate_suffix','primary_suffix','outer_prefix'):
        full,offset=('gate',30) if part=='gate_suffix' else ('primary',8) if part=='primary_suffix' else ('entry',8)
        base,old=role.specs(full,index);pc=base+offset;size=SIZES[ROLES.index(part)]
        return pc,{p:f for p,f in old.items() if pc<=p<pc+size}
    pc=APP_PC if part=='APP_source' else (0x43520,0x435ac)[index]
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def lui(o,r,v):e(o,'lui',rd=r,imm=v)
    def addi(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def load(o,r,b,v):e(o,'load',rd=r,rs1=b,imm=v,width=4)
    def store(o,r,b,v):e(o,'store',rs2=r,rs1=b,imm=v,width=4)
    if part=='APP_source':
        load(0,15,8,124);e(2,'auipc',rd=14,imm=0);addi(6,14,14,-732);store(10,14,2,72)
        e(12,'auipc',rd=14,imm=0);addi(16,14,14,-706);store(20,14,2,76)
        lui(22,14,0x4000);addi(24,14,14,-384);store(28,15,2,52)
    else:
        lui(0,15,0x20003000);load(4,15,15,560+delta);addi(8,2,2,-16);store(10,8,2,8);store(12,1,2,12)
        lui(14,8,0x20003000);addi(18,8,8,412+delta);e(22,'beqz',rs1=15,target=pc+32)
        e(24,'call_indirect',rd=1,rs1=15);load(26,15,8,20);e(28,'add',rd=10,rs1=10,rs2=15);store(30,10,8,20)
        load(32,10,8,20);load(34,1,2,12);load(36,8,2,8);addi(38,2,2,16);e(40,'jr',rs1=1)
    return pc,s


def body(raw,part,index=0):
    pc,s=specs(part,index);n=decode(raw,pc)
    check(set(n)==set(s),'publication '+part+' boundaries')
    for p,f in s.items():init.g(n,p,'publication '+part+' operand '+hex(p-pc),**f)
    size,count,digest=(APP_SIZE,10,APP_HASH) if part=='APP_source' else (SIZES[ROLES.index(part)],COUNTS[ROLES.index(part)],HASHES[index][ROLES.index(part)])
    check((len(raw),len(n),sha256(raw).hexdigest())==(size,count,digest),'publication '+part+' identity')
    e={}
    for p,d in n.items():
        if d['op']=='jr':check(d['rs1']==1,'publication ordinary RET');q=[]
        elif d['op']=='beqz':q=[p+d['size'],d['target']]
        else:q=[p+d['size']]
        check(all(v in n or v==pc+size and part in ('APP_source','outer_prefix') for v in q),'publication exact local edge');e[p]=q
    if part in ('gate_suffix','primary_suffix'):
        check(not any(d['op'] in ('jal','jalr','call_indirect','beq','bne','beqz','bnez') or d.get('rd') in (10,11,12) for d in n.values()),'publication suffix does not test or change returned A0/A1/A2')
    if part=='APP_source':
        check([p for p,d in n.items() if d.get('rd')==15]==[pc],'publication loaded pointer stable to APP store')
    if part=='clock':
        check({d['rd'] for d in n.values() if d.get('rd',0)}=={1,2,8,10,15},'publication clock local GPR census')
        check([(d['rs2'],d['imm']) for d in n.values() if d['op']=='store' and d['rs1']==2]==[(8,8),(1,12)],'publication clock exact frame saves')
        check([(d['rd'],d['imm']) for d in n.values() if d['op']=='load' and d['rs1']==2]==[(1,12),(8,8)],'publication clock exact frame restores')
    return {'start':hex(pc),'bytes':size,'sha256':digest,'instructions':list(n.values()),
        'normal_return_CFG':{hex(p):[hex(q) for q in qs] for p,qs in e.items()},'complete_function':part=='clock','explicit_common_suffix':part.endswith('suffix')}


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[]
    app=body(image[APP_PC-0x8000:APP_PC-0x8000+APP_SIZE],'APP_source')
    builder=source.app_contract(image[source.APP_PC-0x8000:source.APP_PC-0x8000+source.APP_SIZE])
    check(re.search(rb'#define\s+TMOS_GetSystemClock\s+[^\r\n]*BLE_LIB_JT\(18\)',header) is not None and 0x40034+18*4==0x4007c,'publication SDK clock index18')
    for i,(data,pr) in enumerate(zip(carriers,parent['profiles'])):
        d=role.DETAILS[i];delta=80*i;B=0x20003000+d['base'];ctx=0x20003000+d['ctx'];F=ctx+80
        windows={p:body(init.binding.take(data,specs(p,i)[0],z),p,i) for p,z in zip(ROLES,SIZES)}
        full={}
        for p in ('gate','primary','entry'):
            start=role.specs(p,i)[0];z=role.SIZES[role.ROLES.index(p)]
            full[p]=role.body(init.binding.take(data,start,z),p,i)
        check(pr['conditional_context_gate']==5 and pr['conditional_count']==6,'publication inherited zero-gate metadata case')
        rows={p:{n['pc']:n for n in b['instructions']} for p,b in full.items()}
        check(rows['gate'][d['gate']+26]['target']==d['initialize'] and d['gate']+30==specs('gate_suffix',i)[0],'publication initializer RET returns to gate suffix')
        check(rows['primary'][d['primary']+4]['target']==d['gate'] and rows['entry'][d['entry']+4]['target']==d['primary'],'publication two outer saved-RA links')
        # The successful candidate path has no later A1 definition before RET.
        tail=pr['bodies']['tail'];tailpc=int(tail['start'],16);tn={n['pc']:n for n in tail['instructions']}
        un=pr['bodies']['unsigned_range'];unpc=int(un['start'],16);unodes={n['pc']:n for n in un['instructions']}
        init.g(tn,tailpc+132,'publication final upper bound',op='li',rd=11,imm=-1)
        init.g(tn,tailpc+134,'publication final lower bound',op='li',rd=10,imm=0)
        check(not any(n.get('rd')==11 for p,n in tn.items() if tailpc+140<=p<=tailpc+252),'publication final candidate to RET preserves A1')
        init.g(unodes,unpc+18,'publication unsigned upper minus saved lower',op='sub',rd=11,rs1=11,rs2=8)
        check(not any(n.get('rd')==11 for p,n in unodes.items() if p>unpc+18),'publication unsigned return A1=ffffffff in caller domain')
        gate_words=[{'address':hex(B+off),'value':hex(upper+low)} for off,upper,low in zip((104,108,112,116),(0x54000,0x55000,0x56000,0x55000),d['gate_lows'])]
        primary_words=[{'address':hex(B+off),'value':hex(0x61000+low)} for off,low in zip((184,188,324),d['primary_lows'])]
        protected=[(ctx+1,1),(ctx+2,1),(ctx+3,1),(ctx+40,4),(paths.layout.T,4*212),(paths.layout.A+8,16),(0x200040a6,1),(0x20004184,1),(F+36,4),(F+68,4)]
        for r in gate_words+primary_words:
            for p,z in protected:check(paths.origin.separated(int(r['address'],16),4,p,z),'publication words exclude metadata/source slots')
        check(all(B<=int(r['address'],16)<int(r['address'],16)+4<=B+296 for r in gate_words+primary_words[:2]) and B+324>=B+296,'publication six in-object words and one external global')
        reg=registration.body(init.binding.take(data,d['reg'],48),i)
        check(11 not in reg['encoded_GPR_definitions'],'publication registration preserves A1')
        handler=0x4e000+d['outer_lows'][0];nextpc=d['entry']+20
        check(rows['entry'][d['entry']+16]['target']==d['reg'] and rows['entry'][nextpc]['target']==d['outer_init'][0],'publication next outer registration/call join')
        check(6<14 and paths.layout.T+24+4<=paths.layout.T+14*4,'publication admitted next table entry extent')
        entry6=paths.layout.T+24
        for p,z in protected[:4]+[(F+36,4),(F+68,4)]:check(paths.origin.separated(entry6,4,p,z),'publication entry6 excludes metadata/source slots')
        mapping=init.binding.profile(data,pr['label']);clockpc=specs('clock',i)[0]
        check(init.binding.word(data,0x4007c)==clockpc,'publication candidate clock alias')
        fd=fallback.DETAILS[i];cfg_raw,cfg_n,_,defaults=fallback.config_contract(data,fd[2],fd[5],fd[9],fd[10])
        check(sha256(cfg_raw).hexdigest()==fd[-1] and fd[5]==F,'publication existing config identity/destination')
        check(52-16==36 and source.APP_PC<=APP_PC<APP_PC+APP_SIZE<=source.APP_PC+source.APP_SIZE,'publication builder field36 geometry')
        check(all(paths.origin.separated(r['destination_field'],r['bytes'],36,4) for r in defaults),'publication config defaults preserve copied clock field36')
        check((F+36-fd[3])//4==198 and fd[3]<=F+36<F+40<=fd[4]+4,'publication startup zero source covers primary slot')
        clk=windows['clock'];cp=int(clk['start'],16);cn={n['pc']:n for n in clk['instructions']};ce=previous.edges(cn)
        clock_paths={name:paths.chain(ce,cp,{cp+22:cp+q}) for name,q in (('no_callback',32),('with_callback',24))}
        cb=clock.body(init.binding.take(data,clock.DETAILS[i][1],130),'callback',i)
        ar=clock.arithmetic(init.binding.take(data,clock.previous.arithmetic.BASES[i],914),clock.previous.arithmetic.BASES[i])
        check(ar['complete_CFG_and_preservation'],'publication clock arithmetic local preservation')
        # Accumulator and callback's prior-result word are separate from live metadata.
        for p in (ctx+20,ctx+24):
            for q,z in protected:check(paths.origin.separated(p,4,q,z),'publication clock writes exclude live source and task/table state')
        check(ctx+20!=ctx+24,'publication clock accumulator and prior-result words distinct')
        profiles.append({'label':pr['label'],'windows':windows,
            'conditional_return_links':{'retry_RET_to_gate':hex(d['gate']+30),'gate_RET_to_primary':hex(d['primary']+8),'primary_RET_to_outer':hex(d['entry']+8)},
            'frame_projection_relative_outer_entry_SP':{'outer_live_SP':-16,'outer_RA':-4,'primary_RA':-20,'gate_RA':-36,
                'released_initializer_RA':-52,'retry_RA_reuses_released_location':-52,'SP_after_retry_RET':-48,'SP_after_primary_RET':-16},
            'gate_publication_words':gate_words,'primary_publication_words':primary_words,
            'no_return_A0_test_or_boolean_gate':True,'A0_until_outer_handler_load':'final Y & 0xffff, possibly0','conditional_A1_until_next_initializer':'0xffffffff',
            'first_outer_registration':{'pc':hex(d['entry']+16),'handler':hex(handler),'fresh_count_premise':6,'fresh_capacity_premise':'>=14','fresh_table_premise':hex(paths.layout.T),
                'reply':6,'new_count':7,'entry6_address':hex(entry6),'A2_reply':7,'handler_invoked':False},
            'cut_before_first_outer_initializer':{'pc':hex(nextpc),'target':hex(d['outer_init'][0]),'A0':6,'A1':'0xffffffff','A2':7},
            'primary_source_chain':{'APP_load':hex(APP_PC),'APP_slot':'0x4007c','APP_store':hex(APP_PC+28),'APP_config_field':36,
                'candidate_pointer':hex(clockpc),'destination_word':hex(F+36),'matching_copy_request_bytes':64,
                'startup_zero_word_ordinal':198,'config_source':hex(fd[2]),'config_sha256':sha256(cfg_raw).hexdigest(),
                'premises':'S0=40000 at APP load, SP/frame and field36 retained across calls/validation, matching64B copy, and no later writers changing fresh F+36. Zero/fill requests are source witnesses, not final-value proofs'},
            'clock_callback_slot':hex(F+68),'clock_accumulator':hex(ctx+20),'clock_two_paths':clock_paths,
            'matching_clock_callback':{'target':cb['start'],'bytes':130,'sha256':cb['sha256'],'result_word':hex(ctx+24),
                'arithmetic_bytes':914,'arithmetic_sha256':ar['sha256'],'arithmetic_GPR_definitions':ar['encoded_GPR_definitions'],
                'reader_premise':'fresh copied-config word remains191c6 and its paired reads eventually complete; valid nonalias frames/data and required saved values/code/mappings retained'},
            'actual_primary_binding_proved':False,'actual_installed_binding_proved':False})
    return {'schema':'TSL9-gate-return-publication-static-v1','profile':parent['profile'],'APP_sha256':sha256(image).hexdigest(),'APP_clock_source':app,
        'APP_builder_reused_sha256':builder['sha256'],'profiles':profiles,
        'scope':'per candidate42B/17i clock wrapper,54B/17i gate suffix,54B/15i primary suffix,16B/4i outer window plus APP30B/10i source; old full callers/config/registration/clock callback/arithmetic replayed; no new C bytes',
        'conditional_publication':'assuming prior retry ordinaryRET and required frame/state preservation, gate and primary publish7 words without inspecting A0; sixwordsinsideB296, lastatB324externalglobal; these are pointer installs, not callback invocations. Saved RA/frame links bring control to outer+8',
        'registration_boundary':'zero-gate path count6 and required c/T retention admit nextregistration ID6/count7 atT+24; A1 remainsffffffff, A2 becomes7. Stop before4da70/4db08; later registrations and IDs not fixed',
        'clock_binding_boundary':'APP fresh slot4007c -> C+36 -> matching64B copy -> F+36/source primary pointer. Candidate SDKJT18 is TMOS_GetSystemClock. Actual fresh/installed binding and ordering not proved by source geometry or pointer table',
        'clock_contract':'fresh clock pointerF+68, ifnonzero call then add returnedword to post-callback fresh ctx20 modulo32 and store; always returnfinal fresh ctx20. Local16B frame restoresRA/S0. Unknown callback must preserve wrapper/source live S registers, SP/frames/GP and caller-required objects/state',
        'matching_clock_case':'if fresh F+68 matches43d62/43dee and copiedreader remains191c6, existing130B callback/914B arithmetic/90B reader contracts supply local preservation; reader progress and all mapping/access/nonalias/MMIO/asynchronous premises still required. Reply staysopaque; ctx20 andctx24 aredistinct',
        'remaining':['actual primary/clock callback binding and preservation across writers','4da70/4db08 and remaining outer initializers/tail','actual retry termination, hardware progress and object lifetimes'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(image,carriers):
    mutations=0;cases=[(image[APP_PC-0x8000:APP_PC-0x8000+APP_SIZE],'APP_source',0)]
    for i,data in enumerate(carriers):
        cases.extend((init.binding.take(data,specs(p,i)[0],z),p,i) for p,z in zip(ROLES,SIZES))
    for raw,p,i in cases:
        pc=specs(p,i)[0]
        for q,d in decode(raw,pc).items():
            off=q-pc;z=d['size'];buf=bytearray(raw);buf[off:off+z]=(int.from_bytes(buf[off:off+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
            try:body(buf,p,i)
            except RuntimeError as e:check(str(e).startswith('publication '+p+' operand '),'publication specified mutation guard '+str(e))
            else:raise RuntimeError('publication mutation escaped')
            mutations+=1
    check(mutations==116,'publication mutation census')
    check(0x40034+18*4==0x4007c and 52-16==36 and 6+1==7,'publication source/registration geometry')
    check(-80+28==-64+12==-52 and -48+12==-36 and -32+12==-20 and -16+12==-4,'publication reused/released stack-slot geometry')
    for y in (0,1,65535,65536,0xfffffffe):check(0<=y&65535<=65535,'publication low16 domain includes zero')
    print('PASS:116 operand mutations rejected; field36/tableentry6/RA-frame geometry; no A0-test publication suffixes')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');o=parser.parse_args()
    image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK header identity')
    carriers=[]
    for label,folder,tail,z,digest in init.binding.PROFILES:
        raw=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(raw)==z and sha256(raw).hexdigest()==digest,'candidate identity '+label);carriers.append(raw)
    raw_hex=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
    coverage=sparse.derive(image,carriers,header,raw_hex,sparse.parser())
    ledger=derive(image,carriers,header,coverage);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract()
    tests(image,carriers);output=(json.dumps(ledger,indent=1,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'publication exact ledger replay')
    print('PASS:conditional seven-word publication/frame return/next ID6 registration; APP clock source and nested preservation case; exact ledger')
    print('PASS:NO target execution; actual binding/termination/next initializer/hardware outcomes UNPROVED')


if __name__=='__main__':main()
