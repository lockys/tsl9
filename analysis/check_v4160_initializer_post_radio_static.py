"""Initializer after conditional radio return: clear/copy and next call cut.

Only original operands/CFG, known provider contracts and byte intervals.
No target execution/emulation, RAM/MMIO or fill/copy register machine.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_nonmagic_service_static as previous
import check_v4160_role_initializer_fields_static as fields
import check_v4160_first_role_gate_static as gate
import check_v4160_config_buffer_source_static as source
import check_v4160_app_nv_callbacks_static as copy

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
paths=previous.paths
OUT=Path(__file__).with_name('v4160-initializer-post-radio-static.json')
ROLES=('fill_wrapper','clear','tail_wrapper','next_prefix')
SIZES=(20,18,20,50)
COUNTS=(6,5,5,17)
DETAILS=(
 ((0x57ac4,0x63704,0x5e758,0x53868),0,0x1ffa9000,-1844,-1366,0x43e8e,
 ('5863dc2aedfc65d2ed4bc63a6e8d36608b0b1c84e2069051f0acb757d5f1f6d9',
  '89e31520941443ae83f15676892ee625646ee5dcafe0e5c999518ac229e1f025',
  'ebd90f8f2adb2d66a67da7757bb1b721ab12291aeb47455499ed0ea94d53ff7a',
  '40ebb51cb88f38219574f11ab40a16e26de066c1d9cd957f0858ce19c206a73d')),
 ((0x57c04,0x637ee,0x5e842,0x53916),80,0x1ffa8000,1932,-1540,0x43f1a,
 ('0a15463a3c6c85f57d3a96c3e67698fbbff16071e2e1f7978657bace0c457fd9',
  '670e4e766171dc1443d3f9f506cf4c5b53ef9ea9598daea51cc070ebc3319acf',
  'cd66358c88ddac92ddc1970ca216f6d77b2443fd80525d6602f1802116701f5b',
  '56cad53f8bdfc14ae8c5b293410d28e6fda504f1a760a678953b8c3224be5c20')))


def specs(role,index):
    addresses,delta,upper,flow,clow,next_call,_=DETAILS[index];pc=addresses[ROLES.index(role)];s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def lui(o,r,v):e(o,'lui',rd=r,imm=v)
    def addi(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    def store(o,r,b,v,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    if role=='fill_wrapper':
        lui(0,10,0x20003000);li(4,12,28);li(6,11,0);addi(8,10,10,1108+delta)
        e(12,'auipc',rd=6,imm=upper);e(16,'jalr',rd=0,rs1=6,imm=flow)
    elif role in ('clear','tail_wrapper'):
        lui(0,15,0x20003000);addi(4,15,15,952+delta)
        if role=='clear':store(8,0,15,196);store(12,0,15,192,1);e(16,'jr',rs1=1)
        else:store(8,0,15,200,1);store(12,0,15,204);e(16,'jal',rd=0,target=addresses[3])
    else:
        lui(0,11,0x20003000);lui(4,10,0x20003000);addi(8,2,2,-32);li(10,12,6)
        addi(12,11,11,516+delta);addi(16,10,10,1184+delta)
        for o,r,v in ((20,1,28),(22,8,24),(24,9,20),(26,18,16),(30,19,12)):store(o,r,2,v)
        lui(28,9,0x4000);e(32,'auipc',rd=1,imm=0x1ffad000);e(36,'jalr',rd=1,rs1=1,imm=clow)
        addi(40,11,9,-1);li(44,10,0);e(46,'jal',rd=1,target=next_call)
    return pc,s


def body(raw,role,index):
    pc,s=specs(role,index);n=decode(raw,pc);j=ROLES.index(role)
    check(set(n)==set(s),'post initializer '+role+' boundaries')
    for p,f in s.items():init.g(n,p,'post initializer '+role+' operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[j],COUNTS[j],DETAILS[index][-1][j]),'post initializer '+role+' identity')
    e={};cuts=[];calls=[]
    for p,d in n.items():
        if d['op']=='jr':check(d['rs1']==1,'post initializer ordinary RET');q=[]
        elif d['op']=='jalr' and d['rd']==0:
            au=n[p-4];q=[(au['pc']+au['imm']+d['imm'])&0xfffffffe]
        elif d['op']=='jal' and d['rd']==0:q=[d['target']]
        else:q=[p+d['size']]
        for v in q:
            if v not in n:cuts.append([hex(p),hex(v)])
        e[p]=q
        if d['op'] in ('jal','jalr') and d['rd']==1:
            target=d.get('target')
            if target is None:target=(n[p-4]['pc']+n[p-4]['imm']+d['imm'])&0xfffffffe
            calls.append({'pc':hex(p),'target':hex(target),'link':hex(p+d['size'])})
    expected={'fill_wrapper':0x2000039c,'tail_wrapper':DETAILS[index][0][3],'next_prefix':pc+50}
    check(cuts==([] if role=='clear' else [[hex(pc+SIZES[j]-4),hex(expected[role])]]),'post initializer exact external edge')
    defs=sorted({d['rd'] for d in n.values() if d.get('rd',0)})
    check(defs=={'fill_wrapper':[6,10,11,12],'clear':[15],'tail_wrapper':[15],'next_prefix':[1,2,9,10,11,12]}[role],'post initializer exact GPR definitions')
    if role=='next_prefix':check([c['target'] for c in calls]==['0x20000332',hex(DETAILS[index][5])],'post initializer prefix call targets')
    else:check(not calls,'post initializer no linked nested calls')
    return {'role':role,'start':hex(pc),'bytes':len(raw),'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),
        'normal_return_CFG':{hex(p):[hex(q) for q in qs] for p,qs in e.items()},'external_edges':cuts,'calls':calls,
        'encoded_GPR_definitions':defs,'complete_function_or_tail_body':role!='next_prefix'}


def APP_slot_templates(image):
    rows=[]
    for off in range(0,len(image)-3,2):
        w=int.from_bytes(image[off:off+4],'little');op=w&127;fun=w>>12&7;imm=w>>20;imm=imm-4096 if imm&2048 else imm
        if op==3 and fun==2 and imm==572 or op==0x13 and fun==0 and imm in (520,572):
            rows.append({'pc':hex(0x8000+off),'op':'LW' if op==3 else 'ADDI','rd':w>>7&31,'base_register':w>>15&31,'displacement':imm})
    return rows


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[]
    for i,(data,pr,detail) in enumerate(zip(carriers,parent['profiles'],DETAILS)):
        addresses,delta,*_=detail;d=gate.DETAILS[i];B=0x20003000+d['base'];F=0x20003000+d['ctx']+80;ctx=0x20003000+d['ctx'];ip=d['initialize']
        bodies={r:body(init.binding.take(data,p,z),r,i) for r,p,z in zip(ROLES,addresses,SIZES)}
        caller=fields.body(init.binding.take(data,ip,426),'initializer',i)
        cn={r['pc']:r for r in caller['instructions']}
        check(fields.DETAILS[i][3][1:]==addresses[:2] and fields.DETAILS[i][4]==addresses[2],'post initializer complete caller/callee join')
        check(caller['calls'][4]['target']==('0x64298','0x64382')[i] and caller['calls'][4]['link']==hex(ip+392),'post initializer conditional radio-return link')
        check([cn[ip+o]['target'] for o in (392,396,410)]==list(addresses[:3]),'post initializer exact suffix targets')
        suffix={p:qs for p,qs in previous.previous.previous.edge_map(caller).items()};suffix[addresses[2]]=[]
        suffix_path=paths.chain(suffix,ip+392,{})
        check(suffix_path==[hex(ip+x) for x in (392,396,400,402,404,406,408,410)]+[hex(addresses[2])],'post initializer straight suffix and frame release')
        mapping=init.binding.profile(data,pr['label']);slots={r['slot']:r for r in mapping['slots']}
        check(slots['0x40048']['target']=='0x2000039c' and slots['0x4004c']['target']=='0x20000332','post initializer candidate provider identities')
        fill=source.fill_contract(init.binding.take(data,int(slots['0x40048']['source'],16),46))
        copier=copy.body(init.binding.take(data,int(slots['0x4004c']['source'],16),58),'copy',0x20000332,18,init.binding.COPY_HASH)
        check(fill['encoded_GPR_writes']==[10,14,15] and copier['encoded_GPR_writes']==[13,14,15,16],'post initializer provider preserves S/frame and copy A0/A1/A2')
        clear_extents=[(B+156,28),(B+196,4),(B+192,1),(B+200,1),(B+204,4)]
        destinations=clear_extents+[(B+232,6)]
        protected=[(ctx+1,1),(ctx+2,1),(ctx+3,1),(ctx+40,4),(paths.layout.T,4*212),(paths.layout.A+8,16),(0x200040a6,1),(0x20004184,1),(F,96)]
        for p,w in destinations:
            check(B<=p<p+w<=B+296,'post initializer all destination extents inside B296')
            for q,z in protected+[(B+193,1),(B+201,1)]:check(paths.origin.separated(p,w,q,z),'post initializer intended object writes preserve source/metadata/sampled bytes')
        check(B+156+28==B+184 and (B+156)!=0 and (B+232)!=0 and F+24!=0,'post initializer bounded provider positive requests')
        check(paths.origin.separated(B+232,6,F+24,6),'post initializer six-byte copy nonoverlap')
        prefix=bodies['next_prefix'];prefix_pc=addresses[3]
        check(prefix['calls'][0]=={'pc':hex(prefix_pc+36),'target':'0x20000332','link':hex(prefix_pc+40)},'post initializer copy return link')
        profiles.append({'label':pr['label'],'bodies':bodies,'initializer_source':{'start':hex(ip),'bytes':426,'sha256':caller['sha256']},
            'conditional_radio_return_link':hex(ip+392),'initializer_suffix_path':suffix_path,
            'B':hex(B),'F':hex(F),'fill_request':{'A0':hex(B+156),'A1':0,'A2':28},'conditional_fill_A0_return':hex(B+184),
            'fill_provider':fill,'copy_provider':copier,
            'new_object_destination_extents':[{'address':hex(p),'bytes':w} for p,w in destinations],
            'preserved_sampled_bytes':[hex(B+193),hex(B+201)],'copy_request':{'A0':hex(B+232),'A1':hex(F+24),'A2':6},
            'copy_A0_preserved':True,'copy_ordered_byte_pairs':[[hex(F+24+j),hex(B+232+j)] for j in range(6)],
            'initializer_16byte_frame_released_before_tail':True,'next_prefix_active_frame_bytes':32,
            'cut_before_next_call':{'pc':hex(prefix_pc+46),'target':hex(detail[5]),'A0':0,'A1':16383},
            'conditional_context_gate':5,'conditional_count':6,'actual_installed_binding_proved':False})
    templates=APP_slot_templates(image);check(not templates,'post initializer bounded APP setter-slot templates empty')
    return {'schema':'TSL9-initializer-post-radio-static-v1','profile':parent['profile'],'APP_sha256':sha256(image).hexdigest(),'profiles':profiles,
        'scope':'per candidate three complete58B/16instruction wrappers/leaves and bounded50B/17instruction next prefix; old426B caller and mappedfill46B/copy58B contracts reused; no new C bytes',
        'conditional_order':'after previous conditional radio normal return at initializer+392: tailfill28 -> clearword196/byte192 -> restore S0/RA/S1/S2 and SP16 -> tailstub byte200/word204 -> nextfunction frame32/copy6 -> cut before range helper(A0=0,A1=16383)',
        'provider_boundary':'fill28 and copy6 rely on actual matching RAM provider bytes, valid nonalias data/frame and no adverse MMIO/FENCE.I/IRQ/DMA/reentry/external writes. Their CPU snapshot store-source restores do not prove hardware restoration. Copy preserves A0; fill advances A0 by28',
        'preservation':'all new data stores intentionally inside B296; intervals exclude F96/context metadata/table/task/node and B193/B201. Copy is six ordered fresh byte loads/stores, not an atomic source snapshot. Entry/new frames and caller saved words need remain valid',
        'APP_setter_slot_template_scan':{'templates':['standard LW immediate572','standard ADDI immediate572 or520'],'step_bytes':2,'input_bytes':len(image),'matches':templates,
            'scope':'raw four-byte encoding candidates only, may include data/overlapping decode; no proof of base value or actual caller. Does not cover rebased/GP/inherited/indexed/nonadjacent or memory-derived addresses'},
        'return_boundary':'last wrapper tails into53868/53916. Stop before43e8e/43f1a with active32B frame; target/later generation/retry body unclosed; no initializer/primary/gate publication or complete return claim',
        'remaining':['43e8e/43f1a and subsequent helper/retry body','actual setter caller and invocation ordering','actual provider retention, hardware completion and object lifetimes'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    mutations=0
    for i,(data,detail) in enumerate(zip(carriers,DETAILS)):
        for role,pc,z in zip(ROLES,detail[0],SIZES):
            raw=init.binding.take(data,pc,z)
            for p,d in decode(raw,pc).items():
                at=p-pc;w=d['size'];buf=bytearray(raw);buf[at:at+w]=(int.from_bytes(buf[at:at+w],'little')^(4 if w==2 else 1<<20)).to_bytes(w,'little')
                try:body(buf,role,i)
                except RuntimeError as e:check(str(e).startswith('post initializer '+role+' operand '),'post initializer specified mutation guard '+str(e))
                else:raise RuntimeError('post initializer mutation escaped')
                mutations+=1
    check(mutations==66,'post initializer mutation census')
    for op,fun,imm in ((3,2,572),(0x13,0,572),(0x13,0,520)):
        raw=((imm<<20)|(10<<15)|(fun<<12)|(15<<7)|op).to_bytes(4,'little')
        check(len(APP_slot_templates(raw))==1,'post initializer APP template positive fixture')
    for B,F in ((0x200033b8,0x200031ec),(0x20003408,0x2000323c)):
        check(len(range(B+156,B+184))==28 and len(range(B+232,B+238))==6,'post initializer positive request extents')
        check(B+193 not in range(B+192,B+193) and B+201 not in range(B+200,B+201),'post initializer adjacent byte preservation')
    print('PASS:66 operand mutations rejected; APP template positive fixtures and28/6-byte extent identities')


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
    else:check(OUT.read_bytes()==output,'post initializer exact ledger replay')
    print('PASS:conditional initializer suffix/fill28/clear/tail/copy6 and frame handoff to next call cut; exact ledger')
    print('PASS:NO target execution; next helper/actual setter caller/provider retention/initializer return UNPROVED')


if __name__=='__main__':main()
