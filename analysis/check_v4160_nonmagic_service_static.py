"""Mapped poll service, nonmagic sampling prefix and SDK magic setter.

Static operands/CFG/rebasing, interval and integer identities only.
No target execution/emulation, service invocation or mutable MMIO model.
"""
import argparse
import json
import re
from hashlib import sha256
from pathlib import Path
import check_v4160_post_rf_leaves_static as previous

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
paths=previous.previous.paths
OUT=Path(__file__).with_name('v4160-nonmagic-service-static.json')
DETAILS=((0x43062,0x20002df2,0x663a6,0,
 'c032068d039379126d7ad6f73f88d8bbff4d2b38a4d452e018be661c666eace0',
 '696fa1e680c009be395611868c86142ffa929cf17062e1e0d95f886da8549f0e',
 'd233db21079691dcf987772b64716a0aea46eee5cd466b0f81e916281370af93'),
 (0x430ee,0x20002e3e,0x664e4,80,
 'b7d1987d7910750f363c19a2cf8181f76080b1ec31a837d80e98371662cf7688',
 '5cd826b0bfa19208a54e9acda26cb8459a2199c67687f5c6d3d4290199cc3d0b',
 '76f0d8e6f0673764b84043fef8b1001a617023c1d102b996c96adc11c98723bb'))
DESTINATIONS=(-90,-89,1428,1412,1429,1420)


def specs(role,index,at=None):
    source,entry,setter,delta,*_=DETAILS[index]
    pc=(entry if at is None else at) if role=='service' else setter if role=='setter' else previous.DETAILS[index][0][0]
    s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def lui(o,r,v):e(o,'lui',rd=r,imm=v)
    def imm(o,op,r,b,v):e(o,op,rd=r,rs1=b,imm=v)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    def load(o,r,b,v,w=4,**f):e(o,'load',rd=r,rs1=b,imm=v,width=w,**f)
    def byte(o,r,b,v):load(o,r,b,v,1,mnemonic='qk.c.lbu')
    def store(o,r,b,v,w=4,**f):e(o,'store',rs2=r,rs1=b,imm=v,width=w,**f)
    def binary(o,op,r,a,b):e(o,op,rd=r,rs1=a,rs2=b)
    def bz(o,r,t):e(o,'beqz',rs1=r,target=pc+t)
    if role=='service':
        lui(0,15,0x20003000);load(4,14,15,1340+delta);lui(8,15,4096);imm(10,'addi',15,15,1904)
        store(14,15,14,100);lui(16,15,0x20003000);load(20,15,15,1424+delta);load(24,13,15,144)
        imm(28,'slli',12,13,5);e(32,'bge',rs1=12,rs2=0,target=pc+48);load(36,13,15,144)
        imm(40,'slli',12,13,6);e(44,'blt',rs1=12,rs2=0,target=pc+52);load(48,13,14,100)
        e(50,'bnez',rs1=13,target=pc+24);e(52,'jr',rs1=1)
    elif role=='setter':
        e(0,'mv',rd=15,rs2=10);bz(2,10,104);byte(4,13,10,0);li(6,14,6);li(8,10,1)
        e(10,'bne',rs1=13,rs2=14,target=pc+106);byte(14,12,15,1);byte(16,13,15,2);byte(18,11,15,3)
        for o in (20,28,36,46,56):lui(o,14,0x20003000)
        for o,r,v in ((24,12,-90),(32,13,-89),(40,11,1428),(50,11,1412),(60,11,1429)):store(o,r,14,v+delta,1)
        byte(44,11,15,4);byte(54,11,15,5);byte(64,14,15,6);lui(66,15,0x20003000);store(70,14,15,1420+delta,1)
        lui(74,14,0x20003000);bz(78,12,98);bz(80,13,98);lui(82,15,0x12345000);imm(86,'addi',15,15,1656)
        store(90,15,14,1416+delta);li(94,10,0);e(96,'jr',rs1=1);store(98,0,14,1416+delta)
        e(102,'jump',target=pc+94);li(104,10,1);e(106,'jr',rs1=1)
    else:
        s={p:f for p,f in previous.specs('large',index)[1].items() if p<pc+340}
        load(120,14,15,4);lui(122,18,0xfffe0000);imm(124,'addi',18,18,255);imm(128,'andi',14,14,-2)
        store(130,14,15,4);load(132,14,15,56);lui(134,13,0xc000);imm(136,'addi',13,13,-256)
        binary(140,'and',14,14,18);binary(144,'or',14,14,13);store(146,14,15,56);load(148,14,15,4)
        imm(150,'ori',14,14,1);store(154,14,15,4);load(168,13,2,12);load(170,14,15,144)
        imm(174,'andi',14,14,63);store(178,14,9,0,1,mnemonic='qk.c.sb');load(180,14,15,148)
        imm(184,'srli',14,14,10);imm(186,'andi',14,14,127);store(190,14,13,0,1,mnemonic='qk.c.sb')
        load(192,14,15,4);lui(194,13,0xe000);imm(196,'addi',13,13,1792);imm(200,'andi',14,14,-2)
        store(202,14,15,4);load(204,14,15,56);binary(206,'and',14,14,18);binary(210,'or',14,14,13)
        store(212,14,15,56);load(214,14,15,4);imm(216,'ori',14,14,1);store(220,14,15,4)
        lui(234,13,0x20003000);load(238,14,15,144);imm(242,'andi',14,14,63);store(246,14,13,1429+delta,1)
        load(250,14,15,148);lui(254,13,0x20003000);imm(258,'srli',14,14,10);imm(260,'andi',14,14,127)
        store(264,14,13,1420+delta,1);load(268,14,15,4);lui(270,13,0xd000);imm(272,'addi',13,13,768)
        imm(276,'andi',14,14,-2);store(278,14,15,4);load(280,14,15,56);binary(282,'and',14,14,18)
        binary(286,'or',14,14,13);store(288,14,15,56);load(290,14,15,4);imm(292,'ori',14,14,1)
        store(296,14,15,4);load(306,14,8,1424+delta);store(318,15,19,1428+delta,1)
        lui(326,14,0x20003000);store(336,15,14,1412+delta,1)
    return pc,s


def edges(n,role):
    e={}
    for p,d in n.items():
        op=d['op']
        if op=='jr':check(d['rs1']==1,'nonmagic ordinary RET');q=[]
        elif op in ('beq','bne','beqz','bnez','bge','blt'):q=[p+d['size'],d['target']]
        elif op=='jump':q=[d['target']]
        else:q=[p+d['size']]
        if role!='prefix':check(all(v in n for v in q),'nonmagic complete local CFG')
        e[p]=q
    return e


def body(raw,role,index,at=None):
    pc,s=specs(role,index,at);n=decode(raw,pc)
    check(set(n)==set(s),'nonmagic '+role+' boundaries')
    for p,f in s.items():init.g(n,p,'nonmagic '+role+' operand '+hex(p-pc),**f)
    size,count,digest={'service':(54,16,DETAILS[index][4]),'setter':(108,36,DETAILS[index][5]),'prefix':(340,117,DETAILS[index][6])}[role]
    check((len(raw),len(n),sha256(raw).hexdigest())==(size,count,digest),'nonmagic '+role+' full identity')
    e=edges(n,role);stores=[d for d in n.values() if d['op']=='store'];loads=[d for d in n.values() if d['op']=='load']
    if role=='service':
        check((len(stores),len(loads))==(1,5),'nonmagic service full memory census')
        check({d['rd'] for d in n.values() if d.get('rd',0)}=={12,13,14,15},'nonmagic service exact GPR preservation')
        cycles=[c for c in previous.previous.previous.graphs.components(e) if len(c)>1 or c[0] in e[c[0]]]
        check(cycles==[[pc+x for x in (24,28,32,36,40,44,48,50)]],'nonmagic exact eight-node poll SCC')
        check(all(n[p]['op']!='store' and n[p].get('rd') not in (14,15) for p in cycles[0]),'nonmagic poll no base reload/store/countdown')
    elif role=='setter':
        check((len(stores),len(loads))==(8,7),'nonmagic setter full memory census')
        check({d['rd'] for d in n.values() if d.get('rd',0)}=={10,11,12,13,14,15},'nonmagic setter RA/SP/GP/S preserved')
        check(previous.acyclic(e),'nonmagic setter acyclic')
        check([p-pc for p,d in n.items() if d.get('rd')==12]==[14] and [p-pc for p,d in n.items() if d.get('rd')==13]==[4,16],'nonmagic marker uses already sampled bytes1/2')
    else:
        check({v-pc for qs in e.values() for v in qs if v not in n}=={340,3380},'nonmagic prefix only common/magic boundary exits')
        check([p-pc for p,d in n.items() if d['op']=='jalr']==[160,226,302],'nonmagic three call sites')
    return {'start':hex(pc),'bytes':len(raw),'sha256':digest,'instructions':list(n.values()),
        'normal_return_CFG':{hex(p):[hex(q) for q in qs] for p,qs in e.items()},'complete_function':role!='prefix'}


def choose(b,choices,cut=None):
    pc=int(b['start'],16);e=previous.previous.edge_map(b)
    return paths.chain(e,pc,{pc+p:pc+q for p,q in choices.items()},None if cut is None else pc+cut)


def encoding_candidates(data,base,displacements):
    stores=[];luis=[]
    for off in range(0,len(data)-3,2):
        v=int.from_bytes(data[off:off+4],'little')
        if v&127==0x23 and v>>12&7==2:
            imm=(v>>25)<<5|(v>>7&31);imm=imm-4096 if imm&2048 else imm
            if imm in displacements:stores.append({'pc':hex(base+off),'base_register':v>>15&31,'source_register':v>>20&31,'displacement':imm})
        if v&127==0x37 and v&0xfffff000==0x12345000:luis.append(hex(base+off))
    return {'standard_SW_immediate_matches':stores,'LUI_12345000_matches':luis,
        'scope':'every halfword-aligned four-byte encoding in provided bytes; includes possible data/overlapping decodes; not exhaustive effective-address or reachable-writer analysis'}


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[]
    text=header.decode('latin-1')  # Lossless mapping; match only the ASCII macro.
    check(re.search(r'#define\s+RFEND_TXCtuneSet\s+\(\(\s*bStatus_t\s*\(\*\)\s*\(\s*uint8_t\s*\*pParm\s*\)\s*\)\s*BLE_LIB_JT\(130\)\s*\)',text) is not None,'nonmagic SDK setter signature/index')
    check(0x40034+130*4==0x4023c,'nonmagic SDK fixed slot arithmetic')
    for i,(data,pr,detail) in enumerate(zip(carriers,parent['profiles'],DETAILS)):
        source,entry,setter,delta,*_=detail;pc=previous.DETAILS[i][0][0];mapping=init.binding.profile(data,pr['label'])
        copy=mapping['first_copy'];lo=int(copy['destination'],16);end=int(mapping['first_copy_end_exclusive'],16)
        check(lo<=entry<entry+54<=end and int(copy['source'],16)+entry-lo==source,'nonmagic complete helper first-copy mapping')
        raw=init.binding.take(data,source,54);service=body(raw,'service',i);flash_service=body(raw,'service',i,source)
        normalized=[]
        for b in (service,flash_service):
            bp=int(b['start'],16);normalized.append([{k:((v-bp) if k in ('pc','target') else v) for k,v in d.items()} for d in b['instructions']])
        check(normalized[0]==normalized[1],'nonmagic flash/RAM instruction translation')
        service_paths={name:choose(service,choices) for name,choices in (
            ('bit26_zero_control_zero',{32:48,44:48,50:52}),
            ('bit26_one_second_bit25_zero_control_zero',{32:36,44:48,50:52}),
            ('bit26_one_second_bit25_one',{32:36,44:52,50:52}))}
        check(hex(entry+36) not in service_paths['bit26_zero_control_zero'] and hex(entry+48) not in service_paths['bit26_one_second_bit25_one'],'nonmagic short-circuit fresh reads')
        loop={entry+24:[entry+28],entry+28:[entry+32],entry+32:[entry+48],entry+48:[entry+50],entry+50:[entry+24]}
        service_edges=previous.previous.edge_map(service)
        check(all(q in service_edges[p] for p,qs in loop.items() for q in qs),'nonmagic continuing witness uses actual CFG edges')
        check(not previous.acyclic(loop),'nonmagic continuing poll CFG witness')
        prefix=body(init.binding.take(data,pc,340),'prefix',i)
        full_n,full_e=previous.inspect(init.binding.take(data,pc,3388),'large',i)
        selected=paths.chain(full_e,pc,{pc+116:pc+120});picked=[full_n[int(p,16)] for p in selected]
        calls=[d for d in picked if d['op']=='jalr']
        check(len(calls)==3,'nonmagic selected path uses three service returns')
        for off,d in zip((160,226,302),calls):
            au=full_n[pc+off-4];check((au['pc']+au['imm']+d['imm'])&0xfffffffe==entry,'nonmagic actual AUIPC/JALR link')
        destinations=[0x20003000+v+delta for v in DESTINATIONS]
        writes=previous.previous.preservation(delta,[(p,1) for p in destinations])
        for p in destinations:check(paths.origin.separated(p,1,entry,54),'nonmagic work fields exclude mapped service bytes')
        check([d['pc']-pc for d in picked if d['op']=='store' and d['width']==1]==[178,190,246,264,318,336],'nonmagic exactly six RAM byte publications')
        check(not any(d['pc']==pc+3380 for d in picked),'nonmagic path does not consume magic')
        setter_body=body(init.binding.take(data,setter,108),'setter',i)
        check(init.binding.word(data,0x4023c)==setter,'nonmagic candidate SDK setter slot')
        setter_paths={name:choose(setter_body,choices) for name,choices in (
            ('null',{2:104,10:106,78:98,80:98}),('bad_tag',{2:4,10:106,78:98,80:98}),
            ('byte1_zero',{2:4,10:14,78:98,80:98}),('byte2_zero',{2:4,10:14,78:80,80:98}),
            ('both_nonzero',{2:4,10:14,78:80,80:82}))}
        sn={d['pc']:d for d in setter_body['instructions']}
        check(all(not any(sn[int(p,16)]['op']=='store' for p in setter_paths[name]) for name in ('null','bad_tag')),'nonmagic rejected setter has no stores')
        check([sn[int(p,16)]['pc']-setter for p in setter_paths['both_nonzero'] if sn[int(p,16)]['op']=='store']==[24,32,40,50,60,70,90],'nonmagic successful setter seven stores')
        scan=encoding_candidates(data,0x40000,{1416+delta})
        check([r['pc'] for r in scan['standard_SW_immediate_matches']]==[hex(setter+90),hex(setter+98),hex(pc+3380)],'nonmagic bounded SW candidate census')
        check(scan['LUI_12345000_matches']==[hex(setter+82),hex(pc+106)],'nonmagic bounded magic-LUI candidate census')
        profiles.append({'label':pr['label'],'service_source':hex(source),'service_entry':hex(entry),'first_copy':copy,
            'mapped_service':service,'flash_service':flash_service,'service_three_exit_paths':service_paths,'service_no_timeout':True,
            'service_poll_SCC_offsets':[24,28,32,36,40,44,48,50],
            'large_prefix':prefix,'nonmagic_full_local_normal_return_path':selected,
            'conditional_six_byte_publications':writes,'sample_groups':[
                {'call_offset':160,'low6_destination':hex(destinations[0]),'shift10_low7_destination':hex(destinations[1])},
                {'call_offset':226,'low6_destination':hex(destinations[4]),'shift10_low7_destination':hex(destinations[5])},
                {'call_offset':302,'low6_destination':hex(destinations[2]),'shift10_low7_destination':hex(destinations[3])}],
            'setter_SDK_name':'RFEND_TXCtuneSet','setter_slot':'0x4023c','setter':setter_body,'setter_paths':setter_paths,
            'setter_byte_destinations':[hex(p) for p in destinations],'magic_word':hex(0x20003588+delta),
            'bounded_encoding_candidates':scan,'actual_setter_APP_caller_proved':False,'actual_installed_binding_proved':False})
    app_scan=encoding_candidates(image,0x8000,{1416,1496})
    check(app_scan['standard_SW_immediate_matches']==[] and app_scan['LUI_12345000_matches']==[],'nonmagic bounded APP encoding census')
    return {'schema':'TSL9-nonmagic-service-static-v1','profile':parent['profile'],'APP_sha256':sha256(image).hexdigest(),'profiles':profiles,
        'APP_bounded_encoding_candidates':app_scan,
        'scope':'per candidate full mapped54B/16instruction helper at both PC coordinates, full108B/36instruction setter, full340B/117instruction large prefix; old full large structural/common contract reused; no new C bytes',
        'poll_contract':'SW6000(decimal) to R0+100, then fresh Q0+144 first bit26; only if set read second fresh Q0+144 bit25. Both set exits without control read; otherwise fresh R0+100 zero exits, nonzero repeats. Eight-node SCC has no base reload/countdown/timeout; actual eventual completion unproved',
        'nonmagic_return':'three distinct helper invocations require actual matching RAM load image, pointer mappings, normal accesses/instructions and eventual poll exit each. Helpers preserve needed frame/S/GP/A0/A1; six fresh sampled byte publications precede old common block. With no adverse alias/MMIO/asynchronous writers, metadata and saved frame survive and large returns A0 opaque. Outer tail still needs later wait completion',
        'setter_contract':'null pointer or initial tag!=6 returns1 without stores. Accepted tag6 writes six bytes in source1..6 order, then magic12345678 iff already loaded source1/source2 both nonzero, else0; returns0. No length/range validation, atomic-source snapshot or actual APP invocation inferred. Aliasing can change later source reads; marker uses preserved A2/A3 samples',
        'source_boundary':'candidate fixed SDK slot identifies a possible marker producer; not proof it ran before large or is installed. Encoding scan covers specified halfword-aligned SW/LUI patterns only, not GP/rebased/pointer/copy/fill/indirect/asynchronous writers or all reachable code',
        'remaining':['actual setter callers and ordering before large','hardware wait progress and actual provider/code retention','remaining initializer callees/tail and later lifetimes'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    mutations=0
    for i,(data,detail) in enumerate(zip(carriers,DETAILS)):
        source,entry,setter,_,*_=detail;pc=previous.DETAILS[i][0][0]
        for role,at,raw in (('service',entry,init.binding.take(data,source,54)),('service',source,init.binding.take(data,source,54)),
                ('setter',setter,init.binding.take(data,setter,108)),('prefix',pc,init.binding.take(data,pc,340))):
            n=decode(raw,at)
            for p,d in n.items():
                off=p-at;z=d['size'];buf=bytearray(raw);buf[off:off+z]=(int.from_bytes(buf[off:off+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
                try:body(buf,role,i,at if role=='service' else None)
                except RuntimeError as e:check(str(e).startswith('nonmagic '+role+' operand '),'nonmagic specified mutation guard '+str(e))
                else:raise RuntimeError('nonmagic mutation escaped')
                mutations+=1
    check(mutations==370,'nonmagic mutation census '+str(mutations))
    for upper in range(65536):
        value=upper<<16
        for shift in (5,6):
            check(bool(((value<<shift)&0xffffffff)&0x80000000)==bool(value&(1<<(31-shift))),'nonmagic signed shift sign identity')
            check((((value|65535)<<shift)&0x80000000)==((value<<shift)&0x80000000),'nonmagic low16 irrelevant to sign')
    marker=sum(a!=0 and b!=0 for a in range(256) for b in range(256))
    check(marker==65025 and 65536-marker==511,'nonmagic full two-byte marker predicate census')
    check(4096+1904==6000 and 0x12345000+1656==0x12345678,'nonmagic constants')
    print('PASS:370 operand mutations rejected;65536 high-half signed-shift cases and65536 two-byte marker cases')


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
    tests(carriers);output=(json.dumps(ledger,indent=1,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'nonmagic exact ledger replay')
    print('PASS:full mapped poll service/three nonmagic joins/six byte sources/SDK marker setter; exact ledger')
    print('PASS:NO target execution; actual APP setter caller, installed binding and hardware progress UNPROVED')


if __name__=='__main__':main()
