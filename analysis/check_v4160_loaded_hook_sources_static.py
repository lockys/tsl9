"""Two loaded hook sources, source publishers and alternate table registrar.

Decode original operands/CFG and host address/predicate arithmetic only.
No target ISA, RAM/frame, callback, CSR, resident or hardware execution/model.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_hook_callers_flag_static as previous

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-loaded-hook-sources-static.json')
DETAILS=(
 (0x412ae,0x41326,0x41336,1276,1268,-1440,0x43b28,456,
  0x5a004,0x60856,0x58ef2,1464,0x61b1c,0x55bde,952,-1894,-1570,564,
  ('0c2d65f2467a04eb0793ee435f580acd9d55b1253fdb24190372fa78a05df48e',
   'ba17d15bf22fc79b003a69fa6fa77da26b2459218dbe9b01247926161abea8b9',
   'fe135666880c1572e6361296b3ba7efa2a590cc98d998e3c6783084bac3bfd7c',
   '77044505f84c5b3b31f3b89512595f456891e9586ec6af891b5fd9363829a818',
   'd8c78551f407222f6fa44d31f65f1e900e9587d2223b3c6c0f74c1de4c4447e0',
   'ed21d79f478408a77e4d50d6bff6a7122aad846e9889b8b6dcaad31d5b43b242')),
 (0x412ee,0x41366,0x41376,1356,1348,-1300,0x43bb4,536,
  0x5a14c,0x60940,0x5903a,1792,0x61c06,0x55d1e,1032,-1660,-1336,798,
  ('33bc4a6e89359e375cc665174b000642c5abd970dc1fe8392ceada84101c247c',
   'bf8396a30874b0e80b1e836799caf84470c94f2179c71f0ae5c4707fe2330b45',
   '985a6de7ec1087edbc5932116fb2cc505ae6656559b2e5da980125b93c5d3315',
   'e24abd28f67967c11109d15d85fcf9c9b3ba6bb7a341fb9e6d5ff9998bb29474',
   '827e861ae5bf02dd02ca0250893d4ec29bff806ce719d6b894174dc91be5655c',
   '63c24ba47085e5d747402a9138c9e5257bc408c847e4141bc645df7f87eab093')))
ROLES=('flow','alternative','bypass','registrar','publish_alternative','publish_primary')
SIZES=(34,16,12,22,34,62)
COUNTS=(11,5,4,8,11,18)


def specs(role,pc,a):
    s={}
    def e(o,op,**f):s[pc+o]=dict(op=op,**f)
    def lui(o,r,v):e(o,'lui',rd=r,imm=v)
    def addi(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def load(o,r,b,v,w=4,**f):e(o,'load',rd=r,rs1=b,imm=v,width=w,**f)
    def store(o,r,b,v,w=4,**f):e(o,'store',rs2=r,rs1=b,imm=v,width=w,**f)
    def qload(o,r,b,v):load(o,r,b,v,1,mnemonic='qk.c.lbu')
    def qstore(o,r,b,v):store(o,r,b,v,1,mnemonic='qk.c.sb')
    if role=='flow':
        primary,alt,bypass,setter=a
        store(0,8,19,164);qload(4,14,8,11);e(6,'li',rd=15,imm=1);e(8,'bne',rs1=14,rs2=15,target=alt)
        addi(12,15,0,-48);qstore(16,15,8,14);lui(18,15,0x20003000);load(22,10,15,primary)
        qload(26,15,9,12);e(28,'beqz',rs1=15,target=bypass);e(30,'jal',rd=1,target=setter)
    elif role=='alternative':
        delta,join=a;addi(0,15,0,-63);qstore(4,15,8,14);lui(6,15,0x20003000);load(10,10,15,delta);e(14,'jump',target=join)
    elif role=='bypass':
        low,join=a;e(0,'li',rd=11,imm=0);e(2,'auipc',rd=1,imm=0xe0043000);e(6,'jalr',rd=1,rs1=1,imm=low);e(10,'jump',target=join)
    elif role=='registrar':
        delta=a;e(0,'li',rd=15,imm=4);e(2,'bltu',rs1=15,rs2=11,target=pc+20);lui(6,15,0x20003000)
        e(10,'slli',rd=11,rs1=11,imm=2);addi(12,15,15,delta);e(16,'add',rd=11,rs1=11,rs2=15);store(18,10,11,0);e(20,'jr',rs1=1)
    elif role=='publish_alternative':
        c1,c2,value_low,slot=a;addi(0,2,2,-16);store(2,1,2,12);e(4,'jal',rd=1,target=c1);e(8,'jal',rd=1,target=c2)
        load(12,1,2,12);lui(14,15,0x59000);lui(18,14,0x20003000);addi(22,15,15,value_low);store(26,15,14,slot)
        addi(30,2,2,16);e(32,'jr',rs1=1)
    elif role=='publish_primary':
        callee,base,low1,low2,main,slot=a;addi(0,2,2,-16);store(2,1,2,12);e(4,'jal',rd=1,target=callee)
        lui(8,15,0x20003000);lui(12,14,0x61000);addi(16,15,15,base);addi(20,14,14,low1);store(24,14,15,184)
        lui(28,14,0x61000);addi(32,14,14,low2);store(36,14,15,188);load(40,1,2,12)
        lui(42,15,0x61000);lui(46,14,0x20003000);addi(50,15,15,main);store(54,15,14,slot);addi(58,2,2,16);e(60,'jr',rs1=1)
    else:raise RuntimeError('unknown loaded hook role')
    return s


def body(raw,role,pc,args,digest):
    n=decode(raw,pc);s=specs(role,pc,args);check(set(n)==set(s),'loaded hook boundaries '+role)
    for p,f in s.items():init.g(n,p,'loaded hook '+role+' operand '+hex(p-pc),**f)
    j=ROLES.index(role);check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[j],COUNTS[j],digest),'loaded hook full window identity')
    edges={};cuts=[];calls=[]
    for p,d in n.items():
        if d['op']=='jr':qs=[]
        elif d['op']=='jump':qs=[d['target']]
        elif d['op'] in ('bne','beqz','bltu'):qs=[p+d['size'],d['target']]
        else:qs=[p+d['size']]
        for q in qs:
            if q not in n:
                check(role in ('flow','alternative','bypass'),'only explicit loaded-hook bounded cuts');cuts.append(hex(q))
        edges[p]=qs
        if d['op'] in ('jal','jalr'):calls.append({'pc':hex(p),'link':hex(p+d['size']),
            'target':hex(d['target']) if 'target' in d else hex((pc+2+0xe0043000+d['imm'])&0xfffffffe),
            'normal_return_and_preservation_proved':False})
    return {'start':hex(pc),'end_exclusive':hex(pc+len(raw)),'bytes':len(raw),'sha256':digest,'instructions':list(n.values()),
        'conditional_normal_return_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},'cuts':cuts,'calls':calls,
        'complete_function':role not in ('flow','alternative','bypass')}


def views(d,shift,setter):
    f,a,b,primary,alternative,low,registrar,table,palt,c1,c2,vlow,pprimary,c3,base,l1,l2,main,hashes=d
    return ((f,shift,('flow'),(primary,a+shift,b+shift,setter)),
        (a,shift,'alternative',(alternative,f+shift+26)),(b,shift,'bypass',(low,f+shift+34)),
        (registrar,0,'registrar',table),(palt,0,'publish_alternative',(c1,c2,vlow,alternative)),
        (pprimary,0,'publish_primary',(c3,base,l1,l2,main,primary)))


def derive(app,carriers,header,coverage):
    parent=previous.derive(app,carriers,header,coverage);profiles=[]
    for i,(data,d) in enumerate(zip(carriers,DETAILS)):
        p=parent['profiles'][i];shift=int(p['mapping_shift'],16);setter=int(p['setter'],16);dviews=views(d,shift,setter);bodies={}
        for j,(source,offset,role,args) in enumerate(dviews):
            raw=init.binding.take(data,source,SIZES[j]);bodies[role]=body(raw,role,source+offset,args,d[-1][j])
        # Re-pin copied instruction targets at original FLASH coordinates too.
        for j,(source,offset,role,args) in enumerate(views(d,0,previous.previous.DETAILS[i][0])):
            if j<3:body(init.binding.take(data,source,SIZES[j]),role,source,args,d[-1][j])
        f,a,b,primary,alternative,low,registrar,table,palt,c1,c2,vlow,pprimary,c3,base,l1,l2,main,_=d
        check(bodies['bypass']['calls'][0]['target']==hex(registrar),'mapped bypass call joins separate table registrar')
        check(bodies['flow']['calls'][0]['target']==hex(setter),'mapped loaded call joins hook setter')
        check(0x20003000+primary!=0x20003000+alternative and 0x20003000+table!=int(p['hook_slot'],16),'distinct source/table/hook slots')
        nodes={x['pc']:x for r in ('flow','alternative','bypass') for x in bodies[r]['instructions']}
        edges={int(k,16):[int(q,16) for q in qs] for r in ('flow','alternative','bypass') for k,qs in bodies[r]['conditional_normal_return_CFG'].items()}
        cut=f+shift+34;check({q for qs in edges.values() for q in qs if q not in nodes}=={cut},'one selected flow continuation cut')
        seen=set()
        def visit(pc):
            if pc not in nodes or pc in seen:return
            seen.add(pc)
            for q in edges[pc]:visit(q)
        visit(f+shift);check(seen==set(nodes),'two source paths and bypass all locally reachable')
        profiles.append({'label':p['label'],'mapping_shift':hex(shift),'flash_windows':{r:hex(src) for src,o,r,args in dviews},
            'bodies':bodies,'primary_source_slot':hex(0x20003000+primary),'alternative_source_slot':hex(0x20003000+alternative),
            'primary_published_pointer':hex(0x61000+main),'alternative_published_pointer':hex(0x59000+vlow),
            'primary_additional_publications':[{'address':hex(0x20003000+base+184),'value':hex(0x61000+l1)},
                {'address':hex(0x20003000+base+188),'value':hex(0x61000+l2)}],
            'hook_slot':p['hook_slot'],'flag':p['flag'],'bypass_index0_slot':hex(0x20003000+table),
            'joined_flow_CFG':{hex(k):[hex(q) for q in qs] for k,qs in edges.items()},'only_local_continuation_cut':hex(cut),
            'actual_installed_binding_or_registration_order_proved':False})
    check(sum(b['bytes'] for p in profiles for b in p['bodies'].values())==360,'loaded hook byte census')
    check(sum(len(b['instructions']) for p in profiles for b in p['bodies'].values())==114,'loaded hook instruction census')
    return {'schema':'TSL9-loaded-hook-sources-static-v1','profile':parent['profile'],'profiles':profiles,
        'scope':'6 bounded flow pieces124B/40instructions +4 complete publishers192B/58instructions +2 complete registrars44B/16instructions',
        'selection_contract':{'first_store':'SW then-live S0 to[then-live S3+164]; object/alias context unproved',
            'selector':'fresh U8[S0+11]==1 ->write low8(-48)=208 to[S0+14],load primary slot toA0',
            'other_selector':'write low8(-63)=193 to[S0+14],load alternative slot toA0; jump to shared byte gate',
            'shared_gate':'QK.C.LBU A5,[S1+12] leaves A0 unchanged; nonzero ->hook setter; zero ->bypass with A1=0',
            'no_A0_null_guard':True,'shared_cut':'after either selected call normally returns, control joins flow end; later continuation unproved'},
        'publication_contract':'source publishers store fixed raw pointers after earlier direct callees normally return; no source load value guaranteed without order/preservation',
        'bypass_contract':{'index':'registrar accepts unsigned A1<=4, SW A0 to table_base+4*A1; otherwise no local table store',
            'selected_call':'A1=0 selects first table word; this table differs from hook slot; no direct hook/flag store in registrar',
            'callback_execution_or_ownership_proved':False},
        'premises':['matching installed candidate and preserved completed first-copy code; valid Xwchc conditional ISA and data accesses',
            'then-live S0/S1/S3 and any object/alias state valid; selectors and slot values may change between accesses',
            'publisher earlier callees and flow calls must return normally with required SP/RA/saved words/context preserved',
            'fixed publication only implies later loaded pointer if publication occurred first and no intervening writer changed it'],
        'remaining':['actual callback bodies595b8/59700 and61234/6131e','complete RAMcallback20000d50 arithmetic/loops/continuations',
            'source publication callers/order and other writers','installed provider, ECALL route, object/frame/payload lifetime'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    check(init.timer.encode('lbu',15,9,12)==0x24dc and init.timer.encode('lbu',14,8,11)==0x3438
          and init.timer.encode('sb',15,8,14)==0xa47c,'official Xwchc fields for critical gate/selector/store')
    counts=[0,0,0]
    for selector in range(256):
        for gate in range(256):counts[2 if gate==0 else 0 if selector==1 else 1]+=1
    check(counts==[255,65025,256],'two byte selector/gate partitions')
    for delta in (456,536):
        addresses=[0x20003000+delta+(x<<2) for x in range(5)]
        check(len(set(addresses))==5 and addresses[-1]-addresses[0]==16,'five valid registrar word positions')
        check(all(x>4 for x in (5,255,0x7fffffff,0x80000000,0xffffffff)),'unsigned invalid index boundary cases')
    changes=(((4,4),(8,1<<12),(16,4),(22,1<<20),(26,4),(28,4),(30,1<<20)),
        ((4,4),(10,1<<20),(14,4)),((0,4),(2,1<<12),(6,1<<20)),
        ((0,4),(2,1<<12),(12,1<<20),(18,4)),
        ((4,1<<20),(8,1<<20),(22,1<<20),(26,1<<20)),
        ((4,1<<20),(16,1<<20),(24,1<<20),(46,1<<12),(54,1<<20)))
    count=0
    for i,(data,d) in enumerate(zip(carriers,DETAILS)):
        for j,(source,offset,role,args) in enumerate(views(d,0,previous.previous.DETAILS[i][0])):
            raw=init.binding.take(data,source,SIZES[j])
            for off,flip in changes[j]:
                b=bytearray(raw);n=decode(raw,source)[source+off]['size'];b[off:off+n]=(int.from_bytes(b[off:off+n],'little')^flip).to_bytes(n,'little')
                try:body(b,role,source,args,d[-1][j])
                except RuntimeError as e:check(str(e)=='loaded hook '+role+' operand '+hex(off),'specific loaded hook mutation guard '+str(e))
                else:raise RuntimeError('loaded hook mutation escaped')
                count+=1
    check(count==52,'loaded hook mutation census')
    print('PASS: critical official Xwchc encodings; 65536 selector/gate cases; 5 registrar positions; 52 specified mutations rejected')


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
    else:check(OUT.read_bytes()==output,'loaded hook sources exact ledger replay')
    print('PASS: 360B/114instructions; 6 bounded flow pieces +6 complete functions; source slots/publishers and distinct table registrar joined')
    print('PASS: exact ledger; NO target execution; installed binding/publication order/actual callback lifetime UNPROVED')


if __name__=='__main__':main()
