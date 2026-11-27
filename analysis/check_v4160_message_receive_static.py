"""Offline message receive/unlink and conditional interior-pointer release.

Original operand/CFG guards, immutable position witnesses and scalar equations.
No target ISA, mutable queue/heap/register model, callback or MMIO execution.
"""
import argparse,json,re
from collections import Counter
from hashlib import sha256
from pathlib import Path
import check_v4160_threshold_message_static as previous
import check_v4160_payload_consumers_static as app
import check_v4160_builtin_record_handlers_static as handlers

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
life=previous.previous
OUT=Path(__file__).with_name('v4160-message-receive-static.json')
PARTS=('receive','unlink')
STARTS=((0x2000028c,0x4319c),(0x2000028c,0x43228))
SOURCES=((0x404fc,0x4319c),(0x4053c,0x43228))
SIZES=(136,30)
COUNTS=(50,10)
FIELDS,BRANCHES=previous.FIELDS,previous.BRANCHES
HASHES=(('5771f29cb783ef341662bdd56d13a702628ba2ce41c39009aa1f66352d2f858e', '17fe4759b755d24e7d6f1ee920448a0483109c37373e4eb5ec70ae54a2f5a517'), ('b66fd81feca3ce5e88d1fd235fe8eb087ea28793f0790ecd0a67d549652cf4a3', '17fe4759b755d24e7d6f1ee920448a0483109c37373e4eb5ec70ae54a2f5a517'))
LITERALS=(
{
'receive':'''
000 addi 2 2 -32
002 store 2 18 16 4
004 store 2 19 12 4
006 lui 15 1073889280
00a store 2 1 28 4
00c store 2 8 24 4
00e store 2 9 20 4
010 load 19 15 524 4
014 mv 18 10
016 store 15 0 524 4
01a fence.i
01e lui 10 536883200
022 load 8 10 408 4
026 li 9 0
028 li 12 0
02a bnez 8 60
02c bnez 9 70
02e lui 11 32768
030 mv 10 18
032 auipc 1 3758370816
036 jalr 1 1 1770
03a jump 98
03c load 15 8 -2 1
040 bne 15 18 122
044 beqz 9 132
046 mv 11 9
048 addi 10 10 408
04c auipc 1 3758370816
050 jalr 1 1 -316
054 beqz 8 46
056 lui 11 32768
058 mv 10 18
05a auipc 1 3758370816
05e jalr 1 1 612
062 load 1 2 28 4
064 load 8 2 24 4
066 lui 15 1073889280
06a store 15 19 524 4
06e mv 10 9
070 load 18 2 16 4
072 load 9 2 20 4
074 load 19 2 12 4
076 addi 2 2 32
078 jr 1
07a bnez 9 126
07c mv 12 8
07e load 8 8 -8 4
082 jump 42
084 mv 9 8
086 jump 126
''',
'unlink':'''
000 load 14 10 0 4
002 load 15 11 -8 4
006 bne 14 11 24
00a store 10 15 0 4
00c li 15 -1
00e store 11 0 -8 4
012 store 11 15 -2 1
016 jr 1
018 store 12 15 -8 4
01c jump 12
'''
},
{
'receive':'''
000 addi 2 2 -32
002 store 2 18 16 4
004 store 2 19 12 4
006 lui 15 1073889280
00a store 2 1 28 4
00c store 2 8 24 4
00e store 2 9 20 4
010 load 19 15 524 4
014 mv 18 10
016 store 15 0 524 4
01a fence.i
01e lui 10 536883200
022 load 8 10 488 4
026 li 9 0
028 li 12 0
02a bnez 8 60
02c bnez 9 70
02e lui 11 32768
030 mv 10 18
032 auipc 1 3758370816
036 jalr 1 1 1910
03a jump 98
03c load 15 8 -2 1
040 bne 15 18 122
044 beqz 9 132
046 mv 11 9
048 addi 10 10 488
04c auipc 1 3758370816
050 jalr 1 1 -176
054 beqz 8 46
056 lui 11 32768
058 mv 10 18
05a auipc 1 3758370816
05e jalr 1 1 752
062 load 1 2 28 4
064 load 8 2 24 4
066 lui 15 1073889280
06a store 15 19 524 4
06e mv 10 9
070 load 18 2 16 4
072 load 9 2 20 4
074 load 19 2 12 4
076 addi 2 2 32
078 jr 1
07a bnez 9 126
07c mv 12 8
07e load 8 8 -8 4
082 jump 42
084 mv 9 8
086 jump 126
''',
'unlink':'''
000 load 14 10 0 4
002 load 15 11 -8 4
006 bne 14 11 24
00a store 10 15 0 4
00c li 15 -1
00e store 11 0 -8 4
012 store 11 15 -2 1
016 jr 1
018 store 12 15 -8 4
01c jump 12
'''
}
)


def specs(part,index):
    pc=STARTS[index][PARTS.index(part)];out={}
    for line in LITERALS[index][part].splitlines():
        if not line:continue
        off,op,*args=line.split();values=[int(x,0) for x in args]
        check(len(values)==len(FIELDS[op]),'message-receive literal fields')
        f=dict(zip(FIELDS[op],values));f['op']=op
        if op in BRANCHES|{'jump'}:f['target']+=pc
        out[pc+int(off,16)]=f
    return out


def body(raw,part,index):
    k=PARTS.index(part);pc=STARTS[index][k]
    if part=='receive':
        check(raw[0x1a:0x1e]==bytes.fromhex('0f100000'),'message-receive fence bytes')
        check(int.from_bytes(raw[0x3c:0x40],'little')&0x707f==0x4003,'message-receive unsigned marker encoding')
    n=decode(raw,pc);s=specs(part,index);check(n.keys()==s.keys(),'message-receive boundaries '+part)
    for p,f in s.items():init.g(n,p,'message-receive operand '+part+' '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[k],HASHES[index][k]),'message-receive identity '+part)
    e={};calls=[];rets=[]
    for p,v in n.items():
        op=v['op'];qs=[p+v['size']]
        if op=='jr':check(v['rs1']==1,'message-receive ordinary RET');qs=[];rets.append(p)
        elif op in BRANCHES:qs.append(v['target'])
        elif op=='jump':qs=[v['target']]
        elif op=='jalr':
            check(v['rd']==v['rs1']==1 and n[p-4]['op']=='auipc' and n[p-4]['rd']==1,'message-receive call pair')
            calls.append({'offset':p-pc,'target':(p-4+n[p-4]['imm']+v['imm'])&0xfffffffe})
        check(all(q in n for q in qs),'message-receive closed CFG');e[p]=qs
    seen=set();pending=[pc]
    while pending:
        p=pending.pop()
        if p in seen:continue
        seen.add(p);pending.extend(e[p])
    check(seen==set(n),'message-receive all nodes reachable')
    stores=[{'offset':p-pc,'base':v['rs1'],'source':v['rs2'],'imm':v['imm'],'bytes':v['width']} for p,v in n.items() if v['op']=='store']
    check((len(calls),len(stores),len(rets))==((3,7,1),(0,4,1))[k],'message-receive census')
    check(previous.acyclic(e)==(part=='unlink'),'message-receive cycle census')
    if part=='receive':
        cut={p:list(qs) for p,qs in e.items()};cut[pc+0x82].remove(pc+0x2a)
        check(previous.acyclic(cut),'message-receive scan single backedge')
        check([p-pc for p,v in n.items() if v.get('rd')==9]==[0x26,0x72,0x84],'message-receive selected pointer definitions')
        check([p-pc for p,v in n.items() if v.get('rd')==12]==[0x28,0x7c],'message-receive predecessor definitions')
    else:
        check(sorted({v['rd'] for v in n.values() if v.get('rd',0)})==[14,15],'message-receive unlink preserves S/SP/RA/A0/A1/A2')
    return {'start':pc,'source':SOURCES[index][k],'bytes':len(raw),'sha256':sha256(raw).hexdigest(),
      'instructions':list(n.values()),'CFG':e,'calls':calls,'tails':[],'returns':rets,'stores':stores,
      'complete_local_body':True,'local_CFG_acyclic':previous.acyclic(e),'actual_progress_proved':False}


def position_certificate(b):
    """Immutable match-position strings produce CFG witnesses, not queue states."""
    pc=b['start'];prefix=[p-pc for p in b['CFG'] if p<pc+0x2a]
    epilogue=[0x62,0x64,0x66,0x6a,0x6e,0x70,0x72,0x74,0x76,0x78]
    unlink=[0x46,0x48,0x4c,0x50,0x54]
    stop=[0x2e,0x30,0x32,0x36,0x3a]
    event=[0x56,0x58,0x5a,0x5e]
    walks=[];hist=Counter();examples={};edge_union=set()
    for length in range(9):
        for bits in range(1<<length):
            matches=tuple(k for k in range(length) if bits>>k&1)
            first=matches[0] if matches else None;second=matches[1] if len(matches)>1 else None
            seq=prefix[:];limit=second+1 if second is not None else length
            for k in range(limit):
                seq.extend((0x2a,0x3c,0x40))
                if k==first:seq.extend((0x44,0x84,0x86,0x7e,0x82))
                elif k==second:seq.extend((0x44,*unlink,*event))
                else:
                    seq.append(0x7a)
                    if first is None or k<first:seq.append(0x7c)
                    seq.extend((0x7e,0x82))
            if second is None:
                seq.extend((0x2a,0x2c))
                if first is not None:seq.extend(unlink)
                seq.extend(stop)
            seq.extend(epilogue);life.valid(b['CFG'],[pc+o for o in seq])
            check(seq[-1]==0x78,'message-receive position witness RET')
            check(seq.count(0x50)==(first is not None) and seq.count(0x5e)==(second is not None) and seq.count(0x36)==(second is None),'message-receive position/call relation')
            check(seq.count(0x7c)==(length if first is None else first),'message-receive selected predecessor retained')
            name='no_match' if first is None else 'one_match' if second is None else 'multiple_matches'
            hist[name]+=1;examples.setdefault(name,{'length':length,'match_bits':bits,'first':first,'second':second,'offsets':seq})
            edge_union.update(zip(seq,seq[1:]));walks.append(seq)
    check(len(walks)==511 and dict(hist)=={'no_match':9,'one_match':36,'multiple_matches':466},'message-receive immutable pattern census')
    expected={(p-pc,q-pc) for p,qs in b['CFG'].items() for q in qs}
    check(edge_union==expected,'message-receive position witnesses cover every local edge')
    return {'immutable_match_position_cases':len(walks),'length_domain':[0,8],'case_counts':dict(hist),'first_examples':examples,
      'walks_sha256':sha256(json.dumps(walks,separators=(',',':')).encode()).hexdigest(),'all_local_edges_covered':True,
      'general_scan_reason':'before first match predecessor updated on each mismatch; first match captures S1 once; after first match predecessor unchanged; second match exits before following next',
      'unbounded_list_termination_or_dynamic_feasibility_proved':False}


def interior_release(data,index):
    core=life.previous.core;release=life.release;layout=life.layout
    H,B,E=layout.A,layout.B,layout.E;Q,M,R=H+8,H+16,H+20
    check((H,Q,M,R,B,E)==(0x200043ac,0x200043b4,0x200043bc,0x200043c0,0x200045ac,0x2000b184),'message-receive nominal heap anchors')
    check(H+8+504==B and R+8+484==B and 12+8+484==504,'message-receive request12 split equations')
    check(H<=M<=R and M>=H+8 and H<E and R not in (B,E),'message-receive interior input selects original header')
    check(M!=Q and 0xf004!=0x8001,'message-receive interior is not exact payload; no special counter tag')
    local_message_writes=((Q,4),(Q+4,2),(Q+6,1),(M+2,2),(M,1),(M+1,1),(M-2,1),(M-8,4),(M-8,4),(M-2,1))
    check(all(H+8<=a and a+z<=R for a,z in local_message_writes),'message-receive wrapper/body/marker/next writes exclude H and R headers')
    an,ae=life.previous.core_body(init.binding.take(data,core.DETAILS[index][0],208),index)
    fn,fe=life.free_body(init.binding.take(data,release.DETAILS[index][0],212),index)
    ap,fp=core.ENTRY,release.ENTRY
    allocation={22:24,24:38,56:60,76:110,112:114,116:120,134:138}
    freeing={16:24,44:48,52:56,56:60,64:68,74:92,120:158,160:164,172:176,178:180}
    aw=life.until(ae,ap,{ap+a:ap+z for a,z in allocation.items()})
    fw=life.until(fe,fp,{fp+a:fp+z for a,z in freeing.items()})
    check(aw[-1]==ap+202 and fw[-1]==fp+22,'message-receive split/release selected returns')
    check([p-fp for p in fw if fn[p]['op']=='store']==[8,104,118,190,192,198,18],'message-receive selected private release stores')
    check(fn[fp+52]['rs1']==10 and fn[fp+52]['rs2']==15 and fn[fp+56]['rs1']==17 and fn[fp+56]['rs2']==10,'message-receive containing-block bounds use input')
    check(fn[fp+68]['rs1']==15 and fn[fp+100]['rs1']==15 and fn[fp+100]['imm']==4,'message-receive size/tag read from selected header,not M-8')
    check(all(a+z<=M or M+4<=a for a,z in ((H,4),(H+4,2),(H+6,2),(release.DETAILS[index][4]+6,2))),'message-receive free does not erase4-byte body on selected path')
    for count in range(65536):check((((count-20)&65535)+12+8)&65535==count,'message-receive account inverse')
    return {'header_H':H,'core_payload_Q':Q,'message_M':M,'remainder_header_R':R,'original_next_B':B,'heap_limit_E':E,
      'allocation_offsets':[p-ap for p in aw],'private_release_offsets':[p-fp for p in fw],
      'header_selection':'walk begins H; H<=M<=R and M>=H+8 selects H even though M!=Q; size/tag use H+4/H+6',
      'roundtrip':'request12,tagf004 splits504 into12+8+484; retained free R then merges toH.size504,H.nextB; account-20+20 mod65536',
      'message_write_intervals_relative_to_H':[[a-H,z] for a,z in local_message_writes],
      'local_message_body_and_marker_next_writes_exclude_H_R_headers':True,
      'premises':'retained nominal heap globals,H/R headers,size/tag/next/account; valid message allocation; no intervening header writes/reallocation; no alias,concurrent writer,IRQ,DMA,reentry; public markerFF and normal callees',
      'scope':'conditional same-original-block release now proved for this nominal allocation; not every interior pointer or arbitrary heap geometry; body bytes not wiped; post-free ownership/access not valid',
      'unconditional_real_heap_ownership_or_lifetime_proved':False}


def profile(image,data,index,parent):
    bs={part:body(init.binding.take(data,SOURCES[index][k],SIZES[k]),part,index) for k,part in enumerate(PARTS)}
    receive,unlink=bs['receive'],bs['unlink'];rp,up=STARTS[index];C=0x2000319c+80*index
    rn={v['pc']-rp:v for v in receive['instructions']};un={v['pc']-up:v for v in unlink['instructions']}
    mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);copy=mapping['first_copy']
    check(init.binding.word(data,0x4006c)==rp and int(copy['source'],16)+rp-int(copy['destination'],16)==SOURCES[index][0],'message-receive JT14/full mapping join')
    check(rp+136<=int(mapping['first_copy_end_exclusive'],16),'message-receive complete captured mapping')
    stop=previous.dealloc.DETAILS[index][1];event=life.consumer.DETAILS[index][1]
    check(receive['calls']==[{'offset':0x36,'target':stop},{'offset':0x50,'target':up},{'offset':0x5e,'target':event}],'message-receive three mapped call targets')
    check(rn[0x1e]['imm']+rn[0x22]['imm']==C-4 and rn[0x48]['imm']==rn[0x22]['imm'],'message-receive same global queue head as sender')
    check(rn[0x3c]['imm']==un[0x12]['imm']==-2 and rn[0x7e]['imm']==un[2]['imm']==un[0xe]['imm']==-8,'message-receive marker/link geometry')
    check(rn[0x6e]['rd']==10 and rn[0x6e]['rs2']==9,'message-receive saved first pointer return')
    sender=parent['bodies']['sender'];sn={v['pc']-sender['start']:v for v in sender['instructions']}
    check(sn[0x74]['imm']==-2 and sn[0x78]['imm']==rn[0x22]['imm'],'message-receive enqueue/dequeue field join')
    unlink_walks={name:previous.walk(unlink,{6:z}) for name,z in (('head',10),('interior',24))}
    for seq in unlink_walks.values():check(seq[-4:]==[12,14,18,22],'message-receive reset next0/ownerFF before RET')
    task_spec=next(v for v in app.DETAILS if v[0]=='task');role,pc,size,count,stores,digest=task_spec
    task=app.body(image[pc-0x8000:pc-0x8000+size],*task_spec)
    tn={v['pc']-pc:v for v in task['instructions']}
    check(tn[24]['imm']==108 and tn[30]['imm']==104 and tn[26]['op']==tn[32]['op']=='call_indirect','message-receive APP fresh receive/free slots')
    check(not any(v['op'] in ('load','store') and (v.get('rs1')==10 or v.get('rs2')==10) for o,v in tn.items() if 26<o<34),'message-receive APP no body dereference before free')
    hpc=life.producer.post.DETAILS[index][5];pool=life.producer.init.DETAILS[index][5]+64
    handler=handlers.body(init.binding.take(data,hpc,130),hpc,1,pool-0x20003000,previous.dealloc.DETAILS[index][0],handlers.DIGESTS[index][1])
    hn={v['pc']-hpc:v for v in handler['instructions']}
    check((hpc+22+hn[22]['imm']+hn[26]['imm'])&0xfffffffe==rp,'message-receive registered handler receive target')
    check(hn[30]['rs1']==10 and hn[32]['target']==previous.dealloc.DETAILS[index][0],'message-receive handler free same receive reply')
    return {'label':init.binding.PROFILES[index][0],'bodies':bs,'CFG_certificates':{p:previous.certificates(b) for p,b in bs.items()},
      'immutable_position_certificates':position_certificate(receive),'unlink_walks':unlink_walks,
      'queue_head_slot':C-4,'reused_APP_task':{k:task[k] for k in ('start','bytes','sha256')},
      'reused_kind1_handler':{k:handler[k] for k in ('start','bytes','sha256')},'conditional_interior_release':interior_release(data,index),
      'receive_contract':['full entrytask captured; no local task/count bound; compare freshU8[M-2] to full task',
        'S1 firstmatching M; A2 predecessor only updated beforefirstmatch; scan until secondmatch or null; no mutation before unlink',
        'no match ->stop(task,8000),return0; one match ->unlinkfirst,stop(task,8000),return firstM; multiple ->unlinkfirst,event(task,8000),return firstM',
        'stop/event replies ignored; return from liveS1 before restoring entryS1; requires normal return/context and savedframe preservation',
        'receive may loop forever on invalid/cyclic list; finite list length n has <=n marker comparisons; secondmatch exits earlier'],
      'unlink_contract':['if freshhead==selected M then head=freshU32[M-8],else predecessor-8=freshU32[M-8]',
        'then M-8=0,M-2=255; no body reads/writes,free or event calls; correct predecessor/list/membership/nonalias required'],
      'caller_join':['APP task17476 and registered kind1 handler bit15:receive(task); if nonzero reply M,free(M); neither examines body before cleanup',
        'under original entryevent/frame/S preservation, both return full E XOR8000 even if receive0 or cleanup has no effect',
        'different entries and profiles are alternatives,not a proved synchronous pipeline; actual callback registration/dispatch/runtime IDs unresolved'],
      'remaining':['actual installed provider and execution/registration order','global/header/frame lifetime and all writers','other message-processing consumers and event rescheduling'],
      'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage)
    match=re.search(rb'^#define\s+tmos_msg_receive\s+[^\r\n]*BLE_LIB_JT\(\s*(\d+)\s*\)',header,re.M)
    check(match is not None and int(match[1])==14,'message-receive SDK JT identity')
    profiles=[profile(image,data,i,parent['profiles'][i]) for i,data in enumerate(carriers)]
    check(sum(b['bytes'] for p in profiles for b in p['bodies'].values())==332,'message-receive byte census')
    check(sum(len(b['instructions']) for p in profiles for b in p['bodies'].values())==120,'message-receive instruction census')
    return {'schema':'TSL9-message-receive-static-v1','APP_sha256':sha256(image).hexdigest(),'SDK_receive_JT':14,'profiles':profiles,
      'new_complete_body_bytes':332,'new_complete_body_instructions':120,'C_reconstruction_coverage_changed':False,
      'scope':'complete candidate receive/unlink plus conditional same-block interior release and existing APP/registered-handler cleanup joins',
      'target_execution_or_emulation':False,'hardware_accessed':False,'network_analysis':False}


def tests(carriers):
    count=unsigned=0
    for i,data in enumerate(carriers):
        for k,part in enumerate(PARTS):
            raw=init.binding.take(data,SOURCES[i][k],SIZES[k]);n=decode(raw,STARTS[i][k])
            for p,v in n.items():
                off=p-STARTS[i][k];z=v['size'];bad=bytearray(raw)
                bad[off:off+z]=(int.from_bytes(bad[off:off+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
                try:body(bad,part,i)
                except RuntimeError:pass
                else:raise RuntimeError('message-receive mutation escaped')
                count+=1
            if part=='receive':
                bad=bytearray(raw);off=0x3c;bad[off:off+4]=(int.from_bytes(bad[off:off+4],'little')^(1<<14)).to_bytes(4,'little')
                try:body(bad,part,i)
                except RuntimeError as ex:check('unsigned marker' in str(ex),'message-receive exact signedness guard')
                else:raise RuntimeError('message-receive signedness mutation escaped')
                unsigned+=1
    check((count,unsigned)==(120,2),'message-receive mutation census')
    for event in range(65536):
        if event&0x8000:check((event^0x8000)==event-0x8000,'message-receive bit15 caller reply')
    print('PASS:120 instruction and2 signedness mutations rejected;1022 immutable position witnesses;65536 accounting/event domains')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK identity')
    carriers=[]
    for label,folder,tail,z,digest in init.binding.PROFILES:
        raw=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(raw)==z and sha256(raw).hexdigest()==digest,'candidate identity '+label);carriers.append(raw)
    hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
    coverage=sparse.derive(image,carriers,header,hexes,sparse.parser())
    ledger=derive(image,carriers,header,coverage);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract()
    tests(carriers);raw=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
    if args.write:
        with OUT.open('xb') as f:f.write(raw)
    else:check(OUT.read_bytes()==raw,'message-receive exact ledger replay')
    print('PASS:4 complete candidate bodies332B/120i;receive/unlink/caller joins and conditional interior-pointer release;exact ledger')
    print('PASS:NO target execution/emulation;actual provider,complete ownership and physical progress UNPROVED')


if __name__=='__main__':main()
