"""Offline list lookup and two pure integer output maps.

Original operands/CFG and interval/branch certificates only. No target ISA
execution/emulation, mutable register/RAM machine, linked-list or provider model.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_request_core_static as previous

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-request-output-static.json')
PARTS=('lookup','signed_map','unsigned_map')
STARTS=((0x55108,0x639ca,0x63966),(0x551d2,0x63ab4,0x63a50))
SIZES=(24,98,100)
COUNTS=(9,36,37)
HASHES=(('a4f5290ffabd758e28dcb1a814d2e3a532159c08fbd1a5d201452754e3b89a02','02c74eb297403042d031b821bbd2a49806b6f80f0ae65886f2ca7719ae49485b','f24cecffc2c307dd170e3740cd5f9547fccb0ead5f40c87440d73e959364e32f'),
 ('9ab880d04b37819190908a01c23280a0edbe59b144aba86af0c3ed84d39fccce','02c74eb297403042d031b821bbd2a49806b6f80f0ae65886f2ca7719ae49485b','f24cecffc2c307dd170e3740cd5f9547fccb0ead5f40c87440d73e959364e32f'))


def specs(part,index):
    pc=STARTS[index][PARTS.index(part)];s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    def ai(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def br(o,op,a,b,t):e(o,op,rs1=a,rs2=b,target=pc+t)
    def ret(o):e(o,'jr',rs1=1)
    def mv(o,r,b):e(o,'mv',rd=r,rs2=b)
    def j(o,t):e(o,'jump',target=pc+t)
    if part=='lookup':
        e(0,'lui',rd=15,imm=0x20003000);e(4,'load',rd=15,rs1=15,imm=1044+80*index,width=4);e(8,'bnez',rs1=15,target=pc+14)
        mv(10,10,15);ret(12);e(14,'load',rd=14,rs1=15,imm=8,width=1);br(16,'beq',14,10,10);e(20,'load',rd=15,rs1=15,imm=0,width=4);j(22,8)
    elif part=='signed_map':
        li(0,15,-17);br(2,'blt',10,15,94)
        for o,threshold,value in ((6,-9,3),(14,-4,5),(22,-2,7)):
            li(o,14,threshold);li(o+2,15,value);br(o+4,'blt',10,14,90)
        li(30,15,9);br(32,'bge',0,10,90)
        for o,x,v in ((36,1,11),(44,2,13),(52,3,17),(60,4,21),(68,5,27)):
            li(o,14,x);li(o+2,15,v);br(o+4,'beq',10,14,90)
        li(76,14,6);ai(78,15,0,63);br(82,'bne',10,14,90);ai(86,15,0,37);mv(90,10,15);ret(92);li(94,15,1);j(96,90)
    else:
        ai(0,15,0,62);br(4,'bltu',15,10,96);ai(8,14,0,36);li(12,15,6);br(14,'bltu',14,10,92)
        for o,threshold,v in ((18,26,5),(26,20,4),(34,16,3),(42,12,2),(50,10,1),(58,8,0),(66,6,-3),(74,4,-5)):
            li(o,14,threshold);li(o+2,15,v);br(o+4,'bltu',14,10,92)
        li(82,14,2);li(84,15,-18);br(86,'bgeu',14,10,92);li(90,15,-10);mv(92,10,15);ret(94);li(96,15,7);j(98,92)
    return s


def body(raw,part,index):
    k=PARTS.index(part);pc=STARTS[index][k];s=specs(part,index);n=decode(raw,pc)
    check(set(n)==set(s),'output '+part+' boundaries')
    for p,f in s.items():init.g(n,p,'output '+part+' operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[k],HASHES[index][k]),'output '+part+' identity')
    edges={}
    for p,d in n.items():
        op=d['op'];q=[p+d['size']]
        if op=='jr':check(d['rs1']==1,'output RET RA');q=[]
        elif op in ('bnez','beq','bne','blt','bge','bltu','bgeu'):q.append(d['target'])
        elif op=='jump':q=[d['target']]
        check(op not in ('store','jal','jalr','call_indirect'),'output no stores/calls')
        check(all(v in n for v in q),'output '+part+' closedCFG');edges[p]=q
    seen={pc};todo=[pc]
    while todo:
        for q in edges[todo.pop()]:
            if q not in seen:seen.add(q);todo.append(q)
    check(seen==set(n),'output '+part+' all nodes locally reachable')
    if part!='lookup':
        check(all(v['op']!='load' for v in n.values()),'output integer maps no memory reads')
        check(all(v.get('rd') in (None,10,14,15) for v in n.values()),'output integer maps onlyA0/A4/A5 writes')
    return {'start':hex(pc),'end_exclusive':hex(pc+SIZES[k]),'bytes':SIZES[k],'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),
            'conditional_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},'complete_local_body':True,'stores':0,'calls':0,'frame_bytes':0}


def uniform_relation(lo,hi,op,c):
    # Arithmetic proof over a whole interval, not target instruction evaluation.
    if op=='lt':yes,no=hi<c,lo>=c
    elif op=='gt':yes,no=lo>c,hi<=c
    elif op=='le':yes,no=hi<=c,lo>c
    elif op=='eq':yes,no=lo==hi==c,c<lo or c>hi
    elif op=='ne':yes,no=c<lo or c>hi,lo==hi==c
    else:raise RuntimeError('output relation')
    check(yes!=no,'output interval must not straddle branch threshold');return yes


def interval_certificates(b,part,index):
    pc=int(b['start'],16);n={v['pc']:v for v in b['instructions']};e={int(p,16):[int(q,16) for q in qs] for p,qs in b['conditional_CFG'].items()};s=specs(part,index)
    val=lambda o:s[pc+o]['imm']
    if part=='signed_map':
        bounds=[(-2147483648,val(0)-1,94),(val(0),val(6)-1,8),(val(6),val(14)-1,16),(val(14),val(22)-1,24),(val(22),0,30)]
        bounds += [(val(o),val(o),r) for o,r in ((36,38),(44,46),(52,54),(60,62),(68,70),(76,86))]
        bounds += [(val(76)+1,2147483647,78)]
        schema=[(2,'lt',val(0)),(10,'lt',val(6)),(18,'lt',val(14)),(26,'lt',val(22)),(32,'le',0)]
        schema += [(o,'eq',val(o-4)) for o in (40,48,56,64,72)];schema +=[(82,'ne',val(76))]
        expected=[1,3,5,7,9,11,13,17,21,27,37,63];domain=(-2147483648,2147483647)
    else:
        bounds=[(0,val(82),84),(val(82)+1,val(74),90),(val(74)+1,val(66),76),(val(66)+1,val(58),68),
                (val(58)+1,val(50),60),(val(50)+1,val(42),52),(val(42)+1,val(34),44),(val(34)+1,val(26),36),
                (val(26)+1,val(18),28),(val(18)+1,val(8),20),(val(8)+1,val(0),12),(val(0)+1,4294967295,96)]
        schema=[(4,'gt',val(0)),(14,'gt',val(8))]+[(o,'gt',val(o-4)) for o in (22,30,38,46,54,62,70,78)]
        schema +=[(86,'le',val(82))]
        expected=[-18,-10,-5,-3,0,1,2,3,4,5,6,7];domain=(0,4294967295)
    check((bounds[0][0],bounds[-1][1])==domain and all(a[1]+1==z[0] for a,z in zip(bounds,bounds[1:])),'output intervals tile full32 domain')
    rows=[]
    for row,(lo,hi,reply_at) in enumerate(bounds):
        choices={pc+o:n[pc+o]['target'] if uniform_relation(lo,hi,op,c) else pc+o+n[pc+o]['size'] for o,op,c in schema}
        path=previous.previous.previous.previous.previous.paths.chain(e,pc,choices)
        definitions=[int(p,16)-pc for p in path if n[int(p,16)].get('rd')==15]
        check(definitions[-1]==reply_at and val(reply_at)==expected[row],'output final literal reply definition')
        rows.append({'lo':lo,'hi':hi,'logical_reply':val(reply_at),'RV32_reply_bits':val(reply_at)&0xffffffff,'reply_definition_offset':reply_at,
                     'path':path,'all_branch_relations_uniform_over_interval':True})
    check(len(rows)==12,'output twelve interval certificates');return rows


def lookup_certificates(b):
    pc=int(b['start'],16);edges={int(p,16):[int(q,16) for q in qs] for p,qs in b['conditional_CFG'].items()}
    paths={'head_null':[0,4,8,10,12],'first_match':[0,4,8,14,16,10,12],'one_skip_then_null':[0,4,8,14,16,20,22,8,10,12]}
    for offsets in paths.values():
        check(all(pc+z in edges[pc+a] for a,z in zip(offsets,offsets[1:])),'output lookup selected edges')
    return {name:[hex(pc+v) for v in offsets] for name,offsets in paths.items()}


def interval_value(rows,x):
    matches=[r['logical_reply'] for r in rows if r['lo']<=x<=r['hi']];check(len(matches)==1,'output interval membership');return matches[0]


def composition(q,r):
    nonsentinel=[];sentinel=[]
    for raw in range(256):
        s=raw-256 if raw&128 else raw
        if s!=127:
            capped=min(s,6);code=interval_value(q,capped);reply=interval_value(r,code)
            nonsentinel.append({'raw_query25':raw,'signed_query25':s,'capped_input':capped,'Q_reply':code,'R_reply':reply,'output_byte':reply&255})
        code=interval_value(q,s);reply=interval_value(r,code)
        sentinel.append({'old_object21_byte':raw,'old_signed_value':s,'Q_reply':code,'R_reply':reply,'output_byte':reply&255})
    a=sorted({v['R_reply'] for v in nonsentinel});z=sorted({v['R_reply'] for v in sentinel})
    check(a==[-18,-10,-5,-3,0,1,2,3,4,5,6] and z==a+[7],'output exact core composition domains')
    check(len(nonsentinel)==255 and len(sentinel)==256,'output composition case census')
    return {'nonsentinel_query25_cases':nonsentinel,'sentinel_old_object21_cases':sentinel,'nonsentinel_signed_results':a,'sentinel_signed_results':z,
            'limits':'composition is integer algebra on guarded literal intervals; core ABI/target identity/nonalias/outputpointer/frame preservation required; no physical unit assigned'}


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[]
    for i,(data,pr) in enumerate(zip(carriers,parent['profiles'])):
        windows={part:body(init.binding.take(data,STARTS[i][k],SIZES[k]),part,i) for k,part in enumerate(PARTS)}
        rows={part:interval_certificates(windows[part],part,i) for part in PARTS[1:]};paths=lookup_certificates(windows['lookup'])
        check(pr['object_acquisition']['direct_target']==windows['lookup']['start'],'output published lookup join')
        check([pr['body']['calls'][k]['target'] for k in (4,5)]==[windows['signed_map']['start'],windows['unsigned_map']['start']],'output published Q/R call order')
        head=0x20003414+80*i;lp=STARTS[i][0];ln={v['pc']:v for v in windows['lookup']['instructions']}
        check(ln[lp+4]['imm']+0x20003000==head,'output exact list head slot')
        profiles.append({'label':pr['label'],'bodies':windows,'interval_certificates':rows,'lookup_selected_paths':paths,
            'lookup':{'head_slot':hex(head),'context_relation':'B+92 from previouscore; distinct from B+88 busyobject slot',
                'entry':'full32A0 key; published register chain supplies1 under preceding caller contract','loop':'while node!=0:ifU8[node+8]==entrykey returnnode;node=U32[node+0];null returns0',
                'read_extent':'at least9readablebytes/node; returns no allocation/108byte extent guarantee','key_domain':'byte key compared to full32entryA0; >255 cannotmatch, but termination still depends onlist',
                'finite_bound_proved':False,'required':'valid node/next pointers, progress/acyclicity andstable readablelist if termination claimed; frameless, no calls/stores or explicit pointer retention'},
            'signed_map':{'name':'Q','input':'signed32A0','output':'literalpositive integer from full32 interval certificate','effects':'no memoryread/store/call/frame; only A0/A4/A5 written'},
            'unsigned_map':{'name':'R','input':'unsigned32A0','output':'logical signedliteral represented inRV32twoscomplement bits','effects':'no memoryread/store/call/frame; only A0/A4/A5 written'},
            'core_composition':composition(rows['signed_map'],rows['unsigned_map']),
            'output_closure':{'normal_path':'core caps signedquery25 to6 unless127, Q ->object104byte, fullQreply ->R ->object21byte andfresh outputpointer',
                'sentinel127':'core initiallywritesglobalbyte tooutput but reads preexisting signedobject21 forQ; under samepointer/nonalias preservation finalRbyte supersedes initialglobalbyte',
                'reply_vs_status':'R result can benegative asfullregister; outputSBretainslow8; corestatus remains separately0/7/12/17/18/69',
                'remaining_limit':'earlycore paths withoutoutputwrite, list initialcontents, actualinstalled targets, callback allocation, provider effects andsource/frame/outputpointer lifetime still unproved'},
            'actual_installed_binding_proved':False,'target_execution_or_emulation':False})
    return {'schema':'TSL9-request-output-static-v1','profile':parent['profile'],'APP_sha256':sha256(image).hexdigest(),'profiles':profiles,
            'scope':'two full24Blookup/98BQ/100BR bodies;444originalbytes/164instructions;48full32interval certificates plus6selectedlookup paths;1022corecomposition cases',
            'boundary':'Q/R pure integer body contracts and conditional core composition; no list execution or termination proof, no actualinstalled binding/object/pointer lifetime proof',
            'remaining':['list head/next/key writers andallocationcallback source','200004bc/20000332 installedproviders andborrowed6byte retention','earlycore outputgap andnotification providers','callback enumerators/missingROMpattern'],
            'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    mutations=intervals=paths=0
    for i,data in enumerate(carriers):
        for k,part in enumerate(PARTS):
            pc=STARTS[i][k];raw=init.binding.take(data,pc,SIZES[k]);b=body(raw,part,i)
            if part=='lookup':paths+=len(lookup_certificates(b))
            else:intervals+=len(interval_certificates(b,part,i))
            for p,d in decode(raw,pc).items():
                at=p-pc;z=d['size'];buf=bytearray(raw);buf[at:at+z]=(int.from_bytes(buf[at:at+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
                try:body(buf,part,i)
                except RuntimeError as e:check(str(e).startswith('output '+part+' operand '),'output specified mutation '+str(e))
                else:raise RuntimeError('output mutation escaped')
                mutations+=1
    check((mutations,intervals,paths)==(164,48,6),'output mutation/certificate census')
    print('PASS:164 operand mutations rejected;444 original bytes;48 full32 interval certificates;6 selected lookup paths;1022 core composition cases')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');o=parser.parse_args()
    image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK identity')
    carriers=[]
    for label,folder,tail,z,digest in init.binding.PROFILES:
        data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidate identity '+label);carriers.append(data)
    raw_hex=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
    coverage=sparse.derive(image,carriers,header,raw_hex,sparse.parser());ledger=derive(image,carriers,header,coverage);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers)
    output=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'output exact ledger replay')
    print('PASS:Q/R branch intervals andcore output algebra;lookup list/progress boundary;exact ledger')
    print('PASS:NO target execution/emulation;list/source/installedprovider/pointer lifetime UNPROVED')


if __name__=='__main__':main()
