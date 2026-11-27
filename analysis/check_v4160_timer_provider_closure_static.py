"""Offline conditional clock/zero-fallback provider call-graph closure.

Only guarded original bodies, graphs, source intervals and scalar algebra.
No target ISA, register/RAM machine, clock, allocator, MMIO or provider run.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_timer_wrapper_composition_static as previous
import check_v4160_service_provider_link_static as service
import check_v4160_config_buffer_source_static as source
import check_v4160_fallback_initialization_static as fallback
import check_v4160_config_gates_static as gates
import check_v4160_app_config_source_static as appsource
import check_v4160_constructor_publication_chain_static as publication
import check_v4160_comparator_tail_static as wrappers

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
timer,core=previous.timer,previous.timer.core
OUT=Path(__file__).with_name('v4160-timer-provider-closure-static.json')


def graph(nodes):
    e={}
    for p,d in nodes.items():
        op=d['op'];q=[] if op=='jr' else [d['target']] if op=='jump' else [p+d['size'],d['target']] if op in ('bne','beq','beqz','bnez','bgeu','bltu','bge','blt') else [p+d['size']]
        check(all(v in nodes for v in q),'closure graph no cuts');e[p]=q
    return e


def reach(edges,start):
    seen=set();pending=[start]
    while pending:
        p=pending.pop()
        if p in seen:continue
        seen.add(p);pending.extend(edges[p])
    return seen


def walk(edges,start,choices):
    seq=[];p=start
    while True:
        check(p not in seq,'closure selectedwalk acyclic');seq.append(p);qs=edges[p]
        if not qs:return seq
        p=choices[p] if p in choices else qs[0];check(p in qs,'closure selectededge')


def core_body(raw,index):
    check(raw[18:22]==bytes.fromhex('0f100000'),'closure core fencebytes')
    n=core.decode(raw);expected=core.specs(core.DETAILS[index]);check(n.keys()==expected.keys(),'closure core boundaries')
    for p,f in expected.items():core.message.guard(n,p,'closure core operand '+hex(p-core.ENTRY),**f)
    check(sha256(raw).hexdigest()==core.DETAILS[index][-1],'closure core identity')
    return n,graph(n)


def reader(raw):
    b=service.body(raw,'reader',0x191c6,service.APP_HASHES[1]);n={d['pc']:d for d in b['instructions']};e=graph(n);pc=0x191c6
    check(not b['calls'] and not any(v['op']=='store' for v in n.values()),'closure reader no calls/stores')
    check(sorted({v['rd'] for v in n.values() if v.get('rd',0)})==[10,11,12,13,14,15],'closure reader allS/GP/SP/RA keptlocally')
    check([p-pc for p,d in n.items() if d['op']=='bne']==[16,36,56,80],'closure four reader retries')
    paths={}
    for name,last in (('same_high',84),('changed_high',64)):
        s=walk(e,pc,{pc+16:pc+20,pc+36:pc+40,pc+56:pc+60,pc+60:pc+last,pc+80:pc+84})
        check(s[-1]==pc+88,'closure reader soleRET');paths[name]=[p-pc for p in s]
    return {'start':pc,'bytes':90,'sha256':b['sha256'],'GPR_writes':[10,11,12,13,14,15],'selected_walks':paths,
      'preserved_locally':'allS/GP/SP/RA/A6/A7; no stack/calls/stores/direct pointer retention',
      'inputs':'entryA0 ignored beforeoutput; timer incomingquotient isnotanobjectpointerargument',
      'reads':'paired U16 at40002818(H0),4000281c(L0),40002818(H1);ifH0!=H1 fourthpair4000281c(L1)',
      'return':'(H1<<16)|L0 ifH0==H1 else(H1<<16)|L1','final_high_recheck_after_L1':False,
      'hardware/coherent_counter/monotonicity/termination_proved':False}


def domains():
    count=0
    for h in range(65536):
        for lo in (0,1,65535):
            w=(h<<16)|lo;check(w>>16==h and w&65535==lo,'closure reader unsignedpacking');count+=1
        n=h*192000+800;u=n>>11;l=(n&2047)<<21;q1,r1=divmod(u,51200);m=(r1<<16)|(l>>16);q0=m//51200
        check(n>>32<=2<1600 and m==32*(n%104857600) and m<0xc8000000,'closure startup normalization/merge')
        check(((q1<<16)|q0)==n//1600==120*h and 0<=q1<=119 and q0<=65535,'closure startup quotient120H')
    check(65535*192000+800==12582720800 and 65535*120==7864200,'closure startup extrema')
    period=0xffffffff;delta=1920000
    for r in (0,1,period-delta-1,period-delta,period-delta+1,period-1,period):
        total=r+delta;s=total&0xffffffff;deadline=(s-period)&0xffffffff if s<delta or s>=period else s
        check(deadline==total%period and 0<=deadline<period,'closure nominal single-subtraction deadline')
    check(0xfe363c7f==(period-30000000)&0xffffffff and 1920000<=0xfe363c7f,'closure nominaladmission quotient')
    check(period+1==1<<32 and 0<delta<period and period+delta<2*period,'closure nominal modulo one-subtraction bounds')
    return {'reader_packing_cases':count,'startup_H_cases':65536,'startup_K':192000,'startup_N_max':12582720800,'startup_N_highword':[0,2],
      'same50node_D1600_path':'highN<=2<1600; normalizedD c8000000,digits51200/0;correctionproducts0 ->A0=120*H,A1=0',
      'startup_quotient_range':[0,7864200],'nominal_retained_clock_config':publication.CONFIG.hex(),'nominal_H':16000,'nominal_period':period,
      'nominal_both_quotients':1920000,'nominal_threshold':0xfe363c7f,'nominal_deadline':'(readerreplyR+1920000)mod(2^32-1) onlyifretainedperiodffffffff/H16000 andnormalclosedpath',
      'no_actualsource_reachability/physicalunit/whole_startup_completion_proof':True}


def source_witnesses(image,data,index):
    builder=source.app_contract(image[source.APP_PC-0x8000:source.APP_PC-0x8000+source.APP_SIZE])
    uid=source.uid_contract(image[source.UID_PC-0x8000:source.UID_PC-0x8000+source.UID_SIZE])
    fields={x for _,_,o,z in source.DIRECT for x in range(o,o+z)}|set(range(8,14))|set(range(40,46))
    check(fields.isdisjoint(range(68,72)) and 16+52==68,'closure APP64 field52 isSP68..71')
    fd=fallback.DETAILS[index];cfg=fd[2];F=fd[5];T=F+52
    raw,n,e,defaults=fallback.config_contract(data,cfg,F,fd[9],fd[10])
    check(all(r['destination_field']+r['bytes']<=52 or r['destination_field']>=56 for r in defaults),'closure defaults excludeF52')
    check(T==core.DETAILS[index][4]==0x20003000+timer.DETAILS[index][5],'closure same failure/allocator word')
    cp,size=gates.DETAILS[index][:2];consumer=gates.body(init.binding.take(data,cp,size),index)
    G=int(consumer['copied_config'],16);S=int(consumer['service_word'],16)
    check(G==F+72 and S==F-12 and G+8==0x2000323c+80*index,'closure clock/failure separate geometry')
    check(consumer['V140_unconditional_pre_hook_clear'] in (None,hex(F+88)),'closure V140 extraclear separate')
    check(init.binding.word(data,0x40074)==cp and init.binding.word(data,0x400a4)==cfg,'closure candidate config slots')
    construct=appsource.body(image[0x19b56-0x8000:0x19bd4-0x8000],'construct')
    wrapper=appsource.body(image[0x19b16-0x8000:0x19b56-0x8000],'wrapper');wn={d['pc']:d for d in wrapper['instructions']}
    check(wn[0x19b48]['imm']+wn[0x19b4c]['imm']==192000 and wn[0x19b50]['imm']==8192 and wn[0x19b54]['rs1']==6,'closure startup tailargs')
    return {'config64_builder':{k:builder[k] for k in ('start','bytes','sha256')},'UID':{k:uid[k] for k in ('start','bytes','sha256')},
      'config64_destination':F,'failure_slot':T,'source_field52':'matchingclear64(C=APP_SP+16,0,64) +localdisjointstores/UIDloop ->SP68..71 zero; configcopy64 transfersC52..55 toF52..55',
      'resident_config':{'entry':cfg,'bytes':228,'sha256':sha256(raw).hexdigest(),'default_stores':defaults},
      'clock_constructor':{k:construct[k] for k in ('start','bytes','sha256')},'startup_wrapper':{k:wrapper[k] for k in ('start','bytes','sha256')},
      'clock_config':{'candidate40074':cp,'copied16base':G,'published_service_word':S,'conditional16source':publication.CONFIG.hex(),'clock_reader_value':0x191c6},
      'role_addresses':{'timer_context':F-80,'config64':F,'optional_apply_hook':F+48,'failure_allocator_fallback':T,'clock_service':S,'clock16copy':G,'wordsource_primary':F+36,'clock_callback':F+68},
      'startup_tail':'afterconstructorreturn, freshtaskbyte[thenliveGP388],A1=8192,A2=192000;freshT1[thenliveS1+88];JR T1 afterrestoringframe; actual40058onlyifS1=40000',
      'retention_gap':'fullsourcefunctions andcopy/publication areexisting witnesses; allinterveningfieldwrites/alias/frame/code/providerpreservation stillpremises. Config64 bulkcopycanrewriteF52; startupzeroisnotalater-valueproof',
      'source32bit_pointers':'clockcopiedcodevalue191c6 isdistinctfromshort-livedstacksourceaddress; nooverall externalretention guarantee'}


def profile(image,data,index):
    witnesses=source_witnesses(image,data,index);T=witnesses['failure_slot'];S=witnesses['clock_config']['published_service_word'];pc=timer.DETAILS[index][0]
    sb=timer.body(init.binding.take(data,pc,332),'service',index);sn={v['pc']:v for v in sb['instructions']};se=graph(sn)
    check(sn[pc+52]['imm']+0x20003000==S and sn[pc+52]['rd']==23 and sn[pc+162]['rs1']==23,'closure heldclockpointer source')
    check(sn[pc+272]['imm']+0x20003000==T,'closure timerfallback source')
    original_core=init.binding.take(data,core.DETAILS[index][0],208);cn,ce=core_body(original_core,index);cc=core.ENTRY
    check(cn[cc+84]['imm']+0x20003000==T,'closure corefallback source')
    reduced_core={p:list(q) for p,q in ce.items()};reduced_core[cc+88]=[cc+26];cr=reach(reduced_core,cc)
    reduced_service={p:list(q) for p,q in se.items()};reduced_service[pc+56]=[pc+70];reduced_service[pc+276]=[pc+60];sr=reach(reduced_service,pc)
    check(cc+96 not in cr and not any(cn[p]['op'] in ('jal','jalr','call_indirect') for p in cr),'closure no allocator fallbackcall')
    check(pc+282 not in sr and {p-pc for p in sr if sn[p]['op'] in ('jal','jalr','call_indirect')}=={126,162,194,228,262},'closure timer onlyfive resolvedcalls')
    check(len(cr)==67 and len(sr)==109,'closure specialized graphcounts')
    prefix=timer.chain(se,pc,{pc+44:pc+48,pc+56:pc+70,pc+130:pc+162},cut=pc+162)
    check([int(p,16)-pc for p in prefix if sn[int(p,16)].get('rd')==23]==[52],'closure heldclockpointer unchangedbeforecall')
    core_zero=walk(reduced_core,cc,{cc+22:cc+24,cc+24:cc+38,cc+56:cc+60,cc+76:cc+80})
    check(cc+84 in core_zero and core_zero[-1]==cc+202,'closure zero nofit corewalk')
    suffix=core_zero[core_zero.index(cc+84):]
    check(all(cn[p]['op']!='store' or (cn[p]['rs1']==15 and cn[p]['imm']==524) for p in suffix),'closure zero coreexit onlycontrolstore')
    check(all(sn[pc+o]['op']!='store' for o in (266,268,272)),'closure timerreload nointerveningstore')
    first=init.binding.profile(data,init.binding.PROFILES[index][0])['first_copy'];lsrc=int(first['source'],16)+0x20000314-int(first['destination'],16)
    lookup=timer.body(init.binding.take(data,lsrc,30),'lookup',index)
    ev=wrappers.body(init.binding.take(data,0x43932+140*index,118),'event_wrapper',index)
    check([c['target'] for c in ev['calls']]==[hex(pc),'0x20000314',hex(previous.config.BASES[index])],'closure outerevent edges fromoriginal calls')
    ar=previous.selected(init.binding.take(data,previous.config.BASES[index],914),init.binding.take(data,previous.config.BASES[index]+0xa42,16),index)
    check(all(v not in ar['whole_GPR_definitions'] for v in (1,2,3,8,9,*range(18,28))),'closure arithmeticallS/GP/SP/RA kept')
    graph_calls={'event_wrapper':['timer','lookup','arithmetic'],'APP_timer_tail':['timer'],'timer':['arithmetic','reader','lookup','allocator'],'reader':[],'lookup':[],'allocator':[],'arithmetic':[]}
    frames={'event_wrapper':32,'APP_timer_tail':0,'timer':48,'reader':0,'lookup':0,'allocator':16,'arithmetic':0}
    check(ev['instructions'][0]['imm']==-32 and sn[pc]['imm']==-48 and cn[cc]['imm']==-16,'closure frames tiedtooriginal prologues')
    cut={p:([] if p==pc+228 else list(q)) for p,q in se.items()};before_lookup=reach(cut,pc)
    check(all(sn[p]['rs1']==2 or sn[p]['imm']==524 for p in before_lookup if sn[p]['op']=='store'),'closure beforeH1/W1 onlyframe/control stores')
    def depth(v,active=()):
        check(v not in active,'closure acycliccallgraph');return frames[v]+max((depth(q,active+(v,)) for q in graph_calls[v]),default=0)
    check(depth('event_wrapper')==96 and depth('APP_timer_tail')==64,'closure boundedsubgraph frames')
    check(witnesses['clock_config']['published_service_word']==S and init.binding.word(data,0x40058)==pc,'closure candidate tailtarget')
    return {'label':init.binding.PROFILES[index][0],'sources':witnesses,'reused_bodies':{'timer':{k:sb[k] for k in ('start','bytes','sha256')},'lookup':{k:lookup[k] for k in ('start','bytes','sha256')},
        'event_wrapper':{k:ev[k] for k in ('start','bytes','sha256')},'allocator':{'RAM_entry':cc,'source':core.DETAILS[index][0],'bytes':208,'sha256':sha256(original_core).hexdigest()},'arithmetic50':{'entry':ar['entry'],'whole_sha256':ar['whole_sha256'],'selected_offsets':ar['selected_offsets'],'lookup':ar['lookup']}},
      'specializations':{'observed_captured_clockword':0x191c6,'fallback_at_relevantloads':0,'core_removed_edge':[88,90],'timer_removed_edge':[276,278],
        'core_reachable_offsets':sorted(p-cc for p in cr),'timer_reachable_offsets':sorted(p-pc for p in sr),'core_zero_return_walk':[p-cc for p in core_zero],
        'clock_capture_prefix':[int(p,16)-pc for p in prefix]},'call_graph':graph_calls,'own_frames':frames,'conditional_live_frame_max':{'event_wrapper_subgraph':96,'APP_timer_tail_subgraph':64},
      'zero_retention':'beforecoresentinelread, searchonlyreads +ownframe/controlstores; fitbranch cannotrejoinfallback. Fromcorezeroreadthroughreturn onlycontrolstore,thentimernostorebeforereload. Withdisjointframe/control/slot andnoexternalwriters, retainedzero suppressesbothcalls',
      'nonzero_ABI_boundary':{'core':'A0=1,A1=fulltag OR(roundedR<<16),A2then-live;normalreplydiscarded/no retry','timer':'A0=4,A1=savedfulltask,A2then-live;normalreplydiscarded/no retry','same_slot_not_same_ABI':True},
      'nominal_startup_extra_premises':'constructor16copy retained(reader191c6,periodffffffff,H16000);taskadmitted; sourceF52zero retained; matchingcode/table; validfiniteheap/list asneeded; allstores/read/MMIO/framesnonalias andnoIRQ/DMA/reentry interference',
      'nominal_startup_conclusion':'K192000 ->Q0=Q1=1920000; admissionthresholdallows; H/periodunchangedbetweenreadsbecauseclosedprefixonlyframe/controlwrites. ClockR frompairedreader; deadline=(R+1920000)modffffffff. Allocation/nodeoutcome stillconditionalonheap/list',
      'boundary':'conditional staticcallgraph, notinstalledbinding orallwritersabsence. Localreader/list/searchloops canrunforever; no hardwarecriticalsection/coherence/purity/overallownership/asynccompletion proof',
      'other_consumers_of_same_failureword':'recordproducer43414/434a0 andmappedRAMtail alsoreadit; thisgraphisnotawholebinaryreader/writercensus','target_execution_or_emulation':False}


def derive(image,carriers,header,coverage):
    previous.derive(image,carriers,header,coverage)
    r=reader(image[0x191c6-0x8000:0x19220-0x8000]);profiles=[profile(image,d,i) for i,d in enumerate(carriers)]
    return {'schema':'TSL9-timer-provider-closure-static-v1','APP_sha256':sha256(image).hexdigest(),'reader':r,'profiles':profiles,'integer_domains':domains(),
      'new_original_bytes':0,'scope':'conditional reader191c6/fallback0 callgraph closure plusstartupK192000 same50-node quotient; allsourcebodies reused, no Ccoverage increase',
      'remaining':['sourcefield/slot retention andactualinstalledprofile','otherfallbackconsumers/nonzeroABIs/globalwriters','heap/list/node lifetimes,hardware/MMIO/progress/eventdelivery'],
      'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(image,carriers):
    nr=ns=nc=nt=nf=nw=0;raw=image[0x191c6-0x8000:0x19220-0x8000];nodes=decode(raw,0x191c6)
    for p,v in nodes.items():
        at=p-0x191c6;z=v['size'];buf=bytearray(raw);buf[at:at+z]=(int.from_bytes(buf[at:at+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
        try:reader(buf)
        except RuntimeError as ex:check(str(ex).startswith('service link reader operand '),'closure readermutation '+str(ex))
        else:raise RuntimeError('closure readermutation escaped')
        nr+=1
    for off in (4,8,24,28,44,48,68,72):
        buf=bytearray(raw);buf[off:off+4]=(int.from_bytes(buf[off:off+4],'little')^(1<<14)).to_bytes(4,'little')
        try:reader(buf)
        except RuntimeError as ex:check(str(ex)=='service reader unsigned halfword encodings','closure unsignedguard')
        else:raise RuntimeError('closure signmutation escaped')
        ns+=1
    for i,data in enumerate(carriers):
        for part,src,z,offs in (('core',core.DETAILS[i][0],208,(84,88,96)),('timer',timer.DETAILS[i][0],332,(52,272,276,282)),('config',fallback.DETAILS[i][2],228,(92,98,102))):
            original=init.binding.take(data,src,z);base=core.ENTRY if part=='core' else src;nn=core.decode(original) if part=='core' else decode(original,base)
            for off in offs:
                size=nn[base+off]['size'];buf=bytearray(original);buf[off:off+size]=(int.from_bytes(buf[off:off+size],'little')^(4 if size==2 else 1<<20)).to_bytes(size,'little')
                try:
                    if part=='core':core_body(buf,i)
                    elif part=='timer':timer.body(buf,'service',i)
                    else:
                        fd=fallback.DETAILS[i];mut=bytearray(data);mut[src-0x40000:src-0x40000+z]=buf;fallback.config_contract(mut,src,fd[5],fd[9],fd[10])
                except RuntimeError as ex:
                    expected='closure core operand ' if part=='core' else 'timer service operand ' if part=='timer' else 'config '
                    check(str(ex).startswith(expected),'closure expected bindingguard '+str(ex))
                else:raise RuntimeError('closure bindingmutation escaped')
                if part=='core':nc+=1
                elif part=='timer':nt+=1
                else:nf+=1
    wrapper=image[0x19b16-0x8000:0x19b56-0x8000];nn=decode(wrapper,0x19b16)
    for off in (42,50,54,58):
        size=nn[0x19b16+off]['size'];buf=bytearray(wrapper);buf[off:off+size]=(int.from_bytes(buf[off:off+size],'little')^(4 if size==2 else 1<<20)).to_bytes(size,'little')
        try:appsource.body(buf,'wrapper')
        except RuntimeError as ex:check('wrapper' in str(ex),'closure expected startupguard '+str(ex))
        else:raise RuntimeError('closure startupmutation escaped')
        nw+=1
    check((nr,ns,nc,nt,nf,nw)==(28,8,6,8,6,4),'closure mutationcensus');domains()
    print('PASS:28 reader/8unsigned/6core/8timer/6config/4startup mutations rejected;196608 readerpacking +65536 startupH cases;conditional DAG/96B64B framebounds')


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');o=p.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK identity')
    carriers=[]
    for label,folder,tail,z,digest in init.binding.PROFILES:
        data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidate identity '+label);carriers.append(data)
    raw_hex=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,raw_hex,sparse.parser())
    ledger=derive(image,carriers,header,coverage);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(image,carriers);output=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'closure exactledger replay')
    print('PASS:conditional clock191c6/fallback0 callgraph; startup quotient120H andnominaldeadline;exactledger;0 newbodybytes')
    print('PASS:NO target execution/emulation;actualinstalledbindings/globalretention/looptermination/physicaleffects UNPROVED')


if __name__=='__main__':main()
