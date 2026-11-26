"""Post return -> APP continuation -> first registration, strictly static.

Original operands/CFG and scalar range/return identities only. No target ISA,
MMIO, callback table, initialization or registration state is run/emulated.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_mismatch_temp_release_static as previous
import check_v4160_mode3_frame_static as mode
import check_v4160_fallback_initialization_static as fallback
import check_v4160_config_buffer_source_static as source
import check_v4160_optional_hook_origin_static as origin
import check_v4160_task_registration_static as registration
import check_v4160_app_config_source_static as app_source
import check_v4160_initial_table_extent_static as layout
import check_v4160_post_config_static as post

init,sparse,check,decode=previous.init,previous.sparse,previous.check,mode.decode
OUT=Path(__file__).with_name('v4160-first-registration-chain-static.json')
CLOCK_PC=0x19106
CLOCK_HASH='69724f8e22551d238b67e52e25b3c1cbcaa62db28756da9b59a5c96ff7f16d87'
INIT_TAIL_HASH='d4a63a2cc4909d4b98a681a708ca931fb575dbacd2862c88c1aca0bb0f249e0f'
APP_TAIL_HASH='1a484d27c64160612fcb4c0ced28df525afe02edc2d2b698f68a350abecfbbe1'


def specs(role,pc,index=0):
    s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def load(o,r,b,v,w=4):e(o,'load',rd=r,rs1=b,imm=v,width=w)
    def store(o,r,b,v):e(o,'store',rs2=r,rs1=b,imm=v,width=4)
    def imm(o,op,r,b,v):e(o,op,rd=r,rs1=b,imm=v)
    def lui(o,r,v):e(o,'lui',rd=r,imm=v)
    if role=='clock':
        e(0,'beqz',rs1=11,target=pc+14);lui(2,14,0x40021000);load(6,15,14,20)
        e(8,'or',rd=10,rs1=10,rs2=15);store(10,10,14,20);e(12,'jr',rs1=1)
        lui(14,15,0x40021000);load(18,14,15,20);imm(20,'xori',10,10,-1)
        e(24,'and',rd=10,rs1=10,rs2=14);store(26,10,15,20);e(28,'jr',rs1=1)
    elif role=='init_tail':
        e(0,'jal',rd=1,target=fallback.DETAILS[index][2]-320)
        e(2,'li',rd=15,imm=0);load(4,1,2,12);load(6,8,2,8);load(8,9,2,4)
        e(10,'mv',rd=10,rs2=15);imm(12,'addi',2,2,16);e(14,'jr',rs1=1)
    elif role=='app_tail':
        e(0,'beqz',rs1=10,target=pc+4);e(2,'jump',target=pc+2);e(4,'li',rd=11,imm=1)
        imm(6,'addi',10,0,64);e(10,'jal',rd=1,target=CLOCK_PC)
        lui(14,15,0xe000e000);lui(18,14,0x80000000);load(22,1,2,92);load(24,8,2,88)
        store(26,14,15,260);e(30,'li',rd=14,imm=1);store(32,14,15,264)
        imm(36,'addi',2,2,96);e(38,'jr',rs1=1)
    else:raise RuntimeError('unknown first registration role')
    return s


def body(raw,role,index=0):
    pc={'clock':CLOCK_PC,'init_tail':fallback.DETAILS[index][2]+206,'app_tail':0x19aee}[role]
    size,count,digest={'clock':(30,12,CLOCK_HASH),'init_tail':(16,8,INIT_TAIL_HASH),'app_tail':(40,14,APP_TAIL_HASH)}[role]
    n=decode(raw,pc);s=specs(role,pc,index);check(set(n)==set(s),'first registration boundaries '+role)
    for p,f in s.items():init.g(n,p,'first registration '+role+' operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(size,count,digest),'first registration whole window identity '+role)
    edges={}
    for p,d in n.items():
        if d['op']=='jr':q=[]
        elif d['op']=='jump':q=[d['target']]
        elif d['op']=='beqz':q=[p+d['size'],d['target']]
        else:q=[p+d['size']]
        check(all(v in n for v in q),'first registration local CFG no cuts '+role);edges[p]=q
    selected=dict(edges)
    if role=='clock':selected[pc]=[pc+2]
    if role=='app_tail':selected[pc]=[pc+4]
    seen=set();pending=[pc]
    while pending:
        p=pending.pop()
        if p in seen:continue
        seen.add(p);pending.extend(selected[p])
    expected_ret=pc+{'clock':12,'init_tail':14,'app_tail':38}[role]
    check(expected_ret in seen and all(len(selected[p])==1 for p in seen if p!=expected_ret) and selected[expected_ret]==[],'first registration selected finite chain '+role)
    if role=='clock':
        check(sorted({d['rd'] for d in n.values() if d.get('rd',0)})==[10,14,15],'clock no S/GP/SP/RA definitions')
        check(not any(d['op'] in ('jal','call_indirect','jalr') for d in n.values()),'clock leaf no calls')
    return {'role':role,'start':hex(pc),'end_exclusive':hex(pc+size),'bytes':size,'sha256':digest,
        'instructions':list(n.values()),'CFG':{hex(p):[hex(v) for v in q] for p,q in edges.items()},
        'selected_instruction_PCs':[hex(p) for p in sorted(seen)],
        'complete_function':role=='clock','call_returns_and_saved_word_integrity_are_premises':True}


def derive(app,carriers,header,coverage):
    parent=previous.derive(app,carriers,header,coverage)
    clock=body(app[CLOCK_PC-0x8000:0x19124-0x8000],'clock')
    tail=body(app[0x19aee-0x8000:0x19b16-0x8000],'app_tail')
    builder=source.app_contract(app[source.APP_PC-0x8000:source.APP_PC-0x8000+source.APP_SIZE])
    setup=origin.window(app[0x8e88-0x8000:0x8eb0-0x8000],'setup')
    wrapper=app_source.body(app[0x19b16-0x8000:0x19b56-0x8000],'wrapper')
    wn={d['pc']:d for d in wrapper['instructions']}
    check(builder['config_call']=='0x19aec' and wrapper['calls'][0]['pc']=='0x19b2e','first registration APP call joins')
    check(wrapper['calls'][0]['target']=='fresh U32[40080] & ~1' and 0x19b26-458==0x1995c,'first registration callback source join')
    check(wn[0x19b2e]['op']=='call_indirect' and wn[0x19b2e]['rs1']==15,'first registration link to cutoff')
    profiles=[]
    for i,(data,fd,prior) in enumerate(zip(carriers,fallback.DETAILS,parent['profiles'])):
        cfg,dest,hoff,boff=fd[2],fd[5],fd[9],fd[10]
        raw,n,_,_=fallback.config_contract(data,cfg,dest,hoff,boff)
        init_tail=body(raw[206:222],'init_tail',i)
        leaf=registration.body(init.binding.take(data,registration.DETAILS[i][0],48),i)
        check(init.binding.word(data,0x400a4)==cfg and init.binding.word(data,0x40080)==int(leaf['start'],16),'first registration candidate slot joins')
        check(init_tail['instructions'][0]['target']==post.DETAILS[i][0],'first registration post entry join')
        # The post target is cfg-320; IO-entry is a different callee. Keep both roles explicit.
        init.g(n,cfg+206,'first registration outer post call',op='jal',rd=1,target=cfg-320)
        ctx=int(leaf['context_base'],16);hook=dest+48;d=layout.T+12
        check(d==0x20004800 and d+4==0x20004804 and layout.T+4*14==0x2000482c,'first registration exact admitted footprint')
        check(origin.separated(d,4,hook,4) and origin.separated(ctx+1,1,hook,4) and origin.separated(d,4,ctx+1,1),'first registration count/table writes exclude hook and each other')
        init.g(wn,0x19b1e,'first registration fresh slot source',op='load',rd=15,rs1=9,imm=128,width=4)
        init.g(wn,0x19b2a,'first registration callback pointer',op='addi',rd=10,rs1=10,imm=-458)
        profiles.append({'label':prior['label'],'outer_initializer_tail':init_tail,'registration_leaf_sha256':leaf['sha256'],
            '400a4_candidate':hex(cfg),'40080_candidate':leaf['start'],'count_byte':leaf['count_byte'],
            'capacity_byte':leaf['capacity_byte'],'table_pointer_word':leaf['table_pointer_word'],'hook_word':hex(hook),
            'conditional_input_n':3,'conditional_reply':3,'conditional_stored_count':4,
            'conditional_callback_word_store':{'address':hex(d),'width':4,'value':'0x1995c'},
            'cut_at_return_link':'0x19b30','actual_installed_binding_proved':False})
    return {'schema':'TSL9-first-registration-chain-static-v1','profile':parent['profile'],'APP_sha256':sha256(app).hexdigest(),
        'scope':'new complete19106 RMWleaf30B/12instructions, boundedAPP/initializerreturn windows plusreusedfull setup/builder/wrapper/registration; no newly reconstructed C bytes',
        'clock_leaf':clock,'APP_return_tail':tail,'setup_order':setup,'profiles':profiles,
        'branch_premise':'either earlier shortcut post-return1 or nominalmismatch post-return0, with their ownalternativeconditions; preservefreshH/L/validownedtable/capacity/count3 andallrequiredcode/frames/context',
        'outer_return':'afterpostnormalreturn, initializerLI A5=0 thenMV A0,A5; restoresRA/S0/S1 andSP+16,RET; doesnotforwardpost0/1 distinction',
        'APP_success_and_RMW':'19aee sees0 andbypasses19af0selfspin; calls19106(A0=64,A1=1); matching code readsW=U32[40021014], writes/returnsW|64; no S/GP/SP/RA definitions',
        'APP_reply_boundary':'afterhelperAPPdoesnotredefineA0; normalbuilderreplyW|64 hasbit6setandisnonzero, not initializer0 or anerrorflag; setupnextCALL19b16 ignoresreply andwrapperreestablishesA0=1995c',
        'APP_late_CPU_stores':[{'address':'0xe000e104','width':4,'value':'0x80000000'},
            {'address':'0xe000e108','width':4,'value':'0x1'}],
        'preservation_to_registration':'outertailonlyloads savedwords; APPtail/RMW onlyfixedMMIOstores; wrapperprefix onlyownframewordstores. Under validnonaliasframes/globals/heap andnoadverseMMIO/asynchronous/contextinterference, T/c/n/ownership/hookword survive to40080',
        'first_registration':'n3<cN0(min14) soaccept; firstSB count4 atctx+1,thenSW1995c atT+12=20004800,returnoldn3; storesinsideallocatedtable/disjointmetadata/hook, no invocationofstoredcallback',
        'hook_value_boundary':'only preservationof thehookwordvalue atpost-return is shown; earlier field44/source-copy writers andactual197b8/slotvalues remainconditional',
        'lifetime_boundary':'proof stops at19b30 beforewrapperGP+388 byte-save andconstructor19b56; no newclaim aboutsubsequentpayloadretention orcallbackexecution',
        'remaining':['wrapperbyte-save/constructor/fresh40074/optionalhook continuation','sourcefields/field44effects beforepost-entry andactualinstalledproviders',
            'physicalMMIO/IRQ/DMA effects, otherdomains/faults/externalwriters andlifetime'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(app,carriers):
    for row in layout.facts():
        cap=row['N0'];r=row['rounded_payload'];check(3<cap and 3+1==4 and layout.T+16<=layout.T+4*cap<=layout.P+r,'first registration admitted footprint bounds')
    for low in range(65536):check((low|64)&64==64 and low|64!=0,'first registration RMW lower-word identity')
    for high in (0,1,0x7fff,0x8000,0xffff):
        for low in (0,1,63,64,255,65535):
            v=(high<<16)|low;check((v|64)&64 and (v|64)&0xffff0000==v&0xffff0000,'first registration fullword OR identity')
    count=0
    for role,pc,size in (('clock',CLOCK_PC,30),('app_tail',0x19aee,40)):
        raw=app[pc-0x8000:pc-0x8000+size]
        for p,d in decode(raw,pc).items():
            b=bytearray(raw);at=p-pc;w=d['size'];b[at:at+w]=(int.from_bytes(b[at:at+w],'little')^(1<<20 if w==4 else 4)).to_bytes(w,'little')
            try:body(b,role)
            except RuntimeError as e:check(str(e).startswith('first registration '+role+' operand '),'specific APP continuation mutation guard '+str(e))
            else:raise RuntimeError('first registration APP mutation escaped')
            count+=1
    for i,(data,fd) in enumerate(zip(carriers,fallback.DETAILS)):
        raw=init.binding.take(data,fd[2]+206,16)
        for p,d in decode(raw,fd[2]+206).items():
            b=bytearray(raw);at=p-fd[2]-206;b[at:at+2]=(int.from_bytes(b[at:at+2],'little')^4).to_bytes(2,'little')
            try:body(b,'init_tail',i)
            except RuntimeError as e:check(str(e).startswith('first registration init_tail operand '),'specific outer return mutation guard '+str(e))
            else:raise RuntimeError('first registration outer mutation escaped')
            count+=1
    check(count==42,'first registration continuation mutation census')
    print('PASS:256 layoutcases;65536 RMW bit identities/fullword boundaries;42 clock/APP/initializer operand mutations rejected')


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
    tests(app,carriers);output=(json.dumps(ledger,indent=1,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'first registration chain exact ledger replay')
    print('PASS:post/outer/APP/setup/first40080 joins; conditional table/index3/count4/hookword preservation to19b30; exact ledger')
    print('PASS:NO target execution; actualslots/MMIOinterrupts/latercontinuation/lifetime UNPROVED')


if __name__=='__main__':main()
