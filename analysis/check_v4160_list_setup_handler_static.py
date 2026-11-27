"""Offline reused setup/list provenance and newly guarded registered handler.

Literal instruction/CFG and interval/integer certificates only. No target ISA,
event/list/provider/allocator/IRQ/MMIO execution or mutable machine model.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_list_origin_static as previous
import check_v4160_role_initializer_fields_static as fields
import check_v4160_first_role_gate_static as role
import check_v4160_task_registration_static as registration
import check_v4160_config_buffer_source_static as source

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-list-setup-handler-static.json')
STARTS=(0x5352c,0x535da)
HASHES=('00ff53ae3db7eb1655258f2266f4e1b42861a4d16519310f3557733d71c20280','6477bf3c4cf3a9e94864d76dd37b2963c1290d8871fe971ebb9efa8403cf8eb5')


def specs(index):
    pc=STARTS[index];d=80*index;s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    def lui(o,r,v=0x20003000):e(o,'lui',rd=r,imm=v)
    def ai(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def ld(o,r,b,v,w=4):e(o,'load',rd=r,rs1=b,imm=v,width=w)
    def st(o,r,b,v):e(o,'store',rs2=r,rs1=b,imm=v,width=4)
    def mv(o,r,b):e(o,'mv',rd=r,rs2=b)
    def imm(o,op,r,b,v):e(o,op,rd=r,rs1=b,imm=v)
    def bz(o,r,t):e(o,'beqz',rs1=r,target=pc+t)
    def br(o,op,a,b,t):e(o,op,rs1=a,rs2=b,target=pc+t)
    def j(o,t):e(o,'jump',target=pc+t)
    def indirect(o):e(o,'call_indirect',rd=1,rs1=15)
    def call(o,t):e(o,'jal',rd=1,target=t)
    ai(0,2,2,-16);imm(2,'slli',15,11,16);st(6,8,2,8);st(8,1,2,12);st(10,9,2,4);imm(12,'srai',15,15,16);mv(14,8,11);br(16,'bge',15,0,60)
    e(20,'auipc',rd=1,imm=0x1ffad000);e(24,'jalr',rd=1,rs1=1,imm=-692-174*index);mv(28,9,10);bz(30,10,54);ld(32,15,10,0,1);li(34,14,1);imm(36,'xori',15,15,128);br(40,'bltu',14,15,48)
    call(44,0x5e230+328*index);mv(48,10,9);call(50,0x431ba+140*index);lui(54,10,0x8000);e(56,'xor',rd=10,rs1=10,rs2=8);j(58,82)
    imm(60,'andi',15,11,1);bz(64,15,92);lui(66,15);ld(70,15,15,1064+d);bz(74,15,78);indirect(76);imm(78,'xori',10,8,1)
    ld(82,1,2,12);ld(84,8,2,8);ld(86,9,2,4);ai(88,2,2,16);e(90,'jr',rs1=1)
    imm(92,'andi',15,11,2);bz(96,15,116);lui(98,15);ld(102,15,15,1068+d);bz(106,15,110);indirect(108);imm(110,'xori',10,8,2);j(114,82)
    for o,bit,nextoff,slot,field in ((116,8,142,1080,112),(142,4,168,1080,108)):
        imm(o,'andi',15,11,bit);bz(o+4,15,nextoff);lui(o+6,15);ld(o+10,15,15,slot+d);ld(o+14,15,15,field);bz(o+16,15,o+20);indirect(o+18);imm(o+20,'xori',10,8,bit);j(o+24,82)
    for o,bit,nextoff,field in ((168,32,196,144),(196,16,224,140)):
        imm(o,'andi',15,11,bit);bz(o+4,15,nextoff);lui(o+6,15);ld(o+10,15,15,1100+d);ld(o+14,15,15,field);bz(o+18,15,o+22);indirect(o+20);imm(o+22,'xori',10,8,bit);j(o+26,82)
    imm(224,'slli',15,11,18);li(228,10,0);br(230,'bge',15,0,82);lui(234,15);ai(238,15,15,952+d)
    for o,r,v in ((242,13,7),(244,12,6),(246,11,5),(248,10,4)):ld(o,r,15,v,1)
    call(250,0x67c0e+318*index);lui(254,10,0x2000);j(256,56)
    return s


def body(raw,index):
    pc=STARTS[index];n=decode(raw,pc);s=specs(index)
    check(set(n)==set(s),'handler boundaries')
    for p,f in s.items():init.g(n,p,'handler operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(258,90,HASHES[index]),'handler identity')
    edges={};calls=[]
    for p,d in n.items():
        op=d['op'];q=[p+d['size']]
        if op=='jr':check(d['rs1']==1,'handler RET RA');q=[]
        elif op in ('beqz','bge','bltu'):q.append(d['target'])
        elif op=='jump':q=[d['target']]
        elif op in ('jal','jalr','call_indirect'):
            if op=='jal':target=hex(d['target'])
            elif op=='call_indirect':target='loadedA5functionpointer'
            else:
                a=n[p-4];check(a['op']=='auipc' and a['rd']==d['rs1'],'handler PC pair');target=hex((p-4+a['imm']+d['imm'])&0xfffffffe)
            check(d['rd']==1,'handler call link');calls.append({'pc':hex(p),'target':target})
        check(all(v in n for v in q),'handler closedCFG');edges[p]=q
    seen=set();active=set()
    def visit(p):
        check(p not in active,'handler no local cycle')
        if p in seen:return
        active.add(p)
        for q in edges[p]:visit(q)
        active.remove(p);seen.add(p)
    visit(pc);check(seen==set(n),'handler all nodes locally reachable')
    stores=[(p-pc,v) for p,v in n.items() if v['op']=='store'];check([(o,v['rs1'],v['rs2'],v['imm']) for o,v in stores]==[(6,2,8,8),(8,2,1,12),(10,2,9,4)],'handler exactlythree frame stores')
    check(len(calls)==10 and sum(v['target']=='loadedA5functionpointer' for v in calls)==6,'handler exact call census')
    check(n[pc+14]['rs2']==11 and n[pc+224]['imm']==18,'handler saves fullmask andchecksbit13')
    return {'start':hex(pc),'end_exclusive':hex(pc+258),'bytes':258,'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),
            'conditional_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},'calls':calls,'frame_stores':3,'persistent_local_stores':0,'complete_local_body':True,'local_CFG_acyclic':True}


def certificates(b):
    pc=int(b['start'],16);e={int(p,16):[int(q,16) for q in qs] for p,qs in b['conditional_CFG'].items()}
    cases={'message_null':{16:20,30:54},'message_type128or129':{16:20,30:32,40:44},'message_other':{16:20,30:32,40:48}}
    callback_rows=((1,{16:60,64:66},74,78,76),(2,{16:60,64:92,96:98},106,110,108),
        (8,{16:60,64:92,96:116,120:122},132,136,134),(4,{16:60,64:92,96:116,120:142,146:148},158,162,160),
        (32,{16:60,64:92,96:116,120:142,146:168,172:174},186,190,188),
        (16,{16:60,64:92,96:116,120:142,146:168,172:196,200:202},214,218,216))
    for bit,c,branch,skip,call in callback_rows:
        for label,t in (('fnnull',skip),('fnnonnull',call)):cases['bit'+str(bit)+'_'+label]={**c,branch:t}
    tail={16:60,64:92,96:116,120:142,146:168,172:196,200:224};cases['bit13']={**tail,230:234};cases['no_known_bit']={**tail,230:82}
    paths={name:role.previous.chain(e,pc,{pc+p:pc+q for p,q in c.items()}) for name,c in cases.items()}
    check(len(paths)==17,'handler17 selected paths/profile');return paths


def domains():
    priority=(32768,1,2,8,4,32,16,8192);counts={str(v):0 for v in (*priority,0)}
    for low in range(65536):
        bit=next((v for v in priority if low&v),0);counts[str(bit)]+=1
        for upper in (0,1,32768,65535):
            mask=upper<<16|low
            check(bool(((mask<<18)&0xffffffff)&0x80000000)==bool(low&8192),'handler bit13 shift identity')
            check(bool(((mask<<16)&0xffffffff)&0x80000000)==bool(low&32768),'handler bit15 shift identity')
            if bit:check((mask^bit)>>16==upper,'handler XOR preserves high16')
    check(list(counts.values())==[32768,16384,8192,4096,2048,1024,512,256,256],'handler priority domain census')
    types=[v for v in range(256) if (v^128)<=1];check(types==[128,129],'handler parser exactmessage types')
    admitted=0
    for count in range(256):
        for cap in range(256):
            reply=count if count<cap else 255;admitted+=int(count<cap)
            check((reply&255)==reply,'setup rawtaskreply byte domain')
    check(admitted==32640,'setup registration capacity pair census')
    check((0 if 0<1 else 255)==0 and (255 if 255<255 else 255)==255,'setup gate0 successfulindex0 andfailure255 cases')
    return {'priority_bits':list(priority),'low16_counts':counts,'upper16_vectors':[0,1,32768,65535],'recognized_message_types':types,
            'registration_capacity_pairs':65536,'registration_admitted':admitted,'gate_prefix_value':'rawregistrationreply low8, including successful0 andfailure255; not an automatic successboolean'}


def reuse_contracts(data,index,parent_profile):
    d=role.DETAILS[index];B=0x20003000+d['base'];sp=d['initialize']
    setup=fields.body(init.binding.take(data,sp,426),'initializer',index);selector=fields.body(init.binding.take(data,fields.DETAILS[index][0],70),'selector',index)
    prefix=role.body(init.binding.take(data,sp,62),'initialize',index)
    reg=registration.body(init.binding.take(data,d['reg'],48),index)
    entry=role.body(init.binding.take(data,d['entry'],112),'entry',index);primary=role.body(init.binding.take(data,d['primary'],62),'primary',index)
    setters=[role.body(init.binding.take(data,p,10),'setter'+str(k),index) for k,p in enumerate(d['setters'])]
    fill=source.fill_contract(init.binding.take(data,(0x4060c,0x4064c)[index],46))
    check(init.binding.word(data,0x401a0)==d['entry'] and init.binding.word(data,0x40080)==d['reg'],'setup candidate tablewords join source bodies')
    check(entry['calls'][0]['target']==primary['start'] and primary['calls'][0]['target']==parent_profile['bodies']['installer']['start'],'setup knownstaticcaller entry-primary-installer')
    sn={v['pc']:v for v in setup['instructions']};pn={v['pc']:v for v in parent_profile['bodies']['installer']['instructions']};gp=d['gate']
    check(pn[gp+14]['imm']+pn[gp+18]['imm']==STARTS[index] and pn[gp+22]['target']==int(reg['start'],16),'setup installerregistration literalpoints tonewhandler')
    check(sn[sp+20]['rs2']==10 and sn[sp+58]['rs2']==8 and sn[sp+58]['width']==1,'setup rawregistrationreply saved thenstorelow8togate')
    local=[]
    for p,v in sn.items():
        if v['op']!='store' or v['rs1']==2:continue
        o=p-sp
        if o==28:a=B+300
        elif o==58:a=0x20003000+d['ctx']+3
        elif v['rs1']==8 and o>=62 or v['rs1']==15 and o>=266 or v['rs1']==9 and o>=334:a=B+v['imm']
        else:raise RuntimeError('setup unclassified directstore')
        local.append({'offset':o,'address':a,'width':v['width']})
    protected={'count':(B+62,1),'busy':(B+88,4),'head':(B+92,4),'tail':(B+96,4),'callbacks':(B+104,16),'outer128':(B+128,4),'outer148':(B+148,4),'handlerbytes4to7':(B+4,4)}
    for name,(a,z) in protected.items():
        check(B<=a<a+z<=B+296,'setup fill296 contains '+name)
        check(all(v['address']+v['width']<=a or a+z<=v['address'] for v in local),'setup localstores exclude '+name)
    cap=[v['offset'] for v in local if v['address']<=B+63<v['address']+v['width']];check(cap==[222] and sn[sp+220]['imm']==1,'setup exactcapacity SB1 writer')
    calls_between=[v['target'] for v in setup['calls'] if sp+62<=int(v['pc'],16)<sp+388];check(calls_between==[selector['start']] and not selector['calls'] and selector['store_count']==0,'setup onlypureselector beforelatecut')
    check(set(sn[sp+p]['rs1'] for p in (282,284,314,330,366,380,382,384))=={15},'setup timing stores use fixedB A5 base')
    metadata=lambda b:{k:b[k] for k in ('start','bytes','sha256')}
    return {'B':hex(B),'candidate_tablewords':{'401a0':entry['start'],'40080':reg['start'],'actualinstalled_proved':False},
            'reused_source_bodies':{'fullsetup':metadata(setup),'prior62byteprefix':metadata(prefix),'selector':metadata(selector),'registration':metadata(reg),'entry':metadata(entry),'primary':metadata(primary),'setters':[metadata(v) for v in setters]},
            'staticcaller_chain':[entry['start'],primary['start'],parent_profile['bodies']['installer']['start']],
            'registered_handler_literal':hex(STARTS[index]),'setup_entry_A0':'rawregistrationreply; no255 rejection before setup',
            'fill296':{'target':'0x2000039c','reference_sha256':fill['sha256'],'reference_encoded_GPR_writes':fill['encoded_GPR_writes'],
                'requested_extent':[hex(B),hex(B+296)],'conditional_output':'matchingreference positivefill andnormalreturn -> low8(0) over296bytes; no provider/MMIO executed',
                'covered_fields':{k:{'address':hex(a),'bytes':z} for k,(a,z) in protected.items()}},
            'direct_capacity_writer':{'pc':hex(sp+222),'address':hex(B+63),'value':1},
            'three_trailing_zero_words':{'explicit_beforefill':hex(B+300),'leafsetters_afterfill':[hex(B+296),hex(B+304)],'separate_from_fill296':True},
            'local_cut_before_latecall':{'pc':hex(sp+388),'target':setup['calls'][4]['target'],
                'conditional_fields':'count0,head/tail/busy/callbackwords/outer128/outer148/bytes4..7zero;capacity1. Requires matchingfill/selector, validnonaliasdata/frame andnointerference',
                'scope':'localcut only; latecalls andtailmaychange state. No finalsetup/callbackinvocation claim'},
            'normal_return_boundary':{'last_local_edge':setup['tail_cuts'][0],'installer_callback_stores':'only after required fullsetup/tailreturn','later_effects_preserved_proved':False},
            'registration_gate_examples':{'success_index0':'gateprefix0 even though registrationaccepted','rejection255':'no handler tablestore byregistration; gateprefix255 if setup reachesstore','other_success':'gateprefix actualindex,notfixedtaskID'}}


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[]
    for i,(data,pr) in enumerate(zip(carriers,parent['profiles'])):
        b=body(init.binding.take(data,STARTS[i],258),i);joins=reuse_contracts(data,i,pr);B=int(joins['B'],16);p=STARTS[i];n={v['pc']:v for v in b['instructions']};paths=certificates(b)
        check(b['calls'][0]['target']=='0x2000028c' and n[p+250]['target']==0x67c0e+318*i,'handler receive andlastservice exacttargets')
        values=pr['installer']['callback_word_values']
        check(n[p+70]['imm']+0x20003000==B+112 and n[p+102]['imm']+0x20003000==B+116,'handler directcallbacks join installerwords')
        check(all(n[p+o]['width']==1 for o in (242,244,246,248)),'handler finalargs unsignedbytes nothalfwords')
        profiles.append({'label':pr['label'],'handler':b,'selected_CFG_paths':paths,'setup_list_joins':joins,
            'event_contract':{'frame_bytes':16,'saved':['RA','S0','S1'],'full32mask_saved':'S0','priority_bits':[32768,1,2,8,4,32,16,8192],
                'normal_return':'originalfull32mask XOR selectedbit; ifnoneknown,0; requiredcalls preserveS0/SP/frame/RA',
                'no_local_persistent_stores':True,'scheduler_invocation_or_actualeventvalues_proved':False},
            'message_bit15':{'receive_target':'0x2000028c','receive_A0':'originalentrytaskvalue, not freshfixedglobal ID','null':'skipmessage access/release',
                'nonnull':'S1=M;U8[M0] XOR128<=1 selects exactlytypes128/129 for'+hex(0x5e230+328*i)+'(M); thenallnonnulltypes call'+hex(0x431ba+140*i)+'(originalM)',
                'limits':'messageextent/parser semantics/release/ownership/retention andS1/frame preservation unproved'},
            'direct_callbacks':{'bit0':{'slot':hex(B+112),'conditional_installer_value':values['112']},'bit1':{'slot':hex(B+116),'conditional_installer_value':values['116']},
                'function_null_guard':True,'arguments':'A0originaltask,A1originalfullmask locally unchanged beforecall; otherarguments unspecified','callee_replies':'ignored forlocalmaskreturn'},
            'nested_callbacks':{'bit3':{'outer_slot':hex(B+128),'function_offset':112},'bit2':{'outer_slot':hex(B+128),'function_offset':108},
                'bit5':{'outer_slot':hex(B+148),'function_offset':144},'bit4':{'outer_slot':hex(B+148),'function_offset':140},
                'outer_pointer_locally_null_guarded':False,'function_pointer_null_guarded_after_dereference':True,
                'limits':'validouterobjects ofatleast116/148bytes needed; conditionalsetupzero outerwords do not provide thoseobjects; actualwriters/consumers remainunknown'},
            'bit13':{'target':hex(0x67c0e+318*i),'args':['freshU8[B4]','freshU8[B5]','freshU8[B6]','freshU8[B7]'],'result':'ignored; fullmask XOR2000hex'},
            'actual_installed_binding_proved':False,'target_execution_or_emulation':False})
    return {'schema':'TSL9-list-setup-handler-static-v1','profile':parent['profile'],'APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'integer_domains':domains(),
            'scope':'newfull258B/90i registeredhandler perprofile;516neworiginalbytes/180operand guards/34selectedpaths;reusedfullsetup426B,selector70B,registration48B andcaller/source bodies',
            'boundary':'candidate staticcaller/setup-cut/handler contracts only; no finalzero or actualscheduler/provider/binding/object lifetime proof',
            'remaining':['late setup/tail preservation andactualeventinvocation','directcallback558a8/559e0 and550cc/55196 bodies','outerB128/B148 objectwriters andnestedcallbacks','messageparser/release andbit13 service, otherlistwriters/removal'],
            'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    mutations=paths=0
    for i,data in enumerate(carriers):
        pc=STARTS[i];raw=init.binding.take(data,pc,258);b=body(raw,i);paths+=len(certificates(b))
        for p,d in decode(raw,pc).items():
            at=p-pc;z=d['size'];buf=bytearray(raw);buf[at:at+z]=(int.from_bytes(buf[at:at+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
            try:body(buf,i)
            except RuntimeError as e:check(str(e).startswith('handler operand '),'handler specifiedmutation '+str(e))
            else:raise RuntimeError('handler mutation escaped')
            mutations+=1
    check((mutations,paths)==(180,34),'handler mutation/pathcensus');domains()
    print('PASS:180 operand mutations rejected;516 new originalbytes;34 CFG certificates;65536 eventmasks/registrationpairs;256 message typecases')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');o=parser.parse_args()
    image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK identity')
    carriers=[]
    for label,folder,tail,z,digest in init.binding.PROFILES:
        data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidate identity '+label);carriers.append(data)
    raw_hex=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
    coverage=sparse.derive(image,carriers,header,raw_hex,sparse.parser());ledger=derive(image,carriers,header,coverage);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers)
    output=(json.dumps(ledger,indent=1,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'handler exactledger replay')
    print('PASS:reused setup/caller/registration sourcejoins;list-state localcut andcallback consumers;exact ledger')
    print('PASS:NO target execution/emulation;latepreservation/actualscheduler/provider/outerobjects UNPROVED')


if __name__=='__main__':main()
