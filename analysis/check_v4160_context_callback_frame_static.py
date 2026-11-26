"""Separate APP context entries and candidate JT2 callback frame-word source.

Complete original operands/CFGs plus bounded publication prefixes, mappings
and host field algebra only. No target ISA/CSR/MRET/ECALL, RAM/frame/copy,
callback, resident or hardware execution/emulation.
"""
import argparse
import json
import re
from hashlib import sha256
from pathlib import Path
import check_v4160_irq_setup_stack_sources_static as previous
import check_v4160_dispatch_origin_mask_static as origin

init,sparse,check,take=previous.init,previous.sparse,previous.check,previous.take
OUT=Path(__file__).with_name('v4160-context-callback-frame-static.json')
REGS=[1]+list(range(4,32))
APP_DETAILS=(('restore',0x8448,78,35,0,'73aa41f786d162c82daf96fd6db44a01d962d253f50b842aef2b49e5fef290b9'),
 ('save',0x8498,134,64,29,'d4cd66dcce6f24ad8ca4dc75e882cb851321268c465e2b644de42e3cd95f7f2a'),
 ('publish',0x199e2,14,5,2,'7615b34b38a4b7f28af86dfcdaba7de8477c700565ab43e31e19a61a0af0cbb2'),
 ('setup_prefix',0x8e88,36,13,3,'f081eac86e7fda5fdb2bd2757c70931c57b82ed587759f76e78c323674b2304e'))
REF_DETAILS=((0x430a4,0x20002e34,200,0x20002b4c,0x2000298e,
 '02cb85da2c289eeb380c25ecf2af13f574b57dc0ae6b3b4d3ecdb2c9fea5a5ab','790f92f9fd6bf01f58c1dcb38ea11e287cc3887a476e51ac30be5a0080ab5773'),
 (0x43130,0x20002e80,204,0x20002b98,0x200029da,
 '5d8c97f83dbf92ed50694aaf66bdecb9a2d56840a81208c580051254cd103c42','885483f98c36f544a5b6921fd6683c454b030cc5385e3617ec5b739eea850132'))


def decode(raw,pc):
    n={};off=0
    while off<len(raw):
        h=int.from_bytes(raw[off:off+2],'little');size=2 if h&3!=3 else 4
        check(off+size<=len(raw),'context whole instruction');chunk=raw[off:off+size];w=int.from_bytes(chunk,'little');p=pc+off
        if size==4 and w==0x00000073:d=dict(pc=p,size=4,bytes=chunk.hex(),op='ecall')
        elif size==4 and w&0x707f==3:
            d=dict(pc=p,size=4,bytes=chunk.hex(),op='load',rd=w>>7&31,rs1=w>>15&31,
                   imm=((w>>20)^2048)-2048,width=1,signed=True)
        else:d=previous.decode(chunk,p)[p]
        n[p]=d;off+=size
    return n


def specs(role,pc,params=None):
    s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def load(o,r,b,v=0,w=4):e(o,'load',rd=r,rs1=b,imm=v,width=w)
    def store(o,r,b,v=0,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    def addi(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    if role=='restore':
        addi(0,11,0,32);e(4,'csr',rd=0,rs1=11,funct3=2,csr=0x804);load(8,11,2)
        e(10,'csr',rd=0,rs1=11,funct3=1,csr=0x341)
        for i,r in enumerate(REGS):load(14+2*i,r,2,4+4*i)
        addi(72,2,2,128);e(74,'mret')
    elif role=='save':
        addi(0,2,2,-128)
        for i,r in enumerate(REGS):store(2+2*i,r,2,4+4*i)
        addi(60,11,3,384);load(64,10,11);e(66,'jalr',rd=1,rs1=10,imm=0)
        for i,r in enumerate(REGS):load(70+2*i,r,2,4+4*i)
        addi(128,2,2,128);e(130,'mret')
    elif role=='publish':
        e(0,'lui',rd=15,imm=0x20000000);load(4,15,15,8);addi(6,2,2,-96);store(8,8,2,88);store(10,15,3,384)
    elif role=='setup_prefix':
        addi(0,2,2,-32);store(2,8,2,24);e(4,'lui',rd=8,imm=0x40000);load(8,15,8,72)
        e(10,'lui',rd=12,imm=0x1000);store(12,1,2,28);addi(14,12,12,-1972);e(18,'li',rd=11,imm=0)
        e(20,'auipc',rd=10,imm=0x20002000);addi(24,10,10,752);store(28,9,2,20)
        e(30,'call_indirect',rd=1,rs1=15);e(32,'jal',rd=1,target=0x199e2)
    elif role=='callback':
        flag,nonzero_target,zero_target=params
        e(0,'auipc',rd=5,imm=0);addi(4,5,5,flag);e(8,'load',rd=6,rs1=5,imm=0,width=1,signed=True)
        store(12,0,5,0,1);e(16,'beq',rs1=6,rs2=0,target=pc+46)
        e(20,'csr',rd=11,rs1=0,funct3=2,csr=0x341);store(24,11,2)
        e(26,'auipc',rd=11,imm=0);addi(30,11,11,-38);e(34,'csr',rd=0,rs1=11,funct3=1,csr=0x341)
        e(38,'jal',rd=1,target=nonzero_target);e(42,'mret');store(46,1,2,120)
        e(48,'jal',rd=1,target=zero_target);load(52,1,2,120);e(54,'jr',rs1=1)
    elif role=='gateway':e(0,'jal',rd=1,target=params);e(4,'ecall')
    else:raise RuntimeError('unknown context role')
    return s


def body(raw,role,pc,size,count,store_count,digest,params=None):
    n=decode(raw,pc);expected=specs(role,pc,params);check(set(n)==set(expected),'context complete boundaries '+role)
    for p,f in expected.items():init.g(n,p,'context '+role+' instruction '+hex(p-pc),**f)
    edges={};calls=[];terminals=[];cuts=[]
    for p,d in n.items():
        if d['op'] in ('mret','ecall','jr'):
            if d['op']=='jr':check(d['rs1']==1,'context ordinary RET register')
            qs=[];terminals.append({'pc':hex(p),'kind':d['op']})
        elif d['op']=='beq':qs=[p+d['size'],d['target']]
        else:qs=[p+d['size']]
        for q in qs:
            if q not in n:check(role in ('publish','setup_prefix') and q==pc+size,'context explicit bounded prefix end');cuts.append(hex(q))
        edges[p]=qs
        if d['op'] in ('jal','jalr','call_indirect'):
            check(d['rd']==1,'context linked call');calls.append({'pc':hex(p),'link':hex(p+d['size']),
                'target':hex(d['target']) if 'target' in d else 'fresh A0 & ~1' if role=='save' else 'fresh A5 & ~1',
                'normal_return_proved':False})
    seen=set()
    def visit(p):
        if p not in n or p in seen:return
        seen.add(p)
        for q in edges[p]:visit(q)
    visit(pc);check(seen==set(n),'context complete local reachability '+role)
    stores=[d for d in n.values() if d['op']=='store']
    check((len(raw),len(n),len(stores),sha256(raw).hexdigest())==(size,count,store_count,digest),'context full identity '+role)
    return {'start':hex(pc),'end_exclusive':hex(pc+size),'bytes':size,'sha256':digest,'bounded_prefix':role in ('publish','setup_prefix'),
        'instructions':list(n.values()),'stores':stores,'calls':calls,'terminal_edges':terminals,'prefix_cuts':cuts,
        'conditional_normal_return_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()}}


def raw_edges(app,target):
    hits=[]
    for off in range(0,len(app)-1,2):
        p=0x8000+off;h=int.from_bytes(app[off:off+2],'little');w=int.from_bytes(app[off:off+4],'little')
        if off+4<=len(app) and w&127==111:
            d=(w>>31<<20)|((w>>12&255)<<12)|((w>>20&1)<<11)|((w>>21&1023)<<1);d=(d^0x100000)-0x100000
            if p+d==target:hits.append(hex(p))
        if h&0xe003 in (0x2001,0xa001):
            d=((h>>12&1)<<11)|((h>>11&1)<<4)|((h>>9&3)<<8)|((h>>8&1)<<10)|((h>>7&1)<<6)|((h>>6&1)<<7)|((h>>3&7)<<1)|((h>>2&1)<<5)
            if p+(d^2048)-2048==target:hits.append(hex(p))
    return hits


def derive(app,carriers,header,coverage):
    parent=previous.derive(app,carriers,header,coverage)
    bodies={r:body(take(app,p,size),r,p,size,n,stores,h) for r,p,size,n,stores,h in APP_DETAILS}
    check(sum(b['bytes'] for b in bodies.values())==262 and sum(len(b['instructions']) for b in bodies.values())==117
          and sum(len(b['stores']) for b in bodies.values())==34,'context APP body/prefix census')
    check(re.search(rb'^\s*#define\s+LLE_IRQLibHandler\s+[^\r\n]*BLE_LIB_RAM_JT\(2\)',header,re.M) is not None,'SDK RAMJT2 alias')
    # Match each saved register to both distinct restore sequences; never pair exits automatically.
    ns={r:{d['pc']:d for d in b['instructions']} for r,b in bodies.items()}
    for i,r in enumerate(REGS):
        a=ns['save'][0x8498+2+2*i];b=ns['save'][0x8498+70+2*i];c=ns['restore'][0x8448+14+2*i]
        check(a['rs2']==b['rd']==c['rd']==r and a['imm']==b['imm']==c['imm']==4+4*i,'29 exact register-field matches')
    check(not any(d['rs1']==2 and d['imm']==0 for d in bodies['save']['stores']),'APP save does not fill MEPC slot0')
    pub=ns['publish'];check(pub[0x199e6]['rs1']==15 and pub[0x199e6]['imm']==8 and pub[0x199ec]['imm']==384,'RAMJT2 to GP384 publication')
    check(bodies['setup_prefix']['calls'][-1]['target']=='0x199e2' and (24,0x8e88) in previous.boot.INIT_CALLS,'init sequence selected setup join')
    refs={hex(t):[hex(0x8000+i) for i in range(len(app)-3) if app[i:i+4]==t.to_bytes(4,'little')] for t in (0x8448,0x8498,0x12c24)}
    check(refs=={'0x8448':['0x804c','0x8058'],'0x8498':['0x8138'],'0x12c24':['0x80c8']},'distinct raw vector words')
    candidates={hex(t):raw_edges(app,t) for t in (0x8448,0x8498,0x12c24)};check(not any(candidates.values()),'raw direct edge candidate census')
    profiles=[]
    for i,(data,detail) in enumerate(zip(carriers,REF_DETAILS)):
        source,runtime,flag,nz,z,digest,gh=detail;mapping=init.binding.profile(data,init.binding.PROFILES[i][0])
        first=mapping['first_copy'];src=int(first['source'],16);dest=int(first['destination'],16);end=int(mapping['first_copy_end_exclusive'],16)
        check(source-src+dest==runtime and dest<=runtime-12 and runtime+56<=end,'complete callback/gateway first-copy mapping')
        cbraw=init.binding.take(data,source,56);graw=init.binding.take(data,source-12,8)
        cb=body(cbraw,'callback',runtime,56,16,3,digest,(flag,nz,z));gateway=body(graw,'gateway',runtime-12,8,2,0,gh,0x200007a0)
        # Decode same source at FLASH coordinates, independently pin relocated relative targets.
        delta=runtime-source;flash=body(cbraw,'callback',source,56,16,3,digest,(flag,nz-delta,z-delta))
        fg=body(graw,'gateway',source-12,8,2,0,gh,0x200007a0-delta)
        jt1,jt2,_=origin.DETAILS[i];initdetail=origin.init.DETAILS[i];ip=initdetail[0]
        initializer=origin.initializer_body(init.binding.take(data,ip,114),ip,initdetail,jt1,jt2)
        word=initializer['JT_words'][2];check(int(word['address'],16)==0x20000008 and int(word['value'],16)==runtime,'candidate published JT2 equals callback entry')
        check(initdetail[3]<=runtime+flag<initdetail[4]+4,'candidate callback flag inside startup zero request')
        cn={d['pc']:d for d in cb['instructions']};formed=(runtime+26+cn[runtime+26]['imm']+cn[runtime+30]['imm'])&0xffffffff
        check(formed==runtime-12,'candidate MEPC source is gateway entry')
        profiles.append({'label':mapping['label'] if 'label' in mapping else init.binding.PROFILES[i][0],
            'initializer_JT2_word':word,'initializer_body_sha256':initializer['sha256'],
            'flash_source':hex(source),'first_copy_source':hex(src),'first_copy_destination':hex(dest),'first_copy_end':hex(end),
            'callback':cb,'gateway':gateway,'flash_call_targets':[c['target'] for c in flash['calls']+fg['calls']],
            'flag_address':hex(runtime+flag),'startup_zero_request':[hex(initdetail[3]),hex(initdetail[4]+4)],
            'initial_flag_zero_only_if_completed_and_preserved':True,'gateway_MEPC_operand':hex(formed),
            'installed_binding_or_copy_completion_proved':False,'full_boot_proved':False})
    return {'schema':'TSL9-context-callback-frame-static-v1','profile':init.timer.PROFILE,
        'scope':'2 complete APP bodies212B/99instructions +2 bounded APP prefixes50B/18instructions +4 reference bodies128B/36instructions',
        'APP':bodies,'profiles':profiles,'register_fields':[{'register':r,'frame_offset':4+4*i} for i,r in enumerate(REGS)],
        'frame_contract':{'restore8448':'set CSR804 mask20hex; LW F0->CSRW341;29 wordloads F4..116; SP+=128; MRET',
            'save8498':'SP-=128;29 storesF4..116; freshU32[GP+384] ->JALR A0 link84de; conditional29reloads/SP+=128/MRET',
            'not_stored_by_APP_save':[0,1,2,3,120,121,122,123,124,125,126,127],
            'GP_not_saved_or_restored':True,'callback_reply_overwritten_by_saved_A0':True,
            '8448_and8498_are_independent_entries':True,'8498_alone_is8448_frame_producer':False},
        'publication':'8e88 boundedprefix requestsfill(2000b18c,0,2124), thenCALL199e2; first14B readU32[20000008] thenSW same pointer toGP+384 without intermediateA5 definition/call',
        'candidate_callback_contract':{'flag':'signed freshLB flag, thenSB0 before branch; rawzero ->ordinary RET path, nonzero ->MRET path',
            'zero':'SWcallerRA F+120; direct callee; LWRA F+120;RET, conditional to8498 inline reloads',
            'nonzero':'CSR read341->A1; SWA1 F+0; form gateway pointer->CSRW341; direct callee; MRET; no ordinary return edge',
            'gateway':'direct200007a0 call thenECALL, no proved trap route to8448',
            'direct_callee_effects_and_MEPC_SP_frame_preservation':False},
        'conditional_frame0_origin':'if actual binding equals candidate, initialization/mapping/pointer retention/context/access hold,8498 callback can write current CSR341 to its reservedF0 before nonlocalMRET; value/target retention across downstream callee unproved',
        'vector_evidence':{'raw_words':refs,'nominal_indices':{'8448':[5,8],'8498':[64],'12c24':[36]},
            'raw_halfword_JAL_CJ_CJAL_candidates':candidates,'not_an_all_indirect_edge_or_runtime_delivery_proof':True},
        'separation':'no proved forwarding of12c24 through8448/8498; independent numeric vector entries do not establish shared hardware frame or ordinary ABI',
        'premises':['matching bytes/conditional ISA; valid frame/code/CSR/slot accesses and no adverse aliases/interrupt/writer/reentry',
            'actual resident binding and completed first-copy mapping, required GP/SP/frame and saved-word preservation',
            'all direct resident callees remain unknown normal-return/context boundaries; MRET/ECALL effects not executed or inferred from candidate word alone',
            'prefixes do not prove full setup completion; source alias names do not establish actual vendor runtime identity'],
        'remaining_boundaries':['gateway200007a0 and ECALL/8448 actual trap linkage','resident callback direct callees and flag writers',
            'actual JT2/GP384 binding/preservation','drivers18f88/18ab0 and broader interrupt frame lifetime'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(app,carriers):
    check(len(REGS)==29 and len(set(REGS))==29 and set(REGS)==set(range(1,32))-{2,3},'frame excludes SP/GP only among nonzero GPRs')
    written={x for i in range(29) for x in range(4+4*i,8+4*i)}
    check(written==set(range(4,120)) and not written&set(range(4)),'frame0 is absent from APP saves')
    check(written|set(range(4))==set(range(120)),'candidate savedMEPC plus29fields covers restore reads')
    for byte in range(256):check(((byte^128)-128!=0)==(byte!=0),'signed LB zero/nonzero partition')
    roles={r:(p,size,count,stores,h) for r,p,size,count,stores,h in APP_DETAILS}
    cases=(('restore',0,1<<20),('restore',8,0x80),('restore',10,1<<20),('restore',74,1<<20),
        ('save',2,4),('save',60,1<<20),('save',66,1<<15),('publish',4,4),('publish',10,1<<20),('setup_prefix',30,0x80))
    def reject(raw,role,pc,size,count,stores,digest,off,flip,params=None):
        raw=bytearray(raw);w=decode(raw,pc)[pc+off]['size'];raw[off:off+w]=(int.from_bytes(raw[off:off+w],'little')^flip).to_bytes(w,'little')
        try:body(raw,role,pc,size,count,stores,digest,params)
        except RuntimeError as e:check(str(e)=='context '+role+' instruction '+hex(off),'unexpected context mutation guard '+str(e))
        else:raise RuntimeError('context mutation escaped')
    for role,off,flip in cases:
        pc,size,count,stores,digest=roles[role];reject(take(app,pc,size),role,pc,size,count,stores,digest,off,flip)
    for data,detail in zip(carriers,REF_DETAILS):
        source,runtime,flag,nz,z,digest,gh=detail
        for off,flip in ((8,1<<20),(24,4),(30,1<<20),(34,1<<20)):
            reject(init.binding.take(data,source,56),'callback',runtime,56,16,3,digest,off,flip,(flag,nz,z))
        reject(init.binding.take(data,source-12,8),'gateway',runtime-12,8,2,0,gh,4,1<<20,0x200007a0)
    print('PASS: 29 save/reload/register-field pairs; exact frame0/tail holes; 256 signed-byte cases; 20 specified raw mutations')


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true',help='Create ledger exclusively');o=p.parse_args()
    app=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(app)==76800 and sha256(app).hexdigest()==init.binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK header identity')
    carriers=[]
    for label,folder,tail,size,digest in init.binding.PROFILES:
        raw=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(raw)==size and sha256(raw).hexdigest()==digest,'candidate identity '+label);carriers.append(raw)
    raw_hex=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
    coverage=sparse.derive(app,carriers,header,raw_hex,sparse.parser())
    sources,vectors=init.timer.source_contract();ledger=derive(app,carriers,header,coverage)
    ledger['sources'],ledger['official_Xwchc_vectors']=sources,vectors
    tests(app,carriers);output=(json.dumps(ledger,indent=1,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'context callback frame exact ledger replay')
    print('PASS: APP212B/99instructions +bounded50B/18instructions; reference128B/36instructions; JT2->GP384->callback frame0 writer joined')
    print('PASS: exact ledger bytes; NO target execution; installed binding/direct callee effects/ECALL routing/IRQ36 linkage UNPROVED')


if __name__=='__main__':main()
