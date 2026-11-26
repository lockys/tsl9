"""Callback reply copies and their conditional overwrite on config continuation.

Static source bytes, operand guards and host halfword/interval algebra only;
no target register, memory, fill, callback, provider or MMIO execution/model.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_app44_closure_static as closure

source=closure.parent.source
init,post,ROOT,MASK=closure.init,source.cb.io.post,closure.ROOT,closure.MASK
check=init.check
OUT=Path(__file__).with_name('v4160-callback-reply-lifetime-static.json')


def segment(raw,pc,n):
    return {'start':hex(pc),'end_exclusive':hex(pc+len(raw)),'bytes':len(raw),
            'sha256':sha256(raw).hexdigest(),'instructions':list(n.values())}


def chain_contract(data,index):
    detail=init.DETAILS[index];cfg=detail[2];C=detail[5];M=C-80
    pd=post.DETAILS[index];pc=pd[0]
    whole_cfg=init.binding.take(data,cfg,228);whole_post=init.binding.take(data,pc,272)
    tail_raw=whole_cfg[188:208];tail=closure.decode(tail_raw,cfg+188)
    expected={188:dict(op='lui',rd=15,imm=0x20003000),
      192:dict(op='store',rs1=15,rs2=10,imm=M+8-0x20003000,width=2),
      196:dict(op='lui',rd=15,imm=0x20003000),200:dict(op='li',rd=14,imm=-1),
      202:dict(op='store',rs1=15,rs2=14,imm=detail[10],width=1),
      206:dict(op='jal',rd=1,target=pc)}
    check(set(tail)=={cfg+o for o in expected},'lifetime complete caller window')
    for off,f in expected.items():init.g(tail,cfg+off,'lifetime caller instruction '+hex(off),**f)
    prefix_raw=whole_post[:74];prefix=closure.decode(prefix_raw,pc)
    pe={p:f for p,f in post.specs(pc,M,pd).items() if p<pc+74}
    check(set(prefix)==set(pe)|{pc+o for o in (48,52,66,70)},'lifetime complete post prefix')
    for p,f in pe.items():init.g(prefix,p,'lifetime post instruction '+hex(p-pc),**f)
    for off,role in ((48,'fill20'),(66,'fill40')):
        init.pair(prefix,pc+off,1,0x2000039c,'lifetime '+role+' target pair')
    check(not any(d['op']=='load' for d in list(tail.values())+list(prefix.values())),
          'lifetime no explicit local memory load in continuation windows')
    # After SH, the scalar R has no local consumer before LUI A0 kills it.
    before_kill=[d for p,d in tail.items() if p>cfg+192]+[d for p,d in prefix.items() if p<pc+8]
    check(not any(d.get('rs1')==10 or d.get('rs2')==10 for d in before_kill),
          'lifetime scalar reply unconsumed before kill')
    init.g(prefix,pc+8,'lifetime scalar A0 overwrite',op='lui',rd=10,imm=0x20003000)
    own_fixed=[(M+76,4),(C+68,4),(M+68,4),(0x20003000+detail[10],1)]
    reply=set(range(M+8,M+10));first_fill=set(range(M+44,M+64));second_fill=set(range(M,M+40))
    check(all(reply.isdisjoint(range(a,a+w)) for a,w in own_fixed),'lifetime intervening fixed stores disjoint')
    check(reply.isdisjoint(first_fill) and reply<=second_fill,'lifetime fill extent relationship')
    check(M+40<=MASK and M>0,'lifetime fill endpoint nonwrapping')
    # Bind both requests to the complete first-copy source body, not a name.
    label=init.binding.PROFILES[index][0];mapping=init.binding.profile(data,label)
    row=next(r for r in mapping['slots'] if r['slot']=='0x40048')
    check(row['target']=='0x2000039c','lifetime fill slot target')
    fill_source=int(row['source'],16);fill=source.fill_contract(init.binding.take(data,fill_source,46))
    check(fill_source==(0x4060c if index==0 else 0x4064c),'lifetime fill source address')
    check(fill['encoded_GPR_writes']==[10,14,15],'lifetime fill required SP/S0/RA encoded nonwrites')
    loads=[d for d in fill['instructions'] if d['op']=='load']
    check(len(loads)==1 and loads[0]['rd']==15 and loads[0]['rs1']==14 and loads[0]['imm']==524 and loads[0]['width']==4,
          'lifetime fill sole load is projected control word')
    check(not any(d['op'] in ('jal','jalr','call_indirect') for d in fill['instructions']),
          'lifetime fill no nested call')
    check(sha256(whole_cfg).hexdigest()==detail[-1] and sha256(whole_post).hexdigest()==pd[-1],
          'lifetime inherited complete body identities')
    return {'label':label,'config_base':hex(C),'metadata_base':hex(M),
        'reply_halfword':{'store_pc':hex(cfg+192),'bytes':[hex(M+8),hex(M+9)],'width':2},
        'caller_window':segment(tail_raw,cfg+188,tail),'post_prefix_window':segment(prefix_raw,pc,prefix),
        'scalar_kill_pc':hex(pc+8),'local_register_consumers_after_SH_before_kill':[],
        'A4_overwrite_pc':hex(cfg+200),'A4_replacement':-1,
        'local_memory_loads_in_both_windows':[],
        'intervening_fixed_stores':[{'address':hex(a),'bytes':w} for a,w in own_fixed],
        'fill20':{'pair_start':hex(pc+48),'transfer_pc':hex(pc+52),'normal_link':hex(pc+56),
            'destination':hex(M+44),'byte':0,'count':20,'reply_overlap':False,'normal_A0_with_context':hex(M+64)},
        'fill40':{'pair_start':hex(pc+66),'transfer_pc':hex(pc+70),'normal_link_and_heap_init_call':hex(pc+74),
            'destination':hex(M),'byte':0,'count':40,'reply_overlap_offsets':[8,9],
            'low_byte_store_ordinal':9,'high_byte_store_ordinal':10,'stores_atomic':False,
            'normal_A0_with_context':hex(M+40),'reply_after_completed_fill_with_premises':0},
        'fill_body':dict(fill,flash_source=hex(fill_source)),
        'scope_is_not_global_reader_or_writer_census':True}


def derive(app,carriers,header):
    old=closure.derive(app,carriers,header)
    profiles=[chain_contract(data,i) for i,data in enumerate(carriers)]
    check(len(old['prior_reply_stores'])==2,'lifetime prior callback reply provenance')
    for now,before in zip(profiles,old['prior_reply_stores']):
        check(now['reply_halfword']['store_pc']==before['store_pc'] and now['reply_halfword']['bytes'][0]==before['store_address'],
              'lifetime store joins proved reply edge')
    check(sum(p['caller_window']['bytes']+p['post_prefix_window']['bytes'] for p in profiles)==188,
          'lifetime window byte total')
    check(sum(len(p['caller_window']['instructions'])+len(p['post_prefix_window']['instructions']) for p in profiles)==56,
          'lifetime window instruction total')
    return {'schema':'TSL9-callback-reply-lifetime-static-v1','profile':init.timer.PROFILE,
        'scope':'2 caller20B windows +2 post-prefix74B windows; 2 complete mapped46B fill bodies; original callback closure revalidated',
        'profiles':profiles,
        'reply_source':'conditional preserved low16 result from original APP197f0 callback, not a measured hardware sample',
        'selected_software_copies_not_exhaustive':{'scalar':'A0 survives SH but is not locally consumed before post+8 LUI A0',
            'halfword':'M+8..9 survives disjoint fixed stores/fill20 then fill40 writes zeros in byte order'},
        'conditional_normal_continuation':{'unknown_software_callee_before_overwrite':False,
            'metadata_reply_reloaded_or_scalar_consumed_after_SH_before_overwrite':False,
            'both_copies_still_represent_sample_at_heap_init':False,
            'metadata_halfword_zero_after_fill40':True},
        'other_copy_boundary':{'A4':'callback result reload also leaves A4, then config+200 LI A4,-1 overwrites it',
            'callback_result_stack_word_relative_to_same_returned_SP':[-100,-97],
            'post_saved_words_relative_to_same_SP':[-12,-1],
            'callback_result_stack_word_explicitly_cleared_by_selected_chain':False,
            'actual_old_stack_contents_or_lifetime_proved':False},
        'premises':['APP callback returns normally; original code and supported encoding semantics hold',
            'required config/global/SP/S0 registers and saved frame remain valid at projected accesses',
            'candidate first-copy fill bytes match actual RAM and target2000039c executes those bytes',
            'both fill requests complete valid nonwrapping writes; frame/code/objects do not adversely alias',
            'control word4002420c maps separately from metadata; no interrupts/external writer/hardware effects interfere'],
        'not_proved':['global absence of other readers/writers','physical overwrite or installed provider',
            'universal termination or behavior on fault/nonreturn','hardware value has no other use or side effect',
            'absence of other copies or physical zeroization of old callback stack',
            'later heap or config-I/O object ownership/pointer lifetime'],
        'unconditional_reply_zero_at_arbitrary_time':False,
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    # Bit masks/interval relationships, not a target output-buffer model.
    for r in range(65536):
        check(r-(r&255)==r&0xff00,'halfword low-byte clear mask')
        check((r&0xff00)-256*(r>>8)==0,'two-byte clear mask')
    check(set(range(-100,-96)).isdisjoint(range(-12,0)),'old callback result and post frame extents')
    for count in range(41):
        covered=set(range(count));check(({8,9}<=covered)==(count>=10),'minimum span to cover reply')
    for M in (0x2000319c,0x200031ec):
        check(set(range(M+8,M+10)).isdisjoint(range(M+44,M+64)) and
              set(range(M+8,M+10))<=set(range(M,M+40)),'profile interval arithmetic')
    cfg=init.DETAILS[0][2];pc=post.DETAILS[0][0]
    cases=((cfg+192,'2392a71a','2393a71a','lifetime caller instruction 0xc0'),
      (cfg+192,'2392a71a','23a2a71a','lifetime caller instruction 0xc0'),
      (cfg+202,'a38ae75e','a38ce75e','lifetime caller instruction 0xca'),
      (pc+8,'37350020','b7350020','lifetime post instruction 0x8'),
      (pc+30,'1305851c','1305051c','lifetime post instruction 0x1e'),
      (pc+22,'5146','4146','lifetime post instruction 0x16'),
      (pc+56,'1305c419','13054419','lifetime post instruction 0x38'),
      (pc+60,'13068002','13068000','lifetime post instruction 0x3c'),
      (pc+64,'8145','8545','lifetime post instruction 0x40'),
      (pc+70,'e780c081','e780e081','lifetime fill40 target pair'))
    for where,old,new,wanted in cases:
        raw=bytearray(carriers[0]);off=where-0x40000
        check(raw[off:off+len(bytes.fromhex(old))]==bytes.fromhex(old),'lifetime mutation source '+hex(where))
        raw[off:off+len(bytes.fromhex(new))]=bytes.fromhex(new)
        try:chain_contract(raw,0)
        except RuntimeError as error:check(str(error)==wanted,'unexpected lifetime mutation guard '+str(error))
        else:raise RuntimeError('lifetime mutation escaped')
    for changed in ('a30fb5fc','a30fa5fe'):
        raw=bytearray(init.binding.FILL);check(raw[36:40].hex()=='a30fb5fe','lifetime fill mutation source')
        raw[36:40]=bytes.fromhex(changed)
        try:source.fill_contract(raw)
        except RuntimeError as error:check(str(error)=='fill instruction 0x24','unexpected fill mutation guard')
        else:raise RuntimeError('lifetime fill mutation escaped')
    print('PASS: 65536 halfword mask cases; 41 span cases; 2 profile interval identities; 12 specified raw mutations')


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true',help='Create ledger exclusively');o=p.parse_args()
    app,header=init.binding.APP.read_bytes(),init.core.outer.HEADER.read_bytes()
    check(len(app)==76800 and sha256(app).hexdigest()==init.binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK header identity')
    carriers=[]
    for label,folder,tail,size,digest in init.binding.PROFILES:
        raw=(ROOT/'analysis/wch-resident-candidate-2026-10-21'/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(raw)==size and sha256(raw).hexdigest()==digest,'candidate identity '+label);carriers.append(raw)
    sources,vectors=init.timer.source_contract();ledger=derive(app,carriers,header)
    ledger['sources'],ledger['official_Xwchc_vectors']=sources,vectors
    tests(carriers);output=(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'reply lifetime exact ledger replay')
    print('PASS: 4 continuation windows, 188 bytes/56 instructions; 2 complete46B fill bodies; scalar kill + conditional halfword clear')
    print('PASS: exact ledger replay; no explicit local read before overwrite; global/physical lifetime UNPROVED; NO target execution')


if __name__=='__main__':main()
