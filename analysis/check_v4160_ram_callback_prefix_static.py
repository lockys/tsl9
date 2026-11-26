"""Mapped callback prefix and first conditional call/fixup graph.

Exact original operands/CFG plus host integer/address arithmetic only.
No target ISA, callback, RAM/frame, CSR, resident or hardware execution/model.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_loaded_hook_sources_static as previous

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-ram-callback-prefix-static.json')
MASK=0xffffffff
DETAILS=((0x40fc0,952,564,480,
 ('ef4777186c30e11cc321d60304bd8c66e65518db9953a420b70f8bfd5f6b27c2',
  'b09bbae91930005a32ee9d68479b36fb7c904b73f7888ca09ce4e09061aa85c9',
  '6c467bfba84f57ecd71c02d01c9172e31fafbc7693c56a146db793721cf3ac1c',
  '49d0990db1e48bc22fc557a272690362e51fd186ad5624682fe124ffc8f1ef6e')),
 (0x41000,1032,644,560,
 ('3b6115270fff9303beada863e7e709a802c30ed735000b9d4a164d6eb0b748ea',
  'e8d376a8c3496593186cfc57f75ec2de8026a20174b40a6769b2ddc46b233119',
  '6c467bfba84f57ecd71c02d01c9172e31fafbc7693c56a146db793721cf3ac1c',
  '4798b3283cf2604f89fe09245af89d4625fcf0f082cd8d258bba0270a00042b9')))
PARTS=(('prefix',0,82,26),('first_call',82,26,7),('fixups',136,12,6),('second_call',148,16,5))
SAVED=((1,28),(8,24),(9,20),(18,16),(19,12),(20,8),(21,4),(22,0))


def specs(role,entry,obj_delta,factor_delta,service_delta):
    s={};start=entry+next(off for r,off,size,n in PARTS if r==role)
    def e(o,op,**f):s[start+o]=dict(op=op,**f)
    def addi(o,r,b,v):e(o,'addi',rd=r,rs1=b,imm=v)
    def load(o,r,b,v,w=4,**f):e(o,'load',rd=r,rs1=b,imm=v,width=w,**f)
    def store(o,r,v):e(o,'store',rs2=r,rs1=2,imm=v,width=4)
    def lui(o,r,v):e(o,'lui',rd=r,imm=v)
    def binary(o,op,r,a,b):e(o,op,rd=r,rs1=a,rs2=b)
    if role=='prefix':
        addi(0,2,2,-32);store(2,19,12);lui(4,19,0x20003000);addi(8,15,19,obj_delta)
        store(12,8,24);load(14,8,15,164);store(18,9,20);lui(20,9,0x20003000);addi(24,15,9,factor_delta)
        load(28,15,15,8,2,mnemonic='qk.c.lhu');store(30,18,16);load(32,18,8,134,2);load(36,10,8,144)
        store(40,1,28);binary(42,'mul',18,18,15);lui(46,15,999424);addi(50,14,15,575);addi(54,15,15,576)
        store(58,20,8);store(60,21,4);store(62,22,0);addi(64,19,19,obj_delta);addi(68,9,9,factor_delta)
        binary(72,'add',18,18,14);binary(74,'divu',18,18,15);e(78,'bltu',rs1=10,rs2=18,target=entry+136)
    elif role=='first_call':
        lui(0,20,0x20003000);load(4,15,20,service_delta);binary(8,'sub',18,10,18)
        e(12,'call_indirect',rd=1,rs1=15);e(14,'bltu',rs1=18,rs2=10,target=entry+142)
        binary(18,'sub',18,18,10);e(22,'blt',rs1=18,rs2=0,target=entry+148)
    elif role=='fixups':
        load(0,15,9,4);binary(2,'add',10,10,15);e(4,'jump',target=entry+82)
        load(6,15,9,4);binary(8,'add',18,18,15);e(10,'jump',target=entry+100)
    elif role=='second_call':
        load(0,15,20,service_delta);e(4,'call_indirect',rd=1,rs1=15);load(6,14,8,136)
        e(10,'bltu',rs1=10,rs2=14,target=entry+316);binary(14,'sub',10,10,14)
    else:raise RuntimeError('unknown callback prefix role')
    return s


def window(raw,role,entry,detail,digest):
    _,obj,factor,service,_=detail;_,off,size,count=next(d for d in PARTS if d[0]==role)
    if role=='prefix':check(int.from_bytes(raw[32:36],'little')&0x707f==0x5003,'callback prefix unsigned halfword encoding')
    n=decode(raw,entry+off);s=specs(role,entry,obj,factor,service)
    check(set(n)==set(s),'callback prefix whole boundaries '+role)
    for p,f in s.items():init.g(n,p,'callback prefix '+role+' operand '+hex(p-entry-off),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(size,count,digest),'callback prefix whole window identity '+role)
    edges={};calls=[]
    for p,d in n.items():
        if d['op']=='jump':qs=[d['target']]
        elif d['op'] in ('bltu','blt'):qs=[p+d['size'],d['target']]
        else:qs=[p+d['size']]
        edges[p]=qs
        if d['op']=='call_indirect':calls.append({'pc':hex(p),'link':hex(p+d['size']),
            'target':'fresh U32[then-live S4+service_delta] & ~1','service_delta':service,'null_guard':False,
            'normal_return_and_register_frame_preservation_proved':False})
    return {'start':hex(entry+off),'end_exclusive':hex(entry+off+size),'bytes':size,'sha256':digest,
        'instructions':list(n.values()),'conditional_normal_return_CFG':{hex(p):[hex(q) for q in qs] for p,qs in edges.items()},
        'calls':calls,'complete_function':False}


def derive(app,carriers,header,coverage):
    parent=previous.derive(app,carriers,header,coverage);profiles=[]
    for i,(data,d) in enumerate(zip(carriers,DETAILS)):
        source,obj,factor,service,hashes=d;p=parent['profiles'][i];shift=int(p['mapping_shift'],16);entry=source+shift
        check(entry==0x20000d50,'callback first-copy entry')
        const=previous.previous.CALLERS[i][0];check(const[1]+const[2]==entry,'prior constant setter argument joins this callback')
        bodies={}
        for j,(role,off,size,count) in enumerate(PARTS):
            raw=init.binding.take(data,source+off,size);bodies[role]=window(raw,role,entry,d,hashes[j]);window(raw,role,source,d,hashes[j])
        nodes={x['pc']:x for b in bodies.values() for x in b['instructions']}
        edges={int(k,16):[int(q,16) for q in qs] for b in bodies.values() for k,qs in b['conditional_normal_return_CFG'].items()}
        cuts={q for qs in edges.values() for q in qs if q not in nodes}
        check(cuts=={entry+108,entry+164,entry+316},'callback three explicit continuation cuts')
        colors={}
        def visit(pc):
            if pc not in nodes:return
            check(colors.get(pc)!=1,'selected callback graph must be acyclic')
            if colors.get(pc)==2:return
            colors[pc]=1
            for q in edges[pc]:visit(q)
            colors[pc]=2
        visit(entry);check(set(colors)==set(nodes),'callback all selected nodes locally reachable')
        stored=[(x['rs2'],x['imm']) for x in bodies['prefix']['instructions'] if x['op']=='store']
        check(set(stored)==set(SAVED) and len(stored)==8,'callback eight exact saved-register fields')
        profiles.append({'label':p['label'],'flash_entry':hex(source),'mapped_entry':hex(entry),'mapping_shift':hex(shift),
            'prior_constant_setter_window_sha256':const[3],'bodies':bodies,'object_pointer_source':hex(0x20003000+obj+164),
            'factor_halfword_source':hex(0x20003000+factor+8),'nominal_S3':hex(0x20003000+obj),'nominal_S1':hex(0x20003000+factor),
            'nominal_wrap_word':hex(0x20003000+factor+4),'nominal_service_pointer_word':hex(0x20003000+service),
            'joined_CFG':{hex(k):[hex(q) for q in qs] for k,qs in edges.items()},'continuation_cuts':[hex(q) for q in sorted(cuts)],
            'selected_graph_is_acyclic':True,'whole_callback_completion_or_termination_proved':False,
            'actual_installed_binding_or_callback_execution_proved':False})
    check(sum(b['bytes'] for p in profiles for b in p['bodies'].values())==272,'callback selected byte census')
    check(sum(len(b['instructions']) for p in profiles for b in p['bodies'].values())==88,'callback selected instruction census')
    return {'schema':'TSL9-RAM-callback-prefix-static-v1','profile':parent['profile'],'profiles':profiles,
        'scope':'8 bounded pieces272B/88instructions; complete selected graph only, not complete callback',
        'saved_frame_fields':[{'register':r,'offset':o} for r,o in SAVED],
        'entry_contract':{'frame':'SP-=32; save RA/S0..S6, 8 word fields','object':'fresh pointer ->S0, no local null guard; U16[object+134], U32[object+144]',
            'Q':'((U16[object+134]*U16[factor_source]+999999) modulo2^32) unsigned_div1000000',
            'first_predicate':'unsigned loaded word144 < Q, before any call in the selected prefix',
            'overflow_threshold_product':4293967297,'max_wrapped_numerator_when_overflow':868928,
            'if_addition_overflows':'Q=0; unsigned word144<Q cannot be true; reachability of overflow inputs unproved'},
        'first_call_contract':{'precall':'optional fresh U32[then-live S1+4] add to A0; fresh service word->A5; S2=A0-Q; linked call A5',
            'postcall':'if unsigned S2<returned A0, add a new fresh U32[then-live S1+4] to S2; S2-=returned A0 modulo2^32',
            'next_predicate':'signed S2<0 enters second_call; otherwise external cut',
            'call_argument_ABI_and_return_semantics_known':False},
        'second_call_contract':{'target':'reload service word after first call; equality with first target not proved',
            'field136':'fresh U32[then-live S0+136] after second call; unsigned reply<field branches to external cut, else subtract and leave selected graph'},
        'fixup_contract':'two backward-address jumps rejoin after their selecting predicates; selected graph acyclic, broader callback may loop/reenter',
        'premises':['matching installed candidate and completed preserved first-copy code; valid conditional Xwchc ISA and data/stack accesses',
            'source object/factor/wrap values, pointer validity, object identity/aliasing and runtime input reachability unproved',
            'unknown callees may not return or may change S0/S1/S2/S4, frame, saved words, code, pointers or CSR; preservation is conditional',
            'separate fresh loads may differ; nominal global addresses require the relevant live base registers to retain their values'],
        'remaining':['three continuation cuts and remaining callback loops/exits','service pointer writers and provider semantics',
            'object/factor/wrap sources, practical input bounds and saved-frame lifetime','installed binding, source registration order and ECALL route'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    check(init.timer.encode('lhu',15,15,8)==0x279e,'official factor QK.C.LHU encoding')
    threshold=(1<<32)-999999;maxproduct=65535*65535
    check(threshold==4293967297 and maxproduct+999999-(1<<32)==868928<1000000,'closed-form overflow bounds')
    overflow_count=0
    for a in range(65536):
        product=a*65535;numerator=product+999999;q=(numerator&MASK)//1000000
        if numerator<=MASK:check(q==(product+999999)//1000000,'nonoverflow agrees with mathematical ceiling')
        else:check(q==0 and product>=threshold,'overflow max-factor row quotient zero');overflow_count+=1
        check(0<=q<=4294,'quotient bound')
    check(overflow_count>0,'max-factor row includes overflow witnesses')
    check((maxproduct+999999)//1000000==4295 and ((maxproduct+999999)&MASK)//1000000==0,'explicit non-ceiling counterexample')
    changes=(((8,1<<20),(14,1<<20),(24,1<<20),(28,4),(32,1<<14),(36,1<<20),(42,1<<15),(50,1<<20),(74,1<<15),(78,1<<12)),
        ((4,1<<20),(8,1<<15),(12,0x80),(14,1<<12),(22,1<<12)),((0,4),(4,4),(10,4)),((0,1<<20),(6,1<<20),(10,1<<12)))
    count=0
    for data,d in zip(carriers,DETAILS):
        source,obj,factor,service,hashes=d
        for j,(role,off,size,n) in enumerate(PARTS):
            raw=init.binding.take(data,source+off,size)
            for at,flip in changes[j]:
                b=bytearray(raw);width=decode(raw,source+off)[source+off+at]['size'];b[at:at+width]=(int.from_bytes(b[at:at+width],'little')^flip).to_bytes(width,'little')
                try:window(b,role,source,d,hashes[j])
                except RuntimeError as e:check(str(e) in ('callback prefix '+role+' operand '+hex(at),'callback prefix unsigned halfword encoding'),'specific callback mutation guard '+str(e))
                else:raise RuntimeError('callback prefix mutation escaped')
                count+=1
    check(count==42,'callback mutation census')
    print('PASS: official QK.C.LHU; 65536 max-factor arithmetic cases and overflow witness; 42 specified mutations rejected')


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
    else:check(OUT.read_bytes()==output,'RAM callback prefix exact ledger replay')
    print('PASS: 8 bounded pieces272B/88instructions; eight saved fields; joined selected CFG acyclic with 3 explicit cuts')
    print('PASS: exact ledger; NO target execution; whole callback/provider/input reachability/preservation UNPROVED')


if __name__=='__main__':main()
