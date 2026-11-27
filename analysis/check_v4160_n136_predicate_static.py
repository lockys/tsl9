"""Offline N+136 callback and mapped predicate operands/CFG/argument proofs.

Only original-byte decoding, finite graphs and host integer predicates.
No target ISA, provider, MMIO, FENCE, register/stack machine or device execution.
"""
import argparse
import json
from collections import deque
from hashlib import sha256
from pathlib import Path
import check_v4160_large_consumer_service_static as previous

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
OUT=Path(__file__).with_name('v4160-n136-predicate-static.json')
PARTS=('callback','predicate','lookup')
STARTS=((0x57b7c,0x200004bc,0x2000202c),(0x57cbc,0x200004bc,0x20002084))
SOURCES=((0x57b7c,0x4072c,0x4229c),(0x57cbc,0x4076c,0x42334))
SIZES=(322,62,76)
COUNTS=(111,19,31)
FIELDS={**previous.FIELDS,'fence.i':()}
BRANCHES=previous.BRANCHES
HASHES=(('7215e521c29d60d3cc385e9fcaf4d7ccae636f0a782b66dc2101703c5b495c20', '39eff00fe85a0bdea780df359a1f1d1356681a168097a60b7b805faac6303581', '32e9cb0655f6b631abb0efd7d7d06c2ae1e6f4be1f1f463d06cc6e3d960345c3'), ('3ff02c07dfa2df14997e209c911fc0974f3f55310f3bf82b9dca3de90d55b14b', '39eff00fe85a0bdea780df359a1f1d1356681a168097a60b7b805faac6303581', '86e230d99c24e9a84b64eea26b58b3cb17e499193c54b05aa7248f1428357175'))
LITERALS=(
{
'callback':'''
000 addi 2 2 -16
002 store 2 9 4 4
004 lui 9 536883200
008 addi 14 9 952
00c store 2 8 8 4
00e load 8 14 148 4
012 store 2 1 12 4
014 store 2 18 0 4
016 load 15 8 101 1
01a store 8 0 100 1
01e bnez 15 62
020 li 15 1
022 lui 11 536883200
026 store 8 15 100 1
02a li 12 6
02c addi 11 11 1184
030 addi 10 8 102
034 auipc 1 536510464
038 jalr 1 1 1922
03c jump 192
03e li 13 1
040 bne 15 13 86
044 load 14 14 2 1
046 bnez 14 120
048 li 10 18
04a load 1 2 12 4
04c load 8 2 8 4
04e load 9 2 4 4
050 load 18 2 0 4
052 addi 2 2 16
054 jr 1
056 load 11 8 132 4
05a addi 18 9 952
05e bnez 11 284
060 load 15 8 108 1
064 bnez 15 136
066 load 14 8 101 1
06a li 15 2
06c beq 14 15 32
070 load 15 18 2 1
074 beqz 15 72
076 li 15 1
078 lui 11 536883200
07c store 8 15 100 1
080 li 12 6
082 addi 11 11 1190
086 jump 48
088 addi 10 8 108
08c auipc 1 536518656
090 jalr 1 1 1060
094 store 8 10 132 4
098 beqz 10 182
09a load 15 10 10 1
09c beqz 15 182
09e li 15 2
0a0 store 8 15 100 1
0a4 li 12 6
0a6 addi 11 10 12
0aa addi 10 8 102
0ae auipc 1 536510464
0b2 jalr 1 1 1800
0b6 load 14 8 100 1
0ba li 15 2
0bc bne 14 15 102
0c0 lui 11 16777216
0c4 addi 11 11 -1
0c6 li 10 0
0c8 jal 1 278194
0cc store 8 10 92 4
0ce jal 1 409816
0d2 store 8 10 88 4
0d4 li 11 16
0d6 li 10 5
0d8 jal 1 278122
0dc li 15 1
0de store 8 15 7 1
0e0 li 15 3
0e2 store 8 15 4 1
0e4 load 15 8 56 1
0e8 lui 18 536883200
0ec store 8 10 12 1
0ee li 14 3
0f0 addi 18 18 412
0f4 bne 15 14 300
0f8 load 12 8 52 2
0fa load 15 8 70 2
0fe load 10 18 3 1
102 li 11 16
104 add 12 12 15
106 jal 1 276786
10a load 10 18 3 1
10e li 11 16
110 jal 1 275786
114 li 10 0
116 store 9 0 952 1
11a jump 74
11c load 15 11 10 1
11e beqz 15 102
120 li 15 2
122 store 8 15 100 1
126 li 12 6
128 addi 11 11 12
12a jump 170
12c li 14 2
12e load 10 18 3 1
132 bne 15 14 318
136 load 12 8 70 2
13a li 11 16
13c jump 262
13e load 12 8 52 2
140 jump 314
''',
'predicate':'''
000 lui 14 1073889280
004 load 15 14 524 4
008 store 14 0 524 4
00c fence.i
010 beqz 10 24
012 add 14 10 12
016 bnez 12 36
018 lui 14 1073889280
01c store 14 15 524 4
020 li 10 0
022 jr 1
024 addi 10 10 1
026 load 13 10 -1 1
02a bne 13 11 24
02e bne 10 14 36
032 lui 14 1073889280
036 store 14 15 524 4
03a li 10 1
03c jr 1
''',
'lookup':'''
000 addi 2 2 -32
002 lui 15 536883200
006 store 2 8 24 4
008 load 8 15 1156 4
00c store 2 9 20 4
00e store 2 18 16 4
010 store 2 19 12 4
012 store 2 1 28 4
014 mv 9 10
016 addi 18 10 2
01a li 19 1
01c beqz 8 60
01e load 15 9 1 1
020 load 14 8 3 1
022 andi 15 15 1
024 beq 14 15 44
028 load 8 8 60 4
02a jump 28
02c li 12 6
02e addi 11 8 4
032 mv 10 18
034 jal 1 536872002
038 bne 10 19 40
03c mv 10 8
03e load 1 2 28 4
040 load 8 2 24 4
042 load 9 2 20 4
044 load 18 2 16 4
046 load 19 2 12 4
048 addi 2 2 32
04a jr 1
'''
},
{
'callback':'''
000 addi 2 2 -16
002 store 2 9 4 4
004 lui 9 536883200
008 addi 14 9 1032
00c store 2 8 8 4
00e load 8 14 148 4
012 store 2 1 12 4
014 store 2 18 0 4
016 load 15 8 101 1
01a store 8 0 100 1
01e bnez 15 62
020 li 15 1
022 lui 11 536883200
026 store 8 15 100 1
02a li 12 6
02c addi 11 11 1264
030 addi 10 8 102
034 auipc 1 536510464
038 jalr 1 1 1602
03c jump 192
03e li 13 1
040 bne 15 13 86
044 load 14 14 2 1
046 bnez 14 120
048 li 10 18
04a load 1 2 12 4
04c load 8 2 8 4
04e load 9 2 4 4
050 load 18 2 0 4
052 addi 2 2 16
054 jr 1
056 load 11 8 132 4
05a addi 18 9 1032
05e bnez 11 284
060 load 15 8 108 1
064 bnez 15 136
066 load 14 8 101 1
06a li 15 2
06c beq 14 15 32
070 load 15 18 2 1
074 beqz 15 72
076 li 15 1
078 lui 11 536883200
07c store 8 15 100 1
080 li 12 6
082 addi 11 11 1270
086 jump 48
088 addi 10 8 108
08c auipc 1 536518656
090 jalr 1 1 828
094 store 8 10 132 4
098 beqz 10 182
09a load 15 10 10 1
09c beqz 15 182
09e li 15 2
0a0 store 8 15 100 1
0a4 li 12 6
0a6 addi 11 10 12
0aa addi 10 8 102
0ae auipc 1 536510464
0b2 jalr 1 1 1480
0b6 load 14 8 100 1
0ba li 15 2
0bc bne 14 15 102
0c0 lui 11 16777216
0c4 addi 11 11 -1
0c6 li 10 0
0c8 jal 1 278334
0cc store 8 10 92 4
0ce jal 1 410050
0d2 store 8 10 88 4
0d4 li 11 16
0d6 li 10 5
0d8 jal 1 278262
0dc li 15 1
0de store 8 15 7 1
0e0 li 15 3
0e2 store 8 15 4 1
0e4 load 15 8 56 1
0e8 lui 18 536883200
0ec store 8 10 12 1
0ee li 14 3
0f0 addi 18 18 492
0f4 bne 15 14 300
0f8 load 12 8 52 2
0fa load 15 8 70 2
0fe load 10 18 3 1
102 li 11 16
104 add 12 12 15
106 jal 1 276926
10a load 10 18 3 1
10e li 11 16
110 jal 1 275926
114 li 10 0
116 store 9 0 1032 1
11a jump 74
11c load 15 11 10 1
11e beqz 15 102
120 li 15 2
122 store 8 15 100 1
126 li 12 6
128 addi 11 11 12
12a jump 170
12c li 14 2
12e load 10 18 3 1
132 bne 15 14 318
136 load 12 8 70 2
13a li 11 16
13c jump 262
13e load 12 8 52 2
140 jump 314
''',
'predicate':'''
000 lui 14 1073889280
004 load 15 14 524 4
008 store 14 0 524 4
00c fence.i
010 beqz 10 24
012 add 14 10 12
016 bnez 12 36
018 lui 14 1073889280
01c store 14 15 524 4
020 li 10 0
022 jr 1
024 addi 10 10 1
026 load 13 10 -1 1
02a bne 13 11 24
02e bne 10 14 36
032 lui 14 1073889280
036 store 14 15 524 4
03a li 10 1
03c jr 1
''',
'lookup':'''
000 addi 2 2 -32
002 lui 15 536883200
006 store 2 8 24 4
008 load 8 15 1236 4
00c store 2 9 20 4
00e store 2 18 16 4
010 store 2 19 12 4
012 store 2 1 28 4
014 mv 9 10
016 addi 18 10 2
01a li 19 1
01c beqz 8 60
01e load 15 9 1 1
020 load 14 8 3 1
022 andi 15 15 1
024 beq 14 15 44
028 load 8 8 60 4
02a jump 28
02c li 12 6
02e addi 11 8 4
032 mv 10 18
034 jal 1 536872002
038 bne 10 19 40
03c mv 10 8
03e load 1 2 28 4
040 load 8 2 24 4
042 load 9 2 20 4
044 load 18 2 16 4
046 load 19 2 12 4
048 addi 2 2 32
04a jr 1
'''
}
)


def specs(part,index):
    pc=STARTS[index][PARTS.index(part)];out={}
    for line in LITERALS[index][part].splitlines():
        if not line:continue
        off,op,*args=line.split();vals=[int(v,0) for v in args]
        check(len(vals)==len(FIELDS[op]),'n136 literalfields')
        d=dict(zip(FIELDS[op],vals));d['op']=op
        if op in BRANCHES|{'jump'}:d['target']+=pc
        out[pc+int(off,16)]=d
    return out


def body(raw,part,index):
    if part=='predicate':check(raw[12:16]==bytes.fromhex('0f100000'),'n136 predicate fencebytes')
    k=PARTS.index(part);pc=STARTS[index][k];n=decode(raw,pc);s=specs(part,index)
    check(set(n)==set(s),'n136 '+part+' boundaries')
    for p,f in s.items():
        if f['op']=='fence.i':check(n[p]['bytes']=='0f100000','n136 predicate fencebytes')
        init.g(n,p,'n136 '+part+' operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[k],HASHES[index][k]),'n136 '+part+' identity')
    edges={};calls=[];rets=[]
    for p,v in n.items():
        op=v['op'];qs=[p+v['size']]
        if op=='jr':check(v['rs1']==1,'n136 RAreturn');qs=[];rets.append(p)
        elif op in BRANCHES:qs.append(v['target'])
        elif op=='jump':qs=[v['target']]
        elif op in ('jal','jalr'):
            check(v['rd']==1,'n136 RAcall')
            if op=='jal':t=v['target']
            else:
                a=n[p-4];check(a['op']=='auipc' and a['rd']==v['rs1'],'n136 PCpair');t=(p-4+a['imm']+v['imm'])&0xfffffffe
            calls.append({'offset':p-pc,'target':hex(t)})
        check(all(q in n for q in qs),'n136 closedCFG');edges[p]=qs
    pending=[pc];seen=set()
    while pending:
        p=pending.pop()
        if p in seen:continue
        seen.add(p);pending.extend(edges[p])
    check(seen==set(n),'n136 allnodes reachable')
    cycles=[c for c in previous.common.sccs(edges) if len(c)>1 or c[0] in edges[c[0]]]
    check(bool(cycles)==(part!='callback'),'n136 cycleclassification')
    stores=[{'offset':p-pc,'base':v['rs1'],'source':v['rs2'],'offset_from_base':v['imm'],'bytes':v['width']} for p,v in n.items() if v['op']=='store']
    check((len(stores),len(calls),len(rets))==((16,8,1),(3,0,2),(5,1,1))[k],'n136 census')
    if part=='predicate':
        check({v['rd'] for v in n.values() if 'rd' in v}=={10,13,14,15},'n136 predicate GPRwrites')
        check(n[pc+4]['imm']+n[pc]['imm']==0x4002420c,'n136 controlword address')
        check([v['offset'] for v in stores]==[8,28,54] and [v['source'] for v in stores]==[0,15,15],'n136 controlword stores')
    elif part=='callback':
        check([v['target'] for v in calls]==['0x20000332',hex(0x2000202c+88*index),'0x20000332',hex(0x43eb2+140*index),hex(0x640d8+234*index),hex(0x43e6a+140*index),hex(0x43932+140*index),hex(0x4354a+140*index)],'n136 exactcalls')
        check(n[pc+0xe]['rd']==8 and n[pc+0xe]['imm']==148 and n[pc+0x16]['rs1']==8,'n136 captures freshglobalN')
    else:
        check(calls==[{'offset':0x34,'target':'0x20000442'}],'n136 lookup comparecallee')
        check(all(v['base']==2 for v in stores),'n136 lookup frame storesonly')
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
            s=path(pc,p)+[q]+suffix(q)[1:]
            check(all(z in e[a] for a,z in zip(s,s[1:])),'n136 edgewitness')
            witnesses.append([v-pc for v in s])
    selected={}
    for off in ((0x38,0x48,0x70,0x90,0xb2,0xc8,0xce,0xd8,0xf8,0x106,0x110,0x11c,0x136,0x13e) if part=='callback' else (0x1c,0x26,0x2e,0x36) if part=='predicate' else (0x1e,0x28,0x34,0x38)):
        selected[hex(off)]=[v-pc for v in path(pc,pc+off)+suffix(pc+off)[1:]]
    # Graph dominators certify that even null/zero-length exits follow controlword writes.
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
    if part=='predicate':
        check(all({pc+4,pc+8,pc+12}<=dom[p] for p in ends),'n136 controlwrite/fence dominatebothreturns')
        check(pc+0x1c in dom[pc+0x22] and pc+0x36 in dom[pc+0x3c],'n136 restore before returns')
    elif part=='callback':check(all(pc+0x1a in dom[p] for p in ends),'n136 N100clear dominatesreturn')
    return {'selected_syntactic_walks':selected,'edge_witness_count':len(witnesses),'edge_witness_sha256':sha256(json.dumps(witnesses,separators=(',',':')).encode()).hexdigest(),
      'scope':'graph walks/dominance only; no input feasibility, provider completion or actual hardware preservation proof'}


def domains():
    # Address intervals and scalar comparisons only, never mutable target memory/registers.
    check([x for x in range(256) if x==0]==[0],'n136 zero byte exact')
    check(all(x!=256 for x in range(256)),'n136 fullA1 notbyte-truncated')
    for length in range(1,257):
        for k in range(length):check(k+1<=length,'n136 boundedoffset')
    for tag in range(256):check((tag in (0,1,2))==(tag<=2),'n136 acceptedtag partition')
    check(65535+65535==131070,'n136 unsaturated event sum')
    return {'byte_cases':256,'selected_positive_lengths':256,'A1_comparison':'fullwordA1 versus zeropaddedU8; any A1>255 mismatches first byte',
      'selected_A1_0_A2_6':'nonnull source reads 1..6 bytes until mismatch; exactly six zeros ->1; null/any mismatch ->0',
      'loop_bound':'under valid reads, original instruction/register semantics and fixed uint32 length n>0, successive modulo32 pointers reach P+n after n successful comparisons; no earlier hit for k<n',
      'maximum_successful_reads_uint32':4294967295,'target_execution_or_emulation':False}


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[]
    for i,(data,pr) in enumerate(zip(carriers,parent['profiles'])):
        bodies={part:body(init.binding.take(data,SOURCES[i][k],SIZES[k]),part,i) for k,part in enumerate(PARTS)}
        mapping=init.binding.profile(data,pr['label']);m=mapping['first_copy'];ram=0x200004bc
        source=int(m['source'],16)+ram-int(m['destination'],16)
        check(source==SOURCES[i][1] and int(m['destination'],16)<=ram and ram+62<=int(mapping['first_copy_end_exclusive'],16),'n136 predicate entirecopyinterval')
        lookup=STARTS[i][2];lsource=int(m['source'],16)+lookup-int(m['destination'],16)
        check(lsource==SOURCES[i][2] and lookup+76<=int(mapping['first_copy_end_exclusive'],16),'n136 lookup sourceinterval')
        check(pr['final_callback']['conditional_constructor_value']==hex(STARTS[i][0]),'n136 prior constructor/callbackjoin')
        check(pr['initial_copy_sequence']['predicate_request']==['RAM200004bc','entryA3',0,6],'n136 predicate argsjoin')
        B=pr['B'];pc=STARTS[i][0];n={v['pc']:v for v in bodies['callback']['instructions']}
        check(n[pc+8]['imm']+0x20003000==B and n[pc+0x2c]['imm']+0x20003000==0x200034a0+80*i,'n136 freshN/source globals')
        profiles.append({'label':pr['label'],'B':B,'bodies':bodies,'CFG_certificates':{p:certificates(b,p) for p,b in bodies.items()},
          'predicate_mapping':{'first_copy':m,'first_copy_end_exclusive':mapping['first_copy_end_exclusive'],'RAM_entry':ram,'source':source,'bytes':62,'actualstartup/installedbinding_proved':False},
          'callback_contract':{'frame':16,'saved':['RA','S0','S1','S2'],'entry_A0_ignored':'capture freshU32[B148] intoS0 beforeaccesses; noNnullguard. ThismaydifferlargeconsumerN',
            'first_write':'N100=0 beforetagbranches andallnormalreturns','tag0':'N100=1;copy6(N102,globalG0);thenfinalization',
            'tag1':'freshU8[B2]==0 ->18;elsen100=1;copy6(N102,globalG1);thenfinalization',
            'other_tags':'freshU32[N132] nonnull ->readbyteQ10; ifnonzero markN100=2,copy6(N102,Q12); elsefallback. NullQ checksN108; nonzero requestsRAM2000202c(N108),storesreplyQtoN132 beforeQnull/Q10guards',
            'fallback':'freshN101==2 ->globalG0; elsefreshB2==0 ->18; elseglobalG1. Fullrawtagdomain, caller<=3domain isconditionalonpreservation',
            'copy_contract':'both encodedcopycalls targetRAM20000332,length6; pointervalidity/synchronouscompletion/retention remainunproved',
            'G0':0x200034a0+80*i,'G1':0x200034a6+80*i,'lookup_target':lookup,
            'finalization':['request43eb2/43f3e(0,0xffffff) ->storeactualA0toN92','request640d8/641c2 ->storeactualA0toN88',
              'request43e6a/43ef6(5,16) ->storelow8actualreplytoN12;N7=1,N4=3',
              'freshN56==3 ->A2=U16[N52]+U16[N70] full32sum;==2 ->A2=U16[N70];elseA2=U16[N52]',
              'request43932/439be(freshU8[C3],16,A2);request4354a/435d6(freshU8[C3],16);B0=0;A0=0;restoreRET'],
            'C':0x2000319c+80*i,'normal_local_A0_domain':[0,18],'failure18_can_follow_writes/lookup/copies':True,
            'fixed_min_extents':{'B':152,'N':136,'Q_if_used':18,'G0/G1_ifcopy6':6,'C':4,'frame':16},
            'local_CFG_acyclic':True,'allcallee_effects/objectidentity/lifetime/physicalcompletion_proved':False},
          'lookup_contract':{'RAM_entry':lookup,'mapped_source':lsource,'bytes':76,'frame':32,'saved':['RA','S0','S1','S2','S3'],
            'head_slot':B+204,'query':'entryA0 retainedS1;query+2 retainedS2; no querynullguard beforeaccess onnonnullhead',
            'loop':'freshU8[node3] == (freshU8[query1]&1); equal ->RAM20000442(query2,node4,6); compare reply exactly1 returnsnode. Otherwise next=freshU32[node60]',
            'empty_or_exhausted':'return0; emptyhead doesnotreadquery','stores':'frameonly; borrowedquery/nodepointers passedtounknowncompare',
            'minimum_extents':{'query_forcompare':8,'node_fornext':64},'normalreturns':'0 orcapturedmatchingnodepointer; caller savesintoN132',
            'installedbinding/comparesemantics/retention/listacyclicity/finitecompletion_proved':False},
          'predicate_contract':{'args':['sourceP=entryA0','fullwordvalueV=entryA1','uint32lengthn=entryA2'],
            'before_any_null_length_check':['captureU32[0x4002420c] inA5','SW0to0x4002420c','FENCE.I'],
            'return0':'Pnull OR n0 OR firstU8[P+k]!=fullwordV','return1':'Pnonnull,nnonzero,allnbytecomparisons equalV',
            'normal_exit':'SWcapturedwordto0x4002420c beforebothreturns; notatomic/physicalrestoreguarantee','input_writes':False,
            'GPR_writes':[10,13,14,15],'preserved_locally':'A1,A2,allSregisters,SP,RA; noframe/calls',
            'control_sideeffects_present_even_null':True,'no_direct_inputpointer_store':True,'object_retention/hardware_semantics_proved':False},
          'target_execution_or_emulation':False})
    return {'schema':'TSL9-n136-predicate-static-v1','APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'integer_domains':domains(),
      'newbytes':796,'reusedbytes':124,'decodedbytes':920,'instruction_guards':322,'scope':'2*(322Bcallback+76Blookup) new;2*62Bpredicate reused from sealedprecopyproof; no Ccoverage increase',
      'reused_predicate_proof':'analysis/v4160-resident-memory-2026-10-22/precopy-review/check.py',
      'remaining':['RAM20000442 comparator completebody/binding','finalization callees andactualevent/timing effects','B148/N132/globalwriters,sourcebuffers,alias/lifetime andinstalledproviders'],
      'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    mutations=walks=edges=0
    for i,data in enumerate(carriers):
        for k,part in enumerate(PARTS):
            raw=init.binding.take(data,SOURCES[i][k],SIZES[k]);pc=STARTS[i][k];b=body(raw,part,i);c=certificates(b,part)
            walks+=len(c['selected_syntactic_walks']);edges+=c['edge_witness_count']
            for p,v in decode(raw,pc).items():
                at=p-pc;z=v['size'];buf=bytearray(raw);buf[at:at+z]=(int.from_bytes(buf[at:at+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
                try:body(buf,part,i)
                except RuntimeError as ex:check(str(ex).startswith('n136 '+part+' operand ') or str(ex)=='n136 predicate fencebytes','n136 mutation specific '+str(ex))
                else:raise RuntimeError('n136 mutation escaped')
                mutations+=1
    check(mutations==322,'n136 mutation census');domains()
    print('PASS:322 instruction mutations rejected;796 new/124 reused originalbytes;'+str(walks)+' selectedCFG walks;'+str(edges)+' edge witnesses; predicate/controlword/argument joins')


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');o=p.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK identity')
    carriers=[]
    for label,folder,tail,z,digest in init.binding.PROFILES:
        data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidate identity '+label);carriers.append(data)
    raw_hex=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
    coverage=sparse.derive(image,carriers,header,raw_hex,sparse.parser());ledger=derive(image,carriers,header,coverage)
    ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers);output=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'n136 exactledger replay')
    print('PASS:full callback/predicate bodies andconstructor/consumer/startup joins;exact ledger')
    print('PASS:NO target execution/emulation;installedproviders/retention/physicalcontrolrestore/calleecompletion UNPROVED')


if __name__=='__main__':main()
