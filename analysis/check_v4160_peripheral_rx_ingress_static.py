"""Other ingress: complete interrupt entry and peripheral record reader.

Bytes, conditional CFG/store projections and host interval arithmetic only.
No target ISA/MRET, CSR/MMIO, provider, stack/RAM/copy execution/emulation.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_rx_cache_ingress_static as previous
import check_v4160_app_jt0_call_chain_static as boot

init,sparse,check,take=previous.init,previous.sparse,previous.check,previous.take
OUT=Path(__file__).with_name('v4160-peripheral-rx-ingress-static.json')
DETAILS=(('irq',0x12c24,52,17,0,'44ab1cdae33f0151e8270b3769d9dca81847154bf88d3f691443d77200ece51a'),
 ('reader',0x18d78,164,53,16,'678a3cbf42bc02d5c730973675858a18e538af9fdc1cb74dd9296f220f487ae3'))


def decode(raw,pc):
    n={};off=0
    while off<len(raw):
        h=int.from_bytes(raw[off:off+2],'little');size=2 if h&3!=3 else 4
        check(off+size<=len(raw),'peripheral RX whole instruction');chunk=raw[off:off+size];p=pc+off
        if size==4 and int.from_bytes(chunk,'little')==0x30200073:
            d=dict(pc=p,bytes=chunk.hex(),size=4,op='mret')
        else:d=previous.decode(chunk,p)[p]
        n[p]=d;off+=size
    return n


def specs(role,pc):
    s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def load(o,r,b,v=0,w=4):e(o,'load',rd=r,rs1=b,imm=v,width=w)
    def store(o,r,b,v=0,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    def addi(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    def imm(o,op,r,a,v):e(o,op,rd=r,rs1=a,imm=v)
    def bz(o,op,r,t):e(o,op,rs1=r,target=pc+t)
    def call(o,t):e(o,'jal',rd=1,target=t)
    if role=='irq':
        e(0,'lui',rd=10,imm=0x40006000);addi(4,10,10,1024);load(8,15,10,12)
        imm(10,'andi',15,15,3);bz(12,'beqz',15,48);addi(14,2,2,-32);addi(16,12,2,12);li(18,11,0)
        call(20,0x18d78);load(24,12,2,22,1);load(28,10,2,12,2);addi(32,11,2,23);li(36,13,0)
        call(38,0x12bc8);addi(42,2,2,32);e(44,'mret');e(48,'mret')
    elif role=='reader':
        imm(0,'slli',15,11,4);e(4,'add',rd=15,rs1=15,rs2=10);load(6,14,15,432)
        imm(10,'andi',14,14,4);store(12,14,12,8,1);bz(16,'bnez',14,144)
        load(18,14,15,432);imm(22,'srli',14,14,21);store(24,14,12,0)
        load(26,14,15,432);imm(30,'andi',14,14,2);store(32,14,12,9,1)
        load(36,14,15,436);imm(40,'andi',14,14,15);store(42,14,12,10,1)
        load(46,14,15,436);imm(50,'srli',14,14,8);store(52,14,12,19,1)
        load(56,14,15,440);store(60,14,12,11,1)
        for off,source,shift,dest in ((64,440,8,12),(74,440,16,13),(84,440,24,14)):
            load(off,14,15,source);imm(off+4,'srli',14,14,shift);store(off+6,14,12,dest,1)
        load(94,14,15,444);store(98,14,12,15,1)
        for off,shift,dest in ((102,8,16),(112,16,17)):
            load(off,14,15,444);imm(off+4,'srli',14,14,shift);store(off+6,14,12,dest,1)
        load(122,15,15,444);imm(126,'srli',15,15,24);store(128,15,12,18,1)
        bz(132,'bnez',11,154);load(134,15,10,12);imm(136,'ori',15,15,32);store(140,15,10,12);e(142,'jr',rs1=1)
        load(144,14,15,432);imm(148,'srli',14,14,3);store(150,14,12,4);e(152,'jump',target=pc+26)
        load(154,15,10,16);imm(156,'ori',15,15,32);store(160,15,10,16);e(162,'jr',rs1=1)
    else:raise RuntimeError('unknown peripheral RX role')
    return s


def body(raw,role,pc,size,count,store_count,digest):
    n=decode(raw,pc);expected=specs(role,pc);check(set(n)==set(expected),'peripheral RX complete boundaries '+role)
    for p,f in expected.items():init.g(n,p,'peripheral RX '+role+' instruction '+hex(p-pc),**f)
    edges={};calls=[];terminals=[]
    for p,d in n.items():
        if d['op'] in ('jr','mret'):
            if d['op']=='jr':check(d['rs1']==1,'peripheral RX ordinary return register')
            qs=[];terminals.append({'pc':hex(p),'kind':d['op']})
        elif d['op']=='jump':qs=[d['target']]
        elif d['op'] in ('beqz','bnez'):qs=[p+d['size'],d['target']]
        else:qs=[p+d['size']]
        check(all(q in n for q in qs),'peripheral RX full local successors '+role);edges[p]=qs
        if d['op']=='jal':
            check(d['rd']==1,'peripheral RX linked calls');calls.append({'pc':hex(p),'target':hex(d['target']),
                'link':hex(p+d['size']),'normal_return_proved':False})
    seen=set();active=set()
    def visit(p):
        check(p not in active,'peripheral RX acyclic local CFG '+role)
        if p in seen:return
        seen.add(p);active.add(p)
        for q in edges[p]:visit(q)
        active.remove(p)
    visit(pc);check(seen==set(n),'peripheral RX full reachability '+role)
    stores=[d for d in n.values() if d['op']=='store'];writes=sorted({d['rd'] for d in n.values() if d.get('rd',0)})
    check((len(raw),len(n),len(stores),sha256(raw).hexdigest())==(size,count,store_count,digest),'peripheral RX full identity '+role)
    check(writes==([1,2,10,11,12,13,15] if role=='irq' else [14,15]),'peripheral RX exact encoded GPR writes '+role)
    check(len(terminals)==2 and all(t['kind']==('mret' if role=='irq' else 'jr') for t in terminals),'MRET vs ordinary RET distinction')
    paths=[]
    def project(p,path):
        path=path+[p]
        if not edges[p]:
            path_stores=[n[q] for q in path if n[q]['op']=='store']
            record=set()
            for d in path_stores:
                if d['rs1']==12:record.update(range(d['imm'],d['imm']+d['width']))
            paths.append({'pcs':[hex(q) for q in path],'store_pcs':[hex(d['pc']) for d in path_stores],
                'direct_record_store_offsets':sorted(record),
                'record_offsets_not_directly_written':sorted(set(range(20))-record),
                'base_relative_control_store_offsets':[d['imm'] for d in path_stores if d['rs1']==10]})
        for q in edges[p]:project(q,path)
    if role=='reader':
        check(not calls and all(d['rs2'] in (14,15) for d in stores),'reader no calls or direct record-pointer value stores')
        project(pc,[]);check(len(paths)==4,'reader format/control complete path combinations')
        check({tuple(p['record_offsets_not_directly_written']) for p in paths}=={(0,1,2,3),(4,5,6,7)},'reader exact format-specific holes')
        check({tuple(p['base_relative_control_store_offsets']) for p in paths}=={(12,),(16,)},'reader control write selection')
    return {'start':hex(pc),'end_exclusive':hex(pc+size),'bytes':size,'sha256':digest,'instructions':list(n.values()),
        'stores':stores,'calls':calls,'encoded_GPR_writes':writes,'terminal_edges':terminals,'reader_path_projections':paths,
        'conditional_normal_return_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()}}


def footprint(length,index):
    row=0x2000c038+12*index;end_source=23+length;end_dest=3+length
    return {'length':length,'queue_index':index,'source_relative_entry_frame':[23,end_source],
        'source_outside32B_frame':([32,end_source] if end_source>32 else None),
        'destination_relative_row':[3,end_dest],
        'own_tag_in_copy_range':length>=9,
        'next_row_prefix':([0,end_dest-12] if end_dest>12 else None),
        'past_queue_end':([hex(0x2000c1b8),hex(row+end_dest)] if row+end_dest>0x2000c1b8 else None)}


def derive(app,carriers,header,coverage):
    parent=previous.derive(app,carriers,header,coverage)
    bodies={r:body(take(app,p,size),r,p,size,n,stores,h) for r,p,size,n,stores,h in DETAILS}
    check(sum(b['bytes'] for b in bodies.values())==216 and sum(len(b['instructions']) for b in bodies.values())==70
          and sum(len(b['stores']) for b in bodies.values())==16,'peripheral RX body census')
    irq={d['pc']:d for d in bodies['irq']['instructions']};reader={d['pc']:d for d in bodies['reader']['instructions']}
    base=irq[0x12c24]['imm']+irq[0x12c28]['imm'];check(base==0x40006400,'entry absolute I/O base')
    check([c['target'] for c in bodies['irq']['calls']]==['0x18d78','0x12bc8'] and
          parent['bodies']['producer']['start']=='0x12bc8','entry to reader/complete prior producer joins')
    check(irq[0x12c34]['imm']==12 and irq[0x12c3c]['imm']==22 and irq[0x12c40]['imm']==12 and irq[0x12c44]['imm']==23,
          'record R=SP+12, length R+10, ID R+0, source R+11')
    check(reader[0x18da0]['imm']==15 and reader[0x18dac]['imm']==19,'reader length nibble and ninth source byte')
    producer={d['pc']:d for d in parent['bodies']['producer']['instructions']}
    check(producer[0x12c0e]['rs2']==9 and producer[0x12c0e]['imm']==11 and irq[0x12c48]['imm']==0,'post-copy queue tag0 join')
    vector=take(app,0x80c8,4);check(vector.hex()=='242c0100','raw APP vector word to this entry')
    _,rp,rs,rn,rc,rh=boot.DETAILS[0];reset=boot.body(take(app,rp,rs),'reset',rp,rh,rn,rc)
    bn={d['pc']:d for d in reset['instructions']};vectorbase=(0x18710+bn[0x18710]['imm']+bn[0x18714]['imm'])&0xffffffff
    check(vectorbase==0x8038 and (0x80c8-vectorbase)//4==36,'nominal vector-base/word arithmetic')
    return {'schema':'TSL9-peripheral-RX-ingress-static-v1','profile':init.timer.PROFILE,
        'scope':'2 complete APP bodies216B/70instructions/16stores; previous producer/consumer/cache chain revalidated',
        'bodies':bodies,'raw_vector_reference':{'address':'0x80c8','bytes':vector.hex(),'target':'0x12c24',
            'nominal_reset_vector_base':hex(vectorbase),'word_index_relative_base':36,
            'actual_interrupt_number_delivery_or_hardware_context_proved':False},
        'entry_contract':{'gate':'fresh U32[4000640c]&3; zero ->12c54 MRET without frame/callee',
            'active':'entrySP-32=H; reader(40006400,0,H+12); then producer(U16[H+12],H+23,U8[H+22],0)',
            'return':'SP+=32 then12c50 MRET; no ordinary RET, no explicit GPR save/restore or record erasure',
            'reader_status_tested':False,'general_register_or_machine_context_restoration_proved':False},
        'reader_contract':{'inputs':'T=A0,channel=A1,R=A2; D=T+16*full_channel, RV32',
            'fresh_format':'F=fresh U32[D+432]&4 ->SB R+8; chooses branch; ID is a separate fresh U32 read',
            'standard':'fresh U32[D+432]>>21 ->SW R+0; directly writes R0..3, leavesR4..7 untouched',
            'extended':'fresh U32[D+432]>>3 ->SW R+4; directly writes R4..7, leavesR0..3 untouched',
            'common':['fresh U32[D+432]&2 ->R+9','fresh U32[D+436]&15 ->R+10',
                'another fresh U32[D+436]>>8 ->SB R+19','four fresh word reads D+440 ->bytesR+11..14',
                'four fresh word reads D+444 ->bytesR+15..18'],
            'control':'full A1==0: fresh U32[T+12] OR20hex ->same address; otherwise T+16; not a physical acknowledge-success claim',
            'context':'only A4/A5 encoded writes, no frame/callees or direct R-pointer value store; A0/A1/A2 remain values but do not establish lifetime'},
        'caller_record_projection':{'R':'H+12, full direct record store domain inside H+12..31',
            'standard_ID':'U16[R] from local U32 standard store ->0..2047, if no adverse alias/writer',
            'extended_ID':'caller still reads U16[R0]; not directly initialized by extended path, prior contents unknown',
            'length':'fresh-derived low nibble0..15; entry no length clamp; full count forwarded to producer',
            'source':'H+23..31 includes8 payload bytes plus separately stored R+19, not merely8 initialized bytes'},
        'reference_copy_footprints':[footprint(n,i) for i in (0,31) for n in range(16)],
        'footprint_boundaries':{'length9':'copy includesR+19 ->own queue tag, overwritten by post-copy SB0 under intact context',
            'length10_to15':'source reaches H+32..37 outside this32B frame; destination reaches next row offsets0..5',
            'last_queue_slot':'row31 starts2000c1ac; next row at2000c1b8 is cachetable row0; maxcopy ends2000c1be, does not directly reach row18 O2000c290',
            'conditional_only':'intervals do not prove real length reachability, valid outside-frame data, copy completion, corruption or fault'},
        'conditional_cache_bridge':{'requirements':['active entry and valid selected frame/I/O/record accesses',
            'actual reference copy, valid full source ranges, intact context, no adverse aliases/IRQ/other writers',
            'nonzero consumer ID, complete snapshot, filter reply0, configbit3 clear, probe replynonzero, mode1 and resampledID1657'],
            'fields':'cacheO length0..15, tag0 under these premises; ID1657 standard numeric witness cf200000>>21=1657 is not observed input',
            'extended_ID1657':'not determined by reader ID+4 store; depends on prior R0 contents/other evidence',
            'later_dispatch':'unchanged tag0 chooses untagged12a08 path, not16b7c; length0 can fail prior C6a8 nonzero gate',
            'later_copy_domain':'untagged O+3 length9 includes O+11; length10..15 includes adjacent config first1..6 bytes; outside-object access validity unproved'},
        'lifetime':'R/H+23 may be observed through resident copy source; entry releases32B frame without erase, no provider nonretention proof',
        'premises':['matching bytes and conditional ISA; valid nonwrapping/aligned accesses and preserved code/context',
            'fresh MMIO words remain separate snapshots; record/MMIO/frame alias and asynchronous effects not ignored',
            'MRET encoded control exit is not a general C ABI or automatic GPR restoration proof',
            'raw vector arithmetic is not installed delivery/ROM/provider identity or a physical peripheral feature proof'],
        'remaining_boundaries':['actual vector/interrupt context and callers','actual copy binding/retention and concurrent writers',
            'extended-path prior stack ID provenance','physical repeated-read/control semantics and object lifetime'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(app):
    for raw in range(256):check(raw&15==raw%16,'length nibble is modulo not8byte cap')
    for ident in range(2048):
        for low in (0,(1<<21)-1,1,1<<20):
            w=(ident<<21)|low;check(w>>21==ident,'standard ID field projection')
    check(0xcf200000>>21==1657 and not 0xcf200000&4,'standard numeric ID1657 witness')
    for index in range(32):
        for length in range(16):
            f=footprint(length,index)
            check(bool(f['source_outside32B_frame'])==(length>=10),'source frame threshold')
            check(bool(f['next_row_prefix'])==(length>=10) and f['own_tag_in_copy_range']==(length>=9),'destination row/tag thresholds')
            check(bool(f['past_queue_end'])==(index==31 and length>=10),'lastslot cachetable boundary')
            check(0x2000c038+12*index+3+length<0x2000c290,'copy range does not directly reach row18')
    for first in (0,4):
        for second in (0,0xffffffff,0xcf200000):
            check((first!=0)==(first==4),'independent format input domain')
            check(second>>21<=2047 and second>>3<=0x1fffffff,'independent ID read projections')
    roles={r:(p,size,count,stores,h) for r,p,size,count,stores,h in DETAILS}
    cases=(('irq',0,1<<12),('irq',10,4),('irq',12,0x80),('irq',16,4),('irq',18,4),('irq',24,1<<20),
        ('irq',28,1<<20),('irq',36,4),('irq',44,1<<20),('reader',10,4),('reader',24,4),
        ('reader',42,1<<20),('reader',52,1<<20),('reader',70,1<<7),('reader',122,1<<20),
        ('reader',132,0x80),('reader',140,4),('reader',150,4))
    for role,off,flip in cases:
        pc,size,count,stores,digest=roles[role];raw=bytearray(take(app,pc,size));w=decode(raw,pc)[pc+off]['size']
        raw[off:off+w]=(int.from_bytes(raw[off:off+w],'little')^flip).to_bytes(w,'little')
        try:body(raw,role,pc,size,count,stores,digest)
        except RuntimeError as e:check(str(e)=='peripheral RX '+role+' instruction '+hex(off),'unexpected peripheral RX mutation guard '+str(e))
        else:raise RuntimeError('peripheral RX mutation escaped')
    print('PASS: 256 length-byte +8192 standard-ID cases; 512 queue/source footprints; 4 reader path projections; 18 specified raw mutations')


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
    tests(app);output=(json.dumps(ledger,indent=1,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'peripheral RX exact ledger replay')
    print('PASS: 2 complete APP bodies216B/70instructions/16stores; MRET/RET, format-specific writes, queue/cache interval joins')
    print('PASS: exact ledger bytes; NO target execution; actual interrupt context/provider/retention/physical MMIO UNPROVED')


if __name__=='__main__':main()
