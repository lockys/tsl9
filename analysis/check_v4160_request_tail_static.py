"""Offline prepare, stack normalization, tail adapter and notification contract.

Original bytes/operands, conditional CFG and integer/interval certificates only.
No target ISA execution/emulation, mutable register/RAM model or provider model.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_request_consumers_static as previous

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-request-tail-static.json')
PARTS=('prepare','wrapper','adapter','notify_stub','notify')
STARTS=((0x45612,0x533ce,0x679ce,0x6a70c,0x52f96),(0x456aa,0x5347c,0x67b0c,0x6a8f0,0x5303e))
SIZES=(62,70,96,4,98)
COUNTS=(24,25,33,1,39)
HASHES=(('0806ce9cbd8477d55f3b0858ce03f575462b0cf4da67dfb8ed1773bb8aba2382','b179cc29878f5a02db2601daf26e8cdfc7a7b94a5567b0077882758ada49a5d9','bf657a5e5f331748b41863f05d06fa774dd76eb586a0df79f2188c3eab6d3753','64070a07d0e599d5709054d218ae7d38b2648440662c4a360195d3d419e37e32','ec52c8473420e9edfa553fa16fd396d65cbc493e77c1f845437f951138d80e22'),
 ('0806ce9cbd8477d55f3b0858ce03f575462b0cf4da67dfb8ed1773bb8aba2382','d5784d793ad6e2dfee1aa9b528cd9caf97e44775b06d45c75b970c117fd8e14c','f789cc995ad8d05158b3d27a0eda8f24a19ffa2c200e8e4183ad3d88a79e5157','eaaf9ed68533165c1e98ddc81fd15eda912941c397d64c0ea47a97dad7ba3685','074529d72daeb6a82b137b388ed16e2dab603bd5c8dffd54d0f8800e87df41d9'))


def specs(part,index):
    pc=STARTS[index][PARTS.index(part)];s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def ai(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def li(o,r,v):e(o,'li',rd=r,imm=v)
    def ld(o,r,b,v,w=4,**f):e(o,'load',rd=r,rs1=b,imm=v,width=w,**f)
    def st(o,r,b,v,w=4):e(o,'store',rs2=r,rs1=b,imm=v,width=w)
    def mv(o,r,b):e(o,'mv',rd=r,rs2=b)
    def imm(o,op,r,b,v):e(o,op,rd=r,rs1=b,imm=v)
    def bz(o,r,t):e(o,'beqz',rs1=r,target=pc+t)
    def br(o,a,b,t):e(o,'bne',rs1=a,rs2=b,target=pc+t)
    def j(o,t):e(o,'jump',target=pc+t)
    def call(o,t):e(o,'jal',rd=1,target=t)
    def tail(o,t):e(o,'jal',rd=0,target=t)
    def ret(o):e(o,'jr',rs1=1)
    if part=='prepare':
        li(0,15,0);bz(2,11,22);bz(4,10,22);li(6,15,1);br(8,10,15,26);ld(12,15,11,5,1);imm(14,'ori',15,15,-64);st(18,15,11,5,1);li(20,15,1);mv(22,10,15);ret(24)
        li(26,15,2);br(28,10,15,40);ld(32,15,11,5,1);imm(34,'andi',15,15,63);j(38,18);li(40,14,3);li(42,15,1);br(44,10,14,22)
        ld(48,14,11,5,1);imm(50,'andi',14,14,63);imm(54,'ori',14,14,64);st(58,14,11,5,1);j(60,22)
    elif part=='wrapper':
        ai(0,2,2,-16);st(2,8,2,12);ld(4,8,2,44,1);st(8,9,2,8);ld(10,9,2,48,1)
        for o,r,v in ((14,6,16),(18,28,20),(22,29,24),(26,30,28),(30,31,32),(34,5,36),(38,7,40)):
            ld(o,r,2,v,1,**({'signed':True} if o==18 else {}))
        st(42,8,2,44);ld(44,8,2,12);st(46,9,2,48);ld(48,9,2,8)
        for o,r,v in ((50,7,40),(52,5,36),(54,31,32),(56,30,28),(58,29,24),(60,28,20),(62,6,16)):st(o,r,2,v)
        ai(64,2,2,16);tail(66,STARTS[index][2])
    elif part=='adapter':
        ai(0,2,2,-80);ai(2,6,2,61);st(6,6,2,36);ld(8,6,2,112,1);st(12,1,2,76);st(14,6,2,32)
        for o,v in ((16,108),(22,104),(28,100),(34,96),(40,92),(46,88),(52,84),(58,80)):
            ld(o,6,2,v,1,**({'signed':True} if o==52 else {}));st(o+4,6,2,v-80)
        call(64,0x68bb4+318*index);st(68,10,2,60,1);e(72,'lui',rd=10,imm=0x2000);ai(74,12,2,60);ai(76,10,10,54);li(80,11,2);call(82,STARTS[index][3]);ld(86,1,2,76);ld(88,10,2,60,1);ai(92,2,2,80);ret(94)
    elif part=='notify_stub':tail(0,STARTS[index][4])
    else:
        ai(0,2,2,-32);st(2,9,2,20);mv(4,9,11);st(6,18,2,16);mv(8,18,10);ai(10,10,9,12);st(14,1,2,28);st(16,8,2,24);st(18,12,2,12)
        e(20,'auipc',rd=1,imm=0x1ffad000);e(24,'jalr',rd=1,rs1=1,imm=652-168*index);bz(28,10,86);e(30,'lui',rd=15,imm=0x1000);ai(32,15,15,-367);ld(36,11,2,12)
        st(38,15,10,0,2);st(40,9,10,2,1);st(42,18,10,4,2);mv(46,8,10);ai(48,10,10,12);st(50,10,8,8);mv(52,12,9)
        e(54,'auipc',rd=1,imm=0x1ffad000);e(58,'jalr',rd=1,rs1=1,imm=870-168*index);mv(62,11,8);e(64,'lui',rd=15,imm=0x20003000)
        for o,r,v in ((68,8,24),(70,1,28),(72,9,20),(74,18,16)):ld(o,r,2,v)
        ld(76,10,15,940+80*index,1);ai(80,2,2,32);tail(82,0x43208+140*index)
        for o,r,v in ((86,1,28),(88,8,24),(90,9,20),(92,18,16)):ld(o,r,2,v)
        ai(94,2,2,32);ret(96)
    return s


def body(raw,part,index):
    k=PARTS.index(part);pc=STARTS[index][k];s=specs(part,index);n=decode(raw,pc)
    check(set(n)==set(s),'tail '+part+' boundaries')
    for p,f in s.items():init.g(n,p,'tail '+part+' operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[k],HASHES[index][k]),'tail '+part+' identity')
    edges={};calls=[];tails=[]
    for p,d in n.items():
        op=d['op'];q=[p+d['size']]
        if op=='jr':check(d['rs1']==1,'tail returnRA');q=[]
        elif op in ('beqz','bne'):q.append(d['target'])
        elif op=='jump':q=[d['target']]
        elif op in ('jal','jalr'):
            if op=='jal':t=d['target']
            else:
                a=n[p-4];check(a['op']=='auipc' and a['rd']==d['rs1'],'tail PC pair');t=(p-4+a['imm']+d['imm'])&0xfffffffe
            row={'pc':hex(p),'target':hex(t),'link':d['rd']}
            if d['rd']==0:tails.append(row);q=[]
            else:check(d['rd']==1,'tail callRA');calls.append(row)
        check(all(v in n for v in q),'tail '+part+' closedCFG');edges[p]=q
    seen=set();active=set()
    def visit(p):
        check(p not in active,'tail '+part+' acyclic')
        if p in seen:return
        active.add(p)
        for q in edges[p]:visit(q)
        active.remove(p);seen.add(p)
    visit(pc);check(seen==set(n),'tail '+part+' all nodes locally reachable')
    stores=[v for v in n.values() if v['op']=='store'];check((len(calls),len(tails),len(stores))==((0,0,2),(0,1,11),(2,0,12),(0,1,0),(2,1,9))[k],'tail '+part+' call/tail/store census')
    if part in ('wrapper','adapter'):check(all(v['rs1']==2 for v in stores),'tail only frame-base stores')
    if part=='wrapper':check(all(v.get('rd') not in range(10,18) and v.get('rd')!=1 for v in n.values()),'tail wrapper A0-A7 andRA unmodified')
    return {'start':hex(pc),'end_exclusive':hex(pc+SIZES[k]),'bytes':SIZES[k],'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),
            'calls':calls,'tails':tails,'store_count':len(stores),'conditional_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},'complete_local_body':True,'local_CFG_acyclic':True}


def certificates(b,part):
    pc=int(b['start'],16);e={int(p,16):[int(q,16) for q in qs] for p,qs in b['conditional_CFG'].items()}
    if part=='prepare':cases={'null_pointer':{2:22},'mode0':{2:4,4:22},'mode1':{2:4,4:6,8:12},'mode2':{2:4,4:6,8:26,28:32},'mode3':{2:4,4:6,8:26,28:40,44:48},'other_mode':{2:4,4:6,8:26,28:40,44:22}}
    elif part=='notify':cases={'allocation_null':{28:86},'allocation_nonnull':{28:30}}
    else:cases={'complete_local_chain':{}}
    return {name:previous.previous.previous.paths.chain(e,pc,{pc+p:pc+q for p,q in c.items()}) for name,c in cases.items()}


def domains():
    counts={'return0':0,'return1':0,'write':0};examples=[]
    for mode in range(256):
        for old in range(256):
            new=(old|192) if mode==1 else (old&63) if mode==2 else ((old&63)|64) if mode==3 else old
            check(new&63==old&63,'tail low6 preservation')
            counts['return0' if mode==0 else 'return1']+=1;counts['write']+=int(mode in (1,2,3))
        if mode<5:examples.append({'mode':mode,'reply_nonnull':int(mode!=0),'write':mode in (1,2,3),'low6_preserved':True})
    check(counts=={'return0':256,'return1':65280,'write':768},'tail byte-mode domain census')
    for b in range(256):
        signed=b-256 if b&128 else b
        check((((signed&0xffffffff)<<24&0xffffffff)^0x80000000)-0x80000000>>24==signed,'tail signed byte normalization identity')
        check((b&255)==b,'tail unsigned byte normalization identity')
    wrapper=[];adapter=[]
    for k in range(9):
        wrapper.append({'caller_word_offset':4*k,'wrapper_load_offset':16+4*k,'wrapper_store_offset':16+4*k,'signed':k==1})
        adapter.append({'caller_word_offset':4*k,'adapter_load_offset':80+4*k,'adapter_outgoing_word_offset':4*k,'signed':k==1})
    check(all(v['wrapper_store_offset']-16==v['caller_word_offset'] for v in wrapper),'tail wrapper writes caller arguments')
    check(all(0<=v['adapter_outgoing_word_offset']<=32 and v['adapter_load_offset']>=80 for v in adapter),'tail adapter disjoint incoming/outgoing intervals')
    check(40<=60<61<76 and 76+4==80,'tail outgoing0..39, payload60..61 andRA76..79 disjoint')
    return {'mode_byte_pairs':65536,'counts':counts,'mode_examples':examples,'null_pointer_reply':0,
            'full32_mode_note':'only exact1/2/3 mutate; any other nonzero full32 mode with nonnull pointer returns1 withoutstore',
            'wrapper_stack_translation':wrapper,'adapter_stack_translation':adapter,'normalization_cases':256,
            'unchanged_low6_source_gap':'when pointer=P0+4,prepare modifiesP0+9 high2bits only; low6 still depend on prior copy/source'}


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[]
    for i,(data,pr) in enumerate(zip(carriers,parent['profiles'])):
        windows={part:body(init.binding.take(data,STARTS[i][k],SIZES[k]),part,i) for k,part in enumerate(PARTS)}
        certs={part:certificates(b,part) for part,b in windows.items()};check(sum(map(len,certs.values()))==11,'tail11 selected paths/profile')
        check(pr['fallback']['prepare_call']['target']==windows['prepare']['start'] and pr['fallback']['final_call']['target']==windows['wrapper']['start'],'tail joins published fallback calls')
        check(windows['wrapper']['tails'][0]['target']==windows['adapter']['start'] and windows['adapter']['calls'][1]['target']==windows['notify_stub']['start'] and windows['notify_stub']['tails'][0]['target']==windows['notify']['start'],'tail wrapper-adapter-stub-notify target joins')
        check([c['target'] for c in windows['notify']['calls']]==['0x20000236','0x20000332'],'tail notifier allocator/copy exact PC targets')
        ap=STARTS[i][2];an={v['pc']:v for v in windows['adapter']['instructions']}
        check(an[ap+2]['imm']==61 and an[ap+6]['imm']==36 and an[ap+68]['imm']==60,'tail tenth stackargSP61 and statusbyteSP60')
        check([v['imm'] for v in an.values() if v['op']=='store' and v['width']==1]==[60],'tail no local initializeSP61')
        wp=STARTS[i][1];wn={v['pc']:v for v in windows['wrapper']['instructions']};check([(wn[wp+o]['imm'],wn[wp+o].get('signed',False)) for o in (14,18,22,26,30,34,38,4,10)]==[(16,False),(20,True),(24,False),(28,False),(32,False),(36,False),(40,False),(44,False),(48,False)],'tail exact wrapper nine byte read widths/signs')
        profiles.append({'label':pr['label'],'bodies':windows,'selected_CFG_paths':certs,
            'prepare':{'entry':['fullmodeA0','pointerA1'],'null_pointer_or_mode0':'return0, no dereference/store',
                'mode1':'U8[pointer+5] |= c0','mode2':'U8[pointer+5] &= 3f','mode3':'U8[pointer+5]=(old&3f)|40',
                'other_nonzero_mode':'return1 withoutdereference/store','nonnull_nonzero_reply':1,'frame_bytes':0,'calls':0,
                'upstream_effect':'with P0+4 argument,modifies P0+9; mode isU8[P0+3]. Low6 origin remains unknown; slot/object stability still premise'},
            'wrapper':{'frame_bytes':16,'saved_and_restored':['S0','S1'],'A0_A7_RA_unchanged':True,'nine_stack_words':'rewrites original callerSP+0..32 as unsignedlow8 except signedlow8 at+4',
                'tail':'SP restored thenJAL rd0 toadapter; RA from originalfallbackcall preserved','pointerA7':'passed unchanged; wrapper does not dereference or explicitly retain it'},
            'adapter':{'frame_bytes':80,'saved':['RA'],'input_registers_forwarded':'A0-A7 unchanged before firstcall',
                'core_target':windows['adapter']['calls'][0]['target'],'core_stack_arguments':'nine normalized input words atSP0..32 plus tenthwordSP36=&SP61;18 total register/stack positions, prototype not proved',
                'output_SP61':'not locally initialized beforecore; actual output/extent/retention requires core contract',
                'aftercore':'SB coreA0 low8 toSP60; notification(2036hex,2,SP60)',
                'notification':'statusSP60 and borrowedSP61 are requested as two sourcebytes; no proof of SP61 initialization yet',
                'return':'fresh U8[SP60] after notification returns, not fullcoreA0; equality tooriginalcorelow8 requires preservation/nonalias premises'},
            'notification':{'stub':'rd0 tail tobody, preserves originalRA','frame_bytes':32,'saved':['RA','S0','S1','S2'],
                'entry':['codeA0','full32lengthA1','borrowedsourceA2'],'allocation_target':'0x20000236','allocation_A0':'length+12 modulo2^32; this callerlength2 ->14',
                'null_allocation':'returnactualnullA0=0 withoutcopy/delivery','nonnull_layout':{'SH_at0':'0e91','SB_at2':'low8(length)','SH_at4':'low16(code)','SW_at8':'N+12'},
                'copy':{'target':'0x20000332','args':['N+12','original borrowedsource','full32length']},
                'delivery_tail':{'target':hex(0x43208+140*i),'args':['freshU8['+hex(0x20003000+80*i+940)+']','original N'],'SP_restored_before_tail':True},
                'unwritten_header_bytes':[3,6,7],'limits':'valid allocation extent and synchronous copy outputs/nonretention, delivery ownership/success, source lifetime, pointer/frame/nonalias preservation unproved'},
            'actual_installed_bindings_proved':False,'target_execution_or_emulation':False})
    return {'schema':'TSL9-request-tail-static-v1','profile':parent['profile'],'APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'integer_domains':domains(),
            'scope':'two full62Bprepare/70Bwrapper/96Badapter/4Bstub/98Bnotify bodies;660 originalbytes/244instructions;22selectedCFGpaths',
            'boundary':'local prepare/stack normalization/notification contracts only; core68bb4/68cf2, outputSP61, provider binding and retention remain unproved',
            'remaining':['core68bb4/68cf2 outputSP61 and A7/stack retention','20000236/20000332/43208 actual providers and message lifetime','source writers and enumerators/missingROMpattern'],
            'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    count=paths=0
    for i,data in enumerate(carriers):
        for k,part in enumerate(PARTS):
            pc=STARTS[i][k];raw=init.binding.take(data,pc,SIZES[k]);b=body(raw,part,i);paths+=len(certificates(b,part))
            for p,d in decode(raw,pc).items():
                at=p-pc;z=d['size'];buf=bytearray(raw);buf[at:at+z]=(int.from_bytes(buf[at:at+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
                try:body(buf,part,i)
                except RuntimeError as e:check(str(e).startswith('tail '+part+' operand '),'tail specified mutation '+str(e))
                else:raise RuntimeError('tail mutation escaped')
                count+=1
    check((count,paths)==(244,22) and sum(SIZES)*2==660,'tail mutation/path/byte census');domains()
    print('PASS:244 operand mutations rejected;660 original bytes;22 CFG certificates;65536 mode/byte cases;256 signed/unsigned normalization cases')


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
    else:check(OUT.read_bytes()==output,'tail exact ledger replay')
    print('PASS:prepareP9/low6 origin, stack tail joins, two-byte notification and freshbyte return;exact ledger')
    print('PASS:NO target execution/emulation;core/outputSP61/provider/retention UNPROVED')


if __name__=='__main__':main()
