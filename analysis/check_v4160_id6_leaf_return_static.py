"""Offline getter/callback-table leaf proof and conditional ID7 return link.

Decode original bytes, verify operands/CFG and integer/interval identities.
No target ISA, mutable memory, callbacks, allocator or fill execution/model.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_outer_id6_initializer_static as previous

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
paths=previous.paths
role=previous.previous.role
registration=previous.previous.registration
OUT=Path(__file__).with_name('v4160-id6-leaf-return-static.json')
PARTS=('getter','callback_register','next_outer')
SIZES=(10,42,16)
COUNTS=(3,17,4)
HASHES=(('b97fcee3c37d952ce71ecb05fd2ce901bf4aa68dbc1aa8f7c8041846fe964c37',
 '5817fb22f99830f5abb07b366dcee8800bf94c6a215ee23d68e756adc0cffcad','59dbe6d110bb1c30b3eb7a3f58ba12a51fd28df5b16038e0aa6c61f3065f0e3d'),
 ('1fb792016a003da073b38a76d6e6db2a00dfc38439dd3660ade01847211b4430',
 'd4a461baaf66debe24cb72b5b90fe44320d36aa67daeb171ebccc3b42b0868f1','031ce727ef6bb1b4b06923145cc77737260806aafbdf510de33c08ca5e345d41'))


def specs(part,index):
    delta=80*index
    if part=='next_outer':
        entry,s=role.specs('entry',index);pc=entry+24
        return pc,{p:f for p,f in s.items() if pc<=p<pc+16}
    pc=(0x4efd8 if part=='getter' else 0x4efe2)+152*index
    if part=='getter':
        return pc,{pc:dict(op='lui',rd=15,imm=0x20003000),
            pc+4:dict(op='load',rd=10,rs1=15,imm=948+delta,width=1),pc+8:dict(op='jr',rs1=1)}
    s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    e(0,'lui',rd=14,imm=0x20003000);e(4,'addi',rd=13,rs1=14,imm=856+delta)
    e(8,'li',rd=15,imm=0);e(10,'addi',rd=14,rs1=14,imm=856+delta);e(14,'li',rd=12,imm=12)
    e(16,'load',rd=11,rs1=13,imm=0,width=4);e(18,'bnez',rs1=11,target=pc+30)
    e(20,'slli',rd=15,rs1=15,imm=2);e(22,'add',rd=15,rs1=15,rs2=14)
    e(24,'store',rs1=15,rs2=10,imm=0,width=4);e(26,'li',rd=10,imm=0);e(28,'jr',rs1=1)
    e(30,'addi',rd=15,rs1=15,imm=1);e(32,'addi',rd=13,rs1=13,imm=4)
    e(34,'bne',rs1=15,rs2=12,target=pc+16);e(38,'li',rd=10,imm=19);e(40,'jr',rs1=1)
    return pc,s


def body(raw,part,index):
    k=PARTS.index(part);pc,s=specs(part,index);n=decode(raw,pc)
    check(set(n)==set(s),'id6leaf '+part+' boundaries')
    for p,f in s.items():init.g(n,p,'id6leaf '+part+' operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[k],HASHES[index][k]),'id6leaf '+part+' identity')
    edges={}
    for p,d in n.items():
        if d['op']=='jr':check(d['rs1']==1,'id6leaf ordinary RET');q=[]
        elif d['op'] in ('bnez','bne'):q=[p+d['size'],d['target']]
        elif part=='next_outer' and p==pc+12:q=[]
        else:q=[p+d['size']]
        check(all(v in n for v in q),'id6leaf '+part+' closed local edges');edges[p]=q
    seen={pc};todo=[pc]
    while todo:
        for q in edges[todo.pop()]:
            if q not in seen:seen.add(q);todo.append(q)
    check(seen==set(n),'id6leaf '+part+' all nodes locally reachable')
    defs=sorted({d['rd'] for d in n.values() if d.get('rd',0)})
    stores=[p for p,d in n.items() if d['op']=='store']
    if part!='next_outer':
        check(defs==([10,15] if part=='getter' else [10,11,12,13,14,15]),'id6leaf exact GPR definitions')
        check(not any(d['op'] in ('jal','jalr','call_indirect','csr','fence.i') for d in n.values()),'id6leaf no calls/privileged operations')
        check(stores==([] if part=='getter' else [pc+24]),'id6leaf exact local store census')
        check([p-pc for p,d in n.items() if d['op']=='load']==([4] if part=='getter' else [16]),'id6leaf exact fresh load census')
    else:
        check(defs==[1,10] and not stores,'id6leaf outer replaces A0 and has no result test')
    return {'start':hex(pc),'bytes':len(raw),'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),
        'conditional_CFG':{hex(p):[hex(q) for q in v] for p,v in edges.items()},'encoded_GPR_definitions':defs,
        'complete_function':part!='next_outer','last_call_is_cut':part=='next_outer'}


def path_certificates(leaf):
    """Finite CFG certificates, not table contents or an interpreter."""
    pc=int(leaf['start'],16);edges={int(p,16):[int(q,16) for q in qs] for p,qs in leaf['conditional_CFG'].items()}
    prefix=[0,4,8,10,14];cycle=[16,18,30,32,34];success=[16,18,20,22,24,26,28]
    cases=[]
    for k in range(13):
        offsets=prefix+cycle*k+(success if k<12 else [38,40]);trace=[pc+o for o in offsets]
        check(all(b in edges[a] for a,b in zip(trace,trace[1:])) and not edges[trace[-1]],'id6leaf finite CFG path '+str(k))
        reads=offsets.count(16);writes=offsets.count(24)
        check(reads==(k+1 if k<12 else 12) and writes==int(k<12),'id6leaf path read/write census')
        # After j nonzero reads, the encoded +1/+4 steps give j and base+4*j.
        check(all(0<=j<=12 and 4*j<=48 for j in range(k+1)),'id6leaf cursor/index domain')
        cases.append({'first_observed_zero_index':k if k<12 else None,'prior_nonzero_reads':k,
            'read_count':reads,'store_count':writes,'store_offset':4*k if k<12 else None,
            'A0_reply':0 if k<12 else 19,'A1_reply':0 if k<12 else 'last observed nonzero word at slot11',
            'A2_reply':12,'path':[hex(p) for p in trace]})
    return cases


def getter_domain():
    rows=[{'getter_reply':v,'request_bytes':12*v,'low16_request_bytes':12*v&65535} for v in range(256)]
    check(all(r['request_bytes']==r['low16_request_bytes'] for r in rows),'id6leaf low16 redundant in U8 getter domain')
    check(min(r['request_bytes'] for r in rows)==0 and max(r['request_bytes'] for r in rows)==3060,'id6leaf getter size domain')
    check(12*5==60 and 12*66==792,'id6leaf retained source examples')
    return rows


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[]
    for i,(data,pr) in enumerate(zip(carriers,parent['profiles'])):
        d=role.DETAILS[i];pc=previous.STARTS[i][0];entry=d['entry'];base=0x20003358+80*i
        windows={p:body(init.binding.take(data,specs(p,i)[0],SIZES[k]),p,i) for k,p in enumerate(PARTS)}
        getter=windows['getter'];leaf=windows['callback_register'];outer=windows['next_outer'];cases=path_certificates(leaf)
        gn={x['pc']:x for x in getter['instructions']};ln={x['pc']:x for x in leaf['instructions']};on={x['pc']:x for x in outer['instructions']}
        pn={x['pc']:x for x in pr['bodies']['initializer']['instructions']}
        rn={x['pc']:x for x in pr['bodies']['resources']['instructions']};rpc=int(pr['bodies']['resources']['start'],16)
        lpc=int(leaf['start'],16);gpc=int(getter['start'],16)
        check(gn[gpc+4]['imm']+0x20003000==int(pr['resource_source']['count_byte'],16),'id6leaf getter source is resource count byte')
        check([pn[pc+o]['target'] for o in (276,316)]==[gpc,gpc],'id6leaf both parent getter call joins')
        check(pn[pc+360]['rd']==0 and pn[pc+360]['target']==lpc,'id6leaf parent unlinked tail join')
        init.g(pn,pc+340,'id6leaf parent RA restore',op='load',rd=1,rs1=2,imm=44,width=4)
        init.g(pn,pc+358,'id6leaf parent frame release',op='addi',rd=2,rs1=2,imm=48)
        check(pn[pc+350]['imm']+pn[pc+354]['imm']==0x4d916+152*i,'id6leaf tail input callback pointer')
        check(pn[pc+68]['rs2']==1 and pn[pc+68]['imm']==44,'id6leaf parent saved caller RA')
        check(ln[lpc+24]['rs2']==10 and all(x.get('rd')!=10 for p,x in ln.items() if p<lpc+26),'id6leaf input pointer retained until store')
        check(ln[lpc+4]['imm']+0x20003000==base and ln[lpc+10]['imm']+0x20003000==base,'id6leaf scan/store cursor base identity')
        # All 12 slot extents are in this fixed 48B table without wrap.
        slots=[base+4*k for k in range(12)]
        check(base&3==0 and all(base<=a<a+4<=base+48<=0xffffffff for a in slots),'id6leaf exact table extent')
        ctx=0x20003000+d['ctx'];F=ctx+80
        protected=[(ctx+1,1),(ctx+2,1),(ctx+3,1),(ctx+40,4),(paths.layout.T,4*212),(paths.layout.A+8,16),(F+21,1),(F+36,4),(F+68,4),(int(pr['resource_source']['count_byte'],16),1)]
        for a in slots:
            for b,z in protected:check(paths.origin.separated(a,4,b,z),'id6leaf callback table excludes task/config/count fields')
        check(paths.origin.separated(base,48,0x20003320+80*i,48),'id6leaf parent first fill excludes callback table')
        check(paths.origin.separated(base,48,0x20003354+80*i,4),'id6leaf pool pointer immediately before callback table')
        init.g(rn,rpc+112,'id6leaf resource tail fill length',op='addi',rd=12,rs1=0,imm=48)
        init.g(rn,rpc+118,'id6leaf resource tail fill destination',op='addi',rd=10,rs1=10,imm=856+80*i)
        check(rn[rpc+108]['imm']+rn[rpc+118]['imm']==base,'id6leaf resource tail fill/table address join')
        check(on[entry+32]['target']==d['reg'] and on[entry+36]['target']==d['outer_init'][1],'id6leaf next two calls exact')
        next_handler=0x46000+d['outer_lows'][1]
        check(on[entry+24]['imm']+on[entry+28]['imm']==next_handler,'id6leaf next handler load overwrites prior reply')
        # Prior outer full body establishes first initializer's saved return PC.
        old=role.body(init.binding.take(data,entry,112),'entry',i)
        en={x['pc']:x for x in old['instructions']}
        check(en[entry+20]['target']==pc and en[entry+20]['rd']==1 and entry+24==int(outer['start'],16),'id6leaf outer return address join')
        reg=registration.body(init.binding.take(data,d['reg'],48),i)
        check(11 not in reg['encoded_GPR_definitions'],'id6leaf next task registration preserves A1')
        entry7=paths.layout.T+4*7
        check(7<14 and entry7+4<=paths.layout.T+4*14,'id6leaf admission entry7 extent')
        for b,z in protected[:4]+[(base,48)]:check(paths.origin.separated(entry7,4,b,z),'id6leaf entry7 excludes task slots and callback table')
        profiles.append({'label':pr['label'],'bodies':windows,'callback_table':{'base':hex(base),'bytes':48,'slots':[hex(v) for v in slots]},
            'table_paths':cases,'getter_contract':{'fresh_U8_address':pr['resource_source']['count_byte'],'reply_range':[0,255],'local_stores':0,'GPR_definitions':[10,15],
                'parent_allocation_bytes':'12*g1, 0..3060; low16 does not truncate','parent_fill_bytes':'12*g2, 0..3060, separate fresh getter after allocator',
                'g1_equals_g2_proved':False,'retained_q_case':'if source count retained across calls, g1=g2=q0..66; APP source14 case gives5 and60 bytes, conditional only'},
            'leaf_contract':{'GPR_definitions':[10,11,12,13,14,15],'SP_RA_GP_S_unchanged_locally':True,'nested_calls':0,'maximum_fresh_reads':12,
                'success':'first observed zero word -> one SW of entry A0, then reply A0=0/A1=0/A2=12; accepts null or duplicate input without a check',
                'full':'12 observed nonzero words -> no SW, reply A0=19/A1=last observed word/A2=12',
                'not_a_coherent_snapshot':'each slot is a fresh read; no atomic publication, duplicate check or lifetime guarantee follows',
                'callback_invoked':False,'preservation_premises':'valid code/48B table accesses, physical nonalias with caller frame/code, and no interfering GPR/code writes'},
            'conditional_parent_tail_return':{'parent_tail_pc':hex(pc+360),'target':hex(lpc),'entry_A0':hex(0x4d916+152*i),'returns_to_outer':hex(entry+24),
                'premises':'parent reaches tail after all required callees return, preserves saved RA/frame/live values, restores original SP, and table store cannot corrupt caller state',
                'does_not_test_leaf_reply':True,'whole_parent_completion_proved':False},
            'conditional_cleared_table_case':{'fill_source_PC':hex(rpc+128),'table_bytes':48,'first_zero_slot':0,'slot0_pointer':hex(0x4d916+152*i),'leaf_reply_A0_A1_A2':[0,0,12],
                'premises':'nonzero resource path reaches matching fill; its48B zero result retained through all later parent/provider/dynamic-payload writes until leaf fresh read',
                'zero_resource_case_has_this_fill':False,'actual_zero_table_proved':False},
            'conditional_next_registration':{'pc':hex(entry+32),'handler':hex(next_handler),'target':hex(d['reg']),'fresh_count_premise':7,'fresh_capacity_premise':'>=14','fresh_table_premise':hex(paths.layout.T),
                'table_entry7':hex(entry7),'reply_A0':7,'reply_A2':8,'new_count':8,'A1_on_empty_slot_case':0,'A1_on_full_table_case':'last observed nonzero callback slot11 word',
                'premises':'valid nonalias task table extent, required metadata retained or independently fresh as specified; no interfering writers'},
            'cut_before_second_outer_initializer':{'pc':hex(entry+36),'target':hex(d['outer_init'][1]),'A0':7,'A2':8,'A1':'0 on callback insertion; last observed nonzero word on full callback table'},
            'actual_installed_binding_proved':False})
    return {'schema':'TSL9-ID6-leaf-return-static-v1','profile':parent['profile'],'APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'getter_domain':getter_domain(),
        'scope':'per candidate full10B/3i getter, full42B/17i callback-register leaf and16B/4i outer return window;48 new operand guards,26 finite CFG path certificates; prior full initializer/resource/registration evidence replayed',
        'boundary':'conditional parent tail ordinaryRET joins next task registration without testing callback insertion reply; under fresh count7/capacity>=14/tableT stop before second initializer with ID7/count8 and changed A1',
        'remaining':['parent allocator/fill actual provider binding, payload extents and metadata/frame preservation','second initializer46570/46608 and callback4d916/4d9ae consumer flow','actual fresh config/count writers, table publication/lifetime and asynchronous effects'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    count=0;certificates=0
    for i,data in enumerate(carriers):
        for k,part in enumerate(PARTS):
            pc=specs(part,i)[0];raw=init.binding.take(data,pc,SIZES[k]);b=body(raw,part,i)
            if part=='callback_register':certificates+=len(path_certificates(b))
            for p,d in decode(raw,pc).items():
                at=p-pc;z=d['size'];buf=bytearray(raw)
                buf[at:at+z]=(int.from_bytes(buf[at:at+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
                try:body(buf,part,i)
                except RuntimeError as e:check(str(e).startswith('id6leaf '+part+' operand '),'id6leaf specified mutation guard '+str(e))
                else:raise RuntimeError('id6leaf mutation escaped')
                count+=1
    check(count==48 and certificates==26,'id6leaf mutation/path census');getter_domain()
    print('PASS:48 operand mutations rejected;26 finite CFG path certificates;256 getter-byte sizes0..3060; callback-table48B/12slots')


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
    tests(carriers);output=(json.dumps(ledger,indent=1,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'id6leaf exact ledger replay')
    print('PASS:getter/tail-register/full-table return contracts;conditional ID7/count8 join with changed A1;exact ledger')
    print('PASS:NO target execution/emulation; actual provider/parent completion/callback lifetime UNPROVED')


if __name__=='__main__':main()
