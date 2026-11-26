"""JT0 early publication and stop-task/dispatcher return-mask static join.

Only original bytes, operand guards, conditional graphs and host equations.
No target ISA, copy state, scheduler, node, provider or MMIO execution/model.
"""
import argparse
import json
import re
from hashlib import sha256
from pathlib import Path
import check_v4160_event_dispatch_static as previous
import check_v4160_sparse_boot_coverage as sparse

init,ROOT,MASK=previous.init,previous.ROOT,previous.MASK
check=init.check
OUT=Path(__file__).with_name('v4160-dispatch-origin-mask-static.json')
DETAILS=((0x2000251c,0x20002e34,'98fe32a0b24638e9f678c2112dbae4fa05ad6e45d2a9fb84bedb67c3831880b0'),
         (0x20002568,0x20002e80,'be10a8a9345b43c9581cade65059b0aa39b9e6cf46953b5179b7cd909aaa926c'))


def startup_body(raw,pc,initializer,seed,digest):
    check(len(raw)==68,'startup complete length')
    n=init.decode(raw[:64],pc)
    check(raw[64:]==bytes.fromhex('73002030'),'startup MRET encoding')
    n[pc+64]=dict(pc=pc+64,bytes=raw[64:].hex(),size=4,op='mret')
    check(len(n)==18,'startup instruction count')
    for off,reg,target in ((0,3,0x20004000),(8,2,0x20010000),(16,10,seed),
                           (24,11,0x20000010),(32,12,0x20000040)):
        a,b=n[pc+off],n[pc+off+4]
        init.g(n,pc+off,'startup constant upper '+hex(off),op='auipc',rd=reg)
        init.g(n,pc+off+4,'startup constant lower '+hex(off),op='addi',rd=reg,rs1=reg)
        check((pc+off+a['imm']+b['imm'])&MASK==target,'startup constant target '+hex(off))
    specs={40:dict(op='bgeu',rs1=11,rs2=12,target=pc+64),
        44:dict(op='load',rd=5,rs1=10,imm=0,width=4),
        48:dict(op='store',rs2=5,rs1=11,imm=0,width=4),
        52:dict(op='addi',rd=10,rs1=10,imm=4),54:dict(op='addi',rd=11,rs1=11,imm=4),
        56:dict(op='bltu',rs1=11,rs2=12,target=pc+44),60:dict(op='jal',rd=1,target=initializer),
        64:dict(op='mret')}
    for off,f in specs.items():init.g(n,pc+off,'startup instruction '+hex(off),**f)
    edges={}
    for p,d in n.items():
        if d['op']=='mret':qs=[]
        elif d['op'] in ('bltu','bgeu'):qs=[p+d['size'],d['target']]
        else:qs=[p+d['size']]
        check(all(q in n for q in qs),'startup bounded CFG')
        edges[p]=qs
    check(sha256(raw).hexdigest()==digest,'startup complete identity')
    return {'start':hex(pc),'end_exclusive':hex(pc+68),'bytes':68,'sha256':digest,'instructions':list(n.values()),
        'conditional_normal_return_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},
        'MRET_external_exit':hex(pc+64),'MRET_CSR_target_or_effect_proved':False,
        'initializer_link':hex(pc+64),'unconstrained_skip_edge_bypasses_initializer':True,
        'constant_operand_premise':'A1=20000010 < A2=20000040; valid normal loop progress gives 12 source words before initializer call',
        'actual_loop_or_boot_executed':False}


def initializer_body(raw,pc,detail,jt1,jt2):
    n=init.decode(raw,pc);G=0x20003000;R=0x20000000
    first_last,second_src,second_dest,second_last=detail[7],detail[6],detail[7],detail[8]
    first_src=0x402b0 if pc==0x6de0c else 0x402f0
    specs={0:dict(op='addi',rd=2,rs1=2,imm=-16),2:dict(op='lui',rd=14,imm=R),
        6:dict(op='store',rs2=1,rs1=2,imm=12,width=4),8:dict(op='lui',rd=15,imm=R),
        12:dict(op='addi',rd=14,rs1=14,imm=previous.ENTRY-R),
        16:dict(op='store',rs2=14,rs1=15,imm=0,width=4),
        18:dict(op='lui',rd=14,imm=0x20002000),22:dict(op='addi',rd=14,rs1=14,imm=jt1-0x20002000),
        26:dict(op='store',rs2=14,rs1=15,imm=4,width=4),28:dict(op='lui',rd=14,imm=G),
        32:dict(op='addi',rd=14,rs1=14,imm=jt2-G),36:dict(op='lui',rd=12,imm=G),
        40:dict(op='lui',rd=11,imm=R),44:dict(op='lui',rd=10,imm=0x40000),
        48:dict(op='store',rs2=14,rs1=15,imm=8,width=4),
        50:dict(op='addi',rd=12,rs1=12,imm=first_last-G),
        54:dict(op='addi',rd=11,rs1=11,imm=64),58:dict(op='addi',rd=10,rs1=10,imm=first_src-0x40000),
        70:dict(op='lui',rd=12,imm=G),74:dict(op='lui',rd=11,imm=G),78:dict(op='lui',rd=10,imm=0x6f000),
        82:dict(op='addi',rd=12,rs1=12,imm=second_last-G),
        86:dict(op='addi',rd=11,rs1=11,imm=second_dest-G),90:dict(op='addi',rd=10,rs1=10,imm=second_src-0x6f000),
        102:dict(op='load',rd=1,rs1=2,imm=12,width=4),104:dict(op='addi',rd=2,rs1=2,imm=16)}
    check(set(n)=={pc+o for o in specs}|{pc+o for o in (62,66,94,98,106,110)},'initializer complete boundaries')
    for off,f in specs.items():init.g(n,pc+off,'JT initializer instruction '+hex(off),**f)
    for off,rd,target in ((62,1,0x20000010),(94,1,0x20000010),(106,0,init.ZERO)):
        init.pair(n,pc+off,rd,target,'JT initializer transfer '+hex(off))
    check(len(raw)==114 and len(n)==32 and sha256(raw).hexdigest()==detail[11],'JT initializer complete identity')
    check(not any(d['op'] in ('jal','jalr','call_indirect','jump','jr','beqz','bnez','beq','bne','bgeu','bltu')
                  for p,d in n.items() if p<pc+62),'JT stores precede first call without branch')
    stores=[d for d in n.values() if d['op']=='store'];check(len(stores)==4,'JT initializer store count')
    edges={hex(p):([hex(p+d['size'])] if p!=pc+110 else [hex(init.ZERO)]) for p,d in n.items()}
    return {'start':hex(pc),'end_exclusive':hex(pc+114),'bytes':114,'sha256':detail[11],
        'instructions':list(n.values()),'stores':stores,'conditional_normal_return_CFG':edges,
        'JT_words':[{'pc':hex(pc+o),'address':hex(R+4*i),'value':hex(v)}
            for i,(o,v) in enumerate(((16,previous.ENTRY),(26,jt1),(48,jt2)))],
        'first_copy_transfer_pc':hex(pc+66),'second_copy_transfer_pc':hex(pc+98),'zero_tail_pc':hex(pc+110),
        'pointer_publication_precedes_code_copy':True,'code_ready_when_pointer_published_proved':False}


def stop_body(raw,pc,M,clear_target,digest):
    n=init.decode(raw,pc);G=0x20003000
    specs={0:dict(op='addi',rd=2,rs1=2,imm=-32),8:dict(op='lui',rd=15,imm=0x40024000),
        16:dict(op='load',rd=19,rs1=15,imm=524,width=4),20:dict(op='mv',rd=18,rs2=10),
        22:dict(op='mv',rd=8,rs2=11),24:dict(op='store',rs2=0,rs1=15,imm=524,width=4),
        28:dict(op='fence.i'),40:dict(op='mv',rd=9,rs2=10),42:dict(op='beqz',rs1=10,target=pc+48),
        44:dict(op='store',rs2=0,rs1=10,imm=2,width=2),48:dict(op='mv',rd=11,rs2=8),
        50:dict(op='mv',rd=10,rs2=18),52:dict(op='jal',rd=1,target=clear_target),
        54:dict(op='lui',rd=15,imm=G),58:dict(op='load',rd=15,rs1=15,imm=M-G,width=1),
        62:dict(op='bne',rs1=15,rs2=18,target=pc+80),66:dict(op='lui',rd=15,imm=G),
        70:dict(op='load',rd=14,rs1=15,imm=M+64-G,width=2),74:dict(op='or',rd=8,rs1=8,rs2=14),
        76:dict(op='store',rs2=8,rs1=15,imm=M+64-G,width=2),80:dict(op='lui',rd=15,imm=0x40024000),
        84:dict(op='store',rs2=19,rs1=15,imm=524,width=4),88:dict(op='li',rd=10,imm=0),
        90:dict(op='bnez',rs1=9,target=pc+94),92:dict(op='li',rd=10,imm=6),
        104:dict(op='addi',rd=2,rs1=2,imm=32),106:dict(op='jr',rs1=1)}
    for save,restore,reg,off in ((2,96,8,24),(4,100,18,16),(6,102,19,12),(12,94,1,28),(14,98,9,20)):
        specs[save]=dict(op='store',rs2=reg,rs1=2,imm=off,width=4)
        specs[restore]=dict(op='load',rd=reg,rs1=2,imm=off,width=4)
    check(set(n)=={pc+o for o in specs}|{pc+32,pc+36},'stop-task complete boundaries')
    for off,f in specs.items():init.g(n,pc+off,'mask stop instruction '+hex(off),**f)
    init.pair(n,pc+32,1,0x20000314,'stop-task lookup target')
    edges,cycles=init.timer.cfg(n,pc);check(not cycles,'stop-task acyclic conditional CFG')
    stores=[d for d in n.values() if d['op']=='store']
    check(len(n)==39 and len(stores)==9 and len(raw)==108 and sha256(raw).hexdigest()==digest,'stop-task complete identity')
    return {'start':hex(pc),'end_exclusive':hex(pc+108),'bytes':108,'sha256':digest,'instructions':list(n.values()),
        'stores':stores,'conditional_normal_return_CFG':edges,'lookup_target':'0x20000314',
        'node_mask_clear':'nonzero lookup reply Q -> SH0 at Q+2 before clear-event; no release here',
        'clear_call':{'pc':hex(pc+52),'target':hex(clear_target),'A0':'saved full entry task','A1':'saved full entry event','scalar_reply_tested':False},
        'return_mask_update':{'cursor_read_pc':hex(pc+58),'branch_pc':hex(pc+62),'load_pc':hex(pc+70),'store_pc':hex(pc+76),
            'slot':hex(M+64),'predicate':'fresh U8[M] == preserved full entry task',
            'value':'low16(fresh U16[M+64] OR preserved full entry event)',
            'requires_lookup_hit':False,'requires_clear_event_success':False},
        'normal_reply':'0 iff preserved lookup result S1 nonzero, else6; not event-clear/mask-update acknowledgement',
        'control':'save/read4002420c, write0, FENCE.I; restore outer saved word after nested clear normal return; physical effects unproved'}


def derive(app,carriers,header,coverage):
    parent=previous.derive(app,carriers,header);leaves=init.timer.derive(app,carriers,header);profiles=[]
    check(re.search(rb'^\s*#define\s+RAM_BASE_ADDRESSS\s+0x20000000\s*$',header,re.M) is not None,'header RAM JT base')
    check(re.search(rb'^\s*#define\s+BLE_LIB_RAM_JT\(n\)\s+\(\*\(uint32_t\*\)\(\s*RAM_BASE_ADDRESSS\s*\+\s*n\*4\s*\)\)',header,re.M) is not None,'header RAM JT stride')
    for i,(data,old,leaf,source,desc) in enumerate(zip(carriers,parent['profiles'],leaves['profiles'],coverage['profiles'],DETAILS)):
        jt1,jt2,entry_sha=desc;detail=init.DETAILS[i];pc=detail[0];M=int(old['metadata_base'],16)
        mapping=init.binding.profile(data,old['label']);entry=int(mapping['entry'],16);seed=int(mapping['seed_source'],16)
        startup=startup_body(init.binding.take(data,entry,68),entry,pc,seed,entry_sha)
        initializer=initializer_body(init.binding.take(data,pc,114),pc,detail,jt1,jt2)
        check(initializer['JT_words'][0]['value']==old['body']['runtime_start'],'JT0 to complete dispatcher entry')
        ranges=[('seed',0x20000010,0x20000040),('first_copy',int(mapping['first_copy']['destination'],16),int(mapping['first_copy_end_exclusive'],16)),
                ('second_copy',detail[7],detail[8]+4),('zero',detail[3],detail[4]+4)]
        check(all(0<=a<b<=MASK and (b<=0x20000000 or 0x2000000c<=a) for _,a,b in ranges),'listed startup destinations disjoint from JT0..JT2')
        clear=leaf['clear_event'];outer=init.timer.outer.DETAILS[i];stop_pc=outer[1]
        check(outer[2:4]==(M,M+64) and int(clear['event_table_pointer_slot'],16)==int(old['pending_pointer_slot'],16),
              'stop/clear/dispatcher storage join')
        stop=stop_body(init.binding.take(data,stop_pc,108),stop_pc,M,int(clear['flash_target'],16),outer[-1])
        check(init.binding.word(data,0x4005c)&~1==stop_pc and init.binding.word(data,0x40054)&~1==int(clear['flash_target'],16),'stop/clear slot aliases')
        check(clear['GPR_writes']==[10,11,12,13,14,15] and leaf['lookup']['GPR_writes']==[10,14,15],
              'nested leaves have no encoded S/SP writes')
        check(source['second_copy_request']['missing_bytes']==4 and not source['full_boot_proved'],'sparse boot gap retained')
        profiles.append({'label':old['label'],'metadata_base':hex(M),'startup':startup,'initializer':initializer,'stop_task':stop,
            'clear_event':{'target':clear['flash_target'],'bytes':clear['bytes'],'sha256':clear['sha256'],
                'event_pointer_slot':clear['event_table_pointer_slot'],'normal_return_valid':0,'normal_return_invalid':3,
                'accepted':'full entry task < fresh U8[M+1]; SH(old_U16 & ~full entry event) to fresh pending table',
                'rejected':'no pending pointer read/write; no guard on later stop cursor==task comparison',
                'writes_return_mask_directly':False,'dynamic_alias_exclusion_proved':False},
            'startup_destinations':[{'role':r,'start':hex(a),'end_exclusive':hex(b)} for r,a,b in ranges],
            'second_copy_missing_source_ranges':source['second_copy_request']['missing_ranges'],
            'dispatcher_join':{'entry':old['body']['runtime_start'],'flash_source':old['flash_source'],
                'return_mask_slot':old['return_mask_slot'],'pending_pointer_slot':old['pending_pointer_slot'],
                'mask_clear_pc':hex(previous.ENTRY+310),'mask_reload_pc':hex(previous.ENTRY+316)},
            'actual_installed_binding_proved':False})
    bodies=[p[role] for p in profiles for role in ('startup','initializer','stop_task')]
    check(sum(b['bytes'] for b in bodies)==580 and sum(len(b['instructions']) for b in bodies)==178,
          'origin/mask body byte and instruction census')
    check(sum(d['op']=='store' for b in bodies for d in b['instructions'])==28,'origin/mask store census')
    return {'schema':'TSL9-dispatch-origin-mask-static-v1','profile':init.timer.PROFILE,
        'scope':'2 complete68B startups +2 complete114B initializers +2 complete108B stop-task bodies; transitive clear/dispatch/HEX provenance',
        'profiles':profiles,'masked_return_join':'if mask C0|E survives until dispatcher read, low16(H | (R & ~(C0|E))); H reasserted bits survive',
        'initialization_order':'JT0..2 word stores before first code-copy call; no guarantee pointer ready when published or remains unchanged',
        'formal_CFG_dominance':'unconstrained startup skip edge reaches MRET without initializer; fixed operands/normal finite loop are required',
        'writer_scope':'concrete direct writer plus dispatcher clear only; not a whole-program writer census',
        'premises':['supported ISA/first-copy bytes and code/frame valid; normal progress/callee-return where described',
            'needed S/SP/frame and globals/pointers preserved; no adverse alias, interrupt, writer or reentry',
            'fresh cursor/count/base/mask reads equated only with separate evidence; no whole-boot or atomicity claim'],
        'remaining_boundaries':['actual installed provider and runtime JT0 retention','actual call path/task/cursor/reentry',
            'other direct/computed/bulk writers and node/record ownership','opaque tail/callees, MRET CSR and MMIO effects'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    # Bitfield/range algebra only, no loader/event/node/register state model.
    for value in range(65536):
        for event in (0,1,0x8000,0xffff):
            mask=value|event
            check((value|event|event)==mask,'return-mask OR idempotence')
            for reply in (0,0xffff):
                for pending in (0,0xffff):
                    merged=(pending|(reply&~mask))&0xffff
                    check(merged&event==pending&event,'masked reply cannot reintroduce canceled bits, pending can')
    for cursor in range(256):
        for task in (cursor,cursor+256,0xffffffff):
            check((cursor==task)==(task<=255 and cursor==task),'full task versus U8 cursor')
    check((0x20000040-0x20000010)//4==12 and 0x20000010<0x20000040,'fixed seed interval and initial skip predicate')
    check(0x20000000+0x7d0==previous.ENTRY,'JT0 constant to dispatcher identity')
    check((0xffff&~1)|1==0xffff,'pending reassertion survives return mask')
    # All four lookup/clear outcomes can coexist with a current-task mask update.
    paths=[(found,clear,0 if found else 6) for found in (False,True) for clear in (0,3)]
    check(paths==[(False,0,6),(False,3,6),(True,0,0),(True,3,0)],'stop scalar reply independent of clear reply')
    jt1,jt2,digest=DETAILS[0];detail=init.DETAILS[0];pc=detail[0]
    cases=[('initializer',o,f) for o,f in ((12,1<<20),(16,0x40),(26,0x40),(48,0x40),(54,1<<20),(102,4))]
    cases += [('stop',o,f) for o,f in ((44,1<<20),(58,1<<20),(62,0x1000),(70,1<<20),(74,4),(76,1<<20),(92,4))]
    for role,off,flip in cases:
        stop_pc=init.timer.outer.DETAILS[0][1];start,size=(pc,114) if role=='initializer' else (stop_pc,108)
        raw=bytearray(init.binding.take(carriers[0],start,size));n=init.decode(raw,start);width=n[start+off]['size']
        raw[off:off+width]=(int.from_bytes(raw[off:off+width],'little')^flip).to_bytes(width,'little')
        message=('JT initializer instruction ' if role=='initializer' else 'mask stop instruction ')+hex(off)
        try:
            if role=='initializer':initializer_body(raw,pc,detail,jt1,jt2)
            else:stop_body(raw,stop_pc,detail[5]-80,init.timer.DETAILS[0][1],init.timer.outer.DETAILS[0][-1])
        except RuntimeError as e:check(str(e)==message,'unexpected origin/mask mutation guard '+str(e))
        else:raise RuntimeError('origin/mask mutation escaped')
    data=carriers[0];mapping=init.binding.profile(data,'V1.31');entry=int(mapping['entry'],16);seed=int(mapping['seed_source'],16)
    for off,flip,wanted in ((4,1<<20,'startup constant target 0x0'),
                            (40,0x1000,'startup instruction 0x28'),
                            (48,1<<20,'startup instruction 0x30'),
                            (64,1<<20,'startup MRET encoding')):
        raw=bytearray(init.binding.take(data,entry,68));raw[off:off+4]=(int.from_bytes(raw[off:off+4],'little')^flip).to_bytes(4,'little')
        try:startup_body(raw,entry,pc,seed,digest)
        except RuntimeError as e:check(str(e)==wanted,'unexpected startup mutation guard '+str(e))
        else:raise RuntimeError('startup mutation escaped')
    print('PASS: 262144 mask identities/1048576 merge cases; 768 full-task cases; 17 specified raw mutations')


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true',help='Create ledger exclusively');o=p.parse_args()
    app=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(app)==76800 and sha256(app).hexdigest()==init.binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK header identity')
    carriers=[]
    for label,folder,tail,size,digest in init.binding.PROFILES:
        raw=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(raw)==size and sha256(raw).hexdigest()==digest,'candidate identity '+label);carriers.append(raw)
    hex_sources=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
    coverage=sparse.derive(app,carriers,header,hex_sources,sparse.parser())
    sources,vectors=init.timer.source_contract();ledger=derive(app,carriers,header,coverage)
    ledger['sources'],ledger['official_Xwchc_vectors']=sources,vectors
    tests(carriers);output=(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'dispatch origin/mask exact ledger replay')
    print('PASS: 6 complete bodies, 580 bytes/178 instructions/28 stores; JT0-to-dispatcher and stop-mask/merge joins')
    print('PASS: exact ledger replay and full sparse-source provenance; full boot/retention/installed binding UNPROVED; NO target execution')


if __name__=='__main__':main()
