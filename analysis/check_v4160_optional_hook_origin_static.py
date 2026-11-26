"""Conditional APP field48 -> resident hook -> mode3 frame join, static only.

Original bytes/operands plus integer field/frame projections. No target ISA,
copy, callback, RAM/frame, provider, MMIO or device execution/emulation.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_mode3_frame_static as previous
import check_v4160_config_buffer_source_static as source
import check_v4160_fallback_initialization_static as fallback
import check_v4160_post_config_static as post
import check_v4160_config_gates_static as gates

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-optional-hook-origin-static.json')
WINDOWS=(('setup',0x8e88,40,14,'5cb9c111f8882609ad53a1b67a0b42a60679bf74e99bf0efef7cfe25c47bd2b2'),
 ('source',0x19aa4,16,5,'0efd74834dd9b3216637be797ac67736e1a9129aa3944ad2d2dd10c565e82fc8'))


def specs(role,pc):
    s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def imm(o,op,r,b,v):e(o,op,rd=r,rs1=b,imm=v)
    def store(o,r,b,v,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    if role=='source':
        e(0,'auipc',rd=15,imm=0);imm(4,'addi',15,15,-748);imm(8,'addi',10,2,8)
        store(10,14,2,48,2);store(14,15,2,64)
    elif role=='setup':
        imm(0,'addi',2,2,-32);store(2,8,2,24);e(4,'lui',rd=8,imm=0x40000)
        e(8,'load',rd=15,rs1=8,imm=72,width=4);e(10,'lui',rd=12,imm=4096);store(12,1,2,28)
        imm(14,'addi',12,12,-1972);e(18,'li',rd=11,imm=0);e(20,'auipc',rd=10,imm=0x20002000)
        imm(24,'addi',10,10,752);store(28,9,2,20);e(30,'call_indirect',rd=1,rs1=15)
        e(32,'jal',rd=1,target=0x199e2);e(36,'jal',rd=1,target=0x19b16)
    else:raise RuntimeError('unknown hook source window')
    return s


def window(raw,role):
    _,pc,size,count,digest=next(d for d in WINDOWS if d[0]==role)
    n=decode(raw,pc);s=specs(role,pc);check(set(n)==set(s),'hook origin complete window boundaries '+role)
    for p,f in s.items():init.g(n,p,'hook origin '+role+' operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(size,count,digest),'hook origin exact window identity '+role)
    check(not any(d['op'] in ('jr','jump','beq','bne','beqz','bnez','bge','blt') for d in n.values()),'hook origin bounded sequential window '+role)
    return {'start':hex(pc),'end_exclusive':hex(pc+size),'bytes':size,'sha256':digest,'instructions':list(n.values()),
        'normal_return_prefix_cut':hex(pc+size),'complete_function':False}


def separated(a,size,b,width):return a+size<=b or b+width<=a


def derive(app,carriers,header,coverage):
    parent=previous.derive(app,carriers,header,coverage)
    windows={r:window(app[p-0x8000:p-0x8000+size],r) for r,p,size,count,digest in WINDOWS}
    builder=source.app_contract(app[source.APP_PC-0x8000:source.APP_PC-0x8000+source.APP_SIZE])
    uid=source.uid_contract(app[source.UID_PC-0x8000:source.UID_PC-0x8000+source.UID_SIZE])
    bn={d['pc']:d for d in builder['instructions']}
    check((0x19aa4-748,64-16)==(0x197b8,48),'hook source pointer/field projection')
    direct=[p for p,r,o,w in source.DIRECT if not separated(o,w,64,4)]
    check(direct==[0x19ab2],'hook only local direct SP64 writer')
    suffix={p:d for p,d in bn.items() if 0x19ab2<=p<=0x19aec}
    check([p for p,d in suffix.items() if d['op']=='jal' or d['op']=='call_indirect']==[0x19ab4,0x19aec],'hook source only UID call before initialization')
    check([p for p,d in suffix.items() if d['op']=='store']==[0x19ab2,0x19aca],'hook source suffix store census')
    check(uid['encoded_GPR_writes']==[13,14,15] and uid['output_extent_bytes']==6 and
        builder['UID_loop_source_SP_offsets']==list(range(8,14)) and
        builder['UID_loop_destination_SP_offsets']==list(range(40,46)),'hook source UID disjoint extents')
    check(set(range(64,68)).isdisjoint(range(8,14)) and set(range(64,68)).isdisjoint(range(40,46)),'hook UID/source-loop do not overwrite source field')
    check(builder['config_call']=='0x19aec' and builder['config_slot']=='0x400a4','hook source initialization call')
    mode=parent['mode_callee'];check(mode['complete_function_bytes_CFG_and_memory_classification'] and
        mode['start']=='0x1929a' and len(mode['saved_fields'])==13,'hook reused mode3 closure')
    profiles=[];post_profiles=post.derive(app,carriers,header)['profiles']
    for i,(data,fd,gd,pp) in enumerate(zip(carriers,fallback.DETAILS,gates.DETAILS,post_profiles)):
        _,zsrc,cfg,zstart,zlast,dest,_,_,_,hoff,boff,_,_,digest=fd
        pc,size,_,copied,_,_,_,_,_,_=gd
        check(init.binding.word(data,0x400a4)==cfg and init.binding.word(data,0x40074)==pc,'hook candidate initialization/config slot identities')
        raw,n,edges,defaults=fallback.config_contract(data,cfg,dest,hoff,boff)
        check(len(raw)==228 and sha256(raw).hexdigest()==digest,'hook reused complete initializer body')
        hook=dest+48;state=dest
        zr,zn,ze,zc=fallback.zero_contract(data,zsrc,zstart,zlast)
        check(zstart<=hook and hook+4<=zlast+4 and (hook-zstart)//4+1==202,'hook startup zero word202')
        # Existing 64-byte copy arguments and local defaults are reused exactly.
        init.g(n,cfg+92,'hook 64byte count',op='addi',rd=12,rs1=0,imm=64)
        init.g(n,cfg+96,'hook 64byte source',op='mv',rd=11,rs2=9)
        init.g(n,cfg+98,'hook 64byte destination',op='addi',rd=10,rs1=8,imm=dest-0x20003000)
        check(all(separated(d['destination_field'],d['bytes'],48,4) for d in defaults),'hook initializer defaults exclude48..51')
        check(separated(0x20003000+hoff,2,hook,4) and separated(0x20003000+boff,1,hook,4),'hook later fixed initializer stores exclude slot')
        fixed=pp['fixed_stores_with_live_base_premise'];fills=pp['fixed_zero_fill_requests']
        check(all(separated(int(d['address'],16),d['bytes'],hook,4) for d in fixed+fills),'hook post-init fixed stores/fill requests exclude slot')
        consumer=gates.body(init.binding.take(data,pc,size),i);cn={d['pc']:d for d in consumer['instructions']};shift=8*i
        check(int(consumer['base'],16)==state and state+48==hook,'hook producer/consumer same word')
        init.g(cn,pc+12+shift,'hook fresh load field48',op='load',rd=15,rs1=15,imm=48,width=4)
        init.g(cn,pc+24+shift,'hook save input',op='store',rs1=2,rs2=10,imm=12,width=4)
        init.g(cn,pc+26+shift,'hook indirect call',op='call_indirect',rd=1,rs1=15)
        init.g(cn,pc+28+shift,'hook reload input',op='load',rd=11,rs1=2,imm=12,width=4)
        check(consumer['calls'][0]['link']==hex(pc+28+shift),'hook return link/reload join')
        profiles.append({'label':init.binding.PROFILES[i][0],
            'initialization_entry':hex(cfg),'initialization_body_sha256':digest,'64byte_destination':hex(dest),
            'hook_word':hex(hook),'startup_zero_one_based_word':202,
            'conditional_completed_copy_field48_value':'0x197b8','source_bytes_if_unmodified':'b8970100',
            'consumer_entry':hex(pc),'fresh_hook_load_PC':hex(pc+12+shift),
            'hook_call_PC':hex(pc+26+shift),'hook_link_reload_PC':hex(pc+28+shift),
            'reused_default_writes_disjoint':defaults,'post_init_fixed_ranges_disjoint':fixed+fills,
            'unexcluded_dynamic_post_init_writes':pp['dynamic_stores'],
            'unexcluded_post_copy_calls':[hex(cfg+186),hex(cfg+206),'wrapper fresh40080 call and other intervening writers'],
            'actual_installed_binding_or_hook_value_proved':False})
    return {'schema':'TSL9-optional-hook-origin-static-v1','profile':parent['profile'],'APP_sha256':sha256(app).hexdigest(),
        'scope':'conditional source/copy/hook/mode3 join;2 bounded windows56B/19instructions, all but4B setup continuation already covered; existing full bodies reused',
        'windows':windows,'profiles':profiles,
        'setup_order':'bounded8e88prefix: initialslotfill normalreturn ->8ea8 callsbuilder199e2 ->8eac callswrapper19b16; order conditional on preceding calls returning, not wholefunction/boot reachability',
        'source_contract':'APP19aa4 AUIPC/addi forms197b8; SW19ab2 atSP+64 projects toC+48 withC=SP+16; laterUIDleaf onlywritesSP+8..13 andlocal6byte-loop SP+40..45; no localoverlap ofsourceword before400a4call',
        'copy_contract':'matching400a4 candidate, passedvalidation, liveS1 source andcompleted nonaliasing64-byte fill/copy required; field48..51 transferred as4 ordered bytes, not atomicwordpublication',
        'writer_boundary':'startupzero canwrite0 tohookword202; completedfield48copy canwrite197b8; not an exhaustive writer/value census; initdefaults/fixedpostranges exclude slot butdynamicstores/callees/interveningwriters still needpreservation',
        'optional_hook_binding':'if fresh consumerword retains197b8, calltarget&~1 isAPP197b8; thatwrapper discards incomingA0 byforcing3, tailsverified1929a, returns throughoriginal hooklink ifnestedframe/reader/poll conditions hold',
        'frame_projection':'constructorSP=C; providerSP=H=C-32; savedconfigpointerH+12=C-20,providerS0=C-8,RA=C-4; hookmodechild stores C-100..C-97 andC-84..C-33, disjointproviderframe[C-32,C) andconstructorconfig[C,C+16)',
        'post_hook_contract':'under matchinghookcode, validnormalreturn/noalias/noexternalinterference,modecallee restoresSP/S/RA; GP unchanged locally; providerreload A1 fromH+12 recoversoriginalC, stateS0 andconstructorconfig preserved locally; hookA0replyignored',
        'conditional_gates':'ifconstructorcontext/16Bsourcefields remainmatching, nonzeroC andsavedpointerrecoverC: words191c6/ffffffff andhalfwords16000/1000 pass4gates; initialbyte12=0 bypassesstate+21gate; latercopy/arithmetic paths retaintheirpremises',
        'lifetime':'copiedhookvalue197b8 iscodepointer; source64Bbuilderframe canend withoutinvalidatingthatnumericcodepointer undercorrectcode/preservedcopy; doesnotproveglobalpointerretention orotherpayloadlifetimes',
        'remaining':['actualinstalled400a4/40074/40080 bindings, dynamicpost-init writes andslotwriters',
            'field44callback/post-init/taskregistration preservation ofhookword acrosssetup',
            'MMIO/poll progress, asynchronousaliases/writers andpayload/frame lifetime','GP+108 source andsignedarithmeticdomains'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(app,carriers):
    check((0x19aa4-748).to_bytes(4,'little')==bytes.fromhex('b8970100'),'hook source little-endian pointer oracle')
    # Coordinate projection, not simulated memory/calls.
    provider=set(range(-32,0));config=set(range(16));caller_ra=set(range(28,32))
    mode_writes=set(range(-100,-96))|set(range(-84,-32))
    check(len(mode_writes)==56 and not mode_writes&(provider|config|caller_ra),'hook nested-frame direct-store disjointness')
    check(-32+12==-20 and -32+24==-8 and -32+28==-4,'hook saved-input/S0/RA projection')
    count=0
    for role,pc,size,n,h in WINDOWS:
        raw=app[pc-0x8000:pc-0x8000+size]
        for p,d in decode(raw,pc).items():
            b=bytearray(raw);at=p-pc;w=d['size'];flip=1<<20 if w==4 else 4
            b[at:at+w]=(int.from_bytes(b[at:at+w],'little')^flip).to_bytes(w,'little')
            try:window(b,role)
            except RuntimeError as e:check(str(e).startswith('hook origin '+role+' operand '),'specific hook source mutation guard '+str(e))
            else:raise RuntimeError('hook source mutation escaped')
            count+=1
    for i,(data,fd,gd) in enumerate(zip(carriers,fallback.DETAILS,gates.DETAILS)):
        cfg,dest,hoff,boff=fd[2],fd[5],fd[9],fd[10]
        for off in (92,96,98,106):
            b=bytearray(data);pc=cfg+off;d=decode(init.binding.take(data,pc,4 if off!=96 else 2),pc)[pc];w=d['size'];at=pc-0x40000
            # JALR clears address bit0, so change bit1 of its immediate.
            flip=1<<21 if off==106 else 1<<20 if w==4 else 4
            b[at:at+w]=(int.from_bytes(b[at:at+w],'little')^flip).to_bytes(w,'little')
            try:fallback.config_contract(b,cfg,dest,hoff,boff)
            except RuntimeError as e:check(str(e) in ('config copy count','config copy source','config destination','config copy call'),'specific hook copy mutation guard '+str(e))
            else:raise RuntimeError('hook copy mutation escaped')
            count+=1
        pc,size=gd[:2];raw=init.binding.take(data,pc,size)
        for off in (12+8*i,24+8*i,26+8*i,28+8*i):
            b=bytearray(raw);d=decode(raw,pc)[pc+off];w=d['size'];b[off:off+w]=(int.from_bytes(b[off:off+w],'little')^4).to_bytes(w,'little')
            try:gates.body(b,i)
            except RuntimeError as e:check(str(e).startswith('config operand '),'specific hook consumer mutation guard '+str(e))
            else:raise RuntimeError('hook consumer mutation escaped')
            count+=1
    check(count==35,'hook origin mutation census')
    print('PASS:field48/pointerbyte/three-frame offset algebra;35 source/setup/copy/consumer operand mutations rejected')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');o=parser.parse_args()
    app=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(app)==76800 and sha256(app).hexdigest()==init.binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK header identity')
    carriers=[]
    for label,folder,tail,size,digest in init.binding.PROFILES:
        raw=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(raw)==size and sha256(raw).hexdigest()==digest,'candidate identity '+label);carriers.append(raw)
    raw_hex=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
    coverage=sparse.derive(app,carriers,header,raw_hex,sparse.parser())
    ledger=derive(app,carriers,header,coverage);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract()
    tests(app,carriers);output=(json.dumps(ledger,indent=1,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'hook origin exact ledger replay')
    print('PASS:APPfield48->64bytecopy->candidatehook->mode3 joins; savedinput/three-frame preservation projection; exact ledger')
    print('PASS:NO target execution; actualbinding/interveningwriters/MMIOprogress/lifetime UNPROVED')


if __name__=='__main__':main()
