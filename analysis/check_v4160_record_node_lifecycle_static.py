"""Offline split/release and record/node lifetime composition certificates.

Reuses guarded bodies; graph walks, immutable intervals and scalar equations.
No target ISA, callback/list/heap/event machine, allocator or MMIO execution.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_timer_provider_closure_static as previous
import check_v4160_record_producer_static as producer
import check_v4160_linked_node_consumer_static as consumer
import check_v4160_builtin_record_handlers_static as handlers
import check_v4160_allocator_static as release
import check_v4160_initial_table_extent_static as layout

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-record-node-lifecycle-static.json')


def until(edges,start,choices,stop=None):
    seq=[];p=start
    while True:
        check(p not in seq,'lifetime selectedwalk acyclic');seq.append(p)
        if p==stop or not edges[p]:return seq
        q=choices.get(p,edges[p][0]);check(q in edges[p],'lifetime selectededge');p=q


def valid(edges,seq):check(all(q in edges[p] for p,q in zip(seq,seq[1:])),'lifetime complete validwalk')


def free_body(raw,index):
    check(raw[12:16]==bytes.fromhex('0f100000'),'lifetime free fencebytes')
    n=release.decode(raw);expected=release.specifications(release.DETAILS[index]);check(n.keys()==expected.keys(),'lifetime free boundaries')
    for p,f in expected.items():init.g(n,p,'lifetime free operand '+hex(p-release.ENTRY),**f)
    check(len(raw)==212 and sha256(raw).hexdigest()==release.DETAILS[index][-1],'lifetime free bodyidentity')
    check(not any(v['op'] in ('jal','jalr','call_indirect') for v in n.values()),'lifetime free nocalls')
    defs=sorted({v['rd'] for v in n.values() if v.get('rd',0)})
    check(defs==[6,10,11,12,13,14,15,16,17,28],'lifetime free keepsallS/SP/RA')
    edges,cycles,dom=release.graph(n)
    return n,edges


def domains():
    A,B,E=layout.A,layout.B,layout.E;Q=A+8;R=A+24;arena=layout.P
    check(A==0x200043ac and Q==0x200043b4 and R==0x200043c4 and B==0x200045ac and arena==0x200045b4,'lifetime nominalinterval anchors')
    check(A+8+504==B and R+8+480==B and Q+16==R and 16+8+480==504,'lifetime splitmerge equations')
    check(A<R<B<E and E==0x2000b184 and A!=E and R!=B and Q>=A+8 and Q<=R,'lifetime global-bound selectedguards')
    check(Q+16<=arena and arena+192<=layout.T,'lifetime firstgroup/node disjoint')
    check(0xff00!=0x8001 and ((16+3)&65535)&0xfffc==16,'lifetime tag/counter/rounding')
    for size in range(25,65536):check(16+8+(size-24)==size and size-16>8,'lifetime split sizes')
    for account in range(65536):check((((account-24)&65535)+16+8)&65535==account,'lifetime account inversemod16')
    for i in range(16):
        mask=1<<i;check(mask&65535==mask and (mask^mask)==0 and 12*i+12<=192,'lifetime group0 geometry/onehot')
        check(next(k for k in range(16) if mask>>k&1)==i,'lifetime selectedsinglebit')
    return {'nominal_additional_heap_premise':{'small_head_value':A,'large_head_value':B,'end_sentinel_value':E,'free_header':A,'payload_Q':Q,'allocated_payload_bytes':16,'free_remainder_header':R,'free_remainder_size':480,'original_next_header':B,'original_free_size':504,'arena_P':arena},
      'split_size_cases':65511,'account_word_cases':65536,'group0_singlebit_cases':16,
      'split_release_scalar_inverse':'504=16+8+480;allocationaccount-24;releasepayload16+mergedheader8 ->originalaccountmod65536',
      'counter_tag':'ff00 differs8001 soselectedspecialcounterincrement skipped','no_payload_erasure_inferred_from_free':True,
      'one_shot_metadata':'producerA4=0 ->node4=0 andrecord8=0 onlyifcaptured/livefields preserved','dispatch_and_input_reachability_proved':False}


def profile(data,index):
    F=producer.init.DETAILS[index][5];M=F-80;Pslot=F+64;T=M+132
    pp,digest=producer.DETAILS[index];pb=producer.body(init.binding.take(data,pp,268),pp,M,Pslot,digest);pn={v['pc']:v for v in pb['instructions']};pe=previous.graph(pn)
    src,epc,ch,eh=consumer.DETAILS[index];cb=consumer.consumer_body(init.binding.take(data,src,288),M,F,epc,ch);cn={v['pc']:v for v in cb['instructions']};ce=previous.graph(cn);cpc=consumer.ENTRY
    eb=consumer.event_body(init.binding.take(data,epc,64),epc,M,eh);en={v['pc']:v for v in eb['instructions']};ee=previous.graph(en)
    hpc=producer.post.DETAILS[index][4];hb=handlers.body(init.binding.take(data,hpc,130),hpc,0,Pslot-0x20003000,init.binding.word(data,0x40068),handlers.DIGESTS[index][0]);hn={v['pc']:v for v in hb['instructions']};he=previous.graph(hn)
    fn,fe=free_body(init.binding.take(data,release.DETAILS[index][0],212),index);fpc=release.ENTRY
    alloc=init.binding.take(data,previous.core.DETAILS[index][0],208);an,ae=previous.core_body(alloc,index);apc=previous.core.ENTRY
    cd=previous.core.DETAILS[index];fd=release.DETAILS[index]
    check(cd[1]==fd[1] and cd[2]==fd[5] and cd[3]==fd[2],'lifetime core/free heapglobal role joins')
    heapglobals={hex(cd[1]):hex(layout.A),hex(cd[2]):hex(layout.B),hex(cd[3]):hex(layout.E)}
    ar=until(ae,apc,{apc+22:apc+24,apc+24:apc+38,apc+56:apc+60,apc+76:apc+110,apc+112:apc+114,apc+116:apc+120,apc+134:apc+138})
    fr=until(fe,fpc,{fpc+16:fpc+24,fpc+44:fpc+48,fpc+52:fpc+56,fpc+56:fpc+60,fpc+64:fpc+68,fpc+74:fpc+92,fpc+120:fpc+158,fpc+160:fpc+164,fpc+172:fpc+176,fpc+178:fpc+180})
    check(ar[-1]==apc+202 and fr[-1]==fpc+22 and fpc+88 not in fr,'lifetime alloc/free selectedRET/counter branch')
    check([p-fpc for p in fr if fn[p]['op']=='store']==[8,104,118,190,192,198,18],'lifetime release selectedwrites')
    # Symbolic origins from the retained heap premise; no mutable heap object.
    A,Q,R=layout.A,layout.A+8,layout.A+24
    fieldwrites=[(A+6,2),(A+4,2),(A,4),(M+6,2)]
    check(all(a+z<=Q or Q+16<=a for a,z in fieldwrites),'lifetime release fields exclude16Bpayload')
    check(all(a+z<=layout.P or layout.P+192<=a for a,z in fieldwrites),'lifetime release fields exclude192Barena')
    prefix=until(pe,pp,{pp+38:pp+70},stop=pp+106);tail=until(pe,pp+118,{pp+134:pp+164,pp+172:pp+174,pp+220:pp+228})
    producer_paths={}
    for i in range(16):
        seq=prefix[:]
        for _ in range(i):seq.extend(pp+o for o in (110,114,116,250,252,106))
        seq.extend(pp+o for o in (110,114,116));seq.extend(tail);valid(pe,seq)
        check(seq[-1]==pp+68 and seq.index(pp+174)<seq.index(pp+178)<seq.index(pp+208),'lifetime node/record publication order')
        producer_paths[str(i)]=[p-pp for p in seq]
    selected_consumer={}
    for name,choices in (('cancelled_mask0',{30:32,68:70,72:76,180:182,194:282}),
      ('due_one_shot',{30:32,68:98,110:122,126:130,150:226,226:230,180:182,194:282}),
      ('due_repeat',{30:32,68:98,110:122,126:130,150:152,162:166,166:174,180:182,194:282})):
        seq=until(ce,cpc,{cpc+a:cpc+b for a,b in choices.items()});valid(ce,seq)
        check(seq[-1]==cpc+224,'lifetime consumer selectedRET')
        if name!='due_repeat':
            check(cpc+86 in seq and seq.index(cpc+80)<seq.index(cpc+86)<seq.index(cpc+88),'lifetime next capturedbeforefree')
            after=seq[seq.index(cpc+86)+1:];check(not any(cn[p]['op'] in ('load','store') and cn[p]['rs1']==8 for p in after),'lifetime nofreednode dereference onselectedsingle-nodeexit')
        else:check(cpc+86 not in seq and cpc+174 in seq,'lifetime repeatkeep path')
        selected_consumer[name]=[p-cpc for p in seq]
    eventpaths={name:[p-epc for p in until(ee,epc,{epc+24:epc+z})] for name,z in (('admitted',28),('rejected',56))}
    check(cn[cpc+146]['op']=='load' and cn[cpc+146]['rd']==15 and cn[cpc+146]['rs1']==8 and cn[cpc+146]['imm']==4 and cn[cpc+150]['rs1']==15,'lifetime postevent branches onfreshrepeat')
    check(not any(cn[cpc+o].get(k)==10 for o in (146,148,150) for k in ('rs1','rs2')),'lifetime eventreply nottestedbeforeone-shotchoice')
    handlers_paths={}
    for i in range(16):
        pre=until(he,hpc,{hpc:hpc+2},stop=hpc+18);seq=pre[:]
        for _ in range(i):seq.extend(hpc+o for o in (22,24,116,118,18))
        seq.extend(hpc+o for o in (22,24));seq.extend(until(he,hpc+26,{hpc+62:hpc+64,hpc+88:hpc+90}));valid(he,seq)
        check(hpc+70 in seq and seq.index(hpc+70)<seq.index(hpc+90)<seq.index(hpc+94),'lifetime handlercallback beforeclear')
        handlers_paths[str(i)]=[p-hpc for p in seq]
    check(hn[hpc+86]['imm']==8 and hn[hpc+90]['imm']==0 and hn[hpc+94]['imm']==4,'lifetime metadataread/twoclearwords')
    check(pn[pp+202]['rs2']==pn[pp+216]['rs2']==21 and cn[cpc+146]['imm']==4,'lifetime sharedmetadata0 join')
    check(Pslot not in (T,M+76) and T==previous.core.DETAILS[index][4],'lifetime distinctslot roles')
    check(pn[pp+74]['imm']+0x20003000==M+68 and pn[pp+140]['imm']+0x20003000==T,'lifetime producer clock/fallback globals')
    reduced={p:list(q) for p,q in pe.items()};reduced[pp+144]=[pp+152];pr=previous.reach(reduced,pp)
    ac={p:list(q) for p,q in ae.items()};ac[apc+88]=[apc+26];ac_reach=previous.reach(ac,apc)
    check(pp+150 not in pr and {p-pp for p in pr if pn[p]['op'] in ('jal','jalr','call_indirect')}=={88,130} and apc+96 not in ac_reach,'lifetime zeroTclosedcalls')
    failure=until(reduced,pp,{pp+38:pp+70,pp+116:pp+118,pp+134:pp+136})
    check(pp+160 in failure and pn[pp+160]['imm']==11 and not any(pn[p]['op']=='store' and pn[p]['rs1']!=2 and pn[p]['imm']!=524 for p in failure),'lifetime failedproducer no node/recordstores')
    return {'label':init.binding.PROFILES[index][0],'metadata_base':M,'arena_pointer_slot':Pslot,'failure_slot':T,'list_head_slot':M+76,
      'reused_bodies':{'producer':{k:pb[k] for k in ('start','bytes','sha256')},'consumer':{'RAM_entry':cpc,'source':src,'bytes':288,'sha256':cb['sha256']},'event':{k:eb[k] for k in ('start','bytes','sha256')},'handler0':{k:hb[k] for k in ('start','bytes','sha256')},'release':{'RAM_entry':fpc,'source':release.DETAILS[index][0],'bytes':212,'sha256':release.DETAILS[index][-1]}},
      'producer_first_group_walks':producer_paths,'consumer_walks':selected_consumer,'event_walks':eventpaths,'handler0_singlebit_walks':handlers_paths,
      'nominal_allocate_offsets':[p-apc for p in ar],'nominal_release_offsets':[p-fpc for p in fr],
      'nominal_retained_heap_globals':heapglobals,
      'zero_T_producer_failure_offsets':[p-pp for p in failure],'zero_T_producer_reachable_offsets':sorted(p-pp for p in pr),
      'roundtrip_premises':'retainedglobal smallhead=A200043ac,largehead=B200045ac,end/sentinel=E2000b184;A.size504,tag0,nextB;request16,tagff00;afterfit freeR=A24,size480,tag0,nextB;allheapglobals/headers/links/accounts retained; noalias/IRQ/writers;Q=A8 isexactownedpayload',
      'roundtrip':'alloc splits504 into16+8+480,account-24;freeQ clearsowner tag,mergesnextR,restoresA.size504,A.nextB,account+24mod65536. No Qpayload orarena word erasedbyselectedheaderstores',
      'release_GPR_writes':[6,10,11,12,13,14,15,16,17,28],'release_preservation':'no calls/frame/S/SP/RAwrites; consumerS8capturednext locallypreserved, no generalownership/lifetimeguarantee',
      'one_shot_join':'producerentryA4=0 preserved ->Q4=0,record8=0;consumerdue eventhelperthenQ4fresh0 unlinks/releasesQ; lateractualhandler0(group0,singlebit1<<i) callsrecord thenfreshflag0 clearsrecord0/4 onlyifsamearena/S2/index/frame/metadata preserved',
      'separate_lifetimes':'releaseQ isnot clearingrecord; clearrecord0/4 isnot freeingQ/arena/payloadargument; record8notcleared; eventpostingisnotdirectAPPcallbackinvocation',
      'counterpaths':['mask0 ->unlink/releasewithnoeventcall andnorecordclear','due Q4=0 +eventhelperreject3 ->unlink/releaseanyway,norecordclear','repeatQ4nonzero ->updatedeadline/retainQ; recordretentionindependentlyfreshrecord8'],
      'normalproducer_status':'entrycallback0 ->2;all16initialcallbackwordsnonzero ->8;allocation0 ->11 afteroptionalhook;successfulnode/recordwrites ->0. Not eventdelivery',
      'zero_T_closure':'matchingpreclock191c6,retainedT0,validframe/control/heap/arena separation ->corefallback +producerfallback excluded; producerfailure11 hasnoallocatedQ/recordwrites. Do notextendtoRAMthresholdtailwithoutitscalleeTpreservation',
      'handler_scope':'kind0 only;group0 andsameP snapshots needed;postcallback flag addressomitsgroupterm. Firstlowsetbitonly;otherpendingbits/othergroups needseparateanalysis',
      'call_graph':'producer->reader/core(+failurehookifTnonzero);consumer->reader/event/privatefree;handler0->selectedAPPcallback opaque. Theseareseparateentries, not synchronousfullpipeline',
      'actual_binding/dispatch/atomics/listtermination/record_callback_or_argumentownership_proved':False,'target_execution_or_emulation':False}


def derive(image,carriers,header,coverage):
    previous.derive(image,carriers,header,coverage)
    return {'schema':'TSL9-record-node-lifecycle-static-v1','APP_sha256':sha256(image).hexdigest(),'profiles':[profile(d,i) for i,d in enumerate(carriers)],'integer_domains':domains(),
      'new_original_bytes':0,'scope':'reused268Bproducer/288Bconsumer/64Bevent/130Bhandler0/212Bprivatefree perprofile; new conditionalroundtrip/separate-lifetime certificates',
      'remaining':['thresholdhelper568f6/56a36 andotherfallbacktails','actualouterdispatch/APPcallback,global/arena/heapwriters,objectlifetimes'],
      'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    mutations=0
    for i,data in enumerate(carriers):
        F=producer.init.DETAILS[i][5];M=F-80;Pslot=F+64;pp,pd=producer.DETAILS[i];src,epc,ch,eh=consumer.DETAILS[i];hp=producer.post.DETAILS[i][4]
        cases=(('producer',pp,pp,268,(74,118,124,140,144,150,174,178,192,196,200,202,208,212,216,220)),
          ('consumer',src,consumer.ENTRY,288,(66,76,80,84,86,130,134,136,142,146,148,150,174,230,236)),
          ('event',epc,epc,64,(24,46)),('handler',hp,hp,130,(26,40,58,64,70,80,86,90,94,102)),
          ('free',release.DETAILS[i][0],release.ENTRY,212,(64,74,104,118,142,152,190,192)))
        for part,sourcepc,pc,size,offsets in cases:
            raw=init.binding.take(data,sourcepc,size);ns=release.decode(raw) if part=='free' else handlers.decode(raw,pc)
            for off in offsets:
                z=ns[pc+off]['size'];buf=bytearray(raw);buf[off:off+z]=(int.from_bytes(buf[off:off+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
                try:
                    if part=='producer':producer.body(buf,pc,M,Pslot,pd)
                    elif part=='consumer':consumer.consumer_body(buf,M,F,epc,ch)
                    elif part=='event':consumer.event_body(buf,pc,M,eh)
                    elif part=='handler':handlers.body(buf,pc,0,Pslot-0x20003000,init.binding.word(data,0x40068),handlers.DIGESTS[i][0])
                    else:free_body(buf,i)
                except RuntimeError as ex:check(any(s in str(ex) for s in ('producer','consumer','event helper','handler0','lifetime free')),'lifetime specifiedmutationguard '+str(ex))
                else:raise RuntimeError('lifetime mutation escaped')
                mutations+=1
    check(mutations==102,'lifetime mutationcensus');domains()
    print('PASS:102 lifecycle instruction mutations rejected;65511 split-size/65536 accounting/16 group0 cases;32 producer +32 handler +6 consumer +4 event walks')


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');o=p.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK identity')
    carriers=[]
    for label,folder,tail,z,digest in init.binding.PROFILES:
        data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidate identity '+label);carriers.append(data)
    raw_hex=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,raw_hex,sparse.parser())
    ledger=derive(image,carriers,header,coverage);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers);output=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'lifetime exactledger replay')
    print('PASS:conditional alloc/release headerinverse andnode-vs-record lifecycle;exactledger;0 newbodybytes')
    print('PASS:NO target execution/emulation;actualdispatch/callbackownership/listprogress/installedbindings UNPROVED')


if __name__=='__main__':main()
