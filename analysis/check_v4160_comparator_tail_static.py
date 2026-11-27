"""Offline full comparator/byte-range/event-wrapper call contracts.

Literal original operands, graphs and host integer identities only.
No target ISA/register/RAM machine, comparator, provider, MMIO or device run.
"""
import argparse
import json
from collections import deque
from hashlib import sha256
from pathlib import Path
import check_v4160_n136_predicate_static as previous
import check_v4160_range_retry_static as ranges

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-comparator-tail-static.json')
PARTS=('comparator','byte_range','event_wrapper')
STARTS=((0x20000442,0x43e6a,0x43932),(0x20000442,0x43ef6,0x439be))
SOURCES=((0x406b2,0x43e6a,0x43932),(0x406f2,0x43ef6,0x439be))
SIZES=(72,36,118)
COUNTS=(23,15,42)
FIELDS={**previous.FIELDS,**{o:('rd','rs1','rs2') for o in ('sub','mulhsu','mulhu','sltu')},'sltiu':('rd','rs1','imm')}
BRANCHES=previous.BRANCHES
HASHES=(('a9dbd2b47ccefe55ab45f0b4e5a073d7aeb00f42dbe503191a75b6b66efff3aa', 'b73001994b94bedca8f1b4433f913c6ea9f7e13bfe14f0ec52a1fc611cf3a5f7', '45b980a363d57dd1c8b6a5614ec55d5f9f844c0a1c10540a4695dcba0994c96f'), ('a9dbd2b47ccefe55ab45f0b4e5a073d7aeb00f42dbe503191a75b6b66efff3aa', 'b73001994b94bedca8f1b4433f913c6ea9f7e13bfe14f0ec52a1fc611cf3a5f7', 'fcf050661c53957728ce337d583c3ebd40ac2da1142218f7765dac7e0de2ab1f'))
LITERALS=(
{
'comparator':'''
000 lui 15 1073889280
004 load 14 15 524 4
008 store 15 0 524 4
00c fence.i
010 beqz 10 24
012 beqz 11 24
014 li 15 0
016 bnez 12 42
018 lui 15 1073889280
01c store 15 14 524 4
020 li 10 1
022 jr 1
024 addi 15 15 1
026 beq 12 15 24
02a add 16 10 15
02e add 13 11 15
032 load 16 16 0 1
036 load 13 13 0 1
038 beq 16 13 36
03c lui 15 1073889280
040 store 15 14 524 4
044 li 10 0
046 jr 1
''',
'byte_range':'''
000 addi 2 2 -32
002 store 2 8 24 4
004 store 2 1 28 4
006 mv 8 10
008 store 2 11 12 4
00a jal 1 275368
00e load 11 2 12 4
010 load 1 2 28 4
012 sub 11 11 8
014 mulhsu 10 11 10
018 add 10 10 8
01a load 8 2 24 4
01c andi 10 10 255
020 addi 2 2 32
022 jr 1
''',
'event_wrapper':'''
000 addi 2 2 -32
002 store 2 8 24 4
004 store 2 9 20 4
006 store 2 18 16 4
008 store 2 19 12 4
00a lui 15 1073889280
00e store 2 1 28 4
010 load 18 15 524 4
014 mv 8 10
016 mv 19 11
018 mv 9 12
01a store 15 0 524 4
01e fence.i
022 jal 1 276264
024 mv 10 8
026 mv 11 19
028 auipc 1 536596480
02c jalr 1 1 -1606
030 mv 8 10
032 beqz 10 90
034 lui 15 536883200
038 load 11 15 572 2
03c addi 12 0 1600
040 li 13 0
042 mul 15 11 9
046 mulhu 11 11 9
04a addi 10 15 800
04e sltu 15 10 15
052 add 11 11 15
054 jal 1 450330
058 store 8 10 4 4
05a sltiu 10 8 1
05e load 1 2 28 4
060 load 8 2 24 4
062 lui 15 1073889280
066 store 15 18 524 4
06a load 9 2 20 4
06c load 18 2 16 4
06e load 19 2 12 4
070 slli 10 10 3
072 addi 2 2 32
074 jr 1
'''
},
{
'comparator':'''
000 lui 15 1073889280
004 load 14 15 524 4
008 store 15 0 524 4
00c fence.i
010 beqz 10 24
012 beqz 11 24
014 li 15 0
016 bnez 12 42
018 lui 15 1073889280
01c store 15 14 524 4
020 li 10 1
022 jr 1
024 addi 15 15 1
026 beq 12 15 24
02a add 16 10 15
02e add 13 11 15
032 load 16 16 0 1
036 load 13 13 0 1
038 beq 16 13 36
03c lui 15 1073889280
040 store 15 14 524 4
044 li 10 0
046 jr 1
''',
'byte_range':'''
000 addi 2 2 -32
002 store 2 8 24 4
004 store 2 1 28 4
006 mv 8 10
008 store 2 11 12 4
00a jal 1 275508
00e load 11 2 12 4
010 load 1 2 28 4
012 sub 11 11 8
014 mulhsu 10 11 10
018 add 10 10 8
01a load 8 2 24 4
01c andi 10 10 255
020 addi 2 2 32
022 jr 1
''',
'event_wrapper':'''
000 addi 2 2 -32
002 store 2 8 24 4
004 store 2 9 20 4
006 store 2 18 16 4
008 store 2 19 12 4
00a lui 15 1073889280
00e store 2 1 28 4
010 load 18 15 524 4
014 mv 8 10
016 mv 19 11
018 mv 9 12
01a store 15 0 524 4
01e fence.i
022 jal 1 276404
024 mv 10 8
026 mv 11 19
028 auipc 1 536596480
02c jalr 1 1 -1746
030 mv 8 10
032 beqz 10 90
034 lui 15 536883200
038 load 11 15 652 2
03c addi 12 0 1600
040 li 13 0
042 mul 15 11 9
046 mulhu 11 11 9
04a addi 10 15 800
04e sltu 15 10 15
052 add 11 11 15
054 jal 1 450826
058 store 8 10 4 4
05a sltiu 10 8 1
05e load 1 2 28 4
060 load 8 2 24 4
062 lui 15 1073889280
066 store 15 18 524 4
06a load 9 2 20 4
06c load 18 2 16 4
06e load 19 2 12 4
070 slli 10 10 3
072 addi 2 2 32
074 jr 1
'''
}
)


def specs(part,index):
    pc=STARTS[index][PARTS.index(part)];out={}
    for line in LITERALS[index][part].splitlines():
        if not line:continue
        off,op,*args=line.split();vals=[int(v,0) for v in args];check(len(vals)==len(FIELDS[op]),'tail literalfields')
        d=dict(zip(FIELDS[op],vals));d['op']=op
        if op in BRANCHES|{'jump'}:d['target']+=pc
        out[pc+int(off,16)]=d
    return out


def body(raw,part,index):
    k=PARTS.index(part);pc=STARTS[index][k]
    if part!='byte_range':
        off=12 if part=='comparator' else 30
        check(raw[off:off+4]==bytes.fromhex('0f100000'),'tail '+part+' fencebytes')
    n=decode(raw,pc);s=specs(part,index);check(set(n)==set(s),'tail boundaries')
    for p,f in s.items():init.g(n,p,'tail '+part+' operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[k],HASHES[index][k]),'tail identity')
    edges={};calls=[];rets=[]
    for p,v in n.items():
        op=v['op'];qs=[p+v['size']]
        if op=='jr':check(v['rs1']==1,'tail RAreturn');qs=[];rets.append(p)
        elif op in BRANCHES:qs.append(v['target'])
        elif op=='jump':qs=[v['target']]
        elif op in ('jal','jalr'):
            check(v['rd']==1,'tail RAcall')
            if op=='jal':t=v['target']
            else:
                a=n[p-4];check(a['op']=='auipc' and a['rd']==v['rs1'],'tail PCpair');t=(p-4+a['imm']+v['imm'])&0xfffffffe
            calls.append({'offset':p-pc,'target':hex(t)})
        check(all(q in n for q in qs),'tail closedCFG');edges[p]=qs
    seen=set();pending=[pc]
    while pending:
        p=pending.pop()
        if p in seen:continue
        seen.add(p);pending.extend(edges[p])
    check(seen==set(n),'tail allnodes reachable')
    cycles=[c for c in previous.previous.common.sccs(edges) if len(c)>1 or c[0] in edges[c[0]]]
    check(bool(cycles)==(part=='comparator'),'tail cycleclassification')
    stores=[{'offset':p-pc,'base':v['rs1'],'source':v['rs2'],'offset_from_base':v['imm'],'bytes':v['width']} for p,v in n.items() if v['op']=='store']
    check((len(stores),len(calls),len(rets))==((3,0,2),(3,1,1),(8,3,1))[k],'tail census')
    if part=='comparator':
        check({v['rd'] for v in n.values() if 'rd' in v}=={10,13,14,15,16},'tail comparator GPRwrites')
        check([v['source'] for v in stores]==[0,14,14],'tail comparator capturedrestore')
    elif part=='byte_range':check(calls==[{'offset':10,'target':hex(0x433a8+140*index)}],'tail bytewordsource')
    else:check([v['target'] for v in calls]==[hex(0x43728+140*index),'0x20000314',hex(0x6df1a+496*index)],'tail event exactcallee shifts')
    return {'start':pc,'end_exclusive':pc+SIZES[k],'source':SOURCES[index][k],'bytes':SIZES[k],'sha256':sha256(raw).hexdigest(),
      'instructions':list(n.values()),'CFG':edges,'cyclic_SCCs':cycles,'local_CFG_acyclic':not cycles,'calls':calls,'stores':stores,'returns':rets,
      'complete_local_body':True,'actual_finite_callchain_proved':False}


def certificates(b,part):
    pc=b['start'];e=b['CFG'];ends=b['returns']
    def path(a,z):
        pending=deque([(a,[a])]);seen=set()
        while pending:
            p,s=pending.popleft()
            if p==z:return s
            if p in seen:continue
            seen.add(p);pending.extend((v,s+[v]) for v in e[p])
        return None
    def suffix(a):return min((s for z in ends if (s:=path(a,z)) is not None),key=len)
    witnesses=[]
    for p,qs in e.items():
        for q in qs:
            s=path(pc,p)+[q]+suffix(q)[1:];check(all(z in e[a] for a,z in zip(s,s[1:])),'tail edgewitness');witnesses.append([v-pc for v in s])
    offsets={'comparator':(0x1c,0x24,0x32,0x36,0x40),'byte_range':(10,20,28),'event_wrapper':(0x22,0x2c,0x38,0x4e,0x54,0x58,0x66)}[part]
    selected={hex(o):[v-pc for v in path(pc,pc+o)+suffix(pc+o)[1:]] for o in offsets}
    pred={p:set() for p in e}
    for p,qs in e.items():
        for q in qs:pred[q].add(p)
    dom={p:({pc} if p==pc else set(e)) for p in e};changed=True
    while changed:
        changed=False
        for p in e:
            if p==pc:continue
            value={p}|set.intersection(*(dom[q] for q in pred[p]))
            if value!=dom[p]:dom[p]=value;changed=True
    if part=='comparator':
        check(all({pc+4,pc+8,pc+12}<=dom[p] for p in ends),'tail comparator controlops beforeallreturns')
        check(pc+0x1c in dom[pc+0x22] and pc+0x40 in dom[pc+0x46],'tail comparator restore')
    elif part=='event_wrapper':
        check(all({pc+0x10,pc+0x1a,pc+0x1e,pc+0x66}<=dom[p] for p in ends),'tail event controlrestore dominance')
        # No A2 definition between first callee and second request: its value is opaque.
        n={v['pc']:v for v in b['instructions']};check(not any(0x22<p-pc<0x2c and v.get('rd')==12 for p,v in n.items()),'tail event A2 notreset')
    return {'selected_syntactic_walks':selected,'edge_witness_count':len(witnesses),'edge_witness_sha256':sha256(json.dumps(witnesses,separators=(',',':')).encode()).hexdigest(),
      'scope':'syntactic graph/dominance only; no actualpathfeasibility/hardware/calleecompletion proof'}


def domains():
    M=1<<32;cases=0
    for h in range(65536):
        for k in (0,1,65537,131070,M-1):
            product=h*k;lo=product&(M-1);hi=product>>32;sumlo=(lo+800)&(M-1);carry=int(sumlo<lo)
            check(((hi+carry)<<32)|sumlo==product+800,'tail productcarry identity');cases+=1
    check(65535*(M-1)+800 < 1<<48,'tail product64 nooverflow')
    check(65535*131070+800 < 2*M,'tail callbackproduct upperword01')
    check((65535*65537)&(M-1)==M-1,'tail carrywitness')
    # Symbolic high-product envelope: 0<=R<M implies0<=floor(11R/M)<=10.
    check(11*(M-1)//M==10 and 11*0//M==0,'tail bytecallback envelope')
    samples=[0,1,M//2,M-2,M-1]+[(q*M+10)//11 for q in range(1,11)]
    for r in samples:check(5<=5+(11*r//M)<=15,'tail bytecallback samples')
    return {'pair_multiplication_selected_cases':cases,'productcarry_formula':'H=U16global,K=entryuint32A2;A1:A0=H*K+800 exactU64, nooverflow',
      'pair_max':65535*(M-1)+800,'callback_K_range':[0,131070],'callback_pair_max':65535*131070+800,'callback_pair_highword_range':[0,1],
      'carry_witness':{'H':65535,'K':65537,'product_low32':M-1,'afteradd800_low32':799,'carry':1},
      'byte_range_formula':'low8(A+signedhigh32(signed32((B-A)mod2^32)*unsignedR))','callback_A5_B16_range':[5,15],
      'source_distribution/actualrandomness/physical_units/divisionbody_proved':False,
      'comparator':'nonnull pointers/n>0: firstfresh mismatch0,allnmatch1; eitherpointerNULL OR n0 returns1; local uint32index reachesn in<=n matchsteps',
      'lookup_selected_compare':'query2,node4,6; both validnonnull ->compares6freshbytepairs; nullreturn1 doesnotvalidatepointers/extents',
      'target_execution_or_emulation':False}


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[]
    for i,(data,pr) in enumerate(zip(carriers,parent['profiles'])):
        bodies={part:body(init.binding.take(data,SOURCES[i][k],SIZES[k]),part,i) for k,part in enumerate(PARTS)}
        mapping=init.binding.profile(data,pr['label']);m=mapping['first_copy'];ram=STARTS[i][0];source=int(m['source'],16)+ram-int(m['destination'],16)
        check(source==SOURCES[i][0] and ram+72<=int(mapping['first_copy_end_exclusive'],16),'tail completecomparator mapping')
        check(pr['bodies']['lookup']['calls']==[{'offset':0x34,'target':hex(ram)}],'tail lookupcompare join')
        c={v['pc']-pr['bodies']['callback']['start']:v for v in pr['bodies']['callback']['instructions']}
        check(c[0xd4]['imm']==16 and c[0xd6]['imm']==5 and c[0xd8]['target']==STARTS[i][1],'tail bytecallback argsjoin')
        check(c[0x106]['target']==STARTS[i][2] and c[0x102]['imm']==16,'tail eventcallback join')
        ranges.body(init.binding.take(data,0x433a8+140*i,108),'source',i)
        profiles.append({'label':pr['label'],'bodies':bodies,'CFG_certificates':{p:certificates(b,p) for p,b in bodies.items()},
          'comparator_mapping':{'first_copy':m,'first_copy_end_exclusive':mapping['first_copy_end_exclusive'],'RAM_entry':ram,'source':source,'bytes':72,'installedbinding_proved':False},
          'reused_word_source':{'start':0x433a8+140*i,'bytes':108,'sha256':sha256(init.binding.take(data,0x433a8+140*i,108)).hexdigest()},
          'comparator_contract':{'args':['pointerP=A0','pointerQ=A1','uint32n=A2'],'first':'capturecontrolword4002420c,SWzero,FENCE.I BEFOREanynull/lengthguard',
            'null_or_zero':'eitherpointerNULL OR n0 ->1withoutpayloadreads, aftercontrolops','nonnull_positive':'freshU8[P+index] versusfreshU8[Q+index];firstmismatch0;allncomparisonsmatch1',
            'normalrestore':'capturedwordrestorebeforebothRET; noatomic/externalinterference/physicalrestoreclaim','payloadwrites':False,'local_GPR_writes':[10,13,14,15,16],
            'preserved_locally':'A1,A2,A7,allSregisters,SP,RA; noframe/calls','retention_or_alias_independence_proved':False},
          'lookup_join':{'args':'borrowedquery+2,node+4,6; fullreply1 selectsnode evenif comparatornullfastpathwereused',
            'conditionalvalidnonnull_extents':{'query':8,'node_compare':10,'node_next':64},'no_table/listlifetime_or_installedprovider_proof':True},
          'byte_range_contract':{'frame':32,'saved':['RA','S0'],'one_callee':hex(0x433a8+140*i),'source_reply':'U32R, no randomness/distributionassumed',
            'formula':'difference=(B-A)mod2^32;signeddifference=sign32(difference);reply=(A+high32(signeddifference*unsignedR))&255',
            'generaloutput_range':[0,255],'callback_5_16_output':[5,15],'callback_effect':'callback storeslow8replytoNprime12; source/frame/Sregpreservation stillpremises',
            'nonframe_stores_locally':False,'source_control/callback/stateeffects':'reusedsourcebody hascontrolwordops,statewrite,andoptionalindirectcallback; actualbinding/retentionunproved'},
          'event_wrapper_contract':{'frame':32,'saved':['RA','S0','S1','S2','S3'],'captures':['entryA0inS0','entryA1inS3','entryA2inS1','control4002420c inS2'],
            'beforecalls':'SWzero4002420c;FENCE.I','first_request':{'target':hex(0x43728+140*i),'A0':'entryA0','A1':'entryA1','A2':'entryA2'},
            'second_request':{'target':'0x20000314','A0':'restoredentryA0','A1':'restoredentryA1','A2':'then-liveafterfirstcallee; NOTlocallyreset','otherargs':'opaque'},
            'second_reply':'capturefullA0pointerRintoS0; nullskipsarithmetic/store,nonnullfreshreadsU16global',
            'H_address':0x2000323c+80*i,'K':'preservedentryA2, not secondrequest A2','numerator_pair':'exactU64 H*K+800 throughMUL/MULHU/add800/SLTUcarry',
            'third_request':{'target':hex(0x6df1a+496*i),'A1_A0':'high/low numeratorpair','A2':1600,'A3':0,'interpretation':'division ABI candidate only; existingstructuralproof doesnotbyitselfprove arithmeticreplyformula'},
            'store':'nonnullR:SW actualthirdcalleeA0toR4; no quotientsemanticsguaranteed','R_minimum_extent':8,
            'normal_exit':'SLTIU(capturedR,1)<<3 ->8ifRnull,0otherwise; restorecapturedcontrolword; calleerepliesdonotdeterminefinalA0',
            'callback_K_domain':[0,131070],'callback_status_ignored':True,'globalH_physicalmeaning/actualbinding/calleecompletion/retention_proved':False},
          'target_execution_or_emulation':False})
    return {'schema':'TSL9-comparator-tail-static-v1','APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'integer_domains':domains(),
      'newbytes':308,'reusedbytes':144,'decodedbytes':452,'instruction_guards':160,
      'reused_comparator_proof':'analysis/wch-resident-candidate-2026-10-21/memcmp-port-review/check-review.py',
      'scope':'2*(36Bbytewrapper+118Beventwrapper) new;2*72Bcomparator reused. Earlierwordsource proofs reusedwithoutcoveragecount',
      'remaining':['generator640d8/641c2 fullbody/numericalconstraints','composeexistingtimer/lookup/arithmetic proofs intoactualreturn/effectcontracts','actualglobalwriters/providerbinding/alias/lifetime/physicaleffects'],
      'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    mutations=variants=walks=edges=0
    for i,data in enumerate(carriers):
        for k,part in enumerate(PARTS):
            raw=init.binding.take(data,SOURCES[i][k],SIZES[k]);pc=STARTS[i][k];b=body(raw,part,i);c=certificates(b,part);walks+=len(c['selected_syntactic_walks']);edges+=c['edge_witness_count']
            for p,v in decode(raw,pc).items():
                at=p-pc;z=v['size'];buf=bytearray(raw);buf[at:at+z]=(int.from_bytes(buf[at:at+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
                try:body(buf,part,i)
                except RuntimeError as ex:check(str(ex).startswith('tail '+part+' operand ') or str(ex)=='tail '+part+' fencebytes','tail mutation specific '+str(ex))
                else:raise RuntimeError('tail mutation escaped')
                mutations+=1
            if part in ('byte_range','event_wrapper'):
                at=20 if part=='byte_range' else 70;buf=bytearray(raw);buf[at:at+4]=(int.from_bytes(buf[at:at+4],'little')^(1<<12)).to_bytes(4,'little')
                try:body(buf,part,i)
                except RuntimeError as ex:check(str(ex)=='tail '+part+' operand '+hex(at),'tail signedmultiplyvariant guard')
                else:raise RuntimeError('tail signedmultiplyvariant escaped')
                variants+=1
    check((mutations,variants)==(160,4),'tail mutationcensus');domains()
    print('PASS:160 instruction +4 multiplysignedness mutations rejected;308 new/144 reused bytes;'+str(walks)+' selectedCFG walks;'+str(edges)+' edge witnesses;327680 product/carry cases')


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');o=p.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK identity')
    carriers=[]
    for label,folder,tail,z,digest in init.binding.PROFILES:
        data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidate identity '+label);carriers.append(data)
    raw_hex=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,raw_hex,sparse.parser())
    ledger=derive(image,carriers,header,coverage);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers);output=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'tail exactledger replay')
    print('PASS:complete comparator/byte/event bodies;lookup/callback/startup/wordsource joins;exact ledger')
    print('PASS:NO target execution/emulation;installedproviders/physicalrestore/calleecompletion/lifetimes UNPROVED')


if __name__=='__main__':main()
