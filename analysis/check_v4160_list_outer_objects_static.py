"""Offline outer constructors, handler joins and one complete clear tail.

Original operand/CFG and interval certificates only. No target ISA, mutable
RAM/register machine, allocator/fill/callback/provider or MMIO is executed.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_list_direct_callbacks_static as previous
import check_v4160_loaded_hook_sources_static as hooks

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-list-outer-objects-static.json')
PARTS=('outer128','outer148','clear','publish128','publish148')
STARTS=((0x5e8bc,0x57cbe,0x55330,0x60856,0x58ef2),(0x5e9a6,0x57dfe,0x553fa,0x60940,0x5903a))
SIZES=(148,154,84,68,34)
COUNTS=(48,47,30,20,9)
HASHES=(('5822d741b0c7c252e9094b2add4badf92b74b0ed6807295b5e13d86d959b2389','2b3baa191cc595a7d1ecdfd546cbc61ca1070d21f717b3da093030dd887b11a0','6e0ca4ee091e8fad9b4698a2c29f30d76cc1989a05e62bce1467f927ff75a048','4720676e12b49ef2d91c0fb8225d2918b52ad27ee5e181abab91224703025fee','e6a3be507e9c2a8aa2921b1366a703de21b2389525bc64ab631bc60c2682292a'),
 ('0b83e7a431c563c7e6131eb3c86706a501103bcc78e6c41f273fdc9c86470075','0222833dac090735178b24c31176f950dce84865041f9e672302434f6a20ae09','55b241f2da2f1e44a6e0fd4a1058a4a65e48e384cec3b3bf6b4d1c4108acb516','e9166e91371bee598d96af8479d4df0cc2fbe397ad5dfa2ef615c00af046dcc0','2ebe40ad0abdbf61d421ffc786e3fe433f8913c08c35cfd8631b9fa70f1567c3'))


def specs(part,index):
    pc=STARTS[index][PARTS.index(part)];s={};d=80*index
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def ai(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def lui(o,r,v=0x20003000):e(o,'lui',rd=r,imm=v)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    def ld(o,r,b,v,w=4):e(o,'load',rd=r,rs1=b,imm=v,width=w)
    def st(o,r,b,v,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    def mv(o,r,b):e(o,'mv',rd=r,rs2=b)
    def call(o,t):e(o,'jal',rd=1,target=t)
    def pair(o,upper,low):e(o,'auipc',rd=1,imm=upper);e(o+4,'jalr',rd=1,rs1=1,imm=low)
    def bz(o,r,t):e(o,'beqz',rs1=r,target=pc+t)
    def bnz(o,r,t):e(o,'bnez',rs1=r,target=pc+t)
    def ret(o):e(o,'jr',rs1=1)
    if part=='publish128':
        lui(0,15);ld(4,15,15,415+d,1);ai(8,2,2,-16);st(10,1,2,12);bnz(12,15,30)
        lui(14,10,0x53000);ai(18,10,10,1324+174*index);call(22,0x43c4e+140*index);call(26,0x5362e+174*index)
        lui(30,15,0x5f000);lui(34,14);ai(38,15,15,-1860+234*index);st(42,15,14,1084+d);ld(46,1,2,12)
        lui(48,15,0x60000);lui(52,14);ai(56,15,15,1302+234*index);st(60,15,14,1272+d);ai(64,2,2,16);ret(66)
        return s
    if part=='publish148':
        lui(0,15,0x58000);lui(4,14);ai(8,15,15,-834+320*index);st(12,15,14,1104+d)
        lui(16,15,0x59000);lui(20,14);ai(24,15,15,-942+328*index);st(28,15,14,1264+d);ret(32)
        return s
    ai(0,2,2,-16)
    if part=='clear':
        st(2,1,2,12);st(4,8,2,8);st(6,9,2,4);mv(8,8,10);call(10,0x63e58+234*index);mv(14,10,8)
        st(16,0,8,12,1);st(20,0,8,11,1);st(24,0,8,9,1);lui(28,9);call(32,0x53d98+178*index);ai(36,9,9,412+d)
        ld(40,10,9,3,1);li(42,11,1);call(44,0x439a8+140*index);ld(48,10,9,3,1);li(50,11,2);call(52,0x439a8+140*index)
        ld(56,10,8,22,1);ai(58,15,0,255);e(62,'beq',rs1=10,rs2=15,target=pc+74);call(66,0x43a14+140*index);li(70,15,-1);st(72,15,8,22,1)
        ld(74,1,2,12);ld(76,8,2,8);ld(78,9,2,4);ai(80,2,2,16);ret(82)
        return s
    a=part=='outer128';size=232 if a else 160;end=138 if a else 144
    ai(2,11,0,622 if a else 585);ai(6,10,0,size);st(10,8,2,8);st(12,1,2,12)
    pair(14,0x1ffa1000 if a else 0x1ffa8000,(1910-234*index) if a else (884-320*index))
    mv(22,8,10);bz(24,10,end);ai(26,12,0,size);li(30,11,0)
    pair(32,0x1ffa2000 if a else 0x1ffa8000,(-1344-234*index) if a else (1726-320*index))
    lui(40,15);st(44,8,15,(1080 if a else 1100)+d);lui(48,15)
    if a:
        st(52,0,8,10,1);st(56,0,8,8,1);ai(60,15,15,1300+d);ld(64,14,15,32);ld(66,15,15,36);st(68,14,8,116);st(70,15,8,120)
        li(72,15,-1);st(74,15,8,48,2);st(76,15,8,125,1);st(80,15,8,129,1)
        lui(84,15,0x5e000 if not index else 0x5f000);ai(88,15,15,1900 if not index else -1962);st(92,15,8,104)
        lui(94,15,0x60000);ai(98,15,15,1190+234*index);st(102,15,8,108);lui(104,15,0x60000);ai(108,15,15,848+234*index);st(112,15,8,112)
    else:
        ai(52,15,15,1300+d);ld(56,14,15,32);ld(58,15,15,36);st(60,0,8,4,1);st(64,14,8,148);st(68,15,8,152)
        li(72,15,-1);st(74,15,8,64,1);ai(78,15,0,-79);st(82,15,8,6,1)
        lui(84,15,0x58000);ai(88,15,15,-1156+320*index);st(92,15,8,136);lui(96,15,0x58000);ai(100,15,15,54+320*index);st(104,15,8,140)
        lui(108,15,0x58000);ai(112,15,15,-278+320*index);st(116,15,8,144)
    z=0 if a else 6
    lui(114+z,15);ld(118+z,15,15,576+d,1);bnz(122+z,15,end);lui(124+z,15);ld(128+z,10,15,(1272 if a else 1264)+d);li(132+z,11,3 if a else 4);call(134+z,0x43b28+140*index)
    mv(end,10,8);ld(end+2,1,2,12);ld(end+4,8,2,8);ai(end+6,2,2,16);ret(end+8)
    return s


def body(raw,part,index):
    k=PARTS.index(part);pc=STARTS[index][k];n=decode(raw,pc);s=specs(part,index)
    check(set(n)==set(s),'outer '+part+' boundaries')
    for p,f in s.items():init.g(n,p,'outer '+part+' operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[k],HASHES[index][k]),'outer '+part+' identity')
    edges={};calls=[]
    for p,v in n.items():
        op=v['op'];q=[p+v['size']]
        if op=='jr':check(v['rs1']==1,'outer RET RA');q=[]
        elif op in ('beq','beqz','bnez'):q.append(v['target'])
        elif op in ('jal','jalr'):
            check(v['rd']==1,'outer linkRA')
            if op=='jal':t=v['target']
            else:
                a=n[p-4];check(a['op']=='auipc' and a['rd']==v['rs1'],'outer adjacent PCpair');t=(p-4+a['imm']+v['imm'])&0xfffffffe
            calls.append({'pc':hex(p),'target':hex(t)})
        check(all(x in n for x in q),'outer closed '+part+' CFG');edges[p]=q
    seen=set();active=set()
    def visit(p):
        check(p not in active,'outer acyclic '+part)
        if p in seen:return
        active.add(p)
        for q in edges[p]:visit(q)
        active.remove(p);seen.add(p)
    visit(pc);check(seen==set(n),'outer full '+part+' reachability')
    stores=[{'pc':hex(p),'base_register':v['rs1'],'source_register':v['rs2'],'offset':v['imm'],'bytes':v['width']} for p,v in n.items() if v['op']=='store']
    check((len(stores),len(calls))==((13,3),(11,3),(7,5),(3,2),(2,0))[k],'outer store/callcensus')
    if part.startswith('outer'):check([v['target'] for v in calls]==['0x20000040','0x2000039c',hex(0x43b28+140*index)],'outer exactallocator/fill/registrar requests')
    return {'start':hex(pc),'end_exclusive':hex(pc+SIZES[k]),'bytes':SIZES[k],'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),
      'conditional_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},'calls':calls,'stores':stores,'complete_local_body':True,'local_CFG_acyclic':True}


def certificates(b,part):
    pc=int(b['start'],16);e={int(p,16):[int(q,16) for q in qs] for p,qs in b['conditional_CFG'].items()}
    if part=='clear':cases={'N22_ff':{62:74},'N22_other':{62:66}}
    elif part=='publish128':cases={'gate0_setup_then_publish':{12:14},'gate_nonzero_publish':{12:30}}
    elif part=='publish148':cases={'straight_publications':{}}
    else:
        z=0 if part=='outer128' else 6;end=138+z
        cases={'allocation_null':{24:end},'nonnull_gate_nonzero':{24:26,122+z:end},'nonnull_gate0_register':{24:26,122+z:124+z}}
    result={name:previous.previous.role.previous.chain(e,pc,{pc+a:pc+t for a,t in c.items()}) for name,c in cases.items()}
    for name,path in result.items():
        offsets=[int(x,16)-pc for x in path]
        if part.startswith('publish'):
            check(all(int(v['pc'],16)-pc in offsets for v in b['stores']),'outer publisher stores on everylocalpath')
        elif part=='clear':
            check(all(x in offsets for x in (10,16,20,24,32,44,52,56)),'outer clear mandatory call/store order')
            check((72 in offsets)==(name=='N22_other'),'outer clearff write onlyservicepath')
        elif name=='allocation_null':check(all(int(v['pc'],16)-pc in (10,12) for v in b['stores'] if v['pc'] in path),'outer null hasonlyframestores')
        else:
            writes=[int(v['pc'],16)-pc for v in b['stores'] if v['base_register']==8]
            check(all(offsets.index(44)<offsets.index(x) for x in writes),'outer publishesbeforeallobjectstores')
    return result


def reused_registrar(data,index):
    d=hooks.DETAILS[index];pc=d[6];delta=d[7]
    b=hooks.body(init.binding.take(data,pc,22),'registrar',pc,delta,d[-1][3])
    n={v['pc']:v for v in b['instructions']};table=0x20003000+delta
    check(not b['calls'] and [(v['rs1'],v['imm'],v['width']) for v in n.values() if v['op']=='store']==[(11,0,4)],'outer reused registraroneword only')
    check(set(v['rd'] for v in n.values() if 'rd' in v)<={11,15},'outer reusedregistrar preservesS0/SP/RA/A0')
    return {'start':hex(pc),'bytes':22,'sha256':b['sha256'],'table_base':hex(table),'accepted_args':[3,4],
      'exact_destinations':{'3':hex(table+12),'4':hex(table+16)},'only_store':'U32[table+4*entryA1]=entryA0 forunsignedA1<=4; noreply reset',
      'callbacks_invoked':False,'no_calls_or_frame':True,'GPR_writes':[11,15],'source_checker':'check_v4160_loaded_hook_sources_static.py'}


def publisher_joins(data,index,bodies,B):
    d=hooks.DETAILS[index];pc=d[8]
    caller=hooks.body(init.binding.take(data,pc,34),'publish_alternative',pc,(d[9],d[10],d[11],d[4]),d[-1][4])
    check([v['target'] for v in caller['calls']]==[bodies['publish128']['start'],bodies['publish148']['start']],'outer reusedcaller two newpublisher bodies')
    pubvalues={};rows=[]
    for part,slot,up,low,store,sup,slow,sstore,source in (
        ('publish128',132,30,38,42,48,56,60,320),('publish148',152,0,8,12,16,24,28,312)):
        b=bodies[part];p=int(b['start'],16);n={v['pc']:v for v in b['instructions']}
        value=(n[p+up]['imm']+n[p+low]['imm'])&0xffffffff
        target=bodies['outer128' if part=='publish128' else 'outer148']['start'];check(hex(value)==target,'outer publishedfunction joins fullconstructor')
        check(0x20003000+n[p+store]['imm']==B+slot and 0x20003000+n[p+sstore]['imm']==B+source,'outer functionslot/sourceword exactaddresses')
        sourcevalue=(n[p+sup]['imm']+n[p+slow]['imm'])&0xffffffff;pubvalues[str(source)]=hex(sourcevalue)
        rows.append({'publisher':b['start'],'constructor_function_slot':hex(B+slot),'constructor_value':target,'constructor_invoked_locally':False,
          'separate_callback_source_slot':hex(B+source),'separate_callback_value':hex(sourcevalue)})
    rp=previous.previous.role.DETAILS[index]['reg'];reg=previous.previous.registration.body(init.binding.take(data,rp,48),index)
    check(bodies['publish128']['calls'][0]['target']==reg['start'],'outer publisheruses known taskregistrar')
    return {'reused_immediate_caller':{k:caller[k] for k in ('start','bytes','sha256')},'caller_order':[bodies['publish128']['start'],bodies['publish148']['start']],
      'publications':rows,'callback_source_values':pubvalues,'reused_task_registrar':{k:reg[k] for k in ('start','bytes','sha256')},
      'publish128_zero_gate':'registerhandler5352c/535da; passrawreply including255 tosetup5362e/536dc; afterrequirednormalreturn publishbothfunctionwords',
      'publish128_nonzero_gate':'skipregistration/setup, publishbothfunctionwords; locallyentryA0 retained',
      'construction_limit':'these bodies andimmediatecaller publishconstructoraddresses, notouterobjects; no localcall toconstructors. Sourcevalues reachregistrar3/4 onlyif publishers precedeconstructors andnointerveningwriters',
      'actualcallers_or_entryschedule_proved':False}


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[]
    for i,(data,pr) in enumerate(zip(carriers,parent['profiles'])):
        bodies={part:body(init.binding.take(data,STARTS[i][k],SIZES[k]),part,i) for k,part in enumerate(PARTS)}
        paths={part:certificates(b,part) for part,b in bodies.items()};B=0x200033b8+80*i;reg=reused_registrar(data,i);publishers=publisher_joins(data,i,bodies,B)
        hp=previous.previous.STARTS[i];handler=previous.previous.body(init.binding.take(data,hp,258),i);hn={v['pc']:v for v in handler['instructions']}
        nested={}
        for part,slot,field_events,wordtriples,size,minsize in (
            ('outer128',128,((108,'bit2'),(112,'bit3')),((84,88,92),(94,98,102),(104,108,112)),232,130),
            ('outer148',148,((140,'bit4'),(144,'bit5')),((84,88,92),(96,100,104),(108,112,116)),160,156)):
            b=bodies[part];pc=int(b['start'],16);n={v['pc']:v for v in b['instructions']};a=part=='outer128';z=0 if a else 6
            values={str(n[pc+st]['imm']):hex((n[pc+up]['imm']+n[pc+low]['imm'])&0xffffffff) for up,low,st in wordtriples}
            check(0x20003000+n[pc+44]['imm']==B+slot,'outer exactglobal publication address')
            objectstores=[v for v in b['stores'] if v['base_register']==8]
            check(max(v['offset']+v['bytes'] for v in objectstores)==minsize and minsize<=size,'outer validatedextent fitsrequest')
            check(int(reg['exact_destinations']['3' if a else '4'],16)+4<=B+slot,'outer registrarword disjoint publishedouterword')
            for field,event in field_events:
                load_offset={'bit2':156,'bit3':130,'bit4':210,'bit5':182}[event]
                outer_offset=load_offset-4
                check(hn[hp+load_offset]['op']=='load' and hn[hp+load_offset]['imm']==field,'outer handlerfunctionfield '+event)
                check(hn[hp+outer_offset]['op']=='load' and hn[hp+outer_offset]['imm']+0x20003000==B+slot,'outer handlerouterword '+event)
            nested[part]={'constructor':b['start'],'request':{'target':'0x20000040','A0':size,'A1':622 if a else 585},
              'fill_request':{'target':'0x2000039c','args':['originalallocationreplyN',0,size]},'saved_N_register':'S0',
              'slot':hex(B+slot),'publication_pc':hex(pc+44),'callback_word_values':values,
              'handler_join':{event:{'field':field,'conditional_target':values[str(field)]} for field,event in field_events},
              'local_defaults':({'N8':0,'N10':0,'N48_halfword':65535,'N125':255,'N129':255} if a else {'N4':0,'N6':177,'N64':255}),
              'two_source_words':{'source_addresses':[hex(0x20003534+80*i),hex(0x20003538+80*i)],'destination_offsets':[116,120] if a else [148,152],
                'freshness':'two separate wordloads beforeeither wordstore; sources maychange independently'},
              'minimum_explicit_object_extent':minsize,'handler_field_extent':116 if a else 148,'request_extent':size,
              'null_reply_path':'local nofill/noouterword/noobjectstore; return0 fromsavedreply. Allocationprovider mayhaveeffects; oldslotpreservedonlyifprovider/otherwriters preserveit',
              'publication_order':'allocator->fill returns->publishouterN->all explicitobjectstores/functionwords->optionalregistrar->returnoriginalN',
              'optional_registrar':{'gate':'freshU8['+hex(0x20003240+80*i)+']==0','target':reg['start'],'A0':'freshU32['+hex(0x200034f8+80*i if a else 0x200034f0+80*i)+']','A1':3 if a else 4,
                'slot':reg['exact_destinations']['3' if a else '4'],'conditional_published_source_value':publishers['callback_source_values']['320' if a else '312'],
                'result':'actualregistrarifmatchingreference writesoneword, doesnotinvokeA0; noA0nullguard'},
              'conditional_normalreturn':'ifallocation/fill valid andcalleeSP/RA/frame/S0preserved, N nonaliasglobal/frame/table andnointerference, publishedword/functions remainoriginalN/literals aftermatchingregistrar andnormalreturn',
              'concurrency_limit':'publication precedes fields; no atomic/readiness/scheduling/interference proof',
              'actual_provider_or_lifetime_proved':False}
        clear=bodies['clear'];cp=int(clear['start'],16)
        tails=[v['target'] for v in pr['bodies']['bit0']['tail_cuts']]
        check(clear['start'] in tails,'outer directcallback clear-tail joinsfullbody')
        profiles.append({'label':pr['label'],'B':hex(B),'bodies':bodies,'selected_CFG_paths':paths,'reused_registrar':reg,'publisher_joins':publishers,
          'reused_handler':{k:handler[k] for k in ('start','bytes','sha256')},'outer_objects':nested,
          'clear_tail_contract':{'entry_N':'originalA0 savedinS0; no localnullguard','frame_bytes':16,'saved':['RA','S0','S1'],'minimum_explicit_extent':23,
            'first_call':{'target':hex(0x63e58+234*i),'A0':'originalN'},
            'clear_order':[{'pc':hex(cp+16),'byte':12,'value':0},{'pc':hex(cp+20),'byte':11,'value':0},{'pc':hex(cp+24),'byte':9,'value':0}],
            'next_call':{'target':hex(0x53d98+178*i),'A0':'originalN'},
            'two_request_calls':{'target':hex(0x439a8+140*i),'first':['freshU8['+hex(0x2000319f+80*i)+']',1],'second':['independentlyfreshU8['+hex(0x2000319f+80*i)+']',2],
              'actual_service_semantics_unproved':True},
            'N22_ff':'freshU8[N22]==255: no lastservice/store, locallyreturnsA0=255 afterrestoration',
            'N22_other':'call'+hex(0x43a14+140*i)+' withA0=freshU8[N22], thenN22=255; returnlastserviceA0 subjecttopreservation',
            'not_a_proved_free':'no local head/tail/count/next store, no localslotclear; callees maywrite/retain/release N. Earlierclearedbytes notprovedzeroatfinalreturn',
            'preservation':'all callees mustreturnnormally andpreserve liveS0/S1/SP/RA/frame; originalN mustremainvalid forlaterstores'},
          'actual_installed_binding_proved':False,'target_execution_or_emulation':False})
    return {'schema':'TSL9-list-outer-objects-static-v1','profile':parent['profile'],'APP_sha256':sha256(image).hexdigest(),'profiles':profiles,
      'scope':'976neworiginalbytes/308operandguards/22selectedpaths;fulltwoouterconstructors+oneclear tail+twopublishers perprofile;existing34Bcaller/22Bregistrar/48Btaskregistrar/258Bhandler/directcallback proofs reused',
      'boundary':'conditional static allocation/publication/handler/clear contracts only; no allwriters/runtimeorder/actualprovider/pointerlifetime proof',
      'remaining':['actualconstructorcalls/functionslot consumers/order','full54c08/54cd2 hardware-objectconstruction tail','nestedcallbacks604a6/60590,60350/6043a,58036/58176,57eea/5802a','clearcallees63e58/63f42,53d98/53e4a,439a8/43a34,43a14/43aa0','actualallocator/fill/retention andsetup-latepreservation'],
      'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def domains():
    for old in range(256):check((old==255)==(old^255==0),'outer clearbyte ff exactpredicate')
    check((-79)&255==177 and (-1)&65535==65535,'outer truncated defaultliterals')
    for base in (456,536):
        check(0x20003000+base+3*4!=0x20003000+base+4*4,'outer registrar3/4 distinct')
        check(all(x<=4 for x in (3,4)),'outer fixedregistrar indices accepted')
    return {'N22_bytecases':256,'N22_ff_skip_count':1,'N22_service_and_store_count':255,'registrar_indices':[3,4],
      'null_allocation_partition':'fullwordreply==0 vs!=0; nonzero doesnotprove readable/writable/disjoint/retained object',
      'object_default_truncations':{'low8_minus79':177,'low8_minus1':255,'low16_minus1':65535}}


def tests(carriers):
    mutations=paths=0
    for i,data in enumerate(carriers):
        for k,part in enumerate(PARTS):
            pc=STARTS[i][k];raw=init.binding.take(data,pc,SIZES[k]);b=body(raw,part,i);paths+=len(certificates(b,part))
            for p,v in decode(raw,pc).items():
                at=p-pc;z=v['size'];buf=bytearray(raw);buf[at:at+z]=(int.from_bytes(buf[at:at+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
                try:body(buf,part,i)
                except RuntimeError as e:check(str(e).startswith('outer '+part+' operand '),'outer specifiedmutation '+str(e))
                else:raise RuntimeError('outer mutation escaped')
                mutations+=1
    check((mutations,paths)==(308,22),'outer mutation/pathcensus');domains()
    print('PASS:308 operand mutations rejected;976 new originalbytes;22 selectedCFG paths;256 N22bytecases;request/store interval certificates')


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');o=p.parse_args()
    image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK identity')
    carriers=[]
    for label,folder,tail,z,digest in init.binding.PROFILES:
        data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidate identity '+label);carriers.append(data)
    raw_hex=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
    coverage=sparse.derive(image,carriers,header,raw_hex,sparse.parser());ledger=derive(image,carriers,header,coverage);ledger['integer_domains']=domains();ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers)
    output=(json.dumps(ledger,indent=1,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'outer exactledger replay')
    print('PASS:outer128/148 writers->handler callbackfields;publishers/reusedcaller/sourcewords/registrar3/4;directcallback->full clear tail;exact ledger')
    print('PASS:NO target execution/emulation;actualprovider/callerorder/retention/full54c08 tail UNPROVED')


if __name__=='__main__':main()
