"""Offline selected quotient and timer/lookup/wrapper composition proof.

All bodies are previously guarded. Only operands, finite graphs and closed
Euclidean scalar identities; no target ISA/register/RAM/MMIO/provider runner.
"""
import argparse,json
from hashlib import sha256
from pathlib import Path
import check_v4160_generator_static as previous
import check_v4160_timer_start_setup_static as timer
import check_v4160_registration_return_chain_static as whole
import check_v4160_config_arithmetic_static as config

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-timer-wrapper-composition-static.json')
PATH=(0,2,4,6,8,12,16,18,456,460,462,466,470,472,36,40,44,46,48,50,54,56,58,62,66,70,74,78,82,86,90,92,96,100,104,106,110,130,134,138,140,144,148,152,154,158,180,182,184,186)
CHOICES={8:12,12:16,18:456,462:466,56:58,110:130,158:180}
TABLE=bytes.fromhex('00010202030303030404040404040404')
MAX_N=65535*131070+800


def selected(raw,table,index):
    pc=config.BASES[index];n=decode(raw,pc);expected=config.specs(pc)
    for o,f in {456:dict(op='addi',rd=14,rs1=0,imm=255),460:dict(op='mv',rd=13,rs2=12),
      462:dict(op='bgeu',rs1=14,rs2=12,target=pc+36),466:dict(op='srli',rd=13,rs1=12,imm=8),
      470:dict(op='li',rd=15,imm=8),472:dict(op='jump',target=pc+36)}.items():expected[pc+o]=f
    for o in PATH:init.g(n,pc+o,'compose arithmetic operand '+hex(o),**expected[pc+o])
    check(len(table)==16,'compose tablelength')
    for j,b in enumerate(table):check(b==TABLE[j],'compose tablebyte '+str(j))
    general=whole.arithmetic(raw,pc);e,_=whole.graph(n,pc,'compose general arithmetic')
    for a,z in zip(PATH,PATH[1:]):check(pc+z in e[pc+a],'compose selectededge')
    check(e[pc+PATH[-1]]==[] and len(set(PATH))==50,'compose closed50node path')
    check({p-pc for p in (pc+o for o in PATH) if n[p]['op'] in whole.CONTROL_OPS and len(e[p])>1}==set(CHOICES),'compose selected branchcensus')
    check(all(pc+q in e[pc+p] for p,q in CHOICES.items()),'compose branchchoices membership')
    writes=sorted({n[pc+o]['rd'] for o in PATH if n[pc+o].get('rd',0)})
    check(writes==[6,10,11,12,13,14,15,16,17] and [o for o in PATH if n[pc+o]['op']=='load']==[46],'compose localpreservation/lookupread')
    check(not any(n[pc+o]['op'] in ('store','jal','jalr','call_indirect') for o in PATH),'compose noframe/stores/calls')
    check(pc+36+4096-1506==pc+0xa42 and table[6]==3,'compose normalizationtable index6')
    return {'entry':pc,'whole_bytes':914,'whole_sha256':general['sha256'],'whole_GPR_definitions':general['encoded_GPR_definitions'],
      'selected_offsets':list(PATH),'selected_branch_successors':CHOICES,'selected_instructions':50,'selected_CFG_closed_acyclic':True,
      'instructions':[n[pc+o] for o in PATH],'selected_GPR_definitions':writes,
      'lookup':{'table':pc+0xa42,'prefix_bytes':table.hex(),'selected_index':6,'selected_address':pc+0xa48,'selected_value':3},
      'contract':'onlyD1600,N=H*K+800,H_U16,K0..131070 ->A0=floor(N/1600),A1=0; notgeneralquotient/remainderABI',
      'whole_general_numeric_quotient_proved':False,'target_execution_or_emulation':False}


def digits(value):
    # Closed Euclidean digit identities, independent of bytes, PCs or registers.
    check(0<=value<=MAX_N,'compose scalarbound')
    upper=value>>11;lower=(value&2047)<<21
    first,rem=divmod(upper,51200);merged=(rem<<16)|(lower>>16)
    check(merged==32*(value%104857600) and merged<51200*65536<1<<32,'compose mergedidentity')
    second,tail=divmod(merged,51200);quotient=(first<<16)|second
    check(0<=first<=81 and 0<=second<=65535 and quotient==value//1600<=5368545,'compose quotientidentity')
    check((tail<<16)==(value%1600)<<21 and (lower&65535)==0,'compose normalizedresidue')
    return quotient


def domains():
    check(MAX_N==8589673250 and MAX_N<2*(1<<32),'compose highnum01')
    check(1600>>8==6 and TABLE[6]==3 and 32-(8+3)==21,'compose normalization')
    check(1600<<21==0xc8000000 and (1600<<21)>>16==51200 and ((1600<<21)&65535)==0,'compose zero correctionproducts')
    cases=0
    for h in range(65536):
        for k in (0,1,16,65537,131070):digits(h*k+800);cases+=1
    boundaries=0
    for q in (0,1,65535,65536,5368545):
        for r in range(1600):
            v=1600*q+r
            if v<=MAX_N:digits(v);boundaries+=1
    check((cases,boundaries)==(327680,7651),'compose scalarcase census')
    admitted=sum(t<c for t in range(256) for c in range(256));check(admitted==32640,'compose taskadmission65536cases')
    check((65536&65535)!=65536 and (16&65535)==16,'compose eventwidth witness/currentmask')
    return {'H_K_selected_cases':cases,'quotient_remainder_boundary_cases':boundaries,'task_count_pairs':65536,'admitted_byte_pairs':admitted,
      'selected_domain':{'H':[0,65535],'K':[0,131070],'N_min':800,'N_max':MAX_N,'N_highword':[0,1],'D':1600},
      'normalization':{'index':6,'tablevalue':3,'shift':21,'normalizedD':0xc8000000,'high_digit':51200,'low_digit':0},
      'proof':'U=N>>11;L=(Nmod2048)<<21;q1=Udiv51200;r1=Umod51200;m=(r1<<16)|(L>>16)=32*(Nmod104857600);q0=mdiv51200;Q=(q1<<16)|q0=Ndiv1600;bothlowdigitcorrectionproducts0',
      'selected_outputs':{'A0':'floor((H*K+800)/1600)','A0_range':[0,5368545],'A1':0,'A6':'normalizedresidue=(Nmod1600)<<21, notageneralremainderABI'},
      'three_H_snapshots':'timerH0,timerH1,wrapperH2 freshfromsameaddress;notassertedequal','general_K_U32_or_other_divisors_proved':False,
      'actualinputreachability/physicalunits/probability_proved':False}


def last_definitions(nodes,edges,terminal,register):
    pred={p:[] for p in edges}
    for p,qs in edges.items():
        for q in qs:pred[q].append(p)
    found=set();seen=set();pending=pred[terminal][:]
    while pending:
        p=pending.pop()
        if p in seen:continue
        seen.add(p);v=nodes[p]
        if v.get('rd')==register:found.add(p)
        else:pending.extend(pred[p])
    return found


def compose(data,index):
    pc=timer.DETAILS[index][0];service=timer.body(init.binding.take(data,pc,332),'service',index);n={v['pc']:v for v in service['instructions']};e=timer.edges(n)
    mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);m=mapping['first_copy'];lsource=int(m['source'],16)+0x20000314-int(m['destination'],16)
    lookup=timer.body(init.binding.take(data,lsource,30),'lookup',index)
    wrapper=previous.previous.body(init.binding.take(data,0x43932+140*index,118),'event_wrapper',index)
    wn={v['pc']-wrapper['start']:v for v in wrapper['instructions']};H=0x2000323c+80*index
    check(0x20003000+timer.DETAILS[index][3]+8==H and wn[0x38]['imm']+0x20003000==H,'compose threefreshHaddresses')
    check(n[pc+126]['target']==n[pc+194]['target']==wn[0x54]['target']==config.BASES[index],'compose threearithmetic targetjoins')
    check(n[pc+120]['imm']==n[pc+170]['imm']==wn[0x3c]['imm']==1600,'compose threedivisors')
    check(last_definitions(n,e,pc+160,10)=={pc+138,pc+244} and n[pc+138]['imm']==0 and n[pc+244]['imm']==1,'compose allnormalfirstservice replies01')
    common={44:48,56:70,130:162,208:212,212:220};cases={
      'task_reject':({44:60},0),'service_null':({44:48,56:60},0),'threshold_reject':({44:48,56:70,130:134},0),
      'existing_match':(common|{232:234},1),
      'allocation_failure_nohook':(common|{232:248,266:268,276:60},0),
      'allocation_failure_hook':(common|{232:248,266:268,276:278},0),
      'new_empty':(common|{232:248,266:286,294:296},1),
      'new_append_one':(common|{232:248,266:286,294:324,326:328},1)}
    paths={}
    for name,(choices,reply) in cases.items():
        path=timer.chain(e,pc,{pc+a:pc+z for a,z in choices.items()});seq=[int(v,16)-pc for v in path]
        check(seq[-1]==160 and all(pc+b in e[pc+a] for a,b in zip(seq,seq[1:])),'compose validservice walk')
        definitions=[o for o in seq if n[pc+o].get('rd')==10];last=n[pc+definitions[-1]]
        check(last['op']=='li' and last['imm']==reply,'compose selectedreply immediate')
        if name.startswith('new_'):
            publish=296 if name=='new_empty' else 328
            check(seq.index(publish)<seq.index(302)<seq.index(316),'compose publication precedesinitialization')
        paths[name]={'offsets':seq,'local_reply':reply}
    check(n[pc+316]['imm']==4 and n[pc+316]['rs2']==0 and wn[0x58]['imm']==4 and wn[0x58]['rs2']==10,'compose samenode4 clear/overwrite operands')
    return {'label':init.binding.PROFILES[index][0],'reused_service':{k:service[k] for k in ('start','bytes','sha256')},
      'reused_lookup':{**{k:lookup[k] for k in ('start','bytes','sha256')},'source':lsource,'first_copy':m},
      'reused_wrapper':{k:wrapper[k] for k in ('start','bytes','sha256')},'selected_service_walks':paths,
      'H_address':H,'fresh_H_snapshots':['timerH0 beforeadmissionarithmetic','timerH1 afterclockcallback','wrapperH2 aftersecondlookup'],
      'selected_arithmetic_formula':'eachQi=floor((Hi*K+800)/1600), range0..5368545; Hi independentlyfresh U16; currentcallback K0..131070',
      'admission':'unsignedfulltask<freshU8[C1], freshclockservice nonnull, Q0<=(capturedwordW0-30000000)mod2^32',
      'deadline':'readerreplyR + Q1 mod32; one subtractionoffreshW1 ifcarry orsum>=W1; notgeneralmodulo orunitproof',
      'lookup_contract':'fulltask == U8[node0] AND fullevent == U16[node2]; nextU32[node12], headfreshC76. NoA2read; noS/SP/RAwrites/stores/calls. Traversalmaycycle',
      'widths':'admittedtask0..254 fitsbyte; newnode storeslow16event butlookupcomparesfullwordevent. Currentevent16fits; e.g65536 doesnot',
      'service_replies':[0,1],'wrapper_replies':'secondlookupRnull ->8; nonnull ->0 afterQ2store; firstservice replyignored',
      'reply_counterexamples':['firstservice0 withpreexistingsecondlookupmatch ->wrapper0','firstservice1 withevent65536 truncatednewnode ->secondlookupmiss/wrapper8 underotherwiseempty stablelist'],
      'newnode':'allocatorrequest16/tagff00|tasklow8; next0,deadline+8,task+0,flag1+1,eventlow16+2,word4=0. Head/next publishespointerBEFOREfields initialized',
      'same_node_join':'withmatchingproviders,finitevalidstablelist/originalmiss,nonaliasfreshP16,keys/head/next/lifetime retained, currentevent16 ->secondlookupP; wrapperP4=floor((H2*K+800)/1600),maystill0',
      'existing_node_join':'withfirstmatchidentity/list/key/lifetime preservation, timer updatesP8; wrapperupdatesP4, otherlocalnodefieldsnotwrittenbywrapper',
      'arith_preservation':'matchedselectedleaf hasnostores/calls/frame andnoS/SP/RAdefinitions, so locallykeepswrapperR/S1K andtimerliveS; code/table/ordinaryaccess premisesremain',
      'controlwords':'outer/inner eachcapture/clear/FENCE.I/restoreownsnapshot; innerread0/coherence/IRQcriticalsection/atomicity notinferred',
      'unclosed':['clock/failurehooks/allocatorfallback effects andpointerretention','actualproviderinstallation,adversealiases/IRQ/DMA/writers,objectlifetime','listprogress,postereventdelivery/asynccompletion'],
      'target_execution_or_emulation':False}


def derive(image,carriers,header,coverage):
    previous.derive(image,carriers,header,coverage);profiles=[]
    for i,data in enumerate(carriers):
        pc=config.BASES[i];ar=selected(init.binding.take(data,pc,914),init.binding.take(data,pc+0xa42,16),i)
        profiles.append({**compose(data,i),'arithmetic_selected_domain':ar})
    return {'schema':'TSL9-timer-wrapper-composition-static-v1','APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'integer_domains':domains(),
      'new_original_bytes':0,'scope':'reusecomplete332Btimer/30Blookup/118Bwrapper/914Barithmetic plus16Btableprefix perprofile; new50nodeD1600 quotient andsame-node composition certificates',
      'remaining':['clock/failurehook/allocatorfallback binding andeffects','actualglobal/list/key/lifetime preservation; physicalcontrol/IRQ/eventeffects'],
      'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    instructions=tables=joins=0
    for i,data in enumerate(carriers):
        pc=config.BASES[i];raw=init.binding.take(data,pc,914);tab=init.binding.take(data,pc+0xa42,16);nodes=decode(raw,pc)
        for off in PATH:
            v=nodes[pc+off];z=v['size'];buf=bytearray(raw);buf[off:off+z]=(int.from_bytes(buf[off:off+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
            try:selected(buf,tab,i)
            except RuntimeError as ex:check(str(ex).startswith('compose arithmetic operand '),'compose selectedmutation guard '+str(ex))
            else:raise RuntimeError('compose selectedmutation escaped')
            instructions+=1
        for off in range(16):
            buf=bytearray(tab);buf[off]^=1
            try:selected(raw,buf,i)
            except RuntimeError as ex:check(str(ex)=='compose tablebyte '+str(off),'compose tablemutation guard')
            else:raise RuntimeError('compose tablemutation escaped')
            tables+=1
        groups=(('service',timer.DETAILS[i][0],332,(98,108,112,120,126,194,234,308,316)),
          ('lookup',0x40584+64*i,30,(16,20,22)),('event_wrapper',0x43932+140*i,118,(0x18,0x26,0x46,0x4e,0x54,0x58,0x5a,0x70)))
        for part,src,size,offsets in groups:
            original=init.binding.take(data,src,size);base=0x20000314 if part=='lookup' else src;ns=decode(original,base)
            for off in offsets:
                z=ns[base+off]['size'];buf=bytearray(original);buf[off:off+z]=(int.from_bytes(buf[off:off+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
                try:
                    if part=='event_wrapper':previous.previous.body(buf,part,i)
                    else:timer.body(buf,part,i)
                except RuntimeError as ex:check(str(ex).startswith(('tail event_wrapper operand ','timer '+part+' operand ')),'compose joinmutation guard '+str(ex))
                else:raise RuntimeError('compose joinmutation escaped')
                joins+=1
    check((instructions,tables,joins)==(100,32,40),'compose mutationcensus');domains()
    print('PASS:100 selectedinstruction +32 tablebyte +40 join mutations rejected;327680 H/K cases;7651 quotientboundary cases;65536 task/count pairs;16 service walks')


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
    else:check(OUT.read_bytes()==output,'compose exactledger replay')
    print('PASS:D1600 closed50node quotient path; timer/lookup/wrapper same-node4 certificate;exact ledger;0 new bodybytes')
    print('PASS:NO target execution/emulation;actualbindings/lifetimes/physicaleffects/calleecompletion UNPROVED')


if __name__=='__main__':main()
