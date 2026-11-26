"""Offline operand/CFG proof for the first outer ID6 initializer.

No target instructions, allocator, fill, callbacks or device accesses execute.
Arithmetic domains below are closed-form integer checks, not an ISA model.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_gate_return_publication_static as previous

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
paths=previous.paths
OUT=Path(__file__).with_name('v4160-outer-id6-initializer-static.json')
PARTS=('initializer','resources')
STARTS=((0x4da70,0x4edd2),(0x4db08,0x4ee6a))
SIZES=(386,160)
COUNTS=(123,55)
HASHES=(('49e6f304de8dca4933e6073ab0cb634c7f9e9e74f40fb9832adbba4e8d7c9697',
         'ff03c3855a727e51f327cf10a39c9fd02be5586841ce170111552a66d825de42'),
        ('ff4eb38c1a3e441e3c4bc3e9334be258c48dd8eb3cb7676fbccd873011e23f2f',
         '61f32b743b20e037e35ff4fa289cc2dc507850562dba18ed9793a24b139017e6'))


def specs(part,index):
    pc=STARTS[index][PARTS.index(part)];d=80*index;s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def lui(o,r,v=0x20003000):e(o,'lui',rd=r,imm=v)
    def ai(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    def ld(o,r,b,v,w=4):e(o,'load',rd=r,rs1=b,imm=v,width=w)
    def st(o,r,b,v,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    def sh(o,op,r,b,v):e(o,op,rd=r,rs1=b,imm=v)
    def binary(o,op,r,a,b):e(o,op,rd=r,rs1=a,rs2=b)
    def beqz(o,r,t):e(o,'beqz',rs1=r,target=pc+t)
    def pair(o,upper,low,r=1,link=1):
        e(o,'auipc',rd=r,imm=upper);e(o+4,'jalr',rd=link,rs1=r,imm=low)
    if part=='resources':
        lui(0,15);ld(4,10,15,513+d,1);ai(8,2,2,-16);st(10,8,2,8);lui(12,8)
        sh(16,'andi',15,10,3);ai(20,8,8,940+d);sh(24,'srli',10,10,2);st(26,15,8,9,1)
        binary(28,'add',15,15,10);st(30,1,2,12);st(32,9,2,4);st(34,15,8,8,1);beqz(36,15,150)
        ai(38,10,0,60);binary(42,'mul',10,15,10);lui(46,11,0x9000);ai(48,11,11,1);lui(50,9)
        pair(54,0x1ffb1000,568-152*index);ld(62,12,8,8,1);ai(64,15,0,60);li(68,11,0)
        binary(70,'mul',12,12,15);st(74,10,9,852+d);pair(78,0x1ffb1000,1404-152*index)
        ld(86,15,9,852+d);ld(90,13,8,8,1);li(92,14,0);ai(94,15,15,2);li(96,12,-1)
        e(98,'blt',rs1=14,rs2=13,target=pc+132);ld(102,8,2,8);ld(104,1,2,12);ld(106,9,2,4)
        lui(108,10);ai(112,12,0,48);li(116,11,0);ai(118,10,10,856+d);ai(122,2,2,16)
        pair(124,0x1ffb1000,1358-152*index,6,0);st(132,12,15,0,2);st(134,0,15,2,1);st(138,0,15,42)
        ai(142,14,14,1);ai(144,15,15,60);e(148,'jump',target=pc+98)
        ld(150,1,2,12);ld(152,8,2,8);ld(154,9,2,4);ai(156,2,2,16);e(158,'jr',rs1=1)
    else:
        lui(0,15);st(4,0,15,-94+d,1);lui(8,15);ai(12,2,2,-48);li(14,14,1);st(16,0,15,-100+d,1)
        lui(20,15);st(24,14,15,796+d,1);st(28,19,2,28);lui(30,15);lui(34,19)
        st(38,8,2,40);st(40,9,2,36);st(42,18,2,32);lui(44,8);lui(48,9);st(52,0,15,-91+d,1)
        lui(56,18);lui(60,15);ai(64,19,19,-93+d);st(68,1,2,44);st(70,20,2,24);st(72,10,2,12)
        st(74,0,8,-96+d,1);st(78,0,9,-95+d,1);st(82,0,15,-98+d,2);st(86,0,18,-104+d);st(90,0,19,0,1)
        e(94,'jal',rd=1,target=STARTS[index][1]);ld(98,10,2,12);lui(100,15);ai(104,12,0,48)
        st(108,10,15,788+d,1);lui(112,10);ai(116,10,10,800+d);li(120,11,0)
        pair(122,0x1ffb3000,-1870-152*index);lui(130,20);ld(134,10,20,848+d,1)
        ai(138,8,8,-96+d);ai(142,9,9,-95+d);ai(146,18,18,-104+d);beqz(150,10,206)
        lui(152,11,0x5000);ai(154,11,11,-1020);sh(158,'slli',10,10,4);pair(160,0x1ffb2000,1328-152*index)
        lui(168,14);st(172,10,14,784+d);beqz(176,10,206);ld(178,12,20,848+d,1);ai(182,15,20,848+d)
        ld(186,15,15,1,1);st(188,12,19,0,1);li(192,11,0);sh(194,'slli',12,12,4);st(196,15,9,0,1)
        pair(198,0x1ffb3000 if index==0 else 0x1ffb2000,-1946 if index==0 else 1998)
        lui(206,15);ld(210,10,15,948+d,1);ld(214,15,9,0,1);lui(216,11,0x5000);ai(218,11,11,-1019)
        binary(222,'add',10,10,15);sh(224,'andi',10,10,255);st(228,10,8,0,1);sh(230,'slli',10,10,4)
        pair(232,0x1ffb2000,1256-152*index);st(240,10,18,0);beqz(244,10,376);ld(246,12,8,0,1);li(248,11,0)
        sh(250,'slli',12,12,4);pair(252,0x1ffb3000 if index==0 else 0x1ffb2000,-2000 if index==0 else 1944)
        ld(260,14,18,0);ld(264,13,8,0,1);li(266,15,0);ai(268,14,14,9);li(270,12,-1)
        e(272,'bne',rs1=13,rs2=15,target=pc+364);e(276,'jal',rd=1,target=0x4efd8+152*index)
        li(280,15,12);binary(282,'mul',10,10,15);lui(286,11,0x5000);ai(288,11,11,-1018)
        sh(292,'slli',10,10,16);sh(294,'srli',10,10,16);pair(296,0x1ffb2000,1192-152*index)
        lui(304,15);st(308,10,15,792+d);e(312,'mv',rd=8,rs2=10);beqz(314,10,338)
        e(316,'jal',rd=1,target=0x4efd8+152*index);li(320,12,12);binary(322,'mul',12,10,12)
        li(326,11,0);e(328,'mv',rd=10,rs2=8);pair(330,0x1ffb2000,2018-152*index)
        for o,r,v in ((338,8,40),(340,1,44),(342,9,36),(344,18,32),(346,19,28),(348,20,24)):ld(o,r,2,v)
        lui(350,10,0x4e000);ai(354,10,10,-1770+152*index);ai(358,2,2,48)
        e(360,'jal',rd=0,target=0x4efe2+152*index);ai(364,15,15,1);st(366,12,14,0,1)
        sh(368,'andi',15,15,255);ai(372,14,14,16);e(374,'jump',target=pc+272)
        st(376,0,8,0,1);st(380,0,9,0,1);e(384,'jump',target=pc+276)
    return pc,s


def body(raw,part,index):
    k=PARTS.index(part);pc,s=specs(part,index);n=decode(raw,pc)
    check(set(n)==set(s),'id6 '+part+' boundaries')
    for p,f in s.items():init.g(n,p,'id6 '+part+' operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[k],HASHES[index][k]),'id6 '+part+' identity')
    edges={};calls=[];tails=[]
    for p,d in n.items():
        op=d['op'];q=[p+d['size']]
        if op in ('beqz','bne','blt'):q.append(d['target'])
        elif op=='jump':q=[d['target']]
        elif op=='jr':check(d['rs1']==1,'id6 ordinary RET');q=[]
        elif op in ('jal','jalr'):
            if op=='jal':t=d['target']
            else:
                a=n.get(p-4,{});check(a.get('op')=='auipc' and a['rd']==d['rs1'],'id6 adjacent call pair')
                t=(p-4+a['imm']+d['imm'])&0xfffffffe
            item={'pc':hex(p),'offset':p-pc,'target':hex(t),'rd':d['rd']}
            if d['rd']==0:tails.append(item);q=[]
            else:calls.append(item)
        check(all(t in n for t in q),'id6 '+part+' local CFG closed');edges[p]=q
    reachable={pc};todo=[pc]
    while todo:
        for t in edges[todo.pop()]:
            if t not in reachable:reachable.add(t);todo.append(t)
    check(reachable==set(n),'id6 '+part+' all nodes locally reachable')
    stores=[d for d in n.values() if d['op']=='store'];loads=[d for d in n.values() if d['op']=='load']
    check((len(stores),len(loads))==((26,15) if k==0 else (9,10)),'id6 '+part+' memory census')
    check(len(calls)==(10 if k==0 else 2) and len(tails)==1,'id6 '+part+' call census')
    if k==0:
        check(not any(d['op']=='jr' for d in n.values()),'id6 initializer only tail exit')
        check([(d['rs2'],d['imm']) for d in stores if d['rs1']==2]==[(19,28),(8,40),(9,36),(18,32),(1,44),(20,24),(10,12)],'id6 initializer frame exact')
        check([(d['rd'],d['imm']) for d in loads if d['rs1']==2]==[(10,12),(8,40),(1,44),(9,36),(18,32),(19,28),(20,24)],'id6 initializer restores exact')
    else:
        check([(d['rs2'],d['imm']) for d in stores if d['rs1']==2]==[(8,8),(1,12),(9,4)],'id6 resource frame exact')
        check([d['pc']-pc for d in n.values() if d['op']=='jr']==[158],'id6 only zero-count ordinary RET')
        check(not any(d['op'] in ('beqz','bne','blt') for p,d in n.items() if pc+58<p<pc+98),'id6 no allocator-result null guard before fill/loop setup')
    return {'start':hex(pc),'bytes':len(raw),'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),
        'instruction_count':len(n),'stores':len(stores),'loads':len(loads),'complete_local_function':True,
        'normal_return_CFG':{hex(p):[hex(q) for q in v] for p,v in edges.items()},
        'calls':calls,'tail_exits':tails,'call_edges_are_return_premises':True}


def domains():
    values=[{'byte':b,'low2':b&3,'quarter':b>>2,'count':(b&3)+(b>>2),'allocation_bytes':60*((b&3)+(b>>2))} for b in range(256)]
    check(min(v['count'] for v in values)==0 and max(v['count'] for v in values)==66,'id6 count domain')
    check([v['byte'] for v in values if v['count']==0]==[0],'id6 count zero iff byte zero')
    check(max(v['allocation_bytes'] for v in values)==3960,'id6 allocation bound')
    check(values[14]['count']==5 and values[14]['allocation_bytes']==300,'id6 source default14 is nonzero')
    # Index interval identities only: no memory accesses or loop execution.
    for count in range(256):
        check(all((k&255)!=count for k in range(count)) and (count&255)==count,'id6 local byte-loop bound')
    return values


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[];values=domains()
    for i,(data,pr) in enumerate(zip(carriers,parent['profiles'])):
        delta=80*i;g=0x20003000;pc,callee=STARTS[i];F=g+492+delta;D=g+940+delta
        windows={p:body(init.binding.take(data,STARTS[i][k],SIZES[k]),p,i) for k,p in enumerate(PARTS)}
        check(pr['cut_before_first_outer_initializer']=={'pc':pr['cut_before_first_outer_initializer']['pc'],'target':hex(pc),'A0':6,'A1':'0xffffffff','A2':7},'id6 inherited exact call inputs')
        check(pr['first_outer_registration']['new_count']==7,'id6 inherited task count7')
        prefix=[(g+o+delta,w,v) for o,w,v in ((-94,1,0),(-100,1,0),(796,1,1),(-91,1,0),(-96,1,0),(-95,1,0),(-98,2,0),(-104,4,0),(-93,1,0))]
        ctx=g+previous.role.DETAILS[i]['ctx']
        protected=[(ctx+1,1),(ctx+2,1),(ctx+3,1),(ctx+40,4),(paths.layout.T,4*212),(paths.layout.A+8,16),(0x200040a6,1),(0x20004184,1),(F+21,1),(F+36,4),(F+68,4)]
        for a,z,_ in prefix:
            for b,w in protected:check(paths.origin.separated(a,z,b,w),'id6 prefix excludes live task/source fields')
        # Direct local source/ID stores, not a claim about unknown dynamic payload or heap metadata.
        for a,z in ((D+8,1),(D+9,1),(g+788+delta,1)):
            for b,w in protected:check(paths.origin.separated(a,z,b,w),'id6 count and ID slots exclude live task/source fields')
        check(F+21==g+513+delta,'id6 F21 source geometry')
        check(g+800+delta+48==g+848+delta,'id6 first parent fill ends before fresh count byte')
        check(g+856+delta+48<=D,'id6 resource tail fill excludes count slots')
        r=windows['resources'];p=windows['initializer']
        check([x['target'] for x in r['calls']+r['tail_exits']]==['0x20000040','0x2000039c','0x2000039c'],'id6 exact resource call targets')
        check([x['target'] for x in p['calls']]==[hex(callee),'0x2000039c','0x20000040','0x2000039c','0x20000040','0x2000039c',hex(0x4efd8+152*i),'0x20000040',hex(0x4efd8+152*i),'0x2000039c'],'id6 exact parent call inventory')
        rn={d['pc']:d for d in r['instructions']};pn={d['pc']:d for d in p['instructions']}
        re={int(k,16):[int(v,16) for v in vs] for k,vs in r['normal_return_CFG'].items()}
        zero_path=[int(v,16) for v in paths.chain(re,callee,{callee+36:callee+150})]
        check(zero_path[-1]==callee+158 and all(callee+o not in zero_path for o in (54,58,78,82,124,128)),'id6 zero path excludes allocator/fills')
        check([d['pc']-pc for d in p['instructions'] if d['op']=='store' and d['rs1']==2 and d['imm']==12]==[72],'id6 sole local saved input write')
        check(pn[pc+98]['rd']==10 and pn[pc+108]['rs2']==10,'id6 publish saved ID rather than callee result')
        check(-48+12==-36 and -48-16+12==-52,'id6 nested frames do not overlap saved ID slot')
        cfg=previous.fallback.DETAILS[i]
        _,_,_,defaults=previous.fallback.config_contract(data,cfg[2],cfg[5],cfg[9],cfg[10])
        check(cfg[5]==F and all(paths.origin.separated(x['destination_field'],x['bytes'],21,1) for x in defaults),'id6 config defaults do not overwrite field21')
        app=previous.source.app_contract(image[previous.source.APP_PC-0x8000:previous.source.APP_PC-0x8000+previous.source.APP_SIZE])
        an={d['pc']:d for d in app['instructions']}
        init.g(an,0x19a66,'id6 APP packed source literal',op='addi',rd=15,rs1=15,imm=-449)
        init.g(an,0x19a70,'id6 APP packed source store',op='store',rs1=2,rs2=15,imm=36,width=2)
        check(0x1000-449==0x0e3f and 36-16+1==21 and ((0x0e3f>>8)&255)==14,'id6 default source high byte14')
        profiles.append({'label':pr['label'],'bodies':windows,
            'inherited_entry':pr['cut_before_first_outer_initializer'],'prior_task_count':7,
            'prefix_fixed_writes':[{'address':hex(a),'bytes':z,'value':v} for a,z,v in prefix],
            'frames_relative_initializer_entry_SP':{'initializer_SP':-48,'saved_ID6':-36,'initializer_RA':-4,'nested_resources_SP':-64,'nested_RA':-52,'nested_S0':-56,'nested_S1':-60},
            'resource_source':{'address':hex(F+21),'config_field':21,'D':hex(D),'low2_byte':hex(D+9),'count_byte':hex(D+8),'formula':'q=(fresh_byte&3)+(fresh_byte>>2)','q_range':[0,66]},
            'zero_resource_case':{'additional_premise':'fresh F+21=0; valid nonalias frames and required live state/code/access retained','path':[hex(v) for v in zero_path],
                'returns_to':hex(pc+98),'saved_ID_reload':hex(pc+98),'ID_byte_publish':{'pc':hex(pc+108),'address':hex(g+788+delta),'value':6},
                'next_cut_before_fill':{'pc':hex(pc+126),'target':'0x2000039c','A0':hex(g+800+delta),'A1':0,'A2':48},'fill_excludes_next_fresh_count':hex(g+848+delta)},
            'nonzero_resource_case':{'cut_before_allocator':{'pc':hex(callee+58),'target':'0x20000040','A0':'60*q','A1':'0x9001'},'request_bytes_range':[60,3960],
                'no_local_allocator_null_guard':True,'pointer_store':hex(g+852+delta),'fill_length':'60*fresh(D+8), not necessarily entry q',
                'loop_bound':'fresh(D+8) reloaded after fill; signed comparison of 0..255; at most255 iterations if accesses/GPRs/data remain valid',
                'record_stride':60,'record_writes':[{'offset':2,'bytes':2,'value':65535},{'offset':4,'bytes':1,'value':0},{'offset':44,'bytes':4,'value':0}],
                'tail_fill':{'pc':hex(callee+128),'target':'0x2000039c','A0':hex(g+856+delta),'A1':0,'A2':48,'frame_released_before_tail':True},
                'premises':'allocator/fill must return and preserve required S/SP/RA frames and objects; valid nonalias payload extent, retained/refreshed count relationship and actual RAM code/provider remain unproved'},
            'APP_source_case':{'packed_halfword':'0x0e3f','source_halfword_field':20,'source_byte_field':21,'source_byte':14,'conditional_q':5,'conditional_request_bytes':300,
                'premises':'APP source literal/frame retained, successful matching64B copy and validation/defaults, no later writer changing fresh F+21; this is not a proved current setting'},
            'parent_remaining':{'fresh_count_byte':hex(g+848+delta),'fresh_tag_byte':hex(g+849+delta),'first_request':'16*fresh_count, tag4c04',
                'second_request':'16*((fresh(D+8)+fresh(2fa1/2ff1))&255), tag4c05','third_request':'(12*getter_reply)&65535, tag4c06; fill uses second fresh getter reply',
                'local_record_byte_loop_offsets':[272,364,366,368,372,374],'local_record_byte_offset':9,'local_record_stride':16,
                'tail_target':hex(0x4efe2+152*i),'tail_A0_pointer':hex(0x4d916+152*i),'parent_ordinary_RET':False,'later_outer_IDs_fixed':False},
            'actual_installed_binding_proved':False,'task_metadata_preserved_across_all_calls_proved':False})
    return {'schema':'TSL9-outer-ID6-initializer-static-v1','profile':parent['profile'],'APP_sha256':sha256(image).hexdigest(),
        'profiles':profiles,'byte_domain':values,
        'scope':'two candidates each full386B/123i initializer plus full160B/55i first callee; all356 instructions operand-guarded; no new C reconstruction bytes',
        'boundary':'zero fresh config byte closes nested ordinaryRET and ID6 publication to next fill request; nonzero byte stops at first allocator. Remaining calls/tails/loops have exact static operands and CFG, not unconditional successful execution',
        'remaining':['allocator/fill actual RAM binding, payload and metadata preservation','parent getter/setter tail and later outer initializers','fresh config and count writers, actual callback binding and object lifetimes'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    mutations=0
    for i,data in enumerate(carriers):
        for k,part in enumerate(PARTS):
            pc=STARTS[i][k];raw=init.binding.take(data,pc,SIZES[k])
            for p,d in decode(raw,pc).items():
                off=p-pc;z=d['size'];buf=bytearray(raw)
                buf[off:off+z]=(int.from_bytes(buf[off:off+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
                try:body(buf,part,i)
                except RuntimeError as e:check(str(e).startswith('id6 '+part+' operand '),'id6 specified mutation guard '+str(e))
                else:raise RuntimeError('id6 mutation escaped')
                mutations+=1
    check(mutations==356,'id6 mutation census');domains()
    print('PASS:356 operand mutations rejected; all256 config bytes, q0..66, zero iff byte0, request60..3960; local byte-loop domain0..255')


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
    else:check(OUT.read_bytes()==output,'id6 exact ledger replay')
    print('PASS:full two-profile initializer/resource CFG; ID6 frame/publication and conditional zero/nonzero cuts; APP field21 source; exact ledger')
    print('PASS:NO target execution/emulation; actual provider/payload preservation/parent completion UNPROVED')


if __name__=='__main__':main()
