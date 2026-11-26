"""Nominal config-I/O mismatch temporary allocation/release case, static only.

Closed-form sizes/links and original operand checks. No mutable heap/list/NV,
target registers, callback, flash operation or MMIO is executed/emulated.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_post_shortcut_preservation_static as previous
import check_v4160_initial_table_extent_static as layout
import check_v4160_allocation_core_static as core
import check_v4160_allocator_static as release
import check_v4160_app_nv_callbacks_static as callbacks
import check_v4160_config_io_static as io
import check_v4160_post_config_static as post
from check_v4160_optional_hook_origin_static import separated

init,sparse,check=previous.init,previous.sparse,previous.check
OUT=Path(__file__).with_name('v4160-mismatch-temp-release-static.json')
NV,LENGTH,RECORDS=0x08077c00,256,3
CORE_OFFSETS=(56,110,112,114,116,124,134,146,156,166,168,176,180)
FREE_OFFSETS=(28,36,44,52,56,64,68,74,100,104,118,120,128,132,136,138,
 158,160,168,172,176,178,180,182,184,186,188,190,192,194,196,198)


def guarded_core(raw,index):
    n=core.decode(raw);s=core.specs(core.DETAILS[index]);check(set(n)==set(s),'mismatch core boundaries')
    for p,f in s.items():init.g(n,p,'mismatch core operand '+hex(p-core.ENTRY),**f)
    check(sha256(raw).hexdigest()==core.DETAILS[index][-1],'mismatch whole core identity')
    return n


def guarded_free(raw,index):
    n=release.decode(raw);s=release.specifications(release.DETAILS[index]);check(set(n)==set(s),'mismatch free boundaries')
    for p,f in s.items():init.g(n,p,'mismatch free operand '+hex(p-release.ENTRY),**f)
    check(len(raw)==212 and len(n)==73 and sha256(raw).hexdigest()==release.DETAILS[index][-1],'mismatch whole free identity')
    check(not any(d['op'] in ('jal','jalr','call_indirect') for d in n.values()),'mismatch free no calls')
    check(sorted({d['rd'] for d in n.values() if d.get('rd',0)})==[6,10,11,12,13,14,15,16,17,28],'mismatch free GPR set')
    return n


def geometry_cases():
    cases=[]
    for cap in range(14,213,3):
        request=576+6*cap;r=(request+3)&~3
        b2=layout.P+r;p2=b2+8;b3=p2+LENGTH
        free1=27600-r-8;free2=free1-LENGTH-8
        account1=28104-r-8;account2=account1-LENGTH-8
        check(layout.A<layout.B<b2<p2<b3<layout.E,'mismatch ordered nonwrapping header facts')
        check(free1>=25744 and free1-LENGTH>8 and free2>=25480,'mismatch second allocation fits/splits')
        check(b3+8+free2==layout.E and p2+256==b3,'mismatch temporary payload end/newheader')
        check(0<account2<account1<65536 and account2+256+8==account1,'mismatch accounting add-back without U16 wrap')
        check(256+8+free2==free1 and b2+8+free1==layout.E,'mismatch forward merge restores linked extent')
        check(78!=0x8001 and 1!=0 and b2!=layout.A and b2!=layout.B and b3!=layout.E and b3!=layout.B,'mismatch exact free branch predicates')
        check(layout.B<p2 and b2<p2 and b2+8==p2 and p2<b3,'mismatch two search advances then exact payload fit')
        check(layout.P+request<=layout.P+r==b2 and layout.T+4*cap<=b2,'mismatch original table payload separated')
        # Fixed first-header/link facts, not allocated-header objects or a list traversal.
        cases.append({'capacity':cap,'first_request':request,'first_payload_R':r,
            'temporary_header':hex(b2),'temporary_payload':hex(p2),'temporary_size':256,
            'next_free_header':hex(b3),'free_remainder_before_temp':free1,'free_remainder_during_temp':free2,
            'account_after_first':account1,'account_during_temp':account2,'account_after_temp_free':account1,
            'released_linked_payload_size':free1,'released_next':'0x2000b184'})
    check(len(cases)==67,'mismatch67 capacity cases')
    return cases


def derive(app,carriers,header,coverage):
    parent=previous.derive(app,carriers,header,coverage);profiles=[];cases=geometry_cases()
    ios=io.derive(app,carriers,header)['profiles'];posts=post.derive(app,carriers,header)['profiles']
    cb=callbacks.derive(app,carriers,header);app_bodies={b['role']:b for b in cb['APP_bodies']}
    check(set(app_bodies)=={'read','write','unlock','lock','erase','program','timer'},'mismatch closed APP callback family')
    write=app_bodies['write'];wn={d['pc']:d for d in write['instructions']}
    check(write['encoded_GPR_writes']==[1,2,8,10,11,12] and
        all(18 not in b['encoded_GPR_writes'] and 3 not in b['encoded_GPR_writes'] for b in app_bodies.values()),'mismatch S2/GP callback preservation')
    init.g(wn,0x197c4,'mismatch save entry source',op='store',rs1=2,rs2=12,imm=12,width=4)
    init.g(wn,0x197d2,'mismatch reload source',op='load',rd=12,rs1=2,imm=12,width=4)
    # All five direct callees and their exact stores/loops are pinned by cb.body.
    check([d['target'] for d in write['instructions'] if d['op']=='jal']==[0x18e98,0x18ec4,0x18ef2,0x18eb6,0x19764],'mismatch write direct callee set')
    for i,(data,ip,pp,prior) in enumerate(zip(carriers,ios,posts,parent['profiles'])):
        ctx=int(ip['metadata_base'],16);state=ctx+80;pc=int(ip['target'],16)
        check({'address':hex(ctx),'bytes':40} in pp['fixed_zero_fill_requests'],'mismatch initial count0 fill witness')
        cn=guarded_core(init.binding.take(data,core.DETAILS[i][0],208),i)
        fn=guarded_free(init.binding.take(data,release.DETAILS[i][0],212),i)
        check(core.DETAILS[i][5]==ctx and release.DETAILS[i][4]==ctx,'mismatch shared accounting base')
        check(ip['direct_calls'][-1]['target']==hex(release.ENTRY) and ip['direct_calls'][0]['target']==hex(core.ENTRY),'mismatch IO allocate/free joins')
        n={d['pc']:d for d in ip['instructions']}
        for off,f in ((58,dict(op='beq',rs1=14,rs2=15,target=pc+22)),
            (62,dict(op='load',rd=10,rs1=8,imm=12,width=2)),
            (84,dict(op='store',rs1=14,rs2=10,imm=32,width=4)),
            (92,dict(op='load',rd=12,rs1=8,imm=12,width=2)),
            (98,dict(op='li',rd=18,imm=0)),(108,dict(op='load',rd=15,rs1=8,imm=14,width=1)),
            (110,dict(op='load',rd=12,rs1=9,imm=32,width=4)),
            (138,dict(op='load',rd=11,rs1=8,imm=12,width=2)),
            (150,dict(op='addi',rd=18,rs1=18,imm=1)),
            (154,dict(op='store',rs1=12,rs2=10,imm=0,width=4)),
            (126,dict(op='li',rd=10,imm=0)),(128,dict(op='store',rs1=9,rs2=0,imm=32,width=4)),
            (132,dict(op='store',rs1=9,rs2=0,imm=36,width=4))):init.g(n,pc+off,'mismatch IO operand '+hex(off),**f)
        check(ip['cache_pointer_slot']==hex(ctx+32) and ip['neighbor_clear_slot']==hex(ctx+36),'mismatch cache and cleanup slots')
        for case in cases:
            b2=int(case['temporary_header'],16);p2=int(case['temporary_payload'],16);b3=int(case['next_free_header'],16)
            for a,w in ((ctx+1,1),(ctx+2,1),(ctx+32,4),(ctx+36,4),(ctx+40,4),(ctx+72,4),(state+48,4),(state+64,4)):
                check(separated(p2,256,a,w) and separated(b2,8,a,w),'mismatch temp/cache/config disjoint')
                check(separated(b3,8,a,w),'mismatch remainder header/config disjoint')
            for a,w in ((ctx+1,1),(ctx+2,1),(ctx+32,4),(ctx+36,4),(ctx+40,4),(ctx+72,4),(state+48,4)):
                check(separated(ctx+6,2,a,w),'mismatch accounting excludes live global')
        check(all(separated(NV+256*j,256,layout.P,1848) for j in range(3)),'mismatch numeric NV/table intervals separate')
        profiles.append({'label':ip['label'],'IO_entry':ip['target'],'IO_body_sha256':ip['sha256'],
            'reused_core_sha256':core.DETAILS[i][-1],'free_source':hex(release.DETAILS[i][0]),'reused_free_sha256':release.DETAILS[i][-1],
            'cache_pointer_slot':ip['cache_pointer_slot'],'cleanup_neighbor':ip['neighbor_clear_slot'],
            'count_byte':pp['count_byte'],'capacity_byte':pp['capacity_byte'],'table_pointer_word':pp['table_slot'],
            'builtin_values':pp['registered_literals'],'conditional_post_count':3,'conditional_IO_and_post_reply':0,
            'installed_binding_actual_NV_or_poll_progress_proved':False})
    return {'schema':'TSL9-mismatch-temp-release-static-v1','profile':parent['profile'],'APP_sha256':sha256(app).hexdigest(),
        'scope':'nominal mismatch path composition usingexisting complete allocator/free/IO/read/write/helper bodies; scalar67-case geometry only; no newly reconstructed C bytes',
        'profiles':profiles,'capacity_cases':cases,
        'reused_APP_bodies':[{'role':b['role'],'start':b['start'],'bytes':b['bytes'],'sha256':b['sha256']} for b in app_bodies.values()],
        'entry_premises':['initial-table-extent nominal freshH2000418c/L7000 andfirstP/table extent premises; not the previous shortcut readback-equal premise',
            'IO entry freshNVbase08077c00,U16length256,U8recordcount3,read1979a/write197be andcopy20000332 matchandremainstable',
            'completedinitialread4bytes assembledLE differsfromfreshNVbase; actualNVcontents notobserved',
            'code/context/ownedheaders andnonaliasingvalidframes preserved; normalinstruction/MMIO/NV/pollcompletion, noDMA/interrupt/reentry/externalwriters oradversephysicalalias'],
        'second_allocation':'largeheadB1 tagged1 is skipped; nextB2=P1+R1 free,sizeS1=27600-R1-8; R2=256 andS1-256>8 =>split,tag78,returnP2=B2+8; nextfreeB3=P2+256,sizeS1-264,nextE',
        'loop_preservation':'IO cachectx+32 storesP2; fill(P2,ff,256) andprecallSW[P2] stayintemp payload. Matchingwritefamily onlyownframes, encodedMMIO and256B alignedNVdestination stores; no localwrite tocache/config/headers understatednonaliaspremises. S2 survives allcalls; exact3 iterations indices0/1/2',
        'per_record_arguments':{'destination_hex':[hex(NV+256*i) for i in range(3)],'A1_num':64,'A2_source':'P2 for all3calls',
            'write_wrapper_entry_num_used':False,'program_source_bytes':256,'source_word_offsets':list(range(0,256,4)),
            'program_destination_extent':'alignedNVbase+256*i .. +255, not target execution or NV success'},
        'free_case':'lastcachePcurrent=P2 exactownedpayload. Search advances A->B1->B2; P2=B2+8 betweenB2/nextB3. tag78!=8001 so no specialcounter. prevB1 tag1 blocksbackmerge; nextB3 free andneithersentinel norlargehead =>forwardmergeonly',
        'free_effects':'clearB2tag; account+256; B2.size=256+8+(S1-264)=S1,B2.next=E; account+8. FirstB1header/tag andP1payload/table untouched; noSP/RA/S/GP definitions inprivatefree',
        'restoration_limit':'restoreslinked-header layout/accounting forfree remainder; obsoleteB3headerbytes andtemp payloadcontentsremain in now-freepayload; no heapbyteimage restoration/wipe claim',
        'cleanup_and_publication':'IO ignoresfreeA0, forces0, clearsctx+32/+36,restoresframe. P1/table/capacity/count0 survive; postthreebuiltin words T/T+4/T+8,count3,postreply0. No firstallocationfree onthisnominalcase',
        'remaining':['outerinitializer/APP continuation throughregistration andoptionalhook','establishactualfreshsourcefields/callbackslots andinstalledproviders',
            'otherlength/count/NV domains, interrupted/faulting/clobberingcallbacks andgeneral freeownership','physicalNV/MMIOeffects/polltermination andexternalpayloadlifetime'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    cases=geometry_cases();check(len(cases)==67,'mismatch geometry cases')
    for case in cases:
        p2=int(case['temporary_payload'],16);b2=int(case['temporary_header'],16)
        for off in range(0,256,4):check(p2<=p2+off and p2+off+4<=p2+256,'mismatch program64word source extent')
        check(layout.P+case['first_payload_R']==b2 and p2>b2,'mismatch table/temp boundary')
    check([NV+256*i for i in range(3)]==[0x08077c00,0x08077d00,0x08077e00] and all((NV+256*i)&255==0 for i in range(3)),'mismatch three alignedNV destinations')
    count=0
    for i,data in enumerate(carriers):
        for module,details,offsets,guard in ((core,core.DETAILS,CORE_OFFSETS,guarded_core),(release,release.DETAILS,FREE_OFFSETS,guarded_free)):
            size=208 if module is core else 212
            raw=init.binding.take(data,details[i][0],size);nodes=module.decode(raw)
            for off in offsets:
                b=bytearray(raw);w=nodes[module.ENTRY+off]['size'];b[off:off+w]=(int.from_bytes(b[off:off+w],'little')^(1<<20 if w==4 else 4)).to_bytes(w,'little')
                try:guard(b,i)
                except RuntimeError as e:check(str(e).startswith('mismatch core operand ' if module is core else 'mismatch free operand '),'specific mismatch mutation guard '+str(e))
                else:raise RuntimeError('mismatch mutation escaped')
                count+=1
    check(count==90,'mismatch mutation census')
    print('PASS:67 first-capacity cases; second256B split/release/accounting and64word source extents;90 core/free mutations rejected')


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
    tests(carriers);output=(json.dumps(ledger,indent=1,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'mismatch exact ledger replay')
    print('PASS:original IO/core/free/APP callbacks joins; conditional mismatch temp-release/table preservation throughpostRET; exact ledger')
    print('PASS:NO target execution; actualNV/pollprogress/otherinputdomains/installedprovider/lifetime UNPROVED')


if __name__=='__main__':main()
