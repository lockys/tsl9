"""First registration -> constructor -> config publication, strictly static.

Original operand/CFG joins and finite interval/field algebra only. No target
ISA, register machine, RAM/frame, copy, callback, polling or MMIO runner.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_first_registration_chain_static as previous
import check_v4160_app_config_source_static as app
import check_v4160_config_precallees_static as pre
import check_v4160_mode3_frame_static as mode
import check_v4160_config_gates_static as gates
import check_v4160_config_arithmetic_static as arithmetic
import check_v4160_app_jt0_call_chain_static as boot
import check_v4160_event_payload_chain_static as payload

init,sparse,check=previous.init,previous.sparse,previous.check
OUT=Path(__file__).with_name('v4160-constructor-publication-chain-static.json')
GP=0x20004000
TASK=GP+388
CONFIG=bytes.fromhex('c6910100ffffffff803ee80300000000')


def path(b,index,hook,calculate):
    """Finite normal-return CFG with explicit, algebra-justified branch facts."""
    pc=gates.DETAILS[index][0];_,a=gates.specs(pc,index)
    choices={22:24 if hook else 30,30:32,36:38,40:42,44:46,48:50,52:70,
        106:108 if calculate else 140}
    edges={int(p,16):[int(q,16) for q in qs] for p,qs in b['conditional_CFG'].items()}
    for o,q in choices.items():
        check(a(q) in edges[a(o)],'publication branch successor membership')
        edges[a(o)]=[a(q)]
    cut=a(148);edges[cut]=[];seen=set();todo=[pc]
    while todo:
        p=todo.pop()
        check(p not in seen,'publication selected path acyclic')
        seen.add(p);check(len(edges[p])==int(p!=cut),'publication selected finite chain')
        todo.extend(edges[p])
    check(cut in seen and a(160) not in seen and a(152) not in seen,'publication before-registration cut, no null/failure epilogue')
    check((a(26) in seen)==hook and (a(134) in seen)==calculate and a(84) in seen and a(100) in seen,'publication hook/arithmetic/copy/publish join')
    return {'hook':'matching 197b8' if hook else 'zero','fresh_state23':'zero' if calculate else 'nonzero',
        'selected_PCs':[hex(p) for p in sorted(seen)],'cut_before_call':hex(cut),
        'not_executed_callee':b['calls'][3]['target']}


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage)
    # Each reused body verifies every operand and whole-window byte identity.
    wrapper=app.body(image[0x19b16-0x8000:0x19b56-0x8000],'wrapper')
    constructor=app.body(image[0x19b56-0x8000:0x19bd4-0x8000],'construct')
    wn={d['pc']:d for d in wrapper['instructions']};cn={d['pc']:d for d in constructor['instructions']}
    r=boot.DETAILS[0]
    reset=boot.body(image[r[1]-0x8000:r[1]-0x8000+r[2]],r[0],r[1],r[-1],r[3],r[4])
    rn={d['pc']:d for d in reset['instructions']}
    check((0x186aa+rn[0x186aa]['imm']+rn[0x186ae]['imm'])&0xffffffff==GP,'publication reset GP source algebra')
    check(all(p['cut_at_return_link']=='0x19b30' and p['conditional_reply']==3 for p in parent['profiles']),'publication prior reply join')
    init.g(wn,0x19b30,'publication index address',op='addi',rd=8,rs1=3,imm=388)
    init.g(wn,0x19b34,'publication index byte',op='store',rs1=8,rs2=10,imm=0,width=1)
    check(wrapper['calls'][1]['target']==constructor['start'] and wrapper['calls'][1]['link']=='0x19b3a','publication constructor call/link')
    for p,f in ((0x19bc8,dict(op='load',rd=15,rs1=15,imm=116,width=4)),
        (0x19bca,dict(op='mv',rd=10,rs2=2)),(0x19bcc,dict(op='call_indirect',rd=1,rs1=15))):
        init.g(cn,p,'publication constructor provider join',**f)
    check(constructor['calls'][-1]=={'pc':'0x19bcc','link':'0x19bce','target':'fresh U32[40074] & ~1','normal_return_and_preservation_proved':False},'publication fresh provider call boundary')
    preproof=pre.derive(image,carriers,header,coverage)
    reader=mode.service.body(image[0x191c6-0x8000:0x19220-0x8000],'reader',0x191c6,mode.service.APP_HASHES[1])
    reader_defs=sorted({d['rd'] for d in reader['instructions'] if d.get('rd',0)})
    modebody=mode.body(image[mode.PC-0x8000:mode.END-0x8000],reader_defs)
    check(preproof['remaining_constructor_site']=={'pc':'0x19ba8','target':'0x197b8'} and constructor['calls'][-2]['target']=='0x197b8','publication all13 pre-call closure')
    # No mode3 GP store; its other stores are own frame or classified fixed MMIO.
    check(all(d['address'].startswith('entrySP') or 0x40000000<=int(d['address'],16)<0x50000000
        for d in modebody['memory_accesses_with_origin_proofs'] if d['op']=='store'),'publication mode direct RAM store classification')
    check(TASK==0x20004184 and TASK+8==previous.layout.H,'publication byte at heap-8')
    check(CONFIG[:4]==(0x191c6).to_bytes(4,'little') and CONFIG[4:8]==b'\xff'*4
        and int.from_bytes(CONFIG[8:10],'little')==16000 and int.from_bytes(CONFIG[10:12],'little')==1000
        and CONFIG[12:]==b'\0'*4,'publication constructor exact little endian fields')
    check(0x19bba-4096+1548==0x191c6 and 0x3e84000-384==int.from_bytes(CONFIG[8:12],'little'),'publication constructor constants')
    profiles=[]
    for i,(data,prior) in enumerate(zip(carriers,parent['profiles'])):
        pc,size=gates.DETAILS[i][:2];b=gates.body(init.binding.take(data,pc,size),i)
        check(init.binding.word(data,0x40074)==pc,'publication candidate40074 mapping')
        arith=arithmetic.body(data,i)
        mapping=init.binding.profile(data,init.binding.PROFILES[i][0])['first_copy']
        src=int(mapping['source'],16)+0x20000332-int(mapping['destination'],16)
        copy=payload.body(init.binding.take(data,src,58),'copy',0x20000332,58,18,3,init.binding.COPY_HASH)
        check(copy['encoded_GPR_writes']==[13,14,15,16] and not copy['calls'],'publication copy leaf frame/GPR preservation')
        check(b['calls'][1]['target']==copy['start'] and b['copy_call_arguments']['A2']==16 and b['calls'][2]['target']==arith['entry'],'publication copy/arithmetic calls join')
        dest=int(b['copied_config'],16);state=int(b['base'],16);service=int(b['service_word'],16)
        hook=int(b['optional_hook_word'],16);ctx=int(prior['count_byte'],16)-1
        stores=[(dest,16),(service,4),(state+23,1)]
        if i:stores.append((int(b['V140_unconditional_pre_hook_clear'],16),4))
        protected=[(TASK,1),(ctx+1,1),(ctx+2,1),(ctx+40,4),(hook,4),
            (previous.layout.B,8),(previous.layout.T+12,4)]
        for address,width in stores:
            for other,n in protected:check(previous.origin.separated(address,width,other,n),'publication direct resident writes exclude saved fields')
        check(all(address+width<=previous.layout.H for address,width in stores),'publication fixed RAM stores below nominal heap')
        paths=[path(b,i,h,z) for h in (False,True) for z in (False,True)]
        profiles.append({'label':prior['label'],'candidate40074':hex(pc),'config_body_sha256':b['sha256'],
            'copied_config':hex(dest),'service_word':hex(service),'hook_word':hex(hook),
            'fixed_direct_RAM_writes':[{'address':hex(p),'bytes':w} for p,w in stores],
            'paths':paths,'copy_source_candidate':hex(src),'copy_sha256':copy['sha256'],
            'arithmetic_entry':arith['entry'],'conditional_copied_16bytes':CONFIG.hex(),
            'conditional_published_service_word':'0x191c6','conditional_state23_if_zero':22,
            'state23_if_nonzero':'original fresh byte preserved on this path',
            'conditional_saved_task_byte':3,'conditional_count':4,'conditional_entry3':'0x1995c',
            'unclosed_registration_call':b['calls'][3],'actual_installed_binding_proved':False})
    return {'schema':'TSL9-constructor-publication-chain-static-v1','profile':parent['profile'],
        'APP_sha256':sha256(image).hexdigest(),'scope':'joins of already verified complete bodies; no new C reconstruction bytes',
        'reused_bodies':{'reset':{'start':reset['start'],'sha256':reset['sha256']},
            'wrapper':{'start':wrapper['start'],'sha256':wrapper['sha256']},
            'constructor':{'start':constructor['start'],'sha256':constructor['sha256']},
            'mode3':{'start':modebody['start'],'sha256':modebody['sha256']}},
        'nominal_GP':hex(GP),'saved_index_byte':hex(TASK),'profiles':profiles,
        'source':'constructor frame C: words0=191c6,4=ffffffff,8=03e83e80; bytes12..15 remain zero after all13 matching normal-return pre-calls',
        'optional_hook_cases':'fresh hook is either zero or 197b8 with matching mode3 code/reader and valid normal return; other nonzero hooks remain unclosed',
        'frame_algebra':'relative C: constructor frame[0,32), wrapper frame[32,48); provider frame[-32,0); hook stores[-100,-96) and[-84,-32); constructor mode stores[-68,-64) and[-52,0)',
        'gate_join':'C nonzero; words0/4 and halfwords8/10 are nonzero; byte12 zero bypasses state+21 gate, regardless of its fresh byte',
        'copy_publication':'matching 58B forward byte-copy leaf transfers16 bytes from C to copied_config if nonoverlap/source stability/completion hold; fresh word0 publishes191c6 to service_word',
        'arithmetic_join':'if fresh state+23=0, h16000 gives floor(7*h/5000)=22 on verified specialized path; nonzero state+23 skips helper/store',
        'preservation':'nominal GP at19b30, valid nonalias frames/code/globals/heap, preserved providers and required normal returns, no adverse MMIO/FENCE.I/IRQ/DMA/reentry/external writers are premises; direct fixed stores exclude task byte,count,capacity,table pointer,entry3,hook and allocated header',
        'stop':'before config registration call (not 40080); no assumption that registration returns or preserves fields, no constructor/wrapper completion or subsequent40058 call claim',
        'lifetime':'copy has no direct source-pointer-register store; value bytes include code191c6. Config source remains within active constructor frame at cut. No external retention or later object-lifetime conclusion',
        'remaining':['config registration callee effects/return and wrapper40058 tail','actual GP persistence, installed slots/hook and field44 sources',
            'physical effects/progress/external writers, GP+108 signed arithmetic and object lifetime'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(image,carriers):
    # Pure offsets/fields; no mutable frame, RAM or target-register model.
    config=set(range(16));constructor_ra=set(range(28,32));wrapper=set(range(32,48))
    children=[set(range(-20,-16))|set(range(-4,0)),set(range(-68,-64))|set(range(-52,0)),
        set(range(-100,-96))|set(range(-84,-32))]
    check(all(not s&(config|constructor_ra|wrapper) for s in children),'publication nested stores exclude caller data')
    check(all(v!=0 for v in (int.from_bytes(CONFIG[:4],'little'),int.from_bytes(CONFIG[4:8],'little'),16000,1000)),'publication gate fields nonzero')
    for flag in range(256):check(CONFIG[12]==0 and ((1400*16000)//1000000 if flag==0 else flag)==(22 if flag==0 else flag),'publication conditional arithmetic flags')
    for row in previous.layout.facts():
        check(TASK+1<previous.layout.H<previous.layout.B<previous.layout.T+12<previous.layout.T+16<=previous.layout.T+4*row['N0'],'publication task/table disjoint across layout domain')
    mutations=0
    for role in ('wrapper','construct'):
        _,pc,size,*_=next(d for d in app.DETAILS if d[0]==role);raw=image[pc-0x8000:pc-0x8000+size]
        for p,d in app.decode(raw,pc).items():
            at=p-pc;w=d['size'];buf=bytearray(raw)
            buf[at:at+w]=(int.from_bytes(buf[at:at+w],'little')^(1<<20 if w==4 else 4)).to_bytes(w,'little')
            try:app.body(buf,role)
            except RuntimeError as e:check(str(e).startswith(('APP config '+role+' operand ','APP config wrapper unsigned byte encoding')),'publication APP mutation guard '+str(e))
            else:raise RuntimeError('publication APP mutation escaped')
            mutations+=1
    for i,data in enumerate(carriers):
        pc,size=gates.DETAILS[i][:2];raw=init.binding.take(data,pc,size);_,a=gates.specs(pc,i)
        for off in (12,24,26,28,32,38,42,46,50,52,74,76,84,92,100,104,112,134,138,148):
            d=gates.decode(raw,pc)[a(off)];at=a(off)-pc;w=d['size'];buf=bytearray(raw)
            buf[at:at+w]=(int.from_bytes(buf[at:at+w],'little')^(1<<20 if w==4 else 4)).to_bytes(w,'little')
            try:gates.body(buf,i)
            except RuntimeError as e:check(str(e).startswith('config operand '),'publication gate mutation guard '+str(e))
            else:raise RuntimeError('publication gate mutation escaped')
            mutations+=1
    check(mutations==105,'publication mutation census')
    arithmetic.algebra_tests()
    print('PASS:256 layouts/256 flag cases; nested frame intervals;105 APP/config operand mutations rejected')


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
    tests(image,carriers);output=(json.dumps(ledger,indent=1,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'constructor publication exact ledger replay')
    print('PASS:first registration -> constructor13calls -> optional hook/gates/copy/publication;8 finite paths; exact ledger')
    print('PASS:NO target execution; next registration/installed bindings/physical effects/later lifetime UNPROVED')


if __name__=='__main__':main()
